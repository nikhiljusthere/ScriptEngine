# VOID FORMAL — D7 close (council #37, chairman ruling Q5)

Model-free, pre-stamp, executed 2026-09-20 (docs-only standing session;
no GPU, no :8000). Spec: chairman ruling item 2 (R4's 3-check minimal
VOID formal). Any fire ⇒ no close, reconvene. **Result: 3/3 PASS.**

## Check 1 — reboot_rule (gate regression)

- HEAD = `ea9a541c` ≥ `4a8616bd` (merge-base ancestor: yes).
- Gate-relevant diff `git diff --name-only 4a8616bd..HEAD --
  scriptengine series/csm/overrides.yaml tests` = **empty**.
- last_green green @`0c8cc953` per committed `GATE_LEDGER.json`
  (4 gates: pytest 1,331 / eval jjk 31/31 / span-recall 48,572 + 398/400
  live / canon 236/236·10/16·79.0%; ts 2026-09-20T01:34:00+05:30).

**PASS** — the four gates stand; no gate regression.

## Check 2 — d6_flip rc=0 (flips)

Census state **declared** (never the silent 469v469):
- live/worktree census `reports/csm/census_widened_csm_results.jsonl`
  = **469-era product state** (Leg B's grade; flag-OFF; file clean vs
  HEAD, `git status` empty).
- `tools/csm/d6_flip.py` rc=**0**: pre 469/486 = post 469/486, red→
  green 0, green→red 0; oos200 168/200 → 195/200 (delta +27, no
  drop ≥ 3); green30 flips: 0.
- Campaign 473-era: `d6_flip rc 0` **cited** from committed
  `GATE_LEDGER.json` last_green.legs.legA_tiered ("d6_flip rc 0"),
  OOS200 168→198, green30 clean.

**PASS** — no green→red flip in either declared state.

## Check 3 — A20 trigger (A-row closes still red)

- 13 reds @473 derived from committed data: 17 reds @469 (baseline
  `snapshots/census_head_469.jsonl`, 486 rows, 469 MECH_GREEN) − FLIPS
  A {csm-dim-arcn-02, csm-dim-arcn-10, csm-dim-org-03, csm-dim-state-
  08} (`check_targets.py:36`) = 13. Cross-check: 13 == FLOOR16 −
  {arcn-02, arcn-10, state-08} (`check_targets.py:42-49`) — OK.
  The 13: csm-abl-pool-140, csm-abl-pool-358, csm-dim-abl-01/02/09,
  csm-dim-arcn-03/04/06/08, csm-dim-caus-03, csm-dim-state-02/03/09.
- A20's 46-set: `receipts/d6_probe/CONFIRM_FLIPS.json` red2green =
  46 rows, green2red = 0; 46-set ⊆ greens@469.
- **13 reds @473 ∩ 46-set = ∅.**

**PASS** — no A-row closed row is red at 473.

---

3/3 PASS → the D7 close may proceed to the ratification re-stamp and
the docs-only close commit (chairman ruling, execution order step 3).
Attribution note for the close register: 463→469 closed-6 = 4 deriv
{arcn-01, org-05/06, vol-10} + 2 Q1-L1 {csm-dim-chap-01, csm-dim-
arcn-07} (R1 verified; drift D57:2093 "bank 465" — the 2 were a
ledger artifact of D61/63 tracking the deriv leg only).