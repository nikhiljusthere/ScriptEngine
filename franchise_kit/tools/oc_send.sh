#!/usr/bin/env bash
# Type a message into the opencode worker's TUI and verify it was delivered.
#
#   franchise_kit/tools/oc_send.sh "<window title substring>" <message-file> [session-title-substring]
#
# Needs the owner's xdotool permission. Proven method (2026-09-28):
#   - activate the window, confirm it is the active one, then type WITHOUT --window
#     (`xdotool type --window` sends synthetic events gnome-terminal IGNORES: three
#     messages were silently lost that way);
#   - only when the worker is idle (text typed mid-turn is not reliably queued);
#   - delivery is verified by finding the text as a `type='user'` row in opencode.db.
# The message file must be a single line (a newline would submit early).
set -u
WIN_TITLE=$1; MSG=$2; SESS=${3:-$1}
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PY:-/home/goblin/ScriptEngine/scriptengine/.venv/bin/python}
export DISPLAY=${DISPLAY:-:0}

[ "$(tr -cd '\n' < "$MSG" | wc -c)" -le 1 ] || { echo "message has internal newlines; refuse"; exit 2; }
"$PY" "$HERE/oc_status.py" --title "$SESS" --stopped-after 30 >/dev/null; st=$?
[ "$st" -eq 3 ] || { echo "worker is not idle (status rc=$st); refuse to type mid-turn"; exit 3; }

W=$(xdotool search --onlyvisible --name "$WIN_TITLE" | tail -1)
[ -n "$W" ] || { echo "no window matching '$WIN_TITLE'"; exit 4; }
xdotool windowactivate --sync "$W"; sleep 0.4
[ "$(xdotool getactivewindow)" = "$W" ] || { echo "could not activate window $W"; exit 5; }
printf '%s' "$(cat "$MSG")" > /tmp/oc_send_msg.$$
xdotool type --delay 6 --clearmodifiers --file /tmp/oc_send_msg.$$
sleep 0.3; xdotool key --clearmodifiers Return
NEEDLE=$(head -c 60 "$MSG")
for i in $(seq 1 12); do
  n=$("$PY" - "$SESS" "$NEEDLE" <<'EOF'
import sqlite3, sys, pathlib
db = pathlib.Path.home() / ".local/share/opencode/opencode.db"
c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
sid = c.execute("select id from session_v2 where title like ? order by time_updated desc limit 1", (f"%{sys.argv[1]}%",)).fetchone()
print(c.execute("select count(*) from session_message where session_id=? and type='user' and data like ?",
                (sid[0] if sid else "", f"%{sys.argv[2][:40]}%")).fetchone()[0])
EOF
)
  [ "${n:-0}" -gt 0 ] && { echo "DELIVERED (window $W, ~$((i*5))s)"; rm -f /tmp/oc_send_msg.$$; exit 0; }
  sleep 5
done
rm -f /tmp/oc_send_msg.$$
echo "NOT DELIVERED after 60s: check the TUI"; exit 6
