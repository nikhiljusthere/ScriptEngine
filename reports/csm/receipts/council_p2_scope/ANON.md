# Anonymized advisor responses — council #38 (peer-review input)

Five advisors independently answered the framed question (see framed_question.md in this directory). Responses are anonymized A–E.

**Response A:**

**Q1** Yes — the D6 zero-flip is mechanical (the events table feeds only the narrative door; qa rows lose at ranking against chunks that already hold the expect sentences), so no row is extraction-content. The state-over-time interval facts are already on the in-scope narrative axis.

**Q2** Sound; add the post-shape span-recall + coverage re-proof line (the P2-execute step demands it; it's missing from the budget table, ~10 min) and re-run the `--dry-run` at window start to re-verify 230/406 at current HEAD.

**Q3** Faithful — class-scoped, zero engine change, counters measured (149/252 + 486), not assumed. Other counter-flips reopen class scope without voiding the trigger bar: exactly #37's line.

**Q4** Run (d) right after (b): it's in-process, 30–45 min, independent of extraction. The width decision must not ride on extraction; a RED at hour 3 lets you shrink the window.

**Q5** Separate gated window — it's an engine commit; #37 already ruled it standalone. Bundling it into a measurement window breaks one-mechanism-at-a-time attribution.

**Legs** (launch → poll → proof → wedge):
- **(a)** `setsid nohup bash tools/csm/d7_gates.sh </dev/null >/dev/null 2>&1 &` → `tail /tmp/d7_gates.log; cat /tmp/d7_gates/state` → `/tmp/d7_gates/STATE.{pytest,eval,span,canon,banks}` + pre-bank snapshot. Wedge: the restore trap runs the owner's UNCOMMITTED argv (`/mnt/PROJECTS/ninfer-transfer` model path, root-owned mount) — if that mount is down at window start, Qwen never comes back.
- **(b)** `setsid nohup bash tools/csm/p21_sweep.sh >/dev/null 2>&1 < /dev/null &` → `reports/master-work/p21_sweep_<stamp>_run.log` → `p21_sweep_<stamp>_RECEIPT.md`. Wedge: stale stamp @`4b60043` — wipe stamps at current HEAD first or pre-checks 10–12 halt.
- **(c)** first `scriptengine/.venv/bin/python -m scriptengine.cli events-extract --series csm --scope corpus --pages reports/csm/p2_keep_pages.txt --dry-run` (re-verify 230/406), then the same command detached `--workers 2` → per-page lines in the log → a fresh session must WRITE `reports/csm/receipts/p2_extract/RECEIPT_<stamp>.md` — no pre-baked runner exists; that's the first Monday-morning build. Wedge: OOM → resume `--workers 1`.
- **(d)** first: write `tools/csm/widthclass_run.py` (driver over `p23_grader.grade_item(top_k=30)`: 4 rows + 486 sweep + blind/OOS), then detach in-process → run log → `reports/csm/receipts/d6_probe/widthclass_run.md`. Wedge: GPU free < 6 GB after Qwen down (halt 11) / missing venv (halt 12).
- **(e)** `setsid nohup bash tools/csm/p23_handoff.sh >/dev/null 2>&1 < /dev/null &` → newest `reports/master-work/p23_grader_*_RECEIPT.md` (the proof) → halt 10: Qwen still up (mode file not off).

**Window** One window: (a)+(b)+(d)+(e) ≈ 4.75–5.75 h is minimum-viable; (c) is the stretch leg (total 7–9 h, still < 2 GPU-days). If any gate leg is RED or the start is late, cut (c) to a second window — nothing in (d)/(e) depends on it.

---

**Response B:**

**Q1.** "0 of 486 flipped" proves only that the D6 extraction shape flipped nothing at the 417-era HEAD; the load-bearing evidence is the wiring fact (the qa door does not consume the events table), which is sound. But the registered retest "post-extraction re-grade" for the 11 "extraction-gated" rows is a no-op by construction — re-label them retrieval-gated — and the chunk-substring check is stated class-level ("every pool phrase"); the state/arc rows' gold phrases owe a per-row disk check, not a D6-family inference.

**Q2.** Scope is sound; the budget is not. The 7–9 h omits the post-extraction full-gate cycle + span/coverage re-proof that plan step P2-execute requires ("full gates + guards" after the shape change) — the honest window is 8.5–11 h. A 1.2–2× rate drift, or the workers-1 OOM resume, blows the 9 h bound with no pre-registered path (the abort trigger fires only >2×); and any mid-window commit mixed-stamps the A18 sweep ledger → 2.7 h restart. Pre-register a no-commit rule.

**Q3.** Faithful to the trigger line, but the full-486 counter sweep at top_k=30 is missing a guard: the bar binds {149, 252} only, beyond-class counter-flips are "recorded and reported" with no bound, and blind/OOS are measured at product config — so the top_k=30 config itself is guarded only by {149, 252} + an unbounded log. A sweep showing 40 counter-flips still PASSes. Pre-register a bound: beyond-class counter-flips = 0, else only a class-scoped top_k hunk may ship.

**Q4.** Order is right for attribution (sweep before extraction; one post-extraction re-grade avoids a double re-grade). But the real defect is the reverse: extraction is off the 486 critical path, so pre-register it as a non-blocking stretch leg — minimum viable window = gates + sweep + instrument + re-grade (≈5 h), extraction on owner call, not only on the rate trigger.

**Q5.** Keep it separate. A mid-window TIERED commit moves HEAD, mixed-stamps the sweep ledger (2.7 h restart), confounds the A17 flag-OFF floors with flag-ON numbers, and breaks D7b's one-mechanism-at-a-time counter-flip attribution. Its own gated window, after this one.

---

**Response C:**

**What we're actually solving.** Not "486 green" — the CLOSE step lets rows close via *explicit void-set*, so "100%" is *ledger* closure (every row green or explicitly voided), with OOS / green30 / blind / JJK as *floors*. This window *does not* buy the close — it buys the *evidence base* + *content* leg; the close still needs TIERED-flip + width-ship + R-9 roster. Window 1 of ~3.

**Q1.** Extraction isn't the qa-door *ranking* lever — but it *is* the only lever for state-02/03/09 interval facts *if* they're absent from the kept chunks. Check (c) says present *today*; pre-register a content-absence check — the locked scope ("keep-list ∩ corpus queue") may exclude those sections.

**Q2.** Sound with 2 holes: the 4 gates run *before* the store changes (leg c), but the JJK "no code/corpus/store" guard is *exactly* what a store change threatens — add post-extraction JJK-diff + span re-proof to leg (e); the pre-extraction sweep is stale, label it "mechanism verification."

**Q3.** Faithful: top_k=30 *through the qa endpoint* is a measurement, not an ABILWIDTH knob, so it respects D59. Bar is right: the full-486 counter-sweep re-opens class-scope on *any* other counter-flip (re-diagnosis, not ex-post retune) rather than voiding the bar.

**Q4.** Move the instrument *before* extraction: zero event-layer dependency (events only feed the narrative door), so it *shouldn't* ride on extraction's OOM risk; as ordered, a leg-(c) abort loses the width-class evidence for the window.

**Q5.** Keep TIERED separate — a 1-character *engine* change moving JJK bundles (tier-2 append), needing its *own* flag-ON 4-gate window + owner decision; folding it into a flag-OFF window breaks "one mechanism at a time." Pre-register as the *next* window.

**Not 4 levers.** 2 gaps + 1 disposition: width + door-routing + "retest" (a *disposition*, not a lever). The width gap gets 2 *redundant* mechanisms (TIERED append *and* top_k=30) — sequence narrowest first, or over-widen and leave counter-flip guards as the only backstop.

---

**Response D:**

Q1. The D6 zero-flip result (333 events, 0 flips) justifies "extraction is not the qa-door lever," but the claim is door-specific: the docs themselves concede state-over-time interval facts (state-02/03/09) are enriched by extraction for the narrative door. Keep those rows in scope — but the narrative-axis re-grade has no named bar, so that lever is unmeasured.

Q2. Two load-bearing gaps. The on-disk census file is the Leg B census (469, pool-140/358 green / pool-149/252 red) — the same count as product (469) but the opposite red set; a fresh owner reading it at the window will mistake Leg B for product state. And the window's restore path depends on an uncommitted "do not commit it" edit in `tools/csm/d7_gates.sh` (the /mnt/PROJECTS model path): a 7–9 h Qwen-down window whose recovery hinges on an unversioned file.

Q3. Faithful to #37, but the line between "new pre-registered instrument" and the forbidden "ex-post re-tune" (D59) is undefined operationally — a stranger cannot tell when measuring top_k=30 becomes a re-tune. The bar is also weaker than the standing guards it runs under: it binds only on the 4-row class and lets an outside counter-flip "re-open class scope" without voiding PASS, while every regrade's guard is 0 green→red counter-flips.

Q4. The instrument is stated to be measurement-only and to touch no engine state, so it has no hard dependency on extraction. But it grades against whatever index exists, and extraction rebuilds it — so the width verdict silently rides on extraction's index state. If extraction OOMs/shrinks (pre-registered), the instrument runs against a partial index and the width verdict is confounded. Run it before extraction, or pre-register which index state it grades against.

Q5. Keep TIERED separate: it is a one-char engine commit + 4 gates at flag-ON + owner word — a different gate profile and a different decision than this flag-OFF measurement window. Bundling couples a binary engine-ship to a 7–9 h window and muddies the abort path.

---

**Response E:**

Q1. Yes — the re-proof redirects extraction to its real, bigger value: the 333→~900 event-row layer is the writer-path, narrative-door, and Q4-coverage-compounding engine; "not the 16-row flip lever" must not be misread as "not worth doing" — it's the only leg that makes CSM a generation surface. The keep-list + pre-filter (JJK 837/838, zero forced inclusions) is a reusable 7-wiki method; the P6 §7 seed is due 2026-09-25.

Q2. Sound, but it only pre-registers the downside. Add a GROW branch: if the first-10-page rate is ≤ half of D6's, the slack funds the full 511-page keep-list in the same window — a fast extractor buys the whole Q4 compounding for the cost of the delta.

Q3. Faithful; the full-486 counter-sweep measures instead of assumes, correctly calibrated. The undervalued read: a PASS validates the width lever for the whole numeric-collision shape (the D7a chap-01 residual) and pre-registers the class-scoped predicate the 8 campaign-residual rows ride on — one instrument clears three lever families, and sets up leg three.

Q4. Keep the order: the instrument must ride the post-extraction index, else the counter-sweep and re-grade attribute width to a stale index — Q2's own failure list. One window then yields two simultaneously ratifiable legs.

Q5. Keep it separate (council #37's bar; the re-grade must stay flag-OFF product state for the Q3 re-gate) — but the owner's decision set then collapses to one "TIERED flip" word, and if the width instrument PASSes, option 3 is cleared too. Flip: 469→473. Flip + width ship: 486/486.

Undervalued: all 69 pre-extraction reds green at 60000/50 proves the content layer is DONE — only product-config width stands between the campaign and 486/486. And measure the JEV pruner's prefix-cache hit rate against the R-5 baseline (6.1%): the pre-registration structure is cache-friendly, and as council cadence scales, governance cost falls.
