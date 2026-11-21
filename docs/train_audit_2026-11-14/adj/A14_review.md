# A14 adjudication: fix and unsure windows

Counts: gold_ok 30, fix 6, unsure 2 (38 windows).

## Fix

### b1301 (Reverse Cursed Technique / Yuta Okkotsu)
- S1: "Up against Kurourushi in the Sendai Colony, Yuta knew he could exorcise the curse by driving positive energy into its body, which will compromise a body made of cursed energy regardless of how powerful that cursed spirit may be."
- S2: "However, using reverse cursed technique is a rare ability and Yuta did not want to reveal it during the fight with other Culling Game players watching his moves.(Chapter 175) He only resorted to using reverse cursed technique when his life was in danger to destroy Kurourushi."
- S3: "He bit the cursed spirit's face and delivered a mouth-to-mouth blast to its brain, completely compromising the integrity of its body.(Chapter 175)"
- Gold: `Yuta|killed|Kurourushi` only.
- Proposed: `+ Yuta|fought|Kurourushi|Up against Kurourushi in the Sendai Colony`.
- Rule: step 5 ("A killing after a stated fight is fought AND killed"; "faced X in battle" is fought); A145 allows fought beside killed when the fight is stated separately. The fight is stated in S1 and S2 ("during the fight"), apart from the killing act in S3.

### b1154 (Rika / Overall Skill Level)
- S3: "Additionally, it created an opening for Rika to counterattack, which served as a diversion for Yuta to redirect Ryu's blast back down on him."
- S4: "Rika was taken out of the fight before Ryu was defeated but the blast was redirected back down on him thanks to her efforts.(Chapter 180, Episode 59)"
- Gold: `Yuta|fought|Ryu`, `Yuta|defeated|Ryu`, `Yuta|defeated|Uro`; nothing for Rika against Ryu (S3 also tagged no_relation).
- Proposed: `+ Rika|fought|Ryu|it created an opening for Rika to counterattack`.
- Rule: A40 / step 5 fought ("any attack MADE"). The counterattack happened: it "served as a diversion", and S4 credits "her efforts" and has her in the fight. The second reader's Uro-Yuta fought is not added (defeated covers it, A145).

### b1646 (Riko Amanai/Synopsis / Gojo's Past Arc)
- S1: "When she arrived at school, Riko attended her classes, spending time with her friends one last time.(Chapter 67, Episode 26) During music class, Gojo suddenly entered the room and dragged her away, as curse users had invaded the school.(Chapter 69, Episode 26) The two then encountered one of the curse users who was capable of cloning himself."
- Gold: fact `Gojo|other_verb|dragged`; no met.
- Proposed: `+ Gojo|met|Riko|Gojo suddenly entered the room and dragged her away` (the dragged fact stays: a different act).
- Rule: met table ("walked in on X", "X arrived where Y was"); Addendum 6: an earlier scene together does not make them companions already together. Riko had gone to class on her own. Her arrival "at school" is a description, so no arrived.

### b1424 (Riko Amanai/Synopsis / Gojo's Past Arc)
- S3: "The next day, the four left Okinawa and arrived at the technical college, where they were ambushed by Toji Fushiguro.(Chapter 70, Episode 27) While Gojo occupied Toji, Riko was quickly brought deeper into the college by Misato and Geto.(Chapter 71, Episode 27) Once the three reached the Tombs of the Star Corridor, Riko and Misato tearfully bid each other farewell."
- Gold: `Toji Fushiguro|fought|Gojo` only; the departed rows already expand "the four" to Gojo, Geto, Riko and Misato.
- Proposed: `+ Toji Fushiguro|fought|Riko`, `+ Toji Fushiguro|fought|Geto` and `+ Toji Fushiguro|fought|Misato`, all with the quote "they were ambushed by Toji Fushiguro".
- Rule: the fought table lists "ambushed"; step 4 says to expand "they" to the named people; Example 10 is the same case ("only for them to be ambushed by Killmonger" gives one fought row per person). The second reader's arrived rows are rejected because "the technical college" is a description.

### b1212 (Satoru Gojo/Synopsis / Gojo's Past Arc)
- S6: "The next day, the four head back to the college but are attacked by Toji Fushiguro when they arrive, with Gojo having a sword stabbed through his chest.(Chapter 70, Episode 27)"
- Gold: `Toji Fushiguro|fought|Gojo` only.
- Proposed: `+ Toji Fushiguro|fought|Riko`, `+ Toji Fushiguro|fought|Geto` and `+ Toji Fushiguro|fought|Misato`, all with the quote "are attacked by Toji Fushiguro".
- Rule: same as b1424. "The four" (Gojo, Riko, Geto, Misato) is the subject of "are attacked"; the stab names only Gojo's wound. "The college" is a description, so no arrived. This window and b1424 tell the same scene, so they should be fixed the same way.

### b1088 (Satoru Gojo/Synopsis / Cursed Child Arc)
- S1 (second part): "Realizing Yuta's potential, Gojo instead brings him back to Tokyo Jujutsu High and convinces the higher-ups to push off his execution and to let Yuta join the college."
- Gold: `Gojo|arrived|Tokyo Jujutsu High` only.
- Proposed: `+ Yuta Okkotsu|arrived|Tokyo Jujutsu High|Gojo instead brings him back to Tokyo Jujutsu High`.
- Rule: the arrived table lists "was taken/brought to"; A138 says the one carried arrives; Example 8 is the same case ("Shaw took Mackenzie to the Lighthouse" gives both arrived).
- Not changed: S4 "...but Rika shows up to defend Yuta." The second reader has `Rika saved Yuta`, but the three only "prepare to attack". Addendum 6 names b1088 as left for a reviewer, so the gold `protected` fact stays.

## Unsure

### b1247 (Reverse Cursed Technique / Yuta Okkotsu)
- S1: "When tasked to execute Yuji Itadori, Yuta was able to avoid permanently killing him by instantaneously healing him with reverse cursed technique the moment his heart stopped."
- Gold: `Yuta|saved|Yuji Itadori`; no awakened.
- Second reader: `Yuji Itadori|awakened` (and a fought row; that one is rejected because it is a staged execution and no attack is stated).
- Why unsure: "his heart stopped" and "avoid permanently killing him" read as a clinical death reversed by Yuta's healing. A106/A147 give `awakened` for a return from death beside `saved`. But the window never says he died or was revived. The supervisor should decide whether the clinical-death ruling reaches "heart stopped".

### b1669 (Satoru Gojo/Synopsis / Culling Game Arc)
- S1: "Due to the efforts of Hana Kurusu, Yuji Itadori and many others Gojo is eventually unsealed and upon his unsealing confronts Kenjaku and attempts to kill him but is prevented from doing so by Sukuna."
- Gold: `Gojo|met|Kenjaku` ("confronts Kenjaku"), `Sukuna|saved|Kenjaku` (rulings 2026-11-04 owner question 5: an intercepted attack, A75), fact `Gojo|other_verb|kill|attempted`.
- Second reader: `Gojo fought Kenjaku`.
- Why unsure: if this is an intercepted attack, as the gold's saved row reads it, step 5 ("An interception is fought (attacker vs target) AND saved") gives `Gojo|fought|Kenjaku`, and A145 then drops the met. But "attempts to kill him but is prevented" does not say an attack was made, and the owner-question ruling addressed only saved/defeated. If the attack counts as made, the change would be `- Gojo|met|Kenjaku` and `+ Gojo|fought|Kenjaku|confronts Kenjaku and attempts to kill him`.
