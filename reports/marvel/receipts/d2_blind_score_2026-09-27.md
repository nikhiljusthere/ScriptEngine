# D2 blind-fresh set — validate + freeze + score (marvel, 2026-09-27)

Plan item: **D2 — blind fresh set (CSM Step 0 shape)** (plan §816–820) and
the D5-declaration input "blind set at declared threshold" (plan §834).
The threshold itself is a COUNCIL declaration (plan §839: "That council,
not this plan, declares 100%"; `blind_panel.py` header: "The D4 threshold
is declared in the protocol") — this receipt records the numbers +
characterization that feed that declaration.

## Protocol run (executing side = mechanics only; the questions are the
owner's, authored corpus-blind — owner-attested, no wiki/corpus/search
lookups in either round)

- Panel: v2 `reports/marvel/blind_panel_2026-09-27.jsonl`, sha256
  `61f5109376eef77b7af0eb7a73a3848440948570711368f826f1dc64bf1aa829`
  (24 subjects = 4 classes × 6; v2 = post-`_universe`-fix re-seal,
  known_diffs D2 section; v1 `623153ba…` superseded — commit `11b0dc9b`).
- Owner drafts (kept OUTSIDE the repo by protocol):
  - v1 `~/ninfer-work/d2_draft.v1.jsonl` (24 rows, one per panel subject):
    14/24 verified, floor NOT met (issue-level 3/4, universe-variant 3/4).
  - v2 `~/ninfer-work/d2_draft.jsonl` (20 rows): 4 rows dropped (no
    confident second guess from memory), 4 RESIDUE rows trimmed to their
    already-verified terms, 2 re-guesses (`Athena`; `Namor`+`Black Bolt`).
- `validate --draft` (v2): **20 rows → 18 verified, floor met in all 4
  classes** (event-enumeration 4 · issue-level 4 · state-over-time 4 ·
  universe-variant 6; floor 4/class). RESIDUE (left out of the frozen
  set): `Assault on New Olympus` (new term `Athena` unverified) ·
  `New Avengers: Illuminati Vol 1 1` (`Namor`, `Black Bolt` unverified).
- Frozen set: `reports/marvel/blind_fresh.jsonl` — **18 rows**, sha256
  `ebc7f3beaf21c6c81a886530c3b891495e39450c9e8652b5ccb99097e31a8735`.
  The executing agent never edits the frozen file (protocol); this file is
  committed as-sealed.

## Score (in-process GPU; NO `:8000` needed — local chunks + in-process
embeddings + local judge; ran with ~8.8 GB free headroom on the card)

`blind_panel.py score --series marvel` → `reports/marvel/blind_fresh_scored.jsonl`:
**18 rows, 0 errors, MECH_GREEN 13/18 = 0.722.**

| class | verdicts |
|---|---|
| event-enumeration | 4/4 GREEN |
| issue-level | 1/4 GREEN (3 RED) |
| state-over-time | 2/4 GREEN (2 RED) |
| universe-variant | 6/6 GREEN |

### The 5 RED rows (all = fine-grained credit/affiliation terms)

| row | question | missing | hits in served bundle |
|---|---|---|---|
| AvX: Consequences TPB 1.1 | Who wrote it? | Kieron Gillen | **0** |
| FF Vol 1 #328 | Who wrote and drew it? | Steve Englehart, Keith Pollard | **0** |
| Thor Vol 1 #387 | Who wrote and pencilled it? | Ron Frenz (Tom DeFalco hit) | 1 |
| Beetle (Earth-1610) | Who did the Ultimate Beetle work for? | Latveria (Doctor Doom hit) | 1 |
| Stephen Strange (Earth-199999) | Which groups was he in? | Masters of the Mystic Arts (Avengers hit) | 1 |

Systematic pattern: the served qa bundle (3,000 chars) carries the core
character/event facts but not **issue-credit blocks** — both 0-hit rows are
writer/artist questions. This is an actionable served-bundle coverage
finding for the D5 council (the issue-level door is thin on credits), NOT
a blind-set artifact: every expect term was corpus-verified at freeze
time, so all 5 missing terms exist in the corpus — the served bundle just
does not surface them.

## Interpretation + what is on the record

- The blind set (0.722) sits BELOW the C6 census (55/64 = 86%) and OOS pre
  (184/200 = 92%) — the expected direction for a blind, novel set whose
  expect terms come from author memory at finer grain than the served
  bundle's coverage. The blind set's role is precisely to find what the
  corpus-drawn arms (census/OOS) cannot. The standing guard "blind-set
  accuracy must not trail bank movement" (plan §814) is satisfied: the
  score ran against the frozen build.
- Gold-quality note (owner's own, recorded — owner/council call, not a
  blocker): 5 universe-variant rows rest on a single expect term, 3 of
  them codename-only (Spider-Man, Wolverine, Scarlet Witch) — weak
  discriminative gold that counts toward the floor. Enrichment is
  optional (add a distinctive second term from memory, re-validate; the
  panel is unchanged and nothing downstream is invalidated).

## Files

- Owner drafts (outside repo, by protocol): `~/ninfer-work/d2_draft.jsonl`
  (v2, the validated input) + `~/ninfer-work/d2_draft.v1.jsonl` (24-row
  first pass, kept for the record).
- Repo (committed with this receipt): `reports/marvel/blind_fresh.jsonl`
  (frozen 18-row set) · `reports/marvel/blind_fresh_scored.jsonl` (18-row
  score with per-row hits/missing/verdict) · this receipt.