#!/usr/bin/env python3
"""Live monitor for the universal labeling run (owner 2026-10-05: "a live
monitor that I can see in Brave ... progress of 3000 windows, and update as
each window is verified and logged").

Read-only: every request re-reads the files on disk -- the drafter outputs
(draft_frozen*.jsonl), the verifier's saved records (pool_verified.jsonl /
test_verified.jsonl, written only by verify_save.py), Claude's audit log
(pool_audit.jsonl), the drafting chain's status file, the running processes
and nvidia-smi. Standard library only.

    scriptengine/.venv/bin/python tools/train/live_monitor.py [--port 8770]
    -> http://localhost:8770
"""
import argparse
import json
import os
import subprocess
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WIKIS = ["opm", "csm", "marvel", "mcu", "berserk", "bleach", "db", "onepiece"]
TEST_WIKIS = WIKIS + ["hxh"]
STATUS = ROOT / "series/jjk/training/pools_draft.status"


def lines(path):
    try:
        with open(path) as f:
            return [l for l in f if l.strip()]
    except OSError:
        return []


def records(path):
    out = []
    for l in lines(path):
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out


def wiki_state(s, pool):
    lab = ROOT / "series" / s / "training" / "labels"
    src = lab / ("pool_in.jsonl" if pool == "pool" else "test_in.jsonl")
    drafts = lab / ("draft_frozen.jsonl" if pool == "pool" else "draft_frozen_test.jsonl")
    ver = records(lab / f"{pool}_verified.jsonl")
    audit = records(lab / f"{pool}_audit.jsonl")
    draft_rows = sum(len(r.get("events") or []) for r in records(drafts)) if pool == "pool" else None
    verdicts = {"keep": 0, "fix": 0, "reject": 0}
    added = final_rows = 0
    for r in ver:
        for x in r.get("draft") or []:
            v = x.get("verdict")
            if v in verdicts:
                verdicts[v] += 1
        added += len(r.get("added") or [])
        final_rows += len(r.get("final") or [])
    return {"wiki": s, "total": len(lines(src)), "drafted": len(lines(drafts)),
            "verified": len(ver), "audited_corrections": len({a["id"] for a in audit}),
            "verdicts": verdicts, "added": added, "final_rows": final_rows,
            "draft_rows": draft_rows,
            "mtime": max([p.stat().st_mtime for p in (drafts, lab / f"{pool}_verified.jsonl") if p.exists()] or [0])}


def recent_verified(n=14):
    feed = []
    for pool, wikis in (("pool", WIKIS), ("test", TEST_WIKIS)):
        for s in wikis:
            lab = ROOT / "series" / s / "training" / "labels"
            audited = {a["id"] for a in records(lab / f"{pool}_audit.jsonl")}
            for r in records(lab / f"{pool}_verified.jsonl")[-n:]:
                feed.append({"wiki": s, "pool": pool, "id": r["id"], "page": r.get("page"),
                             "section": r.get("section"), "saved_at": r.get("saved_at") or "",
                             "final": [f"{e.get('subject')} {e.get('verb')} {e.get('object') or ''}".strip()
                                       for e in r.get("final") or []],
                             "added": len(r.get("added") or []),
                             "corrected": r["id"] in audited,
                             "order": (r.get("saved_at") or "", os.path.getmtime(lab / f"{pool}_verified.jsonl"))})
    feed.sort(key=lambda x: x["order"], reverse=True)
    for x in feed:
        x.pop("order")
    return feed[:n]


def processes():
    procs = []
    for pid in os.listdir("/proc"):
        if not pid.isdigit():
            continue
        try:
            cmd = open(f"/proc/{pid}/cmdline", "rb").read().replace(b"\0", b" ").decode(errors="replace")
        except OSError:
            continue
        if "draft_v2.py" in cmd and "--series" in cmd:
            parts = cmd.split()
            ser = parts[parts.index("--series") + 1]
            kind = "test" if "test_in" in cmd else "pool"
            procs.append({"what": f"35B drafter: {ser} ({kind})", "pid": int(pid)})
        elif "opencode run" in cmd and "--title" in cmd and "bin/opencode" in cmd:
            title = cmd.split("--title", 1)[1].split(" Read ")[0].strip()
            model = cmd.split(" -m ", 1)[1].split()[0] if " -m " in cmd else "?"
            procs.append({"what": f"verifier session: {title} [{model}]", "pid": int(pid)})
        elif "ninfer-serve" in cmd:
            port = cmd.split("--port", 1)[1].split()[0] if "--port" in cmd else "?"
            ctx = cmd.split("--max-context", 1)[1].split()[0] if "--max-context" in cmd else "?"
            name = "35B" if "35b" in cmd else ("27B" if "27b" in cmd else "model")
            procs.append({"what": f"ninfer {name} server :{port} (ctx {ctx})", "pid": int(pid)})
    return procs


def gpu():
    try:
        out = subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu",
                              "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        u, m, t, c = [x.strip() for x in out.strip().split(",")]
        return {"util": int(u), "mem_used": int(m), "mem_total": int(t), "temp": int(c)}
    except Exception:  # noqa: BLE001
        return None


def state():
    pools = [wiki_state(s, "pool") for s in WIKIS]
    tests = [wiki_state(s, "test") for s in TEST_WIKIS]
    tot = lambda rows, k: sum(r[k] for r in rows)  # noqa: E731
    return {"now": time.strftime("%Y-%m-%d %H:%M:%S"),
            "pool": {"wikis": pools, "total": tot(pools, "total"), "drafted": tot(pools, "drafted"),
                     "verified": tot(pools, "verified"), "corrections": tot(pools, "audited_corrections")},
            "test": {"wikis": tests, "total": tot(tests, "total"), "drafted": tot(tests, "drafted"),
                     "verified": tot(tests, "verified"), "corrections": tot(tests, "audited_corrections")},
            "status": [l.rstrip() for l in lines(STATUS)[-8:]],
            "processes": processes(), "gpu": gpu(), "feed": recent_verified()}


PAGE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Labeling Monitor</title>
<style>
:root{--bg:#0f1115;--card:#171a21;--ink:#e6e8ee;--mute:#8b92a3;--line:#262b36;
--draft:#5b8def;--ver:#3fb97f;--fix:#e0a63a;--bad:#e05d5d;--track:#232834}
@media (prefers-color-scheme: light){:root{--bg:#f6f7f9;--card:#fff;--ink:#1b1f27;--mute:#5d6576;
--line:#e3e6ec;--track:#eceff4}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);
font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif;padding:20px 16px}
h1{font-size:20px;margin:0}h2{font-size:15px;margin:0 0 10px}
.top{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px;margin-bottom:16px}
.mute{color:var(--mute)}.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:14px}
.big{display:flex;gap:22px;flex-wrap:wrap;margin:6px 0 12px}.big div{min-width:90px}
.big b{display:block;font-size:26px;font-variant-numeric:tabular-nums}
.bar{position:relative;height:10px;background:var(--track);border-radius:6px;overflow:hidden}
.bar i{position:absolute;left:0;top:0;bottom:0;border-radius:6px}
.row{display:grid;grid-template-columns:78px 1fr 92px;gap:10px;align-items:center;margin:7px 0}
.row .n{font-variant-numeric:tabular-nums;text-align:right;color:var(--mute);font-size:12px}
.legend{display:flex;gap:14px;font-size:12px;color:var(--mute);margin-top:8px;flex-wrap:wrap}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:5px;vertical-align:-1px}
pre{margin:0;white-space:pre-wrap;font:12px/1.5 ui-monospace,Menlo,monospace;color:var(--mute)}
.feed div{border-top:1px solid var(--line);padding:7px 0;font-size:13px}.feed div:first-child{border:0}
.tag{font-size:11px;padding:1px 6px;border-radius:9px;background:var(--track);color:var(--mute);margin-left:4px}
.tag.fix{background:var(--fix);color:#111}.ev{color:var(--mute);font-size:12px}
.ok{color:var(--ver)}.warn{color:var(--bad)}
</style></head><body>
<div class="top"><h1>Labeling monitor <span class="mute" style="font-size:13px">universal event windows</span></h1>
<span class="mute" id="now">connecting...</span></div>
<div class="grid">
 <div class="card" style="grid-column:1/-1"><h2>Training pools &mdash; 3,000 windows</h2>
  <div class="big" id="poolbig"></div><div id="poolrows"></div>
  <div class="legend"><span><span class="dot" style="background:var(--draft)"></span>drafted (35B)</span>
  <span><span class="dot" style="background:var(--ver)"></span>verified + logged</span>
  <span><span class="dot" style="background:var(--fix)"></span>corrected by Claude's audit</span></div></div>
 <div class="card"><h2>Held-out test windows</h2><div class="big" id="testbig"></div><div id="testrows"></div></div>
 <div class="card"><h2>Running now</h2><div id="procs"></div><h2 style="margin-top:14px">Drafting log</h2><pre id="status"></pre></div>
 <div class="card"><h2>Latest verified windows</h2><div class="feed" id="feed"></div></div>
</div>
<script>
const $=id=>document.getElementById(id), fmt=n=>n.toLocaleString();
function rows(el, wikis){el.innerHTML=wikis.map(w=>{const t=w.total||1;
 return `<div class="row"><span>${w.wiki}</span><div class="bar">
 <i style="width:${100*w.drafted/t}%;background:var(--draft);opacity:.45"></i>
 <i style="width:${100*w.verified/t}%;background:var(--ver)"></i>
 <i style="width:${100*w.audited_corrections/t}%;background:var(--fix)"></i></div>
 <span class="n">${w.verified}/${w.drafted}/${w.total}</span></div>`}).join("")}
function big(el,p){const pct=x=>p.total?(100*x/p.total).toFixed(1)+"%":"0%";
 el.innerHTML=`<div><b>${fmt(p.drafted)}</b><span class="mute">drafted · ${pct(p.drafted)}</span></div>
 <div><b class="ok">${fmt(p.verified)}</b><span class="mute">verified · ${pct(p.verified)}</span></div>
 <div><b>${fmt(p.corrections)}</b><span class="mute">audit corrections</span></div>
 <div><b>${fmt(p.total)}</b><span class="mute">windows</span></div>`}
async function tick(){try{const s=await (await fetch("/api/state",{cache:"no-store"})).json();
 $("now").textContent="updated "+s.now;
 big($("poolbig"),s.pool);rows($("poolrows"),s.pool.wikis);big($("testbig"),s.test);rows($("testrows"),s.test.wikis);
 const g=s.gpu;$("procs").innerHTML=(s.processes.length?s.processes.map(p=>`<div>&bull; ${p.what} <span class="mute">pid ${p.pid}</span></div>`).join(""):'<div class="warn">nothing running</div>')
  +(g?`<div class="mute" style="margin-top:6px">GPU ${g.util}% · ${fmt(g.mem_used)}/${fmt(g.mem_total)} MiB · ${g.temp}°C</div>`:"");
 $("status").textContent=s.status.join("\n");
 $("feed").innerHTML=s.feed.length?s.feed.map(f=>`<div><b>${f.wiki}</b>${f.pool=="test"?'<span class="tag">test</span>':""}
  ${f.corrected?'<span class="tag fix">corrected</span>':""}${f.added?`<span class="tag">+${f.added} missed</span>`:""}
  <span class="mute">${f.saved_at}</span><br>${f.page||""}${f.section?" / "+f.section:""}
  <div class="ev">${f.final.length?f.final.join(" · "):"no events (earned empty)"}</div></div>`).join(""):'<span class="mute">none yet</span>';
}catch(e){$("now").textContent="monitor server unreachable";}}
tick();setInterval(tick,3000);
</script></body></html>"""


class H(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        if self.path.startswith("/api/state"):
            body, ctype = json.dumps(state()).encode(), "application/json"
        else:
            body, ctype = PAGE.encode(), "text/html; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *a):
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8770)
    a = ap.parse_args()
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
