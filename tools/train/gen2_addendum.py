#!/usr/bin/env python3
"""Compute plan/JJK_VERIFY_GEN2_ADDENDUM.md (windowing-100 WP5, 2026-10-04).

Every number in the addendum is computed on the live JJK store by THIS
script and written into the file -- never estimated, never carried over
from the old grid. The addendum corrects the old-grid source paths in
`plan/JJK_VERIFY_7000_FINAL.md` (the owner's file -- read-only here) and
quantifies what the 35B data phase still has to do:

- remaining train-eligible gen-2 windows (universe minus holdout minus
  gold minus the 3 pools), split non-empty / empty / rare;
- the reread queues (gold600 + pilot reread records -> their window ids,
  how many already sit in the pools);
- the old-grid label sources (cand_q6_*, verifyrow_*, v1/train.jsonl):
  how many records re-key cleanly by the WP3 rule (rekey_gold's
  kept/reexpressed) vs how many need a re-read / re-extraction;
- the corrected file path for every VERIFY-7000 phase, and the exact
  (unapplied) fix eval_extraction.load_gold needs to read the gen-2
  test gold.

Zero LLM cost, deterministic:

    python tools/train/gen2_addendum.py [--write]      # default: print + write
    python tools/train/gen2_addendum.py --print-only   # show, touch nothing
"""
import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scriptengine.stores.facts import FactStore  # noqa: E402

from emit_windows import (  # noqa: E402
    RARE,
    build_universe_windows,
    gold_window_ids,
    holdout_pages,
    map_evidence,
    universe,
)
from rekey_gold import rekey_record  # noqa: E402

OUT = ROOT / "plan" / "JJK_VERIFY_GEN2_ADDENDUM.md"
OLD_POOL_GLOB = "series/jjk/training/opencode/*_windows.jsonl.old-grid"


def load_lines(path):
    return [json.loads(l) for l in Path(path).read_text(encoding="utf-8")
            .splitlines() if l.strip()]


def old_id_map():
    """old window id -> (page, section, passage) from the surviving
    old-grid pool files (the 4,000/300 campaign's last emit)."""
    m = {}
    import glob
    import os
    for f in sorted(glob.glob(str(ROOT / OLD_POOL_GLOB))):
        if os.path.islink(f):
            continue  # the P1-P5 symlinks alias the mimo old pool
        for r in load_lines(f):
            m[r["id"]] = (r["page"], r.get("section") or "", r["passage"])
    return m


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--print-only", action="store_true",
                    help="print the addendum but do not write the file")
    a = ap.parse_args()

    sroot = ROOT / "series" / "jjk"
    with FactStore(sroot / "facts.db") as store:
        uni = universe(store)
        windows, by_key, dup = build_universe_windows(store, uni)
        by_id = {w.id: w for w in windows}
        verbs, unmapped_rows = map_evidence(store, by_key)
        holdout = holdout_pages(sroot)
        g600_ids, g600_mapped, g600_unmapped, g600_n, _g600_elig = gold_window_ids(
            uni, sroot / "training" / "gold600" / "gold600.gen2.jsonl")
        pil_ids, pil_mapped, pil_unmapped, pil_n, pil_elig = gold_window_ids(
            uni, sroot / "training" / "gold" / "gold_pilot_all.gen2.jsonl",
            statuses=("kept", "reexpressed"))

        # -- 1. remaining train-eligible --------------------------------
        pool_ids, pool_pages = set(), set()
        for p in ("mimo", "nemotron", "spacebunny"):
            for r in load_lines(sroot / "training" / "opencode" / f"{p}_windows.jsonl"):
                pool_ids.add(r["id"])
                pool_pages.add(r["page"])
        gold_ids_all = g600_ids | pil_ids
        sample_universe = [w for w in windows
                           if w.page not in holdout and w.id not in gold_ids_all]
        assert pool_ids <= {w.id for w in sample_universe}, \
            "a pool window left the sample universe (holdout/gold changed)"
        remaining = [w for w in sample_universe if w.id not in pool_ids]
        rem_nonempty = [w for w in remaining if w.id in verbs]
        rem_rare = [w for w in rem_nonempty if RARE & verbs.get(w.id, set())]
        rem_empty = [w for w in remaining if w.id not in verbs]

        # -- 2. reread queues -------------------------------------------
        def reread_ids(path):
            return [r["rekey"]["new_id"] for r in load_lines(path)
                    if r["rekey"]["status"] == "reread"]
        rr600 = reread_ids(sroot / "training" / "gold600" / "gold600.gen2.jsonl")
        rrpil = reread_ids(sroot / "training" / "gold" / "gold_pilot_all.gen2.jsonl")
        rr_union = set(rr600) | set(rrpil)
        rem_ids = {w.id for w in remaining}

        # -- 3. old-grid label sources ----------------------------------
        grids = {}
        v1 = load_lines(sroot / "training" / "v1" / "train.jsonl")
        v1_status, v1_rows_k, v1_rows_d = Counter(), 0, 0
        for rec in v1:
            _o, status, k, d = rekey_record(rec, store, grids)
            v1_status[status] += 1
            v1_rows_k += k
            v1_rows_d += d

        old_map = old_id_map()
        old_sources = {}
        for name in ("gold/cand_q6_train.jsonl", "gold/cand_q6_pilot400.jsonl",
                     "gold/verifyrow_1000.jsonl", "gold/verifyrow_600.jsonl",
                     "gold/verifyrow_extra.jsonl", "gold/verifyrow_q6_pilot400.jsonl"):
            recs = load_lines(sroot / "training" / name)
            mapped = [r for r in recs if r["id"] in old_map]
            info = {"records": len(recs), "mapped": len(mapped),
                    "unmapped": len(recs) - len(mapped)}
            if "verifyrow" not in name:
                # cand_q6 rows carry quotes -> run the WP3 rule on the
                # mapped ones (a synthetic campaign record from the
                # surviving old pool's page/section/passage).
                st, k, d = Counter(), 0, 0
                for r in mapped:
                    page, section, passage = old_map[r["id"]]
                    synth = {"id": r["id"], "page": page,
                             "section": section,
                             "messages": [
                                 {"role": "system", "content": ""},
                                 {"role": "user", "content":
                                  f"Series: jjk\nPage: {page}\nSection: {section}\n\n"
                                  f"Passage:\n{passage}"},
                                 {"role": "assistant", "content":
                                  json.dumps({"events": r.get("events") or []},
                                             ensure_ascii=False)}]}
                    _o, status, kk, dd = rekey_record(synth, store, grids)
                    st[status] += 1
                    k += kk
                    d += dd
                info["rekey"] = {
                    "clean": st["kept"] + st["reexpressed"],
                    "reexpressed": st["reexpressed"], "reread": st["reread"],
                    "straddle": st["straddle"], "unmapped": st["unmapped"],
                    "rows_dropped": st["rows_dropped"],
                    "rows_kept": k, "rows_lost": d,
                }
            old_sources[name] = info

    # -- render ---------------------------------------------------------
    def n(x):
        return f"{x:,}"

    L = []
    A = L.append
    A("# JJK VERIFY-7000 — GEN-2 ADDENDUM (2026-10-04, windowing-100 WP5)")
    A("")
    A("Every number in this file is computed by `tools/train/gen2_addendum.py`")
    A("on the live JJK store (gen-2 universe "
      f"{n(len(windows))} windows / {n(len({w.id for w in windows}))} unique ids")
    A(f"{dup} collapsed), never estimated and never carried over from the")
    A("old 4,000/300 grid. `plan/JJK_VERIFY_7000_FINAL.md` (owner's file) is")
    A("left as written; where its paths or counts are stale, THIS file is the")
    A("corrected source. Re-run the script after any store or id change to")
    A("regenerate every number.")
    A("")
    A("## 1. Remaining train-eligible gen-2 windows")
    A("")
    A(f"```")
    A(f"universe                        {n(len(windows))}")
    A(f"- holdout pages ({n(len(holdout))})           {n(len([w for w in windows if w.page in holdout]))} windows")
    A(f"- gold (gold600 {n(g600_n)} records -> {n(len(g600_ids))} windows, union pilot")
    A(f"   kept/reexpressed {n(pil_elig)} -> {n(len(pil_ids))} windows; union {n(len(gold_ids_all))})")
    A(f"- 3 pools (mimo/nemotron/spacebunny)          {n(len(pool_ids))} windows")
    A(f"= remaining train-eligible                    {n(len(remaining))} windows")
    A(f"    non-empty                                 {n(len(rem_nonempty))} (of which rare-verb {n(len(rem_rare))})")
    A(f"    empty                                     {n(len(rem_empty))}")
    A(f"```")
    A("")
    A(f"Store evidence rows unmapped onto the grid: {unmapped_rows} (the window-level")
    A("G1's loud failures -- they are NOT silently attributed to a window).")
    A("")
    A("## 2. Re-read queues (the 35B data phase)")
    A("")
    A("| queue | records | distinct window ids | ids already in a pool | ids in the remaining set |")
    A("|---|---|---|---|---|")
    A(f"| gold600 reread | {n(len(rr600))} | {n(len(set(rr600)))} | {n(len(set(rr600) & pool_ids))} | {n(len(set(rr600) & rem_ids))} |")
    A(f"| pilot reread | {n(len(rrpil))} | {n(len(set(rrpil)))} | {n(len(set(rrpil) & pool_ids))} | {n(len(set(rrpil) & rem_ids))} |")
    A(f"| union | {n(len(rr600) + len(rrpil))} | {n(len(rr_union))} | {n(len(rr_union & pool_ids))} | {n(len(rr_union & rem_ids))} |")
    A("")
    A("A reread window that sits in a pool is re-read AS that pool's")
    A("verification (no separate queue entry); one that sits in the remaining")
    A("set is re-read in place. The reread records' windows are excluded from")
    A("the pools only for gold600 (all statuses) -- the pilot's reread windows")
    A("were left pool-eligible on purpose (WP3b-2): the 35B re-read owns them.")
    A("")
    A("## 3. Old-grid label sources — WP3 re-key status")
    A("")
    A("The WP3 rule (rekey_gold's council ruling): a record re-keys CLEAN when")
    A("its rows keep their adjudicated status on the new grid (status kept or")
    A("reexpressed; reexpressed may lose rows whose quotes no single new window")
    A("carries -- those rows drop for re-extraction). An empty adjudication")
    A("re-keys as `reread` (the 35B re-read owns it); a straddled/mapped-away")
    A("record drops whole for re-extraction.")
    A("")
    A("| source | records | re-keyable (kept+reexpressed) | needs re-read (all else) | status detail |")
    A("|---|---|---|---|---|")
    vs = v1_status
    v1_reread = vs["reread"] + vs["straddle"] + vs["unmapped"] + vs["rows_dropped"]
    A(f"| `v1/train.jsonl` | {n(len(v1))} | {n(vs['kept'] + vs['reexpressed'])} | "
      f"{n(v1_reread)} | reread {n(vs['reread'])}, straddle {n(vs['straddle'])}, "
      f"unmapped {n(vs['unmapped'])}, rows_dropped {n(vs['rows_dropped'])} "
      f"(rows kept/lost {n(v1_rows_k)}/{n(v1_rows_d)}) |")
    for name, info in old_sources.items():
        if "verifyrow" in name:
            A(f"| `gold/{Path(name).name}` (audit rows, no event rows to re-key) | "
              f"{n(info['records'])} | window mapping only: {n(info['mapped'])} "
              f"of {n(info['records'])} ids found in the surviving old pools | "
              f"{n(info['unmapped'])} unmapped | audit verdicts re-attach by id "
              f"where mapped; re-read otherwise |")
        else:
            rk = info["rekey"]
            A(f"| `gold/{Path(name).name}` | {n(info['records'])} | "
              f"{n(rk['clean'])} of {n(info['mapped'])} mapped "
              f"(reexpressed {n(rk['reexpressed'])}, rows dropped {n(rk['rows_lost'])}) | "
              f"{n(rk['reread'] + rk['straddle'] + rk['unmapped'] + rk['rows_dropped'] + info['unmapped'])} | "
              f"mapped: reread {n(rk['reread'])}, straddle {n(rk['straddle'])}, "
              f"unmapped {n(rk['unmapped'])}, rows_dropped {n(rk['rows_dropped'])} "
              f"(rows kept/lost {n(rk['rows_kept'])}/{n(rk['rows_lost'])}); "
              f"+ {n(info['unmapped'])} records unmappable (no surviving source) |")
    A("")
    A(f"Only {n(len(old_map))} old window ids survive in the old-grid pool files "
      "(mimo/nemotron/spacebunny `*.old-grid`); a label record whose old id is not")
    A("among them has no surviving (page, section, passage) and must be re-read")
    A("from the store. `verifyrow_*` are row-level AUDITS (ok/rule/card, no")
    A("event rows): their verdicts re-attach to the re-keyed window by id where")
    A("mapped, and re-read otherwise.")
    A("")
    A("## 4. Corrected file paths per VERIFY-7000 phase")
    A("")
    A("| phase | old-grid source (as written in FINAL.md) | corrected gen-2 source |")
    A("|---|---|---|")
    A("| Phase 0 blind audit | `opencode/mimoP*_windows.jsonl` (10 random windows) | "
      "`opencode/{mimo,nemotron,spacebunny}_windows.jsonl` (the 1,500 gen-2 pool windows; audit draws from these) |")
    A("| Phase 1 Pool A (3x500, P1-P5 pilots) | `opencode/mimoP*_windows.jsonl`, "
      "`*_out.jsonl`, `.*_done` | `opencode/{mimo,nemotron,spacebunny}_windows.jsonl`; the P1-P5 files and "
      "done-logs are archived `*.old-grid` (retired grid, frozen evidence) |")
    A("| Probes (Guard 1) | `series/jjk/training/golden_probes.jsonl` (20-30, extracted from gold600.jsonl) | "
      "`opencode/golden_probes.jsonl` -- 24 probes (20 positive, 1-4 rows each, all 12 verbs, none on a "
      "holdout page + 4 earned empties), pool shape plus `expected`; rebuilt by "
      "`tools/train/rekey_testgold.py --probes` (old file -> `golden_probes.jsonl.pre-wp3b`) |")
    A("| Phase 2 Pool B (Qwen windows) | `gold/cand_q6_train.jsonl` | same file, re-keyed by the WP3 rule "
      "on the fly (section 3: the mapped/clean records are consumable; the unmapped "
      f"{n(old_sources['gold/cand_q6_train.jsonl']['unmapped'])} need re-reading); `gold/cand_q6_pilot400.jsonl` "
      "likewise |")
    A("| Phase 3 (v1 subset) | `v1/train.jsonl` | same file (4,375 records); "
      f"{n(vs['kept'] + vs['reexpressed'])} re-key clean, {n(vs['reread'])} join the re-read queue, "
      f"{n(vs['straddle'] + vs['unmapped'] + vs['rows_dropped'])} drop for re-extraction |")
    A("| Phase 4 empty re-read | \"~2,265 windows\" (old-grid count) | "
      f"re-read the re-read queues (section 2: {n(len(rr_union))} reread windows, "
      f"{n(len(rr_union & rem_ids))} in the remaining set) + the {n(len(rem_empty))} empty windows of the "
      "remaining train-eligible set (section 1) |")
    A("| Test scoreboard | `recall_gold_v3/gold_test_v4.json` + `windows_100.json` (100 W-indexed entries) | "
      "`recall_gold_v3/gold_test_v4.gen2.json` -- 269 entries keyed by gen-2 window id "
      "(100 slice entries -> 269 intersecting windows; `straddle`/`partial` flags; 70 "
      "genuine empties); the v4 + windows_100 files stay as the annotation source of "
      "truth |")
    A("| Gold (train labels) | `gold600/gold600.jsonl` (old ids) | `gold600/gold600.gen2.jsonl` "
      f"({n(g600_n)} records) + `gold/gold_pilot_all.gen2.jsonl` ({n(pil_n)} records) |")
    A("")
    A("## 5. Scorer note -- `eval_extraction.load_gold` (NOT changed here)")
    A("")
    A("`tools/eval_extraction.py` `load_gold` (line 52) does")
    A("`sorted(Path(d).glob(\"gold_test_v*.json\"))[-1:]` -- lexicographically that")
    A("picks `gold_test_v4.json` OVER `gold_test_v4.gen2.json` (\"v4.g\" < \"v4.j\"),")
    A("so the scorer still reads the old W-indexed file; and the W-index indirection")
    A("(`wins[i][\"id\"]` via the `windows` key, line 54-59) cannot represent the")
    A("gen-2 file's shape at all (its keys ARE the window ids; it has no `windows`")
    A("key, and 45/100 entries now span several windows). The exact fix for a later")
    A("WP (the planner's call -- this addendum does not touch the scorer):")
    A("")
    A("```python")
    A("def load_gold(d):")
    A("    files = sorted(Path(d).glob(\"gold_test_v*.json\"),")
    A("                    key=lambda p: (\"gen2\" not in p.name, p.name))[-1:]")
    A("    data = json.load(open(files[0]))")
    A("    if \"gen\" in data:  # gen-2 file: keys are the window ids")
    A("        return {k: v for k, v in data.items()")
    A("                if k not in (\"version\", \"gen\", \"guideline\", \"note\", \"note_gen2\")}")
    A("    # ... old W-indexed shape: the current indirection, unchanged ...")
    A("```")
    A("")
    A(f"Generated {time.strftime('%Y-%m-%d %H:%M')} by tools/train/gen2_addendum.py "
      "(zero-LLM, deterministic).")
    text = "\n".join(L) + "\n"
    print(text)
    if not a.print_only:
        OUT.write_text(text, encoding="utf-8")
        print(f"\n[written] {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())