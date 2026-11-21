# A07 adjudication: fix and unsure windows

28 windows: 21 gold_ok, 6 fix, 1 unsure.

## b818 (fix): Frieza Saga / Fight against Frieza
- S2: "Since the first two wishes had already been used to bring Piccolo back to life and then to Namek, Vegeta wants to save the last wish for eternal life for himself."
- Gold: no row for Piccolo. The sentence is covered only by `Vegeta|other_verb|wants`.
- Proposed: `+ Piccolo|awakened|-` ("the first two wishes had already been used to bring Piccolo back to life") and `+ Piccolo|arrived|Namek` ("to bring Piccolo back to life and then to Namek").
- Rule: step 3 counts a reason clause or a recap as having happened. The awakened table includes "came back to life" (A147: the revived one is the subject, and no doer is needed). The arrived table includes "was taken/brought to" a proper-named place. The page text that follows confirms that Piccolo was "just teleported to Namek by a wish".

## b872 (fix): Giru / Personality
- S4: "When they reach planet M-2 Giru \"betrays\" the group."
- Gold: the whole sentence is tagged `no_relation`, because the betrayal is fake.
- Proposed: `+ Giru|arrived|M-2|When they reach planet M-2 Giru`. The tag stays, since it still covers the fake betrayal.
- Rule: the arrived table covers reaching a proper-named place. Step 1 says a descriptive section that narrates one specific occurrence still states an event. Giru is one of "they": he betrays "the group" there. Only Giru is named and tied to the arrival, so the other members get no row.

## b1019 (fix): Glorio (episode) / Summary
- S1: "Meanwhile at Capsule Corporation, a now much smaller Goku and Vegeta fall from the sky, almost hitting Krillin on the way down."
- Gold: from this clause it has `Goku|met|Krillin` and `Vegeta|met|Krillin`, but no arrival.
- Proposed: `+ Goku|arrived|Capsule Corporation` and `+ Vegeta|arrived|Capsule Corporation`, both quoting "Meanwhile at Capsule Corporation, a now much smaller Goku and Vegeta fall from the sky".
- Rule: the arrived table includes "landed in" a proper-named place, and A151 applies because the passage says they came there. The gold already reads the landing as an arrival, since it writes met from it.

## b868 (fix): Hang In There, Kakarot! You Are No. 1! / Summary
- S6: "Vegeta then steps in, but that finds he is no match for Buu."
- S7: "Buu cleans his clock, and just as he's about to deal Vegeta the finishing blow, Goku pushes him out of the way."
- Gold: `Kid Buu|defeated|Vegeta`, quoted as "Vegeta then steps in, but that finds he is no match for Buu. Buu cleans his clock". That quote runs across two sentences.
- Proposed: the row itself is right (A145: one act, so defeated only, and the second reader's extra `fought` is rejected). Re-quote it inside S7: `- Kid Buu|defeated|Vegeta`, then `+ Kid Buu|defeated|Vegeta|Buu cleans his clock, and just as he's about to deal Vegeta the finishing blow`.
- Rule: step 7 and B.1 require a quote inside one sentence ("never stitch two sentences together").
- Note: this block removes and re-adds the same triple. If the fix tool rejects that, the block is only a quote change.

## b850 (fix): Ready to Fuse? / Summary
- S4: "Goku appears in the nick of time and cuts Buu in half with a Destructo Disc."
- Who is present, from the window itself: Mr. Satan (S3: "empties his gun in Buu's direction"), Tien (S7: "Super Buu knocks Tien out with one swift kick") and Gohan (S8: "Goku throws a Potara earring to Gohan").
- Gold: `Goku|fought|Super Buu` and no met. The reviewer note reads "an appearance is no meeting".
- Proposed: `+ Goku|met|Gohan`, `+ Goku|met|Tien` and `+ Goku|met|Mr. Satan`, all quoting "Goku appears in the nick of time". There is no met with Super Buu (A145).
- Rule: Addendum 6 (2026-11-14) says a named character who shows up where named allies are gets a met with each named person there. This follows the b1229 precedent (Nanami: met beside the fought row), and the table entry "X arrived where Y was". Addendum 6 is later than the reviewer note and wins. The second reader's extra `Super Buu|fought|Tien` is rejected (A145).

## b964 (fix): Roasie / Universe Survival Saga
- S3: "Ribrianne reverted into Brianne and was sent to Universe 2's bench, where she immediately broke down into tears over her defeat."
- S4: "Sous and Sanka rushed to Brianne's side to comfort her."
- Gold: `Sous|helped|Brianne` and `Sanka|helped|Brianne` (comforting), and no met.
- Proposed: `+ Sous|met|Brianne` and `+ Sanka|met|Brianne`, both quoting "Sous and Sanka rushed to Brianne's side to comfort her". The helped facts stay, because comforting is a separate claim.
- Rule: the met table includes "approached X" and "X arrived where Y was", and step 8.1 lists walk-ins as a common miss. Brianne has just been sent from the arena to the bench, so they are not "companions already together" (Addendum 6). The second reader's defeated rows for Android 17 and Android 18 are rejected: "bested by the Androids" ties no named member to the act (A57).

## b945 (unsure): Earthling / Power
- S2: "It is said that a single Saiyan infant would be capable of destroying the average human population on its own (in fact, Goku was sent as an infant to Earth for that exact purpose)."
- Gold: only the first clause is tagged `capability`. The parenthetical gets no row.
- Second reader: `Goku|arrived|Earth`.
- Why unsure: "was sent ... to Earth" is narrator fact, and it reads like the table's "taken/brought to" or "transported to", which A138 says the carried one arrives by. But A109 allows no arrived row until the passage says he got there. The gold also does not write "sent to" as arrived elsewhere (b782 "sending him back to Hell"). If the supervisor rules for arrived, the row is `+ Goku|arrived|Earth|Goku was sent as an infant to Earth`.
