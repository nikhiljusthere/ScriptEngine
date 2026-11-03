#!/usr/bin/env python3
"""Reading list for the gold v2 lint (stage 8a, 2026-11-03): lint_work's READ classes over the gold audit AS IT WILL
BE after the mechanical proposal (gold_v2/lint/proposed_mechanical.jsonl overlaid on the latest audit record), so
rule-decided rows are not read twice. Windows whose mechanical fix the gate refused join as `M_refused`; with
`--regate JSON` (lint_gold.sh --regate --json) the re-gate refusals join as REGATE_* classes.

Why not `BV2_SET=gold lint_work.sh build`: it reads only audit records (no proposal overlay) and writes
big/lint/work_{app,term}.txt, overwriting the big-set lists. This writes one file, gold_v2/lint/work_gold.txt,
same line format ("b<n> G<group> CLASS,CLASS"; `partner` = an unflagged overlap partner of a flagged window, read
with it so both stay identical), groups ordered largest first. Read a line with
`BV2_SET=gold bash plan/review_tools/pre27.sh show B` (shows the audit rows, not the overlay) plus
`lint_gold_work.sh show B` (the classes after the overlay).

    lint_gold_work.sh build [--regate JSON]
    lint_gold_work.sh show B
"""
import json
import os
import sys
from collections import defaultdict

os.environ["BV2_SET"] = "gold"
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools")
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools/recon")
import lint_gold  # noqa: E402
import lint_work  # noqa: E402
import recon_lib  # noqa: E402

bv = lint_work.bv
assert bv.GOLD and "gold_v2" in str(bv.AUDIT2), bv.AUDIT2
LINT = bv.BIG / "gold_v2" / "lint"
# F_A89_event_twin / F_duplicate / F_ordered_rel_nonactual are rule classes: after the overlay they remain only where
# the M-rule does not reach (lint_v2's twin table has left_group~departed and reverse twins that lint_fix's lacks)
READ = lint_work.READ


def records():
    ids, a2, pas = bv.order(), bv.audit2(), bv.br.passages()
    recs = {**{r["id"]: r for r in bv.jl(bv.V2)}, **a2}
    for p in bv.jl(LINT / "proposed_mechanical.jsonl"):
        if p["id"] in a2:
            recs[p["id"]] = {**recs[p["id"]], "facts": p["facts"], "tags": p["tags"]}
    return ids, recs, pas, set(a2)


def classes(b, rec, text):
    return lint_work.window_classes(b, rec, text)


def build(regate_json):
    ids, recs, pas, reviewed = records()
    flagged = defaultdict(set)
    for b, wid in enumerate(ids, 1):
        flagged[b] |= set(classes(b, recs[wid], pas[wid]))
        if wid not in reviewed:
            flagged[b].add("UNREVIEWED")
    for r in bv.jl(LINT / "proposed_mechanical_refused.jsonl"):
        flagged[r["b"]].add("M_refused")
    # overlap partners with diverging rows on the shared sentences (lint_gold.overlap_lint; the gold set had no recon)
    for b, cl in lint_gold.overlap_lint(ids, recs).items():
        if "R_overlap_inconsistent" in cl:
            flagged[b].add("R_overlap_inconsistent")
    if regate_json:
        for k, v in json.load(open(regate_json)).items():
            if k.startswith("REGATE_"):
                for b, _ in v:
                    flagged[b].add(k)
    flagged = {b: sorted(c) for b, c in flagged.items() if c}
    _, sents = recon_lib.load()
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x
    for a, b in recon_lib.overlap_pairs(sents):
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for b in flagged:
        groups[find(b)].append(b)
    members = defaultdict(set)
    for b in list(parent) + list(flagged):
        members[find(b)].add(b)
    order_ = sorted(groups, key=lambda g: (-len(members[g]), min(groups[g])))
    LINT.mkdir(parents=True, exist_ok=True)
    n_lines = 0
    with open(LINT / "work_gold.txt", "w") as f:
        for g in order_:
            for b in sorted(members[g]):
                f.write(f"b{b} G{g} {','.join(flagged.get(b, ['partner']))}\n")
                n_lines += 1
    n = defaultdict(int)
    for cs in flagged.values():
        for c in cs:
            n[c] += 1
    print(f"flagged windows {len(flagged)}; groups {len(groups)}; lines (with partners) {n_lines} -> {LINT / 'work_gold.txt'}")
    for c in sorted(n):
        print(f"  {c:30s} {n[c]}")


def show(b):
    ids, recs, pas, _ = records()
    for k, v in classes(b, recs[ids[b - 1]], pas[ids[b - 1]]).items():
        print(f"LINT {k}: {v}")
    for k, v in lint_gold.overlap_lint(ids, recs).get(b, {}).items():
        print(f"LINT {k}: {v}  (partner, shared sentences, [(layer, rows only here, rows only there)])")


if __name__ == "__main__":
    if sys.argv[1:2] == ["build"]:
        a = sys.argv
        build(a[a.index("--regate") + 1] if "--regate" in a else None)
    elif sys.argv[1:2] == ["show"]:
        show(int(sys.argv[2].lstrip("b")))
    else:
        sys.exit(__doc__)
