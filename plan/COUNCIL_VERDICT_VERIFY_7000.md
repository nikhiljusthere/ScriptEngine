# Council Verdict: JJK_VERIFY-7000

**Date:** 2026-09-30
**Advisors:** Contrarian, First Principles, Expansionist, Outsider, Executor
**Source question:** Is the VERIFY-7000 inline verification plan structurally sound? What could go wrong?

---

## Where the Council Agrees (High-Confidence Signals)

1. **Fragile checkpointing is #1 risk.** "Save → advance" without atomic transactions/write-ahead logging means crashes corrupt progress. At 6,700 windows, 0.2% silent-fail = 100+ rows lost.
2. **Unbounded retry loops drain throughput.** Model reasons-truncates → retries consume concurrency-2 queue for minutes, zero progress. 5% stubborn rate = 200 zombie sessions.
3. **Two-pass design doubles wall-clock cost.** Rule 9 missed-event pass forces 2 LLM passes per window → ~8-10s/window → 15+ hours total.
4. **Server restart = state loss.** Single-point infrastructure (:18081), no rollback strategy, context purges on NInfer restart.

## Where the Council Clashes

- **7.8% confirmation rate:** C called it "the asset" (hallucination mapping). A/D/E said it proves noisy source data. Resolution: valuable signal but shouldn't romanticize the warning flag.
- **"No auto-verifiers" paradox:** D noted entire pipeline IS auto-verification. Owner's defense: inline wiki lookups add human-level scrutiny. True in spirit, flawed in practice — verdicts still go through model.
- **Parallelization vs discipline:** Multiple advisors pushed batching. Owner explicitly rejected ("quality matters more"). Counterpoint: cross-window contamination degrades accuracy, which inline avoids.

## Blind Spots Caught

1. **Pre-run quality gate untested.** Blind audit mandated before grinding but never run. Starting 1,500 windows without confirming model can handle stricter rules cascades errors uniformly.
2. **Rule 8 output schema undefined.** "Keep every [] verdict row" — what does the format look like post-crash? Rollback impossible without known structure.
3. **Context drift at scale.** None flagged that accumulating 6,700 windows of context will degrade attention quality well before halfway.

## The Recommendation

Three patches before Phase 1:
1. Add transactional checkpoints (`.tmp` + validate + `os.rename()` + `.done` log). <1hr engineering.
2. Cap retries at 3 escalating (10k → 20k → 20k), then `SKIP:<reason>`. Not data loss — marks gaps for later return.
3. Run blind audit sample (10 windows across pools) BEFORE committing to pool order.

## One Thing to Do First

Write the atomic-save wrapper around `save → advance`. 20-line Python change: write `.tmp`, validate JSONL schema, atomic rename, append window ID to `.done`. Once this exists, everything else becomes survivable.
