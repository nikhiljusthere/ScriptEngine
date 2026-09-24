# P2-scope: extraction-leg design + Q1–Q4 ruling application (CSM 100% close)

2026-09-24, opencode session (CPU side; every datum below is model-free,
disk-verified). This is the design leg of `plan/CSM_100_CLOSE.md` step
P2-scope ("re-prove retrieval-vs-extraction per row FIRST — a misdiagnosed
retrieval failure must never buy GPU-days; residual extraction scope only;
NOTHING extracts until this council locks scope") plus the Q1–Q4 ruling
application owed by the P2.3 widened-census work (council #29
`CLOSE_COUNCIL_RULINGS_Q1_Q4.md`, executed through `tools/census_dimensions.py`
judge + `tools/csm/p23_grader.py`). **COUNCIL #38 LOCKED this design with
8 amendments** (record `reports/csm/receipts/council_p2_scope/chairman.md`;
all amendments landed below, marked `(amend #38-n)`). The D6/P2-execute
leg consumes the JEV keep-list (2026-09-24 pre-filter, JJK gate
837/838 = 99.9%).

**Window shape (council #38 ruling):** the window commits to
**minimum-viable (a)+(b)+(d)+(e) ≈ 5 h**; leg (c) extraction is a
**pre-registered stretch leg** (owner word + rate probe). Window order:
**(a) gates → (b) sweep → (d) width instrument → (e) re-grade → (c)
extraction only if the owner calls the stretch** — (d) BEFORE (c), so the
width verdict never rides extraction's index state (chairman Q4 ruling:
(c) only appends the narrative-door events table, which the instrument
does not grade).

## Ledger as of today (disk-verified)

- **486 bank, product state** (flag-OFF committed tree `20d6da4e`-behavior,
  campaign path with subject, p23 endpoint defaults): **469/486, 17 red** =
  {arcn-02/03/04/06/08/10, state-02/03/08/09, abl-01/02/09, caus-03,
  org-03, pool-140/358}. Reference file:
  `reports/csm/receipts/d7_window/snapshots/census_head_469.jsonl`
  (the D7-window pre-stage capture of the product-state census).
- **Campaign grade** (TIERED ON, council #36 Leg A): **473/486, 13 red** =
  17 − {arcn-02, arcn-10, org-03, state-08} (the Leg A flips).
- **CSM_100_CLOSE's 23-red ledger (at 463) — 6 since closed on disk:**
  chap-01 + arcn-07 (Q1-L1 story-pages floor, `90206940`) and org-05/06 +
  vol-10 + arcn-01 (derivation leg, `20d6da4e`). org-03 = TIERED-dependent
  (product-red, 473-green). pool-140/358 = width-class P2 retest (council
  #37 trigger line).
- **FLOOR16** (`tools/csm/check_targets.py:42`) = the 16 Phase-2 floor rows
  = the 17 product reds minus org-03 (the D7 holdout) = {pool-140/358,
  abl-01/02/09, arcn-02/03/04/06/08/10, caus-03, state-02/03/08/09}
  (14 floor + 2 ratified-width, the council #37 relabel).
- **File-state note (auditability):** `reports/csm/census_widened_csm_results.jsonl`
  as committed at `4a8616bd` is the **LEG B census** (ABILWIDTH ON: W=469
  with pool-140/358 green and pool-149/252 counter-flipped red) — the last
  p23 grade the D7 window chain ran, left in place. The product-state
  reference is the snapshot above; a post-window flag-OFF re-grade owes in
  the GPU window (it is leg (e) below).
- **Pre-extraction 69-red class mix** (the 417-era set,
  `census_widened_csm_results_hints.jsonl`): box 37 (chapter_box 9 / episode 9
  / volume_box 9 / story_arcs_box 10), arc-narrative 8, state 5, abilities 6,
  appearance 1, causality 1, organization 5, ability-pool 6. Post-D6-close
  subject routing: **all 37 box-class reds closed** (0 box-class reds in the
  product state). Campaign instrument (subject + 60000/50): all 69 green
  (`…_hints_campaign.jsonl` 8/8 on the residual 8).

## Q1–Q4 rulings applied (council #29)

- **Q1 — widen the census to the 5 in-scope page types: DONE.** v2's 50
  items (10/class × chapter_box/episode/volume_box/story_arcs_box/
  organization) carried verbatim into the 486 bank; the widened census is
  the re-grade denominator. Post-subject-routing the page-type dimension is
  green: 0 box-class reds in product state (Q1's own test: the page types
  the character-only 60-q census could not claim).
- **Q2 — size the ability pool to the 376 rows: DONE.** 376-item pool, 1:1
  on `abilities` rows (75 characters, 28 thin-source flagged,
  `census_widened_author.md`). Product-state pool reds = the width-class
  pair pool-140/358 only (pool-149/252 product-green; they counter-flip in
  the Leg B census, not in product).
- **Q3 — re-gate the P2.3 null branch on the widened census: NOT FIRING.**
  The null branch = the extraction descope claim; its condition is the
  widened census GREEN. 469/486 (product) / 473/486 (campaign) ≠ green →
  no descope; the P2 track continues. Re-gate after P2-execute + the width
  leg: a 486 re-grade at product config; green ⇒ descope claimable; any
  residual ⇒ per-row triage into the named-limit register (defect + owning
  leg + retest), never a catch-all.
- **Q4 — the per-page campaign runs alongside P2: ONGOING.** Coverage
  473/537 remainder 0 at plan start (the denominator annex); the
  extraction leg's event layer feeds the narrative/auto doors and the
  writer path (the Q5 in-parts treatment stays Phase-2 scope).

## Per-row re-proof: retrieval vs extraction (the 16 FLOOR16 rows)

Method (all model-free, disk-only):
1. product-state verdict + hit/miss per row — the D7 snapshot census;
2. gold locations per expect term — `~/tools/jev/reports/csm-red-triage.jsonl`
   (23/23 supported; zero bank/crawl defects);
3. keep-list membership of every gold section —
   `~/tools/jev/reports/csm-prefilter-keep.jsonl` (1,358/3,917 sections,
   all 69 event sections; the JJK sensitivity gate 837/838 = 99.9% ≥ 99%);
4. chunking evidence — the census-authoring receipt check (c): every pool
   phrase is a substring of the character page's chunk text ("a phrase never
   straddles a chunk boundary"); carried v1+v2 terms fail the judge's
   case-insensitive rule on 0 of 330;
5. **the D6 zero-flip root cause** (`GATE.md` D6 closure): "the events
   table is consumed only by the narrative door (`retrieve/narrative.py`);
   the 486 grades the qa door … the expect sentences ARE in chunks but lose
   to the character card → retrieval-ranking gap."

**Finding: every FLOOR16 row's gold sits in kept AND chunked sections, and
the qa-door bundle loses it at RANKING. All 16 rows are retrieval-config
(width / ranking / door) gaps, not extraction-content gaps.** Extraction
buys none of the 16 qa-door flips (D6 measured it: 333 events, 0 flips).

| row (class) | gold location (keep-list p) | product verdict | lever |
|---|---|---|---|
| pool-140 (width) | Falling Devil / Devil Powers (0.84) | RED (gold rank 12–47 cut at top_k=8) | class-scoped top_k=30 instrument (`WIDTHCLASS_PREDICT.md`) |
| pool-358 (width) | Yoru / Weapon Creation (0.80) | RED (gold rank ~19) | same instrument |
| arcn-02, arcn-10 (arc-narrative) | character arc sections (0.63–0.81) | RED (0–1/3 ordered beats served) | TIERED default-flip (Leg A proven) |
| arcn-03/04/06/08 (arc-narrative) | character arc sections (0.65–0.78) | RED | TIERED + width; retest, else 5.4 re-adjudication |
| state-08 (state-over-time) | Seigi Akoku / Dating Denji arc (0.70) | RED | TIERED default-flip (Leg A proven) |
| state-02/03/09 (state-over-time) | chapter + character arc sections (0.67–0.79) | RED | TIERED + width; interval facts enrich the narrative door via extraction; qa-door flip = the ranking lever |
| abl-01/02/09 (abilities) | scattered kept ability sections (0.59–0.83) | RED (roster arm 4/4 in the bar audit) | auto/roster routing (R-9 family); NOT extraction |
| caus-03 (causality) | Asa Mitaka/History / Dating Denji arc (0.71) | RED | TIERED + width family |

The three abilities rows are the sharpest case: the roster door already
serves them 4/4 (the bar-audit roster arm) — the residual is the qa-door
width on enumeration shape, and extraction adds nothing (the ability rows
already exist in the `abilities` table).

## Extraction scope (LOCKED — council #38)

- **Status: pre-registered STRETCH leg** (amend #38-2): the window commits
  to minimum-viable (a)+(b)+(d)+(e); (c) runs only on owner word + the
  first-10-pages rate probe below.
- **Pass:** 27B `events-extract` (in-process, ~5.3 GB; Qwen DOWN, whole card
  per the plan's GPU discipline), `--workers 2`, atomic per-page resume
  (D6 precedent; OOM or per-page crash → resume at workers 1 — the resume
  must ride the detached window chain; there is no mid-window executor,
  amend #38-3).
- **Scope input:** the P2 keep-list
  (`~/tools/jev/reports/csm-prefilter-keep.jsonl`, 1,358 sections over 511
  unique pages; the pre-filter force-include of the 69 event sections
  needed no forcing — all 69 kept at p ≥ 0.3, `forced_event_section=0`).
  Page file for the run: `reports/csm/p2_keep_pages.txt` (this commit;
  `#`-free one-title-per-line, exactly the 511 keep-list docs).
- **Dry-run (model-free, this session):**
  `events-extract --series csm --scope corpus --pages <keep-list> --dry-run`
  = **230 pages / 406 sections** (the 511 pages ∩ the corpus queue; the
  unfiltered corpus queue = 235 pages / 412 sections). Net-new vs the D6
  frozen run (72 pages considered / 71 extracted / 333 events): **~158
  pages**. Re-run the dry-run at window start to re-verify 230/406 at the
  current HEAD.
- **Role (explicit, pre-registered so the re-grade cannot over-claim):**
  the leg completes the event layer for the **narrative/auto doors** + the
  writer path + the Q4 coverage compounding. It is **NOT the flip lever
  for the 16 qa-door floor rows** (root cause above). The plan's three
  exact-match checks on extracted rows are unchanged.
- **Zero-regression receipts after the pass (amend #38-1, the plan's
  P2-execute shape-proof):** index shape (D6 baseline 537 docs / 3,917
  sections / 755 nodes / 11,261 edges / 5,081 facts / 7,797 chunks),
  events remap 333→N with 0 dropped, Qdrant vector counts, JJK diff =
  gate artifacts only, span-recall re-proof + coverage 473/537 remainder
  0 re-proof.
- **Re-grade after the pass:** p23 at product config (the flag-OFF
  re-grade owed by the file-state note) + a narrative-door axis check for
  the event-dependent rows (arc-narrative / state-over-time) — the
  narrative door is the consumer of the events table. The narrative-axis
  check is DIRECTIONAL (evidence; the formal bars are unchanged: the p23
  qa door, the campaign instrument, and the standing guards) (amend
  #38-4).
- **Content-absence check (amend #38-4, model-free, BEFORE the window):**
  row-level disk check that the state-02/03/09 gold phrases are present in
  the kept chunks (the census-authoring check (c) at row level, not the
  class level). If a phrase is ABSENT from the kept chunks, that row moves
  to the extraction-content lever (scope widening ⇒ re-lock before the
  window). Relabel (amend #38-4): the 11 "extraction-gated" dim rows of
  council #37's close register are **retrieval-gated on the qa axis** by
  this per-row re-proof; their disposition is the levers (TIERED flip /
  width instrument / roster routing / retest) or the 5.4 named-limit void
  set — never a catch-all GPU day.

## GPU budget + abort/shrink (the window, Qwen down)

| leg | estimate | status (amend #38-2) | basis |
|---|---|---|---|
| (a) R-8 gate window: 4 standing gates (pytest **1,331** pin / eval jjk **31/31** / span **48,572** + probe ≥390/400 / canon **236/236 · 10/16 · 79.0%**) + green30 | 45–60 min | **MV** | council #30 A2 order; D6/D7 window wall-clocks |
| (b) P2.1 sweep `tools/csm/p21_sweep.sh` (stamp-wipe at current HEAD — the 2026-09-17 receipt @`4b60043` is stale) | ≈ 2.7 h + 4 min heldout | **MV** | the pre-baked runner estimate (council #30 A6) |
| (c) P2-execute extraction: 230 pages (~158 net-new) + index rebuild | ≈ 2.5–3.5 h + ~10 min | **STRETCH** — owner word + rate probe | D6 rate ≈ 71 pages (incl. retry) in the 2026-09-18 window, workers 2 |
| (d) width-class instrument (`WIDTHCLASS_PREDICT.md`): 4 rows + full-486 counter sweep + blind 19 + d6_flip (OOS/green30) | 30–45 min | **MV** | p23_handoff 45-min watchdog |
| (e) p23 re-grade (486 product + campaign config) + guards + zero-regression receipts | ~45 min | **MV** | D7 window p23 legs (25–34 s on 19-row blind; full-bank precedent) |
| **minimum-viable (a)+(b)+(d)+(e)** | **≈ 4.8–5.8 h GPU** | the window commitment | |
| with stretch (c) | ≈ 7.5–9.5 h GPU | owner-discretion leg | |

**Window order (amend #38-2, chairman Q4 ruling):** (a) → (b) → (d) →
(e), then (c) only if the owner calls the stretch. (d) BEFORE (c): the
width instrument grades the same-index counter-sweep; (c) only appends the
narrative-door events table, so the pre-extraction index is not stale for
(d), and a leg-(c) OOM/abort can never grade (d) on a partial index.

**No-commit rule (amend #38-1):** no commits DURING the window. The A18
sweep ledger is stamped at the window's HEAD; a mid-window HEAD move
mixed-stamps the ledger (2.7 h restart). The plan's "commit before gating"
applies at window boundaries only; all window artifacts commit after the
window closes, path-limited, never staging the owner's dirty files.

**Window-killer pre-checks (amend #38-3), run BEFORE Qwen is stopped:**
1. `/mnt/PROJECTS` mount up: `mountpoint /mnt/PROJECTS` (root-owned
   fuseblk; it was touched 2026-09-24 ~00:27 — re-verify at window start).
2. Model file present + readable:
   `/mnt/PROJECTS/ninfer-transfer/models/qwen3_8_27b_nvfp4.ninfer`
   (18.3 GB).
3. The owner's uncommitted `tools/csm/d7_gates.sh` restore argv (line 36,
   `nohup ./ninfer/build/apps/ninfer-serve /mnt/PROJECTS/...`) resolves:
   `bash -n` + the model path from check 2. This session verified
   1–3 (2026-09-24 ~05:3x): mount up, file present, argv resolves.
4. Sentinel receipts: the detached window chain (the
   `d7_window_chain.sh` pattern) writes STATE + RECEIPT sentinels to
   `/tmp/d7_gates/` and `reports/master-work/` per leg; an OOM/per-page
   crash resumes at workers 1 inside the same chain — there is no
   mid-window executor for a 5–9 h Qwen-down window.
5. Owner-alert rule (pre-registered): any gate leg RED, a sentinel
   missing by its leg's budget, or a restore failure ⇒ owner intervention
   (the window runs owner-out-of-the-room; failures surface at window end
   via the sentinels — alert conditions, not just the receipts).

**Abort/shrink (pre-registered, amended #38-1):** (1) measure the first 10
NEW pages of the extraction against the D6 rate: ≤ 1.2× ⇒ run the full
230 pages; 1.2–2× ⇒ shrink the extraction to the 16-floor gold-section
union (~20–25 pages, model-free union of the found_sections above) + the
69 event sections, then re-estimate; > 2× ⇒ abort leg (c) to the next
window (the minimum-viable legs are unaffected); (2) OOM or per-page
crash ⇒ resume at workers 1 on the detached chain (D6 precedent); (3) any
standing gate RED at the window's gate leg ⇒ halt the window, restore
Qwen from the owner's `tools/csm/d7_gates.sh` argv (the owner's
uncommitted edit — the `/mnt/PROJECTS/ninfer-transfer/models/` model path
— is authoritative; do not commit it).

**Retest triggers (owner-triggerable, pre-registered):**
- TIERED default-flip (owner decision, council #37 Q3 bar: one-char commit
  `context.py:583` "0"→"1" + 4 gates flag-ON + p23 473 repro + JJK
  non-regression) → re-grade the 16 + the 4 flips.
- width-class instrument PASS → the width-leg engine ship decision
  (owner word + 4 gates; D59 bars ex-post knobs on the RED Leg B).
- post-extraction → narrative-door axis re-grade for the event-dependent
  rows; Q3 null-branch re-gate on the 486 product re-grade.

## Standing guards (every regrade, per the plan — no exceptions)

0 green→red counter-flips vs the product-baseline green set (any
counter-flip rolls back its mechanism alone); green30 30/30; OOS200 drop
< 3 vs `D6_OOS_PRE` (locked floor 166, plan annex); blind 19/19
(`blind_fresh_d7.jsonl`); the 4 gates green; blind-set accuracy must not
trail bank movement; JJK diff = gate artifacts only, no
code/corpus/store.

## JEV measurement receipts (amend #38-7, CPU-side assignment)

The JEV measurement receipts owed by `plan/CSM_JEV_ACCEL.md` (the
Measurement protocol §) are **not a window leg** — they are assigned to
the CPU-side directing session (this session, post-council #38), written
to `reports/csm/receipts/council_p2_scope/JEV_MEASUREMENT.md`:

- pruner decision logs: `~/.config/opencode/jev-context-pruner/decisions.jsonl`
  + `~/.config/opencode/jev-bash-pruner/decisions.jsonl` (tail;
  `hook_error` lines = fail-open; expect 0 errors).
- NInfer cost: `/home/goblin/ninfer-work/logs/requests.jsonl`
  prompt-token / output-token totals for the council traffic, vs the R-5
  baseline (3.76M prompt / 110k output / 6.1% cache hit). The 09-24 JEV
  session measured a 99.85% prefix-cache hit on a campaign session with
  the pruner.
- Cadence: repeat after every council through the campaign's close.

## Close arithmetic (amend #38-8, corrected record)

Close is **ledger closure**, per the plan's CLOSE step: every 486 row is
GREEN or explicitly VOIDED with a named defect + leg + retest pointer
(council-ruled, never by phrasing). The lever path caps at **475**:
TIERED default-flip → 473 (campaign, flag-ON), + 2 width rows (pool-140/358
instrument PASS) → 475; the 11 residuals close by lever (retest) or the
5.4 named-limit void set. A guaranteed 486/486 is **never** claimed —
correction of the Expansionist's "486/486" arithmetic (R1/R2). OOS200 /
green30 / blind / JJK remain floors on every regrade regardless of
ledger state.