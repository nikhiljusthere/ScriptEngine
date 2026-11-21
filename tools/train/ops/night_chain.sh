#!/bin/bash
# Overnight correct-and-verify loop (owner 2026-09-29): opencode drafts (3 x 500) +
# teacher drafts (500) -> Q8 per-window corrector (judges each draft row, adds
# missed events) -> merge -> Q8 row-by-row wiki check. Rounds repeat while the
# opencode annotators are still writing. Adjudication by Claude follows.
# 2026-09-30: server is now -np 2 (serve_q8_best.sh); batch steps use --workers 1
# so the opencode agent session keeps one slot. Fallback restart uses the best config.
cd /home/goblin/ScriptEngine; S=/tmp/jjk100/night_status; G=series/jjk/training/gold; T=series/jjk/training/v1/train.jsonl
PY=scriptengine/.venv/bin/python
echo "wait small chain $(date +%T)" > $S
true  # small chain finished 2026-09-29
curl -sf http://127.0.0.1:8090/health >/dev/null || { setsid nohup /home/goblin/ScriptEngine/tools/train/ops/serve_q8_best.sh > /tmp/jjk100/q6_server_N.log 2>&1 < /dev/null &
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8090/health >/dev/null && break; sleep 10; done; }
idle=0; last=-1
while true; do
  for m in spacebunny mimo nemotron; do $PY tools/train/drafts.py opencode --model $m --out $G/draft_$m.jsonl; done
  now=$(cat $G/draft_spacebunny.jsonl $G/draft_mimo.jsonl $G/draft_nemotron.jsonl | wc -l)
  echo "round start $(date +%T) opencode windows=$now" >> $S
  $PY tools/train/verify_rows.py --data $T --cand $G/draft_spacebunny.jsonl $G/draft_mimo.jsonl $G/draft_nemotron.jsonl $G/draft_teacher500.jsonl \
    --out $G/stage1_extra.jsonl --workers 1 >> /tmp/jjk100/night_stage1.log 2>&1
  $PY tools/train/drafts.py merge --data $T --cand $G/draft_spacebunny.jsonl $G/draft_mimo.jsonl $G/draft_nemotron.jsonl $G/draft_teacher500.jsonl \
    --verify $G/stage1_extra.jsonl --out $G/stage2_extra.jsonl >> $S 2>&1
  $PY tools/train/verify_row_wiki.py --data $T --cand $G/stage2_extra.jsonl --out $G/verifyrow_extra.jsonl --workers 1 >> /tmp/jjk100/night_stage2.log 2>&1
  echo "round done $(date +%T) stage1=$(wc -l < $G/stage1_extra.jsonl) stage2=$(wc -l < $G/verifyrow_extra.jsonl)" >> $S
  [ "$now" -ge 1500 ] && break
  if [ "$now" -eq "$last" ]; then idle=$((idle+1)); else idle=0; fi
  [ "$idle" -ge 6 ] && { echo "opencode stopped growing at $now windows" >> $S; break; }
  last=$now; sleep 600
done
echo DONE >> $S
