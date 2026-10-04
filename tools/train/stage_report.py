#!/usr/bin/env python3
"""Per-stage accounting of a drafter v2 run against window-level gold
(FLAWLESS plan rounds): hits after each stage (samples, missed, families,
pre-verify, final), verifier drops that were TRUE, and every FN (with the
stage that lost it) and FP. Name match = the scorer's rule; window-level
(same window + same triple).

    python tools/train/stage_report.py --gold G.jsonl --pred P.jsonl
"""
import argparse, collections, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import eval_extraction as E  # noqa: E402


def m(r, e):
    return E.match((r.get("subject"), r.get("verb"), r.get("object")),
                   (e["subject"], e["verb"], e["object"]))


def hits(rows, g):
    used, n = set(), 0
    for r in rows:
        for i, e in enumerate(g["events"]):
            if i not in used and m(r, e):
                used.add(i); n += 1; break
    return n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", required=True)
    a = ap.parse_args()
    G = {json.loads(l)["id"]: json.loads(l) for l in open(a.gold)}
    P = {json.loads(l)["id"]: json.loads(l) for l in open(a.pred)}
    tot = collections.Counter(); fn, fp = [], []
    for wid, g in G.items():
        p = P.get(wid, {}); st = p.get("stages", {})
        tot["core"] += len(g["events"])
        for k, s in enumerate(st.get("samples", [])):
            tot[f"sample{k+1}"] += hits(s, g)
        fams = st.get("families", {}) or {}
        tot["pre_verify"] += hits(st.get("pre_verify", []), g)
        tot["final"] += hits(p.get("events", []), g)
        used = set()
        for r in p.get("events", []):
            ok = False
            for i, e in enumerate(g["events"]):
                if i not in used and m(r, e):
                    used.add(i); ok = True; break
            if not ok and not any(m(r, e) for e in g.get("optional", []) + g["events"]):
                fp.append((g["page"], r.get("subject"), r.get("verb"), r.get("object"), (r.get("quote") or "")[:90]))
        for i, e in enumerate(g["events"]):
            if i in used:
                continue
            if any(m(r, e) for r in st.get("pre_verify", [])):
                stage = "verifier-dropped"
            else:
                stage = "never-drafted"
            fn.append((stage, g["page"], e["subject"], e["verb"], e["object"], e["quote"][:80]))
    print(json.dumps(dict(tot)))
    print("FN", len(fn), collections.Counter(x[0] for x in fn), collections.Counter(x[3] for x in fn))
    for x in sorted(fn): print(" FN", x)
    print("FP", len(fp))
    for x in fp: print(" FP", x)


if __name__ == "__main__":
    main()
