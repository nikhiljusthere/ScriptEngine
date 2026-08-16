# Onboarding a new wiki

The order that took the bank from 71.3% recall / 33.5% precision to 91.2% / 60.0%,
and a One Punch Man battle bank to 97.7% / 97.3%. Written as a checklist because
every step here was learned by getting it wrong first, and the same traps are
waiting on the next wiki.

**The rule underneath all of it:** every wiki names things its own way, and the
shared code reads those names. Where a wiki's vocabulary differs, the answer is
almost never new logic. It is a declaration in `series/<name>/overrides.yaml`.
Measure before declaring, and declare rather than special-casing.

---

## 0. Crawl and index

```powershell
python -m scriptengine.cli crawl --series <name>
python -m scriptengine.cli index --series <name>
```

Everything below assumes `series/<name>/facts.db` exists.

---

## 1. Audit the classification *first*

This is the highest-yield step and the easiest to skip. `page_type` comes from
the infobox the wiki chose, and the shared token table folds it into a semantic
type. When that fold is wrong, entities become invisible, silently, with no
error anywhere.

```python
SELECT page_type, COUNT(*) FROM documents GROUP BY page_type ORDER BY 2 DESC
```

Run every distinct value through `semantics.type_from_page_type` and look hard
at anything landing on `event`, `media` or `unknown`. `event`, `media` and
`location` are in `NEVER_MEMBERS`: a page typed that way **cannot be a member of
anything, ever**.

Three real cases, all found this way:

| wiki | page_type | folded to | truth | cost |
|---|---|---|---|---|
| onepiece, opm | `fighting_style_box` | `event` (matched `fight`) | technique | 63 pages, incl. Zoro's sword styles and Nami's `Art of Weather` |
| opm | `combat` | `event` | technique | 48 pages: `Fire Manipulation`, `Killer Move: Serious Series` |
| opm | `parent_tab` | `unknown` | character | 271 pages: **Saitama, Garou, Genos, Bang, Tatsumaki, King** |

The `parent_tab` one is worth dwelling on. One Punch Man wraps character pages
in a tabber, so the infobox found is the tab container. Every filter asking "is
this a character" dropped the entire main cast, and
`Monster Association Arc` returned a 119-name roster with no Saitama in it.

**Fixes, in order of preference:**

1. A per-series `semantic_types:` declaration, `combat: technique`. Narrow, no
   effect on other wikis.
2. A token added to `_TYPE_TOKENS`, only when the reading is wrong everywhere,
   as `fighting_style` was. Put the specific token *before* the general one it
   contains.
3. The category fallback already handles `unknown` pages filed under
   `Characters`, excluding indexes (a page named after its own category, or
   `List of ...`).

---

## 2. Audit the section names

Each wiki names its sections differently, and both extraction passes are driven
by declarations of those names.

```python
# top-level sections on character pages, by chunk count
SELECT breadcrumb FROM chunks JOIN documents ...  # then split on '/'
```

**Abilities** (`ability_sections:`). jjk declared `Abilities and Powers` and the
wiki also uses `Powers & Abilities` on one page: `Rika`, Yuta's cursed spirit,
reached by nothing. A heading the wiki renames is silent and costs a whole
character.

**Relations** (`relation_sections:`). The defaults are `Relationships` and
`History`, and three wikis matched *nothing*:

| wiki | writes it as | candidates before → after |
|---|---|---|
| berserk | `Story`, `Background` | 0 → 126 |
| hxh | `Background` | 0 → 201 |
| db | `Biography` | 3 → 1,057 |

Also check whether the wiki moved the section to a **subpage**. One Punch Man
keeps `Saitama/Relationships`, 51 chunks, whose breadcrumbs read
`Hero Association / Genos`. The headings are the *other people*, so nothing in
the breadcrumb says "Relationships". Reading only breadcrumbs missed the most
important relationship in the series.

**What to leave out.** Plot-narration sections (`Plot`, `Synopsis`) are where
relationships *happen* rather than where they are described. hxh's `Plot` is
3,014 chunks. Judge them on measured output, not in advance. "fought once" is
not `enemy`.

**And until 2026-08-17 there was no measured output to judge.** `canon-run`
cannot see this pass at all. Its bank holds no relation-shaped set question on
any of the eight wikis -- twelve questions mention a relationship word and
every one is a fact or a roster of people -- and the relations table is not a
member source either: `build_roster` never reads it, and its only consumer is
`chronology.scaffold`, the arc scaffold. So 22,700 rows across eight wikis sat
outside every number the project quotes, and this declaration could be neither
kept nor reverted on evidence.

Score it with the coverage bank instead:

```powershell
python -m scriptengine.eval.build_relation_bank --series <name> --verified <date>
python -m scriptengine.eval.relation_coverage --series <name>
```

The gold is every person the wiki heads a subsection for inside a character's
`Relationships` section: structure rather than prose, so no judgement enters
the transcription. **Recall-only**, deliberately -- the store is *supposed* to
hold partners the wiki gives no heading, because reading the story is the point
of the declaration, so scoring precision against that list would mark the
intended gain as a defect. The extras are reported separately, split by whether
narration is the only thing holding them.

It needs neither the server nor a model, so it runs while an extraction is in
flight, which is the opposite of `canon-run`.

**This only works on a wiki that names the subheading after the other person.**
Measured across all eight: csm 14 subjects, opm 3, the other six none. Where a
wiki does not, the builder refuses rather than emitting gold it cannot justify.

---

## 2b. Ownership the wiki states in a sentence

Some wikis put no `user` field on a technique page and say it in the first line
instead:

    "is a technique of Rukia Kuchiki's Zanpakutō, Sode no Shirayuki"

```powershell
python -m scriptengine.cli link --series <s>     # after index, which rebuilds the graph
```

Whether it is worth running is a property of the wiki, and the audit in step 1
already tells you: **only a wiki that gives techniques their own pages can have
this problem at all.**

| wiki | technique pages | lead names an owner | net new edges |
|---|---:|---:|---:|
| bleach | 488 | 242 | 196 |
| db | 2,123 | 347 | 302 |
| jjk | 149 | 8 | 0, all already had a field |
| onepiece | 63 | 1 | 0 |
| berserk, csm, hxh, opm | **0** | n/a | not applicable |

The four zeros are not a fault. Those wikis give abilities no page at all, which
is exactly why `ingest/abilities.py` exists -- Killua's `Godspeed` is prose and
nothing else. Do not go looking for a classification bug there.

Two properties to keep if this is ever extended:

* **Write under a distinct relation.** `stated user` is not `user`. A claim read
  out of prose must stay tellable from one the wiki wrote in a field, and
  removable if the rule turns out to be wrong.
* **A derived set may not call itself exact.** A test caught this immediately:
  `_owned_roster` claimed exactness the moment the edges existed, and a set
  assembled from sentences is not a set the wiki curated.


## 3. Extract

See `EXTRACTION_RUNBOOK.md` for the model configuration, which matters more
than the model choice.

```powershell
# stop the API server first -- it and the 27B cannot share the card
nvidia-smi -pl 600      # elevated; check the cap before tuning concurrency
lms load qwen/qwen3.8-27b -c 36864 --parallel 8 --ttl 7200 --speculative-draft-mtp -y
$env:SCRIPTENGINE_ANSWER_TOKENS = "3072"

python -m scriptengine.cli abilities --series <name> --refresh --workers 8
python -m scriptengine.cli relations --series <name> --refresh --workers 8
```

**Check `reasoning_tokens == 0` after every load, before starting a long run.**
`lms load` has no preset flag, so the model comes up thinking unless the
per-model default config is in place, and thinking spends ~90% of the output
budget. `scriptengine.eval.model_health` probes this and the runner aborts on it.

Keep `--parallel` and `--workers` equal. Context is a *shared pool* across slots,
so `parallel x (max_prompt + max_tokens) <= context` must hold. 115 consecutive
failures came from getting this backwards.

**Check the GPU power cap before choosing a concurrency.** A power-capped card
looks exactly like a compute-saturated one, and the right answer flips: at a
570 W cap, 6 slots measured *slower* than 4; at the card's 600 W maximum, 8 slots
measured 54% faster in the real run. `nvidia-smi -q -d PERFORMANCE` reports
whether `SW Power Cap` is active.

Judge throughput in **rows/min, not characters/min**: window counts per
character range from 2 to 332, so characters/min reported a 20% gain that
rows/min showed as zero.

Expect zero failures. Anything else means the endpoint is wrong, not the wiki.

Before quoting a completion time, count the whole queue rather than sampling it.
The heaviest characters come first and are wildly unrepresentative (db relations
mean 7.1 windows, median 2), so extrapolating the first few overestimated the job
by 15x.

---

## 4. Check the declarations against the bank

```powershell
python -m scriptengine.eval.audit_declarations
```

Eight names were declared "not anyone's ability" while the gold called them
canon: the three Haki types and their romanisations, and jjk's
`Cursed Energy Manipulation`. The two files were each internally valid; only
comparing them shows the disagreement. Removing them took
`Every ability of Roronoa Zoro` from 7/10 to 10/10.

Re-run it after touching either list.

---

## 5. Build a bank, in two parts

**Researched gold** is the benchmark. Someone reads the wiki and writes the
answer. This is what the headline number means.

**Coverage gold** is transcribed from the wiki's own infobox fields, a primary
source, but nobody checked it independently. File it as `_<series>_<shape>.json`
so `load_all` skips it: it measures whether retrieval reaches what ingestion
stored, and must not move the headline number.

The coverage bank is where new capability gets found. One Punch Man's battle
bank, built to "every ability, every battle, where the technique was used",
scored:

```
Every battle of X                       95.9% recall   95.2% precision
Which techniques did X use in <battle>  36.9% recall    5.6% precision
```

The second shape was not a subtlety. The question named a fight and the engine
answered with the character's whole kit. Reading `combatant1`/`abilities1` off
the battle page took it to 100%/100%.

Score it in-process through `build_roster`. Roster mode is pure SQLite, so it
needs neither the API server nor the GPU, which matters, see below.

---

## 6. Measure

```powershell
python start_scriptengine.py          # MUST restart: canon-run refuses a stale server
python -m scriptengine.cli canon-run --skip-eval
```

Report recall and precision **together**. A change that adds recall usually
costs precision, and the honest form is both numbers, not the flattering one.

---

## The traps, collected

Each of these cost real time and none announced itself.

**The API server and the model cannot share one GPU.** The server loads
`bge-large` and a reranker; with a 27B resident that exhausts a 32GB card and
the model answers `500` to everything. A csm run recorded three failures and no
rows. Stop the server before extracting; the runner now refuses to start while
it is up.

**`Context size has been exceeded` means the pool is too small, not too big.**
LM Studio's context is one KV pool shared by every concurrent slot, and the error
reports *one slot's* usage: `n_tokens = 1199` against a 5,120 context, which
reads as "context is not the problem" and argues for lowering it. It is not:
6 slots x (1,735 prompt + 3,072 output) needed 28,842. Reasoning from the logged
number instead of the arithmetic produced 115 consecutive failures.

**A misconfigured extraction does not leave bad data.** Undersized context and
truncation both *raise*, so the row is dropped rather than half-written, and the
groundedness gate drops anything not present verbatim. A failed character stores
no rows, so `needs_relations` returns it next run. Check with a vocabulary count
(`SELECT relation, COUNT(*) ... GROUP BY relation`) before paying for a
re-extraction. After the 115 failures all 1,700 surviving rows were valid.

**`except OperationalError` turns a schema mismatch into a plausible empty
answer.** Adding an `acquired` column and naming it unconditionally made
`abilities_of` raise on four series that had not been re-extracted, and the
existing handler reported "this character has no abilities". A canon run lost
**152 items** and put 20 questions at recall 0 with nothing saying a schema was
wrong. The tell: every failing question was from the four un-migrated series.

**YAML reads `Name: Value` inside an inline list as a mapping.**

```yaml
members: [Allsight, Whirlwind Water Stream: Roaring Aura Sky Ripping Fist]
```

The second entry becomes a dict, `str()` gives its repr, and the member matches
nothing. Four were lost across three wikis and every one was a known missing
gold item: `Divine Dog: Totality`, `Shūkei: Hakuteiken`, and both of Bang's
Whirlwind techniques. The loader repairs it now; quote them anyway.

**The alias table is one-to-many.** `divine dog` names both `Divine Dogs` and
`Divine Dog: Totality`. It cannot be used to relax scoring: an alias-aware
scorer was written, measured, and reverted for merging two distinct shikigami.
A scorer that reports a better number by being wrong is worse than no change.

**The chunker makes copies.** A section is chunked at more than one level, so
the same prose arrives twice, and two cuts can overlap without either containing
the other. Yuji's part in the Shibuya Incident read as 7,190 words against a
page holding about half that.

**A SQLite connection belongs to one thread.** Passing the store into a worker
for one lookup killed 22 of 25 extractions. Resolve what the workers need on
the thread that owns the connection and hand them a plain map.

**A kind added to `semantics` needs an entry in `_KIND_WORDS`.** Anything
walking the vocabulary by kind raises `KeyError` on a kind that is not in it:
the canon run died on its first question.

---

## What is worth generalising

The pattern that produced most of the gain was not clever retrieval. It was:

1. **Measure where the misses are**, by bucket, from the diagnosis file rather
   than by reading answers.
2. **Ask whether the wiki actually says it.** Half of what looked like retrieval
   failure was a page typed wrong, a heading named differently, or a declaration
   that never parsed.
3. **Declare, don't special-case.** Nine of the fixes above are one line of YAML
   in one series' overrides.
4. **Distinguish the wiki's claim from the bank's claim.** They disagree more
   often than expected. CSM's "how many special divisions" gold counted what
   one page mentions rather than what exists, and the wiki lists Yuta as a user
   of the techniques he copied. Say which one is wrong rather than tuning until
   the number moves.
