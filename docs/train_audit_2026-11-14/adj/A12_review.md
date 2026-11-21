# A12 adjudication: fix and unsure windows

44 windows: 33 gold_ok, 6 fix, 5 unsure.

## Fixes

### b1047 (Kokichi Muta/Synopsis / Shibuya Incident Arc)
- Sentences: "Taking advantage, Kokichi commanded Mode: Absolute to relentlessly pummel Mahito and his surrounding area, forcing him to transform into a bird and flee." / "Although Mahito evaded the beams, Mechamaru's subsequent punches sent him crashing into a nearby forest."
- Gold: `Kokichi|fought|Mahito` and `Mechamaru|fought|Mahito` (plus `Mahito|escaped|Kokichi`).
- Proposed: `- Mechamaru|fought|Mahito`.
- Rule: A119 (a named robot body counts as the character itself) / step 4 (a suit or vehicle is never the subject, its user is). Either way Mechamaru is Kokichi's piloted puppet, so the row is a second fought row for the one Kokichi-Mahito pair (step 5: fought once per pair).

### b1594 (Larue / Cursed Child Arc)
- Sentence: "He then infiltrates the Jujutsu High along with Geto, Nanako and Mimiko Hasaba."
- Gold: only `Larue|arrived|Jujutsu High`.
- Proposed: `+ Geto|arrived|Jujutsu High`, `+ Nanako|arrived|Jujutsu High`, `+ Mimiko Hasaba|arrived|Jujutsu High` (same quote). The name forms follow the window and the gold's existing rows ("Nanako" in the interrupted fact).
- Rule: A1 / A141 (not only the page subject); worked example 2 ("Davy accompanied Kingpin to Tamaha", so both arrived).

### b1749 (Larue / Shibuya Incident Arc)
- Sentence: "While Yuki confronts Kenjaku, Larue takes this opportunity to rescue Aoi Todo, Mai Zenin and Kasumi Miwa.(Chapter 136, Episode 47)"
- Gold: fact `Yuki|other_verb|confronts` (no object) and no event.
- Proposed: `+ Yuki|met|Kenjaku|While Yuki confronts Kenjaku`, `f- Yuki|other_verb|confronts`.
- Rule: the decision table has met YES for "confronted X (also with a fight)". The window states no fight between them, so A145 does not block it. Section B: an event is never also a fact.

### b1417 (Mai Zenin/Synopsis / Fearsome Womb Arc)
- Sentence: "Nobara insulted Mai about her looks, which angered her enough to shoot Nobara several times with rubber bullets.(Chapter 17, Episode 8) Suddenly, Maki showed up and distracted Mai long enough for Nobara to put her in a chokehold."
- Gold: `Maki|met|Mai` only.
- Proposed: `+ Maki|met|Nobara Kugisaki|Maki showed up and distracted Mai long enough for Nobara to put her in a chokehold`.
- Rule: Addendum 6 says a character who "shows up" where a named ally is gets a met with each named person there. Nobara is present and fighting alongside her.
- Not proposed: Aoi Todo met Mai for "Aoi then appeared", because the two came together and the window never clearly parts them.

### b1685 (Maki Zenin/Synopsis / Shinjuku Showdown Arc)
- Sentences: "Weeks later, after winning the fight against Sukuna, Nobara, Yuji and Megami arrived to where Yuta was being berated by Maki again." / "While Yuji and Megumi attempted to apologize to everyone, Maki and Kusakabe told them it wasn't necessary."
- Gold: Nobara and Yuji each met Yuta and Maki. There is no row for Megumi, although the gold writes "Megumi" in its apologize fact.
- Proposed: `+ Megumi|met|Yuta`, `+ Megumi|met|Maki` (the gold's quote of sentence 1).
- Rule: A4, one name per person. "Megami" is a typo for the Megumi of sentence 2, and the table has met for "X arrived where Y was".
- Not proposed: `Megumi|defeated|Sukuna`. The reviewer's note deliberately limits "winning the fight" to Nobara and Yuji, and a supervisor may want to confirm that.

### b1475 (Megumi Fushiguro / Overview)
- Sentences: "Then Toji isolated Megumi from the rest of the team and the latter immediately realized the amount of danger he was in.(Chapter 111, Episode 40) However, he was able to survive against the same monstrous physical prowess that overpowered Ino and Dagon." / "He rationally accepted that he couldn't escape the fight without an injury, ..."
- Gold: no event between Toji and Megumi, only the fact `Megumi|other_verb|survive`.
- Proposed: `+ Toji Zenin|fought|Megumi|However, he was able to survive against the same monstrous physical prowess that overpowered Ino and Dagon.` The survive fact stays, because surviving is a separate claim.
- Rule: A1. Fought YES covers "faced X in battle", and the window names the fight itself ("escape the fight").

## Unsure

### b1568 (Kokichi Muta vs. Mahito / Battle)
- Sentences: "He takes another technique tube and tries to stab Mahito with it in a last-ditch effort." / "The two fighters lunge at each other and their hands pass by one another's with great speed." / "Unfortunately for Kokichi, he was the slower one and his dreams are taken away along with his life."
- Gold: `Mahito|killed|Kokichi`, the fact `Kokichi|other_verb|stab` (attempted), and a no_relation tag on the lunge sentence.
- Why unsure: the lunge may be a failed attack that was actually made (table: fought YES "even if blocked, dodged or failed"; step 5: fought + killed when a fight is stated before the kill). Against that, the gold's A134 attempted reading and A145 (the lunge and the kill as one exchange) are also defensible.
- Candidate if decided for fought: `+ Kokichi|fought|Mahito|The two fighters lunge at each other`, `t- no_relation|The two fighters lunge`.

### b1368 (Mai Zenin/Synopsis / Culling Game Arc)
- Sentence: "After massacring the entire Zenin clan, Maki took Mai's corpse and handed it over to Momo, who tearfully mourned her death.(Chapter 152, Episode 51)"
- Gold: the fact `Maki|other_verb|massacring`, with no killed row.
- Why unsure: the Zenin clan is a named group and the window ties none of its members to the act, so step 6 could allow `Maki|killed|Zenin clan`. Against that, killed NO excludes killing groups ("killed numerous Masters"), and the reviewer chose the fact deliberately.

### b1678 (Maki Zenin vs. Ogi Zenin / Prologue)
- Sentences: "Only Ogi Zenin is inside with a heavily injured Mai lying in her own blood behind him." / "Ogi anticipated Maki's moves and emptied the place of all cursed tools before she got here and slashed Mai himself, leaving her alive to only serve as an emergency hostage."
- Gold: `Ogi Zenin|fought|Mai` and `Ogi Zenin|wounded|Mai`.
- Why unsure: the second reader adds defeated. Mai is left incapacitated with nothing continuing, so the Klaue test (2026-11-04 FW) would give defeated, and one act means fought drops (A145, as in b1177). But no fight is stated, and Add.3 treats harm to a captive or hostage as wounded only, without fought or defeated.

### b1408 (Maki Zenin, Toge Inumaki & Panda vs. Suguru Geto / Prologue)
- Sentence: "While standing over Maki's bloodied and defeated body, Geto senses a hole was made in the barrier and expects his adversaries to take five minutes to reach him."
- Gold: `Suguru Geto|defeated|Maki`.
- Why unsure: the window never states who defeated Maki. The doer is only implied by Geto standing over her, and Add.5 says "implied doer = A8 no row" (A8 strict reading). The reviewer, however, read the doer from this window. If the strict reading applies, the fix is `- Suguru Geto|defeated|Maki`. The sentence stays covered by Geto's discovered and suspected facts.

### b1142 (Maki Zenin/Synopsis / Shinjuku Showdown Arc)
- Sentence: "Maki and Miwa were then transferred to safety by Aoi Todo's Boogie Woogie.(Chapter 260) Sometime following the successful raid on Sukuna, Maki went to scold Yuta leading to Inumaki, Panda, and fellow surviving sorcerers to gather together to \"save Yuta\" from her scolding.(Chapter 268)"
- Gold: `Maki|other_verb|scold` (planned), with no met.
- Why unsure: "went to scold" is a purpose clause (A19: no met), but "save Yuta from her scolding" suggests the scolding and the encounter happened (A35: check what follows). If the encounter happened, add `+ Maki|met|Yuta|Maki went to scold Yuta`.
