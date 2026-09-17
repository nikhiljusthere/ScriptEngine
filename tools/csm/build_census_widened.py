"""Build the CSM widened census bank (council #29 Q1/Q2) from series/csm/facts.db.

`reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md` ruled that "dimensions green" is
not claimable from the character-only 60-question census:

- Q1: widen to the 5 in-scope page types (chapter_box / episode / volume_box /
  story_arcs_box / organization). That breadth is already on disk as
  `census_dimensions_csm_v2.json` (10 per class, JJK's 14 x 10 census shape),
  so it is carried here verbatim, never regenerated.
- Q2: 10 ability questions cannot stand for 376 ability rows (75 characters);
  size the pool to the rows (JJK precedent: the 315-pair pool,
  `reports/comprehension/P3A_ABILITY_CENSUS.md`). That pool is built here, one
  item per `abilities` row.

Q3 re-gates the P2.3 null branch on the widened census, so the bank also
carries the v1 character census (60) verbatim: widened = v1 + v2 + the pool.

Pool item shape = the census v1 item (`id/class/subject/q/expect/source`),
graded by the same rule (`tools/census_dimensions.py` judge: >= 2 of 3 expect
terms in the served text). `expect[0]` is the ability name; `expect[1:]` are
two mechanics phrases cut from the sentence(s) of the ability's own section
that name it. A bundle that carries the name but not what the ability does is
therefore RED -- the "thin" signal JJK's census measured separately.

Every term is verified model-free, under the judge's own matching:
  (a) term == norm(term)           (norm: span_recall's whitespace/NFC fold,
                                    applied to served text before matching)
  (b) term in norm(section.text)   (case-sensitive, the item's source section)
  (c) term.lower() in norm(chunk.text).lower() for a chunk of the character's
      page (the stored unit /context serves -- reachable in principle)
Terms failing any check are never emitted. No model, no :8000, no Qdrant;
facts.db is opened read-only. This file is data, not logic: re-run it after
any re-crawl or re-extraction so the pool tracks the corpus.

Usage:
    python tools/csm/build_census_widened.py [--out PATH]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.eval.span_recall import norm, sentences  # noqa: E402

DB = ROOT / "series/csm/facts.db"
V1 = ROOT / "reports/csm/census_dimensions_csm.json"
V2 = ROOT / "reports/csm/census_dimensions_csm_v2.json"
OUT = ROOT / "reports/csm/census_widened_csm.json"

MIN_CHARS = 25   # below this a phrase ("is able to use") matches anywhere
MIN_WORDS = 4
MAX_CHARS = 80   # long spans break on chunk-boundary / formatting drift
EDGE = " ,.;:-–—\"'"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trim(piece: str, keep_start: bool) -> str:
    """Cut a slice to MAX_CHARS at a word boundary, from the end nearest the name."""
    piece = piece.strip(EDGE)
    if len(piece) > MAX_CHARS:
        if keep_start:
            cut = piece[:MAX_CHARS]
            piece = cut[:cut.rfind(" ")] if " " in cut else cut
        else:
            cut = piece[-MAX_CHARS:]
            piece = cut[cut.find(" ") + 1:] if " " in cut else cut
    return piece.strip(EDGE)


def windows(piece: str) -> list[str]:
    """Two consecutive MAX_CHARS windows from the start of a slice.

    Most entries are one long "Name: what it does ..." sentence, so the second
    mechanics phrase has to come from further along the same sentence.
    """
    first = trim(piece, keep_start=True)
    rest = piece.strip(EDGE)[len(first):]
    return [first, trim(rest, keep_start=True)] if rest.strip(EDGE) else [first]


def clean_slices(text: str) -> list[str]:
    """Citation- and parenthesis-free contiguous slices of text (verbatim)."""
    # A citation "(Chapter 12)" is a parenthetical, so splitting on every
    # parenthetical drops citations too: a term spanning one would bind the
    # grade to citation formatting.
    return [s for s in re.split(r"\([^()]*\)|[()]", text) if s.strip()]


def candidates(section: str, name: str, others: list[str]) -> list[str]:
    """Mechanics phrases for one ability, nearest the name first.

    others = the character's other ability names: a following sentence that
    names one is that ability's entry ("Dancing: Kobeni ..."), and a phrase
    from it would grade this ability on another one's mechanics.
    """
    sents = sentences(section, min_words=1)
    out: list[str] = []
    for idx, sent in enumerate(sents):
        pos = sent.find(name)
        if pos < 0:
            continue
        for piece in clean_slices(sent[pos + len(name):]):
            out.extend(windows(piece))
        before = clean_slices(sent[:pos])
        if before:
            out.append(trim(before[-1], keep_start=False))
        # the sentence after the naming one usually continues the mechanic
        if idx + 1 < len(sents) and not any(o in sents[idx + 1] for o in others):
            for piece in clean_slices(sents[idx + 1]):
                out.extend(windows(piece))
    return out


def possessive(character: str) -> str:
    subject = f"the {character}" if character.split()[-1] in ("Devil", "Fiend") else character
    return f"{subject}'" if subject.endswith("s") else f"{subject}'s"


def build_pool(con: sqlite3.Connection) -> tuple[list[dict], Counter, list[dict]]:
    rows = con.execute(
        "select rowid, character, name, kind, section from abilities order by character, rowid"
    ).fetchall()
    stats: Counter = Counter()
    dropped: list[dict] = []
    items: list[dict] = []
    for rowid, character, name, kind, section in rows:
        secs = [norm(t) for (t,) in con.execute(
            "select s.text from sections s join documents d on d.id = s.document_id"
            " where d.title = ? and s.breadcrumb = ?", (character, section))]
        home = next((s for s in secs if name in s), None)
        chunks = [norm(t).lower() for (t,) in con.execute(
            "select c.text from chunks c join documents d on d.id = c.document_id"
            " where d.title = ?", (character,))]
        if home is None or not any(name.lower() in c for c in chunks):
            stats["name_unverified"] += 1
            dropped.append({"character": character, "name": name, "why": "name not verbatim in section/chunks"})
            continue
        others = [n for (n,) in con.execute(
            "select name from abilities where character = ? and name != ?", (character, name))]
        picked: list[str] = []
        for term in candidates(home, name, others):
            low = term.lower()
            # a term may contain the name ("slicing its targets" for Slicing):
            # the overlap check below keeps it from being the name alone
            if (len(term) < MIN_CHARS or len(term.split()) < MIN_WORDS
                    or term != norm(term) or term not in home
                    or not any(low in c for c in chunks)
                    or any(low in p.lower() or p.lower() in low for p in picked)):
                continue
            picked.append(term)
            if len(picked) == 2:
                break
        stats[f"mechanics_terms_{len(picked)}"] += 1
        if len(picked) < 2:
            # Q2 sizes the pool to the rows, so a thin source still gets its
            # item; it is flagged, never silently dropped (receipt lists it).
            dropped.append({"character": character, "name": name, "section": section,
                            "why": f"only {len(picked)} verifiable mechanics phrase(s) -- emitted, flagged"})
        items.append({
            "id": "",  # numbered after the loop, so drops leave no gaps
            "class": "ability-pool",
            "subject": character,
            "q": f"What is {possessive(character)} {name}, and how does it work?",
            "expect": [name, *picked],
            "source": {"table": "abilities", "character": character, "name": name,
                       "kind": kind, "section": section, "abilities_rowid": rowid,
                       **({"thin_source": True} if len(picked) < 2 else {})},
        })
    for n, item in enumerate(items, 1):
        item["id"] = f"csm-abl-pool-{n:03d}"
    return items, stats, dropped


def union_verbatim(con: sqlite3.Connection, term: str, fold: bool = False) -> bool:
    """The v1/v2 meta's verification: substring of one of four fields.

    fold=True matches case-insensitively, as the judge does; the v1/v2 authors
    verified with SQLite LIKE (ASCII case-insensitive), so a sentence-initial
    "The" lowered to "the" passed there and fails the case-sensitive instr.
    """
    wrap = "lower({})" if fold else "{}"
    probe = term.lower() if fold else term
    for table, col in (("sections", "text"), ("facts", "value"),
                       ("abilities", "name"), ("documents", "title")):
        sql = f"select 1 from {table} where instr({wrap.format(col)}, ?) > 0 limit 1"
        if con.execute(sql, (probe,)).fetchone():
            return True
    return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=OUT)
    args = ap.parse_args()

    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    v1, v2 = json.loads(V1.read_text()), json.loads(V2.read_text())
    pool, stats, dropped = build_pool(con)

    carried = v1["items"] + v2["items"]
    carried_fail = [(i["id"], t) for i in carried for t in i["expect"] if not union_verbatim(con, t)]
    carried_fold_fail = [(i, t) for i, t in carried_fail if not union_verbatim(con, t, fold=True)]
    pool_terms = [t for i in pool for t in i["expect"]]
    pool_union_fail = [t for t in pool_terms if not union_verbatim(con, t)]
    n_abilities = con.execute("select count(*) from abilities").fetchone()[0]
    n_chars = con.execute("select count(distinct character) from abilities").fetchone()[0]

    bank = {
        "meta": {
            "series": "csm",
            "generated": "2026-09-17",
            "spec": "reports/csm/CLOSE_COUNCIL_RULINGS_Q1_Q4.md:11-22 (council #29 Q1/Q2; Q3 re-gates the P2.3 null branch on this bank)",
            "composition": {
                "v1_character_census": {"items": len(v1["items"]), "source": str(V1.relative_to(ROOT)), "sha256": sha256(V1), "carried": "verbatim"},
                "v2_page_type_census_q1": {"items": len(v2["items"]), "source": str(V2.relative_to(ROOT)), "sha256": sha256(V2), "carried": "verbatim"},
                "ability_pool_q2": {"items": len(pool), "abilities_rows": n_abilities, "characters": n_chars,
                                    "thin_source": sum(1 for i in pool if i["source"].get("thin_source"))},
            },
            "classes": sorted({i["class"] for i in carried + pool}),
            "judge": "tools/census_dimensions.py judge(): >= 2 of 3 expect terms (case-insensitive) in served_text(bundle) => MECH_GREEN",
            "expect_verified": (
                f"pool: all {len(pool_terms)} terms pass (a) term == norm(term), (b) case-sensitive in norm(source section text), "
                f"(c) case-insensitive in norm(chunk text) of the character's page; union check (sections.text + facts.value + "
                f"abilities.name + documents.title) fails {len(pool_union_fail)}. carried v1+v2: case-sensitive union check fails "
                f"{len(carried_fail)} of {sum(len(i['expect']) for i in carried)}, case-insensitive (the judge's rule) fails "
                f"{len(carried_fold_fail)}. Checked 2026-09-17, facts.db read-only."
            ),
            "builder": "python tools/csm/build_census_widened.py (regenerate after any re-crawl / re-extraction)",
            "grading": "not graded here (model-free authoring); P2.3 grades it against the live engine",
        },
        "items": carried + pool,
    }
    args.out.write_text(json.dumps(bank, indent=1, ensure_ascii=False))
    print(f"wrote {args.out}: {len(carried)} carried + {len(pool)} pool = {len(bank['items'])} items")
    print("pool stats:", dict(stats))
    print(f"pool union-check failures: {len(pool_union_fail)}; carried union-check failures: {len(carried_fail)}")
    if carried_fail:
        print("  carried failures (case-sensitive):", carried_fail[:10])
        print(f"  of those, case-insensitive failures: {len(carried_fold_fail)} {carried_fold_fail}")
    if dropped:
        print(f"flagged {len(dropped)}:")
        for d in dropped:
            print("  ", d)


if __name__ == "__main__":
    main()
