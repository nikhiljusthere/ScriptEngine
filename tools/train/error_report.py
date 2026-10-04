#!/usr/bin/env python3
"""Every FN and FP of a prediction file against a window-level gold, using
the scorer's own match rule (names + verb, quote spans overlapping) — the
input to the FLAWLESS plan's error taxonomy (section 3).

    python tools/train/error_report.py --gold G.jsonl --pred P.jsonl [--out R.jsonl]
"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
import eval_extraction as E  # noqa: E402


def span(text, q):
    q = (q or "").strip()
    i = text.find(q) if q else -1
    return (i, i + len(q)) if i >= 0 else None


def overl(a, b):
    return a is not None and b is not None and a[0] < b[1] and b[0] < a[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True); ap.add_argument("--pred", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(a.gold)}
    pred = {json.loads(l)["id"]: json.loads(l) for l in open(a.pred)}
    out = []
    for wid, g in gold.items():
        text = g["passage"]
        core = [(e, span(text, e["quote"])) for e in g["events"]]
        opt = [(e, span(text, e["quote"])) for e in g.get("optional", [])]
        preds = [(p, span(text, p.get("quote"))) for p in pred.get(wid, {}).get("events", [])]
        used = set()
        for p, ps in preds:
            trip = (p.get("subject"), p.get("verb"), p.get("object"))
            hit = None
            for i, (e, es) in enumerate(core):
                if i not in used and E.match(trip, (e["subject"], e["verb"], e["object"])) and overl(ps, es):
                    hit = i; break
            if hit is not None:
                used.add(hit); continue
            if any(E.match(trip, (e["subject"], e["verb"], e["object"])) and overl(ps, es) for e, es in opt):
                continue
            if any(E.match(trip, (e["subject"], e["verb"], e["object"])) and overl(ps, es)
                   for j, (e, es) in enumerate(core) if j in used):
                continue  # duplicate of a matched event: neutral
            out.append({"kind": "FP", "id": wid, "page": g["page"], "section": g["section"],
                        "row": p, "units": g.get("units")})
        for i, (e, es) in enumerate(core):
            if i not in used:
                near = [p for p, ps in preds if overl(ps, es)]
                out.append({"kind": "FN", "id": wid, "page": g["page"], "section": g["section"],
                            "row": e, "near_preds": near, "units": g.get("units")})
    if a.out:
        with open(a.out, "w") as f:
            for r in out:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    fn = sum(1 for r in out if r["kind"] == "FN"); fp = len(out) - fn
    print(json.dumps({"FN": fn, "FP": fp}))
    for r in out:
        x = r["row"]
        tail = f" | near: {[(n.get('subject'), n.get('verb'), n.get('object')) for n in r.get('near_preds', [])]}" if r["kind"] == "FN" else ""
        print(f"{r['kind']} {r['units']} {r['page']} / {r['section']}: {x.get('subject')} ={x.get('verb')}=> {x.get('object')} | \"{(x.get('quote') or '')[:110]}\"{tail}")


if __name__ == "__main__":
    main()
