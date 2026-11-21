"""Pick the pytest files a git diff can affect, with the local decision model.

jev-test-filter (mizchi) covers vitest / jest / node / bun / playwright / go /
rust but not pytest, so this is its pytest adapter, at file granularity: one
`score` question per `tests/test_*.py` file, asked against the diff, using
jev-test-filter's own four levels and its gate (select at or above
`at-risk`; an unsure or missing answer selects the file, never drops it).

The diff is the state. Each file's question carries its imports, which is what
ties a test file to the modules a change touched.

    python tools/jev/pytest_filter.py --base HEAD~1               # print selected files
    python tools/jev/pytest_filter.py --base main --exec -- scriptengine/.venv/bin/python -m pytest -q
    python tools/jev/pytest_filter.py --staged --json

It is a dev-loop speed-up, not a gate: the four standing gates still run the
full `pytest tests/ -q`.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEVELS = [
    "Unrelated to this change: running this test cannot produce a different result than before.",
    "This test exercises code the change touched, but nothing in the change can alter its outcome.",
    "This test could be affected by the change: it might fail.",
    "This test directly exercises behaviour the change altered or broke: it is likely to fail.",
]
TASK = (
    "The state is a git diff. Judge only the one pytest file identified below, and only for "
    "whether this change can alter the outcome of its tests."
)
MAX_DIFF_CHARS = 20_000


def git_diff(base: str | None, staged: bool) -> str:
    args = ["git", "-C", str(ROOT), "diff", "--unified=3"]
    if staged:
        args.append("--staged")
    elif base:
        merge_base = subprocess.run(["git", "-C", str(ROOT), "merge-base", base, "HEAD"],
                                    capture_output=True, text=True, check=True).stdout.strip()
        args.append(merge_base)
    return subprocess.run(args, capture_output=True, text=True, check=True).stdout


def imports_of(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (SyntaxError, UnicodeDecodeError):
        return []
    names: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            names.append(node.module)
        elif isinstance(node, ast.Import):
            names.extend(a.name for a in node.names)
    return sorted({n for n in names if n.startswith("scriptengine") or n.startswith("tools")})


def question(path: Path) -> dict:
    return {"type": "score", "instructions": {
        "task": TASK, "test_file": str(path.relative_to(ROOT)),
        "imports": imports_of(path)}, "criteria": LEVELS}


def ask(base_url: str, state: str, questions: dict, timeout: float) -> dict:
    body = json.dumps({"model": "jev-latest", "state": state, "questions": questions}).encode()
    req = urllib.request.Request(base_url.rstrip("/") + "/v1/systemone", data=body, method="POST", headers={
        "content-type": "application/json",
        "authorization": "Bearer " + os.environ.get("JEV_API_KEY", "local")})
    with urllib.request.urlopen(req, timeout=timeout) as reply:
        return json.load(reply).get("answers", {})


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", help="compare against the merge base with this ref")
    ap.add_argument("--staged", action="store_true")
    ap.add_argument("--base-url", default=os.environ.get("JEV_API_BASE_URL", "http://127.0.0.1:8018"))
    ap.add_argument("--cutoff", type=int, default=2)
    ap.add_argument("--min-confidence", type=float, default=0.5)
    ap.add_argument("--batch", type=int, default=24)
    ap.add_argument("--timeout", type=float, default=300.0)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--exec", dest="exec_cmd", nargs=argparse.REMAINDER)
    a = ap.parse_args()

    diff = git_diff(a.base, a.staged)
    files = sorted((ROOT / "tests").glob("test_*.py"))
    if not diff.strip():
        print("no change; nothing selected", file=sys.stderr)
        return 0
    state = diff[:MAX_DIFF_CHARS]

    results = []
    for i in range(0, len(files), a.batch):
        chunk = files[i:i + a.batch]
        qs = {f"q{j:04d}": question(p) for j, p in enumerate(chunk, i)}
        try:
            answers = ask(a.base_url, state, qs, a.timeout)
        except (urllib.error.URLError, TimeoutError) as e:
            print(f"jev failed ({e}); selecting the whole batch", file=sys.stderr)
            answers = {}
        for j, p in enumerate(chunk, i):
            ans = answers.get(f"q{j:04d}") or {}
            score, conf = ans.get("score"), ans.get("confidence")
            if not isinstance(score, (int, float)):
                selected, reason = True, "missing"
            elif conf is not None and conf < a.min_confidence:
                selected, reason = True, "unsure"
            else:
                selected, reason = score >= a.cutoff, "above" if score >= a.cutoff else "below"
            results.append({"file": str(p.relative_to(ROOT)), "score": score, "confidence": conf,
                            "selected": selected, "reason": reason})

    chosen = [r["file"] for r in results if r["selected"]]
    if a.json:
        print(json.dumps({"selected": len(chosen), "total": len(results), "files": results,
                          "diff_truncated": len(diff) > MAX_DIFF_CHARS}, indent=2))
    elif not a.exec_cmd:
        print(" ".join(chosen))
    print(f"pytest_filter: {len(chosen)}/{len(results)} test files selected", file=sys.stderr)

    if a.exec_cmd:
        cmd = [c for c in a.exec_cmd if c != "--"]
        if not chosen:
            print("nothing selected; not running", file=sys.stderr)
            return 0
        return subprocess.call(cmd + chosen, cwd=ROOT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
