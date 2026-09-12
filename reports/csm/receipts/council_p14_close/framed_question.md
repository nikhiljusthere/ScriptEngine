# Framed question — CSM P1.4 close council (2026-09-12)

**Question: Ratify the CSM Phase 1 (P1.4) close at the documented floor and
authorize the `PHASE_A_COMPLETE <ts>` marker (`reports/master-work/phase_status.txt`)
+ `reports/csm/PHASE_A_COMPLETE_AT_FLOOR.md` — or hold for fixes?** Phase 2
(P2.1: ~51 GPU-h tier-1 x 3 doors; P2.3: D6 extraction campaign) may start only
after the marker; its gate reads "marker present" and nothing else (plan A20).

State on disk (raw receipts cited; if you doubt a number, read the cited file
before judging):

1. **Four-gate copy** (P1.4, @`407c016`, stamp `af382ee`): pytest **1,321**
   (1,316 passed + 3 known env-mcp trio failures under a stopped :8000 + 2
   xpassed) / eval jjk **31/31** / span-recall jjk **48,572 offline rc=0 +
   398/400 live (99.5%)** / canon opm **236/236, 10/16 exact, 79.0%** —
   `reports/2026-09-11-2218/`, `GATE_LEDGER.json p14_close_copy`, drift D24.
2. **Miss queue at the documented floor** (D23 convergence PASS @`407c016`):
   35 open = 22 extraction-gated floor (21 `csm-dim-*` 1:1 with D6 census reds
   + `csm-char-04` R-7x) + 13 residuals; the halt meter counts only the 33
   fixable rows; no regression / no no-reduction iteration fired in iter-1
   (R-1..R-7 all green, `407c016`).
3. **5.4 re-adjudication** (council R6; executed 2026-09-12): 34 s one-copy
   census re-run — **21/21 reds identical** to the 09-09 run, **0 closed, 0
   new regressions** => no de-scope; the 22-row floor stands; the 5.4 gate
   stays LIVE; P2.3 in scope. `receipts/census_5_4_readjudication_p14.md`.
4. **Close conditions (a)–(e)**: (a) campaign-todos synced
   (`plan/SWITCHPOINT.md`); (b) C3 doc-hygiene commit `e411214` landed;
   (c) `reports/csm/GATE.md` exists (live state updated to the P1.4 copy);
   (d) bar-audit pre-registered before the marker:
   `reports/csm/bar_audit_p14_preregistered.json` (26 panel-line cases over
   the 6 D6 classes, 3-5 each, 78/78 expect terms verbatim-verified
   model-free vs `series/csm/facts.db`; authored by a fresh-context subagent
   — the executor never edits its oracle, campaign-council D4);
   (e) R-6 floor-inheritance verdict recorded (drift D21: an alias-resolved
   subject inherits the level-0 card via the floor; the qa-seam residual is
   documented for the Phase-2 re-probe).
5. **One known open finding:** the env-mcp trio live proof was 2/3 — bare
   character name "Maki Zenin" routes `qa` (`router.py:809-812`), mismatching
   the test's narrative intent; pre-existing since `8d07487` (predates the
   test by a month), a JJK routing change is forbidden mid-wave, deferred to
   P1.5; gate-1 pin 1,321 unchanged.
6. **Pre-registered coverage-denominator item**
   (`reports/csm/CLOSE_COUNCIL_PREREREGISTERED.md`, 2026-09-10, Q1-Q4): a
   campaign "100%" claim must state its denominator — at writing JJK
   893/987 (90.5%) vs CSM 0/537 (0.0%); CSM in-scope remainder 227 pages; the
   D6 dimension census (60 questions) covers only the 6 character-page
   dimensions (no chapter/volume/episode/org/establishment questions);
   chapter/episode summary content = 90,421 words / 243 sections. The council
   must answer on disk before Phase 2 commits a GPU-day. **New fact since the
   item was written:** the CSM per-page campaign advanced —
   `coverage_report.py` 2026-09-12: CSM **175/537 (32.6%)**, 1,260 questions,
   in-scope remainder 52.
7. **P1.5 (MCP bridge) is owner-directed:** the directing session executes it;
   B skips it and goes straight to Phase 2 after this council passes.

**Decide:** (i) APPROVE / HOLD the close + marker (A20: marker only at the
documented floor); (ii) rulings on Q1-Q4 (does the 22-floor / "100%" claim
need a denominator caveat; does CSM owe a per-page campaign before or
alongside the Phase-2 extraction — the page campaign now stands at 175/537);
(iii) treatment of the env-mc finding (defer to P1.5, or fix before the
marker); (iv) anything else that should block Phase 2 (P2.1 step-0
sanity-100 go/no-go, P2.3 extraction scope, the 200-row held-out leg).