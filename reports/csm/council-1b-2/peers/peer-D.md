# Peer D — review of advisor responses A–E (council 1b-2, CSM-1b + CSM-2)

**1. Strongest: D.** Only D caught the receipt conflict: the 0752 bucket table
assigns the missing Makima item to "extraction gap — fix the prompt in
`ingest/abilities.py`", but the CSM-override REFUTED note (2026-08-17) records
the extraction *correctly* returning `[]` (the wiki never names the contract).
A fixer following the bucket table patches a refuted prompt and the cached
answer survives. D also forces a ruling on csm-set-14: 0752 buckets 3 of the 5
divisions as "corpus gap" ("the wiki does not support the claim"), unreconciled
with the 2026-08-15 roster audit — accept or retire. Both verified in-tree.

**2. Biggest blind spot: A.** Only A misses that GATE_REBASELINE's 1,242
predates CSM-2's +7 tests (tree now 1,249) — the gate baseline is no longer
reproducible. A also rubber-stamps (b) "complete" and never questions
G-CSM-2's under-scoping; E's "fix G-CSM-4 first / G-CSM-2 as CSM-3's first fix"
smuggles fix-work into an item scoped as measurement infra.

**3. All five missed:** CSM-3's mechanical scope. Nobody re-verified the four
§2a traps (seed-7 shuffle, unwired `done` dedupe, partial-denominator
`hit_rate`, zero-measurement doors) or the tier-0 rename (blind spot 5) against
the tree — all still open (verified in `span_recall.py`/`cli.py`). The
re-baseline must also rewrite the stale baseline record (CLAUDE.md and plan
item 8 still pin 1,242).