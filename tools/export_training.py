"""Teacher trace + gated store -> a distillation dataset for the event
extractor (plan/JJK_STUDENT_TRAINING.md). Offline: no model, writes nothing
back to the store or the trace.

    python tools/export_training.py --series jjk \
        --trace series/jjk/events_trace_2026-09-29.9.jsonl --out data/train/jjk

One record per model call (window), in the exact shape the teacher was asked:
the system prompt for this wiki's verbs, the user message the extractor sent,
and as the target the teacher's own entries that survived every engine gate.

Why the target is re-derived through the engine and not copied from the
answer: a gate-rejected entry (illegal verb, self-object, a person as a
movement's destination, an unquoted or fanned-out clause, an end the wiki has
no page for) is a teacher error the store already refuses. Removing it teaches
the student not to write it. A verifier "no" is not removed row by row: the
verifier rejects about half of the true rows, and dropping a true row from a
window's target teaches the student to omit events. The verifier instead
grades the whole window (`tier`).

Every entry is classified by replaying the traced answer through
`extract_from_sections` itself with a stub client, so the dataset can never
disagree with the extractor about what a row is.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import random
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest import events as E  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402


class _Replay:
    """`LLMClient`'s surface: answers every call with the traced answer."""

    def __init__(self, answer: str, model: str | None) -> None:
        self.answer = answer
        self.settings = type("S", (), {"llm_model": model})()

    def complete(self, *args: Any, **kwargs: Any) -> str:
        return self.answer


def _entry(row: dict[str, Any]) -> dict[str, Any]:
    # The prompt's own field order: quote first, then who did what.
    return {
        "quote": row["quote"],
        "subject": row["subject_mention"],
        "verb": row["verb"],
        "object": None if row["verb"] in E._SELF_VERBS
        and row["object_mention"] == row["subject_mention"] else row["object_mention"],
    }


def _split_of(page: str, seed: str, dev: float, test: float) -> str:
    # By page, never by row or window: a page's overlapping windows and its
    # repeated events must not straddle train and test.
    h = int(hashlib.sha256(f"{seed}:{page}".encode()).hexdigest()[:8], 16) / 0xFFFFFFFF
    return "test" if h < test else "dev" if h < test + dev else "train"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", required=True)
    ap.add_argument("--trace", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--prompt-version", default=E.PROMPT_VERSION)
    ap.add_argument("--seed", default="jjk-2026-09-29")
    ap.add_argument("--dev", type=float, default=0.05)
    ap.add_argument("--test", type=float, default=0.10)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    trace = [
        json.loads(line) for line in open(args.trace, encoding="utf-8")
        if line.strip()
    ]
    trace = [t for t in trace if t.get("prompt_version") == args.prompt_version]
    db = ROOT / "series" / args.series / "facts.db"
    tally: collections.Counter = collections.Counter()
    by_tier: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    records: dict[str, list[dict[str, Any]]] = {"train": [], "dev": [], "test": []}

    with FactStore(db) as store:
        verbs = E.eventive_verbs(store)
        system = E.system_prompt(verbs)
        known = E.participant_candidates(store)
        place_nodes = E.declared_place_nodes(store)
        default_real = E._wiki_default_reality(store)
        pages = sorted({t["page"] for t in trace})
        realities = E.page_realities(store, pages, default_real)
        linked: dict[str, set[int]] = {}
        for title, node in store.connection.execute(
            "SELECT c.doc_title, cn.node_id FROM chunk_nodes cn"
            " JOIN chunks c ON c.id = cn.chunk_id"
        ):
            linked.setdefault(title, set()).add(int(node))
        sections = {
            int(r["id"]): r for r in store.connection.execute(
                "SELECT id, ordinal, title FROM sections"
            )
        }
        # The verifier's grade of each stored row, by the row's identity.
        verified = {
            (r["doc_title"], r["quote"], r["verb"], r["subject_mention"],
             r["object_mention"]): r["verified"]
            for r in store.connection.execute(
                "SELECT doc_title, quote, verb, subject_mention, object_mention,"
                " verified FROM events WHERE prompt_version = ?",
                (args.prompt_version,),
            )
        }

        for t in trace:
            holder = t["holders"][0]
            if holder["kind"] == "section":
                sec = sections.get(int(holder["id"]))
                if sec is None:
                    tally["skipped_section_gone"] += 1
                    continue
                passage = {"kind": "section", "id": int(sec["id"]),
                           "ordinal": int(sec["ordinal"]), "title": sec["title"],
                           "passage": holder["passage"], "text": t["window"]}
            else:
                passage = {"kind": holder["kind"], "id": holder["id"],
                           "passage": holder["passage"], "title": "",
                           "text": t["window"], "rank": 0.0}
            client = _Replay(t["answer"], t.get("model"))
            found, stats = E.extract_from_sections(
                client, args.series, t["page"], [passage], known,
                realities.get(t["page"]), linked.get(t["page"]), verbs,
                place_nodes,
            )
            proposed = len(E.parse_events_response(t["answer"]))
            target = [_entry(r) for r in found]
            grades = [
                verified.get((t["page"], r["quote"], r["verb"],
                              r["subject_mention"], r["object_mention"]))
                for r in found
            ]
            corrected = proposed - len(found) - stats["dropped"]["dedup"]
            if not target:
                tier = "empty"
            elif all(g == 1 for g in grades):
                tier = "confirmed"
            elif any(g == 0 for g in grades):
                tier = "contested"
            else:
                tier = "unverified"
            split = _split_of(t["page"], args.seed, args.dev, args.test)
            user = E._TEMPLATE.format(series=args.series, page=t["page"],
                                      section=t["section"], passage=t["window"])
            records[split].append({
                "id": hashlib.sha256(f'{t["page"]}\n{t["window"]}'.encode()).hexdigest()[:16],
                "page": t["page"], "section": t["section"], "split": split,
                "tier": tier, "teacher_proposed": proposed,
                "gate_corrected": corrected,
                "dropped": {k: v for k, v in stats["dropped"].items() if v},
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                    {"role": "assistant",
                     "content": json.dumps({"events": target}, ensure_ascii=False)},
                ],
            })
            tally["windows"] += 1
            tally["proposed"] += proposed
            tally["target_entries"] += len(target)
            for k, v in stats["dropped"].items():
                tally[f"dropped_{k}"] += v
            by_tier[split][tier] += 1

    for split, rows in records.items():
        random.Random(args.seed).shuffle(rows)
        with open(out / f"{split}.jsonl", "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    receipt = {
        "series": args.series, "prompt_version": args.prompt_version,
        "trace": args.trace, "seed": args.seed, "tally": dict(tally),
        "splits": {s: {"windows": len(r), "pages": len({x["page"] for x in r}),
                       "tiers": dict(by_tier[s])} for s, r in records.items()},
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(json.dumps(receipt, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
