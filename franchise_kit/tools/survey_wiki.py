#!/usr/bin/env python3
"""Structure survey for a newly indexed wiki: what to verify and what to declare.

    scriptengine/.venv/bin/python franchise_kit/tools/survey_wiki.py --series <name>
    # -> reports/<name>/SURVEY.md  (+ SURVEY_suggested_overrides.yaml)

Read-only (SQLite `mode=ro`), model-free, CPU. It automates the checks that each
cost a day on Marvel/MCU (2026-09-25..28) and on the earlier wikis
(docs/NEW_SERIES_PLAYBOOK.md):

  S1 page types + suspicious folds ('list'-typed main pages, unknown share)
  S2 where the narrative lives: sections vs leads vs long infobox fact values
  S3 section headings the events extractor's narrative test would miss
  S4 placement-page candidates (types carrying order signals) vs the defaults
  S5 time-axis signals: date keys, previous/next chains, issue/episode order keys
  S6 partition (multiverse / reality) signals in titles and facts
  S7 disambiguation + participant-resolution hazards (bare names -> hubs)
  S8 index health (NOCASE indexes that keep /context fast on big stores)

It SUGGESTS override values; it never writes `series/<name>/overrides.yaml`.
Measure, then declare (the playbook rule). Every number in the report comes from
the store, so a re-run after re-indexing shows what changed.
"""

from __future__ import annotations

import argparse
import collections
import re
import sqlite3
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

# Engine constants, imported rather than copied, so the survey measures against
# what the engine actually does today.
from scriptengine.ingest.events import (  # noqa: E402
    NARRATIVE_SECTION_TITLES,
    PLACEMENT_TYPES,
    _excluded_section_titles,
)

ORDER_KEYS = ("date", "previous", "next", "prev", "preceded by", "followed by",
              "first", "last", "releasedate", "release date", "air date",
              "airdate", "year", "chapter", "chapters", "episode", "episodes",
              "arc", "story arc", "story_arcs", "timeline")
PARTITION_KEYS = ("reality", "universe", "earth", "continuity", "timeline",
                  "dimension", "world")
SUFFIX = re.compile(r"\(([^()]{1,40})\)\s*$")


def q(c: sqlite3.Connection, sql: str, *args):
    return c.execute(sql, args).fetchall()


def fmt(n: float) -> str:
    return f"{n:,.0f}" if isinstance(n, (int, float)) else str(n)


def survey(series: str, sample: int) -> tuple[str, str]:
    db = ROOT / "series" / series / "facts.db"
    if not db.exists():
        raise SystemExit(f"no store at {db} -- crawl + index first")
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    c.row_factory = sqlite3.Row
    out: list[str] = []
    sug: dict[str, object] = {}
    t0 = time.time()
    w = out.append

    n_docs = q(c, "select count(*) from documents")[0][0]
    n_secs = q(c, "select count(*) from sections")[0][0]
    w(f"# Structure survey: `{series}`\n")
    w(f"Store `series/{series}/facts.db`: {fmt(n_docs)} documents, {fmt(n_secs)} sections. "
      f"Read-only; engine constants imported from `scriptengine/ingest/events.py`.\n")

    # S1 page types -------------------------------------------------------
    w("## S1: page types and suspicious folds\n")
    types = q(c, "select page_type t, count(*) n, sum(word_count) wc, "
                 "max(infobox_template) tpl from documents group by page_type order by n desc")
    w("| page_type | pages | words | an infobox template |\n|---|---:|---:|---|")
    for r in types[:30]:
        w(f"| {r['t']} | {fmt(r['n'])} | {fmt(r['wc'] or 0)} | {(r['tpl'] or '')[:40]} |")
    unknown = sum(r["n"] for r in types if (r["t"] or "unknown") == "unknown")
    w(f"\n- `unknown` share: {unknown / max(n_docs, 1):.2%} (GATE A wants < 5% among infobox pages).")
    big_list = q(c, "select title, page_type, word_count from documents where "
                    "page_type in ('list','disambiguation','hub_main','gallery') and word_count > 3000 "
                    "order by word_count desc limit 8")
    if big_list:
        w("- **Large pages typed as list/hub/disambiguation** (MCU trap: `Infobox List` typed Thanos, "
          "Gamora, Mantis as `list`): check whether these are really main articles; fix via `type_aliases`.")
        for r in big_list:
            w(f"  - `{r['title']}` ({r['page_type']}, {fmt(r['word_count'])} words)")
    junk = q(c, "select count(distinct page_type), count(*) from documents where length(page_type) > 40 "
                "or page_type like '%\\_vol\\_%' escape '\\'")[0]
    if junk[1]:
        w(f"- **Junk page-type ids**: {fmt(junk[0])} distinct types over {fmt(junk[1])} pages (long / title-derived ids, "
          "e.g. Marvel's slash-titled comic crossovers read as subpages). Fix the typing generically, then re-index.")
    w("")

    # S2 where the narrative lives ---------------------------------------
    w("## S2: where the narrative lives\n")
    sec_words = q(c, "select coalesce(sum(word_count),0) from sections")[0][0]
    lead = q(c, "select count(*), coalesce(sum(length(lead)),0) from documents where length(coalesce(lead,'')) > 200")[0]
    long_facts = q(c, "select key, count(*) n, avg(length(value)) a, sum(length(value)) s from facts "
                      "group by key having a > 300 and n >= 20 order by s desc limit 15")
    fact_chars = sum(r["s"] for r in long_facts)
    w(f"- Section words: **{fmt(sec_words)}** (about {fmt(sec_words * 6)} chars).")
    w(f"- Page leads over 200 chars: {fmt(lead[0])} pages, {fmt(lead[1])} chars.")
    w(f"- Long infobox fact values (avg > 300 chars, n >= 20): **{fmt(fact_chars)} chars** across {len(long_facts)} keys.")
    if long_facts:
        w("\n| fact key | rows | avg chars | total chars |\n|---|---:|---:|---:|")
        for r in long_facts:
            w(f"| `{r['key']}` | {fmt(r['n'])} | {fmt(r['a'])} | {fmt(r['s'])} |")
    if fact_chars > 0.2 * sec_words * 6:
        w("\n**The story lives substantially in infobox facts** (the Marvel shape: `history`, `synopsis1..N`). "
          "A sections-only extractor would leave it unread. Declare the narrative keys.")
        keys = sorted({re.sub(r"\d+$", "*", r["key"]) for r in long_facts})
        sug["events.narrative_fact_keys"] = keys
    w("")

    # S3 headings the narrative test misses -------------------------------
    w("## S3: section headings outside the narrative-title test\n")
    excl = _excluded_section_titles()
    heads = collections.Counter()
    words_in = words_out = 0
    for r in c.execute("select title, word_count from sections"):
        t = (r["title"] or "").strip().lower()
        wc = r["word_count"] or 0
        if not t or t in excl:
            continue
        if t in NARRATIVE_SECTION_TITLES or t.endswith(" arc"):
            words_in += wc
        else:
            words_out += wc
            heads[r["title"]] += 1
    tot = max(words_in + words_out, 1)
    w(f"- Words under narrative-titled headings: {fmt(words_in)} ({words_in / tot:.1%}); "
      f"under other, non-furniture headings: **{fmt(words_out)} ({words_out / tot:.1%})**.")
    w("- A heading allow-list reads only the first share. The 100% scope is heading-agnostic "
      "(every prose section; an explicit, counted furniture list is the only exclusion).")
    w("\nTop headings outside the narrative test (decide each: prose to read, or furniture to declare):\n")
    w(", ".join(f"`{h}` {n}" for h, n in heads.most_common(30)))
    w("")

    # S4 placement candidates ---------------------------------------------
    w("## S4: placement-page candidates (types that carry order signals)\n")
    placeholders = ",".join("?" * len(ORDER_KEYS))
    cand = q(c, f"select d.page_type t, count(distinct d.id) pages, "
                f"group_concat(distinct lower(f.key)) keys from facts f "
                f"join nodes n on n.id = f.node_id join documents d on d.id = n.document_id "
                f"where lower(f.key) in ({placeholders}) group by d.page_type "
                f"order by pages desc limit 15", *ORDER_KEYS)
    w(f"Engine default placement types: `{sorted(PLACEMENT_TYPES)}`.\n")
    w("| page_type | pages with order keys | keys | in defaults |\n|---|---:|---|---|")
    extra = []
    for r in cand:
        inside = r["t"] in PLACEMENT_TYPES
        w(f"| {r['t']} | {fmt(r['pages'])} | {(r['keys'] or '')[:70]} | {'yes' if inside else 'no'} |")
        if (not inside and r["t"] and r["pages"] >= 20
                and any(tok in r["t"] for tok in ("event", "arc", "battle", "conflict", "war", "saga", "story"))):
            extra.append(r["t"])
    if extra:
        sug["events.placement_types"] = extra
        w(f"\nSuggested `events: placement_types:` additions (event/arc/battle-shaped types outside the defaults): `{extra}`. "
          "Verify each is a container of events before declaring (MCU `conflict`, Marvel `story_arc`).")
    w("")

    # S5 time-axis signals -------------------------------------------------
    w("## S5: time-axis signals\n")
    date_like = q(c, "select lower(key) k, count(*) n from facts where lower(key) in "
                     "('date','releasedate','release date','air date','airdate','year') group by 1 order by n desc")
    chain = q(c, "select lower(key) k, count(*) n from facts where lower(key) in "
                 "('previous','next','prev','preceded by','followed by') group by 1 order by n desc")
    w("- Date-like keys: " + (", ".join(f"`{r['k']}` {fmt(r['n'])}" for r in date_like) or "none"))
    w("- Chain keys: " + (", ".join(f"`{r['k']}` {fmt(r['n'])}" for r in chain) or "none"))
    if date_like:
        samples = [r[0] for r in q(c, "select value from facts where lower(key)='date' limit 400")]
        shapes = collections.Counter(
            "YYYY" if re.fullmatch(r"\d{4}", s.strip()) else
            "Month YYYY" if re.fullmatch(r"[A-Z][a-z]+ \d{4}", s.strip()) else
            "Month D, YYYY" if re.fullmatch(r"[A-Z][a-z]+ \d{1,2}, \d{4}", s.strip()) else
            "has-year" if re.search(r"\d{4}", s) else "no-year" for s in samples)
        w(f"- `date` value shapes (sample of {len(samples)}): {dict(shapes)}. "
          "A no-year value is residue: counted, never guessed.")
        sug["events.axis.date_keys"] = [r["k"] for r in date_like[:2]]
    if chain:
        sug["events.axis.chain_keys"] = [r["k"] for r in chain[:2]]
    w("- The engine's manga-shaped axis (arc chain, `arc` fact, `chapters` fact) orders nothing on "
      "wikis like MCU/Marvel. Declare `events: axis:` and verify `temporal` coverage after re-derivation.\n")

    # S6 partition signals -------------------------------------------------
    w("## S6: partition (multiverse / reality) signals\n")
    suffixes = collections.Counter()
    for (title,) in c.execute(f"select title from documents limit {sample}"):
        m = SUFFIX.search(title or "")
        if m:
            suffixes[re.sub(r"[0-9]+", "#", m.group(1))] += 1
    w(f"- Title suffix shapes in a {fmt(sample)}-title sample: "
      + ", ".join(f"`({s})` {n}" for s, n in suffixes.most_common(8)))
    pk = q(c, "select lower(key) k, count(*) n from facts where lower(key) in (%s) group by 1 order by n desc"
              % ",".join("?" * len(PARTITION_KEYS)), *PARTITION_KEYS)
    w("- Partition-like fact keys: " + (", ".join(f"`{r['k']}` {fmt(r['n'])}" for r in pk) or "none"))
    dominant = suffixes.most_common(1)
    if dominant and dominant[0][1] > 0.1 * max(sample, 1):
        w("\n**Titles carry a partition suffix** (the Marvel `(Earth-616)` shape). Participant resolution must "
          "pick the variant in the passage page's partition, declared per wiki (`events: reality:`), "
          "never hard-coded in `.py`.")
        sug["events.reality.title_pattern"] = r"\((?:<prefix>)-?([\w-]+)\)\s*$  # fill <prefix> from the suffix shapes above"
    w("")

    # S7 disambiguation / resolution hazards -------------------------------
    w("## S7: disambiguation and participant-resolution hazards\n")
    dis = q(c, "select count(*) from documents where page_type = 'disambiguation'")[0][0]
    w(f"- Disambiguation-typed pages: {fmt(dis)}.")
    hub_names = q(c, "select n.name from nodes n join documents d on d.id = n.document_id "
                     "where d.page_type = 'disambiguation' order by d.word_count desc limit 12")
    if hub_names:
        w("- Biggest disambiguation hubs (a bare mention of these names resolves to the HUB unless the resolver "
          "follows `main_articleN` + partition): " + ", ".join(f"`{r[0]}`" for r in hub_names))
    has_events = q(c, "select count(*) from sqlite_master where name='events'")[0][0]
    if has_events:
        bad = q(c, "select count(distinct e.rowid) from events e join nodes n on n.id in (e.subject_node, e.object_node) "
                   "join documents d on d.id = n.document_id where d.page_type = 'disambiguation' "
                   "or d.page_type in ('list','hub_main')")[0][0]
        tot_ev = q(c, "select count(*) from events")[0][0]
        if tot_ev:
            w(f"- Stored event rows touching a disambiguation/list/hub page: **{fmt(bad)} of {fmt(tot_ev)} "
              f"({bad / tot_ev:.0%})**. Marvel measured 48% before the reality-aware resolver.")
    w("")

    # S8 index health --------------------------------------------------------
    w("## S8: index health (keeps `/context` fast on big stores)\n")
    idx = {r[0] for r in q(c, "select name from sqlite_master where type='index'")}
    for name in ("idx_nodes_name_nocase", "idx_nodes_label_nocase", "idx_categories_name_nocase"):
        w(f"- `{name}`: {'present' if name in idx else '**missing** (re-index, or create in place; results unchanged, '
                                                              'Marvel qa went 13 s to 1 s per probe)'}")
    w("")

    # declared vs suggested ---------------------------------------------------
    ov = ROOT / "series" / series / "overrides.yaml"
    w("## Declared today vs suggested\n")
    if ov.exists():
        import yaml
        declared = yaml.safe_load(ov.read_text(encoding="utf-8")) or {}
        w("Declared top-level keys: " + ", ".join(f"`{k}`" for k in sorted(declared)))
    else:
        w("No `overrides.yaml` yet: start from `franchise_kit/overrides.template.yaml`.")
    w(f"\nSurvey time: {time.time() - t0:.1f}s.\n")

    yml = ["# Suggested by franchise_kit/tools/survey_wiki.py: verify each before declaring.",
           f"# series: {series}"]
    for k, v in sug.items():
        yml.append(f"# {k}: {v}")
    return "\n".join(out), "\n".join(yml) + "\n"


def main() -> None:
    ap = argparse.ArgumentParser(description="Survey a wiki's structure before declaring overrides.")
    ap.add_argument("--series", required=True)
    ap.add_argument("--sample", type=int, default=20000, help="titles sampled for suffix shapes")
    ap.add_argument("--out-dir", default=None, help="default reports/<series>/")
    a = ap.parse_args()
    md, yml = survey(a.series, a.sample)
    od = Path(a.out_dir) if a.out_dir else ROOT / "reports" / a.series
    od.mkdir(parents=True, exist_ok=True)
    (od / "SURVEY.md").write_text(md, encoding="utf-8")
    (od / "SURVEY_suggested_overrides.yaml").write_text(yml, encoding="utf-8")
    print(f"wrote {od / 'SURVEY.md'} and {od / 'SURVEY_suggested_overrides.yaml'}")


if __name__ == "__main__":
    main()
