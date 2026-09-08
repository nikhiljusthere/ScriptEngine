# First principles — CSM-3b close decision

**Strip the "gate = re-baseline, therefore complete" assumption.** The four standing
gates match the re-baseline exactly: a no-regression guard, not progress. Against the
checkable 100% definition (every line classifiable; every event with a participant
set + arc_index; the D1–D10 set), CSM-3b moved zero numbers: the only CSM-specific
signal (seed bank 11/19 exact, 138/148 canon, G-CSM-1/2 persist) is identical to
CSM-1b.

**CSM-3b is Phase 1: it builds the instrument.** Phase 2 measures (17,181 × 3 doors)
and fires D6 extraction only if the census goes red. CSM-3b's deliverable is
*measurement trust*: the roster door — structurally zeroing 1/3 of the Phase-2 sweep —
now flattens `members`/`passages`, with a roster-shaped test (suite 13/13); the sweep
now reports the hash of what it actually ran (Ruling 7); the held-out 200 has a named
consumer. The right bar for a fixing wave; met.

**(a) Close CSM-3b as a wave.** Scope complete (Rulings 1+7 verified, gates
re-baselined, `bc73795`/`78b5cf3`); do not reopen — F1 belongs to Phase 2, not to
CSM-3b's scope.

**(b) F1 is a hard precondition of the Phase-2 sweep.** The merge contract
(`span_recall.py:440-452`) rewrites the ledger with *only the current panel's keys*,
then unlinks the shared sidecar — a held-out run silently dropped 168 pinned rows.
Git is a backstop, not a state machine: the sidecar is the only thing protecting a
multi-day GPU resume. Fix — ledger keyed by the panel hash Ruling 7 already stamps —
is zero-GPU, lands in Wave 2, and yields Ruling 8's fresh-results-file for free.
**G-CSM-1/2: diagnose in Wave 2, fix only the cheap ones.** The sweep re-exposes both
gaps 17,181 times; root-cause them offline now, route expensive residue to CSM-5.
Do not fix blind before measurement.

**(c) Rulings:** (1) F1 = CSM-4 blocker, recorded in GATE.md. (2) Ruling 1 is
unit-verified only (monkeypatched `_ask`); the live check is Ruling 3's N=100 roster
sanity — record that so the done-declaration does not overclaim. (3) F2/F3: record,
no action.