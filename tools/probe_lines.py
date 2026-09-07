"""Targeted line probes: does the live /context door serve a given line?

Reuses the span-recall verdicts (HIT / MISS_DOC / MISS_SPAN / TRUNCATED /
ERROR) against a fixed list of lines, e.g. the 3a inexpressible sample.
Hits the running :8000 (CUDA co-location window) over HTTP, so no in-process
models. One line of output per probe; a count summary at the end.

Usage:
  python tools/probe_lines.py reports/comprehension/census_3a_inexpressible.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scriptengine"))

from eval.span_recall import _ask, decite, make_query, served_text  # noqa: E402


def main() -> None:
    path = Path(sys.argv[1])
    series = sys.argv[2] if len(sys.argv) > 2 else "jjk"
    lines = json.loads(path.read_text())

    def expect_title(source: str) -> str:
        # the wiki's own page titles for the sample's source labels
        if source.startswith("Modulo Ch"):
            return "Modulo Chapter " + source.rsplit(" ", 1)[1]
        if source.startswith("Ch "):
            return "Chapter " + source[3:]
        if source.startswith("Ep "):
            return "Episode " + source[3:]
        return source

    counts: dict[str, int] = {}
    misses: list[dict] = []
    for i, item in enumerate(lines, 1):
        sentence = item["sentence"]
        query = make_query(sentence, "verbatim")
        try:
            bundle = _ask(query, series, timeout=120.0)
            text = served_text(bundle)
            returned = [b.get("doc_title") for b in bundle.get("beats", [])
                        if isinstance(b, dict)]
            if sentence in text or decite(sentence) in decite(text):
                verdict = "HIT"
            elif bundle.get("truncated"):
                verdict = "TRUNCATED"
            elif expect_title(item["source"]) not in returned:
                verdict = "MISS_DOC"
            else:
                verdict = "MISS_SPAN"
        except Exception as exc:
            verdict = "ERROR"
            print(f"  {i:2d}/{len(lines)} {item['id']} ERROR {str(exc)[:120]}")
        counts[verdict] = counts.get(verdict, 0) + 1
        if verdict != "HIT":
            rec = {**item, "verdict": verdict}
            misses.append(rec)
            print(f"  {i:2d}/{len(lines)} {item['id']} [{item['class']}] {verdict} "
                  f"({item['source']}) {sentence[:60]}")
    out = path.with_suffix(".probed.json")
    out.write_text(json.dumps({"counts": counts, "misses": misses}, indent=1))
    print(f"\n{json.dumps(counts)}  -> {out}")


if __name__ == "__main__":
    main()