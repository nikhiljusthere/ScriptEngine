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

**Excursion:** **X2 closed (2026-09-07, D9 — the JJK d6-completion plan, council
row 19, `COUNCIL_d6-completion.md`)**: X2.a council · X2.b door pre-check ·
X2.c R4 · X2.d door censuses (roster 100/100, narrative 99/100) · X2.e
measurements (3a 56/58, 3b 139/140, 3c map-verified, 3d 0-flagged) · X2.f
(contingent extraction — the red set is empty, nothing built) · X2.g done-
declaration (`reports/comprehension/DONE_DECLARATION.md`, D1–D10 all hold) ·
X2.h **RETURN: HALT before P6** — the JJK D6 campaign is closed. The owner
directive (2026-09-07) next authorizes the **CSM (Chainsaw Man) campaign**
to 100% per `plan/Plan_to_perfection.md` (todo #9; up to 3 simultaneous
agents authorized, context windows free to vary per analysis).

**Addition, out-of-campaign (D12, 2026-09-08):** the JJK anime closed
captions (E1–47 + JJK0) are imported as a separate dialogue store —
`series/jjk/transcripts.db` + per-episode JSONs, CLI doors
`transcripts-import` / `transcript` / `dialogue`. Outside the D6 denominator
and the four standing gates; plan + checks in `plan/JJK_TRANSCRIPTS_PLAN.md`.

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

### D10 — X2.b + X2.c: doors verified callable; R4 places 90 of 154, 64 triaged with reasons
- **Trunk step:** `X2.b` + `X2.c` (Phase 0 + Phase 1 of the X2 sequence)
- **What happened:** (1) **X2.b** — the Phase-0 pre-check ran against the live
  `:8000` (launched on CPU by measured decision: Qwen held 28.6/32.6 GB in 262k
  mode, ~4 GB free < the ~5.3 GB the embedder+reranker need — no CUDA
  co-location possible in-mode): the roster door answered a Culling-Game
  enumeration with 15 members (facts + citations + source spans); the
  narrative door answered "what happened in Shibuya, in order" with 5 ordered
  beats (order/title/breadcrumb/text/citations). Both doors exist and are
  callable; the "door missing -> build plumbing" branch never fired. (2)
  **X2.c (R4)** — extended `backfill_event_arc_index` with the third,
  weakest, model-free signal: the wiki's own in-text citation
  (`citation_arc_maps` + `_citation_groups` + `_citation_decision` in
  `timeaxis.py`). Paragraph rule: the paragraph that states the event is the
  one its citation files (citations cover the sentences before them) — all
  mapping to one arc places the row. Section-scope rule: a section cited
  >=2x into a single arc has its scope fixed by the wiki; one citation files
  no scope. The maps are lookups on the wiki's own filings (`chapter_arc_index`
  from the battle pages' `chapters` fact; episode pages' `arc` fact) — a
  chapter no page files stays unmapped, never guessed. Modulo side-story
  citations are excluded (miss, never a wrong arc). Result: **90 of the 154
  placed** (unplaced 154 -> 64; `temporal` 2,594 -> 2,684); cross-page gate
  re-run: 107 -> 109 disagreements (281 agree — two groups that read as
  agreeing while their rows were NULL now carry arcs and disagree, the same
  mechanism the 38 -> 107 jump was). The 64 remainder are triaged, not
  silent: new ledger door `comprehension-gate --triage`
  (`timeaxis.triage_unplaced`) derives per-row reasons from the same lookups —
  53 `no-citation` (incl. the 38 JJK-Modulo side-story chapters) + 11
  `citations-span-arcs`. (3) Tests: `test_citation_signal_places_the_cited_rows`
  (pins 90 / 64; the tally counts rows placed *by right* so it is stable
  across settled re-runs), `test_side_story_citations_place_nothing`,
  `test_triage_ledger_accounts_for_every_unplaced_row`; the 995 section-signal
  count unchanged; targeted suite green (64 tests, incl. gate + continuity).
  Record: `GATE.md` "R4 — in-text citation placement (complete)".
- **Why:** R4 is the council's only non-contingent build (D9) and the
  narrative census is input-stale before it. Bar met: "unplaced = 0 or each
  remainder explicitly triaged with a recorded reason" — 64 triaged with
  machine-derived reasons; the multi-arc and side-story rows were left
  unplaced because forcing them would manufacture misplacements (the
  council's pre-committed branch).
- **Open items:** the standing gates' re-run on the updated corpus (D9 of the
  council's done-set): the full `pytest` under 262k mode OOMs on the
  in-process CUDA reranker (Qwen holds the card; 6 `test_context.py`
  failures are GPU-contention artifacts, not code) — re-run on CUDA after
  the 100k switch, then `:8000` on CUDA for `eval` + `canon-run`.
- **Return address:** **X2.d** — the door censuses (100 roster + 100
  narrative fixed questions, post-R4 corpus, >=99% bar, every miss triaged),
  on the CUDA window (Qwen 100k + `:8000` on CUDA, per the qwen-switch
  protocol).

### D11 — X2.d–X2.h: censuses, measurements, done-declaration, HALT before P6
- **Trunk step:** none — X2 excursion (JJK d6-completion, D9)
- **What happened:** X2.d door censuses (roster 100/100, narrative 99/100;
  the 1 miss = 0-event-row character, triaged; 13 `short` = budget design;
  `87fe80c`). X2.e measurements: 3a 56/58 verbatim (2 MISS_DOC = ranking
  granularity, R1 not triggered) · 3b 139/140 substantively green (1 red =
  wiki-coverage property, Hakari equipment; Outcomes/Causality fully green →
  no layers owed) · 3c 50 open questions, 0 off-map (map verified; R3 stays
  retired) · 3d 0 flagged misplacements (86 repeat-encounter / 11 boundary /
  12 no-signal; 40-group agreeing sample clean) (`87fe80c`, `8ffce8e`). X2.f
  fired nothing (the red set is empty). X2.g done-declaration
  (`reports/comprehension/DONE_DECLARATION.md`): D1–D10 all hold; `semantics`
  formally retired (D7); standing gates green on the final store (pytest
  1,242; eval 31/31; span-recall 0 unreachable + 390/400 probe; canon opm
  10/16 · 236/236 · 79.0%). X2.h HALT before P6, per the owner directive.
- **Why:** every checkable item of the council's done-set (D1–D10) was
  measured and met on the settled post-R4 store; the terminal state is
  done, not not-done — no contingent build was named by any red
  measurement.
- **Return address:** trunk closed at P6-not-started (JJK campaign over);
  next owner-authorized work is the **CSM campaign** (todo #9,
  `plan/Plan_to_perfection.md` to 100%).

### D12 — anime closed-caption corpus import (out-of-campaign, owner-directed 2026-09-08)
- **Trunk step:** none — out-of-campaign, after the JJK campaign closed (D11)
- **What happened:** Phase 1 of `plan/JJK_TRANSCRIPTS_PLAN.md` (council v2,
  run `ea58f12b`): SubArchivist S1 E1–24 + S2 E25–47 + JJK0 (M1) imported →
  48 per-episode JSONs + `series/jjk/transcripts.db` (SQLite FTS5, separate
  from `facts.db`) + hash manifest. 15,411 dialogue lines, 815 sign lines;
  100% dialogue-line coverage vs the raw exports (count check + E1 spot-check
  against the live page). Speaker labels stored verbatim (the archive's best
  effort); deterministic alias rule = `(Flashback) X` → X + 8-entry variant
  map (`VARIANT_MAP`, `scriptengine/transcripts.py` — no guessing, the map is
  a closed list checked against the 368-label inventory). New CLI doors:
  `transcripts-import` / `transcript` / `dialogue`. Campaign-neutral by
  construction: no `facts.db` writes, four standing gates untouched,
  transcripts outside the D6 denominator (D6 is closed anyway, D11).
- **Why:** the owner wants a per-character dialogue dataset alongside the
  wiki; council verdict 5/5 — Phase 1 is parse/SQL only (no GPU), Phase 2
  (embedding) stays deferred to a concrete FTS retrieval failure.
- **Return address:** trunk unchanged (JJK campaign closed; P6 not started;
  next owner-authorized work is the CSM campaign).

### D13 — anime transcript embedding + movie-tag verify branch (out-of-campaign, 2026-09-08)
- **Trunk step:** none — out-of-campaign, after the JJK campaign closed (D11/D12)
- **What happened:** Phase 2 of `plan/JJK_TRANSCRIPTS_PLAN.md` executed in
  the open one-copy CUDA window (A stopped `:8000` 22:51:42, restarted it on
  CUDA 23:17:41 pid 23306 — `reports/master-work/decisions.md`):
  `transcripts-embed --series jjk` → **16,226 points** (15,411 dialogue +
  815 sign lines) in the separate `series/jjk/qdrant-transcripts/` Qdrant
  dir, `device=cuda`, `BAAI/bge-large-en-v1.5` (1024 dims), ~3.5 min; the
  `embed_meta.json` staleness marker (manifest sha + 3 export shas, S1/S2/
  movie) landed and an immediate re-run skips ("Unchanged … 16226 points");
  smoke search plain + `--episode E22` filter passed with no STALE warnings
  (top hits: E21 Geto "Sukuna's actions" 0.754 plain; E22 Mahito
  "Sukuna's fingers cause harm, though." 0.683 filtered). The
  `(Movie <name>)` citation branch in `scriptengine/eval/verify.py`
  (structural check vs the corpus film page; line-level transcript
  cross-check stays a later task, like Phase 1's blind spot #2) is in
  `tests/test_verify_movie.py`, 3/3 green, run first per the job spec.
  One-line fix during the run: `_export_shas` keyed the import manifest's
  export entries on a `key` field that does not exist (they are keyed by
  `url`) — the first two embed runs crashed with `KeyError: 'key'` after
  writing the vectors but before the meta, invisibly (the pipeline rc was
  masked by `| tail`); caught on the third run (RC=1) and fixed by keying
  on `url`. Deliberate exclusions, recorded with reasons in the plan:
  LLM speaker attribution (separate campaign), tier-0 transcript
  containment as a 5th gate (governance sign-off), `/transcript` HTTP
  endpoint (YAGNI), `[MM:SS]` time-rank anchors (optional later).
- **Why:** the v2 council design (run `ea58f12b`) with the owner-directed
  trigger (TRANSCRIPT_JOB.md, B session of the A/B deployment); the
  embedding question was demonstrable in the open window, so it ran then
  instead of waiting for an FTS failure.
- **Return address:** trunk edit — no return (out-of-campaign; CSM campaign
  todos stay parked per the job spec). The pilot transcript skill lives
  outside this repo (subarchive tooling) and is deliberately not committed.

### D14 — Toji script rewrite + transcript-sourced citations (out-of-campaign, owner-directed 2026-09-08)
- **Trunk step:** none — out-of-campaign, after D12/D13 (the JJK campaign is
  closed, D11; CSM campaign todos stay parked)
- **What happened:** the owner-directed autonomous rewrite of the Toji
  Fushiguro script (the `Video 1 - Toji` file, 4,044 words / 91 tags as of
  `c9ff57e`) executed in the fresh 262k session resumed from `plan/
  SWITCHPOINT.md`. Method: the `humanscope` skill Mode A structure sheet
  before drafting, Mode B 30-feature audit before/after, the citation
  discipline (one tag per (chapter, episode) run, tag every sentence on
  source change), and `cli verify --series jjk` before calling it done.
  The D13 transcript dataset was used as a verbatim dialogue source: 5 new
  citation clusters added (Gojo “since he has no cursed energy, I can't
  read his presence” cold-open; the Dagon-fight narrator VO “he had become
  a murder machine, his fangs constantly directed toward the strongest”;
  Gojo “any last words?”; Gojo-to-Megumi “the ultimate card that his dad
  kept on hand against the Zen'in clan”; plus the already-woven Toji
  verbatim lines). Structural AI tells cut: the explaining closing
  (“in one breath …” theme-restate) deleted, the ending now lands on the
  unexplained afterlife image; “not X, it is Y” reframes, rule-of-three
  packs, -ing-tail analyses and weasel wording removed; plain emotion
  words kept (“Toji is proud / glad”). The owner then set the target at a
  ~45-min runtime (~6,000 words), so the script was expanded with sourced
  material (not padding): a full Arsenal section (Split Soul Katana,
  Inverted Spear of Heaven, Chain of a Thousand Miles, the inventory
  curse, Playful Cloud, the broadsword/knives/handgun), a How-he-hunts /
  tactics section (the bounty design, the boat-race/Shiu beat, the
  infiltration, the read-and-counter method), deeper mechanics (the
  Physically Gifted, tracking by footprint/odor, endurance in a long
  fight), the Naobito beat in the Dagon fight, and more Geto/Gojo
  transcript dialogue. Final: **6,037 words, 104 tags /
  29 distinct, `cli verify` clean** (every tag checks out against the raw
  wiki; ~46 min at 132 wpm). Original backed up alongside the file
  (`Toji.md.orig-20260908-2343`).
- **Why:** owner directive 23:4x (“you will do it on your own”) + the follow-
  up to add Gojo / old-man-Dagon / “fangs” citations at the start and in
  between; the transcript store (D13) made verbatim dialogue sourceable.
- **Return address:** trunk edit — no return (out-of-campaign; CSM campaign
  todos stay parked).

- **Addendum (timestamp annotation + JJK0 check, same session):** the owner
  asked for (a) timestamps on the transcript data and (b) the JJK0 movie
  included if done. Both were already in the data — D12's import stored
  `ts` (MM:SS) on every line of all 48 episodes + the JJK0 movie (M1,
  1,433 lines), in both `series/jjk/transcripts/*.json` and
  `transcripts.db`; D13 embedded them. No new fixing run was needed, so no
  council (per the owner's fallback: "if already done, forget it, just add
  the timestamps"). **Toji does not appear in the JJK0 movie (0 mentions),**
  so there are no movie quotes to fold into this (Toji) script; the movie's
  timestamps are in the dataset for a Yuta/Okkotsu video. Added 21
  `[E<n> mm:ss]` timestamp annotations to the Toji script's verbatim quotes
  (exact `ts` pulled from `transcripts.db`), so the editor can find each
  line's footage. Format is episode + MM:SS; multi-line quotes carry a
  comma-separated span. `cli verify` still clean (104 tags / 29 distinct);
  the square-bracket timestamps do not affect the chapter/episode tag
  check. 6,082 words.

- **Addendum 2 (event ranges + glossary + clean version, same session):**
  the owner asked that (a) a line covering several events cite all of them
  (the cast-list line named both the Gojo's Past and Shibuya arcs but cited
  only one), (b) fight/span lines carry a chapter/episode **range** in the
  citation ("X fought Y" → the span the fight actually runs), (c) a
  glossary of every event's range, and (d) a second, citation-free version.
  Ranges were **sourced from the wiki's own adaptation data** (the
  `anime episode` edges in `series/jjk/facts.db`: ch 66→ep 25 … ch 79→ep 30
  for Gojo's Past, ch 94→ep 35 … ch 113→ep 40 for Shibuya, fight spans
  derived from the same mapping) — never invented. Added 5 `[range: …]`
  annotations (the multi-arc cast-list line now cites both arcs; the
  Toji-vs-Gojo / vs-Geto / vs-Dagon / vs-Megumi fight lines carry their
  ch+ep span plus a start timestamp) **appended after** the existing single
  `(Chapter, Episode)` tags, so `cli verify` stays clean (104 tags; the
  range annotations are a new human-curated format, not verify-checked).
  Added a `## Event ranges` glossary at the end (11 events, each with its
  ch+ep range and start time where it is a distinct scene). Created
  `Toji-clean.md` alongside (5,589 words, zero citation markers, glossary
  excluded — pure narrative for the editor). Main file 6,378 words (the
  +~290 over 6,082 is the range annotations + glossary, reference not
  narration); the clean version's 5,589 words ≈ 43 min at 130 wpm.

- **Addendum 3 (passage pass + cast-list correction, same session):** the
  owner corrected the cast-list range — it must cite **Toji's appearance**
  in each arc, not the arc's full span (sentence-level citations cite only
  what the sentence talks about). Removed the 5 inline `[range: …]`
  annotations and the end-glossary; replaced with a **passage pass** — each
  of the 25 body passages now carries a `[covers: …]` line directly beneath
  it, listing the arc/event(s) + ch/ep range(s) that passage draws from
  (Toji in Gojo's Past = Ch 66-75, Ep 25-28; Toji in Shibuya = Ch 95-113,
  Ep 35-40; the four fights, the Zenin massacre, the afterlife, the
  mechanics, the arsenal). Ranges still sourced from the wiki's `anime
  episode` edges, never invented. `Toji-clean.md` regenerated (5,589 words;
  it now also strips the `[covers:]` reference lines, so it is pure
  narrative). `cli verify` still clean (104 tags).

- **Addendum 4 (passage pass → 3 acts, same session):** the per-passage
  `[covers:]` lines (25 of them) read crowded and repeated the same ranges
  over and over. Grouped into **3 acts, one deduplicated block each**: the
  script is split into passage 1 (who he is, how the body works — through the
  arsenal), passage 2 (the Riko job + the two strongest — through Gojo's
  death), passage 3 (Shibuya + the aftermath — through the afterlife). Each
  act ends with a `[passage N of 3 · <label>]` block listing only the
  distinct arcs/events that act draws on (fights, arcs, the Zenin, the
  afterlife, mechanics, arsenal), so no range is repeated across blocks.
  Ranges unchanged (sourced, never invented). `Toji-clean.md` regenerated
  (5,589 words; now strips the `[passage N of 3]` + `·` reference lines).

- **Addendum 5 (passage pass → every 3 passages, same session):** corrected
  the addendum-4 grouping — the owner wanted a covers block after **every 3
  passages**, not 3 total. Removed the 3 `[passage N of 3]` blocks; added
  **9 `[covers X-Y]` blocks** (after passages 3, 6, 9, 12, 15, 18, 21, 24,
  and the lone 25th), each citing the distinct events/battles + ch/ep ranges
  those 3 passages draw on. `Toji-clean.md` regenerated (5,589 words; strips
  the `[covers X-Y]` + `·` lines). `cli verify` still clean (104 tags).

- **Addendum 6 (opening framing line, same session):** the owner asked for
  (a) the "no one ever sensed him standing behind them" line (the Gojo-notice
  beat) and (b) a "Gojo has only been overwhelmed twice" framing in the
  opening 2-3 paragraphs. (a) was already in the script (passage 7, Ch 71).
  (b) added to the cold open: "Gojo has been truly overwhelmed exactly twice…
  the second was Shibuya, where the special-grade curses came with a
  countermeasure to the Infinity and a plan to seal him in the Prison Realm"
  — sourced from the Shibuya Incident page (Jogo/Hanami/Choso + the Infinity
  countermeasure + the Prison Realm), cited `(Chapter 94, Episode 35)`.
  Deliberately no count of "special grades": the wiki gives no clean number,
  so it says "the special-grade curses" rather than invent one. `cli verify`
  now 105 tags (all clean). `Toji-clean.md` regenerated (5,658 words).

### D15 — the Toji script conventions made permanent in the pipeline (out-of-campaign, 2026-09-08)
- **Trunk step:** none — out-of-campaign (the JJK campaign closed at D11; CSM
  todos stay parked).
- **What happened:** the three citation conventions the owner set on the Toji
  script — verbatim `[E<n> mm:ss]` timestamps, a `[covers X-Y]` source-span
  line after every 3 passages, a words-only companion, and the "cite the
  thing the line is about, not the whole arc" principle — are now baked into
  the pipeline, not just the one Toji file. `scriptengine/api/rules.py`
  (`ANNOTATION_RULES`, the contract every prompt gets) now states all four.
  `scriptengine/script/writer.py` always writes the words-only
  `<title>-clean.md` companion (`make_clean_version`) and a deterministic
  backstop (`ensure_covers_blocks`) rebuilds the `[covers]` lines from the
  tags if the model omits them. `docs/SCRIPT_STYLE.md` §6 + a `CLAUDE.md`
  working-agreement quote the new rules. 6 new tests in
  `tests/test_script_gen.py` (all 47 script-gen tests green; the Toji
  `Toji-clean.md` regenerated through the pipeline function, 5,589 words,
  0 markers). The square-bracket markers are invisible to `cli verify`
  (which only reads the round-bracket `(Chapter/Episode)` tags).
- **Why:** the owner asked the conventions to be permanent — reproducible on
  every future `script-gen`, not a hand-edit to one script.
- **Return address:** none — out-of-campaign; CSM campaign todos stay parked.

### D16 — Gojo script v2 (essence-driven) + the essence contract made permanent in the pipeline (out-of-campaign, owner-directed 2026-09-09)

- **What:** the owner gave the *essence* of the Gojo script (open dark — the
  world without Gojo, slow pacing, the tragedies in between, resolution
  "even the strongest, you were overpowered [thematically] by Sukuna") and
  directed that for **all future scripts the agent asks the owner for the
  essence first** (offering options when asked). The Gojo script
  (`E:\Personal\Plot Works\Video 2 - Gojo\Script\Gojo.md`, 3,780 w /
  56 tags / 30 distinct, verify-clean; clean companion 3,126 w) was rewritten
  around that essence: the dark open uses E34 "Pandemonium" (the seal told
  by a first-year through the robot-faced device) — the owner's "19 days"
  image was kept only where the corpus supports a number (the Culling Game
  inactivity rule, Ch 158, as the slow "days" beat; there is no "19 days
  without Gojo" fact in the corpus, and numbers are looked up, never
  inferred). The close lands on the owner's verdict in the story's own
  grammar ("The King did not beat the man. The King beat the strongest.").
  The rule is permanent in the engine: `scriptengine/api/rules.py`
  `ESSENCE_RULES` (folded into `writing_rules()`, so `script-gen` and
  `/context` carry it with every bundle) + a `CLAUDE.md` working agreement.
  Same session: the Toji script was reverted to the 6,520-word Gojo-quote-open
  version and the Script dir trimmed to `Toji.md` + `Toji-clean.md`
  (owner instruction).
- **Why:** shape belongs to the owner, facts belong to the research — the
  two were conflated until now (the first Gojo draft opened light on the
  "I'm the strongest" line; the owner wanted the dark reality).
- **Note:** 6 `tests/test_context.py` QA-retrieval tests fail under the 262k
  Qwen profile with `torch.OutOfMemoryError` at embedder load (Qwen holds
  ~30 GB of the 32 GB card) — environmental, pre-existing, unrelated to D16
  (the rules/contract tests pass). Re-run them at the 100k dial.
- **Return address:** none — out-of-campaign; CSM campaign todos stay parked.
The owner powers the machine off at the end of the session that closed this
entry.

### D17 — CSM resume: Wave 2 + §9a closure loop under the A/B bay (out-of-campaign resume of CSM, owner-directed 2026-09-09)

- **What:** the owner directed the CSM campaign resume ("carry it back up
  from where you left it") deployed via the A/B terminal bay (`ab-bay` skill
  + `terminal-pilot` + `tools/master-work/csm-control.sh`): **A monitors
  shells** (the machine monitor as its eyes: 5-s process-tree poll, every B
  shell → `shell_log.jsonl`, auto-kill of provably-CPU model work >15 s,
  LONG >300 s flagged, MODEL_DOWN backstop; the LLM half of A judges only
  from the jsonl files every ~3 min, typed hints probed via file
  side-channel), **B works** (executes `reports/master-work/CSM_WAVE2_JOB.md`:
  CSM-6 instrument + CSM-5 remainder as the 2-subagent wave pair → §9a
  closure loop iteration 1 → phase close). Two new standing rules (owner
  2026-09-09): **(1) the council trigger** — the LLM council (sequential, one
  agent at a time, DB-verified claims, on disk + ledger) assesses
  correctness *after every CSM phase completes, at every big decision, and
  at every big engine change* (supersedes the "every 2–3 todos" cadence for
  CSM work); **(2) the JJK-100% invariant** — whatever CSM requires, JJK
  stays at 100%: the four standing gates (pytest 1,254 / eval jjk 31/31 /
  span-recall 48,572+400-probe / canon opm 236/236 · 79.0%) re-run after
  every engine change, CSM work lands in CSM-centric files only
  (`tools/csm/*`, `series/csm/overrides.yaml`, `reports/csm/*`), the JJK
  baseline is untouched. New plan: `plan/CSM_WAVE2_RESUME.md` (progress
  review: Wave 1 + CSM-3b + the 19:45 pre-step all done with receipts; next
  = Wave 2). Job spec: `reports/master-work/CSM_WAVE2_JOB.md` (units + the
  A/B bootstrap type-lines). Doc updates: `plan/flow.md` (CSM node),
  `CLAUDE.md` (working agreements), this entry, `plan/SWITCHPOINT.md`.
- **Why:** the machine state changed (the owner powered the box off at the
  end of the Toji/Gojo script session, rebooted, and started Qwen fresh via
  `ninfer-start` at 262k), and the owner wants the campaign to move under the
  supervised A/B deployment rather than the old single-session pattern.
- **Machine note:** 2026-09-09 ~01:50 — post-reboot; Qwen 262k (pid 3550,
  `--vision --max-context 262144`, 30.3 GB on the card); `:8000` down; no
  tmux sessions. The session that wrote this entry restarts first (owner:
  "this current session will restart first, because i started ninfer with
  ninfer-start"); the fresh session dials 150k (plan §2) and launches the bay.
- **Return address:** the A/B bay + Wave 2 per `plan/CSM_WAVE2_RESUME.md`.

### D18 — CSM unit-3 §9a iteration 1: the 400-gate, the frozen miss queue, and the R-1 council verdict (2026-09-09, A/B bay)

- **What:** unit 3 of `reports/master-work/CSM_WAVE2_JOB.md` (the §9a closure
  loop, iteration 1) ran to its first engine-class decision under the A/B bay:
  (1) the **device-path fork went to a §3 council** (`reports/csm/
  COUNCIL_unit3_sweep.md`, 11 sequential members) — verdict **C-deferred-
  panel** (unanimous core): stay 150k, the 400-probe gate runs on the live CPU
  `:8000` (bounded, LONG-flagged), the exhaustive 17,181-row panel defers to
  Phase B (pre-extraction control arm, the planned `PHASE_A_COMPLETE` → 100k
  switch is the only switch); the 21 extraction-gated census reds are the
  documented Phase-1 floor; (2) the **400-gate ran** (CPU `:8000`, ~57 min,
  rate ≈8.5 s/probe measured): ledger `sweep_qa_e3d73720.jsonl` 172 → 572 rows
  (559 HIT / 5 MISS_DOC / 8 MISS_SPAN; the 168-probe datapoint re-confirmed
  CUDA, not CPU); (3) the **miss queue froze** (`reports/csm/
  miss_queue_csm_iter1.jsonl`, 55 rows = 33 fixable / 22 floor, every row
  stamped fix_class + ruling = the halt meter per the council's R2); (4)
  **wave-1 serial fix**: the R-1 router count-rule draft (`router.py` +22/−1,
  11-test CSM file) + the no-council override package (closed 0 rows — all 13
  d5 line-misses verified retrieval-side R-2; two engine hooks recorded:
  `subject_aliases` (R-6) + `identity_fields` (R-7)); (5) **council R-1**
  (`reports/csm/receipts/council_r1_router/`, 11 members) ruled **AMEND**:
  the hunk ships exactly as drafted (the mechanical discovery-side guard is
  verified infeasible without breaking the Geto/hxh pins), B applied the three
  blast-radius test pins (csm-Tokyo / opm-Blizzard opm-set-16 /
  onepiece-Marines, 11 → 14 tests), the receipt corrections (gate-1 1,265 →
  1,283 collect-only; census 9 → 11; the "theoretical" residual is **live** —
  the kept phrase completes *discovered* set names; two named cases), the
  three queue stamp rows (55 → 58), the gate-4 pre-registration (an opm-set-
  16-confined canon drop = the documented R-1 delta → halt to council with the
  gold-shape decision the 2026-08-15 bank note sets up), and the red-list +
  this entry's records (db-flip pinned-not-stamped; class boundary =
  `\bhow many\b` only; the rejected layers: a roster-side stopword cannot close
  the phantom `many` — it is a content word, `roster.py` stopword list — and a
  mechanical name-guard breaks the Geto/hxh basis shapes).
- **Why:** §3 trigger (every big engine change) + the unit-3 halt meter; the
  amendment set is what makes the closure protocol enforceable (close-only-
  HIT rows; zero new misses on stamped rows; gate-time collect-only as
  source of truth).
- **Position:** the four standing gates (one-copy 150k ordering) are next,
  then the R-1 class re-sweep (set-14/15 + the 3 stamps), then the selective
  commit; wave 2 (R-2 qa-passage-leg + R-3 roster-scoping drafts, 2 workers)
  is staged (`/tmp/csm_iter1_wave2.js`), launches only after R-1 clears.
- **Return address:** `plan/state.md` §B (live) + `reports/master-work/
  work_log.md` (append-only); unit 4 (phase close) after iteration 1's
  classes close or the halt meter trips.

### D20 — CSM Phase 1 under the A/B bay: 100k switch via the safe helper, bay booted, directing session stands down (2026-09-10 00:3x–00:5x, post-reboot)

- **What:** (1) the 262k→100k switch ran through the new detached helper
  `tools/master-work/switch_restart.sh` (commit `39f18ab`): kill pi (grace 5 s)
  → `qwen-switch.sh 100k --api --force` → relaunch pi in tmux `pi-csm` +
  resume line; switch log 00:37:25 (ctx=102400, api=cuda, free=7084 MiB;
  Qwen pid 53406; `:8000` pid 53467 on CUDA, parented by the
  qwen-switch `--api` wrapper 53465 — the wrapper is not a stray). The 00:1x
  inline-switch stranding (262k restored by hand 00:30, owner) is the root
  cause this helper retires. (2) the A/B bay opened per the `ab-bay` skill:
  A = tmux `control` (A-pi 53776; BOOT line 00:41:22 in
  `reports/master-work/decisions.md` with the live-verified snapshot; monitor
  `csm-control.sh` pointed at B main pi 53912; the stray 150k-era idle pi
  53686 (ppid 3451, old visible terminal) is NOT bay — ignored, not killed),
  B = tmux `work` (B-pi 53912; job spec
  `reports/master-work/PHASE1_JOB.md`, **Phase 1 only, P1.1–P1.4**). The
  directing session (tmux `pi-csm`, pi 53523) stands down: bounded status
  polls, relay escalations, report to the owner. (3) the phase-1 close is
  gated by `reports/master-work/PHASE1_CLOSE_REVIEW.md` (fresh-context
  reviewer re-runs the four standing gates + verifies every P1.4 close
  condition + marker-at-floor) **plus the owner's go — never the marker
  alone**; B's last act is marker-at-floor + final work_log line + STOP.
- **Why:** owner directive (2026-09-09 night): switch 100k, close this
  agent as ninfer restarts, come back and open the bay — A watches every
  shell B launches (GPU-only-shell rule: every model-bearing shell on CUDA;
  CPU-caught → immediate kill + the standard "Control A killed your shell…
  Re-run on GPU" message; B auto-reruns), B works Phase 1 only; the phase
  boundary gets a checking/reviewer before Phase 2 starts.
- **Position:** B's first units = P1.1 step 0 (zero-GPU baseline
  re-verify: pytest collect 1,305 + span-recall offline 48,572/48,572 +
  red-list recount) + step 1 (model-free rebuild of the reboot-lost
  `/tmp/csm_iter1_records`; the Part-A panel was never DONE pre-reboot,
  rebuild don't assume); then the four gate legs on the CUDA `:8000` (one-
  copy ordering) → C1/C2/C3 selective commits (path-limited `git add` by
  named paths, `git add .` banned; the dirty tree carries the 9-file
  R-2/R-3 package + unrelated files) → P1.2 R-5 wave (council per the kept
  trigger) → P1.3 halt meter (33 fixable only) → P1.4 close + marker
  (floor only) → the phase-close reviewer gate → owner go → Phase 2.
- **Return address:** `reports/master-work/decisions.md` (A) +
  `reports/master-work/work_log.md` (B) + `plan/state.md` (B→A
  escalations, new appends only — the pre-boot 37 lines are stale 150k-era);
  the directing session relays and reports.
