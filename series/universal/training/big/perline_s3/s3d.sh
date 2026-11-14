#!/bin/bash
# Per-line run 2 on the refreshed train data (2026-11-14 train-window gold audit: 184 windows, fixes G133-G153), owner go
# "Start training". Same recipe and seed as perline-s1 so the only change is the corrected labels. Live output on ext4,
# copied to the HDD runs folder at the end.
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
export PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
L=/home/goblin/student_runs_local/jjk_side; J=/home/goblin/student_runs_big/jjk_side; M=/home/goblin/models/Qwen3.5-9B; PY=~/train-env/bin/python
log() { echo "=== $* $(date -Is)" | tee -a "$L/s3d.driver.log" >> "$J/s3.driver.log"; }
log "s3d train start (local)"
$PY tools/train/sft_qwen.py --model $M --train "$L/s3data/train.jsonl" --dev "$L/s3data/dev_mon.jsonl" --out "$L/perline-s2" \
  --lr 1e-4 --rank 16 --alpha 16 --dropout 0.05 --epochs 3 --patience 99 --seed 1 --loss-norm step --micro-batch 1 --accum 16 \
  --max-len 4096 --save-last > "$L/perline-s2.log" 2>&1
log "s3d train rc=$?"
$PY tools/train/eval_base_v2.py --model $M --adapter "$L/perline-s2/last" --in "$L/s3data/holdout.jsonl" --out "$L/perline-s2/holdout_preds.jsonl" --batch 8 > "$L/perline-s2.holdout.log" 2>&1
log "s3d perline holdout preds rc=$?"
mkdir -p "$J/refreshed" && cp -r "$L/perline-s2" "$L/perline-s2.log" "$L/perline-s2.holdout.log" "$L/s3data" "$J/refreshed/" && log "s3d copied to HDD rc=$?"
log "S3D DONE"
