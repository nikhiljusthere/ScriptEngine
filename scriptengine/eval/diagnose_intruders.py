"""Say where each wrong name the engine returned came from.

`diagnose_misses.py` buckets every canon item that did not come back, and that
table is what recall work has been aimed at. There was no equivalent for the
other side of the number, so precision work had nothing to aim at: the report
could say a question returned 70 members for 6 canon items without being able
to say where the other 64 came from, and a fix could only be evaluated by
re-running the whole thing and watching a percentage move.

This is the mirror. For every member the engine returned that matched no canon
item, it records which of the candidate paths vouched for it, the section
breadcrumb it was read from, and whether it has a page of its own:

  prose row       `abilities` holds it for this character. The section it was
                  extracted from comes with it, which is the actionable part:
                  the named techniques and the generic traits come from
                  different headings under the same parent.
  heading         a section on the character's own page (or a subpage) is
                  named this. `_section_roster` reads those directly.
  ownership edge  a page names this character in a `users`-shaped field. The
                  only one of the three that `validate_member` gates.
  category page   none of the above, but the wiki has a page by this name --
                  so it arrived through a category or a declared roster.
  unattributed    no page, no edge, no row, no heading. Nothing here vouches
                  for it at all.

A member can be vouched for by more than one, and that matters more than the
label: corroboration across paths is the signal the union throws away when it
deduplicates on lowercased name alone. `sources` keeps all of them; the bucket
below is the most specific one, because that is the one naming the fix.

Two arithmetic rules are inherited from `canon_gold.score_sets` rather than
re-derived, so this counts exactly the members precision counts:

* precision is `matched_gold_keys / len(members)`, and a canon item claims only
  the *first* of its aliases found. A set returning both "Imperfect Form" and
  "Imperfect Cell" therefore scores one match and one intruder, and that second
  name shows up here -- which is a bank problem, not an engine one, and worth
  seeing rather than hiding.
* `recall_only` questions are excluded. Their gold is a curated core list, not
  the complete set, so a "wrong" member there is usually right.

Run against a scores file written by `canon_gold.py`:

    python scriptengine/eval/diagnose_intruders.py reports/<run>/canon_scores.json
"""

import io
import json
import sqlite3
import sys
from collections import Counter, defaultdict

sys.path.insert(0, ".")

from scriptengine.config import series_paths, load_overrides  # noqa: E402
from scriptengine.eval import questions as _questions  # noqa: E402
from scriptengine.eval.canon_gold import GOLD, RECALL_ONLY, norm  # noqa: E402
from scriptengine.retrieve import roster  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

_BANKS = _questions.load_all()

SUBJECT: dict[str, str] = _questions.subjects(
    [q for bank in _BANKS for q in bank.questions]
)

# Most specific first: the bucket a member is filed under is the one that names
# its fix. A prose row is the only source carrying a section, and the section is
# what Phase 1 acts on, so it wins over a heading that happens to share the name.
_PRECEDENCE = ("prose row", "heading", "ownership edge", "category page")


def is_lead_row(section: str, character: str) -> bool:
    """Whether an extracted row came from the article's lead, not a heading.

    Tested against the page title and deliberately *not* as "the breadcrumb has
    no `/`": breadcrumb depth is a property of the wiki, not of the lead. Dragon
    Ball files ability prose under a single-segment `Abilities`, so the depth
    test called all 26 of Cell's rows lead-level when none of them are, and
    reported 259 lead rows across the run where there are 45.
    """
    return not section or norm(section) == norm(character)


def _canon_of(question: str) -> list[tuple[str, list[str]]]:
    for _, query, canon in GOLD:
        if query == question:
            return canon
    return []


def _matched_keys(canon: list[tuple[str, list[str]]], members: list[str]) -> set[str]:
    """The keys `score_sets` counted as hits, reproduced exactly.

    Not "every canon key that appears": one item claims one member, first alias
    wins. Anything else here would disagree with the precision it is explaining.
    """
    seen = {norm(m) for m in members}
    matched: set[str] = set()
    for item, aliases in canon:
        keys = [norm(item)] + [norm(a) for a in aliases]
        hit = next((k for k in keys if k in seen), None)
        if hit:
            matched.add(hit)
    return matched


def _rows_by_name(store: FactStore, character: str) -> dict[str, sqlite3.Row]:
    """This character's extracted ability rows, keyed by folded name."""
    if not character:
        return {}
    return {norm(row["name"]): row for row in store.abilities_of(character)}


def _heading_leaves(store: FactStore, character: str) -> dict[str, str]:
    """Folded leaf of every breadcrumb on the character's page, to its crumb.

    The leaf is what `_section_roster` returns as a member name
    (`roster.py:1260`), so this is the same string the union would have added.
    """
    if not character:
        return {}
    try:
        rows = store.sections_of(character)
    except Exception:  # noqa: BLE001 - no page is not a crash
        return {}
    out: dict[str, str] = {}
    for row in rows:
        crumb = str(row["breadcrumb"] or "").strip()
        if not crumb:
            continue
        out.setdefault(norm(crumb.split("/")[-1].strip()), crumb)
    return out


def _owned(store: FactStore, character: str) -> set[str]:
    if not character:
        return set()
    try:
        return {
            norm(row)
            for row in store.owned_by(character, roster._BELONGS_RELATIONS)
        }
    except sqlite3.Error:  # a character with no edges is normal
        return set()


def diagnose(scores_path: str) -> str:
    with open(scores_path, encoding="utf-8") as handle:
        scores = json.load(handle)

    rows_by_query = {row["query"]: row for row in scores.get("rows", [])}
    detail = {d["query"]: d for d in scores.get("detail", [])}

    stores: dict[str, FactStore] = {}
    buckets: Counter = Counter()
    sections: Counter = Counter()
    per_question: dict[str, dict] = {}
    lines: list[dict] = []

    for query, row in rows_by_query.items():
        if row.get("recall_only"):
            continue
        entry = detail.get(query) or {}
        members = entry.get("members") or []
        if not members:
            continue
        series = row["series"]
        if series not in stores:
            paths = series_paths(series)
            stores[series] = FactStore(paths.facts_db)
            load_overrides(paths)  # fails loudly here rather than mid-loop
        store = stores[series]

        canon = _canon_of(query)
        matched = _matched_keys(canon, members)
        intruders = [m for m in members if norm(m) not in matched]
        if not intruders:
            continue

        character = SUBJECT.get(query, "")
        ability_rows = _rows_by_name(store, character)
        headings = _heading_leaves(store, character)
        owned = _owned(store, character)

        counted: Counter = Counter()
        for name in intruders:
            key = norm(name)
            ability = ability_rows.get(key)
            section = str(ability["section"] or "").strip() if ability else ""
            kind = str(ability["kind"] or "").strip() if ability else ""

            sources: list[str] = []
            if ability is not None:
                sources.append("prose row")
            if key in headings:
                sources.append("heading")
            if key in owned:
                sources.append("ownership edge")
            page = store.node_by_name(name) is not None
            if not sources and page:
                sources.append("category page")
            bucket = next((s for s in _PRECEDENCE if s in sources), "unattributed")

            # Recorded rather than bucketed: it cuts across sources, and it is
            # the cheapest single filter available to Phase 1.
            lead = bool(ability is not None and is_lead_row(section, character))

            buckets[bucket] += 1
            counted[bucket] += 1
            if section:
                sections[section] += 1
            lines.append({
                "series": series, "question": query, "subject": character,
                "item": name, "bucket": bucket, "sources": sources,
                "section": section, "kind": kind, "page": page,
                "lead_level": lead,
            })

        per_question[query] = {
            "series": series, "subject": character,
            "returned": len(members), "canon": len(canon),
            "matched": len(matched), "intruders": len(intruders),
            "precision": round(len(matched) / len(members), 3),
            "buckets": dict(counted),
        }

    for store in stores.values():
        store.close()

    by_section: dict[str, Counter] = defaultdict(Counter)
    for line in lines:
        if line["section"]:
            by_section[line["question"]][line["section"]] += 1

    out = scores_path.replace(".json", "_intruders.json")
    payload = {
        "buckets": dict(buckets),
        "sections": dict(sections.most_common()),
        "lead_level": sum(1 for line in lines if line["lead_level"]),
        "single_source": sum(1 for line in lines if len(line["sources"]) == 1),
        "corroborated": sum(1 for line in lines if len(line["sources"]) > 1),
        "questions": per_question,
        "sections_by_question": {q: dict(c.most_common())
                                 for q, c in by_section.items()},
        "items": lines,
    }
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)

    total = len(lines)
    print("\n" + "=" * 78)
    print(f"{total} intruders over {len(per_question)} closed-set questions")
    for bucket, count in buckets.most_common():
        print(f"  {bucket:15} {count:4}  ({count / total:.0%})" if total else "")
    print(f"\n  {'single-source':15} {payload['single_source']:4}"
          f"  ({payload['single_source'] / total:.0%})" if total else "")
    print(f"  {'corroborated':15} {payload['corroborated']:4}"
          f"  ({payload['corroborated'] / total:.0%})" if total else "")
    print(f"  {'lead-level rows':15} {payload['lead_level']:4}"
          f"  ({payload['lead_level'] / total:.0%})" if total else "")

    print("\nworst questions")
    worst = sorted(per_question.items(), key=lambda kv: -kv[1]["intruders"])[:15]
    for query, stats in worst:
        top = by_section.get(query)
        crumb = f"  mostly {top.most_common(1)[0][0]!r}" if top else ""
        print(f"  {stats['intruders']:4} intruders  {stats['precision']:5.0%} prec  "
              f"[{stats['series']}] {query[:44]}{crumb}")

    print("\nsections supplying the most intruders")
    for section, count in sections.most_common(20):
        print(f"  {count:4}  {section}")

    print(f"\nwrote {out}")
    return out


if __name__ == "__main__":
    # Windows stdout defaults to cp1252 and half these wikis romanise with
    # macrons. The artifact is already on disk by here; this is only the echo.
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    diagnose(sys.argv[1] if len(sys.argv) > 1 else "canon_scores.json")
