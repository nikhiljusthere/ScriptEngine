#!/usr/bin/env python3
"""Live monitor for VERIFY-7000 inline workflow.

Serves a browser-dashboard at http://127.0.0.1:8950 showing real-time
progress of each pool's verification. Open it in any browser (Brave) to watch
windows complete. Auto-refreshes every 2 seconds.

Usage:
    python tools/train/verify_monitor.py [--port 8950]

Pools monitored (main table):
    series/jjk/training/opencode/mimo_out.jsonl              MIMO main (500)
    series/jjk/training/opencode/nemotron_out.jsonl          NEMOTRON main (500)
    series/jjk/training/opencode/spacebunny_out.jsonl        SPACE BUNNY main (500)
    series/jjk/training/v1/*_train*.jsonl                    v1 train subsets
    series/jjk/training/empty_out.jsonl                      Empty re-read

Pilot batches (compact section below table):
    mimoP1_out.jsonl through mimoP5_out.jsonl  (5 × 31 = 155 total)

Grand target: 7,000 windows across all phases.
"""

import argparse, json, os, time, glob as globmod
from pathlib import Path
from html import escape
from http.server import HTTPServer, BaseHTTPRequestHandler

REPO = Path(__file__).resolve().parent.parent.parent  # ScriptEngine root
OPS_DIR = REPO / "series" / "jjk" / "training" / "opencode"
V1_TRAIN = REPO / "series" / "jjk" / "training" / "v1" / "train.jsonl"

# ── Pool definitions for the MAIN dashboard table ───────────────
# Pilot batches are NOT shown here (they clutter the view). See PILOT_SIZES dict.
# Grand total breakdown: 3×500 mains + 4535 v1 (includes empty re-read) + 155 pilots = 7000
POOLS = [
    ("mimo",   "MIMO (500)",           "mimo_out.jsonl",             500),
    ("nemo",   "NEMOTRON (500)",       "nemotron_out.jsonl",         500),
    ("sbunny", "SPACE BUNNY (500)",    "spacebunny_out.jsonl",       500),
    ("v1train", "Phase 3+4: v1 + empty (4535)", None, 4535),
]

# Pilot batch sizes — tracked but displayed compactly, not as individual rows
PILOT_SIZES = {"mimoP1": 31, "mimoP2": 31, "mimoP3": 31, "mimoP4": 31, "mimoP5": 31}

# Total windows verified across all phases (exactly 7000):
#   3 main × 500 + v1/all-reread 4535 + pilots 155 = 7000
TOTAL_WINDOWS = 7000


def _unique_n_count(out_file):
    """Count unique 'n' values in an output JSONL."""
    path = OPS_DIR / out_file
    try:
        ids = set()
        for line in open(path, encoding='utf-8'):
            line = line.strip()
            if not line:
                continue
            try:
                d = json.loads(line)
                n = d.get("n")
                if n is not None:
                    ids.add(n)
            except json.JSONDecodeError:
                pass
        return len(ids)
    except FileNotFoundError:
        return 0


def count_done(out_file):
    """Count unique window IDs verified in the output JSONL."""
    return _unique_n_count(out_file)


def count_total(pool_name, out_file):
    """Count total windows for a pool.
    
    - Main pools with known size: use expected_total
    - Special pools use fixed targets to maintain 7,000 grand total
    """
    for pname, _, ofile, expected in POOLS:
        if pname == pool_name:
            if expected is not None:
                return expected
            break

    # Fallback
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
    grand_total = 0

    for name, label, win_file, expected in POOLS:
        done = count_done(win_file) if win_file else 0
        total = count_total(name, name)

        data[name] = {
            "label": label,
            "done": done,
            "total": total,
        }
        total_done += done
        grand_total += total

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
    data["_grand_total"] = TOTAL_WINDOWS  # Use the defined target
    data["_server_status"] = "UP" if server_up else "DOWN"
    data["_server_pid"] = get_server_pid()
    data["_v1_tiers"] = v1_info

    return data


def pct_bar(pct, width=200):
    """Build HTML progress bar snippet."""
    bar_w = min(width, max(0, int(pct / 5)))
    if pct >= 100:
        color = "#4caf50"
    elif pct > 0:
        color = "#ff9800"
    else:
        color = "#9e9e9e"
    return (color, bar_w)


def build_html(data):
    """Build the dashboard HTML."""
    rows = []
    in_section = ""

    for name, label, _, _ in POOLS:
        info = data[name]
        done = info["done"]
        total = info["total"]
        pct = (done / total * 100) if isinstance(total, int) and total > 0 else 0
        color, bar_w = pct_bar(pct)

        # Group into sections
        if label.startswith("MIMO") or label.startswith("NEMOTRON") or label.startswith("SPACE"):
            section = "Main Pools"
        elif "v1" in label.lower():
            section = "Phase 3 — v1/train.jsonl"
        elif "empty" in label.lower():
            section = "Phase 4 — Empty Re-read"
        else:
            section = "Other"

        if section != in_section:
            rows.append(f"<tr class='section-row'><td colspan='5'>{escape(section)}</td></tr>")
            in_section = section

        pct_str = "{:.1f}%".format(pct).rjust(6)
        done_str = "{:>4}".format(done)
        total_str = "{:>5}".format(total) if isinstance(total, int) else "??"

        rows.append(f'''
        <tr>
            <td><strong>{escape(label)}</strong></td>
            <td style="text-align:center"><span class="done-cell">{done_str}</span></td>
            <td style="text-align:center">{total_str}</td>
            <td style="text-align:center"><strong>{pct_str}</strong></td>
            <td style="width:220px">
                <div class="bar-bg">
                    <div class="bar-fill" style="background:{color};width:{bar_w}px;"></div>
                </div>
            </td>
        </tr>''')

    grand_done = data["_total"]
    grand_total = data["_grand_total"]
    grand_pct = (grand_done / grand_total * 100) if isinstance(grand_total, int) and grand_total > 0 else 0

    # Server badge
    server_badge = '<span style="color:#4caf50">&#9679; UP</span>' if data["_server_status"] == "UP" \
                   else '<span style="color:#f44336">&#9679; DOWN</span>'

    # Tier breakdown
    tier_rows = ""
    if data.get("_v1_tiers"):
        for tier_name, count in sorted(data["_v1_tiers"].items()):
            tier_rows += f'<tr><td>{escape(tier_name)}</td><td style="text-align:right">{count:,}</td></tr>'

    # Build stats cards
    stats_cards = f'''
        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-label">Windows Verified</div>
                <div class="stat-value">{grand_done:,}/{grand_total:,}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Overall Progress</div>
                <div class="stat-value">{grand_pct:.1f}%</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Server Status</div>
                <div class="stat-value" style="font-size:18px;">{data["_server_status"]}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Last Updated</div>
                <div class="stat-value" style="font-size:14px;">{data["_timestamp"]}</div>
            </div>
        </div>
    '''

    # Pilot batch grid — compact summary below main table
    pilot_cards = []
    for pname, psize in PILOT_SIZES.items():
        out_file = f"{pname}_out.jsonl"
        pdone = count_done(out_file)
        ppct = (pdone / psize * 100) if psize > 0 else 0
        p_color, _ = pct_bar(ppct)
        pilot_cards.append(f'''
            <div class="pilot-card">
                <div class="pilot-label">{pname}</div>
                <div class="pilot-bar"><div class="bar-fill" style="background:{p_color};width:{min(int(ppct * 2.4), 120)}px;"></div></div>
                <div class="pilot-count">{pdone}/{psize}</div>
            </div>''')
    pilot_html = ''.join(pilot_cards)

    # Full HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="2">
    <title>JJK VERIFY-7000 Monitor</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; margin: 0; padding: 20px; color: #e0e0e0; }}
        .container {{ max-width: 960px; margin: 0 auto; }}
        h1 {{ color: #e0e0e0; margin-bottom: 8px; font-size: 22px; display: flex; align-items: center; gap: 10px; }}
        .subtitle {{ color: #888; font-size: 13px; margin-bottom: 20px; }}
        .stats-row {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
        .stat-card {{ background: #16213e; border-radius: 10px; padding: 16px 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); flex: 1; min-width: 180px; border: 1px solid #25345c; }}
        .stat-label {{ color: #8899aa; font-size: 11px; text-transform: uppercase; letter-spacing: 0.8px; }}
        .stat-value {{ font-size: 26px; font-weight: bold; color: #64b5f6; margin-top: 6px; }}
        table {{ width: 100%; border-collapse: collapse; background: #16213e; border-radius: 10px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.3); margin-bottom: 24px; border: 1px solid #25345c; }}
        th {{ background: #0f3460; padding: 14px 12px; text-align: left; font-weight: 600; color: #b0bec5; border-bottom: 2px solid #25345c; }}
        td {{ padding: 12px; border-bottom: 1px solid #1e2d4d; color: #e0e0e0; }}
        tr:last-child td {{ border-bottom: none; }}
        tr:hover {{ background: #1a2744; }}
        tr.section-row {{ background: #0f3460 !important; }}
        tr.section-row td {{ padding: 8px 12px; font-size: 13px; font-weight: 700; color: #90caf9; letter-spacing: 0.5px; }}
        .done-cell {{ color: #4caf50 !important; font-weight: 600; }}
        .bar-bg {{ background: #25345c; border-radius: 4px; height: 20px; overflow: hidden; }}
        .bar-fill {{ height: 100%; border-radius: 4px; transition: width 0.3s ease; }}
        .footer {{ margin-top: 24px; text-align: center; color: #556; font-size: 12px; line-height: 1.8; }}
        .pulse-text {{ color: #64b5f6; animation: pulse 1.5s infinite; display: inline-block; }}
        @keyframes pulse {{ 0% {{ opacity: 1; }} 50% {{ opacity: 0.5; }} 100% {{ opacity: 1; }} }}
        .pilot-section {{ background: #16213e; border-radius: 10px; padding: 20px; margin-bottom: 24px; box-shadow: 0 2px 8px rgba(0,0,0,0.3); border: 1px solid #25345c; }}
        .pilot-grid {{ display: flex; gap: 12px; flex-wrap: wrap; }}
        .pilot-card {{ background: #0f3460; border-radius: 8px; padding: 12px; min-width: 100px; flex: 1; }}
        .pilot-label {{ font-size: 13px; font-weight: 600; color: #90caf9; margin-bottom: 6px; }}
        .pilot-bar {{ background: #25345c; border-radius: 4px; height: 12px; overflow: hidden; margin-bottom: 4px; }}
        .pilot-count {{ font-size: 11px; color: #8899aa; text-align: right; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>JJK VERIFY-7000 Live Monitor {server_badge}</h1>
        <div class="subtitle">Manual inline verification · one window at a time · wiki-backed · strict rules · Grand target: {grand_total:,} windows</div>
        {stats_cards}
        <table>
            <thead>
                <tr>
                    <th>Pool</th>
                    <th style="text-align:center">Done</th>
                    <th style="text-align:center">Total</th>
                    <th style="text-align:center">% Done</th>
                    <th>Progress</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        <div class="pilot-section">
            <h3 style="margin-bottom:10px;color:#8899aa;font-size:14px;">Pilot Batches (P1–P5 × 31 = 155 total)</h3>
            <div class="pilot-grid">{pilot_html}</div>
        </div>
        <h3 style="margin-top:24px;margin-bottom:10px;color:#8899aa;font-size:14px;">v1/train.jsonl Tier Breakdown ({sum(data.get('_v1_tiers', {}).values()):,} windows)</h3>
        <table style="width:50%;background:#16213e;border-radius:10px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.3);border:1px solid #25345c;">
            <thead>
                <tr>
                    <th style="background:#0f3460;padding:10px 12px;text-align:left;font-weight:600;color:#b0bec5;">Tier</th>
                    <th style="background:#0f3460;padding:10px 12px;text-align:right;font-weight:600;color:#b0bec5;">Windows</th>
                </tr>
            </thead>
            <tbody>
                {tier_rows}
            </tbody>
        </table>
        <div class="footer">
            Auto-refreshes every 2 seconds · VERIFY-7000 Inline Workflow ·
            Server: :18081 (pid {data["_server_pid"]}) ·
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
        pass


def main():
    parser = argparse.ArgumentParser(description="Verify-7000 progress monitor")
    parser.add_argument("--port", type=int, default=8950, help="Port to serve on (default: 8950)")
    args = parser.parse_args()

    print("Verify-7000 Monitor starting...")
    print("Dashboard URL: http://127.0.0.1:{}/".format(args.port))
    print("")
    print("Monitoring pools:")
    for name, label, win_file, expected in POOLS:
        expected_str = str(expected) if expected else "auto"
        print(f"  {label:25s} -> expected={expected_str}")
    print(f"\nGrand total target: {TOTAL_WINDOWS} windows\n")
    print("Press Ctrl+C to stop\n")

    try:
        while True:
            server = HTTPServer(("127.0.0.1", args.port), Handler)
            server.serve_forever(poll_interval=2)
    except KeyboardInterrupt:
        print("\nMonitor stopped.")


if __name__ == "__main__":
    main()
