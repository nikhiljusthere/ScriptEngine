#!/usr/bin/env python3
"""S3 source-blind audit sheet for the per-line side test. For every sentence where the per-line model and the v2
model (projected per line) disagree on who takes part or on the event triples, the sheet shows the sentence in
its passage, then two answers labelled A and B in a seeded random order, names written out (no numbers). The
key maps each line to which system is A. Lines where both agree are listed as agreed and not judged.

Verdict lines: `<L#> <A verdict> <B verdict>`, each one of
  ok      every person named takes part in this sentence and every act is right
  wrong   names someone who does not take part, or an act/ends that the sentence does not state
  miss    nothing wrong, but leaves out a person or an act the sentence states
  both    wrong and miss

    python3 tools/train/perline_sheet.py --data s2data/holdout.jsonl --perline RUN/holdout_preds.jsonl --v2 seed2.jsonl \
        --db COPY.db --split dev --out-sheet sheet.txt --out-key key.json
    python3 tools/train/perline_sheet.py --unblind --key key.json --verdicts verdicts.txt
"""
import argparse, collections, json, random, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import fact_gate  # noqa: E402
import score_layers_v2 as sl  # noqa: E402
from perline_build import project  # noqa: E402
from perline_candidates import Resolver  # noqa: E402
from perline_score import parse_lines  # noqa: E402


def show(ans, cands):
    nm = lambda k: cands[int(k) - 1] if str(k).isdigit() and 0 < int(k) <= len(cands) else f"?{k}"
    ppl = ", ".join(nm(k) for k in sorted(set(ans.get("people") or []), key=str)) or "(nobody)"
    evs = "; ".join(f"{nm(t[1])} {t[0]} {nm(t[2]) if t[2] else ''}".strip() for t in (ans.get("events") or [])
                    if isinstance(t, list) and len(t) == 3) or "(no act)"
    return f"people: {ppl}\n        acts: {evs}"


def unblind(a):
    key = json.load(open(a.key))
    C = collections.Counter()
    for l in open(a.verdicts):
        p = l.split()
        if len(p) < 3: continue
        k = key[p[0]]
        for lab, v in (("A", p[1]), ("B", p[2])):
            sysname = k["A"] if lab == "A" else k["B"]
            C[(sysname, v)] += 1
    agreed = key["_agreed"]; total = key["_lines"]
    for s in ("perline", "v2"):
        w = C[(s, "wrong")] + C[(s, "both")]; m = C[(s, "miss")] + C[(s, "both")]
        print(f"{s:8s} judged {sum(v for (x, _), v in C.items() if x == s)}  ok {C[(s, 'ok')]}  wrong {w}  miss {m}  "
              f"-> wrong lines {w}/{total} = {w/total:.3f}, missed lines {m}/{total} = {m/total:.3f} (agreed lines {agreed} taken as ok)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data"); ap.add_argument("--perline"); ap.add_argument("--v2"); ap.add_argument("--db")
    ap.add_argument("--split", default="dev"); ap.add_argument("--out-sheet"); ap.add_argument("--out-key")
    ap.add_argument("--unblind", action="store_true"); ap.add_argument("--key"); ap.add_argument("--verdicts")
    ap.add_argument("--seed", type=int, default=3)
    a = ap.parse_args()
    if a.unblind:
        return unblind(a)
    R = Resolver(a.db)
    pl = {json.loads(l)["id"]: json.loads(l).get("raw", "") for l in open(a.perline)}
    v2 = sl.load(a.v2)
    rng = random.Random(a.seed)
    key, out, L, agreed, total = {}, [], 0, 0, 0
    for r in (json.loads(l) for l in open(a.data)):
        if a.split != "all" and r["split"] != a.split: continue
        cands = r["candidates"]
        P = parse_lines(pl.get(r["id"], ""))[0]
        p = v2.get(r["id"], {"events": [], "facts": [], "tags": []})
        V = {x["n"]: x for x in project(dict(r, **{k: p[k] for k in ("events", "facts", "tags")}), cands, r["candidate_ids"], R)[0]["lines"]}
        sents = fact_gate.sentences(r["passage"])
        block = []
        for n, s in enumerate(sents, 1):
            total += 1
            x, y = P.get(n, {}), V.get(n, {})
            sx = (sorted(set(map(str, x.get("people") or []))), sorted(map(str, x.get("events") or [])))
            sy = (sorted(set(map(str, y.get("people") or []))), sorted(map(str, y.get("events") or [])))
            if sx == sy:
                agreed += 1; continue
            L += 1; lid = f"L{L:03d}"
            first = rng.random() < .5
            key[lid] = {"A": "perline" if first else "v2", "B": "v2" if first else "perline", "id": r["id"], "n": n}
            A, B = (x, y) if first else (y, x)
            block.append(f"  {lid} [{n}] {s}\n    A {show(A, cands)}\n    B {show(B, cands)}")
        if block:
            out.append(f"===== {r['page']} / {r.get('section', '')}\n{r['passage']}\n\n" + "\n".join(block) + "\n")
    key["_agreed"], key["_lines"] = agreed, total
    open(a.out_sheet, "w").write("\n".join(out)); json.dump(key, open(a.out_key, "w"), indent=0)
    print(f"lines {total}, agreed {agreed}, to judge {L}")


if __name__ == "__main__":
    main()
