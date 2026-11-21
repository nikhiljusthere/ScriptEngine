# A18 adjudication: fix and unsure windows

## FIX

### b3042, Heart Pirates / Dressrosa Arc
- s1: "Law was defeated and captured, and when Luffy came to rescue him, he attempted to end the alliance, but Luffy refused."
- Gold: `Luffy|saved|Law` ("Luffy came to rescue him"), and no met.
- Proposed: `+ Luffy|met|Law|when Luffy came to rescue him`.
- Rule: A34 (met each person reached + saved). Addendum 6 cites A34 for a rescue that follows an arrival. The s2 confrontation with Doflamingo becomes the fight, so it gets no met (A145).

### b3040, Jesus Burgess / Personality
- s2: "This is further shown when he tried to kill Sabo just to get his hands on the Mera Mera no Mi when he interfered in his attempts to kill Luffy, believing that it was his right to have the fruit."
- Gold: the fact `Sabo|other_verb|interfered` (actual), and no saved.
- Proposed: `+ Sabo|saved|Luffy|when he interfered in his attempts to kill Luffy` and `f- Sabo|other_verb|interfered`.
- Rule: A75, and Addendum 3 (intercepting a killing attempt on a named person = saved). An event is never also a fact (section B, A89). Burgess carries on (he tries to kill Sabo), so there is no defeated row (Addendum 4 STOP).

### b2835, Monkey D. Luffy/Relationships / Crocodile
- s4: "Luffy reluctantly allowed him to be released and worked with him to escape and to try and rescue his brother, Ace."
- Gold: `Luffy|escaped|Impel Down` and `Crocodile|escaped|Impel Down` (quote "worked with him to escape"). The rescue in the same clause is already an attempted fact.
- Proposed: remove both escaped rows. Add `Luffy|other_verb|escape` and `Crocodile|other_verb|escape`, planned|stated, each asserted by himself.
- Rule: step 3 (a purpose or goal is no row) and A19 (the purpose clause is a planned fact). The window never says the escape happened; only page_text_before does. The second reader also omitted the escape.

### b2854, Sun Pirates / Whole Cake Island Arc
- s1: "Two days later, Jinbe then decided to stage a rebellion against Big Mom by entering the Whole Cake Chateau and attacking Charlotte Opera in order to free the imprisoned Luffy and Nami."
- s2: "Jinbe and Nami then ran through the Whole Cake Chateau, taking out the enemies in their way, before Chopper and Carrot pulled them into the Mirro-World, an alternate dimension inside the mirrors."
- Gold: `Jinbe|fought|Charlotte Opera` from the same "by ... attacking" clause, so the gold treats that clause as actual. Gold has no arrived rows.
- Proposed: `+ Jinbe|arrived|Whole Cake Chateau`, `+ Jinbe|arrived|Mirro-World` and `+ Nami|arrived|Mirro-World`.
- Rule: the step-5 arrived table ("entered", "was taken/brought to" a proper-named place) and A78. s2 confirms Jinbe was inside the Chateau.

### b2888, Usopp/History/Non-Canon / Strong World
- s1: "Xiao reappears and gives them the Dial Nami left them."
- s3: "They then play the message, and after hearing only the first bit of it, Luffy is angered to the point that he will not listen to the rest (the rest of the crew does, however)."
- Gold: no events. Xiao's giving is a handed fact.
- Proposed: `+ Xiao|met|Luffy|Xiao reappears and gives them the Dial`.
- Rule: Addendum 6 ("shows up" where a named person is gets a met) and the met table ("X arrived where Y was"), with B.7 pronoun resolution. Luffy is one of "them": he hears the message on the Dial. Nami's mother is unnamed, so she gets no row.

### b2995, Vegapunk/Edison / Egghead Arc
- s7: "Edison later rejoined the rest of the surviving satellites, Vegapunk, and the Straw Hats after they had captured the traitor York, though his prior injuries had not been repaired."
- s9: "Edison was later horrified when Kizaru suddenly showed up in the Control Room and got more surprised when he saw a giant Luffy grabbing Kizaru."
- Gold: `Straw Hats|captured|York`, `Kizaru|arrived|Control Room` and `Luffy|fought|Kizaru`. It has no Vegapunk capture and no Kizaru-Edison met.
- Proposed: `+ Vegapunk|captured|York` and `+ Kizaru|met|Edison`.
- Rule: A57/A2. "they" covers the named Vegapunk, so the named member tied to the act takes a row. For Kizaru, the met table ("X arrived where Y was") and A45 (met those who see him) apply: Edison sees him. A145 excludes only Luffy, whom Kizaru fights. Addendum 6 listed b2995 as an enemy appearance "left for a reviewer". The Kizaru row is the less certain of the two.

### b2873, Water 7 / Blue Station
- s1: "The Blue Station is where the Sea Train stops in Water 7."
- s2: "Sanji snuck aboard here, and this is where the CP9 boarded the train with Nico Robin and Franky."
- Gold: `arrived Blue Station` for Sanji, CP9, Nico Robin and Franky.
- Proposed: remove the four arrived rows and add a `located_at Blue Station` fact for each of the four.
- Rule: A151 (located_at the place; arrived only when the passage says X went or came there), A109, and the arrived table's NO column ("being in a place"). Boarding a train at the station does not say they reached it.

### b3251, Angel ☆ Style / Known Techniques
- s2 (excerpt): "For instance, after locating Child Emperor who was trapped in a small space under rubble and about to die due to the lack of oxygen, Puri-Puri Prisoner used Angel ☆ Crawl to save him."
- Gold: `Puri-Puri Prisoner|saved|Child Emperor` and the fact `Puri-Puri Prisoner|discovered|-` ("after locating Child Emperor").
- Proposed: `+ Puri-Puri Prisoner|met|Child Emperor|after locating Child Emperor` and `f- Puri-Puri Prisoner|discovered|-`.
- Rule: A34 (met + saved for the one reached) and A132 (met for the finder). The met table also lists "found X" with contact. An event is never also a fact (section B).

## UNSURE

### b2878, Joy Boy
- s4: "When Luffy awakened the fruit 12 years later, Zunesha proclaimed that Joy Boy had returned."
- Gold: the fact `Monkey D. Luffy|other_verb|awakened`. The reviewer ruled that awakening a fruit is no awakened.
- Why unsure: the step-5 awakened YES column ("gained a new power or form for the FIRST time") and A126 fit literally. But the gold treats fruit awakening like a transformation into a form (the settled transformed_into practice). This needs a supervisor's ruling.

### b2920, Lily / Later Events
- s2: "After Bellamy managed to bring this back to Doflamingo, he regained Doflamingo's trust and forfeited his captaincy to join the Donquixote Pirates."
- Gold: the fact `Bellamy|other_verb|bring`, and no met.
- Why unsure: bringing the pillar back to Doflamingo may be "came to see X" (met). The window does not say Bellamy came in person, and Bellamy is Doflamingo's subordinate. ("a Sky Island" is correctly no arrived, A10.)

### b3002, Raizo / Wano Country Arc
- s1: "The Scabbards' happiness was short-lived, however, as Kanjuro came out to confront them with several samurai accompanying him."
- s2: "Kikunojo clashed with Kanjuro and managed to defeat him before Kin'emon and Denjiro arrived, and Raizo wept over his fallen former comrade."
- Gold: the facts `Kin'emon|other_verb|arrived` and `Denjiro|other_verb|arrived`, and no met.
- Why unsure: Addendum 6 and "X arrived where Y was" suggest that Kin'emon and Denjiro each met Kikunojo and Raizo, replacing the two arrived facts. But s1 has Kanjuro confronting "the Scabbards" as one group, so the window does not make clear that they had parted. The rest of the window is consistent with A145 and A2.

### b2985, Summit War of Marineford / New Allies Arrive
- s2: "About one-and-a-half hours after the battle's start, Sentomaru brought an army of Pacifista units as their master strategy to eliminate the pirates."
- s4 names "Marineford" ("an encircling formation around Marineford").
- Gold: `Sentomaru|arrived|Marineford` (quote "Sentomaru brought an army of Pacifista units").
- Why unsure: A109/A150 ask for the named place reached to be stated. s2 has no place; the place comes only from s4 and the battle setting. It may be right as an arrival at the battle site, or it may be a located fact.
