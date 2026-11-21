# A17 adjudication: fix and unsure windows

40 windows: 31 gold_ok, 7 fix, 2 unsure.

## b1401 (fix): Yuki Tsukumo & Choso vs. Kenjaku / Battle
- Sentence 7: "Kenjaku blasts a hole through Yuki's lower torso, dealing a fatal blow as Choso watches from the ground.(Chapter 207)"
- Gold: `Kenjaku|killed|Yuki` on "Kenjaku blasts a hole through Yuki's lower torso, dealing a fatal blow". `Yuki|fought|Kenjaku` is already there.
- Proposed: remove `Kenjaku|killed|Yuki`. The window states no death, and she is still alive in page_text_after ("Before Yuki has time to use reverse cursed technique, Kenjaku activates his gravity technique...").
- Rule: step 5 table (killed NO "'fatal blow' without a stated death (fought)"; defeated NO the same), A145. The pair keeps its one fought row. The supervisor may also want `f+ Kenjaku|wounded|Yuki` (FW ruling). I did not add it because the brief leaves facts alone.

## b1554 (fix): Yuta Okkotsu vs. Suguru Geto / Prologue
- Sentence 4: "However, Suguru defeats Maki, Toge, and Panda all in brutal fashion."
- Sentence 5: "Yuta arrives late to the scene of the battle where he finds his friends all bloodied and battered by Suguru."
- Gold: no met. It has `Yuta|other_verb|finds`. Reviewer note: "finding unnamed 'friends'".
- Proposed: `+ Yuta|met|Maki`, `+ Yuta|met|Toge`, `+ Yuta|met|Panda` (quote: sentence 5 up to "by Suguru"), and `f- Yuta|other_verb|finds`.
- Rule: the friends are named by the window. "bloodied and battered by Suguru" is the three he defeated in sentence 4 (step 4 "the two / they" expansion, A2/A57). Arriving where they are is met (table "X arrived where Y was"; Addendum 6). Under section B, the event replaces the fact. There is no met with Suguru, because the fight follows (A145, Addendum 6).

## b2882 (fix): Brook/History / Entering Totto Land
- Sentence 4: "As Brook pleaded to Pedro not to use violence, they were saved by Charlotte Pudding, who then invited the Sanji Retrieval Team into her home where she offered them food."
- Gold: `Charlotte Pudding|saved|Luffy` and `|saved|Chopper`, plus met with Brook, Nami, Carrot and Pedro. There is no met with Luffy or Chopper.
- Proposed: `+ Charlotte Pudding|met|Luffy` and `+ Charlotte Pudding|met|Chopper` on "they were saved by Charlotte Pudding".
- Rule: A34 (met each person reached + saved). Both are also members of the team she meets.

## b2824 (fix): Caesar Clown / Personality
- Sentence 2: "He was very surprised that his poisons did not affect Luffy due to the latter's immunity to poison given to him from his near-death poisoning by Magellan."
- Sentence 5: "He was extremely excited when the Fire Tank Pirates used his KX Launchers in their attempt to assassinate Big Mom and was frustrated when the Emperor easily destroyed his weapons simply by screaming."
- Gold: facts only. It has `Magellan|wounded|Luffy`, `Fire Tank Pirates|other_verb|assassinate` (attempted) and `Big Mom|destroyed|weapons`. There is no fought event.
- Proposed: `+ Fire Tank Pirates|fought|Big Mom` and `+ Magellan|fought|Luffy` (quotes in the fix file). The existing facts stay: the attempt and the wound are different claims from the attack.
- Rule: step 5 fought YES. It covers "any attack MADE on someone, even if blocked", "'tried to hinder her by ...' when an act is done", "a power or technique used ON someone" and "attacks told in passing". The FW ruling keeps fought beside the wounded fact. The Fire Tank Pirates name no member in the window, so the group is the end. This is a medium-confidence fix: the reviewer saw the attempt and wrote it as a fact only.

## b2915 (fix): Chapter 1067 / Long Summary
- Sentence 1: "On Momoiro Island, Kuma starts moving, perplexing the Revolutionary Army."
- Sentence 3: "This causes Dragon and Ivankov to ask him to stay, as their battle as the Revolutionary Army is now beginning."
- Gold: `Dragon|met|Kuma` and `Ivankov|met|Kuma` on "This causes Dragon and Ivankov to ask him to stay".
- Proposed: remove both. No one arrives, shows up or comes together in the passage. The three are already together at the Revolutionary Army's location. The ask/stay facts still cover the sentence.
- Rule: met table NO ("talking inside a meeting already under way; companions who are already together"). Addendum 6 keeps that exclusion for people who never parted in the passage.

## b2826 (fix): Chapter 111 / Long Summary
- Sentence 1: "We return to the two Baroque Works agents, who identify Zoro as the one who defeated the town's agents; they ask him further why he is protecting Vivi."
- Sentence 2: "After an ambiguous answer from Zoro, the pair prepare to attack, Miss Valentine boasting about her Devil Fruit ability."
- Gold: `Miss Valentine|met|Zoro` on "they ask him further why he is protecting Vivi". Reviewer note: "ok".
- Proposed: remove it. "We return to" and "ask him further" continue an encounter that is already under way, and no coming-together is narrated. The attack is only prepared, which makes it a plan.
- Rule: met table NO ("talking inside a meeting already under way").

## b2965 (fix): Elbaph Arc / Loki's Lament
- Sentence 6: "... constructing what would become Shakky's Rip-off Bar ..."
- Sentence 7: "Two years later, Roger decided to go to the bar to try and win her, ..."
- Sentence 8: "At the bar, Shakky noted that Rocks was no longer as infatuated with her, ..."
- Sentence 9: "When Roger arrived, he and Rocks quickly got into a confrontation, but they were prohibited from fighting in the bar."
- Gold: `Roger|met|Rocks`, with no arrival for Roger. Gold already resolves "Shakky came to the island" to `Shakuyaku|arrived|Hachinosu`.
- Proposed: `+ Roger|arrived|Shakky's Rip-off Bar` on "When Roger arrived, he and Rocks quickly got into a confrontation".
- Rule: arrived table ("X arrived where Y was"), A151 (the passage says he came there), A123 (the most specific named place). "The bar" resolves to the named bar exactly as "the island" does in this same window.

## b1170 (unsure): Yuta Okkotsu / Cursed Techniques
- Sentence 2: "Reverse Cursed Technique 反転術式 Hanten Jutsushiki: When faced with the dire injuries of his friends, Yuta was able to tap into the core of his cursed energy and unlock the ability to heal their injures with reverse cursed technique."
- Sentence 8: "He also used it to exorcise Kurourushi, compromising the cursed spirit's body with a blast of positive energy.(Chapter 175, Episode 59)"
- Gold: `Yuta|gained_power|reverse cursed technique` (reviewer: "unlocking a power is no awakening") and `Yuta|other_verb|exorcise` (Kurourushi). The second reader has awakened and `killed Kurourushi`.
- Why unsure: the awakened table says YES to "gained a new power or form for the FIRST time", which matches a first-time unlock. The reviewer deliberately ruled it out, and A140 routes first powers to a gained_power fact. Separately, exorcising a named cursed spirit (its body destroyed) may be `killed` (a named non-human destroyed, as A69). It could also be read as a purpose clause ("used it to exorcise"). Both points need a ruling on this gold's JJK practice.

## b2982 (unsure): Chapter 928 / Long Summary
- Sentence 6: "Some of the Flower Capital's forces then arrive and subdue Komurasaki's assailants, exiling them from the village for having no money as Komurasaki arrives at Orochi's palace."
- Gold: `Komurasaki|arrived|Orochi's palace`. The second-reader differences are name forms only (Komurasaki/Hiyori, Kyoshiro/Denjiro).
- Why unsure: "Orochi's palace" is a possessive description, not a proper name. The arrived table says NO to "a description instead of a name ('her apartment', 'his room')". I cannot tell whether this gold accepts it as the name of the castle. If not, the row should go, and the clause would need an `other_verb arrives` fact or a tag.
