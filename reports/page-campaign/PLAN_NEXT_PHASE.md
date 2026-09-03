# PLAN — NEXT PHASE (analysis + sequencing, 2026-08-27)

Companion to `HANDOFF_PROSE_PASS.md`. That file records *where we are*; this one records
*what to do next and in what order*, with the evidence behind each call.
All routing evidence below was produced **in-process** (`route()` / `_is_interrogative()`
called directly against `series/jjk`) — no server, no GPU, so it is reproducible any time.

---

## 0. Verdict in three lines

1. The **method** is right (verbatim answers, diagnose-don't-dodge, gate every fix).
2. The **sequencing** is wrong for what remains: gaps are being *accumulated* across
   batches (G5, G8a–d, G9a–d, G10 = 10 open) while volume continues. Each open gap is a
   future re-run of every batch authored after it.
3. The **corpus does not yet test the NORTH STAR.** 9 of 21,521 live questions (0.04%)
   are yes/no forms. The pass rate measures wh-questions, which the router already
   handles. Five of eight open router gaps are yes/no — they appeared the moment
   Shoko/Geto authored them naturally.

---

## 1. Measured state (this repo, today)

| Quantity | Value | Source |
|---|---|---|
| JJK wiki pages | 987 | `series/jjk/wikitext/*.json` |
| Real batches (non-`.verify`) | 513 (77 empty) | `questions/_jjk_page_*.json` |
| Live questions | **21,521** | scan |
| Retired (cross-page debt) | **339** across 48 batches | scan |
| Characters done | 14 redos + **7 of 132** new | §5 handoff |
| `page-run` cost | **26.9 s / 31 questions** (~0.87 s/q) | `jjk-mei_mei-…-2341/run.json` |
| Full-corpus re-sweep cost | **~5.2 GPU-hours** (21.5k × 0.87 s) | derived |
| Yes/no questions in corpus | **9 / 21,521 (0.04 %)** | scan |
| Pace | ~2.3 characters/day at 2 agents | 08-25 → 08-27 state updates |

**The two numbers that decide the plan:** a full re-sweep is ~5 GPU-hours (cheap), and
authoring one character is hours of agent time (expensive). *Re-scoring is not the cost.
Re-authoring is.* So: never fear a re-run; always fear a gap that forces re-authoring, and
always fix the engine before authoring more pages against it.

---

## 2. Root-cause diagnosis of the 8 OPEN router gaps

Each question was routed in-process. `route()` result and the actual mechanism:

| Gap | Routed | Real root cause |
|---|---|---|
| G8a `Was Geto dependent … in battle?` | narrative | **A** — `_is_interrogative` is wh-only; `Was` → not interrogative → narrative default |
| G8d `Can Geto cast Curtain over a weaker sorcerer's barrier?` | narrative | **A** + **B** — also `_subject()` resolves **`Jujutsu Sorcerer` (organization)** off "sorcerer's", not Geto |
| G9a `Does Shoko have an innate cursed technique?` | narrative | **A** |
| G9c `Can Shoko teach someone …?` | narrative | **A** |
| G9d `Is it easier for Shoko to heal herself or others?` | narrative | **A** |
| G8b `What was the true goal of the Night Parade …?` | narrative | **B** — subject resolves to the *event* `Night Parade of a Hundred Demons`; the page the question was authored against (Geto) is never considered |
| G8c `Under what condition can Geto absorb a curse with no consequences?` | roster | **C** — `wants_chronology()` substring-matches **"sequence" inside "con-sequence-s"** (`chronology.py:589`, no word boundaries) → "asks for the story in order" → 0-beat roster |
| G9b `What happened to Ijichi and Ino if they had not been treated by Shoko?` | narrative | **D** — past "what happened to" is *deliberately* narrative (guards an eval gold row); needs a negated-conditional discriminator |

**Three causes cover seven of eight gaps.** G8/G9 are not two gap families — they are one
missing interrogative branch, plus one missing subject hint, plus one regex typo.

### Cause A — no yes/no interrogative branch
`router.py:96 _is_interrogative` recognises wh-words only (directly, behind a comma,
behind a leading preposition, behind a discourse marker). Auxiliary-fronted questions
(`Is/Are/Was/Were/Do/Does/Did/Can/Could/Will/Would/Has/Have/Had/Should/May/Might/Must`)
are not questions to it, so they fall through rule 3 to the narrative default.

Verified in-process:

```
G8a  interrog=False  Was Suguru Geto dependent on his curses in battle?
G8d  interrog=False  Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?
G9a  interrog=False  Does Shoko have an innate cursed technique?
G9c  interrog=False  Can Shoko teach someone how to use reverse cursed technique?
G9d  interrog=False  Is it easier for Shoko to heal herself or others?
```

### Cause B — the router never sees `subject`
`api/main.py:204` calls `route(paths, request.query)`. `request.subject` — the page the
question was authored against, which the scorer *does* send (the G3a fix) — is only
forwarded to `build_context` (`:213`) and, inside it, only to the **qa** path
(`api/context.py:154, :336`). So the mode decision is made blind to the authored page.
Every "authored on page X, answered from page Y" failure is downstream of this.

### Cause C — `wants_chronology` substring match
`chronology.py:589`: `any(w in lowered for w in ("in order","chronolog","timeline","sequence"))`.
Latent corpus-wide for `consequence(s)`, `consequently`, `subsequent`. One live hit today
(`jjk-pg-suguru_geto-073`); it will recur on technique/battle pages where "consequence"
is common vocabulary.

### Cause D — negated conditional vs. past-event narrative
Genuinely hard: `What happened to Nanami during the Shibuya Incident?` must stay
narrative (eval gold). Lowest priority, highest regression risk — do it last, alone.

---

## 3. Release R1 — engine fixes (do this BEFORE more volume)

One release, one gate, one server restart. Scope:

- **R1-a (Cause A).** Add an aux-fronted branch to `_is_interrogative`. Guard: a yes/no
  question whose head verb is a *story* verb stays narrative (`Did Sukuna kill Nanami?`
  is an account). Fixes G8a, G9a, G9c, G9d, and half of G8d.
- **R1-b (Cause B).** Thread `subject` into the router: `route(paths, query, settings,
  subject=None)`, passed from `api/main.py:204`. When an explicit subject is supplied and
  it is a non-story type, it wins over `_subject()`'s inference for the mode decision.
  Fixes G8b and the rest of G8d. **Highest-leverage change in this release** — it is the
  same recall argument as G3a, applied one stage earlier.
- **R1-c (Cause C).** Word-boundary the chronology trigger:
  `\b(in order|chronolog\w*|timeline|sequences?)\b`. Fixes G8c.
- **R1-d.** Extend the G6 guard to the *partial-confidence, did-not-narrow* roster case
  (belt-and-braces behind G8c).
- **R2 (G10, independent).** UTF-8 write path for batch files (`ensure_ascii=False`,
  `utf-8-sig` round-trip assertion), correct `mei_mei` Q001's garbled kanji answer,
  un-retire it, add a CJK round-trip regression test.

**Gate (unchanged, all three must pass):** `pytest tests/ -q` (>= 1046),
`eval --series jjk` 24/24, `canon-run --series opm` at baseline (8/16 exact, 235/237,
78.5 %). Add regression tests named per gap (`TestGetoGaps`, `TestShokoGaps`) the way
`TestPandaGaps` was added for G6/G7.

**Then re-run, expecting:** `suguru_geto` 94/94, `shoko_ieiri` 34/34, `mei_mei` 32/32
(after the un-retire), `toge_inumaki` unchanged at 84/86 (its two are retrieval, not
routing — they belong to R4). Cost: ~2 minutes of GPU. That is the whole re-run bill.

---

## 4. R3 — the phrasing-bias gate (the NORTH STAR's actual test)

0.04 % of the corpus is yes/no. The bank has been self-selecting toward forms that pass.
Until that is fixed, "100 % on 21,521 questions" does not mean "any natural question
resolves".

**Add a standing adversarial probe set.** For every character already marked done, author
~6 questions in the forms the wh-bank never exercises, against facts already proven to be
on the page:

1. yes/no (`Does/Is/Can/Was …?`)
2. comparative (`Is X easier than Y …?`)
3. negated conditional (`What would have happened if X had not …?`)
4. scope-phrase (`… in battle`, `… during the Shibuya Incident`)
5. event-name scope (`… of the Night Parade of a Hundred Demons`)
6. possessive-noun bait (`a weaker sorcerer's barrier` — the G8d subject trap)

Run them as a **separate probe batch**, not inside the page batches, so a failure does not
block a page's exit 0 but does surface a gap. 21 characters × 6 ≈ 126 probes ≈ 2 minutes
to score. Every new failure becomes a G-n with a root cause, exactly as now. This is the
cheapest insurance available: it finds router classes *before* 125 more characters are
authored against them.

---

## 5. R4 — the retrieval track (G5), run in parallel, not in the critical path

Open members: the 5 residual §11 misses, Toge `051` (unique keywords absent from the
top-k beam) and `060` (answer spans a chunk boundary). All are *in-page* facts that exist
in the index but rank below top-50, so beam depth is exhausted — the API cap is 50.

Three candidate levers, in order of expected value per unit of risk:
1. **Question-side expansion** (synonyms of the wh-object). Answer-side expansion would be
   dodging and is forbidden; question-side is legitimate and cheap to A/B.
2. **Reranker depth**: rerank a wider shortlist than the fused top-50 before truncation.
3. **Quote-aware / boundary-aware chunking**: `060` is a chunk-boundary artefact of the
   G3b v2 line-unit rule — a sentence-clause split. Lowest-risk of the three, but needs a
   re-index (16,875 chunks) and a full re-sweep to prove no regression (~5 GPU-hours,
   affordable).

Do **not** block the character volume on R4. Document, batch the findings, and take one
re-index + one re-sweep when there are enough of them to justify it.

---

## 6. Throughput plan for the remaining ~979 pages

Remaining: 125 characters, then 59 episodes, 90 battles, 149 techniques, 304 chapters,
72 character_synopses, 35 volumes, misc.

At the current 2.3 characters/day, 125 characters ≈ **8 weeks**, and the other 704 pages
are the larger half of the job. Three levers, in order:

1. **Parallel authoring, serialized scoring.** Scoring is 27 s; authoring is hours.
   Run 2–4 authoring agents concurrently and let them queue their `page-run`s. The real
   ceiling is VRAM (the ScriptEngine CUDA server on :8000 shares the GPU with the
   Qwen3.8-27B NVFP4 server on :18080) — pick the agent count from VRAM headroom, not
   from scoring throughput.
2. **Template the uniform page types NOW, in parallel with characters.** Characters are
   the *least* uniform page type and the most expensive per page. Episodes (59), chapters
   (304) and volumes (35) are highly templated wiki pages — one section-shape study each
   should yield a near-mechanical generator, which is where the 304-chapter block becomes
   affordable. Start one agent on an **episode template study** now; do not wait for
   character 132.
3. **Batch the engine work.** Every engine edit invalidates in-flight runs (the page-run
   stale guard) and costs a server restart. Collect gaps, ship them as R-releases (R1,
   R5, …), not one at a time.

---

## 7. Retire-debt ledger (needed before the techniques pass)

339 retires sit inside 48 individual batch files. The techniques pass (149 pages) is
supposed to *absorb* the cross-page technique-definition retires (e.g. Mahito `108`
Black Flash, `116`/`117` Polymorphic Soul Isomer), but nothing currently links a retire
to the page that owes the answer.

**Build `reports/page-campaign/retire_ledger.json`** — one row per retire:
`{batch, id, question, reason, owed_by_page, absorbed:false}`. Generate it by scanning the
batches (cheap, no GPU). Each later page-type pass marks `absorbed:true` when it authors
the owning question. The final sweep asserts **zero unabsorbed cross-page retires** — that
is the piece of the NORTH STAR the current per-batch exit-0 gate cannot see.

---

## 8. Ordered work queue

| # | Work | GPU? | Blocks volume? |
|---|---|---|---|
| 1 | **R1-a/b/c/d + R2** engine release, gated | gate only | yes, briefly |
| 2 | Re-run `suguru_geto`, `shoko_ieiri`, `mei_mei` | ~2 min | no |
| 3 | **R3 adversarial probe batch** for the 21 done characters | ~2 min | no |
| 4 | Resume volume: Tengen + Hanami, then Mai Zenin + Kinji Hakari, … | yes | — |
| 5 | `retire_ledger.json` generator | no | no |
| 6 | Episode-template study (parallel agent) | no | no |
| 7 | R4 retrieval track — collect, then one re-index + re-sweep | yes | no |
| 8 | Final proof: full corpus re-sweep, gate triple green, zero unabsorbed retires | ~5 h | — |

Resume pointers are unchanged and correct: `jjk_character_order.json` `order[21]` =
**Tengen**, `order[22]` = **Hanami** (0-based; verified against the file).

---

## 9. Risks

- **R1-a over-claims.** Making yes/no interrogative could pull genuine event questions
  (`Did Sukuna kill Nanami?`) out of narrative. The story-verb guard is the mitigation;
  the `canon-run --series opm` baseline is the detector. If opm drops, narrow the branch
  to yes/no questions whose subject is a character/thing rather than an event.
- **R1-b over-steers.** A subject hint that *overrides* rather than *informs* would make
  the router unable to answer a question that legitimately belongs to another page. Keep
  it a precedence rule for non-story subject types only, and keep the wide search intact —
  the same shape as the G3a recall fix.
- **R3 finds a lot.** Expect the adversarial batch to surface new G-n classes. That is the
  point, and it is far cheaper now than after 125 more characters.
- **Question quality drift.** Spot-check of the Mei Mei batch shows forms drifting toward
  what the retriever will pass rather than toward natural questions — e.g. `024` "What
  degree of control does Mei Mei have over cursed energy making her a master?" → answer
  "cursed energy control" (near-tautological), `030` "Mei Mei uses Black Bird Manipulation
  to imbue crows with what to control them?" (wh-word stranded at the end, statement
  shape), `018` "How many individuals …?" answered with names rather than a count. These
  pass the scorer and still fail the NORTH STAR. Add a cheap authoring lint: reject a
  question whose answer string appears inside the question, reject a non-initial wh-word,
  and require a count answer for a "how many" question.
- **Pace.** Even with every fix above, the 987-page NORTH STAR is a months-scale program at
  character-style per-page cost. The templating lever (§6.2) is what changes the order of
  magnitude — treat it as first-class work, not as an afterthought after the characters.
