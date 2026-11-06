# Rulings pass 2026-11-04 — agent brief

You apply the 2026-11-04 rulings to one candidate list of windows. Tools run from the worktree
`/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags`; your files go in this directory
(`/home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/`).

## Read first (in this order)
1. `plan/review_tools/gold27_system.md` — the whole file; binding: "Owner ruling 2026-11-03" (decide every outcome
   row from the factual state the passage establishes; one act can carry several true rows; write all the text
   supports and none it does not) and "Rulings 2026-11-04" (the open questions, now decided).
2. `plan/BIG_REVIEW_PATTERNS.md` — the A-table at the top (A2, A8, A11, A53, A74, A75, A113, A116, A145 ...).
3. `series/universal/training/big/outcome/SUMMARY.md` — "Decision rules applied" (same rules, big set).

## Your list
`list_<NAME>.txt`: one line per window, `b<n> CLASS: hint ; CLASS: hint`. `# group ...` lines join big overlap
partners: partners share sentences and must be edited identically (same rows for the shared sentences). A `PARTNER`
line is listed only as a partner. Classes are heuristic hits: READ each window; many need no change.

- CAPT   fought + captured/sealed for a pair, no defeated -> ruling "CAPTURED / SEALED AS OUTCOMES".
- STOP   `X|other_verb|stopped/prevented/foiled/thwarted/...` actual. A completed stop of a NAMED person or of a named
         person's plot/crime is the event `X|defeated|Villain` (2026-10-14 ruling) and the other_verb fact goes (`f-`).
         Keep the fact when the stop is of a thing/disaster with no named villain, of an ally, of a self-harm, or inside
         an ongoing exchange; a purpose clause ("went to stop him") is `planned` (fix modality with f- + f+ if actual).
- FW     a stated wound inside a fought row's quote (shot, stabbed, severed, impaled, set on fire ...) with no wounded
         fact -> `f+ Attacker|wounded|Victim|quote`; `defeated` too only when nothing continues (Klaue test); A145
         drops `fought` only when fight and outcome are one stated act.
- WBY    `Victim|wounded|-` where the sentence names the doer -> `f- Victim|wounded|-` + `f+ Doer|wounded|Victim|quote`.
- ESC    defeated row whose quote says the beaten side fled/retreated/went into hiding, no escaped row ->
         `+ Beaten|escaped|Winner|quote` (A74).
- TEAM   team-up outcome credited to one doer -> the partner named in the same clause gets the same outcome row.
- NEAR   `X|other_verb|V` stated from a "nearly/almost V" quote -> certainty denied (`f-` + `f+ ...|actual|denied|`).
- PATIENT patient written as subject ("X was attacked by Y" as X|attacked|Y) -> reverse the roles.
- LISTED a window named in an open ruling; the hint names which. Decide it by the 2026-11-04 rulings.
Fix what the class or ruling concerns, plus a plain error in the same rows (reversed row, a row contradicting a
ruling). Do not restyle rows that are fine.

## View
- gold: `BV2_SET=gold bash plan/review_tools/pre27.sh show B [B ...]` (full rows; ignore the old "27B" answer)
- big:  `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine /home/goblin/ScriptEngine/scriptengine/.venv/bin/python plan/review_tools/outcome_scan_big.py show B [B ...]`

## Fix files
```
@<b> rulings 2026-11-04: <reason, citing the ruling>
keep
r Old=>New
- S|verb|O
+ S|verb|O|quote
f- S|rel|O
f+ S|rel|O|quote|modality|certainty|asserted_by     (omit the last three for actual/stated/none)
t- tag|quote-prefix
t+ tag|quote
```
`defeated`/`saved`/`killed`/`escaped`/`captured`/`sealed` are EVENTS (`+`), never `f+`. Removals use the exact strings
shown in the rows. Quotes: verbatim window text, >=12 chars, no `|`. Files: `<NAME>_01.txt`, `<NAME>_02.txt`, ...
(at most ~15 windows each). A window needing no change gets NO block (note it in your notes).

## Submit — `rv.sh fix` is NOT idempotent (every run appends records)
Per file, in order:
1. dry run until 0 refused and no unmatched removal:
   gold `bash plan/review_tools/outcome_scan_gold.sh check FILE`;
   big `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine /home/goblin/ScriptEngine/scriptengine/.venv/bin/python plan/review_tools/outcome_scan_big.py check FILE`
2. never submit a file already in `ledger_<NAME>.txt`;
3. submit ONCE, under the shared lock (three agents append to the same big audit file):
   gold `flock /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/.submit.lock env BV2_SET=gold bash plan/review_tools/rv.sh fix FILE`;
   big `flock /home/goblin/ScriptEngine/series/universal/training/big/rulings_2026-11-04/.submit.lock bash plan/review_tools/rv.sh fix FILE`;
4. immediately append `FILE  b... (applied N)` to `ledger_<NAME>.txt`.
If restarted, read your ledger and notes first and continue after the last submitted file.

## Notes
`notes_<NAME>.md`, updated after every file: per window `b<n> CLASS changed|no change: why`; a section "For the
owner" (cases the rulings do not settle: leave them unchanged, do not guess); "Counts" per class (read / changed /
no change). Final message: counts, files, owner questions, new patterns.

## Do not
- use the GPU or start a model server; edit code, docs or the catalog; commit; run `rv.sh mark`; touch a window
  outside your list; edit gold b825 b893 b1014 b3543 b3657 (waiting for an owner decision on the fact gate);
- kill processes by pattern (`pgrep -f` / `pkill -f`).
You may be stopped at any time (usage limit): keep ledger and notes current so a successor can resume.

## Addendum 2026-11-04 (owner rulings: torture, mind control, clinical death)
Read `gold27_system.md` "Owner rulings 2026-11-04 (torture, mind control, clinical death)". Classes in the tc lists:
- TORT / TORT?  a fought/defeated row for cruelty to a captive or helpless victim -> `f+ T|tortured|V|quote`, drop the
  fought/defeated (`- T|fought|V`), add wounded/interrogated/killed only as stated. A real fight keeps its rows.
- CTRL  an event near a mind-control/possession cue. If the window states that the doer acted under someone's
  control and not by his own will: remove the plain event and add the controlled fact
  (`f+ B|attacked|C|quote|controlled|stated|A`, outcomes as `f+ B|other_verb|<verb>|quote|controlled|stated|A`).
  Most CTRL hits are the controller's own acts, the victim's resistance, or control that ended: no change.
The new relation `tortured` and modality `controlled` are in fact_gate (the dry-run check accepts them).

## Addendum 2 (2026-11-04 evening, decisions on the TCG questions)
- A creature or person acting on a summoner's or master's COMMAND is an `ordered` act (`Y|other_verb|V|...|ordered|
  stated|X`, plus `X|ordered|Y`); `controlled` is only for stated mind control / possession / hypnosis /
  programming by a named controller (asserted_by = that controller).
- A controlled act the doer partly resists by his own will ("purposely missed any vitals", b1989): the act stays
  `controlled`; the resisting act is the doer's own actual fact (`Mockingbird|other_verb|missed|quote`).
- other_verb objects are the quote's own verb word, also under `controlled`: "shot in the head" ->
  `B|other_verb|shot|...|controlled|stated|A` (+ `B|wounded|C|...|controlled|stated|A` when injured), never an outcome
  word the quote does not contain. Re-check gold b1989 and b2041 (TCG_01) for this and fix them in your first file
  if you are the agent with list_TCG_rest.txt.
- Torture of a captive also seen as `defeated` (b1861) or as `fought` beside a capture (b10653 Nebula): `tortured`.
- RESUME lists (`list_R_B1/B2/B3.txt`): read your predecessor's notes_<B1|B2|B3>.md first. Its drafts ("STOPPED HERE")
  must be re-read against the window before use; its "no change" decisions stand. Some lines also carry TC classes.

## Addendum 3 (2026-11-04 night, decisions on the second round's questions)
- Shooting, stabbing or killing a hostage/captive is NOT `tortured` (that is cruelty to make him suffer): write
  wounded / killed as stated. Fix b12511, b12550 (RB3_*) if they carry `tortured` for a shot.
- An arrest or capture of someone who does not resist is `captured` alone (no `defeated`): fix b12634.
- A stun shot that knocks out a hostile target = `defeated` (knockout); no `wounded` unless an injury is stated.
- "was informed / told that X had shot Y" (b12346): the act is known only from a report -> A113 claimed fact.
- Possession: the possessed body's acts are the body owner's acts under the possessor's control (`B|attacked|C|...|
  controlled|stated|A`), not the possessor's plain events (b12392: Victor under Jonah).
- Two named controllers of one act: one controlled row per controller (asserted_by differs) (b12405).
- Forced by threat or command ("made her stab") with no stated mind control: `ordered`, not `controlled` (b12319).
- Hypnotised by A while obeying B's command: modality `controlled` (asserted_by A) + `B|ordered|X` (b9001).
- A remotely piloted body or symbiote acts under its pilot's control: `controlled` (b8123 Dylan).
- Brainwashing stated with no named controller, or only implied/ordered: plain events (b6150, b8902, b9312, b1159).
- One modality per row: when an act is both attempted/ordered and controlled, `controlled` wins.
- Any act can be controlled (arrivals, speech): yes (b526/b9628, b2226).
- A torture that follows a fight the victim started: the fight keeps its outcome rows; the torture adds `tortured`.
- Restraining a captive with no cruelty (b1503) is no torture: keep what the text states.
- Intercepting a killing blow on a named person = `saved` (b6539 Kindred|saved|Spider-Man).
- A foe who leaves under a stated threat (b6609 Galactus, Ultimate Nullifier) = `defeated` for the one who made the
  threat, + `escaped` only if the text says he fled.
- Partners differ where one window does not name the ends (b2514/b9590 vs b2841): leave the window without the
  names as is and log the pair in recon/exceptions.txt (`C<id> bA~bB reason`).
- Rows the scan did not flag but that contradict a ruling (e.g. `Controller|fought|Victim` for "enthralled",
  "enslaved", "infected"): fix them when they are in a window you are editing.

## Addendum 4 (2026-11-06, Claude, decisions on the open "For the owner" questions; owner delegated)
Decided factually under the owner rulings of 2026-11-03/04. Each line: the rule, then the windows it settles.
- Capture after STATED resistance ("went for his gun", "tried to fight back") = `defeated` + `captured` (the CAPTURED
  ruling's "stated resistance"): b12972 Dottie Underwood|defeated|Pike.
- "made it clear that", "revealed that", "it became clear that" narrate the act as true (factive) -> the event stays;
  A113 is only for says/claims/tells/explains/boasts (b13643 Will Simpson|killed|Clemons kept).
- A plural class or army noun with no proper organization name ("Conquistadores", "soldiers", "the guards", "the
  villagers") is a crowd (A5): no end; a named member tied to the act takes the row. A named organization
  (Ten Rings, Watchdogs, S.H.I.E.L.D., the FBI, A.I.M., HYDRA) is an end (b13854 b13859 b13863; b1973 b724 b6277
  FBI kept).
- A stop of a named person's attack that ends his part (Osiris stops Spector's punch at Harrow and forbids violence)
  = STOP rule + INTERCEPTED ATTACKS: `Stopper|defeated|Attacker` + `Stopper|saved|Target`, the other_verb fact goes
  (b13741). A halt by mere arrival with no subdue stays a fact (b3771). A stop of one instance of a continuing scheme
  whose head is absent and the scheme goes on stays a fact (b7522, b5203).
- Control stated but no controller named for THAT person (Betsy "involuntarily" b9588/b9594; an army brainwashed as a
  group with named members not individually tied b6477/b6763; "the enthralled Hernandez" b2342; "the
  mind-controlled Pike" b2652): plain events (Add.3 "no named controller").
- WILL DECIDES with a symbiote/possessor: when the window gives the host his own will or motive ("his sadism",
  "vengefully", b6522; Otto "by his own power" b5687) the acts are the host's plain events.
- A creature or ally "unleashed" / "sent" on a target by a master: `ordered` (Add.2); `controlled` only if the window
  states the master controls its mind/body (b8302: read the window; Puppet Master's puppet control stated ->
  controlled|stated|Puppet Master, else ordered).
- A stun/sedative shot (I.C.E.R., Night-Night Gun) that knocks out a HOSTILE target and ends the encounter =
  `defeated`, no `wounded` (Add.3; b4016 Ward|defeated|Peterson if the window ends there). Stunning an ALLY to stop
  him (b10667 Hunter stuns Skye/May to chase Creel alone) = ALLY RESTRAINING ALLY: `Hunter|other_verb|<quote verb>`
  per ally, no fought/defeated.
- Stabbing a held ally to cure him (b2041 big: Norman stabs the sin-filled Peter) = ally act: `Norman|other_verb|
  stabbed|Peter` + the wounded row; no fought.
- Mind manipulation / hypnosis written as `fought` (b79 Mastermind's illusions in Phoenix's mind, b653 "freed from
  A.I.M.'s hypnosis", b1242 Puppet Master's commands): A116 - drop the fought, the control is the controller's
  `other_verb` fact with the quote's own verb; Phoenix/Michael/Iron Man's acts under it follow the controlled rule
  when stated.
- Torture of a captive after a fight the victim started keeps the fight's outcome row (Add.3): b1453/b8155 restore
  `Morbius|defeated|Vic Slaughter` on the clause that ends the rampage; `tortured` stays.
- Killing/staking a bound captive is no torture and no fight (Add.3): b7573 Eisner stakes the tied Dracula ->
  `killed` only if the window states the death, else `Marie Eisner|other_verb|staked` (+ `wounded`); b7563 (no
  capture sentence) stays; log the pair in recon/exceptions.txt.
- Add.3 decisions that were noted but may not be applied yet: b6539 + `Kindred|saved|Spider-Man`; b6609
  `<threat-maker>|defeated|Galactus`. Check current rows before adding.
- A8 strict reading confirmed (b4448 b6425 b2763/b9551 b664/b4486 no row); a neutralizer shot is a power loss
  (b5977 b5312); "tore into the Watchdogs" with nothing continuing = defeated (b8954); "killed" by a named doer with
  a later return stays killed + awakened (clinical-death ruling, b9585); a seal the victim leaves in the same scene
  is sealed only (b7537).
- Partners whose context differs (A8 refinement b3375 vs b9059; b7563 vs b7573): leave the window without the
  context as is and log the pair in recon/exceptions.txt (Add.3).
- Rank names in events vs the fact-gate form (b8054 Emperor Prime/Lieutenant Madrox, b9603 Captain Glory, b9984
  King Arrkam, b8927 Dr. Steve): ONE NAME PER PERSON - when the window itself uses the bare name for that person
  ("Prime", "Glory", "Arrkam", "Steve"), rename the event rows to the bare form (`r Old=>New`); no new RANK entry.
- Torture/de-aging of a captive written as `fought` (b68, and b39/b79 if not already fixed by T1_01): TORT ruling.
- A seal that holds the victim while the sealer flees (b12790 Vulture seals Spider-Man in the truck, leaves his loot):
  `sealed` (+ `defeated` only if the seal ends a stated fight between them); the sealer's flight is `escaped` only if
  the text says he fled from the victim; the lost loot gives no outcome row.
- Agents' NEW owner-type questions (2026-11-06 round): leave the window unchanged, list it under "For the owner" in
  your notes; the coordinator decides and records it here (Addendum 5).

## Addendum 5 (2026-11-06, Claude, decisions on the E1-E5 round's questions; owner delegated)
- TWO CONTROLLERS, ONE ROW (revises Add.3 b12405). The fix tool keeps one fact per subject|relation|object|modality,
  so a second `controlled` row that differs only in asserted_by cannot be stored. One controlled row per act;
  asserted_by = the controller whose stated power does the controlling (b12405: Lorelei's enchantment); the partner's
  part is his own fact (`Grant Ward|other_verb|taken`, already present). b12405 stays as it is.
- A creature, robot or minions a named master sends against targets ("unleashed his Punisher robot upon them",
  "symbiotes controlled by Venom"): A63 - the master keeps the `fought`/`defeated` row (b6609, b4277/b6962). The
  controlled modality is for a NAMED person acting under control.
- Possession of an unnamed body (Wanda in her unnamed Earth-838 self, b4657): no named host to credit, so the
  possessor's plain events stay.
- One blow to a captive (b5187 pistol-whip for a wrong name) is neither fought nor tortured: `X|other_verb|hit`
  (M_02). Torture needs cruelty meant to make the victim suffer (repeated beating, tormenting).
- Symbiote possession with the host later freeing himself (b2834/b6813 Peter as Spider-Carnage fights MJ): the host's
  act is `controlled|stated|<symbiote>`; the other side's fight back is her plain event (M_02).
- Brainwasher unnamed, only his own controller named (b2885/b8362 "a scientist controlled by Black Cat"): the
  control of the doer has no named controller -> plain events.
- Same-name host and person (b3610 adult Jean Grey possessed by the Phoenix Force beside young Jean Grey): left as
  is (A18; no clean name for the host).
- "made his escape attempt" with the escape not completed: no `escaped` (keep only what is stated); b2945 left as
  the predecessor wrote it unless the window states the escape succeeded.
- Confirmed as decided by E1-E5: b7573 Eisner|killed|Dracula (stated execution; the later resurrection does not undo
  it - clinical-death ruling); b13047 no row for an absent helper of a stopped group; b3097 "nearly" covers only the
  decapitation; b3349/b4157 implied doer = A8 no row; gold b532 no row for unnamed summoners; b653 a noun is allowed
  as the other_verb object when the quote has no verb for the act; b9774 tortured beside the CAPTURED-ruling
  defeated (Add.3: torture after a fight keeps the fight's outcome); b13659 controlled attacked for an
  "assassination attempt" while enthralled.
- Outside-class errors found by E3 and fixed in M_02: b2996 Logan|killed|Sabretooth on "destroyed his body" ->
  fought + defeated; b3463 WBY -> Nico|wounded|Robert Minoru.
- Still with the owner (needs a fact_gate.RANK change, owner approval): rank names whose bare form the window never
  uses for that person: b8054 Emperor Prime / Lieutenant Madrox (bare "Prime" also names Jamie Prime in the same
  window), b9603 Captain Glory, b9984 King Arrkam, b8927 Dr. Steve. Events keep the full name; facts carry the
  gate-stripped form. Small inconsistency, left until the owner decides on more RANK entries.
