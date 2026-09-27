#!/usr/bin/env python
"""Gate 5 sample selection (MCU set).

From the NEW-parser extract JSONL (with --values), select:
  - up to 40 character-type pages with n_facts > 0 (spread across titles)
  - every stored disambiguation-shaped page ("may refer to" / Disambig template)
and write a hand-grading sheet: for each page, its extracted facts (key=value)
plus the raw wikitext head, so a grader can check fact/infobox fidelity.

Usage:
  python tools/marvel/gate5_pick.py \
      --new reports/marvel/receipts/parse_diff_mcu_new.jsonl \
      --series mcu --n-chars 40 --sheet reports/marvel/receipts/gate5_mcu_sheet.md
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

DISAMBIG = re.compile(r"\{\{(?:disambig|Disambig)|may refer to", re.I)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--new", required=True)
    ap.add_argument("--series", required=True)
    ap.add_argument("--n-chars", type=int, default=40)
    ap.add_argument("--sheet", required=True)
    args = ap.parse_args()

    rows = [json.loads(line) for line in open(args.new, encoding="utf-8")]
    by_title = {r["title"]: r for r in rows}

    chars = [r for r in rows if r["type"] == "character" and r["n_facts"] > 0]
    step = max(1, len(chars) // args.n_chars)
    sample = chars[::step][: args.n_chars]
    disambig = [r for r in rows if re.search(r"disambig", r["title"], re.I)]

    wdir = Path("series") / args.series / "wikitext"

    def slug(title: str) -> str:
        return re.sub(r'[\\/:*?"<>|]', "_", title) + ".json"

    lines = [
        f"# Gate 5 hand-grading sheet — {args.series} (new parser)",
        "",
        f"- character sample: {len(sample)} of {len(chars)} typed-character pages with facts",
        f"- disambiguation pages found in extract: {len(disambig)}",
        "",
    ]

    def emit(header: str, row: dict, note: str = "") -> None:
        path = wdir / slug(row["title"])
        head = ""
        if path.exists():
            try:
                stored = json.loads(path.read_text(encoding="utf-8"))
                head = (stored.get("wikitext") or "")[:600].replace("\n", " | ")
            except Exception as exc:  # noqa: BLE001
                head = f"<unreadable: {exc}>"
        facts = row.get("facts") or [[k, ""] for k in row.get("keys", [])]
        lines.append(f"## {header}: {row['title']}")
        lines.append(
            f"pageid={row['pageid']} type={row['type']} infobox={row.get('infobox') or '-'} "
            f"n_facts={row['n_facts']} {note}"
        )
        if facts:
            lines.append("")
            lines.append("```")
            for key, value in facts[:25]:
                lines.append(f"{key} = {str(value)[:120]}")
            lines.append("```")
        if head:
            lines.append("")
            lines.append(f"wikitext head: `{head[:400]}`")
        lines.append("")

    for row in sample:
        emit("CHARACTER", row)
    for row in disambig:
        # zero-facts assertion: report pass/fail per page
        ok = row["n_facts"] == 0
        emit(
            "DISAMBIGUATION",
            row,
            note=f"-> ZERO-FACTS {'PASS' if ok else 'FAIL (n_facts=%d)' % row['n_facts']}",
        )
    Path(args.sheet).write_text("\n".join(lines), encoding="utf-8")
    n_zero = sum(1 for r in disambig if r["n_facts"] == 0)
    chars_all = [r for r in rows if r["type"] == "character"]
    cur = [r for r in chars_all if "currentalias" in r.get("keys", [])]
    unknown = sum(1 for r in rows if r["type"] in ("", "unknown"))
    print(
        f"gate5 {args.series}: {len(sample)} character pages, "
        f"{len(disambig)} disambig pages ({n_zero} zero-facts) -> {args.sheet}"
    )
    print(
        f"assertions: currentalias on {len(cur)}/{len(chars_all)} character pages; "
        f"type-unknown {unknown}/{len(rows)} (colon-template typing residual)"
    )


if __name__ == "__main__":
    main()