# R1 ENGINE RELEASE — Report (2026-08-27)

Release **R1 + R2**: closed the router gaps **G8a–d**, **G9a/c/d** and the CJK
encoding gap **G10**, gated on the triple (`pytest` + `eval jjk` +
`canon-run opm`), then verified on the live server with the four page re-runs
and a fresh **R3 adversarial probe batch**. **G9b** (the negated conditional)
is deliberately left OPEN per the release spec. R3 confirmed G9b across seven
characters and surfaced one new retrieval-quality class (**G11**).

No character volume was authored in this run (per the release mandate). The
resume pointer is **Tengen** (`jjk_character_order.json` `order[21]`), then
**Hanami** (`order[22]`).

---

## 1. What changed, file by file

### `scriptengine/retrieve/router.py` (R1-a, R1-b, R1-d)

- **`_AUX_FRONT` (L100)** — a `frozenset` of auxiliary verbs
  (`is/are/was/were/do/does/did/can/could/will/would/has/have/had/should/
  may/might/must`). A yes/no question fronts one of these instead of a
  wh-word, which is why the wh-only test read it as a statement.
- **`_is_interrogative` (L106, branch L128)** — *R1-a.*
  `if parts[0].lower() in _AUX_FRONT: return True`. This is what carries
  G8a / G9a / G9c / G9d to `qa`.
- **`_YES_NO_STORY` (L200, applied L311)** — a story-verb guard so a yes/no
  question whose head is an *account* verb (`Did Sukuna kill Nanami?`) stays
  narrative, the way the wh-form head-window check does. The opm canon
  baseline is the detector for over-claiming.
- **`route(..., subject=None)` (L278) + `_subject_hint` (L677)** — *R1-b.*
  The page the question is authored against (the scorer sends it, the G3a
  fix) now takes **precedence** over `_subject()`'s inference for the mode
  decision. A precedence rule, not an override: a non-story-typed subject
  takes the decision; a story-typed (or unresolvable) subject keeps the
  query's own read; the qa wide search takes the page as a focus either way.
  This is what fixes **G8b** (the event scope resolves only the event) and
  reinforces **G8d** (the possessive bait resolves the organization off
  "sorcerer's").
- **`_resolves_a_set(..., counting=False)` (L495–496)** — *R1-d.* The strict
  partial-confidence gate (`roster.matched and confidence in
  ("exact","declared")`) now applies **only when `counting=True`**. A
  counting question with a narrowing qualifier ("…used to trap?") reads the
  number from prose; a plural membership question ("Who are the members…?")
  keeps the `matched` short-circuit (its `partial` confidence is only because
  the interrogative is unverified, not because the set is absent).
  Belt-and-braces behind G8c.

### `scriptengine/retrieve/chronology.py` (R1-c)

- **`_CHRONOLOGY_CUES` (L527)** — now a word-boundary regex
  (`\b(in order|chronolog\w*|timeline|sequences?)\b`). It used to
  substring-match **"sequence" inside "con-sequence-s"**, so G8c
  ("…absorb a curse with no consequences?") walked a 0-beat roster "asking
  for the story in order". `wants_chronology` (L592, applied L599) uses it.
  Latent corpus-wide for `consequence(s)` / `consequently` / `subsequent`.

### `scriptengine/api/main.py` (R1-b)

- **L207** — `route(paths, request.query, subject=request.subject)` threads
  the authored page into the mode decision (previously it reached only the
  qa wide search at L216/L228).
- **L85–89** — `ContextRequest.subject` doc comment names the R1-b
  precedence rule.

### `scriptengine/eval/page_gen.py` (R2 / G10)

- **`write_batch` (L937)** — the batch is written `ensure_ascii=False`
  (L1045) in **`utf-8-sig`** (L1054) and the round-trip is verified before
  `tmp.replace` (L1055, `assert json.loads(tmp.read_text("utf-8-sig")) ==
  batch`). A kanji answer can no longer be garbled on write (the G10 defect:
  UTF-8 read back as cp1252).
- **L898, L957** — the batch readers switched to `utf-8-sig` (BOM-tolerant).

### `scriptengine/eval/questions.py` (R2 / G10)

- **`load_file` (L206, L224)** — reads `utf-8-sig`: strips the BOM when
  present, reads a plain file otherwise. `norm()` already keeps CJK (the
  `\w` fold), so a correct stored kanji now matches end-to-end.

### Tests (regressions, modelled on `TestPandaGaps`)

- **`tests/test_router.py`** — `TestGetoGaps` (G8a/c reach `qa` without a
  hint; G8b/d with `subject=`; the no-hint event keeps its narrative read;
  the story-verb yes/no stays narrative; a matched-partial roster is not a
  set) and `TestShokoGaps` (G9a/c/d reach `qa`; **G9b stays narrative**).
- **`tests/test_chronology.py`** —
  `TestWantsChronology::test_consequence_words_do_not_ask_for_order`.
- **`tests/test_page_gen.py`** —
  `test_cjk_answer_survives_the_batch_round_trip` (a kanji fact round-trips
  the `utf-8-sig` write path).

---

## 2. Before / after route — all 8 gap questions (in-process probe)

`route()` on the patched code, with and without the scorer's `subject` hint.
"Before" is the documented pre-release read (the live misroute each gap was
caught on).

| gap | question | before (pre-R1) | after, no subject | after, `subject=` (scorer) |
|---|---|---|---|---|
| G8a | Was Suguru Geto dependent on his curses in battle? | narrative (87-beat battle bundle, page absent) | `qa` | `qa` |
| G8b | What was the true goal of the Night Parade of a Hundred Demons? | narrative (11-beat event-summary bundle, page absent) | `narrative` | **`qa`** |
| G8c | Under what condition can Suguru Geto absorb a curse with no consequences? | roster (0-beat `Suguru Geto Techniques`, partial, "did not narrow") | `qa` | `qa` |
| G8d | Can Suguru Geto cast Curtain over a weaker sorcerer's barrier? | qa-but-wrong-page (`Curtain` + `Cursed Spirit Manipulation` bundle) | `qa` | `qa` |
| G9a | Does Shoko have an innate cursed technique? | narrative (yes/no fell to the story default) | `qa` | `qa` |
| G9b | What happened to Ijichi and Ino if they had not been treated by Shoko? | narrative (negated conditional) | `narrative` | `narrative` — **OPEN** |
| G9c | Can Shoko teach someone how to use reverse cursed technique? | narrative (capability + discourse marker) | `qa` | `qa` |
| G9d | Is it easier for Shoko to heal herself or others? | narrative (comparative fell to the story default) | `qa` | `qa` |

Notes: G8a, G8c, G9a, G9c, G9d close on R1-a/R1-c/R1-d alone (no hint needed).
**G8b closes only with the R1-b `subject` hint** — without it the event keeps
its narrative read (the shape the eval's story rows rest on, kept by
`TestGetoGaps::test_without_the_hint_the_event_keeps_its_narrative_read`).
**G9b stays narrative** by design (`why: "asks how something happened"`); the
past "what happened to" form guards the eval gold row "What happened to
Nanami during the Shibuya Incident?".

---

## 3. Gate results (verbatim)

| gate | command | result |
|---|---|---|
| 1 | `pytest tests/ -q` | **1059/1059 passed** (≥ 1046) |
| 2 | `python -m scriptengine.cli eval --series jjk` | **24/24 (100%)** |
| 3 | `python -m scriptengine.cli canon-run --series opm` | **8/16 exact, 235/237 canon, 78.5% precision** (at baseline) |

Gate 3 came back exactly at the recorded baseline, so R1-a's yes/no branch is
not over-claiming across series (the mitigation the spec required).

---

## 4. Four re-run scores (live server, started after the edits)

| batch | before R1 | after R1 | expected | status |
|---|---|---|---|---|
| `suguru_geto` | 90/94 | **94/94** | 94/94 | ✓ G8a–d all pass |
| `shoko_ieiri` | 30/34 | **33/34** | 34/34* | G9a/c/d pass; **G9b (OPEN) is the 1 miss** |
| `mei_mei` | 31/31 (Q001 retired) | **32/32** | 32/32 | ✓ kanji 冥冥 now passes (G10) |
| `toge_inumaki` | 84/86 | **85/86** | 84/86 (unchanged) | `051` retrieval gap still OPEN; `060` now passing |

\* The spec's "expect 34/34" assumed G9b would close; G9b is deliberately OPEN
this release, so **33/34 with the single miss = G9b** is the correct result.
`toge_inumaki` improved by one (`060`, beam non-determinism); `051`
("What gave Megumi and Noritoshi a chance against Hanami…", the unique
keywords `ability`/`immobilize` absent from the top-k beam) remains the
documented retrieval gap.

Reports: `jjk-suguru_geto-2026-08-27-0059`, `jjk-shoko_ieiri-2026-08-27-0100`,
`jjk-mei_mei-2026-08-27-0101`, `jjk-toge_inumaki-2026-08-27-0101`.

---

## 5. R3 adversarial probe batch

`_jjk_page_probe_r3.json` — **126 probes** (21 completed characters × 6
forms: yes/no, comparative, negated-conditional, scope-phrase, event-name
scope, possessive-noun bait). Every answer is a verbatim item already proven
on that character's own page batch, so a failure isolates router/retrieval,
not authoring. Scored `jjk-probe_r3-2026-08-27-0055`.

**117/126 passed. 9 failures**, root-caused:

| # | char | form | probe (abridged) | missing answer | root cause | G-n |
|---|---|---|---|---|---|---|
| 1 | Yuji | neg-cond | …if Yuji had not become a sorcerer? | firefighter | counterfactual → narrative, answer never served | **G9b** |
| 2 | Yuta | neg-cond | …if Yuta had not pretended to kill Yuji? | to help protect Yuji from the higher-ups | counterfactual → narrative | **G9b** |
| 3 | Choso | neg-cond | …if Eso & Kechizu had been accepted by humanity? | Eso and Kechizu wouldn't be accepted by humanity | counterfactual → narrative (gold is a weak counterfactual, but routing is the block) | **G9b** |
| 4 | Toji | neg-cond | …to Megumi if Toji had not committed suicide to protect him? | committing suicide to protect him | counterfactual → narrative | **G9b** |
| 5 | Naoya | neg-cond | …if Naoya's domain had been able to detect Maki? | it was unable to detect Maki, leading to Naoya's defeat | counterfactual → narrative | **G9b** |
| 6 | Panda | event-scope | outcome of the fight at the Gachinko Fight Club's ring? | Megumi subdues Kirara. | routed `qa` (correct); outcome sentence below the top-k beam for the location-scoped phrasing (proven in-corpus as `jjk-pg-panda-028`) | **G11 (new)** |
| 7 | Toge | neg-cond | …if Maki had not taken over the battle against Hanami? | Maki takes over the battle. | counterfactual → narrative | **G9b** |
| 8 | Jogo | event-scope | outcome of the fight at the Fukutoshin Line Platform's station? | Satoru Gojo is sealed. Hanami is killed. | routed `qa` (correct); outcome sentence below the beam for the location-scoped phrasing (proven in-corpus in the Jogo batch) | **G11 (new)** |
| 9 | Shoko | neg-cond | …if Shoko had not sutured Gojo's body for Yuta? | She sutured Gojo's body in order for Yuta to transfer himself into it. | counterfactual → narrative | **G9b** |

**7 × G9b** (the open negated-conditional class) + **2 × G11** (new: a
location-scoped battle-outcome phrasing drops the outcome sentence below the
top-k beam — a retrieval-quality / G5-family gap, not routing).

---

## 6. Left OPEN (one-line fix plan each)

- **G9b — negated conditional / counterfactual (router).** 7 R3 probes + the
  shoko `020` miss. Fix plan: a "would have happened if" / "happened to … if"
  counterfactual discriminator in `_is_interrogative` that routes the
  *hypothetical* form to `qa` while leaving the past-factual "What happened
  to Nanami…" (the eval gold row) on narrative; gate on `eval jjk` 24/24 +
  opm canon. Highest regression risk in the set — deferred past R1.
- **G5 / R4 — retrieval quality (buried quote-style facts below the top-50).**
  Pre-existing (the toji/aoi/yuta residuals, §11 of the handoff). Fix plan:
  a retrieval-quality pass (reranker depth / quote-aware chunking / query
  expansion), not rephrasing.
- **G11 — location-scoped battle outcome (new, R3; G5 family).** Fix plan:
  fold the battle-outcome + location into the query focus (or a
  battle-outcome-aware passage) so "…outcome of the fight at X's ring?"
  retrieves the outcome sentence; one of the R4 retrieval-quality items.
- **toge_inumaki `051`** — "What gave Megumi and Noritoshi a chance against
  Hanami" (`ability`/`immobilize` absent from the beam). Same G5/G11
  retrieval-quality family; documented in `jjk-toge_inumaki-2026-08-27-0101`.

**Closed and gated this release:** G8a, G8b, G8c, G8d, G9a, G9c, G9d, G10.