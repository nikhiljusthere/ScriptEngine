# The Expansionist (CSM-3b council, advisor 3/5)

Close CSM-3b — but bank the two byproducts as campaign assets, not footnotes.

**(a) Close.** All four standing gates identical to the 15:22–15:26 re-baseline, seed bank no NEW fails (11/19 · 138/148 = CSM-1b post-fix, G-CSM-1/2 persist as scheduled), sanity-4 8/8 cumulative HIT. Nothing in CSM-3b scope is left open. One condition: rule F1 a CSM-4 precondition (below).

**(b) Fix F1 before the Phase-2 exhaustive sweep — it is small, and it converts the trap into an asset.** The F1 sidecar trap (ledger pair shared per series, not per panel; a merge on one panel silently unlinks the other panel's rows — today: 168 pinned-sweep rows dropped from disk) is the seed of a general *resumable, auditable per-panel ledger*. Key the ledger by panel hash and the 17,181×3 sweep, the 200-row heldout, and every future panel get their own append-only, committable, diffable progress record. That is what turns the 1200-s incident from a one-off into a closed bug class. The git-recovery workaround is a band-aid: the third door batch's resume hits the same trap again. G-CSM-1/2 stay in CSM-4/5 — pulling them forward mixes the measurement pass with a fixing pass, and §9a (the fixing agent never grades its own fix) exists for exactly this.

**Undervalued upside if this wave lands clean:**
1. **The instrument is series-agnostic** — `build_panel`/`--panel`/`--door`/`--sanity` + Ruling-7 bare-list loading take any series. CSM is the first of the 8 wikis with a pinned, resumable exhaustive tier-1; the same sweep runs on JJK's 48,572 lines, where D5 exhaustive *has never run* (COMPREHENSION_REMAINDER §2a). That is the P6 unlock nobody is pricing.
2. **The seed-bank method** — revid-stamped `questions/csm.json` + `canon-run` (7 s, zero GPU, rc=0) — is a per-wiki comprehension smoke test. Standing-gate candidate #5 for all eight wikis: "does the engine still answer the campaign's own questions."
3. **The 200-row heldout is a free out-of-sample fixture.** A 200-probe CUDA probe is minutes — a standing early-warning number after every reindex, far cheaper than the exhaustive sweep.

If CSM-3b closes green, Phase 2 stops being "the CSM sweep" and becomes the cross-wiki D5 template. Price that, not the gate cycle.