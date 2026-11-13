#!/usr/bin/env python3
"""student_v3 (step 2c of docs/9B_STUDENT_ANALYSIS_2026-11-14.md): the v3 split (split_v3_dev.py) with
normalised TRAIN targets, so one statement has one encoding in what the student learns. The gold files on
disk are not touched; dev_v3 is copied unchanged (score it statement-level, score_v3.py).

The transform (facts only, object-less knowledge/belief rows; rule A133 allows either encoding, so the
target picks one):
  discovered (object null)                                    -> learned
  other_verb realize|learn|notice|discover|deduce|figure      -> learned (object null)
  other_verb believe|think|suspect|assume                     -> suspected (object null)
Not merged: located_at/resides_at (different statements in training; merged only by the scorer),
discovered WITH an object (found a thing), other_verb find/know/recognize (often take an object), typed
relations that need an object (an other_verb row does not carry one).
Duplicate rows created by the merge (same quote, subject, relation, object, modality) are dropped.

    python3 tools/train/compose_v3.py --split series/universal/training/student_v3_split \
        --out series/universal/training/student_v3 [--subset nonmarvel]
"""
import argparse, collections, json, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from statement_norm import lemma  # noqa: E402

TO_LEARNED = {"realize", "learn", "notice", "discover", "deduce", "figure"}
TO_SUSPECTED = {"believe", "think", "suspect", "assume"}


def norm_fact(f, stats):
    rel = f.get("relation")
    if rel == "discovered" and f.get("object") is None:
        stats["discovered->learned"] += 1
        return dict(f, relation="learned")
    if rel == "other_verb":
        lm = lemma(f.get("object"))
        if lm in TO_LEARNED:
            stats[f"ov:{lm}->learned"] += 1
            return dict(f, relation="learned", object=None)
        if lm in TO_SUSPECTED:
            stats[f"ov:{lm}->suspected"] += 1
            return dict(f, relation="suspected", object=None)
    return f


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--subset", choices=("all", "nonmarvel"), default="all")
    a = ap.parse_args()
    src, out = Path(a.split), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    stats, n = collections.Counter(), 0
    with open(out / "train.jsonl", "w") as w:
        for l in open(src / "train.jsonl"):
            r = json.loads(l)
            if a.subset == "nonmarvel" and (r["series"] in ("marvel", "mcu") or r["source"] != "gold_v2"):
                continue
            facts, seen = [], set()
            for f in r["facts"]:
                f2 = norm_fact(f, stats)
                k = (f2.get("quote"), f2.get("subject"), f2.get("relation"), f2.get("object"), f2.get("modality"))
                if k in seen:
                    stats["dup_dropped"] += 1; continue
                seen.add(k); facts.append(f2)
            if facts != r["facts"]:
                stats["windows_changed"] += 1
                r["facts"] = facts
                r["messages"][-1]["content"] = json.dumps({"events": r["events"], "facts": facts, "tags": r["tags"]},
                                                          ensure_ascii=False)
            w.write(json.dumps(r, ensure_ascii=False) + "\n"); n += 1
    shutil.copy(src / "dev_v3.jsonl", out / "dev_v3.jsonl")
    rep = {"train": n, "subset": a.subset, **dict(stats)}
    json.dump(rep, open(out / "compose_report.json", "w"), indent=1); print(json.dumps(rep))


if __name__ == "__main__":
    main()
