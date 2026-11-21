# A13 adjudication: fix and unsure windows

## Fixes

### b1099 · Megumi Fushiguro, Toge Inumaki & Noritoshi Kamo vs. Hanami / Prologue
- Sentence: "As Toge flees from Hanami's giant roots, he reaches the roof of a building while the wooden attack goes overhead."
- Gold has `Toge|escaped|Hanami` and no fought row.
- Proposed: `+ Hanami|fought|Toge|As Toge flees from Hanami's giant roots`.
- Rule: A40 and the fought table ("any attack MADE on someone, even if blocked, dodged or failed"). The roots are Hanami's power (A120). Escaped records the getaway, not the attack.
- Not proposed: no fought for Megumi and Noritoshi on "dodge the crashing roots". The window does not say the roots were aimed at them. No saved for the command (A12/A64).

### b1260 · Momo Nishimiya/Synopsis / Kyoto Goodwill Event Arc
- Sentence: "Just as Nobara was about to knock Momo unconscious, Mai shot Nobara from afar, knocking the first-year unconscious."
- Gold has `Mai|defeated|Nobara` only.
- Proposed: `+ Mai|saved|Momo`.
- Rule: A75 (intercepted attack: saved for the one protected), and Addendum 4, where stopping a named person's attack is `defeated` plus `saved` for the target. Momo was about to be knocked out.

### b1757 · Nanako Hasaba/Synopsis / Cursed Child Arc
- Sentences:
  - 1: "After the meeting, Nanako accompanied Geto to Tokyo Jujutsu High alongside Mimiko and Larue."
  - 3: "Following Geto's declaration, Nanako alerted him that the crepe shop they planned to visit was about to close, causing the curse users to leave."
- Gold has `Nanako|departed|Tokyo Jujutsu High` only.
- Proposed: `+ Geto|departed|...`, `+ Mimiko|departed|...` and `+ Larue|departed|...`, each quoting "causing the curse users to leave".
- Rule: A2/A57. The curse users are the four the window names as arriving together, so each named member gets the row.

### b1667 · Nanako Hasaba/Synopsis / Shibuya Incident Arc
- Sentence: "Later, Nanako and Mimiko found Yuji Itadori unconscious after his fight with Choso."
- Gold has no fought row for Yuji and Choso.
- Proposed: `+ Yuji Itadori|fought|Choso|found Yuji Itadori unconscious after his fight with Choso`.
- Rule: step 3 (a past event mentioned in passing) and the fought table. The same gold writes "his fight with X" as fought in b1141 (Kamo) and b1155 (Choso).
- Not proposed: no defeated, because who knocked Yuji out is not stated. No met for finding the unconscious Yuji (the reviewer's ruling, A135).

### b1284 · Panda vs. Hajime Kashimo / Battle
- Sentences:
  - 2: "He separates the charges of his electrified cursed energy, applying the positive charge to Panda before discharging the negative charge from himself."
  - 4: "In a flash of lightning, Panda's body is torn to shreds ... as he stands victorious ..."
- Gold has `Kashimo|defeated|Panda` and the fact `Kashimo|other_verb|applying`.
- Proposed: `+ Kashimo|fought|Panda|applying the positive charge to Panda` and `f- Kashimo|other_verb|applying`.
- Rule: the fought table counts "a power or technique used ON someone". By step 5 and A145, a fight stated separately from its outcome gets fought plus defeated, and this gold applies that to separate sentences (b1299, b1134). Section B: the event replaces its twin fact.

### b1377 · Playful Cloud / Toji Fushiguro
- Sentence: "It even destroyed Dagon's water shield in a single hit, a technique that withstood blows from Naobito Zenin, Kento Nanami, and Maki at the same time."
- Gold has no rows for this clause and tags it `no_relation`.
- Proposed: `+ Naobito Zenin|fought|Dagon`, `+ Kento Nanami|fought|Dagon` and `+ Maki|fought|Dagon`, each quoting the clause.
- Rule: A40 and the fought table ("even if blocked"). The blows were attacks on Dagon that his shield blocked, and step 3 covers a past act mentioned in passing.
- Note: the brief says to leave tags alone, so the `no_relation` tag on "a technique that withstood blows from ..." stays. The supervisor may want to drop it (`t- no_relation|a technique that withstood`).
- Possible objection: A42 (an attack on an object only), if the shield is read as the target.

## Unsure

### b1448 · Megumi Fushiguro / Physical Prowess
- Sentence: "He suffered a beatdown at the hands of Sukuna without any major injuries.(Chapter 9, Episode 5) Todo also overpowered Megumi in a similar fashion, but in both cases, Megumi never passed out and he continuously refused to back down."
- Gold has `Todo|defeated|Megumi`, with the note "overpowered is the defeat (one act)". Sukuna's "similar" beatdown is written as fought.
- Why unsure: the defeated table's NO column has "overpowers" while the fight continues, and "never passed out ... refused to back down" says the fight did not end with Megumi beaten. That would make it `fought`. The reviewer read it the other way.

### b1360 · Megumi Fushiguro, Toge Inumaki & Noritoshi Kamo vs. Hanami / Prologue
- Sentence: "As Megumi begins the call and suggests to Noritoshi that they must retreat, Hanami blitzes behind them and breaks the phone with a wooden projectile."
- Gold has `Hanami|fought|` for Megumi, Toge and Noritoshi.
- Why unsure: the only act stated is breaking a phone, an attack on an object, which is no fought under A42. "Them" is Megumi and Noritoshi in this clause, so including Toge rests on the reviewer's "Toge is behind them too". If A42 applies, all three rows go. If the projectile counts as an attack on the holder, only Megumi's row is clearly supported.

### b1715 · Nanako Hasaba/Synopsis / Shibuya Incident Arc
- Sentences:
  - 1: "Before the Shibuya Incident, Nanako and Mimiko reluctantly agreed to cooperate with Pseudo-Geto, who promised to return Geto's body to them if they helped kill non-sorcerers during the attack."
  - 3: "However, Pseudo-Geto reneged on the deal, mocking the sisters for not making a binding vow that would have compelled him to honor the agreement."
- Gold has `Pseudo-Geto|other_verb|reneged` and the allied_with facts.
- Why unsure: A54 says breaking faith with an ally is `betrayed`. Gold could also be right that reneging on a deal is only a broken promise, not "turning on" an ally.

### b1144 · Osada / Jujutsu Kaisen Modulo
- Sentences:
  - 2: "Osada appeared while Tsurugi and Maru were arguing, prompting the two to attack him."
  - 4: "After chastising them for calling him old, Osada introduced himself and explained his desire to save Toranosuke, ..."
- Gold has the fought rows plus `Osada|met|Tsurugi` and `Osada|met|Maru`, quoted on "Osada introduced himself". This was a lint override: "a stated talk after the opening attack".
- Why unsure: Addendum 6 confirms "no `met` with the one the newcomer then fights (A145)". The met table's NO column excludes "talking inside a meeting already under way". By the brief's standard both met rows would go, but the reviewer decided this case explicitly.

### b1038 · Piercing Ox / Usage
- Sentence: "Piercing Ox was subjugated by Sukuna after he took control of Megumi Fushiguro's body."
- Gold has `Sukuna|other_verb|subjugated`.
- Why unsure: "subjugated" may be the defeated table's "subdued", which would give `+ Sukuna|defeated|Piercing Ox` and `f- Sukuna|other_verb|subjugated`. It may also be only a taming or binding with no fight stated.

### b1048 · Playful Cloud / Maki Zenin & Megumi Fushiguro
- Sentence: "Although she was eventually overpowered, Playful Cloud's equalizing power allowed Maki to contend with Hanami despite her injuries."
- Gold has `Hanami|defeated|Maki`. The reviewer note says "the overpowering is Hanami's act".
- Why unsure: the passive has no "by", so Hanami as the doer comes from context. A110 and the strict A8 reading (Addendum 5: an implied doer gets no row) would give no defeated row and a `no_doer` tag instead.
