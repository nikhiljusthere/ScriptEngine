#!/usr/bin/env python3
"""Stage A/B/C driver for the student search (U-WP6, train-env).

    python tools/train/sweep.py [--root ~/student_runs] [--plan] [--stage A|B|C|all]

Stage A: lr {3e-5,6e-5,1e-4,2e-4} x rank {16,64,128} (alpha=2r,
dropout 0.05, 1 epoch), plus FULL fine-tune arms at lr {1e-5,2e-5}
(language layers only, 8-bit paged AdamW; owner 2026-10-05: "I want the
best results" -- LoRA vs full FT is decided by dev F1, not assumed)
-> top-3 by dev F1.
Stage B: around each top-3, lr x{0.7,1.0,1.4}, up to 4 epochs with
per-epoch early stop; rare-verb repeat {1,3} ONLY for the best Stage-A
lr.
Stage C: the best config x seeds {1,2,3}, then eval_student on the
blind test gold for each and the report.

Every run is a subprocess (one GPU job at a time); a run is skipped
when its final.json exists (resumable). Results: results.jsonl +
results.md under the root. Once Stage B has started, the non-best
Stage-A adapters are deleted (the disk policy keeps only best/).
Selection metric everywhere: dev micro event-F1, with dev precision
as the tie-break.
"""
import argparse, json, math, os, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# The universal verified set (tools/train/build_universal_set.py): the 8
# verified pools + the JJK verified gold, page-split dev, 35% mix cap.
TRAIN = ROOT / "series/universal/training/student/train.jsonl"
DEV = ROOT / "series/universal/training/student/dev.jsonl"
TEST = ROOT / "series/jjk/training/recall_gold_v3/gold_test_v4.gen2.json"
RUNS = Path.home() / "student_runs"

LRS_A = [3e-5, 6e-5, 1e-4, 2e-4]
LRS_FULL_A = [1e-5, 2e-5]
RANKS_A = [16, 64, 128]
DROP, EPOCHS_A = 0.05, 1
B_LR_MULT = [0.7, 1.0, 1.4]
B_EPOCHS = 4
SEEDS_C = [1, 2, 3]


def lr_tag(lr):
    return f"{lr:g}".replace("-", "-")


def stage_a():
    runs = []
    for lr in LRS_A:
        for r in RANKS_A:
            runs.append({"stage": "A", "lr": lr, "rank": r,
                         "alpha": 2 * r, "dropout": DROP, "epochs": EPOCHS_A,
                         "seed": 1, "rare_x": 1,
                         "name": f"A-lr{lr_tag(lr)}-r{r}"})
    for lr in LRS_FULL_A:
        runs.append({"stage": "A", "lr": lr, "rank": 0, "alpha": 0, "dropout": 0.0,
                     "epochs": EPOCHS_A, "seed": 1, "rare_x": 1, "full_ft": True,
                     "name": f"A-lr{lr_tag(lr)}-full"})
    return runs


def arm(t):
    """'full' for a full fine-tune, else 'r<rank>' -- run-name tag."""
    return "full" if t.get("full_ft") else f"r{t['rank']}"


def stage_b(top3, best_lr):
    runs = []
    for t in top3:
        for m in B_LR_MULT:
            lr = t["lr"] * m
            for rx in ([1, 3] if abs(t["lr"] - best_lr) < 1e-12 else [1]):
                runs.append({"stage": "B", "lr": lr, "rank": t["rank"],
                             "alpha": t["alpha"], "dropout": t.get("dropout", DROP),
                             "epochs": B_EPOCHS, "seed": 1, "rare_x": rx,
                             "full_ft": bool(t.get("full_ft")),
                             "name": f"B-lr{lr_tag(lr)}-{arm(t)}-rx{rx}"})
    return runs


def stage_c(best):
    return [{"stage": "C", "lr": best["lr"], "rank": best["rank"],
             "alpha": best["alpha"], "dropout": best.get("dropout", DROP), "epochs": B_EPOCHS,
             "seed": s, "rare_x": best["rare_x"], "full_ft": bool(best.get("full_ft")),
             "name": f"C-lr{lr_tag(best['lr'])}-{arm(best)}-rx{best['rare_x']}-s{s}"}
            for s in SEEDS_C]


def cmd(run, root):
    out = root / run["name"]
    return [sys.executable, str(ROOT / "tools/train/sft_qwen.py"),
            "--train", str(TRAIN), "--dev", str(DEV), "--out", str(out),
            "--lr", str(run["lr"]), "--rank", str(run["rank"]),
            "--alpha", str(run["alpha"]), "--dropout", str(run["dropout"]),
            "--epochs", str(run["epochs"]), "--seed", str(run["seed"]),
            "--rare-x", str(run["rare_x"])] + (["--full-ft"] if run.get("full_ft") else [])


def final_f1(out):
    try:
        f = json.load(open(out / "final.json"))
        return f.get("best_dev_f1")
    except (FileNotFoundError, ValueError):
        return None


def last_metric(out):
    try:
        lines = [json.loads(l) for l in open(out / "metrics.jsonl")]
        return lines[-1] if lines else {}
    except FileNotFoundError:
        return {}


def record(root, run):
    out = root / run["name"]
    m = last_metric(out)
    f = {**run, "best_dev_f1": final_f1(out),
         "dev_p": m.get("dev_p"), "dev_r": m.get("dev_r"),
         "json_validity": m.get("json_validity"),
         "quote_verbatim": m.get("quote_verbatim"),
         "windows_per_s": m.get("windows_per_s"),
         "out": str(out)}
    with open(root / "results.jsonl", "a") as fh:
        fh.write(json.dumps(f) + "\n")
    return f


def write_table(root, results):
    rows = sorted(results, key=lambda r: (r["best_dev_f1"] or -1), reverse=True)
    lines = ["| run | stage | lr | rank | rare_x | seed | dev F1 | P | R | JSON-val | quote-verb | win/s |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['stage']} | {r['lr']:g} | {r['rank']} | {r['rare_x']} | {r['seed']} | "
                     f"{r['best_dev_f1']} | {r['dev_p']} | {r['dev_r']} | {r['json_validity']} | "
                     f"{r['quote_verbatim']} | {r['windows_per_s']} |")
    (root / "results.md").write_text("\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=str(RUNS))
    ap.add_argument("--plan", action="store_true")
    ap.add_argument("--stage", default="all", choices=["A", "B", "C", "all"])
    a = ap.parse_args()
    root = Path(a.root)

    root.mkdir(parents=True, exist_ok=True)
    results = []
    if (root / "results.jsonl").exists():
        results = [json.loads(l) for l in open(root / "results.jsonl")]
    def prior(stage):
        return [r for r in results if r["stage"] == stage and r["best_dev_f1"] is not None]

    if a.stage == "all":
        plans = {"A": stage_a()}
    elif a.stage == "A":
        plans = {"A": stage_a()}
    elif a.stage == "B":
        a_recs = sorted(prior("A"), key=lambda r: r["best_dev_f1"], reverse=True)[:3]
        plans = {"B": stage_b(a_recs, a_recs[0]["lr"] if a_recs else None)}
    else:
        ranked = sorted(results, key=lambda r: (r["best_dev_f1"] or -1), reverse=True)
        plans = {"C": stage_c(ranked[0]) if ranked else []}

    if a.plan:
        for stage in plans:
            for r in plans[stage]:
                print(f"{r['name']:34s} lr={r['lr']:<8g} rank={r['rank']:<4d} alpha={r['alpha']:<4d} "
                      f"epochs={r['epochs']} seed={r['seed']} rare_x={r['rare_x']}")
            print(f"  -> {len(plans[stage])} runs")
        if a.stage == "all":
            a_recs = sorted(prior("A"), key=lambda r: r["best_dev_f1"], reverse=True)[:3]
            if a_recs:
                b = stage_b(a_recs, a_recs[0]["lr"])
                print(f"(Stage B would be {len(b)} runs given the current top-3: "
                      f"{[r['name'] for r in a_recs]})")
            else:
                a_names = sorted({(f"lr{lr_tag(lr)}-r{r}") for lr in LRS_A for r in RANKS_A})
                print(f"(Stage A has no results yet; Stage B follows the top-3 of its {len(LRS_A)*len(RANKS_A)} runs)")
        return

    def run_plan(plan):
        for r in plan:
            out = root / r["name"]
            if (out / "final.json").exists():
                print("skip (done):", r["name"])
                if r["name"] not in {x["name"] for x in results}:
                    results.append(record(root, r))
                continue
            print("run:", r["name"], flush=True)
            t0 = time.time()
            rc = subprocess.run(cmd(r, root)).returncode
            print(f"  rc={rc} in {time.time()-t0:.0f}s")
            if rc != 0:
                print("  FAILED; continuing (final.json absent -> a rerun resumes it)")
                continue
            results.append(record(root, r))
            write_table(root, results)
            if r["stage"] == "B":
                import shutil
                a_recs = sorted([x for x in results if x["stage"] == "A" and x["best_dev_f1"] is not None],
                                key=lambda x: x["best_dev_f1"], reverse=True)
                for x in a_recs[3:]:
                    shutil.rmtree(root / x["name"], ignore_errors=True)
                    print("  disk policy: removed non-best Stage-A adapter", x["name"])

    if a.stage == "all":
        run_plan(plans["A"])
        a_recs = sorted(prior("A"), key=lambda r: r["best_dev_f1"], reverse=True)[:3]
        if a_recs:
            run_plan(stage_b(a_recs, a_recs[0]["lr"]))
            best = sorted(results, key=lambda r: (r["best_dev_f1"] or -1), reverse=True)[0]
            run_plan(stage_c(best))
    else:
        for stage in plans:
            run_plan(plans[stage])
    write_table(root, results)

    # Stage C tail: eval_student on the blind test gold per seed.
    if a.stage == "C" or a.stage == "all":
        for r in [x for x in results if x["stage"] == "C"]:
            adapter = Path(r["out"]) / "best"
            if not adapter.exists():
                continue
            print("eval_student:", r["name"])
            subprocess.run([sys.executable, str(ROOT / "tools/train/eval_student.py"),
                            "--adapter", str(adapter), "--out", str(Path(r["out"]) / "test_preds.jsonl")])


if __name__ == "__main__":
    main()
