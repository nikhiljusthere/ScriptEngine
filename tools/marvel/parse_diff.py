#!/usr/bin/env python
"""Gate 4/6 harness: base-parser vs new-parser extraction diff on a stored corpus.

Council A1c/A1b verdict (reports/marvel/COUNCIL_a1c_a1b_landed.md), gates 4+6:
run the BASE parser (worktree of 1adb0d42, selected via PYTHONPATH) and the
NEW parser over the same stored wikitext snapshots, then diff fact counts,
types, and fact-key sets. Stop conditions (council): stable-population
fact-count delta > 10%, or a systematic content rewrite (one fact key
net-lost from >= 25% of the stable population) -> A2 stays blocked.

Usage (repo root; venv = scriptengine/.venv/bin/python):

  NEW:  scriptengine/.venv/bin/python tools/marvel/parse_diff.py extract \
            --series mcu --out reports/marvel/receipts/parse_diff_mcu_new.jsonl
  BASE: PYTHONPATH=/tmp/se_base_1adb0d42 scriptengine/.venv/bin/python \
            tools/marvel/parse_diff.py extract --series mcu \
            --out reports/marvel/receipts/parse_diff_mcu_base.jsonl
  DIFF: scriptengine/.venv/bin/python tools/marvel/parse_diff.py diff \
            --base .../parse_diff_mcu_base.jsonl --new .../parse_diff_mcu_new.jsonl \
            --report .../parse_diff_mcu_report.md

Semantics: `extract` uses the active tree's official `load_extracted` (the
same path the real `index` uses), so the diff measures exactly
"re-parse with the base parser" vs "re-parse with the current parser +
current overrides". The BASE run passes overrides=None: at 1adb0d42 no
series overrides.yaml existed, so the baseline is base parser +
manifest-carried ontology only (the commit-under-test 6a1f6ceb is the full
delta: parser + hooks + overrides).

`--limit N` mirrors load_extracted's ontology setup for rate estimation only
(it is not the official output path). `--truncation N` is review-5's
synthetic test: N infobox pages have their wikitext cut mid-template
(simulating a truncated download) and are re-extracted, to characterize
what F2's unclosed-lead branch does to a download artifact (crash /
garbage facts / benign lead) without ever touching the stored corpus.
"""

from __future__ import annotations

import argparse
import itertools
import json
import sys
import time
from pathlib import Path


def _tree():
    """Import the ACTIVE tree's modules (selected by PYTHONPATH).

    Lazy so that `diff` stays pure-stdlib and can run without the engine.
    """
    from scriptengine.config import SeriesPaths, load_overrides
    from scriptengine.ingest import crawler as C
    from scriptengine.ingest.ontology import Ontology

    return SeriesPaths, load_overrides, C, Ontology


def _row(page, values: bool) -> dict:
    row = {
        "title": page.title,
        "pageid": page.pageid,
        "revid": page.revid,
        "type": page.page_type,
        "infobox": page.infobox_template,
        "n_facts": len(page.facts),
        "keys": sorted({f.key for f in page.facts}),
        "n_aliases": len(page.aliases),
        "n_warnings": len(page.warnings),
        "warnings": list(page.warnings[:5]),
    }
    if values:
        row["facts"] = [[f.key, str(f.value)[:300]] for f in page.facts]
        row["aliases"] = list(page.aliases[:10])
    return row


def _ontology_merge(ontology, manifest: dict, pages, overrides) -> None:
    """Tree-agnostic mirror of load_extracted's ontology setup (rate mode only)."""
    from scriptengine.ingest import crawler as C

    discovered = C.discover_infoboxes(
        manifest.get("wiki", ""),
        ((p.title, p.wikitext) for p in pages if p.wikitext),
        overrides,
    )
    ontology.infobox_types.update(discovered.infobox_types)
    ontology.infobox_votes = discovered.infobox_votes
    ontology.skip_categories |= discovered.skip_categories
    ontology.citation_works = discovered.citation_works
    ontology.item_sections = discovered.item_sections
    # L2 hooks exist only on the post-A1b trees; getattr keeps this tree-agnostic.
    if getattr(discovered, "skip_patterns", None) is not None:
        ontology.skip_patterns = discovered.skip_patterns
    if getattr(discovered, "alias_fact_keys", None):
        ontology.alias_fact_keys = discovered.alias_fact_keys


def cmd_extract(args) -> int:
    SeriesPaths, load_overrides, C, Ontology = _tree()
    paths = SeriesPaths(args.series, Path("series") / args.series)
    overrides = load_overrides(paths) if not args.no_overrides else None
    t0 = time.time()
    if args.limit:
        manifest = C.load_manifest(paths)
        pages = list(itertools.islice(C.load_pages(paths), args.limit))
        ontology = Ontology.from_dict(manifest.get("ontology") or {})
        _ontology_merge(ontology, manifest, pages, overrides)
        rows = [_row(C.reextract(p, ontology), args.values) for p in pages]
    else:
        pages, ontology = C.load_extracted(paths, overrides)
        rows = [_row(p, args.values) for p in pages]
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    total_facts = sum(r["n_facts"] for r in rows)
    print(
        f"extract {args.series}: {len(rows)} pages, {total_facts} facts, "
        f"{time.time() - t0:.1f}s "
        f"({len(rows) / max(time.time() - t0, 1e-6):.0f} pages/s)"
        + (f" [RATE MODE: limit={args.limit}]" if args.limit else "")
    )
    return 0


def cmd_diff(args) -> int:
    def load(path: str) -> dict:
        rows = {}
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                row = json.loads(line)
                rows[(row["title"], row["pageid"])] = row
        return rows

    base = load(args.base)
    new = load(args.new)
    common = [k for k in base if k in new]
    only_base = sorted(set(base) - set(new))
    only_new = sorted(set(new) - set(base))

    stable = [k for k in common if base[k]["n_facts"] > 0]
    stable_delta = (
        (sum(new[k]["n_facts"] for k in stable)
         - sum(base[k]["n_facts"] for k in stable))
        / max(sum(base[k]["n_facts"] for k in stable), 1)
    )
    all_delta = (
        sum(new[k]["n_facts"] for k in common)
        - sum(base[k]["n_facts"] for k in common)
    ) / max(sum(base[k]["n_facts"] for k in common), 1)

    type_changes = {}
    for k in common:
        if base[k]["type"] != new[k]["type"]:
            type_changes.setdefault(
                (base[k]["type"], new[k]["type"]), []
            ).append(k[0])

    # fact-key churn over the stable population (systematic-rewrite detector)
    lost = {}
    gained = {}
    for k in stable:
        bkeys, nkeys = set(base[k]["keys"]), set(new[k]["keys"])
        for key in bkeys - nkeys:
            lost[key] = lost.get(key, 0) + 1
        for key in nkeys - bkeys:
            gained[key] = gained.get(key, 0) + 1
    n_stable = max(len(stable), 1)
    systemic_lost = {
        key: count for key, count in lost.items() if count / n_stable >= 0.25
    }

    diffs = sorted(
        (
            (abs(new[k]["n_facts"] - base[k]["n_facts"]), k)
            for k in common
            if new[k]["n_facts"] != base[k]["n_facts"]
        ),
        reverse=True,
    )
    top = diffs[:20]

    blocked = stable_delta > 0.10 or bool(systemic_lost)
    lines = [
        "# Parser diff report — gate 4/6 (council stop condition)",
        "",
        f"- base: `{args.base}` (base parser + manifest ontology, no overrides)",
        f"- new:  `{args.new}` (current parser + current overrides.yaml)",
        f"- pages: base {len(base)}, new {len(new)}, common {len(common)}"
        + (f"; ONLY IN BASE {len(only_base)}: {only_base[:5]}" if only_base else "")
        + (f"; ONLY IN NEW {len(only_new)}: {only_new[:5]}" if only_new else ""),
        f"- stable population (base n_facts > 0): {len(stable)}",
        f"- stable fact-count delta: {stable_delta:+.2%}  (stop if > 10%)",
        f"- all-common fact-count delta: {all_delta:+.2%} "
        f"(includes base-unknown pages gaining type — the intended A1 effect)",
        f"- type changes: "
        + (
            "; ".join(
                f"{b}→{n} ×{len(titles)}"
                for (b, n), titles in sorted(type_changes.items())
            )
            or "none"
        ),
        f"- keys net-lost from stable pages: "
        + (
            "; ".join(f"{k} ×{c}" for k, c in sorted(lost.items(), key=lambda x: -x[1])[:15])
            or "none"
        ),
        f"- keys gained: "
        + (
            "; ".join(f"{k} ×{c}" for k, c in sorted(gained.items(), key=lambda x: -x[1])[:15])
            or "none"
        ),
        f"- systematic rewrite (key lost from >=25% of stable): "
        + ("; ".join(f"{k} ×{c}" for k, c in systemic_lost.items()) if systemic_lost else "none"),
        "",
        "## Top 20 |Δ facts| (common pages)",
        "",
        "| title | base | new | b-type | n-type |",
        "|---|---|---|---|---|",
    ]
    for delta, k in top:
        b, n = base[k], new[k]
        lines.append(
            f"| {k[0]} | {b['n_facts']} | {n['n_facts']} | {b['type']} | {n['type']} |"
        )
    lines += [
        "",
        "## Verdict",
        "",
        f"**{'A2 BLOCKED' if blocked else 'PROCEED'}** — "
        + (
            f"stable delta {stable_delta:+.1%} exceeds 10%"
            if stable_delta > 0.10
            else f"stable delta {stable_delta:+.1%} within 10%"
        )
        + (
            f" AND systematic key loss: {', '.join(systemic_lost)}"
            if systemic_lost
            else (", no systematic key loss" if not blocked else "")
        )
        + ".",
        "",
    ]
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(f"diff: stable_delta={stable_delta:+.2%} blocked={blocked} -> {args.report}")
    return 0


def cmd_truncation(args) -> int:
    """Review-5 synthetic test: what does the current parser do to a
    truncated fetch? (F2's unclosed-lead branch fires on a genuinely
    unclosed template OR a truncated download; characterize which.)"""
    SeriesPaths, load_overrides, C, Ontology = _tree()
    paths = SeriesPaths(args.series, Path("series") / args.series)
    overrides = load_overrides(paths)
    manifest = C.load_manifest(paths)
    ontology = Ontology.from_dict(manifest.get("ontology") or {})
    _ontology_merge(ontology, manifest, [], overrides)
    from scriptengine.ingest.documents import WikiPage

    examined = 0
    for page in C.load_pages(paths):
        if examined >= args.n:
            break
        if page.page_type in ("unknown", "") or not page.wikitext:
            continue
        control = C.reextract(page, ontology)
        cut = int(len(page.wikitext) * args.frac)
        payload = json.loads(page.to_json())
        truncated = WikiPage.from_dict({**payload, "wikitext": page.wikitext[:cut]})
        result = {}
        try:
            out = C.reextract(truncated, ontology)
            result = {
                "crash": False,
                "type": out.page_type,
                "n_facts": len(out.facts),
                "control_facts": len(control.facts),
                "lead_head": (out.lead or "")[:120].replace("\n", " | "),
            }
        except Exception as exc:  # noqa: BLE001 - the crash IS the finding
            result = {"crash": True, "error": f"{type(exc).__name__}: {exc}"}
        print(json.dumps({"title": page.title, "control_type": control.page_type, **result}))
        examined += 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    ex = sub.add_parser("extract", help="run the active tree's load_extracted over a series")
    ex.add_argument("--series", required=True)
    ex.add_argument("--out", required=True)
    ex.add_argument("--limit", type=int, default=0, help="rate-estimation only")
    ex.add_argument("--values", action="store_true", help="include fact values (gate 5)")
    ex.add_argument("--no-overrides", action="store_true", help="base-tree semantics")
    ex.set_defaults(fn=cmd_extract)

    di = sub.add_parser("diff", help="diff two extract JSONLs")
    di.add_argument("--base", required=True)
    di.add_argument("--new", required=True)
    di.add_argument("--report", required=True)
    di.set_defaults(fn=cmd_diff)

    tr = sub.add_parser("truncation", help="synthetic truncated-fetch test (review 5)")
    tr.add_argument("--series", required=True)
    tr.add_argument("--n", type=int, default=5)
    tr.add_argument("--frac", type=float, default=0.6,
                   help="fraction of wikitext kept before the cut (0.6 = cut at 60%)")
    tr.set_defaults(fn=cmd_truncation)

    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())