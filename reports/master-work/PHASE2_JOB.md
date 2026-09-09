# CSM Phase 2 job spec — the pre-baked batch design (owner idea 2026-09-10)

**Read first:** `plan/CSM_2PHASE_PLAN.md` §Phase 2. This file does not replace
the plan's Phase-2 content (A15–A26 all stand); it changes *how* the hours are
spent, not what is measured.

**Do not start any of this until the Phase-1 close council PASSes.** B's
Phase-1 end sequence is unchanged (`PHASE1_JOB.md`, "B's last act").

## The owner's idea, and why it is right

> "prepare all the prompts and everything beforehand, load the model on even
> smaller context, restart and start doing GPU work non-stop, so that no
> thinking is spent in GPU heavy tasks"

The load-bearing observation: **agent reasoning and the GPU job are competing
for the same card.** Every turn B takes while a sweep runs is Qwen decoding at
92–100 % SM utilisation on the same 5090 the embedder and reranker are trying
to use, plus (measured this session) a 37:1 prompt-to-completion ratio from
prefix-cache eviction. Taking the agent out of the loop during the batch
removes both.

**It generalises further than "smaller context" for the sweep leg.** P2.1's
sweep is `span-recall --panel … --door …`, which is HTTP against `:8000` —
the embedder + reranker. **It needs no Qwen inference at all.** So for that
leg the ceiling is not a smaller Qwen, it is **no Qwen**: unload it and the
retrieval stack gets the whole 32 GB instead of the 2.9 GB of headroom it is
squeezed into right now.

**Phase 2's two legs want opposite machines**, which is what makes the
pre-bake worth the effort:

| leg | needs | wants the other unloaded |
|---|---|---|
| P2.1 sweep (17,181 × 3 doors + 200 held-out) | `:8000` embedder+reranker | Qwen **down** → whole card, no SM contention |
| extraction (the 21 D6-extraction reds) | Qwen 27B | `:8000` down or CPU (the standing hard rule) |

Run them as two non-overlapping pre-baked batches, each with the other's model
unloaded, and neither ever waits on an agent.

## The test B runs first (this is the go/no-go, not a rehearsal)

This **is** P2.1 step 0 (A15, the sanity-100 timer) — the plan already forbids
spending a panel hour before a measured re-estimate exists on disk. The
pre-bake does not skip that gate; it makes step 0 also answer the contention
question, for ~40 min total:

1. **Pre-bake everything** while Qwen is still up and B can still think:
   the panel files, the three door commands, the ledger targets, the resume
   flags, the halt conditions, and a single runner script per arm. After this
   point no agent judgement is required to execute.
2. **Arm A — Qwen UP (today's baseline):** `--sanity 100` on qa → narrative →
   roster against the CUDA `:8000`, Qwen resident. Record per-door s/probe.
3. **Arm B — Qwen DOWN:** stop Qwen, re-run the identical three sanity-100
   commands with the whole card free. Record per-door s/probe.
4. **Report:** per-door s/probe for both arms, the ratio, and the full-sweep
   re-estimate (17,181 × measured s/probe **per door**, no uniform-rate
   assumption) for whichever arm wins. Into `reports/csm/GATE.md`.

The pre-registered threshold is unchanged: **re-estimate > 2 GPU-days ⇒
abort / defer / shrink, do not start.** The existing estimates span 8 h to
122 h and the plan itself calls the 51-GPU-h figure fiction, so this
measurement is what decides whether Phase 2's sweep happens at all — arm B
may be the difference between "fits" and "abort".

Sanity-100 rows are `--sanity` first-run-only (resume runs drop it) and are
zero panel spend, so running the three doors twice costs nothing but time.

## What "pre-baked" has to mean, since nothing is watching

A batch with no agent has no judgement, so the script must carry it:

- **Resumable.** The sweep ledgers are keyed and resume-safe (proven through
  P1's gate legs and the two 400-probe restarts). A crash at row 9,000 must
  resume forward, never restart.
- **Halt conditions in the script, not in someone's head.** The engine's
  `--sanity` dead-door halt already exists (CSM-3). Add: stop on `:8000`
  health failure, and stop if the ERROR rate over a rolling window exceeds a
  declared bound — the 11:23 incident wrote 400 straight connection-refused
  ERROR rows into a ledger against a dead service, and no agent noticed for
  minutes.
- **Detached and logged.** `setsid` + a status line per N probes to a log the
  directing session can poll (a detached job reparents out of A's monitor
  tree — established behaviour, so A cannot be the safety net here).
- **A18 control arm.** Default the sweep from zero rather than resuming
  Phase-1-stamped rows, so P1 parser fixes are not attributed to P2.3.
- **A26.** Record `panel_csm.json`'s hash + the held-out hash in GATE.md at
  P2 start, freezing the control-arm inputs in the receipt.

## Better option for the sweep leg: the directing session pilots it, Qwen OFF

The pre-bake design above buys the GPU back by removing the agent's judgement
from the batch. **That trade is unnecessary for the sweep leg**, because the
directing session (Claude, cloud-hosted) does not run on Qwen at all. It can
drive `span-recall` against `:8000` with **Qwen fully stopped**:

- **The whole 32 GB goes to the retrieval stack** instead of the ~2.9 GB of
  headroom it is squeezed into beside a resident Qwen — and, more important,
  **zero SM contention**: today the embedder and reranker share the card with
  a Qwen decoding at 92–100 % utilisation.
- **Judgement is retained during the run.** Halt calls, ERROR-rate triage,
  per-door re-estimates and the A17 floor decisions happen live, which the
  blind-batch design explicitly gives up.
- **No prefix-cache thrash**, because that pathology is a Qwen/pi KV-pool
  artifact and Qwen is not in the loop.

**What this does NOT cover:** the extraction leg (the 21 `D6-extraction`
reds) is genuine 27B work over corpus pages — it needs Qwen, and the standing
hard rule gives Qwen the card alone for it. So the split is:

| leg | pilot | Qwen | `:8000` |
|---|---|---|---|
| P2.1 sweep + sanity-100 | directing session | **stopped** | CUDA, whole card |
| extraction | B (pre-baked, per above) | owns the card | down / CPU |

The owner's pre-bake idea and this are complementary, not alternatives: it is
the right design for the extraction leg, where a local agent's thinking really
does compete with the job.

**Cost of the window:** with Qwen down, A and B have no model and the bay
pauses. So this runs *after* the Phase-1 close council (which B needs Qwen
for), as a bounded window, and A/B relaunch as **fresh** sessions afterwards
(a pi alive across a dial change keeps the stale context window — the
2026-09-10 01:1x lesson).

## Restart sequencing

Stopping Qwen kills A's and B's model — the agents cannot supervise their own
blackout. So the switch is the directing session's, using the established
path (`tools/master-work/switch_restart.sh` / the gpu-handoff chain,
`docs/ops/PC_GPU_HANDOFF.md`), and it happens **after** the pre-bake is on
disk and verified, never before. Sequence: pre-bake + verify → checkpoint →
Qwen down → run arm B detached → Qwen back at the working dial → agents
relaunch → read the receipts.

If a leg genuinely needs a supervising agent, the fallback is the owner's
original form: Qwen at a **small** dial (32k–64k) rather than fully down —
it still frees 10–18 GB, and a pre-baked batch needs almost no context.

## Open question for the owner

Whether the extraction leg's prompts can be fully pre-baked is **not yet
established** — some extraction targets may depend on census output that only
exists once the sweep has run. B should answer that explicitly before the
extraction batch is designed, rather than assuming symmetry with the sweep leg.
