#!/usr/bin/env python3
"""Live browser monitor for the D3 3-door tier-1 sweep (marvel).

    scriptengine/.venv/bin/python tools/marvel/d3_monitor.py      # -> http://127.0.0.1:8090

Read-only and zero-egress: stdlib only, bound to localhost, no CDN assets. It
reads the per-door ledgers + `.new` sidecars the sweep writes, the supervisor
logs, the two serving stacks' /health and nvidia-smi -- it never writes into
the repo and never touches the sweep (history goes to /tmp/opencode).

Counting follows the sweep's own resume semantics (span_recall.recall):
one verdict per (title, sentence) key, sidecar rows win over ledger rows,
ERROR rows count as ERROR until re-probed, and hit_rate divides by the FULL
panel (517,960), never by rows done (plan §2a trap 3). Ledgers reach ~400 MB
per door, so sidecars are read incrementally by byte offset; a ledger is
only re-read when the merge rewrites it (atomic replace -> new inode).
"""

from __future__ import annotations

import argparse
import collections
import json
import os
import re
import subprocess
import threading
import time
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGERS = ROOT / "reports/span-recall/marvel"
HASH8 = "a880bf25"
PANEL_SIZE = 517_960
DOORS = ("qa", "narrative", "roster")
VERDICTS = ("HIT", "MISS_DOC", "MISS_SPAN", "TRUNCATED", "ERROR")
SUPERVISORS = {"qa": "/tmp/opencode/d3_sweep_qa.log", "nr": "/tmp/opencode/d3_sweep_nr.log"}
SERVERS = {":8000 (qa, CUDA)": "http://127.0.0.1:8000/health",
           ":8002 (narrative/roster)": "http://127.0.0.1:8002/health"}
HISTORY = Path("/tmp/opencode/d3_monitor_history.jsonl")
ANSI = re.compile(r"\x1b\[[0-9;]*m")


class DoorState:
    """Unique-key verdict tally for one door, fed incrementally."""

    def __init__(self, door: str) -> None:
        self.door = door
        self.ledger = LEDGERS / f"sweep_{door}_{HASH8}.jsonl"
        self.sidecar = self.ledger.with_name(self.ledger.name + ".new")
        self.reset()

    def reset(self) -> None:
        self.verdict: dict[int, str] = {}
        self.counts = collections.Counter()
        self.ledger_sig: tuple | None = None
        self.side_ino: int | None = None
        self.side_off = 0
        self.recent: collections.deque = collections.deque(maxlen=12)
        self.commits = collections.Counter()

    def _take(self, row: dict, recent: bool) -> None:
        key = hash((row.get("title"), row.get("sentence")))
        v = row.get("verdict", "ERROR")
        old = self.verdict.get(key)
        if old is not None:
            self.counts[old] -= 1
        self.verdict[key] = v
        self.counts[v] += 1
        if row.get("commit"):
            self.commits[row["commit"]] += 1
        if recent and v != "HIT":
            self.recent.append({"verdict": v, "title": row.get("title"),
                                "breadcrumb": row.get("breadcrumb"),
                                "sentence": (row.get("sentence") or "")[:220],
                                "returned": (row.get("returned_docs") or [])[:3],
                                "error": row.get("error")})

    def _read(self, path: Path, start: int, recent: bool) -> int:
        """Consume whole lines from `start`; returns the new offset."""
        try:
            with path.open("rb") as fh:
                fh.seek(start)
                data = fh.read()
        except OSError:
            return start
        end = data.rfind(b"\n")
        if end < 0:
            return start
        for line in data[: end + 1].splitlines():
            if line.strip():
                try:
                    self._take(json.loads(line), recent)
                except json.JSONDecodeError:
                    pass
        return start + end + 1

    def refresh(self) -> None:
        try:
            st = self.ledger.stat()
            sig = (st.st_ino, st.st_size, st.st_mtime_ns)
        except OSError:
            sig = None
        if sig != self.ledger_sig:          # merge rewrote it (or first read)
            self.reset()
            self.ledger_sig = sig
            if sig is not None:
                self._read(self.ledger, 0, recent=False)
        try:
            ss = self.sidecar.stat()
        except OSError:
            self.side_ino, self.side_off = None, 0
            return
        if ss.st_ino != self.side_ino or ss.st_size < self.side_off:
            if self.side_ino is not None:   # sidecar replaced mid-run: rebuild
                self.reset()
                self.ledger_sig = sig
                if sig is not None:
                    self._read(self.ledger, 0, recent=False)
            self.side_ino, self.side_off = ss.st_ino, 0
        self.side_off = self._read(self.sidecar, self.side_off, recent=True)

    def running(self) -> bool:
        for pid in os.listdir("/proc"):
            if not pid.isdigit():
                continue
            try:
                cmd = Path(f"/proc/{pid}/cmdline").read_bytes().split(b"\0")
            except OSError:
                continue
            if b"span-recall" in cmd and b"--door" in cmd:
                i = cmd.index(b"--door")
                if i + 1 < len(cmd) and cmd[i + 1] == self.door.encode():
                    return True
        return False


def _health(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=2) as r:
            body = json.loads(r.read())
        return {"up": True, "device": body.get("device"), "started": body.get("started")}
    except Exception as exc:
        return {"up": False, "error": str(exc)[:80]}


def _gpu() -> dict:
    try:
        out = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu,temperature.gpu",
             "--format=csv,noheader,nounits"], capture_output=True, text=True, timeout=5).stdout
        used, total, util, temp = [float(x) for x in out.strip().split(",")]
        return {"used": used, "total": total, "util": util, "temp": temp}
    except Exception:
        return {}


def _ram() -> dict:
    info = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        k, v = line.split(":", 1)
        info[k] = int(v.split()[0]) / 1048576
    return {"total": info.get("MemTotal", 0), "available": info.get("MemAvailable", 0),
            "swap_used": info.get("SwapTotal", 0) - info.get("SwapFree", 0)}


def _log_tail(path: str, n: int = 8) -> list[str]:
    try:
        lines = Path(path).read_text(errors="replace").splitlines()
    except OSError:
        return []
    keep = [ANSI.sub("", l) for l in lines
            if re.match(r"^\d\d:\d\d:\d\d ", ANSI.sub("", l))]
    return keep[-n:]


class Monitor:
    def __init__(self, interval: float) -> None:
        self.interval = interval
        self.doors = {d: DoorState(d) for d in DOORS}
        self.history: dict[str, collections.deque] = {
            d: collections.deque(maxlen=20_000) for d in DOORS}
        self._load_history()
        self.snapshot: dict = {"loading": True}
        self.lock = threading.Lock()

    def _load_history(self) -> None:
        try:
            for line in HISTORY.read_text().splitlines():
                row = json.loads(line)
                for d in DOORS:
                    if d in row:
                        self.history[d].append((row["t"], row[d]))
        except (OSError, json.JSONDecodeError):
            pass

    def _rate(self, door: str, now: float, done: int) -> float | None:
        """Probes/s over the last ~15 min of samples (falls back to all)."""
        hist = self.history[door]
        base = next(((t, n) for t, n in hist if now - t <= 900), None)
        if base is None or now - base[0] < 30:
            base = hist[0] if hist else None      # young window: use it all
        if base is None or now - base[0] < 30:
            return None
        return max(0, done - base[1]) / (now - base[0])

    def tick(self) -> None:
        now = time.time()
        doors = {}
        sample = {"t": now}
        for d, st in self.doors.items():
            st.refresh()
            done = len(st.verdict)
            sample[d] = done
            self.history[d].append((now, done))
            rate = self._rate(d, now, done)
            remaining = PANEL_SIZE - done + st.counts["ERROR"]
            doors[d] = {
                "done": done, "panel": PANEL_SIZE,
                "counts": {v: st.counts[v] for v in VERDICTS},
                "hit_rate_panel": st.counts["HIT"] / PANEL_SIZE,
                "hit_rate_done": st.counts["HIT"] / done if done else None,
                "rate": rate,
                "eta_s": remaining / rate if rate else None,
                "running": st.running(),
                "complete": done >= PANEL_SIZE and st.counts["ERROR"] == 0,
                "recent": list(st.recent)[::-1],
                "commits": dict(st.commits.most_common(4)),
                "spark": self._spark(d),
            }
        try:
            with HISTORY.open("a") as fh:
                fh.write(json.dumps(sample) + "\n")
        except OSError:
            pass
        snap = {
            "now": now, "panel_hash": HASH8,
            "doors": doors,
            "servers": {k: _health(u) for k, u in SERVERS.items()},
            "gpu": _gpu(), "ram": _ram(),
            "logs": {k: _log_tail(p) for k, p in SUPERVISORS.items()},
            "load": os.getloadavg(),
        }
        with self.lock:
            self.snapshot = snap

    def _spark(self, door: str, points: int = 120) -> list:
        hist = list(self.history[door])
        if len(hist) <= points:
            return [[round(t), n] for t, n in hist]
        step = len(hist) / points
        return [[round(hist[int(i * step)][0]), hist[int(i * step)][1]]
                for i in range(points)] + [[round(hist[-1][0]), hist[-1][1]]]

    def loop(self) -> None:
        while True:
            t = time.time()
            try:
                self.tick()
            except Exception as exc:  # the monitor must outlive a bad read
                with self.lock:
                    self.snapshot = {**self.snapshot, "monitor_error": str(exc)[:200]}
            time.sleep(max(1.0, self.interval - (time.time() - t)))


PAGE = r"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>D3 Sweep Monitor</title>
<style>
:root{--bg:#f6f7f9;--card:#fff;--ink:#16181d;--muted:#5d6472;--line:#e3e6eb;--track:#eceef2;
--hit:#1f9d6b;--doc:#6b5bd6;--span:#2f7fd1;--trunc:#d08a1f;--err:#d64545;--accent:#1f6feb}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#0f1115;--card:#171a21;--ink:#e8eaef;--muted:#9aa3b2;--line:#262b35;--track:#232833;
--hit:#35c48b;--doc:#8f82ee;--span:#58a2ec;--trunc:#e6a53d;--err:#ef6666;--accent:#58a6ff}}
:root[data-theme="dark"]{--bg:#0f1115;--card:#171a21;--ink:#e8eaef;--muted:#9aa3b2;--line:#262b35;--track:#232833;
--hit:#35c48b;--doc:#8f82ee;--span:#58a2ec;--trunc:#e6a53d;--err:#ef6666;--accent:#58a6ff}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 system-ui,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:20px 16px 40px}
header{display:flex;flex-wrap:wrap;align-items:baseline;gap:8px 16px;margin-bottom:14px}
h1{font-size:20px;margin:0;font-weight:650;letter-spacing:-.01em}
.sub{color:var(--muted);font-size:13px}.grow{flex:1}
button{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:4px 10px;font:inherit;cursor:pointer}
.card{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}
.overall{display:grid;grid-template-columns:1fr auto;gap:10px 20px;align-items:center;margin-bottom:14px}
.big{font-size:30px;font-weight:700;font-variant-numeric:tabular-nums;letter-spacing:-.02em}
.bar{height:10px;background:var(--track);border-radius:99px;overflow:hidden;display:flex}
.bar>span{display:block;height:100%}
.doors{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;margin-bottom:14px}
.door h2{font-size:16px;margin:0;display:flex;align-items:center;gap:8px}
.chip{font-size:11px;font-weight:600;padding:2px 8px;border-radius:99px;border:1px solid var(--line);color:var(--muted)}
.chip.run{color:var(--hit);border-color:color-mix(in srgb,var(--hit) 45%,transparent)}
.chip.done{color:var(--accent);border-color:color-mix(in srgb,var(--accent) 45%,transparent)}
.chip.idle{color:var(--trunc)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}
.stat .k{color:var(--muted);font-size:11.5px;text-transform:uppercase;letter-spacing:.04em}
.stat .v{font-size:17px;font-weight:650;font-variant-numeric:tabular-nums}
.legend{display:flex;flex-wrap:wrap;gap:6px 12px;font-size:12px;color:var(--muted);margin-top:8px}
.legend i{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:5px;vertical-align:-1px}
.legend b{color:var(--ink);font-weight:600;font-variant-numeric:tabular-nums}
svg.spark{width:100%;height:46px;display:block;margin-top:10px}
.sys{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:14px;margin-bottom:14px}
.sys .v{font-size:15px;font-weight:600;font-variant-numeric:tabular-nums}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
.cols{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:14px}
h3{font-size:13px;margin:0 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.05em;font-weight:600}
pre{margin:0;font:12px/1.5 ui-monospace,SFMono-Regular,Menlo,monospace;white-space:pre-wrap;word-break:break-word;color:var(--ink)}
.miss{border-top:1px solid var(--line);padding:8px 0;font-size:12.5px}.miss:first-of-type{border-top:0}
.miss .t{font-weight:600}.miss .s{color:var(--muted)}
.tag{font-size:10.5px;font-weight:700;padding:1px 6px;border-radius:4px;color:#fff;margin-right:6px}
select{background:var(--card);color:var(--ink);border:1px solid var(--line);border-radius:8px;padding:3px 6px;font:inherit}
.err{color:var(--err)}
</style></head><body><div class="wrap">
<header><h1>D3 tier-1 sweep · Marvel</h1><span class="sub" id="meta">connecting…</span><span class="grow"></span>
<button id="theme" title="Toggle theme">◐</button></header>
<div class="card overall"><div><div class="sub">All three doors · probes done of 3 × 517,960</div>
<div class="big" id="ov-num">—</div></div><div style="text-align:right"><div class="sub">campaign ETA</div><div class="big" id="ov-eta">—</div></div>
<div class="bar" style="grid-column:1/-1" id="ov-bar"></div></div>
<div class="doors" id="doors"></div>
<div class="sys" id="sys"></div>
<div class="cols"><div class="card"><h3>Recent non-HIT rows <select id="missdoor"></select></h3><div id="misses"></div></div>
<div class="card"><h3>Supervisor logs</h3><div id="logs"></div></div></div>
<p class="sub" style="margin-top:16px">Local, read-only view of <code>reports/span-recall/marvel/sweep_*_a880bf25.jsonl(.new)</code>.
hit rate = HIT ÷ full panel (517,960), plan §2a; “of done” shown for context. Refreshes every 5 s.</p>
</div>
<script>
const C={HIT:'--hit',MISS_DOC:'--doc',MISS_SPAN:'--span',TRUNCATED:'--trunc',ERROR:'--err'};
const V=Object.keys(C);const css=v=>getComputedStyle(document.documentElement).getPropertyValue(v).trim();
const f=n=>n==null?'—':Math.round(n).toLocaleString();
const pct=(x,d=1)=>x==null?'—':(x*100).toFixed(d)+'%';
function dur(s){if(s==null||!isFinite(s))return'—';if(s<90)return Math.round(s)+'s';const m=s/60;if(m<90)return Math.round(m)+'m';const h=m/60;if(h<48)return h.toFixed(1)+'h';return(h/24).toFixed(1)+'d'}
function pace(r){if(r==null)return'—';if(r===0)return'stalled';return r>=1?(r).toFixed(1)+'/s':(1/r).toFixed(2)+'s/probe'}
try{const t=localStorage.getItem('d3theme');if(t)document.documentElement.dataset.theme=t}catch(e){}
document.getElementById('theme').onclick=()=>{const r=document.documentElement;const dark=r.dataset.theme?r.dataset.theme==='dark':matchMedia('(prefers-color-scheme:dark)').matches;r.dataset.theme=dark?'light':'dark';try{localStorage.setItem('d3theme',r.dataset.theme)}catch(e){};if(last)render(last)};
function bar(counts,total){return V.map(v=>{const w=100*(counts[v]||0)/total;return w>0?`<span style="width:${w}%;background:var(${C[v]})" title="${v} ${f(counts[v])}"></span>`:''}).join('')}
function spark(pts){if(!pts||pts.length<2)return'<svg class="spark"></svg>';const t0=pts[0][0],t1=pts[pts.length-1][0],n0=pts[0][1],n1=Math.max(pts[pts.length-1][1],n0+1);
const W=300,H=46,x=t=>((t-t0)/Math.max(1,t1-t0))*W,y=n=>H-3-((n-n0)/(n1-n0))*(H-8);
const d=pts.map((p,i)=>(i?'L':'M')+x(p[0]).toFixed(1)+' '+y(p[1]).toFixed(1)).join(' ');
return`<svg class="spark" viewBox="0 0 ${W} ${H}" preserveAspectRatio="none"><path d="${d} L${W} ${H} L0 ${H}Z" fill="var(--accent)" opacity=".12"/><path d="${d}" fill="none" stroke="var(--accent)" stroke-width="1.6" vector-effect="non-scaling-stroke"/></svg>`}
let last=null,missdoor=null;
function render(s){last=s;const D=s.doors;let done=0,tot=0,agg={};let eta=0,etaKnown=true;
for(const d in D){done+=D[d].done;tot+=D[d].panel;for(const v of V)agg[v]=(agg[v]||0)+D[d].counts[v];}
// doors sharing a stack run in sequence; qa runs beside them
// a queued door has no pace yet: the ETA covers what is measured and says so
const ev=d=>D[d].complete?0:D[d].eta_s;let pending=[];
const nr=['narrative','roster'].reduce((a,d)=>{const e=ev(d);if(e==null){pending.push(d);return a}return a+e},0);
const q=ev('qa');if(q==null)pending.push('qa');const ce=Math.max(q||0,nr);
document.getElementById('ov-num').innerHTML=`${f(done)} <span class="sub" style="font-size:15px">/ ${f(tot)} · ${pct(done/tot,2)}</span>`;
document.getElementById('ov-eta').innerHTML=(pending.length?'≥ ':'')+dur(ce)+(pending.length?`<div class="sub" style="font-size:12px;font-weight:400">+ ${pending.join(', ')} (not started; no pace yet)</div>`:'');document.getElementById('ov-bar').innerHTML=bar(agg,tot);
document.getElementById('meta').textContent=`panel ${s.panel_hash} · updated ${new Date(s.now*1000).toLocaleTimeString()}`+(s.monitor_error?' · monitor error: '+s.monitor_error:'');
document.getElementById('doors').innerHTML=Object.entries(D).map(([d,x])=>{
const chip=x.complete?'<span class="chip done">complete</span>':x.running?'<span class="chip run">● running</span>':(x.done?'<span class="chip idle">paused</span>':'<span class="chip">queued</span>');
return`<div class="card door"><h2>${d}${chip}</h2>
<div class="stats"><div class="stat"><div class="k">done</div><div class="v">${pct(x.done/x.panel,2)}</div><div class="sub">${f(x.done)}</div></div>
<div class="stat"><div class="k">pace</div><div class="v">${x.done||x.running?pace(x.rate):'—'}</div><div class="sub">${x.rate?f(x.rate*60)+'/min':'&nbsp;'}</div></div>
<div class="stat"><div class="k">eta</div><div class="v">${x.complete?'done':dur(x.eta_s)}</div><div class="sub">${x.eta_s&&!x.complete?new Date((s.now+x.eta_s)*1000).toLocaleString([], {weekday:'short',hour:'2-digit',minute:'2-digit'}):'&nbsp;'}</div></div></div>
<div class="bar">${bar(x.counts,x.panel)}</div>
<div class="legend">${V.map(v=>`<span><i style="background:var(${C[v]})"></i>${v} <b>${f(x.counts[v])}</b></span>`).join('')}</div>
<div class="stats" style="margin-bottom:0"><div class="stat"><div class="k">hit rate (panel)</div><div class="v">${pct(x.hit_rate_panel,2)}</div></div>
<div class="stat"><div class="k">hit rate (of done)</div><div class="v">${pct(x.hit_rate_done)}</div></div>
<div class="stat"><div class="k">commits</div><div class="sub">${Object.entries(x.commits).map(([c,n])=>c+' '+f(n)).join('<br>')||'—'}</div></div></div>
${spark(x.spark)}</div>`}).join('');
const g=s.gpu||{},r=s.ram||{};
document.getElementById('sys').innerHTML=Object.entries(s.servers).map(([k,h])=>`<div class="card"><h3>${k}</h3><div class="v"><span class="dot" style="background:var(${h.up?'--hit':'--err'})"></span>${h.up?'up · '+h.device:'down'}</div><div class="sub">${h.up?'started '+new Date(h.started).toLocaleTimeString():(h.error||'')}</div></div>`).join('')+
`<div class="card"><h3>GPU</h3><div class="v">${g.used?f(g.used)+' / '+f(g.total)+' MiB':'—'}</div><div class="sub">${g.util!=null?g.util+'% util · '+g.temp+'°C':''}</div></div>`+
`<div class="card"><h3>Host</h3><div class="v">${r.total?(r.total-r.available).toFixed(1)+' / '+r.total.toFixed(0)+' GB RAM':'—'}</div><div class="sub">load ${s.load.map(x=>x.toFixed(1)).join(' ')} · swap ${r.swap_used?r.swap_used.toFixed(1):0} GB</div></div>`;
const sel=document.getElementById('missdoor');if(!sel.options.length){sel.innerHTML=Object.keys(D).map(d=>`<option>${d}</option>`).join('');sel.onchange=()=>render(last)}
const md=sel.value;const rows=D[md].recent;
document.getElementById('misses').innerHTML=rows.length?rows.map(m=>`<div class="miss"><span class="tag" style="background:var(${C[m.verdict]})">${m.verdict}</span><span class="t">${esc(m.title)}</span> <span class="s">› ${esc(m.breadcrumb||'')}</span><div class="s">${esc(m.sentence)}</div>${m.error?`<div class="err">${esc(m.error)}</div>`:m.returned.length?`<div class="s">returned: ${m.returned.map(esc).join(' · ')}</div>`:''}</div>`).join(''):'<div class="sub">none yet in this run</div>';
document.getElementById('logs').innerHTML=Object.entries(s.logs).map(([k,l])=>`<div class="sub" style="margin:6px 0 4px">${k}</div><pre>${esc(l.join('\n'))||'—'}</pre>`).join('');}
function esc(t){return String(t??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
async function poll(){try{const r=await fetch('api/status',{cache:'no-store'});const s=await r.json();if(!s.loading)render(s);else document.getElementById('meta').textContent='reading ledgers…'}catch(e){document.getElementById('meta').textContent='monitor unreachable — is d3_monitor.py running?'}setTimeout(poll,5000)}
poll();
</script></body></html>"""


def serve(port: int, interval: float) -> None:
    mon = Monitor(interval)
    threading.Thread(target=mon.loop, name="d3-monitor", daemon=True).start()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            if self.path.startswith("/api/status"):
                with mon.lock:
                    body = json.dumps(mon.snapshot).encode()
                ctype = "application/json"
            elif self.path in ("/", "/index.html"):
                body, ctype = PAGE.encode(), "text/html; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *_):
            pass

    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--port", type=int, default=8090)
    ap.add_argument("--interval", type=float, default=15.0,
                    help="seconds between ledger reads")
    args = ap.parse_args()
    serve(args.port, args.interval)
