"""Regenerate the page-campaign coverage report (facts.db x committed batches).

This file's output is the single source of truth for "what is done / what
remains" in a series' prose campaign. Run it after every batch commit; do NOT
hand-edit the generated markdown. Other docs must not state what is next or
what remains — they point here.

The campaign scope (which page types are in-scope, how the `unknown` pages
are disposed, the remainder paragraph) is read from `series/<name>/
overrides.yaml` (`page_scope` + `unknown_pages` + `remainder_note`) — the
former JJK-hardcoded `IN_SCOPE_TYPES` / `IN_SCOPE_PAGES` were retired in
CSM-2. Silence is an error: a page_type the series has not been told how to
classify exits non-zero (3), never a silent default.

Usage:
    python tools/coverage_report.py [series] [--out PATH]

Exit codes: 2 = no facts.db (not indexed), 3 = scope not fully classified.
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scriptengine.config import load_overrides, series_paths  # noqa: E402
from scriptengine.stores.facts import FactStore       # noqa: E402
from scriptengine.eval.page_gen import slug_of        # noqa: E402


class ScopeError(RuntimeError):
    """The series has not declared its campaign scope — silence is an error."""


def load_page_scope(paths) -> dict:
    """The series' campaign scope from its overrides (CSM-2).

    `page_scope` is mandatory: a series whose page types are not classified
    cannot be measured. Raises ScopeError when it is missing."""
    ovr = load_overrides(paths)
    types = ovr.get("page_scope")
    if not isinstance(types, dict) or not types:
        raise ScopeError(
            f"no `page_scope` declared in {paths.overrides} — every page_type "
            f"must be classified in-scope or excluded-in-writing (CSM-2)")
    return {
        "types": types,
        "unknown_pages": ovr.get("unknown_pages") or {},
        "remainder_note": ovr.get("remainder_note"),
    }


def scope_violations(docs, ps: dict) -> list[str]:
    """Unclassified page types + `unknown` pages without a per-page
    disposition. Empty = the series is fully classified."""
    out: set[str] = set()
    for title, pt in docs:
        if pt not in ps["types"]:
            out.add(f"page_type {pt!r} is not classified in `page_scope`")
        if pt == "unknown" and title not in ps["unknown_pages"]:
            out.add(f"unknown page {title!r} has no disposition in `unknown_pages`")
    return sorted(out)


def in_scope(pt: str, title: str, ps: dict) -> bool:
    if ps["types"].get(pt, {}).get("in_scope"):
        return True
    return pt == "unknown" and bool(ps["unknown_pages"].get(title, {}).get("in_scope"))


def base_batches(qdir: Path, series: str) -> dict[str, Path]:
    """slug -> path for every committed BASE batch.

    The slug itself carries no dots; the `.coverage` / `.verify` /
    `.sectionN` siblings do, so the `[^.]+` before `.json` keeps only the base."""
    out: dict[str, Path] = {}
    pat = re.compile(rf"^_{re.escape(series)}_page_([^.]+)\.json$")
    for f in sorted(qdir.glob(f"_{series}_page_*.json")):
        m = pat.match(f.name)
        if m:
            out[m.group(1)] = f
    return out


def active_questions(path: Path) -> int | None:
    """Active (non-retired) question count for a base batch, or None if unreadable."""
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError, UnicodeDecodeError):
        return None
    q = data.get("questions", []) if isinstance(data, dict) else data
    return len(q) if isinstance(q, list) else 0


def render(series: str, docs, batches: dict[str, Path], ps: dict) -> tuple[str, dict]:
    pages = collections.Counter(pt for _, pt in docs)
    covered = collections.Counter()
    questions = collections.Counter()
    uncovered = collections.defaultdict(list)
    in_scope_uncovered: list[tuple[str, str]] = []
    covered_zero: list[str] = []
    parse_errors: list[str] = []
    doc_slugs: set[str] = set()

    for title, pt in docs:
        s = slug_of(title)
        doc_slugs.add(s)
        if s in batches:
            covered[pt] += 1
            n = active_questions(batches[s])
            if n is None:
                parse_errors.append(title)
                n = 0
            questions[pt] += n
            if n == 0:
                covered_zero.append(title)
        else:
            uncovered[pt].append(title)
            if in_scope(pt, title, ps):
                in_scope_uncovered.append((pt, title))

    orphans = sorted(set(batches) - doc_slugs)
    total_pages = len(docs)
    total_covered = sum(covered.values())
    total_q = sum(questions.values())

    def pct(c: int, p: int) -> str:
        return f"{100 * c / p:.1f}%" if p else "—"

    a: list[str] = []
    ap = a.append
    ap(f"# {series.upper()} page-campaign coverage")
    ap("")
    ap("> Regenerated by `tools/coverage_report.py` — **do not hand-edit;** run it")
    ap("> after every batch commit. No document states what is next or what")
    ap("> remains; it points here.")
    ap(">")
    ap(f"> Facts: `series/{series}/facts.db` (`documents`). Batches:")
    ap(f"> `questions/_{series}_page_<slug>.json`. Slug rule: `slug_of`")
    ap("> (`scriptengine/eval/page_gen.py`) — lowercase, non-alphanumeric runs")
    ap("> become `_` (so `&` collapses away).")
    ap(">")
    ap(f"> Generated: {datetime.date.today().isoformat()}")
    ap("")
    ap("## Headline")
    ap("")
    ap(f"**{total_covered} / {total_pages} pages covered ({pct(total_covered, total_pages)}) · "
       f"{total_q:,} active questions** across the committed batches.")
    ap("")
    ap("## Per-type coverage")
    ap("")
    ap("| page_type | pages | covered | % | questions |")
    ap("|---|---:|---:|---:|---:|")
    for pt in sorted(pages, key=lambda x: (-pages[x], x)):
        ap(f"| {pt} | {pages[pt]} | {covered[pt]} | {pct(covered[pt], pages[pt])} | {questions[pt]:,} |")
    ap(f"| **TOTAL** | **{total_pages}** | **{total_covered}** | "
       f"{pct(total_covered, total_pages)} | **{total_q:,}** |")
    ap("")
    ap("## In-scope content remainder")
    ap("")
    if ps.get("remainder_note"):
        for line in ps["remainder_note"].rstrip("\n").splitlines():
            ap(line)
    else:
        ap("Content-bearing pages not yet covered (authorable prose). Excluded")
        ap("types carry a one-line reason in the series' overrides.yaml")
        ap("`page_scope` (excluded-in-writing).")
    ap("")
    by_type = collections.Counter(pt for pt, _ in in_scope_uncovered)
    unknown_in_scope = sorted(t for t, disp in ps["unknown_pages"].items() if disp.get("in_scope"))
    n_pages_in = sum(1 for pt, _ in in_scope_uncovered if pt == "unknown")
    ap("| source | pages |")
    ap("|---|---:|")
    in_scope_types = [pt for pt, v in ps["types"].items() if v.get("in_scope")]
    for t in sorted(in_scope_types, key=lambda x: (-by_type.get(x, 0), x)):
        if by_type.get(t):
            ap(f"| {t} | {by_type[t]} |")
    if n_pages_in:
        ap(f"| `unknown` ({', '.join(unknown_in_scope)}) | {n_pages_in} |")
    ap(f"| **total** | **{len(in_scope_uncovered)}** |")
    ap("")
    ap("## Uncovered titles")
    ap("")
    for pt in sorted(uncovered, key=lambda x: (-len(uncovered[x]), x)):
        ap(f"### {pt} ({len(uncovered[pt])})")
        ap("")
        for t in sorted(uncovered[pt]):
            ap(f"- {t}")
        ap("")
    ap("## Integrity")
    ap("")
    ap(f"- Orphan batches (base batch whose slug matches no live document): **{len(orphans)}**")
    for s in orphans:
        ap(f"  - `_{series}_page_{s}.json`")
    if covered_zero:
        ap(f"- Covered pages with 0 active questions: **{len(covered_zero)}** — "
           f"{', '.join(sorted(covered_zero))}")
    if parse_errors:
        ap(f"- Batch files that failed to parse: {', '.join(parse_errors)}")
    ap("")
    ap("---")
    ap("")
    ap("*Standing rule: no document states what is next or what remains; it points at")
    ap("this file, which is regenerated (not edited) after every batch commit.*")
    ap("")

    stats = {
        "total_pages": total_pages, "total_covered": total_covered,
        "total_q": total_q, "in_scope": len(in_scope_uncovered),
        "orphans": len(orphans),
    }
    return "\n".join(a), stats


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Regenerate the page-campaign coverage report.")
    ap.add_argument("series", nargs="?", default="jjk")
    ap.add_argument("--out", default=None,
                    help="markdown path (default reports/page-campaign/COVERAGE.md)")
    args = ap.parse_args(argv)

    series = args.series
    paths = series_paths(series)
    if not paths.facts_db.exists():
        print(f"error: no facts.db at {paths.facts_db}", file=sys.stderr)
        return 2
    qdir = ROOT / "questions"
    out = Path(args.out) if args.out else ROOT / "reports" / "page-campaign" / "COVERAGE.md"

    batches = base_batches(qdir, series)
    st = FactStore(paths.facts_db)
    try:
        docs = [(r["title"], r["page_type"]) for r in
                st.connection.execute("SELECT title, page_type FROM documents")]
    finally:
        st.close()

    # CSM-2: the scope comes from the series' overrides; an unclassified
    # page_type (or an `unknown` page without a per-page disposition) is an
    # error, not a silent default.
    try:
        ps = load_page_scope(paths)
    except ScopeError as error:
        print(f"error: {error}", file=sys.stderr)
        return 3
    violations = scope_violations(docs, ps)
    if violations:
        for v in violations:
            print(f"error: {v}", file=sys.stderr)
        print(f"error: {len(violations)} unclassified — declare them in "
              f"{paths.overrides} (`page_scope` / `unknown_pages`)", file=sys.stderr)
        return 3

    md, stats = render(series, docs, batches, ps)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"{series}: {stats['total_covered']}/{stats['total_pages']} pages "
          f"({100 * stats['total_covered'] / stats['total_pages']:.1f}%), "
          f"{stats['total_q']:,} questions; in-scope content remainder "
          f"{stats['in_scope']}; orphans {stats['orphans']}.")
    print(f"  wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())