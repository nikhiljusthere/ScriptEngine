# A08 adjudication: fix and unsure windows

## Fix

### b802 Shenron / Super Hero Saga
- S1: "With few options left to defend the Earth from a new android threat, Piccolo flies to the Lookout to ask Dende if he can unlock his potential similar to how the Grand Elder Guru once did for Gohan and Krillin."
- Gold: `Piccolo|met|Dende` only.
- Proposed: `+ Piccolo|arrived|Lookout`. The table's arrived YES column includes "flew to" a proper-named place. "the Lookout" is a proper name in the same way as "the Lighthouse" in example 8. The gold's own met with Dende shows he got there (A109). The power unlock is still not an awakening.
- Rule: step 5 arrived; A109.

### b837 Unavoidable? The Ferocity of a Stealth Attack! / Summary
- S7: "Gohan however opts to fire a series of Ki Blasts to create a cloud of dust, thus revealing the vaguely lizard-like outline of their opponent, Gamisalas."
- Gold: `Gohan|fought|Gamisalas` on this clause.
- Proposed: `- Gohan|fought|Gamisalas`. The blasts were fired to raise dust. The window states no attack on Gamisalas, and an attack on an object only is not fought. `Gohan|revealed|-` still covers the sentence.
- Rule: step 5 fought (an attack MADE on someone); A42.

### b957 Yajirobe / Frieza Saga
- S1: "Yajirobe is next seen with the group going to the West City hospital, Wukong Hospital."
- S2: "He is not kept at the hospital very long as his injuries are only minor."
- S3: "He later delivers a new crop of Senzu Beans to Goku in the hospital, so that Goku can instantly heal from his injuries and go to Namek."
- Gold: no events; `Yajirobe|gave|Goku` fact.
- Proposed: `+ Yajirobe|met|Goku`. Yajirobe left the hospital and later came back to Goku in person, which is a visit. Addendum 6 says an earlier scene together does not make them "already together". The gave fact is a different claim and stays. No arrived at Wukong Hospital: "seen ... going to" is heading toward the place (A109).
- Rule: met table YES (a visit, "came to see X"); Addendum 6.

### b1060 Atsuya Kusakabe/Synopsis / Shinjuku Showdown Arc
- S1: "Sometime following Sukuna's defeat and death, Kusakabe made a full recovery from his injuries and accompanied his students among fellow surviving sorcerers to "save Yuta" from Maki's wrath.(Chapter 268) While Maki was in the middle of scolding Yuta, Megumi and Yuji felt the need to apologize, though Kusakabe and Maki told them its not necessary."
- Gold: only `Rika|saved|Yuta`; Kusakabe's coming is the fact `other_verb accompanied`.
- Proposed: `+ Kusakabe|met|Yuta` and `+ Kusakabe|met|Maki`. He comes to where Maki is scolding Yuta, and the same sentence then has him with them, speaking alongside Maki. No met with Megumi or Yuji, because the window does not say whether they came with him. The accompanied fact is about his students, so it stays.
- Rule: met table ("X arrived where Y was", "joining people not already with them"); Addendum 6.

### b1600 Atsuya Kusakabe/Synopsis / Shinjuku Showdown Arc
- S2 (part): "Kusakabe used Simple Domain to protect Higuruma from Sukuna's slashes, vowing he would protect him with his life as his cursed technique would be the easiest way to kill Sukuna."
- Gold: `Kusakabe|saved|Higuruma`, with no fought row for the blocked slashes.
- Proposed: `+ Sukuna|fought|Higuruma`. Step 5 says "An interception is fought (attacker vs target) AND saved", and fought covers any attack made, even if blocked. Supervisor note: A75 can also be read as the interceptor fighting the attacker (`Kusakabe|fought|Sukuna`). I did not add that row because the reviewer's lint note treats Kusakabe's attack on Sukuna as only attempted.
- Rule: step 5 verb rules; A75.

### b1130 Chapter 107 / Plot Details
- S1: "Frustrated, Nanami understands they are dealing damage but it feels like this curse had boundless health."
- S2: "Naobito is impressed two grade 1 jujutsu sorcerers aren't enough to exorcise the cursed spirit."
- S3: "Maki laments being saved by Naobito, humiliated by the fact she would have died if he hadn't stopped Dagon earlier."
- Gold: `Naobito|saved|Maki`, `Naobito|defeated|Dagon` (note: "stopping Dagon is defeated").
- Proposed: `- Naobito|defeated|Dagon` and `f+ Naobito|other_verb|stopped|he hadn't stopped Dagon earlier`. The stop happened inside a battle that is still going on in this window (S1-S2), and Dagon's part did not end. The STOP class keeps such a stop as a fact. Add.4 makes a stop `defeated` only when it ends the attacker's part. The saved row stays.
- Rule: rulings brief STOP class ("inside an ongoing exchange"); Add.4; table defeated NO ("while the fight continues").

### b1330 Chapter 112 / Plot Details
- S2: "Suddenly, Mimiko's head is severed in a very violent fashion."
- Gold: `Sukuna|killed|Mimiko`.
- Proposed: `- Sukuna|killed|Mimiko` and `t+ no_doer|` (the sentence). It is a passive with no "by", and no doer appears in the sentence. Sukuna is only implied by the surrounding sentences. Example 9 ("Thor was chained down" gets no row) and the no_doer tag definition cover this case. Nanako's killing (S6, Sukuna named) stays.
- Rule: A110; step 4 (never supply a doer); example 9.

### b1311 Chapter 120 / Plot Details
- S1: "Sukuna returns to the area in front of Shibuya 109 after dropping off Megumi at the Shibuya Tollgate to be medically treated."
- Gold: `Sukuna|arrived|Shibuya 109` and `Sukuna|arrived|Shibuya Tollgate`.
- Proposed: `+ Megumi|arrived|Shibuya Tollgate`, because the one carried arrives as well.
- Rule: A138.

### b1315 Chapter 134 / Plot Details
- S1: "Suddenly, Choso also arrives on the battlefield, surprising Yuji."
- Gold: `Choso|met|Geto` (S2); S1 only as the fact `Choso|other_verb|arrives`.
- Proposed: `+ Choso|met|Yuji` and `f- Choso|other_verb|arrives`. Choso arrives where Yuji is. An event is never also a fact, so the arrives fact goes, as with the shows fact in Addendum 6.
- Rule: met table ("X arrived where Y was"); Addendum 6; section B.

### b1782 Chapter 134 / Summary
- S1: "Pseudo-Geto continues his conversation with Yuji about all the techniques he's acquired."
- S3: "As more people gather for the final clash of the Shibuya Incident, Choso appears and unveils a shocking revelation about the man controlling Suguru Geto's body."
- Gold: `Pseudo-Geto|met|Yuji` (note: "the conversation is in person (met)"), `Choso|met|Pseudo-Geto`.
- Proposed: `- Pseudo-Geto|met|Yuji` plus `f+ Pseudo-Geto|other_verb|continues|` (S1), and `+ Choso|met|Yuji`. "continues" is talking inside a meeting already under way, which the met table lists under NO. A91 only routes in-person talk away from `contacted`. Choso appears where both of them are, so he meets each of them.
- Rule: met table NO; A91; Addendum 6.

## Unsure

### b804 Super Saiyan C-type / Usage and Power
- S4: "Broly in this state was also shown to be strong enough to elbow Paragus in the face hard enough to gouge the latter's eye out."
- Gold: capability tag. This may be a depicted occurrence (A114/A122 would give `Broly|fought|Paragus` + wounded), but it is worded as ability ("strong enough to"). S1 ("is powerful enough to defeat ... is able to outmatch") is ability wording, so the capability tag is fine there.

### b992 Yamcha/Biography / Emperor Pilaf Saga
- S2: "There, he has to intervene and help Goku after Bulma is turned into a carrot by Monster Carrot, leader of the Rabbit Mob."
- S3: "He orders Puar to turn into a bird and rescue the hostage carrot-Bulma while he takes out Monster Carrot's two henchmen."
- Gold: `Monster Carrot|other_verb|turned` and `Bulma|transformed_into|carrot`; the reviewer ruled "a transformation is no capture". The table may count turning someone into a carrot as "a power used ON someone" (`Monster Carrot|fought|Bulma`, the second reader's row), and "the hostage" may be a capture (A82). The window names no captor, so I did not add either.

### b1705 Angel / Shinjuku Showdown Arc
- S1: "Hana was later healed by Yuta Okkotsu and Shoko Ieiri after being saved earlier by Rin Amai and possibly Takaba."
- S2 (part): "The Angel notes that without their help they would have died, ..."
- Gold: `healed` facts for Yuta Okkotsu and Shoko Ieiri (reviewer: "healing is no rescue"). Table saved YES includes "healed ... someone who would otherwise die", and S2 states she would have died. But "their" may refer only to the rescuers (Rin Amai, Takaba). If the saved rows are added, the two `healed` facts go.

### b1517 Blood Meteorite / Usage
- S2: "During the raid against Sukuna, Choso used Blood Meteorite to coagulate a large volume of blood into a dome shield around him and Yuji, protecting them from the explosion caused by Sukuna's Divine Flame."
- Gold: `Choso|saved|Yuji Itadori`, with no fought row for Sukuna. Under A75 / step 5 interception, `Sukuna|fought|Yuji Itadori` (and Choso) may be due. The window does not say the Flame was aimed at them, only that they were shielded from its explosion.

### b1450 Chapter 0-1 / Plot Details
- S1: "Satoru Gojo and the jujutsu sorcerers of Tokyo Jujutsu High learn of the incident and hold Yuta at the school in a room sealed with many talismans."
- Gold: `Satoru Gojo|captured|Yuta` ("held prisoner"). The table's captured NO column sends "a sealed place" to `sealed` (the second reader's choice). Yuta also agrees to stay, so either verb is arguable.

### b1710 Chapter 140 / Plot Details
- S1: "Slowing approaching them, he asks who is with Yuji, and Choso says that Yuta must be Yuji's executioner."
- Gold: only `Naoya|met|Yuta`; S1 is tagged deictic (note: "the approach"). "approached X" is a met, which would give Yuta met Yuji and Choso. But "he" is resolved to Yuta only by meaning, Yuta comes as Yuji's executioner (A145 if the encounter becomes the fight), and the reviewer considered the approach.
