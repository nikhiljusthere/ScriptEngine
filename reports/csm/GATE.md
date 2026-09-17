# CSM gate — the four standing gates, live state

The CSM campaign (Phase 1, §9a closure loop) runs the **same four standing
gates** the JJK campaign uses, because every CSM engine change must not
regress the JJK baseline (JJK stays at 100%). Nothing here is graded — the
gates are mechanical (counts, string/foreign-key equality); they report, they
do not judge.

The four gates (re-run after every fix-class, before calling it done):

1. **gate-1 — `pytest tests/ -q`** (in-process, CUDA): the full suite green.
    Current pin **1,331** (1,321 R-7 pin + 10 new R-8 router tests; the only
    failures are the known env-mcp trio under a stopped :8000, 2 xpassed).
    **R-8 window DISCHARGED (2026-09-17):** the four gates + `eval --series jjk`
    31/31 re-ran green on the post-R-8 tree `8661850` (receipts `4b60043`,
    `receipts/r8_gate_window.md`); `GATE_LEDGER` `last_green` = R-8 `aada154`.
    **W-state pin (council #30, 2026-09-17):** W1 (`:8000` down) = 1,331
    collected with the 3 known env-mc failures
    (`tests/test_mcp_server.py:20,35,46`); W2 (`:8000` up) = 1,331/0.
    (SITUATION/R4's 1,334/0 is a +3 arithmetic drift — verified collect-only
    = 1,331.)
    **Order (council #30): stop Qwen (`ninfer-stop.sh`, verify `mode=off`) →
    W1 in-process, whole card → `:8000` up on CUDA → W2 gates → move
    `GATE_LEDGER` + re-stamp `phase_status` sha → launch the runner against
    the same service. The runner's pre-checks (exit 11/12) see service state
    only, not the gates.**
2. **gate-2 — `eval --series jjk`**: **31/31 (100%)** gold.
3. **gate-3 — `span-recall --series jjk`**: **48,572/48,572 offline (rc=0)**
   + a 400-probe (seed-rotated; the live window must clear the 390/400 =
   97.5% bar).
4. **gate-4 — `canon-run --series opm --skip-eval`** (one-copy rule):
   **236/236 canon (100%)**, 79.0% closed-set precision, 0 confident-wrong.

## Live state

> **Superseded 2026-09-17:** the R-8 gate window has since been DISCHARGED
> (tree `8661850`, pin 1,331, receipts `4b60043`) — see the "Gate debt —
> DISCHARGED" section below. The P1.4 copy recorded here is the historical
> baseline, not the current pin.

**GREEN at the P1.4 four-gate copy** (P1.4 close, 2026-09-12, @`407c016`;
copy stamp commit `af382ee`). All four gates re-run green on CUDA (one-copy
100k dial): pytest **1,321** (1,316 passed + 3 known env-mcp trio failures
under a stopped :8000, 2 xpassed), eval jjk **31/31**, span-recall **48,572
rc=0 + 398/400 (99.5%)**, canon opm **236/236, 10/16 exact, 79.0%** (run dir
`reports/2026-09-11-2218/`). The env-mcp trio was live-proven 2/3 against a
running :8000 (the 1 failure is a **REAL pre-existing finding**: bare
character name "Maki Zenin" routes `qa` via `router.py:809-812`, mismatching
the test's narrative intent; the mismatch predates the test by a month —
deferred to P1.5, not a campaign regression; the gate-1 pin stays 1,321).
**5.4 re-adjudication (council R6):** 34 s one-copy census re-run (CUDA,
co-located with Qwen, 33 s, RC=0, Qwen alive) — 21/21 reds identical to the
09-09 run, **0 closed, 0 new regressions** => no de-scope; the 22-row
extraction-gated floor stands in full (21 `csm-dim-*` + `csm-char-04`), the
5.4 gate stays LIVE, P2.3 stays in scope. Raw receipts:
`reports/csm/receipts/census_5_4_readjudication_p14.md` (this run overwrote
`census_dimensions_csm_results.jsonl` in place; the 09-09 version is in git
at `af382ee`) + `reports/2026-09-11-2218/` (gate-4) +
`reports/span-recall/jjk/recall_verbatim.jsonl` (gate-3 live) +
`GATE_LEDGER.json` `p14_close_copy` + drift D24. **Bar-audit pre-registration
(close condition d):** `reports/csm/bar_audit_p14_preregistered.json` — 26
panel-line cases over the 6 D6 classes (3–5 each), 78/78 expect terms
verbatim-verified vs `series/csm/facts.db` (model-free, authoring subagent,
receipt `reports/csm/receipts/bar_audit_p14_author.md`).

Previous live state (R-7 @`81df799`, queue 35 open / 23 closed) stands in
`GATE_LEDGER.json` + drift D22; its receipts are unchanged.

**Machine-readable ledger-of-record v1:** `reports/csm/GATE_LEDGER.json` —
read it *first* after a reboot; if `HEAD == last_green.commit` the four gates
stand, do not re-run them.

## The halt rule

Phase 1 halts at the **extraction-gated floor**: the `D6-extraction` class
(21 rows, closed only by the Phase-2 extraction campaign) **plus
`csm-char-04`** — the 8th Makima-ability row, confirmed 22nd floor row by the
R-7 close re-sweep (its close lever is the Phase-2 extraction track / 5.4
re-adjudication) — and the invariant floor rows: the roster floor
`csmdoor-01` 31/88, the D5 reachability residuals
(`csmd5-01/02/03/05/06`, `gate400-320`, `red-R-4`) and the closed-class
curation residuals (`csm-char-03`, `csm-set-02`) — the ten stamped by-design
open, governing stamps in the red-list R-2/R-3 close notes. When every
non-floor, non-extraction fix-class is green and the queue's remaining open
rows are all extraction/floor (halt residual 35 = 22 floor + 10 residual +
3 `r1blast-*` stamps), B writes
`reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` and stops.
---

## P2.1 step-0 — the sanity-100 timer, A17 floor policy, A26 hashes (2026-09-12)

Run by the directing session with **Qwen stopped and the whole card free**
(31.9 GB), `:8000` on CUDA, one consumer. Tier-0 first: **17,382/17,382
sentences present in a chunk, 0 unreachable, 100.0000%** (11 link-list
boilerplate lines excluded).

### A26 — control-arm inputs, frozen before the sweep

| input | value |
|---|---|
| `panel_csm.json` stored hash | `e3d737205cd07245a8a3677dc03b0eb1f3c08d43ed7d8ab0b308bf97e73ebe6d` |
| panel / held-out size | 17,181 / 200 (seed 42, min_words 6) |
| `panel_csm.json` sha256 | `cf72135fb03ef82cbe3cfeb4d943442d165b6fa8cf1f34058bbcda98c6ab25ec` |
| `panel_csm.json.heldout.json` sha256 | `604dc8ca14b177701511b73b27d64170de792f3b0d212846f66b2756264124e8` |

A18 satisfied: the qa ledger was wiped to zero before this window (`ba3a866`),
so the 100 rows in `sweep_qa_e3d73720.jsonl` are a post-P1-engine control arm,
not a resume of the 572 pre-fix rows stamped `5c424f3`.

### The measurement (100 probes per door, first-run-only `--sanity`)

| door | wall | s/probe | HIT | MISS_DOC | MISS_SPAN | TRUNCATED | full sweep (17,181) |
|---|---:|---:|---:|---:|---:|---:|---:|
| qa | 50.56 s | **0.506** | **95** | 3 | 2 | 0 | **2.41 h** |
| narrative | 2.31 s | **0.023** | 35 | 40 | 3 | 22 | 0.11 h |
| roster | 4.43 s | **0.044** | 2 | 51 | 6 | 41 | 0.21 h |
| **total** | | | | | | | **2.73 h** |

No dead-door halt fired (all rc=0); roster cleared the zero-hit bar by 2 rows.

### Go/no-go — **GO**

Pre-registered threshold: re-estimate > 2 GPU-days (48 h) ⇒ abort/shrink/council.
**Measured 2.73 h — 17.6× under budget.** The break-even rate was 3.350 s/probe;
the worst measured door is 0.506. The 51-GPU-h figure the plan called fiction
was ~19× too high, because it priced an unmeasured 4 s/probe against what is
actually 0.506 on a free card. Per-door rates differ by 22×, so the
no-uniform-rate rule mattered: a uniform estimate off qa alone would have read
7.2 h.

### A17 — per-door floor policy, declared BEFORE the sweep

- **qa — a regression target.** Bar: JJK's standing band, ≥ 97.5 %. **The
  sanity window measured 95 % (95/100), which is UNDER that bar** — recorded
  here as the pre-sweep finding rather than discovered mid-run. The 5 misses
  (3 MISS_DOC + 2 MISS_SPAN) are the first rows to triage; the full-panel rate
  decides whether 95 % is the sanity sample or the corpus.
- **narrative — documented floor, not a regression target.** 35 %. The 22
  TRUNCATED rows are budget design, not misses.
- **roster — documented floor, not a regression target.** 2 %. Structurally
  low-yield on verbatim-line probes exactly as A17 predicted; closure is
  floor + every residual triaged with class and reason, never "miss file
  empty".

"Miss file empty" applies to the qa door alone.

## P2.1 step-0 addendum — the auto door measured (2026-09-12)

The council's decisive test: the same 100 panel probes through **`--door auto`**,
the path `/context` actually serves. 19.20 s wall (0.192 s/probe), rc=0.

**auto = 37/100 HIT. Forced qa = 95/100.** A 58-point gap, on identical probes.

The router's own choices explain all of it:

| router picked | probes | HIT | rate |
|---|---:|---:|---:|
| narrative | **81** | 28 | 34.6 % |
| qa | 9 | **9** | **100 %** |
| roster | 9 | 0 | 0 % |
| relations | 1 | 0 | 0 % |

**When the router picks qa it is perfect (9/9). It picks qa 9 % of the time.**
It sends **81 %** of verbatim line-retrieval probes to narrative, which serves
about a third of them, and 9 % to roster, which serves none.

### What this overturns

The Contrarian's prediction — that the panel's synthetic verbatim lookups are
"shapes the router would send to qa essentially always", making narrative 35/100
and roster 2/100 forcing artifacts with no referent — is **falsified**. The
router sends 9 % to qa. The forced narrative/roster numbers were not artifacts:
they are close to what the live router actually produces (35 forced vs 34.6
routed on narrative), because the router is genuinely choosing those doors.

The earlier "17 of 21 recover by routing" claim is also further undercut from the
other side: routing is not the rescue, it is the leak.

### What this promotes

**R-8 is no longer bookkeeping — it is the largest measured lever in the
system.** For this probe class, door choice alone is worth 58 points of recall
(37 % → 95 %). No extraction campaign is competitive with that: extraction was
scoped to close ~21 census rows, while the router is losing ~58 of every 100
lines on the served path.

Reviewer-4's reframe stays live and is now partly answered: roster serves 0/9
and narrative 28/81, so those doors *are* weak on verbatim lookups — but the
proximate defect is that the router hands them 91 % of the traffic.

### Scope caveat, stated so it is not over-read

These are panel probes (verbatim/scoped sentence lookups), not writer questions.
The claim is bounded: **for line-retrieval shapes**, the router misroutes 91 %
away from the door that answers perfectly. Whether the same gap holds for
script-writing questions is a separate measurement and is not claimed here.

### Consequence for the sweep

The 3-door sweep is **not** run. qa-full (2.41 h) is deferred until R-8 lands:
a qa-forced ledger measures a door the router almost never picks, and the A17
bar (≥ 97.5 %, sanity measured 95 %) should be re-taken on the post-R-8 auto
path, which is the number that describes the product.

## R-8 sized: the 21 floor rows hand-labelled (2026-09-12)

Reviewer-3's cheap decisive test — label the correct door for each floor row by
hand (n=21, zero GPU), then compare with what `route()` actually picks. Labels
were written and **committed blind** (`ff96f58`) before any measurement, because
this session had already been burned once by oracle contamination.

**Agreement: 13/21 (62 %). Every one of the 8 mismatches is the same defect.**

| labelled | routed | rows | |
|---|---|---:|---|
| qa | qa | 7 | correct |
| roster | roster | 6 | correct |
| **narrative** | **roster** | **8** | all arc-narrative, all `why="asks for the story in order"` |

### Verdict: a GUARD, not a redesign

The router is right on 13 of 21 and wrong on exactly one class through exactly
one rule — `router.py:627`:

```python
if chronology.wants_chronology(query):
    return Route("roster", "asks for the story in order", signals)
```

Its comment records why it exists: *"Every arc in order" is set-shaped and
"Timeline of Dragon Ball" opens like a question*, and narrative answered the
latter with "eight loose beats". For genuinely **set-shaped** chronology the
rule is correct and must be preserved.

It over-claims on **per-subject** chronology. "What happened to Fake Chainsaw
Man during the War Devil arc, in order?" is one character's beats inside one
arc — narrative's exact purpose — and there is no set behind it. Rule 1 fires
before any other reading, so all 8 land in roster.

**R-8 shape:** gate rule 1 on set-shape as well as chronology; chronology
without a set falls through to narrative. Preserve "Every arc in order" and
"Timeline of X".

### Reviewer-4's reframe, answered

"Maybe roster's *serving* is the defect, not the router." On these 21 rows: no.
Roster is chosen correctly for all 6 rows where roster was the right door. The
defect is the choice, not the serving.

### A second, distinct misroute — recorded, not yet labelled

The auto sweep showed the router sending **81 of 100 verbatim line-lookup
probes to narrative** (34.6 % hit) while qa scored 9/9 when picked. That is the
opposite over-selection from the one above, on a different question shape, and
it is **not** covered by the rule-1 guard. R-8 may therefore be two guards. The
panel probes have not been hand-labelled, so this stays a finding rather than a
sized fix.

### Cost owed

`router.py` is series-agnostic and on the served path, so R-8 owes the four
standing gates **plus `eval --series jjk` 31/31** — not pytest alone. The
"Timeline of Dragon Ball" and "Every arc in order" cases are the regression
pins the guard must not break.

## R-8 landed: `aada154` (2026-09-16) + P2.1 runner pre-baked

### The fix, as landed

`wants_chronology_set` (chronology.py +27) splits the two shapes rule 1 was
conflating: a **set in order** ("Every arc in order", "Timeline of X" —
roster, preserved) vs. **one subject's beats in order** (one character's span
inside one arc — narrative, falls through). `router.py` rule 1 (+9/−1) gates on
the set shape. 10 new router tests (the "+39" in the fix log is 39 diff lines:
`test_the_set_in_order_is_still_a_roster`, 6 params, +
`test_one_subjects_story_in_order_is_not_a_set`, 4 params). The 8 mislabelled
floor rows (labelled narrative, routed roster, `why="asks for the story in
order"`) are the class this closes.

### The env-mc deferral, discharged

The P1.4 live-prove finding (bare character name "Maki Zenin" routes `qa`,
mismatching the test's narrative intent, deferred to P1.5) is resolved: the
bare-name → qa rule (`router.py:816-820`, landed 8d07487) is the intended
behavior; the stale test now asserts it
(`tests/test_mcp_server.py::test_research_bare_character_name_is_qa`,
count-neutral — no pin change).

### Gate debt — DISCHARGED (R-8 window, 2026-09-17)

The R-8 gate window is discharged: W1 (Qwen down, whole card) pytest
**1,331** + `eval --series jjk` **31/31** → `:8000` up on CUDA → W2
span-recall **48,572/48,572 + 398/400** + canon **236/236**, all green on tree
`8661850` (receipts `4b60043`). `GATE_LEDGER.json` `last_green` = R-8
`aada154` (pin 1,331, gate tree `8661850`; receipts_commit `4b60043`).
No open gate debt.

### P2.1 sweep runner pre-baked

`tools/csm/p21_sweep.sh` — the whole P2.1 sweep as one launch line (pre-baked
per PHASE2_JOB: the sweep needs no Qwen inference, so it runs with Qwen DOWN
and the whole 32 GB on `:8000`):

    setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &

- **Pre-checks** (exit 10/11/12): panel+heldout sha256 vs the A26 frozen
  values (`cf72135f…` / `604dc8ca…`), row counts 17,181/200, `:8000` /health
  (records `device`; non-cuda → exit 11), Qwen `:18080` down.
- **A18 pre-wipe, stamp-based**: a ledger resumes forward after a halt only
  when every row (main + `.new` sidecar) is stamped with the current HEAD;
  any older stamp (the pre-R-8 `f2a611d`/`2f67222` sanity rows) — in the main
  file or the sidecar — is wiped and the door restarts, so P1 parser fixes
  are never attributed to P2.3 (a mixed-stamp ledger, i.e. a mid-run commit
  move, restarts in full).
- **Sequence**: qa → narrative → roster → auto (full 17,181-row panel, 30 s
  per-door watchdog over main + live-sidecar rows), then the 200-row heldout
  under label **auto-heldout** running api door **auto** (the A24(a)
  out-of-sample number; `api/main.py:79` accepts only the five fixed modes,
  extra heldout doors are a one-liner if wanted).
- **Halt codes**: `exit 4` = `:8000` health failure ×2 rolling (PHASE2_JOB
  line 78); `exit 5` = ERROR > 10 of the last 50 rows THIS RUN wrote (rolling
  window from the door's resume baseline, line 79; ERROR rows re-probe on
  resume); `exit 20+rc` = CLI rc (2 ledger corrupt/tier-0 miss, 3 dead-door
  (`--sanity` found 0 hits on the door's 100 probes; `cli.py:2196-2202`),
  1 crash); `exit 30` = row-count integrity.
- **Receipts**: `reports/master-work/p21_sweep_<stamp>_RECEIPT.md` (pre-checks,
  A18 state, per-door verdict table, halt bounds) + `_run.log` + per-door logs.
- Wall estimate ≈ 3.7 h panel (2.73 h + 17,181 × 0.192 s auto ≈ 0.9 h,
  the "P2.1 step-0 addendum — the auto door measured" section) + ~4 min heldout.

### Runner fix-up (council-1 findings, disk-verified 2026-09-16)

The pre-bake had two real defects, both found by the first audit council and
verified against the engine before fixing:

1. **The heldout leg would 422**: `--door` is POSTed as the request's `mode`
   (`span_recall.py:214`) and `api/main.py:79` accepts only
   `qa/narrative/roster/relations/auto` — `auto-heldout` would 422 on all 200
   heldout probes (all-ERROR, A24(a) unmeasurable), and the CLI's ledger name
   (`sweep_{door}_{h8}.jsonl`, `span_recall.py:287`) would have missed the
   watched `sweep_auto_{h8}.jsonl` anyway. `run_door` now takes a **label**
   (receipt row, door log) and an **api door** separately; the heldout leg
   runs `run_door auto-heldout auto …` and the heldout panel's distinct 8-char
   hash keeps its ledger apart.
2. **Exit 5 was unreachable and A18 ignored the sidecar**: the CLI writes
   live rows to the `<ledger>.new` sidecar and merges only on a clean exit
   (`span_recall.py:469-489`), so for a wiped ledger the main file is absent
   for the whole door — the old main-file-only watchdog never saw progress or
   the ERROR bound, and a stale-stamp sidecar would be re-merged into the
   fresh door. The watchdog now counts main + sidecar and tails the sidecar
   for the ERROR window; the A18 wipe manages all five ledgers (the heldout's
   `sweep_auto_{h8}.jsonl` included) and wipes stale-stamp sidecars.

The receipt's halt/resume sections now precede the door sequence (a halted
receipt carries them), and the A18 bullet above is corrected: the auto sanity
ledger was stamped `2f67222`, not `f2a611d` (qa/narrative/roster were
`f2a611d` — all four stale vs HEAD, so the A18 wipe set is unchanged).

### Runner audit (council #30, 2026-09-17, pre-GPU)

Council #30 (5 advisors + 5 reviewers + chairman, `reports/csm/receipts/
council_p21_audit/`) re-audited the runner before the GPU session and returned
**SHIP-WITH-CHANGES**. Resolved:

1. **Resume-boundary defect (R5, verified on disk):** after a burst-halt,
   `span_recall.py:408-411` reads the stale `.new` sidecar into `prior` and
   :469 appends after it, so a pre-halt ERROR burst sits in the watchdog's
   50-row window on resume → false exit 5. `run_door` now records
   `base_main`/`base_side` at door start and the ERROR window counts only
   rows THIS RUN wrote (`tail -n +$((base+1))`).
2. **Orphan-CLI guard:** `trap 'kill "$pid"' EXIT` — a non-reboot runner death
   no longer orphans the nohup'ed CLI into a second sweep on the same sidecar.
3. **Sanity pre-pass:** a first-run-only `--sanity 100` CLI call per panel
   door before the sweep (PHASE2_JOB.md:66-67, zero panel spend); resumed
   ledgers skip it (a capped resume would trip exit 30). rc maps to exit
   21/22/23 (crash/ledger/dead-door).
4. **Device pre-check:** the `/health` receipt records `device`; non-cuda →
   exit 11 (a CPU `:8000` passed all pre-checks before this).
5. **Wall estimate corrected** 2.7 h → ≈ 3.7 h (the 2.7 h sum omitted the
   auto full-panel door, 17,181 × 0.192 s ≈ 0.9 h).

Verification: the 16-assert dry-run (`/tmp/p21test2/run.sh`, T1–T5) is green;
T5 (a 11-ERROR-row sidecar at resume → no false exit 5) fails against the
pre-patch window logic (exit 5 at 12/20, `last-50 ERROR=11`) and passes
post-patch. No CLI change.

**Launch order (the undischarged gate window, council #30 A2):**

1. **W1 — in-process, whole card:** stop Qwen FIRST via
   `~/ninfer-work/ninfer-stop.sh` (writes `mode=off`; blocks the
   `ninfer_restart.sh` poller — a bare kill lets it resurrect Qwen mid-sweep;
   `qwen-switch.sh` has no stop mode, the pre-#30 text mislabeled it). Verify
   `mode=off` + :18080 free. Then `pytest tests/ -q` (W1 expectation, A5:
   1,331 collected, 3 known env-mc failures) + `eval --series jjk` 31/31.
2. **Service:** `:8000` up on CUDA from the current tree (setsid-detached);
   record HEAD; confirm `/health` `device=cuda` (models load lazily).
3. **W2 — gates against that one service:** `span-recall --series jjk`
   (offline rc=0 + 400-probe ≥ 390/400) + `canon-run --series opm --skip-eval`
   (236/236, 79.0%).
4. **Ledger + re-stamp:** move `GATE_LEDGER.json` `last_green` to the R-8
   commit, then re-stamp `phase_status.txt:4`'s `ledger_sha256` (the :9 pin is
   otherwise unsatisfiable; a literal executor reads the drift as ledger drift
   and re-runs the window — 1–2 GPU-h).
5. **Canary:** count HITs in the 4 pre-wipe sanity ledgers (qa 95 /
   narrative 35 / roster 2 / auto 37 per 100; A18 wipes at launch). At ~10 min
   in, HIT% must sit near the qa floor (~90+); a large deficit = a
   quietly-wrong `:8000` (MISS_DOC floods the 10/50 bound can't catch) →
   kill + diagnose.
6. **Launch the runner** against the same service (no restart; exit 12
   enforces Qwen-down). **No mid-sweep commits** (A18 wipes all 5 ledgers;
   ~3.7 h restart).

Post-sweep: restart Qwen via `qwen-switch.sh 100k` (plan A19), not the 262k
default `ninfer-stop.sh` restarts.

## P2.1 full-panel sweep result (2026-09-17, tree `4b60043`, device cuda) + post-sweep council (#31)

All five ledgers complete (panel 17,181 + heldout 200; A26 shas
`cf72135f…` / `604dc8ca…`; report `reports/csm/p21_sweep_2026-09-17/REPORT.md`):

| door | HIT | rate | A17 disposition |
|---|---:|---:|---|
| qa | 16,920 | **98.48 %** | **PASS** (bar ≥ 97.5 %; 261 misses → triage `p21_sweep_2026-09-17/triage/`) |
| narrative | 1,846 | 10.74 % | documented floor (histogram + sample triaged, P-4) |
| roster | 133 | 0.77 % | documented floor (same) |
| auto | 2,651 | 15.43 % | descriptive raw (heldout 28/200 = 14.0 %) |

Routing: 89.1 % of line lookups → narrative (serves 10.6 % of those),
6.0 % → qa (97.8 %), 4.7 % → roster (2.7 %), 0.2 % relations; 14,293
auto-miss/qa-hit; **237 both-misses (a router fix cannot reach them)**; 24
auto-only hits.

**Council #31 pre-registrations** (full record `reports/csm/COUNCIL_p21_post_sweep.md`):

- **P-1** auto is not a gate number on this panel (clearing 97.5 % needs ~99.7 %
  qa routing; a perfect router tops out at ~98.62 %). Descriptive raw only;
  any future bar is set on the heldout (14.0 %).
- **P-2** P2.2 bar audit (26 lines) graded pre-fix on the qa control arm
  (JJK 3b in-process, the `tools/census_dimensions_csm_v2_grade.py` pattern),
  auto door recorded as the R-9-contingent supplement; verdict R-9-contingent.
- **P-3** R-9 (the second misroute, 89.1 % → narrative) deferred, not
  pre-committed; fires on writer-shaped evidence (P2.4 + P2.3); check the
  per-wiki route in `series/csm/overrides.yaml` before any series-agnostic
  `router.py` change (which owes the four gates + the JJK debt).
- **P-4** `PHASE_B_COMPLETE` residual scope: full class + reason on the qa 261
  (237 both-misses first) / 24 auto-only / 26 bar-audit lines; narrative +
  roster floors by complete histogram + first-5-per-cell sample with
  deterministic class/reason (`tools/csm/p23_triage_inputs.py`, outputs in
  `p21_sweep_2026-09-17/triage/`).
- **P-5** P2.3 = pointer grader over the writer-shaped 486-item widened bank
  (no re-authoring); in-process CUDA, whole card, Qwen down
  (`tools/csm/p23_grader.py`; handoff `reports/master-work/P23_HANDOFF.md`).

Close order: P2.2+P2.3 grade (the model-unloaded GPU handoff) → P2.4 writer
leg (Qwen up) → R-9-vs-writer-bar evidence call → `PHASE_B_COMPLETE`
(§P2.5 checklist + P-4 scope).
