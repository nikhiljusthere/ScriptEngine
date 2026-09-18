# Council #35 — CSM 100% Phase-2 D6 extraction-leg design lock (2026-09-18)

Council #35 of the CSM 100% campaign. Sequential, one agent at a time
(owner rule 2026-09-08, supersedes the parallel convention): 5 advisors →
5 reviewers (blind to each other's positions) → chairman, each in a fresh
context, no shared transcript. This file is the complete on-disk record
(positions, critiques, ruling) — no separate digest receipts; the raw
per-agent outputs live in the opencode session transcripts of the day.

**De-anonymization (fixed at deployment):** A = Outsider, B = Executor,
C = Contrarian, D = First-Principles, E = Expansive; R1 = Rigor,
R2 = Practicality, R3 = Risk, R4 = Voice/Clarity, R5 = Stakeholder.

## Framed question

**The D6 extraction-leg design lock.** How should the D6 extraction leg
be designed and executed so that it closes what it owns (204 open rows:
22 census-v1 floor + 134 set/relation + 42 new dim + 6 ability-pool) in a
pre-registered, minimal, testable scope?

- **(i) Minimal floor close:** D6 = a targeted `events-extract` over only
  the pages/sections the 22 floor rows need (19 subjects); the 134 setrel
  pages (424 questions) + 42 dim + 6 abl stay documented design limits
  with manual wiki cross-check (the writer-facing statement already
  issued says exactly this: "424 known failures with no closer until D6"
  for setrel, "22 extraction-gated facts stay missing until Phase 2").
- **(ii) Plan A22 default (P2.3b):** the full meaning-layer pass —
  `events-extract` over the red class ∪ a pre-registered green-class
  sample (N panel rows per green dimension, frozen before extraction) so
  the comprehension step fires even when reds = 0; pre-registered pass
  test = "same 400-gate + reds green post-extraction + 200-row held-out
  OOS"; re-grade the p23 bank + recount the census; the 134 setrel rows
  get claimed only insofar as extraction can actually close them (rest
  documented limit — setrel enumeration is a retrieval-layer limitation:
  "the engine retrieves single candidates and cannot enumerate sets").
- **(iii) Full-ownership:** D6 claims all 204 rows; extraction + 5.4
  re-adjudication + targeted re-crawl for the CONTENT rows whose facts
  are not in the crawl (e.g. `csm-dim-abl-01` Yoru, `csm-dim-caus-03`
  Asa Mitaka — triage CONTENT/PARTIAL, `recovered_by` none).

Sub-decisions the lock must settle:

1. **Scope**: (i) / (ii) / (iii); the green-sample N if (ii).
2. **Per-row lever map**: which rows extraction closes, which 5.4
   re-adjudication, which targeted re-crawl, which stay documented
   design limits (verify, don't assume, whether extraction can close
   setrel enumeration).
3. **Pre-registered closure criteria**: the pass test, p23 re-grade,
   census recount, A20 stamp rule (register diff; regression voids the
   stamp), the four standing gates re-run at fix-class closure.
4. **Window mechanics**: the dedicated-GPU window (stop `:8000`, Qwen
   100k owns the card, `nvidia-smi` verify model-only + ~7 GB free,
   `--dry-run` records the scope plan, `--workers` start value,
   per-page state-based resume, post-extraction `index` rebuild for the
   derived layers, model-unloaded side session for the post-extraction
   gates per GATE.md W order).
5. **P6 boundary**: does the lock pre-register the cross-corpus method
   (Census v1 schema + grader + 200-row held-out) so the 7-wiki rollout
   inherits it, or does the §7 addendum stand alone (separate artifact,
   due 2026-09-25) and the 7-wiki rollout remain a separate future
   campaign decision?

**Stakes:** the JJK/CSM shared bar and the P6 measurement foundation
(council #34 R3: an under-scoped method propagates ×7 and is hard to
roll back); 204 open rows with named closers; campaign close vs.
campaign extension; the owner's writer-facing statement.

## Inputs verified on disk (fact base, 2026-09-18)

- Campaign state: CSM Phase 1 closed 2026-09-17 (PHASE_A_COMPLETE @
  `407c016`, PHASE_B_COMPLETE @`2419a01`); JJK 100% baseline-exact, the
  reference no CSM change may regress; four standing gates re-run at
  each fix-class closure (Ruling 5e: a known +N test delta alone does
  not re-run them).
- Open-set register `reports/csm/census_v1_floor_triage.jsonl`:
  **233 rows** = 134 setrel + 42 dim + 6 abl + 16 empty + 22 floor +
  10 bydesign + 3 r1blast (one-pager `census_v1_open_population.md`,
  committed @`da599fd`). D6-owned buckets: 134 + 42 + 6 + 22 = 204 rows
  (16 empty struck per #34 R2; bydesign/r1blast not D6-owned).
- 22 floor rows: 21 `csm-dim-*` (8 arc-narrative, 5 state-over-time,
  6 ability, 1 appearance, 1 causality) + `csm-char-04` (Makima
  abilities, 7/8; the missing 8th = "Contract with the Prime Minister of
  Japan"). Triage classes: 17 ROUTING / 2 CONTENT (abl-01 Yoru,
  caus-03 Asa Mitaka; `recovered_by` none) / 3 PARTIAL (abl-02, abl-09,
  char-04). All `root_cause` = "extraction-gated (D6 census floor; R-7
  close re-sweep 2026-09-10)"; `closer` = "D6 extraction / 5.4
  re-adjudication"; `owning_phase` = Phase-2 (D6).
- 134 setrel pages = 424 failing set/relation questions (affiliations
  109 · named techniques 75 · enemies 55 · allies 49 · aliases 39 ·
  superiors 27 · subordinates 23 · romances 10 · families 9 · friends
  8 · rivals 6 · members 6 · mentors 3 · students 2 · creators 1 ·
  creations 1 · employees 1). Council #33: "not a router lever; R-9
  absorbed, no-fire"; register row: closer "D6 set/relation extraction",
  re-test "re-run D36 page-run after D6".
- p23 widened bank: **486 rows, 417 MECH_GREEN (85.8%) / 69 RED**
  (21 floor-dim + 42 new-dim + 6 ability-pool).
- Extraction state (`series/csm/facts.db`): `relations` 748 +
  `abilities` 376 already extracted; **`events` 0, `semantics` 0,
  `meaning` 0** → D6 is CSM's first `events-extract` pass; the derived
  `meaning`/`semantics` layers rebuild at `index` (CLI L1096/1156:
  "derived model layers (events, meaning)").
- `events-extract` (`scriptengine/cli.py` L640;
  `scriptengine/ingest/events.py`, PROMPT_VERSION
  events-2026-09-05.3): `--scope placement|corpus|all` (placement =
  arc/event/battle set; corpus = narrative sections naming ≥2
  characters; all = union, required for a `--refresh` run), `--workers
  N`, `--dry-run` (records the scope plan, calls no model), per-page
  state-based resume (skips current answers); writes the `events`
  table only.
- Plan (`plan/CSM_2PHASE_PLAN.md` L273–414): A22 default path
  de-contingents P2.3 as the numbered D6 item (P2.3b): "extract the
  meaning layer against the red class ∪ a pre-registered green-class
  sample (N panel rows per green dimension, frozen before extraction)
  so the step fires even when reds = 0"; pre-registered pass test =
  "same 400-gate + reds green post-extraction + 200-row held-out OOS";
  A19: the sanctioned GPU mechanism is the tier-1 chain (no-flip
  batched side sessions in Qwen's quiet window); the gpu-handoff
  (262k→100k flip) is reserved for when VRAM forces a dial-down.
- Council #34 (`reports/csm/COUNCIL_csm_100p.md`): the D6 design lock +
  7-wiki rollout were **refused pre-register** (R3's under-scoped ×7
  risk), "they return post-register" — the register is on disk, so the
  lock is now owed. R5 issued the writer-facing statement: setrel 424
  "no closer until D6"; the 22 extraction-gated facts stay missing
  until Phase 2.
- GPU standing state: Qwen 100k (`--kv-capacity 102400`, ~24.9 GB) +
  `:8000` CUDA (~5.9 GB) co-located on the 32 GB card. Hard rule: a
  heavy LLM batch (`events-extract`) keeps the card dedicated to the
  model — stop `:8000` (or run it on CPU) first, confirm `nvidia-smi`
  shows only the model process and ~7 GB free before launching.
  Post-extraction gates run in a model-unloaded side session per the
  GATE.md W order.
- P6 boundary: the P6 §7 method addendum (Census v1 schema + grader +
  200-row held-out into `plan/Plan_to_perfection.md` §7 "Order of
work") is a separate artifact due ≤2026-09-25 (drift pointer filed);
   the 7-wiki rollout is a separate future campaign decision.

## Advisor positions (A–E, in deploy order)

### A — Outsider (ses_f4dc4a368f)
**(ii) + amendments.**
- **Scope:** extraction over the 69 red rows ∪ a pre-registered green
  sample (N=5 per green dimension, ~40–50 rows, stratified by question
  type, draw recorded in the register *before* any model call). The
  sample's only job is catching green→red flips from the index rebuild;
  it is NOT corpus scope.
- **Amendment 1 (zero-cost offline triage before the GPU window):** the
  facts DB already holds 748 relations + 1,079 aliases + 376 abilities,
  and retrieval already surfaces LLM-extracted relation rows. Test per
  question whether the expected set is recoverable from those tables or
  the crawl text. Pre-register the split into the lever map:
  facts-present-but-question-fails → closer is roster/enumeration
  (retrieval, no GPU); facts-absent → extraction; neither → documented
  limit. D6 claims the 134 setrel only where triage says extraction
  closes them.
- **Amendment 2 (P6):** the lock pre-registers the METHOD (Census v1
  schema + grader + 200-row held-out protocol) as the P6 seed; the §7
  method addendum (due 2026-09-25) stands alone; the 7-wiki rollout
  stays a separate decision — the ×7 risk is about method, not scope.
- **Pass test:** same 400-gate + 21 floor reds green + 200-row held-out
  OOS ≥ pre-extraction + p23 bank re-grade + census recount; four
  standing gates at fix-class closure; A20 stamps against the register
  diff.
- **Window:** stop :8000 (or run it CPU), LLM 100k owns the card,
  `--dry-run` records the scope plan first, workers 2 (scale only if
  p95 latency holds), per-page state resume, post-extraction index
  rebuild, gates in a model-unloaded side session.
- **NOT doing:** (iii)'s targeted re-crawl (the 2 CONTENT rows — Yoru,
  Asa Mitaka — stay documented limits with a manual wiki cross-check)
  and no green sample beyond the 5-per-dimension net.

### B — Executor (ses_f4dc34ae7f)
**(ii) + CONTENT-row pre-check ("A22 default + CONTENT pre-check").**
- **Scope:** `--scope corpus` — claims the CSM placement set is empty
  (placement_pages = 0), corpus = 235 pages / 412 sections, "the only
  native scope"; the red ∪ green subjects are a subset; section-level
  extraction with per-page resume makes the pass resumable and
  idempotent.
- **Green sample N = 5 per green dimension** (6 dims = 30 rows),
  frozen in the gate file before the model call; re-grade set = 69
  reds ∪ 30 green ∪ 200-row held-out.
- **Levers:** 22 floor (17 routing / 3 partial) + 42 dim + 6 abl →
  extraction + index rebuild of the derived layers + 5.4
  re-adjudication; the 2 CONTENT rows (Yoru, Asa) get a raw-crawl
  pre-check first (claims the needed sections are already in the
  crawl) with one targeted re-crawl only if a fact is genuinely absent;
  the 16 empty + 10 by-design + 3 r1-blast rows stay struck/stamped,
  out of scope; the 134 setrel are claimed only if a post-extraction
  page-run re-test closes them, the rest documented as retrieval-layer
  limits.
- **Closure (pre-registered before the window opens):** same 400-gate +
  ALL 69 p23 reds green post-extraction (recounted from raw jsonl) +
  200-row held-out OOS + p23 486-row re-grade + page-run re-run on the
  134 + A20 stamps against the register diff (regression voids) + four
  standing gates at fix-class closure with the baseline-corpus diff
  empty.
- **Window:** checkpoint → LLM 100k owns the card → stop :8000 (or move
  it CPU) → `nvidia-smi`: model-only + ~7 GB free → `--dry-run` records
  the 235-page scope plan → workers 2 (scale to 4 only if the model
  stays healthy) → index rebuild → post-extraction gates in a
  model-unloaded CPU side session → closure council.
- **P6:** the lock pre-registers the method surface (Census v1 + grader
  + 200-row held-out arm) so the §7 addendum and a future 7-wiki
  rollout inherit it; the wiki list stays a separate future decision.
- **NOT doing:** (i)'s 19-subject targeted run (would need a new
  `--pages` flag the plan never pre-registered, leaving 182 register
  rows without the layer they are gated on) and (iii) blanket
  re-crawl + 5.4 over all 204.

### C — Contrarian (ses_f4dbe7a3df; first deploy ses_f4dc201f0f failed → retry)
**(i) re-cut to a lever-split — D6 owns the 70 extraction-gated rows
(22 floor + 42 dim + 6 abl), not 204.**
- The register's own root-cause labels are the tell: the 70 rows read
  "extraction-gated" but all 134 setrel rows read "set/relation-
  completeness residual (box-ranking / width / state-over-time)".
  "Box-ranking" is a retrieval defect (the answer page exists and ranks
  low), and extraction adds facts but does not re-rank.
- So (ii)/(iii) — which pre-register "post-extraction reds turn green"
  as the pass test over the WHOLE red class — will fail on the 134 for
  a reason the extraction lever cannot address; you then either inflate
  the green sample N until the test passes (over-scope) or declare the
  134 a floor (under-scope). The mis-scoped method is exactly what a
  7-wiki rollout would inherit ×7.
- **Lock:** the events/relations/abilities extractors over the 70 rows,
  dedicated-GPU window (LLM model owns the whole card; `--dry-run`
  records the scope plan; workers start 4; per-page resume); the
  pre-registered closure test runs on the 70 ONLY: same 400-gate +
  reds-green + 200-row held-out OOS on the frozen green sample.
- Re-classify the 134 setrel to a named ranking/retrieval leg (D7) or
  a documented limit; their re-test trigger is a ranking fix, not D6.
- Do NOT bundle the 134 into D6's pass test, and do NOT pre-register the
  7-wiki rollout until this lever-split is verified green on this
  corpus.

### D — First-Principles (ses_f4dbc9799f)
**(ii) minus the green sample: extract the 70-row red class (69 p23
reds + 1 ability row) + targeted re-crawl of the 2 CONTENT rows; the
green sample becomes a null-branch rule, not a frozen N.**
- First principles: D6's value is "failing questions stop failing"; the
  hypothesis is "extraction closes the extraction-gated rows", and the
  70-row red class is exactly the pre-registered failing population.
- Setrel is a different animal: set enumeration is a retrieval-layer
  limit (single-candidate retrieval), so D6 RE-TESTS (re-run the
  page-run), claims what closes with receipts, and documents the rest.
- **Scope:** (1) targeted re-crawl of the 2 CONTENT rows (Yoru, Asa
  Mitaka — recovery is impossible from a crawl that lacks the fact);
  (2) events-extract over the red class's DISTINCT PAGES — frozen page
  list, dry-run receipt, and a minimal new `--pages` option (verified:
  no page-targeting option exists yet; default behavior unchanged);
  (3) 5.4 re-adjudication on the 3 PARTIAL rows.
- **No green sample:** its job (firing comprehension on green rows) is
  already carried by the 200-row held-out OOS (frozen at lock) + the
  four standing gates; green rows already pass.
- **Null branch (re-adjudication closes all reds):** pre-registered
  rule — a council re-decides N with receipts on disk; a frozen N now
  is a guess.
- **Closure (pre-registered):** p23 re-grade (69 reds green or
  individually triaged) + 200-row held-out OOS + same 400-gate + census
  recount + A20 stamp + four standing gates at fix-class closure.
- **Window:** drop :8000 to CPU; LLM 100k owns the card; `nvidia-smi`
  confirms model-only + ~7 GB free; dry-run records the plan; workers 2
  start, state-based resume; index rebuild lands derived layers; gates +
  re-grade in a model-unloaded side session.
- **P6:** the lock names the method artifacts (census v1 schema +
  grader + held-out harness) as pre-registered deliverables; the 7-wiki
  rollout stays a separate future decision.
- **NOT doing:** full-corpus extraction, a setrel closure claim, or the
  rollout in this lock.

### E — Expansive (ses_f4dba5edbffeT5O2)
**(iii) with (ii)'s green sample — full ownership, pre-registered, P6
method in the lock.**
- **Lever map:** (1) pre-window re-crawl of the 5 CONTENT/PARTIAL floor
  rows (Yoru, Asa Mitaka ×2, Denji, Makima) → re-index; ~4 pages, no
  GPU — without it, 2 of the 22 floor rows can never close (facts
  absent from the crawl); (2) `events-extract --scope all` over the
  frozen dry-run plan: 69 reds ∪ N=10 per green dimension (57 rows,
  capped; frozen pre-extraction) — the comprehension step fires even at
  0 reds; (3) 5.4 re-adjudication: p23 re-grade + page-run re-run,
  mechanical, model-unloaded side session.
- **Claim = a CLASSIFICATION claim, not "zero reds":** each of the 204
  rows closes verified, or as a NAMED design limit (setrel: single-
  candidate retrieval cannot enumerate sets — retrieval-layer, not a D6
  lever), or re-opens with a new root cause; no silent residuals.
- **Pass test:** 400-gate + reds green post-extraction + 200-row held-
  out OOS (frozen pre-extraction) + p23 re-grade + census recount from
  raw jsonl + four standing gates at fix-class closure; A20 stamps
  against the register diff.
- **Window:** one dedicated GPU window — stop :8000, LLM 100k owns the
  card, `nvidia-smi` model-only + ~7 GB verified; workers 2; state-
  based resume covers OOM (a prior full-corpus run lost 508/524 pages
  when the model died mid-run); then index rebuild, model-unloaded side
  session for re-grade + gates.
- **P6:** the lock carries the cross-corpus method (Census v1 schema +
  grader + held-out spec) in the lock document, so a 7-wiki rollout
  inherits a closed method; the rollout itself stays a separate campaign
  decision via the §7 addendum due 2026-09-25.
- **NOT doing:** corpus re-crawl (only the 4 named pages), an
  enumeration rewrite in D6 (new fix class, its own council), a second
  GPU window, the rollout itself, or a green sample without the held-
  out.

## Blind peer reviews (R1–R5, in deploy order)

### R1 — Rigor (ses_f4db77130f)
Strongest = D; weakest = E.
- **A:** (a) the pass test gates on "21 floor reds" but the floor is 22
  named — which row is out? (b) the setrel triage is not a FROZEN
  protocol (recoverability test undefined, per-row buckets unsigned) →
  the lever map is post-hoc without a pre-registered recoverability
  test; (c) the p23 re-grade has no acceptance threshold (green count?
  all-69? noise band?), and N=5/dim has no stated detection power if
  the rebuild flips 1 of ~40 green rows.
- **B:** (a) the 134 "close-or-document" re-test is a no-fail test
  ("the rest documented as a limit" can never make B fail) — without a
  frozen cap, "retrieval-layer limit" is a catch-all for any red that
  stays red; (b) "all 69 reds green" is a hard bar while B's own 17
  floor "routing" rows (extraction can't close them) sit in the same
  set — is the "individually triaged" escape pre-registered or post-hoc?
  (c) green N=30 vs the 200-row OOS: is the 30 a subset of the 200 or
  additive, and "OOS ≥ pre" — what noise band (1-of-200 drop = fail or
  noise?).
- **C:** (a) the premise "extraction adds facts but does not re-rank"
  is asserted, not verified (the index rebuild may re-embed/re-rank →
  new facts could close some of the 134, making the D7 re-classification
  premature); (b) the 70-row scope includes the 2 CONTENT rows whose
  facts are absent from the crawl — extraction alone cannot close them.
- **D:** (a) the 200-row held-out's green composition (drawn from a red-
  skewed population?) — if it holds no green rows it detects no green→red
  flip, so "minus the green sample" drops the only flip arm; (b)
  "individually triaged" is an unfrozen protocol; (c) the `--pages`
  spec (frozen list, default-unchanged test) is unfrozen.
- **E:** (a) internal contradiction — a classification claim ("each
  row closes, OR a named limit, OR re-opens") vs the pass test "reds
  green post-extraction"; (b) "N=10 per green dimension (57 rows,
  capped)" — 10×6 = 60, so "capped" is an undefined rule; (c) no
  stated incremental closure over D.

### R2 — Practicality (ses_f4db597e1ffezNBm5pvosFTVaM)
Most executable = D; least = E.
- **A:** the "ZERO-COST" triage has no existing tool — the per-row
  recoverability harness (join expected-set members against 748
  relations / 1,079 aliases / 376 abilities / crawl wikitext) must be
  written; who writes it, how many CPU-hours, and is it a hard pre-
  window blocker? The green draw — existing register command or a
  manual JSON edit?
- **B:** is `--scope corpus` native today or a plan artifact (verify
  before the window)? does a per-page checkpoint file exist for the
  235-page pass? what is the wall-clock at workers 2 on a 100k
  context? which tool makes the CONTENT pre-check claim reproducible?
- **C:** "extractors over the 70 rows" needs a row→page mapping + a
  page-targeting flag that does not exist → who writes it? does
  workers 4 fit the 100k profile's ~7–8 GB headroom (A/B/D start at 2)?
  who relabels the 134 to D7 (a council vote or a unilateral register
  edit)?
- **D:** the new `--pages` flag — how many lines/files, does it interact
  with the resume state, and does "default unchanged" ship with a gate
  test? the targeted re-crawl — does crawl skip existing pages (so it
  needs delete-then-crawl or a force flag)? does re-crawl + re-index
  touch a JJK-shared derived layer? the null branch — when exactly does
  the council re-decide N, and does it block the A20 stamp?
- **E:** `--scope all` over "69 ∪ 57" is a ROW SET, not a scope value
  → E inherits D's new-flag work while paying the full 235-page GPU
  time; if the 134 cannot close via extraction, full scope pays B's
  cost for classification, not closure; is the re-crawl CSM-scoped so
  the JJK baseline shows zero regression?

### R3 — Risk (ses_f4db4597bffekaj2oNhXxsJ7j0)
Strongest = C; weakest = E.
- **A:** the red∪green scope needs a page-targeting flag the CLI lacks
  → the JJK zero-regression proof + 4-gate re-run that A's "NOT doing"
  omits? the offline triage pre-registers the lever split before the
  model call — is a mis-triage (a ranking-defect row locked to
  "extraction") undoable or inherited ×7? the 2 CONTENT "documented
  limits with a manual cross-check" are non-reproducible — do they
  survive ×7?
- **B:** what receipt proves corpus ⊇ red∪green before the model call
  (if placement is non-zero, B under-scopes and 182 rows go unlayered)?
  is "documented limit" pre-registered so A20's void-on-regression does
  not void when the 134 stay red? what is the exact A20 void predicate
  (which regressions void)? workers 2→4 at a 100k KV pre-reserve —
  OOM headroom, and is per-page resume atomic (no half-page garbage fed
  into the index rebuild)? is the method surface closed enough that ×7
  inherits a complete method?
- **C:** the 70-row scope needs page-targeting → a new flag (JJK
  regression + 4-gate re-run) or a native corpus scope with only the 70
  pass-tested? C starts workers 4 WITHOUT stating stopping :8000 or an
  `nvidia-smi` pre-check (the 508/524 loss was a co-location OOM) —
  verify model-only + ~7 GB free? OOM headroom at 4? on a crash, is
  resume atomic or does it leave half-pages the rebuild ingests as
  garbage? deferring ×7 is right, but C opens a D7 that may become a
  silent residual — does opening D7 while deferring ×7 lower total
  campaign risk?
- **D:** the new `--pages` flag is an engine change: a JJK zero-
  regression proof (4 gates + baseline diff) that an additive flag does
  not perturb the native corpus/all path, and does it force a SECOND
  gate cycle (re-opening risk)? dropping the green sample leaves a
  finite-power 200-row held-out + 4 gates — if the rebuild flips a
  green row outside the held-out, what catches it? is a method without
  a flip-detection arm pre-registered as a hole ×7 inherits? the null
  branch re-opens a council in the BEST case (all reds close) — a
  pre-registered stall? the 2-page re-crawl + re-index: zero JJK
  regression, resumable?
- **E:** the full method locked IN the lock document is the strongest,
  least-reversible ×7 lock — what is the rollback path for a flawed
  method, and a pre-registered escape hatch? `--scope all` + the 4-page
  re-crawl → a re-index BEFORE the window is a baseline mutation: JJK
  zero-regression before the model call? does the re-crawl invalidate
  the pre-extraction 200-row held-out baseline E freezes? the
  "classification claim" pass test — a pre-registered predicate for
  "re-open"? can E game a hard row into a "named design limit" to go
  green while leaving a residual? is A20 void-on-regression strong
  enough to catch a mis-classified limit?

### R4 — Voice/Clarity (ses_f4db20e37ffeiJ8tPkEKC6coxZ)
Strongest = B; weakest = C.
- **A:** "recoverable from those tables or the crawl text" is two
  implementations (a text-grep vs a structured match) — the operational
  definition of "recoverable" is missing, and who signs the split? the
  triage assigns "extraction" as closer for setrel rows whose pages are
  not in the red∪green scope → which pages, and the "~40–50 rows"
  number is wrong if more? the sample's stated job is catching green→red
  flips yet the pass test has no flip check (a caught flip = fail or a
  note?), and "21 floor reds" vs the frozen 22: which row is missing?
- **B:** "22 floor (17 routing / 3 partial)" sums to 20, not 22 — the 2
  CONTENT rows sit outside the decomposition, and the register does not
  reconstruct; "the rest documented as retrieval-layer limits" is not
  NAMED (name the defect, the owning leg, the closer); A20 "(regression
  voids)" — regression against what (JJK 4-gates? a CSM red turning
  red? a held-out drop?) — define the void set or the stamp is
  undecidable; "idempotent" for LLM section-extraction is wrong (a re-
  run overwrites with fresh generations).
- **C:** the pass test runs "the 200-row held-out OOS on the frozen
  green sample" but the scope is the 70 red rows and C pre-registers no
  green sample → where does the 200-row set come from, what threshold,
  is it frozen? the test references an input the position excludes.
  "Re-classify the 134 to a named leg (D7) OR a documented limit" is an
  "or" with no decision rule. "Workers start 4" vs 2 everywhere else +
  the 508/524 OOM history — what justifies 4, what is the abort check?
  "reds-green" over the 70 has no null branch (65 closed = fail or per-
  row triage?).
- **D:** "69 reds green OR individually triaged" is a back door unless
  triage is defined to yield a named limit or a new root cause — define
  the buckets. The null branch "council re-decides N" — N is the green
  sample D dropped; a post-hoc N after the red results are in is
  exactly the post-hoc draw pre-registration forbids (evidence
  selection) — pre-register the sample or delete the branch. "200-row
  held-out OOS (frozen at lock)" — by what mechanism, drawn from how
  many green rows? if the green population is in the thousands, 200 may
  not carry the flip-catch job the dropped sample carried.
- **E:** "`--scope all` … 69 reds ∪ N=10/dim (57 rows, capped)" is one
  sentence, two scopes (full-corpus extraction vs the re-grade set) —
  separate them; "57 rows, capped" — capped by what, over which
  dimensions? the pass test "reds green post-extraction" vs the claim
  allowing rows to close "as a NAMED design limit" = two readings (all
  69 green, or all reds classified) — rewrite: "all 69 closed: green OR
  named limit with defect name + owning leg". "The comprehension step
  fires even at 0 reds" — what IS the comprehension step (undefined)?
  "re-opens with a new root cause" — into which scope, owned by whom?
  a re-opened row with no destination is a silent residual by another
  name.

### R5 — Stakeholder (ses_f4db0b5d9ffedQLAOCFQbi0NEK)
Best deal for the owner = A; worst = E.
- **A:** who signs the "facts-present/absent" triage verdict, and is the
  receipt recorded *before* the model call so a wrong triage is
  attributable to triage, not extraction? if triage mislabels 30 of the
  134 as "extraction closes" and they don't, how much of the leg's
  receipts are void? if triage says most of the 134 are "documented
  limits," what pre-registered bar does the owner accept before 100+
  rows are stamped (a named defect per limit, or a blanket "facts
  absent")? does the writer get a fix schedule or a wall? the 5/dim
  sample is a tripwire only — if the rebuild flips green→red outside the
  sample, which gate catches it and what is the re-run cost?
- **B:** the 235-page corpus scope is the only position spending GPU-
  hours on pages that may close zero rows — what abort checkpoint exists
  after the red-class pages land (if the corpus pages add no closures,
  does the leg stop and report, or burn the window)? the 134 "documented
  as retrieval-layer limits" — named with a defect owner + a next leg
  (D7?), or just stamped? the writer's largest class ends at
  "documented" — what exactly does the owner sign against that? "the
  only native scope" rests on a CSM-specific claim (placement set
  empty) — does the lock document that the method's corpus-scope
  assumption does not transfer to a 7-wiki rollout, or does the
  pre-registered method seed inherit a corpus-shaped scope other wikis
  cannot assume?
- **C:** D6 delivers 70 of 204 and kicks the 134 to a D7 that does not
  exist (no schedule, no owner, no closure criteria) — what does the
  owner sign: the public 204-row commitment with 134 now unscheduled?
  is D7 pre-registered with its own lock, or just a label? the
  re-classification is label-based — what per-row evidence shows none
  of the 134 are actually extraction-gated? if 20 misroute to D7, its
  ranking fix cannot close them and they come back — what is the
  re-attribution cost? with no method surface pre-registered, the §7
  addendum (due 2026-09-25) has nothing to document — does the owner
  get a clean P6 decision surface by that date, or a hollow addendum
  that re-litigates the 7-wiki rollout from zero?
- **D:** dropping the frozen green sample: the 200-row held-out tests
  method OOS, not that the rebuild broke green rows — what catches a
  silent green→red flip outside the 69 reds (a GPU saving or a
  regression blind spot the four gates cannot see)? the new `--pages`
  option is untested surface on a first-ever run — is it verified
  against default behavior with receipts, and if it carries a bug, do
  the leg's receipts invalidate and force a re-run? the null branch =
  "council re-decides N" — a pre-registered escape valve with a stated
  cost, or a hidden reopening the owner cannot plan around? if the reds
  do not close, what is the wall-clock + GPU cost of the re-council?
- **E:** "full ownership" signs all 204 yet the 134 land as "named
  design limits" with no fix path, no owner, no next leg (the
  enumeration rewrite is "its own council") — what does the owner
  actually sign: ~75 closures + 134 open-ended limits + a future
  council, i.e. the set's biggest over-promise? N=10/dim vs A's ~40–50:
  what marginal value can the owner NAME for the extra green rows (if
  the 200-row held-out already carries the OOS job, is the extra spend
  buying tripwires the owner already pays for)? the pre-window
  re-crawl of 5 rows mutates the corpus before the window — is the
  400-gate re-baselined post-re-crawl, or is the pre-re-crawl value the
  comparison baseline? which receipts let a distrustful owner audit
  which baseline moved and when?

## Chairman's ruling (de-anonymized, ses_f4daf53e5ffemMdfYaw4eVLov5)

### 1. Verdict
Locked scope: **a (ii) composite — targeted red-class extraction, armed
with a frozen flip-detection green sample and a pre-registered named-
limit register.** Not (iii) full ownership, not blind (i).

Rationale: the 204 rows split into two populations with different
levers. The extraction-gated red class (17 routing + 2 content + 42 dim
+ 6 abl + the setrel/abl rows the pre-window triage marks fact-absent)
closes via extraction + index rebuild + re-grade. Set/relation rows
whose facts already exist close (or don't) in the retrieval layer —
extraction cannot widen enumeration, so (iii) pays full-corpus GPU for
rows the lever cannot move, and C's blind hand-off to a D7 lacks per-
row evidence. The locked design extracts exactly the pages the triage
names, keeps a small frozen green sample to catch rebuild flips, and
closes every residual as a **named limit (defect + owning leg)** — no
ownerless "retrieval-layer limit."

Adopts **D (First-Principles)**, adapted: (a) reinstates **A's** frozen
30-row green sample as the flip arm D dropped (R1/R4/R5 flag the
blind spot on green→red); (b) adds **A's** frozen offline recoverability
triage on the 134 setrel + 6 abl (D's "re-test, document the rest" had
no pre-registered protocol, R1a); (c) imposes **C's** named-limit
discipline (defect + owning leg on every residual, fixing D's
ownerless documentation); (d) deletes D's post-hoc null branch (council
re-deciding N after red results = evidence selection, R4).

### 2. Scope + green-sample N + per-row lever map
- **Extraction scope: a new additive `--pages <frozen-list>` flag, not
  `--scope corpus`.** Minimal change: read a slug list, intersect the
  scope page queue. JJK zero-regression proof (pre-registered, model-
  unloaded, seconds): `--dry-run` on `--scope corpus` with the flag
  absent vs present-with-full-list yields identical scope plans, plus a
  gate test that the flag's default (absent) leaves the native path
  byte-identical. This rides on the standing 4 gates re-run at D6
  closure — **no second gate cycle.** Pre-registered fallback: if the
  dry-run equivalence fails, fall back to native `--scope corpus`
  (longer window, zero JJK regression). Frozen list = distinct pages of
  {69 p23 red, 42 dim, 6 abl, setrel A-bucket, 2 CONTENT}, computed
  post-triage.
- **Green sample: N = 5 per green dimension (6 dims = 30), stratified
  by the 6 green dimensions, drawn by a seeded RNG (seed recorded),
  frozen in the register before the model call (before the dry-run
  receipt).** Job = catch green→red flips from the rebuild.
  **Disjoint from the 200-row held-out OOS** (also frozen pre-
  extraction, disjointness asserted). Flip arm: the 30 rows are
  **always re-graded at closure, never dropped post-hoc**; any
  green→red flip = rebuild void + re-run (pre-registered cost).
- **Per-row lever map (all 204):**
  - **22 floor** (= 17 routing + 3 partial + 2 content, not 21): 17
    routing → extraction; 3 partial → 5.4 re-adjudication (model-
    unloaded); 2 content (Yoru, Asa Mitaka) → targeted re-crawl (pre-
    window, CSM-scoped, no GPU) + extraction.
  - **134 setrel:** frozen offline triage (are the expected set's
    members present in the facts DB [P] / the stored crawl wikitext [T]
    / absent [A]?). P, T → **named limit "single-candidate enumeration
    width (retrieval-layer)", owning leg D7 (ranking/retrieval)**, re-
    tested post-rebuild via page-run (any that close are credited to
    rebuild re-rank, receipted; the rest stay D7 limits). A →
    extraction-gated, into the `--pages` list.
  - **42 dim:** extraction (new dimensions, facts absent by definition).
  - **6 abl:** triage P/T/A; A → extraction; P/T → named limit
    (enumeration width, D7).
  - **Struck rows (16 empty + 10 by-design + 3 r1-blast):** out of
    scope, stamped, unchanged.
- **"Does extraction re-rank?" — ruled:** C's premise holds **for P/T
  setrel rows** (set members already in the crawl; span-recall
  guarantees a chunk; a re-embed cannot widen top-k), so extraction
  does not close them. It does **not** hold for A rows, and the
  rebuild's effect on existing rows is **unverified — so it is not pre-
  litigated.** The settling evidence is the **post-rebuild page-run re-
  run on all 134 (model-unloaded side session)**: any P/T row that
  closes is credited to rebuild re-rank (receipted). This converts C's
  factual claim into an empirical result and protects against the blind
  D7 hand-off (R5: the triage is the per-row evidence).

### 3. Pre-registered closure criteria (the pass test, unambiguous)
- **Every p23 red row (69)** ends as (a) **green** at re-grade (via
  extraction / 5.4 re-adjudication / re-crawl+extraction), or (b)
  **individually triaged to a pre-registered bucket**: bucket 2 =
  named limit (defect + owning leg), bucket 3 = new root cause (new
  register row + owning leg). **No catch-all bucket.** The bar is
  "every red closed **or** named," not "all 69 green."
- **P/T setrel:** each ends as a named limit (defect + D7) or closes
  post-rebuild (receipted). No silent residual.
- **200-row held-out OOS:** post ≥ pre − **2 rows** (1% noise band); a
  3+ drop = fail (rebuild void).
- **30-row green sample:** zero green→red flips; any flip = rebuild
  void + re-run.
- **4 standing gates** (pytest / eval jjk / span-recall jjk / canon-
  run opm) at fix-class closure: JJK baseline diff empty.
- **A20 stamp:** stamped against the **register diff** (the 204-row
  register, pre- vs post-D6). **Void set (pre-registered):** (a) any
  JJK 4-gate regression below baseline; (b) any green-sample / held-out
  flip or OOS drop 3+; (c) an extraction-gated row triaged "extraction
  closes" still red at re-grade (voids that row's receipt only).
  **A named limit does not void the stamp** (declared, owned residual,
  not a regression).
- **Null/exception branches (each with a named cost):**
  1. Flag dry-run not equivalent → fall back to native `--scope corpus`
     (cost: longer window, zero JJK regression).
  2. Green flip or OOS drop 3+ → rebuild void, re-run index rebuild +
     re-grade (cost: one model-unloaded rebuild + re-grade cycle).
  3. An A-bucket row still red at re-grade → individually triaged to
     bucket 2/3 (cost: that row's receipt void; D7 absorbs if
     retrieval-layer).
  4. All reds close (best case) → **no reopening**; the 30-row sample
     is still re-graded; no council re-decision of N.

### 4. GPU-window mechanics (ordered, executable)
1. **Checkpoint:** switchpoint (`plan/SWITCHPOINT.md` + git commit).
2. **Pre-window (model-unloaded, no GPU):** targeted re-crawl of the 2
   CONTENT pages + CSM re-index (JJK untouched, zero-regression
   receipt). Run the frozen triage (P/T/A, receipt in the register).
   Compute the frozen `--pages` list. Run the flag dry-run equivalence
   check (fail → corpus fallback). Freeze the 30-row sample + 200-row
   held-out (seeded, disjoint). Record pre-extraction OOS baseline +
   the 134 page-run.
3. **nvidia-smi pre-check:** stop :8000 (or move to CPU); confirm the
   LLM model owns the card (model-only + ~7 GB free), else the 100k
   switch.
4. **Dry-run receipt:** `events-extract --pages <list> --dry-run`
   records the scope plan before any model call (confirms/refutes the
   235/412 claim for the target scope).
5. **Launch:** `events-extract --pages <list> --workers 2`.
6. **Resume:** per-page state, **atomic** — a page's extraction state
   commits only on full page completion, so no half-page garbage is
   ingested by the rebuild; on OOM/crash, resume skips completed pages.
7. **Index rebuild:** re-parse + re-embed derived layers (shared engine
   path → JJK 4 gates re-run at closure prove zero regression).
8. **Model-unloaded side session:** stop the LLM; run re-grade (69-row
   p23, 30-row sample, 200-row OOS, 134 page-run, 5.4 re-adjudication
   on the 3 partial) **and** the 4 standing gates.
9. **Closure council** → A20 stamp on the register diff (if the void
   set is clean).

**Workers = 2** (100k KV pre-reserve leaves ~7–8 GB headroom; 4 risks
OOM under sustained load given the 508/524 co-location history).
**Abort check:** if `nvidia-smi` shows the model climbing to the memory
ceiling or a per-page crash → stop, resume from per-page state, drop to
workers 1. Pre-registered.

### 5. P6 boundary
- **Pre-registered IN the lock as the P6 method seed:** the Census v1
  schema + the grader + the 200-row held-out OOS protocol (frozen draw
  mechanism + the −2-row acceptance threshold) + the named-limit
  register format (defect + owning leg). This is the closed method
  surface a 7-wiki rollout inherits — the method artifacts, **not** a
  rollout commitment (E's "full method in the lock" is the least-
  reversible ×7 lock, R3; we pre-register the surface, not the ×7
  commitment).
- **Separate future owner decision:** the 7-wiki rollout itself (which
  wikis, order, when). Not in the lock.
- **§7 addendum by 2026-09-25:** documents the pre-registered method
  surface as a stand-alone addendum; does **not** commit the rollout
  (the addendum now has a method seed to document, not a hollow
  re-litigation).
- **Pre-registered escape hatch:** the OOS threshold (post ≥ pre − 2) +
  the named-limit format + the A20 void set. If the method (Census v1 /
  grader) proves flawed on CSM (OOS collapse, named limits missing
  defect+owner), the §7 addendum is **void and the method re-locked
  before the rollout inherits it**; the rollout cannot start without a
  green CSM method lock + a clean §7 addendum. A flawed method is
  caught at CSM closure, not after ×7 propagation.