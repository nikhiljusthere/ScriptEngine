# Decision: one engine, per-wiki declarations (no per-franchise code)

Decided 2026-09-28 (architect session), on the owner's question: *"should we have different files for different anime, as some of them have different structures and infoboxes, or modify the existing files to accommodate changes?"*

## The decision

1. **One shared engine** (`scriptengine/`) serves every franchise. There are no per-franchise Python modules, no `if series == ...` branches, and no forks.
2. **Everything that differs per wiki is declared** in `series/<name>/overrides.yaml`: type names, placement types, where the narrative lives, time-axis signals, the reality/partition convention, furniture sections, citation grammar, roster registry, and so on. The full list of keys is in `OVERRIDES_REFERENCE.md`.
3. **When a new wiki has a shape the engine cannot express**, the engine gains a **generic mechanism plus a new override key**, and its **default reproduces the old behavior exactly**. So yes, onboarding a new franchise *does* modify shared engine files, but only in this additive, default-preserving way. The four standing gates plus a pin test prove every existing wiki is byte-identical.
4. **Per-franchise files are data and records, never logic:**
   - `series/<name>/overrides.yaml`: the declarative profile.
   - `plan/<NAME>_100_PLAN.md` + `plan/SWITCHPOINT.md` entries: the campaign.
   - `reports/<name>/`: receipts, councils, surveys.
   - Campaign scripts, when needed, are thin CLIs parameterized by `--series` (see `CAMPAIGN_TOOLS.md`).

## Why

- **It already works at scale.** Nine wikis (JJK, CSM, OPM, Bleach, HxH, Berserk, Dragon Ball, One Piece, Marvel/MCU) run on one engine. Seven onboarded with only an `overrides.yaml`.
- **Every Marvel fix this campaign was generic + declared, and improved the engine for all wikis:**
  - `placement_types` (MCU `conflict`, Marvel `story_arc`);
  - narrative fact passages (`history`, `synopsis*`);
  - a heading-agnostic prose scope with a counted furniture list;
  - an override-declared time axis (date / chain / order / partition);
  - a reality-aware participant resolver;
  - NOCASE indexes and store memos (a 36–42× retrieval speed-up, byte-identical).

  In a fork each of these lands once and rots in the others.
- **The baselines stay provable.** JJK (100%) and CSM are the regression reference. "JJK stays byte-identical" is only checkable when JJK runs the same code the new franchise changed.
- **The test matrix stays one matrix.** Per-franchise code multiplies tests, gates and bugs; per-franchise data does not.
- **CLAUDE.md rule:** *"if a fix mentions a series name and lives in a `.py` file, it is in the wrong place."* This extends to a series' *conventions*. Example: the regex for Marvel's `(Earth-616)` suffix was sent back from `events.py` to overrides (review R8, 2026-09-28).

## The trade-off, and how it is contained

The engine accumulates knobs. That is contained by:
- `OVERRIDES_REFERENCE.md`: every key, its reader, its default, an example;
- defaults that preserve prior behavior, pinned by a test;
- `tools/survey_wiki.py`, which proposes values from the data so nobody guesses them;
- dead keys retired when found (`archetypes` is declared by csm/jjk but read by nothing, 2026-09-28).

## How to apply, on each new wiki

Survey → declare → re-index → verify. If a declaration cannot express the shape:
1. write a design note (`reports/<name>/DESIGN_*.md`) naming the generic mechanism and its new key;
2. get an architect review;
3. implement it with default = old behavior;
4. write tests (including one proving the default is inert);
5. pass the four standing gates;
6. declare the key for the new wiki.
