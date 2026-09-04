# Checkpoint — stopped before the Hybrid roster build

**Status: PAUSED by decision, 2026-09-04.** Nothing is mid-flight. Every gate is
green and the tree is in a consistent state. This file is the resume point.

## TODO, in order

- [ ] **1. Commit the work.** It is all uncommitted (see *Risk* below). Decide
      this first — everything else can wait, this cannot.
- [ ] **2. Fix Finding B (proposed G28)** — the auto-router sends "which
      characters appear in X?" to `narrative` on non-chapter pages, which
      under-enumerates (Aizo 1/12, Ao no Sumika 4/12 under `auto`; both 12/12
      under `qa`). Do this **before or with** the roster build: if the natural
      door still narrates instead of enumerating, declaring 550 rosters will not
      make it answer correctly. Router code → propose-and-approve.
- [ ] **3. Hybrid roster build** — ~550 declared-member entries in
      `series/jjk/overrides.yaml` for `Characters in Order of Appearance` +
      `Battles & Events` across 304 chapter pages. `Locations` + `Jujutsu` are
      **waived** by decision (State 122). `overrides.yaml` is forbidden to the
      execution tier → draft the delta, stop for sign-off.
- [ ] **4. Chapter narrative prose** — `Summary` + `Plot Details` at ~1.5
      questions/section, ≈600–900 questions for the tranche. Only after step 3.
- [ ] **5. Outstanding gate: `canon-run --series opm`** (expect 10/16 exact ·
      236/236 canon · 79.0%). This is the last leg of the gate triple for the
      `span-recall` addition; `pytest` and `eval` are done.
- [ ] **6. Re-index the other series** to collect the Scroll-box fix — see
      *Cross-series* below. Cheap, and it is the concrete test of the standing
      open question about OPM's 1,039 and Bleach's 1,171 unreachable lines.
- [ ] **7. Decide the fate of `series/jjk/.backup_20260904_074609`** (186 MB).
      Keep until step 1 is done and the index has been exercised for a while.

## Risk: everything is uncommitted

Branch `character-scoped-questions`, last commit `d531329`. Uncommitted:

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
| `pytest tests/ -q` | **1,122 passed / 0 failed** | with the `:8000` API **stopped**. With it running, expect 5 `torch.OutOfMemoryError` + the pre-existing `test_page_sweep_command` = 1,117/5–6. Not regressions. |
| `eval --series jjk` | **24/24** | |
| `span-recall --series jjk` | **48,570/48,572, exit 2** | the two known `Chapter 239 / References` misses. Exit 2 is expected here, not a failure. |
| `canon-run --series opm` | **not run** | outstanding, see TODO 5 |
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

## Open findings

- **Finding A** — the `roster` door returns a generic 40-member fallback for
  pages with no declared roster (0/40 overlap on Ao no Sumika). Expected; TODO 3
  closes it. Not a bug.
- **Finding B (proposed G28)** — router mode-selection gap, see TODO 2.
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
