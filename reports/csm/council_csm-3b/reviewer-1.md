# Peer reviewer 1 (CSM-3b council)

All five files present and non-empty (A=first-principles, B=outsider, C=contrarian, D=executor, E=expansionist).

**1. Strongest: C (Contrarian).** Only response to catch the concrete evidence gap the others glossed: the roster door — Phase 2's largest consumer (1/3 of sweep GPU-hours) — has no live proof in the 3b cycle (unit-level monkeypatched `_ask` only, plus pre-CSM-3 42aa296 evidence). C also names F1 a live armed landmine (sidecar on disk now, CPU-provenance 168 rows, no device/commit field, a fresh side session won't remember the git recovery) rather than a "documented workaround", and demands the 30-second `door=roster` probe before Phase 2.

**2. Biggest blind spot: E (Expansionist).** All upside pricing (cross-wiki D5 template, P6 unlock, gate #5, heldout fixture), zero critical-path risk. E prices a "clean close" before validating the instrument's largest consumer, ignores F3's flag-theater point, and never touches provenance.

**3. What all five missed:** (a) F1's fix rekeys the ledger files in the code Ruling 7 just shipped — migrating the committed `sweep_qa.jsonl`/`.new` pair, the 400-probe gate command that references that path, and resume-key semantics are all unbudgeted. (b) The council's new items (F1 + roster probe + optional G-CSM diagnosis) collide with the two-worker cap — a de-facto Wave 2.5 before the Phase-2 400-probe gate. (c) The 8 cumulative live rows are the only clean csm evidence; the 168 rows are CPU-provenance, so Phase 2 resumes from a provenance-tainted ledger unless re-probed.