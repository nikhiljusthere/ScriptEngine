# CSM P1.4 close council — peer reviews (council #29)

- Date: 2026-09-12, 11:32–11:35 IST
- Method: 5 peer reviewers deployed in parallel (owner directive 2026-09-12), each
  fresh-context, zero-GPU, read-only, reviewing the five advisor finals **anonymized by
  letter** (A–E); reviews ≤200 words.
- Provenance: restored from `~/.local/share/opencode/opencode.db` after the 2026-09-12
  reboot; finals transcribed verbatim (final answer only; full thinking traces in
  `/tmp/opencode/council_close/rev_N.txt`).
- R1–R5 mapping: R1 = reviewer 1 = `ses_f6bca5236fferUj4`, R2 = reviewer 2 =
  `ses_f6bca522dffef333`, R3 = reviewer 3 = `ses_f6bca5226ffecaNa`, R4 = reviewer 4 =
  `ses_f6bca5221ffe3oe3`, R5 = reviewer 5 = `ses_f6bca521affeSPwH`.

## R1

**1. Strongest: E.** Only response that read the actual receipts (GATE_LEDGER, 58-row queue, bar-audit JSON) and verified the arithmetic (58 = 22 floor + 33 fixable + 3 stamps). Its CONDITIONAL APPROVE is most defensible: it names the pre-registration's hard rule (no GPU-day until Q1–Q4 are answered *on disk*), patches the self-attestation hole (marker carries the ledger sha256 + floor count, not a bare flag), and gives P1.5 concrete exit conditions (trio 3/3, pin re-pin, ledger). B is runner-up — right minimal verdict, but reads the marker as a 15-min formality.

**2. Biggest blind spot: B.** "Monday is 15 minutes" frames a 51-GPU-hour, self-gated phase as a formality. It misses the self-attestation hole (the campaign writes the very file that gates the phase) and downgrades Q1–Q4 from a pre-registration *condition* to a "3-line caveat, not a block." Approving without the rulings on disk is exactly the gap the pre-registration closes.

**3. All five missed:** the 22-vs-21 mismatch. The floor is 22 rows, but the 5.4 re-adjudication re-verified only 21/21 reds; no one reconciles whether the 22nd row is a red (unproven stable) or a non-red category, so "22-row floor stands" rests on a 21-row re-run. Also: four of five inherited the question's 35-open/33-fixable without the on-disk 58-row queue (only E reconciled it) — the close record's count should come from disk, not the prompt.

## R2

**1. Strongest: E.** Conditional approval, every condition model-free and on-disk — rulings on disk (the pre-registration's "answered on disk" clause), a self-verifying marker (ledger hash + floor count), the character-only census as a P2.1 entry condition, the deferral with an exit condition. No hold: the 5.4 floor is stable; A20 already gates the marker on (a)–(e) + floor. A's HOLD fails on disk: the 200-row held-out is declared (`heldout_declaration_csm.md`, A24/A26). E's "58 = 22+33+3" ignores the ledger's 23 closed rows.

**2. Biggest blind spot: B.** Its numbers check out, but B mis-cites the close copy's commit — af382ee, when `GATE_LEDGER.json` says head=407c016: what a bare marker should carry. "Write the line and commit" makes a self-attesting marker sufficient for 51+ GPU-h; "the MCP bridge fixes it" is unverified — P1.5's scope is pi MCP tools, not the JJK router rule the root cause points at.

**3. What ALL five missed:** (a) The env-mc fix is undefined — root cause = router rule (8d07487) vs test expecting narrative (d531329); none chose test-side vs router-side; router-side collides with the JJK baseline freeze, and E's "re-pin 1,321→1,324" contradicts the ledger's "pin (1,321) unchanged." (b) The 51-GPU-h is double-stale on disk (17,181 base; 4 s/probe fiction; ceiling ≈122h; A17 floor policy missing) — sanity-100's go needs a re-estimation + cap on disk.

## R3

Verified E's arithmetic against the actual queue (58 rows = 22 floor + 33 fixable + 3 r1blast stamps; 35 open = 22 + 10 fixable-open + 3 by-design stamps). E holds up; A's "irreconcilable" objection doesn't.

**1. Strongest: E.** The only response that read the receipts: E's 58-row reconciliation (22 floor + 33 fixable + 3 r1blast stamps) is correct against `miss_queue_csm_iter1.jsonl`, which refutes A's central HOLD argument outright. E's CONDITIONAL APPROVE is the right call — two one-line on-disk conditions (rulings committed with the marker; marker carries sha256 of `GATE_LEDGER`'s `p14_close_copy` + floor count 22) instead of A's HOLD or B's ceremonial gate. E alone also flags that the 60-question census is character-only: 5.4 proves red *stability*, not that the reds need extraction.

**2. Biggest blind spot: B.** B asserts the 200-row held-out leg is "declared on disk" — the question states it is pre-registered nowhere. B approves a ~51-GPU-hour gate on a false verification claim, and never touches A20's self-attestation hole (a file the campaign writes itself gates Phase 2).

**3. All five missed:** the on-disk plan for the 52-page/376-row remainder. All wave it ("alongside" B/C, "already running" D, "compounding asset") without demanding owner, method, and schedule be pre-registered before the GPU day — contradicting the same pre-registration rule the council enforces on Q1–Q4. Also unaddressed: the sanity-100 null branch (extraction closes 0 rows → what happens?) and operational sequencing of the 51 GPU-hours under the Qwen GPU hard rule.

*Correction (parent verification, 2026-09-12): R3's ground 2 is itself refuted on disk —
the 200-row held-out leg IS declared (`heldout_declaration_csm.md`, plan A24/A26; verified
by R2 and R5). B's assertion was correct; R3's review of it was not.*

## R4

**1. Strongest: E.** Only one to reconcile the queue arithmetic (58 = 22 floor + 33 fixable + 3 stamps), which dissolves A's "irreconcilable arithmetic" hold. It alone (a) binds approval to the pre-registration — rulings Q1–Q4 as a committed on-disk file, not the transcript; (b) plugs the self-attestation hole (marker carries sha256 of `GATE_LEDGER` + floor 22; gate verifies the hash); (c) gives P1.5 a real exit (trio 3/3, re-pin 1,321→1,324); (d) uses live numbers (175/537, 1,260 q). A disciplined conditional-approve with a testable exit, not a hold.

**2. Biggest blind spot: B.** Treats the close as 15-minute paperwork, approves with no gate amendment, and is the only response to miss the self-attestation hole — a campaign-written marker gating a 51-GPU-hour phase is ceremonial. Red flag: B pins commit `af382ee`, but the question states `407c016`. Fastest path to execute; leaves Phase 2 on a self-attested boolean.

**3. What all five missed:** the load-bearing "halt met at the floor" rests on a queue accounting in three incompatible forms (question: 35 = 22 + 13; E: 58 = 22 + 33 + 3; B: 22a + 13b + 0c). No one produced a single on-disk canonical breakdown the council ratified; they each assert halt-met. Require one reconciled accounting that the marker hashes, and resolve the disputed commit (407c016 vs af382ee) so the marker encodes the verified commit, not an assumed one.

## R5

Verified the receipts on disk before ranking: `GATE_LEDGER.json` `p14_close_copy` (head `407c016`, queue 35 open/23 closed/58), `HALT_METER_P13` (a=22/b=13/c=0), `CLOSE_COUNCIL_PREREGISTERED.md` (Q1–**Q5**, standing instruction), `CSM_2PHASE_PLAN.md` A16/A20, and `reports/csm/COVERAGE.md` (175/537, 1,260 q).

**1. Strongest: E.** Its numbers check out: 58 = 22 floor + 33 fixable + 3 stamps (halt meter (a)=22/(b)=13/(c)=0; ledger 35/23/58). E alone conditions the marker on the pre-registration's standing instruction (Q1–Q4 rulings committed on disk, before/in the marker commit), fixes A20's self-attestation hole with a one-line sha256 carrier, and gives the env-mcp deferral an exit condition.

**2. Biggest blind spot: B.** B poses as the verified approver but misquotes its own receipt: the ledger's `p14_close_copy.head` is `407c016` (matching the question), not the `af382ee` B cites. "15 minutes, no HOLD" rests on that misread, and B accepts "marker present, nothing else" unchallenged — no self-attestation critique, no pre-marker Q1–Q4 commit that the standing instruction requires before any GPU-day. A is near-miss: two of its three HOLD grounds (the "irreconcilable" 33; the "unregistered" 200-row leg) are refuted on disk.

**3. All five missed:** (a) the pre-registration's closing section — P2.2/P2.4/A17 acceptance bars need the same denominator re-audit before they gate anything; (b) the marker is also the planned one-shot 100k Qwen switchpoint, so the close act includes the checkpoint→qwen-switch chain, not 15 minutes; (c) Q5 (in-parts long prose) got no ruling from A/B/C/E and should be recorded out-of-gate explicitly.

## Cross-note (parent session verification, 2026-09-12)

- **On-disk confirmations:** 58 = 22 floor + 33 fixable + 3 stamps and 35 open = 22 +
  10 fixable-open + 3 stamps reconcile in `miss_queue_csm_iter1.jsonl` (R3 verified
  against the file; E's account stands). Ledger `p14_close_copy.head` = `407c016` (B's
  `af382ee` is the P1.4 stamp commit, not the gate tree — every reviewer who checked is
  right). 200-row held-out leg declared in `heldout_declaration_csm.md` (A24/A26) — A's
  HOLD ground 3 and R3's objection to B are both refuted.
- **Unresolved, carried to the chairman:** (i) E's "re-pin 1,321→1,324" vs the ledger's
  "pin (1,321) unchanged"; (ii) the 22-vs-21 gap (5.4 re-verified 21 census reds; the
  22nd floor row `csm-char-04` is the R-7x class, not in the 60-q census — one-line
  reconciliation owed); (iii) env-mc test-side vs router-side fix undefined; (iv) the
  51-GPU-h is double-stale (17,181-row base; ≈122 h ceiling; A17 floor policy missing) —
  P2.1 step-0 sanity-100 must re-estimate on disk before any go.
- **Q5 (in-parts long prose, 90,421 words / 243 sections)** was ruled only by D (yes,
  in-parts waves); A/B/C/E silent → record explicitly per the chairman.