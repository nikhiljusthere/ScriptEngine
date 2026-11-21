# JJK events re-extraction — receipt (2026-09-29)

For the council (P5). Read against the database, not against this file. Every
number below is reproducible from the files named here.

## What was done, in order

1. **Independent verification** of the findings report: `reports/jjk/VERIFY_2026-09-29.md`.
2. **Four gates before** (pre-change store, `:8000` on CUDA): pytest 1,451 +
   2 xpassed + 2 known env failures; eval jjk 31/31; span-recall 48,572/48,572 +
   probe 398/400; canon opm 10/16 · 236/236 · 79.0%. Receipts `/tmp/jjk100/gates_pre/`.
3. **Engine fixes** (generic, tested, per-wiki behaviour only through overrides):
   - resolver: an unlinked exact title yields to the one entity the page points
     at; a subpage names its base; a name part resolves through the page's
     links or the page itself (`name_pool`); a title-word tie-break;
     declared `events: participant_exclude_types:`;
   - extraction-time counted drops: `self_object` (G3), `shape` (G4, inert
     unless `events: place_types:` is declared), `fanout` (a clause paired
     with more than 6 people it does not name);
   - teacher trace `SCRIPTENGINE_EVENTS_TRACE` (exact window + raw answer per
     call, incl. empty answers);
   - `gate.py`: the continuity/coverage gate no longer crashes on the engine's
     own ambiguous-end (NULL node) and lead-row (NULL section) forms;
   - `re_resolve_participants` uses the extraction's own pool.
   Tests: `tests/test_events_resolver_pointing.py` (new), `tests/test_events_tgap.py` (+5).
4. **JJK overrides** (`series/jjk/overrides.yaml` → `events:`): outcome verbs
   `defeated/escaped/captured` (as Marvel/MCU), `place_types`, work page types
   excluded as participants.
5. **Prompt** `events-2026-09-29.7` → **`.9`** (verb definitions only; see A/B below).
6. **Re-extraction**, `--scope all --refresh`, 966 pages / 3,657 sections, trace
   on; failures retried at concurrency 1 → **966/966, 0 stale rows**.
7. **events-verify** (27B yes/no) on every row.

## The corpus now (`series/jjk/facts.db`)

| | old (`09-05.2`) | `.7` pass (superseded) | **`.9` (live)** |
|---|---:|---:|---:|
| rows | 2,748 | 7,264 | **8,491** |
| pages with rows | 508 | 834 | **869** |
| sections with rows | 838 | 1,727 | **1,851** |
| in-scope sections read | ~22% | 3,657/3,657 | **3,657/3,657** |
| G1 verbatim / G2 verb / G3 self / G4 place / G7 stale | 0/0/807/735/— | 0/0/0/0/0 | **0/0/0/0/0** |
| misfiled Akari→song / Ryu→shikigami | 35 | 0 | **0** |
| `verified = 1` | — | 2,459 (34%) | **3,830 (45%)** |
| judged precision | not judged | ≈67% (n=300, weighted) | **77.3% ± 6.7 (n=150, uniform)** |
| precision of the `verified = 1` tier | — | 89.9% (n=99) | **93.0% (n=71)** |

Old-corpus G4 counted with organizations as a pass (see VERIFY §2.4).

## Judged sets (judge A = Claude, blind to `verified`/arm; judge B NOT yet done)

- `reports/jjk/judged/sample_300.json` + `judge_A_batch1..6.json` — `.7`, 300 rows
  stratified by verb. 192/300; error classes: verb semantics 77, entity 17,
  not-an-event 10.
- `reports/jjk/judged/ab_p7_p8_150.json` + `ab_judge_A_1..3.json` — blind A/B on the
  same 100 pilot pages: `.7` 42/75 (56.0%) vs `.8` 54/75 (72.0%), z≈2.0.
- `reports/jjk/judged/final_p9_150.json` + `final_judge_A_1..3.json` — `.9` live
  corpus, 150 uniform rows: 116/150.

**One judge is not the bar.** The plan requires two independent judges and an
adjudication pass (κ reported). Judge B has to be the owner or a different
model family. The sheets carry the context each row was judged on and hide the
verifier's verdict, so a second judge can work from them unchanged.

## Why `.8`/`.9` (prompt), with the evidence

Judged `.7` errors were dominated by an action read as an outcome: a hit, a
dodge or a grab filed as `defeated` / `escaped` / `captured` (`defeated` 26/61).
`.8` tightened only the verb definitions and added "a technique's user is the
subject": +16 points on the same pages. `.8` moved domain/ice traps from
`sealed` to `captured` (a regression in meaning); `.9` restores the boundary
(`sealed` 1→19, `captured` 14→3 on the pilot pages).

## Run-to-run variance (a finding in its own right)

At temperature 0 with batched decoding, re-reading the same 100 pages moved
`met` 188→262 with no change to its definition: one clause ("Yuji, Megumi and
Nobara then enter the room") became 42 rows pairing them with everyone in the
scene. The `fanout` gate removes exactly that shape (39 rows on that pilot, 0
on the whole `.7` corpus and 0 on the `.8` pilot). Any single-run precision
has ± variance beyond its sampling CI.

## Gates after (on the `.9` store, `:8000` on CUDA, 10:06–10:18)

| gate | before | after |
|---|---|---|
| pytest | 1,451 + 2 xp, 2 failed (env: `blind_panel` date-rot, `page_gen` ANSI) | **1,461 + 2 xp, 7 failed** = the same 2 env + 5 frozen-from-old-rows (3 continuity gold, 2 `timeaxis` ledger pins — open items 1–2) |
| eval jjk | 31/31 | **31/31** |
| span-recall jjk | 48,572/48,572 · probe 398/400 | **48,572/48,572 · probe 398/400** |
| canon opm | 10/16 · 236/236 · 79.0% | **10/16 · 236/236 · 79.0%** |
| /context narrative bundles (30 JJK subjects) | snapshot | **30/30 byte-identical** |

The +10 passing tests are the new ones (resolver pointing, drops, trace,
fan-out). The 9 `int(None)` failures the first post-run surfaced
(`test_gate` ×6, continuity triage ×3) are fixed in `gate.py`.

## Open — the council's, not the executor's

1. **Continuity gold** (`scriptengine/eval/gold_continuity.json`) was frozen from
   the discarded `09-05.2` rows: 6 of 20 cases no longer hold, and the anachronism
   core it was drawn from grew 31 → 168 filings. Re-freeze (the council's own
   20-cleanest recipe) or redesign — a governed decision; left untouched.
2. **`tests/test_timeaxis.py` ledger pins** (995 / 90) count old rows; they move
   with any re-extraction. Re-pin with a recorded reason, or make them relative.
3. **Prompt `.9` is shared** by Marvel/MCU; their stored rows are `.7`. Ratify `.9`
   before their full run (their shard-1 `defeated` precision was never judged).
4. **The events layer reaches no served answer by default**
   (`SCRIPTENGINE_EVENTS_ORDER` is off; the 30-query narrative bundle diff was
   byte-identical before/after). Until a door serves it, events quality cannot
   move a script — this is where D-R (the reasoning bank) has to start.
5. **Remaining error classes** at `.9`: verb semantics (confrontation/threat/argument
   as `fought`; presence/noticing as `met`), entity (generic classes like
   "Curse User", "cursed spirits"; Geto-as-Kenjaku before the reveal; techniques
   as ends), not-an-event (attempts, intentions). Each is a candidate for the next
   closure iteration.

## Restore points

`/mnt/PROJECTS/backups/jjk_100_20260929/`: `facts.db.pre-P0` (the 09-05.2 store),
`facts.db.post-P2-p7` (the `.7` store), `events_trace_2026-09-29.7.jsonl`,
`engine_v2.patch`, `engine_v2b.patch`. Live trace for `.9`:
`series/jjk/events_trace_2026-09-29.9.jsonl`.
