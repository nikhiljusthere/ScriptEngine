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
        f"({manifest['pages_skipped']} skipped, {manifest['pages_failed']} failed), "
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

    summary = Table(title=f"Extraction audit: {series} ({report['sampled']} pages)")
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
def prune(
    series: str = typer.Option(..., "--series"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="List the pages that would be removed, write nothing."
    ),
) -> None:
    """Drop a series' low-quality pages, per `prune_types` in its overrides.yaml.

    Every wiki is crawled whole and filtered later, so a video game or
    soundtrack page the engine will never cite still costs a slot in the
    corpus and in the vector store. The blocklist lives in
    `series/<name>/overrides.yaml`, the only place a series-specific decision
    is allowed to live, and this command deletes the stored wikitext those
    pages produced. A page is matched by its type family, so pruning
    `song_box` also removes a subpage typed `song_box_other_versions`. Bring
    what was removed back with `crawl --refresh`.
    """
    from collections import Counter

    from scriptengine.ingest.crawler import load_extracted, sanitise_filename

    paths = series_paths(series)
    overrides = _load_overrides(paths)
    blocklist = {
        str(entry).strip().lower() for entry in (overrides.get("prune_types") or [])
    }
    if not blocklist:
        console.print(f"[yellow]{series} declares no prune_types; nothing to do.[/yellow]")
        return

    # Classify the way `audit` and `index` do. The type stored on disk at
    # crawl time can be stale: a crawl whose template enumeration was
    # rate-limited typed everything "unknown", and the types only appear once
    # re-extraction runs. Pruning on the stored field would remove nothing
    # from that corpus while the engine itself knows what the pages are.
    pages, _ = load_extracted(paths, overrides)

    matched: list[tuple[Path, str]] = []
    seen: set[Path] = set()
    for page in pages:
        kind = (page.page_type or "").lower()
        if kind in blocklist or any(kind.startswith(f"{entry}_") for entry in blocklist):
            destination = paths.wikitext / f"{sanitise_filename(page.title)}.json"
            if destination.exists() and destination not in seen:
                seen.add(destination)
                matched.append((destination, kind))

    by_type = Counter(kind for _, kind in matched)
    total = len(list(paths.wikitext.glob("*.json")))
    kept = total - len(matched)

    table = Table(
        title=f"Prune: {series} "
        f"({'dry run, ' if dry_run else ''}{len(matched)} of {total} pages)"
    )
    table.add_column("type")
    table.add_column("pages", justify="right")
    for kind, count in by_type.most_common():
        table.add_row(kind, str(count))
    console.print(table)

    if dry_run:
        console.print(
            f"[dim]{len(matched)} pages would be removed, {kept} kept. "
            "Re-run without --dry-run to delete.[/dim]"
        )
        return

    for path, _ in matched:
        path.unlink()
    console.print(
        f"[green]Removed {len(matched)} pages, kept {kept}.[/green] "
        f"Next: `audit --series {series}`, then `index --series {series}`."
    )


@app.command("resolve-templates")
def resolve_templates(
    series: str = typer.Option(..., "--series"),
    refresh: bool = typer.Option(
        False, "--refresh", help="Re-fetch cached template expansions."
    ),
) -> None:
    """Splice declared list templates into stored wikitext, pre-index.

    The crawler skips the Template: namespace, so a page whose "list" section
    is a bare transclusion stores no links and the wiki's canonical curated
    list is invisible to the index. The allowlist lives in
    `series/<name>/overrides.yaml` under `template_lists:`; this command
    fetches each declared template's expansion via the MediaWiki
    `expandtemplates` action and splices it into the page's stored wikitext,
    so the next `index` parses the real list.
    """
    import asyncio
    import logging

    from scriptengine.ingest.templates import resolve_series

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    paths = series_paths(series)
    overrides = _load_overrides(paths)
    report = asyncio.run(resolve_series(paths, overrides, refresh=refresh))

    if report["status"] != "ok":
        if report["status"] == "no_template_lists":
            console.print(
                f"[yellow]{series} declares no template_lists; nothing to resolve.[/yellow]"
            )
        else:
            console.print(
                f"[yellow]Nothing resolved ({report['status']}). "
                "Is the corpus crawled?[/yellow]"
            )
        return

    console.print(
        f"[green]Resolved {report['templates_declared']} declared templates[/green] "
        f"({report['templates_fetched']} fetched), spliced into "
        f"{report['pages_updated']} of {report['pages_with_unresolved']} pages "
        f"carrying a transclusion."
    )
    console.print(f"\nNext: [bold]index --series {series}[/bold]")


_COUNT_WORDS = {
    "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
    "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
}


def _stated_count(name: str) -> int | None:
    """The size a set's own name claims, if it claims one.

    `Seven Warlords of the Sea`, `Gotei 13`, `Zodiac Twelve`. A name that counts
    itself is a free assertion to check the membership against, and the check
    is worth having even though most of what it finds turns out to be a naming
    convention rather than a defect.
    """
    import re as _re

    digits = _re.search(r"\b(\d{1,3})\b", name or "")
    if digits:
        return int(digits.group(1))
    for word, value in _COUNT_WORDS.items():
        if _re.search(rf"\b{word}\b", name or "", _re.IGNORECASE):
            return value
    return None


@app.command()
def abilities(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Stop after this many characters."),
    refresh: bool = typer.Option(
        False, "--refresh", help="Re-extract even where a current answer is stored."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show whose prose would be read, call no model."
    ),
    workers: int = typer.Option(
        1, "--workers", help="Extract this many characters at once (opencode only)."
    ),
    bank_only: bool = typer.Option(
        False, "--bank-only",
        help="Only characters this series' question bank asks about."
    ),
) -> None:
    """Extract the abilities this wiki writes only as prose.

    Half of what a character-scoped question asks for is not an entity: Killua's
    Godspeed, Saitama's Serious Punch and Genos' Incinerate have no page, no
    category and no `users` field. They are named in a paragraph under
    `Abilities & Powers`, and the chunk text carries no markup, so nothing
    structural can pick them out.

    A local model reads those sections once and the answer is stored, so
    retrieval keeps reading a table rather than reasoning. Only the series that
    declare `ability_sections:` are touched; Dragon Ball records ownership as
    edges and needs none of this.

    Cached on the page's revision, so running it twice costs nothing.
    """
    import logging

    from scriptengine.ingest.abilities import extract_series, needs_extracting
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    only: set[str] | None = None
    if bank_only:
        from scriptengine.eval import questions as _bank

        subjects = {q.subject.strip() for q in _bank.load_bank(series).questions
                    if q.subject and q.subject.strip()}
        if not subjects:
            console.print(f"[red]No question in {series!r} names a subject.[/red]")
            raise typer.Exit(code=1)
        only = subjects
        console.print(f"[dim]--bank-only: {len(only)} subjects in this bank[/dim]")

    if dry_run:
        with FactStore(paths.facts_db) as store:
            names = needs_extracting(store, _load_overrides(paths))
        if only:
            wanted = {n.lower() for n in only}
            names = [n for n in names if n.strip().lower() in wanted]
        console.print(f"[dim]{len(names)} characters would be read:[/dim]")
        for name in names[:40]:
            console.print(f"  {name}")
        if len(names) > 40:
            console.print(f"  [dim]… {len(names) - 40} more[/dim]")
        return

    def show(character: str, count: int) -> None:
        console.print(f"  [dim]{count:3} found[/dim]  {character}")

    try:
        report = extract_series(
            paths, limit=limit or None, refresh=refresh, progress=show,
            workers=max(1, workers), only=only,
        )
    except LLMUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Abilities extracted: {series}")
    table.add_column("outcome")
    table.add_column("count", justify="right")
    for key in ("considered", "extracted", "cached", "failed", "abilities"):
        table.add_row(key, str(report[key]))
    console.print(table)


@app.command("narrative-abilities")
def narrative_abilities(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Stop after this many passages."),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be read, call no model."
    ),
    workers: int = typer.Option(
        1, "--workers", help="Read this many passages at once."
    ),
) -> None:
    """Read the abilities a wiki only shows happening, in a chapter summary.

    `abilities` reads a character's own ability sections, which is where a wiki
    lists what someone has. It cannot see what the wiki records only as
    something that happened: Makima's contract with the Prime Minister of Japan
    is on `Chapter 216`, Power's blood weapons on `Chapter 90`, and neither is on
    either character's page in any form. Both were scored as items the corpus
    did not contain, and the corpus contained them the whole time.

    Pages are read once each and the model attributes the owner, because reading
    per character would re-read the same chapter for everyone it names: Denji
    alone appears in 664 chapter chunks of Chainsaw Man.

    Only series declaring `ability_narrative_types:` are touched, and rows are
    added without replacing what a character's own page already gave.
    """
    import logging

    from scriptengine.ingest import narrative_abilities as narrative
    from scriptengine.ingest.abilities import _windows
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        with FactStore(paths.facts_db) as store:
            found = narrative.passages(store, _load_overrides(paths))
        windows = sum(len(_windows(t)) for _p, _s, t in found)
        console.print(
            f"[dim]{len(found)} passages, {windows} windows would be read[/dim]")
        for page, section, _text in found[:20]:
            console.print(f"  {page}  [dim]{section}[/dim]")
        return

    try:
        report = narrative.extract_series(paths, limit=limit, workers=max(1, workers))
    except LLMUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Narrative abilities: {series}")
    table.add_column("outcome")
    table.add_column("count", justify="right")
    for key in ("passages", "windows", "added", "failed"):
        table.add_row(key, str(report[key]))
    console.print(table)


@app.command()
def relations(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Stop after this many characters."),
    refresh: bool = typer.Option(
        False, "--refresh", help="Re-extract even where a current answer is stored."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show whose prose would be read, call no model."
    ),
    workers: int = typer.Option(
        1, "--workers", help="Extract this many characters at once."
    ),
) -> None:
    """Extract the relationships this wiki writes only as prose.

    The infobox gives family and faction: `relatives`, `affiliation`. It does
    not give what a script is built from: that Gojo and Geto were the strongest
    duo until Geto defected. That is a sentence under `Relationships`, reachable
    by no category and no edge.

    Every row keeps the clause it came from, checked against the passage word
    for word, and the other end must be somebody this wiki actually has.
    """
    import logging

    from scriptengine.ingest.relations import extract_series as extract_relations
    from scriptengine.ingest.relations import needs_relations
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        with FactStore(paths.facts_db) as store:
            names = needs_relations(store, _load_overrides(paths))
        console.print(f"[dim]{len(names)} characters would be read:[/dim]")
        for name in names[:40]:
            console.print(f"  {name}")
        if len(names) > 40:
            console.print(f"  [dim]… {len(names) - 40} more[/dim]")
        return

    def show(character: str, count: int) -> None:
        console.print(f"  [dim]{count:3} found[/dim]  {character}")

    try:
        report = extract_relations(
            paths, limit=limit or None, refresh=refresh, progress=show,
            workers=max(1, workers),
        )
    except LLMUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Relations extracted: {series}")
    table.add_column("outcome")
    table.add_column("count", justify="right")
    for key in ("considered", "extracted", "cached", "failed", "relations"):
        table.add_row(key, str(report[key]))
    console.print(table)


@app.command()
def events(
    series: str = typer.Option(..., "--series"),
    arc: str = typer.Option("Shibuya Incident", "--arc"),
    seed_phase1: bool = typer.Option(
        False,
        "--seed-phase1",
        help="Gate and store the hand-written Phase-1 batch for this arc.",
    ),
) -> None:
    """Placed, time-ranked events an arc's article states as events.

    A relation says how two characters stand to each other; an event says what
    happened and where on the arc's time axis, which is what a script's beat
    order needs. Rows carry the clause they came from verbatim and both ends
    must resolve to nodes this wiki actually has. `--seed-phase1` stores the
    hand-written door-test batch; without it the command reports what is
    stored and under which prompt and revision.
    """
    from scriptengine.ingest.events import (
        PHASE1_ARC,
        PHASE1_ROWS,
        seed_phase1_rows,
        validate_phase1_rows,
    )
    from scriptengine.stores.facts import FactStore

    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    with FactStore(paths.facts_db) as store:
        if seed_phase1:
            if arc != PHASE1_ARC:
                console.print(
                    f"[red]The Phase-1 batch is hand-written for {PHASE1_ARC!r};"
                    f" --arc {arc!r} has no batch to seed.[/red]"
                )
                raise typer.Exit(code=1)
            stored, findings = seed_phase1_rows(store)
            if findings:
                console.print(f"[red]Phase-1 batch did not pass its gates:[/red]")
                for finding in findings:
                    console.print(f"  [red]{finding}[/red]")
                raise typer.Exit(code=1)
            console.print(
                f"[green]Stored {stored} of {len(PHASE1_ROWS)} Phase-1 events for"
                f" {arc!r} (model hand-written).[/green]"
            )
            return

        state = store.event_state(arc)
        if state is None:
            findings = validate_phase1_rows(store)
            console.print(f"No events stored for {arc!r} in {series}.")
            if findings:
                console.print(f"[yellow]Phase-1 batch fails its gates:[/yellow]")
                for finding in findings:
                    console.print(f"  [yellow]{finding}[/yellow]")
            else:
                console.print(
                    f"[dim]The Phase-1 batch ({len(PHASE1_ROWS)} rows) passes its"
                    " gates. Store it with --seed-phase1.[/dim]"
                )
            return

        table = Table(title=f"Events stored: {arc} ({series})")
        table.add_column("model")
        table.add_column("prompt")
        table.add_column("revid")
        table.add_row(
            state["model"], state["prompt_version"], str(state["revid"] if state["revid"] is not None else "-")
        )
        console.print(table)

        rows = store.events_of(arc)
        placed = [row for row in rows if row["temporal"]]
        console.print(
            f"[dim]{len(rows)} rows, {len(placed)} on the time axis"
            f" ({len(rows) - len(placed)} standing state).[/dim]"
        )
        for row in rows:
            when = (
                f"t={row['time_rank']:g}" if row["temporal"] else "state"
            )
            console.print(
                f"  [dim]{when:9}[/dim] {row['subject_name']} [bold]{row['verb']}[/bold]"
                f" {row['object_name']}"
            )


@app.command()
def events_extract(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Stop after this many pages."),
    refresh: bool = typer.Option(
        False, "--refresh", help="Re-extract even where a current answer is stored."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show which pages and sections would be read, call no model."
    ),
    workers: int = typer.Option(
        1, "--workers", help="Extract this many pages at once."
    ),
) -> None:
    """Extract the events this wiki's arc, event and battle pages state.

    A relation says how two characters stand to each other; an event says what
    happened and where on the arc's time axis. Every row keeps the clause it
    came from, checked against the passage word for word, and both ends must
    be entities this wiki actually has. Where on the axis an event sits is
    looked up from its section -- a heading's clock time, or article order --
    never inferred by the model.
    """
    import logging

    from scriptengine.ingest.events import (
        PROMPT_VERSION,
        extract_events_series,
        extractable_sections,
        placement_pages,
    )
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        with FactStore(paths.facts_db) as store:
            store.ensure_events()
            pages = placement_pages(store)
            if limit:
                pages = pages[:limit]
            console.print(
                f"[dim]{len(pages)} pages would be read (prompt {PROMPT_VERSION}):[/dim]"
            )
            for page in pages[:40]:
                sections = extractable_sections(store, page)
                console.print(f"  {page}  [dim]({len(sections)} sections)[/dim]")
                for section in sections:
                    console.print(f"    [dim]{section['title']}[/dim]")
            if len(pages) > 40:
                console.print(f"  [dim]… {len(pages) - 40} more[/dim]")
        return

    def show(page: str, count: int) -> None:
        console.print(f"  [dim]{count:3} events[/dim]  {page}")

    try:
        report = extract_events_series(
            paths, limit=limit or None, refresh=refresh, progress=show,
            workers=max(1, workers),
        )
    except LLMUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Events extracted: {series}")
    table.add_column("outcome")
    table.add_column("count", justify="right")
    for key in ("considered", "extracted", "cached", "failed", "events"):
        table.add_row(key, str(report[key]))
    console.print(table)


@app.command()
def link(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Read only the first N pages."),
) -> None:
    """Write the ownership a wiki states in prose rather than in a field.

    `owned_by` walks `user`/`owner` infobox edges. Bleach puts no such field on
    a technique page and says it in the first line instead -- "is a technique of
    Rukia Kuchiki's Zanpakutō, Sode no Shirayuki". 196 of its 488 technique
    pages name their owner that way and belonged to nobody.

    Rule-based, not a model: the sentence is formulaic. Run after `index`, which
    rebuilds the graph.
    """
    import logging

    from scriptengine.ingest.ownership import derive

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    report = derive(paths, limit)
    table = Table(title=f"Stated ownership: {series}")
    table.add_column("outcome")
    table.add_column("count", justify="right")
    for key in ("considered", "stated", "written", "unknown_owner"):
        table.add_row(key, str(report[key]))
    console.print(table)


@app.command()
def classify(
    series: str = typer.Option(..., "--series"),
    limit: int = typer.Option(0, "--limit", help="Stop after this many pages."),
    refresh: bool = typer.Option(
        False, "--refresh", help="Reclassify even where a current answer is stored."
    ),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be classified, call no model."
    ),
) -> None:
    """Classify the ability pages the wiki's own fields cannot settle.

    `Class = Transformation` and a `Saiyans` category describe Spirit Bomb Super
    Saiyan and Great Ape identically, and only one is a form a Saiyan body
    reaches. A local model decides that once and the answer is stored, so
    retrieval keeps reading a table rather than reasoning.

    Cached on the page's revision, so running it twice costs nothing and a
    re-crawl only pays for what changed.
    """
    import logging

    from scriptengine.ingest.classify import classify_series, needs_classifying
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    if dry_run:
        with FactStore(paths.facts_db) as store:
            titles = needs_classifying(store, _load_overrides(paths))
        console.print(f"[dim]{len(titles)} pages would be classified:[/dim]")
        for title in titles[:40]:
            console.print(f"  {title}")
        if len(titles) > 40:
            console.print(f"  [dim]… {len(titles) - 40} more[/dim]")
        return

    def show(title: str, result) -> None:
        console.print(f"  [dim]{result.semantic_type:16}[/dim] {title}")

    try:
        report = classify_series(
            paths, limit=limit or None, refresh=refresh, progress=show
        )
    except LLMUnavailable as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    table = Table(title=f"Classified: {series}")
    table.add_column("outcome")
    table.add_column("pages", justify="right")
    for key in ("considered", "classified", "cached", "failed"):
        table.add_row(key, str(report[key]))
    console.print(table)
    if report["types"]:
        console.print(
            "[dim]types:[/dim] "
            + ", ".join(f"{k} {v}" for k, v in sorted(report["types"].items()))
        )


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
    from rich.progress import TaskID

    from scriptengine.index.build import build_index, write_status

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s | %(levelname)-7s | %(message)s",
        datefmt="%H:%M:%S",
    )

    paths = series_paths(series)

    with RichProgress(transient=True) as bar:
        tasks: dict[str, TaskID] = {}

        def on_progress(stage: str, done: int, total: int) -> None:
            if stage not in tasks:
                tasks[stage] = bar.add_task(stage, total=total)
            bar.update(tasks[stage], completed=done, total=total)

        report = build_index(paths, embed=not no_embed, progress=on_progress)

    if "error" in report:
        console.print(f"[red]{report['error']}[/red]")
        raise typer.Exit(code=1)

    stats = report["stats"]
    table = Table(title=f"Index built: {series}")
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
def catalogue(
    output: str = typer.Option(
        "docs/CATALOGUE.md", "--output", help="Where to write the catalogue."
    ),
    show: bool = typer.Option(False, "--show", help="Print it instead of writing."),
) -> None:
    """Write what is in the engine to a document, from the engine.

    Every series brings its own wiki, citation grammar, roster registry and
    sourcing rate, and nothing said so in one place. Generated rather than
    hand-written so it cannot quietly go stale.
    """
    from scriptengine.eval.catalogue import collect, render

    records = collect()
    if not records:
        console.print("[yellow]No indexed series found.[/yellow]")
        raise typer.Exit(code=1)

    text = render(records)
    if show:
        console.print(text)
        return

    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(text, encoding="utf-8")

    table = Table(title="Catalogue")
    table.add_column("series")
    table.add_column("pages", justify="right")
    table.add_column("prose → chapter", justify="right")
    table.add_column("rosters", justify="right")
    for record in sorted(records, key=lambda r: -r["documents"]):
        chapter = record.get("with_chapter")
        table.add_row(
            record["series"], f"{record['documents']:,}",
            "n/a" if chapter is None else f"{chapter * 100:.0f}%",
            str(len(record["rosters"])),
        )
    console.print(table)
    console.print(f"\nWrote {destination}")


@app.command()
def cite(
    script: str = typer.Argument(..., help="Path to a finished script."),
    series: str = typer.Option(..., "--series"),
    top_k: int = typer.Option(6, "--top-k", help="Passages weighed per block."),
    agreement: int = typer.Option(
        2, "--agreement", help="Hits that must name a locator before it is used."
    ),
    min_score: float = typer.Option(
        None, "--min-score", help="Ignore passages the reranker scored below this."
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Report without writing."),
) -> None:
    """Source a script that already exists, without changing a word of it.

    Each block of prose is used as a query against the index; the passages that
    come back carry the wiki's own references, and the locators on those become
    the block's tag. A block whose hits disagree is left exactly as it was,
    because an untagged line is honest where a guessed chapter is not.

    The original is never opened for writing. The result goes to
    `<name> (cited).md` beside it, so a bad run cannot damage a script.
    """
    from scriptengine.eval.verify import verify_script
    from scriptengine.retrieve.annotate import annotate, unannotate

    path = Path(script)
    if not path.exists():
        console.print(f"[red]No such script: {script}[/red]")
        raise typer.Exit(code=1)

    paths = series_paths(series)
    original = path.read_text(encoding="utf-8")
    result = annotate(
        original, paths, top_k=top_k, min_agreement=agreement, min_score=min_score
    )

    # The guarantee, checked on every run rather than trusted: strip the tags
    # back off and the input must be there, byte for byte.
    if unannotate(result.text) != original:
        console.print(
            "[red]Refusing to write: the cited text does not reduce back to the "
            "original. This is a bug in annotate, not in your script.[/red]"
        )
        raise typer.Exit(code=1)

    summary = result.summary()
    console.print(
        f"[dim]{summary['prose_blocks']} blocks of prose, "
        f"{summary['tagged']} tagged, {summary['untagged']} left alone[/dim]"
    )

    report = verify_script(result.text, paths)
    if report["findings"]:
        console.print(f"[red]{len(report['findings'])} tag(s) failed verification:[/red]")
        for finding in report["findings"][:10]:
            console.print(f"   {finding['tag']}: {finding['issues'][0]}")
    else:
        console.print(
            f"[green]All {report['distinct']} distinct tags check out against "
            f"the raw wiki pages.[/green]"
        )

    if dry_run:
        console.print("[dim]--dry-run: nothing written.[/dim]")
        return

    destination = path.with_name(f"{path.stem} (cited){path.suffix}")
    destination.write_text(result.text, encoding="utf-8")
    console.print(f"\nWrote {destination}")


@app.command()
def rosters(
    series: str = typer.Option(..., "--series"),
    audit: bool = typer.Option(
        False,
        "--audit",
        help="List declarations that can swallow a narrower topic.",
    ),
) -> None:
    """The enumeration sets this series declares.

    Without this the registry is invisible to whoever writes the next script,
    and they would go back to guessing which topics the engine answers well.
    """
    from scriptengine.config import load_overrides
    from scriptengine.retrieve.roster import _declared_members, load_rosters
    from scriptengine.stores.facts import FactStore

    paths = series_paths(series)
    declared = load_rosters(load_overrides(paths))
    if not declared:
        console.print(f"[yellow]{series} declares no rosters.[/yellow]")
        return

    if audit:
        # A one-word phrase claims the whole topic, so anything narrower that
        # contains the word answers with the parent set: `Deities` declared
        # `kai`, and "Every Kai" came back as 169 deities with nothing left over
        # for the validator to notice. The bigger the set, the worse the
        # swallow, so they are listed largest first.
        table = Table(title=f"Swallow surface: {series}")
        table.add_column("word")
        table.add_column("claims", overflow="fold")
        table.add_column("members", justify="right")
        rows: list[tuple[str, str, int]] = []
        with FactStore(paths.facts_db) as store:
            for definition in declared:
                size = (
                    len(definition.groups)
                    if definition.groups
                    else len(_declared_members(store, definition))
                )
                for phrase in definition.match:
                    if " " not in phrase:
                        rows.append((phrase, definition.name, size))
        for phrase, name, size in sorted(rows, key=lambda row: -row[2]):
            style = "yellow" if size >= 40 else ""
            table.add_row(f"[{style}]{phrase}[/{style}]" if style else phrase, name, str(size))
        console.print(table)

        # A set whose *name* states a size, against what it actually holds.
        # Reported, never corrected: of the seven found across the corpus, only
        # some are defects. `Gotei 13` holds 127 because the 13 counts divisions
        # and the category is the whole organisation; `Seven Warlords` holds 12
        # because twelve people held seven seats over time. Both are correct
        # data and a misleading name, and a tool that "fixed" them would be
        # wrong. Which is which is a judgement for a person.
        counted = Table(title=f"Sets whose name states a count: {series}")
        counted.add_column("set")
        counted.add_column("name says", justify="right")
        counted.add_column("holds", justify="right")
        counted.add_column("for review")
        found = 0
        with FactStore(paths.facts_db) as store:
            for definition in declared:
                stated = _stated_count(definition.name)
                if stated is None:
                    continue
                size = (
                    len(definition.groups)
                    if definition.groups
                    else len(_declared_members(store, definition))
                )
                if size == stated:
                    continue
                found += 1
                counted.add_row(
                    definition.name,
                    str(stated),
                    str(size),
                    "seats vs holders, a broader category, or duplicate pages",
                )
        if found:
            console.print(counted)
        return
        console.print(
            f"[dim]{sum(1 for r in rows if r[2] >= 40)} of {len(rows)} single-word "
            "phrases claim a set of 40+ members. Each is a topic that cannot be "
            "narrowed, because the phrase consumes the whole question.[/dim]"
        )
        return

    table = Table(title=f"Declared rosters: {series}")
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
def script_gen(
    subject: str = typer.Argument(..., help="The arc, character or set the script is about."),
    series: str = typer.Option("jjk", "--series"),
    words: int = typer.Option(6000, "--words", help="Target script length in words."),
    intro: bool = typer.Option(True, "--intro/--no-intro"),
    mode: str = typer.Option(
        "auto", "--mode", help="auto | narrative | roster | qa: the shape of the context."
    ),
    budget: int = typer.Option(
        0, "--budget", help="Context token budget; 0 = words * 8, clamped 6000-60000."
    ),
    max_attempts: int = typer.Option(3, "--max-attempts", help="Repair passes after the first draft."),
    title: str = typer.Option(
        None, "--title", help="Save under this title; default is the subject, so a regenerate reuses the video's folder."
    ),
    write: bool = typer.Option(True, "--write/--no-write"),
) -> None:
    """Write a script for a topic and verify its tags against the wiki.

    Fetches the context bundle, asks the writer model for the script, checks
    every chapter/episode tag against the raw crawl, and when a tag fails
    sends only the findings back for a repair pass. The script is expanded
    and trimmed until it lands within 500 words of the target. Saves under
    `scripts output/Video N - <Title>/Script/`.
    """
    from scriptengine.llm.client import LLMUnavailable
    from scriptengine.script.writer import generate_script

    try:
        result = generate_script(
            subject,
            series=series,
            words=words,
            intro=intro,
            mode=mode,
            token_budget=budget,
            max_attempts=max_attempts,
            write=write,
            title=title,
        )
    except ValueError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1)
    except LLMUnavailable as error:
        console.print(
            f"[red]The writer model could not answer:[/red] {error}\n"
            "[dim]Start LM Studio and load the writer model (default "
            "qwen/qwen3.8-27b), or set SCRIPTENGINE_WRITER_BACKEND=opencode.[/dim]"
        )
        raise typer.Exit(code=1)

    bundle = result["bundle"]
    report = result["report"]
    routed = bundle.get("routed")
    route_note = f" [dim](routed: {routed['mode']} - {routed.get('why', '')})[/dim]" if routed else ""
    console.print(
        f"[dim]mode:[/dim] {bundle.get('mode')}   [dim]subject:[/dim] "
        f"{bundle['subject']}{route_note}"
    )
    beats = len(bundle.get("beats") or [])
    members = len(bundle.get("members") or [])
    console.print(
        f"[dim]context: {bundle.get('tokens_used', 0)} tokens, "
        f"{beats} beats, {members} members, "
        f"{len(bundle.get('facts') or [])} facts[/dim]"
    )
    if result["attempts"] > 1:
        console.print(
            f"[yellow]{result['attempts'] - 1} repair pass(es) after the first draft.[/yellow]"
        )
    length_note = ""
    if result["target_words"]:
        length_note = (
            f"   [dim]words:[/dim] {result['words']}/{result['target_words']}"
            f" [dim]({result['length_passes']} length passes)[/dim]"
            f"{' [yellow](expanded)[/yellow]' if result['expanded'] else ''}"
            f"{' [yellow](trimmed)[/yellow]' if result['trimmed'] else ''}"
        )
    console.print(
        f"[dim]{report['tags']} tags, {report['distinct']} distinct, "
        f"checked against {series}[/dim]{length_note}\n"
    )
    for finding in report["findings"]:
        console.print(f"  [red]FAIL[/red]  {finding['tag']}")
        for issue in finding["issues"]:
            console.print(f"          [dim]{issue}[/dim]")

    if report["passed"]:
        console.print("[green]Every tag checks out against the raw wiki pages.[/green]")
        if result["path"]:
            console.print(f"[green]Saved:[/green] {result['path']}")
    else:
        console.print(
            f"\n[red]{len(report['findings'])} tag(s) failed verification. "
            "The script was still written; fix the tags or raise --max-attempts.[/red]"
        )
        if not write:
            raise typer.Exit(code=1)


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
        help="qa | narrative | roster | auto: the shape of the answer, as on /context.",
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
            f"[dim]- {passage.breadcrumb} "
            f"(score {passage.score:.3f}, via {'+'.join(passage.sources)})[/dim]"
        )
        console.print(f"   {passage.text[:400]}\n")


def _show_bundle(paths, question: str, mode: str, top_k: int) -> None:
    """Print a narrative or roster bundle the way `/context` assembles it."""
    from scriptengine.api.context import build_context
    from scriptengine.retrieve.router import route

    if mode == "auto":
        chosen = route(paths, question)
        mode = chosen.mode
        console.print(f"[dim]routed to[/dim] {mode} [dim]({chosen.why})[/dim]")

    bundle = build_context(
        paths, question, mode=mode, token_budget=24000, top_k=top_k or None
    )
    if mode == "roster" and not bundle["members"]:
        console.print("[yellow]No such set on this wiki; falling back to narrative.[/yellow]")
        bundle = build_context(paths, question, mode="narrative", token_budget=24000)

    console.print(f"[dim]mode:[/dim] {bundle['mode']}   [dim]subject:[/dim] {bundle['subject']}")
    if bundle.get("basis"):
        console.print(f"[dim]set:[/dim] {bundle['basis']}")
    if bundle.get("warning"):
        console.print(f"[yellow]{bundle['warning']}[/yellow]")
    rejected = bundle.get("rejected") or []
    if rejected:
        kept = len(bundle.get("members") or [])
        console.print(
            f"[dim]validated:[/dim] {kept} of {bundle.get('candidates', kept)} "
            f"({bundle.get('scope', 'canon')} scope)"
        )
        for entry in rejected[:5]:
            console.print(f"  [dim]-[/dim] {entry['name']}: [dim]{entry['reason']}[/dim]")
        if len(rejected) > 5:
            console.print(f"  [dim]… {len(rejected) - 5} more[/dim]")
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
            f"[bold]{beat['title']}[/bold] [dim]- {beat['doc_title']}"
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

    console.print(f"[bold]{narrative.subject}[/bold]: {len(narrative.beats)} beats")
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


@app.command()
def chronicle(
    subject: str = typer.Argument(..., help="A character, or an arc with --cast."),
    series: str = typer.Option(..., "--series"),
    cast_of: bool = typer.Option(
        False, "--cast", help="Treat the subject as an arc and list who is in it."
    ),
    full: bool = typer.Option(False, "--full", help="Print the prose, not a summary."),
    arc: str = typer.Option(
        "", "--arc", help="One arc, cut into cited beats: a section to write from."
    ),
) -> None:
    """A character's story arc by arc, in the shape a life script is written.

    `The Entire Life of Garou` runs one section per arc, each headed with the
    chapters and episodes it covers. This is that spine: the arcs the wiki files
    this character's history under, in the order its own `previous`/`next` chain
    puts them, with the heading already rendered.

    Reads the store and nothing else: no model, so the chronology is the same
    every time it is asked.
    """
    import logging

    from scriptengine.retrieve import chronology
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)
    paths = series_paths(series)
    if not paths.facts_db.exists():
        console.print(f"[red]Series {series!r} is not indexed. Run `index` first.[/red]")
        raise typer.Exit(code=1)

    with FactStore(paths.facts_db) as store:
        if cast_of:
            who = chronology.cast(store, subject, _load_overrides(paths))
            if not who:
                console.print(f"[yellow]No character's history is filed under "
                              f"{subject!r}.[/yellow]")
                raise typer.Exit(code=1)
            console.print(f"[bold]{chronology.heading(store, subject)}[/bold]")
            console.print(f"[dim]{len(who)} characters, most-written first[/dim]\n")
            for name in who:
                console.print(f"  {name}")
            return

        if arc:
            section = chronology.scaffold(store, subject, arc, _load_overrides(paths))
            if section is None:
                console.print(f"[yellow]{subject!r} has no history filed under "
                              f"{arc!r}.[/yellow]")
                raise typer.Exit(code=1)
            console.print(f"[bold]{section.heading}[/bold]")
            console.print(f"[dim]{len(section.beats)} beats, "
                          f"{section.words} words[/dim]\n")
            for order, beat in enumerate(section.beats, 1):
                console.print(f"[bold]{order}.[/bold] [cyan]{beat.locator or 'n/a'}[/cyan]")
                console.print(f"   {beat.text}\n")
            if section.abilities:
                console.print(f"[dim]abilities on hand ({len(section.abilities)}):[/dim]"
                              f" {', '.join(section.abilities[:14])}")
            if section.relations:
                console.print(f"\n[dim]relations in scope "
                              f"({len(section.relations)}):[/dim]")
                for tie in section.relations[:14]:
                    console.print(f"   {tie}")
            return

        found = chronology.appearances(store, subject)
        if not found:
            console.print(f"[yellow]No arc files any history for "
                          f"{subject!r}.[/yellow]")
            raise typer.Exit(code=1)
        total = sum(appearance.words for appearance in found)
        console.print(f"[bold]{subject}[/bold]: {len(found)} arcs, {total} words\n")
        for appearance in found:
            console.print(f"[bold]{appearance.heading}[/bold]")
            if full:
                for passage in appearance.passages:
                    console.print(f"   {passage}\n")
            else:
                console.print(f"   [dim]{len(appearance.passages)} passages, "
                              f"{appearance.words} words[/dim]")
                console.print(f"   {appearance.passages[0][:200]}…\n")


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

    table = Table(title=f"Retrieval eval: {series}")
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


@app.command("canon-run")
def canon_run(
    series: list[str] = typer.Option(
        None, "--series",
        help="Limit to these series. Repeat the flag or comma-separate. "
             "Default: every series in questions/."),
    skip_eval: bool = typer.Option(
        False, "--skip-eval",
        help="Skip the in-process gold suite. Use this while the server is "
             "hot: it loads an embedder and a reranker here while the server "
             "may still hold its own, which double-allocates on one GPU."),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Validate the question bank and print what would be asked. "
             "Calls nothing."),
    out: Path = typer.Option(
        None, "--out", help="Write the run folder here instead of reports/."),
) -> None:
    """Measure the engine against `questions/` and write a report.

    Never exits non-zero on a bad score. A low number is the finding, and a
    measurement command that fails the build is one nobody runs. Exit 1 is
    reserved for the run being untrustworthy: no server, a server running
    superseded code, or a bank that does not validate.
    """
    import logging

    from scriptengine.eval.canon_run import CanonRunError
    from scriptengine.eval.canon_run import run as canon_run_impl

    logging.disable(logging.INFO)

    wanted = [s.strip() for entry in (series or []) for s in entry.split(",") if s.strip()]

    try:
        result = canon_run_impl(
            series=wanted or None, skip_eval=skip_eval, dry_run=dry_run,
            out=out, log=console.print,
        )
    except CanonRunError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    if dry_run:
        return

    summary = result["summary"]
    table = Table(title=f"Canon run: {result['meta']['run_id']}")
    table.add_column("")
    table.add_column("", justify="right")
    # First row, because it is the one that says whether the questions were
    # answered. The other two can both look healthy while it does not move.
    table.add_row("answered exactly right",
                  f"{summary.get('exact_answers', 0)}/{summary.get('exact_of', 0)} "
                  f"({summary.get('exact_rate', 0):.1%})")
    table.add_row("canon items recovered",
                  f"{summary['canon_found']}/{summary['canon_total']} "
                  f"({summary['canon_recall']:.1%})")
    table.add_row("precision, closed sets",
                  f"{summary['precision_closed']:.1%} over {summary['precision_over']}")
    table.add_row("questions at recall 0",
                  f"{summary['at_recall_zero']}/{summary['questions']}")
    table.add_row("confident and wrong", str(len(summary["confident_and_wrong"])))
    if summary["fact_questions"]:
        table.add_row("fact answers present in the bundle",
                      f"{summary['fact_present']}/{summary['fact_questions']}")
    console.print(table)
    console.print(f"\n[bold]{result['folder'] / 'REPORT.md'}[/bold]")


@app.command("span-recall")
def span_recall(
    series: str = typer.Option(..., "--series", help="The series to sweep."),
    probe: int = typer.Option(
        0, "--probe",
        help="Also probe the live server with this many sampled sentences "
             "(tier 1). Omit for the offline coverage check alone, which is "
             "the cheap exhaustive one and needs no server."),
    mode: str = typer.Option(
        "verbatim", "--mode",
        help="Tier 1 query shape: verbatim (reachability floor), scoped "
             "(prefixes the page title, controlling for a wiki that narrates "
             "one event on four pages), or terms (stopwords stripped)."),
    min_words: int = typer.Option(
        6, "--min-words", help="Ignore sentences shorter than this."),
    include_boilerplate: bool = typer.Option(
        False, "--include-boilerplate",
        help="Also audit Navigation/See Also/External Links sections, which "
             "are excluded by default because the indexer drops them on "
             "purpose."),
    out: Path = typer.Option(
        None, "--out", help="Write the run folder here instead of reports/."),
) -> None:
    """Check every sentence in a series is reachable, not just the sampled ones.

    The gold bank asks about roughly one line in eight. This asks about all of
    them: tier 0 proves each sentence sits whole inside some chunk (offline,
    exhaustive, sub-second), and `--probe` samples the live server to see
    whether the line actually comes back.

    Exit 2 when tier 0 finds unreachable lines -- that is a defect, and the
    whole point is for a re-index that drops content to fail loudly. A tier 1
    score never fails the command: a low number is the finding, and a
    measurement that breaks the build is one nobody runs. Exit 1 is reserved
    for a run that cannot be trusted at all.
    """
    from scriptengine.eval import span_recall as impl

    settings = get_settings()
    reports_root = Path(out) if out else Path(settings.reports_root)
    folder = reports_root / "span-recall" / series
    folder.mkdir(parents=True, exist_ok=True)

    try:
        tier0 = impl.index_coverage(
            series, settings, min_words=min_words,
            include_boilerplate=include_boilerplate)
    except impl.SpanRecallError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    _write_jsonl(folder / "index_misses.jsonl", tier0["misses"])

    table = Table(title=f"Span recall: {series}")
    table.add_column("")
    table.add_column("", justify="right")
    table.add_row("sections", str(tier0["sections"]))
    table.add_row("sentences", str(tier0["sentences"]))
    table.add_row("present in a chunk", str(tier0["covered"]))
    table.add_row("unreachable", str(tier0["missing"]))
    table.add_row("coverage", f"{tier0['coverage']:.4%}")
    console.print(table)
    if tier0["boilerplate_skipped"]:
        console.print(
            f"[dim]{tier0['boilerplate_skipped']} sentences in link-list "
            f"boilerplate excluded; --include-boilerplate to audit them.[/dim]")

    if tier0["missing"]:
        worst: dict[str, int] = {}
        for row in tier0["misses"]:
            worst[row["title"]] = worst.get(row["title"], 0) + 1
        console.print("\n[bold]documents with unreachable lines[/bold]")
        for title, count in sorted(worst.items(), key=lambda kv: -kv[1])[:20]:
            console.print(f"  {count:>5}  {title}")
        console.print(f"\n[bold]{folder / 'index_misses.jsonl'}[/bold]")

    if probe:
        rows_path = folder / f"recall_{mode}.jsonl"
        handle = rows_path.open("a", encoding="utf-8")

        def on_row(row: dict) -> None:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            handle.flush()

        def on_progress(i: int, total: int, counts: dict) -> None:
            console.print(f"  [dim]{i}/{total}  {counts}[/dim]")

        try:
            tier1 = impl.recall(
                series, settings, mode=mode, sample=probe, every=100,
                min_words=min_words, on_row=on_row, on_progress=on_progress)
        finally:
            handle.close()

        counts = tier1["counts"]
        t1 = Table(title=f"Live probe: {series} ({mode})")
        t1.add_column("")
        t1.add_column("", justify="right")
        t1.add_row("probes", str(tier1["probes"]))
        t1.add_row("served the line", f"{counts['HIT']} ({tier1['hit_rate']:.1%})")
        t1.add_row("page not retrieved", str(counts["MISS_DOC"]))
        t1.add_row("page retrieved, line absent", str(counts["MISS_SPAN"]))
        t1.add_row("bundle truncated", str(counts["TRUNCATED"]))
        t1.add_row("errors", str(counts["ERROR"]))
        console.print(t1)
        console.print(f"[bold]{rows_path}[/bold]")

    if tier0["missing"]:
        raise typer.Exit(code=2)


def _write_jsonl(path: Path, rows: list[dict]) -> None:
    """Plain utf-8, no BOM: a BOM corrupts the first record of a JSONL stream."""
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    tmp = path.with_suffix(path.suffix + ".tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        assert tmp.read_text(encoding="utf-8") == payload
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


@app.command("page-run")
def page_run(
    series: str = typer.Option(..., "--series", help="The series the batch belongs to."),
    slug: str = typer.Option(
        ..., "--batch",
        help="The page cluster's slug; loads questions/_<series>_page_<slug>.json "
             "(e.g. --batch yuji_itadori)."),
    dry_run: bool = typer.Option(
        False, "--dry-run",
        help="Validate the batch and print what would be asked. Calls nothing."),
    out: Path = typer.Option(
        None, "--out",
        help="Write the run folder here instead of reports/page-campaign/."),
) -> None:
    """Score one page campaign's question batch against the live server.

    The page-driven accuracy loop: author ~100 questions about one wiki page
    and its siblings in `questions/_<series>_page_<slug>.json`, run this, triage
    every failure (gold error vs engine gap), fix or declare, re-run until 100%.
    Batches are excluded from the official bank by their `_` prefix.

    Exit codes: 0 at 100%, 2 while questions still fail (the loop scripts on
    this), 1 when the run is untrustworthy -- no server, a stale server, or a
    batch that does not validate. A bad score never crashes the command.
    """
    import logging

    from scriptengine.eval.canon_run import CanonRunError
    from scriptengine.eval.page_campaign import run as page_run_impl

    logging.disable(logging.INFO)

    try:
        result = page_run_impl(series=series, slug=slug, dry_run=dry_run,
                               out=out, log=console.print)
    except CanonRunError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    if result.get("dry_run"):
        return

    summary = result["summary"]
    table = Table(title=f"Page run: {result['meta']['run_id']}")
    table.add_column("")
    table.add_column("", justify="right")
    passed = sum(1 for r in result["results"] if r["passed"])
    total = len(result["results"])
    colour = "green" if result["complete"] else "red"
    table.add_row("questions passed", f"[{colour}]{passed}/{total}[/{colour}]")
    table.add_row("set questions exact",
                  f"{summary.get('exact_answers', 0)}/{summary.get('exact_of', 0)} "
                  f"({summary.get('exact_rate', 0):.1%})")
    if summary["fact_questions"]:
        table.add_row("fact answers present in the bundle",
                      f"{summary['fact_present']}/{summary['fact_questions']}")
    console.print(table)
    console.print(f"\n[bold]{result['folder'] / 'REPORT.md'}[/bold]")
    if not result["complete"]:
        raise typer.Exit(code=2)


@app.command("page-gen")
def page_gen(
    series: str = typer.Option(..., "--series", help="The series the page belongs to."),
    page: str = typer.Option(..., "--page", help="The wiki page title, e.g. 'Angel'."),
    out: Path = typer.Option(
        None, "--out",
        help="Write the batch there instead of questions/_<series>_page_<slug>.json."),
    verify_sheet: Path = typer.Option(
        None, "--verify-sheet",
        help="Write the verify sheet there instead of alongside the batch."),
    no_prose_scaffold: bool = typer.Option(
        False, "--no-prose-scaffold",
        help="Skip the coverage.json + verify.json scaffolds; keep the batch and decl."),
) -> None:
    """Generate the structured half of a page-campaign batch from `facts.db`.

    The regular questions (infobox identity, the per-battle block, roster sets)
    are a deterministic function of the store, so they are generated, numbered
    into the campaign batch without touching a hand-authored question, and
    paired with a decl fragment plus the prose pass's scaffolds:

      questions/_<series>_page_<slug>.json        the reconciled batch
      questions/_<series>_page_<slug>.decl.yaml   the roster declarations
      questions/_<series>_page_<slug>.coverage.json  the section-coverage ledger
      questions/_<series>_page_<slug>.verify.json    the verify sheet

    Exit 0 on success, 1 when the page cannot be generated or the batch fails
    validation.
    """
    import logging

    from scriptengine.config import load_overrides
    from scriptengine.eval import questions as Q
    from scriptengine.eval.page_gen import (
        PageGenError, run_page_gen, slug_of)

    logging.disable(logging.INFO)

    settings = get_settings()
    paths = series_paths(series, settings)
    overrides = load_overrides(paths)
    slug = slug_of(page)
    questions_root = settings.questions_root
    questions_root.mkdir(parents=True, exist_ok=True)
    base = f"_{series}_page_{slug}"
    batch_path = Path(out) if out else questions_root / f"{base}.json"
    decl_path = questions_root / f"{base}.decl.yaml"
    coverage_path = questions_root / f"{base}.coverage.json"
    verify_path = Path(verify_sheet) if verify_sheet else questions_root / f"{base}.verify.json"

    try:
        status = run_page_gen(
            paths, page, overrides, batch_path, decl_path, coverage_path,
            verify_path, no_prose_scaffold)
    except (PageGenError, Q.QuestionsError) as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error

    by_class = status["by_class"]

    table = Table(title=f"page-gen: {series} / {page}")
    table.add_column("")
    table.add_column("", justify="right")
    for cls in sorted(by_class):
        table.add_row(f"{cls} questions", str(by_class[cls]))
    table.add_row("structured questions", str(status["structured"]))
    table.add_row("rosters declared", str(status["rosters"]))
    table.add_row("auto-retires", str(status["auto_retires"]))
    table.add_row("hand-authored kept", str(status["hand_kept"]))
    table.add_row("collisions superseded", str(status["superseded"]))
    if not no_prose_scaffold:
        table.add_row("uncovered sections", str(len(status["uncovered"])))
    console.print(table)
    for retire in status["retires"]:
        console.print(f"  [dim]retired: {retire['question']} -- {retire['reason']}[/dim]")
    console.print(f"[bold]batch[/bold]: {batch_path}")
    console.print(f"[bold]decl[/bold]: {decl_path}")
    if not no_prose_scaffold:
        console.print(f"[bold]coverage[/bold]: {coverage_path}")
        console.print(f"[bold]verify[/bold]: {verify_path}")


@app.command("page-sweep")
def page_sweep(
    series: str = typer.Option(..., "--series", help="The series to sweep."),
    tier: str = typer.Option(
        "b", "--tier", help="a = characters, b = character-centric non-characters."),
    include: str = typer.Option(
        "", "--include",
        help="Comma-separated extra titles (e.g. the redos the store types unknown)."),
    force: bool = typer.Option(
        False, "--force", help="Re-sweep pages already in the report."),
    limit: int = typer.Option(
        0, "--limit", help="Sweep at most N pages this run (0 = all that remain)."),
    out: Path = typer.Option(
        None, "--out", help="Write the report there instead of alongside the batches."),
) -> None:
    """Run `page-gen` across a whole page tier, writing each page's artifacts
    plus a per-page status report. Resumable: pages already swept (no error) are
    skipped unless `--force`. A page that fails is recorded with its error and
    the sweep continues, so one bad page never aborts the tier."""
    import logging
    from datetime import date

    from scriptengine.config import load_overrides
    from scriptengine.eval.page_gen import (
        PageGenError, page_set, run_page_gen, slug_of)
    from scriptengine.stores.facts import FactStore

    logging.disable(logging.INFO)

    settings = get_settings()
    paths = series_paths(series, settings)
    overrides = load_overrides(paths)
    store = FactStore(paths.facts_db)
    try:
        include_list = [t for t in (include or "").split(",") if t.strip()]
        titles = page_set(store, tier, include_list)
    except PageGenError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
    finally:
        store.close()

    questions_root = settings.questions_root
    questions_root.mkdir(parents=True, exist_ok=True)
    report_path = (out if out
                   else questions_root / f"_{series}_page_sweep_{tier}.report.json")
    report = (json.loads(report_path.read_text(encoding="utf-8"))
              if report_path.exists()
              else {"series": series, "tier": tier, "pages": []})
    done = {p["page"] for p in report["pages"] if not p.get("error")}

    swept = 0
    errors = 0
    for title in titles:
        if limit and swept >= limit:
            break
        if title in done and not force:
            continue
        slug = slug_of(title)
        base = f"_{series}_page_{slug}"
        batch_path = questions_root / f"{base}.json"
        decl_path = questions_root / f"{base}.decl.yaml"
        coverage_path = questions_root / f"{base}.coverage.json"
        verify_path = questions_root / f"{base}.verify.json"
        try:
            status = run_page_gen(
                paths, title, overrides, batch_path, decl_path,
                coverage_path, verify_path)
        except Exception as error:  # record and continue; the sweep is resilient
            status = {"page": title, "error": f"{type(error).__name__}: {error}"}
        row = {k: v for k, v in status.items() if k != "retires"}
        index = next(
            (i for i, p in enumerate(report["pages"]) if p["page"] == title), None)
        if index is None:
            report["pages"].append(row)
        else:
            report["pages"][index] = row
        swept += 1
        if row.get("error"):
            errors += 1
            console.print(f"[red]  {title}: {row['error']}[/red]")
        else:
            console.print(f"[dim]  {title}: {row['structured']} structured, "
                          f"{len(row['uncovered'])} uncovered[/dim]")

    report["updated"] = date.today().isoformat()
    report_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    total_structured = sum(
        p.get("structured", 0) for p in report["pages"] if not p.get("error"))
    console.print(
        f"swept {swept} page(s) this run ({errors} errors); "
        f"report holds {len(report['pages'])} pages, {total_structured} structured Qs")
    console.print(f"[bold]report[/bold]: {report_path}")


@app.command("page-merge")
def page_merge(
    series: str = typer.Option(..., "--series", help="The series the decl belongs to."),
    batch: str = typer.Option(
        ..., "--batch",
        help="The page cluster's slug; merges questions/_<series>_page_<slug>.decl.yaml "
             "(e.g. --batch angel)."),
    decl: Path = typer.Option(
        None, "--decl",
        help="Merge this decl file instead of the cluster's default."),
) -> None:
    """Merge a page-gen decl fragment into `series/<series>/overrides.yaml`.

    Text-insert only: the house comments in `overrides.yaml` survive, duplicate
    roster names are skipped, and the result is re-parsed before it is written.
    Exit 0 on success, 1 when the merge or its validation fails.
    """
    from datetime import date

    from scriptengine.eval.page_gen import PageGenError, _decl_rosters, merge_decl

    settings = get_settings()
    paths = series_paths(series, settings)
    decl_path = (Path(decl) if decl
                 else settings.questions_root / f"_{series}_page_{batch}.decl.yaml")
    if not decl_path.exists():
        console.print(f"[red]no decl at {decl_path}[/red]")
        raise typer.Exit(code=1)
    try:
        inserted = merge_decl(
            decl_path, paths.overrides,
            f"# ── page-gen: {batch} ({date.today().isoformat()}) ──")
    except PageGenError as error:
        console.print(f"[red]{error}[/red]")
        raise typer.Exit(code=1) from error
    total = len(_decl_rosters(decl_path))
    console.print(
        f"merged {inserted}/{total} roster(s) from {decl_path.name} into {paths.overrides}")
    if total - inserted:
        console.print(f"[dim]{total - inserted} skipped (already declared)[/dim]")
    console.print(
        "[dim]overrides.yaml reloads per request -- no server restart needed.[/dim]")


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
    # canon_gold's scorer prints raw CJK (kanji identity answers) to stdout; on a
    # Windows cp1252 console that raises UnicodeEncodeError unless stdout is
    # UTF-8. canon_gold.main() reconfigures itself, but the CLI entry never runs
    # that path, so force it here (page-run, canon-run, etc.).
    for _stream in (sys.stdout, sys.stderr):
        _reconfigure = getattr(_stream, "reconfigure", None)
        if _reconfigure is not None:
            _reconfigure(encoding="utf-8", errors="replace")
    sys.exit(app())
