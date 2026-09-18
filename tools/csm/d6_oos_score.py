"""D6: pre-extraction baseline for the frozen green30 + oos200 rows, via :8000.

Reads the frozen 230 rows (reports/csm/D6_OOS_FREEZE.jsonl), sends each query
to the live :8000 /context endpoint in the P2.3 shape ({"series": "csm",
"query": q, "mode": "qa"} -- no subject, endpoint-default budget/top_k), and
grades with the same judge rule as p23_grader (tools/census_dimensions.judge
over span_recall.served_text). No in-process model load: `:8000` stays the
single model holder, so Qwen keeps the card's headroom untouched.

Sequential (one model, no concurrency), 60 s timeout, 3 retries per row.
Output: reports/csm/D6_OOS_PRE.jsonl (id/set/in_window/class/subject/verdict/
hits/missing/error/t_ms per row) + a summary. Exit 0 if errors < 10% of the
rows, else 3 (mirrors p23_grader).

Run with :8000 up (CUDA):
  ./scriptengine/.venv/bin/python tools/csm/d6_oos_score.py
"""
from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from tools.census_dimensions import judge  # noqa: E402  same MECH_GREEN rule as p23_grader
from scriptengine.eval.span_recall import served_text  # noqa: E402

FREEZE = ROOT / "reports/csm/D6_OOS_FREEZE.jsonl"
OUT = ROOT / "reports/csm/D6_OOS_PRE.jsonl"
BASE = "http://127.0.0.1:8000"
TIMEOUT = 60.0
RETRIES = 3


def ask(q: str) -> dict:
    body = json.dumps({"series": "csm", "query": q, "mode": "qa"}).encode()
    last: Exception | None = None
    for _ in range(RETRIES):
        try:
            req = urllib.request.Request(
                f"{BASE}/context", data=body,
                headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
                return json.loads(resp.read())
        except Exception as e:
            last = e
            time.sleep(2.0)
    assert last is not None
    raise last


def main() -> int:
    rows = [json.loads(l) for l in FREEZE.read_text().splitlines() if l.strip()]
    out: list[dict] = []
    errors = 0
    t0 = time.time()
    for i, row in enumerate(rows, 1):
        rec = {k: row[k] for k in ("id", "set", "in_window", "class", "subject")}
        t1 = time.time()
        try:
            rec.update(judge(row, served_text(ask(row["q"]))))
            rec["error"] = None
        except Exception as e:
            rec.update({"hits": [], "missing": list(row["expect"]),
                        "verdict": "ERROR", "error": f"{type(e).__name__}: {e}", "served": ""})
            errors += 1
        rec["t_ms"] = int((time.time() - t1) * 1000)
        out.append(rec)
        if i % 25 == 0 or i == len(rows):
            OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))
            verdicts = {v: sum(1 for r in out if r["verdict"] == v)
                        for v in {r["verdict"] for r in out}}
            print(f"[{i}/{len(rows)}] verdicts={verdicts} errors={errors} "
                  f"elapsed={int(time.time() - t0)}s", flush=True)
    OUT.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out))

    by_set: dict[str, dict] = {}
    for s in ("green30", "oos200"):
        vs = {r["verdict"] for r in out if r["set"] == s}
        by_set[s] = {v: sum(1 for r in out if r["set"] == s and r["verdict"] == v) for v in vs}
    print(json.dumps({"rows": len(out), "errors": errors, "by_set": by_set,
                      "elapsed_s": int(time.time() - t0)}, indent=2))
    return 0 if errors < 0.1 * len(out) else 3


if __name__ == "__main__":
    sys.exit(main())