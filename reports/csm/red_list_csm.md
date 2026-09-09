# CSM pre-registered red list — expected failures, written before Wave-2 execution

**Frozen: 2026-09-09.** Plan §5.5.3 — "a pre-registered red list of expected
failures, written before the wave." Every entry is **mechanical** (a count
comparison, a substring/span-presence check, or a router-mode check) — no LLM
judged entries, by the CSM-5 no-judge ruling. The §9a closure loop's miss queue
pre-triages against this list: a hit here is a *known* debt, not a finding.

Sources (all on-disk receipts from the 2026-09-08 cycle):
`reports/csm/CSM3B_GATES.md` §3 (seed bank), `reports/csm/CSM1B_BANK_VALIDATION.md`
(G-CSM-1..4), `reports/csm/GCSM1_ROSTER_DOOR.md`, `reports/csm/CSM1B_RELATIONS_BANK.md`,
`reports/csm/CSM3B_PRESTEP.md` §4 (roster probe), `reports/csm/COUNCIL_csm-1b-2.md`.

---

## R-1 · G-CSM-1 — count phrasings bypass the declared-roster door

- **Mechanical expectation.** `route("csm", "How many special divisions exist in
  Public Safety Devil Hunters?").mode == "qa"` (not `"roster"`); the qa bundle for
  `csm-set-14` returns **0 members** (recall 0/5) and `csm-set-15` recall 0/4. The
  roster door itself serves 5/4 correctly in declared mode
  (`reports/csm/GCSM1_ROSTER_DOOR.md`) — the debt is the *routing*, not the door.
- **Gate.** bank (d5 reachability via the roster door).
- **Fix class.** **engine** — the router's count rule (`scriptengine/retrieve/router.py`,
  rule 2 / `_resolves_a_set`). CSM-3's door work. *Not* a per-wiki override: the
  declared rosters already exist in `series/csm/overrides.yaml`; only the routing is broken.

## R-2 · G-CSM-2 — the qa passage leg returns nothing for CSM subject-named questions

- **Mechanical expectation.** The qa bundle for "What is Denji's hybrid
  transformation trigger?" (`subject: "Denji"`, `csm-fact-06`) contains **0
  passages** and does not carry the verbatim span `pulling a cord on his chest`.
  The store floor is intact (the `Denji` document yields 90 passage rows, verified
  2026-09-09) — the debt is the *bundle* leg (budget/ranking), not the store.
- **Gate.** bank / d5.
- **Fix class.** **engine** — the qa passage/retrieval leg. **Not** the extraction
  prompt: council CSM-1b-2 Ruling 2 — the prompt correctly returned `[]` (the wiki
  never names the PM contract as an ability); a prompt patch would be cached and
  would not fix it.

## R-3 · Roster-door shortfall — the `Devils` roster probe serves 31 of 88

- **Mechanical expectation.** The declared `Devils` roster (88 members) door probe
  serves **31 of 88** members (16,231 chars, `truncated=true`) — a budget floor,
  not the full 88. Pre-CSM-3b Ruling-1 this line shape served 31 members / **0
  chars** (every roster probe structurally MISS_DOC); post-fix (`f93d396`)
  31 / 16,231. The N=100 roster-sanity escalation is **not** triggered (the yield
  matches the `GATE.md:757` re-probe).
- **Gate.** door (roster).
- **Fix class.** **engine** — the roster-door token budget / `served_text`
  flattening (CSM-3b Ruling 1 already landed `f93d396`; the 31/88 is the residual
  budget floor, documented, not a new failure).

## R-4 · G-CSM-3 — section-scoped intruders on closed-set asks (precision)

- **Mechanical expectation.** Closed-set asks return **intruders** beyond the
  correct set:
  - `csm-set-17` ("members of Tokyo Special Division 4"): returns 14 vs the 7
    closed members — 7 category-page intruders (Kishibe, Angel Devil, Beam,
    Galgali, Princi, Fushi, Madoka).
  - `csm-char-03` ("Every ability of Aki Hayakawa"): 18 vs 11 — form headings, an
    `Enhanced Reflexes` trait row, 4 `Antemortem Abilities / Devil Contracts` rows.
  - `csm-set-02` ("Every ability of Power"): 18 vs 13 — form headings + 3 trait rows.
  - `csm-set-01` ("Every form of Denji"): 7 vs 4 — a form heading + 2 prose rows.
- **Gate.** bank (precision on closed sets).
- **Fix class.** **engine** — the chunker skip set /
  `effective_boilerplate_sections` + section scoping (CSM-3's item). The intruders
  are *real* wiki rows; the fix scopes the door to the question, it does not
  delete members.
- **ID-mapping addendum (council R-2+R-3, 2026-09-09).** The miss queue
  (`reports/csm/miss_queue_csm_iter1.jsonl`) and this red list use colliding
  `R-3`/`R-4` spellings, so the join is pinned here once: queue `fix_class R-3`
  scoping rows (`csm-set-17/02/01`, `csm-char-03`, `red-R-3`) = this row
  (**R-4**, G-CSM-3); queue `fix_class R-3` row `csmdoor-01` = red-list **R-3**
  (the 31/88 roster-door budget floor, landed `f93d396` — expected *invariant*
  at sweep time, a regression on it is a new miss = halt); queue
  `fix_class R-4` / `R-4/R-2` rows (`red-R-4`, `csmd5-01..07`,
  `gate400-188/189/211/320/490/542`) = the d5 line-miss class (override-first;
  fix leg = the R-2 qa-passage leg; no red-list row of its own). One spelling
  per debt; the queue↔red-list join can no longer be read two ways.

## R-5 · G-CSM-4 — the relations door is unreachable through auto-routing

- **Mechanical expectation.** The relations-bank questions (`expect_mode: relations`,
  `csm-rel-05`/`08`/`09`/`02`) auto-route to **`roster`** (there is no `relations`
  router mode), and the `relations` channel exists only on qa-mode bundles, so all
  four return **0** (the bank sits at 0/11).
- **Gate.** door (relations).
- **Fix class.** **engine** — a `relations` router mode (named owner = CSM-7 fix
  phase, council COUNCIL_csm-1b-2 Ruling 3).
- **CLOSED 2026-09-09 (iter-1 R-5 wave, council_r5, 11 members + addendum, AMEND
  with A1–A5).** The `relations` router mode + budgeted bundle builder landed
  (router.py `_RELATIONS`, context.py `_relations_context`, main.py MODES/door);
  amendments A1–A5 (tightened trigger, budget-unit fix, empty-pair qa fallback,
  store-free tests) + the 68-row bank re-pin. Four standing gates + eval jjk
  GREEN; R-5 meter 0/11 → 5/11 complete (≥1 HIT bar met). Residuals, carried to
  the close council: (a) the meter harness's small default `token_budget`
  budget-trims 5 rows (proven: all expected names present at `token_budget=60000`);
  (b) csm-rel-03 Chocolate content gap (1 relation row in the store → Phase-2
  extraction). Raw: `reports/csm/receipts/iter1_r5_gate.md` +
  `iter1_r5_relations_sweep.md`; council: `reports/csm/receipts/council_r5/`.

---

### Notes for the §9a executor

- A *hit* on any entry above is a **known debt**, not a finding — it was
  pre-registered here, before the wave ran. It flips to `closed` only when the
  corresponding engine fix lands and the mechanical check turns green.
- The fix class is load-bearing: R-1/R-2/R-3/R-5 are **engine** changes (they
  trigger the §3 council + the JJK-100% four-gate re-run); R-4 is engine too,
  though a per-wiki override in `series/csm/overrides.yaml` is the *preferred*
  first attempt where it can scope a skip set without a series name in `.py`.
- No LLM-judged entry may be added to this list. A failure whose expected output
  cannot be stated as a mechanical check (count / substring / mode) is a finding
  for the council, not a red-list row.
---

## Addendum — council R-1 records (2026-09-09, after the R-1 draft's §3 council)

These are records about R-1's blast radius, not new red-list rows (a red row
is a pre-registered mechanical debt; these are post-hoc records per the
council R-1 chairman's amendment 4).

- **db-flip record.** `series/db/overrides.yaml:291` ("how many gods of
  destruction exist across the multiverse") flipped qa→roster as a positive
  same-bug-shape delta. It is **pinned** (the db param row in
  `tests/test_csm_router_count_rule.py`) but **not stamped** in the miss
  queue: a stamp would unfreeze the R2 halt meter beyond the gate400
  precedent for a delta that is already tripwired and positively shaped
  (chairman's ruling, `reports/csm/receipts/council_r1_router/chairman.md`).
  The db suite has no count-question gold row in the four gates — an accepted
  residual.
- **Class boundary.** The fix fires only on `\bhow many\b` (`_COUNT`,
  `router.py:170`). "what is the number of X" / "how much" retain both
  sub-bug shapes (phantom `many` on the declared path; scope-stripping on the
  discovery path) and are **out of R-1 closure scope** — a future class.
- **Discovery-counting residual (named open item).** The kept prepositional
  phrase also completes *discovered* set names. Two live cases, both accepted
  with tripwires (pin + stamp + zero-new-miss pass criterion): onepiece
  "How many Sweet Commanders are in the Marines?" (serves the discovered 7-
  member "Marine Commanders" set — a wrong-set serving, no gate covers
  onepiece) and opm-set-16 (Blizzard; the only delta inside a standing gate,
  gate-4 pre-registered in the receipt). **Re-probe after R-7's key-map
  widening lands** (the `identity_fields` hook grows the discovered-set
  surface — the R-1×R-7 interaction). R-1×R-5: csm's declared "Every devil
  contract Denji has made" (3 members) will also route through the count rule
  before the CSM-7 relations mode lands — ordering to settle when R-5 is
  drafted.
- **Rejected layers (recorded so the search does not repeat).** (a) Roster-
  side stopword: the phantom is `many`, a **content word** in the roster
  matcher's stopword list (`scriptengine/retrieve/roster.py`) — a stopword
  list cannot close the csm-set-14 phantom (the door receipt's pre-fix
  `rejected: [__unverified__'many']` is the mechanism). (b) Mechanical
  name-guard for the discovery side: infeasible without breaking the pinned
  JJK/hxh wins — the Geto pin's basis "Suguru Geto Techniques" is not a
  contiguous substring of "named techniques does Suguru Geto have" (word
  order), the hxh Nen pin's basis "Nen Types" is a non-contiguous synonym of
  the asked "levels of Nen", and the Blizzard basis "The Blizzard Group"
  **is** contiguous — no name-presence/containment rule accepts {Geto, hxh}
  while rejecting {Marines, Blizzard} (chair-verified basis shapes).
- **Closure rule (as amended).** Pass = csm-set-14 AND csm-set-15 both HIT
  and zero new misses on the stamped rows; close only HIT rows; `red-R-1`
  closes when the class goes green; any open recall-row miss = halt to
  council (no partial close). The first-draft rule (≥ 1 HIT, then close all
  three) was unenforceable — a 1-of-2 partial satisfied it while closing a
  failing row (reviewer 4's finding, chair-adopted).
