# The Expansionist — COUNCIL_csm-3 advisor response (run 1)

Completed in workflow ffe7b645 (run 523a4478-f48c-4f73-8e50-20948e3320fe); recovered verbatim after the workflow crashed at the peer round (the reviewer agent lacks bash for the verification commands).

**(a) All four traps + addendum criteria met — and the infra is bigger than the record says.** Panel hash recomputes (e3d73720… matches the pin), sweep/held-out disjoint, floor respected; wired resume, full-denominator hit_rate, and the exit-3 sanity halt are in code with 4 tests (1,253 collected). The upside everyone is missing: it's all series-agnostic — `--make-panel`/`--panel`/`--door` take any series. CSM-3 is the first exhaustive tier-1 instrument any of the 8 wikis has had; JJK's 400-probe shortcut becomes optional, and P6 inherits the hashed, resumable sweep for free. CSM-4 dry-runs an instrument seven other corpora will reuse.

**(b) Honest.** It's ruling 4b's own authorized option, and the census verifies: 775 sub-6-word lines, all in chunks, list-shaped sections (Manga Chapters 133, Chapters 114, poll rows). The floor is a dial, not a wall: `min_words` is a parameter + CLI option, recorded in the panel metadata — a later re-pin at `min_words=1` re-includes all 775 with zero code.

**(c) No JJK regression:** the legacy branch is untouched (`if probe:` → `elif probe:`, title change only); seed-7, sample=400, append-mode jsonl preserved as the recorded exception; the gate re-ran identically at 390/400 on the 1,249 tree before CSM-3. Upside: a pinned 400-line JJK sub-panel (400-row JSON + `--panel`) upgrades the standing gate to resume + hash + full denominator, zero code.

**(d)** (1) Sanity policy: run `--sanity 200` per door in one ~40-min session — a healthy door has near-zero probability of a zero-hit 200-subset, a dead qa leg (G-CSM-2) trips exit 3; one cheap session de-risks the whole sweep. (2) 58h is now the *measured* number (17,181 × 3 × 4s ≈ 57.3h), replacing the 51h estimate — plan 6–9 chained 100k sessions, one per door; a dead door then costs only its sanity run. (3) A C-side task brief (gpu_gate3_task.md shape) naming per-door commands + the GATE.md landing spot; §9a: fresh session, never the f93d396 author.

**Verified:**
- `git log --oneline -8`; `git show --stat f93d396`; `git show --stat 2c80867`; `git show f93d396 -- scriptengine/cli.py` (full CLI diff: legacy branch vs new sweep branch)
- python one-liner: `json.load` of `reports/csm/panel_csm.json` + `panel_csm.json.heldout.json` — recomputed `sha256(json.dumps(panel, sort_keys=True))` = e3d737205cd07245… = pinned hash; panel 17,181 / held-out 200 / overlap 0 / min line 6 words
- python one-liner against `series/csm/facts.db` via `span_recall._corpus("csm")`: 775 sub-6-word lines in non-boilerplate sections, all 775 present in a chunk; section histogram (Manga Chapters 133, Chapters 114, arc lists, poll rows)
- `pytest tests/ --collect-only -q` → 1,253 tests collected
- read: `scriptengine/eval/span_recall.py` (build_panel, pinned recall branch, legacy branch), `scriptengine/cli.py` L1995–2220 (both command registrations, sweep/probe branches), `tests/test_span_recall.py`, `series/csm/overrides.yaml` (floor decision comment), `reports/csm/panel_csm.json` metadata, the four context files
