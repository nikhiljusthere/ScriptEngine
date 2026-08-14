"""One command that measures the engine and writes the report a human reads.

The pieces already existed and were run by hand, in order, from three different
working directories, writing into whichever folder `argv` pointed at. That is
how six earlier answer sheets were lost. This orchestrates them into a single
run folder under `reports/`, and refuses to start when the measurement would be
untrustworthy.

Two refusals, both operational, both learned from a real incident:

* **The server is down.** Thirty questions in, a 503 is an hour wasted.
* **The server is stale.** Sheet 7 records a measurement taken against a server
  running superseded code, which reported no change from a fix that had in fact
  worked. The API holds its code in memory; editing a module under
  `scriptengine/` does not reach a process that is already serving. `/health`
  reports when the process started, and this compares that against the newest
  `.py` on disk.

A bad *score* is never a failure. `cli eval` gates the build because it is a
regression suite; this is a measurement, and a measurement command that fails
the build is one nobody runs.
"""

from __future__ import annotations

import json
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scriptengine.config import REPO_ROOT, Settings
from scriptengine.eval import canon_gold, canon_report
from scriptengine.eval import questions as Q

# Everything the runner reads over HTTP goes to the same place `canon_gold`
# asks, so a redirected base only has to be changed in one file.
BASE = canon_gold.BASE

START_HINT = "python start_scriptengine.py"

# `scriptengine/.venv` lives under the package root and holds tens of thousands
# of `.py` files whose mtimes have nothing to do with this project's code. A
# staleness check that walked them would compare the server against pip.
SKIP_DIRS = {".venv", "__pycache__", ".git", "node_modules"}


class CanonRunError(RuntimeError):
    """An operational failure: the run cannot produce a trustworthy number.

    Distinct from a bad score, which is the point of the exercise and never
    raises.
    """


# ── preflight ────────────────────────────────────────────────────────────────


def health(base: str = BASE, timeout: int = 10) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(f"{base}/health", timeout=timeout) as response:
            return json.loads(response.read())
    except urllib.error.URLError as error:
        raise CanonRunError(
            f"no server on {base} ({error.reason}). Start it with `{START_HINT}`"
        ) from error
    except (TimeoutError, OSError) as error:  # pragma: no cover - network shape
        raise CanonRunError(
            f"{base} did not answer /health ({error}). Start it with `{START_HINT}`"
        ) from error


def newest_source(root: Path | None = None) -> tuple[Path | None, datetime]:
    """The most recently modified `.py` under the package, and when.

    Returns the epoch when there is nothing to compare against, so a caller
    can treat "no sources found" as "not stale" rather than as an error.
    """
    root = root or (REPO_ROOT / "scriptengine")
    newest: Path | None = None
    stamp = 0.0
    for path in root.rglob("*.py"):
        if SKIP_DIRS & set(path.parts):
            continue
        mtime = path.stat().st_mtime
        if mtime > stamp:
            newest, stamp = path, mtime
    return newest, datetime.fromtimestamp(stamp, timezone.utc)


def check_fresh(started: str, root: Path | None = None) -> None:
    """Refuse a server older than the code it is supposed to be running."""
    if not started:
        raise CanonRunError(
            "/health reports no `started` field, so staleness cannot be "
            "checked. Restart the server on current code and try again."
        )
    try:
        server_started = datetime.fromisoformat(started)
    except ValueError as error:
        raise CanonRunError(f"/health `started` is unreadable: {started!r}") from error
    if server_started.tzinfo is None:
        server_started = server_started.replace(tzinfo=timezone.utc)

    path, modified = newest_source(root)
    if path is None:
        return
    if modified > server_started:
        raise CanonRunError(
            f"server started {server_started:%Y-%m-%d %H:%M:%S%z}, but "
            f"{path.relative_to(REPO_ROOT)} was modified "
            f"{modified:%Y-%m-%d %H:%M:%S%z}. The API holds its code in "
            f"memory — restart it (`{START_HINT}`) or this measures the old "
            f"code."
        )


def check_series(payload: dict, wanted: list[str]) -> None:
    """Refuse a series the server cannot answer for, before asking anything."""
    indexed = set(payload.get("series") or [])
    missing = sorted(set(wanted) - indexed)
    if missing:
        raise CanonRunError(
            f"the bank asks about {', '.join(missing)}, which the server does "
            f"not serve (it has: {', '.join(sorted(indexed)) or 'nothing'}). "
            f"Index the series or narrow the run with --series."
        )


# ── run metadata ─────────────────────────────────────────────────────────────


def git_sha() -> str:
    """The commit the measurement was taken at, or `?`.

    Without it a moved number is an anecdote — there is no way to say which
    code produced it.
    """
    try:
        out = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=10, check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return "?"
    return out.stdout.strip() or "?"


def previous_summary(reports_root: Path, current: str) -> dict:
    """The last run's summary, for the delta columns. Absent on the first run."""
    if not reports_root.exists():
        return {}
    folders = sorted(
        (p for p in reports_root.iterdir() if p.is_dir() and p.name != current),
        reverse=True,
    )
    for folder in folders:
        scores = folder / "canon_scores.json"
        if scores.exists():
            try:
                return json.loads(scores.read_text(encoding="utf-8")).get("summary", {})
            except (OSError, json.JSONDecodeError):
                continue
    return {}


def answers_markdown(scores: dict, facts: list[dict]) -> str:
    """The raw per-question dump, kept out of the report and out of git.

    Long enough to bury the report if inlined, and regenerable, which is why
    `.gitignore` carries `reports/*/answers.md` and nothing else under
    `reports/`.
    """
    out: list[str] = ["# Raw answers", ""]
    detail = {d["query"]: d for d in scores.get("detail", [])}
    for row in scores.get("rows", []):
        entry = detail.get(row["query"], {})
        out += [
            f"## [{row['series']}] {row['query']}",
            "",
            f"- basis `{row['set']}`, confidence `{row['confidence']}`, "
            f"returned {row['returned']} of {row['available']} available",
            f"- recall {row['recall']:.0%} ({row['found']}/{row['canon']}), "
            f"precision {row['precision']:.0%}",
            f"- **found**: {', '.join(entry.get('found') or []) or '—'}",
            f"- **missing**: {', '.join(entry.get('missing') or []) or '—'}",
            f"- **returned**: {', '.join(entry.get('members') or []) or '—'}",
            "",
        ]
    if facts:
        out += ["# Fact questions", ""]
        for fact in facts:
            mark = "present" if fact["passed"] else "ABSENT"
            out += [
                f"## [{fact['series']}] {fact['query']}",
                "",
                f"- expected: {', '.join(fact['expected'])}",
                f"- answer **{mark}** in the bundle "
                f"(routed `{fact['routed']}`, confidence `{fact['confidence']}`)",
            ]
            if fact["intruders"]:
                out.append(f"- named distractors also present: "
                           f"{', '.join(fact['intruders'])}")
            out.append("")
    return "\n".join(out)


# ── the run ──────────────────────────────────────────────────────────────────


def run(series: list[str] | None = None, skip_eval: bool = False,
        dry_run: bool = False, out: Path | None = None,
        log: Callable[[str], None] = print) -> dict[str, Any]:
    """Measure the engine and write a run folder. Raises only on operations."""
    settings = Settings()
    reports_root = Path(out) if out else settings.reports_root

    banks = Q.load_all(settings.questions_root)
    Q.validate(banks)

    wanted = sorted(series) if series else sorted(b.series for b in banks)
    unknown = sorted(set(wanted) - {b.series for b in banks})
    if unknown:
        raise CanonRunError(
            f"no question bank for {', '.join(unknown)} in {settings.questions_root}"
        )

    gold = [g for g in canon_gold.GOLD if g[0] in set(wanted)]
    facts_asked = [f for f in canon_gold.FACTS if f.series in set(wanted)]
    baseline = {q.question for q in Q.sets(banks) if q.baseline and q.series in set(wanted)}

    if dry_run:
        log(f"bank validates: {len(gold)} set questions, {len(facts_asked)} fact "
            f"questions over {len(wanted)} series ({', '.join(wanted)}).")
        log(f"{len(baseline)} of the set questions are the migrated baseline.")
        log(f"would write into {reports_root}. Nothing was asked of the server.")
        return {"dry_run": True, "sets": len(gold), "facts": len(facts_asked),
                "series": wanted, "baseline": len(baseline)}

    payload = health()
    check_fresh(payload.get("started", ""))
    check_series(payload, wanted)

    started = time.time()
    run_id = canon_report.run_id()
    folder = reports_root / run_id
    folder.mkdir(parents=True, exist_ok=True)

    log(f"scoring {len(gold)} set questions over {', '.join(wanted)}…")
    scores = canon_gold.score_sets(gold)
    facts = canon_gold.score_facts(facts_asked) if facts_asked else []
    summary = canon_gold.summarise(scores["rows"], facts)
    scores_path = folder / "canon_scores.json"
    scores_path.write_text(
        json.dumps({"rows": scores["rows"], "detail": scores["detail"],
                    "facts": facts, "summary": summary}, indent=2),
        encoding="utf-8")

    log("diagnosing misses…")
    from scriptengine.eval.diagnose_misses import diagnose

    diagnosis_path = Path(diagnose(str(scores_path)))
    diagnosis = json.loads(diagnosis_path.read_text(encoding="utf-8"))

    evals = _run_eval(wanted, skip_eval, log)
    (folder / "eval.json").write_text(json.dumps(evals, indent=2), encoding="utf-8")

    meta = {
        "run_id": run_id,
        "series": wanted,
        "git_sha": git_sha(),
        "server_started": payload.get("started", "?"),
        "health": payload,
        "questions": {b.series: len(b.questions) for b in banks},
        "seconds": round(time.time() - started, 1),
        "skip_eval": skip_eval,
    }
    (folder / "run.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (folder / "answers.md").write_text(answers_markdown(scores, facts),
                                       encoding="utf-8")

    report = canon_report.render(
        {"rows": scores["rows"], "detail": scores["detail"], "facts": facts,
         "summary": summary},
        diagnosis, evals, meta,
        baseline=baseline,
        previous=previous_summary(reports_root, run_id),
    )
    (folder / "REPORT.md").write_text(report, encoding="utf-8")
    canon_report.append_index(reports_root, meta, summary)

    log(f"\nwrote {folder / 'REPORT.md'}")
    return {"folder": folder, "summary": summary, "meta": meta}


def _run_eval(wanted: list[str], skip_eval: bool,
              log: Callable[[str], None]) -> dict[str, Any]:
    """`cli eval`'s in-process suite, per series, recorded but never gating.

    Loads an embedder and a reranker in *this* process while the server may
    still hold its own (`model_idle_unload_seconds`), which double-allocates on
    a single GPU. `--skip-eval` is the way out while the server is hot; the
    rest of the run is pure HTTP.
    """
    from scriptengine.config import series_paths

    evals: dict[str, Any] = {}
    if skip_eval:
        return {s: {"skipped": "--skip-eval"} for s in wanted}

    from scriptengine.eval.harness import evaluate

    for name in wanted:
        gold_file = Path(__file__).parent / f"gold_{name}.json"
        if not gold_file.exists():
            evals[name] = {"skipped": "no gold set"}
            continue
        try:
            report = evaluate(series_paths(name))
        except Exception as error:  # noqa: BLE001 - a bad score must not stop the run
            evals[name] = {"error": str(error)}
            log(f"  eval {name}: {error}")
            continue
        evals[name] = {"passed": report["passed"], "questions": report["questions"],
                       "score": report["score"]}
        log(f"  eval {name}: {report['passed']}/{report['questions']} "
            f"({report['score']:.0%})")
    return evals
