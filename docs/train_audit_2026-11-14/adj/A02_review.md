# A02 adjudication: fix and unsure windows

Counts: 20 gold_ok, 8 fix, 3 unsure (31 windows).

## Fix

### b166 — Berserk: Millennium Falcon Arc - Flowers of Oblivion Chapter / Story
- s1: "But Guts still insists that the Mandragora's heart as Eriza takes refuge in the village's church, following after her through an underground passage where she assumes Mandragoran form to defend Mandragoran Tree: revealed to be spawned from Niko's body."
- s2: "Though Guts manages to cut out the tree's heart, Eriza refuses to part with the only thing she has left of Niko and flees with the heart."
- Gold: `Guts|defeated|Mandragoran Tree`, plus the fact `Eriza|took|Mandragora's heart` on "flees with the heart". It has no escape row, although the reviewer's note says "Eriza flees with it".
- Proposed: `+ Eriza|escaped|Guts` (quote from s2).
- Rule: the escaped table lists "fled" as YES, and its object is the pursuer the window names: Guts, who was "following after her" (A50). The `took` fact records the heart, not the escape, so nothing is removed.

### b99 — Episode 116 (Manga) / Summary
- s3: "He calls back toward the Holy Iron Chain Knights, telling them that he's stopped Guts' attack; from Zepek and the Holy Iron Chain Knights' perspective, Guts was about to kill two small innocent girls, not the monster that Rosine is."
- Gold: `Zepek|fought|Guts` on "he's stopped Guts' attack" and `Guts|fought|Rosine`. It has no saved row.
- Proposed: `+ Zepek|saved|Rosine` (quote from s3, which names Zepek, the stop and Rosine).
- Rule: A75 says an intercepted attack is fought (attacker) AND saved (the one protected). Addendum 3 says intercepting a killing blow on a named person is `saved`. The gold already accepts the stop as fact, since it wrote the fought row from that clause.

### b248 — Millennium Falcon Arc / The Harlot Princess
- s5: "This attracts more of the trolls who surround them with only the Farnese's silver dagger keeping the monsters from giving them an agonizing death."
- s6: "Luckily, Guts arrives in time and stays behind to cover the group as the captive women and children escape to Enoch Village."
- Gold: `Guts|met|Farnese` and `Guts|met|Casca`, plus the facts `Guts|protected|Farnese` and `Guts|protected|Casca` ("cover protects both").
- Proposed: `+ Guts|saved|Farnese` and `+ Guts|saved|Casca` (quote "Guts arrives in time and stays behind to cover the group"). Remove the two `protected` facts.
- Rule: A34 says an arrival that rescues gives met with each person reached plus saved. The saved table lists "protected from harm" as YES. Section B says an event is never also a fact, so the protected twins go.

### b105 — Mozgus' Disciples / Story
- s6: "Then, they are turned into pseudo-apostles by the Egg of the Perfect World."
- s11: "Once the Crow grabs Guts' head, the other disciples grab him so that the Angel Face may kill him with the wheel, only for Guts to use momentum and attack them."
- s13: "Despite attacking Guts with catcher and feathers, Guts slices the Crow's throat, who collapses in praying position."
- Gold:
  - Five facts `X|transformed_into|pseudo-apostle` (Bubblehead, Imp, Angel Face, Crow, Twins). The note says "being turned into pseudo-apostles is no revival".
  - `Guts|defeated|Crow`, with no fought row for the Crow.
- Proposed:
  - `+ X|awakened|-` for each of the five, removing the five `transformed_into` twins.
  - `+ Crow|fought|Guts` (quote "Despite attacking Guts with catcher and feathers").
- Rule:
  - The awakened table lists "gained a new power or form for the FIRST time" as YES, and A126 says the first new form is `awakened`. The reviewer only ruled out a revival.
  - Step 5 verb rules and A145 add fought beside the outcome when the fight is stated separately. Here the Crow's own attack is a separate clause.
- Supervisor check: the gold practice may intend a `transformed_into` object beside awakened (A126 says "a described form is a legal object"). If so, keep the facts and apply only the `+` lines.

### b169 — Pseudo-Apostle / Ganishka's Spawn
- s1: "After transcending apostlehood as a "reincarnation of a reincarnation" by gathering more evil power from the Abyss and assuming a divine state, Ganishka crushes most of his Kushan soldiers under his feet."
- Gold: `Ganishka|transformed_into|divine state` (fact). It has no event.
- Proposed: `+ Ganishka|awakened|-` (quote "assuming a divine state"). Remove the transformed_into twin.
- Rule: the awakened table (first new form) and A126. The second reader's `killed Kushan` is a crowd, so no row.
- Supervisor check: the same A126 question as b105.

### b69 — Pseudo-Apostle / Zondark
- s1: "The Count transforms Zondark into a pseudo-apostle by forcing the general to ingest a slug-like "daemon" (not to be confused with a daimon) so that he can seek his revenge on Guts while under the influence of the apostle."
- Gold: `Zondark|transformed_into|pseudo-apostle` (fact). It has no event.
- Proposed: `+ Zondark|awakened|-` (quote "The Count transforms Zondark into a pseudo-apostle"). Remove the transformed_into twin.
- Rule: the awakened table (first new form) and A126. The Count's part stays as his `other_verb forcing` fact.
- Supervisor check: the same A126 question as b105.

### b83 — Schierke / Fantasia Arc
- s1: "When the group reaches Elfhelm, Schierke's experience with magic helps the party navigate the many barriers in their way and to combat the beings that Molda and her group send their way."
- Gold: no event. The whole sentence is tagged `crowd_end`.
- Proposed: `+ Schierke|arrived|Elfhelm` (quote "When the group reaches Elfhelm").
- Rule: A57 gives the row to a named member the window ties to the act, and the arrived table accepts a proper-named place reached. Schierke is helping the party navigate Elfhelm, so she is in the group that reached it.
- Not changed: the `crowd_end` tag stays, as instructed. The supervisor may want to drop it now that the sentence carries an event. The second reader's `met Kukka` is a friendship with no stated meeting, so no row.

### b447 — Bambietta Basterbine / The Thousand-Year Blood War arc
- s1: "As Shinji is wounded by the explosion, Bambietta explains that if everything around her is reversed, she simply has to explode everything around her."
- Gold: no row between Bambietta and Shinji. The fact `Shinji|wounded|-` is there, and the note says "an explosion-only wounding names no doer".
- Proposed: `+ Bambietta|fought|Shinji` (quote is the whole of s1).
- Rule: A120 says the owner of the power is the doer. The same sentence names Bambietta as the one who explodes everything around her, so this is not A39 (an item with an unnamed user).
- Left alone:
  - The `Shinji|wounded|-` fact. The WBY form `Bambietta|wounded|Shinji` would follow the same reasoning, but fact edits were out of scope.
  - The second reader's `Komamura awakened` (a reveal of his appearance, not a first new form stated) and `Bambietta fought Komamura` (no target stated). Neither is added.

## Unsure

### b185 — Blue Whale Knights / Golden Age Arc
- s4: "As the sun sets, the Falcon members are surrounded by a mercenary troop led by Adon himself."
- s10: "Despite having been degraded, Adon commands his knights -after having seen their numbers reduced in the previous battle against the Band of the Falcon- within Doldrey against Casca's platoon, which had successfully infiltrated the fortress."
- Gold: s4 is tagged `crowd_end` ("descriptive groups"). There is no arrived row for Casca.
- Why unsure:
  - In s4, "the Falcon members" are by meaning Guts and Casca, the two mercenaries from s2-s3. That would give Adon met Guts and Adon met Casca. But the troop's encounter turns into the fight (A145), and A63 might instead make Adon the fighter. The text does not settle which.
  - In s10, Casca's platoon (A63 makes Casca the end) "infiltrated the fortress", which the same sentence names as Doldrey. But the arrived clause itself uses a description.
- The other second-reader rows are wrong by the catalog: the group fight (A2/A57) and "some Band of the Falcon members" rescuing Guts (indefinite, A52).

### b97 — Enoch Village / Story
- s1: "Arriving at Enoch Village, the party is met by the villagers and priest, who express doubt in their ability to alleviate the troll problem."
- Gold: `Guts|arrived|Enoch Village` and `Casca|arrived|Enoch Village`. The rest of the sentence is tagged `crowd_end` ("the priest and the villagers are unnamed").
- Why unsure: step 6 makes a definite description of one specific individual an end ("the driver", "the old man"; A20). That would give Guts met priest and Casca met priest. But A112 ("an unnamed relative stays a tag") and the reviewer's practice give an unnamed person no row. An owner ruling on definite descriptions decides this.

### b66 — Sonia / Millennium Falcon Arc
- s2: "As Griffith stabs the Kushan leader in the eye after he questioned him, she looks on with shock."
- Gold: tagged `crowd_end`, with the note '"the Kushan leader" is unnamed (no end)'.
- Why unsure: this is the same definite-description question as b97. Under step 6 it would be `Griffith|fought|Kushan leader`.
- The other second-reader row is wrong: Sonia freeing her hands from a rope names no captor and no place, so it is no `escaped` (A117).
