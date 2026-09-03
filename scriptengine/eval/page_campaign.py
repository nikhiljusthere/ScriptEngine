"""The page-driven accuracy campaign: one page cluster's batch, scored live.

`canon-run` measures the official bank in `questions/<series>.json`. This
measures a single campaign batch -- `_jjk_page_<slug>.json`, roughly 100
questions about one wiki page and its sibling pages (its synopsis, its
battles, its category members) -- so each cluster can be driven to 100%
exact/present before the next one starts.

Batches live under `_*.json` names on purpose: `load_all` skips them, so a
campaign in progress never moves the official bank's number or breaks
`audit_declarations`. When a batch reaches 100% it stays where it is; the
declarations that got it there are what the engine keeps.

Same scoring as `canon-run` (reused from `canon_gold`, not re-implemented),
same preflight refusals, and a report shaped for triage: every question with
its missing items and intruders beside it, because the campaign's loop is to
assign each failure -- gold error or engine gap -- before anything else moves.

Exit codes differ from `canon-run` on one point only: 2 means "not yet 100%",
so the test-fix-retest loop can be scripted. A bad score is still never a
crash, and exit 1 is still reserved for an untrustworthy run: no server, a
server running superseded code, or a batch that does not validate.
"""

from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scriptengine.config import Settings
from scriptengine.eval import canon_gold
from scriptengine.eval.canon_run import CanonRunError, check_fresh, check_series, health
from scriptengine.eval import questions as Q


def batch_path(settings: Settings | None = None, series: str = "", slug: str = "") -> Path:
    """Where a campaign batch lives: `questions/_<series>_page_<slug>.json`."""
    root = (settings or Settings()).questions_root
    return root / f"_{series}_page_{slug}.json"


def run(series: str, slug: str, dry_run: bool = False, out: Path | None = None,
        log: Callable[[str], None] = print,
        settings: Settings | None = None) -> dict[str, Any]:
    """Score one batch against the live server and write a triage report.

    Returns `{"complete": True}` when every question is exact/present. Raises
    only on operations (no server, stale server, invalid or missing batch).
    """
    settings = settings or Settings()
    path = batch_path(settings, series, slug)
    if not path.exists():
        raise CanonRunError(
            f"no campaign batch at {path}. Author it first: ~100 questions "
            f"about the page cluster, every gold item sourced to a page in "
            f"the local corpus."
        )

    try:
        bank = Q.load_file(path)
        if bank.series != series:
            raise Q.QuestionsError(
                f"{path.name} declares series {bank.series!r}, "
                f"asked for as {series!r}"
            )
        Q.validate([bank])
    except Q.QuestionsError as error:
        # An invalid batch scores nothing; it must stop the run, not crash it.
        raise CanonRunError(str(error)) from error

    sets_qs = [q for q in bank.questions if q.kind == "set"]
    facts_qs = [q for q in bank.questions if q.kind == "fact"]
    gold = [(q.series, q.question,
             [(i.item, list(i.aliases)) for i in q.scored_items()])
            for q in sets_qs]

    reports_root = Path(out) if out else settings.reports_root / "page-campaign"

    if dry_run:
        log(f"batch validates: {len(sets_qs)} set questions, {len(facts_qs)} fact "
            f"questions ({path.name}).")
        log("would write into "
            f"{reports_root}/{series}-{slug}-<run>/. Nothing was asked of the server.")
        return {"dry_run": True, "sets": len(sets_qs), "facts": len(facts_qs)}

    payload = health()
    check_fresh(payload.get("started", ""))
    check_series(payload, [series])

    started = time.time()
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    folder = reports_root / f"{series}-{slug}-{run_id}"
    folder.mkdir(parents=True, exist_ok=True)

    log(f"scoring {len(gold)} set + {len(facts_qs)} fact questions "
        f"({path.name})…")
    # Sets keep the writer's tight top-8 (precision matters for rosters); facts
    # score on a wide beam -- the campaign measures "is this fact retrievable from
    # the corpus", and a niche fact that ranks just past the top-8 still is.
    scores = canon_gold.score_sets(gold) if gold else {"rows": [], "detail": []}
    facts = canon_gold.score_facts(facts_qs, top_k=50) if facts_qs else []
    summary = canon_gold.summarise(scores["rows"], facts)

    # Per-question verdicts, the unit of the campaign's triage loop. A set is
    # done when it came back exactly right; a fact when its answer was present.
    detail_by_query = {d["query"]: d for d in scores.get("detail", [])}
    id_by_query = {q.question: q.id for q in sets_qs}
    results: list[dict[str, Any]] = []
    for row in scores.get("rows", []):
        entry = detail_by_query.get(row["query"], {})
        results.append({
            "id": id_by_query.get(row["query"], ""),
            "kind": "set", "query": row["query"],
            "passed": bool(row["exact"]),
            "basis": row["set"], "confidence": row["confidence"],
            "found": entry.get("found") or [],
            "missing": entry.get("missing") or [],
            "returned": entry.get("members") or [],
        })
    for fact in facts:
        results.append({
            "id": fact["id"], "kind": "fact", "query": fact["query"],
            "passed": bool(fact["passed"]),
            "basis": f"routed {fact['routed']}", "confidence": fact["confidence"],
            "found": fact["found"], "missing": fact["missing"],
            "returned": [], "intruders": fact.get("intruders") or [],
        })

    complete = all(r["passed"] for r in results) and bool(results)
    meta = {
        "run_id": run_id,
        "series": series,
        "slug": slug,
        "batch": path.name,
        "server_started": payload.get("started", "?"),
        "seconds": round(time.time() - started, 1),
        "complete": complete,
    }

    (folder / "scores.json").write_text(
        json.dumps({"rows": scores["rows"], "detail": scores["detail"],
                    "facts": facts, "summary": summary}, indent=2),
        encoding="utf-8")
    (folder / "run.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    (folder / "REPORT.md").write_text(
        report_markdown(bank, results, summary, meta), encoding="utf-8")

    log(f"\n{'COMPLETE' if complete else 'NOT COMPLETE'}: "
        f"{sum(1 for r in results if r['passed'])}/{len(results)} questions passed")
    for r in results:
        if not r["passed"]:
            miss = ", ".join(r["missing"]) or "-"
            extra = f"  intruders: {', '.join(r['intruders'])}" if r.get("intruders") else ""
            log(f"  FAIL [{r['kind']}] {r['query']}  missing: {miss}{extra}")
    log(f"\nwrote {folder / 'REPORT.md'}")
    return {"folder": folder, "summary": summary, "meta": meta,
            "results": results, "complete": complete}


def report_markdown(bank: Q.Bank, results: list[dict[str, Any]],
                    summary: dict, meta: dict) -> str:
    """The triage sheet: every question with what it missed beside it."""
    by_id = {q.id: q for q in bank.questions}
    out: list[str] = [
        f"# Page campaign {meta['series']}/{meta['slug']} — {meta['run_id']}",
        "",
        f"Batch `{meta['batch']}`: {len(results)} questions "
        f"({sum(1 for r in results if r['kind'] == 'set')} set, "
        f"{sum(1 for r in results if r['kind'] == 'fact')} fact), scored against the "
        f"live server (started {meta['server_started']}), {meta['seconds']}s wall clock.",
        "",
        "## Headline",
        "",
        "| | |",
        "|---|---:|",
        f"| **questions passed** | **{sum(1 for r in results if r['passed'])}/{len(results)}** |",
        f"| set questions exact | {summary.get('exact_answers', 0)}/{summary.get('exact_of', 0)} "
        f"({summary.get('exact_rate', 0):.1%}) |",
        f"| canon items recovered | {summary.get('canon_found', 0)}/"
        f"{summary.get('canon_total', 0)} ({summary.get('canon_recall', 0):.1%}) |",
        f"| fact answers present | {summary.get('fact_present', 0)}/"
        f"{summary.get('fact_questions', 0)} |",
        "",
    ]

    failed = [r for r in results if not r["passed"]]
    out += ["## Failures to triage", ""]
    if not failed:
        out.append("None. The batch is at 100%.")
    else:
        out.append("| | kind | question | missing | returned / intruders | source |")
        out.append("|---|---|---|---|---|---|")
        for r in failed:
            q = by_id.get(r["id"]) if r["id"] else None
            source = f"<sub>{q.sources[0]}</sub>" if q and q.sources else "-"
            returned = (", ".join(r["returned"][:12]) + ("…" if len(r["returned"]) > 12 else "")
                        or "-")
            intruders = f"; **intruders**: {', '.join(r['intruders'])}" \
                if r.get("intruders") else ""
            out.append(
                f"| `{r['confidence']}` | {r['kind']} | {r['query']} | "
                f"{', '.join(r['missing']) or '-'} | {returned}{intruders} | {source} |"
            )

    out += ["", "## All questions", "",
            "| passed | kind | question | basis / confidence | detail |",
            "|---|---|---|---|---|"]
    for r in results:
        mark = "**yes**" if r["passed"] else "no"
        if r["kind"] == "set":
            detail = (f"{len(r['found'])} found, {len(r['missing'])} missing; "
                      f"returned {len(r['returned'])}")
        else:
            detail = ", ".join(r["found"]) or "answer absent"
        out.append(f"| {mark} | {r['kind']} | {r['query']} | "
                   f"`{r['basis']}` / `{r['confidence']}` | {detail} |")

    out += ["",
            "Triage rule: a miss is either a **gold error** (the batch's answer is "
            "not what the cited page documents -- fix the batch) or an **engine gap** "
            "(undeclared roster, stolen routing, missing link -- declare it in "
            "`series/<name>/overrides.yaml` with a comment naming this question).",
            ""]
    return "\n".join(out)
