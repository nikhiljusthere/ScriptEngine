#!/usr/bin/env python3
"""Worker (opencode) status from opencode's own records: no screenshots.

    python franchise_kit/tools/oc_status.py --title "MARVEL C4"            # newest session whose title matches
    python franchise_kit/tools/oc_status.py --session ses_... --stopped-after 180

Prints one line: STATE age=<s> newest=<type> | text: <last visible assistant text> | last tool: <cmd>
STATE is STOPPED when the newest record is an `idle` marker, or a completed assistant
message with nothing newer for --stopped-after seconds; otherwise WORKING. Exit code:
0 WORKING, 3 STOPPED, 2 no session.

Reads ~/.local/share/opencode/opencode.db READ-ONLY (session_v2 + session_message
only; never the account/credential tables) and the tail of the opencode log.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import time
from pathlib import Path

DB = Path.home() / ".local/share/opencode/opencode.db"
LOG = Path.home() / ".local/share/opencode/log/opencode.log"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--title", help="substring of the session title")
    ap.add_argument("--session", help="exact session id")
    ap.add_argument("--stopped-after", type=int, default=180)
    a = ap.parse_args()
    c = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    if a.session:
        sid = a.session
    else:
        row = c.execute("select id from session_v2 where title like ? order by time_updated desc limit 1",
                        (f"%{a.title or ''}%",)).fetchone()
        if not row:
            print("NO-SESSION")
            return 2
        sid = row[0]
    rows = c.execute("select type, time_created, data from session_message where session_id=? "
                     "order by seq desc limit 40", (sid,)).fetchall()
    if not rows:
        print("NO-SESSION")
        return 2
    now = time.time() * 1000
    typ, created, data = rows[0]
    tm = json.loads(data).get("time") or {}
    last = max(created, tm.get("completed") or 0, tm.get("streamed") or 0)
    age = int((now - last) / 1000)
    stopped = typ == "idle" or (typ == "assistant" and bool(tm.get("completed")) and age >= a.stopped_after)
    text = ""
    for t, _, d in rows:
        if t != "assistant":
            continue
        for part in json.loads(d).get("content") or []:
            if part.get("type") == "text" and part.get("text", "").strip():
                text = part["text"].strip().replace("\n", " ")
                break
        if text:
            break
    tool = ""
    try:
        with LOG.open("rb") as f:
            f.seek(0, 2)
            f.seek(max(0, f.tell() - 200_000))
            for line in f.read().decode("utf-8", "replace").splitlines():
                if 'message="spawning process"' in line:
                    m = re.search(r'args="(.*?)" cwd', line)
                    tool = (m.group(1) if m else line)[-160:]
    except OSError:
        pass
    state = "STOPPED" if stopped else "WORKING"
    print(f"{state} session={sid} age={age}s newest={typ} | text: {text[:400]} | last tool: {tool}")
    return 3 if stopped else 0


if __name__ == "__main__":
    sys.exit(main())
