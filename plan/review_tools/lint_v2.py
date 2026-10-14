#!/usr/bin/env python3
"""Corpus-wide lint of the FINAL big-v2 rows (latest big_audit_v2 record per id), 2026-10-14.

Owner: "If there are any more inconsistencies in the dataset, fix all of them and make the dataset
flawless, then only move to train the 9B model." Every check prints a count and the b-numbers it hits;
`--show CHECK` lists the rows. Run via lint.sh (main venv, SCRIPTENGINE_ROOT=main checkout).

    lint.sh [--regate] [--show CHECK] [--json OUT]
"""
import json
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/tools/train")
import big_review_v2 as bv  # noqa: E402

br = bv.br
KNOW = {"learned", "discovered", "revealed", "suspected", "forgot", "remembered"}
TWIN = {"helped": "saved", "assisted": "saved", "protected": "saved", "attacked": "fought",
        "kidnapped": "captured", "greeted": "met", "contacted": "met", "left_group": "departed"}
SYMF = bv.fact_gate.SYMMETRIC | {"met", "fought"}


def ek(e):
    return (e["subject"], e["verb"], e["object"])


def checks(b, wid, rec, text):
    ev, fa, tg = rec.get("events", []), rec.get("facts", []), rec.get("tags", [])
    out = defaultdict(list)
    for e in ev:
        if not e.get("quote") or e["quote"] not in text:
            out["E_quote_not_verbatim"].append(ek(e))
        if e["subject"] == e["object"]:
            out["E_self_pair"].append(ek(e))
        if "\xa0" in (e.get("quote") or ""):
            out["nbsp_quote"].append(ek(e))
    for f in fa:
        k = (f.get("subject"), f.get("relation"), f.get("object"), f.get("modality"), f.get("asserted_by"))
        q = f.get("quote") or ""
        if not q or q not in text:
            out["F_quote_not_verbatim"].append(k)
        if f.get("subject") == f.get("object") and f.get("object"):
            out["F_self_pair"].append(k)
        mod = f.get("modality") or "actual"
        if f.get("relation") == "ordered" and mod != "actual":
            out["F_ordered_rel_nonactual"].append(k)
        if mod == "actual" and f.get("asserted_by"):
            out["F_actual_with_asserter"].append(k)
        if mod != "actual" and not f.get("asserted_by"):
            out["F_nonactual_no_asserter"].append(k)
        if f.get("relation") == "other_verb" and (f.get("object") or "").lower() in (
                "tried", "attempted", "attempt", "trying", "attempting", "try"):
            out["F_A134_attempt_word"].append(k)
        if f.get("relation") == "other_verb" and (f.get("object") or "").lower() in (
                "was", "were", "is", "be", "been", "became", "had", "has", "should", "would", "could"):
            out["F_A125_copula"].append(k)
        if f.get("relation") in KNOW and f.get("object") and " " in f["object"] and f["object"][:1].islower():
            out["F_A115_clause_object"].append(k)
        if f.get("relation") in ("parent_of", "child_of"):
            out["F_kinship_" + f["relation"]].append(k)
        if f.get("relation") in ("married", "married_to"):
            out["F_" + f["relation"]].append(k)
        if f.get("relation") in ("codename_of", "also_known_as", "real_name_of"):
            out["F_alias_variant_" + f["relation"]].append(k)
        if f.get("relation") == "other_verb" and (f.get("object") or "").lower() in ("died", "perished", "die"):
            if mod == "actual":
                out["F_A146_died_other_verb"].append(k)
        tw = TWIN.get(f.get("relation"))
        if tw and mod == "actual" and any(ek(e) in ((f.get("subject"), tw, f.get("object")), (f.get("object"), tw, f.get("subject")))
                      for e in ev):
            out["F_A89_event_twin"].append(k)
        if "\xa0" in q:
            out["nbsp_quote"].append(k)
    for t in tg:
        if not t.get("quote") or t["quote"] not in text:
            out["T_quote_not_verbatim"].append((t.get("tag"), (t.get("quote") or "")[:40]))
    # duplicates
    c = Counter(ek(e) for e in ev)
    out["E_duplicate"] += [k for k, n in c.items() if n > 1]
    sym = Counter(tuple(sorted((e["subject"], e["object"] or ""))) + (e["verb"],) for e in ev if e["verb"] in SYMF)
    out["E_symmetric_both_dirs"] += [k for k, n in sym.items() if n > 1]
    cf = Counter((f.get("subject"), f.get("relation"), f.get("object"), f.get("modality")) for f in fa)
    out["F_duplicate"] += [k for k, n in cf.items() if n > 1]
    symf = Counter(tuple(sorted((f.get("subject") or "", f.get("object") or ""))) + (f.get("relation"), f.get("modality"))
                   for f in fa if f.get("relation") in SYMF)
    out["F_symmetric_both_dirs"] += [k for k, n in symf.items() if n > 1]
    kin = {(f.get("subject"), f.get("relation"), f.get("object")) for f in fa}
    for s, r, o in kin:
        if r == "parent_of" and (o, "child_of", s) in kin:
            out["F_kinship_both_dirs"].append((s, r, o))
        if r in ("married", "married_to") and ({(s, "married", o), (s, "married_to", o), (o, "married", s),
                                                (o, "married_to", s)} - {(s, r, o)}) & kin:
            out["F_married_twins"].append((s, r, o))
    ct = Counter((t.get("tag"), t.get("quote")) for t in tg)
    out["T_duplicate"] += [k for k, n in ct.items() if n > 1]
    # A145: fought next to defeated/killed for the same pair
    pairs = {frozenset((e["subject"], e["object"])) for e in ev if e["verb"] in ("defeated", "killed") and e["object"]}
    out["E_A145_fought_and_defeat"] += [ek(e) for e in ev if e["verb"] == "fought" and frozenset((e["subject"], e["object"])) in pairs]
    fpairs = {frozenset((e["subject"], e["object"])) for e in ev if e["verb"] in ("fought", "defeated", "killed") and e["object"]}
    out["E_met_and_fight_same_pair"] += [ek(e) for e in ev if e["verb"] == "met" and frozenset((e["subject"], e["object"])) in fpairs]
    # a fact quote that is also an event row's quote with the same pair = possible twin
    # names: one person, two forms (short form of another end in the same window)
    ends = {x for e in ev for x in (e["subject"], e["object"]) if x} | \
           {x for f in fa for x in (f.get("subject"), f.get("object"), f.get("asserted_by")) if x}
    aliased = {x for f in fa if f.get("relation") in ("alias_of", "disguise_as", "revealed_as", "transformed_into",
                                                         "codename_of", "also_known_as", "real_name_of", "became")
               for x in (f.get("subject"), f.get("object"))}
    for x in ends:
        if " " in x or not x[:1].isupper() or x in aliased:
            continue
        longer = [y for y in ends if y != x and y not in aliased and re.search(r"(?:^|\s)" + re.escape(x) + r"(?:$|\s)", y)
                  and y.split()[0] not in ("Earth", "New")]
        if longer:
            out["name_short_and_full"].append((x, tuple(sorted(longer))))
    return out


def main():
    a = sys.argv[1:]
    show = a[a.index("--show") + 1] if "--show" in a else None
    ids = bv.order()
    a2 = bv.audit2()
    pas = br.passages()
    total, hits = Counter(), defaultdict(list)
    missing = [b for b, i in enumerate(ids, 1) if i not in a2]
    for b, wid in enumerate(ids, 1):
        rec = a2.get(wid)
        if not rec:
            continue
        for k, rows in checks(b, wid, rec, pas[wid]).items():
            if rows:
                total[k] += len(rows)
                hits[k].append((b, rows))
    if "--regate" in a:
        regate(ids, a2, pas, total, hits)
    print(f"windows {len(ids)} | with audit record {len(ids) - len(missing)} | missing {len(missing)} {missing[:10]}")
    for k in sorted(total):
        print(f"{k:32s} rows {total[k]:6d}  windows {len(hits[k]):5d}  e.g. b{[h[0] for h in hits[k][:8]]}")
    if show:
        for b, rows in hits.get(show, []):
            print(f"b{b}", rows)
    if "--json" in a:
        json.dump({k: v for k, v in hits.items()}, open(a[a.index("--json") + 1], "w"), default=list)


def regate(ids, a2, pas, total, hits):
    """Re-run today's gates on every final record (refusals = rows the current gates would not store)."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    wikis = {}
    for b, wid in enumerate(ids, 1):
        rec = a2.get(wid)
        if not rec:
            continue
        w = pas[wid]
        series = rec.get("series") or "marvel"
        wiki = wikis.setdefault(series, vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db")))
        evs = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in rec.get("events", [])]
        kept, dropped = ls.gate(evs, w, wiki)
        if dropped or len(kept) != len(evs):
            total["REGATE_events"] += max(len(dropped), 1)
            hits["REGATE_events"].append((b, [(d.get("subject"), d.get("verb"), d.get("object"), d.get("why")) for d in dropped]
                                          or [f"kept {len(kept)}/{len(evs)}"]))
        fk, fd = ls.fact_gate_keep([dict(f) for f in rec.get("facts", [])], w, wiki)
        if fd:
            total["REGATE_facts"] += len(fd)
            hits["REGATE_facts"].append((b, [(d.get("subject"), d.get("relation"), d.get("object"), d.get("why")) for d in fd]))
        old = Counter((f.get("subject"), f.get("relation"), f.get("object"), f.get("modality"), f.get("asserted_by"))
                      for f in rec.get("facts", []))
        new = Counter((f.get("subject"), f.get("relation"), f.get("object"), f.get("modality"), f.get("asserted_by"))
                      for f in fk)
        if not fd and old != new:
            total["REGATE_facts_changed"] += 1
            hits["REGATE_facts_changed"].append((b, [("-",) + k for k in old - new] + [("+",) + k for k in new - old]))
        tk, td = ls.tag_gate_keep([dict(t) for t in rec.get("tags", [])], w)
        if td:
            total["REGATE_tags"] += len(td)
            hits["REGATE_tags"].append((b, [(d.get("tag"), d.get("why")) for d in td]))


if __name__ == "__main__":
    main()
