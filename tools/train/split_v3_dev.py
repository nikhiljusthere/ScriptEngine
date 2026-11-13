#!/usr/bin/env python3
"""Step 1a of the 2026-11-14 analysis (docs/9B_STUDENT_ANALYSIS_2026-11-14.md, worktree
9b-model-extraction-analysis-a7e9c9): a dev set of 600+ windows outside Marvel and MCU, page-disjoint from
train. Holds out ~20% of each non-Marvel series' gold_v2 TRAIN pages (whole pages, seeded), adds the existing
non-Marvel dev windows, and drops from train every window that shares a >=40-char sentence with the new dev
(the compose leak rule). Test is untouched and stays sealed. Writes OUT/{train,dev_v3,holdout_ids}.jsonl.

Why 600: at 151 dev_pool windows the events CI is ~+-.11, wider than any arm gap seen so far.

    python3 tools/train/split_v3_dev.py --src series/universal/training/student_v2_short --out DIR [--frac .2 --seed 7]
"""
import argparse, json, random, re
from collections import defaultdict
from pathlib import Path

MARVEL = {"marvel", "mcu"}


def sents(text):
    return {s.strip() for s in re.split(r"(?<=[.!?])\s+", text or "") if len(s.strip()) >= 40}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--frac", type=float, default=0.2); ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    src, out = Path(a.src), Path(a.out); out.mkdir(parents=True, exist_ok=True)
    train = [json.loads(l) for l in open(src / "train.jsonl")]
    dev = [json.loads(l) for l in open(src / "dev.jsonl")]
    test = [json.loads(l) for l in open(src / "test.jsonl")]
    rng = random.Random(a.seed)
    pages = defaultdict(list)
    for r in train:
        if r["series"] not in MARVEL and r["source"] == "gold_v2":
            pages[r["series"]].append(r["page"])
    hold = set()
    for s, ps in sorted(pages.items()):
        n_target = round(len(ps) * a.frac)
        uniq = sorted(set(ps)); rng.shuffle(uniq)
        cnt = {p: ps.count(p) for p in uniq}; got = 0
        for p in uniq:
            if got >= n_target: break
            hold.add((s, p)); got += cnt[p]
    held = [r for r in train if (r["series"], r["page"]) in hold]
    dev_nm = [dict(r, split="dev_v3_olddev") for r in dev if r["series"] not in MARVEL]
    dev_v3 = [dict(r, split="dev_v3_holdout") for r in held] + dev_nm
    dev_s = set().union(*(sents(r["passage"]) for r in dev_v3))
    dev_pages = {(r["series"], r["page"]) for r in dev_v3}
    test_s = set().union(*(sents(r["passage"]) for r in test))
    new_train, leak = [], 0
    for r in train:
        if (r["series"], r["page"]) in hold:
            continue
        if sents(r["passage"]) & dev_s:
            leak += 1; continue
        new_train.append(r)
    with open(out / "train.jsonl", "w") as f:
        for r in new_train: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(out / "dev_v3.jsonl", "w") as f:
        for r in dev_v3: f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rep = {"train_in": len(train), "train_out": len(new_train), "held_out_windows": len(held), "held_pages": len(hold),
           "dropped_for_sentence_leak": leak, "dev_v3": len(dev_v3), "old_dev_non_marvel": len(dev_nm),
           "dev_v3_by_series": {s: sum(r["series"] == s for r in dev_v3) for s in sorted({r["series"] for r in dev_v3})},
           "page_overlap_train_dev": len({(r["series"], r["page"]) for r in new_train} & dev_pages),
           "sentence_overlap_dev_test": len(dev_s & test_s), "frac": a.frac, "seed": a.seed}
    json.dump(rep, open(out / "split_report.json", "w"), indent=1)
    print(json.dumps(rep, indent=1))


if __name__ == "__main__":
    main()
