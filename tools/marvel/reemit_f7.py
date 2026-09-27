#!/usr/bin/env python3
"""F7 re-emit: re-extract the stored corpus with the current (F7-patched) parser.

Zero egress. For every stored page it reads the stored `wikitext`, re-runs
extraction with the SAME enriched ontology `load_extracted` builds (manifest
ontology + `discover_infoboxes` vote + overrides, then mutated per-page in
sorted-file order — the exact sequence `index`/`audit` use), diffs the
re-extracted page against the stored file, and writes back ONLY the changed
files (backing up the old bytes first).

Why a full pass rather than a targeted one: `build_page` mutates the shared
ontology as it goes (`learn_field_labels`, `ontology.page_types[title] = ...`),
and subpage typing reads `ontology.page_types.get(parent)`. Re-extracting only
the F7-affected subset would type a candidate subpage differently than
`load_extracted` does when its parent is not itself a candidate (484 MCU +
16 Marvel F7 files are subpages). Processing every file in sorted-file order
keeps the result byte-faithful to what `index` would produce.

Preserved fields (title/url/pageid/revid/wikitext/fetched_at/warnings-as-stored)
round-trip unchanged; only the cleaned values (facts/lead/sections/aliases/
edges/links/citations/page_type/infobox_template) may change. The stored
19-key JSON matches the `WikiPage` dataclass field-for-field, so the
`from_dict` -> `reextract` -> `to_json` round-trip is lossless.

This is the campaign re-emit for the F7 fix (commit 06d39c94): it applies the
unbounded `_QUOTES` + transparent-`conjecture` change to the ~5.3k Marvel /
~250 MCU stored pages whose cleaned values carried a stray `'` or a lost name.

Usage (run from the repo root):
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/reemit_f7.py --series marvel --benchmark 200
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/reemit_f7.py --series marvel --dry-run
  PYTHONPATH=$PWD scriptengine/.venv/bin/python tools/marvel/reemit_f7.py --series marvel
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from scriptengine.config import load_overrides, series_paths  # noqa: E402
from scriptengine.ingest.crawler import load_manifest, reextract  # noqa: E402
from scriptengine.ingest.documents import WikiPage  # noqa: E402
from scriptengine.ingest.ontology import Ontology, discover_infoboxes  # noqa: E402


def _trim(value, limit: int = 160):
    """Compact a value for a receipt sample: scalars as-is, containers truncated."""
    if isinstance(value, str):
        return value if len(value) <= limit else value[:limit] + f"...[{len(value)} chars]"
    if isinstance(value, list):
        kept = value[:4]
        if len(value) > 4:
            kept = kept + [f"...[{len(value)} items]"]
        return [_trim(v, limit // 2) for v in kept]
    if isinstance(value, dict):
        return {k: _trim(v, limit // 2) for k, v in list(value.items())[:6]}
    return value


def build_enriched_ontology(paths, overrides: dict) -> Ontology:
    """Mirror `load_extracted`'s ontology construction, but stream the wikitext
    so the whole corpus never sits in memory at once.

    `discover_infoboxes` is order-independent (a Counter vote over all pages),
    so streaming the (title, wikitext) pairs in sorted-file order is faithful.
    """
    manifest = load_manifest(paths)
    ontology = Ontology.from_dict(manifest.get("ontology") or {})

    def wt_iter():
        for p in sorted(paths.wikitext.glob("*.json")):
            try:
                d = json.loads(p.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, TypeError, ValueError):
                continue
            w = d.get("wikitext") or ""
            if w:
                yield (d.get("title", ""), w)

    discovered = discover_infoboxes(
        manifest.get("wiki", ""), wt_iter(), overrides
    )
    ontology.infobox_types.update(discovered.infobox_types)
    ontology.infobox_votes = discovered.infobox_votes
    ontology.skip_categories |= discovered.skip_categories
    ontology.citation_works = discovered.citation_works
    ontology.item_sections = discovered.item_sections
    if discovered.skip_patterns is not None:
        ontology.skip_patterns = discovered.skip_patterns
    if discovered.alias_fact_keys:
        ontology.alias_fact_keys = discovered.alias_fact_keys
    return ontology


def reemit(
    series: str,
    *,
    dry_run: bool = False,
    benchmark: int = 0,
    receipt_dir: Path | None = None,
) -> dict:
    paths = series_paths(series)
    overrides = load_overrides(paths)
    wt = paths.wikitext
    files = sorted(wt.glob("*.json"))
    total = len(files)
    print(f"[{series}] {total} files; building enriched ontology (streaming vote) ...", flush=True)
    t0 = time.time()
    ontology = build_enriched_ontology(paths, overrides)
    print(f"[{series}] ontology ready in {time.time() - t0:.1f}s", flush=True)

    changed: list[str] = []
    skipped_unreadable = 0
    key_diffs: Counter = Counter()
    sample_diffs: list[dict] = []
    PRESERVED = {"title", "url", "pageid", "revid", "wikitext", "fetched_at",
                 "categories", "templates", "redirects"}
    RE_DERIVED = {"lead", "sections", "facts", "edges", "links", "citations",
                  "aliases", "page_type", "infobox_template", "warnings"}

    def key_set(a: dict, b: dict) -> list[str]:
        keys = set(a) | set(b)
        return [k for k in sorted(keys) if a.get(k) != b.get(k)]

    t1 = time.time()
    last_report = t1
    for i, p in enumerate(files):
        try:
            stored_bytes = p.read_text(encoding="utf-8")
            stored_dict = json.loads(stored_bytes)
        except (json.JSONDecodeError, TypeError, ValueError, OSError):
            skipped_unreadable += 1
            continue
        page = WikiPage.from_dict(stored_dict)
        new_page = reextract(page, ontology)  # mutates `ontology`, in order
        new_dict = json.loads(new_page.to_json())
        if new_dict != stored_dict:
            rel = str(p.relative_to(wt))
            changed.append(rel)
            diffs = key_set(stored_dict, new_dict)
            for k in diffs:
                key_diffs[k] += 1
            if len(sample_diffs) < 12:
                sample_diffs.append({
                    "file": rel,
                    "keys": diffs,
                    "detail": {
                        k: {"stored": _trim(stored_dict.get(k)),
                            "new": _trim(new_dict.get(k))}
                        for k in diffs
                    },
                })
            if not dry_run and receipt_dir is not None:
                backup = receipt_dir / rel
                backup.parent.mkdir(parents=True, exist_ok=True)
                backup.write_text(stored_bytes, encoding="utf-8")
                # Atomic replace: no torn file if the pass is interrupted.
                tmp = p.with_name(p.name + ".tmp")
                tmp.write_text(new_page.to_json(), encoding="utf-8")
                tmp.replace(p)
        if benchmark and i + 1 >= benchmark:
            break
        now = time.time()
        if now - last_report >= 30:
            last_report = now
            rate = (i + 1) / (now - t1)
            eta = (total - i - 1) / rate if rate else 0
            print(
                f"[{series}] ...{i + 1}/{total} ({(i + 1) * 100 // total}%) "
                f"changed={len(changed)} rate={rate:.1f}/s eta={eta / 60:.1f}m",
                flush=True,
            )

    dt = time.time() - t1
    rate = (i + 1) / dt if dt else 0
    est_full = (total / rate) if rate else 0
    preserved_violations = [k for k in key_diffs if k in PRESERVED]
    result = {
        "series": series,
        "dry_run": dry_run,
        "benchmark": benchmark,
        "files": total,
        "reextracted": i + 1 if benchmark else total,
        "changed": len(changed),
        "changed_pct": round(100 * len(changed) / max(i + 1, 1), 3),
        "skipped_unreadable": skipped_unreadable,
        "reextract_seconds": round(dt, 1),
        "est_full_pass_seconds": round(est_full, 1),
        "key_diffs": dict(key_diffs.most_common()),
        "preserved_key_violations": preserved_violations,
        "sample_diffs": sample_diffs,
        "changed_files": changed,
    }
    if receipt_dir is not None and not dry_run:
        result["backup_dir"] = str(receipt_dir)
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", default="marvel", choices=["marvel", "mcu"])
    ap.add_argument("--dry-run", action="store_true",
                    help="re-extract + diff, report the changed set, write nothing")
    ap.add_argument("--benchmark", type=int, default=0, metavar="N",
                    help="re-extract only the first N files and estimate full-pass time")
    ap.add_argument("--receipt-dir", default=None,
                    help="dir to back up changed files into (default: "
                         "reports/marvel/receipts/reemit_f7_<series>_backup)")
    a = ap.parse_args()

    if not (a.dry_run or a.benchmark):
        # Real run always writes a receipt + backup dir.
        default_dir = REPO / "reports" / "marvel" / "receipts" / f"reemit_f7_{a.series}_backup"
        receipt_dir = Path(a.receipt_dir) if a.receipt_dir else default_dir
        receipt_dir.mkdir(parents=True, exist_ok=True)
    else:
        receipt_dir = None

    result = reemit(
        a.series,
        dry_run=a.dry_run,
        benchmark=a.benchmark,
        receipt_dir=receipt_dir,
    )
    # Trim the (potentially large) changed list for the console, keep it in the file.
    console = {k: v for k, v in result.items() if k != "changed_files"}
    print(json.dumps(console, indent=2, ensure_ascii=False))

    if a.benchmark:
        return 0
    stamp = "dryrun" if a.dry_run else "real"
    out = REPO / "reports" / "marvel" / "receipts" / f"reemit_f7_{a.series}_{stamp}_2026-09-26.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {out}")
    if a.dry_run:
        print(f"  changed {result['changed']} files (dry run, nothing written)")
    else:
        print(f"  changed {result['changed']} files; backups in {result['backup_dir']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())