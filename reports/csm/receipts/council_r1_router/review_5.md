# Council R-1 (router count rule) — peer review 5 (weighted: interactions with other engine classes in the queue, R-2/R-3/R-5 + R-6/R-7 hooks)

**1. Strongest: B.** Live-probed all three kill attempts (uncovered scope stays qa; `_resolves_a_set` single caller; `_SCOPE_PHRASE` untouched), and the only one to catch a receipt error: 11 "how many" phrases, not 9 (jjk:855/881/911 hold 5; A/C/D repeated the grep line count). D strongest on gate/commit process.

**2. Biggest blind spot: A.** "No new failure class opens" is argued only against the router's own R1-d gate; zero engagement with sibling classes (R-2/R-3/R-4/R-5) or the R-6/R-7 hooks. E, the only interaction-aware response, also misjudges R-7 ("additive") and its db row proposal (misses the frozen-queue ruling and the db pin already in the new test file).

**3. All five missed:**
- **R-1×R-5** — csm declares a "Every devil contract Denji has made" roster (`series/csm/overrides.yaml`); counting relation questions ("how many devil contracts…") can be captured by the count rule before the CSM-7 relations mode lands — ordering + pin undecided.
- **R-1×R-7** — key-map/IDENTITY_FIELDS widening grows the discovered-set surface of the receipt's un-tripwired discovery-count residual; needs a post-R-7 counting probe.
- **db flip** — already tripwired by the pytest pin in `tests/test_csm_router_count_rule.py`; record in the red list, don't unfreeze the halt meter.