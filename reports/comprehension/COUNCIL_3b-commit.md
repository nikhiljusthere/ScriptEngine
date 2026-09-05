# Council — step: 3b commit (corpus-scope work)

Run: 2026-09-05. Five advisor passes (anonymized A–E), five peer-review passes
(Skeptic, Pragmatist, Formalist, Domain-expert, Fresh-eyes). Every factual claim
below was verified against `series/jjk/facts.db` and source before recording; a
claim that failed verification is struck and the correction noted.

## The step under review
Widened event extraction from the 108-page placement set to the full corpus
(524 pages), re-ran the comprehension gate on the widened set, and fixed the
backfill test's off-axis predicate to be temporal-aware. Artifacts: the 7-file
diff, `GATE.md`'s filled-in 3b Results, and the `test_timeaxis.py` fix.

## Agreements (all five advisors)
- The headline is a **set-size gain, not a comprehension gain**. The event set
  grew 714 → 2,748, but `temporal=1` is still exactly **714** (the pre-corpus
  baseline total); all **2,034** new rows are `temporal=0` (atemporal /
  off-axis). Net contribution to *placed* events is **zero**, which is exactly
  why coverage holds at 61.9%.
- The test-invariant fix is a **legitimate semantic update** (atemporal rows
  are off-axis by definition), not a dodge — *but* it narrows the gate from
  "everything is placed" to "off-axis is justified by temporality," and that
  narrowing should be stated in `GATE.md`, not buried in a comment.
- The one check that proves the step holds: `COUNT(events WHERE arc_index IS
  NULL AND temporal=1) = 0` (no temporal row lost), paired with
  `COUNT(arc_index IS NULL) = 2,034 = COUNT(temporal=0)`. **Verified — both
  hold.**

## Clashes
- **D (Contrarian) vs B/Formalist** on the new invariant: D called it "nearly
  tautological." **Struck.** A `temporal=1` row with `arc_index IS NULL` still
  fails `null == count(temporal=0 OR residue)`, so the invariant is real; both
  B and the Formalist refuted D on this.
- **D's "every surviving temporal row is baseline"** is *consistent* but not
  proven: it needs the unstated assumption that zero baseline rows were demoted.
  `temporal=1 = 714 = baseline total`, so it is the most likely reading, not a
  forced one.
- **C (Outsider) vs the document** on arithmetic: C's flags are all closed
  in-document derivations (strongest on evidentiary discipline), but C itself
  smuggled in "874 extracted atemporal." **874 is an unverified residual**
  (2,034 − 1,160), not shown to be extraction-atemporal as opposed to a third
  category.

## Blind spots (raised by peer review; no single advisor had them)
1. **The scope may have shrunk the candidate set** (Skeptic). The new scope
   (narrative heading + ≥2 character nodes) replaced the old node-degree-2 /
   ~19,684-chunk scope. No one diffed the pre/post candidate sets, so the flat
   714 could mask a recall *loss*, not neutrality. **Not yet checked.**
2. **The ~874 extraction-atemporal rows are unaudited** (Formalist). The gate
   polices only temporal→atemporal demotion (the 1,160). Rows the extractor
   labeled atemporal from the start face no placement or consistency check — a
   mislabeled temporal event becomes a permanent standing state, invisible to
   both the gate and the 38-count.
3. **The cross-page check is single-wiki self-consistency** (Fresh-eyes). It
   catches the extractor contradicting itself, not the wiki being
   systematically wrong; all 2,748 rows can corroborate cleanly while being
   wrong. "38 held" is not a correctness win.

## Verified hazards (checked against source/DB before recording)
- **Re-index id-dangling — latent, real.** `reset()` (`facts.py:160`) drops
  `nodes` + `sections` (reassigning rowids) but keeps `events`, whose PK is
  `(subject_node, verb, object_node, section_id, time_rank)` with **no foreign
  keys** (verified in the DB). A routine `index` calls `reset()`
  (`build.py:96`), so it would dangle the **139 node refs + 838 section refs**
  the events carry. The gate groups by **node-id pair** (`gate.py:109`), so it
  would silently stop grouping with no error. *Currently clean (no re-index
  since extraction): 139 ≤ 1,557 node rows, 838 ≤ 7,601 section rows.*
- **A corpus "rescue" that only sets `arc_index` would be undone.** The gate
  calls `backfill_event_arc_index` (`gate.py:45,97`), which sets
  `arc_index = page_index.get(page)` for every distinct `arc_key`; a corpus page
  is not in the placement axis, so its events are clobbered back to `NULL`. The
  pending continuity-check placement must register corpus pages in the
  placement axis, not just write `arc_index`. **Verified.**
- **Zero-event pages never cache** (`facts.py:1087` probes stored rows). This
  also explains the 16-vs-15 reconciliation: run-1's 16 survivors = 15 cached
  + 1 re-extracted (a zero-event / revid-changed page), giving the tidy
  509 + 15 = 524.

## Recommendation
Commit 3b as a **data step, not a comprehension win**: the widened event set is
correct and the gate re-ran clean, but it added 2,034 atemporal rows and **zero
placed events**. `GATE.md`'s "Results" must be re-graded to say so — reconcile
the 508/16/15 and 1,160/874/2,034 figures, state the invariant-narrowing
deliberately, and list the hazards above as queued follow-ups. Do **not**
report it as moving the comprehension number.

## One next step
Before the continuity-check todo: (1) amend `GATE.md`'s 3b Results to the
honest framing above, (2) queue two follow-ups — the re-index id-stability fix
(FK, or re-extract-after-reset) and the ~874 atemporal-row audit — and (3) diff
the pre/post-scope candidate sets to rule out a masked recall loss. These are
the real blockers to trusting the 2,034 rows; none is auto-resolved here.

## Advisor → lens map (record only)
A=First-Principles · B=Executor · C=Outsider · D=Contrarian · E=Expansionist.
Peer reviews: Skeptic, Pragmatist, Formalist, Domain-expert, Fresh-eyes.

## Post-council re-derivation (per the standing rule: pull the raw rows before accepting a null)

The council's "Blind spots" and "Verified hazards" both inherited the premise
that the 2,034 off-axis rows are *unplaceable* / *atemporal*. That premise was
accepted, not checked. Running the raw rows down to a query-backed floor:

- **All five advisors (and this report's own hazard list) missed the
  section-heading signal.** 995 of the 2,034 off-axis rows sit under a section
  heading that **names an arc, and all nine such arc names are on the placement
  axis**. The backfill keys on the *page* (`arc_key`), so a character `Synopsis`
  page is off-axis even though its `Shibuya Incident Arc` section names the
  exact arc. The "unplaceable" conclusion is the "accept a null result without
  checking the free placement signals" error.
- **The 874 "atemporal-at-extraction" blind spot is mis-targeted.** The real
  open item is not auditing 874 rows — it is the **placement key**: `backfill`
  never consults the section heading (995 rows) or the in-text `Chapter`/
  `Episode` citation (~209 more of the 1,039 generic-heading rows). The 874 is
  exact by construction (2,034 − 1,160) and correct as a count; it just isn't
  per-row isolable (the gate leaves no demotion marker).
- **The id-dangling hazard is pre-existing and latent, not a 3b defect.** The
  `events` table has always lacked FKs on node/section ids; 3b *amplified* the
  exposure (139 node + 838 section refs now), it did not introduce the
  mechanism. Currently clean (no re-index since extraction).

**Corrected one-next-step.** The continuity-check placement pass should extend
`backfill_event_arc_index` to map by **section heading** and **in-text
citation** (placing ~995 + ~209 rows) *and* register those corpus pages on the
axis (so the gate's backfill doesn't clobber them). That is the concrete fix
behind the flat number; the id-stability FK and the scope-shrink diff remain
queued follow-ups.