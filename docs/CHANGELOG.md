# Changelog

Dated log of changes made through prompt-driven work sessions on this project.
Newest entry first. Git commit history (`git log`) remains the authoritative
record of code changes; this log exists to track intent and doc/workflow
changes at a coarser grain, including things that don't map to a single
commit.

## 2026-08-12

- Deleted `OBSIDIANPLAN.md` (root) — pre-implementation design doc for the
  Obsidian export feature; the feature it planned is now fully built
  (`scriptengine/export.py`, the `export` CLI command, `tests/test_export.py`,
  and README/CLAUDE.md both list it done). Nothing referenced the file.
- Deleted `Plan to follow.md` (root) — untracked scratch planning file.
- Deleted six superseded dev-log snapshots from `scripts output/`:
  `Engine Answer Sheet.md`, `Engine Answer Sheet 2.md`,
  `Engine Answer Sheet 3 - Ontology.md`, `Engine Answer Sheet 4 - Real Topics.md`,
  `Engine Answer Sheet 5 - Character Scoped.md`,
  `Engine Answer Sheet 6 - Online Comparison.md`. Kept
  `Engine Answer Sheet 7 - Canon Recheck.md` as the current one.
- Deleted four superseded canon-score snapshots from `scripts output/`:
  `canon_scores_after.json`, `canon_scores_after_diagnosis.json`,
  `canon_scores_before.json`, `canon_scores_before_diagnosis.json`. Kept
  `canon_scores_pagefirst.json` as the latest.
- Added `docs/STRUCTURE.md` — full directory/module inventory, complementing
  `ARCHITECTURE.md`'s design rationale.
- Added `docs/ROADMAP.md` — phase status table plus narrative on open phases
  (5, 6, 20, 21) and longer-term direction.
- Added `docs/CHANGELOG.md` (this file).
