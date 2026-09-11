# P1.3 halt meter — CSM Phase 1 (DRAFT)

**Status: DRAFT — not a stamp.** This meter finalizes only after the R-7
(`identity_fields`) gate window + R-7 class re-sweep (the csm-char-04 close
path, §Blockers). Until then it is a working instrument, not the recorded
halt record. Re-issue as `HALT_METER_P13.md` at the R-7 close.

**Inputs (all on disk, read 2026-09-12):**
- `reports/csm/GATE.md` — halt rule (L36–44), the four standing gates (L9–18),
  live GREEN state at the R-6 pass (L20–30).
- `reports/csm/miss_queue_csm_iter1.jsonl` — 58 rows; **35 open**
  (status == "open"), matching GATE.md L27 + GATE_LEDGER `queue_stamps`
  (open 35 / closed 23 / total 58).
- `reports/csm/red_list_csm.md` — documented floors/residuals (R-3 L41–52,
  ID-mapping addendum L70–80, R-1 addendum L149–181, R-2 close note).
- `reports/csm/GATE_LEDGER.json` L45 (`reboot_rule`): "The 21 D6-extraction
  rows + the invariant floor rows (csmdoor-01 31/88, D5 reachability
  residuals) are the Phase-2/extraction-gated floor and stay open by design."
- `plan/CSM_WAVE2_RESUME.md` §3 (council trigger) + §5 item 3 (halt on
  miss-count regression / two no-reduction iterations); `plan/CSM_2PHASE_PLAN.md`
  P1.3 (L174–185): the meter counts **only the fixable rows**; the 22 floor
  rows + 3 stamped rows are excluded from the halt trip.

## Buckets

- **(a) extraction-gated floor** — `D6-extraction` class; closes only in the
  Phase-2 extraction campaign (GATE.md L38–39: "the D6-extraction class
  (21 rows, closed only by the Phase-2 extraction campaign)").
- **(b) invariant floor** — documented floor rows: the roster 31/88 ceiling
  (GATE.md L39–40), D5 reachability residuals that need a new
  chunking/coverage pass, not a retrieval fix (GATE.md L40–41), and
  bank-curation residuals of CLOSED fix classes (stamped rows, tripwired,
  "not a fix target" — red_list R-1 addendum L168–175).
- **(c) open fix-class row, fixable in Phase 1** — these BLOCK the halt.

## The 35 open rows

| id | fix_class | bucket | basis (one line) |
|---|---|---|---|
| csm-dim-arcn-01 | D6-extraction | a | queue row ruling "floor": "extraction-gated (5.4 LIVE; R3 documented floor)"; GATE.md L38–39 |
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
| csmdoor-01 | R-3 (queue spelling = red R-3) | b | roster-door 31/88 budget floor: red_list R-3 L43–52 ("a budget floor… documented, not a new failure") + ID-mapping addendum L74–76 ("expected invariant at sweep time, a regression on it is a new miss = halt"); GATE.md L39–40 |
| csmd5-01 | R-4/R-2 | b | d5 MISS_DOC residual: red-R-2 close note (queue L22) "5 d5 + gate400-320 stay open as documented residuals for D5/Phase-2"; queue note "if structural, escalate to floor" |
| csmd5-02 | R-4/R-2 | b | same documented D5/Phase-2 residual (Academy Saga Plot Summary) |
| csmd5-03 | R-4/R-2 | b | same documented D5/Phase-2 residual (Academy Saga Story Arcs) |
| csmd5-05 | R-4/R-2 | b | same documented D5/Phase-2 residual (Aging Devil, Primal Fear line) |
| csmd5-06 | R-4/R-2 | b | same documented D5/Phase-2 residual (Aging Devil, Nigh-Absolute Immortality) |
| gate400-320 | R-4/R-2 | b | named in the red-R-2 close note (queue L22): "gate400-320 stay open as documented residuals for D5/Phase-2" |
| red-R-4 | R-4 | b | class row of the d5 line-miss class; fix leg (R-2 qa-passage) closed 2026-09-09T21:05Z with 2/7 HIT; remaining lever = chunker skip-set (a new chunking/coverage pass = bucket b per GATE.md L40–41) |
| r1blast-tokyo | R-1 (stamped) | b | queue note: "not a fix target"; red_list R-1 addendum L168–175: stamped post-hoc record, positive delta, pinned in `tests/test_csm_router_count_rule.py`; pass criterion = zero new misses on stamped rows |
| r1blast-blizzard | R-1 (stamped) | b | red_list addendum L168–179 "Discovery-counting residual": accepted with tripwires (pin + stamp + zero-new-miss); "Re-probe after R-7's key-map widening lands" |
| r1blast-marines | R-1 (stamped) | b | same discovery-counting residual (second live case, onepiece); accepted, tripwired, re-probe post-R-7 |
| csm-char-03 | R-3 (queue spelling = red R-4/G-CSM-3) | b | bank row of the CLOSED R-3 class (red-R-3 closed 2026-09-09T21:05Z, "zero new misses on stamped rows"); row stays open as a closed-class curation residual (18-vs-11 intruder expectation, red_list L61–62) |
| csm-set-02 | R-3 (queue spelling = red R-4/G-CSM-3) | b | same: closed-class residual (18-vs-13 intruder expectation, red_list L63–64) |
| csm-char-04 | R-7x | c | queue note: "PM-contract ability sits in section prose, never a named heading; extraction stored nothing (abilities extraction track; 5.4 gate LIVE)"; ruling "floor" but the close lever (R-7 `identity_fields`) is a Phase-1 no-council pass (council P1 A6) → the one (c) row |

**Counts: (a) = 21, (b) = 13, (c) = 1. Total 35.**

## Blockers (bucket c)

**`csm-char-04` (R-7x) is the ONLY open (c) row** and the only row that can
move (c) → closed in this window.

- **Expected close path:** the R-7 `identity_fields` engine hook (the 61/62-key
  infobox key map, `series/csm/overrides.yaml` field + series-agnostic engine
  branch — recorded "ENGINE HOOK PENDING" in `reports/csm/override_fixes_iter1.md`
  §3) lands as a **separate short no-council pass** (council P1 A6), inside a
  **gate window** (the four standing gates green on CUDA), followed by the
  **R-7 class re-sweep** (the abilities extraction track, 5.4 gate LIVE;
  own-new-row HIT + zero new misses on stamped rows, per the class-closure
  rule). A HIT on the "Every ability of Makima" probe closes the row.
- If the R-7 gate window + re-sweep does NOT hit, csm-char-04 stays open as a
  (c) row and **blocks the halt** (halt-to-council per §5 item 3, not a floor).
- The three `r1blast-*` stamped rows and the D5/D6 residual rows are (b) by
  construction: they stay open at halt by design (GATE_LEDGER L45) and cannot
  block it; none of them closes in this window either.

## Verdict — the halt condition

**Phase 1 halts when: all open rows ∈ {a,b} ∪ {closed R-7 rows} and the 4
standing gates are green at the final commit.**

Concretely, at the final commit:
1. The 21 (a) D6-extraction rows remain open (Phase-2 closure).
2. The 13 (b) invariant-floor/residual rows remain open (documented:
   `csmdoor-01` 31/88 held, 7 d5-class rows carried to the D5/Phase-2 pass,
   3 R-1 stamped rows + 2 R-3 closed-class rows tripwired, none a fix target).
3. The 1 (c) row `csm-char-04` is **closed** by the R-7 gate window + class
   re-sweep (i.e., it sits in the {closed R-7 rows} set). If it did not
   close, the set condition fails and Phase 1 does NOT halt.
4. All four standing gates (GATE.md L9–18: pytest / eval jjk 31/31 /
   span-recall 48,572 + 400-probe ≥ 390/400 / canon opm 236/236 @ 79.0%) are
   green at that commit, per the JJK-100% invariant.

**Expected residual open count at halt: 35 − 1 = 34** (21 (a) + 13 (b));
the 1 closed row is csm-char-04 via R-7. This matches GATE.md L42–44:
"when every non-floor, non-extraction fix-class is green and the queue's
remaining open rows are all extraction/floor, B writes
`reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops."

## Drafting notes (ambiguities resolved in this draft — re-check at the R-7 close)

1. **csm-char-04 is ruled "floor" in the queue** and the session-audit council
   counted it inside "22 extraction-gated floor rows (21 D6 + 1
   extraction-gated)" — yet its close lever (R-7 `identity_fields`) is a
   Phase-1 no-council pass. This meter therefore buckets it (c), not (a)/(b):
   the documented floor set stays 22, but one of those 22 (csm-char-04) is
   Phase-1-reachable, so the halt set is {a,b} ∪ {closed R-7 rows} rather than
   {a,b} alone.
2. **csm-char-03 / csm-set-02 (b, closed-class residuals):** no receipt
   explicitly stamps them as residuals — the R-3 class row (red-R-3) closed
   with "zero new misses on stamped rows" while these two bank rows stayed
   open. Bucketed (b) by inference (class closed, rows open, no extraction
   dependency); if the R-3 class is ever re-opened they move to (c).
3. **red-R-4 (b):** the class row is still `open` although the d5 residual
   decision (red-R-2 close note) already carries its rows to D5/Phase-2 and
   the override-first leg was verified in the iter-1 override package ("0 rows
   close — all 13 d5 line-misses verified R-2"). It is bucketed (b) as a D5
   reachability residual; its explicit close stamp should land at the D5 pass.