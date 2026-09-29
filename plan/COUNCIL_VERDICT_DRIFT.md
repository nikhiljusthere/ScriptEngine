# Council Verdict: Drift Prevention for JJK_VERIFY-7000

**Date:** 2026-09-30
**Advisors:** Contrarian, First Principles, Expansionist, Outsider, Executor
**Peer Reviewer:** [codebase-memory agent]
**Source question:** Additional mechanisms to detect/prevent model drift over 7,000 inline verification windows?

---

## Where the Council Agrees

**Golden sentinels/probes are the single most valuable addition.** Every advisor except the Contrarian proposed embedding pre-adjudicated test windows throughout the pipeline. But they converged on a key distinction: *disguised inserts* (arriving identically to production) beat *fixed-interval sentinels* (which the model can learn to recognize and special-case). **Recommendation: embed 2 golden probes per 200 windows**, drawn from the full range of difficulties.

**Statistical process control beats periodic sampling.** A Shewhart chart or EWMA (exponentially weighted moving average) of the per-100-window acceptance rate catches gradual drift *before* it corrupts thousands of results. Periodic checks at fixed intervals let slow degradation hide in the gaps.

**Detect format drift, not just factual drift.** Two models can agree on style while both hallucinate identically. Tracking what changes — acceptance rate, rule citations used, rejected-vs-accepted subject distribution — tells you *how* the model is drifting, not just that it is.

**Action thresholds must be explicit.** All advisors proposed detection but left "what to do when detected" underspecified. The council converged on: golden probe failure → immediate Ruling Card refresh + restart last 20 windows from checkpoint. Acceptance rate >2pp deviation from EWMA baseline → same response.

## Where the Council Clashes

**Second-model sanity check: useful or wasteful?** The Contrarian and First Principles argued it's wrong-headed at 7.8% acceptance — double the cost for even fewer accepted rows. The Executor and Expansionist countered that a sampled second-pass (only on accepted windows, different prompt template) catches plausible-but-wrong verdicts at ~1% marginal cost. Resolution: do it, but only as a 50-window sample audit, not full re-processing.

**Treating drift as failure vs feature.** The Expansionist argued the 92.2% rejection rate isn't noise — it's structured signal mapping where understanding diverges from source truth. Others treated it purely as a defect. Both views hold: the rate is analytically valuable data AND a warning that something structural may be wrong.

**Golden probe frequency: every 200 or every 50?** First Principles said 200; Contrarian suggested embedding anchors that "never move"; Executor said "every 50." Trade-off: more frequent = better detection but higher cost.

## Blind Spots Caught

**Reviewer flagged 4 critical omissions ALL advisors missed:**

1. **Order effects:** Position within the run matters. Context-window boundary effects are well-documented LLM artifacts relevant given the 262k mode. Earlier/later windows behave differently.
2. **Passage-length confounder:** Larger windows may inherently produce lower acceptance regardless of drift. Without controlling for this, apparent drift may just be window-size distribution shift.
3. **Cost/benefit budget:** Every added guard burns tokens and latency across ~6,700 windows. No one computed the actual compute overhead of their proposals.
4. **Automated remediation:** Everyone proposed detection but left the action undefined. When gold fails: halt? roll back? adjust?

**Additional insight from the Contrarian:** The 7.8% acceptance rate itself is THE ROOT CAUSE. All guard proposals layer atop an unknown baseline defect. If the system starts rejecting at 7.8%, adding sophistication won't help until you understand why.

## The Recommendation

### Immediate actions (Monday-morning, <1 hour total engineering):

1. **Disguised golden probes: 2 per 200 windows.** Extract from existing `gold600/` data. They arrive identically to production windows. If either fails → immediate action (see below). **Cost: ~2 API calls per 200 windows (~1% overhead).**

2. **EWMA acceptance-rate chart on `verify_monitor.py`.** Currently shows per-pool progress. Add a rolling 200-window EWMA overlay. Alert threshold: ±2pp from baseline. **Cost: a few lines in the monitor's HTML generation.**

3. **Define the remediation protocol explicitly.** Golden probe failure OR EWMA alert → (a) trigger Ruling Card refresh, (b) reload the last 20 verified windows from `.done` checkpoint, (c) verify them again under fresh context. If ≥1 still disagrees → flush and restart the entire block.

### Medium-term (after first pool complete):

4. **Rule-citation distribution monitoring.** Log which guideline sections the model cites in the `rule:` field. If citations shift away from stricter sub-rules over time, the model is relaxing standards even if acceptance looks stable. Simple histogram — no LLM needed.

5. **Thematic consistency gate.** Group accepted events by narrative domain (Shibuya Incident, Culling Game, character arcs). Track acceptance rate per domain. Sudden collapse in one domain = corpus-region issue, not global drift. Faster fix: entity set expansion, not whole-pipeline re-run.

### What NOT to do:

- Do NOT run a second-model pass on all accepted rows (too expensive, unclear ROI).
- Do NOT treat the 7.8% acceptance rate as acceptable without diagnosing why.
- Do NOT add more than 3 simultaneous detection mechanisms — diminishing returns.

## The One Thing to Do First

**Add disguised golden probes to your output JSONL format.** Create a small file (`series/jjk/training/golden_probes.jsonl`) with 20–30 pre-adjudicated windows covering all difficulty tiers. During verification, after every 100 windows, insert 2 from this file. Mark them in output as `"__is_probe": true`. Monitor dashboard already tracks them — any probe failure triggers an immediate alert. Cost: negligible compute impact, maximum signal for minimum effort.
