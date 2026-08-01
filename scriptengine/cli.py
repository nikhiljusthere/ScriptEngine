"""ScriptEngine command line.

    python -m scriptengine.cli --help

Commands are added as their phase lands. Anything not yet implemented exits
non-zero with a message naming the phase, rather than failing obscurely.
"""

from __future__ import annotations

import json
import sys

import typer
from rich.console import Console
from rich.table import Table

from scriptengine.config import get_settings, series_paths

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
    console.print(summary)

    types = Table(title="Discovered page types")
    types.add_column("type")
    types.add_column("pages", justify="right")
    for name, count in report["types"].items():
        types.add_row(name, str(count))
    console.print(types)

    console.print()
    for check in report["checks"]:
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
def query(
    question: str = typer.Argument(...),
    series: str = typer.Option(..., "--series"),
) -> None:
    """Retrieve context for a question."""
    _not_yet("Phase 3", "Querying")


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
