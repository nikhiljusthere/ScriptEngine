# COUNCIL — CSM D7 re-score (2026-09-18, council #36)

## Question

Decide the D7 re-score after the committed derivation leg (HEAD `20d6da4e`,
post-commit gate window `/tmp/d7_gates` ALL PASS, D6 CLOSED): (Q1) order —
grade the two uncommitted narrow legs (TIERED / ABILWIDTH, 44-line diff in
`scriptengine/api/context.py`) vs the GATE-ordered focus-resolution spike
first; (Q2) ship ABILWIDTH unflagged (as-implemented) vs flagged; (Q3) GPU
path — 100k switch (stale state record) vs stop→grade→restore-135k window
vs CPU (forbidden >15 min); (Q4) scope of the owner-ordered single-subagent
task. Framed question + evidence pack:
`reports/csm/receipts/council_d7_rescore/framed_question.md`.

## Members

11: 5 advisors + 5 peer reviewers + chairman.

| Letter | Role | File |
|---|---|---|
| A | The Executor | `advisors.md` (final verbatim) |
| B | The Outsider | `advisors.md` |
| C | The First-Principles Thinker | `advisors.md` |
| D | The Contrarian | `advisors.md` |
| E | The Expansionist | `advisors.md` |
| R1–R5 | Peer reviewers | `reviews.md` |
| Chair | Chairman | `chairman.md` |

**Method note:** all 11 ran **strictly sequential** (owner rule 2026-09-08:
one subagent at a time; the session itself runs on the Qwen server, so the
2026-09-12 parallel-batch exception does not apply), each fresh-context,
zero-GPU, read-only. Advisor sessions `ses_f4bbd8163ffe…` (A) …
`ses_f4bbf8b4cffe…` (E); reviewers `ses_f4bbc4629ffe…` (R1) …
`ses_f4bb4aad0ffe…` (R5); letter↔session maps in `advisors.md` /
`reviews.md`. The chairman ran as a single fresh-context subagent
(`ses_f4bb05537ffeYp79GIRq7R63az`). All finals + the verdict were
**restored verbatim from opencode.db session transcripts** (in-conversation
copies truncated the chairman at clash C2); transport markers stripped, no
words changed.

## Verification notes

Chairman re-verified every load-bearing claim against disk before ruling;
the opencode session additionally spot-checked after the ruling:

| Claim | Verification | Result |
|---|---|---|
| D59's 473 tree excluded the ABILWIDTH hunk | `reports/csm/receipts/d6_probe/ABILWIDTH_PREDICT.md` post-dates D60's "remaining reds: 17" and was authored at D62 staging; pool-140/358 stayed red in D59's run | **Confirmed** — C's receipts question settled negatively; the full-bank ABILWIDTH grade genuinely remains unbought; the window is needed (receipts-read stays pre-check #1) |
| ABILWIDTH "never pre-registered" (D/R4) | `ABILWIDTH_PREDICT.md` exists, headered "written BEFORE the change," with registered flips + kill clause + the *deliberate* "behind no new flag" choice | **False as stated** — a pre-registration exists; the council overrode its unflagged choice on the JJK-baseline-untouched rule (Q2) |
| 17-vs-23 red arithmetic (R4) | p23 486-bank: 486−469 = **17** reds (D60 list: org-03, pool-140/358 + 14 floor); OOS200 second instrument 194/200 ⇒ **6** reds; 17+6 = **23** = 7 D7 holdout rows (org-05/06/vol-10 green post-commit ⇒ 4 live D7 reds: chap-01, org-03, pool-140/358) + 16 Phase-2 floor rows | **Confirmed** — instrument ownership to be re-stated by the task's pre-check |
| OOS floor authority | `tools/csm/d6_flip.py` exit-2 = any green30 flip OR oos200 drop ≥ 3 vs `D6_OOS_PRE.jsonl` | **Confirmed** — that is the named floor |
| 135k live profile | `ps` 16:4x: pid 1137321, `--max-context 135168 --kv-capacity 143360`, 26,948/32,607 MiB (chairman) / 26,962 used / 5,142 free MiB (SWITCHPOINT 16:4x); `qwen_mode.txt` STALE (last entry 2026-09-17 100k); `tools/csm/d7_gates.sh` restore argv STALE (65k) | **Confirmed** — (a) rides a stale record; restore must be from freshly captured argv |
| TIERED flag-off byte-identity | asserted in the diff, not proven | **Folded into the gate run** (flag-off gates = the JJK no-op proof), not a separate ceremony |

## Verdict (chairman, full text `chairman.md`)

**Legs first, singly (A → B → C), in one detached kill-window; the
focus-resolution spike runs immediately after, GPU-free, in the live
session.** ABILWIDTH **flagged** behind a new
`SCRIPTENGINE_ABILWIDTH_RECALL` (default OFF, 3-line mirror of
`_tiered_enabled`) — **ruled against the 3-advisor as-is majority (A, C,
E)** on the JJK-baseline-untouched hard constraint (its JJK no-op was
data-dependent, not by construction). GPU path **(b) 4–1** (only E for
(a)): stop owner-manual 135k → grade legs + four standing gates on the
whole card → restore 135k from the freshly captured argv — executed as
**one `setsid nohup` detached chain** (`tools/csm/d7_window_chain.sh`)
issued as the subagent's final act; every post-kill step is shell (the
session runs on the killed server). GATE's "spike first" line ruled
**stale/superseded** (predates D59, which already flipped D7 row org-03).

### Rulings (summary)

- **C1** — C's "read D59 receipts first" is right as a pre-check, wrong as a
  window-killer: the timeline verifies ABILWIDTH ∉ D59's tree, so the
  window stands with the receipts-read as pre-check #1 (record, not gate).
- **C2** — flag ABILWIDTH (against A/C/E): makes the JJK no-op structural,
  turns rollback from "revert hunk" into "unset flag"; standing rule: JJK
  baseline-exact is a hard constraint and the gates exist to police exactly
  this.
- **C3** — legs before the spike (against GATE's own line, and D/E): the
  legs are the pre-registered fix-class closure; the spike is an
  unregistered probe on a row in none of the D7 holdouts, with zero code
  overlap. Spike survives as the *next* task, GPU-free.
- **C4** — A's "stop Qwen at step 2" design is fatal (unanimous R1–R4):
  the agent is the Qwen model. R3's detached-chain insight dissolves both
  A's and D's constraints: kill → grade → gates → restore → receipts is one
  shell artifact; no LLM step follows the kill.
- **C5** — TIERED's +4 flips extraction-floor rows (arcn-02/10, state-08):
  the receipt must **re-count the 16-row floor after the legs** and
  GATE.md carries the re-count; the 473 itself stands.
- **C6** — 17/6/23 arithmetic + floor authority verified (table above); the
  task re-states instrument ownership before any pass bar is applied.

### Task spec (Q4, full text in `chairman.md`)

One subagent task, two phases. **Phase 1 (LLM alive, Qwen 135k):** six
pre-staging steps — (1) D59 receipts gate (if contradicted: discard legs
B/C, no window, record + stop); (2) 17/6/23 arithmetic re-statement + HEAD
census baseline = 469-era confirmation; (3) OOS floor authority recorded +
`D6_OOS_PRE.jsonl` backed up; (4) TIERED flag-off inertness by read;
(5) argv capture + verification (`/tmp/d7_qwen_{pid,argv,cwd}.txt`,
`test -x` binary, `test -e` model path); (6) snapshots to
`reports/csm/receipts/d7_window/` + the 3-line flag edit (Q2) +
`PREDICT.md` (per-leg pass bars: Leg A W ≥ 469 w/ flips ⊇ {arcn-02,
arcn-10, org-03, state-08}; Leg B W ≥ 469 w/ flips ⊇ {pool-140, pool-358};
Leg C the union; each 0 counter-flips, blind 19/19, `d6_flip.py` rc=0;
plus the floor re-count) + `check_targets.py` + the SWITCHPOINT
governance commit (engine code stays uncommitted). **Phase 2 (shell
only):** the chain — kill 135k → poll ≥ 8 GB free → legs A→B→C singly
(stop at first red) → four standing gates (both flags default OFF) →
restore 135k from captured argv → `RECEIPT_DONE`. Pass bar (whole task):
all three legs PASS; pytest 1,331 pin; eval jjk 31/31; span-recall jjk
48,572 rc=0 + 400-probe ≥ prior baseline; canon opm ≥ 10/16 · 236/236 ·
79.0%. Stop conditions: any leg RED → halt remaining legs, gates still run
for the record, restore Qwen, receipt = RED + that leg's kill clause (no
ex-post retuning, D59); OOM / restore failure → receipt, owner relaunches
manually; **no commit of engine code without owner word.**

**Post-commit flag configuration (R5 gap, closed):** both flags ship
default OFF; the CSM campaign grade (`p23_grader`) runs **flag-ON**; the
four standing gates run **default-OFF** (the committed tree — the
structural JJK no-op proof). **Default-flip (shipping CSM default-ON) + its
4-gate rerun + GATE.md record: deferred** to a separate owner decision.

## Residuals

- **Owner resume path:** the subagent's final act kills its own model; the
  owner runs `opencode -c` and reads
  `reports/csm/receipts/d7_window/RECEIPT_DONE` + `/tmp/d7_gpu_chain.log`.
  No sentinel within the hour ⇒ card in known-bad state ⇒ owner relaunches
  135k by hand from the captured argv.
- **Stale switch machinery:** `qwen_mode.txt` (stale since 2026-09-17) and
  `tools/csm/d7_gates.sh` (65k argv) remain stale; the captured-argv
  restore supersedes both for this window only.
- **P6 framing (E):** the TIERED/ABILWIDTH mechanisms are generic
  cross-corpus retrieval primitives — recorded as the P6 seed; P6 stays
  deferred until Phase 1 closes (campaign rule), the spike is the first P6-adjacent task.

## Next

Single-subagent task per the chair's Q4 spec (launch from the live 135k
session, final act = issue the chain). Then: owner reads receipts; commit
engine diff only on all-green + owner word; focus-resolution spike
(GPU-free) is the following task.