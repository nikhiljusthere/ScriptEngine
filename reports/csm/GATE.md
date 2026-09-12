# CSM gate — the four standing gates, live state

The CSM campaign (Phase 1, §9a closure loop) runs the **same four standing
gates** the JJK campaign uses, because every CSM engine change must not
regress the JJK baseline (JJK stays at 100%). Nothing here is graded — the
gates are mechanical (counts, string/foreign-key equality); they report, they
do not judge.

The four gates (re-run after every fix-class, before calling it done):

1. **gate-1 — `pytest tests/ -q`** (in-process, CUDA): the full suite green.
   Current pin **1,321** (1,318 R-6 pin + 3 new R-7 tests; the only failures
   are the known env-mcp trio under a stopped :8000, 2 xpassed).
2. **gate-2 — `eval --series jjk`**: **31/31 (100%)** gold.
3. **gate-3 — `span-recall --series jjk`**: **48,572/48,572 offline (rc=0)**
   + a 400-probe (seed-rotated; the live window must clear the 390/400 =
   97.5% bar).
4. **gate-4 — `canon-run --series opm --skip-eval`** (one-copy rule):
   **236/236 canon (100%)**, 79.0% closed-set precision, 0 confident-wrong.

## Live state

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
