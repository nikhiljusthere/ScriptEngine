# P1.3 halt meter — CSM Phase 1 (FINAL)

**Status: FINAL — re-issued 2026-09-12 from `HALT_METER_P13_DRAFT.md` at the
R-7 close** (council SHIP-AMENDED, chairman A2; DRAFT + final committed
together as the recorded halt instrument). The DRAFT's single (c) row
(`csm-char-04`) moved to the (a) extraction-gated floor: the R-7 class
re-sweep (`reports/csm/receipts/r7_class_resweep.md`) confirmed the row is
the **22nd extraction-gated floor row** — the 8th Makima ability (the PM
contract) sits in section prose, the corpus never names it as an ability,
the R-7 hunk (`60e568f`) is generation-only (retrieval shape bit-identical
pre/post window), and its close lever is the Phase-2 extraction track / 5.4
re-adjudication (gate LIVE). The 10 invariant/residual (b) rows are stamped
by-design open here (chairman A2, closing the DRAFT's A11 gap); their
governing stamps are the red-list R-2/R-3 close notes.

**Inputs (all on disk, read 2026-09-12):**
- `reports/csm/GATE.md` — halt rule (the 22-row floor wording, moved at the
  R-7 close), the four standing gates, live GREEN state at the R-7 pass.
- `reports/csm/miss_queue_csm_iter1.jsonl` — 58 rows; **35 open**
  (status == "open"), matching GATE.md + GATE_LEDGER `queue_stamps`
  (open 35 / closed 23 / total 58).
- `reports/csm/red_list_csm.md` — documented floors/residuals (R-3 L41–52,
  ID-mapping addendum L70–80, R-1 addendum L149–181 incl. the R-7
  re-probe stamp, R-2 close note, R-6 section + close stamp).
- `reports/csm/GATE_LEDGER.json` (`reboot_rule`): the 22 extraction-gated
  floor rows (21 D6-extraction + `csm-char-04`) + the 10 invariant/residual
  rows stay open by design; the 3 `r1blast-*` rows stay open as stamps.
- `plan/CSM_2PHASE_PLAN.md` P1.3 (L174–185): the meter counts **only the
  fixable rows**; floor + stamped rows are excluded from the halt trip.

## Buckets

- **(a) extraction-gated floor (22 rows)** — the `D6-extraction` class
  (21 rows, closed only in the Phase-2 extraction campaign) **plus
  `csm-char-04`** (R-7x; close lever = Phase-2 extraction track / 5.4
  re-adjudication; confirmed floor by the R-7 close re-sweep).
- **(b) invariant floor (13 rows, stamped by-design open)** — the 10
  documented residual rows (roster 31/88 budget floor `csmdoor-01`; D5
  reachability residuals `csmd5-01/02/03/05/06`, `gate400-320`, `red-R-4`;
  closed-class curation residuals `csm-char-03`, `csm-set-02`) plus the 3
  `r1blast-*` stamped rows (never fix targets; re-probe pass criterion =
  zero new misses, met for `r1blast-tokyo` at the R-7 close;
  `r1blast-blizzard`/`r1blast-marines` held by gate-4 baseline-identity).
- **(c) open fix-class row, fixable in Phase 1 (0 rows)** — none remain.

## The 35 open rows

| id | fix_class | bucket | basis (one line) |
|---|---|---|---|
| csm-dim-arcn-01 | D6-extraction | a | queue row ruling "floor": "extraction-gated (5.4 LIVE; R3 documented floor)"; GATE.md halt rule |
| csm-dim-arcn-02 | D6-extraction | a | same: extraction-gated, 21-red census class (arc-narrative, Hirokazu Arai) |
| csm-dim-arcn-03 | D6-extraction | a | same (arc-narrative, Santa Claus / International Assassins) |
| csm-dim-arcn-04 | D6-extraction | a | same (arc-narrative, Yuko / Justice Devil) |
| csm-dim-arcn-06 | D6-extraction | a | same (arc-narrative, Yutaro Kurose / Katana Man) |
| csm-dim-arcn-07 | D6-extraction | a | same (arc-narrative, Gun Devil) |
| csm-dim-arcn-08 | D6-extraction | a | same (arc-narrative, Beam / Bomb Girl) |
| csm-dim-arcn-10 | D6-extraction | a | same (arc-narrative, Bat Devil) |
| csm-dim-state-01 | D6-extraction | a | same (state-over-time, Nobana Higashiyama) |
| csm-dim-state-02 | D6-extraction | a | same (state-over-time, Haruka Iseumi) |
| csm-dim-state-03 | D6-extraction | a | same (state-over-time, Nail Fiend) |
| csm-dim-state-08 | D6-extraction | a | same (state-over-time, Seigi Akoku) |
| csm-dim-state-09 | D6-extraction | a | same (state-over-time, Tolka) |
| csm-dim-abl-01 | D6-extraction | a | same (abilities, Yoru) |
| csm-dim-abl-02 | D6-extraction | a | same (abilities, Denji) |
| csm-dim-abl-04 | D6-extraction | a | same (abilities, Aki Hayakawa) |
| csm-dim-abl-05 | D6-extraction | a | same (abilities, Power) |
| csm-dim-abl-06 | D6-extraction | a | same (abilities, Reze) |
| csm-dim-abl-09 | D6-extraction | a | same (abilities, Asa Mitaka) |
| csm-dim-appr-06 | D6-extraction | a | same (appearance, Falling Devil) |
| csm-dim-caus-03 | D6-extraction | a | same (causality, Asa Mitaka) |
| **csm-char-04** | **R-7x** | **a** | **R-7 close re-sweep stamp (2026-09-12, `receipts/r7_class_resweep.md`):** the PM-contract ability name sits in section prose only, never named as an ability in the corpus; the R-7 hunk is generation-only, so the row's close lever is the Phase-2 extraction track / 5.4 re-adjudication — the **22nd extraction-gated floor row** (moved from the DRAFT's (c) at the R-7 close, chairman A2) |
| csmdoor-01 | R-3 (queue spelling = red R-3) | b | roster-door 31/88 budget floor: red_list R-3 L43–52 ("a budget floor… documented, not a new failure") + ID-mapping addendum L74–76; **stamped by-design open** (this meter + GATE.md halt rule + GATE_LEDGER reboot_rule) |
| csmd5-01 | R-4/R-2 | b | d5 MISS_DOC residual: red-R-2 close note "5 d5 + gate400-320 stay open as documented residuals for D5/Phase-2"; **stamped by-design open** |
| csmd5-02 | R-4/R-2 | b | same documented D5/Phase-2 residual (Academy Saga Plot Summary); **stamped by-design open** |
| csmd5-03 | R-4/R-2 | b | same documented D5/Phase-2 residual (Academy Saga Story Arcs); **stamped by-design open** |
| csmd5-05 | R-4/R-2 | b | same documented D5/Phase-2 residual (Aging Devil, Primal Fear line); **stamped by-design open** |
| csmd5-06 | R-4/R-2 | b | same documented D5/Phase-2 residual (Aging Devil, Nigh-Absolute Immortality); **stamped by-design open** |
| gate400-320 | R-4/R-2 | b | named in the red-R-2 close note: "gate400-320 stay open as documented residuals for D5/Phase-2"; **stamped by-design open** |
| red-R-4 | R-4 | b | class row of the d5 line-miss class; fix leg (R-2 qa-passage) closed with 2/7 HIT; remaining lever = chunker skip-set (a new chunking/coverage pass); **stamped by-design open** |
| r1blast-tokyo | R-1 (stamped) | b | queue note: "not a fix target"; pinned in `tests/test_csm_router_count_rule.py`; **re-probed live at the R-7 close** (qa→roster, 5/5 divisions, 0 new misses — pass criterion met); re-sweep stamp in `receipts/r7_class_resweep.md` §2 |
| r1blast-blizzard | R-1 (stamped) | b | red_list addendum "Discovery-counting residual": accepted with tripwires; direct re-probe **skipped by council** at the R-7 close (chairman) — held by gate-4 baseline-identity + the CSM-scoped R-7 hunk; stamp in `receipts/r7_class_resweep.md` §2 |
| r1blast-marines | R-1 (stamped) | b | same discovery-counting residual (onepiece, no standing gate); **skipped, same basis**; named follow-up (discovery-counting) stays open at the D5/Phase-2 pass; stamp in `receipts/r7_class_resweep.md` §2 |
| csm-char-03 | R-3 (queue spelling = red R-4/G-CSM-3) | b | bank row of the CLOSED R-3 class (closed with "zero new misses on stamped rows"); 18-vs-11 intruder expectation (red_list L61–62); **stamped by-design open** as a closed-class curation residual |
| csm-set-02 | R-3 (queue spelling = red R-4/G-CSM-3) | b | same: 18-vs-13 intruder expectation (red_list L63–64); **stamped by-design open** |

**Counts: (a) = 22, (b) = 13, (c) = 0. Total 35.** (Supersedes the DRAFT's
(a)=21/(b)=13/(c)=1, residual 34.)

## Blockers (bucket c)

**None.** The DRAFT's only (c) row, `csm-char-04`, was ruled floor at the R-7
close (re-sweep GREEN: the R-7 gate window 4/4 @`81df799` + class re-sweep;
zero new misses, zero new queue rows, no miss-count regression; the row's
close lever is Phase-2 / 5.4 re-adjudication, gate LIVE). With (c) = 0, the
halt is no longer blocked: every non-floor, non-extraction fix-class
(R-1…R-7) is green.

## Verdict — the halt condition (chairman, final wording)

**Phase 1 halts when every non-floor, non-extraction fix-class (R-1…R-7) is
green, the 33-fixable meter reads 33/33 (the 10 documented residual rows
stamped by-design open), and the queue's remaining 35 open rows are all
extraction-gated floor (22, incl. `csm-char-04`), stamped (3 `r1blast-*`),
or invariant/residual (10) — B then writes
`reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops.**

Concretely, at the final commit:
1. The 22 (a) extraction-gated floor rows remain open (Phase-2 closure).
2. The 13 (b) rows remain open (10 stamped by-design open; 3 `r1blast-*`
   stamps; none a fix target).
3. (c) = 0.
4. All four standing gates green at that commit (pytest pin **1,321** /
   eval jjk **31/31** / span-recall **48,572 + 398/400 (99.5%)** /
   canon opm **236/236 @ 79.0%**), per the JJK-100% invariant.
   Env-mcp live-API caveat (chairman A4): the 3 env-mcp failures are the
   known trio that needs a live `:8000`; their live proof is owed at P1.4's
   four-gate copy (service up), not new GPU work.

**Residual open count at halt: 35** (22 (a) + 13 (b) + 0 (c)). Matches
GATE.md's halt rule (22-row floor wording, moved at the R-7 close).

## Carry-over notes (from the DRAFT, still true)

1. `csm-char-03` / `csm-set-02` (b, closed-class curation residuals): bucketed
   (b) because the R-3 class closed with "zero new misses on stamped rows"
   while these two bank rows stayed open; if the R-3 class is ever re-opened
   they move to (c).
2. `red-R-4` (b): the class row stays `open` although the d5 residual
   decision carries its rows to D5/Phase-2; its explicit close stamp lands
   at the D5/Phase-2 pass.
3. `r1blast-marines`'s named follow-up (discovery-counting, onepiece) is not
   a Phase-1 fix target — it rides the D5/Phase-2 pass.