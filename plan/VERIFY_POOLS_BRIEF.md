# VERIFY POOLS — manual inline verification of the universal training windows

Owner (2026-10-05): "I want these 3000 windows to be flawless." Protocol:
`plan/UNIVERSAL_DATASET_PLAN.md` "Labeler + verification protocol" — manual,
inline, ONE window at a time, exact wiki pages opened, every verdict logged,
Claude audits. **No scripts that call an LLM, no batch verifiers, no loops.**
You (the opencode session) are the verifier: you read, you look up, you decide.

## What you are checking

The frozen ninfer-35B drafter (`plan/FLAWLESS_LABELING_PLAN.md` §11) wrote
candidate event rows for every window. On a blind test it was **precise (P .91)
but missed a quarter of the events (R .73)**. So your main job is FINDING WHAT
IT MISSED; striking wrong rows is the smaller job. A window with no draft rows
is NOT done: re-read every sentence.

The rules are `plan/EVENT_ANNOTATION_GUIDELINE.md`, sections A–G (read it once
at the start of every session, all of it, including the G.1 YES/NO table, G.2
ends and G.5). The 12 verbs: fought, defeated, killed, captured, escaped,
saved, betrayed, sealed, met, arrived, departed, awakened.

### The drafter's measured blind spots — check EVERY window for these

1. **Visits, arrivals and encounters with groups** — "went to check up on A
   and B", "joins up with A and B", "appears before X", "Y and Z show up where
   X is", "finds X" + contact, "both sides meet" -> `met`, one row per
   (newcomer, named person) pair, groups expanded. An entry to people not
   already present is `met` even when a fight follows.
2. **Blocks and interceptions** — "punched her but was blocked by Z", "takes
   the hit for", "intercepts the blow aimed at X" -> Z `saved` X (and the
   attacker `fought` the target).
3. **Knockouts and eliminations** — "incapacitating them", "takes X out",
   "beat him", "finishes the fight" -> `defeated` (one row per named person).
4. **Oblique fights** — "failed to defeat him within <domain>", "trade blows
   with", "continues his fight with", "matched up against ... in a battle",
   a technique used ON someone, "rejoins the fight" -> `fought`.
5. **Background mentions** — "for murdering X", "never regretted saving him",
   "X almost killed him earlier" — tense never removes an event (A.3/G.5).
6. **One sentence, several events** — check every verb whose G.1 YES fits.

### And the drafter's false-positive classes — strike these

People already together "introducing themselves" (not met); animals/unnamed
people as ends; a technique, mode or attack as the subject (write its user:
"Gorilla Mode defeated X" -> Panda defeated X); healing with no stated threat
to life (not saved); "returned to a youthful body" type changes (not
awakened); attempts never made, plans, threats, hypotheticals.

## Files (per series S; work ONE series at a time, in the order given)

- input + drafts: `series/S/training/labels/pool_in.jsonl` + `draft_frozen.jsonl`
- your saved records: `series/S/training/labels/pool_verified.jsonl` (append-only,
  written ONLY by `verify_save.py`)
- your human log: `series/S/training/verify_log/pool.md` (append one section per
  window: id, page/section, each draft row + verdict + reason, each added row +
  reason, pages consulted)

## Per window (in order, every time)

1. `scriptengine/.venv/bin/python tools/train/verify_next.py --series S`
   — shows the next unsaved window, its numbered sentences and the draft rows.
   (`WAIT` = the drafter has not reached it yet: stop and report.)
2. For every named person/creature/group in the window and every draft row:
   `scriptengine/.venv/bin/python tools/train/wiki_card.py --series S "Subject" verb "Object"`
   and open the pages that decide the row:
   `scriptengine/.venv/bin/python tools/train/page_read.py --series S "Page"` (section
   list) then `--section N [--offset 500]` (500-char chunks). Read enough to know
   who each end IS (and that it is a character/creature/named group, not a
   technique, item, species or place) and that the event is what the window says.
   The WINDOW decides what is stated; the pages decide identity and direction.
3. Each draft row: keep / fix (give the fixed row) / reject, with a one-line
   reason citing the guideline rule (e.g. "G.1 met NO: already together").
4. Missed-event pass: go sentence by sentence through the blind-spot list
   above; add every stated event with its reason.
5. Write `/tmp/vp_S.json` (the decision) and save it:
   `scriptengine/.venv/bin/python tools/train/verify_save.py --series S /tmp/vp_S.json`
   ```json
   {"id": "<window id>",
    "draft": [{"row": {"quote":"...","subject":"...","verb":"...","object":"..."},
               "verdict": "keep|fix|reject", "reason": "...", "fixed": {...only for fix}}],
    "added": [{"row": {...}, "reason": "..."}],
    "pages_consulted": ["Page / Section", "..."],
    "final": [{"quote":"...","subject":"...","verb":"...","object":"..."}],
    "notes": "..."}
   ```
   `final` = kept + fixed + added rows. Quotes copied VERBATIM from the window.
   If it says REFUSED, fix the decision and save again. Then append the same
   content to the human log.
6. Next window.

## Session limits

Verify **20 windows** per session (or stop earlier if the context grows large),
then STOP and report: windows saved, rows kept/fixed/rejected/added, and every
case you were unsure about (Claude adjudicates those). Never skip a window,
never save a window you did not read, never edit `pool_verified.jsonl` by hand.

## Order

opm -> csm -> berserk -> bleach -> db -> onepiece -> marvel -> mcu (pools),
then the held-out test windows (`--pool test`, same steps) of every wiki + hxh.

## Audit rulings (Claude; binding, read before every session)

**Audit 1 (opm windows 1-20, 2026-10-05): 4/20 windows corrected -> run paused,
rules below added, verify_save now refuses classes 2-4 mechanically.**
Corrections are in `series/opm/training/labels/pool_audit.jsonl`.

1. **Read possessives and pronouns against the whole sentence.** "Saitama and
   Tatsumaki ... accidentally show up during *their* fight and defeat Big Iron":
   "their fight" is Saitama vs Tatsumaki (they arrive mid-fight with each
   other), so Saitama `fought` Tatsumaki — and NOT `fought` Big Iron (the
   defeat row covers it; write `fought` beside `defeated` only when a fight
   with that opponent is stated separately). Their entry also `met` everyone
   present they were not already with (Feather, Big Iron).
2. **Named group vs its members (G.2):** a group ("the private squad",
   "Narinki's Private Squad", "the Iron Fist gang") is an end ONLY when the
   window names none of its members. If it names members (Noria, Sanshon), write
   one row per named member and no group row.
3. **Species / race pages are never ends** (JJK calls them `species`, OPM
   `race`): "The Subterranean People" -> no row. wiki_card's species warning is
   binding, not advisory.
4. **Indefinite descriptions are never ends** ("a monster disguised as
   Waganma"); use the window's definite description for the same individual
   ("the monster") or its name.
5. `met` and `fought` are symmetric: ONE row per pair (not "A met B" + "B met A").
6. "X appears being defeated by Y" with X then rescued is a defeat in progress
   (G.1 defeated NO) -> `fought`.

**Audit 2 (opm windows 21-40): 4/20 corrected. Claude now reviews EVERY saved
window (100%, not 5%) — the worker's window accuracy is ~80% in both sessions.**

7. **A row must be true in the window's own words.** "being injured by King
   (unaware that it was actually Saitama who kicked him)" -> Saitama fought
   Garou, and NO King row: a character's mistaken belief is not an event.
8. **"finishes off X" is G.1 `defeated` YES** ("finishes the fight"); `killed`
   only when the death is stated — check the page: if X survives, `defeated`.
9. **Ability / Appearance descriptions** ("this light is bright enough to blind
   both A and B", "can activate accidentally") are not attacks made on someone
   unless the window narrates the attack as an act against them.
10. **Attacks on a building or place** ("unleashed this attack on the Hero
    Association headquarters") are not `fought` with the organization.

**Audit 3-4 (opm 41-75, csm 1-40): 4/75 corrected** (take-by-surprise is not
captured; a group's arrival meets everyone present; "not enough to stop her" =
escaped; "kills X" stays killed even if X revives).

**Worker switch (owner 2026-10-05 ~14:10):** Space Bunny sessions stopped at
opm 75 / csm 40 verified (all reviewed). Verification resumes on the local
**ninfer 27B** (`-m ninfer-27b/qwen3.8-27b-ninfer`; owner: smarter and faster)
once the 35B finishes the pool + test drafting; same brief, same rulings,
Claude still reviews every saved window.
