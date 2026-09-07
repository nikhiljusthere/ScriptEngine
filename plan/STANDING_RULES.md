# STANDING RULES

**These three rules hold for the entire run — every phase, every excursion,
every fix loop.** They are repeated verbatim at the top of `flow.md`,
`Plan_to_perfection.md` and `drift_log.md`, deliberately and redundantly, so
that reading any one plan document is sufficient. If work drifts far enough
that only one document is in view, these rules are still in it.

---

## 1. No user input. None, for the duration of this plan.

Every wall where you would normally stop and ask — a design fork, an ambiguous
result, a blocked step, a judgement call, two defensible options — **you run
`llm-council` instead.** The council decides; you act on its verdict and record
it. Do not ask for approval, do not ask which option to take, do not ask
whether to proceed, do not stop to report progress and wait.

The only stop before the plan completes is the halt path in `flow.md` — and
that runs a council first, and stops only if the council finds the halt
unresolvable inside the plan as written.

**A council you run is not a substitute for evidence.** Its claims are
DB-verified before being recorded; a claim that fails verification is struck
with the correction noted. A council that cannot be verified against the store
did not happen.

---

## 2. The GPU is available. Do not default to CPU.

Qwen's compute idles while a shell command runs, and its resident weights leave
roughly **7.4 GB free** on the 32 GB card — enough for the **~5.3 GB retrieval
stack** (cross-encoder + embedder). Tests, the `:8000` server and the census
all run on GPU **without stopping Qwen**.

*Measured 2026-09-07: ninfer-serve 24,670 MiB resident, a co-located retrieval
process 6,186 MiB, 991 MiB spare — co-location working under real load.*

**Two qualifications, because the margin is thin:**

- **Check `nvidia-smi` free memory first and size the job against it.** With a
  retrieval job already co-located the spare can fall under 1 GB; a second
  concurrent GPU job will OOM.
- **A sustained 27B extraction batch wants the card to itself.** One such batch
  OOM-crashed at 508/524 when co-located with the reranker. Short retrieval
  jobs co-locate safely; long 27B passes do not.

The default is GPU. Falling back to CPU is a decision that needs a reason —
a measured VRAM shortfall — not a habit.

---

## 3. Council cadence — three mandatory points

1. **Every 2–3 completed todos:** a council reviewing **the fixes just made**.
   Not the plan, not the strategy — the fixes. Did they do what they claimed?
   Is the evidence real?
2. **At the end of every sub-list** (`1a–1d`, `X1.a–X1.f`): a council assessing
   whether the sub-list actually completed — **before the return pointer
   fires.** A sub-list is not done because its last line was reached; it is
   done when a council says the work behind those lines holds.
3. **At every phase gate:** the gate council already specified in `flow.md`.

Write each council to `reports/comprehension/COUNCIL_<subject>.md` and commit
it with the work it reviewed. **If it is not on disk, it did not happen.**
