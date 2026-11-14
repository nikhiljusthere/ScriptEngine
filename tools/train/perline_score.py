#!/usr/bin/env python3
"""S3 of the per-line side test: score per-line predictions and v2 predictions on the same sentences, against the
gold re-projected per line (perline_build.project). A v2 prediction ({events, facts, tags} or raw) is projected
through the same function with the window's candidate list, so both systems are read on the same footing.

Per sentence: class (4-way accuracy), is-event F1, people as candidate numbers (exact-set share, micro F1),
wrong-person lines (pred names someone the gold line does not), missed lines (gold names people, pred none),
event triples [verb, s, o] F1 and verb-only F1. Reported for all windows and per split (holdout / dev).

    python3 tools/train/perline_score.py --data s2data/holdout.jsonl --perline RUN/holdout_preds.jsonl \
        --v2 seed2_holdout_preds.jsonl [--out-lines lines.jsonl]
"""
import argparse, collections, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "train"))
import score_layers_v2 as sl  # noqa: E402
from perline_build import project  # noqa: E402


def parse_lines(raw):
    body = re.sub(r"<think>.*?</think>", "", raw or "", flags=re.S)
    s, e = body.find("{"), body.rfind("}")
    try:
        d = json.loads(body[s:e + 1])
        return {int(x["n"]): x for x in d.get("lines", []) if isinstance(x, dict) and "n" in x}, True
    except Exception:
        return {}, False


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--perline"); ap.add_argument("--v2", action="append", default=[])
    ap.add_argument("--out-lines")
    ap.add_argument("--db", required=True, help="the series store copy the candidate lists came from (aliases)")
    a = ap.parse_args()
    data = [json.loads(l) for l in open(a.data)]
    from perline_candidates import Resolver
    R = Resolver(a.db)
    systems = {}
    if a.perline:
        raw = {json.loads(l)["id"]: json.loads(l).get("raw", "") for l in open(a.perline)}
        systems["perline:" + Path(a.perline).parent.name] = ("perline", raw)
    for p in a.v2:
        systems["v2:" + Path(p).stem] = ("v2", sl.load(p))
    out_lines = []
    for name, (kind, preds) in systems.items():
        for split in ("all", "holdout", "dev"):
            C = collections.Counter()
            for r in data:
                if split != "all" and r["split"] != split: continue
                gold = {x["n"]: x for x in r["target"]["lines"]}
                if kind == "perline":
                    pl, ok = parse_lines(preds.get(r["id"], ""))
                    C["valid"] += ok
                else:
                    p = preds.get(r["id"], {"events": [], "facts": [], "tags": []})
                    cands = r["candidates"]  # same name + alias forms the gold projection used (perline_build.build)
                    t, _ = project(dict(r, events=p["events"], facts=p["facts"], tags=p["tags"]), cands, r["candidate_ids"], R)
                    pl = {x["n"]: x for x in t["lines"]}
                    C["valid"] += 1
                C["windows"] += 1
                for n, g in gold.items():
                    q = pl.get(n, {"class": None, "people": [], "events": []})
                    gp, pp = set(g["people"]), set(int(x) for x in (q.get("people") or []) if str(x).isdigit())
                    C["lines"] += 1; C["class_ok"] += q.get("class") == g["class"]
                    ge, pe = g["class"] == "event", q.get("class") == "event"
                    C["ev_tp"] += ge and pe; C["ev_p"] += pe; C["ev_g"] += ge
                    C["exact"] += gp == pp; C["pp_tp"] += len(gp & pp); C["pp_p"] += len(pp); C["pp_g"] += len(gp)
                    C["wrong_person"] += bool(pp - gp); C["missed"] += bool(gp) and not pp; C["gold_has_people"] += bool(gp)
                    gt = {tuple(x) for x in g["events"]}
                    pt = {tuple(x) for x in (q.get("events") or []) if isinstance(x, list) and len(x) == 3}
                    C["tr_tp"] += len(gt & pt); C["tr_p"] += len(pt); C["tr_g"] += len(gt)
                    gv, pv = collections.Counter(x[0] for x in gt), collections.Counter(x[0] for x in pt)
                    C["vb_tp"] += sum((gv & pv).values()); C["vb_p"] += sum(pv.values()); C["vb_g"] += sum(gv.values())
                    if split == "all" and a.out_lines:
                        out_lines.append({"system": name, "id": r["id"], "n": n, "gold": g, "pred": q})
            f1 = lambda tp, p, g: 2 * tp / (p + g) if p + g else 0.0
            print(f"{name:28s} {split:7s} win {C['windows']:3d} lines {C['lines']:4d} valid {C['valid']}/{C['windows']} "
                  f"class {C['class_ok']/C['lines']:.3f} is_event F1 {f1(C['ev_tp'], C['ev_p'], C['ev_g']):.3f} "
                  f"people exact {C['exact']/C['lines']:.3f} F1 {f1(C['pp_tp'], C['pp_p'], C['pp_g']):.3f} "
                  f"wrong-person {C['wrong_person']/C['lines']:.3f} missed {C['missed']}/{C['gold_has_people']}={C['missed']/max(C['gold_has_people'],1):.3f} "
                  f"triples F1 {f1(C['tr_tp'], C['tr_p'], C['tr_g']):.3f} verbs F1 {f1(C['vb_tp'], C['vb_p'], C['vb_g']):.3f}")
    if a.out_lines:
        with open(a.out_lines, "w") as f:
            for x in out_lines: f.write(json.dumps(x, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
