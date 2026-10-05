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
