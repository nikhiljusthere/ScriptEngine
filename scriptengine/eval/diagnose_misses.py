"""Say why each canon item the engine missed was missed.

A recall number tells you how many items did not come back. It does not tell
you whether the fix is a crawl, a prompt, or a retriever -- and those are three
different jobs. This reads `canon_scores*.json` and puts every miss in exactly
one bucket, each assigned from a lookup rather than from reading the answer:

  corpus gap      the name is nowhere in this wiki's crawl -- no page, no
                  section heading, no sentence. Nothing downstream can recover
                  it; the fix is a crawl or an `overrides.yaml` declaration.
  extraction gap  the prose names it and the `abilities` table does not. The
                  model read the passage and did not return this. Fix is the
                  extraction pass.
  retrieval gap   it is stored -- as a page, a section or an extracted row --
                  and the query still did not return it. Fix is the retriever.
  gold error      the canon list is wrong. Never assigned automatically; a
                  human writes the name into GOLD_ERRORS below with a reason.

Run against a scores file written by `canon_gold.py`:

    python scriptengine/eval/diagnose_misses.py "scripts output/canon_scores_after.json"
"""

import json
import sys
from collections import Counter

sys.path.insert(0, ".")

from scriptengine.config import series_paths, load_overrides  # noqa: E402
from scriptengine.eval.canon_gold import GOLD, norm  # noqa: E402
from scriptengine.ingest.abilities import passages  # noqa: E402
from scriptengine.retrieve import roster  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

# Items a human has checked and found to be wrong in the gold set itself.
# Keyed by "<question> :: <item>". Kept here rather than deleted from GOLD so
# the reason survives and the item is not silently re-added by a later pass.
GOLD_ERRORS: dict[str, str] = {}

# Whose ability prose each question is about.
#
# Stated rather than parsed out of the question. The distinction that matters
# is between "this name appears somewhere on this wiki" and "this name appears
# in the passages the extraction pass actually read", and only the second is
# evidence about extraction. Searching the whole wiki credited `Tatsumaki` to
# a Sanji page and Killua's `Lightning Palm` to `Bomber`.
SUBJECT = {
    "Every form of Goku": "Goku",
    "Every form of Vegeta": "Vegeta",
    "Every transformation of Frieza": "Frieza",
    "Every technique Goku uses": "Goku",
    "Every form of Gohan": "Gohan",
    "Every form of Cell": "Cell",
    "Every form of Majin Buu": "Majin Buu",
    "Every form of Trunks": "Future Trunks",
    "Every form of Luffy": "Monkey D. Luffy",
    "Every Gear of Luffy": "Monkey D. Luffy",
    "Every technique of Zoro": "Roronoa Zoro",
    "Every sword style of Zoro": "Roronoa Zoro",
    "Every technique of Sanji": "Sanji",
    "Every Saitama technique": "Saitama",
    "Every technique of Genos": "Genos",
    "Every technique of Garou": "Garou",
    "Every technique of Speed-o'-Sound Sonic": "Speed-o'-Sound Sonic",
    "How many 1v1 battles did Yuji Itadori have with named characters": "Yuji Itadori",
    "Every cursed technique of Sukuna": "Sukuna",
    "Every cursed technique of Satoru Gojo": "Satoru Gojo",
    "Every shikigami of Megumi Fushiguro": "Megumi Fushiguro",
    "Every cursed technique of Yuta Okkotsu": "Yuta Okkotsu",
    "Every form of Ichigo Kurosaki": "Ichigo Kurosaki",
    "Every technique of Ichigo Kurosaki": "Ichigo Kurosaki",
    "Every technique of Byakuya Kuchiki": "Byakuya Kuchiki",
    "Every form of Ulquiorra Cifer": "Ulquiorra Cifer",
    "Every Nen ability of Killua": "Killua Zoldyck",
    "Every Nen ability of Kurapika": "Kurapika",
    "Every Nen ability of Gon": "Gon Freecss",
    "Every Nen ability of Meruem": "Meruem",
    "Every Nen ability of Chrollo": "Chrollo Lucilfer",
    "Every Nen ability of Hisoka": "Hisoka Morow",
    "Every form of Denji": "Denji",
    "Every ability of Power": "Power",
    "Every devil contract of Aki Hayakawa": "Aki Hayakawa",
    "Every armor of Guts": "Guts",
    "Every weapon of Guts": "Guts",
}


def _series_of(question: str) -> str:
    for series, query, _ in GOLD:
        if query == question:
            return series
    return ""


def _canon_of(question: str) -> list[tuple[str, list[str]]]:
    for _, query, canon in GOLD:
        if query == question:
            return canon
    return []


def _keys(item: str, aliases: list[str]) -> list[str]:
    return [norm(item)] + [norm(a) for a in aliases]


def _has_page(store: FactStore, keys: list[str]) -> str:
    for key in keys:
        row = store.node_by_name(key)
        if row is not None:
            return key
    return ""


def _in_abilities(store: FactStore, keys: list[str]) -> str:
    rows = store.connection.execute("SELECT DISTINCT name FROM abilities").fetchall()
    stored = {norm(row["name"]): row["name"] for row in rows}
    for key in keys:
        if key in stored:
            return stored[key]
    return ""


def _in_own_prose(passages: list[tuple[str, str]], raw: list[str]) -> str:
    """Whether the character's own ability passages name this.

    These are the exact passages `cli abilities` fed the model, so a hit here
    means the model saw the name and did not return it — which is what makes
    this an extraction gap rather than a corpus one.
    """
    for section, text in passages:
        haystack = norm(f"{section} {text}")
        for name in raw:
            if name and norm(name) in haystack:
                return section or "lead"
    return ""


def _anywhere(store: FactStore, raw: list[str]) -> str:
    """Whether the name occurs anywhere on this wiki at all.

    Only ever used to separate "this wiki has never heard of it" from "it is
    here, just not on the page this question is about".
    """
    for name in raw:
        if not name:
            continue
        row = store.connection.execute(
            "SELECT d.title FROM chunks c JOIN documents d ON d.id = c.document_id"
            " WHERE c.text LIKE ? COLLATE NOCASE LIMIT 1",
            (f"%{name}%",),
        ).fetchone()
        if row is not None:
            return row["title"]
    return ""


def _own_headings(store: FactStore, character: str) -> list[str]:
    """The section headings on the character's own page, and only those.

    Searching every breadcrumb on the wiki credited Denji's `Chainsaw Devil`
    to `List of Known Devils / Devils erased by the Chainsaw Devil`, which is
    a heading on another page entirely. A heading is evidence about this
    question only when it is on this character's article.
    """
    if not character:
        return []
    try:
        rows = store.sections_of(character)
    except Exception:  # noqa: BLE001 - no page is not a crash
        return []
    return [str(row["breadcrumb"] or "") for row in rows]


def _in_headings(headings: list[str], raw: list[str]) -> str:
    for crumb in headings:
        folded = norm(crumb)
        for name in raw:
            if name and norm(name) in folded:
                return crumb
    return ""


def diagnose(scores_path: str) -> None:
    with open(scores_path, encoding="utf-8") as handle:
        scores = json.load(handle)

    stores: dict[str, FactStore] = {}
    overrides_by_series: dict[str, dict] = {}
    buckets: Counter = Counter()
    lines: list[dict] = []

    for entry in scores["detail"]:
        question = entry["query"]
        missing = entry.get("missing") or []
        if not missing:
            continue
        series = _series_of(question)
        if not series:
            continue
        if series not in stores:
            paths = series_paths(series)
            stores[series] = FactStore(paths.facts_db)
            overrides_by_series[series] = load_overrides(paths)
        store = stores[series]
        canon = dict((item, al) for item, al in _canon_of(question))

        character = SUBJECT.get(question, "")
        try:
            own = passages(store, character, overrides_by_series[series]) if character else []
        except Exception:  # noqa: BLE001 - a missing page is not a crash
            own = []
        stored_names = {
            norm(row["name"])
            for row in store.abilities_of(character)
        } if character else set()
        # The edges the wiki itself wrote: `X -user-> Y`. This is what the
        # ownership path reads, and the difference between "the retriever
        # missed it" and "the wiki never linked it".
        try:
            owned_names = {
                norm(row["name"] if "name" in row.keys() else row[0])
                for row in store.owned_by(character, roster._BELONGS_RELATIONS)
            } if character else set()
        except Exception:  # noqa: BLE001 - a character with no edges is normal
            owned_names = set()
        own_headings = _own_headings(store, character)

        for item in missing:
            gold_key = f"{question} :: {item}"
            if gold_key in GOLD_ERRORS:
                bucket, evidence = "gold error", GOLD_ERRORS[gold_key]
            else:
                # Raw spellings for the store lookups, which index real
                # titles; normalised keys only where this file does its own
                # comparing.
                raw = [item] + list(canon.get(item, []))
                keys = _keys(item, canon.get(item, []))
                page = _has_page(store, raw)
                stored = _in_abilities(store, keys)
                heading = _in_headings(own_headings, raw)
                own_prose = _in_own_prose(own, raw)
                mine = bool(stored_names & set(keys))
                owned = bool(owned_names & set(keys))

                # Reachable from this character, and still not returned: the
                # retriever had every chance. `owned` is an edge the wiki
                # wrote, `mine` a row extraction stored, `heading` a section
                # on the character's own page.
                if owned or mine or heading:
                    where = (
                        f"a {character!r} ownership edge" if owned
                        else f"an extracted row on {character!r}" if mine
                        else f"heading {heading!r}"
                    )
                    bucket, evidence = "retrieval gap", f"reachable as {where}"
                elif page:
                    # The page exists and nothing connects it to this
                    # character -- no users field, no heading, no sentence in
                    # their prose. Retrieval cannot invent the link, and the
                    # fix is the wiki's data or an overrides declaration, not
                    # the retriever. `Shunpo` is every Soul Reaper's, and the
                    # page does not name Ichigo.
                    bucket = "unlinked page"
                    evidence = f"page {page!r} exists, nothing ties it to {character!r}"
                elif own_prose:
                    bucket = "extraction gap"
                    evidence = f"named under {own_prose!r} on {character!r}, not extracted"
                elif stored:
                    bucket = "retrieval gap"
                    evidence = f"extracted, but on another character ({stored!r})"
                else:
                    elsewhere = _anywhere(store, raw)
                    bucket = "corpus gap"
                    evidence = (
                        f"not in {character!r}'s ability prose"
                        + (f"; appears on {elsewhere!r}" if elsewhere
                           else "; nowhere on this wiki")
                    )

            buckets[bucket] += 1
            lines.append({
                "series": series, "question": question, "item": item,
                "bucket": bucket, "evidence": evidence,
            })

    for store in stores.values():
        store.close()

    width = max((len(line["item"]) for line in lines), default=10)
    current = ""
    for line in lines:
        if line["question"] != current:
            current = line["question"]
            print(f"\n{current}  [{line['series']}]")
        print(f"  {line['bucket']:15} {line['item']:{width}}  {line['evidence']}")

    total = sum(buckets.values())
    print("\n" + "=" * 78)
    print(f"{total} missing canon items")
    for bucket, count in buckets.most_common():
        print(f"  {bucket:15} {count:3}  ({count / total:.0%})")

    out = scores_path.replace(".json", "_diagnosis.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump({"buckets": dict(buckets), "items": lines}, handle, indent=2)
    print(f"\nwrote {out}")


if __name__ == "__main__":
    diagnose(sys.argv[1] if len(sys.argv) > 1 else "canon_scores.json")
