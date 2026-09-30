# COUNCIL WINDOWING 100-DEFINITION — transcript (2026-09-30)

Convened per owner request: design the window builder FROM SCRATCH for JJK event
extraction so it satisfies the 100% definition (JJK_100_PLAN.md §0 / RUNBOOK_100 §0:
every line understood, recallable, traceable). Method: 5 independent advisors
(contrarian, first-principles, expansionist, outsider, executor), one subagent at a
time, identical brief, no cross-visibility; then 5 independent peer reviewers
(one subagent at a time, anonymized A-E); then a chairman synthesis.
All load-bearing code claims in the verdict below were re-verified against the
repo (verification notes inline in the chairman section).

---

# BRIEF (shared by all advisors)

# COUNCIL BRIEF — how to build windows from scratch for JJK event extraction

Project: ScriptEngine (/home/goblin/ScriptEngine). A wiki-based fact store (JJK =
Jujutsu Kaisen wiki, facts.db) feeds an event-extraction pipeline. "Windows" are
passage inputs: a 27B/35B LLM reads one window, extracts event rows
{quote, subject, verb, object} (12 closed verb set), quotes must be VERBATIM in
the passage. Rows pass mechanical gates (G1 quote verbatim-in-section; G2 verb
legality; G3 self-object; G4 movement object; G5 quote length; G7 prompt
version), then verification; verified windows become LoRA training examples for a
Granite-4.2-3B student that will later run over 300k+ wiki pages.

DEFINITION OF DONE (franchise_kit/RUNBOOK_100.md §0): "every line of the corpus
understood, recallable and traceable." Gates: D6 (understood: every event's
participants resolved, placed on timeline) and D-T (traceable: every fact
resolves to its source section).

## Current window construction (code facts)

1. Section model: `sections` table (title, level, ordinal, text). A section is a
   wiki `==heading==` block (split_sections, ingest/wikitext.py:1258). Sub-entries
   inside a section (`'''term'''` or `;term` definition markers, bare bold
   subhead lines) are split into items ONLY for sections declared in the wiki's
   `item_sections` (ability sections). In any other section the markers are
   flattened into one text blob.
2. `_windows(text, size=4000, overlap=300)` (ingest/abilities.py:472): fixed
   character slices. A 5,200-char section yields window1 = chars 0:4000,
   window2 = chars 3700:5200. Cuts are at arbitrary character offsets — a
   sentence straddling a boundary appears truncated in BOTH windows.
3. Packed reads (ingest/events.py:2401-2424): if a page's total passage chars fit
   `_pack_chars()` (env, off by default), ALL the page's sections are joined
   into ONE window with `[Title]` labels.
4. The index side already has a sentence splitter: `split_sentences`
   (index/chunker.py:107) + `sentence_content_hash` (chunker.py:137, sha256 per
   sentence, stable while section text unchanged). The index chunks per-sentence;
   the extractor windows per-4000-chars. The two sides see different boundaries.
5. Teacher trace (P0b): SCRIPTENGINE_EVENTS_TRACE records the exact window each
   LLM call read + its raw answer (incl. {"events": []}). Only the trace holds
   exact inputs and negatives; the store holds neither.

## The training pools (what we are verifying right now)

- 3 opencode pools × 500 windows = 1,500 (mimo/nemotron/spacebunny,
  series/jjk/training/opencode/mimoP1_windows.jsonl etc.; keys:
  {n, id, page, section, passage}; passage ≤ 4000 chars, one section per window).
- Plus a 1,000-window Qwen pool, plus v1 corpus; UNION = 4,375 distinct windows
  + 2,265 "empty" windows needing a re-read pass ("7,000" campaign; barely
  started — 3/500 of mimoP1 done).
- 333/600 of an older gold adjudication exist under the OLD windowing; they must
  be re-verified under stricter rules anyway.

## Measured defects in the current 500-window MIMO pool (measured 2026-09-30)

- ~35/500 (7%) CATEGORY A: passage starts mid-sentence ("hnique to visit…",
  "his strike.", "t of all of them…") — fixed-char slicing cut a sentence at
  the window boundary; the sentence is incomplete in both neighboring windows.
- ~55/500 (11%) CATEGORY B: several sub-topics in one window. Example n=0:
  Tsurugi Okkotsu / "Cursed Techniques" (1,902 chars) holds FOUR unrelated
  sub-entries (Simple Domain, Battō Sword Drawing, Maculation, Rika lore)
  because the wiki's sub-entries were flattened into one section. Three of the
  four sub-topics contain zero events; they dilute the one that might.
- ~389/500 (78%): clean, single-topic, work fine.
- Separate operational defect: the harness truncates tool output >~2,500 bytes,
  so verifiers reading long passages mid-analysis saw partial text (19 rows
  needed cleanup). Mitigation exists (write passage to temp file, read in
  ≤500-char chunks).
- Separate defect: tools/train/wiki_card.py always reports END-OF-SERIES status
  (e.g. "Deceased" for a character alive in the chapter being read) —
  contaminated reasoning context for the flagger, flagged not fatal.

## Council verdict already on record (2026-09-30, prior session)

The prior council ruled the current windowing STRUCTURALLY INCOMPATIBLE with
D-T/D6: when four topics are mashed in one window you cannot prove which
sentence supported which extracted event; training-signal density collapses;
retrieval serves contaminated windows on any partial hit. Owner flagged n=0 as
over-stuffed.

## Constraints the new builder must respect

- C1: NO sentence may be cut. Every window's text must be a union of whole
  sentences; every corpus sentence must be covered by ≥1 window (intentional
  overlap only, whole sentences only).
- C2: one sub-topic per window where structurally possible (wiki sub-entries:
  `'''term'''`/`;term` markers, blank-line-delimited label blocks). If one
  sub-topic exceeds the size cap, split it at sentence boundaries with a
  whole-sentence overlap — never mid-sentence.
- C3: traceability — each window gets a stable ID + provenance: (page, section,
  sub-entry, sentence-range). A stored event row must be attributable to the
  exact sentences that support it (D-T).
- C4: size — windows sized for a 3B student and a 27B/35B verifier. The 4,000
  char cap is a runbook convention (docs/EXTRACTION_RUNBOOK.md:119), tunable,
  but the owner's "not over-stuffed" flag argues for smaller, single-topic
  windows (median current window ≈ 398 chars; n=0 at 1,902 chars/4 topics was
  called over-stuffed).
- C5: compatibility — G1 requires quotes verbatim in the SECTION, so window text
  must remain a provable span of section text (or the gate must move to
  window-level spans — a deliberate change, with the four standing gates
  (pytest, eval jjk, span-recall, canon) green before AND after; JJK is the
  baseline-exact reference, regressions block other campaigns).
- C6: the empty-window share (~43% natural) and rare-verb ×3 upsampling are
  properties the training build relies on; zero-event windows are RESULTS (D6
  J6.8), not failures.
- C7: the campaign is mid-flight on OLD window IDs (id field; done-logs keyed by
  n+id; 333 old gold). A rebuild changes the ID space — say what happens to the
  in-flight and finished artifacts.
- C8: `split_sentences`/`sentence_content_hash` already exist and are the
  index's identity — reusing them keeps extractor and index on the same
  sentence grid (a prior council finding: they currently disagree).

## THE QUESTION

Design the window builder FROM SCRATCH: the concrete algorithm and data model
(window record fields, splitting rules, overlap rules, ID scheme, size target)
that satisfies C1–C8. Also decide: what happens to (a) the 3×500 opencode pools
mid-campaign, (b) the 333 old gold, (c) the two separate defects (truncation
protocol, wiki_card end-state)? Recommend, don't survey.
---

# ADVISOR: contrarian

The fatal flaw is in the verdict the constraints implement. "Structurally incompatible" was concluded from n=0 — one 1,902-char window, four topics — but the census disagrees: 78% of windows are clean whole-section reads; Category A (7%) is `_windows` slicing sections over 4,000 chars; Category B (11%) is item-marker flattening in sections the wiki's `item_sections` declaration omits — JJK declares only Abilities and Powers / Powers & Abilities / Equipment, so "Cursed Techniques" was never item-split, while the index side already itemizes per line for every 3+-item list section. A from-scratch builder is a sledgehammer: a declaration fix plus a sentence-aligned cut covers the whole defect census.

The real flaw is C2: "one sub-topic per window" is not decidable at scale — prose sections have no structural sub-topic marker. It either degenerates to sentence-aligned spans (unenforceable) or forces topic segmentation, which breaks C1 (dropped sentences) or C5 (non-provable spans). D-T does not need topic purity: it needs quote + section, which today's section-level G1 already proves.

C3 is underspecified: a window ID records the window's range, not the row's. Row provenance needs quote→sentence-span mapping, and G1 must move to window-level, or a quote verbatim in the section but absent from the window read gets attributed to sentences that don't cover it — D-T breaks silently. That move re-baselines span-recall and every campaign that references JJK exactly; the four-gates-green was not priced.

C7 is inverted: the campaign is 3/500 done; restarting costs three LLM calls. What C7 needs is a generation field ("stable ID" across a rebuild is a contradiction) and a recompute owner — "4,375 distinct / 7,000 campaign" are gen-1 ID-space numbers that become meaningless after the rebuild. C4's size target is a zero-data guess that silently moves C6: the empty-window share is an output of size, not a corpus property.

Defects: the 2,500-byte truncation caps usable window size; wiki_card's end-state is a chapter-scoping bug in wiki_card.py, not a windowing problem.
---

# ADVISOR: firstprinciples

Strip the question: a window is not the artifact. The artifact is a **sentence grid**; a window is a *view* over it. All four consumers (27B/35B extraction, 3B training, verification, retrieval) want one irreducible thing: a single-sub-topic, sentence-complete span with stable provenance. The invariants: (1) coverage — every corpus sentence in ≥1 window (D-T); (2) attribution — every event ties to specific sentences; (3) verifiability — the span reconstructs from provenance + stable hashes, quotes verbatim inside. Size, cap, overlap, ID string: contingent knobs, not invariants — the brief over-weights them.

The grid already exists on the index side: `split_sentences` + `sentence_content_hash` (sha256, index/chunker.py:107/137). The extractor's `_windows` (abilities.py:472) slices raw characters — the whole Category-A defect, and why extractor and index disagree (C8). Make the grid the source of truth: split each section into sub-topics first (C2: `'''term'''`/`;term`/blank-line markers, generalizing `item_sections`), then cap each sub-topic into ≤N-char windows cut *only* at sentence boundaries (C1), whole-sentence overlap at a cut. Record: {page, section, sub_entry, sent_start, sent_end, [sent_hashes], gen}. **ID = sha(gen|page|section|sub_entry|range)** — derived, stable, remappable by hash; that kills C8 because both sides read one grid.

Decisions: (a) the 3×500 pools + 4,375 union — **supersede, don't salvage**: mid-campaign, barely started (mimoP1 3/500), and the prior council already ruled old windowing structurally incompatible with D-T/D6. Freeze, tag `superseded`, point the campaign at the new grid. (b) 333 gold — **remap by sentence hash, re-adjudicate only the delta**: events whose supporting sentences now sit in one new window keep their verified status; anything that now straddles a boundary gets re-verified. (c) both defects are **orthogonal** — fix the >2,500-byte truncation in the harness and the wiki_card end-state bug on their own tracks; neither gates the builder, and don't shrink the cap to appease a harness bug.
---

# ADVISOR: expansionist

This isn't a window-format change. A sentence grid + hashed provenance is the store's **incremental-maintenance primitive** — the upside C1–C8 don't even name. The index already runs this exact contract: `remap_derived` re-splits a section and re-anchors stored rows by `sentence_content_hash`, dropping stale rows for re-extraction when text no longer says what it said. Put windows on that same grid and every wiki edit becomes diffable at sentence-hash level: changed hash ⇒ re-extract only the affected windows, re-verify only the affected rows. The 300k-page Marvel/MCU scale-out stops being a one-shot campaign and becomes a continuous delta pipeline: the corpus self-heals as the wikis change. That single upgrade outweighs the two defect fixes combined.

Second under-valued upside: **negatives become addressable**. The ~43% empty share (C6) is now a stable, ID-keyed artifact — "verified empty" is cached forever, and the 2,265-window re-read pass is delta-only after the first pass. Rows attributable to exact sentences also buy per-sentence evals (per-verb precision by sentence class) and a `/context` door that can cite sentences instead of serving contaminated windows on partial hits.

So: (a) don't kill the 3×500 pools — harvest their verified rows, re-key done-logs from old ID to new ID by passage-hash match (the pools already carry `{page, section, passage}`; the 16-hex `id` maps onto the new grid by which sentence range it covers), mark old pools superseded but kept; (b) don't LLM-re-verify the 333 gold — hash-anchor each gold quote's sentences onto the new grid and only re-read the unanchored remainder; (c) size windows so the passage fits under the harness's ~2,500B truncation limit and the truncation defect vanishes structurally (temp-file mitigation stays as legacy path); wiki_card end-state is an independent bug — separate track, but stable IDs make the flagger re-run on fresh windows cheap once it's fixed.

Bonus nobody is counting: the builder is series-generic by repo convention (no series names in .py), so Marvel/MCU inherit the same grid, the same per-sentence evals, and the same delta pipeline for free — one window format, N wikis.
---

# ADVISOR: outsider

1. C4 is self-contradictory: it calls the 4,000-char cap "tunable" while citing the owner's flag that 1,902 chars is "over-stuffed" and a median of 398 chars. Three numbers, no stated target. A fresh engineer sets the size from the sub-topic length distribution, not a runbook convention — I'd design ~800–1,000 chars for a 3B student.

2. Numbers don't add up: 7% + 11% + 78% = 96%, not 100%. "4,375 distinct + 2,265 empty" — is 2,265 a subset of 4,375 or on top of it (the thing that makes the "7,000 campaign")? "~43% natural empty share" is asserted with no measurement behind it. The gate list skips G6 (G1–G5, G7) — a silent omission nobody explained.

3. "Stable ID" (C3) is undefined: stable to what — section text changes, builder-version changes, cap changes? I'd hash (page, section, sub-entry, sentence-range, builder-version) and version the builder explicitly. "Stable" cannot survive a cap change, yet C7 asks what happens in that case without defining the invariant.

4. The "two separate defects" aren't separate: a 1,000-char window fits under the 2,500-byte truncation, so shrinking the C4 size target kills the truncation defect. The brief never connects them. And the wiki_card end-state defect is a data-freshness bug in a different tool — folding it into the windowing decision is a category error; track it separately.

5. Mid-campaign pools: the campaign is 3/500 (0.2%) done. Don't migrate. Freeze the pools, restart the campaign on the new grid. 333 old gold: re-verify only where sentence ranges map 1:1 to the new grid; drop the rest — they must be re-verified under stricter rules anyway, so there is nothing to salvage by keeping old IDs.

A customer's first question before trusting this spec: how many windows does the new builder produce, and what is the cost delta over 300k+ pages?
---

# ADVISOR: executor

Monday morning: TDD the pure builder — `scriptengine/ingest/windows.py` + `tests/test_windows.py`. No DB. One function: `build_windows(section_text, sub_items, size=4000)`.

Build on existing seams: `split_sentences`/`sentence_content_hash` (scriptengine/index/chunker.py:107,137) — extractor joins the index's sentence grid: C8 free, no re-index. `_section_items` (chunker.py:152) already itemizes any section's text line-by-line — that IS the item_sections generalization. Don't touch `split_sections` (ingest/wikitext.py:1258) or the `sections` table (stores/schema.sql:35): sub-topics split at window-time. YAGNI: no schema change, no re-ingest, no new overlap heuristics (≤1 whole-sentence carry), defer the wiki_card end-state fix (flagged-not-fatal).

Build order:
- Day 1, ~8h: builder. Section → sentences + per-sentence hashes; sub-topic items close window boundaries (C2); oversized sub-topics pack whole-sentence windows with carry overlap (C1). Window record: {id: sha1(page|section|sub|s_start:s_stop)[:16], sub, s_start, s_stop, hashes, text}. Tests: window text is a verbatim section substring (C5); hash-union covers the section (C1); no window straddles two sub-topics (C2); IDs stable across rebuilds (C3/C7).
- Day 2, ~6h: replace `_windows` (ingest/abilities.py:472; callers events.py:392,2421); packed reads (events.py:2401) become labeled grid windows; move G1 to window-level — quote verbatim in the row's window span (section text + s_start:s_stop) at events.py:606 and tools/events_gates.py. Standing gates before and after; span-recall byte-identical (index untouched).
- Day 3, ~8h: `tools/train/emit_windows.py` → regenerate the 3×500 pools (seeded, stratified to keep the ~43% empty share, C6); `tools/train/rekey_gold.py` → each of the 333 gold rows: quote → sentence range → covering new window via hashes; non-verbatim quotes drop for re-extraction.

Kill the mid-campaign pools — 3/500 is 0.6%; archive `mimoP1_windows.jsonl` + done-logs as `*.old-grid`, restart at n=0. Truncation: mitigation exists (temp file, ≤500-char chunks); smaller windows make it rarer — zero work.

Fastest path: (a) pools = a minutes-long emit run, day 3; (b) gold re-key = one script, 4–8h; (c) gates green days 2–3 (pytest 1,345+2xp+3 env-fails, eval 31/31, span-recall 48,572, canon opm 10/16). Total: ~2.5–3 working days.
---

# PEER REVIEW 1

# Council review — window builder (review_1)

**1. Strongest: D.** The only response that answers the question: concrete record fields, splitting rule (sub-topics close boundaries; ≤1-sentence carry), 16-hex sha1 ID, size target, TDD plan mapping tests to C1–C8, and decisions on (a)(b)(c) with gate baselines — code refs verified. A frames better (grid-as-artifact) and re-keys gold better, but only D yields a buildable spec. Caveats: D's ID lacks a gen field (C's critique) and it keeps the 4,000 cap with no data.

**2. Biggest blind spot: B.** Sells the delta-pipeline upside, gives no builder: no data model, splitting, overlap, ID, size, or gate plan. Self-contradictory — "verified-empties cached forever" dies on B's own wiki-edit hash delta; and fitting under 2,500B doesn't "structurally kill" the truncation (size mitigates; long tool outputs still truncate).

**3. What ALL five missed:** the extraction-time cost. Sub-topic splitting + smaller cap increases windows (and LLM calls) per page; no one prices that at 300k+ pages (E asks, none answers) — the crux of C4. Also: packed reads (events.py:2401) join multiple sections into one window, violating C2 — ignored by all (D: one hand-wave); and the unexplained missing G6 in the gate list went uninvestigated.
---

# PEER REVIEW 2

# Peer review 2 — JJK window-builder council

**1. Strongest: A.** Right and clean: the sentence grid is the artifact, the window a view over it; ID = sha(gen|page|section|sub_entry|range); gold remapped by sentence hash, re-verify only the diff. It is the existing `remap_derived`/`sentence_content_hash` contract (stores/facts.py:403, index/chunker.py:137); all references check out. D's concrete plan is a strong second, but its "ID stable across rebuilds" test is the wrong invariant: a cap change *should* change the ID; the stable thing is the sentence hash.

**2. Biggest blind spot: B.** The council asked for a concrete algorithm + data model; B gives none — no record fields, split/overlap rules, ID scheme, or size target; it's a thesis on incremental maintenance. "Harvest the pools" also underweights the council's prior ruling that the old windowing is structurally incompatible with D-T/D6 (contaminated windows → unprovable attribution).

**3. All five missed:** (a) the P0b teacher trace: the question asks for G1/trace compatibility and no one mentions it; the trace holds the exact window text + raw answer, so trace records need a window ID + generation. (b) scale: per-sub-entry splitting *increases* window count; nobody estimates the 300k-page LLM cost (E asks, no one answers). (c) G6/D6 participant-resolution under smaller single-topic windows.

## Verification notes (claims checked against the repo)
- A/D: `split_sentences`/`sentence_content_hash` at index/chunker.py:107/137 and `_windows` at ingest/abilities.py:472 — confirmed (fixed 4000-char slices, 300 overlap).
- B: `remap_derived` (stores/facts.py:403) really re-splits sections and re-anchors per-sentence rows by content hash, dropping stale rows — B's core claim is accurate.
- C: JJK's `ability_sections` (overrides.yaml:49-52) declares only [Abilities and Powers, Powers & Abilities, Equipment]; "Cursed Techniques" is not declared, so n=0 was flattened — C's census reading is correct.
- E: G6 (both participants resolved to one node, soft) exists in tools/events_gates.py — the brief's gate list really omits it; the 7%+11%+78%=96% arithmetic and the 4,375-vs-7,000 ambiguity are real (plan/JJK_VERIFY_7000_RESUME.md:32 explains 4,375 is the de-duped union).
- Truncation limit (~2,000–2,500 bytes per tool call) confirmed in plan/JJK_VERIFY_7000_FINAL.md:22; wiki_card status is the series-end infobox value (tools/train/verify_row_wiki.py:55,80) — both defect characterizations hold.
---

# PEER REVIEW 3

# Review 3 — window-builder council

**1. Strongest: A.** The only complete design: grid as single source of truth (resolves C8), full record {page, section, sub_entry, s_start, s_end, [hashes], gen}, derived ID with a generation field so C7 re-keying works, crisp (a)/(b)/(c) calls. D (runner-up, best plan, seams verified) omits a generation field in its sha1[:16] ID — the flaw C/E flagged — and mislabels callers (events.py:392 → abilities.py:392; misses relations.py:320, narrative_abilities.py:136/212).

**2. Biggest blind spot: B.** No design at all — no record fields, split rules, or ID scheme. It contradicts the prior-council ruling (harvests "verified" rows from a grid already ruled structurally incompatible with D-T/D6; 7% of pool passages are mid-sentence slices, unanchorable to whole-sentence spans) and sizes windows to the harness's 2.5KB truncation bug — baking a tooling defect into a spec invariant.

**3. All five missed:** (i) Overlap sizing: G5 bounds quotes only from below (≥20 chars, no max). With one-sentence carry (A/D), a multi-sentence quote straddling a cut is verbatim in neither window → boundary events unextractable → systematic recall loss. Size overlap to the quote distribution. (ii) Existing trace files (series/jjk/events_trace_*.jsonl) hold exact inputs + negatives under the old ID space; the C7 re-key orphans them — trace re-anchoring unaddressed.
---

# PEER REVIEW 4

# Council review 4 — JJK window builder

**1. Strongest: A.** Only response that separates invariants (coverage, attribution, verifiability) from contingent knobs (size, ID string). Gives a complete, correct data model with sentence-level attribution ({page, section, sub_entry, sent_start/sent_end, [sent_hashes], gen}; ID=sha(gen|…|range)) and decisive, code-grounded calls: (a) supersede, (b) hash-remap + re-adjudicate the delta, (c) orthogonal. D is most executable (real seams, day plan, gate baselines) but keeps size=4000 against the owner's "over-stuffed" flag, lacks row-level attribution, and muddles the empty-share.

**2. Biggest blind spot: B.** Its "strategic upside" rests on overstating `remap_derived` (stores/facts.py:403) as a per-wiki-edit "self-healing delta pipeline." It is a rebuild-time snapshot remap (after reset + reindex) that re-anchors rows by content_hash, not a per-edit diff. B also folds the truncation defect into window sizing (shrink under 2.5KB), contradicting C4's 4000-char convention and the brief's "separate defects" framing.

**3. What all five missed:** the `n`-ordinal / done-log problem. The campaign key is n+id; the new grid changes the per-page window count, so ordinal `n` shifts. The in-flight done-log cannot be rekeyed by id alone (A/B) or silently dropped (D/E) — the council needs an explicit `n`-stability / re-sequencing policy. Second: nobody answers E's cost question (window-count / token delta over 300k+ pages) before committing.
---

# PEER REVIEW 5

# Council peer review — JJK window-builder design (responses A–E)

## 1. Strongest: **D**
The only response that actually delivers the ask — a concrete, testable, costed design
(pure `build_windows`; window record `{id, sub, s_start, s_stop, hashes, text}`;
C1/C2/C3/C5 test invariants; 3-day plan wired to real files and real gate baselines)
plus all three decisions (a: archive the pools, restart at n=0; b: one re-key script
for the 333 gold; c: wiki_card deferred). It is grounded in the real code. It must
absorb what it lacks: B/E's "cap under the 2,500-byte truncation limit" (D's "zero
work" is false while the 4,000 cap is kept) and A's cross-generation ID clarity.

## 2. Biggest blind spot: **E**
For a "design from scratch, recommend, don't survey" question, E builds nothing:
no algorithm, no data model, no ID scheme, no split/overlap rules, no emit/re-key
plan, and no costed (a)(b)(c). It supplies sharp spec-gap critiques (C4
self-contradiction, 7+11+78=96, the gate list skipping G6, undefined "stable ID")
and one size number (800–1,000) — an audit, not the requested builder.

## 3. What ALL five missed
The size target is never grounded in the 3B student's actual context/token budget
(or the runbook's KV-pool math). A calls size a "knob," B sizes to the 2,500-byte
harness limit, D inherits 4,000, E asserts 800–1,000 — none derive a number from
Granite-4.2-3B. Consequently no one answers E's own open question: how many windows
the builder produces, and the cost delta over 300k+ pages.
---

# CHAIRMAN VERDICT

# COUNCIL VERDICT — JJK window builder from scratch (chairman, 2026-09-30)

All load-bearing code claims were re-verified against the repo before adoption:
`split_sentences`/`sentence_content_hash`/`_section_items` (index/chunker.py:107/137/152),
`_windows` size=4000/overlap=300 (ingest/abilities.py:472; callers abilities.py:392,
relations.py:320, narrative_abilities.py:136/212), packed reads joining sections
(ingest/events.py:2401-2424), `remap_derived` as a rebuild-time snapshot remap
(stores/facts.py:403), G5 lower-bound-only + G6 present (tools/events_gates.py:14-17,95-98),
G1 `quoted_in` (tools/events_gates.py:73), truncation ~2,000-2,500B per tool call
(plan/JJK_VERIFY_7000_FINAL.md:22), 4,375 = de-duped union / 2,265 empty
(plan/JJK_VERIFY_7000_RESUME.md:32), `ability_sections` declaring only
[Abilities and Powers, Powers & Abilities, Equipment] (series/jjk/overrides.yaml:49-52,
so "Cursed Techniques" was never item-split — the n=0 census reading is correct),
done-logs keyed n+id (series/jjk/training/opencode/.mimoP1_done), gold600.jsonl =
333 windows / 1,298 events keyed by old 16-hex id, and the student budget: seq len
4,096, "window ≤4k chars ≈1k tokens + ~1k system prompt + answer"
(plan/JJK_STUDENT_TRAINING.md:166).

## Where the Council Agrees

1. **The sentence grid is the source of truth; the window is a view over it.**
   A (firstprinciples) frames it, D (executor) builds on it, and everyone else
   converges: the extractor stops slicing raw characters and reuses
   `split_sentences` + `sentence_content_hash` (index/chunker.py:107/137). This
   satisfies C8 for free — extractor and index sit on one grid, no re-index —
   and it is the same content-hash re-anchoring contract `remap_derived`
   (stores/facts.py:403) already implements for stored rows.

2. **Sub-topic splitting must generalize `item_sections`.** C (contrarian) shows
   Category B (11%) is pure marker-flattening (JJK declares only Abilities/Powers/
   Equipment, so "Cursed Techniques" was never item-split), and the index side
   *already* itemizes every section line-by-line (`_section_items`,
   chunker.py:152). A, C, and D all independently land on: split each section
   into sub-topics first (marker/heading/blank-line blocks), then cap.

3. **The mid-campaign pools are frozen and restarted, not migrated.** A, D, and E
   all say: freeze, tag `superseded`, restart the campaign on the new grid. The
   campaign is ~8% done (done-logs: MIMO 67, NEMOTRON 25, SPACEBUNNY 25 of 500
   each; the brief's "3/500" is the mimoP1 sub-pilot) — redoing ~117 verifications
   is trivially cheaper than proving a salvage row-by-row safe.

4. **The 333 old gold are re-keyed by sentence hash, not wholesale re-adjudicated.**
   A, B, D, and E all hash-anchor gold quotes onto the new grid and touch only the
   delta (what straddles a new boundary or fails a gate). The mechanism is the
   same `remap_derived` contract.

5. **Both defects are separate tracks, neither gates the builder.** A: orthogonal.
   D: the truncation mitigation already exists (temp file, ≤500-char chunks,
   encoded in the final plan doc). E: folding wiki_card into the windowing
   decision is a category error. Verified: wiki_card's "end-of-series status" is a
   chapter-scoping bug — the card reads `status` from the `facts` table
   (tools/train/verify_row_wiki.py), i.e. the series-end infobox value. Nothing in
   the builder should depend on either defect.

6. **Window IDs are content-derived (page, section, sub-entry, sentence range),
   not allocated ordinals.** A, D, and E agree on hashing content coordinates;
   the stable *remappable core* is the sentence hash, the window ID is a derived
   convenience.

## Where the Council Clashes

1. **Salvage vs. supersede the 3×500 pools (decision a).** B (expansionist):
   harvest verified rows, re-key done-logs by passage-hash match, keep the pools.
   A/D/E: freeze and restart. B's position optimizes against 300k-page scale-out
   cost; the counter is that the prior council already ruled the old windowing
   structurally incompatible with D-T/D6, and 7% of pool passages are mid-sentence
   slices that cannot anchor to whole-sentence spans — so "harvested verified rows"
   are *unproven* rows, and proving them safe costs about as much as re-running the
   ~117 done windows. The clash is real and reasonable; it resolves by the prior
   ruling: supersede. B's genuine upside (addressable verified-empties as a
   delta cache) survives as a later delta-pipeline story, not part of this decision.

2. **ID generation field — what "stable" means.** A: ID = sha(gen|page|section|
   sub_entry|range); a cap change *should* change the ID; stability is the
   sentence-hash contract, scoped per generation. D: sha1(page|section|sub|
   range)[:16], no gen, with a test that "IDs are stable across rebuilds."
   Reviews 2/3/5 all side with A: D's test encodes the wrong invariant — "stable
   ID across a cap change" is a contradiction, and the only thing that survives a
   cap change is the content hash. Reasonable disagreement (D wanted test
   simplicity), but A's semantics are the correct ones: the ID is stable *within
   a generation*, remappable *across* generations by hash.

3. **Size target.** D keeps 4,000 (no data). B sizes to the 2,500B harness limit.
   E asserts 800-1,000 (no derivation). A calls size a "knob." The council splits
   because nobody derived a number from the 3B student budget (review 5) — and
   the derivation shows none of the four picked it for the right reason: the 3B's
   4,096-token training seq len is *not* binding (2,000 chars ≈ 570 tokens at the
   runbook's measured 0.286 tok/char, plus ~1k system + answer ≈ 2.2k « 4,096),
   and the 27B/35B KV-pool constraint (parallel × (max_prompt+max_tokens) ≤ 36,864;
   currently 8 × (1,463+3,072) = 36,280) gets *more* headroom from smaller
   windows. The binding constraints are the ~2,000-2,500B harness truncation and
   the owner's over-stuffing flag (which the sub-topic split, not the char cap,
   actually fixes).

4. **How far C2 goes.** C's objection is correct in principle: for marker-free
   prose sections, "one sub-topic" is not structurally decidable, and forcing
   topic segmentation breaks C1 or C5. But the defect census (78% clean / 11%
   marker-flattening / 7% mid-sentence) says JJK is marker-dominated. The
   resolution the brief itself supplies: C2 is "one sub-topic *where
   structurally possible*" — markers, headings, blank-line blocks split;
   marker-free sections stay whole. C is right about the boundary of C2, not
   against the split itself.

## Blind Spots the Council Caught

Weighing each — real or noise:

- **Extraction cost at 300k pages (E asks; all five miss).** REAL and
  load-bearing. Sub-topic splitting + a smaller cap increases windows-per-page
  and therefore LLM calls. Nobody priced it. The fix is procedural, not numeric:
  the builder is pure and deterministic, so run it over the JJK store (zero LLM
  cost) and report the window-count delta *before* committing to the Marvel/MCU
  scale-out. (Reviews 1, 2, 4, 5 all flag it.)
- **P0b teacher-trace re-anchoring (reviews 2, 3).** REAL. The traces
  (series/jjk/events_trace_*.jsonl) hold exact window inputs + negatives + raw
  answers under the *old* ID space; a rebuild orphans them unless (i) new trace
  records carry window ID + generation, and (ii) old traces are re-anchored by
  passage sentence-hash or archived as gen-1 artifacts. Nobody in the advisor
  round addressed it.
- **The n-ordinal / done-log policy (review 4).** REAL. Done-logs key on n+id
  (verified in .mimoP1_done); the new grid changes per-page window counts, so
  ordinal n shifts and is no longer an identity. Policy: done-logs key on the
  content-stable 16-hex ID; n becomes a display-only per-page sort key within a
  generation. The in-flight log is archived with the pool.
- **Quote-straddling overlap sizing (review 3).** REAL, and the sharpest
  technical catch. G5 bounds quotes from below only (≥20 chars, no max —
  verified); a multi-sentence quote straddling a window cut is verbatim in
  *neither* window, so boundary events are systematically unextractable →
  silent recall loss. The gold distribution (1,298 quotes: median 55, p95 118,
  p99 172, max 231; guideline: "the shortest clause") sizes the carry:
  overlap = whole-sentence run ≥ max(2 sentences, 250 chars). Any quote longer
  than the carry fails G1 loudly (gate) rather than being lost silently.
- **Packed reads violate C2 (review 1).** REAL. events.py:2401-2424 joins
  *multiple sections* into one `[Title]`-labeled window — multiple sub-topics
  by construction. The council must retire the path (off by default; four gates
  confirm no regression).
- **G6 missing from the brief's gate list (E; review 2).** REAL, low-weight.
  G6 (both participants resolved to one node, soft) exists at
  tools/events_gates.py:17/98; the before/after gate runs must include it, and
  single-topic windows should shift G6 soft-fail rates (less cross-topic
  participant confusion) — worth measuring, not assuming.
- **Size never derived from the 3B budget (review 5).** REAL as a process gap,
  but the derivation is anti-climactic: the student's 4,096 seq len does not pick
  the size. The 2,000-char target comes from the truncation limit + over-stuffing
  flag, with the 3B and 27B/35B budgets as "not binding" checks.
- **D's caller list is wrong (review 3).** REAL, small: `_windows` callers are
  abilities.py:392, relations.py:320, narrative_abilities.py:136/212 (verified),
  not events.py:392/2421. Affects the replacement diff, not the design.
- **NOISE / overclaim:** B's "self-healing continuous delta pipeline" —
  `remap_derived` is a rebuild-time snapshot remap after reset+reindex, not a
  per-wiki-edit diff (verified in code); review 4's correction stands, though
  the per-sentence-hash re-anchoring *mechanism* is accurately described and is
  what the council reuses. B's "verified-empties cached forever" dies on B's own
  hash-delta (review 1). B's "fitting under 2,500B structurally kills the
  truncation" is false — size mitigates passage reads; long tool outputs of any
  kind still truncate (review 1). E's 7+11+78=96 arithmetic is a real gap but
  benign (categories overlap; not load-bearing). The "43% natural empty share"
  is asserted, not measured — C6 treats it as an output of size, so the emit
  step must *measure* the new empty share on the new grid and stratify to it,
  not assume 43%.

## The Recommendation

**The builder is a pure function over the index sentence grid. Build it, not a
pipeline.** New module `scriptengine/ingest/windows.py`, TDD'd with
`tests/test_windows.py`, no DB, no schema change (YAGNI — D's day plan holds).

**Algorithm (per section of the `sections` table):**
1. **Grid:** `S = split_sentences(section.text)`; `H[i] = sentence_content_hash(S[i])`.
   Reused verbatim from index/chunker.py — C8 satisfied, no re-index, extractor
   and index on the identical grid.
2. **Sub-topics (C2, where structurally possible):** itemize the section with the
   index's itemizer (generalizing `_section_items`, chunker.py:152): `'''term'''`
   / `;term` marker lines, bare-heading lines attaching to the block below,
   blank-line-delimited blocks. Each item = one sub-topic with a sentence range.
   A marker-free section is one sub-topic (the whole section) — no free-form
   topic segmentation (C's objection respected).
3. **Packing (C1):** within one sub-topic, greedily pack whole sentences up to
   the cap. A sub-topic boundary *always* ends a window — no window straddles two
   sub-topics. An oversized sub-topic splits at sentence boundaries with a
   whole-sentence carry: the next window starts at the previous window's end minus
   the carry; no sentence is ever cut.
4. **Overlap rule (quote-straddling, from review 3 + gold data):** carry = the
   smallest whole-sentence run ≥ max(2 sentences, 250 chars). 250 = observed max
   gold quote (231) + margin, so any quote straddling a cut is fully contained in
   at least one window. A quote longer than the carry fails G1 at the gate —
   loud, never silent.
5. **Packed reads (events.py:2401-2424): retired.** They join multiple sections
   into one window (C2 violation by construction). Delete the joined-unit path
   (or leave the env flag permanently off); the four standing gates confirm no
   regression. Small pages simply get a few small windows.
6. **G1 moves to window level (C5):** quote verbatim in the row's window span
   (section text sliced by s_start:s_end), at tools/events_gates.py:73 and the
   extractor's `quoted_in` call sites — a deliberate gate change: a quote
   verbatim in the section but *absent from the window read* must not be
   attributed to sentences that don't cover it (C's silent-D-T-break point).
   Four standing gates green before AND after (pytest, eval jjk, span-recall,
   canon opm); span-recall must be byte-identical (index untouched); G6 included
   in the runs. JJK stays the baseline-exact reference.

**Data model:**

Window record:
```
{ id,            # 16-hex, derived (scheme below)
  gen,           # builder generation, int (this rebuild = gen 2)
  page,          # wiki page title
  section,       # section heading
  sub,           # sub-entry label, or null when the whole section is one sub-topic
  s_start, s_end,# sentence ordinals on the section grid, inclusive
  hashes,        # [sentence_content_hash(s) for s in s_start..s_end] — the content-addressed core
  text }         # verbatim join of S[s_start..s_end]; a provable span of section text
```
Row (event) attribution adds `quote_span` (sentence ordinals whose span contains
the quote verbatim) — D-T attribution to exact sentences, enabling per-sentence
evals and the `/context` door later.

**ID scheme:** `id = sha256(gen | page | section | sub | s_start:s_end)[:16]`.
Stability contract (A's semantics, gen-scoped): the ID is stable across
re-runs and across re-ingests that leave the section text unchanged (it derives
from content coordinates, not a sequence); it changes when gen, cap,
sub-topic split, or section text changes — and that is *correct*, because the
remappable invariant is `hashes`, which survives any of those via the
`remap_derived` contract. Re-keying old→new is a mechanical script: old window's
`{page, section, passage}` → split into sentences → hashes → covering new window.
Done-logs key on `id` only; `n` is a display-only per-page sort key within a
generation (the n-ordinal is deprecated as an identity, review 4).

**Size target: cap = 2,000 chars per window, with the derivation nobody gave:**
- 3B student (Granite-4.2-3B, LoRA, seq len 4,096 — plan/JJK_STUDENT_TRAINING.md:166):
  2,000 chars ≈ 570 tokens (runbook measured ratio 0.286 tok/char) + ~1k system
  + answer JSON ≈ 2.2k tokens « 4,096. **Not binding.** The student budget allows
  up to ~8k-char windows; it does not demand 4k.
- 27B/35B verifier (KV-pool rule, docs/EXTRACTION_RUNBOOK.md:125-137):
  parallel 8 × (max_prompt + 3,072) ≤ 36,864. Today's max prompt 1,463 tokens
  barely fits (36,280/36,864); a 2,000-char window drops max prompt to ≈700-900
  tokens → strictly more headroom. **Not binding, improved.**
- Binding constraint 1: the harness truncates any tool output >~2,000-2,500 bytes
  (plan/JJK_VERIFY_7000_FINAL.md:22). A 2,000-char passage read sits under it, so
  *passage* truncation in verifier workflows structurally stops; the underlying
  harness limit is fixed on its own track (see c).
- Binding constraint 2: the owner's "not over-stuffed" flag on n=0 (1,902 chars
  / 4 topics). The real fix is sub-topic purity, not the char count — a
  1,900-char *single-sub-topic* window is fine.
- 2,000 is the target cap, not a floor: most windows end at their sub-topic
  length (median current window ≈ 398 chars), so the cap only bites on the
  minority of long sub-topics. The 4,000 runbook cap is retired as a target; it
  remains a safe upper bound that no window exceeds.

**Empty share (C6):** the ~43% figure is an output, not an input. The emit step
(`tools/train/emit_windows.py`) re-measures the empty share on the new grid,
stratifies the 3×500 pools to it, and preserves the rare-verb ×3 upsampling.
Zero-event windows stay results (D6 J6.8), not failures.

**Trace compatibility (P0b, reviews 2/3):** new trace records carry window `id`
+ `gen` (exact inputs stay re-anchorable forever); existing
series/jjk/events_trace_*.jsonl files are re-anchored by passage sentence-hash
where they map, else archived as gen-1 artifacts.

**(a) The 3×500 pools mid-campaign:** freeze, tag `superseded`, archive
`*_windows.jsonl` + done-logs as `*.old-grid`, restart the campaign at n=0 on the
new grid. No row salvage: the prior ruling says the old windowing is structurally
incompatible with D-T/D6, 7% of passages are mid-sentence slices that cannot
anchor to whole-sentence spans, and the campaign is ~8% done — re-running ~117
verifications is cheaper than proving a harvest safe. B's verified-empties-cache
upside returns later via the delta pipeline, not now.

**(b) The 333 old gold:** one re-key script (`tools/train/rekey_gold.py`): each
gold600.jsonl record (id, page, section, passage in messages) → sentence split →
hashes → covering new window(s). Positive rows whose quote stays verbatim inside
a single new window span and passes G1-G7 (incl. G6) keep their adjudicated
status; rows whose quote straddles a new boundary or fails a gate drop for
re-extraction; and every *empty* adjudication among the 333 is re-read on the new
grid, because those empties were judged on contaminated multi-topic windows
(C6 false-negative risk). This is the SWITCHPOINT's "re-verified, not trusted" —
but mechanical gate re-verification, with LLM re-adjudication only for the
delta, not for all 333.

**(c) The two defects:** separate tracks, neither gates the builder.
- *Truncation protocol:* the mitigation already exists (temp file, ≤500-char
  chunk reads, encoded in the final plan doc) and stays as the legacy path; the
  2,000-char cap means passage reads no longer hit the limit; the harness limit
  itself is fixed separately. The spec must not *depend* on the defect (B's
  "structurally kills it" is false — long tool outputs of any kind still
  truncate).
- *wiki_card end-of-series status:* verified as a chapter-scoping bug — the card
  reads `status` from the `facts` table (the series-end infobox value,
  tools/train/verify_row_wiki.py). Flagged-not-fatal, fixed on its own track as
  a chapter-scoped status lookup. Stable window IDs make the flagger re-run on
  fresh windows cheap once it is.

**Cost question (E's, all missed):** the builder run over the JJK store (zero
LLM cost) emits the window-count delta report; the 300k-page commitment happens
only after that number is in hand. Series-genericity is inherited by repo
convention (no series names in .py): Marvel/MCU get the same grid, the same
delta pipeline, and the same per-sentence evals.

Build order (D's plan, with corrections): day 1 ~8h pure builder + invariant
tests (C1 verbatim-substring + hash-union coverage; C2 no cross-sub-topic window;
C5 quote-in-span; ID stability within gen; carry rule); day 2 ~6h replace
`_windows` (callers abilities.py:392, relations.py:320,
narrative_abilities.py:136/212), retire packed reads, move G1 to window level,
four gates before/after; day 3 ~8h emit tool + gold re-key script + JJK
window-count delta report. Total ~2.5-3 working days.

## The One Thing to Do First

TDD the pure builder: `scriptengine/ingest/windows.py` with
`build_windows(section_text) -> [window records]` over the index sentence grid,
plus `tests/test_windows.py` pinning the invariants (verbatim span, hash-union
coverage, no cross-sub-topic windows, carry rule, ID stability within a
generation) — and make its last test a run over the whole JJK store that emits
the window-count delta report. That one artifact unblocks everything else
(emit, re-key, gate move, campaign restart) and answers the council's unanswered
cost question at zero LLM cost, before the 300k-page scale-out is committed.