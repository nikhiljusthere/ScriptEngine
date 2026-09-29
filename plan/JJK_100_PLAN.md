# JJK to 100% — campaign plan (proposed, 2026-09-29)

# OBJECTIVE: a JJK BRAIN (RUNBOOK §0, owner's definition 2026-09-28)
#
# Not a data store. Every line of the corpus understood, recallable and
# traceable, AND the corpus holds a complete understanding of the events,
# characters and everything there is to know about them — enough to make good,
# grounded assumptions and speculations when asked. The cross-Earth "who would
# win" match-up is one case of a whole class (hypotheticals, trajectories,
# group/state). ScriptEngine serves the complete cited evidence; the model
# reasons; the engine never asserts an unstated fact.
#
# This plan does NOT restate that definition — `franchise_kit/RUNBOOK_100.md`
# §0 is canon and governs. This file is the JJK instance of it.

meta:
  version: 2
  series: jjk
  authored: 2026-09-29 (v1); revised 2026-09-29 (v2, after independent
    verification + a 100-page pilot — reports/jjk/VERIFY_2026-09-29.md)
  status: v2 EXECUTING — owner go-ahead 2026-09-29 ("move forward to fixing
    JJK to the actual 100%"); P5 declaration remains the council's
  supersedes: nothing (JJK's D1–D10 record of 2026-09-07 stands for the prose
    layer; this plan re-opens the EVENTS layer only, on evidence below)
  governing_definition: franchise_kit/RUNBOOK_100.md §0
  reference_shape: plan/CSM_100_CLOSE.md (closure loop), plan/MARVEL_100_PLAN.md (D-gates)

# ---------------------------------------------------------------------------
# FINDING — why JJK needs re-opening (measured 2026-09-29, read-only)
# ---------------------------------------------------------------------------
#
# The 2026-09-07 record declares JJK's PROSE pass 100%. That claim is about the
# prose/classification layer and I have not disputed it. The EVENTS layer, which
# the brain definition makes a required dimension (D6: defeats, feats, who did
# what to whom, on the timeline), does not meet the bar. Measured on the store:
#
#   rows                                    2,748 over 508 pages
#   prompt_version                          events-2026-09-05.2  (ALL of them)
#   model                                   qwen3.8-27b-ninfer  (ALL of them)
#   verified flag                           NULL on all 2,748 — never verified
#   subject == object                       807  (29.4%)   ← violates a prompt rule
#   arrived/departed w/ object==subject      685  (24.9%)   ← "object is a PLACE"
#   quotes < 20 chars                        87
#   quote verbatim in its own section        2,748/2,748  ✓ (traceability intact)
#   invalid verbs                            0  ✓
#
# Real rows from the store, not hypotheticals:
#   "Akari and the jujutsu sorcerers learned that Yasohachi Bridge might hold
#    answers"                → Akari departed Akari   (a description, not an event)
#   "Suddenly Akari shows up"                      → Akari arrived Akari
#   "During their fight"                            → Aoi Todo fought Aoi Todo
#
# The prompt the rows came from predates the 2026-09-29 council rewrite
# (events-2026-09-29.7). So this is not "90% teacher → 10% label noise": on the
# two most common movement verbs the corpus is ~25% wrong, by the old prompt's
# own stated rule, with a zero verification pass. Training a small model on it
# would teach the student exactly the bug the current prompt forbids.
#
# CONSEQUENCE: the JJK events corpus is DISCARDED as a training set. It is
# re-extracted under events-2026-09-29.7, gated, and verified. Only what
# survives that is eligible to become training data.

# ---------------------------------------------------------------------------
# GATES — the checkable numbers (RUNBOOK §0, four layers)
# ---------------------------------------------------------------------------
#
# D5 RECALLABLE  — /context serves every line.
#   tier-1 HIT per door ÷ full panel, `span-recall --panel … --door {qa,narrative,roster}`
#   JJK is the baseline-exact reference; any engine change that moves it is a
#   regression, not an improvement.
#
# D6 UNDERSTOOD  — every line read and classified; every event's participants
#   resolved to the RIGHT entity in the RIGHT reality; placed on the timeline;
#   powers/abilities, affiliations over time, relationships, feats and defeats
#   held as structured rows.
#   J6.1  extraction coverage   : events extracted / events stated, per section
#   J6.2  gate violations       : 0 (the five mechanical gates, §GATES below)
#   J6.3  self-object rate      : 0 rows where subject==object, EXCEPT rows
#         where the passage states the subject did it to themselves
#   J6.4  verbatim quotes      : 100% of rows, in the section they claim
#   J6.5  verb legality        : 100% in eventive_verbs(store)
#   J6.6  participant resolution: unresolved / ambiguous / cross-reality counts
#         reported with cause; 0 silently dropped
#   J6.7  placement pages with ZERO events: 0, or named cause (a page with no
#         prose above the word-count floor legitimately has none)
#   J6.8  empty pages          : 0 unexplained (a `{"events": []}` answer is a
#         result, not a silence — it must be distinguishable from a failure)
#
# D-T TRACEABLE  — every fact resolves to its source section.
#   `audit --series jjk`; gaps named by cause. JJK currently PASSES (2,748/2,748).
#
# D-R REASONED  — the brain layer. The one that makes it a brain.
#   A reasoning bank of ~50-100 JJK questions across match-ups (incl. cross-
#   reality), hypotheticals/counterfactuals, trajectories/parallels, and
#   group/state. Each with a PRE-REGISTERED required-evidence set drawn from the
#   store. Scored on (a) evidence served ⊇ required, (b) zero fabricated facts,
#   (c) assumptions stated as assumptions. Plus an OWNER-authored blind set —
#   the executing side must not write it.
#   JJK currently has ORACLE_v1/v2 (recall probes). A reasoning bank is a
#   DIFFERENT artifact and does not exist yet for JJK.

# ---------------------------------------------------------------------------
# THE FIVE MECHANICAL GATES — run on every proposed row, before storage
# ---------------------------------------------------------------------------
#
# These are the project's own predicates (scriptengine/ingest/verbatim.py,
# events.py), not new judgement. A row that fails is a counted drop with a
# cause, never a silent loss.
#
# G1 quote is verbatim in the section it claims      (quoted_in / fold)
# G2 verb ∈ eventive_verbs(store) for THIS wiki     (closed set, per-wiki)
# G3 subject==object only if the passage says so    (self-directed is legal:
#                                                      "he shot himself")
# G4 arrived/departed object is a PLACE or a GROUP  (never a person)
# G5 quote ≥ 12 chars and is a clause, not a fragment
#
# Measured on today's corpus: G1 ✓ 2748/2748, G2 ✓ 2748/2748, G3 ✗ 807,
# G4 ✗ 685 (subset of G3), G5 ✗ 87.

# ---------------------------------------------------------------------------
# v2 — WHAT THE VERIFICATION AND THE PILOT CHANGED (2026-09-29)
# ---------------------------------------------------------------------------
#
# Evidence: reports/jjk/VERIFY_2026-09-29.md (every v1 number re-derived) and a
# 100-page seeded pilot of prompt .7 on a store copy, replayed offline from the
# teacher trace through both resolvers (same model output, exact A/B).
#
# 1. P0 IS NOT A MUTATION. `events.passage` is a load-bearing label (in the
#    PRIMARY KEY and the replace predicate). The input text is recovered by
#    the section_id join (2,748/2,748) — see plan/JJK_P0_PASSAGE_FINDING.md.
#    NEW P0b: the teacher trace (SCRIPTENGINE_EVENTS_TRACE) records the exact
#    window each call read and its raw answer, incl. {"events": []}. Only the
#    trace holds exact inputs and negatives; the store holds neither.
# 2. P1 (constrained decoding) IS DROPPED FOR THE TEACHER. Pilot: illegal
#    verbs were 20/1,301 proposals (1.5%: created ×7, destroyed, transformed…)
#    and every one is a correct refusal — a verb enum would coerce them into
#    legal-but-wrong rows, turning a counted drop into a silent error. It
#    stays in the student plan (a 3B's JSON validity), reported with it off.
# 3. THE RECALL HOLE IS THE RESOLVER. Pilot: 421/1,301 (32%) proposals dropped
#    as unknown participants (shard 1: 47% Marvel, 50% MCU). Fixed in the
#    engine, generic, tested (tests/test_events_resolver_pointing.py):
#    - name part → the one entity the page links, or the page itself (a
#      subpage's base): "Kiyotaka", "Chizuru", "Takako", "Dhruv" → +52 rows;
#    - an exact title the page never links yields to the one entity it does
#      point at (Akari → Akari Nitta, Ryu → Ryu Ishigori; never to a variant,
#      never away from the page's own entity);
#    - title-word tie-break where no link decides ("Gojo" → Satoru Gojo, not
#      the Sorcerer Clan page that lists clan names as aliases);
#    - declared `events: participant_exclude_types:` (JJK: songs, volumes,
#      discs — works about the story, never actors in it).
#    Remaining unknowns are overwhelmingly generics ("the crowd", "civilians",
#    "the curse") — correct refusals, a named floor.
# 4. G3/G4 ARE EXTRACTION-TIME COUNTED DROPS, not report-only. Pilot under .7:
#    self-object 6/637 (was 29.4%); movement rows 34/637 but 23 of 34 named a
#    person ("Shoko Ieiri arrived Satoru Gojo"). `self_object` (generic) and
#    `shape` (inert unless the wiki declares `events: place_types:`) drop
#    classes, counted in the run report.
# 5. JJK DECLARES THE OUTCOME VERBS (defeated / escaped / captured). The brain
#    definition asks who won; the old corpus had 1,200 `fought` and no outcome.
#    Pilot: 134 `defeated` in 637 rows. Their precision is the first thing the
#    judged set must measure (bake-off pattern: a failed ambush read as
#    "defeated").
# 6. STALE ROWS SURVIVE A FAILED PAGE. A page whose extraction fails keeps its
#    old rows. The run retries failures at concurrency 1, then G7 (prompt
#    version) must be 0 or each stale page named — never a mixed corpus.
# 7. RETRIEVAL READS `events` (narrative.py:331, :453). So the four gates are
#    run BEFORE (done: pytest 1,451+2xp+2 known env; eval 31/31; span-recall
#    48,572/0 + probe 398/400; canon 10/16·236/236·79.0%) and AFTER, plus a
#    30-query /context narrative bundle diff (bundles_pre.json). A moved gold
#    is a finding to adjudicate, not an automatic regression or win.
# 8. G5 IS SOFT. quoted_in already refuses < 12 chars; the 20-char cut flags
#    real events ("Bayer takes on Gojo"). Reported, never a drop.
# 9. P4 USES THE 27B YES/NO VERIFIER, NOT OPEN-JEV. Open-Jev is a candidate-
#    scoring head (LoRA + scalar head), not a chat model; `events-verify`
#    cannot drive it and its GPU test has never produced a verdict. It can be
#    a second, independent judge later — on a different base than any student.
# 10. THE BINDING CONSTRAINT IS UNCHANGED: ≥300 judged rows, two judges,
#    adjudicated, plus a ≥40-window recall set. Nothing is "improved" or
#    "100%" until it is measured there (plan/JJK_STUDENT_TRAINING.md §6).
#
# v2 PHASES (status 2026-09-29 ~10:20 — receipt: reports/jjk/RECEIPT_events_2026-09-29.md)
#   P0  derived input (section_id join) + teacher trace on every run    DONE
#   P1  engine fixes above, with tests; 4 gates BEFORE                  DONE
#   P2  re-extract `--scope all --refresh` (966 pages / 3,657 sections),
#       trace on, failed pages retried at concurrency 1                 DONE (.7, then .9: 966/966, 8,491 rows)
#   P2b judged set → prompt .8/.9 (verb definitions), blind A/B, fanout
#       gate; judge A: .7 ≈67% → .9 77.3% ± 6.7, verified tier 93.0%   DONE (judge A only)
#   P3  tools/events_gates.py: G1 G2 G3 G4 G7 hard, G5 G6 soft          DONE: 0/0/0/0/0
#   P4  events-verify (27B yes/no) → `verified` 1/0/NULL on every row,
#       a confidence tier, never a filter                               DONE: 3,830 / 4,644 / 17
#   P4b 4 gates AFTER + bundle diff; each moved gold diagnosed          see receipt
#   P4c the judged set (≥300 rows / 2 judges) + recall set             owner + judge
#   P5  council reads the receipt against the DATABASE and declares    council
#   P6  student training — plan/JJK_STUDENT_TRAINING.md                after P5
#   D-R the reasoning bank + owner blind set (RUNBOOK §0)               owner-authored blind set
#
# Floors that are NOT defects (named cause, not a shortfall):
#   - 481 extractable sections outside `all` scope: Trivia 222, "Characters in
#     Order of Appearance" 98, "Battles & Events" link lists 58, Music 58, …
#   - generic-noun participants with no page ("the crowd", "civilians").

# ---------------------------------------------------------------------------
# PHASES (v1 — superseded by v2 above; kept for the record)
# ---------------------------------------------------------------------------
#
# P0 — Rebuild the passages (prerequisite, no model, no GPU)
#   `events.passage` is EMPTY on all 22,666 rows across all wikis. Rebuild it
#   from `sections` by section_id. JJK recovers 2,748/2,748 by section_id.
#   Marvel needs the stale-id repair first (2,568/9,004 by id; 4,334 by
#   doc_title+ordinal) — that is P0 for the OTHER wikis, not JJK.
#   Exit: every JJK row carries the exact passage it was read from.
#   Why it matters: without it there is no training example — only a label.
#
# P1 — Constrained decoding (no new model, ~1 hour)
#   The 35B-A3B bake-off lost to bad structure, not bad understanding: 27
#   invalid verbs, 125 duplicate drops, 801 rows vs 481. G2 becomes mechanical
#   via SGLang `response_format: {"type":"json_schema"}` with `verb` as an enum
#   of eventive_verbs(store). XGrammar is the default backend.
#   Exit: bad-verb drops = 0 on a 160-page sample; row-set diff recorded
#   against the unconstrained read.
#   THIS IS FIRST ON PURPOSE: it is free, and it changes what P2 must fix.
#
# P2 — Re-extract JJK under events-2026-09-29.7 (the whole-card window)
#   Model: Qwen3.8-27B uncensored NVFP4, SGLang native MTP, thinking OFF,
#   prompt .7 — the method already settled by council (2026-09-29, d88141de).
#   Scope: `all` (placement + corpus + prose), not just placement. Today's
#   2,748 rows sit mostly on character_synopsis (929) and chapter (629) — the
#   `corpus` scope is where a character page states what happened to them.
#   Constraints: whole-card window (:8018 and the retrieval stack down), the
#   27B + MTP memory budget (6 concurrent slots, 16k KV pool on a 32 GB card).
#   Exit: 0 failed pages; every drop counted by gate with a cause.
#
# P3 — Gate and re-resolve (no model)
#   Run G1-G5 over every proposed row. Re-point participants through the
#   reality-aware resolver (`re_resolve_participants`), which uses page reality +
#   the page's own wikilinks to break Earth-variant ambiguity.
#   Exit: J6.1-J6.8 all green, or each shortfall carries a named cause.
#
# P4 — Verify (Open-Jev-9B) — BLOCKER, see §BLOCKERS
#   Open-Jev-9B set `verified` = 1/0/NULL per row. It is a CONFIDENCE FLAG,
#   never a filter (council 2026-09-29, bdc9942f): a row it dislikes is kept
#   and marked, never dropped.
#   Exit: every row carries a verified value; the 0/NULL counts are reported.
#
# P5 — Declare or iterate (council, not the executing side)
#   A council reads the receipt against the DATABASE (not the report). 100% is
#   DECLARED, never self-certified, and only when D5 + D6 + D-T + D-R are green
#   and the blind set clears its threshold. Remainder rows close by flip or by
#   an explicit void-set (cause + defect + retest pointer) — never by phrasing.
#
# P6 — THEN, and only then, the training question
#   The eligible set is whatever survived P3+P4. Only the events-2026-09-29.7
#   rows from any wiki are candidates; the 2026-09-05.x rows are discarded.
#   Reference point: STAGE fine-tuned Qwen3-4B from 31.4% to 74.3% exact match
#   on 18K source-grounded examples. Below ~10K verified rows the 9B pilot is
#   not worth the GPU-week.

# ---------------------------------------------------------------------------
# BLOCKERS — resolve before P2, not during
# ---------------------------------------------------------------------------
#
# B1. Open-Jev-9B HAS NO WEIGHTS ON DISK. `models--ZefanCai--Open-Jev-9B` is
#     512 bytes (a refs/main file) and models/open-jev-9b is 25 MB of eval data
#     + a python package. A 9B model is ~18 GB. It must be located (another
#     host? a venv symlink? an API?) or re-downloaded, or P4 has nothing to run
#     and JJK cannot be verified at all. /mnt/PROJECTS now has 70 GB free
#     (was 35 GB), so a re-download is affordable.
#
# B2. Measurement power. Precision is currently judged on 30 seeded rows
#     (±~10 pts). The 27B's 90% vs the 35B-A3B's 80% is THREE ROWS. Before any
#     bake-off — this one or the student's — the judged set must be ≥300 rows
#     with two independent judges and an adjudication pass. Without this, P2
#     cannot tell whether it improved anything.
#
# B3. JJK is the baseline-exact reference. CLAUDE.md: JJK D6 is DONE and is the
#     reference every CSM/Marvel engine change must not regress. Re-extracting
#     JJK's events changes that artifact. The four standing gates must be green
#     BEFORE and AFTER, and the diff recorded — a JJK regression blocks the
#     other campaigns.
#
# B4. Disk. /mnt/PROJECTS at 93% (70 GB free). decider-35b-a3b-nvfp4 (39 GB
#     resolved) is still resident and is not needed; it is the obvious reclaim
#     if P2's window needs headroom.

# ---------------------------------------------------------------------------
# WHAT I CAN AND CANNOT DO
# ---------------------------------------------------------------------------
#
# I can run P0, P1, P3, and the P2 extraction (the card is free: 285 MiB used,
# no model server up, the 27B NVFP4 weights are on disk at
# /mnt/PROJECTS/models/fleetml-qwen3.8-27b-uncensored-nvfp4). P4 needs B1
# resolved. P5 is a council and is not mine to self-certify.
#
# I will NOT declare 100%. Under the owner's own definition that is a council
# verdict on a blind set, and a single extraction pass cannot produce it.
