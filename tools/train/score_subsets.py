#!/usr/bin/env python3
"""Score saved window predictions on the dev/test subsets that matter, with
bootstrap 95% CIs over windows (council 2026-10-06: the 151 pool-dev windows
give a CI ~±0.1, wider than most single-seed arm gaps, so every comparison
reports its interval).

    python tools/train/score_subsets.py --gold series/universal/training/student/dev.jsonl \
        --pred RUN/dev_preds_e1.jsonl [--pred OTHER.jsonl ...] [--teacher]

--pred accepts a JSONL of {id, events} rows or a JSON {id: {events, raw}} map.
--teacher adds the frozen 35B drafter (series/<s>/training/labels/
draft_frozen.jsonl) scored on the same windows -- the bar the student must
clear on the target domain (Marvel+MCU), not the JJK blind number.
Subsets: all, pool (non-JJK), marvel+mcu, jjk.
"""
import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools"))
from eval_extraction import load_gold, score  # noqa: E402

SUBSETS = {"all": lambda s: True, "pool": lambda s: s != "jjk",
           "marvel+mcu": lambda s: s in ("marvel", "mcu"), "jjk": lambda s: s == "jjk"}


def load_preds(path):
    p = Path(path)
    if p.suffix == ".json":
        d = json.load(open(p))
        return {k: {"events": v.get("events") or [], "raw": v.get("raw", "")} for k, v in d.items()}
    out = {}
    for line in open(p):
        r = json.loads(line)
        out[r["id"]] = {"events": r.get("events") or r.get("final") or [], "raw": r.get("raw", "")}
    return out


def teacher_preds(series):
    out = {}
    for s in series:
        f = ROOT / "series" / s / "training" / "labels" / "draft_frozen.jsonl"
        if f.exists():
            out.update(load_preds(f))
    return out


def f1_of(units):
    core = sum(u["core"] for u in units)
    hit = sum(u["hit"] for u in units)
    pred = sum(u["pred"] for u in units)
    fp = sum(u["fp"] for u in units)
    p = (pred - fp) / pred if pred else 0.0
    r = hit / core if core else 0.0
    return (2 * p * r / (p + r) if p + r else 0.0), p, r


def report(name, rows, gold_path, preds, n_boot, rng):
    """One line per subset: F1 [CI] P R over the windows the preds cover."""
    for sub, keep in SUBSETS.items():
        ids = [r["id"] for r in rows if keep(r["series"]) and r["id"] in preds]
        if not ids:
            continue
        gold = {k: v for k, v in load_gold(Path(gold_path)).items() if k in set(ids)}
        summary, units = score(gold, {k: preds[k] for k in gold})
        us = [units[k] for k in units]
        f, p, r = f1_of(us)
        boots = sorted(f1_of([us[rng.randrange(len(us))] for _ in us])[0] for _ in range(n_boot))
        lo, hi = boots[int(0.025 * n_boot)], boots[int(0.975 * n_boot) - 1]
        print(f"{name:28s} {sub:11s} n={len(us):4d}  F1 {f:.3f} [{lo:.3f}-{hi:.3f}]  P {p:.3f}  R {r:.3f}  "
              f"(scorer f1 {summary['f1']})")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gold", required=True)
    ap.add_argument("--pred", action="append", default=[])
    ap.add_argument("--teacher", action="store_true")
    ap.add_argument("--boot", type=int, default=1000)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.gold)]
    rng = random.Random(20261006)
    for p in a.pred:
        report(Path(p).parent.name + "/" + Path(p).name, rows, a.gold, load_preds(p), a.boot, rng)
    if a.teacher:
        report("teacher draft_frozen (35B)", rows, a.gold, teacher_preds({r["series"] for r in rows}), a.boot, rng)


if __name__ == "__main__":
    main()
