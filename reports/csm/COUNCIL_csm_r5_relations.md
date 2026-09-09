# COUNCIL — CSM iter-1 R-5 relations-mode package (2026-09-09)

## Question

Approve / amend / reject the **R-5 (G-CSM-4) relations-mode package**: a 4th
router mode `relations` (the `_RELATIONS` trigger in `scriptengine/retrieve/
router.py`), a budgeted relations bundle builder (`scriptengine/api/context.py`
`_relations_context`, `rank_relations`), and the MODES/endpoint update
(`scriptengine/api/main.py`) — the §9a pre-registered fix class that makes the
`relations` channel (facts.db, 11,261 csm edges) reachable for
relationship-shaped queries, which auto-routing sent to `roster` (0/11 in the
relations bank). Package as drafted: +223/−4 over 5 files (draft diff frozen
in `reports/csm/receipts/council_r5/package_diff.md`; reconstructed frame in
`frame.md`).

## Members

11: 5 advisors + 5 peer reviewers + chairman. All zero-GPU, read-only (each
member could write only its assigned receipt), fresh context, no member saw
another's response.

| Letter | Role | Verdict | File |
|---|---|---|---|
| A | The Executor | **OBJECTION** — `\bconnection\b` over-matches 11 qa-pinned non-relationship questions | `adv_A.md` |
| B | The Contrarian | **OBJECTION (amend)** — tighten alt-5 | `adv_B.md` |
| C | The First Principles Thinker | APPROVE | `adv_C.md` |
| D | The Outsider | **OBJECTION** — no roster-style empty-pair fallback (halt risk on empty-pair firings) | `adv_D.md` |
| E | The Expansionist | APPROVE | `adv_E.md` |
| R1–R5 | Peer reviewers (weighted to failure modes) | see `rev_1.md` … `rev_5.md` | `rev_N.md` |
| Chair | Chairman (this record) | **AMEND** | `reports/csm/receipts/council_r5/chairman.md` |

**Method note:** sequential — one member at a time (owner rule 2026-09-08,
the 5-parallel convention retired for CSM; the 2026-09-09 parallel override
applied only to the p1/p2 plan councils, ledger #25/#26). The 5 advisor
rulings were recovered from disk after the boot session crash; the 5
reviewers + chairman ran as one serial async workflow @100k (high thinking),
each reading its seed from disk (frame + package diff + prior receipts).

## Verdict

**AMEND** — the relations door is the right fix for G-CSM-4 and the bundle
shape is sound (C, E), but the package ships only with A1–A5 (below). The
chairman's full reasoning, per-finding adjudication and the governance-
addendum answer: `reports/csm/receipts/council_r5/chairman.md`; independent
claim verification + two corrections to the chairman's own record (re-pin
class is 68 rows, not ~34; fallback vs re-pin have separate roles):
`reports/csm/receipts/council_r5/b_session_verification.md`.

## Amendments (all applied, 2026-09-09, session b)

- **A1** — `router.py`: `_RELATIONS` tightened to 4 alternatives
  (documented-relationship / relationship-of-with-to-between / how-is-related
  / how-does-relate); dropped `\bconnection\b` (rev-4: 20 bank hits, zero
  official-gold), the bare `\brelationship\b` over-capture (episode-anchored
  prose + "relationship status"), and the who-branch verb-phrase over-
  captures ("Who is left to stand against…", "Who was chosen to be…").
  Bank sweep: 233 → 79 firings; 0 new hits in official + eval banks.
- **A2** — `context.py`: budget-unit bug (rev-2) — the guard compared token
  costs against a char-unit budget (3.6× over-permissive); now token-units.
- **A3/A4** — empty-pair relations→qa fallback (D): `api/main.py` (auto-only),
  `cli.py` (unconditional, matching the local roster style), `script/
  writer.py` (auto-gated, matching its local roster style); `mcp/server.py`
  untouched (thin proxy — D's "4 caller sites" corrected by rev-4 to 3).
- **A5** — `tests/test_router.py` store-free trigger-boundary test (4
  positive / 7 negative) + `tests/test_context.py` `test_relations_budget_
  units`; gate-1 pin 1,305 → **1,315**.
- **Residual 4 (bank curation)** — 68 rows (39 qa + 29 roster) re-pinned
  `expect_mode: relations` in 25 `_`-batch files; re-bind debt 222 → 0
  (deterministic list from the post-amendment sweep).

## Gates (raw receipts `reports/csm/receipts/iter1_r5_gate.md`)

All four standing gates + eval jjk GREEN after the amendments (2026-09-09
~23:50Z): pytest **1,315 collected** (chairman's pin), 0 failures attributable
to R-5 — one mcp bare-name failure **proven pre-existing at HEAD** (stash +
fresh `:8000`); eval jjk 31/31; span-recall jjk offline unreachable 0 + live
probe 398/400 (99.5%); canon opm 10/16 exact, 236/236 canon, 79.0%. R-5 meter
0/11 → **5/11 complete** (the ≥1-HIT wave bar); 5 partials proven harness
budget-trim (all expected names present at `token_budget=60000`; e.g. facts.db
holds 168 Denji relation rows) + 1 content gap (Chocolate — 1 relation row in
the store → Phase-2 extraction). Sweep raw:
`reports/csm/receipts/iter1_r5_relations_sweep.md`.

## Carried to the close council (numbered)

1. **Pre-existing mcp bare-name mismatch** — `test_research_bare_character_
   name_is_narrative` fails at HEAD: the router's bare-name rule (8d07487)
   routes a bare character name to qa, the test's stated intent (d531329) is
   narrative. Out of R-5 scope (fixing it changes JJK routing; the baseline-
   exact invariant forbids a routing change mid-wave).
2. **Meter harness budget-trim** — `tools/csm/validate_relations.py` runs at
   a small default `token_budget`; 5 of 11 rows trim. Sizing the harness
   budget is a tooling fix, not an engine fix class.
3. **R-6 floor-inheritance** (council_r2r3/chairman.md findings 6/8:
   `closed_members` / alias-inherited rows) — answer before the first
   Phase-2 GPU-day.
4. **Governance addendum answer** (slim 4-member form for narrow classes;
   20-turn checkpoint) — answered in `chairman.md`, recorded for the close
   council's process record.