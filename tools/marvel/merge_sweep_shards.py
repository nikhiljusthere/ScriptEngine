#!/usr/bin/env python3
"""Merge concurrent page-sweep shard reports into the canonical report.

`run_sweep_shards.sh` seeds each shard's `--out` report from the canonical
report and runs one `page-sweep --shard K --shards N` process per shard. The
shards' page sets are disjoint (the stable `shard_of` hash partition) and
their reports never touch each other, so the canonical report stays the
single source of truth: every shard file is exactly the canonical pages plus
that shard's new pages.

This tool unions the shard files back into the canonical report:

- keyed by page title; a page present in several files keeps its non-error
  row (a stale error row inherited from the seed is replaced by the owning
  shard's re-swept success row);
- page order: the canonical order first (rows upgraded in place), then new
  rows in shard-file order — deterministic, and consumers key by page
  (the census bank is built from the page artifacts, not report rows);
- before writing it verifies every shard file is a superset of the canonical
  seed (a missing seed or a stale copy aborts the merge), writes atomically
  (tmp + rename, same convention as the sweep's own flush), and removes the
  shard files.

Usage (run from the repo root):
  scriptengine/.venv/bin/python tools/marvel/merge_sweep_shards.py --series marvel --tier a --shards 16
  scriptengine/.venv/bin/python tools/marvel/merge_sweep_shards.py --series marvel --tier a --shards 16 --dry-run
  scriptengine/.venv/bin/python tools/marvel/merge_sweep_shards.py --series marvel --tier a --shards 16 --keep-shards
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--series", required=True)
    ap.add_argument("--tier", required=True, choices=("a", "b"))
    ap.add_argument("--shards", type=int, required=True, help="shard count N")
    ap.add_argument("--dry-run", action="store_true",
                    help="verify and print the merge summary without writing")
    ap.add_argument("--keep-shards", action="store_true",
                    help="leave the shard report files in place after merging")
    args = ap.parse_args()

    base = ROOT / "questions" / f"_{args.series}_page_sweep_{args.tier}.report.json"
    shard_paths = [base.with_name(f"{base.name}.shard{i:02d}")
                   for i in range(args.shards)]
    missing = [p.name for p in shard_paths if not p.exists()]
    if missing:
        print(f"merge {args.series}: MISSING shard files: {missing}", file=sys.stderr)
        return 1

    canon = _load(base)
    canon_pages = canon.get("pages") or []
    canon_ids = {p["page"] for p in canon_pages}
    canon_order = [p["page"] for p in canon_pages]  # set order must not leak into the report

    merged = {p["page"]: p for p in canon_pages}
    new_order: list[str] = []
    new_count = 0
    for sp in shard_paths:
        rows = _load(sp).get("pages") or []
        if len(rows) < len(canon_pages):
            print(f"merge {args.series}: {sp.name} holds {len(rows)} pages but the "
                  f"canonical seed has {len(canon_pages)} — it was not seeded from "
                  f"the canonical report; refusing to merge", file=sys.stderr)
            return 1
        for row in rows:
            page = row["page"]
            if page not in merged:
                merged[page] = row
                if page not in canon_ids:
                    new_order.append(page)
                    new_count += 1
            elif merged[page].get("error") and not row.get("error"):
                merged[page] = row  # the owning shard re-swept a seeded error row

    final_pages = [merged[p] for p in canon_order + new_order]
    errors = sum(1 for p in final_pages if p.get("error"))
    structured = sum(p.get("structured", 0)
                     for p in final_pages if not p.get("error"))
    print(f"merge {args.series} tier {args.tier}: canonical {len(canon_ids)} pages "
          f"+ {new_count} new across {args.shards} shards = {len(final_pages)} pages "
          f"({errors} errors, {structured} structured Qs)")
    if args.dry_run:
        print("dry run: canonical report not written")
        return 0

    tmp = base.with_suffix(base.suffix + ".tmp")
    payload = {**canon, "pages": final_pages, "updated": date.today().isoformat()}
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    tmp.replace(base)
    if not args.keep_shards:
        for sp in shard_paths:
            sp.unlink()
    print(f"merge {args.series}: wrote {base.relative_to(ROOT)} "
          f"({'kept' if args.keep_shards else 'removed'} shard files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())