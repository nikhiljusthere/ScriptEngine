# PEER REVIEW R4 — the 2-prep fix spec (P23 / P25 + P24 deferral), round 2

Mandate: is the recorded 2-prep fix (subject-anchored fact floor before 2A)
correct, complete, and safe — does it fix the B2/B4 oracle failures without
regressing the 14 passing items or the standing gates?

Everything below was verified on tree `94909d2` (branch
`character-scoped-questions`) against a read-only copy of the live store
(`/tmp/facts_probe.db`) and the 1A raw bundles (`/tmp/oracle_1a_bundles/`).
No index, eval, or embedding run; `:8000` (PID 94330) untouched.

## Verdict

PROCEED-WITH-CHANGES — the 2-prep **fact floor** (P23 change 2) is correctly
shaped and will turn B2 and B4 green; the anchor choice (P25) and the
over-match deferral (P24) are sound. But the recorded spec is **not safe as
written**: P23 change (1) (passing `subject` into `build_context`) activates
the *uncapped* subject-anchored **passage floor**, which on a large subject
page (Gojo = 42 passages ≈ 8.5k token-cost vs a ~5.5k passage budget)
consumes the entire 6000 budget and evicts the ranked beam. B1's ground truth
is cross-page (on Angel's page; **zero** Gojo-page chunks carry it), so B1
regresses green→red. The spec's own gate says "B1 held" — that expectation is
wrong. The recorded 2-prep spec must gain a **floor cap / beam reservation**
(or the B1 expectation must be re-anchored to "B1 may go red, cross-page gap")
before 2-prep is executed. This is a record amendment, not a 1C stop: the 18-
item re-run (the spec's own gate) would *catch* the B1 red, so the gate
mechanism is sound; only the stated expectation and the missing cap are
defective.

## Rulings on the fix-spec items

| Item | Ruling | One-line reason |
|---|---|---|
| P23 | MODIFY | The fact floor (change 2: subject's own facts lead, per-subject cap ~24, remainder from `result.facts`, total cap 30) is correctly shaped and fixes B2/B4 (Geto `occupation` is fact #13 of 19, Gojo `class`/Grade is fact #14 of 20 — both inside the 24 cap); **but** change (1) (passing `subject` in) activates the uncapped passage floor and regresses B1 — see NR1. |
| P24 | ACCEPT | Over-match verified in the live alias table: `sorcerer`→Hana Kurusu AND Jujutsu Sorcerer; `gojo`→Satoru Gojo AND Sorcerer Clan; `geto`→Suguru Geto AND Kenjaku; `pseudo-geto`→Kenjaku; 168 single-token aliases are shared by >1 node (top: `fight` 9, `battle` 8, `domain` 8). `Grade` matching "grade" is legitimate recall. After P23 no oracle item depends on the over-match — defer as a data ticket (audit single-token generic aliases at harvest; report collisions in `audit`). |
| P25 | ACCEPT | Confirmed live: `rank_subjects(link_entities(q), demote, priority)[0]` returns **"Hana Kurusu"** for both the B2 and B4 questions (character type-priority + the `sorcerer`/generic alias, not question relevance). The correct anchor is the router's `signals["subject"]` — the 1A bundles show it returning "Suguru Geto" (B2) and "Satoru Gojo" (B4) correctly. State this in the 2-prep spec. |

Tally (fix-spec items): 1 MODIFY / 2 ACCEPT / 0 REJECT.

## Why P23 is MODIFY — the B1 regression (NR1, in detail)

The fix has two serving-side changes, `hybrid.py` untouched:

1. `main.py` auto mode (lines 202, 209-216, 219-224) passes only
   `request.subject` (never `routed.signals["subject"]`) into
   `build_context`. In the 1A oracle `request.subject` is `None`, so the qa
   builder ran with `subject=None`: the R6 passage floor was off
   (`context.py:380` `passages_for_subject(subject) if subject else []`) and
   `focus` was `None`. P23 change (1) makes `main.py` compute
   `subject = request.subject or routed.signals.get("subject")` and pass it in.
2. In the qa builder, lead the fact list with the subject's own facts
   (per-subject cap ~24), fill the remainder from `result.facts` excluding the
   subject's rows, total cap 30 (replacing the flat `result.facts[:30]`,
   `context.py:385-393`).

Change (2) is correct and is what fixes B2/B4:

- B2: subject `Suguru Geto` owns 19 facts (cap 24 → all 19 lead); `occupation
  = Jujutsu Sorcerer (Former) Curse User` is store-order fact #13 (id 8616) →
  served. B2 green.
- B4: subject `Satoru Gojo` owns 20 facts (cap 24 → all 20 lead); `class`/
  `Grade = Special Grade` is store-order fact #14 (id 8192) → served. B4
  green. (At 1A the flat slice cut Gojo's facts at `Species`, fact #5, dropping
  the `class` row — exactly Finding 3.)

Change (1) is the defect. Passing `subject` in also activates:

- `context.py:352` `retriever.search(..., focus=subject)` — a vector search
  narrowed to the subject's page; and
- `context.py:370-381` the R6 passage floor — `passages_for_subject(subject)`
  leads the budget walk (line 419 `ordered = [*floor, *beam-minus-floor]`),
  cut at passage boundaries (line 420-436).

The floor has **no size cap**. Measured live (level-2 passages of each
subject page, `estimate_tokens = len/3.6 + 1`, plus the walk's +30/passage
overhead):

| subject (oracle item) | floor passages | chars | ~token-cost | vs ~5.5k passage budget |
|---|---|---|---|---|
| Satoru Gojo (B1, B4, E2) | 42 | 26,127 | ~8.5k | **exceeds — beam evicted** |
| Maki Zenin (E4) | 66 | 36,582 | ~12.2k | **exceeds** |
| Aoi Todo (C3, F1, F2) | 46 | 19,279 | ~7.2k | **exceeds** |
| Kento Nanami (E1) | 41 | 18,515 | ~6.5k | **exceeds** |
| Angel (D1) | 22 | 17,315 | ~5.6k | borderline |
| Suguru Geto (B2) | 35 | 14,497 | ~5.1k | fits |
| Hanami (C2) | 24 | 11,092 | ~3.8k | fits |
| Toge Inumaki (E3) | 21 | 10,561 | ~2.9k | fits |

For a subject whose floor exceeds the budget, the walk breaks *inside* the
floor (Gojo: after ~27 of 42 passages) and **the ranked beam is never
reached**. Whether an item still passes then depends entirely on whether its
ground truth is in the subject's own page floor (early sections) or only in
the beam:

- **Same-page GT → still green.** E1 (Nanami `Personality`), E2 (Gojo
  `Personality`, early in the floor), E3 (Toge), E4 (Maki `Personality`,
  paid at ~843 tokens), C3/F1/F2 (Todo page sections), D1 (Angel page) all
  carry their GT on the subject's own page, in sections the floor reaches
  before the cut → held (in fact reinforced).
- **Cross-page GT → red.** **B1**: subject `Satoru Gojo`, but the GT
  ("…she ought to be found so that she may help them unseal Satoru Gojo")
  lives on **Angel's** page (and 9 other docs: Ch.144/145/148/221/263,
  Takaba/Kurusu/Yuta synopses) and on **zero** Gojo-page chunks (verified:
  `SELECT count(*) FROM chunks … d.title='Satoru Gojo' AND text LIKE '%unseal
  Satoru Gojo%'` → 0). At 1A B1 passed via the Angel beat in the ranked beam
  (bundle beat #8, `Angel | Synopsis / Culling Game Arc`). After the fix the
  Gojo floor evicts that beam, so B1's GT is not served → **B1 FAIL**. B1 was
  PASS at 1A → **regression**.
- **C2** (subject `Hanami`, GT on the Todo/Playful-Cloud page, also
  cross-page) is the one other cross-page item, but Hanami's floor (~3.8k)
  fits the budget, so the beam still gets ~1.7k tokens and the GT beat
  (top-2 of the 1A beam) survives → held, low residual risk (the post-fix beam
  is `focus=Hanami`, so confirm on the re-run).

Consequence: the spec's gate line — "expect B4 green, B2 green,
**B1/B3/C2/C3/D1/E/F held**" — is wrong for B1. The fix as recorded trades a
red (B4, and B2's diagnosis) for another red (B1). That is not a net win and
violates its own gate.

## New defects

**NR1 — P23 change (1) regresses B1; the floor needs a cap (or the B1
expectation re-anchors). Blocking-for-the-record.** P23 as written passes
`subject` in, activating the *uncapped* subject-anchored passage floor
(`context.py:370-381` + walk `420-436`). For Gojo (42 passages ≈ 8.5k
token-cost > the ~5.5k passage budget) the floor fully consumes the 6000
budget and the ranked beam is never walked. B1's GT is cross-page (Angel; 0
Gojo-page chunks contain it, verified) so it is served only via the beam →
lost → B1 goes green→red, contradicting the spec's "B1 held." Remediation
(prefer the first): (a) **cap the subject-anchored floor** to a fraction of
the token budget (e.g. ≤ 60–70%), reserving the rest for the beam so
cross-page beats (B1) stay reachable — this keeps B1 green *and* keeps B2/B4
green (the fact floor is change 2, independent of the floor cap); or (b) if
the cap is declined, re-anchor the gate's B1 expectation to "B1 may go red —
cross-page state gap (D-category), not a fact-slice regression" and record
that as a known, accepted loss. The 18-item re-run (the spec's own gate)
would surface B1 red either way, so the gate mechanism is intact; what is
defective is the stated expectation and the missing cap.

**NR2 — the "shared title→alias→node-name helper" does not exist yet (note).**
P23 says to "resolve the subject via a shared title→alias→node-name helper
(the current fact lookup is a plain `n.name` match with no alias resolution)."
Verified: `facts_for` (`facts.py:1077`) and `node_by_name` (`facts.py:771`)
are plain `n.name = ? COLLATE NOCASE`; the only title→alias resolution is
*inline* in `passages_for_subject` (`facts.py:1937-1958`: exact title first,
then the `aliases` table with `ORDER BY n.is_resolved DESC, LENGTH(n.name)
ASC LIMIT 1`). So the helper must be **created** (extract that resolution onto
`FactStore`, e.g. `resolve_node(name)`), not merely "used." It is **not** a
blocker for B2/B4 — the router's `signals["subject"]` is already the resolved
node name ("Suguru Geto"/"Satoru Gojo"), so the plain match works for the
oracle — but the spec should name where the helper lives and that the qa fact
floor and (ideally) the narrative `_subject_facts` (`context.py:225-230`,
also a plain match today) share it.

**NR3 — the fact-floor remainder inherits the linker's over-matched entities
(note, tied to P24).** The "fill the remainder from `result.facts`" keeps the
over-matched entities the linker surfaced (e.g. Hana Kurusu via the `sorcerer`
alias on B2/B4) in the 10 non-subject remainder slots, diluting them. Not a
regression (the subject's own facts lead and carry the GT), but a visible
quality issue that the P24 data ticket should clear; until then the B2/B4
bundles will show spurious participants.

## Completeness questions (the pack's open items)

1. **Where does the shared helper go / does it exist?** It does **not** exist;
   see NR2. Create it on `FactStore` by extracting `passages_for_subject`'s
   title→alias resolution; reuse in the qa fact floor and the narrative
   `_subject_facts`.
2. **What if `signals["subject"]` resolves to a node with zero facts?** Safe
   and degenerate, not a crash: the fact floor contributes 0 subject facts and
   the remainder fills from `result.facts` (total cap 30); for passages,
   `passages_for_subject` returns `[]` when the subject resolves to no
   document, so the floor is empty and ranked behaviour stands unchanged
   (`facts.py:1937` docstring; `context.py:380`).
3. **Is `hybrid.py` truly untouched?** Yes. The fix is in `main.py` (compute
   `subject`) and `context.py` (qa fact floor + the NR1 floor cap).
   `hybrid.py`'s `focus` handling (`:270-280`) and the battle-page prepend
   (`:213-225`) already exist and are reused, not modified. The prepend runs
   inside `search()` (before `context.py` reorders `result.facts`) and binds
   the *battle page's* outcome facts, not the subject's — so the subject-
   anchored fact floor does not disturb it. (Forward note for 2C: the floor's
   "total cap 30" will share slots with 2A's outcome facts; bind outcomes to
   the specific fight, per P4.)

## Unverified claims

1. The exact post-fix beam composition for C2 (and any `focus=subject`
   re-rank shift) — not simulated; the 18-item re-run is the check. C2 is
   assessed "held, low residual risk" on floor-size grounds (Hanami floor
   ~3.8k < budget), not on a re-simulation.
2. Whether a ≤60–70% floor cap is the right share — the direction is verified
   (a reserved beam budget keeps B1's Angel beat reachable); the exact share
   is a 2-prep implementation detail to tune on the re-run.
3. P23's predicted B2/B4-green is a prediction (the fix is unimplemented at
   1C), but the fact-position evidence (Geto #13/19, Gojo #14/20, both inside
   the 24 cap) makes it high-confidence.

## Notes for the chairman

1. The 2-prep **fact floor** is sound and is the right fix for Finding 3
   (B2/B4): the subject's own facts lead, the target facts sit inside the 24
   cap, and `hybrid.py` (incl. the battle-page prepend) is untouched. The
   anchor must be `signals["subject"]`, never `rank_subjects()[0]` (which
   returns "Hana Kurusu" on both B2 and B4 — P25, verified).
2. The one real defect is **NR1**: passing `subject` in also turns on the
   *uncapped* passage floor, which evicts the beam on large subject pages and
   regresses the cross-page item **B1** (green→red) — the spec's "B1 held" is
   wrong. Amend the recorded 2-prep spec to **cap the floor / reserve beam
   budget** (preferred; keeps B1 green and B2/B4 green) or re-anchor the B1
   expectation to an accepted cross-page loss. Record this at 1C; it does not
   stop the 1C gate (the 18-item re-run would catch a B1 red regardless).
3. P24 deferral stands: the over-match is real (168 colliding single-token
   aliases; `sorcerer`→Hana Kurusu, `gojo`→Sorcerer Clan, `geto`→Kenjaku) and
   is ingest data quality; no oracle item depends on it post-P23. NR3 notes
   the fact-remainder dilution it causes until the data ticket lands.
4. Standing gates (eval 24/24, canon-run opm, pytest) remain the safety net;
   the fix is qa-scoped so they are the right check for any gold shift. Before
   2-prep: record NR1 (floor cap or B1 re-anchor), NR2 (helper location), and
   the P26 4C re-anchor as a pending owner decision.