#!/bin/bash
# Stage A of the weight-space edit (tools/train/wsp_edit.py) on the step-5 student, unattended:
# wait for the step-5 chain to exit, refuse to start if anything else holds the GPU, then diagnose -> collect
# -> a small edit sweep scored on dev_pool. No test predictions here: test is scored once, by hand, on the
# edit picked from this sweep (then `wsp_edit.py export` for the standalone checkpoint).
#   setsid nohup bash tools/train/wsp_run.sh <step5 chain PID> > $OUT/run.log 2>&1 < /dev/null &
set -u
WAIT_PID=${1:-}
REPO=$(cd "$(dirname "$0")/../.." && pwd)
P=~/train-env/bin/python
M=/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236235762e1c871ad0ccb60c8ee5ba337b9a
D=/home/goblin/ScriptEngine/series/universal/training/student_v2_short
RUNS=/mnt/PROJECTS/student_runs_big
OUT=${OUT:-$RUNS/wsp-v2}
export PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
mkdir -p "$OUT"
cd "$REPO"

if [ -n "$WAIT_PID" ]; then
  echo "=== waiting for PID $WAIT_PID $(date -Is)"
  while kill -0 "$WAIT_PID" 2>/dev/null; do sleep 60; done
fi
if [ -n "$(nvidia-smi --query-compute-apps=pid --format=csv,noheader)" ]; then
  echo "=== GPU busy, not starting: $(nvidia-smi --query-compute-apps=pid,used_memory --format=csv,noheader | tr '\n' ' ')"
  exit 3
fi

# the seed whose best adapter scored higher on dev_pool during step 5
BEST=$($P - <<EOF
import json
from pathlib import Path
c = [(json.loads((Path("$RUNS") / f"9B-v2-short-a16-lr1e-4-s{s}" / "final.json").read_text()).get("best_dev_f1") or -1, s)
     for s in (1, 2) if (Path("$RUNS") / f"9B-v2-short-a16-lr1e-4-s{s}" / "final.json").exists()]
print(f"$RUNS/9B-v2-short-a16-lr1e-4-s{max(c)[1]}/best" if c else "")
EOF
)
[ -n "$BEST" ] && [ -d "$BEST" ] || { echo "=== no step-5 adapter found"; exit 4; }
echo "=== student adapter $BEST $(date -Is)"

$P tools/train/wsp_edit.py diag-set --dev $D/dev.jsonl --dev-pool $D/dev_pool.jsonl --train $D/train.jsonl \
  --n-train 300 --out $OUT/diag.jsonl || exit 5
$P tools/train/eval_base_v2.py --model $M --adapter $BEST --in $OUT/diag.jsonl --out $OUT/diag_preds.jsonl || exit 6
$P tools/train/wsp_edit.py positions --gold $OUT/diag.jsonl --pred $OUT/diag_preds.jsonl --out $OUT/pos.jsonl || exit 7
$P tools/train/wsp_edit.py collect --model $M --adapter $BEST --gold $OUT/diag.jsonl --pos $OUT/pos.jsonl \
  --out $OUT/acts.pt || exit 8
for pair in "bad_stop good_stop" "continue_over continue_ok"; do
  set -- $pair
  echo "=== report $1 vs $2"; $P tools/train/wsp_edit.py report --acts $OUT/acts.pt --bad $1 --ref $2
done

# sweep: name bad ref layers k alpha. "merged" is the zero edit (adapter merged, nothing changed), the
# baseline every point is compared with; the first real point is the paper's shape (2 layers x 64 columns).
SWEEP="merged:bad_stop:good_stop:0:0:1
stop-t2-k64-a1:bad_stop:good_stop:top2:64:1
stop-t2-k256-a1:bad_stop:good_stop:top2:256:1
stop-t4-k64-a1:bad_stop:good_stop:top4:64:1
stop-t2-k64-a2:bad_stop:good_stop:top2:64:2
stop-t1-k64-a1:bad_stop:good_stop:top1:64:1
over-t2-k64-a1:continue_over:continue_ok:top2:64:1"
PREDS=()
for line in $SWEEP; do
  IFS=: read -r name bad ref layers k alpha <<< "$line"
  echo "=== sweep $name $(date -Is)"
  $P tools/train/wsp_edit.py make-edit --model $M --adapter $BEST --acts $OUT/acts.pt --bad $bad --ref $ref \
    --layers $layers --k $k --alpha $alpha --out $OUT/edit-$name.pt || continue
  $P tools/train/eval_base_v2.py --model $M --adapter $BEST --edit $OUT/edit-$name.pt --in $D/dev_pool.jsonl \
    --out $OUT/pool-$name.jsonl && PREDS+=(--pred $OUT/pool-$name.jsonl)
done
echo "=== unedited adapter on dev_pool $(date -Is)"
$P tools/train/eval_base_v2.py --model $M --adapter $BEST --in $D/dev_pool.jsonl --out $OUT/pool-adapter.jsonl \
  && PREDS=(--pred $OUT/pool-adapter.jsonl "${PREDS[@]}")
echo "=== scores $(date -Is)"
# the teacher drafts (series/<s>/training/labels/draft_frozen.jsonl) live only in the main checkout; run from a
# worktree, score_subsets --teacher silently prints no teacher line (step-5 handoff 2026-11-06 21:25)
$P - "${PREDS[@]}" <<EOF
import sys
from pathlib import Path
sys.path.insert(0, "tools/train")
import score_subsets as ss
ss.ROOT = Path("/home/goblin/ScriptEngine")
sys.argv = ["score_subsets.py", "--gold", "$D/dev_pool.jsonl", *sys.argv[1:], "--teacher"]
ss.main()
EOF
$P tools/train/score_layers_v2.py --gold $D/dev_pool.jsonl "${PREDS[@]}"
echo "=== STAGE A DONE $(date -Is)"
