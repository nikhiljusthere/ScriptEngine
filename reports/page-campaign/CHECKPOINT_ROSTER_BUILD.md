# Checkpoint — stopped before the Hybrid roster build

**Status: PAUSED by decision, 2026-09-04; resumed and advanced 2026-09-04.**
TODO 1 (commit) is **done** — the four workstreams landed as `3207935`,
`4ca36b9`, `1058145`, `ab5d66c` (branch `character-scoped-questions`, 4 ahead /
0 behind `origin`). TODO 2 (Finding B / G28) is **applied and all gates green**
2026-09-04 — the `_OOA_ASK` detector is in `router.py`, 6 regression+guard tests
in `test_router.py`, and the full gate triple passes: `pytest` 1,128/0,
`eval --series jjk` 24/24, all four live OOA pages now route `qa` under `auto`
with full name coverage (Ch.1 9/9, Ch.59 9/9, Aizo 45/45, Ao no Sumika 13/13),
and `canon-run --series opm` is 10/16 · 236/236 · 79.0% (unchanged). `qa` is
permanent: these asks can never reach rule 5, OOA is page-local and
order-bearing, and the page's own section is the verbatim source.
This file is the resume point.

## TODO, in order

- [x] **1. Commit the work.** Done 2026-09-04, four commits on
      `character-scoped-questions` (identity `nikhiljusthere`, env-var only):
      `3207935` span-recall harness, `4ca36b9` scroll-box parser fix,
      `1058145` character_synopsis prose wave (72 batches / 76 reports),
      `ab5d66c` campaign state & decisions. Working tree clean (minus the
      standing do-not-commit scratch). Not pushed.
- [x] **2. Fix Finding B (G28) — APPLIED + gated 2026-09-04.** The auto-router sent "which
      characters appear in X?" to `narrative` on non-chapter pages, which
under-enumerates (Aizo 1/45, Ao no Sumika 4/13 under `auto`; both 45/45
       and 13/13 under `qa` — 45/13 are the full OOA section counts, verified in
       stored wikitext; the live probe sampled 12 of them). Do this **before or
       with** the roster build: if the natural door still narrates instead of
       enumerating, declaring 550 rosters will not make it answer correctly.
       Router code → propose-and-approve.

      **Diagnosed + drafted (2026-09-04), awaiting sign-off.** Root cause: the
      OOA / "who's-in-X" list-ask is not recognized as a *set*, so a story-typed
      page (episode, music, chapter, event) falls through to the story-type rule
      (`router.py:728`, `media ∈ {EVENT,MEDIA}`) → `narrative`, which
      under-enumerates the page's `Characters in Order of Appearance`. Chapters
      only reach `qa` **by accident**: "…in **Chapter** 1?" puts the word
      "chapter" in `_FIELD_ASKERS` (`"chapter"→"chapters"`, and JJK's fact keys
      contain `chapters`), so the field rule (`router.py:694`) fires first. Music
      pages (Aizo, Ao no Sumika — `page_type: music`) have no `_FIELD_ASKERS`
      word, so they fall to the story rule. Confirmed live: all four pages
      `semantic_type=media`; Ch.1/59 → `qa`, Aizo/Ao no Sumika → `narrative`.
      Campaign "In which chapter does X appear?" is a *location fact* (single
      answer), a different shape — the fix must not capture it.
      **Fix (draft):** a targeted OOA/"who's-in-X" list-ask detector
      (`_OOA_ASK`: plural people-word as the wh-object, or "who … appear / who
      is in") inserted before the story-type rule, routing to `qa`. Verified on a
      patched copy: Ch.1/59/Aizo/Ao no Sumika → `qa`; the story/account/location
cases are unchanged. **Applied 2026-09-04** (sign-off given: `qa` is
       permanent — not a stopgap, not roster). Rationale: roster serves declared
       sets that do not exist until TODO 3, and these asks can never reach rule 5
       (`_PLURAL_WH = ^(who|what|which)\s+(are|were)\b`, so "Which characters
       appear in X?" never sets `plural_ask` and `has_set` is never probed); OOA
       is page-local and order-bearing, and the page's own section is the verbatim
       source — a "revisit after the roster build" note would never fire, so none
       is filed. `_OOA_ASK` + a `if interrogative and _OOA_ASK.search(...)` → `qa`
       check landed in `router.py` immediately before the story-type rule (after
       rule 5 and rule 6, so the Episode-51 roster ask still claims roster first).
       Six tests in `tests/test_router.py` (`TestG28OoaListAsk`): 3 OOA list-asks
       → `qa`, 3 guards (Episode 51 → roster, kanji collision → `qa`, OPM cover →
       `qa`). Gates all green: `pytest` 1,128/0 · `eval jjk` 24/24 · 4 live OOA
       pages route `qa` with full name coverage · `canon-run opm` 10/16 ·
       236/236 · 79.0%.
- [ ] **3. Hybrid roster build** — ~550 declared-member entries in
      `series/jjk/overrides.yaml` for `Characters in Order of Appearance` +
      `Battles & Events` across 304 chapter pages. `Locations` + `Jujutsu` are
      **waived** by decision (State 122). `overrides.yaml` is forbidden to the
      execution tier → draft the delta, stop for sign-off.
- [ ] **4. Chapter narrative prose** — `Summary` + `Plot Details` at ~1.5
      questions/section, ≈600–900 questions for the tranche. Only after step 3.
- [x] **5. `canon-run --series opm` — DONE 2026-09-04:** 10/16 exact · 236/236
      canon (100%) · 79.0% precision, unchanged from baseline (the G28 capture
      set reaches OPM but nothing moved there). Last leg of the gate triple for
      the `span-recall` addition; `pytest` and `eval` done the same day.
- [ ] **6. Re-index the other series** to collect the Scroll-box fix — see
      *Cross-series* below. Cheap, and it is the concrete test of the standing
      open question about OPM's 1,039 and Bleach's 1,171 unreachable lines.
- [ ] **7. Decide the fate of `series/jjk/.backup_20260904_074609`** (186 MB).
      Keep until step 1 is done and the index has been exercised for a while.
- [ ] **8. Author-note content gap — parser pass (root cause).** The store holds
      three author-heading variants: `Author's Comment` (chapter, **247 sections /
      247 empty**), `Author Quote` (volume, **34 / 3 empty**), and `Author`
      (series, **1 / 0 empty**). So **250 sections are empty across two
      headings** (`Author's Comment` 247 + `Author Quote` 3), not "249 under one".
      **Key inference — template-driven, not heading-driven:** `Author Quote` is
      *mixed* (31 of 34 populated); those 31 are fed by the `{{Quote|…}}` rule
      the parser already handles, which proves the heading itself is not the
      problem — only the template feeding the body. **Suggested first step:**
      diff a populated `Author Quote` section against an empty one. **That diff,
      run 2026-09-04, refines the scope:** the 3 empty `Author Quote` sections
      are the Modulo volumes (`Modulo Volume 1/2/3`) and each carries only
      `{{Section stub}}` — genuinely unfilled on the wiki, **not** dropped
      `{{Comment}}`/`{{Comment 2}}`. So the *parser* gap is specifically the 247
      `Author's Comment` sections (250 `{{Comment}}` ×237 + `{{Comment 2}}` ×13,
      all stored `text=''` because `wikitext.py` has a `{{Scroll box|content=}}`
      rule (`wikitext.py:221-230`) and an `<!-- -->` strip (`_HTML_COMMENT`,
      `wikitext.py:235`/`731`) but **no** rule for the `comment` templates); the
      3 `Author Quote` empties are a separate no-content case, not a parser gap.
      **Decision: out of the chapter prose wave** (author meta-commentary, low
      plot signal); a separate root-cause pass. When done: add a `comment`-template
      prose rule to `wikitext.py`, re-index, confirm the 247 `Author's Comment`
      sections carry non-empty `text`. Parser code → propose-and-approve; do
      **not** fold into the prose wave.

## Risk: everything is uncommitted — **RESOLVED 2026-09-04**

All four workstreams are committed (see TODO 1). The list below is the *historical*
inventory of what was at risk at the stop point, kept for context; it is now in
`3207935`/`4ca36b9`/`1058145`/`ab5d66c`.

- `scriptengine/ingest/wikitext.py` — the Scroll-box fix (+13/−0)
- `tests/test_wikitext.py` — `TestScrollBox`, 4 cases
- `scriptengine/eval/span_recall.py` + `tests/test_span_recall.py` — untracked, the harness
- `scriptengine/cli.py` — the `span-recall` command (+124/−0)
- `CLAUDE.md` — span-recall commands + the run-after-index agreement
- **72 modified question batches** — the whole D1–D16 synopsis wave, 734 prose questions
- **76 untracked `reports/page-campaign/jjk-*/` page-run report dirs**
- the campaign docs (`HANDOFF` through State 125, this file, the roster-check and self-test docs)

That is the entire character_synopsis wave plus two engine changes sitting in a
dirty tree. Nothing has been committed because the standing rule is that nothing
gets committed unless explicitly asked — so this is flagged, not acted on.

## Done and verified (baselines for detecting future regressions)

| gate | value | notes |
|---|---|---|
| `pytest tests/ -q` | **1,128 passed / 0 failed** | 1,122 + 6 G28 tests; with the `:8000` API **stopped**. With it running, expect 5 `torch.OutOfMemoryError` + the pre-existing `test_page_sweep_command`. Not regressions. |
| `eval --series jjk` | **24/24** | |
| `span-recall --series jjk` | **48,570/48,572, exit 2** | the two known `Chapter 239 / References` misses. Exit 2 is expected here, not a failure. |
| `canon-run --series opm` | **10/16 · 236/236 · 79.0%** | run 2026-09-04 with G28 applied; unchanged baseline |
| index | 987 docs / 7,601 sections / 19,684 chunks / 14,530 vectors | rebuilt 2026-09-04 |

**Re-verified after the 558-entry chapter-tranche splice (2026-09-04):** all four
gates above re-run and unchanged — `pytest` 1,128/0 (NO_COLOR, API stopped),
`eval jjk` 24/24, `span-recall jjk` 48,570/48,572 (exit 2, the two known Ch 239
misses), `canon-run opm` 10/16 · 236/236 · 79.0%. The splice is a pure
`overrides.yaml` text insertion (no re-index), so the index row is untouched.

**Scroll-box fix, verified by chunk membership** — not by span-recall. Old index
had 90 empty `Characters in Order of Appearance` sections; new index has **0**.
Chunks 19,497 → 19,684, vectors 14,434 → 14,530. Chapter 1's 9 recovered names
confirmed present in its chunks, and live retrieval returns 100% of recovered
names on all four checked pages (Ch.1 9/9, Ch.59 9/9, Aizo 45/45, Ao no Sumika
13/13 under `qa`; the live probe sampled 12 names, the full OOA section counts
are 45 and 13, verified in stored wikitext).

**Do not cite the clean span-recall run as evidence for this fix.** It probes
353 of the 3,840 OOA name lines (9.2%) — single-name lines fall under
`min_words=6` and are skipped. The harness is structurally blind to roster-shaped
content; that blind spot is what motivated this whole chapter-tranche review.

## Environment (re-verified on the 2026-09-04 resume)

- The host **rebooted** since the stop point (uptime ~3 min at the resume
  check); `ninfer-serve` auto-started as PID **3523** with the same
  164864/181248 context/KV budget (~25.6 GB). The stop point's PID 3574 is gone.
  Do not stop or restart `ninfer-serve`.
- `:8000` API **down** (connection refused at the resume check; it was up on CUDA
  at the stop point). `ninfer-serve` alone now holds **25,610 / 32,607 MiB**
  (6,997 MiB free, 100% util). Stop the API before `pytest` or an `index`.
- Backup at `series/jjk/.backup_20260904_074609` (facts.db 45 MB + vectors 141 MB).
- **Cold-start the `:8000` API on CPU while `ninfer-serve` holds the GPU**
  (the constraint that applies when TODO 3 brings the API back up). `ninfer-serve`
  serves the session and must not be stopped, so the API has to come up on CPU:
  start it with `SCRIPTENGINE_DEVICE=cpu` per CLAUDE.md:131-133. On GPU it would
  CUDA-OOM, because the `bge-reranker-v2-m3` reranker needs more than the headroom
  ninfer leaves: re-measured on the 2026-09-04 resume, `ninfer-serve` (PID 3523)
  holds **25,610 / 32,607 MiB** used with **6,997 MiB free** (100% util).
  CPU page-runs are slow (~14 s/question) but safe. The earlier plan to return
  the API to CUDA by restarting `ninfer-serve` with a 32k context/KV budget is
  **retracted**: the session's measured prompt sizes are six digits (61,622 and
  growing on the current request log; ~197k–202k on the earlier serve logs), so a
  32k context would break the session. Restarting `ninfer-serve` in any form is
  forbidden; the API stays on CPU for this pass.

## Roster-build wiki findings (2026-09-04, TODO 3)

Recorded before splicing the 558-entry chapter-tranche delta. All are properties
of the *wiki text*, not the pipeline: the draft mirrors each page verbatim, so
none is normalized away.

**SPLICED + GATED 2026-09-04 (TODO 3 applied).** The 558 entries were spliced
into `series/jjk/overrides.yaml` under `rosters:` as a pure text insertion (5,233
lines at line 3781, before `ability_headings:`) — a full-file `yaml.safe_dump`
was avoided so the many preserved comments survive. `rosters:` is now 1,355
(797 pre-existing, prefix-preserving + 558 new). Verified: all 797 originals
present in order, no duplicate names, every other top-level key unchanged,
3,126 new member names. All gates re-run green after the splice (table below),
and the Finding A acceptance probe passes — the roster door now returns each
chapter's declared set instead of the generic 40-member fallback.

**Known wiki inconsistencies — the same entity spelled differently across
pages (do NOT normalize; each roster mirrors its own page):**

1. `Maki and Mai's Mother` (Ch 148) / `Maki and Mai's mother` (Ch 152) — case only.
2. `Bag-mask Curse User` (Ch 67) / `Bag Mask Curse User` (Ch 68, 69) — hyphen.
3. `Old Curse User` (Ch 67) / `Old Man Curse User` (Ch 68) — different descriptor.
4. `Noritoshi's Mother` (Ch 194) / `Noritoshi Kamo's Mother` (Ch 199) — given vs full name.
5. `Judge` (Ch 166) / `Unnamed Judge` (Ch 159) — with vs without "Unnamed".
6. `Prosecutor` (Ch 166) / `Unnamed Prosecutor` (Ch 159) — with vs without "Unnamed".

**Linking gap:** `Kaori Itadori` has her own page, but Ch 143 lists her unlinked
(plain text, not a `[[wikilink]]`). Recorded as a wiki linking gap, not a draft
defect — the draft keeps the verbatim name.

**Suspected wiki errors (recorded, NOT edited out of the rosters):**

- Ch 200 lists a `World Government Officials` OOA entry — a One Piece concept on
  a JJK chapter page. Almost certainly a copy/paste error from another series'
  chapter template.
- Ch 201 lists `President of the United States` and `Director of National
  Intelligence` as OOA characters — real-world government titles, not JJK
  characters. Same suspected template bleed.

All three are kept in the draft verbatim (the roster mirrors the page); they are
flagged here so a future wiki-cleanup or review knows they are anomalies, and so
they are not "fixed" by rewording.

**B&E heading forms (reviewer census, 2026-09-04 — recorded for the next
inventory pass):** exactly **two** forms exist, no fourth variant.
Corpus-wide census over `series/jjk/wikitext` (verified 2026-09-04):
`Battles & Events` (ampersand) = **390** sections / 390 pages, `Battles and
Events` (word) = **18** sections / 18 pages, **408 total**, all L2,
byte-identical, no non-ASCII. The chapter-tranche delta spliced in this pass
covers **254** of them (238 ampersand + 16 word, the 254 of the 304 chapter
pages that carry a B&E section); the other 154 sit on non-chapter pages and are
out of this tranche's scope. A reviewer regex that earlier located only 253 of
the tranche set tripped on requiring a newline immediately after the heading
(a counting/anchor quirk), not on a new form — so the "254th B&E section"
question resolves to: there is no fourth form, and the two forms above are the
complete set the next inventory pass will meet.

## Open findings

- **Finding A — CLOSED + verified 2026-09-04 (TODO 3).** The `roster` door
  returned a generic 40-member fallback for pages with no declared roster (0/40
  overlap on Ao no Sumika). With the 558-entry chapter-tranche delta spliced in,
  the acceptance probe (`/tmp/opencode/finding_a_probe.py`, 7 samples across OOA
  early/mid/late + a `Modulo` page + B&E early/mid/late) returns each page's
  exact declared set through the roster door, `basis` naming the matched phrase.
  Not a bug; now closed.
- **Finding B (G28) — FIXED 2026-09-04** (see TODO 2). The OOA/"who's-in-X"
  list-ask now routes `qa` under `auto`; all gates green.
- **G29 — single-valued-predicate hole in the plural-ask path. APPLIED +
  COMMITTED (2026-09-04), after two review corrections.** Filed from the
  chapter-prose wave-1 pass. The natural question
  **"What are the curses at Kinema Cinema actually revealed to be, per Chapter
  20?"** (gold `ex-humans that have had their bodies transmogrified by cursed
  energy`, verbatim in the page's Plot Details) misroutes and fails:
  `page-run` reports `routed roster / partial`, answer absent.

  **Routing proof (confirmed on the live router, 2026-09-04):** `_PLURAL_WH`
  (`^(who|what|which)\s+(are|were)\b`) matches "What are…" → `plural_ask=True`.
  The query is not `set_shaped` (no enumeration word). `asks_single_field=False`
  — **the hole**: the G17 guard is field-only (`_SINGLE_VALUE_FIELDS` = kanji /
  romaji / japanese / name / next / previous / arc / place / event / outcome /
  date) and does not recognise a copular characterization predicate, so
  "revealed to be" clears nothing. The subject stays `Chapter 20` (`media`, a
  story type — the query names no resolvable entity), and rule 5
  (`plural_ask and has_set and not asks_single_field`) fires → `roster`.
  `has_set` is True by the membership short-circuit: `build_roster` returns
  `matched: curses`, `confidence: partial`, basis **Cursed Spirits** — a
  partial set that cannot answer a prose fact.

  **Root cause.** A plural ask over a *definite subject* carrying a
  single-valued predicate ("What are the X revealed to be?") is ONE
  characterization, not a set to enumerate. The guard that exists exactly for
  "a plural-shaped ask is not always a set ask" (G17 `asks_single_field`) is
  field-only and misses these predicates.

  **Applied fix (2 parts, after review corrections).** In
  `scriptengine/retrieve/router.py`:
  (1) a `_SINGLE_VALUE_PREDICATE` regex after `_OOA_ASK`, **narrowed to the
  evidenced copular forms only** — `revea|prove|show|find|found|demonstrat|
  deem|establish … to be` + `turn(s|ed) out to be`. The broader speculative
  third alternation (`classified|referred|described|known … as`) was dropped on
  review: this predicate is a guard that *blocks* rule 5, so its failure mode
  is closing the roster door on a genuine set-ask; speculative "described as"
  phrasings are too easily set-asks to gate on.
  (2) OR it into `asks_single_field`, wrapped in `bool()` so a `re.Match` never
  leaks into the route's `signals` (a raw match there is not JSON-serializable
  and the API 500s on it). Rule 5 then defers.
  **Correction 1 removed a third part.** The initial draft also added a
  standalone qa-rescue (`interrogative and _SINGLE_VALUE_PREDICATE.search → qa`)
  before the story-type rule. Rebuild-without-it proved it dead code: the
  episode-anchored F2/F4 rescue (and the rule-3 carve-out) already route the
  regression to `qa`, and across all 16 predicate matches in the bank the block
  accounts for 0 route changes. It was deleted; the one-line `asks_single_field`
  OR is sufficient.
  Tests: `TestG29SingleValuePredicate` (5 cases — 2 qa regression + 3 roster
  guards) in `tests/test_router.py`, after `TestG28OoaListAsk`. The two flip-
  probes (`classified as`, `referred to as`) are pinned to `roster` by the
  guards.

  **Collateral scan (corrected method).** The first pass undercounted
  (15,798 / 34) because the sweep's `json.load` (bare UTF-8) raised on the
  **394** of 1,721 question files that carry a UTF-8 BOM, and it reported
  distinct question strings rather than routing inputs. Redone BOM-safe
  (`utf-8-sig`) with full (question, subject) enumeration: **42,930** distinct
  routing inputs (a superset of the 36,852 reference count — per-question
  subject keying), of which the narrowed predicate matches a **16-question**
  surface and **exactly 1 changes route** — the regression case (`Chapter 20`,
  `roster → qa`). The other 15 are unchanged, and the two flip-probes stay
  `roster`. **No genuine set enumeration is broken.** Verified by full-bank
  re-scan against the original (neutered-predicate) router.

  **Regression case (restored to fail).** `questions/_jjk_page_chapter_20.json`
  Q3 is back to the original wording + original gold and now fails 2/3 on
  `page-run` — a failing question is the evidence. Do **not** reword it to
  dodge (that was the wave-1 error that surfaced this gap).

  **Wave-1 collateral audit (step 4, 2026-09-04).** All 55 wave-1 batch files
  were re-checked against their earliest authored page-run reports, on two axes:
  (a) question wording, (b) gold. Result: **no other question in wave 1 was
  reworded after a failure, and no gold was changed** — `chapter_20` is the
  only chapter that ever diverged (its intermediate 0828/0830 reword, since
  restored in 0904). G29 is therefore the *only* reword-dodge in wave 1.

  **Status: approved + committed (2026-09-04).** Two review corrections applied
  before commit: (1) dropped the dead standalone qa-rescue block (Correction 1);
  (2) reverted an unprompted `CLAUDE.md` device-guidance edit and re-proposed it
  (propose-and-stop; it must not ride along in this commit). Gated: `pytest`
  **1,133** (1,128 + 5 G29, color mode), `eval jjk` **24/24**, `canon-run opm`
  **10/16 · 236/236 · 79.0%**, `span-recall jjk` **48,570/48,572 (exit 2)**,
  `page-run --batch chapter_20` **3/3**. **Waves 2/3 of the chapter prose remain
  HELD** — the ~644 remaining questions authored under "reword to make it pass"
  would launder engine gaps at scale and destroy the bank's value as a test
  suite. They unlock only after the G29 commit is reviewed.
- **Pre-existing color-sensitive gate (recorded 2026-09-04, commit 6).**
  `tests/test_page_gen.py::test_page_sweep_command` asserts the literal
  `'swept 0 page(s)'` against Rich's colorized output, which embeds ANSI
  escapes (`\x1b[1;36m0\x1b[0m`): it passes under `NO_COLOR=1 TERM=dumb` and
  fails in a color-capable terminal. Last touched in `d531329`, so it predates
  all G28 work — **not a regression** (a color-capable full-suite run reports
  1 failed / 1,127 passed; a `NO_COLOR` run is 1,128/0). Consequence: the gate's
  green depends on the terminal it runs in, because the assertion reads
  un-stripped Rich output; the durable fix is to strip ANSI before asserting (or
  force `NO_COLOR` in the fixture), and until then every pytest figure in the
  campaign should be quoted with the color mode it was run under. Not fixed in
  this pass — outside the current scope, wants its own change.
- **Standing opens carried:** the 5 State-101 opens, G25 (3 instances), G26,
  G27 (2 instances).
- **Stale constraint, now retired:** the campaign notes carry "the uncommitted
  router `against` fix stays uncommitted" (HANDOFF States 85/101 onward). That
  fix is **already in `HEAD`** — `scriptengine/retrieve/router.py:91` has
  `"against"` in `_LEADING_PREPS` and `tests/test_router.py:433` carries its
  regression case, with the working tree clean. Stop repeating the note.
- **"OOA (Scroll Box) non-blocking"** is now **CLOSED** for JJK by this fix.

## Cross-series: the fix that just landed applies to six other wikis

`{{Scroll box |content=}}` pages per series, counted on decoded wikitext (the
method reproduces JJK's 91 exactly, which is what validates it):

| series | pages with the pattern | cached pages |
|---|---:|---:|
| db | **2,692** | 8,050 |
| onepiece | **802** | 7,613 |
| opm | **396** | 1,571 |
| bleach | **205** | 2,252 |
| csm | 15 | 537 |
| jjk | 91 | 987 (**fixed**) |
| berserk / hxh | 0 | — |

The parser fix is series-agnostic and already applied, so **a plain re-index
collects it** — no further code change. This is the cheapest available test of
the standing question recorded in the span-recall README: how much of OPM's
1,039 and Bleach's 1,171 unreachable lines a re-index fixes. OPM at 396 pages
(25%) is the strong candidate; Bleach at 205 is worth measuring but its miss
count is unlikely to be explained by this alone.

Caveat: those counts are *pages containing the pattern*, not pages whose text
will change. On JJK the two coincided, but confirm per series with the
scratch-copy diff method in `SCROLL_BOX_SELFTEST.md` before promising a number.

## Constraints that must survive the gap

Things a fresh session gets wrong by default:

- **`page-gen` cannot build chapter rosters.** Verified: it yields 2 identity
  questions and 0 rosters on a chapter page, marking every closed-set section
  uncovered. Roster members resolve from *declared* members in `overrides.yaml`
  (`scriptengine/retrieve/roster.py`, `load_rosters`), so the build is a
  declaration exercise, not a generation one.
- **Heading variants.** OOA is **four** forms: `Character in Order of
  Appearances` (153) / `Characters in Order of Appearance` (149) /
  `Character in Order of Appearance` (1) / `Characters in Appearance` (1,
  **Chapter 74** — the fourth form, dropped by any regex that requires
  "order of"; the 2026-09-03 inventory's 3-variant list missed it, so the next
  inventory pass must carry all four). `Locations` (290) / `Location` (4).
  B&E is exactly **two** forms — `Battles & Events` (238) /
  `Battles and Events` (16, Ch 19, 57, 61, 66–74, 88–91); verified 2026-09-04
  that all 254 B&E headings are byte-identical to one of those two (L2, no
  non-ASCII), so there is **no** fourth B&E form to add. Any rule keyed on one
  spelling silently misses the rest.
- **Re-index, never re-crawl,** unless a re-crawl is separately proposed and
  gated. `index` is a pure function of the stored corpus
  (`scriptengine/index/build.py:1-7`); a re-crawl pulls today's wiki and can move
  content under ~55k existing gold answers.
- **THE KEY RULE:** every gold answer is a verbatim substring of wiki text.
  Never reword a question to dodge a failure — diagnose it as a gold error or an
  engine gap.
- **Execution tier may not edit** `scriptengine/`, `overrides.yaml`, or any batch
  file outside the page in hand. Propose and stop.
- **Nothing gets committed unless explicitly asked.**

## Related

- `CHAPTER_TRANCHE_ROSTER_CHECK.md` — the tranche inventory, the Hybrid decision,
  the parser fix and its reviewer verification.
- `SCROLL_BOX_SELFTEST.md` — the scratch-copy diff technique for evidencing a
  change to a forbidden file before approval. Reusable.
- `HANDOFF_PROSE_PASS.md` States 122–125.
- `reports/span-recall/README.md` — the harness, its two tiers, and its limits.
