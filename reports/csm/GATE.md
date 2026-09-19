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

## P2.3 + P2.2 graded (2026-09-17, model-unloaded, `3d43a21`)

The handoff batch (`p23_grader_20260917-103148`, receipt + results committed)
ran clean: 0/538 probe errors, in-process CUDA, whole card (Qwen down,
31,800 MiB free — it was already stopped when the session arrived).

- **P2.3 / A14 widened census (qa door): 417/486 MECH_GREEN (85.8%)**, 69 reds.
- **P2.2 bar audit (pre-fix, P-2): qa control arm 11/26** (the primary
  verdict — the P1.4 bar does not pass pre-fix), **auto door 14/26**
  (the R-9-contingent supplement; routed: 17 qa / 5 narrative / 4 roster).

Red triage + P-3 pre-analysis: `reports/csm/p23_red_triage.md`. Headline:
the 69 reds are 37 box-class **wrong-page ranking** (numeric-title
collisions, arc page vs character/game page — the same family as the
sweep triage's 83 defect-rank rows), 27 width/enumeration, 5 state-over-time
**content** (CSM has no interval facts; JJK `extra_facts` precedent), 0 judge
artifacts (0 reds flip under apostrophe/whitespace normalization). On the
26-case bar the auto door beats forced-qa by only 3 cases and both doors are
red on state-over-time (0/4) — **R-9 is not the lever for these reds**; the
evidence call waits on P2.4.

## Four pilot numbers (council #34 step 1, 2026-09-18)

Item-8 spec: `COUNCIL_csm-campaign.md` L372–379 — "plus §7's four pilot
numbers (T0 emergence, T0 survival, new numbered gaps, human round-trips)".

| # | Pilot number | Value | Source |
|---|--------------|-------|--------|
| 1 | T0 emergence | **843** (council expectation ~535) | `reports/csm/t0_pilot_csm.json` (pilot_1) + `T0_PILOT_CSM.md` |
| 2 | T0 survival | **843/843 (100.0%)** | `reports/csm/t0_pilot_csm.json` (pilot_2, dead []) + `T0_PILOT_CSM.md` |
| 3 | New numbered gaps | **5 submitted, 0 open** | below |
| 4 | Human round-trips | **27** | below |

### #3 — new numbered gaps: 5 submitted, all closed (hard gate does not fire)

Registry scan (2026-09-18): `grep -rhoE "G-CSM-[0-9]+" plan/ reports/ tools/ scriptengine/ | sort | uniq -c | sort -rn` → G-CSM-1:**106**, G-CSM-2:**89**, G-CSM-3:**64**, G-CSM-4:**54**, G-CSM-5:**4**, G-CSM-7:**1** (G-CSM-6/8+ absent; full doc scope; `reports/` only 100/79/54/50/4/1).

- **Submitted (5):** G-CSM-1..4 — `COUNCIL_csm-1b-2.md` L42 ("four numbered engine gaps were filed (G-CSM-1..4)"); G-CSM-7 — `work_log.md` L114 (R-7 entry).
- **G-CSM-5 was never filed** — all 4 mentions in the corpus are "not filed" variants: `work_log.md` L54, `reports/csm/receipts/waveB_csm6_instrument.md` L14, `reports/csm/crosspage_census_csm.md` L55, `reports/csm/CSM6_INSTRUMENT.md` L100.
- **All 5 closed on disk:** R-1 G-CSM-1 (`work_log.md` L76, `b84445f`); R-2 G-CSM-2 + R-3 G-CSM-3 (`work_log.md` L78, receipts `iter1_r2_passageleg.md` / `iter1_r3_roster_scoping_run.md`); R-5 G-CSM-4 (`work_log.md` L106, `ec60587` + `35c16c9`, meter 0/11→5/11); R-7 G-CSM-7 (`work_log.md` L114, `4f5d075`, gate window 4/4 @ `81df799`).
- **Hard-gate ruling** (`COUNCIL_csm_100p.md` L155–157 + L322–323: "if #3 is non-zero → floor is moving, A20 precondition fails; halt, no marker, council reconvenes with the new count"): the gate's concern is a *moving* floor — new gaps still open or still emerging. #3 = 5 submitted, **0 open** (all 5 closed by the R-class), and no new gap ID since G-CSM-7 (registry max ID = 7; G-CSM-6/8+ absent) ⇒ floor is not moving ⇒ the gate does not fire ⇒ step 1 may stamp.

### #4 — human round-trips: 27

Count rule: owner instruction/correction/decision/halt = 1; distinct asks within a single entry count each; restatements of an earlier owner rule count once; machine-state acts (power-offs, hand model restores) are excluded. Source: `plan/drift_log.md` D1–D36, re-verified by owner-mention scan (case-insensitive) 2026-09-18.

| Era | Count | Entries (drift_log lines) |
|-----|-------|---------------------------|
| JJK D1–D11 | 2 | D5 "user directed (2026-09-07)" (L221–226); §4/D11 2026-09-07 halt + CSM approval (L159/172) |
| Off-campaign D12–D16 | 15 | D12 (L442); D13 (L474); D14 ×8 (L502/515/521/527/539/561/587/594; L574–575 restatements); D15 (L625); D16 ×4 (L631/634/639/650; L643/651/653 restatements) |
| CSM D17–D36 | 10 | D17 ×3 (L664/673/694; L688 power-off + L690 rationale excluded); D19 (L780); D20 (L827); D21 (L911 "Owner steer"); D22 (L956); D25 ×2 (L1053/1098 @ `81df799`); D26 (L1116); D20b + D27–D36 = 0 (post-L1116 lines are "NEXT (owner return)" markers / decision-path references, not interventions) |

**27** = 2 + 15 + 10.

**Double-check (read-only reviewer, 2026-09-18): 8/8 PASS.** Note: the
"0 open" reading of the hard gate is a re-reading (a literalist "5 filed ≠ 0"
would fire it); ratify it explicitly at sequence step 4 before the P2.5
re-assertion. Registry scan delta after this block landed: +20 self-references
(18 in this block + 2 in `p25_done_audit.md` (d)); the pre-append counts
above are the baseline for future scans.

## 22/21 floor reconciliation (council #34 step 2, 2026-09-18)

Canonical floor N = **22** = the 21 `csm-dim-*` Census-v1 red rows
(arc-narrative 8 · state-over-time 5 · abilities 6 · appearance 1 ·
causality 1) + `csm-char-04` (R-7x, "Every ability of Makima", recall 7/8 —
the 8th, "Contract with the Prime Minister of Japan", is prose-only /
never-extracted ⇒ close lever = Phase-2 D6 / 5.4 re-adjudication). "21" = the
Census-v1 subset (the row count of `census_v1_floor_triage.jsonl` pre-diff);
"35" = 22 floor + 10 by-design open + 3 `r1blast-*` stamps (the halt
residual; A20 stamps against the register diff, **not** 35).

One-line diff: `csm-char-04` appended as row 22 of
`reports/csm/census_v1_floor_triage.jsonl` — triage **PARTIAL** (7/8
recovered, 1 extraction-gated), `recovered_by` qa+anchor, `best_hits` = the
7 found abilities per receipt `reports/2026-09-08-0752/canon_scores.json`
(set "Makima, by section and prose"; recall 0.875, precision 1.0, exact
false). Note: `csm-char-04` is a full-set **bank** row, not a Census 3-item
sample row, so its `expect` carries the full 8-item gold set (the 21
`csm-dim-*` rows keep the 3-item sample convention). The file has no
programmatic consumer (governance record only) — the schema departure is
inert.

**Step-3 double-check (read-only reviewer, 2026-09-18): 5/5 PASS.**
Register = 233 rows, all valid JSON; bucket counts setrel 134 / dim 42 /
abl 6 / empty 16 / floor 22 / bydesign 10 / r1blast 3 sum to 233, ids
unique, every row carries the 7 governance fields; the one-pager's 7-bucket
table, the 233 formula, the 424 breakdown, the 42-dim breakdown and the
halt-35 formula all match the register; commit `da599fd` contains exactly
the register + one-pager (no EXCLUDE run-folder or GPU file; the other CSM
governance files ride step 5); the 22 floor rows (21 `csm-dim-*` +
`csm-char-04` full 8-item set) are intact. STEP-3 PASS.

## P2.5 (e) re-assertion @ pin 1,331 (council #34 step 4, 2026-09-18)

Re-asserts P2.5 item (e) — the JJK baseline diff-empty against the named
2026-09-08/09 re-baseline — against the current gate-1 pin, per
`p25_done_audit.md` re-assertion recipe step 2. Read-only: it cites
on-disk receipts, it does not re-run the gates (Ruling 5e: a known +N test
delta does not re-run the gates).

**Pin = 1,331** (`reports/csm/GATE_LEDGER.json` `gate1_pytest`, R-8 window
receipts commit `4b60043`: 1,321 R-7 pin + 10 R-8 router tests). The plan's
named **1,305** (the 2026-09-08/09 re-baseline) is a *test count*; it moved
to 1,331 by the documented +26 known additions (R-7 +16, R-8 +10). Ruling
5e exempts a known +N delta from a full re-run — the pin grew, JJK did not
regress.

**"0 open" hard-gate reading — ratified (before the re-assertion).** The
step-1 double-check (above) flagged that #3's "0 open" is a *re-reading* (a
literalist "5 filed ≠ 0" would fire the halt). Ratified here on the ground
the gate's stated concern is a *moving* floor — new gaps still open or
still emerging. On disk: G-CSM-1..4 + G-CSM-7 all closed by the R-class (R-1
`b84445f` · R-2/R-3 iter1 receipts · R-5 `ec60587`+`35c16c9` · R-7
`4f5d075`), the registry's max ID is 7 (G-CSM-6/8+ absent), so no new gap ID
since G-CSM-7 ⇒ floor not moving ⇒ #3 = 5 submitted, **0 open** ⇒ the gate
does not fire. This is the reading the re-assertion stands on.

**JJK baseline diff-empty (result comparison) — the D36 window receipts.**
The fast diff-empty path does *not* apply: `git diff --name-only b8b0ed5..HEAD --
scriptengine series/csm/overrides.yaml tests` is non-empty (`context.py`,
`overrides.yaml`, `test_coverage_scope.py` — the R-class work itself). The
gates therefore stand on the **D36 re-run**, which re-ran all four standing
gates green on the post-patch tree (`reports/csm/receipts/model_window_d36/state.*`):
- eval: `rc=0` (31/31 = named 31/31).
- span-recall: offline `rc=0` (48,572/48,572 = 100 %) + live probe `rc=0`
  (398/400 = 99.5 % ≥ the 390/400 / 97.5 % named bar).
- canon opm: `rc=0` (236/236 = 100 %, 79.0 % precision — matches named).
- coverage: `rc=0`.
- pytest: first-pass `rc=1` (1328p + 1 failed + 2xp = 1,331 collected) →
  post-patch `1329 passed, 2 xpassed` `rc=0` (= the 1,331 pin; the single
  first-pass failure `test_csm_scope_classifies_the_whole_store` was fixed
  post-patch, `pytest_postfix_d35.log`).
- p23 bank (f): `rc=0`, 417/486 reproduced.

Result: the four JJK standing gates are green at/beside the named
re-baseline levels — JJK stays at 100 %, the baseline-exact reference the
CSM engine must not regress. **P2.5 (e): PASS @ pin 1,331** (evidence: D36
re-run receipts; pin: `GATE_LEDGER.json` R-8 window `4b60043`).

## Writer-facing statement (council #34 Ruling 5, 2026-09-18)

What is and is not ready for a writer drawing CSM context from the engine:

- **Complete, cited, usable today:** narrative / character / fight context —
  the prose pass is 100 % on every in-scope narrative page type; every line
  is traceable to a chapter (episode where the anime adapted it). This is the
  content a script can build on now.
- **Set / relation ("all X of Y"): 424 known failures, no closer until D6.**
  #33 established this class is *not* a Phase-1 router lever — the 134
  rc=2 set/relation pages (and their 424 relation questions) are known,
  pre-registered failures owned by the Phase-2 D6 extraction leg. **Cross-check
  any "all X of Y" answer against the wiki until D6 lands** — the engine will
  under-report the set.
- **22 extraction-gated facts stay missing until Phase 2:** the 21
  `csm-dim-*` box rows + `csm-char-04` (8-item expect set). These are the
  §9a extraction-gated floor — content the prose pass cannot author because
  the facts are not in the crawl.

**Standing-gates scope note:** the four standing gates (pytest / eval-jjk /
span-recall-jjk / canon-opm) are JJK **no-regression guards** by documented
design — they prove the CSM engine changes did not move the JJK baseline.
They are not CSM quality bars; CSM's own bar is the (a)–(h) done-declaration
(re-asserted 8/8 this closure).

## A20 stamps + P6 unlock (council #34 Rulings 2 + 4, 2026-09-18)

- **A20 stamps against the register diff, not 35** (Ruling 2). The six-week
  floor diff = the census register `census_v1_floor_triage.jsonl` (22 → 233
  rows) + commit `da599fd` + the one-pager `census_v1_open_population.md`. A
  regression (a row regressing, or a new gap ID past G-CSM-7) voids the stamp;
  the floor count is the reconciled N = 22, not 22-or-35.
- **No new marker owed.** `PHASE_A_COMPLETE 2026-09-12T11:51:10+05:30`
  (tree `407c016`) and `PHASE_B_COMPLETE 2026-09-17T22:02:05+05:30`
  (tree `2419a01`) stand as written (`reports/master-work/phase_status.txt`);
  the 22 floor rows are the floor (a regression halt), not a new gate.
- **P6 unlocks at this closure commit, scoped to the §7 method addendum**
(Ruling 4): Census v1 schema + grader + 200-row held-out, one drift-log
   pointer (D37), ≤1 week (by 2026-09-25), conditioned on the register proving
   the schema complete on CSM. The D6 design lock and the 7-wiki rollout are
   **refused now** (R3's under-scoped ×7 risk); they return post-register.

## Steps 4–6 double-check (council #34, 2026-09-18): 5/5 PASS

Bounded read-only auditor (fresh context) over the steps 4–6 closure:
(1) every GATE.md block present + internally consistent; (2) D37 drift entry
complete (register buckets, N=22, 8/8, RULINGS 1–5, no-new-marker, P6 §7
pointer, item-7 D26 pre-flight); (3) commit `d53fe40` changed exactly 10 files,
zero excluded (no run-folder / GPU / master-work file staged), the 3 council
artifacts created by it; (4) `p25_done_audit.md` 8/8 (one noted: (e)) matches
the step-4 block; (5) the ratified "0 open" hard-gate reading is uncontradicted.
All 5 PASS. The full 58/58 close (the 22 floor rows) is the Phase-2 D6
extraction leg — out of scope for this re-assertion; next leg = item 7 (D26
pre-flight).

## D26 pre-flight: A18 ledger wipe + CUDA restart + per-door sanity-100 (2026-09-18, opencode)

Phase-2 D6 leg first action (D37 item 7): re-measure the sanity-100 profile on
the post-R-class tree (`7de8055`, after D33 `floor_section_cap` + the D34–D37
windows) before starting the 22 floor-row extraction.

- **Ledger wipe (A18):** all four `sweep_{qa,narrative,roster,auto}_e3d73720.jsonl`
  (17,181 lines each, last-line stamp `4b60043` < HEAD `7de8055` = stale) deleted
  via `python os.remove` (`rm` is on the tool deny list — noted in D38). D37 named
  `sweep_qa` only; A18 semantics + the runner's own A18 pass wipe the same four,
  so the wipe scope is the named set. First-run-only `--sanity 100` pre-pass
  re-armed on all four doors.
- **GPU:** Qwen 100k (`--kv-capacity 102400`, 24,876 MiB pre-reserved, PID 495401)
  confirmed in a quiet window (util sampled 100% → 3–5% over 15 s; `decode_ready=0`;
  no extraction batch running). CPU `:8000` (PID 628916) stopped; `:8000` relaunched
  on CUDA (PID 745658; embedder + reranker lazy-loaded 5,936 MiB). Steady state =
  the sanctioned 100k co-location (Qwen + `:8000` on CUDA); Qwen liveness verified
  before and after the window (still 495401, memory unchanged). GPU after: 30,990
  used / 1,113 free of 32 GB.
- **Per-door `--sanity 100` (all rc=0, zero errors; 100 lines each into the
  wiped ledgers, no `.new` sidecars — idempotent resume, 17,081 probes each remain):**

  | door | HIT/100 | MISS_DOC | MISS_SPAN | TRUNC | wall | s/probe |
  |---|---:|---:|---:|---:|---:|---:|
  | qa | **95** | 3 | 2 | 0 | 59 s | 0.59 (cold) |
  | narrative | 35 | 40 | 3 | 22 | 15 s | 0.15 |
  | roster | 2 | 51 | 6 | 41 | 17 s | 0.17 |
  | auto | 37 | 36 | 5 | 22 | 31 s | 0.31 |

  (qa's 0.59 absorbs the ~45 s embedder+reranker lazy load on the first request;
  the later doors ran warm.)
- **Reading:** the profile is bit-identical to the 2026-09-12 P2.1 step-0
  measurement (qa 95 / narrative 35 / roster 2 / auto 37, 0.192 s/probe warm).
  The D33–D37 R-class tree moved the engine, not the sanity floors: narrative 35
  and roster 2 sit exactly on the documented A17 floors; qa's 95 stays a sanity
  sample under the full-panel ≥97.5 % bar; auto 37 is the known second misroute
  (router 89.1 % narrative) with the R-8 lever unchanged since `4b60043`. No
  regression. **Pre-flight PASS — the 22 floor-row D6 extraction leg is cleared
  to begin (design lock via council; dedicated-GPU window).

## D6 extraction-leg design lock (council #35, 2026-09-18)

Full record: `reports/csm/COUNCIL_csm_d6.md` (5 advisors A–E → 5 blind
reviews R1–R5 → chair, one agent at a time, fresh context each).

**Locked scope: (ii) composite — targeted red-class extraction + a frozen
30-row flip-detection green sample + a pre-registered named-limit
register.** Not (iii) full ownership, not blind (i). Adopts D
(First-Principles), adapted with A's green sample + A's frozen offline
recoverability triage (134 setrel + 6 abl), C's named-limit discipline
(defect + owning leg on every residual), and deletion of D's post-hoc
null branch.

- **Extraction scope = a new additive `--pages <frozen-list>` flag**
  (not `--scope corpus`). Minimal: read a slug list, intersect the
  scope page queue. JJK zero-regression proof pre-registered (model-
  unloaded, seconds): `--dry-run` on `--scope corpus`, flag-absent vs
  present-with-full-list → identical scope plans; gate test that the
  flag's default (absent) leaves the native path byte-identical. Rides
  the standing 4 gates at D6 closure — **no second gate cycle.**
  Pre-registered fallback: dry-run equivalence fails → native
  `--scope corpus`.
- **Green sample:** N = 5 per green dimension (6 dims = 30), seeded
  RNG (seed recorded), frozen in the register before the model call;
  disjoint from the 200-row held-out OOS (also frozen). Always re-
  graded at closure; any green→red flip = rebuild void + re-run.
- **Per-row lever map (204):** 22 floor = 17 routing (extraction) +
  3 partial (5.4 re-adjudication) + 2 content (Yoru, Asa Mitaka —
  targeted re-crawl pre-window + extraction). 134 setrel + 6 abl →
  frozen P/T/A triage: P/T → named limit "single-candidate enumeration
  width (retrieval-layer)", owning leg D7, re-tested post-rebuild via
  page-run; A → extraction (into the `--pages` list). 42 dim →
  extraction. 16 empty + 10 by-design + 3 r1-blast → struck,
  unchanged.
- **Pass test (pre-registered):** every p23 red (69) ends green OR
  individually triaged to a pre-registered bucket (named limit w/
  defect+leg, or new root cause) — no catch-all; P/T setrel each end
  named or close post-rebuild (receipted); 200-row OOS post ≥ pre − 2
  (a 3+ drop = void); 30-row sample zero flips; 4 standing gates at
  fix-class closure (JJK baseline diff empty). A20 stamps against the
  register diff; void set pre-registered (JJK 4-gate regression /
  sample+OOS flip / an A-row triaged "closes" still red). **A named
  limit does not void the stamp.**
- **GPU window (ordered):** checkpoint (switchpoint) → pre-window
  model-unloaded (2-page re-crawl + CSM re-index, zero-regression
  receipt; frozen triage + `--pages` list; dry-run equivalence; freeze
  30-row + 200-row sets; pre-extraction OOS + 134 page-run baselines)
  → `nvidia-smi` pre-check (stop `:8000`/CPU; LLM owns the card,
  model-only + ~7 GB free) → dry-run receipt → `--workers 2` (4 risks
  OOM given the 508/524 history; abort: model near memory ceiling or a
  per-page crash → resume, drop to workers 1) → atomic per-page
  resume → index rebuild → model-unloaded side session (re-grade + 4
  gates) → closure council → A20 stamp.
- **P6 boundary:** the lock pre-registers the **method seed** (Census
  v1 schema + grader + 200-row OOS protocol + named-limit register
  format) — the surface a 7-wiki rollout would inherit, **not** a
  rollout commitment. The §7 addendum (due 2026-09-25) documents that
  seed; the 7-wiki rollout itself stays a separate future owner
  decision. Escape hatch: a flawed method (OOS collapse / named limit
  missing defect+owner) voids the §7 addendum and re-locks the method
  before any rollout.

**Status: LOCKED. Next action = the D6 GPU window (§4 mechanics); P6 §7
method addendum owed by 2026-09-25.****

## D6 closure evidence (2026-09-18, opencode — for the closing council)

- **Extraction:** 72 pages considered / 71 extracted + Katana Man arc failed
  on the 8192 thinking budget → retry at `ANSWER_TOKENS=16384`: 16 extracted
  / 56 cached / 0 failed / +31 events → **333 events total (302+31), 195
  on-axis / 138 off, 59 pages** (`/tmp/d6_events_retry.log`).
- **Index rebuild** (`--force --no-embed`): shape identical
  (537 docs / 3,917 sections / 755 nodes / 11,261 edges / 5,081 facts /
  7,797 chunks); events remapped 333→333, 0 dropped; Qdrant untouched
  (5,513 pts = level 0+2 by design; L1 2,284 never embedded).
- **Side session** (`tools/csm/d6_model_window.sh`): pytest **1,329 passed +
  2 xpassed, rc=0**; eval jjk **31/31**; span-recall **48,572/48,572 offline +
  398/400 live probe** (baseline 390/400); canon-opm **exact baseline
  (10/16, 236/236, 79.0%)**; p23 **417/486, 0 errors**; page-run phase
  **134×rc=1 operational failure** (see anomaly). State files:
  `/tmp/d6_side_session/`.
- **Anomaly:** all 134 page-runs failed at preflight `health()` with
  connection-refused; zero of the 134 checks appear in the `:8000` access
  log, though the server served ~400 requests through ~09:50 and shut down
  gracefully only at the post-phase restore pkill. Eliminated: pipeline
  killers (none in code; only SIGTERM source is the post-phase restore
  pkill), proxy env (none set), port conflict (fresh bind + served
  traffic), stale server (fresh PID), clock skew (self-consistent phase
  durations). Correction: dmesg is UNAVAILABLE in this environment
  (`read kernel buffer failed: Operation not permitted`), so "dmesg
  clean" was no-data, not clean data — OOM is excluded instead by the
  graceful-shutdown lines, which require SIGTERM (an OOM kill is SIGKILL
  and logs nothing). Root cause UNDETERMINED — transient/environmental
  (council adjudicates). Hardening applied: both window scripts now HALT
  (exit 3) when 0/N page-runs score instead of rolling into done.
- **Rerun** (`tools/csm/d6_pagererun.sh`, identical conditions): **134/134
  rc=0, all COMPLETE**; `/tmp/d6_pagererun.tsv`; receipts relocated to
  `reports/csm/receipts/d6_page134_post/`.
- **Flip analysis** (pre = git `3d43a21`, `/tmp/d6_flip.py`): 486 green
  417→417 with **0 flips either way**; **OOS200 168→168 (delta 0, floor
  pre−2 holds)**; **green30 0 flips**. No void condition fires.
- **Why zero flips (root-caused):** the events table is consumed only by the
  narrative door (`retrieve/narrative.py`); the 486 grades the qa door
  (hybrid chunks + facts + relations — the live Katana Man arc bundle,
  14,201 chars, carries zero event content). The expect sentences ARE in
  chunks (`Katana Man arc / Synopsis` L1+L2) but lose to the character card
  → retrieval-ranking gap, same family as the 37 box-class wrong-page reds
  (`p23_red_triage.md`). The judge sees the full bundle (no truncation).
  Consequence for the pass test: the "42 dim → extraction" lever could not
  move qa-door verdicts; the dim reds need re-bucketing to a retrieval-layer
  named limit (owning leg D7) or a new root cause — **council decision**.
- **69-red accounting:** 0 green; all 69 carry pre-registered triage
  (`p23_red_triage.md`: 37 box wrong-page + 27 width/enumeration + 5
  state-over-time content + arc-narrative width/narrative-floor), refined by
  the finding above. No catch-all; A-row "closes" rows: none claimed.
- **Coverage:** `coverage_report.py csm` → **473/537 (88.1%), 4,013 Qs,
  remainder 0, orphans 0** (restores the D36 convention at the shared path;
  the side session's bare run had flipped it to JJK — JJK numbers unchanged,
  reproducible via `coverage_report.py jjk`).
- **JJK baseline diff:** probe artifacts only (`recall_verbatim.jsonl` +400
  rows, `reports/index.md` +1 canon row); no JJK code/corpus moves.

**Status: EVIDENCE COMPLETE. Next = closing council on the pass test → A20
stamp if green.**

## D6 closing council verdict: WITHHOLD — do not STAMP A20 (2026-09-18)

Full record: `reports/csm/COUNCIL_csm_d6_close.md` (5 advisors sequential →
5 blind reviews R1–R5 sequential → chair; advisors 3 WITHHOLD / 2 STAMP;
all 5 reviewers picked the Contrarian response strongest).
Chair verdict WITHHOLD with three exits then re-vote: (1) council-amend
the 48 rows (42 dim + 6 abl) from the failed EXTRACTION-GATED closer to a
D7 retrieval-ranking named limit (defect: character-card dominance over
arc Synopsis chunks in the qa door; owner D7 ranking; cite 0/69
served-text proof + events-OFF proof; quote register lines; no unilateral
re-bucketing); (2) root-cause the 134 preflight/access-log contradiction
with log proof (no full re-run required — post-rebuild reads proven —
unless contamination found); (3) re-vote on the amended register, no new
extraction. Decisive supplements: register pull (dim-42 filed to the
extraction closer, not a named limit — executed, 0 moved); 0/69 served
texts with event markers; reorder OFF by default; void trigger (c) does
NOT fire; JJK diff = probe artifacts only; setrel already green
pre-extraction (closer misattributed, clause satisfied).

**Status: D6 WITHHELD. Next = exit 1 (register amendment) → exit 2
(blackout root-cause) → re-vote.**

## Exits executed (2026-09-18, opencode)

- **Exit 1 DONE:** `census_v1_floor_triage.jsonl` amended — the 48 rows
  (42 dim + 6 abl) re-filed from EXTRACTION-GATED to the D7
  retrieval-ranking named limit (triage/closer/lever/root_cause/
  owning_phase/retest_trigger rewritten, extraction_gated→false; 48+/48-,
  no collateral). Amendment text cites the 0/69 proof + events-OFF proof.
- **Exit 2 DONE as far as evidence goes:** root cause UNDETERMINED after
  the full elimination list above (incl. post-council proxy check);
  dmesg-correction recorded; halt-guard hardening in both scripts. No
  contamination found in any instrument (all show genuine post-rebuild
  server interaction), so no instrument re-run is owed by exit 2's own
  terms.
- **Remaining:** exit 3 — re-vote on the amended register (owner/council
direction needed).

## Landing council verdict: LAND-then-STAMP, conditional on commit (2026-09-18)

Full record: `reports/csm/COUNCIL_csm_d7_landing.md` (5 advisors
parallel → 5 reviews parallel → chair; LAND 3 / REJECT-or-conditional
2; STAMP 3 / WITHHOLD 2; reviews unanimous B-strongest). Chair:
CONDITIONAL LAND + CONDITIONAL STAMP after post-commit receipts.
Staff supplements closed three charges pre-chair (attribution = sole
+64 delta; patterns generic-compliant; per-row prediction pre-existed
via probe-3). Ordered steps: (1) OWNER AUTHORIZES COMMIT (blocking);
(2) commit spike + new tools at pinned hash; (3) re-gate from committed
IDs; (4) JJK-exact re-proof + register 46→green + 16-row docs; (5)
STAMP.

## D7 spike: subject-routing default — +46 green, 0 counter-flips (2026-09-18)

Spike (UNCOMMITTED, +64 insertions in `scriptengine/api/context.py`
only): `_story_page_subject()` (generic arc/chapter/episode/volume
title patterns → node/alias resolution, None when unresolvable) + tier-2
router-subject forward, applied in `_qa_context` when the caller passes
no subject. Design from probes 1–3 (gold never shortlisted unfocused;
45/48 flip with subject). No series names; no instrument changes (p23
still passes subject=None).
- **D7 gate window** (`tools/csm/d7_gates.sh`; Qwen 65k stopped — triple
  residency would peak ~32.6 GB; restored after with exact user argv):
  pytest **1,329+2x rc=0** (pin holds); eval jjk **31/31**; span
  **48,572 offline + 398/400 probe**; canon **exact baseline**;
  official p23 regrade (spike active) **417→463 (+46/−0), 0 errors**.
  State: `/tmp/d7_gates/` (archived to receipts after).
- **Flip ledger:** 46 red→green (10 arcb, 8 chap, 9 ep, 8 vol, 2 org,
  3 abl, 4 abl-pool, state-01, appr-06); **0 green→red**; OOS200
  **168→190 (+22)**; green30 **0 flips**; bar-qa 11→13.
- **Remaining reds: 23** = 7 amended holdouts (chap-01 numeric
  collision; org-03/05/06; vol-10 guidebook; pool-140/358 width) + 16
  floor (8 arc-narrative, 4 state-over-time, 3 abilities, 1 causality;
  Phase-2-tracked).
- **JJK diff:** engine spike (CSM/JJK-shared path, gated green) + probe
  artifacts only; no JJK corpus/store moves.
- Pre-spike 486 snapshot preserved at
  `reports/csm/receipts/d6_window/census_widened_csm_results_pred7.jsonl`.

## PROBE3 subject-scan: 45/48 flip — D7 fix direction proven (2026-09-18)

Pre-registration: `reports/csm/receipts/d6_probe/PROBE3_PREDICT.md`;
runner `tools/csm/d6_probe.py --scan48`; result `PROBE3_RESULT.json`.
Measurement only (official no-hint grade untouched, no code/store
change): all 48 amended rows (all RED post-rebuild) re-graded through
the exact p23 path with subject=item["subject"].
- **45/48 flip RED→GREEN, 0 errors — prediction met (≥40).**
  Per-class: story_arcs 10/10, episode 9/9, volume 9/9, organization
  5/5, chapter 8/9, ability-pool 4/6.
- Holdouts (3): csm-dim-chap-01 (Chapter 1, numeric-collision family,
  missing 2/3 with subject); csm-abl-pool-140 (Falling Devil Body
  Control, missing 3/3 — subsection-width defect); csm-abl-pool-358
  (Yoru Biru Ken, missing 3/3 — width).
- Reading: the 48 rows are answerable TODAY through the supported
  subject parameter; the no-hint entity-focus path is the sole blocker
  for 45 of them. D7 fix = route the question's page subject by default
  (engine change → full 4-gate suite + JJK regression + official
  no-hint regrade must move the same rows). The 3 holdouts need
  subsection-recall work beyond focus routing.

## Re-vote verdict: WITHHOLD A20 again (2026-09-18)

Full record: `reports/csm/COUNCIL_csm_d6_revote.md` (5 advisors
sequential → 5 blind reviews sequential → chair; advisors 3 WITHHOLD / 2
STAMP — same split; reviewers Converged C-strongest / D-blindest again).
Chair WITHHOLD with exact remains: (1) prove the 48-row limit — one
pre-registered, independently-registered ranking probe predicting a
specific red→green flip by rank threshold, run and green; no probe, no
limit; (2) close the blackout — observable OOM signal or declare harness
untrusted + injected-halt test proving guards fire; (3) meet empty
literally — JJK diff byte-empty from committed build-IDs, no /tmp
citations, no probe-artifact exemption. Decisive supplements: 21 floor
rows are Phase-2-tracked (retest_trigger AFTER PHASE-2 on all 21), not
D6-failed — full 69 ledger now 48 amended + 21 floor + 0 unregistered.
One thing first: the single falsifiable ranking probe (if it flips,
items 1+3 fall together; if not, D7 has its first negative result).

**Status: D6 WITHHELD ×2. Next = the falsifiable ranking probe.**

## DERIV leg: FALSIFIABLE PASS (not closed win; confirm + commit pending)

Recorded per results-chair order (defeasible until promotion rule
passes): verbatim-title + possessive-owner deferral + router-kept
derivation measured 4 predicted flips (vol-10/org-05/org-06/arcn-01),
0 counter-flips, blind 19/19, eval-jjk 31/31, OOS200 194 (floor 166),
green30 zero flips, bar-qa 13/26. Bank 469/486.
- git SHA: `90206940` + uncommitted derivation diff
  (`scriptengine/api/context.py`, verbatim + possessive-deferral).
- instrument-hash (context.py + p23_grader.py + census_dimensions.py
  + span_recall.py, sha256-16): `0d882cb9dd57b9dc` — re-verify at
  CONFIRM time; any drift voids this record.
- judge identity: `tools/census_dimensions.judge` (≥2/3 expect
  terms) over `span_recall.served_text`, via in-process
  `api.main.context`, mode qa, subject None, CENSUS_DEVICE=cuda.
- reconstruction command: `CENSUS_DEVICE=cuda
  ./scriptengine/.venv/bin/python tools/csm/p23_grader.py`
  (writes `reports/csm/census_widened_csm_results.jsonl`).
- promotion rule (all must hold): identical-config confirmatory
  regrade reproduces 469 with the same 4 flips + 0 counter;
  independent blind re-run 19/19; OOS/green30 recomputed exact;
  owner word; pre-commit gates green; then commit derivation diff
  only.
## A20 STAMP APPLIED — D6 CLOSED (2026-09-18)

Landing council conditions all posted: commit `9ef7082e` (spike +64,
sole code delta) → post-commit whole-card re-gate green (pytest
1,329+2x, eval 31/31, span 48,572+398/400, canon baseline, p23 463/486
reproducing +46/−0) → JJK-exact (artifacts only) → register 46→green +
16-row docs verified. Marker `reports/csm/D6_CLOSE_A20.md`; ledger key
`d6_close` in `GATE_LEDGER.json`; flip list
`receipts/d6_probe/CONFIRM_FLIPS.json`. 69-ledger: 46 green + 7 D7
limit + 16 Phase-2 floor + 0 unregistered. D6's pass test holds on
every clause. What remains is NOT D6: 7 width/collision holdouts (D7)
+ 16 floor rows (Phase 2) + the Phase-2 extraction campaign.

**Status: D6 CLOSED (A20). Next = D7 holdouts + Phase 2.**

## Ranking probe result: RED — D7's first negative result (2026-09-18)

Pre-registration: `reports/csm/receipts/d6_probe/PROBE_PREDICT.md`
(certified pre-run with FAIL→fixes applied verbatim); runner
`tools/csm/d6_probe.py`; result `PROBE_RESULT.json` (build fingerprinted:
HEAD `db53ec4`, events 333, chunks 7,797, final_top_k 8, cuda).
Row csm-dim-arcb-05 ("What happens in the Katana Man arc?"), gold chunk
4988 ("Katana Man arc / Synopsis" L1, carries all 3 expect terms):
- P1 true: in-process qa bundle (exact p23 path) reproduces MECH_RED,
  missing all 3; 8 beats led by the Katana Man card.
- P2 FALSE: 4988 NOT in top-8, NOT in dropped8 (22 dropped), NOT in
  top-50, NOT in dropped50 — never shortlisted at all. The top-8
  passages match the bundle beats doc-for-doc (honesty control holds),
  so this describes the product path faithfully.
- P3 true: bundle + gold beat → MECH_GREEN, hits all 3.
Probe verdict RED per the registered map ("absent top-50+dropped →
deeper gap, never retrieved"). Consequence: the D7 filing's defect
sentence was imprecise — the mechanism is UPSTREAM of ranking
(candidate generation / entity focus locks the character; the arc
Synopsis never enters the shortlist), not card-over-Synopsis ordering.
The 48-row defect text is corrected accordingly (same surgical method);
bucket (D7 named limit) and owner stand. Remain #1 unresolved: the limit
is still unproven — the follow-up is a focus-resolution spike, then the
D7 leg proper (gated engine change + JJK regression + regrade).

## D7 re-score window (council #36): Leg A (TIERED) PASS / Leg B (ABILWIDTH) RED — window 2026-09-18, recorded 2026-09-20

The LEGS-FIRST-FLAGGED verdict was executed by the detached kill-window
chain `tools/csm/d7_window_chain.sh` (Qwen 135k owner-manual stopped →
whole card to the window → restore; receipts `reports/csm/receipts/
d7_window/`, chain `RECEIPT_DONE`). The chain's own model call died with
its Qwen (by design); this section is the record the window owed,
reconstructed from the receipts. Flags `SCRIPTENGINE_TIERED_RECALL` /
`SCRIPTENGINE_ABILWIDTH_RECALL`, both default "0" (the Q2 flag gate
landed in checkpoint `4a8616bd`).

- **Leg A (TIERED=1, ABILWIDTH=0) — PASS** (`LEGA_targets.log`):
  W = 473/486 (bank 469, +4/−0); registered flips {arcn-02, arcn-10,
  org-03, state-08} all MECH_GREEN; 0 counter-flips; blind 19/19 (0
  errors, 33.8 s); OOS200 168→198 (Δ+30); green30 0 flips; `d6_flip`
  rc 0. **FLOOR A: 3/16 flipped** (arcn-02, arcn-10, state-08) — 13 of
  the 16 floor rows remain.
- **Leg B (TIERED=0, ABILWIDTH=1) — RED** (`LEGB_targets.log`):
  W = 469/486; both registered targets flipped (pool-140, pool-358)
  **but 2 counter-flips {pool-149, pool-252}** ⇒ RED per the
  pre-registration (bar: 0 counter-flips). Blind 19/19 (25.6 s);
  OOS200 168→195; green30 clean. **FLOOR B: 2/16 flipped** (pool-140,
  pool-358). Kill clause (D59): the ABILWIDTH hunk stays behind its
  default-OFF flag (unset = inert); no ex-post re-tuning. The width
  class (pool-140/358) needs a design that does not counter-flip
  pool-149/252.
- **Leg C (both ON) — not run** (halt at the first RED leg; the chain
  still ran the four standing gates for the record, then restored Qwen).
- **Standing gates, both flags default-OFF (= committed-tree behavior =
  `20d6da4e`):** pytest **1,331 collected = 1,326 passed + 2 xpassed +
  3 known env-mc** (the W1 pin shape, :8000-down window conditions) ✓;
  eval jjk **31/31** ✓; span-recall jjk **48,572/48,572 offline rc=0 +
  398/400 live (99.5% ≥ the 390/400 bar)** ✓ (the chain's own CUDA
  `:8000`, Qwen stopped); canon opm — the window's step hit "no server
  on :8000" (mechanical miss: the chain pkilled `:8000` after the span
  probe, before canon); **re-run 2026-09-20 (run dir
  `reports/2026-09-19-2004/`)** on CUDA co-located with Qwen 138240
  (short bounded task, ~5.3 GB within the 5,986 MiB headroom; GPU peak
  31,393 MiB; Qwen alive before/after; `:8000` restored to CPU after):
  **236/236 canon, 10/16 exact, 79.0% closed-set precision, 0
  confident-and-wrong** ✓. **All four gates green on tree `0c8cc953`
  (flag-OFF = `20d6da4e` behavior; the `4a8616bd` hunks are flag-gated
  dead code — gate-relevant diff `4a8616bd..0c8cc953` empty).**
- **Red state after Leg A (TIERED ON): 473/486 = 13 reds.** Per the
  window's instrument (`tools/csm/check_targets.py` FLOOR16: "the 16
  Phase-2 floor rows = the 17 git-HEAD p23 reds minus the org-03 D7
  holdout"), **all 13 remaining reds sit inside the 16-row Phase-2
  floor list** (pool-140/358 are in FLOOR16 even though the D7 spike
  labels their defect class "width" and the D6 close registered them as
  D7 named-limit holdouts). Whether that leaves Phase 1 at the
  extraction floor (halt) or pool-140/358 still Phase-1-closeable is
  the close council's call, not the window's.
- **Post-commit flag configuration (R5):** both flags ship default-OFF;
  the CSM p23 grades run flag-ON; the standing gates run default-OFF.
  The TIERED default-flip (ship CSM default-ON) + its 4-gate re-run +
  this record = **DEFERRED, a separate owner decision**.
- **Next:** council #37 — (a) the ABILWIDTH kill-clause disposition
  (revert the inert hunk vs keep it dead behind the flag); (b) the
  Phase-1 close determination against the halt rule (all 13 remaining
  reds in FLOOR16 → official suite → VOID formal →
  `PHASE_A_COMPLETE_AT_FLOOR.md` + halt at the floor, or a final width
  leg for pool-140/358); (c) the TIERED default-flip = owner decision.

## D7-CLOSE (council #37): PROVISIONAL close re-stamp — Phase 1 closed at the re-stamped floor (2026-09-20)

Council #37 (receipt `reports/csm/receipts/council_d7_close/`:
`framed_question.md`, advisors A–E `advisors.md`, peer reviews R1–R5
`reviews.md`, chairman ruling `chairman.md`) ruled **CLOSE NOW via a
PROVISIONAL council re-stamp** (carries A/B/C/E close-now + D's
constraints through R5's bridge; Q2 unanimous). The VOID formal
(R4's 3 model-free checks, executed pre-stamp, receipt
`receipts/council_d7_close/VOID_FORMAL.md`) passed **3/3**:
(1) reboot_rule — gate-relevant diff `4a8616bd..HEAD`
(`scriptengine`, `series/csm/overrides.yaml`, `tests`) empty,
last_green green @`0c8cc953`; (2) `d6_flip` rc=0 with census state
**declared** (live/worktree = 469-era product state; campaign 473
cited from the committed ledger legA entry — never the silent
469v469); (3) A20's 46-row `CONFIRM_FLIPS.json` ∩ 13 reds @473 = ∅
(13 derived as 17 @469 − FLIPS A; cross-checked = FLOOR16 − {arcn-
02, arcn-10, state-08}).

- **Register 22 → 24; halt meter 35 → 37 (24+10+3; fixed-register
  semantics; 35 = the superseded P1.4 stamp; the 10 now-green floor
  rows are a staleness note, not a strike — 3 of them are flag-ON-
  only greens, so striking is not provable for the flag-OFF product
  state).** The 2 pool rows join the floor as the width-class P2
  retest. Halt rule: UNMET as registered (pool-140/358 ∈ the A20 D7
  holdout register, ∉ register-22 — R1 item 6, verified), **met via
  the provisional re-stamp** (D's governing share, verbatim: "halt
  rule unmet-as-registered, met-via-provisional-stamp").
- **Close register — 13 reds @473/486: 11 extraction-gated dim rows
  ⊂ register-22 (owner: P2 extraction track / 5.4 re-adjudication;
  retest: post-extraction re-grade) + 2 width-class rows
  {csm-abl-pool-140, csm-abl-pool-358} (defect: width — subsection
  recall; gold ranks 12–47 cut at 8; owner: P2 width leg; retest:
  owner-triggerable per the width-class trigger line).**
  **PROVISIONAL: council-ratified (#37); owner-ratified-by-return;
  void on veto.**
- **FLOOR16 relabel (bookkeeping, not re-scope): 14 floor + 2
  ratified-width**, ratified as the 473-era denominator; register-22
  remains the historical P1.4 stamp (`PHASE_A_COMPLETE_AT_FLOOR.md`
  22-row section stands as history).
- **ABILWIDTH (Q2, unanimous): keep dead behind its default-OFF
  flag; no standalone revert** — flag-OFF is byte-inert (R1 item 4,
  code-level); a revert owes a 4-gate re-run + owner word for zero
  behavior change and burns the P6 seed + the Leg-C union
  (`check_targets.py:39`). Trap-stamp: measured RED (counter-flips
  {pool-149, pool-252}); enable only via a new pre-registered
  instrument + 4 gates. P6 seed = `_owner_attribute_hit`
  (`context.py` ~474). An optional revert may ride the TIERED-flip
  window (owner option 3).
- **TIERED default-flip (Q3): owner decision, post-close, its own
  gated engine window.** Bar: one-char commit (`context.py:583`
  "0"→"1") + 4 gates flag-ON (pytest 1,331 / eval jjk 31/31 / span
  48,572 + probe ≥390/400 / canon 236/236·10/16·79.0%) + p23 473/486
  repro, with JJK non-regression at flag-ON (the flag changes JJK
  bundles — tier-2 append). Any gate RED ⇒ no flip (flag stays
  default-OFF; the campaign grade stays flag-ON, R5). Not part of
  this close.
- **Width-class trigger line (pre-registered):** "Width-class
  (pool-140/358) Phase-2 retest, owner-triggerable: one new
  pre-registered instrument — a class-scoped top_k=30 campaign (NOT
  an ABILWIDTH re-tune; D59 bars Leg-B knobs). Bar: flips ⊇
  {pool-140, pool-358} AND 0 counter-flips vs {pool-149, pool-252};
  blind 19/19; OOS200 floor (drop < 3 vs `D6_OOS_PRE`); `d6_flip`
  rc=0. RED ⇒ kill clause: rows stay P2 floor-registered; no ex-post
  re-tune." (A new width leg post-freeze would be a #34 floor-moving
  act — D59 closed the leg, not the class; the class-scoped top_k=30
  vehicle was never run.)
- **Claim-scope line (time-stamped):** "[stamp-commit 78323240,
  2026-09-20] CSM Phase 1 closed at the stamped floor: campaign grade
  flag-ON 473/486; shipped product (flag-OFF) 469/486; 13 reds = 11
  extraction-P2 + 2 width-P2 (PROVISIONAL, owner-ratified-by-return,
  void on veto); JJK remains 100% (4 gates @`0c8cc953`). This line
  is amended by the TIERED flip (owner option 3) if ordered."
- **Owner's decision set on return:** 1 "Commit" = ratify close +
  re-scope → stamp final (the 100% claim stands in full form); 2
  "Commit without sign-off" = close stands as a council stamp, re-
  scope pending (the 2 pool rows stay holdout-pending-ratification);
  3 "TIERED flip word" = the gated engine window per the Q3 bar; 4
  "None — status quo" = the provisional stamp is voided (docs-only
  reversal), the close reverts to "D7 window closed, close deferred",
  the pool rows revert to D7 holdouts, council reconvenes or P2
  opens them.
- **Attribution note (R1):** 463→469 closed-6 = 4 deriv {arcn-01,
  org-05/06, vol-10} + 2 Q1-L1 {csm-dim-chap-01, csm-dim-arcn-07} —
  "the 2 unattributed" was a ledger artifact (D61/63 tracked the
  deriv leg only; drift D57:2093 "bank 465").
- **Auditability fix (in this close commit):** the 473-era evidence
  is committed, not claim-only on a fresh clone — the `LEGA_*.log`
  set is force-added (gitignored `*.log`) and the canon re-run dir
  `reports/2026-09-19-2004/` is tracked.
