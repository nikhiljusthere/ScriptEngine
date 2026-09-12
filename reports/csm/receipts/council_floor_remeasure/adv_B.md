# Advisor B — scope and consequence

Lane: assuming the measurement finding (`reports/csm/EXTRACTION_FLOOR_REMEASURED.md`)
is broadly right, what should Phase 2 do?

## 1. The finding reshapes P2.3; it does not void it

`plan/CSM_2PHASE_PLAN.md` §Phase 2(3) already pre-registered this exact
situation. **A22**: the null branch — "the re-adjudication closes all 21 reds,
de-scoping P2.3 entirely" — **voids P2.5, it does not pass it**, because the
done-set would then close "on triage-log lines, not understanding". The default
path de-contingents P2.3 into **P2.3b**: extract over the red class ∪ a
pre-registered frozen sample of the green class, *so the comprehension step
fires even at 0 reds*. The claim doc argues P2.3's premise is void
(`EXTRACTION_FLOOR_REMEASURED.md:68`) without engaging A22 at all.

So the honest consequence is: **the finding converts P2.3 from a floor-closing
job sized in GPU-days into the A22 condition, which fires P2.3b sized to a
frozen sample.** "~2 gaps, therefore no extraction" is the one reading the plan
explicitly forbids — A14 flags P2.3 as "the plan's sole comprehension step".

## 2. The recovery number is a ceiling, not a measurement

14 of the 17 "ROUTING" recoveries are `qa+anchor`
(`census_v1_floor_triage.jsonl`; 29 of 35 in v2) — the triage hand-fed
`item["subject"]` from the bank (`tools/census_v2_triage.py:59`). That is
**oracle information the writer path does not have**. The real auto path
(`scriptengine/api/main.py:207-214`) must *infer* the subject via
`routed.signals`. Also: `build_context` rejects `mode="auto"`
(`scriptengine/api/context.py:60,148`) — the claim doc's fix-1 as written
raises `ValueError`. Auto lives only in the API layer. So realizable recovery
is ≤17 and **currently unmeasured**.

Related: the P1.4 close condition "5.4 re-adjudication, 21/21 identical, 0
closed" (`reports/csm/GATE.md`) re-ran the *same* deterministic single-door
instrument. It is not independent corroboration of the floor.

## 3. Asymmetry of the two errors

- **Spending GPU-days on an artifact** costs compute *and* corrupts the
  pre-registered extraction-pass test: closing rows that a routing fix would
  also have closed makes the pre/post delta unattributable — the precise
  failure **A18** exists to prevent.
- **De-scoping wrongly** costs nothing irreversible *provided the campaign does
  not ship P2.5 on it*. Extraction is re-runnable; the panel and frozen sets are
  hashed (A26). The one-way door is the **done-declaration**, not the compute.

Therefore: "do not start P2.3 now" is safe; "P2.3 is void" is not.

## 4. P2.1 is a different instrument — and gains value

`span_recall._ask` forces `body["mode"] = door` (`scriptengine/eval/span_recall.py:207-216`)
and P2.1 runs **three** doors with pre-declared per-door floors (A17). It
measures verbatim line containment, not dimension expect-terms. The census
defect does not transfer; the 3-door design is the blind spot the census had.
Two riders: (a) span-recall also *forces* a door, so **no instrument in the
campaign measures the auto door `/context` actually serves** — that is the real
gap this finding exposes; (b) P2.1's go/no-go is a cost question, unaffected
here: break-even is **3.35 s/probe** (17,181 × 3 vs the 2-GPU-day threshold).

## 5. Recommended sequence

1. **Fix the instrument properly**: census + triage via `/context` `mode="auto"`,
   **no oracle subject**. Write to a *new* results file (the 5.4 run already
   overwrote `census_dimensions_csm_results.jsonl` in place).
2. **Re-run the 21 + 42 reds through it** (~63 probes, single attempt, minutes
   on the CUDA `:8000`) — the cheapest decisive measurement, ~10³× cheaper than
   one extraction GPU-day. **Batch it into P2.1 step-0's existing `:8000`
   window** (`plan/drift_log.md` D26 pre-flight); it needs no Qwen.
3. **Run step-0's sanity-100 in that same window** — different question, do not
   delay it on this finding.
4. **Re-derive the floor** from (2); scope **R-8** (subject inference /
   narrative routing on natural phrasings) against whatever survives.
5. **Take the reshaped P2.3/P2.3b scope to the Phase-2 council** with corrected
   numbers (CSM trigger: every big decision), and freeze P2.3b's green-class
   sample *before* R-8 lands.

## What I would NOT do

- **Not fire A22's null branch** on oracle-anchored triage; it voids P2.5.
- **Not skip the comprehension layer** even at 2 reds — that is P2.3b's purpose.
- **Not re-open Phase 1 or retract `PHASE_A_COMPLETE`.** File an erratum to
  `CLOSE_COUNCIL_RULINGS_Q1_Q4.md` recording that the halt meter's 33-fixable
  denominator excluded rows that may be fixable, and book R-8 as a Phase-2
  engine item under the four standing gates. Re-litigating the close buys
  nothing the erratum does not.
- **Not gate Q3 on a raw widened-census score** — 42 reds / 0 content gaps shows
  the score is door-dependent. Q3's "widened census green" consumes the
  *corrected* instrument's output.
- **Not let the directing session decide the de-scope alone.** It authored the
  finding; the scope call is a phase-boundary decision.
