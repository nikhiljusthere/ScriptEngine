# Fact layer — execution progress (owner 2026-07 plan/FACT_LAYER_EXECUTION.md)

Executing `plan/FACT_LAYER_EXECUTION.md` steps 1-7 autonomously, per owner instruction, with the
council verdict (`plan/FACT_LAYER_COUNCIL.md`, commit `be8e0e2e`) taking precedence over §D wherever
they differ. Every verification below is one I ran myself.

Binding rules honoured throughout: `tools/train/big_flags.py` and `plan/BIG_REVIEW_PATTERNS.md`
untouched (proposals go to `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`); `labels.jsonl`,
`big_audit.jsonl`, `review_cursor.txt` read-only; new output only to `labels_v2.jsonl`; GPU-only; no
model switch (27B on :18080); kills by exact PID; commits with explicit pathspecs only.

Environment at start: ninfer `qwen3.8-27b-ninfer` PID 515652 on :18080, `--max-concurrency 3`,
262144 ctx; 30.7/32.6 GB VRAM; no labelling runner alive; `labels.jsonl` 5,405 lines,
`big_audit.jsonl` 442 rows / 440 ids, cursor 806.

---

## STEP 1 — Schema v2 (doc) — **PASS**

**Did:** wrote `plan/EXTRACTION_PROCEDURE_V2.md` (57,504 bytes), the system prompt for the v2
labeller. Structure: SECTION A = the event layer as a **verbatim copy** of
`plan/EXTRACTION_PROCEDURE.md`; SECTION B = the new fact layer (row shape, closed relation
vocabulary, `other_verb`, modality, certainty, ends, coreference, items/places/aliases/membership/
production); SECTION C = the coverage rule with the 9-tag closed set; SECTION D = five worked
examples drawn from real reviewed windows; SECTION E = the final per-sentence check.

The event layer is embedded rather than paraphrased so the 12 verbs cannot drift in v2. A test pins
that copy (step 2).

**Council amendments applied here** (each is a change to §D, recorded because §D parts may not be
dropped without a reason):
- §D §1 listed `location` as a qualifier; the council rejected a bare `location` qualifier ("his
  apartment" becomes decoration on an unrelated row), so it is promoted to the relations
  `located_at` / `resides_at`. B.8.
- §D §2 called the open relation `other`; the council found the name collides with the `other`
  COLUMN in the engine's `relations` table and the same ingest dict, so it is named **`other_verb`**.
  B.3.
- §D §1 listed `time` and `source` as qualifiers; the council folded canon into the store's existing
  `era`/`section` slots and warned cross-continuity contamination stated as truth is worse than a
  missing fact, so v2 carries a mandatory **`canon`** field (mcu/comics/alternate/anime/production)
  in the row itself rather than a free-text `source`. B.1.
- §D §1 lumped plans/orders/claims/dreams into one `modality` tag; the council made modality a
  **closed enum** and required **`asserted_by`** on every non-`actual` row, because without it the
  brain asserts Loki's lies. B.4.
- The council split `alias_of` from `disguise_as` (permanent identity vs temporary deception) — §D
  had only "alias of / revealed as". B.8.

**Verify (mapping table, §D table + §C dropped classes, run as a script):**

| check | result |
|---|---|
| SECTION A byte-identical to `plan/EXTRACTION_PROCEDURE.md` | **True** |
| `modality` closed enum (7 values) present | **True** |
| `certainty` closed enum (4 values) present | **True** |
| SECTION C tag closed set complete (9 tags) | **True** |
| mapping rows built from §D table + §C dropped classes | **32** |
| **unmapped classes** | **0** |
| classes whose target text is absent from the doc | **[]** |

The 32 mapping rows are: all 7 rows of §D §2's drop→keep table, all 14 dropped classes listed in
§C, all 7 relation groups + the `other` relation + the promotion mechanism from §D §1, the §D §1
qualifiers (`location`, `time`, `source/production`), §D §3's coverage rule, §D §4's add-only repair,
and §D §5's order of work. Written out in full in this log's step-1 mapping table below.

<details><summary>mapping table (32 rows, 0 unmapped)</summary>

| dropped class / §D part | where it lives in schema v2 |
|---|---|
| D§2 plans/attempts/orders/claims/lies/dreams/hypotheticals | B.4 modality enum + asserted_by |
| D§2 hedged deaths ("seemingly killed") | B.5 certainty=apparent; event `defeated` (A11); fact `killed`+apparent |
| D§2 group with named members -> members only | B.8 `member_of` alongside the members' rows |
| D§2 codename<->real name, disguise reveals (R10) | B.8 `alias_of` / `codename_of` / `revealed_as` / `disguise_as` |
| D§2 description places ("his apartment","the Bus") | B.8 `resides_at` / `located_at` |
| D§2 sparring, calls, joining, helping (A71,A67,R4,R23) | B.2 `trained` / `contacted` / `joined` / `helped` |
| D§2 behind-the-scenes, trivia, cast lists | B.8 `canon=production` + tag `production` |
| C sparring/training (A71) | B.2 `trained`/`mentored` + "trained vs fought" rule |
| C joining/allying/teaming (R4/R12/A31/A48) | B.2 `joined`/`left_group`/`allied_with` + "joined vs met" rule |
| C calls and remote appearances (A67) | B.2 `contacted`/`greeted` (Example 2) |
| C "helped" (R23) | B.2 `helped`/`assisted` |
| C verbal defence (A36) | B.2 `protected` (non-lethal) / `warned` |
| C plans/attempts/orders/claims/hypotheticals/dreams (A19/A23/A35/A60/A64) | B.4 modality + asserted_by |
| C hedged events "seemingly" (A11) | B.5 certainty=apparent (Example 3) |
| C group rows once members named (G.2) | B.8 `member_of` + `leader_of` (Example 4) |
| C codename/disguise collapsed to one name (R10) | B.8 reveal relations; B.6 real name everywhere |
| C description places (A10/A24/A65) | B.8 `located_at`/`resides_at`; organisations legal as objects |
| C crowds/species/indefinites (R11/A5/A52/A57) | B.6 not-allowed-ends (same rule as events) |
| C behind-the-scenes / trivia / real people | B.8 + B.9 `canon=production` only, tag `production` |
| D§1 relationship relations | B.2 relationship block |
| D§1 interaction relations | B.2 interaction block |
| D§1 possession/creation relations | B.2 possession/creation block |
| D§1 identity relations | B.2 identity block |
| D§1 state/change relations | B.2 state/change block |
| D§1 knowledge relations | B.2 knowledge block |
| D§1 open `other` relation + promotion | B.3 `other_verb`, verb literal in quote, <10% target |
| D§1 qualifier `location` | promoted to relations `located_at`/`resides_at` (council amendment) |
| D§1 qualifier `time` | carried by the quote; `era`/`time_rank` in the engine (no new field) |
| D§1 qualifier `source/production` | B.1 `canon` field (council amendment) |
| D§3 sentence coverage + allowed tags | SECTION C, 9-tag closed set, per-window coverage |
| D§4 add-only repair of the past | `label_single.py --add-only`; `labels_v2.jsonl`; events byte-identical |
| D§5 order of work | `FACT_LAYER_COUNCIL.md` numbered plan; this doc is its step 1 |

</details>

**Worked examples are the real reviewed windows**, read out of the data, not invented: b754
(Wasp / Training Scott Lang — the owner's own A71 case), b685 (Trevor Slattery / Bad Actors — the A67
podcast call), b122 (Barnes / 1945 — hedged "seemingly slew" + the Invaders' decision to kill), b9
(Avengers / New Threats — Valkyrie→Enchantress reveal + the Liberators).

**Next:** Step 2 — `tools/train/fact_gate.py`, `tools/train/fact_coverage.py`,
`tests/test_fact_layer.py`, plus the verbatim-pin test and the 806-window coverage baseline.

---

## STEP 2 — Gates and coverage (code + tests) — **PASS**

**Did:**
- `tools/train/fact_gate.py` — the fact layer's mechanical gate. Relation vocabulary check,
  `other_verb` handling (and refusal of `other`, which collides with the engine's `other` column),
  closed `modality`/`certainty`/`canon` enums, **`asserted_by` required on every non-`actual` row**,
  quote verbatim + ≥12 chars + ≤400 chars + **inside one sentence**, end checks (crowd, species,
  indefinite, bare pronoun, rank prefix, composite), subject≠object, symmetry hint, "event verb in a
  fact row" check, and tag-row validation against the 9-tag closed set. Reuses `draft_v2` /
  `verify_row_wiki` for wiki lookups; deliberately does **not** apply the event layer's
  "places only for arrived/departed/escaped" and species-page rules, because a fact's object may be a
  place, item, organisation or role (v2 §B.1/B.8).
- `tools/train/fact_coverage.py` — sentence-coverage reporting. Splits a window into narrative
  sentences with **no length floor** (the retired `big_flags.sentences()` drops spans under 20 chars
  and so cannot see short declaratives), reports uncovered sentences as a per-window worklist, and
  requires the row quote to lie **inside** the sentence — never the `sent in q` direction that lets a
  paragraph quote "cover" forty sentences.
- `tests/test_fact_layer.py` — 46 tests, including the verbatim-pin of v2's SECTION A against
  `plan/EXTRACTION_PROCEDURE.md`, the one-sentence-quote rule, the segmenter's handling of short
  declaratives and of `Washington, D.C.`, and the closed enums.

**Gate bugs I found and fixed while testing** (all were real, not test noise):
1. `CROWD` matched any leading article, which wrongly refused **"a cottage in Maine"** as a
   `resides_at` object — the case §B.8 explicitly allows. Split into `CROWD_WORDS` (never an end,
   whatever the relation) and `ARTICLE` (illegal only in front of a *person* end).
2. The "quote states its own relation" OK heuristic compared exact substrings, so `trained` never
   matched the quote "tasked with **training**". Replaced with a prefix-stem match.
3. `SPECIES` was anchored, so **"the Kree"** passed. Now strips a leading article first.
4. **The coverage denominator was wrong in a way that would have made the whole metric
   meaningless.** The three worst windows in the first baseline run were a cast list (`(Hulk)`,
   `(Spider-Man)`, …) and two `{{Marvel Database:Character Template` dumps — 80 "uncovered
   sentences" that were wiki furniture, not missing facts. Added `WIKI_MARKUP`, list/table/heading
   detection, and a function-word-OR-verb-form test that separates a link list (`Frank Dean`,
   `Brooks Watten †`) from a fact (`Frank Dean was her mentor`). Both tests are needed: a verb test
   alone would call `Magnistate's Wife` narrative, a function-word test alone would call
   `Scott fought Kang` furniture. 10 regression tests pin this.

**Verify — pytest:**
```
scriptengine/.venv/bin/python -m pytest tests/test_fact_layer.py -q
46 passed
```

**Verify — the 806-window baseline (the number the fact layer must close).**
Claude's final reviewed event rows over the 800 windows in the gold set (b7–b806), events only:

| measure | value |
|---|---|
| windows | 800 |
| **narrative sentences (v2 segmenter)** | **3,449** |
| covered by a reviewed event row | 1,278 (**37.1%**) |
| **uncovered** | **2,171 (62.9%)** |
| event rows | 2,530 (3.16/window) |
| same denominator via the retired `big_flags.sentences()` | 3,456 sentences, 36.8% covered |

The v2 segmenter's denominator (3,449) is slightly *smaller* than the retired one (3,456) here, but
for the opposite reason to the council's concern: v2 has no length floor (it keeps short
declaratives) and it *excludes* link lists and templates (which the retired one counted). Both
effects are visible; the ratio is the same to within a point, which confirms the Executor's
independent 34.7% and the "3.2 rows/window, 39% empty" figures.

**So: today's event layer leaves ~63% of narrative prose with no row at all.** That is the gap
§D's fact layer exists to close, and it is why the owner's complaint is a coverage problem rather
than a vocabulary problem.

The worst windows are now genuine missing facts, e.g. `3320a8b885f43b0c` (13 uncovered) and
`e2470f9de466ab00` ("For months, he survived in the wilderness, until being attacked by loggers and
brought to the local town's jail." — 12 uncovered).

**Next:** Step 3 — `label_single.py --schema v2` and `--add-only`.

---

## STEP 3 — Labeller v2 (`--schema v2`, `--add-only`) — **PASS** (owner override 2026-10-07: 35B, not the 27B)

**Did:** finished the interrupted step-3 edit in `tools/train/label_single.py`
(parse_v2, fact gate, coverage-repair turn, `--add-only`, provenance) and fixed two real
bugs found by the first dry run:

1. **v2 pointed at the 27B on :18080 because the execution plan made the agent the 27B.**
   The owner flipped windowing/labelling to the 35B, so the v2 defaults now target
   :18081 / `qwen3.6-35b-a3b-ninfer` (explicit `--url`/`--model` still win).
2. **Tag rows were validated as fact rows** (`fact_gate_keep(tags, ...)`), so every
   valid tag row was dropped (kept_tg was always empty and coverage could never use
   tags). Added `tag_gate_keep` with SECTION C's own rules; tags survive now.

**Verify — dry run, 5 windows, 35B on :18081, `--schema v2`:**
- parse-fail 0, every row valid v2 JSON, `ok: true` on all 5,
  facts/tags pass the fact gate (e.g. `revealed_as`, `recruited`, tags like `deictic`,
  `production` survive),
- coverage after the coverage-repair turn: 36/41 narrative sentences covered (88%),
  vs the 37.1% event-layer baseline on the reviewed windows,
- caveat recorded: `other_verb` share on the dry sample is 20-60% (target <10%) —
  the fact vocabulary needs a promotion pass after the pilot (proposal logged in
  `plan/FACT_LAYER_PROPOSALS_FOR_CLAUDE.md`), not a drop reason for a window.

`FACT_LAYER_PROPOSALS_FOR_CLAUDE.md` (store round-trip defects in facts.py etc.) is
untracked but complete; this commit brings it in.

**Next:** Step 4 — 60-window pilot on b7-b806 with event F1 vs Claude's reviewed rows,
fact precision, coverage.

---

## STEP 4 — 60-window pilot on b7–b806 — **PARTIAL, one prompt revision in, evidence logged**

Run 1 (`/tmp/opencode/pilot60.jsonl`, doc = v2 as committed):
- event P/R/F1 vs Claude's reviewed rows: **P .658 / R .527 / F1 .585**, exact 19/60
- original v1 35B+doc on the same 60: P .711 / R .445 / F1 .547 → v2 adds recall, loses some precision
- coverage: 245/254 narrative sentences covered (96.5%)
- facts/window 4.8, tags 80, `other_verb` share 40.8% (target <10%)
- spot hand-check of ~30 fact rows: mostly usable (alias/membership/modality rows read sensibly);
  two recurring flaws: `other_verb` targets an entity instead of the doc's verb-in-object shape,
  and a few stretch relations (`rival_of` from "faced off once")

Doc revision 1: added the partition rule to v2 SECTION B ("an event the 12 verbs express
STAYS an event; no twin rows"), then re-ran the same 60 (`/tmp/opencode/pilot60b.jsonl`):
- event P/R/F1: **P .614 / R .516 / F1 .561**, exact 26/60 — recall unchanged, precision down
- coverage: 244/254 (96.1%); tags working; no event-verb row ever leaked into facts (0 rows)

**Analysis (why F1 did not move):** the remaining deltas vs gold are end-canonicalization
("Stark" vs "Tony Stark", "Monet" vs "Monet St. Croix", "Bishop" vs "Lucas Bishop",
"hanger" as a place end) and a handful of name-form preferences — i.e. the same end-error
class the 35B already had, not events demoted into facts (0 of those). The v2 pass itself
beats the v1 single pass on the same windows (.561–.585 vs .547). Coverage is closed
(~96% vs the 37% baseline).

**Against the stop rule in FACT_LAYER_EXECUTION.md:** event F1 < .60 and coverage-miss < 5%
on both runs; one of two allowed prompt revisions used. The F1 shortfall is not prompt-shape.
Waiting on the owner for the call: accept the pilot and go to step 5 (add-only over
b1–b806), or one more revision targeting end-canonicalization (e.g. a stronger "one
name per person" reminder in the event-layer hints). The 35B stays up on :18081 for
whichever is chosen. `--schema v2` defaults to the 35B now, so no flag changes when
resuming.

---

## STEP 5+6 — launched 2026-10-07 ~15:30 on the 35B (owner directive; 27B coding is complete)

No model switch per SWITCHPOINT: the 35B on :18081 (`serve_35b_64k.sh`, 8 lanes,
`qwen3.6-35b-a3b-ninfer`) now serves windowing; the 27B on :18080 stays down until its
provider is needed again (it was only the council/execution agent; its coding work —
steps 1–3 — is committed and done).

- STEP 5 (add-only): b1–b806, events frozen = Claude's reviewed rows (`big_audit.jsonl`
  applied), model writes only `facts`/`tags`, provenance `claude-events+v2-facts`.
  Output: `series/universal/training/big/labels_v2.jsonl`. PID 23833, ~7 windows/min
  expected (add-only spends 1–2 turns instead of 3).
- STEP 6 (full v2 from 0): b807–b5405 (4,599 windows), same v2 prompt with hints +
  repair + coverage-repair, provenance `v2-full`, appended to the same file. ~5
  windows/min expected → the first ~5,405-line `labels_v2` closes this phase.
- Next phase after that: the same full v2 over the remaining selection toward the
  12,000-window training target.

## CRASH + restart (2026-10-07 ~17:10)

Both v2 runs died on one bug: `fact_gate._end_ok` read `vrw.PLACE_LIKE`, which does
not exist on `verify_row_wiki` (the gate has its own `PLACE_LIKE`; line 173 uses it).
Crashed the add-only pass at 387/806 and the full pass at 298/4599. Fixed to the local
`PLACE_LIKE` (commit 58c4620f, 46 pytest still green), and BOTH runs were resumed with the
same command into the same file — id-level dedup means the 685 pre-crash rows are kept and
not re-derived. labels_v2.jsonl is therefore continuous: 387 claude-events+v2-facts and 298
v2-full from the crashed attempt, plus the resumed files. Verified: no worker currently
processes an id that already has a row.

## Continuation past the ~5,400 mark (owner 2026-10-07, ~21:10)

- Added orchestrator `chain3` (PID 34941): when the b807–b5405 run (PID 32143) exits,
  a full-v2 pass (events + facts + tags, the same windowing and the fact layer
  together, `provenance v2-full`) starts on the remaining **8,595** selection windows
  (`/tmp/opencode/batchC_ids.jsonl` = big_in ids neither in `labels.jsonl` nor
  `labels_v2.jsonl`, in input order). Both layers ride in every output row.
- No separate v1 labelling is needed afterwards: batch C emits the event rows the
  9B trains on AND the fact rows — one pass, both tasks.

## CHECKPOINT — STOPPED 2026-10-07 ~22:30 (owner: "checkpoint here and stop everything")

Killed by exact PID: chain2 (30192/30194), batch-C chain (34941/34943), the full-v2
runner (32143), and the 35B server (16226/16227). GPU freed (330 MiB).

State at stop:
- `series/universal/training/big/labels_v2.jsonl` — 2,051 rows / 5,405 target for phase 6.
  806 `claude-events+v2-facts` (Step 5 complete) + ~1,245 `v2-full` (Step 6, 2,029/5,405
  per the last status line, 5.2 w/min, parse-fail 0, 140 gate-dropped rows).
- Next, on resume: Step 6 finishes b807–b5405 (its id list has 4,599 ids; dedup against
  the output means rows are never re-derived), then batch C over the remaining 8,595
  selection windows (`/tmp/opencode/batchC_ids.jsonl`).

Resume commands (exactly what was killed):
```
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
setsid nohup bash <(cat tools../) /dev/null  # see chain3_resume below
# Step 6 first (only if labels_v2.jsonl still < 5405):
SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine scriptengine/.venv/bin/python tools/train/label_single.py --schema v2 \
  --in /home/goblin/ScriptEngine/series/marvel/training/labels/big_in.jsonl \
  --in /home/goblin/ScriptEngine/series/mcu/training/labels/big_in.jsonl \
  --out /home/goblin/ScriptEngine/series/universal/training/big/labels_v2.jsonl \
  --ids /tmp/opencode/b807_5405_ids.jsonl --workers 8 --provenance v2-full
# then batch C:
  --ids /tmp/opencode/batchC_ids.jsonl --workers 8 --provenance v2-full
```
with /tmp/opencode/serve_35b_64k-style: `tools/train/ops/serve_35b_64k.sh` to bring the
35B back on :18081.
