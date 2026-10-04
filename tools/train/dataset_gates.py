#!/usr/bin/env python3
"""Zero-LLM dataset gates over the gen-2 pools + every re-keyed gold
(windowing-100 WP4, 2026-10-04). One PASS/FAIL line per gate D1-D7,
exit 1 on any FAIL. These are the dataset-readiness checks the brief's
WP4 asks for BEFORE the four standing gates (pytest / eval / span-recall
/ canon-run -- the LLM-bearing pass, a separate 100k window).

    python tools/train/dataset_gates.py --series jjk

Run over the pools + gold600.gen2 + pilot gen2 + test gen2 + the
drift probes (whichever exist for the series -- pool files are
auto-discovered as <s>/training/opencode/*_windows.jsonl; a gate whose
inputs do not exist for the series prints SKIP, never PASS on a
missing input; a gate with partial inputs runs on what exists and says
so). D1-D7:
- D1 id-unique: every id unique within each file; universe ids unique.
- D2 re-derivable: every record's (page, section, passage) equals the
  builder's text for that id on the CURRENT store (drift detector -- a
  re-ingest that changes a sentence must fail here, not train silently).
- D3 G1: every gold row's quote is verbatim (quote_grid_span non-None)
  in ITS record's passage, and >= 12 chars (under 12 is report-only).
- D4 leakage: no train/pool page in the holdout; no test-gold id in
  any train/pool file. The holdout is holdout_pages() -- v1 dev/test,
  the blind test gold's pages, and the series' recorded holdout
  (training/holdout_pages.json, WP6). A pool file whose pages sit
  entirely on holdout pages IS the series' test pool: exempt from the
  page check, its ids are what the train files must not carry.
- D5 prompt fidelity: every gold record's system message == current
  events.system_prompt(eventive_verbs(store)) and its user message ==
  events._TEMPLATE filled from the window; reports PROMPT_VERSION.
- D6 coverage: union of universe windows' hashes == every sentence of
  the read passages (window-level span-recall, zero-LLM; expect 0 gaps).
- D7 entity presence (report-only): gold600 rows whose subject or object
  mention appears neither in the window text nor the page title -- listed
  to --d7-out for adjudication (these are labels the student cannot learn
  from its input). D7 never fails.

    python tools/train/dataset_gates.py --series jjk
    python tools/train/dataset_gates.py --series mcu
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scriptengine.ingest.events import (  # noqa: E402
    PROMPT_VERSION,
    _TEMPLATE,
    eventive_verbs,
    system_prompt,
)
from scriptengine.ingest.verbatim import fold  # noqa: E402
from scriptengine.ingest.windows import (  # noqa: E402
    quote_grid_span,
    sentence_spans,
)
from scriptengine.index.chunker import sentence_content_hash  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

from emit_windows import build_universe_windows, holdout_pages, universe  # noqa: E402
from rekey_gold import passage_of  # noqa: E402
from rekey_testgold import name_tokens  # noqa: E402

# The test gold's derived keys: everything else in the file is a
# window-id key (one entry per intersecting window, WP3.2).
TEST_RESERVED = {"version", "gen", "guideline", "note", "note_gen2"}


def load_lines(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8")
            .splitlines() if l.strip()]


def load_lines_opt(path):
    """The file's lines, or None when the file does not exist (a series
    without that input -- the gate SKIPs, never PASSes, on it)."""
    return load_lines(path) if path.exists() else None


def load_test_opt(path):
    """The re-keyed test gold's window-id-keyed entries, or None."""
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items() if k not in TEST_RESERVED}


def section_of(value):
    """Normalize a stored section label the way the pool lines do: the
    builder's `lead` is an empty string in the campaign files."""
    return "" if (value or "") in ("", "lead") else value


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--d7-out", default=None,
                    help="where the D7 entity-absent list goes (default "
                         "series/<s>/training/d7_entity_absent.jsonl)")
    ap.add_argument("--no-write-d7", action="store_true")
    a = ap.parse_args()

    sroot = ROOT / "series" / a.series
    db = sroot / "facts.db"
    if not db.exists():
        sys.exit(f"{a.series} is not indexed (no {db}); run `index` first")
    d7_out = (Path(a.d7_out) if a.d7_out
              else sroot / "training" / "d7_entity_absent.jsonl")

    opencode_dir = sroot / "training" / "opencode"
    # Pool files are auto-discovered (jjk: mimo/nemotron/spacebunny,
    # mcu: mcu + mcu_test); archived files (*.old-grid, *.pre-*) do not
    # match the plain *_windows.jsonl pattern.
    pool_files = sorted(p for p in opencode_dir.glob("*_windows.jsonl")
                        if p.is_file())
    if not pool_files:
        sys.exit(f"no pool files in {opencode_dir} (nothing to gate)")
    pools = {p.name[: -len("_windows.jsonl")]: load_lines(p)
             for p in pool_files}
    g600_path = sroot / "training" / "gold600" / "gold600.gen2.jsonl"
    pilot_path = sroot / "training" / "gold" / "gold_pilot_all.gen2.jsonl"
    test_path = sroot / "training" / "recall_gold_v3" / "gold_test_v4.gen2.json"
    probes_path = opencode_dir / "golden_probes.jsonl"
    g600 = load_lines_opt(g600_path)
    pilot = load_lines_opt(pilot_path)
    test = load_test_opt(test_path)
    probes = load_lines_opt(probes_path)

    holdout = holdout_pages(sroot)
    with FactStore(db) as store:
        uni = universe(store)
        windows, by_key, duplicate_ids = build_universe_windows(store, uni)
        by_id = {w.id: w for w in windows}
        ev_verbs = eventive_verbs(store)
        sysmsg = system_prompt(ev_verbs)

    failures, skipped = [], []

    def gate(name, ok, detail):
        if ok is None:
            print(f"{name} SKIP -- {detail}")
            skipped.append(name)
            return
        print(f"{name} {'PASS' if ok else 'FAIL'} -- {detail}")
        if not ok:
            failures.append(name)

    # ---- D1 id-unique -------------------------------------------------
    uni_ids = {w.id for w in windows}
    pool_uniq = {p: (len(rows), len({r["id"] for r in rows}))
                 for p, rows in pools.items()}
    # The builder's collapse count is REPORT-ONLY: a collapsed id means
    # two (page, label, text) groups carry byte-identical window text,
    # which the content-addressed id (WP1) dedups by design -- counted,
    # never a silent drop, and distinct texts cannot collide (the id
    # carries the sentence-hash list). Only id NON-uniqueness fails.
    d1_ok = (len(uni_ids) == len(windows)
             and all(c == u for c, u in pool_uniq.values()))
    d1_parts = [
        f"universe {len(windows)} windows / {len(uni_ids)} unique ids "
        f"(collapsed {duplicate_ids})",
        " ".join(f"pool {p} {c}/{u}" for p, (c, u) in pool_uniq.items()),
    ]
    if probes is not None:
        probe_ids = [r["id"] for r in probes]
        d1_ok = d1_ok and len(set(probe_ids)) == len(probe_ids)
        d1_parts.append(f"probes {len(set(probe_ids))}/{len(probe_ids)}")
    else:
        d1_parts.append("probes (absent, skipped)")
    if test is not None:
        d1_parts.append(f"testgen2 {len(test)} window keys")
    else:
        d1_parts.append("testgen2 (absent, skipped)")
    rec_notes = []
    if g600 is not None:
        g_ids = [r["id"] for r in g600]
        rec_notes.append(
            f"gold600 {len(g_ids)} records / {len(set(g_ids))} window ids")
    if pilot is not None:
        p_ids = [r["id"] for r in pilot]
        rec_notes.append(f"pilot {len(p_ids)} / {len(set(p_ids))}")
    if rec_notes:
        rec_notes.append("(a window may carry more than one row set -- "
                         "legitimate, the id is the window's, not the "
                         "record's)")
        d1_parts.append(", ".join(rec_notes[:-1]) + " " + rec_notes[-1])
    else:
        d1_parts.append("gold600/pilot (absent, skipped)")
    gate("D1", d1_ok, "; ".join(d1_parts))

    # ---- D2 re-derivable ---------------------------------------------
    def line_mismatches(rows):
        bad = []
        for r in rows:
            w = by_id.get(r["id"])
            if w is None:
                bad.append((r["id"], "id not in the builder universe"))
            elif (w.page != r["page"] or w.text != r["passage"]
                    or section_of(w.section) != r["section"]):
                bad.append((r["id"], "page/section/passage drift"))
        return bad

    pool_bad = {p: line_mismatches(rows) for p, rows in pools.items()}
    probe_bad = line_mismatches(probes) if probes is not None else []
    rec_bad = []
    for src, recs in (("gold600", g600), ("pilot", pilot)):
        if recs is None:
            continue
        for rec in recs:
            w = by_id.get(rec["id"])
            if w is None:
                rec_bad.append((src, rec["id"], "id not in the builder universe"))
            elif (w.page != rec["page"]
                    or section_of(w.section) != section_of(rec.get("section"))
                    or w.text != passage_of(rec)):
                rec_bad.append((src, rec["id"], "page/section/passage drift"))
    test_bad = []
    if test is not None:
        for wid, entry in test.items():
            w = by_id.get(wid)
            if w is None or w.text != entry["passage"]:
                test_bad.append(wid)
    n_bad = (sum(len(v) for v in pool_bad.values()) + len(probe_bad)
             + len(rec_bad) + len(test_bad))
    d2_parts = [f"pools {sum(len(v) for v in pool_bad.values())}"]
    if probes is not None:
        d2_parts.append(f"probes {len(probe_bad)}")
    if g600 is not None or pilot is not None:
        d2_parts.append(f"gold600+pilot records {len(rec_bad)}")
    if test is not None:
        d2_parts.append(f"testgen2 {len(test_bad)}")
    d2_detail = ("mismatches against the current store: "
                 + ", ".join(d2_parts) + " (expect 0)")
    if n_bad:
        examples = [b for v in pool_bad.values() for b in v] + probe_bad \
            + [b for b in rec_bad][:2]
        d2_detail += f"; e.g. {examples[:3]}"
    gate("D2", n_bad == 0, d2_detail)

    # ---- D3 G1 (quotes verbatim in their own passage) ----------------
    d3_missing = d3_short = d3_noquote = 0
    def check_quote(quote, passage):
        nonlocal d3_missing, d3_short, d3_noquote
        q = str(quote or "").strip()
        if not q:
            d3_noquote += 1  # a gold row without a quote is a G1 hole
            return
        if quote_grid_span(passage, q) is None:
            d3_missing += 1
        elif len(q) < 12:
            d3_short += 1  # report-only: under 12 chars is not a clause
    if g600 is not None or pilot is not None:
        for rec in (g600 or []) + (pilot or []):
            passage = passage_of(rec)
            for e in json.loads(rec["messages"][2]["content"]).get("events") or []:
                check_quote(e.get("quote"), passage)
    if probes:
        for r in probes:
            for e in r["expected"]:
                check_quote(e.get("quote"), r["passage"])
    if g600 is None and pilot is None and probes is None:
        gate("D3", None, "no gold rows to check (gold600, pilot and probes "
                          "all absent for this series)")
    else:
        gate("D3", d3_missing == 0 and d3_noquote == 0,
             f"{d3_missing} quote(s) not verbatim in their record's passage, "
             f"{d3_noquote} row(s) without a quote "
             f"(report-only under-12: {d3_short})")

    # ---- D4 leakage ----------------------------------------------------
    # A pool file whose pages sit entirely on holdout pages is the
    # series' TEST pool (WP6): its pages ARE the recorded holdout, so it
    # is exempt from the page check; what it must satisfy is that no
    # train file carries its ids (page-disjointness, asserted below).
    train_pages, train_ids = set(), set()
    test_pool_ids, n_test_pools = set(), 0
    for name, rows in pools.items():
        pgs = {r["page"] for r in rows}
        if rows and pgs <= holdout:
            n_test_pools += 1
            test_pool_ids.update(r["id"] for r in rows)
        else:
            train_pages.update(pgs)
            train_ids.update(r["id"] for r in rows)
    if g600 is not None or pilot is not None:
        for rec in (g600 or []) + (pilot or []):
            train_pages.add(rec["page"])
            train_ids.add(rec["id"])
    if probes:
        for r in probes:
            train_pages.add(r["page"])
            train_ids.add(r["id"])
    leak_pages = train_pages & holdout
    leak_ids = set(test_pool_ids & train_ids)
    if test is not None:
        leak_ids |= train_ids & set(test)
    d4_detail = (f"{len(leak_pages)} train/pool page(s) in the holdout, "
                 f"{len(leak_ids)} test-gold id(s) in train/pool files "
                 f"(expect 0)")
    if test_pool_ids:
        d4_detail += (f"; {n_test_pools} test-pool file(s) "
                      f"({len(test_pool_ids)} window(s) on the recorded "
                      f"holdout pages, exempt from the page check; id "
                      f"disjointness from the train pools asserted)")
    if leak_pages or leak_ids:
        d4_detail += (f"; e.g. pages {sorted(leak_pages)[:3]}, "
                      f"ids {sorted(leak_ids)[:3]}")
    gate("D4", not leak_pages and not leak_ids, d4_detail)

    # ---- D5 prompt fidelity --------------------------------------------
    recs5 = []
    if g600 is not None:
        recs5 += g600
    if pilot is not None:
        recs5 += pilot
    if not recs5:
        gate("D5", None, "no gold records to check (gold600/pilot absent "
                          "for this series)")
    else:
        d5_bad = 0
        for rec in recs5:
            if rec["messages"][0]["content"] != sysmsg:
                d5_bad += 1
                continue
            if rec["messages"][1]["content"] != _TEMPLATE.format(
                    series=a.series, page=rec["page"],
                    section=(rec.get("section") or ""), passage=passage_of(rec)):
                d5_bad += 1
        n_recs = len(recs5)
        absent = [nm for nm, r in (("gold600", g600), ("pilot", pilot))
                  if r is None]
        src_note = f" (absent: {', '.join(absent)})" if absent else ""
        gate("D5", d5_bad == 0,
             f"{n_recs - d5_bad}/{n_recs} gold records{src_note} match the current prompt "
             f"(PROMPT_VERSION {PROMPT_VERSION}, {len(ev_verbs)} eventive "
             f"verbs; system == system_prompt(eventive_verbs(store)), user == "
             f"_TEMPLATE filled from the window)")

    # ---- D6 coverage (window-level span-recall, zero-LLM) --------------
    gap_total = 0
    gap_examples = []
    for page, label, text in uni:
        # The read passage's own sentence hashes vs what the section's
        # windows actually carry: a sentence no window holds is a gap the
        # 35B campaign can never see (the standing span-recall gate's
        # zero-LLM twin).
        h_text = {sentence_content_hash(s) for _a, _b, s in sentence_spans(text)}
        h_win = set()
        for w in by_key.get((page, label), ()):
            h_win.update(w.hashes)
        gaps = h_text - h_win
        gap_total += len(gaps)
        if gaps and len(gap_examples) < 3:
            gap_examples.append((page, label, len(gaps)))
    d6_detail = (f"{gap_total} sentence hash(es) of the read passages "
                 f"missing from the windows' union (expect 0)")
    if gap_total:
        d6_detail += f"; e.g. {gap_examples}"
    gate("D6", gap_total == 0, d6_detail)

    # ---- D7 entity presence (report-only) ------------------------------
    if g600 is None:
        gate("D7", None, "no gold600 rows to check (absent for this series)")
    else:
        # The scorer's own name rule (name_tokens): a 3+ letter word of the
        # name, stop set removed, folded -- the mention it would match on.
        d7, uncheckable, n_rows = [], 0, 0
        for rec in g600:
            w = by_id.get(rec["id"])
            if w is None:
                continue  # D2 has already flagged it
            hay = fold(w.text + " " + w.page)
            for e in json.loads(rec["messages"][2]["content"]).get("events") or []:
                n_rows += 1
                for field in ("subject", "object"):
                    name = str(e.get(field) or "").strip()
                    if not name or name.lower() == "null":
                        continue  # objectless verbs (awakened): nothing to check
                    toks = name_tokens(name)
                    if not toks:
                        uncheckable += 1  # a name with no 3+ letter word
                        continue
                    if not any(t in hay for t in toks):
                        d7.append({"record_id": rec["id"], "page": rec["page"],
                                   "section": rec.get("section") or "",
                                   "event": e, "absent": field, "name": name})
        if not a.no_write_d7:
            d7_out.write_text(
                "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in d7),
                encoding="utf-8")
        n_sub = sum(1 for r in d7 if r["absent"] == "subject")
        gate("D7", True,  # report-only: a list for adjudication, never a failure
             f"entity presence: {n_sub} subject + {len(d7) - n_sub} object "
             f"mentions of {n_rows} gold600 rows absent from window text + "
             f"page title ({uncheckable} uncheckable names) -> {d7_out}")

    print()
    if failures:
        print(f"RESULT: FAIL -- {', '.join(failures)}")
        return 1
    if skipped:
        print(f"RESULT: all gates PASS ({', '.join(skipped)} SKIP -- "
              f"inputs absent for this series)")
    else:
        print("RESULT: all gates PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
