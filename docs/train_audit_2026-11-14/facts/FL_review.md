# FL review -- 2026-11-14 audit of gold facts/coverage

Each entry: the finding, the sentence(s), what the gold has, the proposal, the rule. Fix blocks are in FL_fix.txt.

## b119 -- Foss / Personality -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "His scheme of attempting to kill Griffith was based on the intense and unsettling fear he felt from being in his presence."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Foss|other_verb|kill|His scheme of attempting to kill Griffith|attempted|stated|Foss
```
- Rule: A134/A101: the scheme to kill Griffith is Foss's narrated attempt (named doer, "His" = Foss)

## b185 -- Blue Whale Knights / Golden Age Arc -- unsure

- Finding: sentence s1 has no row and no tag.
  - s1: "The Blue Whale Knights fight the Band of the Falcon at a given point."
- Gold has: no row or tag on the sentence.
- Why unsure: s1 'The Blue Whale Knights fight the Band of the Falcon' is a group-vs-group fight; A2/step 6 forbid a group row because the window names members of both sides (Adon, Samson; Guts, Casca), whose pair rows already exist in s7/s11/s12, and no section C tag fits a named-group line. Needs a ruling: group fact, member fact, or leave.
- Rule: A2 / A57 / step 6 (no group row when members are tied), section C (closed tag set), one fought per pair.

## b235 -- Episode 237 (Manga) / Summary -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "He says that, long ago, he and Flora had a relationship similar to what Guts and Schierke currently have."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Skull Knight|other_verb|had|he and Flora had a relationship similar to what Guts and Schierke currently have|claimed|reported|Skull Knight
```
- Rule: A113/A128: the Skull Knight's account of his past with Flora is his claim; "says" is taken by s4, so the content verb "had"

## b314 -- The Fundamental Virulence (episode) / Summary -- fix

- Finding: name_longer_than_the_window_writes_it -- `Mask De Masculine`
  - s3: "Meanwhile, a grinning Mask flexes his muscles to break free of Kazeshini, but Hisagi exploits his new posture to wrap more chains around him, binding Mask's arms to his side, before Ikkaku stabs Hōzukimaru into Mask's face."
- Gold has (rows changed):
  - event `Hisagi|fought|Mask De Masculine` quote "Hisagi exploits his new posture to wrap more chains around him"
  - event `Ikkaku|fought|Mask De Masculine` quote "Ikkaku stabs Hōzukimaru into Mask's face."
  - fact `Mask De Masculine|other_verb|break` (attempted/stated/Mask De Masculine) quote "flexes his muscles to break free of Kazeshini"
- Proposed:
```
- Hisagi|fought|Mask De Masculine
+ Hisagi|fought|Mask|Hisagi exploits his new posture to wrap more chains around him
- Ikkaku|fought|Mask De Masculine
+ Ikkaku|fought|Mask|Ikkaku stabs Hōzukimaru into Mask's face.
f- Mask De Masculine|other_verb|break
f+ Mask|other_verb|break|flexes his muscles to break free of Kazeshini|attempted|stated|Mask
```
- Rule: A112/A130: the window writes only "Mask"

## b416 -- Marechiyo Ōmaeda / Enhanced Endurance -- fix

- Finding: name_longer_than_the_window_writes_it -- `Marechiyo Ōmaeda`
  - s1: "Even while being skewered by BG9's tendrils, Ōmaeda was able to continue his attempts to attack the Quincy.(Chapter 549) In addition, despite these injuries, he was later able to carry both his captain and sister over a considerable distance.(Chapter 581)"
- Gold has (rows changed):
  - event `Marechiyo Ōmaeda|fought|BG9` quote "Even while being skewered by BG9's tendrils"
  - fact `BG9|wounded|Marechiyo Ōmaeda` (actual/stated/None) quote "Even while being skewered by BG9's tendrils"
  - fact `Marechiyo Ōmaeda|other_verb|carry` (actual/stated/None) quote "he was later able to carry both his captain and sister over a considerable distance"
- Proposed:
```
- Marechiyo Ōmaeda|fought|BG9
+ Ōmaeda|fought|BG9|Even while being skewered by BG9's tendrils
f- BG9|wounded|Marechiyo Ōmaeda
f+ BG9|wounded|Ōmaeda|Even while being skewered by BG9's tendrils
f- Marechiyo Ōmaeda|other_verb|carry
f+ Ōmaeda|other_verb|carry|he was later able to carry both his captain and sister over a considerable distance
```
- Rule: A130: the window writes only "Ōmaeda"; the longer page title is not its name

## b487 -- Ichigo Kurosaki & Kūgo Ginjō vs. Shūkurō Tsukishima / Prelude -- fix

- Finding: name_longer_than_the_window_writes_it -- `Kūgo Ginjō`
  - s1: "As black Reiatsu pours out from the opened fish tank, surprising Ginjō and Sado, Tsukishima states it is interesting."
  - s5: "Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)"
- Finding: name_longer_than_the_window_writes_it -- `Shūkurō Tsukishima`
  - s1: "As black Reiatsu pours out from the opened fish tank, surprising Ginjō and Sado, Tsukishima states it is interesting."
  - s5: "Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)"
- Gold has (rows changed):
  - event `Ichigo|met|Kūgo Ginjō` quote "Ichigo emerges."
  - event `Ichigo|met|Shūkurō Tsukishima` quote "Ichigo emerges."
  - fact `Shūkurō Tsukishima|other_verb|states` (actual/stated/None) quote "Tsukishima states it is interesting."
  - fact `Shūkurō Tsukishima|other_verb|Telling` (actual/stated/None) quote "Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)"
  - fact `Shūkurō Tsukishima|other_verb|expressing` (actual/stated/None) quote "Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)"
  - fact `Shūkurō Tsukishima|other_verb|tells` (actual/stated/None) quote "Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)"
- Proposed:
```
- Ichigo|met|Kūgo Ginjō
+ Ichigo|met|Ginjō|Ichigo emerges.
- Ichigo|met|Shūkurō Tsukishima
+ Ichigo|met|Tsukishima|Ichigo emerges.
f- Shūkurō Tsukishima|other_verb|states
f+ Tsukishima|other_verb|states|Tsukishima states it is interesting.
f- Shūkurō Tsukishima|other_verb|Telling
f+ Tsukishima|other_verb|Telling|Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)
f- Shūkurō Tsukishima|other_verb|expressing
f+ Tsukishima|other_verb|expressing|Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)
f- Shūkurō Tsukishima|other_verb|tells
f+ Tsukishima|other_verb|tells|Telling Ichigo Riruka's Dollhouse forcibly ejects its contents if the container is destroyed, Tsukishima, expressing his surprise at Ichigo mastering Fullbring to such a degree, tells Ginjō he should have told him sooner.(Chapter 445)
```
- Rule: A112/A130: the window writes only "Ginjō" and "Tsukishima"

## b556 -- Nobana Higashiyama / Personality -- fix

- Finding: name_longer_than_the_window_writes_it -- `Nobana Higashiyama`
  - s1: "Much like his older sister, Nobana is perpetually anxious but, unlike her, even more so and he hasn't had any moments of competency or bravery so far."
  - s4: "Nobana's mind is fragile, as he goes insane after a few days of being trapped in the aquarium, licking the glass senselessly."
  - s5: "Later, Nobana joins the Chainsaw Man Church and becomes fully devoted to their cause, easily believing the lies which the Church tells its followers showing he's very susceptible to manipulation and conspiracy theories."
- Gold has (rows changed):
  - fact `Nobana Higashiyama|joined|Devil Hunter Club` (actual/stated/None) quote "like joining the Devil Hunter Club"
  - fact `Nobana Higashiyama|joined|Chainsaw Man Church` (actual/stated/None) quote "Later, Nobana joins the Chainsaw Man Church"
  - fact `Nobana Higashiyama|other_verb|believing` (actual/stated/None) quote "easily believing the lies which the Church tells its followers"
  - fact `Nobana Higashiyama|other_verb|encourages` (actual/stated/None) quote "encourages students to have children and marry each other"
- Proposed:
```
f- Nobana Higashiyama|joined|Devil Hunter Club
f+ Nobana|joined|Devil Hunter Club|like joining the Devil Hunter Club
f- Nobana Higashiyama|joined|Chainsaw Man Church
f+ Nobana|joined|Chainsaw Man Church|Later, Nobana joins the Chainsaw Man Church
f- Nobana Higashiyama|other_verb|believing
f+ Nobana|other_verb|believing|easily believing the lies which the Church tells its followers
f- Nobana Higashiyama|other_verb|encourages
f+ Nobana|other_verb|encourages|encourages students to have children and marry each other
```
- Rule: A130: the window writes only "Nobana"; the longer page title is not its name

## b626 -- Episode 3 / Summary -- fix

- Finding: sentence s4 has no row and no tag.
  - s4: "As they fight, he sees other humans and tells them to run."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Denji|other_verb|sees|he sees other humans and tells them to run
```
- Rule: A101/B.3: Denji's narrated act; "tells" is taken by s1, so "sees"

## b683 -- Chapter 2 / Summary -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "As soon as he reaches her and the situation is dealt with, he falls in her arms as he has lost so much blood from the chainsaws."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Denji|other_verb|falls|he falls in her arms as he has lost so much blood from the chainsaws
```
- Rule: A101/B.3: Denji's narrated act (the meeting is already the met row)

## b731 -- Chapter 115 / Summary -- fix

- Finding: sentence s4 has no row and no tag.
  - s4: "Haruka becomes confused, asking what she's talking about, to which she reminds him about the starter on his chest."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Haruka|other_verb|asking|Haruka becomes confused, asking what she's talking about
```
- Rule: A101/B.3: Haruka's narrated question (Asa's "reminds" is taken by s3)

## b1033 -- Episode 36 / Plot Details -- fix

- Finding: sentence s6 has no row and no tag.
  - s6: "He avoids her attacks while his thrown sword chases after Akari by itself."
- Finding: name_longer_than_the_window_writes_it -- `Akari Nitta`
  - s1: "While on their way, Nobara and Akari are confronted by the curse user Haruta Shigemo on Shoto Bunkamura Street."
  - s3: "Nobara believes that Shigemo is the one who attacked Ijichi and she asks Nitta to pretend to hide in the subway entrance while escaping through another."
  - s5: "She deflects it with her hammer and charges at him while Akari runs."
  - s6: "He avoids her attacks while his thrown sword chases after Akari by itself."
  - s7: "Eventually, the sword catches up to Akari and slashes her ankles, causing her to fall."
  - s8: "Through this attack, Shigemo learns that Akari is not hiding and runs after her, with Nobara giving chase."
- Finding: name_longer_than_the_window_writes_it -- `Nobara Kugisaki`
  - s1: "While on their way, Nobara and Akari are confronted by the curse user Haruta Shigemo on Shoto Bunkamura Street."
  - s3: "Nobara believes that Shigemo is the one who attacked Ijichi and she asks Nitta to pretend to hide in the subway entrance while escaping through another."
  - s4: "Shigemo interrupts their whispering by throwing his sword at Nobara."
  - s8: "Through this attack, Shigemo learns that Akari is not hiding and runs after her, with Nobara giving chase."
- Gold has (rows changed):
  - event `Haruta Shigemo|fought|Nobara Kugisaki` quote "Shigemo interrupts their whispering by throwing his sword at Nobara"
  - fact `Nobara Kugisaki|ordered|Akari Nitta` (actual/stated/None) quote "she asks Nitta to pretend to hide in the subway entrance"
  - fact `Nobara Kugisaki|suspected|-` (actual/stated/None) quote "Nobara believes that Shigemo is the one who attacked Ijichi"
  - fact `Akari Nitta|other_verb|pretend` (ordered/stated/Nobara Kugisaki) quote "she asks Nitta to pretend to hide in the subway entrance while escaping through another."
  - fact `Nobara Kugisaki|other_verb|deflects` (actual/stated/None) quote "She deflects it with her hammer and charges at him while Akari runs."
  - fact `Nobara Kugisaki|located_at|Shoto Bunkamura Street` (actual/stated/None) quote "Nobara and Akari are confronted by the curse user Haruta Shigemo on Shoto Bunkamura Street"
- Proposed:
```
f+ Haruta Shigemo|other_verb|avoids|He avoids her attacks while his thrown sword chases after Akari by itself.
- Haruta Shigemo|fought|Nobara Kugisaki
+ Haruta Shigemo|fought|Nobara|Shigemo interrupts their whispering by throwing his sword at Nobara
f- Nobara Kugisaki|ordered|Akari Nitta
f+ Nobara|ordered|Akari Nitta|she asks Nitta to pretend to hide in the subway entrance
f- Nobara Kugisaki|suspected|-
f+ Nobara|suspected|-|Nobara believes that Shigemo is the one who attacked Ijichi
f- Akari Nitta|other_verb|pretend
f+ Akari Nitta|other_verb|pretend|she asks Nitta to pretend to hide in the subway entrance while escaping through another.|ordered|stated|Nobara
f- Nobara Kugisaki|other_verb|deflects
f+ Nobara|other_verb|deflects|She deflects it with her hammer and charges at him while Akari runs.
f- Nobara Kugisaki|located_at|Shoto Bunkamura Street
f+ Nobara|located_at|Shoto Bunkamura Street|Nobara and Akari are confronted by the curse user Haruta Shigemo on Shoto Bunkamura Street
```
- Rule: A101 + A112: Shigemo's dodge has a named doer; the window writes only "Nobara"
- Note: `Akari Nitta` is kept. The window writes both 'Akari' (s1, s5-s8) and 'Nitta' (s3) for her, so the row name joins the window's own words and supplies nothing from outside; if the supervisor reads A130 strictly, rename to 'Akari' (her most frequent form) in the 3 rows that carry it.

## b1046 -- Shibuya Incident Arc / Pandemonium -- fix

- Finding: name_not_in_window -- `Pseudo-Geto`
  - (no sentence of the window contains the name)
- Gold has (rows changed):
  - event `Nanako|met|Pseudo-Geto` quote "From the crowd of civilians, Nanako and Mimiko demand their master's body back"
  - event `Mimiko|met|Pseudo-Geto` quote "From the crowd of civilians, Nanako and Mimiko demand their master's body back"
  - fact `Pseudo-Geto|other_verb|refuses` (actual/stated/None) quote "to which the imposter refuses"
- Proposed:
```
- Nanako|met|Pseudo-Geto
- Mimiko|met|Pseudo-Geto
f- Pseudo-Geto|other_verb|refuses
```
- Rule: B.7/A112: "Pseudo-Geto" is not in the window ("the imposter" only); the sentence stays covered by the demand rows
- After the removal s5 stays covered by Nanako|other_verb|demand and Mimiko|other_verb|demand.

## b1048 -- Playful Cloud / Maki Zenin & Megumi Fushiguro -- fix

- Finding: name_longer_than_the_window_writes_it -- `Maki Zenin`
  - s1: "Maki and Megumi Fushiguro were able to trade cursed tools mid-battle to confuse Hanami, leaving them open to an attack from Playful Cloud."
  - s4: "Although she was eventually overpowered, Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries.(Chapter 47, Episode 19)"
- Gold has (rows changed):
  - event `Hanami|defeated|Maki Zenin` quote "Although she was eventually overpowered, Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries."
  - event `Maki Zenin|fought|Hanami` quote "Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries."
  - fact `Maki Zenin|other_verb|trade` (actual/stated/None) quote "trade cursed tools"
  - fact `Maki Zenin|wounded|-` (actual/stated/None) quote "despite her injuries"
- Proposed:
```
- Hanami|defeated|Maki Zenin
+ Hanami|defeated|Maki|Although she was eventually overpowered, Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries.
- Maki Zenin|fought|Hanami
+ Maki|fought|Hanami|Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries.
f- Maki Zenin|other_verb|trade
f+ Maki|other_verb|trade|trade cursed tools
f- Maki Zenin|wounded|-
f+ Maki|wounded|-|despite her injuries
```
- Rule: A112/A130: the window writes only "Maki"

## b1058 -- Chapter 0-1 / Plot Details -- fix

- Finding: name_longer_than_the_window_writes_it -- `Maki Zenin`
  - s2: "As soon as Yuta introduces himself, Maki stabs her spear into the blackboard next to Yuta's face, threatening the cursed boy."
  - s3: "Maki points out that Jujutsu High is place to study and learn how to defeat curses, not somewhere for someone who's cursed."
- Finding: name_not_in_window -- `Panda`
  - (no sentence of the window contains the name)
- Finding: name_not_in_window -- `Toge Inumaki`
  - (no sentence of the window contains the name)
- Gold has (rows changed):
  - event `Yuta|met|Maki Zenin` quote "Yuta enters the room, and the three students are shocked to see a powerful curse following him"
  - event `Yuta|met|Toge Inumaki` quote "Yuta enters the room, and the three students are shocked to see a powerful curse following him"
  - event `Yuta|met|Panda` quote "Yuta enters the room, and the three students are shocked to see a powerful curse following him"
  - fact `Maki Zenin|other_verb|threatening` (actual/stated/None) quote "threatening the cursed boy"
  - fact `Maki Zenin|other_verb|stabs` (actual/stated/None) quote "Maki stabs her spear into the blackboard next to Yuta's face"
  - fact `Maki Zenin|other_verb|points` (actual/stated/None) quote "Maki points out that Jujutsu High is place to study and learn how to defeat curses"
- Proposed:
```
- Yuta|met|Maki Zenin
+ Yuta|met|Maki|Yuta enters the room, and the three students are shocked to see a powerful curse following him
- Yuta|met|Toge Inumaki
- Yuta|met|Panda
f- Maki Zenin|other_verb|threatening
f+ Maki|other_verb|threatening|threatening the cursed boy
f- Maki Zenin|other_verb|stabs
f+ Maki|other_verb|stabs|Maki stabs her spear into the blackboard next to Yuta's face
f- Maki Zenin|other_verb|points
f+ Maki|other_verb|points|Maki points out that Jujutsu High is place to study and learn how to defeat curses
```
- Rule: B.7/A112/A130: the window writes only "Maki"; Toge Inumaki and Panda are named only outside the window ("the three students")
- Yuta|met|Maki stays: Maki is named in the window and is in the room (s2).

## b1059 -- Gojo's Past Arc / Escorting the Star Plasma Vessel -- fix

- Finding: name_longer_than_the_window_writes_it -- `Misato Kuroi`
  - s1: "While Satoru and Suguru are occupied, Kuroi gets kidnapped by the Time Vessel Association and taken to Okinawa."
- Finding: name_longer_than_the_window_writes_it -- `Riko Amanai`
  - s2: "Riko, Suguru, and Satoru make it to Naha and rescue her."
- Gold has (rows changed):
  - event `Time Vessel Association|captured|Misato Kuroi` quote "Kuroi gets kidnapped by the Time Vessel Association and taken to Okinawa"
  - event `Riko Amanai|arrived|Naha` quote "Riko, Suguru, and Satoru make it to Naha"
  - event `Riko Amanai|saved|Misato Kuroi` quote "Riko, Suguru, and Satoru make it to Naha and rescue her"
  - event `Suguru|saved|Misato Kuroi` quote "Riko, Suguru, and Satoru make it to Naha and rescue her"
  - event `Satoru|saved|Misato Kuroi` quote "Riko, Suguru, and Satoru make it to Naha and rescue her"
  - event `Riko Amanai|arrived|Tokyo Jujutsu High` quote "When they finally return to Tokyo Jujutsu High and enter the barrier"
- Proposed:
```
- Time Vessel Association|captured|Misato Kuroi
+ Time Vessel Association|captured|Kuroi|Kuroi gets kidnapped by the Time Vessel Association and taken to Okinawa
- Riko Amanai|arrived|Naha
+ Riko|arrived|Naha|Riko, Suguru, and Satoru make it to Naha
- Riko Amanai|saved|Misato Kuroi
+ Riko|saved|Kuroi|Riko, Suguru, and Satoru make it to Naha and rescue her
- Suguru|saved|Misato Kuroi
+ Suguru|saved|Kuroi|Riko, Suguru, and Satoru make it to Naha and rescue her
- Satoru|saved|Misato Kuroi
+ Satoru|saved|Kuroi|Riko, Suguru, and Satoru make it to Naha and rescue her
- Riko Amanai|arrived|Tokyo Jujutsu High
+ Riko|arrived|Tokyo Jujutsu High|When they finally return to Tokyo Jujutsu High and enter the barrier
```
- Rule: A112/A130: the window writes only "Kuroi" and "Riko"

## b1085 -- Maki Zenin/Synopsis / Culling Game Arc -- fix

- Finding: name_longer_than_the_window_writes_it -- `Ogi Zenin`
  - s1: "Ogi drags both of his beaten up daughters to the training room full of cursed spirits and throws them in."
- Gold has (rows changed):
  - event `Ogi Zenin|captured|Maki` quote "Ogi drags both of his beaten up daughters to the training room full of cursed spirits and throws them in"
  - event `Ogi Zenin|captured|Mai` quote "Ogi drags both of his beaten up daughters to the training room full of cursed spirits and throws them in"
  - fact `Ogi Zenin|other_verb|mocks` (actual/stated/None) quote "He mocks Heavenly Restriction saying that sorcerers train daily to reinforce their bodies with curse energy and that Maki's strength is nothing special."
  - fact `Ogi Zenin|other_verb|walks` (actual/stated/None) quote "He walks out of the room, calling him a stain on his life."
  - fact `Ogi Zenin|other_verb|calling` (actual/stated/None) quote "He walks out of the room, calling him a stain on his life."
  - fact `Ogi Zenin|other_verb|saying` (actual/stated/None) quote "He mocks Heavenly Restriction saying that sorcerers train daily to reinforce their bodies with curse energy and that Maki's strength is nothing special."
- Proposed:
```
- Ogi Zenin|captured|Maki
+ Ogi|captured|Maki|Ogi drags both of his beaten up daughters to the training room full of cursed spirits and throws them in
- Ogi Zenin|captured|Mai
+ Ogi|captured|Mai|Ogi drags both of his beaten up daughters to the training room full of cursed spirits and throws them in
f- Ogi Zenin|other_verb|mocks
f+ Ogi|other_verb|mocks|He mocks Heavenly Restriction saying that sorcerers train daily to reinforce their bodies with curse energy and that Maki's strength is nothing special.
f- Ogi Zenin|other_verb|walks
f+ Ogi|other_verb|walks|He walks out of the room, calling him a stain on his life.
f- Ogi Zenin|other_verb|calling
f+ Ogi|other_verb|calling|He walks out of the room, calling him a stain on his life.
f- Ogi Zenin|other_verb|saying
f+ Ogi|other_verb|saying|He mocks Heavenly Restriction saying that sorcerers train daily to reinforce their bodies with curse energy and that Maki's strength is nothing special.
```
- Rule: A112/A130: the window writes only "Ogi"

## b1149 -- Sukuna/Synopsis / Culling Game Arc -- fix

- Finding: sentence s4 has no row and no tag.
  - s4: "Yuji throws a feint that gets Sukuna off balance, and then Maki grabs Yuji and swings him into Sukuna."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Yuji|other_verb|throws|Yuji throws a feint that gets Sukuna off balance
f+ Maki|other_verb|swings|Maki grabs Yuji and swings him into Sukuna
```
- Rule: A101/B.3: the feint and the swing are named acts inside the Yuji/Maki-Sukuna fight already recorded (one fought per pair)

## b1168 -- Kokichi Muta vs. Mahito / Battle -- fix

- Finding: sentence s1 has no row and no tag.
  - s1: "However once again Mahito is caught off guard by Mechamaru's speed."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Kokichi|other_verb|caught|Mahito is caught off guard by Mechamaru's speed
```
- Rule: A101/A120: Mechamaru is Kokichi's piloted body (the window's own reading of the hook); the act is Kokichi's

## b1188 -- Episode 24 / Plot Details -- fix

- Finding: sentence s1 has no row and no tag.
  - s1: "The two then arrive underneath the bridge and find Megumi unconscious, which worries them."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Yuji|other_verb|find|The two then arrive underneath the bridge and find Megumi unconscious
f+ Nobara|other_verb|find|The two then arrive underneath the bridge and find Megumi unconscious
```
- Rule: A101/B.3: "the two" = Yuji and Nobara; the meeting is already the met row after he wakes, the finding is their act

## b1207 -- Megumi Fushiguro / Overview -- fix

- Finding: sentence s1 has no row and no tag.
  - s1: "Megumi fought on equal ground with Noritoshi Kamo during the Goodwill Event."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Megumi|other_verb|fought|Megumi fought on equal ground with Noritoshi Kamo during the Goodwill Event.
```
- Rule: C/step 5: the Megumi-Kamo fight is already recorded (one fought per pair); the repeat gets a fact
- The repeat-of-a-pair rule (one fought per pair; the repeat gets a fact) is applied as the audit brief states it; the verb 'fought' is the sentence's only verb.

## b1211 -- Sukuna/Synopsis / Shinjuku Showdown Arc -- fix

- Finding: sentence s11 has no row and no tag.
  - s11: "He punches Sukuna one more time with his enhanced arm, surprising him."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Yuji Itadori|other_verb|punches|He punches Sukuna one more time with his enhanced arm, surprising him.
```
- Rule: A101/B.3: "He" = Yuji (s10); the punch repeats the recorded Yuji-Sukuna fight

## b1224 -- Panda vs. Hajime Kashimo / Battle -- fix

- Finding: sentence s3 has no row and no tag.
  - s3: "The impact of Kashimo's punch sends cursed energy through Panda's back and electrifies his entire body, stunning him for a moment."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Kashimo|other_verb|electrifies|The impact of Kashimo's punch sends cursed energy through Panda's back and electrifies his entire body
```
- Rule: A120/A101: the punch's owner is the doer of what it does

## b1232 -- Chapter 259 / Plot Details -- fix

- Finding: name_longer_than_the_window_writes_it -- `Aoi Todo`
  - s1: "Some time before December 24, Mei Mei secretly met with Todo to discuss a plan to save the sorcerers trapped within Sukuna's domain."
  - s2: "Todo proposed using his cursed technique to swap the sorcerers inside the domain with Mei Mei's crows stationed outside."
  - s3: "Mei Mei agreed but questioned whether Todo can extend the range of his technique and target multiple individuals simultaneously without his left hand."
  - s4: "Though uncertain, Todo believed he could still sense the rhythm of Boogie Woogie."
- Gold has (rows changed):
  - event `Mei Mei|met|Aoi Todo` quote "Mei Mei secretly met with Todo"
  - fact `Aoi Todo|other_verb|proposed` (actual/stated/None) quote "Todo proposed using his cursed technique to swap the sorcerers inside the domain with Mei Mei's crows stationed outside"
  - fact `Aoi Todo|other_verb|asked` (actual/stated/None) quote "He asked Mei Mei not to inform Yuji of the plan"
  - fact `Aoi Todo|other_verb|requested` (actual/stated/None) quote "He also requested that his plan to adjust his cursed technique with Yuta Okkotsu remain secret until the operation against Kenjaku began"
  - fact `Aoi Todo|other_verb|swap` (planned/stated/Aoi Todo) quote "Todo proposed using his cursed technique to swap the sorcerers inside the domain with Mei Mei's crows stationed outside."
  - fact `Aoi Todo|suspected|-` (actual/stated/None) quote "Though uncertain, Todo believed he could still sense the rhythm of Boogie Woogie."
  - fact `Mei Mei|other_verb|inform` (ordered/denied/Aoi Todo) quote "He asked Mei Mei not to inform Yuji of the plan"
- Proposed:
```
- Mei Mei|met|Aoi Todo
+ Mei Mei|met|Todo|Mei Mei secretly met with Todo
f- Aoi Todo|other_verb|proposed
f+ Todo|other_verb|proposed|Todo proposed using his cursed technique to swap the sorcerers inside the domain with Mei Mei's crows stationed outside
f- Aoi Todo|other_verb|asked
f+ Todo|other_verb|asked|He asked Mei Mei not to inform Yuji of the plan
f- Aoi Todo|other_verb|requested
f+ Todo|other_verb|requested|He also requested that his plan to adjust his cursed technique with Yuta Okkotsu remain secret until the operation against Kenjaku began
f- Aoi Todo|other_verb|swap
f+ Todo|other_verb|swap|Todo proposed using his cursed technique to swap the sorcerers inside the domain with Mei Mei's crows stationed outside.|planned|stated|Todo
f- Aoi Todo|suspected|-
f+ Todo|suspected|-|Though uncertain, Todo believed he could still sense the rhythm of Boogie Woogie.
f- Mei Mei|other_verb|inform
f+ Mei Mei|other_verb|inform|He asked Mei Mei not to inform Yuji of the plan|ordered|denied|Todo
```
- Rule: A112/A130: the window writes only "Todo"

## b1337 -- Sukuna/Synopsis / Shinjuku Showdown Arc -- fix

- Finding: sentence s3 has no row and no tag.
  - s3: "He barrages Kashimo's mid-section with punches from his lower arms, slams him into the ground using the grip on his arms, and then throws him away."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Sukuna|other_verb|barrages|He barrages Kashimo's mid-section with punches from his lower arms
f+ Sukuna|other_verb|slams|slams him into the ground using the grip on his arms
f+ Sukuna|other_verb|throws|and then throws him away.
```
- Rule: A101/B.3: "He" = Sukuna (the King of Curses, s2); the blows repeat the recorded Sukuna-Kashimo fight

## b1347 -- Satoru Gojo/Synopsis / Fearsome Womb Arc -- fix

- Finding: sentence s5 has no row and no tag.
  - s5: "Jogo then continues his assault, and Gojo remains unharmed by any of his attempts."
- Finding: sentence s7 has no row and no tag.
  - s7: "Gojo then attacks Jogo, by kicking him that sends Jogo flying."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Jogo|other_verb|continues|Jogo then continues his assault, and Gojo remains unharmed by any of his attempts.
f+ Gojo|other_verb|kicking|Gojo then attacks Jogo, by kicking him that sends Jogo flying.
```
- Rule: A101/B.3: both acts repeat the recorded Jogo-Gojo fight (one fought per pair)

## b1360 -- Megumi Fushiguro, Toge Inumaki & Noritoshi Kamo vs. Hanami / Prologue -- fix

- Finding: name_longer_than_the_window_writes_it -- `Noritoshi Kamo`
  - s2: "As Megumi begins the call and suggests to Noritoshi that they must retreat, Hanami blitzes behind them and breaks the phone with a wooden projectile.(Chapter 45)"
- Gold has (rows changed):
  - event `Hanami|fought|Noritoshi Kamo` quote "As Megumi begins the call and suggests to Noritoshi that they must retreat, Hanami blitzes behind them and breaks the phone with a wooden projectile."
- Proposed:
```
- Hanami|fought|Noritoshi Kamo
+ Hanami|fought|Noritoshi|As Megumi begins the call and suggests to Noritoshi that they must retreat, Hanami blitzes behind them and breaks the phone with a wooden projectile.
```
- Rule: A112/A130: the window writes only "Noritoshi"

## b1370 -- Vs. Mahito Arc / "I'm Gonna Kill You!" -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "While they're focused on the bait, Mahito escapes back underground through the sewers."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Mahito|other_verb|escapes|Mahito escapes back underground through the sewers.
```
- Rule: A101/B.3: the escape from Yuji is already the escaped row; the repeat is Mahito's fact

## b1382 -- Yuji Itadori vs. Haba & Hanyu / Battle -- fix

- Finding: sentence s1 has no row and no tag.
  - s1: "Yuji takes advantage of this momentary distraction and launches a rock directly into Hanyu's lower abdomen."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Yuji|other_verb|launches|Yuji takes advantage of this momentary distraction and launches a rock directly into Hanyu's lower abdomen.
```
- Rule: A101/B.3: the rock is the defeating act (A145, no separate fought); Yuji's launch gets its fact

## b1408 -- Maki Zenin, Toge Inumaki & Panda vs. Suguru Geto / Prologue -- fix

- Finding: name_longer_than_the_window_writes_it -- `Suguru Geto`
  - s2: "This makes him wise to Geto's scheme and Satoru teleports Toge and Panda back to the school."
  - s3: "They're transported above the curtain, which Panda breaks and then takes the shortest route to Geto."
  - s4: "While standing over Maki's bloodied and defeated body, Geto senses a hole was made in the barrier and expects his adversaries to take five minutes to reach him."
  - s5: "While Geto tries to decide whether to deal with the newcomers or not, Panda suddenly breaks through one of the walls and attacls the curse user."
  - s6: "Getoquickly realizes that Panda took the shortest route to him by breaking through all the walls in a straight line from the point of entry.(Chapter 0-3)"
- Gold has (rows changed):
  - event `Suguru Geto|defeated|Maki` quote "While standing over Maki's bloodied and defeated body"
  - event `Panda|fought|Suguru Geto` quote "Panda suddenly breaks through one of the walls and attacls the curse user"
  - fact `Suguru Geto|discovered|-` (actual/stated/None) quote "Geto senses a hole was made in the barrier"
  - fact `Suguru Geto|suspected|-` (actual/stated/None) quote "and expects his adversaries to take five minutes to reach him."
  - fact `Suguru Geto|other_verb|decide` (attempted/stated/Suguru Geto) quote "While Geto tries to decide whether to deal with the newcomers or not"
  - fact `Suguru Geto|learned|-` (actual/stated/None) quote "Getoquickly realizes that Panda took the shortest route to him"
- Proposed:
```
- Suguru Geto|defeated|Maki
+ Geto|defeated|Maki|While standing over Maki's bloodied and defeated body
- Panda|fought|Suguru Geto
+ Panda|fought|Geto|Panda suddenly breaks through one of the walls and attacls the curse user
f- Suguru Geto|discovered|-
f+ Geto|discovered|-|Geto senses a hole was made in the barrier
f- Suguru Geto|suspected|-
f+ Geto|suspected|-|and expects his adversaries to take five minutes to reach him.
f- Suguru Geto|other_verb|decide
f+ Geto|other_verb|decide|While Geto tries to decide whether to deal with the newcomers or not|attempted|stated|Geto
f- Suguru Geto|learned|-
f+ Geto|learned|-|Getoquickly realizes that Panda took the shortest route to him
```
- Rule: A112/A130: the window writes only "Geto"

## b1446 -- Kento Nanami/Synopsis / Shibuya Incident Arc -- fix

- Finding: sentence s6 has no row and no tag.
  - s6: "Haruta says that he doesn't know, which Nanami hits him again."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Nanami|other_verb|hits|Haruta says that he doesn't know, which Nanami hits him again.
```
- Rule: A101/B.3: the hit repeats the recorded Nanami-Haruta fight; Haruta's "says" is taken by s4

## b1514 -- Sukuna/Synopsis / Shibuya Incident Arc -- fix

- Finding: sentence s6 has no row and no tag.
  - s6: "Mahoraga attacks again but Sukuna dodges and wounds Mahoraga."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Sukuna|other_verb|dodges|Mahoraga attacks again but Sukuna dodges and wounds Mahoraga.
```
- Rule: A101/B.3: the attack and the wound repeat recorded rows; Sukuna's dodge is new

## b1526 -- Kento Nanami/Synopsis / Shibuya Incident Arc -- fix

- Finding: sentence s6 has no row and no tag.
  - s6: "The two have a small chat and Nanami wonders what he is trying to do."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Nanami|other_verb|have|The two have a small chat and Nanami wonders what he is trying to do.
f+ Mahito|other_verb|have|The two have a small chat and Nanami wonders what he is trying to do.
```
- Rule: A101/B.3: "the two" = Nanami and Mahito (met already recorded); Nanami's "wonders" is taken by s4, so the chat's verb "have"
- 'chat' is a noun; 'have' is the only literal verb of the chat clause (Nanami|other_verb|wonders is already used by s4).

## b1571 -- Yuji Itadori vs. Haba & Hanyu / Battle -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "She hits him with enough velocity to drive him straight through two high-rise buildings."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Hanyu|other_verb|hits|She hits him with enough velocity to drive him straight through two high-rise buildings.
```
- Rule: A101/B.3: "She" = Hanyu, "him" = Yuji; the hit repeats the recorded Hanyu-Yuji fight

## b1584 -- Episode 24 / Plot Details -- fix

- Finding: sentence s5 has no row and no tag.
  - s5: "The pain from the deactivated technique has sharpened her focus, and before Wing King can reach her, Yuji lands in front of Eso and prepares to punch him."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Yuji|other_verb|lands|Yuji lands in front of Eso and prepares to punch him.
f+ Yuji|other_verb|punch|Yuji lands in front of Eso and prepares to punch him.|planned|stated|Yuji
```
- Rule: A101/B.4: Yuji's landing is his act; the punch he prepares is planned

## b1759 -- Shibuya Incident Arc / Entering the Station -- fix

- Finding: sentence s7 has no row and no tag.
  - s7: "Naobito also attacks Dagon with the two, but Dagon manages to defend himself."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Naobito|other_verb|attacks|Naobito also attacks Dagon with the two, but Dagon manages to defend himself.
```
- Rule: A101/B.3: the attack repeats the recorded Naobito-Dagon fight

## b2944 -- Kawamatsu / Onimaru -- fix

- Finding: sentence s7 has no row and no tag.
  - s7: "After the raid on Onigashima, Kawamatsu reunited with Onimaru."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Kawamatsu|other_verb|reunited|After the raid on Onigashima, Kawamatsu reunited with Onimaru.
```
- Rule: step 5/A101: one met per pair (s1 already has Kawamatsu|met|Onimaru); the reunion is a fact

## b3002 -- Raizo / Wano Country Arc -- fix

- Finding: sentence s1 has no row and no tag.
  - s1: "The Scabbards' happiness was short-lived, however, as Kanjuro came out to confront them with several samurai accompanying him."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Kanjuro|other_verb|came|Kanjuro came out to confront them with several samurai accompanying him.
```
- Rule: A101/A145: the confrontation becomes Kikunojo's fight (no met, per the window's note); Kanjuro's act gets its verb, as s7's "Kaidou stepped in to confront"

## b3191 -- Awakened Garou vs. S-Class Heroes (Webcomic) / Battle -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "Garou immediately flash steps, catching up as Genos crashes into a rock."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Garou|other_verb|steps|Garou immediately flash steps, catching up as Genos crashes into a rock.
```
- Rule: A101/B.3: Garou's flash step is his act inside the recorded Garou-Genos fight

## b3310 -- Garou vs. Metal Bat / Battle -- fix

- Finding: sentence s2 has no row and no tag.
  - s2: "He wonders if this is the hero's willpower showing."
- Gold has: no row or tag on the sentence.
- Proposed:
```
f+ Garou|other_verb|wonders|He wonders if this is the hero's willpower showing.
```
- Rule: A101/B.3: "He" = Garou; Garou|suspected|- is taken by s1, so the quote's own verb
