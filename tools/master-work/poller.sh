# tools/master-work/poller.sh — the A-loop, shell-only (one-time bootstrap artifact; B commits it; T0 exercises it)
cd /home/goblin/ScriptEngine
STATE=plan/state.md; DEC=plan/decisions.md; STOP=reports/master-work/STOP; LOG=reports/master-work/a_wake_log.md; WORKLOG=reports/master-work/work_log.md
model=up; pane=""; stop_seen=""; last_wl=$(stat -c %Y $WORKLOG 2>/dev/null || echo 0)
wake() { local ev="$1" sid="a-$(date +%s)";   # judgment events → fresh one-shot A (charter in CONTROL.md)
  pi -p --session-id "$sid" "You are A (charter: plan/CONTROL.md). Event: $ev. Read plan/state.md, plan/decisions.md (head -20), reports/master-work/work_log.md (tail -20). Rule/act per the charter: write state.md §state FIRST, then the DEC line to decisions.md (prepend, newest first; include the exact ESC token). Never execute campaign work. Then stop." >>$LOG 2>&1
  echo "[$(date -Is)] EVENT $ev → a_session=$sid" >> $LOG; }
while :; do
  now=$(date +%s)
  # 1. model health (§6.5): a DOWN model gates A's one-shots and suspends B-staleness
  mup=$(curl -s -m 2 -o /dev/null -w '%{http_code}' http://127.0.0.1:18080/health)
  [ "$mup" = 200 ] && mup=up || mup=down
  if [ "$mup" = down ] && [ "$model" = up ]; then
    sed -i 's/^model: up.*/model: down/' $STATE
    setsid nohup tools/master-work/ninfer_restart.sh >> /tmp/ninfer-restart.log 2>&1 &   # scripted restart (§6.5)
    echo "[$(date -Is)] EVENT MODEL-DOWN (restart launched) → a_session=-" >> $LOG
  elif [ "$mup" = up ] && [ "$model" = down ]; then
    sed -i 's/^model: down.*/model: up/' $STATE; echo "[$(date -Is)] EVENT MODEL-UP → a_session=-" >> $LOG
    # lost-flip edge: a B-DOWN that occurred while the model was down was not woken (model gate);
    # re-check now — if the pane is still down, fire the deferred B-DOWN wake
    [ "$(tmux has-session -t work 2>/dev/null && echo up || echo down)" = down ] && pane= && wake "B-DOWN (pane down since model-down; fit-check §6.2)"
  fi
  model=$mup
  # 2. pane liveness
  live=$(tmux has-session -t work 2>/dev/null && echo up || echo down)
  if [ "$live" != "$pane" ]; then
    if [ "$live" = down ] && [ "$mup" = up ]; then wake "B-DOWN (fit-check §6.2: resume pi --session <b_session> if it fits, else fresh spawn §4.3)"; else echo "[$(date -Is)] EVENT B-${live^^} → a_session=-" >> $LOG; fi
    pane=$live; fi
  # 3. STOP appearance/disappearance (mechanical — no LLM)
  if [ -e $STOP ] && [ -z "$stop_seen" ]; then
    echo "[$(date -Is)] EVENT STOP: $(head -1 $STOP)" >> $LOG; stop_seen=1
    pkill -f 'tools/pcloop/loop.py'; tmux kill-session -t work 2>/dev/null
  elif [ ! -e $STOP ] && [ -n "$stop_seen" ]; then echo "[$(date -Is)] EVENT STOP-CLEARED" >> $LOG; stop_seen=""; fi
  # 4. new ESC: newest ESC line with no matching DEC (judgment — wake A; gated on model up)
  esc=$(grep -oP '^\[.*\] ESC \K[^: ]+' $STATE 2>/dev/null | tail -1)
  if [ -n "$esc" ] && ! grep -q "DEC $esc" $DEC && [ "$mup" = up ]; then wake "ESC $esc"; fi
  # 5. B liveness — UNIT-AWARE (council fix 2): stale = no work_log line for max(300, ETA); model-DOWN never counts
  eta=$(sed -n 's/.*ETA: *\([0-9]*\).*/\1/p' $STATE | tail -1); eta=${eta:-0}; lim=$(( eta > 300 ? eta : 300 ))   # newest ETA line (B appends them to §B updates, §4.3)
  wl=$(stat -c %Y $WORKLOG 2>/dev/null || echo $now)
  if [ "$live" = up ] && [ "$mup" = up ] && [ $(( now - wl )) -gt $lim ]; then
    last_wl=$now; wake "B-STALE (no work_log line for >${lim}s; ETA-aware, model up — decide: extend ETA / VETO / REDO / kill+respawn §6.1-6.2)"; last_wl=$(stat -c %Y $WORKLOG)
  fi
  [ "$wl" -gt "$last_wl" ] && last_wl=$wl
  sleep 60
done
