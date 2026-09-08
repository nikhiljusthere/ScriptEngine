# Receipt — twenty-failures author (CSM Wave-2 wave A, 2026-09-09)

**Subagent:** twenty-failures-author (worker, fresh context). **Deliverable:**
`reports/csm/twenty_failures_csm.md` — 20-row frozen acceptance set, all
`status=open`, JJK FAILING_LINES.md shape, correct output + corpus
page/section in the fix/reason cell, receipt path per row.

**Rows (20):**

| gate | rows |
|---|---|
| bank (8) | csm-set-14, csm-set-15 (G-CSM-1 count bypass, recall 0) · csm-fact-06 (G-CSM-2 empty qa bundle), csm-char-04 (7/8, missing PM contract) · csm-set-17, csm-char-03, csm-set-02, csm-set-01 (G-CSM-3 intruders) |
| door (5) | csm-rel-05, csm-rel-08, csm-rel-09, csm-rel-02 (G-CSM-4 relations door, 0/11 found) · csmdoor-01 (Devils roster door 31/88, truncated) |
| d5 (7) | csmd5-01…csmd5-07 (pinned-sweep misses: 3 MISS_DOC + 4 MISS_SPAN, `sweep_qa_e3d73720.jsonl`) |

**Per-row receipts (on-disk):**
- bank rows: `reports/2026-09-08-0752/canon_scores.json` ·
  `reports/2026-09-08-0752/canon_scores_intruders.json` ·
  `reports/2026-09-08-0752/REPORT.md` · `reports/csm/CSM1B_BANK_VALIDATION.md`
  (G-CSM-1/2/3) · `reports/csm/GCSM1_ROSTER_DOOR.md` ·
  `reports/csm/COUNCIL_csm-1b-2.md` (Rulings 1/2) · `series/csm/overrides.yaml`
  (REFUTED note) — each cited in the row's fix/reason cell.
- relations rows: `reports/csm/CSM1B_RELATIONS_BANK.md` (0/11) ·
  `reports/csm/CSM1B_BANK_VALIDATION.md` (G-CSM-4) · Ruling 3.
- csmdoor-01: `reports/csm/CSM3B_PRESTEP.md` §4 ·
  `reports/csm/CSM3B_PRESTEP_ROSTER_PROBE.json` · `reports/comprehension/GATE.md:757`.
- d5 rows: `reports/span-recall/csm/sweep_qa_e3d73720.jsonl` (stamped rows,
  device=cuda, commit=5c424f3, panel hash e3d73720) · `reports/csm/CSM3B_PRESTEP.md` §3.

**Self-check:**
- Row count: 20 (counted, all `status=open`); shortfall: none.
- Every row's truth re-verified in-store 2026-09-09 against
  `series/csm/facts.db` (read-only): Devils=88 members; TSD 1/4/5/6/7 chunk
  mentions 1/31/18/3/12 (TSD 2/3 never named); `Prime Minister Contract` 0
  chunks vs `Prime Minister of Japan` 27; `pulling a cord on his chest` in
  the Denji lead chunk; all 7 d5 lines present at the cited page/section;
  relations table (748 rows) holds every party in the four rel- rows
  (Denji 69 / Makima 33 / Meowy 8 / Asa Mitaka 37 rows).
- Gate column honest: no row labeled d6 — no CSM comprehension-layer receipt
  exists (events build is JJK-only); nothing padded to fill a gate.

**Command audit (read-only; zero engine-model commands; every shell
command <15 s, CPU):**
1. `read` of mandated sources (plan §2c/§9a, CSM3B_GATES, GCSM1_ROSTER_DOOR,
   CSM2_SCOREBOARD, CSM1B_RELATIONS_BANK, CSM1B_BANK_VALIDATION,
   CSM3B_CLOSEOUT, CSM3B_PRESTEP, COUNCIL_csm-1b-2, 0752 REPORT + both
   canon JSONs, questions/csm.json, FAILING_LINES.md, CSM3B_PRESTEP_ROSTER_PROBE.json,
   series/csm/overrides.yaml).
2. `ls` of `reports/` and `reports/csm/`.
3. 3× `scriptengine/.venv/bin/python` read-only sqlite3 queries on
   `series/csm/facts.db` (mode=ro) — schema/counts, store re-verification.
4. Stdlib `grep -v + python3` filter over `sweep_qa_e3d73720.jsonl` (no model).

**Not run:** pytest, eval, span-recall, canon-run, `:8000`, any
engine-model command, git. No engine file touched.

**Risks / open questions:** none blocking. Note: csm-set-17's 7 "intruders"
are themselves TSD4 members of the declared 14-member roster — the G-CSM-3
class fix is door scoping to the question, not member deletion (flagged in
the row). §9a executor consumes the set; rows flip in the triage file, never
in `twenty_failures_csm.md`.