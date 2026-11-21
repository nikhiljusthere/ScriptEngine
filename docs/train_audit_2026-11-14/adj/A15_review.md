# A15 adjudication: fix and unsure windows

41 windows: 30 gold_ok, 7 fix, 4 unsure.

## Fixes

### b1159 · Shibuya Incident / 11:14 P.M. - 11:36 P.M. Shibuya Station
- Sentence 4: "By applying his innate technique to Yuji's wounds, Arata dulls the pain and ensures the injuries won't get any worse."
- Gold: `Arata|saved|Yuji` and the fact `Arata|healed|Yuji`, both for this clause.
- Proposed: `- Arata|saved|Yuji`. Keep the healed fact.
- Rule: step 5 `saved` counts healing only for someone who "would otherwise die", and the window states no such danger. A89 / section B: one act is never both an event and a fact. This matches the gold's own reading in b1530 ("first aid is healing, not a rescue").

### b1456 · Shibuya Incident / 11:14 P.M. - 11:36 P.M. Shibuya Station
- Sentence 3: "Haibara's spirit points Nanami to Yuji as he enters the station."
- Sentence 4: "Nanami tells Yuji that he's got it from here and his upper body is destroyed as a result of Idle Transfiguration."
- Gold: no met row. The reviewer note covers only "the station" (no arrived).
- Proposed: `+ Yuji|met|Nanami|Haibara's spirit points Nanami to Yuji as he enters the station`.
- Rule: step 5 met table, "X arrived where Y was", and Add.6. Nanami was already inside the station (page_text_before). Yuji enters, and the two speak in person; Mahito then kills Nanami "right in front of him".

### b1502 · Shibuya Incident Arc / Entering the Station
- Sentence 1: "Suddenly Megumi breaks into the domain by using his domain, and gives Maki Playful Cloud, a special grade cursed tool."
- Sentence 3: "Nanami manages to protect Megumi, while Naobito and Maki continues to attack on Dagon."
- Sentence 4: "While Dagon is busy, Megumi explains to Nanami how he is trying to create an exit to Dagon's Domain."
- Gold: no met rows. The break-in is the fact `Megumi|other_verb|breaks`.
- Proposed: `+ Megumi|met|Maki`, `+ Megumi|met|Nanami` and `+ Megumi|met|Naobito`, all quoting "Suddenly Megumi breaks into the domain by using his domain". No met with Dagon, who then attacks him (A145). The `breaks` fact stays because it records the forced entry with his own domain, not the meeting.
- Rule: met table, "X arrived where Y was", and Add.6 (a met with each named person there). The window places all three inside the domain.

### b1537 · Shibuya Incident Arc / Entering the Station
- Sentence 1: "Suddenly Toji enters through the hole, much to the surprised of everyone.(Chapter 109, Episode 38, Episode 39) Toji easily takes Playful Cloud from Maki and prepares to fight Dagon."
- Sentence 5 (part): "...tries to escapes, but Naobito block him which gives Toji the chance to impale Dagon."
- Sentence 7: "Toji quickly gabs Megumi and takes him to another location."
- Gold: no met rows, plus the fact `Toji|other_verb|enters`. The reviewer note: "the entrance".
- Proposed: `+ Toji|met|Maki`, `+ Toji|met|Naobito` and `+ Toji|met|Megumi`, all quoting the entrance sentence. Also `f- Toji|other_verb|enters`, because the met now records the same arrival (section B, Add.6 "the met replaces an other_verb shows fact"). No met with Dagon (A145).
- Rule: met table, "X arrived where Y was". Nanami is not named in the window, so he gets no row.
- Check: the supervisor may want to drop `Toji|met|Naobito` if presence alone, with no exchange between the two, is not enough.

### b1442 · Shibuya Incident Arc / Entering the Station
- Sentence 6: "As Smallpox Deity attacks Mei Mei, Mei Mei uses her Bird Strike technique to exorcise Smallpox Deity."
- Sentence 1, for context: "...the Smallpox Deity keeps on trying to kill Mei Mei with its sure-kill technique but Mei Mei easily breaks out of it."
- Gold: `Mei Mei|killed|Smallpox Deity`, but no fought row for this pair.
- Proposed: `+ Smallpox Deity|fought|Mei Mei|As Smallpox Deity attacks Mei Mei`.
- Rule: step 5 verb rules, "a killing after a stated fight is fought AND killed". A145 allows fought "when the fight is stated separately", and here the attack is the deity's own clause. The tried-kill fact for sentence 1 stays. The "Geto imposter" crowd_end tag is the gold's settled practice and is left alone.

### b1056 · Sukuna / Physical Prowess
- Sentence 3 (part): "He even punched Megumi so hard, the raindrops in that area dispersed."
- Sentence 4 (part): "With 16 of his fingers, Sukuna punched Jogo through numerous skyscrapers with sufficient force to blow enormous holes through their sides..."
- Sentence 5: "Upon taking over Megumi's body, he was able to easily pierce through Yuji's gut and send him flying across the city with a single punch, temporarily incapacitating the sorcerer."
- Gold: the facts `Sukuna|attacked|Megumi`, `Sukuna|attacked|Jogo` and `Sukuna|attacked|Yuji`. The only event is `Sukuna|fought|Gojo`.
- Proposed: `+ Sukuna|fought|Megumi`, `+ Sukuna|fought|Jogo` and `+ Sukuna|fought|Yuji` (quotes in the fix file). Remove the three `attacked` facts. The wounded facts stay, and the outcome ruling's "no defeated" stays.
- Rule: step 1 and A114/A122 make a narrated occurrence inside an abilities section an event. Section B: an act the 12 verbs express stays an event and never gets an `attacked` twin. The gold's own b1102 (same section) writes the Megumi blitz as `fought`.

### b1735 · Sukuna / Physical Prowess
- Sentence 2: "When Yuji attempted to attack him in his innate domain, Sukuna effortlessly countered all of Yuji's attacks before seeing through his attempt to trip him and defeating him with a single kick.(Chapter 11, Episode 6)"
- Gold: `Sukuna|defeated|Yuji` and the fact `Yuji|other_verb|attack` (attempted). The reviewer note: "A145 the kick is the defeat; the attempted attack".
- Proposed: `+ Yuji|fought|Sukuna|Sukuna effortlessly countered all of Yuji's attacks` and `f- Yuji|other_verb|attack`.
- Rule: step 5 verb rules, "fought AND defeated when the fight is stated separately" (compare procedure Example 3, Walker and Morgenthau). A145 settles that the kick is defeated and not fought, but the countered attacks are an exchange stated before the kick. A96: the attacks happened (they were countered), so "attempted" no longer fits.
- Check: this goes against an explicit A145 note by the reviewer.

## Unsure

### b1384 · Shibuya / History
- Sentence 4: "Nanami took over the battle and defeated Shigemo inside the Bunkumura substation before regrouping with Team Zenin and heading straight for the Fukutoshin Line.(Chapter 101, Episode 36) On their way, Nanami, Maki, and Naobito were engaged by Dagon and trapped inside his Domain Expansion."
- Gold: the fact `Nanami|joined|Team Zenin`, and no met rows.
- Question: should `Nanami|met|Maki` and `Nanami|met|Naobito` be added? A48 says people met where they are get both a met and a joined row. The team's members are tied only indirectly, through "their way" followed by the three names, and "Team Zenin" itself names no one (A2/A57).

### b1238 · Shibuya Incident / 11:14 P.M. - 11:36 P.M. Shibuya Station
- Sentence 5: "Before Yuji can catch up and finish Mahito off, however, Pseudo-Geto appears to come to his ally's aid.(Chapter 132, Episode 45)"
- Gold: `Pseudo-Geto|met|Mahito` only.
- Question: should `Pseudo-Geto|met|Yuji` be added? The met table supports it, since Pseudo-Geto arrives where Yuji is. Against it: he arrives to stop Yuji, and Yuji fights him in the very next window (b1318). Add.6/A145 rule out a met with the person the newcomer then fights.

### b1732 · Shibuya Incident / 8:51 P.M. - 9:26 P.M. Fukutoshin Line Platform
- Sentence 3: "Mahito and the others wake up from their Unlimited Void induced trance and regroup with Geto."
- Gold: the fact `Mahito|other_verb|wake`, and no awakened row.
- Question: should it be `+ Mahito|awakened|-` with `f- Mahito|other_verb|wake`? A106 makes regaining consciousness after a knockout an `awakened` event and excludes only ordinary sleep, dreams and machine sessions. It is unclear whether a domain-induced trance is a loss of consciousness.

### b1100 · Shibuya Incident / Prologue
- Sentence 1 (part): "Jogo initially refuses and tries to kill Satoru himself in exchange for Prison Realm."
- Sentence 2: "Naturally, Jogo is effortlessly defeated and Geto uses this exchange to emphasize that Satoru must be sealed at the right time and place using every advantage they have."
- Gold: `Satoru Gojo|defeated|Jogo` on "Jogo is effortlessly defeated".
- Question: is this row legal? The passive has no "by", so Satoru is the doer only by context. A110 says no named agent means no row, and Add.5 says an implied doer is "A8 no row", which would mean `- Satoru Gojo|defeated|Jogo` plus a `no_doer` tag. On the other hand, the window names only one possible opponent. If the row goes, the supervisor may also want to consider `Jogo|fought|Satoru Gojo`, since "tries to kill Satoru himself" is followed by "Following the battle".
