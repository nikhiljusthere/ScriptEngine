#!/usr/bin/env python3
"""Live progress monitor for the MARVEL 100% egress batch (2026-09-26/27).

Serves a self-updating dashboard at http://127.0.0.1:8471/ :
  * stage pipeline: F1-MARVEL -> F1-MCU -> F3 -> F5
  * live progress from the stage logs (batch/done/stamped/missing, rate, ETA)
  * watchdog state + log tail (egress rotations, resumes)
  * nordvpn status + live egress IP (ipify)

Read-only: parses logs/state files on each request; rate is sampled
server-side across /data polls (stage logs carry no timestamps).
Campaign tooling (untracked, no repo changes); run detached:

  setsid nohup scriptengine/.venv/bin/python tools/marvel/live_monitor.py &
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
RECEIPTS = REPO / "reports" / "marvel" / "receipts"
WD_STATE = Path("/tmp/opencode/egress_watchdog_2026-09-26.state")
PORT = 8471

STAGES = ["marvel", "mcu", "f3", "f5"]
LABELS = {
    "marvel": "F1 MARVEL revid backfill",
    "mcu": "F1 MCU revid backfill",
    "f3": "F3 re-crawl (What-If Thor x4)",
    "f5": "F5 MCU top-up (33 pages)",
}
BACKFILL_RE = re.compile(
    r"\[backfill (\w+)\] batch (\d+): (\d+)/(\d+) stamped=(\d+) missing=(\d+)"
)
FIXLIST_FETCH_RE = re.compile(r"\[fixlist\] fetching '(.*)'")


def read_log_tail(path: Path, n: int = 8) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    return lines[-n:]


def last_backfill_state(path: Path) -> dict | None:
    state = None
    for line in read_log_tail(path, 200):
        m = BACKFILL_RE.search(line)
        if m:
            state = m
    if not state:
        return None
    series, batch, done, total, stamped, missing = state.groups()
    return {
        "series": series, "batch": int(batch), "done": int(done),
        "total": int(total), "stamped": int(stamped), "missing": int(missing),
    }


def newest_receipt(pattern: str) -> dict | None:
    files = sorted(RECEIPTS.glob(pattern), key=lambda p: p.stat().st_mtime)
    if not files:
        return None
    try:
        return json.loads(files[-1].read_text(encoding="utf-8"))
    except Exception:
        return None


def pgrep(pattern: str) -> list[int]:
    try:
        out = subprocess.run(
            ["pgrep", "-f", pattern], capture_output=True, text=True, timeout=5
        ).stdout.split()
        return [int(p) for p in out]
    except Exception:
        return []


def parse_watchdog_state() -> dict:
    st = {}
    if WD_STATE.exists():
        for line in WD_STATE.read_text().splitlines():
            if "=" in line:
                k, v = line.split("=", 1)
                st[k] = v
    return st


def nordvpn_status() -> str:
    try:
        out = subprocess.run(
            ["nordvpn", "status"], capture_output=True, text=True, timeout=20
        ).stdout
        parts = [l for l in out.splitlines() if l.startswith(("Status", "Server"))]
        return " | ".join(parts) or "unknown"
    except Exception:
        return "unavailable"


# ---- caches / samplers ----
_cache: dict[str, tuple[float, object]] = {}

def cached(key: str, ttl: float, fn):
    now = time.monotonic()
    hit = _cache.get(key)
    if hit and now - hit[0] < ttl:
        return hit[1]
    val = fn()
    _cache[key] = (now, val)
    return val


_rates: dict[str, list[tuple[float, int]]] = {}

def sample_rate(stage: str, value: int | None) -> tuple[float | None, int]:
    """Returns (rate_per_hour, samples_kept). Window: 15 min."""
    now = time.monotonic()
    hist = _rates.setdefault(stage, [])
    if value is not None:
        hist.append((now, value))
    cutoff = now - 900
    hist[:] = [h for h in hist if h[0] >= cutoff]
    if len(hist) < 2 or hist[-1][0] - hist[0][0] < 20:
        return (None, len(hist))
    (t0, v0), (t1, v1) = hist[0], hist[-1]
    rate = (v1 - v0) / (t1 - t0) * 3600
    return (max(rate, 0.0), len(hist))


def stage_log_path(key: str, run: int) -> Path:
    names = {
        "marvel": "revid_backfill_marvel_2026-09-26",
        "mcu": "revid_backfill_mcu_2026-09-26",
        "f3": "fixlist_f3_2026-09-26",
        "f5": "fixlist_f5_2026-09-26",
    }
    base = names[key]
    if run > 1:
        base = f"{base}_run{run}"
    return RECEIPTS / f"{base}.log"


def stage_procs(key: str) -> list[int]:
    pats = {
        "marvel": r"^scriptengine/\.venv/bin/python tools/marvel/revid_backfill\.py --series marvel ",
        "mcu": r"^scriptengine/\.venv/bin/python tools/marvel/revid_backfill\.py --series mcu ",
        "f3": r"^scriptengine/\.venv/bin/python tools/marvel/fixlist_fetch\.py --series marvel",
        "f5": r"^scriptengine/\.venv/bin/python tools/marvel/fixlist_fetch\.py --series mcu",
    }
    return pgrep(pats[key])


def build_data() -> dict:
    wd = parse_watchdog_state()
    wd_stage = wd.get("STAGE", "marvel")
    try:
        run = int(wd.get("RUN", "1"))
    except ValueError:
        run = 1
    cur_idx = STAGES.index(wd_stage) if wd_stage in STAGES else 0

    stages = []
    for i, key in enumerate(STAGES):
        entry: dict = {"key": key, "label": LABELS[key]}
        pids = stage_procs(key)
        entry["pids"] = pids
        log = stage_log_path(key, run)
        entry["log_mtime_age_s"] = (
            max(0, int(time.time() - log.stat().st_mtime)) if log.exists() else None
        )
        entry["log_tail"] = read_log_tail(log, 4)

        if key in ("marvel", "mcu"):
            st = last_backfill_state(log)
            rec = newest_receipt(f"revid_backfill_{key}_*_2026-09-26.json")
            entry["receipt"] = {
                k: rec.get(k) for k in (
                    "stop_reason", "stamped_this_run", "batches_run",
                    "missing_live", "ran_at",
                )
            } if rec else None
            done_receipt = bool(rec and rec.get("stop_reason") == "complete")
            if st:
                entry.update({k: st[k] for k in ("batch", "done", "total", "stamped", "missing")})
                rate, nsamp = sample_rate(key, st["done"])
                entry["rate_per_h"] = round(rate, 1) if rate is not None else None
                entry["samples"] = nsamp
                if rate:
                    entry["eta_min"] = int((st["total"] - st["done"]) / rate * 60)
            else:
                entry.update({"batch": 0, "done": 0, "total": 0,
                              "stamped": 0, "missing": 0, "rate_per_h": None})
        else:  # f3 / f5: count written rows in the log
            total = 4 if key == "f3" else 33
            written = 0
            last_fetch = None
            for line in read_log_tail(log, 400):
                m = FIXLIST_FETCH_RE.search(line)
                if m:
                    last_fetch = m.group(1)
                if line.strip().startswith("-> ") or " (revid=" in line:
                    written += 1
            rec = newest_receipt(f"fixlist_{key + '_recrawl' if key == 'f3' else '_mcu_topup_f5'}_2026-09-26.json".replace("f5_mcu_topup_f5", "mcu_topup_f5"))
            bad_rows = 0
            if rec:
                bad_rows = sum(
                    1 for x in rec.get("rows", [])
                    if str(x.get("status", "")).startswith("missing-or-failed")
                )
            entry["written"] = written
            entry["total"] = total
            entry["last_fetch"] = last_fetch
            entry["receipt"] = {
                "written": rec.get("written"),
                "titles_in": rec.get("titles_in"),
                "bad_rows": bad_rows,
                "ran_at": rec.get("ran_at"),
            } if rec else None
            done_receipt = bool(rec) and bad_rows == 0

        # state relative to the watchdog (receipt-aware: a stage whose receipt
        # is complete counts as done even while the watchdog state file lags)
        if i < cur_idx or done_receipt:
            entry["state"] = "done"
        elif i == cur_idx:
            if pids:
                entry["state"] = "running"
            else:
                wd_lines = read_log_tail(RECEIPTS / "egress_watchdog_2026-09-26.log", 20)
                fail_i = max((j for j, l in enumerate(wd_lines) if "LAUNCH FAILED" in l), default=-1)
                ok_i = max((j for j, l in enumerate(wd_lines)
                            if l.startswith("launched stage=") or "advancing to stage=" in l),
                           default=-1)
                entry["state"] = "stalled" if fail_i > ok_i else "pending"
        else:
            entry["state"] = "queued"
        stages.append(entry)

    wd_alive = bool(pgrep(r"egress_watchdog\.sh"))
    data = {
        "ts": time.strftime("%Y-%m-%d %H:%M:%S"),
        "stages": stages,
        "watchdog": {
            "alive": wd_alive,
            "stage": wd.get("STAGE"),
            "run": run,
            "country": wd.get("COUNTRY"),
            "last_ip": wd.get("LAST_IP"),
            "log_tail": read_log_tail(RECEIPTS / "egress_watchdog_2026-09-26.log", 10),
        },
        "egress": {
            "vpn": cached("vpn", 30, nordvpn_status),
            "ip": cached("ip", 60, lambda: _ipify()),
        },
    }
    return data


def _ipify() -> str:
    try:
        with urllib.request.urlopen(
            "https://api.ipify.org", timeout=8
        ) as r:
            return r.read().decode().strip()
    except Exception:
        return "unavailable"


PAGE = """<!doctype html>
<html><head><meta charset="utf-8">
<title>MARVEL egress batch — live monitor</title>
<style>
  :root { color-scheme: dark; }
  body { background:#0d1117; color:#e6edf3; font:14px/1.5 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace; margin:0; padding:24px; }
  h1 { font-size:18px; margin:0 0 4px; }
  .sub { color:#8b949e; font-size:12px; margin-bottom:20px; }
  .pipe { display:flex; gap:8px; margin-bottom:20px; flex-wrap:wrap; }
  .chip { padding:6px 14px; border-radius:999px; border:1px solid #30363d; font-size:13px; }
  .chip.done { background:#12261e; border-color:#2ea043; color:#3fb950; }
  .chip.running { background:#0d2a3f; border-color:#1f6feb; color:#58a6ff; }
  .chip.stalled { background:#3a2d12; border-color:#d29922; color:#d29922; }
  .chip.queued,.chip.pending { color:#8b949e; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:16px; }
  .card { background:#161b22; border:1px solid #30363d; border-radius:8px; padding:16px; }
  .card h2 { font-size:13px; color:#8b949e; margin:0 0 10px; text-transform:uppercase; letter-spacing:.06em; }
  .big { font-size:26px; margin:4px 0; }
  .bar { height:10px; background:#21262d; border-radius:5px; overflow:hidden; margin:10px 0; }
  .bar > div { height:100%; background:#2ea043; transition:width .8s; }
  .kv { display:flex; justify-content:space-between; padding:3px 0; border-bottom:1px solid #21262d; }
  .kv span:last-child { color:#58a6ff; }
  pre { background:#0d1117; border:1px solid #21262d; border-radius:6px; padding:10px; font-size:11.5px; overflow-x:auto; max-height:260px; overflow-y:auto; color:#9dabbd; margin:0; }
  .warn { color:#d29922; } .ok { color:#3fb950; } .bad { color:#ff7b72; }
  .foot { margin-top:16px; color:#8b949e; font-size:11px; }
</style></head>
<body>
<h1>MARVEL 100% — egress batch live monitor</h1>
<div class="sub">F1 revid backfill + F3 re-crawl + F5 top-up · watchdog-orchestrated · refresh 5 s</div>
<div class="pipe" id="pipe"></div>
<div class="grid">
  <div class="card"><h2>Current stage</h2><div id="cur"></div></div>
  <div class="card"><h2>Egress / watchdog</h2><div id="egress"></div></div>
  <div class="card"><h2>Watchdog log</h2><pre id="wdlog"></pre></div>
  <div class="card"><h2>Stage log (tail)</h2><pre id="stageLog"></pre></div>
</div>
<div class="foot" id="foot"></div>
<script>
function esc(s){return String(s??"").replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));}
function pct(d,t){return t? (100*d/t).toFixed(2)+"%" : "—";}
function etaStr(c){ if(c.eta_min!=null) return Math.round(c.eta_min/60)+" h "+(c.eta_min%60)+" m";
  if(c.rate_per_h&&c.total>c.done){ const h=(c.total-c.done)/c.rate_per_h; return Math.round(h/60)+" h "+Math.round(h%60)+" m (est)"; }
  return "—"; }
function render(d){
  const pipe=document.getElementById('pipe'); pipe.innerHTML="";
  d.stages.forEach(s=>{
    const c=document.createElement('div');
    c.className="chip "+s.state;
    const tag=s.state==="running"?" (run "+ (d.watchdog.run) +")":s.state==="stalled"?" (launch failing)":"";
    c.textContent=s.key.toUpperCase()+tag;
    pipe.appendChild(c);
  });
  const cur=d.stages.find(s=>s.state!=="done"&&s.state!=="queued")||d.stages.find(s=>s.state==="queued")||null;
  const curEl=document.getElementById('cur');
  if(!cur){
    curEl.innerHTML=`<div class="big ok">ALL STAGES COMPLETE</div>
      <div class="sub">next: delta re-gate (plan phase C entry)</div>`;
  } else if(cur.done!==undefined&&cur.total){
    curEl.innerHTML=`<div class="big">${cur.done.toLocaleString()} / ${cur.total.toLocaleString()}</div>
      <div class="bar"><div style="width:${pct(cur.done,cur.total).replace('%','')}"></div></div>
      <div class="kv"><span>batch</span><span>${cur.batch}</span></div>
      <div class="kv"><span>stamped</span><span>${cur.stamped.toLocaleString()}</span></div>
      <div class="kv"><span>missing</span><span class="${cur.missing?'bad':'ok'}">${cur.missing}</span></div>
      <div class="kv"><span>rate</span><span>${cur.rate_per_h?cur.rate_per_h+" units/h ("+cur.samples+" samples)":"warming up…"}</span></div>
      <div class="kv"><span>ETA</span><span>${etaStr(cur)}</span></div>
      ${cur.receipt?`<div class="kv"><span>receipt</span><span class="${cur.receipt.stop_reason==='complete'?'ok':'bad'}">${esc(cur.receipt.stop_reason)}</span></div>`:""}
    `;
  } else if(cur.written!==undefined){
    curEl.innerHTML=`<div class="big">${cur.written} / ${cur.total} written</div>
      <div class="bar"><div style="width:${100*cur.written/cur.total}%"></div></div>
      <div class="kv"><span>last fetch</span><span>${esc(cur.last_fetch)||"—"}</span></div>
      ${cur.receipt?`<div class="kv"><span>receipt</span><span class="ok">${cur.receipt.written}/${cur.receipt.titles_in} written</span></div>`:""}
    `;
  } else {
    curEl.innerHTML=`<div class="big">${cur.state}</div>
      <div class="${cur.state==='stalled'?'warn':'sub'}">${cur.state==='stalled'?'watchdog launch failing — will rotate egress & retry on next tick':'waiting for watchdog to launch this stage'}</div>`;
  }
  const w=d.watchdog;
  document.getElementById('egress').innerHTML=`
    <div class="kv"><span>vpn</span><span class="${/connected/i.test(d.egress.vpn)?'ok':'warn'}">${esc(d.egress.vpn)}</span></div>
    <div class="kv"><span>egress ip</span><span>${esc(d.egress.ip)}</span></div>
    <div class="kv"><span>pool country</span><span>${esc(w.country)}</span></div>
    <div class="kv"><span>watchdog</span><span class="${w.alive?'ok':'bad'}">${w.alive?'alive':'DEAD'}</span></div>
    <div class="kv"><span>stage / run</span><span>${esc(w.stage)} / ${w.run}</span></div>`;
  document.getElementById('wdlog').textContent=w.log_tail.join("\\n");
  const sl=d.stages.find(s=>s.state==="running")||d.stages.find(s=>s.state!=="done")||d.stages[0];
  document.getElementById('stageLog').textContent=(sl.log_tail||[]).join("\\n")||"(no log yet)";
  document.getElementById('foot').textContent="last update "+d.ts+" · watchdog state: stage="+w.stage+" run="+w.run+" ip="+w.last_ip;
}
async function tick(){ try{ const r=await fetch('/data'); render(await r.json()); }catch(e){ document.getElementById('foot').textContent="monitor unreachable: "+e; } }
tick(); setInterval(tick,5000);
</script>
</body></html>
"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/data":
            body = json.dumps(build_data()).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            body = PAGE.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *a):  # quiet
        pass


if __name__ == "__main__":
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print(f"live monitor on http://0.0.0.0:{PORT}/ (LAN: 192.168.1.3:{PORT}) (pid {os.getpid()})")
    srv.serve_forever()