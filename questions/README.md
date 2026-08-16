# The online-canon question bank

One JSON file per series. These are the questions the engine is measured against
and the answers a human researched, with the source for every answer recorded
beside it.

The series list is discovered from the filenames. Adding `marvel.json` adds
Marvel to every run; nothing else needs editing, and no `.py` file names a
series.

## Why this exists separately from `scriptengine/eval/gold_*.json`

Both are gold sets. They measure different things and must not be merged.

| | `questions/` | `scriptengine/eval/gold_*.json` |
|---|---|---|
| Where answers come from | researched online, from the wiki and elsewhere | checked against the crawl as it exists on disk |
| Surface measured | `POST /context` over HTTP, the bundle a caller actually receives | retriever objects in-process |
| Scoring | partial credit: recall and precision | boolean, all-or-nothing |
| Coverage | all 8 series | 4 series |
| Gates the build | no, it is a measurement | yes, `cli eval` exits 1 below 1.0 |

The distinction that matters: `gold_*.json` asks "did a change break what
worked", and locks in today's crawl. `questions/` asks "is the engine right
about the series", and is allowed to say no for a long time. A question here
failing is information, not a broken build, which is why the runner never
exits non-zero on a score.

## How a question gets researched

**Discover on reddit and Q&A sites. Settle on the wiki.**

Reddit is good at telling you which questions people actually ask about a
series. It is bad at answering them: the top comment is frequently an argument.
So a thread is a legitimate way to *find* a question and never a way to answer
one. If the best available answer is a debate, the question does not belong in
this bank, so the engine cannot be marked wrong against a disagreement.

### Source tiers

| Tier | What | Rule |
|---|---|---|
| `wiki` | The series' own Fandom wiki, or official material such as a databook, Viz or Shueisha | The only tier that can carry a **set** alone |
| `editorial` | A bylined article: CBR, GameRant, ScreenRant, FandomWire, ANN | May carry a **fact** alone. For a set, corroboration only |
| `community` | Reddit, Quora, anime.stackexchange, forums | Never a sole source. Good for discovering questions; usable as corroboration when the comment cites a chapter, which must be recorded in `note` |
| *banned* | VS Battles, powerscaling wikis, "who would win", tier lists, content farms | Never a source at all |

A **set** asserts completeness, and only a wiki maintains a complete list. A
"top 10 forms ranked" listicle omits and invents entries as a matter of format.
A **fact** asserts one thing, so a bylined article can carry it.

The banned tier is not theoretical. The previous gold sourced
`Every Nen ability of Meruem` entirely to VS Battles; those four items are in
`hxh.json`'s `retired[]` awaiting re-verification against Hunterpedia. A
powerscaling entry is an argument someone won, not a record of what the series
says.

`tests/test_question_bank.py` enforces all of this mechanically. A banned domain
anywhere, a set without a wiki source, a missing date, a duplicate item after
normalisation. Each is a test failure, not a review comment.

## Schema

```json
{
  "series": "db",
  "wiki": "https://dragonball.fandom.com",
  "updated": "2026-08-12",
  "questions": [
    {
      "id": "db-set-01",
      "kind": "set",
      "question": "Every form of Goku",
      "subject": "Goku",
      "scope": "closed",
      "expect_mode": "roster",
      "tier": "wiki",
      "verified": "2026-08-04",
      "sources": ["https://dragonball.fandom.com/wiki/Goku"],
      "note": "why the set is drawn this way; any judgement call recorded here",
      "absent": ["Black Frieza"],
      "answer": [
        {"item": "Super Saiyan Blue", "aliases": ["ssgss"]},
        {"item": "True Ultra Instinct", "aliases": [],
         "tier": "editorial", "sources": ["https://..."]}
      ]
    }
  ],
  "retired": [
    {"question": "...", "item": "...", "reason": "why it stopped counting"}
  ]
}
```

| Field | Meaning |
|---|---|
| `kind` | `set` (an enumeration) or `fact` (one answer). A fact is a set of one: same structure, same matching; only the haystack differs |
| `subject` | Whose page the question is about. Used to tell "this name is somewhere on the wiki" from "this name is in the prose the extractor read"; only the second is evidence about extraction |
| `scope` | `closed` (the complete set) or `core` (a curated shortlist). Precision is not aggregated over `core` questions |
| `accept` | `all` (every item should come back) or `any` (one suffices) |
| `absent` | Names that must **not** come back. Catches over-inclusion from the other side |
| `expect_mode` | Which mode the router should pick. Recorded as an observation, never as a gate |
| `note` | Why. Judgement calls, corrections, and anything a later reader would otherwise redo |
| `baseline` | One of the 36 questions migrated out of `canon_gold.py`'s inline literal. The report scores these alone as their own row, because they are the only subset comparable to the 74.7% the old gold last recorded. Do not set it on a new question |
| `retired[]` | Items that stopped counting, with the reason. Kept rather than deleted so nothing silently re-adds them |

Per-item `tier` and `sources` are optional and default to the question's. Set
them when an item comes from somewhere other than the question's own source,
which is exactly the set of items most likely to be wrong, so the burden lands
where it belongs.

## Adding a question

1. Find it (reddit, a Q&A site, or what a script you are writing needed).
2. Answer it on the wiki. Record the URL.
3. Write it into the series file with an `id`, a `subject` and today's date.
4. `python -m scriptengine.cli canon-run --dry-run` validates without asking
   the server anything.
5. `python -m pytest tests/test_question_bank.py -q`.

Weight new questions toward what the engine is known to be weak at rather than
what it already answers. The measured defect is precision: closed sets come
back padded, and "Every form of Goku" returns 59 members against a canon 12, so
short complete sets where junk cannot hide are worth more than another long
one. Current-versus-former membership and thinly-filled categories are roadmap
phases 20 and 21 and currently have no question that can fail for those
reasons, which means neither phase has a number attached to it yet.

## A note on Berserk

The Berserk wiki cites cover art and interviews rather than instalments, so its
prose carries no chapter numbers and a Berserk answer cannot be tagged. That is
the wiki, not the pipeline. A report must not record it as a defect.
