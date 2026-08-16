# Expand the question bank to ~335, and measure the instalment class for the first time

*Written 2026-08-14. Not yet executed. Successor to `PRECISION_PLAN.md`, which
is done.*

## Where things stand when this starts

Branch `character-scoped-questions`, pushed to origin, 8 commits ahead of the
last session's start. Latest run `reports/2026-08-14-1605`:

| | |
|---|---:|
| canon items | **836/984 (85.0%)** |
| precision, closed sets | **58.8%** |
| questions fully correct | 62/103 |
| questions returning nothing | **0** |
| confident and wrong | **0** |
| fact answers present | 32/32 |
| tests | 626 pass; `eval --series jjk` 24/24 |

Session start was 626/878 (71.3%) at 33.5% precision with 12 questions failing.

## Context

Every remaining lever is now hard to see, because the bank only asks two shapes:
"every X of Y" (roster) and 32 single-answer lookups. This adds ~200 questions of
a shape the engine has **never been measured on**: direct factual lookups
("In which chapter does Cell become Perfect?") and counts ("How many types of
Chainsaw Man exist?"), plus general per-series questions about arcs, chapters and
episodes.

**The exploration found this class is barely supported, which is the point of
measuring it.** Recorded here so the plan is not written against a fantasy:

| finding | evidence |
|---|---|
| `EpisodeIndex` maps chapter→episode for **3 of 8 series** | jjk 181, opm 117, csm 38; berserk/bleach/db/hxh/onepiece **0** (`retrieve/citations.py:114-132` requires a node titled exactly `Chapter N`) |
| **bleach has 0 chapter pages, 0 episode pages, 0 arc pages** | its only instalment data is 10,123 inline `(Chapter N)` markers in prose |
| db titles chapters by name, not number | `The Complete Cell`, so `locator_from_title` yields 0; the number is an infobox fact `Chapter #: 382 (DBZ 188)` |
| arc spans exist for 6 of 8 series, in 6 different raw formats | jjk `Chapter 1 - 18, Episode 1 - 8`; onepiece `7 chapters, 5 episodes`; berserk `0-9&ndash;94 Total: 101`; bleach/hxh return nothing (`retrieve/chronology.py`) |
| the user's own example phrasings do not route | `wants_chronology()` matches **plural** `arcs`, so "Which arc starts…" misses it. `_WH` is `^`-anchored, so "In which chapter does Cell become Perfect?" routes to *narrative* |
| zero of the 135 existing questions mention chapter/episode/arc/saga | never measured |

**Expected outcome:** a bank that can see this class, a measured baseline for it,
and a remediation table that separates "a declaration can fix this" from "the
crawl has no such page", which is what the next step (applying general and
specific declarations) must be aimed at.

## Decisions taken (do not re-litigate)

- **10 general questions per series** → 80, plus 3 × 5 characters × 8 series →
  120. Bank 135 → ~335.
- **Mixed kinds.** Genuinely single-answer → `kind: "fact"`. Count/enumeration →
  `kind: "set"`, `scope: "closed"`, following the existing `jjk-set-01`
  ("How many 1v1 battles…"). Facts feed only *present in bundle*; closed sets
  feed the **precision** metric.
- **Characters: reuse the existing 39** `<series>-char-01..05` subjects, and add
  a fifth for berserk (only 4 exist; `berserk-char-03` is absent). Use **Casca**.

Existing character subjects, by series:

- berserk Guts, Griffith, Puck, Serpico (+ Casca)
- bleach Ichigo Kurosaki, Rukia Kuchiki, Byakuya Kuchiki, Kenpachi Zaraki, Sousuke Aizen
- csm Denji, Power, Aki Hayakawa, Makima, Himeno
- db Goku, Vegeta, Gohan, Piccolo, Frieza
- hxh Gon Freecss, Killua Zoldyck, Kurapika, Leorio Paradinight, Hisoka Morow
- jjk Yuji Itadori, Satoru Gojo, Megumi Fushiguro, Nobara Kugisaki, Sukuna
- onepiece Monkey D. Luffy, Roronoa Zoro, Sanji, Nami, Usopp
- opm Saitama, Genos, Garou, Tatsumaki, Bang

---

## Phase 0: probe before authoring. **DONE 2026-08-15, and it changed the plan**

16 probes, 2 per series, scored exactly as `score_facts` would (`ask` →
`haystack` → `norm` → `present`). Then a second pass asking the question that
actually matters: **how often does a deliberately WRONG answer score?**

Scripts: `tmp/probe0.py`, `probe1.py`, `probe2.py` (job scratch dir).

### Result 1: raw hit rate 12/16, but the headline is misleading

| shape | hits | verdict |
|---|---|---|
| relation (control) | 2/2 | the existing 32-fact shape, works |
| count | 2/2 | routes **roster** |
| arc-span | 2/2 | routes **roster** |
| attribute | 2/2 | routes qa |
| debut-chapter | 2/4 | routes **narrative** |
| event-chapter | 1/2 | routes narrative |
| episode | 1/2 | routes narrative |

### Result 2: the chapter hits are mostly false positives

Every "in which chapter" question routes to **narrative**, which returns ~195k
characters of prose dense with `(Chapter N)` citation markers. Distinct chapter
numbers per bundle: **hxh 299, jjk 91**, csm 9, db 0.

Feeding 13 decoy chapter numbers the answer is definitely *not*:

| question | decoys that scored | verdict |
|---|---|---|
| hxh "In which chapter does Gon meet Kite?" | **11/13** | UNSCOREABLE |
| jjk "In which chapter does Sukuna first appear?" | **4/13** | UNSCOREABLE |
| csm "In which chapter does Makima first appear?" | 0/13 | ok |
| db "In which chapter does Cell reach Perfect form?" | 0/13 | ok, but scores 0; the bundle has **no** chapter numbers |
| jjk / onepiece arc-span | 0/13 | ok |
| csm count | 0/13 | ok |

**So a `debut-chapter` question on a big wiki passes by accident.** It would
inflate the score while measuring nothing. This is exactly what Phase 0 existed
to catch.

### Result 3: `arc-span` is the strongest shape, not the weakest

jjk returns 9 arcs, each with an exact range in `member.debut`:
`Chapter 1 - 18, Episode 1 - 8`, `Chapter 19 - 31, Episode 9 - 13`. That is the
user's original question answered correctly and precisely. One Piece is degraded
(`7 chapters, 5 episodes`: counts, not ranges; one arc shows `42-68`).

### Decisions taken from Phase 0

1. **Do not author `debut-chapter` / `event-chapter` as scored questions.** The
   narrative route makes them unscoreable on the large wikis. Author **4 total**
   (not 40) as documented known-fails, `note` recording the decoy measurement,
   so the gap stays visible and a future router fix can be measured against them.
2. **Reallocate that budget to `arc-span` and `count`.** Both route to roster,
   both return precise bundles, both scored 0/13 decoys, and both feed the
   **precision** metric as closed sets.
3. **`attribute` and `relation` keep full allocation**, on the qa route, precise.
4. Where an instalment number is wanted, prefer **`arc-span`** phrasing (plural
   "arcs", which `wants_chronology()` matches) over "in which chapter", which it
   does not.

## Phase 1: question design rules

These follow from `present()` being word-boundary containment over a
`norm()`-folded flattening of the whole bundle (`canon_gold.py:120-131`).

1. **Never answer with a bare number.** `norm("382")` → `382`, which matches a
   page count, a power level or a date anywhere in the bundle. Always
   `"Chapter 382"`: the two tokens must appear contiguously.
2. **Dragon Ball needs both numberings.** The wiki writes `Chapter #: 382 (DBZ
   188)`. Author `item: "Chapter 382"`, `aliases: ["chapter 188", "dbz 188"]`.
3. **No single short tokens as the only item.** `Wing`, `Power`, `Bang`, `Blast`
   match incidentally. Prefer multi-word, or add a disambiguating alias.
4. **Global question-text uniqueness is enforced** across all 8 files
   (`test_question_texts_are_unique`). Name the series or character in every
   question. Assume collisions at 200; check mechanically in Phase 5.
5. **`tier` has no default.** Omitting it aborts the whole bank at import
   (`questions.py:176`). Every question needs `tier: "wiki"`, non-empty
   `subject`, `verified`, `sources`.
6. **`kind` defaults to `"set"`**, so `"fact"` must be written explicitly.
7. Facts: `accept: "any"`, one answer item, matching all 32 existing ones.
8. Items must be distinct after `norm()` within a question; a word-prefix overlap
   between two items requires a non-empty `note`.

## Phase 2: allocation

Revised against Phase 0's measurements. Still ~200 questions, reweighted away
from the shapes that cannot be scored.

**Character questions, 3 × 5 × 8 = 120.** Per character, one of each:
- **relation** (fact): "Who taught / killed / sealed / defeated X?", the shape
  the 32 existing facts already use and pass 32/32. qa route, precise.
- **attribute** (fact): a specific named property such as rank, bounty, division,
  grade, hero class, contract, zanpakutō. qa route, precise.
- **character-scoped set** (set, closed): "Every X of Y" in a *kind* the bank
  does not already ask for that character: weapons, contracts, students,
  fights, titles. Roster route, feeds precision, and exercises the `subject:`
  roster mechanism built last session.

**General questions, 10 × 8 = 80.** Per series:

| shape | kind | per series | notes |
|---|---|---:|---|
| arc → chapter+episode span | set | 1 | **skip bleach, hxh** (0 arc pages) |
| "how many X exist": types, divisions, grades, classes, ranks | set (closed) | 4 | strongest shape: roster route, 0/13 decoys |
| organisation membership / leadership | set + fact | 3 | reuses the group-roster path already at 100% precision |
| named-entity attribute | fact | 2 | qa route |

**Explicitly do not author:**
- **`debut-chapter` / `event-chapter` beyond 4 total known-fails**, measured
  unscoreable (hxh 11/13 decoys, jjk 4/13). The 4 exist to keep the gap visible.
- arc questions for **bleach** or **hxh**: 0 arc pages, so a 0 measures the
  crawl, not the engine.
- "which episode" as a *derived* answer for berserk/bleach/db/hxh/onepiece
  (empty `EpisodeIndex`); only where the wiki page states the episode itself.

Record every exclusion in the affected question's `note`, and record the decoy
measurement in the 4 known-fails, so a later reader sees the gap was deliberate
and knows how it was established.

## Phase 3: delegate research to opencode

Reuse the pattern that produced 795 verified verdicts, from
`C:\Users\Nikhil\.claude\jobs\<job>\tmp\audit`:

```
opencode run --auto --format json -m opencode/deepseek-v4-flash-free \
  --dir <audit-dir> "<task>"
```

Four background runs, one per series-pair, monitored by `watch.py` / `probe.py`
(counts only; never dump the JSON logs into context). `fetch.py` reads **raw
wikitext** via `api.php?action=parse&prop=wikitext`.

One JSONL row per proposed question:

```json
{"series":"db","kind":"fact","subject":"Cell","question":"In which chapter does Cell reach his Perfect form?",
 "answer":[{"item":"Chapter 382","aliases":["chapter 188","dbz 188"]}],
 "page":"The Complete Cell","source":"https://dragonball.fandom.com/wiki/...",
 "evidence":"|Chapter #= 382 (DBZ 188)","note":"dual numbering"}
```

Contract: `evidence` must be a **verbatim substring of the fetched wikitext** and
must itself contain the answer's number/name. Never guess a quote.

## Phase 4: verification gate (extended)

Extend `verify_batch.py`. Beyond today's two checks (quote exists in the
re-fetched page; quote mentions the claimed name), add:

1. **The number in the answer appears in the evidence.** "Chapter 382" is
   accepted only if `382` occurs in the quoted wikitext. A plausible *wrong*
   chapter number is the likeliest failure mode and is invisible to today's gate.
2. **The source URL's page matches the `page` field** that was fetched.
3. **Answer scorability**: `norm(item)` must be ≥2 tokens or carry an alias that
   is; reject bare-number items mechanically rather than by eye.

Today's gate caught 13 fabrications in 795 verdicts (2%). Budget a manual review
pass over everything it lets through.

## Phase 5: apply into `questions/*.json`

New script in the job scratch dir, following `apply_patch.py` (gate-then-apply,
`--dry-run` first, additive only).

- **IDs**: facts continue `<series>-fact-05..`; new closed sets continue
  `<series>-set-09..`. **Never set `baseline: true`** (README forbids it for new
  questions), which keeps the comparable subset intact.
- **Pre-write checks**, all mechanical: global question-text uniqueness across
  the merged bank; global id uniqueness; per-question `norm()` distinctness;
  prefix-overlap → note present.
- Write with `json.dump(indent=2, ensure_ascii=False)` + trailing newline, the
  existing file format.

## Phase 6: verify and measure

```powershell
python -m scriptengine.cli canon-run --dry-run       # bank must validate
python -m pytest tests/ -q                           # 626 baseline, must not drop
python start_scriptengine.py                         # MUST restart: staleness guard
python -m scriptengine.cli canon-run --skip-eval
python -m scriptengine.cli eval --series jjk         # must stay 24/24
```

**What the numbers will do, stated in advance so nothing reads as a regression:**
- **Recall will fall.** ~200 questions targeting an unmeasured, weakly-supported
  class will score badly. That is the measurement working.
- **Precision moves only from the new closed sets**; the ~120 new facts do not
  enter the precision denominator.
- The **comparable subset stays fixed** (no new `baseline: true`).
- `canon_report` prints its "the bank changed between these two runs" warning
  whenever the canon total moves. It will fire, correctly.

## Phase 7: triage, then declare

Run `diagnose_misses` + `diagnose_intruders`; split every failure into:

- **retrieval gap**: stored and not returned → a declaration fixes it. Use the
  two mechanisms built in the last session: `rosters:` with `subject:` for
  character-scoped sets, and `ability_stopwords` / `non_canon_works` for junk.
- **routing gap**: the query never reached the right path. Already known:
  `wants_chronology()` is plural-only; `_WH` is `^`-anchored so "In which
  chapter…" routes to narrative. **These need code, not declarations.**
- **corpus gap**: bleach has no arc pages; no declaration invents one. Retire or
  document, never tune against it.

## Risks

- **Authoring 200 questions for a class the router cannot reach**, making the
  whole pass measure one regex. Phase 0 exists to catch that before the cost.
- **Fabricated chapter numbers**, the likeliest research failure and the hardest to
  eyeball. Phase 4's number-in-evidence check is the mitigation.
- **Budget**: research is delegated to opencode and costs no Claude budget, but
  the review pass over ~200 accepted rows does. Batch it.
- `eval --series jjk` must stay 24/24 throughout. It is the leak detector.

## Files

- **Author/modify**: `questions/{berserk,bleach,csm,db,hxh,jjk,onepiece,opm}.json`
- **Reuse read-only**: `scriptengine/eval/questions.py` (schema/validation),
  `scriptengine/eval/canon_gold.py` (`ask`/`haystack`/`present`/`norm`),
  `scriptengine/eval/diagnose_{misses,intruders}.py`, `tests/test_question_bank.py`
- **Scratch (not the repo)**: job tmp `audit/`, holding `fetch.py`, `verify_batch.py`,
  `watch.py`, `probe.py`, `apply_patch.py`, `section.py`
- **Possibly later, code not data**: `scriptengine/retrieve/chronology.py`
  (`wants_chronology`), `scriptengine/retrieve/router.py` (`_WH`)

## Environment notes carried forward

- venv is `scriptengine\.venv\Scripts\python.exe` (not a root `.venv`).
- Start the API server so it **inherits the shell environment**
  (`python start_scriptengine.py` from a normal shell). Starting it via
  PowerShell `Start-Process -WindowStyle Hidden` gives a server that answers
  `/health` and then throws HTTP 500 mid-run from `huggingface_hub`
  ("Cannot send a request, as the client has been closed").
- `canon-run` is run with `--skip-eval` to dodge VRAM double-allocation.
- Redirected stdout is block-buffered; pass `-u` to see live progress.
