#!/usr/bin/env python3
"""Build the reading lists for the lint pass (2026-10-14): every window a lint class flags that no rule can
decide, grouped so that overlapping windows (recon_lib.overlap_pairs) land in the same session, then split
between `app` and `term` by alternating groups (largest first).

    lint_work.sh build        -> big/lint/work_{app,term}.txt  ("b<n> CLASS,CLASS")
    lint_work.sh show B       -> the lint classes and rows for one window
"""
import re
import sys
from collections import defaultdict

sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools")
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools/recon")
import lint_v2  # noqa: E402
import recon_lib  # noqa: E402

bv = lint_v2.bv
LINT = bv.BIG / "lint"
READ = {"E_met_and_fight_same_pair", "F_A115_clause_object", "F_A125_copula", "F_A134_attempt_word",
        "F_A146_died_other_verb", "F_alias_variant_also_known_as", "F_alias_variant_codename_of",
        "F_alias_variant_real_name_of", "F_actual_with_asserter", "F_self_pair", "E_self_pair",
        "F_kinship_both_dirs", "F_married_twins", "F_symmetric_both_dirs", "E_symmetric_both_dirs",
        "E_quote_not_verbatim", "F_quote_not_verbatim", "T_quote_not_verbatim", "F_A89_event_twin",
        "F_duplicate", "E_duplicate", "F_ordered_rel_nonactual", "name_short_and_full", "E_A145_same_sentence",
        "F_became", "F_kidnapped_fact"}
PLACEISH = re.compile(r"\b(?:Residence|Tower|Mansion|Headquarters|HQ|Industries|Building|Castle|Island|City|Base|"
                      r"Academy|School|Prison|Platoon|Corps|Labs?|Enterprises|Foundation|Hall|House|Street|"
                      r"Avenue|Park|Station|Planet|World|Realm|Dimension|construct|armor|of)\b|^(?:Earth|New|Fort)\b")


def window_classes(b, rec, text):
    out = lint_v2.checks(b, rec["id"] if "id" in rec else None, rec, text)
    # name_short_and_full: keep person-like pairs only, and not two relatives sharing a surname
    keep = []
    for x, longer in out.get("name_short_and_full", []):
        longer = [y for y in longer if not PLACEISH.search(y)]
        if len(longer) == 1:
            keep.append((x, tuple(longer)))
    out["name_short_and_full"] = keep
    # A145 only where the fight and its end are quoted in the same sentence (separately stated fights stay)
    sents = bv.big_flags.sentences(text)
    sid = lambda q: next((i for i, s in enumerate(sents) if q and q in s), -1)
    ends = {}
    for e in rec["events"]:
        if e["verb"] in ("defeated", "killed") and e["object"]:
            ends.setdefault(frozenset((e["subject"], e["object"])), set()).add(sid(e["quote"]))
    out["E_A145_same_sentence"] = [lint_v2.ek(e) for e in rec["events"] if e["verb"] == "fought"
                                   and sid(e["quote"]) in ends.get(frozenset((e["subject"], e["object"])), ())]
    return {k: v for k, v in out.items() if v and k in READ}


def build():
    ids, a2, pas = bv.order(), bv.audit2(), bv.br.passages()
    flagged = {}
    for b, wid in enumerate(ids, 1):
        c = window_classes(b, a2[wid], pas[wid])
        if c:
            flagged[b] = sorted(c)
    _, sents = recon_lib.load()
    pairs = recon_lib.overlap_pairs(sents)
    parent = {}

    def find(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x
    for a, b in pairs:
        parent[find(a)] = find(b)
    groups = defaultdict(list)
    for b in flagged:
        groups[find(b)].append(b)
    # overlap partners of a flagged window come along (unflagged): the reader keeps them identical
    members = defaultdict(set)
    for b in list(parent) + list(flagged):
        members[find(b)].add(b)
    order_ = sorted(groups, key=lambda g: (-len(members[g]), min(groups[g])))
    load = {"app": 0, "term": 0}
    LINT.mkdir(exist_ok=True)
    files = {k: open(LINT / f"work_{k}.txt", "w") for k in load}
    for g in order_:
        who = min(load, key=load.get)
        ws = sorted(members[g])
        load[who] += len(ws)
        for b in ws:
            files[who].write(f"b{b} G{g} {','.join(flagged.get(b, ['partner']))}\n")
    for f in files.values():
        f.close()
    n = defaultdict(int)
    for cs in flagged.values():
        for c in cs:
            n[c] += 1
    print(f"flagged windows {len(flagged)}; groups {len(groups)}; load {load}")
    for c in sorted(n):
        print(f"  {c:30s} {n[c]}")


def show(b):
    ids, a2, pas = bv.order(), bv.audit2(), bv.br.passages()
    for k, v in window_classes(b, a2[ids[b - 1]], pas[ids[b - 1]]).items():
        print(f"LINT {k}: {v}")


if __name__ == "__main__":
    if sys.argv[1] == "build":
        build()
    else:
        show(int(sys.argv[2].lstrip("b")))
