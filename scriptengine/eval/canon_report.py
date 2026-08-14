"""Render a measurement run into something a person can act on.

The scores say what the engine got wrong. The diagnosis says why each miss is
missing. This joins them, because neither alone tells you what to do next: a
recall number is not a task, and a bucket count is not a priority until it is
attached to the questions it came from.

The bucket taxonomy is already a remediation map -- each bucket names the layer
the fix belongs in -- so the "what to do" section is generated rather than
written.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

# Bucket -> (where the fix lives, how to act on it, roughly how cheap it is).
# Ordered by items recovered per unit of effort, which is the order the
# generated section uses. No series name appears here, so this belongs in
# Python rather than in a series' overrides.
REMEDY: dict[str, tuple[str, str, int]] = {
    "retrieval gap": (
        "scriptengine/retrieve/",
        "Already in the store and still not returned -- the retriever had every "
        "chance. Trace one query end to end before writing code; the diagnosis "
        "names the row it expected to find.",
        1,
    ),
    "unlinked page": (
        "series/<name>/overrides.yaml",
        "The page exists and nothing ties it to the subject. This is the wiki's "
        "shape, not a retriever bug -- declare the link rather than trying to "
        "infer it.",
        2,
    ),
    "extraction gap": (
        "scriptengine/ingest/abilities.py",
        "The prose names it and the extraction pass did not return it. Fix the "
        "prompt and bump PROMPT_VERSION, or the cached answers survive the "
        "change.",
        3,
    ),
    "corpus gap": (
        "a crawl, or nothing",
        "Not in the subject's prose at all. Check the crawl is not stale for "
        "that page; if it is current, the wiki does not support the claim and a "
        "script must not make it.",
        4,
    ),
    "gold error": (
        "questions/<series>.json",
        "The bank is wrong, not the engine. Retire the item with a reason so "
        "nothing silently re-adds it.",
        0,
    ),
}


def _pct(n: float) -> str:
    return f"{n:.1%}"


def _delta(now: float, before: float | None, pct: bool = True) -> str:
    if before is None:
        return ""
    diff = now - before
    if abs(diff) < 1e-9:
        return " (no change)"
    shown = _pct(abs(diff)) if pct else f"{abs(diff):g}"
    return f" ({'+' if diff > 0 else '-'}{shown})"


def wrong_answers(scores: dict, buckets_by_item: dict) -> list[dict]:
    """Every question the engine did not answer well, worst first.

    Ordered by what actually hurts a script writer rather than by score:
    an answer the engine is confident about and wrong on reaches the page,
    where a visibly thin one gets checked.
    """
    rows = []
    for row in scores.get("rows", []):
        if row["recall"] >= 0.8 and not (
            row["confidence"] in {"exact", "declared"} and row["recall"] < 0.5
        ):
            continue
        confident = row["confidence"] in {"exact", "declared"} and row["recall"] < 0.5
        detail = next((d for d in scores.get("detail", [])
                       if d["query"] == row["query"]), {})
        missing = detail.get("missing", [])
        rows.append({
            **row,
            "missing": missing,
            "confident_and_wrong": confident,
            "buckets": sorted({buckets_by_item.get((row["query"], m), "?")
                               for m in missing}),
            "severity": (0 if confident else
                         1 if row["found"] == 0 else
                         2),
        })
    rows.sort(key=lambda r: (r["severity"], r["recall"], -r["canon"]))
    return rows


def render(scores: dict, diagnosis: dict, evals: dict, meta: dict,
           baseline: set[str] | None = None,
           previous: dict | None = None) -> str:
    summary = scores.get("summary", {})
    rows = scores.get("rows", [])
    facts = scores.get("facts", [])
    buckets = diagnosis.get("buckets", {})
    items = diagnosis.get("items", [])
    by_item = {(i["question"], i["item"]): i["bucket"] for i in items}
    prev = previous or {}
    baseline = baseline or set()

    out: list[str] = []
    w = out.append

    w(f"# Canon run {meta.get('run_id', '')}")
    w("")
    w(f"{summary.get('questions', 0)} set questions and "
      f"{summary.get('fact_questions', 0)} fact questions over "
      f"{len(meta.get('series', []))} series, asked of the live server and "
      f"scored against `questions/`.")
    w("")

    # ── 1. headline ─────────────────────────────────────────────────────────
    w("## Headline")
    w("")
    w("| | |")
    w("|---|---:|")
    w(f"| canon items recovered | **{summary.get('canon_found', 0)}/"
      f"{summary.get('canon_total', 0)}** "
      f"({_pct(summary.get('canon_recall', 0))})"
      f"{_delta(summary.get('canon_recall', 0), prev.get('canon_recall'))} |")
    w(f"| precision, closed sets | **{_pct(summary.get('precision_closed', 0))}** "
      f"over {summary.get('precision_over', '-')} questions"
      f"{_delta(summary.get('precision_closed', 0), prev.get('precision_closed'))} |")
    w(f"| questions at recall 0 | {summary.get('at_recall_zero', 0)}/"
      f"{summary.get('questions', 0)} |")
    w(f"| questions at recall >= 0.8 | {summary.get('at_recall_80', 0)}/"
      f"{summary.get('questions', 0)} |")
    w(f"| confident and wrong | **{len(summary.get('confident_and_wrong', []))}** |")
    if summary.get("fact_questions"):
        w(f"| fact answers present in the bundle | "
          f"{summary.get('fact_present', 0)}/{summary.get('fact_questions', 0)} |")
    w(f"| members returned | {summary.get('members_returned', 0)} |")
    w("")

    if baseline:
        base_rows = [r for r in rows if r["query"] in baseline]
        found = sum(r["found"] for r in base_rows)
        total = sum(r["canon"] for r in base_rows)
        if total:
            w(f"**Comparable subset.** The {len(base_rows)} questions carried over "
              f"from the 2026-08-04 gold set score **{found}/{total}** "
              f"({_pct(found / total)}). That is the only figure comparable with "
              f"earlier runs -- the bank grew underneath every other number here, "
              f"and the questions added since deliberately target known weak "
              f"spots, so a lower headline is the expected and more honest "
              f"result.")
            w("")

    # ── 2. what the engine gets wrong ───────────────────────────────────────
    w("## What the engine gets wrong")
    w("")
    wrong = wrong_answers(scores, by_item)
    absent_facts = [f for f in facts if not f["passed"]]

    if not wrong and not absent_facts:
        w("Nothing below the 0.8 recall line, and every fact answer was present "
          "in the bundle.")
        w("")
    else:
        w("Ordered by what reaches a script. A confidently wrong answer is first "
          "because the engine gives a caller no reason to check it; a visibly "
          "thin one gets checked.")
        w("")
        w("| | series | question | canon | found | recall | engine said | missing |")
        w("|---|---|---|---:|---:|---:|---|---|")
        for r in wrong:
            flag = ("**confident and wrong**" if r["confident_and_wrong"]
                    else "recall 0" if r["found"] == 0 else "")
            miss = ", ".join(r["missing"][:6]) or "-"
            if len(r["missing"]) > 6:
                miss += f", +{len(r['missing']) - 6} more"
            w(f"| {flag} | `{r['series']}` | {r['query']} | {r['canon']} | "
              f"{r['found']} | {_pct(r['recall'])} | `{r['confidence']}` | {miss} |")
        w("")

        if absent_facts:
            w("### Fact answers not present in what was served")
            w("")
            w("The engine serves context rather than an answer sentence, so the "
              "claim here is only that the correct answer was **not present in "
              "the bundle** -- a writer had nothing to write the line from.")
            w("")
            w("| series | question | expected | intruders present |")
            w("|---|---|---|---|")
            for f in absent_facts:
                w(f"| `{f['series']}` | {f['query']} | "
                  f"{', '.join(f['expected'])} | "
                  f"{', '.join(f['intruders']) or '-'} |")
            w("")

    # ── 3. why ──────────────────────────────────────────────────────────────
    w("## Why each miss is missing")
    w("")
    total_missing = sum(buckets.values())
    if total_missing:
        w("Assigned by a lookup against the store, not by eye.")
        w("")
        w("| bucket | count | share | the fix lives in |")
        w("|---|---:|---:|---|")
        for bucket, count in sorted(buckets.items(), key=lambda kv: -kv[1]):
            where = REMEDY.get(bucket, ("-", "", 9))[0]
            w(f"| {bucket} | {count} | {count / total_missing:.0%} | `{where}` |")
        w("")
    else:
        w("No missing items to diagnose.")
        w("")

    # ── 4. what to do ───────────────────────────────────────────────────────
    w("## What to do about it")
    w("")
    if total_missing:
        w("In order of items recovered per unit of effort.")
        w("")
        present = [b for b in buckets if buckets[b]]
        for n, bucket in enumerate(sorted(present,
                                          key=lambda b: REMEDY.get(b, ("", "", 9))[2]), 1):
            where, action, _ = REMEDY.get(bucket, ("-", "No remedy recorded.", 9))
            w(f"{n}. **{bucket} — {buckets[bucket]} items.** {action}")
            w(f"   Fix lives in `{where}`.")
            worst = _worst_for(items, bucket)
            if worst:
                w(f"   Biggest cluster: {worst}.")
            w("")
    else:
        w("Nothing outstanding.")
        w("")

    # ── 5. precision ────────────────────────────────────────────────────────
    padded = sorted(
        (r for r in rows if not r["recall_only"] and r["canon"]
         and r["returned"] > r["canon"] * 2),
        key=lambda r: -(r["returned"] / max(r["canon"], 1)),
    )
    if padded:
        w("## Padded rosters")
        w("")
        w("Closed sets where the engine returned more than twice the canon "
          "count. This is the measured defect: recall is respectable and a "
          "caller still cannot use the answer, because the right names arrive "
          "buried in wrong ones. Roadmap phases 20 (current vs former member) "
          "and 21 (a set the wiki barely fills) are the two named causes.")
        w("")
        w("| series | question | canon | returned | ratio | precision |")
        w("|---|---|---:|---:|---:|---:|")
        for r in padded[:15]:
            w(f"| `{r['series']}` | {r['query']} | {r['canon']} | {r['returned']} | "
              f"{r['returned'] / r['canon']:.0f}x | {_pct(r['precision'])} |")
        w("")

    # ── 6. offline suite ────────────────────────────────────────────────────
    if evals:
        w("## Offline regression suite")
        w("")
        w("A different measurement: `gold_*.json` checked against the crawl, "
          "in-process, boolean. It gates the build; this report does not.")
        w("")
        w("| series | score |")
        w("|---|---|")
        for series in sorted(evals):
            result = evals[series]
            if "skipped" in result:
                w(f"| `{series}` | — {result['skipped']} |")
            else:
                w(f"| `{series}` | {result.get('passed', 0)}/"
                  f"{result.get('questions', 0)} |")
        w("")

    # ── 7. reproducing ──────────────────────────────────────────────────────
    w("## Reproducing")
    w("")
    w("```powershell")
    w("python start_scriptengine.py          # the server must be up")
    w("python -m scriptengine.cli canon-run")
    w("```")
    w("")
    w("The server holds its code in memory, so restart it after any change "
      "under `scriptengine/` or the run measures the old code. `canon-run` "
      "refuses to start against a server older than the newest source file, "
      "because one earlier measurement was taken that way and reported no "
      "change from a fix that had worked.")
    w("")
    w(f"Run metadata: `{meta.get('run_id', '')}`, git `{meta.get('git_sha', '?')}`, "
      f"server started `{meta.get('server_started', '?')}`, "
      f"{meta.get('seconds', 0):.0f}s wall clock.")
    w("")
    w("Sources for every answer are in `questions/<series>.json`, per item.")
    w("")
    return "\n".join(out)


def _worst_for(items: list[dict], bucket: str) -> str:
    counts: dict[str, int] = {}
    for i in items:
        if i["bucket"] == bucket:
            counts[i["question"]] = counts.get(i["question"], 0) + 1
    if not counts:
        return ""
    question, n = max(counts.items(), key=lambda kv: kv[1])
    return f"{question} ({n} items)"


def append_index(reports_root: Path, meta: dict, summary: dict) -> None:
    """One row per run, so a number can be read as a trend rather than a fact."""
    index = reports_root / "index.md"
    if not index.exists():
        header = [
            "# Measurement runs",
            "",
            "Newest last. Each row links the report it came from.",
            "",
            "| run | questions | canon recovered | precision | recall 0 | "
            "confident wrong |",
            "|---|---:|---|---:|---:|---:|",
        ]
        index.write_text("\n".join(header) + "\n", encoding="utf-8")

    run_id = meta.get("run_id", "")
    row = (f"| [{run_id}]({run_id}/REPORT.md) | {summary.get('questions', 0)} | "
           f"{summary.get('canon_found', 0)}/{summary.get('canon_total', 0)} "
           f"({_pct(summary.get('canon_recall', 0))}) | "
           f"{_pct(summary.get('precision_closed', 0))} | "
           f"{summary.get('at_recall_zero', 0)} | "
           f"{len(summary.get('confident_and_wrong', []))} |")
    with index.open("a", encoding="utf-8") as handle:
        handle.write(row + "\n")


def run_id() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
