# Pre-registered item for the Phase-1 close council — the coverage denominator

**Status: PRE-REGISTERED (owner-raised, 2026-09-10). B carries this into the
Phase-1 close council as a numbered item. The council must rule on it before
Phase 2 commits any GPU-day.** It is pre-registered rather than raised in
review because a question asked after the extraction budget is spent cannot
change the answer.

## The finding

The same tool, `tools/coverage_report.py`, series-aware since CSM-2, reports:

| | JJK | CSM |
|---|---|---|
| pages covered | **893 / 987 (90.5 %)** | **0 / 537 (0.0 %)** |
| active questions | **29,819** | **0** |
| in-scope content remainder | **0** | **227 pages** |
| page-campaign artifacts | **1,706 files** | **1** (COVERAGE.md itself) |

CSM's 227-page in-scope remainder: character 175, character_history 22,
episode 12, organization 11, establishment 3, `unknown` 4.

Alongside it, the instrument that decides whether dimensions are green — the
dimension census — is **60 questions: 6 classes × 10, over 36 distinct
subjects**, and all six classes (arc-narrative, state-over-time, abilities,
personality, appearance, causality) are *character-page* dimensions. It
contains **no chapter, volume, episode, organization or establishment
question at all**, though `chapter_box` is 232 of the 537 pages and
chapter/episode summaries are **90,421 words over 243 sections** — the
second-largest prose block in the corpus, behind per-character arc narrative
(112,628 w / 471 sections). Abilities are measured by 10 questions against
**376 ability rows over 75 characters**.

## Why it has to be ruled on *before* Phase 2, not after

`plan/CSM_2PHASE_PLAN.md` P2.3 carries a **null branch**: if the 5.4
re-adjudication closes the 21 extraction-gated reds, *"the adjudication closes
all 21 reds, de-scoping P2.3 entirely — voids P2.5"*. Those 21 reds are reds
**of the 60-question character-only census**. So on the current plan CSM can
reach "all dimensions green" — and skip the extraction leg outright — without
one chapter-page, volume-page or episode-page question ever having been asked,
and with its own page-coverage tracker still reading 0/537.

That would be a 100 % that is not JJK's 100 %, produced by a smaller
denominator rather than by more work. It is precisely the failure mode the
campaign's own standing rule guards against ("raw receipts, never '100 %'
prose").

## What *is* measured — so the council does not over-correct

CSM is not unmeasured. It is measured by instruments with different
denominators, and the gap is specific:

- **17,181-row pinned panel (+200 held-out)** — exhaustive tier-1 over the
  whole corpus, chapter and episode pages included. Measures **whether a
  sentence can be retrieved**, not whether a question about the page can be
  answered.
- **Eight-verb sample** — measures the chapter/episode Summary slice directly,
  and reports **24/100 covered: 76 % of that slice cannot be held by the live
  9-verb set**. So the largest non-character dimension is not unexamined; it
  is examined and known to be thin.
- **T0 identity pilot** 843/843, **door censuses** roster 11/11 + narrative
  97/100, **seed bank** 39, **d4 open-50**, **gold_sliced** 200.
- **`dimension_map_csm.md`** is genuinely thorough: 12 dimensions with
  measured word counts and explicit, reasoned "not scheduled" calls (Trivia
  18,680 w "no named consumer"; Physical Prowess 2,570 w "thin, no failing
  test"; Etymology; Overview; Human Form).

The gap is therefore **not** "CSM was never measured". It is: **no per-page
question coverage exists, and the dimensional instrument samples one page type
out of the five in-scope ones.**

## The JJK precedent the owner is invoking

JJK did not reach 100 % by sampling. Long prose pages were split and worked
deliberately, in parts, with machinery on disk to prove it: six
`CHAPTER_PROSE_WAVE{1..6}.md` waves, `CHAPTER_PROSE_TRIAGE.md`, per-page-type
templates (`chapter_prose_template.md`, `episode_prose_template.md`,
`battle_prose_template.md`, `character_synopsis_prose_template.md`,
`content_pages_template.md`), `EPISODE_SWEEP_PROGRESS.md`, unit ledgers, and
29,819 authored questions tracked page-by-page in COVERAGE.md until the
in-scope remainder hit 0.

**CSM has none of that machinery.** Its COVERAGE.md was generated once
(2026-09-08) and has read 0/537 ever since.

## What the council must decide (each answer recorded with its reason)

1. **Is "dimensions green" claimable from a character-only census?** If not,
   the census must gain items for `chapter_box` (232), `episode` (12),
   `volume_box` (26), `story_arcs_box` (14), `organization` (11) before any
   green claim. Authoring is model-free and cheap; the cost is authoring time,
   not GPU.
2. **Is 10 questions against 376 ability rows a sufficient bar**, or does the
   abilities dimension need a pool sized to the rows (JJK's ability work used
   a 315-pair pool)?
3. **Does the P2.3 null branch survive this?** Specifically: may extraction be
   de-scoped on the strength of the 60-question census, or must the null
   branch be re-gated on the widened census?
4. **Does CSM owe a per-page campaign at all** — i.e. is the 227-page in-scope
   remainder a real deliverable (JJK's shape), or is CSM's done-criterion
   deliberately different? **If deliberately different, the difference must be
   recorded as a scope decision with a reason**, not left as an unstated
   denominator. This is the crux: the plan has been called concrete while this
   was never stated either way.
5. **Do the long-prose dimensions need JJK's in-parts treatment** — arc
   narrative 112,628 w / 471 sections and chapter/episode summaries 90,421 w /
   243 sections — with waves, templates and a triage log, rather than being
   carried by line-level retrievability alone?

## Standing instruction that follows from this item

Whatever the verdict: **no Phase-2 GPU-day is committed until questions 1–4
are answered on disk with reasons.** A widened census is model-free to author
and can run inside the existing sanity window; discovering the denominator was
wrong after a 2-GPU-day sweep cannot be undone.

## The general lesson (raised by the owner, worth its own council minute)

This gap survived a plan review, two councils and a phase of execution because
**every instrument reported its own numerator honestly and none stated its
denominator.** "39/60 green" is true; "60 questions over 36 character
subjects, 0 of 537 pages covered" is the same fact with the denominator
attached, and it reads completely differently. The council should consider
requiring **every** campaign instrument to state its denominator and its
excluded population in the same line as its score — and should re-audit the
other Phase-2 acceptance bars (P2.2 bar audit, P2.4 writer-facing acceptance
leg, the A17 per-door floor policy) for the same defect before they gate
anything.
