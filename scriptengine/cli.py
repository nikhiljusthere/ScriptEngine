"""ScriptEngine command line.

    python -m scriptengine.cli --help

Commands are added as their phase lands. Anything not yet implemented exits
non-zero with a message naming the phase, rather than failing obscurely.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from scriptengine.config import get_settings, script_destination, series_paths

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="A universal knowledge engine over Fandom wikis.",
)
console = Console()


def _not_yet(phase: str, what: str) -> None:
    console.print(f"[yellow]{what} lands in {phase}.[/yellow]")
    raise typer.Exit(code=2)


def _load_overrides(paths) -> dict:
    """Read `series/<name>/overrides.yaml`, the only place series-specific rules live."""
    if not paths.overrides.exists():
        return {}
    import yaml

    loaded = yaml.safe_load(paths.overrides.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        console.print(f"[yellow]Ignoring {paths.overrides}: expected a mapping.[/yellow]")
        return {}
    return loaded


@app.command()
def crawl(
    series: str = typer.Option(..., "--series", help="Short series id, e.g. 'jjk'."),
    start_url: str = typer.Option(..., "--start-url", help="Any page on the target wiki."),
    max_pages: int = typer.Option(0, "--max-pages", help="0 crawls the whole wiki."),
    refresh: bool = typer.Option(
        False, "--refresh", help="Refetch pages already on disk instead of resuming."
    ),
    verbose: bool = typer.Option(False, "--verbose", help="Show per-request logging."),
) -> None:
    """Crawl a Fandom wiki into `series/<name>/`."""
    import asyncio
    import logging

    from scriptengine.ingest.crawler import WikiCrawler

    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    settings = get_settings()
    paths = series_paths(series, settings)
    overrides = _load_overrides(paths)

    from scriptengine.ingest.crawler import EnumerationFailed

    async def run() -> dict:
        async with WikiCrawler(settings) as crawler:
            return await crawler.crawl(start_url, paths, max_pages, overrides, refresh)

    try:
        manifest = asyncio.run(run())
    except EnumerationFailed as error:
        console.print(f"\n[red]Crawl aborted:[/red] {error}")
        raise typer.Exit(code=1) from error

    if manifest.get("status") == "already_running":
        console.print("[yellow]Another crawl is already running.[/yellow]")
        raise typer.Exit(code=1)

    console.print(
        f"\n[green]Fetched {manifest['pages_written']} pages this run[/green] "
        f"({manifest['pages_skipped']} skipped, {manifest['pages_failed']} failed) — "
        f"{manifest['pages_on_disk']} of {manifest['pages_enumerated']} now on disk"
    )
    discovered = sorted(set(manifest["ontology"]["infobox_types"].values()))
    console.print(f"Discovered {len(discovered)} page types: {', '.join(discovered)}")
    console.print(f"\nNext: [bold]audit --series {series}[/bold]")


@app.command()
def audit(
    series: str = typer.Option(..., "--series"),
    sample: int = typer.Option(0, "--sample", help="Audit only the first N pages."),
    page: str = typer.Option("", "--page", help="Inspect one page in detail."),
) -> None:
    """Report what the extractor understood, before you trust it."""
    from scriptengine.ingest.audit import audit_series, compare_page, write_report
    from scriptengine.ingest.crawler import load_pages

    paths = series_paths(series)

    if page:
        for candidate in load_pages(paths):
            if candidate.title.lower() == page.lower():
                console.print_json(json.dumps(compare_page(candidate), ensure_ascii=False))
                return
        console.print(f"[red]No page titled {page!r} in series {series!r}.[/red]")
        raise typer.Exit(code=1)

    report = audit_series(paths, sample)
    if "error" in report:
        console.print(f"[red]{report['error']}[/red]")
        raise typer.Exit(code=1)

    coverage, graph = report["coverage"], report["graph"]
    sourcing = report["sourcing"]

    summary = Table(title=f"Extraction audit — {series} ({report['sampled']} pages)")
    summary.add_column("metric")
    summary.add_column("value", justify="right")
    summary.add_row("pages typed", f"{coverage['typed']:.1%}")
    summary.add_row("with infobox", f"{coverage['with_infobox']:.1%}")
    summary.add_row("sections / page", f"{coverage['mean_sections']}")
    summary.add_row("facts / page", f"{coverage['mean_facts']}")
    summary.add_row("words / page", f"{coverage['mean_words']}")
    summary.add_row("citations", f"{coverage['citations']}")
    summary.add_row("edges", f"{graph['edges']}")
    summary.add_row("edges resolved", f"{graph['resolved']:.1%}")
    # What a script can put a tag on. `cited directly` is where the wiki wrote a
    # reference; `sentences w/ chapter` is what those references cover once each
    # one is read as covering the sentences before it.
    summary.add_row("cited directly", f"{sourcing['cited_directly']:.1%}")
    summary.add_row("sentences w/ chapter", f"{sourcing['with_chapter']:.1%}")
    summary.add_row("sentences w/ episode", f"{sourcing['with_episode']:.1%}")
    summary.add_row("chapters mapped to episodes", f"{sourcing['chapter_episode_map']}")
    console.print(summary)

    types = Table(title="Discovered page types")
    types.add_column("type")
    types.add_column("pages", justify="right")
    for name, count in report["types"].items():
        types.add_row(name, str(count))
    console.print(types)

    console.print()
    for check in report["checks"]:
        if check.get("skipped"):
            console.print(f"  [dim]SKIP[/dim]  {check['name']}: {check['meaning']}")
            continue
        mark = "[green]PASS[/green]" if check["passed"] else "[red]FAIL[/red]"
        console.print(
            f"  {mark}  {check['name']}: {check['value']} "
            f"(threshold {check['threshold']})"
        )
        if not check["passed"]:
            console.print(f"        [dim]{check['meaning']}[/dim]")

    console.print(f"\nFull report: {write_report(paths, report)}")
    if not report["passed"]:
        raise typer.Exit(code=1)


@app.command()
def index(
    series: str = typer.Option(..., "--series"),
    no_embed: bool = typer.Option(
        False, "--no-embed", help="Skip vectors. Facts, graph and BM25 still work."
    ),
) -> None:
    """Build the fact store, graph, BM25 index and vectors."""
    import logging

    from rich.progress import Progress as RichProgress

    from scriptengine.index.build import build_index, write_status

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    paths = series_paths(series)

    with RichProgress(transient=True) as bar:
        tasks: dict[str, int] = {}

        def on_progress(stage: str, done: int, total: int) -> None:
            if stage not in tasks:
                tasks[stage] = bar.add_task(stage, total=total)
            bar.update(tasks[stage], completed=done, total=total)

        report = build_index(paths, embed=not no_embed, progress=on_progress)

    if "error" in report:
        console.print(f"[red]{report['error']}[/red]")
        raise typer.Exit(code=1)

    stats = report["stats"]
    table = Table(title=f"Index built — {series}")
    table.add_column("store")
    table.add_column("rows", justify="right")
    for name in ("documents", "sections", "nodes", "edges", "facts", "chunks"):
        table.add_row(name, f"{stats[name]:,}")
    table.add_row("nodes with a page", f"{stats['resolved_nodes']:,}")
    table.add_row("vectors", f"{report['embedded']:,}")
    console.print(table)

    console.print(f"\nStatus: {write_status(paths, report)}")
    if no_embed:
        console.print(
            "[yellow]No vectors built. Lexical and graph retrieval work; "
            "semantic search needs `index` without --no-embed.[/yellow]"
        )


@app.command()
def rosters(
    series: str = typer.Option(..., "--series"),
) -> None:
    """The enumeration sets this series declares.

    Without this the registry is invisible to whoever writes the next script,
    and they would go back to guessing which topics the engine answers well.
    """
    from scriptengine.config import load_overrides
    from scriptengine.retrieve.roster import load_rosters
    from scriptengine.stores.facts import FactStore

    paths = series_paths(series)
    declared = load_rosters(load_overrides(paths))
    if not declared:
        console.print(f"[yellow]{series} declares no rosters.[/yellow]")
        return

    table = Table(title=f"Declared rosters — {series}")
    table.add_column("set")
    table.add_column("members", justify="right")
    table.add_column("grouped by")
    table.add_column("asked for by")

    with FactStore(paths.facts_db) as store:
        for definition in declared:
            if definition.groups:
                size = sum(
                    1 for c in definition.groups.values()
                    if store.documents_in_category(c, limit=1)
                )
                count, grouped = f"{size} groups", "itself"
            else:
                from scriptengine.retrieve.roster import _declared_members

                found = len(_declared_members(store, definition))
                count = str(found)
                grouped = definition.group_by or ""
                if not found:
                    count = "[red]0[/red]"
            table.add_row(
                definition.name, count, grouped, ", ".join(definition.match[:4])
            )
    console.print(table)


@app.command()
def verify(
    script: str = typer.Argument(..., help="Path to the finished script."),
    series: str = typer.Option(..., "--series"),
) -> None:
    """Check a script's chapter and episode tags against the crawled wiki.

    The engine offers locators; the writer picks which one goes on a line, and a
    writer with ten thousand words of context in front of it is exactly the kind
    of thing that produces a confident wrong number. Checked against the raw
    crawl, not the index, so an indexing bug cannot make a bad tag look fine.
    """
    from scriptengine.eval.verify import verify_script

    path = Path(script)
    if not path.exists():
        console.print(f"[red]No such script: {script}[/red]")
        raise typer.Exit(code=1)

    paths = series_paths(series)
    report = verify_script(path.read_text(encoding="utf-8"), paths)

    console.print(
        f"[dim]{report['tags']} tags, {report['distinct']} distinct, "
        f"checked against {series}[/dim]\n"
    )
    for finding in report["findings"]:
        console.print(f"  [red]FAIL[/red]  {finding['tag']}")
        for issue in finding["issues"]:
            console.print(f"          [dim]{issue}[/dim]")

    if report["passed"]:
        console.print("[green]Every tag checks out against the raw wiki pages.[/green]")
    else:
        console.print(
            f"\n[red]{len(report['findings'])} tag(s) failed verification.[/red]"
        )
        raise typer.Exit(code=1)


@app.command()
def script_path(
    title: str = typer.Argument(..., help="The script's title line, without the ** **."),
    create: bool = typer.Option(
        False, "--create", help="Create the folder as well as printing the path."
    ),
) -> None:
    """Where a finished script should be saved.

    Finished scripts live in the production tree, one numbered folder per video,
    beside that video's audio, images and storyboard. Asking rather than guessing
    keeps a rewrite from landing in a second folder for the same script.
    """
    destination = script_destination(title)
    if create:
        destination.parent.mkdir(parents=True, exist_ok=True)
    console.print(str(destination))


@app.command()
def export(
    series: str = typer.Option(..., "--series"),
    min_confidence: float = typer.Option(
        0.4, "--min-confidence", help="Drop edges below this confidence. 0.95 = infobox only."
    ),
    out: str = typer.Option(
        "", "--out", help="Vault directory; defaults to series/<name>/obsidian/."
    ),
    no_documents: bool = typer.Option(
        False, "--no-documents", help="Write node files only, skip readable pages."
    ),
) -> None:
    """Export the series' graph to an Obsidian vault."""
    from scriptengine.export import export_obsidian

    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    report = export_obsidian(
        paths,
        out_dir=out or None,
        min_confidence=min_confidence,
        include_documents=not no_documents,
    )
    console.print(
        f"[green]Wrote {report['nodes']:,} node files[/green] "
        f"({report['stubs']:,} unresolved stubs), "
        f"{report['documents']:,} document files, "
        f"{report['edges']:,} edges at >= {min_confidence:g} confidence"
    )
    console.print(f"Vault: {report['vault']}")
    console.print("Open it in Obsidian: Open folder as vault.")


@app.command()
def query(
    question: str = typer.Argument(...),
    series: str = typer.Option(..., "--series"),
    top_k: int = typer.Option(0, "--top-k", help="Passages to return."),
    no_rerank: bool = typer.Option(False, "--no-rerank", help="Skip the cross-encoder."),
    show_facts: bool = typer.Option(True, "--facts/--no-facts"),
    mode: str = typer.Option(
        "qa",
        "--mode",
        help="qa | narrative | roster | auto — the shape of the answer, as on /context.",
    ),
) -> None:
    """Retrieve context for a question."""
    import logging

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    # A script topic is answered in whichever shape it needs, and checking that
    # from the CLI has to mean the same thing it means over HTTP.
    if mode != "qa":
        _show_bundle(paths, question, mode, top_k)
        return

    from scriptengine.retrieve.hybrid import HybridRetriever

    with HybridRetriever(paths) as retriever:
        result = retriever.search(
            question, top_k=top_k or None, rerank=not no_rerank
        )
        retriever.release_models()

    if result.entities:
        console.print(f"[dim]Entities:[/dim] {', '.join(result.entities[:6])}")
    if result.related:
        console.print(f"[dim]Related:[/dim]  {', '.join(result.related[:8])}")

    if show_facts and result.facts:
        facts = Table(title="Facts")
        facts.add_column("entity")
        facts.add_column("field")
        facts.add_column("value")
        for fact in result.facts[:12]:
            facts.add_row(fact["entity"], fact["label"], fact["value"][:60])
        console.print(facts)

    if not result.passages:
        console.print("\n[yellow]Nothing retrieved.[/yellow]")
        return

    console.print()
    for rank, passage in enumerate(result.passages, start=1):
        console.print(
            f"[bold]{rank}. {passage.doc_title}[/bold] "
            f"[dim]— {passage.breadcrumb} "
            f"(score {passage.score:.3f}, via {'+'.join(passage.sources)})[/dim]"
        )
        console.print(f"   {passage.text[:400]}\n")


def _show_bundle(paths, question: str, mode: str, top_k: int) -> None:
    """Print a narrative or roster bundle the way `/context` assembles it."""
    from scriptengine.api.context import build_context
    from scriptengine.retrieve.roster import looks_like_enumeration

    if mode == "auto":
        mode = "roster" if looks_like_enumeration(question) else "narrative"

    bundle = build_context(
        paths, question, mode=mode, token_budget=24000, top_k=top_k or None
    )
    if mode == "roster" and not bundle["members"]:
        console.print("[yellow]No such set on this wiki; falling back to narrative.[/yellow]")
        bundle = build_context(paths, question, mode="narrative", token_budget=24000)

    console.print(f"[dim]mode:[/dim] {bundle['mode']}   [dim]subject:[/dim] {bundle['subject']}")
    if bundle.get("basis"):
        console.print(f"[dim]set:[/dim] {bundle['basis']}")
    console.print(f"[dim]tokens:[/dim] {bundle['tokens_used']}\n")

    if bundle.get("members"):
        table = Table(title=f"Members ({len(bundle['members'])})")
        table.add_column("group")
        table.add_column("member")
        table.add_column("debut")
        table.add_column("sourced")
        for member in bundle["members"]:
            table.add_row(
                member.get("group", ""), member["name"],
                member.get("debut", ""), member.get("source_span", ""),
            )
        console.print(table)
        return

    if not bundle["beats"]:
        console.print("[yellow]Nothing retrieved.[/yellow]")
        return

    for beat in bundle["beats"]:
        console.print(
            f"[bold]{beat['title']}[/bold] [dim]— {beat['doc_title']}"
            f"{'  sourced: ' + beat['source_span'] if beat.get('source_span') else ''}[/dim]"
        )
        console.print(f"   {beat['text'][:300]}\n")


@app.command()
def timeline(
    subject: str = typer.Argument(..., help="An arc, event or battle."),
    series: str = typer.Option(..., "--series"),
    max_beats: int = typer.Option(20, "--max-beats"),
) -> None:
    """Retrieve an event as ordered beats, for writing a script."""
    import logging

    from scriptengine.retrieve.narrative import NarrativeRetriever

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    with NarrativeRetriever(paths) as retriever:
        narrative = retriever.timeline(subject, max_beats=max_beats)

    if not narrative.beats:
        console.print(f"[yellow]No narrative found for {subject!r}.[/yellow]")
        raise typer.Exit(code=1)

    console.print(f"[bold]{narrative.subject}[/bold] — {len(narrative.beats)} beats")
    if narrative.participants:
        console.print(f"[dim]Participants:[/dim] {', '.join(narrative.participants[:12])}")
    console.print()

    for beat in narrative.beats:
        heading = f"[bold]{beat.order}. {beat.title}[/bold]"
        if beat.time:
            heading += f" [cyan]({beat.time})[/cyan]"
        console.print(heading)
        console.print(f"   [dim]{beat.breadcrumb}[/dim]")
        console.print(f"   {beat.text[:280]}\n")


@app.command("eval")
def run_eval(
    series: str = typer.Option(..., "--series"),
    top_k: int = typer.Option(8, "--top-k"),
    verbose: bool = typer.Option(False, "--verbose", help="Show every question."),
) -> None:
    """Score retrieval against the gold question set."""
    import logging

    from scriptengine.eval.harness import evaluate, write_report

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    try:
        report = evaluate(paths, top_k=top_k)
    except FileNotFoundError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Retrieval eval — {series}")
    table.add_column("kind")
    table.add_column("passed", justify="right")
    table.add_column("score", justify="right")
    for kind, scores in report["by_kind"].items():
        colour = "green" if scores["score"] == 1.0 else "yellow" if scores["score"] >= 0.6 else "red"
        table.add_row(
            kind,
            f"{scores['passed']}/{scores['total']}",
            f"[{colour}]{scores['score']:.0%}[/{colour}]",
        )
    console.print(table)

    failures = [outcome for outcome in report["results"] if not outcome["passed"]]
    if verbose or failures:
        console.print()
        for outcome in (report["results"] if verbose else failures):
            mark = "[green]PASS[/green]" if outcome["passed"] else "[red]FAIL[/red]"
            console.print(f"  {mark}  [{outcome['id']}] {outcome['question']}")
            if not outcome["passed"]:
                detail = {
                    key: value for key, value in outcome.items()
                    if key not in {"id", "kind", "question", "passed", "seconds"}
                }
                console.print(f"        [dim]{detail}[/dim]")

    console.print(
        f"\n[bold]{report['passed']}/{report['questions']}[/bold] "
        f"({report['score']:.0%})   report: {write_report(paths, report)}"
    )
    if report["score"] < 1.0:
        raise typer.Exit(code=1)


@app.command("list")
def list_series() -> None:
    """Show every series present on disk and what has been built for it."""
    settings = get_settings()
    root = settings.series_root

    table = Table(title="Series")
    for column in ("name", "pages", "facts.db", "vectors"):
        table.add_column(column)

    found = False
    if root.exists():
        for entry in sorted(p for p in root.iterdir() if p.is_dir()):
            found = True
            paths = series_paths(entry.name, settings)
            pages = (
                len(list(paths.wikitext.glob("*.json"))) if paths.wikitext.exists() else 0
            )
            table.add_row(
                entry.name,
                str(pages),
                "yes" if paths.facts_db.exists() else "no",
                "yes" if paths.vectors.exists() else "no",
            )

    if not found:
        console.print("[dim]No series yet. Start with `crawl`.[/dim]")
        return
    console.print(table)


@app.command()
def config() -> None:
    """Print effective settings, after env and `.env` overrides."""
    settings = get_settings()
    dumped = settings.model_dump()
    dumped["device (resolved)"] = settings.resolved_device()
    console.print_json(json.dumps(dumped, default=str))


def main() -> None:
    app()


if __name__ == "__main__":
    sys.exit(app())
