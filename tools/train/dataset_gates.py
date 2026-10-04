#!/usr/bin/env python3
"""Zero-LLM dataset gates over the gen-2 pools + every re-keyed gold
(windowing-100 WP4, 2026-10-04). One PASS/FAIL line per gate D1-D9,
exit 1 on any FAIL. These are the dataset-readiness checks the brief's
WP4 asks for BEFORE the four standing gates (pytest / eval / span-recall
/ canon-run -- the LLM-bearing pass, a separate 100k window).

    python tools/train/dataset_gates.py --series jjk

Run over the pools + gold600.gen2 + pilot gen2 + test gen2 + the
drift probes (whichever exist for the series -- pool files are
auto-discovered as <s>/training/opencode/*_windows.jsonl; a gate whose
inputs do not exist for the series prints SKIP, never PASS on a
missing input; a gate with partial inputs runs on what exists and says
so). D1-D9:
- D1 id-unique: every id unique within each file; universe ids unique.
  (The gen-2 test gold's U-WP5 passage units: covering window ids
  unique within each unit; a window shared by sibling units is the
  gold's own sharing, reported, not a defect. U-WP4c: a passage unit
  whose (page, section) is OFF the production read set cannot re-derive
  in the universe by construction -- the gold files are unchanged and
  stay usable as labels, so those units are reported, not failed; only
  units ON the read set must carry universe ids.)
- D2 re-derivable: every record's (page, section, passage) equals the
  builder's text for that id on the CURRENT store (drift detector -- a
  re-ingest that changes a sentence must fail here, not train
  silently). The test gold's units are re-derived BYTE-IDENTICAL
  (rekey_testgold.derive_unit on the current store's texts). U-WP4c:
  gold records OFF the production read set (their (page, section) is
  not a passage the extractor reads) are reported, not failed -- the
  gold files are unchanged and stay usable as labels; re-derivation is
  impossible for them by construction.
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
  the PRODUCTION READ SET (U-WP4c: universe() IS the read set -- the
  pages of events.scope_plan('all') and, per page, the passages of
  events.build_passages: the read sections, the lead, the declared
  fact values); window-level span-recall, zero-LLM; expect 0 gaps.
- D7 entity presence (report-only): gold600 rows whose subject or object
  mention appears neither in the window text nor the page title -- listed
  to --d7-out for adjudication (these are labels the student cannot learn
  from its input). D7 never fails.
- D8 universal holdout (U-WP4, 2026-10-04): the plan's cross-wiki check --
  (a) no hxh window id in ANY wiki's train pool (hxh is the held-out
  wiki; it never trains; ids are content-addressed, so a cross-wiki hit
  is real content leakage). Cross-wiki page-TITLE collisions are
  reported, not failed: titles are wiki-local, and a "Chapter 114"
  exists in every anime wiki (the U-WP4 first run found 12 such
  collisions, 0 id hits). (b) Per wiki, no test id/page in its own
  train pools (page-disjoint by construction; the gate is the belt).
  The pool files are auto-discovered across every series; a pool whose
  pages sit entirely on the wiki's holdout is its test pool (D4's rule).
  The hxh clause SKIPs while the hxh test pool does not exist yet.
- D9 production read set (U-WP4c, 2026-10-04): every pool window's
  (page, section label) must be a passage the production extractor
  reads (the universe's (page, label) set); 0 violations required.
  U-WP4 measured 5-40 pct of the U-WP4b pools' windows on sections the
  extractor never reads or pages not in its queue; the U-WP4c re-emit
  made the universe the read set, so the pools now carry 0 -- the gate
  is the belt (a stale pre-U-WP4c pool file left in place fails here,
  not in the 35B campaign).

    python tools/train/dataset_gates.py --series jjk
    python tools/train/dataset_gates.py --series mcu
"""
import argparse
import json
import sys
from collections import Counter
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
from rekey_testgold import derive_unit, name_tokens  # noqa: E402

# The test gold's meta keys: everything else in the file is a passage
# unit (U-WP5: one entry per original W-index, keyed W<n>; the old
# per-window re-key's window-id keys are the .pre-u5 archive's shape).
TEST_RESERVED = {"version", "gen", "shape", "guideline", "note", "note_gen2"}


def load_lines(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8")
            .splitlines() if l.strip()]


def load_lines_opt(path):
    """The file's lines, or None when the file does not exist (a series
    without that input -- the gate SKIPs, never PASSes, on it)."""
    return load_lines(path) if path.exists() else None


def load_test_opt(path):
    """The re-keyed test gold's PASSAGE units (U-WP5: one entry per
    original W-index, keyed W<n>, each carrying the annotated passage
    and its covering windows), or None."""
    if not path.exists():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    return {k: v for k, v in data.items()
            if k not in TEST_RESERVED and isinstance(v, dict)
            and isinstance(v.get("windows"), list)}


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
    # U-WP4c: the production read set as (page, label) pairs -- the
    # universe IS the read set (scope_plan('all') pages + build_passages
    # passages: the read sections, the lead, the declared fact values).
    # D9 checks the pools against it; D1/D2 use it to separate gold
    # records OFF the read set (reported, not failed: the gold files
    # are unchanged and stay usable as labels) from genuine drift.
    read_set = {(p, l) for p, l, _t in uni}

    def rec_label(rec):
        """The record's read-set label (pool/gold lines carry '' for the
        lead, the builder's 'lead' otherwise; fact lines carry the
        extractor's 'fact:<key>' label)."""
        return (rec.get("section") or "") or "lead"

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
        # U-WP5 passage units: the W<n> keys are dict keys (unique by
        # construction); the strictness lives in each unit's covering
        # window ids -- unique WITHIN the unit and present in the
        # builder universe. A window shared by two sibling units is
        # legitimate (the gold600 rule: the id is the window's, not
        # the unit's) and is reported, not failed. U-WP4c: a unit
        # whose (page, section) is OFF the production read set cannot
        # re-derive in the universe by construction -- the gold files
        # are unchanged and stay usable as labels, so those units are
        # reported, not failed; only units ON the read set must carry
        # universe ids.
        dup_within = sum(
            1 for u in test.values()
            if len({w["id"] for w in u["windows"]}) != len(u["windows"]))
        on_set_tids, off_units = [], 0
        for u in test.values():
            if (u.get("page"), rec_label(u)) not in read_set:
                off_units += 1  # reported in the detail, never a failure
                continue
            on_set_tids += [w["id"] for w in u["windows"]]
        not_in_uni = [i for i in on_set_tids if i not in uni_ids]
        d1_ok = d1_ok and dup_within == 0 and not not_in_uni
        d1_parts.append(
            f"testgen2 {len(test)} passage units / "
            f"{len(on_set_tids)} covering window(s) on the read set "
            f"(dup-within-unit {dup_within}, off-universe "
            f"{len(not_in_uni)})"
            + (f"; {off_units} unit(s) OFF the read set (report-only, "
               "U-WP4c: gold unchanged, still usable as labels)"
               if off_units else ""))
    else:
        d1_parts.append("testgen2 (absent, skipped)")
    rec_notes = []
    # U-WP4c: how many gold records sit OFF the production read set
    # (reported, never failed -- the gold files are unchanged and stay
    # usable as labels; only their pool-eligibility is off the universe).
    off_gold = sum(
        1 for r in (g600 or [])
        if ((r.get("page") or ""), rec_label(r)) not in read_set)
    off_pilot = sum(
        1 for r in (pilot or [])
        if ((r.get("page") or ""), rec_label(r)) not in read_set)
    if g600 is not None:
        g_ids = [r["id"] for r in g600]
        rec_notes.append(
            f"gold600 {len(g_ids)} records / {len(set(g_ids))} window ids"
            + (f" ({off_gold} OFF the read set, report-only)"
               if off_gold else ""))
    if pilot is not None:
        p_ids = [r["id"] for r in pilot]
        rec_notes.append(f"pilot {len(p_ids)} / {len(set(p_ids))}"
                         + (f" ({off_pilot} OFF the read set, report-only)"
                            if off_pilot else ""))
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
    rec_bad, rec_off = [], 0
    for src, recs in (("gold600", g600), ("pilot", pilot)):
        if recs is None:
            continue
        for rec in recs:
            if ((rec.get("page") or ""), rec_label(rec)) not in read_set:
                # U-WP4c: the record sits OFF the production read set
                # (its (page, section) is not a passage the extractor
                # reads) -- the gold files are unchanged and stay usable
                # as labels; re-derivation is impossible for them by
                # construction, so it is reported, not failed.
                rec_off += 1
                continue
            w = by_id.get(rec["id"])
            if w is None:
                rec_bad.append((src, rec["id"], "id not in the builder universe"))
            elif (w.page != rec["page"]
                    or section_of(w.section) != section_of(rec.get("section"))
                    or w.text != passage_of(rec)):
                rec_bad.append((src, rec["id"], "page/section/passage drift"))
    test_bad, test_off = [], 0
    test_partial = False
    if test is not None:
        rdir = sroot / "training" / "recall_gold_v3"
        w100_path, v4_path = rdir / "windows_100.json", rdir / "gold_test_v4.json"
        if w100_path.exists() and v4_path.exists():
            # The strict drift detector (U-WP5 passage shape): each
            # stored unit must re-derive BYTE-IDENTICAL on the CURRENT
            # store -- derive_unit rebuilds the section's grid from the
            # store's own texts and re-locates the passage, so a
            # re-ingest that changes a sentence fails here, not in
            # training (the gate's whole point). U-WP4c: units OFF the
            # production read set are skipped (reported in test_off,
            # never failed: the gold is unchanged, still usable as
            # labels -- re-derivation is impossible for them by
            # construction).
            w100 = json.loads(w100_path.read_text(encoding="utf-8"))
            v4 = json.loads(v4_path.read_text(encoding="utf-8"))
            grids2 = {}
            with FactStore(db) as store2:
                for key, unit in sorted(test.items()):
                    if ((unit.get("page") or ""), rec_label(unit)) not in read_set:
                        test_off += 1
                        continue
                    n = unit.get("w")
                    evs = v4.get(key)
                    if n is None or n >= len(w100) or evs is None:
                        test_bad.append((key, "no W-index source (drift)"))
                        continue
                    red, why = derive_unit(store2, n, w100[n], evs, grids2)
                    if red is None:
                        test_bad.append((key, why))
                    elif red != unit:
                        test_bad.append((key, "stored unit differs from re-derivation"))
        else:
            # The annotation sources are absent: re-derivation is
            # impossible, so the gate runs the WEAK check (ids in the
            # universe, page/section match) and says so -- it never
            # PASSes a full D2 on a shape it could not verify.
            test_partial = True
            for key, unit in sorted(test.items()):
                if ((unit.get("page") or ""), rec_label(unit)) not in read_set:
                    test_off += 1
                    continue
                for w in unit["windows"]:
                    bu = by_id.get(w["id"])
                    if bu is None:
                        test_bad.append((key, f"{w['id']} not in the builder universe"))
                        break
                    if (bu.page != (unit.get("page") or "")
                            or section_of(bu.section) != (unit.get("section") or "")):
                        test_bad.append((key, f"{w['id']} page/section drift"))
                        break
    n_bad = (sum(len(v) for v in pool_bad.values()) + len(probe_bad)
            + len(rec_bad) + len(test_bad))
    d2_parts = [f"pools {sum(len(v) for v in pool_bad.values())}"]
    if probes is not None:
        d2_parts.append(f"probes {len(probe_bad)}")
    if g600 is not None or pilot is not None:
        d2_parts.append(f"gold600+pilot records {len(rec_bad)}"
                        + (f" (+{rec_off} off the read set, report-only)"
                           if rec_off else ""))
    if test is not None:
        d2_parts.append(f"testgen2 {len(test_bad)}"
                        + (f" (+{test_off} off the read set, report-only)"
                           if test_off else "")
                        + (" (weak check: sources absent)" if test_partial else ""))
    d2_detail = ("mismatches against the current store: "
                 + ", ".join(d2_parts) + " (expect 0)")
    if n_bad:
        examples = [b for v in pool_bad.values() for b in v] + probe_bad \
            + [b for b in rec_bad][:2] + test_bad[:2]
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
        # U-WP5 passage units: the test gold's window ids are the union
        # of the units' covering windows (a window is test gold while
        # any annotated passage reads it).
        test_win_ids = {w["id"] for u in test.values() for w in u["windows"]}
        leak_ids |= train_ids & test_win_ids
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
    # U-WP4c: the universe IS the production read set (scope_plan('all')
    # pages + build_passages passages: the read sections, the lead, the
    # declared fact values), so this checks every sentence the
    # extractor reads, exactly.
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
    d6_detail = (f"{gap_total} sentence hash(es) of the production read "
                 f"set (U-WP4c: universe() = scope_plan('all') pages + "
                 f"build_passages passages) missing from the windows' "
                 f"union (expect 0)")
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

    # ---- D8 universal holdout (U-WP4, 2026-10-04) ---------------------
    # The plan's cross-wiki leakage check (plan/UNIVERSAL_DATASET_PLAN.md
    # U-WP4): (a) hxh is the HELD-OUT wiki -- it never trains: no hxh
    # window id may sit in ANY wiki's train pool; (b) per wiki, no test
    # id/page in its own train pools (page-disjoint by construction,
    # the gate is the belt). The cross-wiki clause fails on window
    # IDs only: ids are content-addressed (page + section + span +
    # sentence hashes), so a cross-wiki id hit is genuine hxh CONTENT
    # in another wiki's pool. Cross-wiki PAGE hits are NOT failed:
    # page titles are wiki-local identifiers, and generic titles (a
    # "Chapter 114" exists in every anime wiki) collide across wikis
    # by construction of a multi-wiki dataset -- they are reported
    # (the U-WP4 first run found 12 "Chapter N" collisions, 0 id
    # hits), never a failure. The pool files are auto-discovered
    # across every series (the cross-wiki clause is the point of D8);
    # a pool whose pages sit entirely on the wiki's holdout is its
    # TEST pool (D4's rule), everything else is train.
    def wiki_pool_files(s):
        d = ROOT / "series" / s / "training" / "opencode"
        if not d.is_dir():
            return {}
        return {p.name[: -len("_windows.jsonl")]: p for p in
                sorted(d.glob("*_windows.jsonl")) if p.is_file()}

    wiki_pools = {}
    for s in sorted(d.name for d in (ROOT / "series").iterdir()
                    if (d / "training" / "opencode").is_dir()):
        hset = holdout_pages(ROOT / "series" / s)
        train_ids, train_pgs = set(), set()
        test_ids, test_pgs = set(), set()
        for _name, p in wiki_pool_files(s).items():
            rows = load_lines(p)
            pgs = {r["page"] for r in rows}
            if rows and pgs <= hset:
                test_ids |= {r["id"] for r in rows}
                test_pgs |= pgs
            else:
                train_ids |= {r["id"] for r in rows}
                train_pgs |= pgs
        wiki_pools[s] = (train_ids, train_pgs, test_ids, test_pgs)

    d8_parts, d8_fail, d8_skip = [], False, True
    if "hxh" in wiki_pools and (wiki_pools["hxh"][2] or wiki_pools["hxh"][3]):
        all_train_ids, all_train_pgs = set(), set()
        for _s, (ti, tp, _x, _y) in wiki_pools.items():
            all_train_ids |= ti
            all_train_pgs |= tp
        d8a_id = len(wiki_pools["hxh"][2] & all_train_ids)
        d8a_pg = len(wiki_pools["hxh"][3] & all_train_pgs)
        d8_skip = False
        if d8a_id:
            d8_fail = True
        d8_parts.append(
            f"hxh holdout: {len(wiki_pools['hxh'][2])} test window(s) / "
            f"{len(wiki_pools['hxh'][3])} test page(s) vs "
            f"{len(all_train_ids)} train window(s) / "
            f"{len(all_train_pgs)} train page(s) across "
            f"{len(wiki_pools)} wiki(s): {d8a_id} id hit(s) (expect 0 -- "
            f"ids are content-addressed, a hit is real leakage) + "
            f"{d8a_pg} page-title collision(s) (wiki-local generic "
            f"titles, e.g. 'Chapter N', collide across wikis -- "
            f"reported, not failed)")
    else:
        d8_parts.append("hxh holdout clause SKIP (no hxh test pool yet)")
    _sti, _stpg, _tti, _ttpg = wiki_pools.get(
        a.series, (set(), set(), set(), set()))
    d8b_id = len(_tti & _sti)
    d8b_pg = len(_ttpg & _stpg)
    if _tti or _ttpg:
        d8_skip = False
        if d8b_id or d8b_pg:
            d8_fail = True
        d8_parts.append(
            f"{a.series} per-wiki: {len(_tti)} test window(s) / "
            f"{len(_ttpg)} test page(s) vs {len(_sti)} train window(s) / "
            f"{len(_stpg)} train page(s): {d8b_id} id + {d8b_pg} page "
            f"hit(s) (expect 0)")
    else:
        d8_parts.append(f"{a.series} per-wiki clause: no test pool file "
                       f"(the test gold's ids are D4's)")
    gate("D8", (None if d8_skip else (not d8_fail)), "; ".join(d8_parts))

    # ---- D9 production read set (U-WP4c, 2026-10-04) ------------------
    # Every pool window's (page, section label) must be a passage the
    # production extractor reads (the universe's (page, label) set: the
    # read sections, the lead, the declared fact values). U-WP4 measured
    # 5-40 pct of the U-WP4b pools' windows off the read set (sections
    # the extractor never selects, or pages not in its queue); the
    # U-WP4c re-emit made the universe the read set, so 0 violations is
    # the expectation. The gate is the belt: a stale pre-U-WP4c pool
    # file left in place fails here, not in the 35B campaign.
    d9_bad = []
    for name, rows in pools.items():
        for r in rows:
            if (r["page"], rec_label(r)) not in read_set:
                d9_bad.append((name, r["id"], r["page"], rec_label(r)))
    gate("D9", not d9_bad,
         f"{len(d9_bad)} pool window(s) on a (page, section) the "
         f"production read set does not carry (expect 0)"
         + (f"; e.g. {d9_bad[:3]}" if d9_bad else ""))

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
