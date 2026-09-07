"""3d: placement-gate false-negative audit (JJK D6 completion campaign).

Re-grounds every cross-page *disagreeing* group against the chapter-in-range
oracle (the B5 spot-check method, COUNCIL_b5-premise.md: a row is
self-consistent when its page's own chapter reference falls inside its
claimed arc's range, the ranges read off the corpus's battle pages) and
re-grounds a seeded sample of *agreeing* groups (a false agreement: the gate
sees one arc, but a row's own chapter contradicts it).

Bar (pre-committed): 0 unflagged unambiguous misplacements.

Model-free, offline. Usage:
  python tools/placement_audit.py [--agree-sample 40]
Writes reports/comprehension/placement_audit_3d.json + prints the summary.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scriptengine"))

from scriptengine.ingest import gate, timeaxis  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402


def arc_ranges(store) -> dict[str, tuple[int, int]]:
    """arc page (lower) -> (min, max) chapter, read off the battle pages."""
    ranges: dict[str, list[int]] = {}
    for chapter, arc in timeaxis.chapter_arc_index(store).items():
        ranges.setdefault(arc.lower(), []).append(chapter)
    return {arc: (min(chs), max(chs)) for arc, chs in ranges.items()}


_CHAPTER_TITLE = re.compile(r"^(?:Modulo )?Chapter (\d+)$", re.IGNORECASE)


def row_chapters(store, page: str) -> list[int]:
    """The chapter numbers a page claims: its `chapters` fact, or -- for a
    chapter page -- its own number. Episode/synopsis/character pages claim
    none: they are no-signal rows (B5's 22% class)."""
    _, chapters = timeaxis._placement_facts(store, [page])[page]  # noqa: SLF001
    nums = timeaxis._chapter_numbers(chapters) if chapters else []  # noqa: SLF001
    if nums:
        return nums
    m = _CHAPTER_TITLE.match(page)
    return [int(m.group(1))] if m else []


def _nearest_arc(ch: int, name_to_pos: dict[str, int],
                 ranges: dict[str, tuple[int, int]],
                 chapter_map: dict[int, str]) -> str | None:
    """The arc a chapter sits in: mapped arcs first, else the range whose edge
    is closest (gap chapters belong to the gap; the battle ranges simply do
    not sample every boundary chapter -- the B5 boundary class)."""
    mapped = chapter_map.get(ch)
    if mapped:
        return mapped.lower()
    best, best_d = None, None
    for arc_l, (lo, hi) in ranges.items():
        d = 0 if lo <= ch <= hi else min(abs(ch - hi), abs(ch - lo))
        if best is None or d < best_d:
            best, best_d = arc_l, d
    return best


def classify_row(
    row, name_to_pos: dict[str, int], pos_to_name: dict[int, str],
    ranges: dict[str, tuple[int, int]],
    chapter_map: dict[int, str], page_chapters: dict[str, list[int]],
) -> str:
    """One row under the oracle: in-range / boundary / out-of-range / no-signal.

    in-range: the page's own chapter falls inside the claimed arc's range.
    boundary: outside, but the nearest arc is within one index step (arc-
              boundary artifact).
    out-of-range: the nearest arc is two or more index steps away -- flagged.
    no-signal: no chapter fact, or the claimed arc is outside the table.
    """
    claimed_i = row["arc_index"]
    if claimed_i is None:
        return "no-signal"
    chs = page_chapters.get(row["arc_key"].strip().lower(), [])
    if not chs:
        return "no-signal"
    claimed_l = pos_to_name.get(claimed_i, "").lower()
    if claimed_l not in ranges:
        return "no-signal"
    lo, hi = ranges[claimed_l]
    if any(lo <= c <= hi for c in chs):
        return "in-range"
    verdict = "in-range"
    for c in chs:
        nearest_l = _nearest_arc(c, name_to_pos, ranges, chapter_map)
        if nearest_l is None or nearest_l == claimed_l:
            continue
        if abs(name_to_pos[nearest_l] - claimed_i) == 1:
            verdict = "boundary"
        else:
            return "out-of-range"
    return verdict


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agree-sample", type=int, default=40)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    from scriptengine.config import series_paths

    paths = series_paths("jjk")
    with FactStore(paths.facts_db) as store:
        report = gate.cross_page_agreement(store)
        name_to_pos = timeaxis.story_arc_index(store)
        pos_to_name = {pos: name for name, pos in name_to_pos.items()}
        ranges = arc_ranges(store)
        chapter_map = {c: a.lower() for c, a in timeaxis.chapter_arc_index(store).items()}

        pages = {r["arc_key"] for d in report["disagreements"] for r in d["rows"]}
        pages |= {r["arc_key"] for a in report["agreements"] for r in a["rows"]}
        page_chapters = {p.lower(): row_chapters(store, p) for p in {p.strip() for p in pages}}

        # --- the disagreeing set, re-grounded ---
        disagree_classes = Counter()
        flagged = []
        for d in report["disagreements"]:
            verdicts = [
                classify_row(r, name_to_pos, pos_to_name, ranges, chapter_map, page_chapters)
                for r in d["rows"]
            ]
            # Rows the oracle cannot judge (no chapter claim) contribute
            # nothing; a group is no-signal only when none of its rows can be
            # judged.  Among the judged rows: a flagged row poisons the
            # group, a boundary row keeps it a boundary artifact, only
            # all-in-range groups are repeat-encounters (B5's 56%).
            judged = [v for v in verdicts if v != "no-signal"]
            if not judged:
                cls = "no-signal"
            elif "out-of-range" in judged:
                cls = "out-of-range"
                flagged.append(
                    {**d, "flagged_rows": [
                        {"arc_key": r["arc_key"], "arc": r["arc"], "direction": r["direction"]}
                        for r, v in zip(d["rows"], verdicts) if v == "out-of-range"
                    ]}
                )
            elif "boundary" in judged:
                cls = "boundary"
            else:
                cls = "repeat-encounter"
            disagree_classes[cls] += 1

        # --- the agreeing set: seeded sample, false-agreement check ---
        rng = random.Random(args.seed)
        sample = rng.sample(
            report["agreements"], min(args.agree_sample, len(report["agreements"]))
        )
        false_agreements = []
        for a in sample:
            for r in a["rows"]:
                if classify_row(r, name_to_pos, pos_to_name, ranges, chapter_map, page_chapters) == "out-of-range":
                    false_agreements.append(
                        {"verb": a["verb"], "participants": a["participants"],
                         "arc": a["arc"], "page": r["arc_key"],
                         "direction": r["direction"], "quote": r["quote"]}
                    )

    out = {
        "stats": report["stats"],
        "arc_ranges": {k: list(v) for k, v in sorted(ranges.items())},
        "disagree_classes": dict(disagree_classes),
        "flagged_out_of_range": flagged,
        "agree_sample": len(sample),
        "false_agreements": false_agreements,
    }
    dest = ROOT / "reports/comprehension/placement_audit_3d.json"
    dest.write_text(json.dumps(out, indent=1))
    print(f"disagreeing {report['stats']['disagreeing']} -> {dict(disagree_classes)}")
    print(f"flagged out-of-range rows: {len(flagged)}")
    for f in flagged:
        for row in f["flagged_rows"]:
            print(f"  {f['verb']} {f['participants']} filed {row['arc']} on page {row['arc_key']}")
    print(f"agreeing sample {out['agree_sample']}: false agreements {len(false_agreements)}")
    for fa in false_agreements:
        print(f"  {fa['verb']} {fa['participants']} arc {fa['arc']} page {fa['page']}")
    print(f"\nbar: 0 unflagged unambiguous misplacements -> "
          f"{'MET' if not flagged and not false_agreements else 'NOT MET'} -> {dest}")


if __name__ == "__main__":
    main()