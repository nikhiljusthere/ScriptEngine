# CSM dimension map — what "everything about a character" means (CSM)

Regenerated 2026-09-09 from CSM's own `sections` on `character` +
`character_history` pages (222,761 words of character prose, 0 events, 0
meaning rows — Phase-2 territory) and from `plan/Plan_to_perfection.md` §12,
whose format this mirrors. JJK's map is the shape reference only; every
number below is CSM's own, measured from `series/csm/facts.db`
(`documents.revid` all 0; the corpus pin lives in `questions/csm.json`
`revids`, 19 pages).

| dimension (CSM's own section) | words | extracted today | consumer — the query this buys | acceptance |
|---|---:|---|---|---|
| Arc narrative (per-character arc/saga sections) | 112,628 (471 sections) | 8-verb events only — **0 extracted (Phase 2)** | "what happened, in order" (the narrative door, §9a sweep) | narrative door ≥1 ordered beat per question; the known miss list (G-CSM-2 passage leg, G-CSM-3 intruders) |
| Chapter/episode summaries | 90,421 (243 sections: 231 chapter_box `Summary` + 12 episode `Summary`) | same 8-verb gate, 0 extracted | "what happened in this chapter/episode" | the eight-verb coverage measurement below (decides widen-set-before-extract, per the JJK 1C rule) |
| **Personality** | 22,322 (164) | **none** | how a character *speaks and behaves* | retrieval test: 10 "how does X behave" questions — served bundle contains the paragraph → no extraction owed; if no, a chunking defect, not a missing table |
| Trivia | 18,680 (159) | none | colour, out-of-universe notes | **not scheduled** — no named consumer; corpus property, stays prose |
| **Appearance** | 7,179 (167) | **none** | how to describe them on screen | retrieval test (same rule as Personality) |
| Abilities + Devil/Hybrid/Supernatural Powers + Skillset (the ability vocabulary) | 23,205 (Abilities 7,545 / 140 + Devil Powers 7,150 / 35 + Hybrid Powers 2,943 / 8 + Supernatural Abilities 1,710 / 6 + Skillset 1,857 / 29) | names only: the `abilities` table (376 rows / 75 characters) + the `page-gen:techniques` roster | "Every ability of X" (the seed bank's G-CSM-3 form) | the census measures the door; the section-scoped intruder (G-CSM-3) is the known miss |
| History (pre-series) | 5,417 (84) | none | pre-series backstory | folded into D4 open-50 where authored; retrieval test |
| Devil Contracts | 2,555 (17) | rosters table (11 of 20 declared rosters carry members) | enumeration ("every devil X contracted with") | the roster door (G-CSM-1 recall 0/5 is the known miss) |
| Physical Prowess | 2,570 (26) | none | feats, limits | **not scheduled** — thin (2.6k), no named failing test |
| Etymology | 1,119 (46) | none | name origins | **not scheduled** — trivia-shaped, no consumer |
| Overview | 1,343 (4) | none | one-paragraph brief | **not scheduled** — 4 sections, corpus property |
| Human Form | 907 (8) | none | form description | **not scheduled** — 8 sections |

### The precondition the map rests on — measured now

The eight-verb coverage (JJK §12's unmeasured precondition) is measured on
CSM in `eight_verb_sample_csm.md`: **24/100 covered, 76% of the CSM
chapter/episode Summary slice cannot be held by the live verb set.** The live
set is 9 verbs (`events.py` `EVENTIVE_VERBS`: fought/killed/awakened/sealed/
betrayed/saved/arrived/departed + `met`, added by the JJK COUNCIL_1 widen
ruling — the job's "eight-verb" is the §12 name, the live set is what the
extractor will run on CSM). 69/76 uncovered are pure description (the closed
set working as designed); 3 fight-adjacent, 3 kill-intentions, 1 save-
decision. No recurring true eventive gap (JJK's `met/encountered` did not
recur: 0 first-contact events in this slice, mid-series chapters). Reading:
on CSM's dialogue-dense summaries the set is thinner than on JJK's (24 vs 39
covered) — the 1C decision (widen before extract) rides on this number when
Phase 2 schedules the extraction.

### The three dimensions the map does not cover, and must (CSM read)

1. **State over time.** What was *true* of a character during an arc —
   affiliation, status, alive/dead, possessed. On CSM the mains carry empty
   saga-section shells (`Public Safety Saga` / `Academy Saga`, 0 words — the
   same JJK gap that motivated interval `extra_facts`); state content lives in
   supporting characters' arc sections and the synopses. `series/csm/
   overrides.yaml` declares **no `extra_facts`** yet. Consumer: D4 open-50's
   state questions (authored, on disk). Acceptance: 10 state questions in the
   dimension census — green means prose retrieval suffices; red is the CSM
   trigger for the interval-facts / extraction build (P6).
2. **Outcomes.** Who won a fight. CSM has **0 battle-type pages and no
   outcome-shaped fact keys** (verified: no `*outcome*`/`*result*` keys in
   `facts`). Stays unmapped — never guess a field the wiki does not publish.
3. **Causality.** Why something happened. No CSM section carries it
   structurally; the 76 measured causal sentences (76 `because`-sentences in
   the narrative sections) are prose. Consumer: D4 open-50's why-questions.
   Acceptance: 10-question retrieval test.

### What schedules off this map

`census_dimensions_csm.json` freezes 60 questions — 10 per schedulable
dimension (arc narrative, state over time, abilities, personality, appearance,
causality), each with 3 verbatim expect-terms drawn from the section text and
a `source` stamp. The model-run of that census is the orchestrator's
one-copy CUDA window (this unit is zero-GPU); green/red per dimension feeds
the 5.4 extraction gate and §9a.