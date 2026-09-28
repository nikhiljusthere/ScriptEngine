# Council: extraction prompt + method for Qwen3.8-27B-uncensored (SGLang MTP, thinking off), 2026-09-29

Run sequentially (5 advisors, 5 anonymized peer reviews, chairman), per the owner's llm-council rule. Question, responses, reviews and architect fact-checks below; the chairman's verdict at the end.

# QUESTION
# Council question (2026-09-29)

**Decision:** what is the most optimized prompt + serving method for ScriptEngine's event extraction on **Qwen3.8-27B-Uncensored NVFP4, served by SGLang with native MTP (NEXTN) and thinking OFF**, on a single RTX 5090 (32 GB), to maximize extraction **precision AND recall AND throughput** over the Marvel + MCU corpus (~360k passages: 51,723 Marvel sections + 225,045 Marvel fact values (median 281 chars, 87% under 1,500 chars) + ~83k MCU sections)? Wanted: a ranked, concrete change list (prompt text changes, request/serving flags, packing policy), the measurement that proves each, and which to adopt first.

**Why it matters:** this is the model/config for the full extraction run (~3 days at the current 0.71 s/passage). Its rows (subject, verb, object, verbatim quote) become the event graph behind a "franchise brain" that must answer cross-reality "who would win" questions from cited facts. A bad prompt baked into 360k passages costs days to redo; a missed speed-up costs days of GPU.

**Measured (same 160 seeded Marvel pages / 285 passages, 2026-09-29):**
- Chosen config: 203 s wall, 0.71 s/passage, 6 concurrent slots (SGLang caps at 6 on 32 GB with MTP: Mamba state + draft; KV pool 16k tokens; mem-fraction 0.95; mamba cache 24), MTP accept length 3.87 of 4, ~135 output tokens/call, 481 rows, extraction precision 27/30 (90%) on a 30-row human-judged sample, 2 pages failed with an empty reply.
- Same model without MTP: 358 s, 8 slots, 26/30. ninfer Qwen3.8-27B thinking-low: 1,150 s, 1,400 output tokens/call, 27/30. Qwen3.6-35B-A3B thinking-off: 127 s but 80% and heavy over-generation. K2-Horizon-36B-A4B: 80%, truncations.
- The run time is dominated by the one huge page (Beast: a 129k-char history value = ~35 sequential 4,000-char windows on one slot) at the tail; steady-state full-batch aggregate decode ~920 tok/s.

**Error taxonomy (extraction, across models):** self-object rows ("Avengers departed Avengers", "Tombstone arrived Tombstone"); `arrived` with a person as object; subject not supported by the quote ("Cyclops reformed the X-Men" -> "Beast met Cyclops"); a solicitation teaser or an intention ("intends on beating") read as an event; a powers sentence read as `met`.

**Resolver (separate fix, not the question, but the prompt may help):** the resolver maps model mentions to wiki pages and causes most wrong rows ("Beast" -> Henry McCoy (Clone) (Earth-616); "Hank" -> Blast-Hands (Hank); "Character Index/M" as a participant). Raw mentions are now stored, so resolver fixes re-apply to stored rows in minutes.

**Current prompt** (scriptengine/ingest/events.py, PROMPT_VERSION events-2026-09-05.3; read the file for the exact text): SYSTEM = "You extract stated events from fiction-wiki prose. You answer with JSON only... You never state an event the passage does not state." User template begins "List the events this passage states ... during {page}", then Series/Page/Section, then the passage, then the JSON shape {"events":[{"subject","verb","object","quote"}]}, the closed verb list (EVENTIVE_VERBS: fought, killed, met, saved, betrayed, arrived, departed, awakened, sealed, ...), and rules (an event vs a description; `met` only for a stated meeting; one name per role; no object -> the subject is the object; quote copied verbatim; an empty answer is fine). Temperature 0.0, answer budget 8,192 tokens, one call per passage window (4,000 chars, 300 overlap). Rows whose quote is not verbatim in the passage are dropped by code; participants must resolve to a wiki page or the row is dropped.

**Levers available (engine support exists or is small):**
1. Packing small pages into one call (SCRIPTENGINE_EVENTS_PACK_CHARS; built, off; rows re-anchored by quote).
2. Put all static text (system + rules + verb list + JSON shape) BEFORE the variable page/passage, so SGLang's radix prefix cache reuses it on every call (today the page name is on line 1, which defeats the cache).
3. Constrained JSON decoding (SGLang response_format json_schema / xgrammar), verb as an enum.
4. Few-shot examples targeting the error taxonomy.
5. Per-verb definitions (arrived/departed need a place object; met needs a stated encounter; no self-object except awakened / self-killing).
6. SGLang serving flags: DSpark drafter (1.6 GB, validated only at batch 1) vs NEXTN MTP; mamba cache / mem-fraction vs concurrency; chunked-prefill size.
7. Retry policy for empty replies.
8. A deterministic code-side post-filter (self-objects, arrived/departed with a person object).
9. Splitting a huge page's windows across slots (today one page's windows run serially on one slot; the queue is densest-page-first).

**Constraints:** coverage is never a budget variable (every line is read; no triage model may drop work); one engine, generic mechanisms, per-wiki differences only in overrides.yaml; any prompt change bumps PROMPT_VERSION and must be proven on the same 160-page sample by a row-set diff + a judged precision sample before adoption; GPU-only; JJK/CSM baselines must stay byte-identical.

# ADVISORS
## The Contrarian
The council is being asked to tune a run whose measurements can't tell good from bad and whose schema can't answer the question the brain exists for. Fix those two things before touching any flag.
1. The verb list can't answer "who would win". It has fought, killed, met, saved, betrayed, arrived, departed, awakened, sealed; no defeated/beat/overpowered/lost to/escaped. `fought` records that a fight happened, not how it ended. Baking this schema into 360k passages costs 3 GPU-days and leaves the headline question unanswerable. Settle the verb set first.
2. Some self-object errors are caused by the prompt: "If the passage names no object... the subject is the object" instructs "Avengers departed Avengers". Make the object nullable; a post-filter only hides it.
3. The measurement is noise: 27/30 vs 26/30 is ~±11pp. Recall is never measured. MTP under batching is not bit-deterministic at temperature 0. Run the current config twice for a noise floor, and hand-annotate recall on ~40 passages.
4. The sample doesn't match the corpus: 225k of 360k passages are fact values (median 281 chars); the sample is section-heavy and 0% MCU. "during {page}" may not suit a fact value.
5. Empty replies break the coverage rule: 1.25% of pages = thousands at scale. Retry and report loudly, before any speed work.
6. PROMPT_VERSION is one global string: a bump marks JJK/CSM events stale and any re-extract breaks byte-identical baselines. Scope the version per series or per prompt.
7. Unverified: xgrammar + NEXTN may lower accept length or be unsupported; the 8,192 answer budget with thinking off lets a runaway hold a slot (cap ~1,024); prefix caching mostly helps short fact values, the 4,000-char windows are decode-bound.

## The First Principles Thinker
You're optimizing the wrong layer. The actual goal is a brain that answers "who would win" from cited facts. The closed verb set (fought, killed, met, arrived, departed, awakened, sealed, betrayed, saved) was designed for JJK timeline ordering. It contains no outcome. "fought" doesn't say who won; nothing captures defeated, overpowered, fled-from, survived, or which power produced which feat. Run 360k passages through this schema and you get a beautifully precise timeline of arrivals and meetings, and almost no match-up evidence. That's the 3-day redo you fear, and no prompt wording or SGLang flag fixes it. First principle: before any tuning, take 30 real "who would win" questions and check whether ANY row the schema could emit would support an answer. If not, change the verb set first (a Marvel-scoped extension in overrides.yaml, JJK untouched).
1. You have no recall measurement and precision is unreadable. 27/30 vs 26/30 is noise (95% CI on n=30 ~ ±11 pts). Build a gold set: 100-200 passages with every event hand-annotated. Without it, none of the listed levers can be ranked.
2. Your 3-day estimate is probably wrong. The 285-passage sample is dominated by the Beast tail. Steady state 920 tok/s / 135 tok per call ~ 0.15 s/passage ~ 15 hours for the corpus. Levers 9 (split huge-page windows across slots) and 2 (static prefix first, for the radix cache) are identity-preserving throughput wins and should go first; with median 281-char fact values, each call is mostly static prompt, so lever 2 is the dominant speed win.
3. Most wrong rows are resolver errors, not model errors. Self-objects and arrived-with-person belong in a deterministic post-filter (lever 8), not prompt pleading: it re-applies to stored rows in minutes, needs no PROMPT_VERSION bump, and is cheaper than any prompt change.
Adopt first: the schema question, then the recall gold, then levers 9 + 2 + 8. Prompt wording and few-shot last.

## The Expansionist
The upside nobody's pricing: this run is a one-shot chance to fill several brain layers at once. You're about to read 360k passages; prefill is paid. A few extra output tokens per call are nearly free next to the ~3-day read, and a second full pass costs 3 more days.
1. Static prefix first (lever 2) + packing (lever 1), together, first. 87% of fact values are under 1,500 chars; packing them to ~4k against a cached static prefix cuts calls maybe 3-5x, 3 days to ~1 day, which funds everything below. Proof: same 160 pages, wall time, and the packed row set must be a superset of the unpacked after quote re-anchoring.
2. Constrained JSON with verb as an enum (lever 3), plus optional fields: `reality`, `place` for arrived/departed, `when` (the issue or film), `outcome` (won/lost/escaped). The "who would win" questions need exactly these. ~20 tokens per row; later they cost a second 360k pass. They also help the resolver (Beast + Earth-616 + page context). Proof: judged sample per field; adopt only fields at >=85%.
3. Split one page's windows across slots (lever 9): the Beast tail is pure waste; ~35 serial windows become ~6 rounds.
4. Few-shot from the error taxonomy (lever 4) + the post-filter (lever 8). With the prefix cached the examples are nearly free on every call, and reusable for every future wiki.
5. MTP over DSpark: accept 3.87 is near the 4.0 ceiling; spend effort elsewhere.
Bigger: this is the prototype of a reusable "franchise ingest pass". Freeze the enriched schema once; re-extract JJK/CSM with it later as a separate versioned layer, their baselines untouched.

## The Outsider
1. Your prompt instructs the top error. "No object -> the subject is the object" literally manufactures "Avengers departed Avengers". Make the object nullable and delete that rule, before any few-shot work. A post-filter (lever 8) only launders a self-inflicted instruction.
2. The "3 days" figure looks wrong and may be steering everything. 0.71 s/passage comes from a 285-passage sample whose wall time is dominated by one Beast page on one slot. Your own steady-state number: 920 tok/s / ~135 tok/call ~ 6.8 calls/s ~ 0.15 s/passage, ~15 hours for 360k. Measure throughput on a tail-free or much larger sample before paying for speed-ups. Lever 9 fixes your benchmark more than production.
3. You can't distinguish configs on precision: 27/30 vs 26/30 is one row; ±10% noise swamps every comparison. Judge >=150-200 rows before ranking.
4. Recall is in the goal but has no measurement. "481 rows" isn't recall. Without a hand-annotated gold set, a stricter prompt that drops real events looks like an improvement.
5. You say the resolver causes most wrong rows, so prompt tuning attacks the minority error. Fix the resolver first; it's cheap and re-appliable.
6. 225k fact values (median 281 chars) are ~2/3 of the corpus and likely mostly non-narrative. Packing (lever 1) reads every line and slashes call count: your real throughput lever, not drafter/cache flags.
7. An empty reply with an 8,192 budget and thinking off is abnormal. Find why before adding a retry that hides it.

## The Executor
Your 3-day estimate is measuring the wrong thing. 0.71 s/passage is wall/285, and wall is the Beast tail. 62% of the corpus is fact values with a median of 281 chars, and your sample barely has any. Fix the scheduler and the sample before the prompt.
Monday, in order:
1. Window-level scheduling (#9), 1 hour. events.py builds `units` per page and runs them serially inside one worker. Put (page, window) units on the pool instead of pages; the Beast tail goes onto all 6 slots. No prompt bump. Proof: row-set diff vs the chosen-config run, plus wall time; expect a big cut in the 203 s.
2. Code post-filter + one retry on empty replies (#8, #7), 1 hour, no GPU. Drop self-object rows unless the verb is awakened or a self-kill; drop arrived/departed whose object resolves to a character page. That kills 2 of 5 error classes deterministically and re-applies to stored rows in minutes, like resolver fixes.
3. One prompt bump holding #2 and #5 together: move {page} out of line 1 so the static text precedes any variable text, and add per-verb definitions. One 160-page validation, not two. Verify in the SGLang log that #cached-token rises; with the hybrid Mamba radix cache (extra_buffer_lazy) a prefix hit is not guaranteed: measure it.
4. Packing (#1) for fact values only. A second ~2k fact-value sample, pack off vs pack at 4,000 chars: row-set recall and s/value. Likely the largest calls-per-hour gain: the ~600-token static prompt is paid again on every 281-char value.
Skip for now: DSpark (batch-1 validated; accept is already 3.87/4); json_schema/xgrammar (the errors are semantic, not syntactic, and grammar + NEXTN is an untested interaction); few-shot (adds prefill to all 360k calls; only if step 3 leaves met/intention errors).
Adopt 1+2 today, 3+4 tomorrow, then launch. The 3-day run is fixed; 4 days of tuning before it isn't.

# PEER REVIEWS (letters: A=Executor, B=Contrarian, C=Expansionist, D=Outsider, E=First Principles)
## Review 1
1. Strongest: E. The only one that both challenges the objective and fixes the measurement. The verb set has no outcome verbs (defeated, overpowered, fled), so "who would win" is unanswerable. It gives a cheap test (30 real match-up questions vs. emittable rows), puts the fix in overrides.yaml, demands recall gold, and redoes the 3-day math (~0.15 s/passage, ~15 h). Its gap: it misses what D and B caught, that the "no object -> subject is object" rule itself manufactures the self-object rows.
2. Biggest blind spot: A. Purely operational: never asks whether the schema can answer match-ups, launders the prompt-caused self-objects with a post-filter instead of deleting the rule, measures neither recall nor noise (27/30 vs 26/30 is noise). C is close behind: it adds fields "judged at >=85%" on samples too small to measure that.
3. All five missed: the KV budget (16k tokens across 6 slots ~ 2.7k each; packing to 4k chars, few-shot and extra fields add per-call tokens and can cut concurrency or trigger preemption; nobody checked the fit); the drop funnel (no one measured how many model rows the verbatim-quote gate and the resolver silently discard: invisible recall loss); and packed fact values lose context (a value leans on "he" and the page's subject; packing across pages can misattribute).
[Architect note for the chairman: the engine packs passages of ONE page only (never across pages), so the cross-page misattribution concern does not apply as stated; within a page the subject is shared.]

## Review 2
1. Strongest: B. The only one to catch every structural failure at once: the verb set lacks outcome verbs (the brain can't answer "who would win"); the prompt's "no object -> subject is object" rule manufactures the top error; n=30 is noise and recall is unmeasured; the sample has no MCU and few fact values; empty replies break the coverage rule. Uniquely, it flags that one global PROMPT_VERSION would mark JJK/CSM stale and threaten the byte-identical baselines, and gives a concrete 1,024-token answer cap. E has the schema insight but misses the self-object rule.
2. Biggest blind spot: C. It measures nothing (no recall gold, no noise floor, trusts 27/30), keeps the self-object instruction, calls cached few-shot "nearly free" without A's Mamba prefix-cache caveat, and adds four output fields on a single judged sample. Its packing proof ("superset after re-anchoring") is unachievable, since temperature-0 MTP output is non-deterministic.
3. All five missed: cross-page bleed in packing (a subject from value A attached to a quote from value B; quote re-anchoring fixes location, not attribution), and two silent recall sinks, the verbatim-quote drop and the must-resolve-to-a-wiki-page drop, whose drop rates nobody counts per config, so a "precise" config may just be discarding more.
[Architect note: packing never spans pages (one page per packed call). Drop counts ARE reported per run (dropped.unknown_participant / unquoted in every pilot report, e.g. MTP run: 247 / 0), but not yet read as a recall signal.]

## Review 3
1. Strongest: B. Only response that catches both fatal problems: the verb set has no outcome verbs ("who would win" is unanswerable), and the "subject is the object" rule itself manufactures the self-object rows (fix = nullable object, not a post-filter). It also demands a noise floor (n=30 ~ ±11pp; MTP batching non-determinism), treats empty replies as a coverage violation, and gives concrete fixes (cap the 8,192 budget ~1,024; scope PROMPT_VERSION per series to protect the JJK/CSM byte-identity). D and E are close, but E routes self-objects to a post-filter, masking a prompt-caused bug.
2. Biggest blind spot: A. A 2-day execution plan that launches on a schema that cannot record who won, never asking whether the rows serve the brain's core question. It post-filters self-objects instead of removing the rule that causes them, and has no recall or noise measurement.
3. All five missed: (a) the verbatim `quote` is most of the ~135 output tokens/call; have the model return sentence IDs over a pre-split, numbered passage: decode drops sharply and "quote not verbatim" drops vanish; (b) nobody asked for the drop-rate funnel (non-verbatim quotes, unresolved participants), an unmeasured recall leak; (c) no staged launch: judge the first ~10k passages before committing to 360k.

## Review 4
1. Strongest: B. The only response that catches both decisive problems: the closed verb set has no outcome verbs (defeated/escaped/lost-to), so the rows cannot answer "who would win"; and the self-object error is prompt-induced ("no object -> subject is object"). It also flags that precision is noise, recall unmeasured, the sample lacks MCU and fact values, PROMPT_VERSION is global (a bump endangers the JJK/CSM baselines), and the 8,192 budget should be capped. D and E are close but each misses one decisive point (D the schema, E the self-object cause).
2. Biggest blind spot: C. It adds four new fields (reality/place/when/outcome) plus few-shot without any recall gold or noise floor to validate them, accepts the 3-day figure uncritically, and treats the prompt-caused self-object rows as a few-shot/post-filter problem.
3. All five missed: packing puts several pages in one call; with the page name as the subject anchor for a 281-char fact value, rows risk being credited to the wrong page, and nobody requires a check. The verbatim-quote and resolver drops are silent recall losses nobody asks to count, the cheapest recall signal available. And Marvel reuses names across realities ("Beast" on 616 vs alternates): the prompt could emit the page's own reality for the resolver.
[Architect note: packing is one page per call; the page's reality is already the resolver's `page_real` signal (P1); the drop counts exist per run.]

## Review 5
1. Strongest: E. The only one asking whether the output can do the job at all: the verb set has no outcomes (defeated/fled/overpowered), so a perfectly tuned run still can't answer "who would win". It also redoes the throughput math from the measured numbers (~0.15 s/passage, ~15 h not 3 days), flags that recall is unmeasured and n=30 precision is noise, and sequences sensibly. Weakness: it misses that the prompt's "subject is the object" rule causes the self-objects (D and B caught it).
2. Biggest blind spot: C. It stacks new schema fields and constrained decoding onto MTP (an untested combination), assumes packed rows are a superset without verifying packing preserves recall, and ignores noise, missing recall and the prompt-induced self-objects. It also proposes re-extracting JJK/CSM. A is second: it never questions the schema.
3. All five missed: page attribution under packing (a fact value's subject is usually implied by its page; packing several pages loses "he" and page context, feeding the resolver, the admitted main error source); no staged launch (raw mentions are stored and results are per passage, so run an MCU + fact-value mixed shard first, judge, then continue; every step is re-appliable, not a "3-day redo"); MCU is 0% of the sample and nobody required MCU coverage in the validation set.

# ARCHITECT FACT-CHECKS
Architect fact-checks on claims made in the council (verified against the code/runs):
- Packing (SCRIPTENGINE_EVENTS_PACK_CHARS) packs the passages of ONE page into a call, never several pages; the page name stays in the prompt. The cross-page misattribution concern does not apply; within-page attribution is unchanged.
- Drop counts are already reported per run (dropped.unknown_participant / unquoted / verb / incomplete / dedup in every pilot report; the MTP run: 247 unknown-participant, 0 unquoted), but never read as a recall signal.
- The page's reality is already a resolver input (page_real, P1 reality-aware resolver).
- PROMPT_VERSION is global, but extraction runs per series; a bump only marks a series' pages stale when that series is re-extracted. JJK/CSM are never re-extracted by the Marvel run and the gates do not re-extract, so the byte-identical baselines hold; scoping the version per series is still a sound hygiene change.
- The steady-state estimate: peak ~922 out tok/s at 6 slots / ~135 tok per call ~ 0.15 s/passage decode-only; prefill (~1.4k prompt tokens per call) is extra, so ~0.2 s/passage is a realistic steady-state figure (~20 h for 360k), not 0.71.
- EVENTIVE_VERBS today has no outcome verb (see events.py).

# CHAIRMAN VERDICT
## Where the Council Agrees
- Measurement is too weak to rank levers: 27/30 vs 26/30 is one row (n=30, ~±11 pts); "481 rows" is not recall. Four of five demanded a hand-annotated recall gold and ≥150 judged rows.
- The 3-day figure is wrong: 0.71 s/passage is the Beast tail. Steady state is ~0.2 s/passage with prefill (~20 h for 360k). Levers 9 (window-level scheduling) and 2 (static prefix first) are identity-preserving and should come early.
- The sample doesn't represent the corpus: fact values are 62% (median 281 chars), under-sampled; MCU is 0%.
- Skip DSpark: MTP already accepts 3.87/4.

## Where the Council Clashes
- Schema first vs throughput first. Contrarian + First Principles: the verb set {fought, killed, awakened, sealed, betrayed, saved, arrived, departed, met} has no outcome; a perfectly tuned run still can't say who won, and "who would win" is the brain's reason to exist. Executor: ship tuning in two days. The schema side wins: a fast run that can't answer the question is the redo everyone fears.
- Self-objects: post-filter (First Principles, Executor) vs prompt fix (Contrarian, Outsider). The prompt rule "no object -> subject is object" manufactures them. Make the object nullable and delete the rule; keep the post-filter only as a backstop for stored rows.
- Enriched fields + constrained decoding (Expansionist). One pass fills more layers, but `reality` is already the resolver's page_real input, grammar + NEXTN is untested, errors are semantic not syntactic, and the outcome question belongs in the verb set, not free-form fields.

## Blind Spots the Council Caught
- The drop funnel as a recall signal: drop counts exist per run (MTP: 247 unknown-participant, 0 unquoted) but nobody reads them as lost recall.
- KV fit: 16k tokens / 6 slots ~ 2.7k each; packing, few-shot and extra fields all raise per-call tokens and can trigger preemption.
- Sentence-ID output instead of verbatim quotes: quotes are most of the ~135 output tokens; pointing to numbered sentences cuts decode and kills non-verbatim drops.
- Staged launch: judge a mixed ~10k-passage first shard (with MCU and fact values) before committing; rows and raw mentions are per passage, so mid-run correction is not a restart.
- Settled by fact-check: packing never spans pages; a global PROMPT_VERSION doesn't endanger JJK/CSM because the Marvel run never re-extracts them (scoping it per series is still sound); an empty reply with an 8,192 budget and thinking off is abnormal, so diagnose it, don't just retry.

## The Recommendation
Adopt in this order:
1. Schema test + Marvel verb extension via an overrides-driven verb list (e.g. defeated, overpowered, escaped, lost-to), JJK untouched. Proof: 30 real match-up questions scored for whether any emittable row supports them, before and after.
2. Measurement set: ~120 passages with every event hand-annotated (half fact values, 20% MCU); run the current config twice for a noise floor; judge ≥150 rows per config; read the drop funnel alongside. Proof: same-config runs differ less than any claimed config gap.
3. Window-level scheduling (lever 9), no prompt change. Proof: wall time, and a row-set diff vs the chosen-config run within MTP batch noise.
4. Empty-reply diagnosis + one logged retry + answer cap ~1,024. Proof: 0 empty pages, 0 truncations on the 160-page sample.
5. One prompt bump, PROMPT_VERSION scoped per series: static text first, page name after; nullable object and the "subject is object" rule deleted; per-verb definitions (arrived/departed need a place; met needs a stated encounter; not intentions or teasers); the outcome verbs; fact-value-appropriate wording (not just "during {page}"). Proof: SGLang cached-token rate up, self-objects ~0, judged precision ≥ baseline, gold recall ≥ baseline.
6. Deterministic post-filter (lever 8) on stored rows as a backstop. Proof: a judged sample of removed rows is ≥90% truly wrong.
7. Packing within a page for fact values only. Proof: calls/hour, gold recall no lower than unpacked, no KV preemption in the SGLang log.
8. Staged launch: a 10k mixed shard, judged, then the full run.
Deferred: constrained JSON (test its effect on MTP accept length first), few-shot (only if step 5 leaves met/intention errors), sentence-ID output (a later bump, measured by output tokens and recall), DSpark.

## The One Thing to Do First
Write the 30 real Marvel "who would win" questions and check each against the rows the current verb set could emit. That result decides the verb set, and the verb set decides the prompt and the whole 360k-passage run.

---
Architect status at close: step 3 (window-level scheduling) landed as `e6af2523` (SCRIPTENGINE_EVENTS_WINDOW_WORKERS, default 1; identity test in tests/test_events_window.py).

## Architect execution record (2026-09-29, after the verdict)

Same 160-page Marvel sample, uncensored 27B on SGLang with MTP, window workers 4, judged by the architect (seed 11):

| step | change | wall | rows | outcome rows (defeated/captured/escaped) | failed | precision |
|---|---|---:|---:|---|---:|---:|
| baseline | prompt .3 (9 verbs) | 203 s | 481 | 0 | 2 | 27/30 (90%) on an easier met/fought mix |
| 1 | outcome verbs per wiki (`de1633a7`), schema test 0/30 (`e103aba9`) | | | | | |
| 3 | window-level scheduling (`e6af2523`) | | | | | |
| 5 | prompt .4: static prefix (cache hit 576 tokens/call), nullable object, verb definitions | 152 s | 924 | 157/113/26 | 0 | 22/30 (73%) |
| 5b | .5 tightened outcome definitions | 152 s | 851 | 122/74/32 | 0 | 22/30 (73%) |
| 5c | .6 direction examples (few-shot) | 141 s | 756 | 129/84/30 | 1 | 44/60 (73%) |
| 5d | .7 quote-first field order (`61573958`) | 155 s | 864 | 147/99/31 | 0 | 46/60 (77%) |
| - | .7 with thinking ON | killed | | | | KV-starved at the MTP profile's 16k-token pool: 1 running, 28 queued, 140 tok/s |
| - | yes/no verifier, quote only | 0.023 s/row | | | | kept 21/46 true rows, 0/14 wrong |
| - | verifier + passage context | 0.051 s/row | | | | kept 21/46 true, 1/14 wrong: 95% precision on the kept tier, 46% recall |

**Decision (best measured method):** extraction prompt .7, thinking off, + the verifier stored as a per-row confidence flag, not a filter. A filter would discard ~54% of true rows (coverage is never a budget variable); a flag keeps every row with its quote and raw mention, and gives the brain a ~95%-precision tier to cite as fact and a labeled lower-confidence tier. Resolver fixes 2+3 landed (`f088539b`); re-resolving stored rows from raw mentions is a follow-up (the mentions are stored).

Next: the staged launch (council step 8): a seeded mixed shard of MCU + Marvel pages, judged, then the full run.
