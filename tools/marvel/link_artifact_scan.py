#!/usr/bin/env python3
"""Scan tier-a sweep golds for raw-wikitext / URL link-artifact residue.

The tier-a `page-sweep` golds are closed-scope, verbatim-faithful to the
stored wiki cells (detail rule). A wiki editor occasionally pastes a raw
wikitext link into an infobox cell (a bare `[https://...` YouTube URL, an
un-stripped `[[Target]]` internal link, or a multi-line infobox block) and
the value cleaner preserves it, because a bare `[https://` is not a
`[[...]]`-style link and a `|`-delimited block is not a single cell. Those
fragments then leak into a gold answer `item`/`aliases` value.

This tool walks every `questions/_<series>_page_*.json` artifact (the
per-page sweep outputs, NOT `.coverage.json`/`.verify.json` sidecars) and
flags any `answer[].item` / `answer[].aliases[]` value that carries raw
wikitext/URL residue. It is read-only and series-generic (marvel/mcu); the
MCU full-sweep run (6/32,129 items, 0.02%, 5 pages) is the precedent this
reproduces for marvel.

Usage:
    python tools/marvel/link_artifact_scan.py --series marvel
    python tools/marvel/link_artifact_scan.py --series marvel --out out.jsonl

Exits 0 always (it is a scan, not a gate); the summary line on stdout is the
finding. A non-zero hit count is a RECORD, not a failure (bounded residue,
per the standing note in known_diffs).
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Residue classes, most-specific first. A value is a hit if ANY fires.
CLASSES = {
    "bare_bracket_url": re.compile(r"\[https?://"),      # [https://…  (the documented MCU class)
    "wiki_link": re.compile(r"\[\["),                      # [[Target]] survived cleaning
    "raw_url": re.compile(r"(?<!\[)https?://"),            # a bare URL (no leading bracket)
    "infobox_residue": re.compile(r"(?:^|\n)\s*\|| = "),   # a multi-field infobox block leaked into a cell
}


def page_files(series: str):
    pat = os.path.join(ROOT, "questions", f"_{series}_page_*.json")
    out = []
    for f in sorted(glob.glob(pat)):
        if f.endswith((".coverage.json", ".verify.json")):
            continue
        out.append(f)
    return out


def value_classes(value: str):
    return [name for name, rx in CLASSES.items() if rx.search(value)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", required=True)
    ap.add_argument("--out", default=None, help="write one JSONL line per hit here")
    args = ap.parse_args()

    files = page_files(args.series)
    total_items = 0
    hits = []
    pages = set()
    bad = 0
    for f in files:
        slug = os.path.basename(f)[: -len(".json")]
        try:
            with open(f, encoding="utf-8-sig") as fh:
                d = json.load(fh)
        except Exception as exc:  # noqa: BLE001 - a corrupt artifact is itself a finding
            bad += 1
            print(f"WARN unreadable artifact {slug}: {exc}", file=sys.stderr)
            continue
        for q in d.get("questions", []):
            for a in q.get("answer", []):
                vals = [str(a.get("item", ""))] + [str(x) for x in (a.get("aliases") or [])]
                for val in vals:
                    total_items += 1
                    cls = value_classes(val)
                    if cls:
                        pages.add(slug)
                        hits.append(
                            {
                                "page": slug,
                                "qid": q.get("id"),
                                "note": q.get("note"),
                                "value": val,
                                "classes": cls,
                            }
                        )

    by_class = {name: 0 for name in CLASSES}
    for h in hits:
        for c in h["classes"]:
            by_class[c] += 1

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            for h in hits:
                fh.write(json.dumps(h, ensure_ascii=False) + "\n")
        print(f"wrote {len(hits)} hits -> {args.out}")

    print(
        f"[link-artifact-scan {args.series}] {len(files)} artifacts, "
        f"{total_items} answer items scanned, {bad} unreadable"
    )
    print(f"  HIT items: {len(hits)}  |  distinct page files: {len(pages)}")
    for name in CLASSES:
        print(f"  {name:<18} {by_class[name]}")
    if hits:
        # distinct pages by most-common residue class, for the known_diffs note
        from collections import Counter

        per_page = Counter(h["page"] for h in hits)
        print("  top pages:")
        for p, n in per_page.most_common(12):
            print(f"    {n:>4}  {p}")


if __name__ == "__main__":
    main()