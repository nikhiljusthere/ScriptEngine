"""X2.d door census — the council's D1 + D2 (COUNCIL_d6-completion.md).

Two FIXED question sets, run through the same in-process path the :8000
`/context` endpoint uses (`build_context`, explicit door mode — no auto-
route):

  roster    100 enumeration questions, stratified character/technique/
            organization/item, drawn from the wiki's own declared rosters
            (series/jjk/overrides.yaml ~1355 entries; the question is the
            declaration's `name`, so every question is one the wiki itself
            asks).
  narrative 100 chronological questions, stratified characters/arcs:
            60 "what happened to <char>, in order", 9 arc overviews, 31
            "what happened to <char> during the <arc>".

The sets are generated once (deterministic, seeded where a sample is taken)
and frozen into reports/comprehension/census_{roster,narrative}_100.json;
every later run executes the same 200 questions. Regenerate only with
--regen.

Reached (the D1/D2 bar):
  roster    the door returns >=1 member for the enumeration subject
  narrative the door returns >=1 ordered beat
>=99% reached per door; every miss triaged (the result file carries the
miss list; a short member set on a reached question is flagged
`short` for triage, not counted a miss).

Usage:
  CENSUS_DEVICE=cuda python tools/census_doors.py [--regen]
"""
from __future__ import annotations

import argparse
import json
import os
import random
import re
import sys
import time
from pathlib import Path

DEVICE = os.environ.get("CENSUS_DEVICE", "cpu")
os.environ.setdefault("SCRIPTENGINE_DEVICE", DEVICE)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import yaml  # noqa: E402

from scriptengine.config import series_paths          # noqa: E402
from scriptengine.api.context import build_context    # noqa: E402

OUT_DIR = ROOT / "reports" / "comprehension"
ROSTER_SET = OUT_DIR / "census_roster_100.json"
NARRATIVE_SET = OUT_DIR / "census_narrative_100.json"
RESULTS = OUT_DIR / "census_doors_results.jsonl"

# Census data, not engine config: the stratification picks are recorded here
# (and in the frozen set files) so a later run measures the same 200.
MAIN20 = [
    "Yuji Itadori", "Satoru Gojo", "Megumi Fushiguro", "Maki Zenin",
    "Nobara Kugisaki", "Sukuna", "Yuta Okkotsu", "Aoi Todo",
    "Toge Inumaki", "Panda", "Choso", "Kenjaku", "Mahito", "Jogo",
    "Hanami", "Kokichi Muta", "Kinji Hakari", "Toji Fushiguro",
    "Suguru Geto", "Kento Nanami",
]

_TECH = re.compile(r"technique|domain expansion|domain (?:name|ability)|cursed energy|soul technique", re.I)
_ORG = re.compile(r"member|roster|squad|team|game|paint|tournament|force|unit|group|council|school|academy|organization|faction|society|alliance|league", re.I)
_ITEM = re.compile(r"item|tool|weapon|equipment|artifact|object|talisman", re.I)


def _stratum(name: str) -> str:
    if _TECH.search(name):
        return "technique"
    if _ORG.search(name):
        return "organization"
    if _ITEM.search(name):
        return "item"
    return "character"


def _character_subjects(series: str) -> list[str]:
    import sqlite3
    db = sqlite3.connect(series_paths(series).facts_db)
    rows = db.execute(
        "SELECT DISTINCT title FROM documents WHERE page_type='character' ORDER BY title"
    ).fetchall()
    return [r[0] for r in rows]


def _subject_tiers(subjects: list[str]) -> tuple[list[str], list[str], list[str]]:
    main = [s for s in MAIN20 if s in subjects]
    rest = [s for s in subjects if s not in main]
    mid = rest[:20]
    minor = sorted(random.Random(42).sample(rest[20:], 20)) if len(rest) > 20 else sorted(rest[20:])
    return main, mid, minor


def _arc_display(key: str) -> str:
    name = key[:-4] if key.lower().endswith(" arc") else key
    return " ".join(w.capitalize() if w not in ("vs", "the") else w for w in name.split())


def build_roster_set(series: str, out: Path) -> list[dict]:
    d = yaml.safe_load((ROOT / "series" / series / "overrides.yaml").read_text())
    rosters = [r for r in d["rosters"] if r.get("members")]
    by_stratum: dict[str, list[dict]] = {}
    for r in rosters:
        by_stratum.setdefault(_stratum(r["name"]), []).append(r)

    main, mid, minor = _subject_tiers(_character_subjects(series))
    char_pool: list[dict] = []
    for tier, cap in ((main, 35), (mid, 20), (minor, 15)):
        taken = 0
        for r in by_stratum.get("character", []):
            if r.get("subject") in tier and taken < cap:
                char_pool.append(r)
                taken += 1

    def by_size(items: list[dict], n: int) -> list[dict]:
        return sorted(items, key=lambda r: (-len(r["members"]), r["name"]))[:n]

    tech = by_size(by_stratum.get("technique", []), 21)
    orgs = by_size(by_stratum.get("organization", []), 4)
    items = by_size(by_stratum.get("item", []), 5)
    take = char_pool[: 100 - len(tech) - len(orgs) - len(items)]
    if len(take) + len(tech) + len(orgs) + len(items) != 100:
        raise SystemExit(f"strata do not fill 100: char={len(take)} tech={len(tech)} org={len(orgs)} item={len(items)}")

    set_ = []
    for r, stratum in ([(r, "character") for r in take]
                       + [(r, "technique") for r in tech]
                       + [(r, "organization") for r in orgs]
                       + [(r, "item") for r in items]):
        set_.append({"q": r["name"], "mode": "roster", "subject": None,
                     "stratum": stratum, "declared": len(r["members"])})
    out.write_text(json.dumps(set_, indent=1))
    print(f"froze {len(set_)} roster questions -> {out.name}")
    return set_


def _story_arcs(series: str) -> list[str]:
    """The canonical story-axis arcs (key order = timeline order)."""
    from scriptengine.stores.facts import FactStore
    from scriptengine.ingest.timeaxis import story_arc_index
    store = FactStore(series_paths(series).facts_db)
    idx = story_arc_index(store)
    return [k for k, _ in sorted(idx.items(), key=lambda kv: kv[1])]


def build_narrative_set(series: str, out: Path) -> list[dict]:
    subjects = _character_subjects(series)
    main, mid, minor = _subject_tiers(subjects)
    for s in main + mid + minor:
        if s not in subjects:
            raise SystemExit(f"stratification names a page not in the corpus: {s}")

    arcs = _story_arcs(series)
    if not arcs:
        raise SystemExit("no story-axis arcs — cannot stratify")

    set_: list[dict] = []
    for tier in (main, mid, minor):
        for c in tier:
            set_.append({"q": f"What happened to {c}, in order?",
                         "mode": "narrative", "subject": c, "stratum": "character"})
    for arc in arcs:
        set_.append({"q": f"What happened in the {_arc_display(arc)}, in order?",
                     "mode": "narrative", "subject": None, "stratum": "arc"})
    grid = [(c, a) for c in main[:5] for a in arcs][: 100 - len(set_)]
    set_.extend({"q": f"What happened to {c} during the {_arc_display(a)}, in order?",
                 "mode": "narrative", "subject": c, "stratum": "char-arc"}
                for c, a in grid)
    if len(set_) != 100:
        raise SystemExit(f"narrative set is {len(set_)} != 100")
    out.write_text(json.dumps(set_, indent=1))
    print(f"froze {len(set_)} narrative questions -> {out.name}")
    return set_


def run(series: str, roster_set: list[dict], narrative_set: list[dict]) -> None:
    paths = series_paths(series)
    declared = {r["name"]: len(r.get("members", [])) for r in
                yaml.safe_load((ROOT / "series" / series / "overrides.yaml").read_text())["rosters"]}
    t0 = time.time()
    results = []
    for i, item in enumerate(roster_set + narrative_set, 1):
        try:
            bundle = build_context(paths, item["q"], mode=item["mode"],
                                   subject=item.get("subject"))
            if item["mode"] == "roster":
                members = bundle.get("members") or []
                reached = len(members) > 0
                extra = {"retrieved": len(members), "declared": declared.get(item["q"], item.get("declared", 0))}
            else:
                beats = bundle.get("beats") or []
                reached = len(beats) > 0
                extra = {"beats": len(beats)}
            rec = {**item, "reached": reached, **extra, "error": None}
        except Exception as e:  # a red question is a triage item, not a crash
            rec = {**item, "reached": False, "error": f"{type(e).__name__}: {e}"}
        results.append(rec)
        if i % 25 == 0 or not rec["reached"]:
            print(f"  {i:3d}/200 {'OK ' if rec['reached'] else 'MISS'} {item['q'][:70]}")
    RESULTS.write_text("\n".join(json.dumps(r) for r in results) + "\n")
    for name, sel in (("roster", roster_set), ("narrative", narrative_set)):
        rs = [r for r in results if r["mode"] == name]
        hit = sum(1 for r in rs if r["reached"])
        print(f"\n{name}: {hit}/{len(rs)} reached ({100 * hit / len(rs):.1f}%)")
        for r in rs:
            if not r["reached"]:
                print(f"  MISS [{r['stratum']}] {r['q'][:75]}  {r.get('error') or ''}")
            elif r["mode"] == "roster" and r["retrieved"] < r["declared"]:
                print(f"  short [{r['stratum']}] {r['q'][:60]} ({r['retrieved']}/{r['declared']})")
    print(f"\n{time.time() - t0:.0f}s; results -> {RESULTS}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--regen", action="store_true", help="rebuild the frozen sets")
    args = ap.parse_args()

    if args.regen or not ROSTER_SET.exists():
        roster_set = build_roster_set(args.series, ROSTER_SET)
    else:
        roster_set = json.loads(ROSTER_SET.read_text())
    if args.regen or not NARRATIVE_SET.exists():
        narrative_set = build_narrative_set(args.series, NARRATIVE_SET)
    else:
        narrative_set = json.loads(NARRATIVE_SET.read_text())
    run(args.series, roster_set, narrative_set)


if __name__ == "__main__":
    main()