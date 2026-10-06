"""Measure label_single variants against the hand-reviewed big windows.

  python eval_hints.py ids N OUT.jsonl         sample N reviewed windows (b7..cursor, seeded) -> ids file
  python eval_hints.py score IDS FILE [FILE..] row P/R/F1 of each label file vs the reviewed rows
  python eval_hints.py repair-rate             share of reviewed windows whose ORIGINAL 35B rows fire a repair flag

Gold = the final reviewed rows (big_audit.jsonl applied; windows with no correction keep the 35B rows,
which the review accepted). Rows match on (subject, verb, object); fought/met are symmetric.
(SCRIPTENGINE_ROOT points at the checkout holding the data.)
"""
import json
import os
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("SCRIPTENGINE_ROOT", str(Path(__file__).resolve().parents[2]))
import big_flags as bf  # noqa: E402
import label_hints  # noqa: E402

br = bf.br


def gold():
    rows, c = br.jl(br.LABELS), br.cursor()
    final = {a["id"]: a["after"] for a in br.jl(br.AUDIT)}
    return {r["id"]: final.get(r["id"], r["events"]) for r in rows[6:c]}


def keys(evs):
    out = set()
    for e in evs:
        s, v, o = e["subject"], e["verb"], e["object"]
        out.add((v, *sorted([s, o])) if v in ("fought", "met") and o else (s, v, o))
    return out


def score(ids, path, g):
    pred = {}
    for l in open(path):
        r = json.loads(l)
        pred[r["id"]] = r["events"]
    tp = fp = fn = exact = n = 0
    for i in ids:
        if i not in pred:
            continue
        n += 1
        p, t = keys(pred[i]), keys(g[i])
        tp += len(p & t); fp += len(p - t); fn += len(t - p)
        exact += p == t
    P = tp / (tp + fp) if tp + fp else 0
    R = tp / (tp + fn) if tp + fn else 0
    F = 2 * P * R / (P + R) if P + R else 0
    return f"{Path(path).name}: n={n} P={P:.3f} R={R:.3f} F1={F:.3f} exact={exact}/{n}"


def main():
    cmd = sys.argv[1]
    g = gold()
    if cmd == "ids":
        n, out = int(sys.argv[2]), sys.argv[3]
        ids = sorted(g)
        random.Random(20261007).shuffle(ids)
        with open(out, "w") as f:
            for i in ids[:n]:
                f.write(json.dumps({"id": i}) + "\n")
        print(f"{n} ids -> {out}")
    elif cmd == "score":
        ids = [json.loads(l)["id"] for l in open(sys.argv[2])]
        for p in sys.argv[3:]:
            print(score(ids, p, g))
        # the original single-pass labels on the same windows, for reference
        orig = {r["id"]: r["events"] for r in br.jl(br.LABELS)}
        tmp = Path(os.environ.get("TMPDIR", "/tmp")) / "eval_hints_orig.jsonl"
        with open(tmp, "w") as f:
            for i in ids:
                f.write(json.dumps({"id": i, "events": orig[i]}) + "\n")
        print("(original run) " + score(ids, tmp, g))
    elif cmd == "compare":
        # paired bootstrap over windows: F1(B) - F1(A), 95% interval
        ids = [json.loads(l)["id"] for l in open(sys.argv[2])]
        A, B = ({json.loads(l)["id"]: json.loads(l)["events"] for l in open(p)} for p in sys.argv[3:5])
        ids = [i for i in ids if i in A and i in B]

        def counts(pred):
            out = []
            for i in ids:
                p, t = keys(pred[i]), keys(g[i])
                out.append((len(p & t), len(p - t), len(t - p)))
            return out
        ca, cb = counts(A), counts(B)

        def f1(c, idx):
            tp = sum(c[k][0] for k in idx); fp = sum(c[k][1] for k in idx); fn = sum(c[k][2] for k in idx)
            return 2 * tp / (2 * tp + fp + fn) if tp else 0.0
        rng = random.Random(7)
        n = len(ids)
        d = sorted(f1(cb, s) - f1(ca, s) for s in ([rng.randrange(n) for _ in range(n)] for _ in range(2000)))
        print(f"n={n} F1 {f1(ca, range(n)):.3f} -> {f1(cb, range(n)):.3f}; "
              f"diff {f1(cb, range(n)) - f1(ca, range(n)):+.3f} [95% {d[50]:+.3f}, {d[1949]:+.3f}]")
    elif cmd == "repair-rate":
        rows, pas = br.jl(br.LABELS), br.passages()
        c = br.cursor()
        fire = sum(1 for r in rows[6:c] if label_hints.repair_note(r["events"], pas[r["id"]], bf.check))
        print(f"repair would fire on {fire}/{c - 6} reviewed windows")


if __name__ == "__main__":
    main()
