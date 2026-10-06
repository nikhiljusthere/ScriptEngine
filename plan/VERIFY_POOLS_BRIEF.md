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

**Audit 5-12 (27B sessions, ~240 windows): ~5% corrected.** Two recurring misses:

11. **Never name an end from outside knowledge.** "Wyald is the first apostle that is
    killed by another apostle" -> NO row (the window never says Zodd; "another
    apostle" is indefinite). The page you opened tells you who someone IS; it never
    supplies an end the window does not state.
12. **Ruling 1 again — entries meet everyone present.** "X, Y and Z emerge from the
    anomaly" in front of A and B -> X/Y/Z met A and B; reinforcements arriving where an
    enemy is attacking -> met the enemy too (and fought, if they attack). Check every
    "appears / emerges / arrives / turns up / responds to a call" sentence for it.
13. A character's catchphrase or boast in a quote ("I've come from the depths of
    Hell!") is not a narrated event.

## Single interactive session mode (owner 2026-10-05 ~21:20) — SUPERSEDES "Session limits" and "Order"

One opencode session (the owner's interactive window), the 27B at its full 262k
context, ONE window at a time, continuously:
- Do NOT stop after 20 windows. After each saved window, run verify_next.py again and
  continue. When a series says ALL VERIFIED, move to the next one.
- Remaining order: opm -> csm -> berserk -> bleach -> db -> onepiece -> marvel -> mcu
  (pools), then `--pool test` for opm, csm, berserk, bleach, db, onepiece, marvel,
  mcu, hxh.
- Decision file: /tmp/vp_<series>_<pool>.json (one at a time, overwritten per window).
- Every 25 windows, re-read the "Audit rulings" sections of this brief (they grow as
  Claude reviews your saves).
- If the context gets long, opencode compacts automatically; after a compaction,
  re-read this brief before the next window.
- Claude reviews every saved window and corrects/logs disagreements; never edit a
  saved record yourself.

**Audit 23 rulings:**
14. **Dreams, visions, hallucinations and imagined scenes are not events.** "In his
    dream ... a small dog-like being ... its jaws kill Casca" -> no rows. A real event
    recalled in a dream or flashback still counts (A.3); what happens only inside the
    dream does not.
15. **Accidental hits on allies are not fights** ("Power drives into him and Denji" —
    she rams the enemy, Denji is collateral; "Rika's attack struck Yuta"). Write the
    intended target only.
16. "the rest of the squadron / team / group" is an unnamed group — never an end.

**Audit 28-36 (Bleach) — the recurring miss:**
17. **Blows and contact mentioned in passing are events.** Slaps, punches, kicks,
    clotheslines, "pins her against a pole", "thanking Isshin for hitting him", "reels
    back with a bloody nose ... wants to be punched again", "a childish fight", "knocking
    his mask off" -> `fought` (comedic or not). Encounters told in passing too: "is
    confronted by her aunt", "asks him if he is a member of the Kuchiki Clan" (first
    contact) -> `met`. Re-read every sentence of a window once more for these before
    saving — they are most of what Claude's review still adds.

**Audit 37-38 (DB) — transformations:**
18. **Using a form the character already has is NOT `awakened`**: "Vegeta transforms
    into a Great Ape", "Gohan turns Super Saiyan 2" (he already had it), "Broly takes on
    his Legendary form", "both of them transform" (hybrids). `awakened` = a FIRST-ever
    transformation or a newly gained power ("Goku becomes a Super Saiyan for the first
    time", "the dragon unlocks his latent potential"), waking up, or being revived
    ("Piccolo revived Gohan ... heart beating again" -> Gohan awakened).
19. "mortally wounding him", "fatal blow" without a stated death -> `fought`, not
    `killed` or `defeated`. "overpowered" mid-fight -> `fought`.

**Audit 43-44 (DB):**
20. **A battle list IS events** ("Battles Featured", "X vs. Y" lines, a "vs." title):
    one `fought` row per opposing pair, the line as the quote; skip illusions, image
    training (imagined) and self-fights. Never rule such a list "structural".
21. **Different characters that share a name are different ends**: Goku / Goku Black,
    Gohan / Future Gohan, Buu / Kid Buu, Zamasu / Fused Zamasu. Write the name the
    window uses; verify_save now decides "same person" by the wiki page, not by words.

**Audit 49-51 (One Piece):**
22. **A definite description of ONE individual is an end** (rule 4), not an unnamed
    class: "a Plesiosaur attacks ... the monster carries Nami off" -> the monster
    `fought` Luffy / Zoro, the monster `captured` Nami. Only plural or class nouns
    ("the Marines", "the opponents", "the subordinates") are never ends.
23. **Attacks told in passing are `fought`** (ruling 17 again, the commonest miss):
    "hitting Vivi", "she exploded Igaram's ship", "help Luffy fight off the admiral"
    (the helper fought too). Fainting from a trick or a fright caused by X -> X
    `defeated` the one who fainted. "run to her aid" against a threat -> `saved`.
    "The group docked at X" -> one `arrived` row per member the window names.

**Audit 58 (Marvel, 8/30 windows corrected):**
24. Marvel synopses are dense with the commonest misses — re-read every sentence for:
    walk-ins and visits ("Fury and Quake walk in on Phobos", "Lisa visits Ralph",
    "goes out clubbing with ... Victor") -> `met`; finding someone mid-fight -> `met`;
    a portal / teleport that pulls named people away against their will -> `captured`;
    "fled ... to escape the threat" -> `escaped` the named threat; "the Avengers attack X"
    when the window names an Avenger -> member rows only (G.2); manipulating two named
    groups "into a fight" -> the groups `fought`.

**Audit 81-82 (MCU):**
25. **A character's claim, lie or accusation is not the event** (a recap, flashback or memory of
    something that did happen still is: "the memory of Thor murdering Thanos" -> killed). "Hoffman told the police that
    the vigilante was the one who killed Blake" is Hoffman's lie -> no `killed` row (the
    narrated event "got information from Blake before he died" is `met`). Label only what
    the passage narrates as happening; MCU synopses quote characters' versions constantly.
