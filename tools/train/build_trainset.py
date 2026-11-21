"""Build the student's training file from verified windows only (council
2026-09-29 recipe): symmetric duplicates removed with the post-filter's own rule,
windows holding a rare verb repeated, empty windows kept at their natural share,
and anything not verified refused.

    python tools/train/build_trainset.py --verified a.jsonl [b.jsonl ...] --out train.jsonl [--rare-x 3]

Inputs are export-shaped records (messages: system, user, assistant) whose tier
is "gold" (Claude-verified). Prints a receipt of what went in.
"""
import argparse, collections, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from postfilter import filter_rows  # noqa: E402

RARE = {"killed", "saved", "captured", "escaped", "betrayed", "sealed", "awakened", "departed", "arrived"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verified", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--rare-x", type=int, default=3)
    a = ap.parse_args()
    recs, seen = [], set()
    for f in a.verified:
        for l in open(f):
            r = json.loads(l)
            if r.get("tier") != "gold":
                sys.exit(f"{f}: window {r['id']} is not verified (tier {r.get('tier')!r}); refusing")
            if r["id"] in seen:
                continue  # a window verified twice keeps its first (latest-listed file wins by order)
            seen.add(r["id"])
            recs.append(r)
    out, stat, verbs = [], collections.Counter(), collections.Counter()
    for r in recs:
        text = r["messages"][1]["content"].split("Passage:\n", 1)[1]
        ev = json.loads(r["messages"][2]["content"])["events"]
        kept, rej = filter_rows(ev, text)
        stat["rows_dropped_by_filter"] += len(rej)
        r = dict(r)
        r["messages"] = r["messages"][:2] + [{"role": "assistant", "content": json.dumps({"events": kept}, ensure_ascii=False)}]
        k = a.rare_x if any(e["verb"] in RARE for e in kept) else 1
        stat["empty" if not kept else "with_events"] += 1
        stat["rare_windows"] += k > 1
        for e in kept:
            verbs[e["verb"]] += 1
        out += [r] * k
    with open(a.out, "w") as f:
        for r in out:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(json.dumps({"windows": len(recs), "records_written": len(out), **stat, "verbs": dict(verbs)}))


if __name__ == "__main__":
    main()
