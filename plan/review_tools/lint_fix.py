#!/usr/bin/env python3
"""Mechanical, rule-decided fixes of the final big-v2 rows (2026-10-14, after lint_v2.py).

Each transform is one the catalog already decides without reading the window:
  M1 `X|ordered|Y` is actual (handoff 2026-10-14 §3.1; 517 rows carried modality `ordered`)
  M2 a fact twin of an event with the same ends (A89: helped/assisted/protected~saved, attacked~fought,
     kidnapped~captured, greeted/contacted~met)
  M3 asserted_by on an actual row when the asserter IS the subject (speech acts are actual, no asserted_by);
     other asserters are left for reading
  M4 duplicate facts/tags; a truly symmetric fact (friend/rival/married/dated/sibling/allied) in both directions -> the first row
  M6 a speech act (other_verb told/said/claimed/...) is actual with no asserter, when the asserter is the speaker
  M5 kinship one direction (`A|child_of|B` -> `B|parent_of|A`); `married_to` -> `married` (both symmetric)
The new record goes through the same three gates as `rv.sh fix`; a window whose gate refuses anything is
NOT written and is printed (it belongs to the reading list). Append-only, latest record wins.

    lint_fix.sh [--dry]
"""
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/tools/train")
import big_review_v2 as bv  # noqa: E402

TWIN = {"helped": "saved", "assisted": "saved", "protected": "saved", "attacked": "fought",
        "kidnapped": "captured", "greeted": "met", "contacted": "met"}


SPEECH = {"told", "said", "says", "asked", "asking", "explained", "noted", "stated", "stating", "replied", "responded",
          "claimed", "claiming", "insisted", "declared", "announced", "informed", "admitted", "confessed", "suggested",
          "accused", "telling", "saying", "explaining", "noting", "boasted", "bragged", "mentioned"}
# fact_gate.SYMMETRIC also lists helped/assisted/protected/contacted/warned, which have a direction (A136)
TRUE_SYM = {"friend_of", "rival_of", "married", "dated", "sibling_of", "allied_with"}


def transform(rec):
    ev = rec["events"]
    evk = {(e["subject"], e["verb"], e["object"]) for e in ev}
    facts, notes = [], set()
    for f in rec["facts"]:
        f = dict(f)
        rel, mod = f.get("relation"), f.get("modality") or "actual"
        if rel == "ordered" and mod != "actual":
            f["modality"], f["asserted_by"] = "actual", None
            notes.add("M1")
        tw = TWIN.get(rel)
        # met/fought are symmetric events, so their twins match either direction; saved/captured keep direction
        # only an ACTUAL fact twins an event: an attempted attack next to the fight is a separate, later act (b3695,
        # recon C403; lint_v2's A89 check has the same condition)
        if tw and mod == "actual" and ((f["subject"], tw, f["object"]) in evk or (tw in bv.SYM and (f["object"], tw, f["subject"]) in evk)):
            notes.add("M2")
            continue
        # M6 (2026-10-14): a speech act is actual with no asserter (recon convention); 4,163 speech-verb other_verb
        # rows were actual, ~670 in 560 windows were `claimed` asserted by the speaker. Rows asserted by someone else stay.
        if rel == "other_verb" and (f.get("object") or "").lower() in SPEECH and mod == "claimed" \
                and f.get("asserted_by") in (None, f["subject"]):
            f["modality"], f["certainty"], f["asserted_by"] = "actual", "stated", None
            notes.add("M6")
        if (f.get("modality") or "actual") == "actual" and f.get("asserted_by") and f["asserted_by"] == f["subject"]:
            f["asserted_by"] = None
            notes.add("M3")
        if rel == "child_of" and f.get("object"):
            f["subject"], f["object"], f["relation"] = f["object"], f["subject"], "parent_of"
            notes.add("M5")
        if rel == "married_to":
            f["relation"] = "married"
            notes.add("M5")
        key = (f["subject"], f["relation"], f["object"], f.get("modality"))
        if any((g["subject"], g["relation"], g["object"], g.get("modality")) == key for g in facts):
            notes.add("M4")
            continue
        if f["relation"] in TRUE_SYM and f.get("object"):
            rev = (f["object"], f["relation"], f["subject"], f.get("modality"))
            if any((g["subject"], g["relation"], g["object"], g.get("modality")) == rev for g in facts):
                notes.add("M4")
                continue
        facts.append(f)
    tags, seen = [], set()
    for t in rec["tags"]:
        k = (t.get("tag"), t.get("quote"))
        if k in seen:
            notes.add("M4")
            continue
        seen.add(k)
        tags.append(t)
    return facts, tags, sorted(notes)


def main():
    dry = "--dry" in sys.argv
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    ids, a2, pas, wikis = bv.order(), bv.audit2(), bv.br.passages(), {}
    n, refused, counts = 0, [], {}
    out = [] if dry else open(bv.AUDIT2, "a")
    for b, wid in enumerate(ids, 1):
        rec = a2[wid]
        facts, tags, notes = transform(rec)
        if not notes:
            continue
        w = pas[wid]
        series = rec.get("series") or "marvel"
        wiki = wikis.setdefault(series, vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db")))
        fk, fd = ls.fact_gate_keep([dict(f) for f in facts], w, wiki)
        tk, td = ls.tag_gate_keep([dict(t) for t in tags], w)
        if fd or td:
            refused.append((b, [(d.get("subject"), d.get("relation"), d.get("object"), d.get("why")) for d in fd]
                            + [(d.get("tag"), d.get("why")) for d in td]))
            continue
        for x in notes:
            counts[x] = counts.get(x, 0) + 1
        n += 1
        if not dry:
            out.write(json.dumps({"id": wid, "b": b, "series": series, "page": rec.get("page"),
                                  "events": rec["events"], "facts": fk, "tags": tk,
                                  "why": "lint " + "+".join(notes)}, ensure_ascii=False) + "\n")
    print(f"{'would write' if dry else 'wrote'} {n} records; windows per transform {counts}; refused {len(refused)}")
    for r in refused:
        print("REFUSED", r)


if __name__ == "__main__":
    main()
