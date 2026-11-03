#!/usr/bin/env python3
"""Mechanical lint fixes (M1-M6, lint_fix.transform) for the REVIEWED gold v2 audit -- proposal first, apply later
(stage 8a, 2026-11-03).

Why a separate tool: `BV2_SET=gold lint_fix.sh` was written before the gold review (2026-10-14). It skips every
window that has a gold audit record and rewrites gold_labels_v2.jsonl for the rest, so on the reviewed gold set it
does nothing useful (and without --dry it would rewrite the label base). Here the base is the latest gold audit
record, the transforms are lint_fix.transform unchanged, and each new record goes through the same fact and tag
gates as `rv.sh fix`.

    lint_gold_fix.sh build            -> gold_v2/lint/proposed_mechanical.jsonl (+ _refused.jsonl, _diff.txt); no audit write
    lint_gold_fix.sh build --raw-m2   -> the same with lint_fix's quote-blind M2, to *_rawM2.* (measurement; never applied)
    lint_gold_fix.sh apply            -> dry check of the proposal against the CURRENT audit (stale / missing windows)
    lint_gold_fix.sh apply --yes      -> backup the audit, then append the non-stale proposals (why "lint M...")

A proposal carries `base_sha`, the sha1 of the audit record it was built from. `apply` refuses a proposal whose
window has a newer record (STALE: rebuild), and refuses to run at all while any gold window has no audit record
(the review is still running) unless `--allow-missing`. Run `build` again right before `apply --yes`.
"""
import hashlib
import importlib.util
import json
import os
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

os.environ["BV2_SET"] = "gold"
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools")
import lint_fix  # noqa: E402

bv = lint_fix.bv
assert bv.GOLD and "gold_v2" in str(bv.AUDIT2), bv.AUDIT2
LINT = bv.BIG / "gold_v2" / "lint"
PROP, REFUSED, DIFF = LINT / "proposed_mechanical.jsonl", LINT / "proposed_mechanical_refused.jsonl", \
    LINT / "proposed_mechanical_diff.txt"
KEYS = ("id", "b", "series", "page", "events", "facts", "tags")
RAW_M2 = "--raw-m2" in sys.argv  # build with lint_fix's quote-blind M2 (measurement only; see gold_transform)
if RAW_M2:  # never the file `apply` reads
    PROP, REFUSED, DIFF = (p.with_name(p.stem + "_rawM2" + p.suffix) for p in (PROP, REFUSED, DIFF))


def sha(rec):
    return hashlib.sha1(json.dumps(rec, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def fkey(f):
    return f"{f.get('subject')}|{f.get('relation')}|{f.get('object') or '-'}" + (
        f"|{f.get('modality')}|{f.get('certainty')}|{f.get('asserted_by') or '-'}"
        if (f.get("modality") or "actual") != "actual" or f.get("asserted_by") else "")


def gates():
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    return ls, vrw


def gold_transform(rec):
    """lint_fix.transform with M2 narrowed to the SAME act. Measured 2026-11-03 on the reviewed gold audit: all 16
    actual fact twins of an event (12 windows lint_fix's M2 would touch) quote a different act -- a phone call next
    to a later in-person meeting (b2297 "called Layla" / "the two were reunited", b3795, b2326), help in an
    investigation next to a rescue from drowning (b2245), backing someone up next to freeing him (b1686). The
    reviewers kept them on purpose (why: "the call is remote contact"), as the big-set lint's final note keeps
    "directional helped/contacted pairs". So here M2 drops a twin only when fact and event quote the same string."""
    saved = lint_fix.TWIN
    lint_fix.TWIN = {}
    try:
        facts, tags, notes = lint_fix.transform(rec)
    finally:
        lint_fix.TWIN = saved
    evq = {(e["subject"], e["verb"], e["object"]): e.get("quote") for e in rec["events"]}
    out = []
    for f in facts:
        tw = saved.get(f.get("relation"))
        q = f.get("quote")
        same = tw and (f.get("modality") or "actual") == "actual" and q and (
            evq.get((f["subject"], tw, f["object"])) == q
            or (tw in bv.SYM and evq.get((f["object"], tw, f["subject"])) == q))
        if same:
            notes = sorted(set(notes) | {"M2"})
            continue
        out.append(f)
    return out, tags, notes


def build():
    ls, vrw = gates()
    ids, a2, pas, wikis = bv.order(), bv.audit2(), bv.br.passages(), {}
    props, refused, diff, counts, missing = [], [], [], {}, []
    for b, wid in enumerate(ids, 1):
        rec = a2.get(wid)
        if not rec:
            missing.append(b)
            continue
        facts, tags, notes = gold_transform(rec) if not RAW_M2 else lint_fix.transform(rec)
        if not notes:
            continue
        w = pas[wid]
        series = rec.get("series") or "marvel"
        wiki = wikis.setdefault(series, vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db")))
        fk, fd = ls.fact_gate_keep([dict(f) for f in facts], w, wiki)
        tk, td = ls.tag_gate_keep([dict(t) for t in tags], w)
        if fd or td:
            refused.append({"b": b, "id": wid, "notes": notes,
                            "refused": [(d.get("subject"), d.get("relation"), d.get("object"), d.get("why")) for d in fd]
                            + [(d.get("tag"), d.get("why")) for d in td]})
            continue
        for x in notes:
            counts[x] = counts.get(x, 0) + 1
        props.append({"id": wid, "b": b, "series": series, "page": rec.get("page"), "events": rec["events"],
                      "facts": fk, "tags": tk, "why": "lint " + "+".join(notes), "base_sha": sha(rec)})
        old, new = Counter(fkey(f) for f in rec.get("facts", [])), Counter(fkey(f) for f in fk)
        ot = Counter((t.get("tag"), t.get("quote")) for t in rec.get("tags", []))
        nt = Counter((t.get("tag"), t.get("quote")) for t in tk)
        diff.append(f"@b{b} [{series}] {rec.get('page')}  lint {'+'.join(notes)}")
        diff += [f"  f- {k}" for k in (old - new).elements()] + [f"  f+ {k}" for k in (new - old).elements()]
        diff += [f"  t- {t}|{(q or '')[:60]}" for t, q in (ot - nt).elements()]
    LINT.mkdir(parents=True, exist_ok=True)
    with open(PROP, "w") as f:
        for p in props:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(REFUSED, "w") as f:
        for r in refused:
            f.write(json.dumps(r, ensure_ascii=False, default=list) + "\n")
    DIFF.write_text("\n".join(diff) + "\n")
    print(f"proposal {len(props)} records -> {PROP}; windows per transform {counts}; gate-refused {len(refused)} "
          f"-> {REFUSED.name}; no audit record (not built) {len(missing)} {missing[:20]}")


def apply(yes, allow_missing):
    ids, a2 = bv.order(), bv.audit2()
    missing = [b for b, i in enumerate(ids, 1) if i not in a2]
    props = bv.jl(PROP)
    stale = [p["b"] for p in props if p["id"] not in a2 or sha(a2[p["id"]]) != p["base_sha"]]
    ok = [p for p in props if p["b"] not in set(stale)]
    print(f"proposal {len(props)} | applicable {len(ok)} | STALE (window re-reviewed since build: rebuild) "
          f"{len(stale)} {stale[:20]} | gold windows without audit record {len(missing)} {missing[:20]}")
    if missing and not allow_missing:
        print("NOT APPLIED: the gold review is unfinished (windows without an audit record); --allow-missing overrides")
        return
    if not yes:
        print("dry check only; `apply --yes` appends the applicable records")
        return
    bak = f"{bv.AUDIT2}.bak-pre-gold-lint-{time.strftime('%Y%m%d-%H%M%S')}"
    shutil.copy(bv.AUDIT2, bak)
    with open(bv.AUDIT2, "a") as f:
        for p in ok:
            f.write(json.dumps({**{k: p[k] for k in KEYS}, "why": p["why"]}, ensure_ascii=False) + "\n")
    print(f"appended {len(ok)} records to {bv.AUDIT2} (backup {bak})")


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "build":
        build()
    elif cmd == "apply":
        apply("--yes" in sys.argv, "--allow-missing" in sys.argv)
    else:
        sys.exit(__doc__)
