#!/bin/bash
# After a blind reader finishes chunk NN: id check, score against the gold, build the third-look input.
#   blind/after_reader.sh NN        (run from docs/train_audit_2026-11-14)
set -e
n=$1
python3 blind/check_ids.py blind/chunks/chunk_${n}_input.jsonl blind/chunks/chunk_${n}_blind.jsonl ~/student_runs_local/jjk_side/s2data/train.jsonl
bash blind/supervise.sh $n
python3 adj/make_adj_input.py $n
