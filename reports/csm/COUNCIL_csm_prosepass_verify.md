# COUNCIL_csm_prosepass_verify — CSM prose-pass reversal + no-formation completion (2026-09-17)

Council #32, sequential one-agent-at-a-time (owner rule 2026-09-08): 5 advisors
→ 5 reviewers (blind to advisor labels) → chairman. Every agent a fresh
context; no shared transcript. Anonymization mapping: A=Executor,
B=Outsider, C=First-Principles, D=Expansionist, E=Contrarian.

**Trigger:** the pasted CSM/JJK report (session work, 2026-09-17) claimed:
(1) CSM really did skip the JJK-style prose pass — 1,260 machine-generated
infobox questions, character pages only; 232 chapter + 14 story-arc pages out
of scope, JJK's in scope; (2) the skip is NOT the cause of CSM's failing
numbers — the failures are two shapes JJK was never put through (the 17,181-line
auto-path sweep at 15.43 % vs 98.48 % forced-qa, and the P2.3 box-class
wrong-page reds); (3) a 19-page/106-question JJK-style pilot scored 106/106
under the JJK instrument and 103/106 bare; (4) implication: running the JJK
pass on CSM would raise the coverage number but NOT touch the reds; the
re-scope and any engine fix go to the council first.

**Inputs (verified on disk this session; paths relative to the repo root):**

- `reports/csm/COVERAGE.md` (regenerated 2026-09-12): 175/537 pages (32.6 %);
  1,260 active questions, ALL on character pages; chapter_box 232 +
  story_arcs_box 14 pages = 0 questions; in-scope content remainder 52 pages
  (character_history 22, episode 12, organization 11, establishment 3,
  unknown 4); scope note: nav boxes + release pages out of scope.
- `questions/_csm_page_*.json`: 177 batch files, 1,276 questions (1,260
  active); every one infobox-shaped (kanji/romaji/status/gender/occupation).
- `series/csm/overrides.yaml` ~L394: `chapter_box: in_scope: false`
  (story_arcs_box likewise).
- `reports/csm/GATE.md` P2.1 (tree `4b60043`, 2026-09-17): panel 17,181 +
  200 heldout; qa 98.48 % PASS (A17 bar ≥ 97.5 %); auto 15.43 % (heldout
  14.0 %); routing 89.1 % → narrative; 237 both-misses; pre-registrations
  P-1…P-5 (auto descriptive-only; perfect router tops out ~98.62 %; R-9
  deferred pending writer-shaped evidence; per-wiki route before any
  `router.py` change).
- `reports/csm/p23_red_triage.md` (committed `3d43a21`): widened 486 (qa)
  85.8 %; 69 reds = 37 box-class wrong-page ranking + 27 width/enumeration +
  5 state-over-time + 0 judge artifacts; bar audit qa 11/26, auto 14/26;
  R-9 is NOT the lever for these reds; first fix route = per-wiki config.
- `reports/csm/panel_csm.json`: 17,181 rows = [page, section, sentence] over
  535 distinct pages, INCLUDING all 232 chapter + 12 episode + 19 arc/saga
  pages — the sweep already covers the out-of-scope pages.
- `reports/page-campaign/PROSE_PASS_FINAL.md`: JJK final 893/987 pages,
  29,819 active questions, in-scope remainder 0; method = verbatim answers +
  root-cause-fix mandate + per-type templates + author loop + gate discipline.
- Halt rule (`GATE.md`): 22 floor rows (21 D6-extraction + csm-char-04) +
  10 stamped by-design open rows; close order P2.4 writer leg → R-9
  evidence call → `PHASE_B_COMPLETE`.
- UNVERIFIABLE: the 106/106 pilot (19 pages, 3 named misses: 2 Yakuza + 1
  Pochita) exists only in the session scratchpad; method (frozen pre-scoring,
  own-page guard) sound, numbers not re-verifiable on disk.

## Questions put to the council

D1 — Is the report's reversal ("the skipped pass isn't the cause of CSM's
reds") sound? Which claims are verified, which unverifiable, which misread?
D2 — How should the CSM prose pass be completed WITHOUT question formation
(the JJK pass hand-wrote per-page questions; the campaign constraint is: no
hand authoring, machine-generated questions from page content are
acceptable)?
D3 — Will completing the pass bring CSM to 100 % — under the campaign
halt-rule definition (all fix-classes closed, remainder = the frozen 22
extraction-gated floor rows + 10 by-design open rows) vs literal 100 % of
every probe through the served auto path (P-1 pre-registration caps this at
~98.62 % even with a perfect router)?

## Advisor responses (de-anonymized)

**The Contrarian (E):**
Tried to break the reversal; its substance held, but two claims are
mischaracterized and D2 is incoherent. The core claim survives: the P2.3
grader already ran a 486-item writer-shaped question bank (that IS question
formation) and it's 85.8 %, with the 37 box-class reds being a ranking
failure ("Chapter 1" → "Chapter 124"), not a missing-questions failure. The
P-1 pre-registration (perfect router → 98.62 %) is a real ceiling I could not
break, corroborated by a second instrument (the 486-item bank). But claim 1
misframes it: CSM did not "skip" the pass — it ran a cheaper machine-infobox
pass: 1,260 questions over 175/537 pages (~7/page), all infobox-shaped, vs
JJK's ~33/page narrative templates. The gap is coverage + shape, not a skip.
That reframes D2: extend the machine pass to the 362 uncovered pages. Claim
3's 106/106 is the page-hint instrument, unreachable on the served writer
auto-path. Honest number: 103/106 (bare), with 3 residual in-scope character
misses (Yakuza, Pochita) absent from the E5 red taxonomy. A full JJK-style
pass therefore does not reach 100 % on the served path — it confirms the
~98.62 % cap. D2's "complete without question formation" is a category error:
the prose pass IS question formation (E5's 486-item bank proves it). You
can't close the box-class reds by adding questions — the bank already has
them and still misranks. The lever is the per-wiki route / R-9 engine fix,
JJK's 31/31 gate as guardrail. D3: literal 100 % through the served path is
unreachable (P-1 cap + 22 floor rows); halt-rule 100 % closes via the
per-wiki route, not the prose pass. The reversal holds only while you keep
those separate.

**The First Principles Thinker (C):**
The reversal is causally sound, but D2 is the wrong question and one premise
misread. D1: (1) verified on disk (COVERAGE.md / batch files / overrides).
(2) sound: the reds are (a) routing — 89.1 % of line lookups misroute to
narrative — and (b) wrong-page ranking — 37 box-class reds. Both are engine
defects; more questions fix neither. But "out of scope" is misread: the sweep
already spans all 232 chapter, 12 episode, 19 arc pages (panel_csm.json).
Out-of-scope governs question generation only, not the sweep — so the reds
are already measured on those pages; re-scoping in only moves the coverage
number. The 106/106 pilot is scratchpad-only — discount it. D2: "complete the
prose pass without question formation" is the wrong frame. The prose pass
isn't a deliverable, it's an instrument: a gate that produces a miss queue
driving root-cause fixes. CSM already has that miss queue (sweep + P2.3).
The real work is the two defects the miss queue localized: (1) per-wiki
routing in overrides.yaml before any series-agnostic router.py change (JJK
gate holds); (2) the 37 box-class wrong-page reds. The sweep is the standing
regression check after each fix, not a to-do list to "complete". D3: the
prose pass doesn't bring CSM to 100 % under either definition; it's a gate,
not the means. Campaign 100 % (halt rule) = closing all fix-classes,
residual 22 floor rows; reached by the engine fixes, verified by the sweep.
Literal 100 % is capped ~98.62 % + 22 floor rows, unreachable by design.
Re-scope chapter/arc only if the campaign wants them in-scope (a scope
decision, not a question-formation decision); re-run the sweep as the gate.

**The Expansionist (D):**
The framing undervalues the pass: it's priced as a coverage lift. All 1,260
CSM questions are already machine-generated from infoboxes. The "no question
formation" constraint in D2 is a misread — JJK's handwork was per-page
authoring; CSM has already proven the machine alternative (106/106 on
never-asked pages). Extending the same generator to the 246 box pages, plus
a one-line "what happens in {title}?" template, is config, not a new
capability. D2 answers itself. D1: the reversal is sound. But the undervalued
upside: the pass is the diagnostic-resolution upgrade for P2.3. The grader
asked 10 questions each on chapters/episodes/arcs and got 1/10, 1/10, 0/10 —
coarse. The 37 box-class wrong-page reds are ranking failures on those pages.
Per-page batches over 246 pages turn "1/10" into per-page signal, and the
root-cause-fix mandate is what closes the reds. The report says the pass
"won't touch the reds"; mechanism right, direction wrong: the pass fixes
them by being the verification loop that forces the fixes. The kicker: the
17,181-line sweep already covers all 232 chapter + 12 episode + 19 arc/saga
pages — the campaign's own instrument has been measuring what it declared out
of scope. Re-scoping aligns scope with instrument; it isn't scope creep.
Bigger prize: blessing the machine generator as the standard instrument makes
every other corpus — 7 indexed wikis, P6 — closable without author handwork.
That's the P6 unlock hiding in this decision. D3: target campaign-100 %
(fix-classes closed; floor = 22 rows). Literal 100 % is capped at 98.62 % by
P-1 — a trap. The per-wiki routing fix collapses auto from 2,651 failures
toward the ~237 both-miss floor, and the pass then verifies it.

**The Outsider (B):**
What a zero-context reader can't follow: (1) "Out of scope" contradicts the
panel — overrides.yaml declares chapter/arc out of scope; panel_csm.json says
the 17,181-line sweep grades all of them. So "out of scope" means "no
questions written" but not "not tested". Claim 1 is only true for questions,
not verification. If out-of-scope pages are graded, scope is a fiction; D2's
"complete the pass" is undefined until someone says which governs: the config
or the panel. (2) The buried red is the product's own router: auto (what the
product serves) = 15.43 % while qa on the same panel = 98.48 %. R-9 is parked
"until writer-shaped evidence appears" — but the P2.3 triage IS
writer-shaped evidence, dated 2026-09-17. The deferral condition looks
already met. Why does the product ship a path serving 15 % when 98 % is
measured on the same corpus? (3) Claim 3 rests on evidence that will be
destroyed: the 106/106 pilot is in a scratchpad slated for deletion; method
sound, evidence not. "JJK's chapter/arc in scope" is also absent from the
evidence — no JJK config shown. (4) D2 is unanswerable from the evidence: the
JJK pass IS per-page question authoring (29,819 questions). "Complete it
without question formation" has no mechanism in the block. The council is
deciding a question the evidence never addresses.

**The Executor (A):**
Monday, cheapest first: (1) Re-scope: flip chapter_box and story_arcs_box to
in_scope: true — the "skipped pass" is a scope flag, not a missing pipeline.
(2) Questions: the per-type generator that produced the 1,260 infobox
questions already exists; add per-type narrative templates (chapters, arcs,
plus the 52 in-scope remainder pages), run through the existing page-run JJK
instrument — that's what "no question formation" means, nobody writes them
by hand. (3) Regenerate COVERAGE.md; in-scope remainder → 0. The 69 reds:
separate workstream, all pre-registered — 37 box-class wrong-page (council
call, JJK 31/31 must not regress), 27 width/enumeration (council assigns
lever), 5 state-over-time (CSM extra_facts in overrides.yaml, else floor).
Auto sweep 15.43 %: council #31 pre-registered the 98.62 % ceiling — floor is
floor. D1: reversal sound on the verifiable parts; the skip is on disk, the
red shapes are documented, a question bank touches neither routing nor
ranking. Unverifiable: the 106/106 pilot — re-run those 106 through page-run
before the council leans on it. One misread: the pass is a no-op until step 1
flips the flags. D3: the pass gets in-scope remainder 0, not campaign 100 %;
literal 100 % is capped at 98.62 % by design.

## Peer reviews (anonymized letters A–E as mapped above)

1. Strongest: C — the pass is a gate, not a deliverable; CSM already has the
   miss queue; the real work is the two localized defects (per-wiki routing +
   37 box-class reds), sweep as standing regression check. E is sharper on
   the mechanism (the bank already has the questions; reds are ranking
   failures). Blind spot: D — rests on the unverifiable 106/106 scratchpad
   and over-promises the P6 unlock while under-weighting that the box-class
   reds are ranking failures the pass structurally cannot close. All five
   missed: the R-9 evidence call is now unblocked AND a required close-order
   gate — the P2.3 bank IS the writer-shaped evidence that un-defers R-9;
   schedule it now. Also: most dropped the 10 by-design open rows — the halt
   remainder is 32, not 22.
2. Strongest: C — only one that gets D2 right and answers D3 under both
   definitions; flaw: drops the 10 by-design rows. Blind spot: D — its D2
   answer and the P6 upside both rest on the 106/106, scratchpad-only,
   page-hint instrument (honest: 103/106 bare). All five understate the
   halt-rule residual: 22 floor + 10 by-design = 32 rows; the 10 by-design
   rows are a distinct class to disposition, not part of the floor.
3. Strongest: E — the only response reframing claim 1 as a coverage + shape
   gap (not a "skip"), noting 103/106 bare is the honest number and the 3
   residual character misses are absent from the red taxonomy; corroborates
   the 98.62 % cap via the 486-item bank. Blind spot: D — inverts the core
   finding (the 486-item bank already has these questions and still fails;
   the pass only surfaces the reds, it doesn't close them) and the P6
   unlock is absent from the evidence. All five missed: re-scoping was
   treated as a neutral coverage lift while the 237 both-misses span the
   out-of-scope pages (later adjudicated — see the chairman's Blind Spots).
4. Strongest: C — the only response answering all three decisions. Blind
   spot: B — calls D2 "unanswerable, no mechanism in the block," but the
   existing machine generator IS the no-hand-authoring mechanism; B also
   calls "out-of-scope" a "fiction" right after conceding it gates
   generation, not verification. All five miss: the halt-rule remainder is
   32 rows (22 + 10), and A's "cheapest first" step 1 (flipping the scope
   flags) is itself the scope decision the report defers to council.
5. Strongest: C — alone reframes D2 correctly; E near-miss (sharpest D1, but
   its D2 chases coverage, not the reds). Blind spot: D — the P6 unlock is
   load-bearing on the 106/106 that won't survive re-verification; D also
   blurs the 237 both-misses with the floor. All five missed: they never
   force *which instrument* defines "100 %" — gate on the qa/miss-queue
   (the halt rule's instrument); the auto panel is descriptive-only by
   pre-registration; gate on auto and campaign-100 % is impossible by
   construction (98.62 % cap).

## Chairman's verdict

### Where the council agrees

1. **The reversal's causal core is sound.** The failing numbers are engine
   defects, not missing questions. The 486-item writer-shaped bank *already
   contains* the failing question shapes and still sits at 85.8 % — the 69
   reds decompose into 37 box-class wrong-page ranking + 27 width/enumeration
   + 5 state-over-time, zero missing-questions failures. The 237
   both-misses are unreachable by any router fix. More questions close none
   of these.
2. **"Out of scope" gates generation, not measurement.** The 17,181-line
   sweep already spans all 232 chapter + 12 episode + 19 arc/saga pages. The
   scope flag only blocks question generation. Scope and instrument are
   currently decoupled.
3. **The ~98.62 % ceiling is real and unbreakable.** P-1 caps even a perfect
   router on the auto panel; corroborated by the 486-item bank and by the
   pilot's 103/106 bare. The both-misses and the 22 floor rows are
   content/extraction-level, not routing-level.
4. **The pass is a gate/instrument, not a deliverable.** CSM already has the
   miss queue (sweep + P2.3 bank). The sweep is the standing regression check
   after each fix, not a to-do list to "complete".
5. **The 106/106 is discounted as evidence.** Scratchpad-only, slated for
   deletion, measured on the page-hint instrument. Honest figure: 103/106
   bare. Method sound; the number is not a decision input until re-run
   through page-run.
6. **The lever for the 37 box-class reds is the per-wiki config, not the
   router.** `series/csm/overrides.yaml` is the first fix route and does not
   trigger the JJK regression gates; series-agnostic `router.py` changes do,
   and stay gated on JJK 31/31.

### Where the council clashes

1. **"Skip" vs "coverage + shape gap" (claim 1).** Contrarian/Executor:
   "skipped" is a misframe — CSM ran a cheaper machine-infobox pass (~7
   infobox-shaped questions/page on 175 character pages vs JJK's ~33/page
   narrative); the gap is a scope flag, not a missing pipeline. First
   Principles: verified on disk as stated. **Ruling: both are true at
   different levels.** The on-disk facts are verified; "skipped the JJK-style
   prose pass" mischaracterizes the mechanism (no pipeline was skipped — a
   scope flag plus a cheaper instrument were chosen). Additionally, the
   claim's JJK side ("JJK's chapter/arc pages were in scope") is unverified
   in the evidence block — no JJK config was shown; grep
   `series/jjk/overrides.yaml` before repeating that half.
2. **D2: category error vs self-answering.** Outsider/Contrarian: "complete
   without question formation" is incoherent — the pass IS question
   formation (E5's bank proves it). Executor/Expansionist: it answers itself
   with the existing machine generator. **The clash dissolves on the user's
   actual constraint:** "no question formation" means no *hand* authoring;
   machine-generated questions from page content are explicitly acceptable.
   "Unanswerable" and "category error" both misread the constraint as "no
   questions at all". With the real constraint, D2 has a mechanism. What
   survives as a genuine clash is the **P6 upside** (blessing the machine
   generator as the standard instrument for 7 wikis): it rests on the
   106/106 scratchpad, is absent from the evidence, and P6 is parked until
   Phase 1 closes anyway. Not a decision input here.
3. **Re-scoping: scope creep or alignment?** Expansionist: it aligns scope
   with the instrument — not creep. Executor/review 4: the flip is itself
   the scope decision the report defers to council. Review 3: re-scoping
   inflates the halt floor toward the 237 both-misses. **Ruling: it is a
   council decision (this verdict makes it), it is not creep (the instrument
   already measures those pages), and the floor-inflation concern is refuted
   by the frozen-rows fact** (see Blind Spots 3). Re-scoping is halt-safe;
   its real costs are +246 pages of machine questions and new misses landing
   on the box-class defect, which is exactly the per-page diagnostic signal
   the root-cause mandate wants.

### Blind spots the council caught

1. **The halt residual is 32 rows, not 22.** 22 extraction-gated floor rows +
   10 by-design open rows. Campaign-100 % means fix-classes closed with a
   frozen **32-row** remainder; the 10 by-design rows are a distinct class to
   disposition, not part of the extraction floor. (Flagged in reviews 1, 2,
   4, 5; advisors C/D/E quoted "22", A/B were silent.)
2. **The R-9 evidence call is unblocked and is a required close-order
   gate.** The P2.3 bank (2026-09-17) IS the "writer-shaped evidence" that
   deferred R-9. Close order: P2.4 writer leg → R-9 call → phase-complete.
   The P2.3 pre-analysis says the call will conclude R-9 is *not* the
   box-class lever — but the call is still the gate. Schedule it now.
3. **The "re-scoping inflates the floor" concern is refuted — the record is
   corrected.** Review 3 claimed re-scoping pushes the halt floor toward the
   237 both-misses. Wrong on the authoritative facts: the 22 + 10 rows are
   **frozen pre-registered row IDs**, and the 237 both-misses are a
   **separate descriptive-only** statistic (pre-registration P-1, council
   #31) that is not a gate number. Re-scoping changes which pages generate
   questions; it does not change which frozen rows exist. New misses from
   newly-scoped pages are new campaign work, not floor.
4. **The JJK side of claim 1 is unverified** (Outsider): no JJK config in the
   evidence block. One-line grep of `series/jjk/overrides.yaml` before the
   comparison is stated as fact.
5. **The pilot's 3 residual misses (Yakuza, Pochita) are absent from the
   red taxonomy** (Contrarian + reviews 2/5): the 37/27/5 breakdown does not
   cover them. A third, unclassified red class exists in-scope; classify it
   when the pilot is re-run.
6. **No one forced which instrument defines "100 %"** (reviews 4/5). The
   halt rule tracks fix-class closure on the **qa/miss-queue** instrument;
   the served-auto panel is descriptive-only by pre-registration. Gate on
   qa/miss-queue; report auto descriptively. Gate on auto and
   campaign-100 % is impossible by construction (98.62 % cap).

### The recommendation

**D1 — The reversal is sound on its verifiable core; two claims need
correction.**
- **Claim 1:** verified on disk (COVERAGE.md / batch files / overrides.yaml)
  but misframed. It is not a skip — it is a scope-flagged, cheaper machine
  pass (1,260 infobox-shaped questions; 0 on the 246 box pages). "Out of
  scope" governs question generation only; the sweep already measures those
  pages (panel_csm.json). The JJK half of the comparison is unverified —
  verify by grep before repeating.
- **Claim 2:** verified (GATE.md P2.1 + p23_red_triage.md) and causally
  sound. The reds are routing (89.1 % → narrative), ranking (37 box-class),
  and extraction (both-misses/floor) — defects no question closes. The 486
  bank is the proof: the questions exist and still fail.
- **Claim 3:** not re-verifiable (scratchpad-only). Discount; method sound;
  103/106 bare is the honest number. Re-run the 106 through page-run before
  any future reliance, and classify the 3 residual misses (Yakuza, Pochita).
- **Claim 4:** mechanism correct (the pass raises the coverage number, not
  the reds) and its routing of re-scope + engine fixes to the council is
  right. This verdict answers that routing.

**D2 — Complete the pass with the existing machine generator; the constraint
is satisfiable.** "No question formation" = no hand authoring. Extend the
generator that produced the 1,260 infobox questions with per-type narrative
templates (chapters, arcs, the 52 in-scope remainder pages — and the 246 box
pages under the re-scope below), run through the existing page-run JJK
instrument, regenerate `COVERAGE.md` → in-scope content remainder 0. That is
the coverage leg. The red-fixing leg is separate and pre-registered: 37
box-class → per-wiki config (`series/csm/overrides.yaml`, no JJK-gate
trigger); 27 width/enumeration → council assigns the lever; 5 state-over-time
→ `extra_facts` in the same file, else floor; 237 both-misses / 22 floor
rows → extraction-gated, Phase 2. The pass's standing role: miss-queue gate;
the sweep is the regression check after each fix.

**D3 — The pass reaches coverage 100 %, not campaign 100 %, and not literal
100 %.**
- **Campaign halt-rule 100 %** = all fix-classes closed with the frozen
  32-row remainder (22 extraction-gated + 10 by-design open). It is reached
  by the close order (per-wiki config for the box-class → R-9 call →
  phase-complete), verified by the sweep. The pass is an input (remainder 0 +
  complete miss queue), not the closer.
- **Literal 100 % of every probe through the served auto path** is
  unreachable by design: P-1 caps a perfect router at ~98.62 %; the
  both-misses and floor rows need extraction, not routing. A full JJK-style
  pass confirms the cap (103/106 bare is consistent with it); it cannot
  break it.
- **Instrument:** gate on qa/miss-queue (the halt rule's instrument); the
  auto panel stays descriptive-only per pre-registration P-1.

**Re-scope ruling: YES — flip `chapter_box` and `story_arcs_box` to
`in_scope: true` in `series/csm/overrides.yaml`.** It aligns scope with the
instrument (the sweep already measures those pages), is halt-safe (frozen row
IDs; the 237 is descriptive-only), and is one line. Costs: +246 pages of
machine questions and new misses on the box-class defect — the per-page
signal the root-cause mandate wants; the reds stay red until the per-wiki
config fix lands.

### The one thing to do first

Flip `chapter_box` and `story_arcs_box` to `in_scope: true` in
`series/csm/overrides.yaml`. It is the council's re-scope ruling, one line,
and the prerequisite for the entire D2 coverage leg ("the pass is a no-op
until step 1", per the Executor). It unblocks machine generation over the
246 box + 52 remainder pages → in-scope remainder 0, leaves the frozen
32-row halt residual untouched, and is the exact decision claim 4 routes to
this council. The generator run + COVERAGE.md regeneration is the second
thing; scheduling the R-9 evidence call (unblocked by the P2.3 bank,
required by the close order) is the third.

## Verification addendum (2026-09-17, post-verdict, disk-checked)

Blind spot 4 is resolved by grep (the record's own instruction): the report's
JJK half — "JJK's chapter/arc pages were in scope" — is **correct as a
statement about the prose pass** (PROSE_PASS_FINAL.md L24–29: chapter 304/304
with 941/941 questions, story_arcs 9/9, in-scope content remainder 0) but is
**NOT readable from the current flags**: `series/jjk/overrides.yaml` (CSM-2
encoding, `42aa296`, 2026-09-08) marks JJK `chapter` / `episode` /
`story_arcs` / `technique` / `character` / `battle` etc. `in_scope: false`
with reason **"Measured in the prose-campaign batches (not the content
remainder)"**, while CSM's `chapter_box` / `story_arcs_box` are `in_scope:
false` with reason **"Manga chapter nav/summary box (nav page)"** — the same
flag value, two different meanings (JJK: done, no remaining obligation; CSM:
never measured, excluded from the obligation). Compare on the campaign
state, never on the flag value alone.

## Pre-registrations (binding for the phase)

- **P-6 (re-scope):** `chapter_box` + `story_arcs_box` → `in_scope: true`
  in `series/csm/overrides.yaml`; the halt residual stays the frozen
  32-row set (22 + 10); new misses on the newly-scoped pages are campaign
  work, not floor.
- **P-7 (pilot re-run):** before any future reliance on the 106/106, re-run
  the 106 through `cli page-run` (page hint, top 50, 60k) on a stable tree
  and commit the results under `reports/csm/`; classify the 3 residual
  misses (Yakuza, Pochita) against the red taxonomy.
- **P-8 (R-9 call):** the P2.3 bank un-defers the R-9 evidence call; it is
  the close-order gate after the P2.4 writer leg. Pre-analysis expectation:
  R-9 is NOT the box-class lever (per-wiki config is); the call may still
  fire R-9 on the auto-panel misroute axis — decision at the call, not
  before.
- **P-9 (100 % instrument):** campaign 100 % is gated on the qa/miss-queue
  instrument; the auto panel is descriptive-only (P-1). Literal served-path
  100 % is declared unreachable (98.62 % cap + 32-row remainder) and is not
  a campaign target.