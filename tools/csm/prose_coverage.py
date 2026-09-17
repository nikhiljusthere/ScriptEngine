"""Prose-coverage leg (council #32 D2): one machine question per in-scope
page that page-gen left with no structured question, so the campaign batches
close without hand question formation.

Gold = the page's first chunked first-sentence (lead first, then sections in
page order) -- verbatim, G3-checked with the same `chunked` probe the
generator uses. Question templates are per-archetype, not per-page:
`What is the history of X?` for the `/History` subpages, `What is X?`
elsewhere. Generated rows carry the `page-gen:prose-coverage` marker and are
merged through `write_batch`, so a later sweep reconciles them instead of
clobbering them.

Usage:
    python tools/csm/prose_coverage.py          # dry run (print only)
    python tools/csm/prose_coverage.py --write  # merge into the batches
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from scriptengine.config import Settings, load_overrides, series_paths  # noqa: E402
from scriptengine.eval import questions as Q  # noqa: E402
from scriptengine.eval.page_gen import (  # noqa: E402
    PageGenOutput, chunked, route_safe, slug_of, wiki_base, write_batch)
from scriptengine.stores.facts import FactStore  # noqa: E402

SUFFIX = "/History"
MIN_GOLD = 10  # a first-sentence shorter than this is a fragment, not a gold


def first_sentence(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", text, maxsplit=1)
    return parts[0].strip()


def gold_for(store: FactStore, title: str) -> tuple[str, str]:
    """The first chunked first-sentence of the page: `(sentence, path)` or
    `("", "")` when nothing is chunked (the caller retires with a reason)."""
    candidates = [("lead", store.document_lead(title))]
    for row in store.document_sections(title):
        candidates.append((row["breadcrumb"] or row["title"] or "", row["text"] or ""))
    for path, text in candidates:
        sentence = first_sentence(text)
        if len(sentence) >= MIN_GOLD and chunked(store, sentence):
            return sentence, path
    return "", ""


def question_for(title: str) -> str:
    if title.endswith(SUFFIX):
        return f"What is the history of {title[:-len(SUFFIX)]}?"
    return f"What is {title}?"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="merge into the batches (default: dry run)")
    args = parser.parse_args()
    settings = Settings()
    paths = series_paths("csm", settings)
    overrides = load_overrides(paths)
    store = FactStore(paths.facts_db)

    report = json.loads(
        (settings.questions_root / "_csm_page_sweep_a.report.json")
        .read_text(encoding="utf-8"))
    pages = [p["page"] for p in report["pages"]
             if not p.get("error") and p.get("structured", 0) == 0]
    if not pages:
        print("no zero-structured pages in the sweep report; nothing to do")
        return 0

    added = retired = 0
    for title in pages:
        question = question_for(title)
        violations = route_safe(question, "fact")
        if violations:
            raise SystemExit(f"route-trap in {question!r}: {violations}")
        sentence, path = gold_for(store, title)
        slug = slug_of(title)
        base = f"_{paths.name}_page_{slug}"
        batch_path = settings.questions_root / f"{base}.json"
        out = PageGenOutput()
        if sentence:
            out.questions.append({
                "id": "",
                "kind": "fact",
                "question": question,
                "subject": title,
                "tier": "wiki",
                "expect_mode": "qa",
                "scope": "closed",
                "answer": [{"item": sentence, "aliases": []}],
                "sources": [f"{wiki_base(paths, title)}/wiki/{title.replace(' ', '_')}"],
                "verified": "2026-09-17",
                "note": f"page-gen:prose-coverage:{path}",
            })
            added += 1
            print(f"{title}: + {question!r} (gold {len(sentence)} chars, {path})")
        else:
            out.retires.append({
                "id": "",
                "item": "",
                "question": question,
                "reason": "no chunked first-sentence on the page (G3)",
                "note": f"page-gen:prose-coverage:{path or 'lead'}",
                "retired": True,
            })
            retired += 1
            print(f"{title}: RETIRED -- no chunked first-sentence")
        if args.write:
            existing = (json.loads(batch_path.read_text(encoding="utf-8-sig"))
                        if batch_path.exists() else {})
            write_batch(batch_path, paths.name, slug,
                        wiki_base(paths, title), out,
                        existing=existing)
            Q.validate([Q.load_file(batch_path)])
            batch = json.loads(batch_path.read_text(encoding="utf-8-sig"))
            print(f"  batch {base}.json: {len(batch.get('questions', []))} questions")
    print(f"{added} questions added, {retired} retired, {len(pages)} pages; "
          f"{'written' if args.write else 'dry run -- rerun with --write'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())