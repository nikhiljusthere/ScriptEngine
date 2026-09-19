# COUNCIL RECORD — chairman ruling (D7 close council, #37)

**Chairman** (session `ses_f447f0f7cffeNP5LTL2em9oXNm`), ruling on the
full record: 5 advisors (A–E, `advisors.md`) + 5 peer reviews
(R1–R5, `reviews.md`). Verdict: **CLOSE**.

---

# CHAIRMAN RULING — D7 close council (#37)

## Rulings (Q1–Q5)

**RULE Q1: CLOSE NOW, via a PROVISIONAL council re-stamp.** Carries
A/B/C/E (close-now) + D's constraints, adopted through R5's bridge;
amends R4's ordering (owner word demoted from gate to post-commit
ratification). The halt rule is UNMET as registered (pool-140/358 ∈
A20 D7 holdout register, ∉ register-22 — R1 item 6, verified) and is
met via the re-stamp: register 22→24, meter 35→37, pool rows → P2
width floor, stamp marked **provisional: "council-ratified (council
#37); owner-ratified-by-return; void on veto."** D's governing share
survives verbatim in the close file: "halt rule unmet-as-registered,
met-via-provisional-stamp." No Phase-1 width leg: a new leg post-
freeze = #34 floor-moving; D59 closed the leg, not the class (the
class-scoped top_k=30 vehicle was never run) — the class survives as
the pre-registered P2 retest trigger (Q5 item 4). R3's switch
condition is adopted: if the owner's "commit" word carries the re-
scope approval, sign-off and close are the same act.

**RULE Q2: Keep ABILWIDTH dead behind its default-OFF flag; no
standalone revert.** Unanimous (A–E). Flag-OFF is byte-inert (R1 item
4, code-level); a revert owes a 4-gate re-run + owner word for zero
behavior change and burns the P6 seed + Leg-C union (`check_targets.
py:39`). The close file carries D's trap-stamp (measured RED; counter-
flips {pool-149, pool-252}; enable only via a new pre-registered
instrument + 4 gates) plus A's P6-seed line; an optional revert may
ride the TIERED-flip window (E).

**RULE Q3: TIERED default-flip = YES, post-close, its own gated owner
decision** (unanimous; the R5-reserved decision). Not inside the
close: gates default-OFF, p23 grade flag-ON. Bar: one-char commit
(`context.py:583` "0"→"1") + 4 gates flag-ON (pytest 1,331 / eval jjk
31/31 / span 48,572 + probe ≥390/400 / canon 236/236·10/16·79.0%) +
p23 473/486 repro, with JJK non-regression at flag-ON (the flag
changes JJK bundles — tier-2 append, R2 flag; E's "JJK no-op-by-
construction" invariant is read hunk-specific). Any gate RED ⇒ no
flip.

**RULE Q4: Bookkeeping as registered below.** Carries R1's facts +
R4's meter + D's relabel + E's ratification. (a) Attribution:
463→469 closed-6 = 4 deriv {arcn-01, org-05/06, vol-10} + 2 Q1-L1
{csm-dim-chap-01, csm-dim-arcn-07} (R1 item 1) — "the 2 unattributed"
was a ledger artifact (D61/63 tracked the deriv leg only). (b) Meter
at close = **37 = 24+10+3** (fixed-register semantics; 35 = the
superseded P1.4 stamp; the 10 now-green floor rows are a staleness
note, not a strike — 3 of them are flag-ON-only greens, so striking is
not provable for the flag-OFF product state). (c) FLOOR16: **relabel
14 floor + 2 ratified-width** (bookkeeping, not re-scope) and
**ratified as the 473-era denominator**; register-22 remains the
historical P1.4 stamp.

**RULE Q5: Close ritual is fully docs-only — cite camp; re-grade
rejected.** Carries R4's A/C/E executable class + R3's cut; rejects
B/D's re-grade (zero-information: expectations 469 flag-OFF / 473
flag-ON are known in advance (R2), at a :8000-window cost (R4)).
"Official suite" = cite the ledger greens @`0c8cc953` (flag-OFF =
`20d6da4e` behavior, R1 item 4) + the reboot-rule diff
`4a8616bd..HEAD` empty. "VOID formal" = R4's 3 model-free checks, run
pre-stamp (fills R1's trigger-3 gap; A/C's recast "register = 13" and
E's trigger-2-only coverage are superseded); any fire ⇒ no close,
reconvene. Stamp set = R4's 7 items, **including the auditability
fix** (the 473-era census is not in the tree: tracked census holds
469, `LEGA_*.log` gitignored, canon dir untracked — 473 must stop
being claim-only on a fresh clone).

## Pre-registrations

Exact text to land in the close files:

1. **Close-file register (13 = 11 extraction-P2 + 2 width-P2):** "13
   reds @473/486: 11 extraction-gated dim rows ⊂ register-22 (owner:
   P2 extraction track / 5.4 re-adjudication; retest: post-extraction
   re-grade) + 2 width-class rows {csm-abl-pool-140, csm-abl-pool-
   358} (defect: width — subsection recall; gold ranks 12–47 cut at
   8; owner: P2 width leg; retest: owner-triggerable per the width-
   class trigger line). PROVISIONAL: council-ratified (#37); owner-
   ratified-by-return; void on veto."
2. **VOID formal 3-check spec** (model-free, pre-stamp, receipted
   `receipts/council_d7_close/VOID_FORMAL.md`): (1) reboot_rule:
   gate-relevant diff `4a8616bd..HEAD` empty + last_green green @
   `0c8cc953`; (2) `d6_flip` rc=0 with census state **declared**
   (live = 469; campaign 473 per committed LEGA evidence — never the
   silent 469v469); (3) A20's 46-row `CONFIRM_FLIPS.json` ∩ 13 reds
   @473 = ∅, 13 derived as 17 @469 − FLIPS A from committed data. Any
   fire ⇒ no close, reconvene.
3. **Stamp set + single ordering:** VOID_FORMAL (fire ⇒ stop) →
   ratification re-stamp (register 22→24; meter 37; FLOOR16 relabel
   14+2, marked provisional) → five doc diffs in R4's order (GATE.md
   D7-CLOSE section; GATE_LEDGER `d7_close` entry — **inside the
   closing commit**, describing gate-tree `0c8cc953`, never its own
   hash; drift_log D65; `PHASE_A_COMPLETE_AT_FLOOR.md` D7 re-stamp
   with the P1.4 22-row section standing as history; `phase_status.
   txt` p14 marker) + the auditability fix (force-add LEGA 473
   evidence; `git add reports/2026-09-19-2004/`) — **one docs-only
   commit**.
4. **Width-class trigger line:** "Width-class (pool-140/358) Phase-2
   retest, owner-triggerable: one new pre-registered instrument —
   class-scoped top_k=30 campaign (NOT an ABILWIDTH re-tune; D59
   bars Leg-B knobs). Bar: flips ⊇ {pool-140, pool-358} AND 0 counter-
   flips vs {pool-149, pool-252}; blind 19/19; OOS200 floor (drop < 3
   vs `D6_OOS_PRE`); `d6_flip` rc=0. RED ⇒ kill clause: rows stay P2
   floor-registered; no ex-post re-tune."
5. **TIERED-flip bar:** "TIERED default-flip (owner decision, post-
   close): one-char commit + 4 gates flag-ON (pytest 1,331 / eval
   31/31 / span 48,572 + probe ≥390/400 / canon 236/236·10/16·79.0%)
   + p23 473/486 repro; JJK non-regression at flag-ON required. Any
   gate RED ⇒ no flip (flag stays default-OFF; campaign grade stays
   flag-ON). Optional ABILWIDTH revert may ride this window."
6. **Claim-scope line (time-stamped):** "[stamp-commit <hash>, 2026-
   09-20] CSM Phase 1 closed at the stamped floor: campaign grade
   flag-ON 473/486; shipped product (flag-OFF) 469/486; 13 reds = 11
   extraction-P2 + 2 width-P2 (PROVISIONAL, owner-ratified-by-
   return, void on veto); JJK remains 100% (4 gates @`0c8cc953`).
   This line is amended by the TIERED flip (owner option 3) if
   ordered."

## Owner's decision set

On return, four bounded choices (the provisional-stamped docs-only
close commit is already landed):

1. **"Commit" (routine)** = ratify close + re-scope → stamp final;
   the 100% claim stands in full form (item 6, un-provisionalized).
2. **"Commit without sign-off"** = close stands as a council stamp;
   re-scope pending owner re-adjudication; the 2 pool rows stay
   "holdout-pending-ratification"; claim demotes to "closed at
   floor, two in-chunks width defects deferred unsigned"; P2 re-
   adjudicates the class.
3. **"TIERED flip word"** (post-close, gated engine window) =
   authorize the flip per the Q3 bar; 473/486 becomes default
   product behavior; claim-scope line amended; optional ABILWIDTH
   revert rides it.
4. **"None — status quo"** = the provisional stamp is voided (docs-
   only reversal); the close reverts to "D7 window closed, close
   deferred"; pool rows revert to D7 holdouts; council reconvenes or
   P2 opens them.

## Execution order (standing session)

1. Run the VOID-formal 3 checks model-free → `receipts/council_d7_
   close/VOID_FORMAL.md`; 3/3 PASS or **stop and reconvene**.
2. Ratification re-stamp (register 22→24, meter 37, FLOOR16 relabel)
   drafted into the close files, marked provisional.
3. Amend the five docs in R4's order + auditability fix; **one docs-
   only commit** (the `d7_close` ledger entry lands in it).
4. The standing session must **NOT**: make any engine diff (including
   an ABILWIDTH revert); flip the TIERED default; run any width leg;
   run any p23 re-grade (only if a VOID check fires); move JJK; use
   the GPU; or treat the stamp as final before the owner's return.
5. On the owner's return, execute the chosen option (1/2/4 docs-only;
   3 a gated engine window).

## Verdict

CLOSE — the standing session executes the docs-only close now under
the PROVISIONAL re-scope stamp (register 22→24, meter 37, width
trigger line, claim-scope line), final on the owner's "commit" and
void on the owner's veto.