#!/usr/bin/env python3
"""Build the UNIVERSAL student-training set from the manually verified pools
(plan/UNIVERSAL_DATASET_PLAN.md "Student model trial"; plan/VERIFY_POOLS_BRIEF.md).

Sources:
* every series' verified pool windows: series/<s>/training/labels/pool_in.jsonl
  (the EXACT production system+user messages the drafter read) joined with
  pool_verified.jsonl (the 27B/Space-Bunny verifier's saved record, every one
  reviewed by Claude; corrections in pool_audit.jsonl) -> assistant
  {"events": final rows};
* the JJK verified student set (series/jjk/training/student/{train,dev}.jsonl).

Split: dev = 5% and test = 10% of each series' PAGES (seeded), never a page on
two sides; dev picks the arm, test is scored once on the winner (owner
2026-10-06: the drafted test windows are not verified, the held-out verified
pages are the exam). JJK keeps its own train/dev (its exam is blind v6). Cap: no series above 35% of the train windows
(the plan's mix rule) -- the overflow is sampled out (seeded), never the
verified rows of a kept window.

Gates (exit non-zero on any failure): every window reviewed by Claude (review
cursor == saved count) unless --allow-unreviewed; every quote verbatim in its
user passage; verbs in the 12; awakened has a null object; no test window id;
no holdout page; unique ids; page-disjoint train/dev per series.

    scriptengine/.venv/bin/python tools/train/build_universal_set.py
        -> series/universal/training/student/{train,dev,test}.jsonl + receipt.json
"""
import argparse
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_student_set import assistant_content  # noqa: E402  (same answer format as the JJK set)

POOLS = ["opm", "csm", "berserk", "bleach", "db", "onepiece", "marvel", "mcu"]
VERBS = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "met", "arrived", "departed", "awakened"}
DEV_FRAC, TEST_FRAC, SEED, CAP = 0.05, 0.10, 20261006, 0.35


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default=str(ROOT / "series/universal/training/student"))
    ap.add_argument("--allow-unreviewed", action="store_true")
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    errors, counts, train, dev, test = [], Counter(), [], [], []
    for s in POOLS:
        lab = ROOT / "series" / s / "training" / "labels"
        src = {r["id"]: r for r in jl(lab / "pool_in.jsonl")}
        ver = jl(lab / "pool_verified.jsonl")
        try:
            reviewed = int((lab / "pool_review_cursor.txt").read_text().strip())
        except (OSError, ValueError):
            reviewed = 0
        if reviewed < len(ver) and not a.allow_unreviewed:
            errors.append(f"{s}: {len(ver) - reviewed} saved windows not reviewed by Claude")
        test_ids = {r["id"] for r in jl(lab / "test_in.jsonl")}
        hold = set()
        hp = ROOT / "series" / s / "training" / "holdout_pages.json"
        if hp.exists():
            h = json.loads(hp.read_text())
            hold = set(h if isinstance(h, list) else h.get("pages", []))
        recs = []
        for v in ver:
            w = src.get(v["id"])
            if w is None:
                errors.append(f"{s}: verified id {v['id']} not in pool_in")
                continue
            if v["id"] in test_ids:
                errors.append(f"{s}: {v['id']} is a test window")
            if w["page"] in hold:
                errors.append(f"{s}: {v['id']} sits on holdout page {w['page']!r}")
            user = w["messages"][1]["content"]
            passage = user.split("Passage:\n", 1)[1]
            events = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in v.get("final") or []]
            for e in events:
                if e["verb"] not in VERBS:
                    errors.append(f"{s}/{v['id']}: bad verb {e['verb']!r}")
                if not e["quote"] or e["quote"] not in passage:
                    errors.append(f"{s}/{v['id']}: quote not verbatim: {str(e['quote'])[:60]!r}")
                if e["verb"] == "awakened" and e["object"]:
                    errors.append(f"{s}/{v['id']}: awakened with an object")
            recs.append({"id": v["id"], "series": s, "page": w["page"], "section": w["section"],
                         "passage": passage, "events": events, "source": "pool_verified",
                         "messages": [w["messages"][0], w["messages"][1],
                                      {"role": "assistant", "content": assistant_content(events)}]})
        pages = sorted({r["page"] for r in recs})
        rnd = random.Random(f"{SEED}-{s}")
        held = rnd.sample(pages, max(2, round(len(pages) * (DEV_FRAC + TEST_FRAC)))) if len(pages) > 2 else []
        n_dev = max(1, round(len(pages) * DEV_FRAC)) if held else 0
        dev_pages, test_pages = set(held[:n_dev]), set(held[n_dev:])
        for r in recs:
            split = "dev" if r["page"] in dev_pages else "test" if r["page"] in test_pages else "train"
            {"dev": dev, "test": test, "train": train}[split].append({**r, "split": split})
        counts[s] = len(recs)
    # the JJK verified set keeps its own split
    for split, bucket in (("train", train), ("dev", dev)):
        for r in jl(ROOT / "series/jjk/training/student" / f"{split}.jsonl"):
            bucket.append({**{k: r[k] for k in ("id", "page", "section", "passage", "events", "messages")},
                           "series": "jjk", "source": r.get("source", "jjk_gold"), "split": split})
    # the 35% mix cap on train windows
    by = defaultdict(list)
    for r in train:
        by[r["series"]].append(r)
    capped = []
    for s, rs in sorted(by.items()):
        # the share is of the FINAL train set: x <= CAP * (x + others)
        # (capping against the pre-cap total left JJK at 43%)
        limit = int(CAP / (1 - CAP) * (len(train) - len(rs)))
        if len(rs) > limit:
            rs = random.Random(f"{SEED}-cap-{s}").sample(rs, limit)
        capped += rs
    train = capped
    ids = [r["id"] for r in train + dev + test]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate ids: {len(ids) - len(set(ids))}")
    for s in set(r["series"] for r in train):
        tp = {r["page"] for r in train if r["series"] == s}
        dp = {r["page"] for r in dev if r["series"] == s}
        sp = {r["page"] for r in test if r["series"] == s}
        if tp & dp or tp & sp or dp & sp:
            errors.append(f"{s}: pages shared across train/dev/test")
    if errors:
        print("BUILD FAILED:\n" + "\n".join(errors[:40]) + (f"\n... {len(errors)} total" if len(errors) > 40 else ""))
        return 1
    for name, rows in (("train", train), ("dev", dev), ("test", test)):
        with open(out / f"{name}.jsonl", "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rec = {"train": len(train), "dev": len(dev), "test": len(test),
           "test_by_series": Counter(r["series"] for r in test),
           "train_by_series": Counter(r["series"] for r in train),
           "dev_by_series": Counter(r["series"] for r in dev),
           "train_empty_windows": sum(1 for r in train if not r["events"]),
           "train_rows": sum(len(r["events"]) for r in train),
           "train_verbs": Counter(e["verb"] for r in train for e in r["events"])}
    (out / "receipt.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
