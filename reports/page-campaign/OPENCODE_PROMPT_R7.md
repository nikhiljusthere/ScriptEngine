# OPENCODE PROMPT — Release R7 (roster/set precision), fold in after R6

Paste everything below the line into opencode, after R6 has landed and reported.

---

You are continuing the JJK page campaign in `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

**Read first:** `reports/page-campaign/R6_RECALL_FLOOR/REPORT.md` (exists, verified complete and gated), then `reports/page-campaign/HANDOFF_PROSE_PASS.md` ENGINE GAPS section, then this file.

## State since this prompt was drafted — read before Part A

R6 finished and G-numbers moved on: **G16 through G22 are now taken.** Two of them are exactly
the JJK over-match bugs this release was going to diagnose from scratch — opencode's own R6 work
already root-caused them, so don't re-diagnose, implement:

- **G16 (Ui Ui, `HANDOFF` line ~507).** The battles-in roster returns the full 90-battle corpus
  roster instead of Ui Ui's own — recall 2/2, exact fails on 88 intruders. Root cause already
  named: the subject's participant filter is not applied to the battles-in roster for this
  subject. Fix plan already stated: apply it, re-run `ui_ui` (expect 32/32, was 31/32).
- **G18 (Yoshinobu Gakuganji, `HANDOFF` line ~531).** The affiliations set question returns 1 of
  2 stored infobox edges even though both are in `facts.db` at confidence 0.95. Root cause
  already named: the live roster drops a stored edge. Fix plan already stated: find the edge
  filter/subject match dropping it, re-run `yoshinobu_gakuganji` (expect 77/77, was 76/77).

**Ogi Zenin and Jinichi Zenin's surname over-match (battle rosters pulling in Maki's and Naoya's
fights) has no G-number yet** — that one still needs Part A's diagnosis. Do not confuse it with
G16/G18; it's a third, separately-shaped bug (no wiki category grounds the roster at all, per the
handoff's own note on Ogi Zenin).

**Next free G-number for anything new this release finds is G23**, not G16/G17 (both used;
G17 is already fixed and closed, unrelated to this release).

## Scope discipline (read this before Part A)

This is a bounded release, not a research program. Every investigation step below names an exact file, an exact report, or an exact command — if a step would require you to go beyond what's named (reading unrelated modules, auditing series not listed, building new diagnostic tooling from scratch, re-deriving something a report already states), **stop and report what's blocking instead of expanding the investigation.** Time-box Part A to what it takes to read one existing report and run one existing command — if you find yourself writing a new script to answer Part A's questions, stop; the answer is already in `reports/2026-08-31-2312/REPORT.md` and `diagnose_intruders.py`'s output, not something to re-derive from scratch. Part B is one additive change to one function (`_combine`), prototyped and measured — not a refactor of the roster module. If a check turns up more than the specific items named here, log them as candidates for a future release and do not chase them now.

**MANDATORY — every shell command you open gets a timeout AND must never go silent for more than ~10-15 seconds.** This has stalled twice already; a timeout alone is not the fix — a command that has one but prints nothing for a minute or two still looks and functions like a hang. Concretely: never write a single call that kills/starts a process then loops silently for up to two minutes waiting on it — split kill+start (fast, returns in seconds) from a separate bounded poll call. Every poll loop prints a heartbeat every iteration (short interval, 3-5s), not just at the end. Cap each poll at ~30-40s; if it times out, return control and report the log tail rather than looping longer. Apply this to everything long-running — `page-run`, `pytest`, `canon-run`, `eval` — not just server restarts.

## Why this release exists

`canon-run --series opm` has reported the same three numbers — **8/16 exact (50%), 235/237 canon recall (99.2%), 78.5% precision** — since at least 2026-08-15, unmoved across every release of this campaign. That is not a healthy-and-stable metric; it is a diagnosis nobody has read. The tool's own report (`reports/2026-08-31-2312/REPORT.md`) names the two static misses causing the recall gap by name, and breaks down every intruder by extraction path (61% prose row, 18% category page, 12% ownership edge, 8% heading) with the exact fix location. Nobody has acted on it once in three weeks.

Independently, today's character volume found the **same failure shape** on JJK: Ogi Zenin's and Jinichi Zenin's battle rosters over-match on the Zenin surname (pulling in Maki's and Naoya's fights), and Ui Ui's battles-in roster returns the full 90-battle corpus roster instead of his own (all three currently informal "G16 candidate" mentions in the handoff, never formally opened). **Recall is fine in all of these; precision fails because of what rides along with the right answer.** That is corroborating evidence the same class of bug exists, not proof it is the same code path — verify before assuming one fix covers both (see Part B).

## Part A — quantify before touching anything

Do not write a fix first. The relevant code (`scriptengine/retrieve/roster.py`) is already carefully tuned with measured, cited trade-offs per series — `_extracted_roster` (line ~2524) deliberately skips `validate_member` for prose-extracted members, and its own comment cites the cost of not doing that: running Sukuna's and Goku's prose-extracted rows through `validate_member` drops `Dismantle`, `Cleave`, `Shrine`, `Super Saiyan Blue Kaio-ken`, and `Ultra Instinct` — real canon items — because "no field on this page names X as a user," which is exactly why those rows needed extraction in the first place. A blanket filter here is a proven regression, already tried and rejected in spirit by whoever wrote that comment. Do not re-propose it.

1. Re-run `canon-run --series opm` once and read the `canon_scores.json` + intruder diagnosis it produces (the same output shape as `reports/2026-08-31-2312/REPORT.md` already shows you). This one run gives you the exact intruder names, characters, and extraction paths — do not re-derive this by hand-tracing queries, it's already computed.
2. **Ogi Zenin / Jinichi Zenin only** (Ui Ui and Gakuganji are already diagnosed — see above, go implement their fixes, don't re-probe them here): a single yes/no bounded check — **does the over-matched battle roster come from `_extracted_roster`, or from a declared/category roster (`series/jjk/overrides.yaml`) / `_resolves_battles_in`?** Grep the roster's `basis`/`kind` field from one `page-run` or `/context` probe per character, two probes total. The handoff's own note ("no `Ogi Zenin Battles` wiki category exists") is a strong hint it's declared/category, not `_extracted_roster` — confirm with the probe, don't build new instrumentation. If this turns out to be a third distinct mechanism from opm's intruder pattern and from G16/G18, say so plainly and scope Part B to whichever one Part B's corroboration signal actually addresses; do not attempt to fix three unrelated paths in one release.

## Part B — the corroboration signal (primary candidate, verified in code, additive not destructive)

I traced the union step myself: `_combine` (`scriptengine/retrieve/roster.py:2716`) merges two independent roster readings (e.g. `_section_roster` + `_extracted_roster`, or `owned` + `extracted` one level up in `build_roster`) by deduping on `member.name.strip().lower()` — **first-seen wins, and the fact that a second, independent path also named the same member is discarded** the moment the duplicate is dropped. This is precisely the gap the opm diagnostic report names: "corroboration is the signal the union discards when it deduplicates on lowercased name alone."

This is the safer lever than touching `_extracted_roster`'s existing filters, because it is **additive** — it does not remove or narrow any of the measured-good behavior already in place (the stopword filter, the kind-folding, the deliberate `validate_member` skip). It adds a new signal on top:

1. In `_combine` (and the `owned`+`extracted` merge in `build_roster`), track how many independent paths named each member — e.g. a `sources` count or set on `Member`, incremented on every merge rather than discarded on the `continue`.
2. Do **not** hard-filter single-source members outright (that risks the same regression the `validate_member` comment already warns about — plenty of real canon items are single-path, e.g. anything found only by `_extracted_roster` because no page field or category names it). Instead, expose the corroboration count as a **confidence tie-breaker**, used only where precision is already known to be the problem (e.g. when `_extracted_roster` contributes members and the resulting set is unusually large relative to the section it came from) — not a blanket rule applied everywhere.
3. Prototype it and re-measure `canon-run --series opm`'s intruder table before and after. If corroboration alone does not move the needle enough, that is a legitimate finding — report it and stop; do not chain speculative fixes to force a number to move.

## Part C — the two static opm misses (small, separate, do these regardless)

From the latest report, two items have been sitting unaddressed since before this campaign started:
- **Retrieval gap:** "Every technique of Speed-o'-Sound Sonic" — already in the store, not returned. Trace one query end to end before writing code, per the report's own instruction.
- **Corpus gap:** "How many hero classes are in the Hero Association?" — check whether the crawl is current; if the wiki genuinely doesn't support the claim, the gold question is wrong and should be corrected, not the engine.

## Part D — structured-fact (infobox) phrase-independence

**This is no longer speculative — R6 Part C already quantified it.** The 6,468-row paraphrase
measurement found **181 failures (of 498) are "structured-only": the answer exists in
`facts.db` (battle outcomes, episode ranges, chapter/issue numbers) but not in any page's prose,
so the prose-containment page-run scorer structurally cannot verify it.** R6's own report names
two candidate fixes — do one of them, don't invent a third:

1. **Generator-side:** filter structured-answer questions out of the prose paraphrase batch
   before scoring (they were never prose-verifiable questions to begin with).
2. **Scorer-side:** the haystack (`canon_gold.py`'s `present()`/`haystack()`) also accepts a
   match against the served bundle's `facts` field when the routed subject carries it, not only
   against beats/passages text.

Pick whichever is cheaper to verify correct — the scorer-side fix is likely more valuable long
term (it also protects every future paraphrase slice, not just this one), but don't over-engineer
it; a targeted haystack extension, not a rewrite of `present()`.

**Then, separately, the original phrase-independence gap this Part was written for** (folded in
from a different investigation):

Every infobox field question (`IDENTITY_FIELDS` in `scriptengine/eval/page_gen.py:47-62` — debut
chapter, anime debut episode, voice actors, birthday, blood type, height, weight, grade, race,
16 fields total) has **exactly one fixed question template**, applied identically across all 146
characters. Unlike prose (R6's 6,963-paraphrase sweep), these have never been tested for phrase
independence at all.

**Why this is smaller than it sounds, and why it belongs here rather than in R6.** Infobox facts
don't depend on beam-ranking a passage — they ride in a `facts[]` array attached to the resolved
subject: `_qa_context` includes up to 30 (`context.py:376`), `_narrative_context` includes up to
24 via `_subject_facts` (`context.py:177`). As long as the subject resolves and the question lands
in **qa or narrative** mode, the fact is very likely present regardless of exact wording — every
router fix from G1 through whatever R6 lands at already protects these questions incidentally,
since those are routing-layer fixes, not prose-content fixes. So this is not a retrieval-ranking
problem (R6's territory) — it is a routing-mode problem, which is what R7 is already about.

**The one confirmed gap:** `_roster_context` (`context.py:230`) does **not** carry the subject's
own infobox facts — only set-specific "Result" cells (e.g. battle outcomes). `roster.facts` there
is a different thing from `result.facts` in qa mode. If a natural rephrasing of an infobox question
misroutes to roster mode — exactly the failure class this campaign keeps finding (G6, G8c,
G11-old/G17) — the fact is not ranked lower, it is **absent**, with no fallback the way narrative
mode has one.

### Bounded checks (same discipline as Parts A-C — do not expand beyond these)

1. **One probe set, not sixteen.** Pick 3 of the 16 `IDENTITY_FIELDS` (recommend: `debut` and
   `class`/grade — both plural-shape-adjacent, already implicated in G6/G17 — plus one more of
   your choice) and write ~3 natural rephrasings each (a yes/no, a plural-shaped variant like
   "What are X's grades?", and one ordinary alternate phrasing) against 5 already-verified
   characters. 45 probes total, hard cap — this is a spot-check for the failure class, not an
   exhaustive sweep of 16 fields x 146 characters.
2. For each probe, record only: did it route qa/narrative (fact present, expected) or roster
   (fact likely absent, the confirmed gap)? Use the faithful probe tooling already in the temp
   dir (`faithful_probe.py`) — do not build new instrumentation.
3. **If roster misrouting shows up in the sample**, the fix belongs in `_roster_context`: give it
   the same `_subject_facts` fallback narrative mode already has, gated behind whatever confidence
   signal keeps it from firing on a genuine multi-member roster question. Do not touch
   `IDENTITY_FIELDS`' templates themselves — the fix is in routing/serving, not in adding more
   templates.
4. If the 45-probe sample shows no roster misrouting at all, report that plainly and stop — do
   not manufacture a fix for a gap the sample didn't reproduce.

## Gate — tiered, not a blanket resweep

This is broader-blast-radius code than R1/R5/R6 (those were qa-mode routing only; `roster.py`'s own comments show `_extracted_roster` has measured, cited trade-offs spanning HxH, JJK, and DBZ in the same function). Recheck in tiers, not with one undifferentiated full resweep:

1. **Standing gate (mandatory, cheap):** `pytest tests/ -q`, `eval --series jjk` 24/24, `canon-run --series opm` — expect the exact/precision numbers to **move** this time; report the new numbers, don't just confirm "no change."
1a. **Also run `canon-run --series jjk --skip-eval` once (bounded, single run).** Its own bank (`questions/jjk.json`, 55 entries) has not been re-measured since **2026-08-19** — before this entire campaign started. Last known numbers: exact 22/29 (75.9%), canon recall 96.6%, precision 87.9%, fact_present 19/23. Unlike opm, do NOT expect this one to be unmoved — 146 characters' rosters have been built and restructured since that run, so this is a **progress check, not a regression check**: report the new numbers plainly, whichever direction they moved.
2. **Cross-series spot-check (this release's actual new requirement):** since this code path is shared across all 8 series, re-run `canon-run` (or the equivalent roster-question spot-check) for **hxh** and **db** at minimum — the two series whose canon math is cited by name in the `_extracted_roster` comment (Killua, Sukuna already covered under jjk, Vegeta, Goku). Confirm none of those cited numbers regressed (Killua's Nen abilities, Vegeta's forms, Goku's forms — the comment gives the exact before/after counts to check against).
3. **Targeted JJK re-runs, not a full corpus resweep:** `ui_ui` (expect 32/32, G16 fix) and `yoshinobu_gakuganji` (expect 77/77, G18 fix) are mandatory — those are the two known, already-diagnosed fixes this release ships. Add Ogi Zenin and Jinichi Zenin if Part A's diagnosis leads to a fix for them too, plus any other character whose batch has a `Every battle involving X` / `Every technique of X` style set question. The other ~140 characters' plain fact questions never touch this code path and do not need re-running. Save the full 987-page resweep for the campaign's actual final-proof step (per `PLAN_NEXT_PHASE.md` §8 item 8), not for every roster tweak.

If any cross-series number regresses, narrow the fix (the corroboration threshold, or scope it to specific extraction paths) and re-gate — do not ship a precision win on one series that costs canon items on another.

## Report

Write `reports/page-campaign/R7_ROSTER_PRECISION/REPORT.md`: the G16 fix (participant filter) and G18 fix (affiliations edge-drop) with their re-run scores; the Ogi Zenin/Jinichi Zenin diagnosis from Part A and whether it shares a code path with opm's intruder pattern or G16/G18 (with evidence either way); the corroboration-signal design as implemented, with before/after `canon-run --series opm` numbers; the two Part C (opm static-miss) fixes; the Part D structured-fact fix (generator- or scorer-side, whichever was chosen) plus the 45-probe phrase-independence results; the tiered gate results (standing gate numbers, hxh/db spot-check numbers against the comment's cited baselines, all targeted JJK re-run scores). Close G16 and G18 in the handoff with their fix + re-run evidence. Open **G23** (not G16/G17) for the Ogi Zenin/Jinichi Zenin mechanism if it turns out distinct from everything else found.

Then check `jjk_character_order.json` yourself: if all 146 characters have a completed run (they did as of this writing), the character volume is done — move to the **episode pass** (59 pages) using `reports/page-campaign/episode_prose_template.md` (from the R5 template study) and `reports/page-campaign/retire_ledger.json` (339 cross-page retires waiting to be absorbed, some of which are technique/episode facts this next phase may own). Do not restart the character loop if it's already finished.
