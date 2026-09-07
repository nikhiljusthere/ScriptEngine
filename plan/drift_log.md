# drift_log.md — the map back to the trunk

## STANDING RULES — repeated in every plan document, deliberately

*Verbatim copy of `plan/STANDING_RULES.md`. Duplicated across `flow.md`,
`Plan_to_perfection.md` and `drift_log.md` so that reading any one plan
document is sufficient, even if work drifts far enough that only one is in
view.*

**1. No user input. None, for the duration of this plan.** Every wall where you
would normally stop and ask — a design fork, an ambiguous result, a blocked
step, a judgement call — **run `llm-council` instead.** The council decides;
you act on its verdict and record it. Do not ask for approval, which option, or
whether to proceed. The only stop is the halt path in `flow.md`, and that runs
a council first. Council claims are DB-verified before recording; one that
cannot be verified did not happen.

**2. The GPU is available. Do not default to CPU.** Qwen's compute idles while
a shell command runs, and its resident weights leave ~7.4 GB free on the 32 GB
card — enough for the ~5.3 GB retrieval stack. Tests, the `:8000` server and
the census run on GPU **without stopping Qwen**. *(Measured 2026-09-07:
ninfer-serve 24,670 MiB + a co-located retrieval process 6,186 MiB, 991 MiB
spare — co-location working under real load.)* Two qualifications: check
`nvidia-smi` free memory first and size the job against it, since with a job
already co-located the spare can fall under 1 GB; and a sustained 27B
extraction batch wants the card to itself (one OOM-crashed at 508/524 beside
the reranker). GPU is the default; CPU needs a measured reason.

**3. Council cadence — three mandatory points.** (a) **Every 2–3 completed
todos**, a council reviewing *the fixes just made* — did they do what they
claimed? (b) **At the end of every sub-list** (`1a–1d`, `X1.a–X1.f`), a council
assessing whether the sub-list actually completed, **before the return pointer
fires** — a sub-list is done when a council says the work holds, not when its
last line is reached. (c) **At every phase gate**, the gate council already
specified. Write each to `reports/comprehension/COUNCIL_<subject>.md` and
commit it with the work it reviewed. If it is not on disk, it did not happen.

---

**Why this file exists.** Work leaves the plan. A council redirects, a gate
fails, a diagnosis opens a sub-sequence — and three excursions later nobody can
say which document is authoritative or where the trunk was left. This file is
the map back.

**This is history, not status.** It is append-only: each entry records what
*happened*, which does not go stale. It never records what *remains* — that is
the claim that produced four phantom work items. `flow.md` holds structure,
this file holds history, status comes from a query. See
`Plan_to_perfection.md` §0.

---

## 1. Addressing

**The trunk is `flow.md`.** Its phases are the only authoritative numbering.
Address a trunk step as `P<phase>.<step>` — `P3.A`, `P0.D`.

**Everything else is an excursion.** An excursion is any ordered work that is
not a trunk step: a council-directed sequence, a fix loop, a diagnostic sweep.
Address it as `X<n>.<step>` — `X1.a`, `X1.b`. An excursion **never** takes a
phase number, even when its own internal notes use one.

> **The collision that made this necessary.** "Phase 5" currently means two
> different things: `flow.md` Phase 5 (the subjective-prose extraction phase,
> now closed) and the executing agent's own "Phase 5 Step 1–5" retrieval
> sequence. Both are internally coherent. Together they are unresolvable
> without this file. **From here: excursions get `X` numbers, never `P`.**

---

## 2. The return rule

**Every excursion's last item is a return pointer.** Not "continue," not "next"
— an explicit trunk address.

```
X1.a → X1.b → X1.c → X1.d → X1.e: RETURN TO P3.A
```

The rule holds recursively: an excursion spawned inside an excursion returns to
its parent's next item, and the parent still returns to the trunk. A todo list
without a terminal return pointer is malformed — **write the return item first,
when the excursion opens, not when it closes.** By the time it closes, the
reason it opened has usually been forgotten.

**A return pointer names where the trunk was left, not where it feels natural
to resume.** If an excursion discovered something that should change the trunk,
that is an edit to `flow.md` with its own drift entry — not a quietly different
return address.

---

## 3. Drift ledger

### D1 — Phase 5 closed early, becoming a verification excursion
- **Trunk step:** `P5` (subjective prose: Personality, Appearance, Overview,
  Trivia, History — ~106,000 words).
- **What happened:** `P1.A` (the held-out oracle) returned E1–E4 all passing —
  retrieval already served the Personality paragraphs. `flow.md` P5's own
  premise says the phase opens *only* if E1–E4 fail. Premise refuted, phase
  closed without extraction.
- **Why it is not a deviation:** the plan predicted and authorised this. P5 was
  written as conditional. The measurement removed the phase, which is the
  design working.
- **What it spawned:** rather than closing on n=4, a scaled verification —
  see X1.
- **Status of the trunk step:** closed. ~106,000 words need no extraction.

### D2 — the F-gate vocabulary
- **What happened:** the census work introduced local acceptance labels `F1`
  (breadcrumb component matcher), `F2b` (the acceptance test), `F3` (the
  tier-scoped gate).
- **Assessment:** a sub-vocabulary inside X1, not a numbering scheme. Harmless,
  but it is *not* a trunk address and must not be cited as one.

### D3 — X1, the retrieval-only sequence (the current excursion)
- **Opened from:** `P5` closure, by council
  (`reports/comprehension/COUNCIL_phase5-next-move.md`).
- **Its own internal name:** "Phase 5 Step 1–5". **Correct address: X1.**
- **Mandate:** prove at scale that retrieval *serves* the five prose dimensions
  P5 declined to extract. Retrieval-only — no 27B extraction, by council
  ruling, because the 27B path OOM-crashed at 508/524 when co-located with the
  reranker.
- **Items:**
  - `X1.a` F2b fix + gates + commit (`dedb949`) — done
  - `X1.b` build + validate the census harness — done
  - `X1.c` run the 545 census on GPU, summarise — done
    (`reports/comprehension/STEP5_CENSUS_545.md`: 98.7% reached, 0 main-cast
    misses, 7 not-reached, all minor tier)
  - `X1.d` fork — fix the 2 genuine faults, or close out and track — **open**
  - `X1.e` record the census milestone in the live docs — **open**
  - `X1.f` copy the harness into the repo — done (`tools/census_545.py`,
    `tools/census_545_pairs.json`)
  - `X1.g` **RETURN TO P3.A** ← added here; the excursion had no return pointer
- **Drift note:** X1 was opened without a return item. That is precisely the
  failure this file exists to prevent, and it is recorded rather than
  retro-fitted silently.

### D4 — P3 gains the P5 gate (a trunk edit, not a drift)
- **What changed:** `flow.md` P3 (ability depth) was written as extraction
  work: widen `abilities` to 146 characters, extract mechanics.
- **Why it changes:** P5 closed because a cheap retrieval measurement proved
  extraction unnecessary. The ability family has had **no such measurement** —
  no census, no oracle item, no report mentions Cursed Technique, Physical
  Prowess or Cursed Energy. Building extraction there without first running the
  test that closed P5 would repeat the mistake P5 avoided.
- **The edit:** P3 opens with a measurement step, and its extraction steps are
  conditional on that measurement, exactly as P5 was.

---

## 4. Current position

**Trunk:** `P0` done · `P1` done · `P2` done · **`P3` done** (P3.3C gate closed
`8e924aa`, CONDITIONAL GREEN; all five ability dims 3C-GREEN per
`P3A_ABILITY_CENSUS.md`) · **`P4` done** (4C closed D7; 4A durable D8
`61311c2` — interval facts re-land on every `index` via `extra_facts`; wiki-
wide 4B → backlog) · `P5` closed by D1 · **`P6` not started — blocked by the
2026-09-07 owner directive (JJK only; halt before P6)**.

**Excursion:** X1 **closed** (`ebe83cf`, end-of-sub-list council
`COUNCIL_X1.md`): X1.d 2 not-reached faults fixed + tracked (`a5e93c3`), X1.e
milestone recorded (`STEP5_CENSUS_545.md`; global not-reached 7 → 5, 99.08%,
the 5 residual sit in the 471-pair minor tier), returned to P3.A at X1.g.

**Excursion:** **X2 open (2026-09-07, D9 — the JJK d6-completion plan, council
row 19, `COUNCIL_d6-completion.md`)**. Items: X2.a council **done**; X2.b
Phase-0 door pre-check (roster/narrative doors exist + callable); X2.c
Phase-1 **R4 — place the 154 unplaced events** (the only non-contingent
build, and the narrative census is input-stale before it); X2.d Phase-2 door
censuses (roster + narrative, 100 fixed questions each, ≥99% reached, every
miss triaged); X2.e Phase-3 measurement (8-verb 100-sentence sample;
140-question per-dimension retrieval-not-extraction incl. outcomes +
causality; 50-question open-ended census; gate false-negative audit);
X2.f Phase-4 contingent extraction (R1 / outcomes / causality / R3 only if a
red measurement names it); X2.g Phase-5 done-declaration memo + standing
gates re-run; X2.h **RETURN: HALT before P6** (the owner directive closes the
trunk at P6-not-started; no cross-corpus work).

**The unmeasured block** — five ability dimensions, ~48,800 words — **was
measured at P3.A** (`P3A_ABILITY_CENSUS.md`, 315-pair pool, 3C-GREEN fork);
the paragraph below is the historical record of why P3 was next:
Cursed Technique 13,611 w, Physical Prowess 10,595 w, Intelligence 9,674 w, Intelligence 9,674 w,
Abilities and Powers 8,481 w, Cursed Energy 6,416 w — **~48,800 words with zero
measurement of any kind.** The census harness that answered this question for
the prose dimensions now exists in `tools/` and runs in ~9 minutes on GPU.

---

## 5. Adding an entry

Append; never edit a past entry. One entry per drift.

```
### D<n> — <one line: what moved>
- **Trunk step:** <P address, or "none — excursion">
- **What happened:** <the event, with the evidence: commit, report, or query>
- **Why:** <premise refuted / council ruling / gate failure / trunk edit>
- **Return address:** <P address the work rejoins, or "trunk edit — no return">
```

A drift entry is not an apology and not a justification. It is an address.

### D5 — P4's 4C gate found vacuous; re-scope routed to council
- **Trunk step:** `P4` (state over time; 4A model / 4B populate / 4C gate)
- **What happened:** DB-verified the 2C oracle (sha `a788fa`) B-group before
  building 4A: `B1` (expect fail) **PASS** (`contains` — the Angel-page Gojo
  quote is in the bundle), `B2` (expect fail) **PASS** (`value_match` — Geto's
  infobox `occupation` `Jujutsu Sorcerer (Former) Curse User` is served verbatim
  by the 2-prep fact floor), `B3`/`B4` PASS. The 4C success criterion "B1 and B2
  must move (fail→pass)" is therefore **already met**; the gate is vacuous as
  written.
- **Why:** premise refuted. The infobox `(Former)` facts + the qa fact floor
  already serve *terminal* state. What is unmodeled is *when* a state held
  (intervals over arcs), not the terminal value — so a new probe set (earlier-
  state / arc-scoped questions) is the thing an interval model would actually add.
- **Return address:** `P4.A` — re-scope the 4C probe set via llm-council
  (`reports/comprehension/COUNCIL_p4-rescope.md`); user directed (2026-09-07)
  that the council decide this fork.

### D6 — Council re-scopes 4C: new arc-scoped probe set replaces the vacuous B1/B2 criterion
- **Trunk step:** `P4` (4A interval model)
- **What happened:** the llm-council the user directed (2026-09-07) ruled the
  4C gate vacuous-as-written (D5) and re-scoped it: (1) author 3–5 arc-scoped
  earlier-state probes with wiki-pinned verbatim ground truth, pre-registered
  with a recorded reason each; (2) verify each **fails** against live
  `/context` before any build — no green on paper; (3) all pass → close 4C on
  that evidence, interval model to the backlog; any fail → that probe set
  becomes the real 4C gate and 4A builds **bounded** to the characters the
  failing probes touch, reusing `events` + the infobox fact floor (not a
  wiki-wide 4B table); (4) a serving-path spike (hand-insert 2 interval rows;
  confirm they reach `/context` with zero router/chunker changes) is a hard
  prerequisite; (5) re-label A1/A2/A3/B1/B2 (P3.3C condition 5) as a recorded
  ORACLE v2 — v1 is reviewer-owned (`editable_by_executing_agent: false`);
  (6) regression re-runs (`eval`, `canon-run`, `span-recall`) after any 4A
  build. Cross-wiki / new-door upside → backlog ticket, not this fork.
- **Why:** council verdict (`reports/comprehension/COUNCIL_p4-rescope.md`).
  A gate green before its feature exists has zero discriminating power (B1's
  PASS is also beam-dependent — it regressed under `RED_floorfirst`); the
  un-modeled gap is *when* a state held (intervals over arcs), which no
  existing probe touches; 4A as specified is a dead table (no serving path;
  the router is in nobody's scope).
- **Return address:** `P4.A` — probe authoring + pinning (offline, against the
   crawl), then server start (GPU-first) + live probe run.

### D7 — 4C gate executed: S-group 4/4 post-build; 4C closed, interval model to backlog
- **Trunk step:** `P4` (4C gate per D6)
- **What happened:** executed the re-scoped gate end-to-end. (1) Pre-registered
  S-group (S1–S4, `plan/ORACLE_v2.yaml` sha `e5f28608…`) ran live against CPU
  `:8000` (Qwen owned the GPU): **2/4 pre-build** — S1 (Nanami during Culling
  Game) and S2 (Gojo at start of Culling Game) FAIL as the real gate; S3/S4
  surprised PASS (character pages' own arc-scoped sections already serve those
  states — the gap is specifically the death/sealing event pages). (2)
  Serving-path spike PASS with zero router/chunker changes: two hand-inserted
  `facts` rows (ids 10065/10066, `state_during_culling_game` /
  `state_at_start_of_culling_game`) ride the subject's own fact floor into the
  bundle. (3) The floor alone failed the oracle's `contains` check (the pin
  must be verbatim in the checked text, and the floor renders `label: value`
  only) → the interval fact `value` now carries the pin verbatim (data fix,
  looked-up wording). (4) Post-build S-group **4/4** (re-verified after rows
  restored). (5) Regressions: `span-recall --series jjk` 100% (0
  unreachable); `eval --series jjk` 29/31 — **eval-neutral w.r.t. the 4A
  build** (identical 29/31 with the rows present and deleted); the 2 red items
  (`personality-01`, `trivia-01`, added in `19c8b75`) are the documented open
  Trivia/personality chunking gap, pre-existing and orthogonal to P4 — the
  "24/24" gate figure is stale (bank grew 24 → 31). `canon-run --series opm`
  (run folder `reports/2026-09-07-1136/`): 10/16 exact, 236/236 canon,
  79.0% — identical to the 2C-era baseline; no P4-related movement in any of
  the three re-runs.
- **Why:** D6's verdict, executed: the re-scoped gate is "every failing
  pre-build probe passes post-build" — satisfied; per D6(3) the wiki-wide
  interval model (4B) goes to the backlog.
- **Open items:** the two interval rows are spike rows — wiped by the next
  `index` (facts rebuild from wikitext); the durable 4A build needs an
  extractor or override-driven interval-fact mechanism so the S-group stays
  green across re-index. `personality-01`/`trivia-01` remain open prose-pass
  chunking gaps.
- **Return address:** `P4.A` (durable 4A build design) + the prose-pass
  chunking gap; 4C itself is **closed** on this evidence
  (`reports/comprehension/COUNCIL_p4-rescope.md`, Gate outcome section).

### D8 — P4.A executed: interval facts durable via `extra_facts`; 4A closed
- **Trunk step:** `P4.A` (durable 4A build, D7 return address)
- **What happened:** (1) Designed per the architecture rule (per-wiki data in
  `overrides.yaml`, generic code in the engine): a new `extra_facts:` key in
  `series/jjk/overrides.yaml` declares the two 4A interval facts by node name
  (Nanami `state_during_culling_game`, Gojo `state_at_start_of_culling_game`,
  values carrying the verbatim pins from D7). `scriptengine/index/build.py`
  upserts them after the graph load (`_apply_declared_facts`): a node absent
  from the build is skipped, not invented; each (node, key) is replaced, never
  appended. (2) Full `index --series jjk --force` (CUDA co-located with the
  bursty Qwen session, ~3.5 min embed, Qwen survived): both facts re-landed
  (ids 10065/10066), derived events remapped 2748/2748 (0 stale/orphaned/
  unverified), vectors 14,531. (3) Regressions on the rebuilt store: S-group
  **4/4** (live `:8000` probe, `oracle_4c_results.txt` re-landed), `eval`
  **31/31** (the two D7-era red items `personality-01`/`trivia-01` are now
  green — the Trivia/personality chunking gap was fixed since D7; the 29/31
  figure was stale), `span-recall` 48,572/48,572 (0 unreachable), audit gates
  all PASS. (4) Committed `61311c2` (build.py + overrides.yaml + oracle
  results).
- **Why:** D7's open item — "the two interval rows are spike rows, wiped by
  the next index" — is the defect this closes: the S-group now stays green
  across re-index without hand-editing `facts.db`.
- **Open items:** none from P4; 4C closed at D7, 4A now durable. P6
  (cross-corpus, `plan/Plan_to_perfection.md` §7) is next: Wave-0
  reachability pre-pass on the seven non-JJK corpora.
- **Return address:** `P6` Wave 0 (smallest corpus first: csm → berserk →
  opm → hxh → bleach → db → onepiece). **Superseded 2026-09-07 by the owner
directive: JJK only, halt before P6 — see D9 / X2.**

### D9 — D6-completion plan by council: R4 first, doors censused, preconditions, contingent extraction
- **Trunk step:** none — new excursion **X2** opened (d6-completion; JJK only,
  halt before P6)
- **What happened:** the todo-2 council ran (standing rule 1) — 5 fresh-context
  advisors in parallel → anonymized → 5 peer reviewers in parallel → chairman
  (`COUNCIL_d6-completion.md`, ledger row 19; full transcript in
  `raw/council_d6-completion/`). Every load-bearing claim DB-verified in this
  session before recording: events 2,748 / 2,594 temporal / 154 unplaced;
  live `comprehension-gate` (107/390 disagree, 283 agree, 154 standing,
  temporal 2,594); span-recall rc=0; the 154 = 116 non-placement pages
  (character 99, character_synopsis 11, location 4, technique 2) + 38 chapter
  rows across 17 `Modulo Chapter` docs; abilities 594/94, relations 821/298,
  semantics 0, edges 35,026; roster/narrative doors exist at
  `/context?mode=` (code-verified); the `semantics` table is **not** door-less
  (upsert + read in `stores/facts.py`) — corrected claim: empty, no extractor.
  Verdict: **"done" = the checkable D1–D10 set** (D1 roster census 100q ≥99% ·
  D2 narrative census 100q ≥99% *post-R4* · D3 tier-0/tier-1 re-verified on
  the final corpus · D4 preconditions: 8-verb 100-sentence sample + 140-
  question per-dimension retrieval-not-extraction incl. outcomes & causality +
  50-question open-ended census that can only *grow* the map · D5 placement-
  gate false-negative audit (40 agreeing groups + the 107 re-grounded) · D6
  unplaced = 0 or triaged · D7 `semantics` resolved (no door-less table) · D8
  contingent builds or an honest not-done memo · D9 standing gates green ·
  D10 halt before P6). Sequencing: P0 door pre-check → P1 **R4** → P2 door
  censuses → P3 measurement batch → P4 contingent extraction (R1 only iff
  3a>10 inexpressible AND 3b red; outcomes/causality layers iff 3b red; R3 iff
  relation questions red) → P5 done-declaration memo. **R2 + R5 retired, not
  deferred** (re-queued only on new red evidence).
- **Why:** standing rule 1 (no user input; the fork goes to the council). The
  peer reviews caught what all five advisors missed: the **R4 → narrative
  input-stale dependency** (a narrative census before the 154 are placed
  measures a stale timeline), the **empty `semantics` table** (done cannot be
  declared with a door-less/extractor-less table standing in the store), the
  **missing 8-verb failure branch** (pre-committed ≤10/>10 rule now),
  **outcomes + causality** absent from every done criterion (joined the 3b
  regime), and the map-as-pre-correction-proxy risk (3c's open-ended census
  makes "everything" checkable — the map can only grow via measured evidence).
- **Return address:** the X2 sequence — X2.b → X2.c (R4) → X2.d → X2.e →
  X2.f → X2.g (done-declaration + gates) → X2.h **RETURN: HALT before P6**
  (trunk stays at P6-not-started; the owner directive closes it).
