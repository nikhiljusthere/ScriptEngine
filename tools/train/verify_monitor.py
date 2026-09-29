#!/usr/bin/env python3
"""Live monitor for VERIFY-7000 inline workflow.

Serves a browser-dashboard at http://127.0.0.1:8950 showing real-time
progress of each pool's verification. Open it in any browser (Brave) to watch
windows complete. Auto-refreshes every 2 seconds.

Usage:
    python tools/train/verify_monitor.py [--port 8950]

Pools monitored:
    series/jjk/training/opencode/mimoP*_out.jsonl        pilot batches (5x31)
    series/jjk/training/opencode/mimo_out.jsonl          main mimo (500)
    series/jjk/training/opencode/nemotron_out.jsonl      main nemotron (500)
    series/jjk/training/opencode/spacebunny_out.jsonl    main spacebunny (500)
"""

import argparse, json, sys, time
from pathlib import Path
from html import escape
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO = Path(__file__).resolve().parent.parent.parent  # /home/goblin/ScriptEngine
OPS_DIR = REPO / "series" / "jjk" / "training" / "opencode"
V1_TRAIN = REPO / "series" / "jjk" / "training" / "v1" / "train.jsonl"

# Pools: label -> input_file, output_file
POOLS = [
    ("mimoP1",   "mimoP1_windows.jsonl",   "mimoP1_out.jsonl"),
    ("mimoP2",   "mimoP2_windows.jsonl",   "mimoP2_out.jsonl"),
    ("mimoP3",   "mimoP3_windows.jsonl",   "mimoP3_out.jsonl"),
    ("mimoP4",   "mimoP4_windows.jsonl",   "mimoP4_out.jsonl"),
    ("mimoP5",   "mimoP5_windows.jsonl",   "mimoP5_out.jsonl"),
    ("mimo",     "mimo_windows.jsonl",     "mimo_out.jsonl"),
    ("nemotron", "nemotron_windows.jsonl", "nemotron_out.jsonl"),
    ("spacebunny","spacebunny_windows.jsonl","spacebunny_out.jsonl"),
]

TOTAL_WINDOWS = sum(500 if "P" not in p[0] else 31 for p in POOLS)


def count_lines(path):
    """Count lines in a file safely."""
    try:
        return sum(1 for _ in open(path))
    except FileNotFoundError:
        return 0


def check_server_health():
    """Check if the NInfer server is responding."""
    try:
        import urllib.request
        r = urllib.request.urlopen("http://127.0.0.1:18081/health", timeout=2)
        return json.loads(r.read())["status"] == "ok"
    except Exception:
        return False


def get_server_pid():
    """Get the NInfer server PID from qwen_mode.txt."""
    try:
        mode_file = Path.home() / "ninfer-work" / "qwen_mode.txt"
        for line in open(mode_file):
            if line.startswith("qwen_pid="):
                return line.split("=")[1].strip().split()[0]
    except Exception:
        pass
    return "?"


def collect_data():
    """Collect current state from all pool files."""
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    data = {}
    total_done = 0
    
    for name, win_file, out_file in POOLS:
        out_path = OPS_DIR / out_file
        inp_path = OPS_DIR / win_file
        
        done = count_lines(out_path)
        total = count_lines(inp_path)
        
        data[name] = {"done": done, "total": total}
        total_done += done
    
    # Count v1 tiers if train exists
    v1_info = {}
    try:
        if V1_TRAIN.exists():
            for line in open(V1_TRAIN):
                d = json.loads(line.strip())
                t = d.get("tier", "?")
                if t not in v1_info:
                    v1_info[t] = 0
                v1_info[t] += 1
    except Exception:
        pass
    
    server_up = check_server_health()
    data["_timestamp"] = now
    data["_total"] = total_done
    data["_server_status"] = "UP" if server_up else "DOWN"
    data["_server_pid"] = get_server_pid()
    data["_v1_tiers"] = v1_info
    
    return data


def build_html(data):
    """Build the dashboard HTML."""
    rows = []
    for name, _, _ in POOLS:
        info = data[name]
        done = info["done"]
        total = info["total"]
        pct = (done / total * 100) if isinstance(total, int) and total > 0 else 0
        bar_w = min(200, max(0, int(pct / 5)))
        
        if pct >= 100:
            color = "#4caf50"
            status_class = "completed"
        elif pct > 0:
            color = "#ff9800"
            status_class = ""
        else:
            color = "#9e9e9e"
            status_class = ""
        
        pct_str = "{:.1f}%".format(pct).rjust(6)
        done_str = "{:>4}".format(done)
        total_str = "{:>4}".format(total) if isinstance(total, int) else "??"
        
        rows.append(f'''
        <tr>
            <td><strong>{escape(name)}</strong></td>
            <td style="text-align:center"><span class="{status_class}">{done_str}</span></td>
            <td style="text-align:center">{total_str}</td>
            <td style="text-align:center"><strong>{pct_str}</strong></td>
            <td style="width:220px">
                <div style="background:#eee;border-radius:4px;height:20px;overflow:hidden;">
                    <div style="background:{color};height:100%;width:{bar_w}px;"></div>
                </div>
            </td>
        </tr>''')

    grand_done = data["_total"]
    grand_pct = (grand_done / TOTAL_WINDOWS * 100) if isinstance(TOTAL_WINDOWS, int) and TOTAL_WINDOWS > 0 else 0
    bar_w_grand = min(200, max(0, int(grand_pct / 5)))
    
    if grand_pct >= 100:
        grand_color = "#4caf50"
    elif grand_pct > 0:
        grand_color = "#ff9800"
    else:
        grand_color = "#9e9e9e"
    
    # Server badge
    server_badge = '<span style="color:green">&#9679; UP</span>' if data["_server_status"] == "UP" \
                   else '<span style="color:red">&#9679; DOWN</span>'
    
    # Tier breakdown
    tier_rows = ""
    if data.get("_v1_tiers"):
        for tier_name, count in sorted(data["_v1_tiers"].items()):
            tier_rows += f'''<tr><td>{escape(tier_name)}</td><td style="text-align:right">{count:,}</td></tr>'''
    
    # Build stats cards
    stats_cards = f'''
        <!-- Stat Cards -->
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">Total Windows Verified</div>
                <div class="stat-value">{grand_done:,}/{TOTAL_WINDOWS:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Overall Progress</div>
                <div class="stat-value">{grand_pct:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Server Status</div>
                <div class="stat-value" style="font-size: 18px;">{data["_server_status"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Last Updated</div>
                <div class="stat-value" style="font-size: 16px;">{data["_timestamp"]}</div>
            </div>
        </div>
    '''
    
    # Full HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2">
    <title>VERIFY-7000 Monitor</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #fafafa; margin: 0; padding: 20px; }}
        .container {{ max-width: 900px; margin: 0 auto; }}
        h1 {{ color: #333; margin-bottom: 10px; font-size: 24px; display: flex; align-items: center; gap: 10px; }}
        .subtitle {{ color: #666; font-size: 14px; margin-bottom: 20px; }}
        .stats-row {{ display: flex; gap: 20px; margin-bottom: 20px; flex-wrap: wrap; }}
        .stat-card {{ background: white; border-radius: 8px; padding: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); flex: 1; min-width: 180px; }}
        .stat-label {{ color: #666; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }}
        .stat-value {{ font-size: 28px; font-weight: bold; color: #1976d2; margin-top: 4px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; }}
        th {{ background: #f5f5f5; padding: 12px; text-align: left; font-weight: 600; color: #333; border-bottom: 2px solid #ddd; }}
        td {{ padding: 12px; border-bottom: 1px solid #eee; color: #333; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #fafafa; }}
        .completed {{ color: #4caf50 !important; }}
        .footer {{ margin-top: 20px; text-align: center; color: #999; font-size: 12px; line-height: 1.6; }}
        .pulse-text {{ color: #1976d2; animation: pulse 1.5s infinite; display: inline-block; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.6; }} 100% {{ opacity: 1; }} }}
    </style>
</head>
<body>
    <div class="container">
        <h1>JJK VERIFY-7000 Live Monitor {server_badge}</h1>
        <div class="subtitle">Manual inline verification &middot; one window at a time &middot; wiki-backed &middot; strict rules</div>
        {stats_cards}
        <table>
            <thead>
                <tr>
                    <th>Pool</th>
                    <th style="text-align:center">Done</th>
                    <th style="text-align:center">Total</th>
                    <th style="text-align:center">% Complete</th>
                    <th>Progress Bar</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <h3 style="margin-top:30px;margin-bottom:10px;color:#555;">v1/train.jsonl Tier Breakdown ({sum(data.get('_v1_tiers', {}).values()):,} windows)</h3>
        <table style="width:60%;">
            <thead>
                <tr>
                    <th>Tier</th>
                    <th style="text-align:right">Windows</th>
                </tr>
            </thead>
            <tbody>
                {tier_rows}
            </tbody>
        </table>
        <div class="footer">
            Auto-refreshes every 2 seconds &middot; VERIFY-7000 Inline Workflow &middot; 
            Server: :18081 (pid {data["_server_pid"]}) &middot;
            Refreshed at <span class="pulse-text">{data["_timestamp"]}</span>
        </div>
    </div>
</body>
</html>'''
    
    return html


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        data = collect_data()
        html = build_html(data)
        
        if self.path == "/":
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_error(404)
    
    def log_message(self, format, *args):
        # Quiet logging
        pass


def main():
    parser = argparse.ArgumentParser(description="Verify-7000 progress monitor")
    parser.add_argument("--port", type=int, default=8950, help="Port to serve on (default: 8950)")
    args = parser.parse_args()
    
    print("Verify-7000 Monitor starting...")
    print("Dashboard URL: http://127.0.0.1:{}/".format(args.port))
    print("")
    print("Monitoring pools:")
    for name, win_file, out_file in POOLS:
        print("  {} -> {}".format(win_file, out_file))
    
    print("\nPress Ctrl+C to stop\n")
    
    # Run persistent HTTP server (not single-request-per-cycle)
    try:
        while True:
            server = HTTPServer(("127.0.0.1", args.port), Handler)
            server.serve_forever(poll_interval=2)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
