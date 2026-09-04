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
      under-enumerates (Aizo 1/12, Ao no Sumika 4/12 under `auto`; both 12/12
      under `qa`). Do this **before or with** the roster build: if the natural
      door still narrates instead of enumerating, declaring 550 rosters will not
      make it answer correctly. Router code → propose-and-approve.

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

**Scroll-box fix, verified by chunk membership** — not by span-recall. Old index
had 90 empty `Characters in Order of Appearance` sections; new index has **0**.
Chunks 19,497 → 19,684, vectors 14,434 → 14,530. Chapter 1's 9 recovered names
confirmed present in its chunks, and live retrieval returns 100% of recovered
names on all four checked pages (Ch.1 9/9, Ch.59 9/9, Aizo 12/12, Ao no Sumika
12/12 under `qa`).

**Do not cite the clean span-recall run as evidence for this fix.** It probes
353 of the 3,840 OOA name lines (9.2%) — single-name lines fall under
`min_words=6` and are skipped. The harness is structurally blind to roster-shaped
content; that blind spot is what motivated this whole chapter-tranche review.

## Environment at the stop point

- `:8000` API **up** on CUDA. `ninfer-serve` PID 3574, 25.5 GB, untouched.
- GPU was ~29.8/32.6 GB with both up. Stop the API before `pytest` or an `index`.
- Backup at `series/jjk/.backup_20260904_074609` (facts.db 45 MB + vectors 141 MB).
- **Cold-start the `:8000` API on CPU while `ninfer-serve` holds the GPU**
  (the constraint that applies when TODO 3 brings the API back up). `ninfer-serve`
  serves the session and must not be stopped, so the API has to come up on CPU:
  start it with `SCRIPTENGINE_DEVICE=cpu` per CLAUDE.md:131-133. On GPU it would
  CUDA-OOM, because the `bge-reranker-v2-m3` reranker needs more than the headroom
  ninfer leaves: measured 2026-09-04, `ninfer-serve` (PID 3881) holds **26,535 /
  32,607 MiB** used with only **5,568 MiB free** (100% util). CPU page-runs are
  slow (~14 s/question) but safe; the API returns to CUDA only after ninfer's
  context/KV budget is shrunk (the pending restart) or the GPU is otherwise freed.

## Open findings

- **Finding A** — the `roster` door returns a generic 40-member fallback for
  pages with no declared roster (0/40 overlap on Ao no Sumika). Expected; TODO 3
  closes it. Not a bug.
- **Finding B (G28) — FIXED 2026-09-04** (see TODO 2). The OOA/"who's-in-X"
  list-ask now routes `qa` under `auto`; all gates green.
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
- **Heading variants.** `Character in Order of Appearances` (153) /
  `Characters in Order of Appearance` (149) / `Character in Order of Appearance`
  (1); `Locations` (290) / `Location` (4); `Battles & Events` (238) /
  `Battles and Events` (16). Any rule keyed on one spelling silently misses the
  rest.
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
