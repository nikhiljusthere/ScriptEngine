Contrarian pass: I tried to kill this draft three ways and it survived.

(1) False-roster on a counting topic the set does not cover: probed live (model-free route()). "How many members are in the Four Horsemen in chapter 100?" → qa; "How many special divisions exist in the manga?" → qa; onepiece "…in the manga?" → qa. The narrower guard is real: a scope not inside the matched phrase survives into parse_constraints as an unverified qualifier → partial → the R1-d counting gate (exact/declared only) refuses. The only scope words that are dropped are the wiki's own title (strip_work_title) — the series name, not a scope. The db qa→roster flip is the same bug shape fixed, not a new hole.

(2) G1 other callers: _SCOPE_PHRASE has exactly one caller (the non-counting branch of _resolves_a_set), byte-identical in the diff; _resolves_a_set has one caller (has_set). No other path sees the new probe.

(3) JJK regression: every pin verified live — Geto subset count qa, full-set count roster, Kenjaku wards qa, hxh Nen roster. The "how many" audit holds but the receipt undercounts: 11 phrases across 5 series, not 9 (jjk 855/881/911 hold 5). All 11 have a shorter sibling, so stripping "how many" never orphans a declaration. I re-ran the 11 tests myself: 11/11 in 3.2 s. No staged files; diff is the claimed +23/-1.

Right fix class: yes. A per-wiki override would have to key routing on a series name in .py — forbidden; the rosters already exist and the fix fires only where a declared phrase matches (pinned: no-roster series → qa, no raise).

One real residual: discovery-side counts (undeclared set, ≥3 members → "exact") now keep their scope in the probe; no such case exists in the suite, the four gates are the named tripwire. Correct the receipt's "9" → 11 before commit.

VERDICT: SHIP / FIRST STEP AFTER VERDICT: run the four standing gates with the receipt's exact commands (expect pytest 1,265 / eval 31/31 / span-recall 48,572 / canon 236/236 · 79.0%), then R-1 class re-sweep ≥1 HIT, then commit / CHANGE-OF-MIND IF: any gate regresses below the 2026-09-08 baseline, or the R-1 re-sweep shows 0 HIT on its own new rows (halt to council per R5), or the router suite shows a new qa→roster delta beyond the db flip.