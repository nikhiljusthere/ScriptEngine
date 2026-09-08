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

## R-5 · G-CSM-4 — the relations door is unreachable through auto-routing

- **Mechanical expectation.** The relations-bank questions (`expect_mode: relations`,
  `csm-rel-05`/`08`/`09`/`02`) auto-route to **`roster`** (there is no `relations`
  router mode), and the `relations` channel exists only on qa-mode bundles, so all
  four return **0** (the bank sits at 0/11).
- **Gate.** door (relations).
- **Fix class.** **engine** — a `relations` router mode (named owner = CSM-7 fix
  phase, council COUNCIL_csm-1b-2 Ruling 3).

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