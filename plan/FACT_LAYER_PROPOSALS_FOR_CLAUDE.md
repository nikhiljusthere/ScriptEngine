# Fact layer — proposals for Claude (owner 2026-10-07)

**I did not edit any of the files proposed here.** `tools/train/big_flags.py` and
`plan/BIG_REVIEW_PATTERNS.md` are Claude-only (owner rule, `plan/WINDOW_METHOD.md`), and so is
`tools/train/label_hints.py`. Everything below is a proposal with the evidence, the line number and
the change I would make if Claude approves it. I may `import` and `call` `big_flags.check()`
(`tools/train/label_single.py` does, for the v2 repair turn); calling is not editing.

Everything here was found by reading the code in this worktree, not by reasoning about it. Where a
claim is about engine behaviour it is quoted with a line number so it can be checked in one step.

---

## P1 — `scriptengine/stores/facts.py`: the fact layer cannot be stored as designed

**This is the most urgent proposal.** `plan/EXTRACTION_PROCEDURE_V2.md` is written and working, but
the rows it produces cannot survive a round-trip through the existing store without losing exactly
the fields that make them facts. Five defects, each verified by reading the file:

### P1.1 Qualifiers are silently discarded — `facts.py:1589-1634`

`save_relations` reads exactly five keys out of each dict:

```python
str(row.get("other") or "").strip(),          # 1619
str(row.get("relation") or "").strip().lower(),
str(row.get("era") or "").strip(),
str(row.get("section") or "").strip(),
str(row.get("quote") or "").strip()[:400],     # 1623
```

`modality`, `certainty`, `asserted_by` and `canon` — the four fields the whole v2 schema exists for —
are **dropped with no error and no warning**. Multi-day GPU output would land in a void.

**Proposal:** add a `qualifiers` TEXT column holding the JSON of the four fields, defaulting to
`{}`, and read it back on the `INSERT`. A side table is equivalent; a column is simpler and keeps the
row atomic.

### P1.2 The primary key collapses planned-vs-actual — `facts.py:1540`

```sql
PRIMARY KEY (character, other, relation)
```

"Hope van Dyne planned to train Scott Lang" and "Hope van Dyne trained Scott Lang" are the same key.
`INSERT OR REPLACE` (1612) means one silently vanishes, and which one survives depends on write order.
That is precisely the distinction §B.4 of the v2 schema exists to preserve, and the store's own
docstring at 1530 says *"Two characters can hold more than one relation at once and the wiki says so"*
— the PK already admits to the design; it just forgets modality. `era` is in the same position: the
docstring says "a relationship that changed is two entries", but `era` is not in the key either.

**Proposal:** `PRIMARY KEY (character, other, relation, modality, era)`. A migration of an existing
store is `CREATE TABLE relations_v2 ... ; INSERT INTO relations_v2 SELECT ..., 'stated', era FROM
relations ; DROP TABLE relations ; ALTER TABLE relations_v2 RENAME TO relations ;`. The
`events_fk_migrated` machinery at `facts.py:1802` is a precedent for rebuilding a derived table in
place.

### P1.3 `relations_of(both_ways=True)` inverts directed relations — `facts.py:1552-1567`

The query returns rows verbatim. A consumer asking "who is Scott Lang to?" gets back
`character='Hope van Dyne', relation='trained'` and, normalising to (query, counterpart), concludes
**"Scott Lang trained Hope van Dyne."** The existing 12 social relations are symmetric by design
(`friend_of`, `married`, `rival_of`), which is why this has never bitten. **Every relation the v2
vocabulary adds is directed**: `trained`, `mentored`, `recruited`, `persuaded`, `tricked`,
`ordered`, `member_of`, `child_of`, `parent_of`, `used`, `owns`, `destroyed`, `revealed_as`.

**Proposal:** store an explicit `inverse` name per relation (the v2 registry already has to carry
`inverse` and `symmetric`, per the council) and have `relations_of` return the row **plus an
`inverted` flag** (and the inverted relation name) when the match came from the `other` column and the
relation is directed. Symmetric relations keep today's behaviour. A consumer that ignores the flag
keeps working, so this is backward compatible.

### P1.4 "Add-only" is destructive in the store — `facts.py:1609`

```python
DELETE FROM relations WHERE character = ? COLLATE NOCASE, (character,)   # line 1609
```

The add-only repair pass of steps 5-6 is additive in the JSONL
and **destructive in the store**: every character's rows are wiped and only the new ones written. An
additive run that does not re-write the union loses the earlier rows. And the 22,700 existing
relations rows that `eval/relation_coverage.py` scores against would be destroyed by a window-fact
write for the same character.

**Proposal:** do not route window facts through `save_relations` at all. Either give window facts
their own writer that never deletes (and make its re-run idempotent by a
`provenance = "fact:<prompt_version>:<window_id>"` prefix, so a re-run is
`DELETE FROM window_facts WHERE provenance LIKE 'fact:<v>:%'`), or add a `replace: bool = True`
parameter that the fact-layer writer passes as `False`.

### P1.5 Quotes are truncated at 400 chars, silently — `facts.py:1623` and `:2092`

`str(row.get("quote") or "").strip()[:400]`. A long fact quote is mangled with no error. The v2 gate
therefore flags any quote over 400 chars (`fact_gate.py MAX_QUOTE`) so at least the labeller is
warned, but the truncation is still a silent data loss for anything the gate admits.

**Proposal:** raise the limit for the fact layer, or store the full quote in a `quote_full` column.
A 400-char cap is fine for one-line evidence; it is wrong for a clause that carries a modal.

---

## P2 — `tools/train/big_flags.py`: the coverage check has no quote-length cap

**Evidence, `big_flags.py:197`:**

```python
if cues and not any(q in sent or sent in q for q in quotes):
```

`check()` has no quote-length check anywhere — the only `quote` references are 99 (unpack), 189
(collect), 197 (compare) and 237 (print). The `sent in q` direction means **one row with a
paragraph-long quote marks every sentence inside it as covered.** Since v2 makes coverage a measured
number, the labeller would learn to hit that number with paragraph quotes. That is the same
"forced into silence" failure the owner is paying to fix, reappearing as "forced into quotes".

**Proposal (Claude-only, so Claude decides):** in `check()`, flag a row whose quote exceeds ~400 chars
as a `FLAG` (`quote is N chars; it will cover sentences it does not state`), and additionally flag
`sent in q` matches where `len(q) > 200`. This does not change v1's behaviour on real answers (real
quotes are short); it only makes the gaming visible.

I have already implemented the non-invasive version in `tools/train/fact_gate.py` (a quote must lie
**inside** one sentence, and ≤400 chars), so the v2 coverage number is safe either way. This proposal
is to make the v1 flagger honest too, not to fix v2.

## P3 — `tools/train/big_flags.py:88`: `sentences()` drops short declaratives

```python
def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if len(s) > 20]
```

The 20-character floor discards exactly the sentences that carry the person's own facts — "He is her
student", the owner's complaint. It also splits on any `.` followed by whitespace, which mangles
`Washington, D.C.` and dialogue containing periods.

**Proposal:** drop the floor to ~3 characters and use a terminal-punctuation split that does not fire
inside an abbreviation or a quotation. I have written that segmenter in `tools/train/fact_gate.py`
(`sentences()`) and `tools/train/fact_coverage.py` (`segments()`) with 8 tests pinning it, so the code
is ready to move into `big_flags.py` verbatim if Claude prefers one segmenter for both layers.

**One caveat before that move:** on the 806 reviewed windows the v2 segmenter counts 3,449 narrative
sentences against the retired one's 3,456 — because v2 has no length floor but *does* exclude link
lists and template dumps (`{{Marvel Database:Character Template`, `(Hulk)`, `(Spider-Man)`, …). The
three worst windows in the first baseline run were exactly that furniture. If `big_flags.sentences()`
is changed for the event layer, `MISS?` will start firing on wiki markup, so the furniture filter has
to go in at the same time.

## P4 — `plan/BIG_REVIEW_PATTERNS.md`: the dropped classes need catalog entries

The catalog's A-classes record what the review **corrected**. Classes A71, R4/R12, A31/A48, A67, R23
and A36 currently read "no row", and under v2 they read "a fact row with this relation and this
modality". A reviewer reading the catalog after v2 would call correct v2 answers errors.

**Proposal:** add a "F" section for fact-layer patterns, mapping each dropped class to its v2 row —
without changing the existing A-rows, because they remain correct for the **event** layer:

| catalog ref | v1 (event layer) | v2 (fact layer) |
|---|---|---|
| A71 | no row (practice, not conflict) | `trained` / `mentored` fact, `modality: actual` |
| R4/R12/A31/A48 | no row (joining is not meeting) | `joined` / `allied_with` / `left_group` fact |
| A67 | no row (a call is not a meeting) | `contacted` / `greeted` fact |
| R23 | no row ("helped" is not `saved`) | `helped` / `assisted` fact |
| A36 | no row (verbal defence is not `saved`) | `protected` (non-lethal) / `warned` fact |
| step 3 / A19/A23/A35/A60/A64 | no row (plans, orders, claims) | `modality: planned/ordered/claimed` + **`asserted_by`** |
| A11 | hedged: `defeated` only | `defeated` + a `killed` fact with `certainty: apparent` |
| R10 | one name per person | same, **plus** `revealed_as` / `alias_of` / `disguise_as` rows |
| G.2 | members only | members' rows **plus** `member_of` for each |
| A10/A24/A65 | no `arrived` for a description-place | `located_at` / `resides_at` fact |
| R11/A5/A52/A57 | drop the row | still no fact row (crowds/species are never facts) |
| production/trivia | no row | `canon: production` facts, tagged `production` |

**Proposal for `big_flags.py`:** a `FACTFLAGS` path in a **new** file rather than in `big_flags.py`,
because `check()`'s signature takes `events` and is shared with the v1 labeller. `tools/train/fact_gate.py`
already is that file. If Claude prefers it inside `big_flags.py`, that is Claude's edit to make.

## P5 — `tools/train/compose_big_set.py`: `--empty-share 0.30` becomes unobtainable

The 9B training set is composed with `--empty-share 0.30` and ~75% of those empties must be **hard**
empties. Under v2 step 3 is reversed: a window whose only content is a plan, a claim or a
hypothetical now carries a `modality: planned` fact row. Those windows are no longer empty in v2, so
either the share is unobtainable or the student is trained on a distribution the schema no longer
describes.

**Proposal:** define emptiness **per layer** — `hard_empty` = no event rows AND no fact rows;
`nonfact_only` = no event rows but ≥1 fact row; `fact_bearing` = ≥1 event row. Then
`--empty-share` counts `hard_empty` only. I record `empty_class` per window in `labels_v2.jsonl`, so
`compose_big_set.py` can read it directly when Claude wants to make this change. **I have not touched
`compose_big_set.py`.**

**Measured on the 806 reviewed windows:** 318/806 (39.5%) have zero final event rows. Under v2, how
many of those are fact-bearing is a number step 6 will produce; my step-4 pilot will measure it on 60
windows first.

## P6 — A new flagger module needs a Claude-owned entry in `WINDOW_METHOD.md`

`plan/WINDOW_METHOD.md` names `tools/train/big_flags.py` as the flagger and states that only Claude
edits it. The v2 fact layer introduces two new modules that need the same ownership statement so a
future session does not "fix" them:

- `tools/train/fact_gate.py` — the fact-layer gate
- `tools/train/fact_coverage.py` — the coverage reporter

**Proposal:** a one-line addition to `plan/WINDOW_METHOD.md` giving them the same owner as
`big_flags.py`.

---

## What I did NOT change, deliberately

- `tools/train/big_flags.py`, `plan/BIG_REVIEW_PATTERNS.md`, `tools/train/label_hints.py` — Claude-only.
- `series/universal/training/big/labels.jsonl`, `big_audit.jsonl`, `review_cursor.txt` — Claude's
  reviewed record. Read-only; every derived artefact (including the reviewed event rows used for
  add-only) goes to a new file.
- `scriptengine/stores/facts.py` — P1 is a proposal, not an edit. The store holds 131k sections across
  every series, including the owner's berserk/bleach/db/hxh/onepiece, and a migration is a decision
  that belongs to Claude.
- `plan/EXTRACTION_PROCEDURE.md` — the event layer's definition of the gold. v2 embeds it verbatim and
  a test (`test_event_section_is_verbatim`) fails if the two ever drift.

## The one decision that unblocks the most

**P1.4** — whether window facts get their own writer/table or extend `save_relations`. Everything
else in P1 can be a follow-up; P1.4 decides whether the fact rows are *additive at all*, and the
answer changes the shape of the final ingest. If the answer is "new table", the provenance-prefix
idempotence in `edges` (`schema.sql`: `provenance` is already a free-form channel carrying
`category:<name>`) is the mechanism to copy.
