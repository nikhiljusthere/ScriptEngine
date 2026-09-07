# COUNCIL — next move after Phase 5 closure: the 5-step retrieval-only sequence

Date 2026-09-07. User directive (standing): after the demand audit, the
council decides the next move — do not ask for instructions; if stuck, run
`llm-council`. This record is the next-move council's verdict: the ordered,
retrieval-only sequence to clear before resuming the phase plan from
checkpoint `2ea235e`, and the items it explicitly defers.

## Context the council weighed

- **Phase 5 is closed on the data** (`COUNCIL_phase5-closure.md`, #10): not
  extracting the five prose dimensions loses no data (prose preserved + 100%
  span-recall; a field is a lossy, citation-severing derivative). What's
  *not* earned is evidence that retrieval actually **serves** all of it.
- **Demand audit done** (recorded in #10): Personality (HIGH), History (HIGH),
  Appearance (MODERATE), Overview (MOD-LOW), Trivia (LOW). Four of five
  dimensions are genuinely consumed by the script genres (cited prose,
  chapter/episode-sourced); Trivia is light. The "close outright if demand ≈ 0"
  branch is **not** taken.
- **The standing gate protects none of the five.** `gold_jjk.json` (24 Q) and
  `ORACLE_v1.yaml` (18 items) target *no* Appearance/Overview/Trivia/History
  item — only E1–E4 (Personality). So the standing regression gate does not
  guard the dimensions scripts actually use.
- **The 2C gate (beam-first) is 16/18** with A4 (outcome) + C1 (timeline,
  documented expected-fail) open; A4's root cause is pinned and fixed
  (`COUNCIL_2c-gate.md`, commit `6af92ca`).

## Where the council agreed

- **Retrieval-only, no 27B extraction, ever, for any of this.** The 27B batch
  is the scarce, load-sustaining path (it OOM-crashed at 508/524 when
  co-located with the :8000 reranker). Every gate below is a relevance/
  reachability check over the *preserved prose* — fix retrieval
  (scope-word misroute / cross-page confusion / chunker / fusion), never
  reopen extraction.
- **Fix the one known open miss before the census.** A4 is a diagnosed,
  localized door bug; leaving a known-failing item while running a 545
  census would pollute the census signal. Fix it, re-gate, *then* measure.
- **The census must be demand-weighted, not flat.** Demand is HIGH for
  Personality/History, MODERATE for Appearance, MOD-LOW for Overview, LOW for
  Trivia. A flat 545 run wastes budget on low-demand pairs and under-tests the
  high-demand ones. Weigh the gate by the audit's demand tiers.
- **Fold representative items back into the gold bank.** Because the standing
  gate protects none of the five dimensions, the census should promote a
  representative slice of each used dimension into `gold_jjk.json` so the
  standing regression suite guards what scripts actually consume.

## Where the council clashed

- **Census-first vs fix-first.** One position ran the 545 census immediately
  (the known miss is one row among 545; let the census expose everything at
  once). The carried position fixed A4 first: a *diagnosed* miss is cheaper to
  close now than to re-triage among 545 census failures, and the census is
  only interpretable when known bugs are already out. **Carried: fix-first.**
- **TF-IDF trait index now vs later.** One position built the optional
  cross-character facet index (the "which characters are kind?" aggregation)
  as part of this pass. Counter: it is a *capability* add, not a data-
  safety gate, and the end goal is script writing from cited prose, not
  cross-character enumeration. **Carried: defer** the TF-IDF index (and the
  cross-series gate) out of this sequence.
- **Per-dimension closure granularity.** The council reaffirmed closure is
  *per-dimension* (coverage is uneven: Overview 41/218, 80 pages have no
  Personality); the gate must pass per used dimension, and return an explicit
  "no section found" signal on a missing section rather than a silent miss the
  writer fills by inference.

## The verdict — the ordered 5-step sequence (retrieval-only)

1. **Fix A4 (the live-qa door drop).** *Done* — `6af92ca`; oracle 17/18
   (only C1, a documented expected-fail), pytest 1239, eval 24/24,
   span-recall 100%.
2. **3-way failure taxonomy.** Classify every open miss (the 2C remainder and
   the coming census failures) into exactly one of:
   **(a) retrievable-but-not-served** (the answer is in the corpus + a chunk
   but retrieval didn't surface it) → fix retriever/roster/chunker/fusion;
   **(b) absent-from-corpus / cross-page** (the answer lives on another page
   or not in the wiki) → re-scope or retire the item as cross-page;
   **(c) gold/oracle item wrong** (ground truth mis-stated or unanswerable as
   phrased) → fix or retire the item. Never rephrase a question to dodge a
   failure — diagnose the class and fix the gap.
3. **Fold demand-audit items into the gold bank.** Promote a representative
   slice of each *used* dimension (Personality, History, Appearance, Overview;
   Trivia at low weight) into `gold_jjk.json` so the standing gate protects
   what scripts actually consume.
4. **Demand-weighted pilot.** Run the relevance gate on a demand-weighted
   subset (heavy on Personality/History, light on Trivia) as the fast signal
   before the full census.
5. **Full 545 census.** One question per existing (dimension, character) pair
   (138+145+41+121+100 = 545); top beat must be that character's own section
   with a valid chapter/episode citation; retrieval-only. Pass per used
   dimension → close, rate recorded in `COVERAGE.md`; fail → classify per
   step 2 and fix retrieval.

**Deferred out of this sequence (council):** the optional **TF-IDF trait
index** (cross-character facets) and the **cross-series gate** (aligning
span-recall oracle policy with the chunker's skip-policy across the other 7
wikis). Neither is a data-safety gate for JJK script writing; both are
capability/coverage adds to revisit after the census.

## Verified-claims ledger (checked this run)

- [x] Phase 5 closed on the data; 545 (dimension,page) pairs; ~106k words —
  `COUNCIL_phase5-closure.md` (#10), `series/jjk/wikitext/*.json`.
- [x] Demand tiers (Personality/History HIGH, Appearance MODERATE, Overview
  MOD-LOW, Trivia LOW) — demand audit in `COUNCIL_phase5-closure.md` (#10).
- [x] Standing gate protects none of the five dimensions (only E1–E4) —
  `scriptengine/eval/gold_jjk.json`, `plan/ORACLE_v1.yaml`.
- [x] 2C beam-first 16/18 (A4 + C1 open); A4 root cause + fix + 17/18 re-gate —
  `COUNCIL_2c-gate.md`, commit `6af92ca`.
- [x] The 27B batch is the scarce, load-sustaining path (508/524 OOM) —
  infrastructure hard rule (CLAUDE.md).

## Evidence pins

- `COUNCIL_phase5-closure.md` (#10) — the closure + demand audit this builds on.
- `COUNCIL_2c-gate.md` — the 2C result + A4 fix this sequence completes step 1 of.
- `plan/ORACLE_v1.yaml`, `plan/flow.md` (Phase 5 gate), `series/jjk/facts.db`.