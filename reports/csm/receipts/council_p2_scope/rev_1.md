# Peer review R1 (fact-check) — council #38 (2026-09-24)

Reviewer: fact-check subagent. Scope: empirical claims in responses A–E
(`ANON.md`) spot-checked read-only against: `GATE.md` (D6 closure + D7
window + D7-CLOSE #37), `P2_SCOPE_EXTRACTION.md`, `tools/csm/check_targets.py`,
`receipts/d6_probe/WIDTHCLASS_PREDICT.md`, `D7A_NUMERIC_COLLISION.md`,
`~/tools/jev/HANDOFF.md`, `plan/CSM_100_CLOSE.md`, and the window scripts
(`d7_gates.sh`, `p21_sweep.sh`, `p23_handoff.sh`) + live git state.

## Verification log (spot-checks)

- **D6 zero-flip root-cause line** — `GATE.md:794-800`: "the events table is
  consumed only by the narrative door (`retrieve/narrative.py`) … the expect
  sentences ARE in chunks … but lose to the character card →
  retrieval-ranking gap" ✓ (cited by A-Q1, B-Q1, D-Q1; quoted verbatim in
  `P2_SCOPE_EXTRACTION.md:85-88`).
- **D6 numbers** — 333 events (302+31), 72 pages considered / 71 extracted,
  p23 417→417 with "0 flips either way" — `GATE.md:760-793` ✓ (A, D "333
  events, 0 flips"; B "417-era HEAD").
- **Council #37 trigger line** — `GATE.md:1118-1127`: class-scoped top_k=30
  campaign, "NOT an ABILWIDTH re-tune; D59 bars Leg-B knobs"; bar = flips ⊇
  {pool-140, pool-358} AND 0 counter-flips vs {pool-149, pool-252}; blind
  19/19; OOS drop < 3; `d6_flip` rc=0; RED ⇒ kill clause ✓. All five Q3
  answers read it faithfully; B's "sweep showing 40 counter-flips still
  PASSes" is a correct reading (`WIDTHCLASS_PREDICT.md:37-41`: bar binds on
  {149,252}; other flips "recorded and reported … re-opens the class scope").
- **Leg A/B** — Leg A (TIERED) PASS: 473/486, flips {arcn-02, arcn-10,
  org-03, state-08} MECH_GREEN, 0 counter-flips, FLOOR A 3/16; Leg B
  (ABILWIDTH) RED: 469/486, targets flipped but counter-flips {pool-149,
  pool-252}, FLOOR B 2/16; Leg C not run — `GATE.md:1010-1026` ✓ (C "Leg A
  already flipped arcn-02/10, state-08, org-03 at 473"; E "Flip: 469→473").
- **Ledger** — product 469/486 (17 red, set counts exactly 17) / campaign
  473/486 (13 red = 17 − Leg A flips) — `P2_SCOPE_EXTRACTION.md:16-23` ✓.
- **FLOOR16** — `check_targets.py:42-49` lists exactly 16 rows = 17 product
  reds − org-03 ✓ (matches `P2_SCOPE_EXTRACTION.md:29-32`; #37 relabel
  "14 floor + 2 ratified-width" per `GATE.md:1097`).
- **37 box-class reds** — chapter_box 9 / episode 9 / volume_box 9 /
  story_arcs_box 10 = 37; all closed post subject routing, 0 box-class reds
  in product state — `P2_SCOPE_EXTRACTION.md:39-45`, `D7A:37-50` ✓.
- **69/69 at 60000/50** — "Campaign instrument (subject + 60000/50): all 69
  green" — `P2_SCOPE_EXTRACTION.md:44-45` ✓ (E's "undervalued" cites this).
- **Keep-list numbers** — 1,358/3,917 sections over 511 pages; JJK gate
  837/838 = 99.9%; 69 event sections kept with `forced_event_section=0`;
  dry-run 230 pages / 406 sections; ~158 net-new vs D6's 72 —
  `P2_SCOPE_EXTRACTION.md:79-80,117-127` + `HANDOFF.md:29-35` ✓ (A Q2/leg (c),
  E Q1 "JJK 837/838, zero forced inclusions").
- **R-5 baseline 6.1% cache hit** — `HANDOFF.md:73-75` ✓ (E "undervalued").
- **P6 §7 seed due 2026-09-25** — `GATE.md:749,755` ✓ (E Q1).
- **Uncommitted restore dependency** — `git status` shows
  `M tools/csm/d7_gates.sh`; the uncommitted diff is exactly the restore-trap
  model path `models/qwen3_8_27b_nvfp4.ninfer` →
  `/mnt/PROJECTS/ninfer-transfer/models/…` ("authoritative; do not commit
  it", `P2_SCOPE_EXTRACTION.md:154-157`) ✓ (A leg (a) wedge, D Q2). The
  "root-owned mount" detail (A) is UNVERIFIED.
- **Halt codes** — `p23_handoff.sh:17-19`: 10 = Qwen still up (mode file),
  11 = GPU free < 6 GB, 12 = venv missing ✓ (A legs (d)/(e));
  `p21_sweep.sh:20`: exit 10-12 pre-checks ✓ (A leg (b)); A17/A18 ledger
  semantics at `p21_sweep.sh:186,277` ✓ (B Q2 "mixed-stamps the A18 sweep
  ledger", Q5 "A17 flag-OFF floors").
- **Stale stamp @`4b60043`** (2026-09-17 receipt) — `P2_SCOPE_EXTRACTION.md:143` ✓ (A leg (b)).
- **On-disk census = Leg B census** (W=469 with pool-140/358 green /
  pool-149/252 red, same count as product, opposite red set) —
  `P2_SCOPE_EXTRACTION.md:33-38` ✓ (D Q2).
- **P2-execute step** requires "span-recall + coverage re-proof after the
  shape change, full gates + guards" — `plan/CSM_100_CLOSE.md:95-99` ✓; that
  line is absent from the P2 budget table (flagged by A Q2, B Q2, C Q2; not
  by D/E).
- **11 "extraction-gated" rows, retest "post-extraction re-grade"** —
  `GATE.md:1089` ✓ (B Q1 no-op point; "13 reds = 11 extraction-P2 + 2
  width-P2" at `GATE.md:1130`).
- **UNVERIFIED / contradicted:** E "333→~900 event-row layer" (no on-disk
  source; rate extrapolation ~4.7 events/page from 333/71); E "Flip + width
  ship: 486/486" (contradicted: 473 + 2 width rows = 475, 11 rows remain —
  `GATE.md:1130`); A "4.75–5.75 h" minimum-viable bound (budget table sums
  to ≈ 4.7–5.2 h); A "root-owned mount".

## Answers

**1. Strongest: B.** Every load-bearing claim verified on disk: the
11-row retest no-op (#37 register:1089), the unbounded beyond-class
counter-flip (WIDTHCLASS_PREDICT bar binds only {149,252}), the 1.2–2×
drift gap (abort triggers only >2×), A18 mixed-stamp (`p21_sweep.sh:186,277`),
the missing post-shape re-proof (plan:99). A is close second: legs all
verified (halts 10/11/12, pre-checks 10–12, 230/406, uncommitted
`d7_gates.sh` argv), but its 4.75–5.75 h bound is off (table sums ≈ 5.2 h).

**2. Biggest blind spot: E.** "Flip + width ship: 486/486" is wrong:
473 + 2 width rows = 475; the 11 extraction-P2 rows stay red (#37:1130).
"Only product-config width stands between" conflates the 417-era 69-red
census with the current 13 reds. "333→~900 event rows" is UNVERIFIED
(extrapolated, not on disk).

**3. All five missed:** connecting B's no-op point to the CLOSE step —
D6's root cause shows the events table cannot flip qa-door rows, so the
11 "extraction-gated" rows can only close via TIERED/width/roster or an
explicit void-set; the council should pre-register the green-vs-void split
of the 486/486 declaration. (Process note: the unmasked `adv_*.md`
originals sit in this same directory, so the letter mapping is recoverable
and blind review was compromised.)