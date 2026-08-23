"""Score the online-canon question bank against a running server.

The bank lives in `questions/<series>.json`, one file per series, with the URL
an answer was researched from recorded beside the answer. This asks the live
server those questions and computes the number: for each, how many canon items
came back (recall) and how many returned members are canon at all (precision).

A canon item counts as found only when a returned member matches it or one of
its aliases after normalisation -- substring matching is deliberately not used,
because "Super Saiyan" is inside "Super Saiyan 2" and would score a miss as a
hit.

The gold used to sit in this file as a Python literal with its provenance in
`#` comments. It moved so that where an answer came from is data a test can
refuse rather than prose a reader has to notice -- the previous version sourced
one whole question to a powerscaling wiki.
"""

import json
import re
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

# Runnable both as `python -m scriptengine.cli canon-run` (package context) and
# as a bare `python scriptengine/eval/canon_gold.py`, where there is no package
# for an import to resolve against. Inserting the resolved repo root rather
# than "." also means it does not matter what directory it was invoked from.
if __package__ in (None, ""):  # pragma: no cover - only on the script path
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from scriptengine.eval import questions as _questions  # noqa: E402

BASE = "http://127.0.0.1:8000"

# Loaded at import, which is deliberate: `diagnose_misses.py` imports `GOLD`,
# and a malformed bank must stop a run rather than quietly score fewer
# questions and let the smaller number read as an improvement.
_BANKS = _questions.load_all()

# Set questions only, in the `(series, query, [(item, [aliases])])` shape this
# module has always exported. `diagnose_misses.py` unpacks exactly that, so it
# is a compatibility contract rather than a convenience.
GOLD = _questions.as_gold(_questions.sets(_BANKS))

# Questions whose gold is a curated core list rather than the complete set the
# wiki keeps. Precision is meaningless on these and is not aggregated over
# them: `Every technique Goku uses` names eight, and the Dragon Ball wiki
# really does record 194 techniques with Goku as a user, so a correct answer
# scores about 4% precision. Recall still counts.
RECALL_ONLY = _questions.recall_only(_questions.sets(_BANKS))

# Fact questions score against the text of the bundle rather than its member
# list, so they are kept out of GOLD: bucketing a fact answer against the
# abilities table, which is what `diagnose_misses` does with GOLD, would be
# meaningless.
FACTS = _questions.facts(_BANKS)


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower().replace("&", "and")
    # \w, not [a-z0-9]: a kanji gold (JJK's `虎杖悠仁`) must survive the fold.
    # The ASCII class erased CJK on both sides, so every kanji question was
    # unanswerable by construction (2026-08-24 campaign).
    text = re.sub(r"[^\w%]+", " ", text)
    # A plural is not a different technique. The engine returned `Machine Gun
    # Blow` for the wiki's `Machinegun Blows` and was scored a miss for it.
    # Folded on both sides, so it can only ever merge a name with its own
    # plural -- this is not substring matching, which stays deliberately out:
    # `Super Saiyan` must not match `Super Saiyan 2`. Four-letter words and up,
    # so `gas`, `ren` and `nen` survive intact.
    #
    # Verb endings are folded too, for the same both-sides reason: the golds
    # say `smashed` while chunked text carries the truncated inflection
    # `smashe`, and the Deep Sea King batch had eighteen questions re-golded
    # to sub-phrases because of it. Drop a trailing `ed` first (`smashed`
    # becomes `smashe`, meeting the chunk's form), then the plural fold above
    # handles the rest. Same four-letter guard: `red`, `bed` and `wed`
    # survive, as do `gas`-shaped words. A further fold of the trailing `e`
    # (`smashe` -> `smash`) was tried and reverted: it merges `Normal Punch`
    # with the `normal punches` alias of `Consecutive Normal Punches`, which
    # breaks the bank's distinctness invariant (opm-set-01). Irregular forms
    # (`blew`/`blows`) and `-ing` (`rip`/`ripping`) are beyond any suffix
    # fold and stay gold rules.
    text = re.sub(r"\b(\w{4,})ed\b", r"\1", text)
    text = re.sub(r"\b(\w{3,})s\b", r"\1", text)
    return " ".join(text.split())


def ask(series: str, query: str) -> dict:
    payload = json.dumps({"series": series, "query": query, "mode": "auto",
                          "token_budget": 60000}).encode()
    request = urllib.request.Request(
        f"{BASE}/context", data=payload,
        headers={"Content-Type": "application/json"})
    start = time.time()
    with urllib.request.urlopen(request, timeout=300) as response:
        body = json.loads(response.read())
    body["_seconds"] = round(time.time() - start, 2)
    return body


def _members(body: dict) -> list[str]:
    return [m if isinstance(m, str) else (m.get("name") or m.get("title") or "")
            for m in (body.get("members") or [])]


def haystack(body: dict) -> str:
    """Everything in a bundle a caller could read an answer out of, folded.

    A fact question cannot be scored against the member list -- the engine
    answers "who killed Ace" with passages, not a roster -- so this flattens
    every field the bundle carries text in. Normalised once here so the
    per-item check below compares like with like.
    """
    parts: list[str] = [body.get("context") or ""]
    for beat in body.get("beats") or []:
        parts += [beat.get("title") or "", beat.get("text") or ""]
        parts += list(beat.get("participants") or [])
    for passage in body.get("passages") or []:
        parts += [passage.get("doc_title") or passage.get("title") or "",
                  passage.get("text") or ""]
    for fact in body.get("facts") or []:
        parts.append(f"{fact.get('entity', '')} {fact.get('label', '')} "
                     f"{fact.get('value', '')}")
    for rel in body.get("relations") or []:
        parts.append(f"{rel.get('source', '')} {rel.get('relation', '')} "
                     f"{rel.get('target', '')} {rel.get('era', '')} "
                     f"{rel.get('quote', '')}")
    parts += _members(body)
    return norm(" ".join(p for p in parts if p))


def present(key: str, folded: str) -> bool:
    """Word-boundary containment, not `in`.

    Plain containment lets `Gon` match inside `Gonta` and `En` inside almost
    anything, which would inflate every fact score into meaninglessness. The
    haystack is already normalised to lowercase alphanumerics and spaces, so a
    boundary is any non-alphanumeric or the end of the string.
    """
    if not key:
        return False
    return re.search(rf"(?<![a-z0-9]){re.escape(key)}(?![a-z0-9])",
                     folded) is not None


def score_sets(gold: list | None = None) -> dict:
    """Recall and precision per set question, against a running server."""
    rows, detail = [], []
    for series, query, canon in (gold if gold is not None else GOLD):
        body = ask(series, query)
        members = _members(body)
        confidence = body.get("confidence") or "-"
        chosen = body.get("basis") or "-"
        available = body.get("members_available", len(members))
        seen = {norm(m) for m in members}

        found, missing, matched_members = [], [], set()
        for item, aliases in canon:
            keys = [norm(item)] + [norm(a) for a in aliases]
            hit = next((k for k in keys if k in seen), None)
            if hit:
                found.append(item)
                matched_members.add(hit)
            else:
                missing.append(item)

        recall = len(found) / len(canon) if canon else 0.0
        precision = len(matched_members) / len(members) if members else 0.0
        # Did the question come back *right* -- every canon item and nothing
        # else? Recall and precision each hide the other's failure. The bank
        # reads 95.4% recall at 63.1% precision while only 38% of closed sets
        # are actually correct, and 40% of them have perfect recall and are
        # still wrong because of what came back beside the answer.
        #
        # Unlike precision this cannot be improved by returning less: dropping
        # a canon item fails it exactly as hard as keeping an intruder. That is
        # the property that makes it the number to drive.
        #
        # Meaningless on `scope: core`, where the gold is a curated subset and
        # returning more is correct, so those are flagged by `recall_only` and
        # excluded from the aggregate, exactly as precision already is.
        exact = len(found) == len(canon) and len(members) == len(canon)
        rows.append({
            "series": series, "query": query, "set": chosen,
            "confidence": confidence, "returned": len(members),
            "available": available,
            "canon": len(canon), "found": len(found),
            "recall": round(recall, 3), "precision": round(precision, 3),
            "exact": exact,
            "recall_only": query in RECALL_ONLY,
        })
        detail.append({
            "query": query, "found": found, "missing": missing,
            "members": members,
        })
        print(f"{recall:5.0%} recall  {precision:5.0%} prec  "
              f"{len(found)}/{len(canon):<3} of canon  "
              f"n={len(members):<4} {confidence:9} {query[:46]}")
    return {"rows": rows, "detail": detail}


def score_facts(questions: list | None = None) -> list[dict]:
    """Whether the correct answer is present in what was served.

    Deliberately not "did the engine answer correctly": this engine serves
    context for a writer, not an answer sentence. Presence in the bundle is
    the strongest claim the measurement supports, and the report must word it
    that way.
    """
    out = []
    for q in (questions if questions is not None else FACTS):
        body = ask(q.series, q.question)
        folded = haystack(body)

        found, missing = [], []
        for item in q.scored_items():
            keys = [norm(item.item)] + [norm(a) for a in item.aliases]
            (found if any(present(k, folded) for k in keys)
             else missing).append(item.item)

        passed = bool(found) if q.accept == "any" else not missing
        # A named distractor present while the answer is absent is the fact
        # equivalent of "confident and wrong" -- the writer is being handed
        # something plausible and incorrect.
        intruders = [a for a in q.absent if present(norm(a), folded)]

        out.append({
            "series": q.series, "query": q.question, "id": q.id,
            "subject": q.subject, "accept": q.accept,
            "expected": [i.item for i in q.scored_items()],
            "found": found, "missing": missing, "intruders": intruders,
            "passed": passed, "confidence": body.get("confidence") or "-",
            "routed": (body.get("routed") or {}).get("mode", "-"),
        })
        print(f"{'  ok  ' if passed else ' MISS '}  "
              f"{'/'.join(found) or '-':38.38} {q.question[:46]}")
    return out


def summarise(rows: list[dict], facts: list[dict] | None = None) -> dict:
    facts = facts or []
    exact_wrong = [r for r in rows
                   if r["confidence"] in {"exact", "declared"} and r["recall"] < 0.5]
    total_found = sum(r["found"] for r in rows)
    total_canon = sum(r["canon"] for r in rows)
    total_returned = sum(r["returned"] for r in rows)
    # Precision is aggregated only over the questions whose gold is a complete
    # set. Including the open-ended ones measures the wiki's breadth, not the
    # engine's aim.
    scored = [r for r in rows if not r["recall_only"]]
    scored_found = sum(r["found"] for r in scored)
    scored_returned = sum(r["returned"] for r in scored)
    # How many questions came back *right*. Aggregated over the same subset
    # precision uses, and for the same reason: a `scope: core` gold is a
    # curated subset the engine is correct to exceed.
    #
    # This is the number to drive, because the other two can both look healthy
    # while it does not move. Measured 2026-08-16: 95.4% recall at 63.1%
    # precision, and 54 of 142 questions right -- with 57 more at *perfect*
    # recall and still wrong, purely from what came back beside the answer.
    exact_right = sum(1 for r in scored if r["exact"])
    return {
        "questions": len(rows),
        "canon_found": total_found,
        "canon_total": total_canon,
        "canon_recall": round(total_found / total_canon, 4) if total_canon else 0.0,
        "members_returned": total_returned,
        "exact_answers": exact_right,
        "exact_of": len(scored),
        "exact_rate": round(exact_right / len(scored), 4) if scored else 0.0,
        "precision_closed": round(scored_found / scored_returned, 4) if scored_returned else 0.0,
        "precision_over": f"{len(scored)}/{len(rows)}",
        "at_recall_zero": sum(1 for r in rows if r["found"] == 0),
        "at_recall_80": sum(1 for r in rows if r["recall"] >= 0.8),
        "confident_and_wrong": [r["query"] for r in exact_wrong],
        "fact_questions": len(facts),
        "fact_present": sum(1 for f in facts if f["passed"]),
    }


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        # Windows stdout defaults to cp1252 and half these wikis romanise with
        # macrons; an unrenderable title must not be able to kill a 40-minute
        # run at the print statement.
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    scores = score_sets()
    facts = score_facts() if FACTS else []
    summary = summarise(scores["rows"], facts)

    print("\n" + "=" * 78)
    print(f"answered exactly right: {summary['exact_answers']}/{summary['exact_of']} "
          f"({summary['exact_rate']:.1%})")
    print(f"canon items recovered : {summary['canon_found']}/{summary['canon_total']} "
          f"({summary['canon_recall']:.1%})")
    print(f"members returned      : {summary['members_returned']}, of which "
          f"{summary['canon_found']} are canon")
    print(f"precision (closed sets): {summary['precision_closed']:.1%} over "
          f"{summary['precision_over']} questions")
    print(f"questions at recall=0 : {summary['at_recall_zero']}/{summary['questions']}")
    print(f"questions at recall>=0.8: {summary['at_recall_80']}/{summary['questions']}")
    print(f"confident and wrong   : {len(summary['confident_and_wrong'])} "
          f"(confidence exact/declared, recall < 50%)")
    for query in summary["confident_and_wrong"]:
        print(f"    {query}")
    if facts:
        print(f"fact answers present  : {summary['fact_present']}/"
              f"{summary['fact_questions']}")

    out = sys.argv[1] if len(sys.argv) > 1 else "canon_scores.json"
    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"rows": scores["rows"], "detail": scores["detail"],
                   "facts": facts, "summary": summary}, handle, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
