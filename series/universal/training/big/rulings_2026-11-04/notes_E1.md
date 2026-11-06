# notes_E1 (rulings pass 2026-11-06, BIG set; agent E1)
List: list_E1.txt (66 lines). Predecessor drafts: notes_D1.md, notes_RB3.md, notes_RB1.md (each re-read against the window).

## Per window
### Part 1: Addendum-3 corrections (second edits) -> E1_01
- b12511 ADD3 changed: f- Bakuto|tortured|Joy (shot hostage = wounded, not tortured).
- b12550 ADD3 changed: f- Bakuto|tortured|Joy.
- b12634 ADD3 changed: - Fahey|defeated|Wilson (non-resisting arrest = captured alone).
- b12346 ADD3 changed: - Cottonmouth|fought|Scarfe; f+ Cottonmouth|other_verb|shot ... claimed|reported|Cottonmouth (A113, "informed").
- b12392 ADD3 changed: Jonah's 3 captured + 2 defeated rows go; Victor Stein's abducted/attacked x2/capturing as controlled|stated|Jonah.
- b12405 ADD3 NOT APPLIED (tool limit): big_review_v2.apply_edits dedupes facts on (subject, relation, object, modality),
  so a second controlled row with asserted_by Grant Ward is silently dropped (verified by parsing the fix file). The
  dry run "accepts" it only because the duplicate is removed before the gate. Needs a code change -> For the owner.
- b12319 ADD3 changed: f- Kthara|other_verb|made; f+ Kthara|ordered|Hastings; f+ Hastings|other_verb|stab ordered/Kthara;
  WBY in the same sentence: f- Helstrom|wounded|- -> f+ Hastings|wounded|Helstrom ordered/Kthara.
### Part 2: list_R_B3 rest
- b12790 CAPT changed (Add.4): + Vulture|defeated|Spider-Man (seal ends the stated fight); escaped stays (he fled from Spider-Man).
- b12884 TORT changed: fought -> tortured.
- b12890 TORT changed: fought -> tortured; + Castle|wounded|-.
- b12962 CAPT/TORT/CTRL changed: fought -> tortured; Stark's flying controlled|stated|Johann Fennhoff.
- b12972 STOP changed (Add.4): + Dottie Underwood|defeated|Pike (stated resistance); Pike's traffic-stop fact stays.
- b12982 LISTED no change (predecessor decision: real fight, Underwood overpowers Carter, no captive).
- b12993 LISTED changed: + Hela|defeated|Thor.
- b12999 FW changed: + Thor|wounded|Hela, Valkyrie|wounded|Hela.
- b13009 FW changed: + Valkyrie|wounded|Hela.
--- E1_02 ---
- b13019 FW no change (rings shot at Wenwu, no hit stated). b13039 STOP no change (Wenwu stops a fight, no villain plot).
- b13047 TEAM no change: D1 drafted + S.H.I.E.L.D.|defeated|Holden Radcliffe, rejected on re-read - Radcliffe is on the
  losing side ("The Watchdogs, assisted by Radcliffe ... were stopped"); "were stopped" has the Watchdogs as subject and
  his presence at the stop is not stated; TEAM concerns a partner of the winner.
- b13111 STOP changed: foiled fact -> Sam Wilson|defeated|Sterns.
- b13124 FW changed: + Black Widow|wounded|Sterns (outcome open).
- b13177 FW no change (arrow blocked). b13205 STOP no change (Simmons halts a fight). b13279 STOP no change (music).
- b13243 CAPT changed: + Nico Minoru|defeated|Magistrate (seal ends the fight).
- b13370 CAPT changed: fought -> defeated (one act with the trapping), sealed kept.
- b13371 ESC changed: 10 escaped rows (Proxima Midnight / Corvus Glaive x 5 winners) + Corvus Glaive|wounded|-.
- b13417 CAPT changed: + Ten Rings|defeated|Stark; fought KEPT (D1 draft removed it; "attacked and failed to kill" is its
  own clause before "instead kidnapped him", so the fight is stated separately, A145 does not apply).
- b13509 WBY no change (unnamed Frost Giant). b13559 STOP no change ("stopped by his mansion").
- b13597 TEAM no change ("half the New York City Police Department" is a part of an org, crowd-like; also a document's content).
- b13643 LISTED changed: + Jessica Jones|defeated|Will Simpson; killed Clemons kept (Add.4 factive).
- b13735 STOP no change (statues). b13809 STOP no change (car; saved exists).
- b13737 FW changed: + Sprite|wounded|Sersi.
- b13741 STOP changed (Add.4): stopped fact -> Osiris|defeated|Marc Spector + Osiris|saved|Arthur Harrow.
- b13854 ESC changed (Add.4 crowd): - Conquistadores|arrived|Sky World, - Kahhori|defeated|Conquistadores; t+ crowd_end.
- b13859 CAPT/STOP no change: Kahhori's stop of the prisoners mid-air is of things/people with no villain; Strange's
  capture is a trap she breaks out of and keeps fighting (a pause, no defeated); no Conquistadores row in this window.
- b13863 STOP changed: f- Conquistadores|attacked|Kahhori's village (+ crowd_end tag); "stop Strange once and for all.
  After they succeeded" -> Kahhori|defeated|Doctor Strange + Peggy Carter|defeated|Doctor Strange; stop fact goes.
- b13911 STOP no change (Sif stops ally Volstagg putting on a crown).
- b13969 CAPT no change: no fight with M.O.D.O.K. stated before the capture ("donned a suit to battle against Kang's Empire"
  is a purpose); the later "facing off M.O.D.O.K." has no stated outcome.
### Part 3: list_R_B1 from b3097
- b3097 NEAR changed: decapitating -> actual/denied.
- b3119 CAPT changed: + M-Squad|defeated|Jubilee.
- b3165 STOP no change (stop inside a continuing exchange). b3189 STOP no change (Okoye's stop ends nothing).
- b3201 TEAM changed: + Galactus|defeated|Hunger; Thanos|helped|Galactus reversed -> Galactus|helped|Thanos.

--- E1_03 ---
- b3203 / b7935 WBY changed (partners identical): Cole/Macon/Reese|wounded|- -> Wolverine|wounded|<each>.
- b3212 STOP no change (weapon production, a thing).
- b3219 FW changed: + Drax the Destroyer|wounded|Thanos; LISTED disarm: Thanos|defeated|Doctor Strange kept.
- b3283 / b9523 CTRL changed (partners identical): Amadeus|other_verb|defeat ordered/Nguyen -> controlled|stated|Nguyen
  (implant control stated; controlled wins). Amadeus|fought|Namor is before the implant (own will): no change. STOP:
  the tsunami is a thing: no change. Amadeus|other_verb|destroy left ordered/Nguyen (an order never carried out).
- b3287 FW changed: + Wilder|wounded|Andre; fought KEPT, no defeated (RB1 draft had dropped fought + added defeated;
  abilities note, no subdue/end stated; consistent with RB3_04 b12349 "shot Koko in the head" -> wounded only).
- b3319 NEAR changed: transforming -> actual/denied.
- b3331 FW changed (plain error in the flagged row): - Ultron|fought|Avengers ("several Avengers", A5) + crowd_end tag.
- b3335 / b6102 LISTED A8 no change (Blastaar is a third side; predecessor decision). b10091 PARTNER no change.
- b8312 / b10080 / b10093 CTRL changed (identical): Spider-Man|joined|Frightful Four -> controlled|stated|Frightful Four;
  the capture is the controllers' own act (no change).
- b3338 LISTED species end changed: - Ikaris|fought|Deviant, - Ikaris|defeated|Deviant; + Ikaris other_verb shooting /
  punches; crowd_end tag.
- b3347 STOP no change (gambling operation's chief of police unnamed).
- b3349 / b4157 WBY no change (passive "Forge was wounded"; Serafina only "tracked down" him; predecessor decision);
  b9360 PARTNER no change.

## For the owner
- b12405: Add.3 "one controlled row per controller" cannot be stored: apply_edits (tools/train/big_review_v2.py, dedupe
  key (subject, relation, object, modality)) drops the Grant Ward rows. Window left with the Lorelei rows only. Fix =
  add asserted_by to the dedupe key (code change, not mine to make).

- b13047 (no change, my call): should a STOP of a group's plot also give `defeated` to a named helper of that group
  ("The Watchdogs, assisted by Radcliffe, tried to take the book, but were stopped by S.H.I.E.L.D.")?
- b3097: "nearly decapitating the former and impaling the latter" - I read "nearly" as scoping decapitating only (the
  existing Kasady|wounded|Spider-Man for impaling stays); confirm.
- b3349/b4157: "After being tracked down by one of the Children, Serafina, Forge was wounded" - doer implied, not
  stated; left as Forge|wounded|- (predecessor decision).

## New patterns
- Fix-file tool limit: facts dedupe on (subject, relation, object, modality); rows differing only in asserted_by (two
  controllers, two claimants) cannot be stored (b12405).
- A crowd/indefinite end removed from a flagged row (Conquistadores, "several Avengers", "the Deviant") gets a
  crowd_end tag on the sentence so the drop is recorded (A94).

## Counts
Files submitted: E1_01 (14 windows), E1_02 (14), E1_03 (12) = 40 windows changed. 26 list lines no change
(incl. b12405 not applied: tool limit). Total list lines 66.
By class (read / changed / no change):
- ADD3 7 / 6 / 1 (b12405 blocked)
- CAPT 9 / 7 / 2 (b13859, b13969 no change; b12962 counted here, also TORT/CTRL)
- STOP 18 / 6 / 12 (changed: b12972, b13111, b13741, b13863, b3283/b9523 via CTRL; no change b13039 b13205 b13279
  b13559 b13735 b13809 b13859 b13911 b3165 b3189 b3212 b3347)
- FW 13 / 9 / 4 (no change b13019 b13177; changed incl. b12884/b12890 via TORT, b3331 via A5)
- TORT 1 (b12884) changed; ESC 2 / 2 / 0; TEAM 3 / 1 / 2 (b13047, b13597 no change); WBY 5 / 2 / 3 (b3203 b7935
  changed; b13509 b3349 b4157 no change); NEAR 2 / 2 / 0; LISTED 8 / 5 / 3 (b12982, b3335, b6102 no change);
  PARTNER 4 / 2 / 2 (b8312 b10093 changed via CTRL; b10091 b9360 no change).
