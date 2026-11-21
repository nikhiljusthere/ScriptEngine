#!/bin/bash
# Smaller verified dataset (owner 2026-09-29): 400 pilot + 600 selected windows.
# Q6 extracts the unlabelled ones; the row-by-row Q6 + wiki verifier checks all 1,000.
cd /home/goblin/ScriptEngine; S=/tmp/jjk100/small_status; G=series/jjk/training/gold
echo "wait runD $(date +%T)" > $S
until grep -q DONE /tmp/jjk100/runD_status; do sleep 20; done
NP=6 CTX=65536 setsid nohup /tmp/jjk100/serve_q6.sh > /tmp/jjk100/q6_server_S.log 2>&1 < /dev/null &
for i in $(seq 1 60); do curl -sf http://127.0.0.1:8090/health >/dev/null && break; sleep 10; done
echo "q6 up $(date +%T)" >> $S
scriptengine/.venv/bin/python tools/train/verify_row_wiki.py --data series/jjk/training/v1/train.jsonl \
  --cand $G/cand_q6_pilot400.jsonl --ids $G/adj_order.json --out $G/verifyrow_1000.jsonl --workers 2 > /tmp/jjk100/verifyrow_a.log 2>&1 &
VA=$!
scriptengine/.venv/bin/python tools/train/qwen_worker.py --data series/jjk/training/v1/train.jsonl \
  --ids $G/select_600.json --out $G/cand_q6_train.jsonl --workers 5 --effort medium > /tmp/jjk100/q6_select.log 2>&1
echo "extract rc=$? $(date +%T) rows=$(wc -l < $G/cand_q6_train.jsonl)" >> $S
scriptengine/.venv/bin/python tools/train/verify_row_wiki.py --data series/jjk/training/v1/train.jsonl \
  --cand $G/cand_q6_train.jsonl --ids $G/select_600.json --out $G/verifyrow_600.jsonl --workers 4 > /tmp/jjk100/verifyrow_b.log 2>&1
echo "verify select600 done $(date +%T)" >> $S
wait $VA; echo "verify pilot400 done $(date +%T) windows=$(cat $G/verifyrow_1000.jsonl $G/verifyrow_600.jsonl | wc -l)" >> $S
echo DONE >> $S
