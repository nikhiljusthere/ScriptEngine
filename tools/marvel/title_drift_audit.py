"""Zero-egress drift audit for a stored wiki corpus (F2/F3, GATE A council 2026-09-25).

Computes, with NO network access:
  * F2: on-disk files whose stored `title` spelling is no longer in the
    same-day enumeration (wiki renames) — the 46-title drift list (marvel).
  * F3: filename-collision groups (titles that fold onto one sanitised
    filename) + orphan files (stored title absent from the enumeration).
  * F7: stray-apostrophe quantification in fact values (values that a
    bold/italic strip left a lone `'`, e.g. `a ' by the O*N*E`).

Campaign tooling (untracked, `tools/marvel/`): mirrors
`scriptengine.ingest.crawler.sanitise_filename` locally so this stays outside
the gated import surface (verified-imported-by-nothing rule).

Usage:
  uv run --with curl-cffi python tools/marvel/title_drift_audit.py --series marvel
  uv run --with curl-cffi python tools/marvel/title_drift_audit.py --series mcu
"""

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sanitise_filename(name: str) -> str:
    # mirror of scriptengine/ingest/crawler.py `sanitise_filename` (F1-era,
    # stable since the crawl): replace the filename-hostile set, strip,
    # cap at 150, fall back to "page".
    for char in r'/\:*?"<>|':
        name = name.replace(char, "_")
    return name.strip()[:150] or "page"


# Stray-apostrophe quantification (F7): for each maximal apostrophe run,
# a run of length >= 2 is bold/italic-marker residue; a run of exactly 1 is
# stray when it sits at a word boundary on both sides (e.g. `a ' by the
# O*N*E`), and legitimate in-word (it's, O'Neil) when letters flank it.
def stray_apostrophe_runs(value: str) -> list[str]:
    hits = []
    for m in re.finditer(r"'+", value):
        run = m.group()
        left = value[m.start() - 1] if m.start() > 0 else ""
        right = value[m.end()] if m.end() < len(value) else ""
        if len(run) >= 2 or (not left or left.isspace()) and (not right or right.isspace()):
            hits.append(value[:80])
    return hits


def enumerate_titles(series: str, enum_file: str | None = None) -> set[str]:
    if enum_file:
        # gate-day accounting list (S5 re-gate 2026-09-27): plain titles,
        # one per line — same format as enumerate_pages.py output.
        return {line for line in Path(enum_file).read_text().splitlines() if line.strip()}
    if series == "marvel":
        m = json.loads((ROOT / "series" / "marvel" / "manifest.json").read_text())
        titles = m["all_titles"]
        if len(titles) != m["pages_enumerated"]:
            raise SystemExit(f"manifest all_titles {len(titles)} != pages_enumerated {m['pages_enumerated']}")
        return set(titles)
    fresh = ROOT / "reports" / "marvel" / "receipts" / "mcu_all_pages_fresh_2026-09-25.jsonl"
    # raw titles, one per line (enumerate_pages.py writes plain text, not JSON)
    return {line for line in fresh.read_text().splitlines() if line.strip()}


def scan(series: str, enum: set[str], stray: bool):
    wt = ROOT / "series" / series / "wikitext"
    files = sorted(wt.glob("*.json"))
    stored = {}          # path -> stored title
    stray_hits: dict[str, list[str]] = {}
    stray_total = 0
    for i, p in enumerate(files):
        d = json.loads(p.read_text())
        stored[str(p.relative_to(wt))] = d.get("title", "")
        if stray:
            vals = [f.get("value", "") for f in d.get("facts", [])]
            vals += [d.get("lead", "")] + [a for a in d.get("aliases", [])]
            hits = []
            for v in vals:
                r = stray_apostrophe_runs(v)
                hits.extend(r)
                stray_total += len(r)
            if hits:
                stray_hits[str(p.relative_to(wt))] = hits[:3]
        if (i + 1) % 50000 == 0:
            print(f"  ...{i + 1}/{len(files)}", file=sys.stderr)

    disk_titles = set(stored.values())
    drift = sorted(t for t in disk_titles if t not in enum)          # F2
    by_file: dict[str, list[str]] = defaultdict(list)
    for t in enum:
        by_file[sanitise_filename(t)].append(t)
    collisions = {f: sorted(ts) for f, ts in by_file.items() if len(ts) > 1}
    # which on-disk files do the collision titles actually live in?
    disk_by_fname = defaultdict(list)
    for fname, t in stored.items():
        disk_by_fname[sanitise_filename(t)].append(fname)

    print(f"series={series} files={len(files)} unique-stored-titles={len(disk_titles)} enum={len(enum)}")
    print(f"F2 drift (stored title not in enumeration): {len(drift)}")
    for t in drift:
        where = sorted(f for f, st in stored.items() if st == t)
        print(f"  {t!r}  -> {where}")
    print(f"F3 collision groups in enumeration (titles sharing one filename): {len(collisions)}")
    for f, ts in sorted(collisions.items()):
        ondisk = disk_by_fname.get(f, [])
        print(f"  {f!r} <- {ts}")
        print(f"    on-disk file(s): {ondisk}")
    if stray:
        print(f"F7 stray-apostrophe values: {stray_total} occurrence(s) in {len(stray_hits)} file(s)")
        for f, ex in list(sorted(stray_hits.items()))[:10]:
            for e in ex:
                print(f"  {f}: {e!r}")
    return {"files": len(files), "drift": drift, "collisions": collisions,
            "stray_files": len(stray_hits), "stray_occurrences": stray_total}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="marvel", choices=["marvel", "mcu"])
    ap.add_argument("--no-values", action="store_true", help="skip the F7 value scan")
    ap.add_argument("--enum-file",
                    help="plain-text title list (one per line) to audit against, "
                         "overriding the series default (marvel: manifest, mcu: archived 09-25 list)")
    ap.add_argument("--out", help="receipt path (default: title_drift_audit_{series}_2026-09-25.json)")
    a = ap.parse_args()
    enum = enumerate_titles(a.series, a.enum_file)
    res = scan(a.series, enum, stray=not a.no_values)
    out = (Path(a.out) if a.out
           else ROOT / "reports" / "marvel" / "receipts" / f"title_drift_audit_{a.series}_2026-09-25.json")
    out.write_text(json.dumps(res, indent=2))
    print(f"wrote {out}")