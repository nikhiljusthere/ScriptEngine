#!/usr/bin/env python3
"""Build the JJK student-training set on the gen-2 grid (U-WP6, 2026-10-04,
plan/UNIVERSAL_DATASET_PLAN.md "Student model trial").

Sources: the verified gen-2 gold -- gold600/gen2 + pilot gen2 records with
rekey status `kept` / `reexpressed` (the adjudicated labels; `reread` and
`straddle` are EXCLUDED: their empties were adjudicated on the contaminated
old-grid windows and the 35B re-read owns them, rekey_gold's ruling). One
record per gen-2 window id: when two sources label the same window the
gold600 record wins (it ran the fuller adjudication) and the conflict is
counted, never silently dropped.

EARNED EMPTIES (mandatory -- the set has zero empties without them): the
gen-2 windows that sit FULLY inside a reexpressed/kept record's ORIGINAL
annotated passage and received no row of that record. The adjudicator read
that whole old passage and listed every event in it, so a new window whose
entire text was read and got no row is a genuine empty (the same rule
tools/train/rekey_testgold.py used for the 4 empty drift probes -- the
candidates are its `empty_candidates`, copied here over kept+reexpressed).
A window any record claims (any status, either file) carries rows of SOME
record and is not an event-free window (the probes' `claimed` rule); the
test gold's covering windows and the drift probes' ids are out (the
labeler/evaluator must stay blind to the student's test set), and every
page in the U-WP2 holdout (v1 dev/test + the blind test gold's pages) is
out (split by page, never by row).

Messages are the EXACT production prompt (decision 6 of the plan): system
= events.system_prompt(eventive_verbs(store)), user = events._TEMPLATE
filled from the window -- the same strings dataset_gates D5 checks, so the
student is a drop-in for the extractor's own call. assistant =
{"events": [...]} with the verified rows (quote, subject, verb, object).
The record's stored passage is RE-VERIFIED against the store's own texts
(content-addressed id located on the page's grid, rekey_gold's
`grid_texts_for`): a re-ingest that changed a sentence fails the build, it
never trains silently.

Dev = 5% of the set's PAGES (seeded 20261004), never split a page -- the
only data any hyper-parameter is chosen on (the plan's "Splits").

    python tools/train/build_student_set.py --series jjk
        -> series/jjk/training/student/{train,dev}.jsonl + receipt.json

The build ends in its own dataset_gates-style checks over the WRITTEN
files (quotes verbatim in their user passage, D5 prompt fidelity, no
holdout page, no test-gold/probe id, unique ids, page-disjoint splits)
and exits non-zero on any failure, like emit_windows' WP2 assertions.
"""
import argparse
import json
import random
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
from scriptengine.ingest.windows import (  # noqa: E402
    CURRENT_GEN,
    build_windows,
    quote_grid_span,
)
from scriptengine.stores.facts import FactStore  # noqa: E402

from emit_windows import holdout_pages, RARE  # noqa: E402
from rekey_gold import grid_texts_for, passage_of  # noqa: E402

# The test gold's meta keys (dataset_gates' TEST_RESERVED): everything
# else in the re-keyed file is a passage unit.
TEST_RESERVED = {"version", "gen", "shape", "guideline", "note", "note_gen2"}

DEV_SEED = 20261004  # the plan's dev split seed (U-WP6 brief)
DEV_FRAC = 0.05
ADJUDICATED = ("kept", "reexpressed")


def load_jsonl(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8").splitlines()
            if l.strip()]


def load_test_units(path):
    """The re-keyed test gold's PASSAGE units (U-WP5 shape) or {}."""
    if not Path(path).exists():
        return {}
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return {k: v for k, v in data.items()
            if k not in TEST_RESERVED and isinstance(v, dict)
            and isinstance(v.get("windows"), list)}


def section_of(value):
    """The pool-line shape: the builder's `lead` is an empty string."""
    return "" if (value or "") in ("", "lead") else value


def render_messages(series, sysmsg, page, section, passage):
    """The exact production messages (decision 6): the same strings
    dataset_gates D5 checks -- system = system_prompt(eventive_verbs),
    user = _TEMPLATE filled from the window."""
    return [
        {"role": "system", "content": sysmsg},
        {"role": "user",
         "content": _TEMPLATE.format(series=series, page=page,
                                     section=section, passage=passage)},
        None,  # the assistant turn is filled by the caller
    ]


def assistant_content(events):
    """The assistant turn: {"events": [...]} with the verified rows, the
    engine's canonical serialization (rekey_gold's assistant shape)."""
    return json.dumps({"events": events}, ensure_ascii=False)


def is_rare_window(events):
    """A window that states a RARE verb (emit_windows' set, the same one
    build_trainset repeats with --rare-x): under-represented in natural
    prose, so --rare-x over-samples it."""
    return any((e.get("verb") or "").lower() in RARE for e in events)


def dev_page_split(pages, frac=DEV_FRAC, seed=DEV_SEED):
    """(dev_pages, train_pages): `frac` of the DISTINCT PAGES, seeded; a
    page is never split (the plan's "Splits": dev = 5% of pages, the only
    data a hyper-parameter is chosen on). Deterministic for a seed."""
    pages = sorted(pages)
    k = max(1, round(frac * len(pages))) if pages else 0
    dev = set(random.Random(seed).sample(pages, min(k, len(pages))))
    return dev, set(pages) - dev


def verify_record(store, rec, grids):
    """Re-locate the record's window on the store's own texts (rekey_gold
   's grid, never the file's stored ids) and return
    (page, section, window_text) or None (store drift: the label's source
    no longer says what it said -- refuse, never guess)."""
    page = (rec.get("page") or "").strip()
    label = (rec.get("section") or "").strip() or "lead"
    stored = passage_of(rec)
    if not stored:
        return None
    for text in grid_texts_for(store, rec):
        key = (page, label, text)
        if key not in grids:
            grids[key] = build_windows(page, label, text, gen=CURRENT_GEN)
        for w in grids[key]:
            if w.id == rec["id"]:
                if w.text != stored:
                    return None  # the id and the passage disagree: drift
                return w.page, section_of(w.section), w.text
    return None


def earned_empty_candidates(store, src, report, grids, claimed, test_ids,
                            probe_ids, holdout):
    """The EARNED EMPTIES (U-WP6): the gen-2 windows fully inside a
    reexpressed/kept record's ORIGINAL annotated passage that received no
    row of that record.

    Copied from tools/train/rekey_testgold.py's `empty_candidates` (the
    4 empty drift probes' rule), extended from `reexpressed` to
    kept+reexpressed per the U-WP6 brief: a `kept` record's old passage
    fits in ONE new window (the kept rule), so no other window sits fully
    inside it (the windows tile the section) and kept contributes nothing
    -- the rule is stated over both because the brief says so and the
    tiling makes it safe. The record's `new_ids` (the rekey report) are
    its rows' windows; a window extending past the passage (a partial
    read) has an unread tail and its empty is NOT earned (the rekeyer's
    rule). Exclusions: a window any record claims (any status, either
    file -- it carries rows of some record), the test gold's covering
    windows and the drift probes (the labeler/evaluator stays blind), and
    the U-WP2 holdout pages. Returns (window ids, receipt counts)."""
    orig = {r["id"]: r for r in load_jsonl(src)}
    tally = {"records": 0, "windows": 0}
    out = set()
    for rec in json.loads(Path(report).read_text(encoding="utf-8"))["records"]:
        if rec["status"] not in ADJUDICATED:
            continue  # reread/straddle: the 35B re-read owns those windows
        o = orig.get(rec["old_id"])
        if o is None:
            continue
        tally["records"] += 1
        page = (o.get("page") or "").strip()
        label = (o.get("section") or "").strip() or "lead"
        passage = passage_of(o)
        if not passage:
            continue
        with_rows = set(rec["new_ids"])
        for text in grid_texts_for(store, o):
            # The grid of the ORIGINAL record's (page, label) texts -- the
            # same grid the rekeyer located the passage on (rekey_gold's
            # grid, never the file's stored ids).
            key = (page, label, text)
            if key not in grids:
                grids[key] = build_windows(page, label, text, gen=CURRENT_GEN)
            span = quote_grid_span(text, passage)
            if span is None:
                continue
            ps, pe = span
            for w in grids[key]:
                # Fully inside the annotated span: the window's whole text
                # was read and listed (the rekeyer's earned-empty rule).
                if not (ps <= w.s_start and w.s_end <= pe):
                    continue
                if w.id in with_rows or w.id in claimed or w.id in test_ids \
                        or w.id in probe_ids:
                    continue
                if w.page in holdout:
                    continue
                out.add(w.id)
                tally["windows"] += 1
    return out, tally


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--out-dir", default=None,
                    help="default series/<series>/training/student")
    ap.add_argument("--dry-run", action="store_true",
                    help="report the receipt, write nothing")
    a = ap.parse_args()

    sroot = ROOT / "series" / a.series
    db = sroot / "facts.db"
    if not db.exists():
        sys.exit(f"{a.series} is not indexed (no {db}); run `index` first")
    out_dir = Path(a.out_dir) if a.out_dir else sroot / "training" / "student"

    g600_path = sroot / "training" / "gold600" / "gold600.gen2.jsonl"
    pilot_path = sroot / "training" / "gold" / "gold_pilot_all.gen2.jsonl"
    g600_src = sroot / "training" / "gold600" / "gold600.jsonl"
    pilot_src = sroot / "training" / "gold" / "gold_pilot_all.jsonl"
    g600_report = sroot / "training" / "gold600" / "gold600.gen2.report.json"
    pilot_report = sroot / "training" / "gold" / "gold_pilot_all.gen2.report.json"
    test_path = sroot / "training" / "recall_gold_v3" / "gold_test_v4.gen2.json"
    probes_path = sroot / "training" / "opencode" / "golden_probes.jsonl"

    # The U-WP2 holdout (emit_windows.holdout_pages over the SERIES root:
    # v1 dev/test pages + the blind test gold's pages + any recorded
    # holdout): a held-out page never trains.
    holdout = holdout_pages(sroot)
    test_units = load_test_units(test_path)
    # The test gold's window ids: a window is test gold while ANY
    # annotated passage reads it (U-WP5 covering windows).
    test_ids = {w["id"] for u in test_units.values() for w in u["windows"]}
    probe_ids = ({r["id"] for r in load_jsonl(probes_path)}
                 if probes_path.exists() else set())
    # The probes stay out of training the same way (they are the labeler's
    # drift check, not data).

    with FactStore(db) as store:
        ev_verbs = eventive_verbs(store)
        sysmsg = system_prompt(ev_verbs)
        # A window any record claims (any status, either file) carries rows
        # of SOME record -- it is not an event-free window (the probes'
        # `claimed` rule, rekey_testgold).
        claimed = set()
        for path in (g600_path, pilot_path):
            for rec in load_jsonl(path):
                claimed.add(rec["rekey"]["new_id"])

        # One record per gen-2 window id, gold600 first (its adjudication
        # is the fuller one): the conflict is counted, never dropped.
        by_id, conflicts = {}, {"cross_source": 0, "same_source": 0}
        src_stat = Counter()
        drift = 0
        excl = {"test_gold_id": 0, "probe_id": 0, "holdout_page": 0}
        grids = {}
        for name, path in (("gold600", g600_path), ("pilot", pilot_path)):
            for rec in load_jsonl(path):
                if rec["rekey"]["status"] not in ADJUDICATED:
                    continue  # reread/straddle: excluded by the brief
                # The brief's exclusions, applied to the source records too
                # (the 20 positive drift probes are built FROM these
                # records, so their ids must never train; a held-out page
                # never trains -- D4 keeps the sources clean, the belt
                # here is the set's own).
                if rec["id"] in test_ids:
                    excl["test_gold_id"] += 1
                    continue
                if rec["id"] in probe_ids:
                    excl["probe_id"] += 1
                    continue
                if (rec.get("page") or "").strip() in holdout:
                    excl["holdout_page"] += 1
                    continue
                loc = verify_record(store, rec, grids)
                if loc is None:
                    drift += 1
                    continue
                page, section, text = loc
                if rec["id"] in by_id:
                    other = by_id[rec["id"]]["source"]
                    conflicts["cross_source" if other != name
                               else "same_source"] += 1
                    continue  # first (gold600) wins
                events = json.loads(rec["messages"][2]["content"])
                if not isinstance(events, dict) or \
                        not isinstance(events.get("events"), list):
                    sys.exit(f"{path.name}: record {rec['id']}'s assistant "
                             f"answer is not the {{\"events\": [...]}} shape")
                rows = events["events"]
                by_id[rec["id"]] = {
                    "id": rec["id"], "page": page, "section": section,
                    "passage": text, "gen": CURRENT_GEN,
                    "source": name, "rekey": rec["rekey"],
                    "events": rows, "rare": is_rare_window(rows),
                    "messages": render_messages(a.series, sysmsg, page,
                                                section, text)[:2] + [
                        {"role": "assistant",
                         "content": assistant_content(rows)}],
                }
                src_stat[f"{name}:{rec['rekey']['status']}"] += 1

        # The EARNED EMPTIES: same rule as the 4 empty drift probes
        # (rekey_testgold.empty_candidates), over kept+reexpressed.
        empty_ids, empty_tally = set(), {}
        for name, src, report in (("gold600", g600_src, g600_report),
                                  ("pilot", pilot_src, pilot_report)):
            ids, tally = earned_empty_candidates(
                store, src, report, grids, claimed, test_ids, probe_ids,
                holdout)
            empty_ids |= ids
            empty_tally[name] = tally

        # The empties' records (their windows' texts come from the same
        # verified grids; a candidate the gold already kept is out of the
        # `claimed` set and so of the candidates by construction).
        empty_ids -= set(by_id)  # belt: a claimed window is a gold window
        for wid in sorted(empty_ids):
            w = next((w for _k, ws in grids.items() for w in ws
                      if w.id == wid), None)
            if w is None:
                # The candidate's grid was built from the ORIGINAL
                # record's texts; the id is content-addressed, so locate
                # it on the record's own (page, label) grid instead.
                sys.exit(f"earned empty {wid} not located on any verified "
                         f"grid (store drift)")
            rec = {
                "id": w.id, "page": w.page,
                "section": section_of(w.section), "passage": w.text,
                "gen": CURRENT_GEN, "source": "earned_empty",
                "rekey": None, "events": [], "rare": False,
                "earned_empty": True,
            }
            rec["messages"] = render_messages(a.series, sysmsg, rec["page"],
                                              rec["section"], rec["passage"])[:2] \
                + [{"role": "assistant", "content": assistant_content([])}]
            by_id[w.id] = rec

    # ---- the split (5% of pages, seeded; a page is never split) -------
    pages = {r["page"] for r in by_id.values()}
    dev_pages, train_pages = dev_page_split(pages)
    for r in by_id.values():
        r["split"] = "dev" if r["page"] in dev_pages else "train"
    train_recs = [r for r in by_id.values() if r["split"] == "train"]
    dev_recs = [r for r in by_id.values() if r["split"] == "dev"]

    verb_hist = Counter()
    for r in by_id.values():
        for e in r["events"]:
            verb_hist[(e.get("verb") or "").lower()] += 1
    n_empty = sum(1 for r in by_id.values() if not r["events"])

    # ---- write (supersede, don't salvage: stale files keep their data)
    if not a.dry_run:
        out_dir.mkdir(parents=True, exist_ok=True)
        for name, recs in (("train", train_recs), ("dev", dev_recs)):
            path = out_dir / f"{name}.jsonl"
            old = path.with_name(path.name + ".pre-u6")
            if path.exists() and not old.exists():
                path.rename(old)
            lines = []
            for i, r in enumerate(recs):
                line = {k: r[k] for k in ("id", "page", "section", "passage",
                                          "gen", "source", "split", "events",
                                          "messages")}
                line["n"] = i
                if r.get("rekey") is not None:
                    line["rekey"] = r["rekey"]
                if r.get("rare"):
                    line["rare"] = True
                if r.get("earned_empty"):
                    line["earned_empty"] = True
                lines.append(json.dumps(line, ensure_ascii=False))
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    # ---- the dataset_gates-style checks over the WRITTEN files --------
    out = {name: load_jsonl(out_dir / f"{name}.jsonl")
           for name in ("train", "dev")} if not a.dry_run \
        else {"train": train_recs, "dev": dev_recs}
    all_recs = out["train"] + out["dev"]
    failures = []

    def gate(name, ok, detail):
        print(f"{name} {'PASS' if ok else 'FAIL'} -- {detail}")
        if not ok:
            failures.append(name)

    # G1 (D3-style): every gold row's quote is verbatim in ITS record's
    # user passage (the engine's own predicate, never a re-implementation).
    g1 = 0
    for r in all_recs:
        passage = r["passage"]
        for e in r["events"]:
            if quote_grid_span(passage, str(e.get("quote") or "").strip()) \
                    is None:
                g1 += 1
    gate("G1", g1 == 0, f"{g1} row quote(s) not verbatim in their passage "
                        f"(expect 0)")

    # G2 (D5 prompt fidelity): the messages are the CURRENT engine's
    # strings -- system == system_prompt(eventive_verbs(store)), user ==
    # _TEMPLATE filled from the record's window.
    g2 = sum(1 for r in all_recs
             if r["messages"][0]["content"] != sysmsg
             or r["messages"][1]["content"] != _TEMPLATE.format(
                 series=a.series, page=r["page"],
                 section=(r.get("section") or ""), passage=r["passage"]))
    gate("G2", g2 == 0, f"{g2}/{len(all_recs)} record(s) off the current "
                        f"prompt (PROMPT_VERSION {PROMPT_VERSION}, "
                        f"{len(ev_verbs)} eventive verbs; expect 0)")

    # G3: no holdout page (the U-WP2 rule, split by page never by row).
    leak_pages = {r["page"] for r in all_recs} & holdout
    gate("G3", not leak_pages,
         f"{len(leak_pages)} record page(s) in the holdout (expect 0)"
         + (f"; e.g. {sorted(leak_pages)[:3]}" if leak_pages else ""))

    # G4: no test-gold window id, no drift-probe id (the labeler and the
    # evaluator stay blind to the student's test set).
    g4 = [r["id"] for r in all_recs if r["id"] in test_ids or r["id"] in probe_ids]
    gate("G4", not g4, f"{len(g4)} test-gold/probe window id(s) in the set "
                        f"(expect 0)" + (f"; e.g. {g4[:3]}" if g4 else ""))

    # G5: ids unique within each file, the splits page-disjoint.
    g5 = (len({r["id"] for r in out["train"]}) == len(out["train"])
          and len({r["id"] for r in out["dev"]}) == len(out["dev"])
          and not set(r["page"] for r in out["train"])
          & set(r["page"] for r in out["dev"]))
    gate("G5", g5, f"train {len(out['train'])} / dev {len(out['dev'])} "
                   f"records, ids unique, splits page-disjoint")

    receipt = {
        "series": a.series, "gen": CURRENT_GEN,
        "prompt_version": PROMPT_VERSION,
        "eventive_verbs": sorted(ev_verbs),
        "sources": {
            "gold600": str(g600_path), "pilot": str(pilot_path),
            "kept_reexpressed": dict(src_stat),
        },
        "records": len(all_recs),
        "train_windows": len(out["train"]), "dev_windows": len(out["dev"]),
        "empty_windows": n_empty,
        "empty_share": round(n_empty / len(all_recs), 4) if all_recs else 0,
        "empty_share_train": round(
            sum(1 for r in out["train"] if not r["events"]) / len(out["train"]), 4)
        if out["train"] else 0,
        "verb_histogram": dict(sorted(verb_hist.items(),
                                      key=lambda kv: (-kv[1], kv[0]))),
        "pages": len(pages),
        "train_pages": len(train_pages), "dev_pages": len(dev_pages),
        "dev_seed": DEV_SEED, "dev_frac": DEV_FRAC,
        "conflicts": conflicts,
        "exclusions": {
            "holdout_pages": len(holdout),
            "test_gold_window_ids": len(test_ids),
            "probe_ids": len(probe_ids),
            "claimed_windows": len(claimed),
            "source_records": excl,
            "store_drift": drift,
        },
        "earned_empties": {
            "per_source": empty_tally, "kept": len(empty_ids),
            "rule": "rekey_testgold.empty_candidates over kept+reexpressed "
                    "(fully inside the original annotated passage, no row, "
                    "not claimed by any record, no test id, no probe id, "
                    "no holdout page)",
        },
        "out": [str(out_dir / f"{n}.jsonl") for n in ("train", "dev")]
        + ([] if a.dry_run else [str(out_dir / "receipt.json")]),
        "note": "messages are the exact production prompt (decision 6): "
                "the student is a drop-in for the extractor's own call; "
                "reread/straddle records are excluded (contaminated "
                "empties, the 35B re-read owns them)",
    }
    if not a.dry_run:
        (out_dir / "receipt.json").write_text(
            json.dumps(receipt, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    if failures:
        sys.exit(f"set gate FAILED: {', '.join(failures)}")


if __name__ == "__main__":
    sys.exit(main())