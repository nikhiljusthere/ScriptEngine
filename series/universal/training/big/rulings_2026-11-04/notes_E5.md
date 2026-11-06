# E5 notes (2026-11-06): BRIEF.md Addendum 4 on list_E5.txt

Status: DONE. E5_01.txt submitted (11 windows changed). No E5_02 needed. Gold b532: no change, so no E5G_01.txt.

## Per window
- b4016 ADD4 changed: Night-Night Gun shot knocks out the hostile Peterson, window ends -> - Ward|fought|Peterson, + Ward|defeated|Peterson (no wounded).
- b10667 ADD4 changed: Hunter stuns allies Skye/May with an I.C.E.R. -> both fought rows dropped, f+ Hunter|other_verb|shot (one fact; the other_verb object is the verb, so one row covers both allies).
- b2041 ADD4 changed (big): Norman stabs the held, sin-filled Peter to cure him -> - Norman|fought|Peter, f+ Norman|other_verb|stabbed; Norman|wounded|Peter stays. Kraven's earlier stab of Spider-Man (hostile, meant for Norman) left as is.
- b79 ADD4 no change: T1_01 already did it (tortured + chained as controlled|Mastermind, Mastermind|fought|Phoenix gone; the control is Mastermind|tricked + other_verb corrupting).
- b653 ADD4 changed: - A.I.M.|fought|Michael, f+ A.I.M.|other_verb|hypnosis ("freed from A.I.M.'s hypnosis by Clea"; the quote has the noun only, so I used it). No act of Michael under the hypnosis is stated.
- b1242 ADD4 no change: T1_01 already dropped Puppet Master|fought|Iron Man; no control fact can be quoted beyond "the Puppet Master's commands" (no verb). Avengers|defeated|Puppet Master stays.
- b1453 ADD4 changed: + Morbius|defeated|Vic Slaughter on "ending his rampage with torturing Slaughter and burying him alive"; tortured stays.
- b8155 ADD4 changed: same row as partner b1453 (shared sentence). Third partner b8134 does not hold the sentence: untouched.
- b7573 ADD4 changed: Father Eisner stakes the tied Dracula -> - Eisner|fought|Dracula, - Eisner|defeated|Dracula, + Eisner|killed|Dracula ("drove a stake into his chest. Present at the execution"; the death is stated by "execution" and Marie "resurrecting the vampire", so killed + the existing awakened). Note: Addendum 4 writes the fallback as `Marie Eisner|other_verb|staked`, but the staker in the text is Father Eisner (row name "Eisner"); Marie removes the stake. Marie's defeated/escaped rows (cross charm) stay.
- b7563 ADD4 no change: no capture sentence in this window (Addendum 4: stays). Pair logged: C628 b7563~b7573.
- b6539 ADD4 changed: + Kindred|saved|Spider-Man (Add.3, intercepted attack); no defeated (Spider-Man finishes Osborn); the Kindred stopped fact stays. Was not yet applied.
- b6609 ADD4 changed: + Johnny|defeated|Galactus (Johnny brought the Ultimate Nullifier; Galactus "agreed to spare Earth and left"); no escaped ("left", not fled). Was not yet applied. Partner b6607 does not hold these sentences.
- b8302 ADD4 changed: no puppet control of Dragon Man stated ("unleashing the Dragon Man android upon them") -> ordered: f+ Puppet Master|ordered|Dragon Man, f+ Dragon Man|other_verb|forcing|...|ordered|stated|Puppet Master; Dragon Man's plain fought/defeated rows stay (A64, as b2422 Discord/Lockdown).
- b8054 ADD4 no change: the window never uses a bare name for the dupe: "Emperor Prime"/"the Emperor Prime" only ("Jamie Prime" is the original Madrox, "the Prime Jamie" a title, "This Madrox" the Emperor); "Lieutenant Madrox" never bare. No rename.
- b9603 ADD4 no change: only "Captain Glory" in the text, never "Glory". ("Midas" rows already use the bare form the window uses.)
- b9984 ADD4 no change: only "King Arrkam" (x3), never "Arrkam".
- b8927 ADD4 no change: only "Dr. Steve", never "Steve".
- b68 ADD4 changed: Mojo de-ages the captured X-Men for TV -> - Mojo|fought|X-Men, f+ Mojo|tortured|X-Men; captured and other_verb de-aging stay.
- b39 ADD4 no change: T1_01 already did it (tortured x2, captured kept, no fought from the torture).
- b3375 ADD4 no change: Zodiac|defeated|<5 squad members> already present (B2). Pair logged: C370 b3375~b9059 (A8 refinement).
- b9059 ADD4 no change: the shared sentence has no fight/doer in this window, A8 stands.
- gold b532 ADD2 no change: Makima's control is stated over the two UNNAMED hunters, not over the Mantis Devil, so no `controlled` row for the devil (Add.2: controlled only for stated control of THAT doer by a named controller). The devil acts on its summoners' command = an ordered act, but the summoners are unnamed (crowd, already tagged crowd_end), so neither `X|ordered|Mantis Devil` nor an asserted_by can be written; the devil's plain fought + wounded stay (A64 keeps the doer's rows), Makima|other_verb|control stays.

## Exceptions logged (recon/exceptions.txt, under the lock)
- C370 b3375~b9059 (A8 refinement)
- C628 b7563~b7573 (bound-captive killing only in b7573)

## For the owner
- b7573: Addendum 4 names `Marie Eisner|other_verb|staked` as the fallback, but the window's staker is Father Eisner; I wrote Eisner|killed|Dracula (death stated). Confirm killed (vs. A53 "destroying the vampire") is the intended read.
- Rank names b8054 b9603 b9984 b8927: no rename (the windows never use the bare form), so the event layer (Emperor Prime, Lieutenant Madrox, Captain Glory, King Arrkam, Dr. Steve) still differs from the fact layer (Prime, Glory, Arrkam, Steve) the fact gate produced. b8054 is the risky one: fact "Prime" for the Emperor collides with "Jamie Prime" (the original, who dies in the same window). These need the RANK allow-list, or the fact rows renamed, to reach one name per person.
- gold b532: is an ordered act by a creature whose summoners are unnamed (and themselves controlled by a named Makima) anything more than the plain rows + crowd_end tag? Left unchanged.
- b6609 (not changed, outside Addendum 4): Galactus|fought|<4 FF members> quotes "he unleashed his lethal Punisher robot upon them" -- an item/robot sent on them (A39 item never the doer vs Add.2 ordered creature); left.
- b653: the control fact uses the noun "hypnosis" (the quote has no verb for it); confirm noun objects are acceptable for A116 control facts.

## Counts
- ADD4 big: 21 read / 11 changed (b4016 b10667 b2041 b653 b1453 b8155 b7573 b6539 b6609 b8302 b68) / 10 no change (b79 b1242 b39 b7563 b8054 b9603 b9984 b8927 b3375 b9059).
- ADD2 gold: 1 read / 0 changed (b532).
- Files: E5_01.txt (11 applied). Exceptions: 2.
