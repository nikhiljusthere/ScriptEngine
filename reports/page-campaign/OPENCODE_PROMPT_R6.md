# OPENCODE PROMPT — Release R6 (numbering hygiene + entity-anchored recall floor)

Paste everything below the line into opencode.

---

You are continuing the JJK page campaign in `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

**Scope discipline:** every number in this prompt (3 paraphrases, 10% slice, the named example pages) is a hard cap, not a floor — if a step tempts you to go broader (more paraphrases, more series, more pages checked "while you're in there"), that's scope creep, not thoroughness. Stop at the cap and log anything more you found as a candidate for a later release.

**MANDATORY — every shell command you open gets a timeout AND must never go silent for more than ~10-15 seconds.** This has caused a stuck-looking shell twice now, and "add a timeout" alone did not fix it the first time — a command that has a timeout but prints nothing for 60-120 seconds is indistinguishable from a hang to anyone watching, timeout or not. The concrete rule:

1. **No long, unbroken internal poll loops.** Never write a single shell call that kills a process, starts a new one, and then loops silently for up to 60-120s waiting for it to come up. Split it: one short call to kill+start (returns in seconds), then a *separate* poll call.
2. **Every poll loop prints a heartbeat on every iteration**, not just at the end or on failure — e.g. `"poll 3/12: still down"` on every pass, so there is never a silent gap longer than the sleep interval (keep that interval short, 3-5s, not 10-15s).
3. **Cap each individual bounded poll at ~30-40s.** If it times out, the command returns control (prints "STILL DOWN after Ns" and the log tail) instead of extending its own wait — decide whether to retry as a new, separate call, don't silently loop longer.
4. Apply this to everything long-running, not just server restarts: `page-run`, the full `pytest` suite, `canon-run`, `eval` — anything that can run more than ~15-20s either needs its own heartbeat output or must be run in a way whose progress is externally checkable (a file it writes incrementally, a background PID you poll), not a single opaque blocking call.

**Read first:** `reports/page-campaign/HANDOFF_PROSE_PASS.md` (ENGINE GAPS section + State updates 8-11), and your own proposal from earlier today (the "map phrasing -> page, then serve the page's full known fact set" reframe). This release does two things: (1) a 10-minute documentation fix, (2) your proposed entity-anchored recall floor, scoped and gated.

## Part A — G-number collision (fix first, trivial)

Your latest report labelled the new plural-shaped-single-field router fix **"G11."** That number is already taken: `HANDOFF_PROSE_PASS.md` line ~400 has **G11 OPEN (retrieval-quality, R1, location-scoped battle outcome, found on Panda/Jogo)** — a completely different bug. Your new fix is real and gated (confirmed: `_SINGLE_VALUE_FIELDS` + `asks_single_field` at `router.py:312`/`:566`, `TestG11SingleFieldPlural` at `tests/test_router.py:494`, 104/104 router tests pass) — it just has the wrong number.

Renumber it. The next free number is **G16** (currently only informally reserved for Ui Ui's battles-in over-match, `HANDOFF` line ~1052, "G16 candidate" — never formally opened in the ENGINE GAPS section). Your Phantom Cursed Spirit fix becomes **G17** (or take G16 for yours and formally open a new numbered entry for Ui Ui's candidate as G17 — either order is fine, just make the ENGINE GAPS section internally consistent, with no number used twice).

While in there: also formally open Yoshinobu Gakuganji's "affiliations set returns 1 of 2 infobox edges" gap (`HANDOFF` SU11 table, currently just "engine-side gap" with no number) and Tsumiki's "generic kanji-meaning questions do not serve Trivia bullets via BM25" gap (also currently unnumbered) — give both real G-numbers so the ledger has no orphans.

**Also fix the stale tail summary.** The handoff's own "Corrected state (supersedes the broken SU10 bullet)" block (near the end of SU11) says "60/146 done, 86 undone, resume order[56]" — that is now wrong; the character-status table above it already has rows through order[145] with real reports on disk (I independently verified `run.json` exists for all 146, with 132 clean exit-0 and 14 carrying documented-open gaps consistent with method). Replace that block with the true current count.

## Part B — the entity-anchored recall floor (your proposal, implemented)

Your reframe is correct and I verified it against the actual code before greenlighting: `_qa_context` (`scriptengine/api/context.py:324`) calls `retriever.search(query, top_k=top_k, rerank=True, focus=subject)` at line 335, then the budget loop at line 373 (`for order, passage in enumerate(result.passages, ...)`) walks `result.passages` **in ranked order** and stops at `token_budget`. `subject` today only biases the vector focus inside `search()` — it does not guarantee any specific chunk from the resolved page survives the ranked cut. That is the exact, single mechanism behind the G5/G11/G13/G14 "fact exists on page, ranks below the beam" family that has recurred on Panda, Jogo, Kechizu, Tsumiki, Toge, Kamo, and others across this whole campaign. Your fix is the generalized closure of that family, not another point patch.

### Design (concrete, scoped to the qa path only)

1. In `_qa_context`, when `subject` resolves to a known document, fetch that document's own passages **directly from the store** (bypass the vector/rerank path entirely for this part — a lookup by `document_id`/title, not a similarity search).
2. **Order matters more than deduplication.** The existing budget loop (`context.py:373-386`) already has the right shape — it takes items in whatever order they arrive and stops at budget, never dropping the very first item even if it's over budget alone (`if used + cost > token_budget and beats: break`). Feed it: **[subject's own passages, in the wiki's own section order] + [the ranked beam's passages, subject's own passages excluded by id]**. This guarantees the resolved page's content is what the budget gets spent on first, and the beam's cross-page context fills whatever budget remains. Do not build a separate union-then-sort step; reuse the existing loop's cutoff semantics.
3. **Size-aware fallback.** Some pages are large (Ko-Guy: 398 questions; Sukuna: 320). Before unconditionally injecting the full page, estimate its token cost. If it fits within `token_budget`, inject all of it. If it doesn't, inject as much as fits (same loop, same cutoff) and fall back to the existing ranked-beam behavior for the remainder — do not silently truncate mid-sentence; cut on passage boundaries only (the existing chunking already gives you that granularity).
4. **Production vs. evaluation budgets differ on purpose** (`api/main.py:90` defaults `token_budget=6000`; the scorer (`eval/canon_gold.py:101`) already uses `60000`). At 60000 nearly every character page fits whole, so the page-run gate should show close to a step function to 100% on the qa-routed questions across the whole corpus once this lands — that is the actual verification signal, not a hand-picked example. At the production default of 6000, check whether a full page still fits for a representative spread of page sizes (a small character like Kaito Yuki vs. a large one like Ko-Guy) and report the numbers; if 6000 is too tight for typical pages, that is a separate, explicit decision for the user (raise the qa default when a subject resolves, vs. accept partial-page inclusion in production) — do not silently change the production default without calling it out.
5. **This does not touch router mode-selection.** If a question is misrouted to `roster` or `narrative` before it ever reaches `_qa_context`, this fix does nothing for it — the G6/G7/G8/G9/G12/new-G16/G17-class bugs stay on the existing router-fix track, unchanged. Say this explicitly in your report so it isn't read as "phrase-independence, solved."
6. **This does not touch roster/set precision.** The surname-over-match family (Ogi Zenin's and Jinichi Zenin's battle rosters, Ui Ui's battles-in over-match) is a roster-mode bug on a different code path entirely. Out of scope here.

### Gate (unchanged triple, plus one new check)
```
pytest tests/ -q                       # expect >= current count, 0 regressions
eval --series jjk                      # expect 24/24
canon-run --series opm                 # expect baseline: 8/16 exact, 235/237, 78.5%
```
Add a regression test that a resolved-subject qa question whose answer sentence ranks outside today's top-50 beam (pick 2-3 known cases from the G5/G11/G13/G14 gap list, e.g. Kechizu `036`, Tsumiki's kanji-meaning class) now passes. If `canon-run --series opm` regresses, the likely cause is the recall floor injecting subject content into questions where `subject` was a **weak** guess rather than a confident resolution — narrow the floor to apply only when subject resolution confidence is high (reuse whatever confidence signal `_subject_hint`/`_subject` already expose), and re-gate.

## Part C — scoped paraphrase-recall measurement (your idea, sized down)

Your proposal to LLM-generate ~10 paraphrases per fact question and require full recall is the right instrument, but at the corpus's current size (21,500+ live questions) that is roughly 215,000 additional probes — at ~0.87s/question that is over 50 GPU-hours per measurement pass, which is not a sane repeating gate.

**Scale it down, not out:**
- Generate **3 paraphrases per fact**, not 10 — sampled from a **rotating 10% slice of the corpus per release** (different slice each time, so the whole corpus gets covered over ~10 releases), rather than the whole bank every time.
- Reuse the existing R3 adversarial-form machinery (`_jjk_page_probe_r3.json`, the FAST SYSTEM's `faithful_probe.py`/`prose_triage.py`) as the harness — extend it to accept LLM-generated paraphrases as an additional probe-question source, not a new tool.
- Score exactly like every other probe batch: word-boundary containment via the faithful scorer replica, never a qa-mode probe (masks routing failures).
- Every failure gets root-caused and either fixed or given a real G-number — same standing rule as everywhere else in this campaign. Do not report an aggregate "paraphrase recall %" without a root-caused table backing it; an aggregate number with no diagnosis is exactly the kind of measurement that lets a systemic gap hide in plain sight (see: the SU11 audit, which found a prior session's summary numbers looked fine until checked against wikitext ground truth).

## Report

Write `reports/page-campaign/R6_RECALL_FLOOR/REPORT.md`: the G-number corrections made (old wrong number -> new number, for each); the handoff tail-summary fix; the recall-floor design as implemented (file/line references); before/after page-run scores for a sample of the known G5/G11/G13/G14-family failures (Kechizu `036`, Tsumiki kanji class, Toge `051`, at minimum); the three gate results verbatim; the production-budget token-fit numbers for a small vs. large character page, with your recommendation (and explicit flag if you're not making the production default change yourself); and the first paraphrase-recall slice's results, root-caused.

Then resume the character volume at wherever `order[]` currently stands after this session's work — confirm the exact index against `jjk_character_order.json` before resuming, since the handoff's own resume pointer has been wrong before (SU10's fast-model session misreported it; SU11 caught and corrected it).
