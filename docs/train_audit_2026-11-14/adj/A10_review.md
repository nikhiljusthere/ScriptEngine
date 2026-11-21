# A10 adjudication: fix and unsure windows

Counts: 19 gold_ok, 6 fix, 8 unsure (33 windows).

## Fixes

### b1444, Episode 13 / Plot Details (fix)
- S3: "Just as Nanami prepares to die, Yuji breaks into Mahito's domain from the outside."
- Gold: no meeting row. It has the fact `Yuji|other_verb|breaks`.
- Proposed: `+ Yuji|met|Nanami` and `f- Yuji|other_verb|breaks`. The met event takes over the clause, because section B says an event is never also a fact.
- Rule: the met table's "X arrived where Y was", and Addendum 6 (a companion showing up after the two were apart). No met with Mahito: Sukuna fights him next (A145).

### b1584, Episode 24 / Plot Details (fix)
- S1: "When Yuji and Nobara trade places, Eso gets a glance at his younger brother and realizes that he's been grievously injured by Yuji's barrage of punches."
- Gold: it has `Yuji|wounded|Kechizu` (fact) but no event for Yuji against Kechizu.
- Proposed: `+ Yuji|fought|Kechizu|he's been grievously injured by Yuji's barrage of punches`. The wounded fact stays, as the FW class requires.
- Rule: the fought table counts "attacks told in passing". "realizes" is factive, so the punches happened. A1.

### b1547, Episode 32 / Plot Details (fix)
- S5: "Mei Mei notices the curtain is gone and tells Ui Ui they'll meet up with Yuji before heading down to B5F."
- S8: "Team Mei Mei regroups, and the grade 1 sorcerer commends Yuji for his performance."
- Gold: no met. It tags "Team Mei Mei regroups," as `no_relation`.
- Proposed: `+ Mei Mei|met|Yuji` and `+ Ui Ui|met|Yuji`, both quoting S8.
- Rule: the met table includes "a reunion", and Addendum 6 says an earlier scene together does not mean they are "already together".
- Note: the brief says to leave tags alone, so the `no_relation` tag on "Team Mei Mei regroups," stays even though it is now covered. The supervisor may want to remove it.

### b1345, Episode 36 / Plot Details (fix)
- S4: "Mei Mei then prepares to kill Ebina, who begs for forgiveness and swears to never do evil again."
- S9: "She then reveals that service potential is life itself for her before swinging her axe down on Ebina."
- Gold: `Mei Mei|killed|Niji Ebina`.
- Proposed: `- Mei Mei|killed|Niji Ebina` and `+ Mei Mei|fought|Niji Ebina|swinging her axe down on Ebina`.
- Rule: killed needs "a stated death with its doer", and the killed row's NO column says a fatal blow without a stated death is fought. The window states the swing and a plan to kill, but no death. The existing planned `kill` fact stays.

### b1404, Episode 46 / Plot Details (fix)
- S4: "She reveals to the person calling her that she was almost killed by Pseudo-Geto and had to escape with Ui Ui's cursed technique."
- Gold: `Mei Mei|escaped|Pseudo-Geto` (event) and `Pseudo-Geto|other_verb|killed` (actual, denied).
- Proposed: `+ Pseudo-Geto|fought|Mei Mei|she was almost killed by Pseudo-Geto`.
- Rule: step 3 and A40 count an attack that was made but failed as fought. "revealed" is factive (Add.4), and the gold already treats it that way with the escaped row. The NEAR denied fact stays: it records that the kill did not happen, which is a different claim from the attack.

### b1348, Episode 8 / Juju Stroll (fix)
- S2: "Once Todo comes back to her, he insists that his schoolmate uses the other ticket he has to shake hands with the idol."
- S6: "When Mai returns back to Todo, she is uncharacteristically quiet, mumbling to herself that Takada-chan wasn't so bad."
- Gold: only `Mai|met|Takada-chan`.
- Proposed: `+ Todo|met|Mai|Once Todo comes back to her`. One met per pair, so S6 needs no second row.
- Rule: the met table's "X arrived where Y was" and "a reunion", and Addendum 6.

## Unsure

### b1605, Dagon/Synopsis / Shibuya Incident Arc (unsure)
- S6: "As a hole to the outside of the domain opened up beneath Megumi, Toji Fushiguro suddenly entered through it.(Chapter 109, Episode 38)"
- Gold: `Toji Fushiguro|other_verb|entered`. The second reader has Toji met Megumi.
- Why unsure: the met table's "X arrived where Y was" could support `Toji Fushiguro|met|Megumi` replacing the entered fact. But Toji is not a companion (Addendum 6), and the window does not settle whether Maki, Nanami and Naobito, who are in the same domain, also get a met.

### b1308, Mahoraga / Yuka Okkotsu (unsure)
- S1: "At the climax of their battle, Mahoraga witnessed Dabura discover his Cursed Technique Reversal, surprising it once again."
- Gold: `Dabura|other_verb|discover`. The reviewer wrote "discovering a technique is no awakening". The second reader has Dabura awakened.
- Why unsure: the awakened row in the verb table includes "gained a new power ... for the FIRST time", but this gold records first powers as facts (see b1598). This needs a ruling on first-power awakened versus the fact route, which is broader than the brief's transformed_into exception.

### b1598, Episode 13 / Plot Details (unsure)
- S3: "As they continue to beat Mahito closer to death, he gains inspiration from it, enough to activate Domain Expansion for the first time."
- Gold: `Mahito|gained_power|Domain Expansion` (fact). The second reader has Mahito awakened.
- Why unsure: this is the same question as b1308. The table says awakened, while A140 names the power in a fact. Adding the event would, under section B, delete the fact that names the power.

### b1642, Episode 24 / Plot Details (unsure)
- S1: "Back at Yasohachi Bridge, Akari is trying to contact the first-years but none of them answer her phone calls much to her annoyance."
- S2: "She then drives off to look for them."
- Gold: `Akari|located_at|Yasohachi Bridge` and `Akari|other_verb|drives`. The second reader has Akari departed Yasohachi Bridge.
- Why unsure: "drives off" names no place left, and the first-years she is looking for are at the bridge, so leaving the named place is not plainly stated.

### b1145, Episode 24 / Plot Details (unsure)
- S2: "As Nobara turns around, Kechizu makes the last ditch effort to try and take her life, attempting to devour her from behind."
- S3: "However, Nobara quickly snaps and activates Straw Doll Technique: Hairpin, detonating the nail in Kechizu's head, killing him instantly."
- Gold: `Kechizu|other_verb|devour` (attempted). The reviewer wrote "the tried verb".
- Why unsure: this may be an attack made that failed, which would be `Kechizu|fought|Nobara`, as in b1605 where "tried to attack Megumi but missed" became fought. It may also be an attempt cut off by the kill, which is A134 and the reviewer's reading.

### b1188, Episode 24 / Plot Details (unsure)
- S1: "The two then arrive underneath the bridge and find Megumi unconscious, which worries them."
- S7: "Up on the bridge, Akari arrives and yells at the three who ignore her much to Akari's annoyance."
- Gold: no Akari met. The bridge has no arrived row, which is right because "the bridge" is unnamed.
- Why unsure: Akari is up on the bridge while the three are underneath it. This may be a met under Addendum 6, or only contact at a distance (A45).

### b1762, Episode 44 / Plot Details (unsure)
- S1: "Overjoyed by Yuji's suffering, Mahito rushes at Yuji with his arm shaped into a jagged blade."
- S2: "Todo claps his hands and activates Boogie Woogie to switch Mahito with Arata behind him."
- S4: "Todo quickly swaps Arata and Mahito again, preventing a collision as the special grade tumbles away on the ground."
- Gold: `Todo|fought|Mahito`, `Todo|other_verb|swaps` and the `used` Boogie Woogie fact. The second reader has Todo saved Yuji and Todo saved Arata.
- Why unsure: the S2 switch may intercept Mahito's rush at Yuji (A75 saved), and S4 may protect Arata. But the window never states that either person was protected from harm.

### b1179, Episode 46 / Plot Details (unsure)
- S2: "Recognizing Geto's name, Yuji acts quickly and rushes towards the curse user while demanding he return Satoru Gojo."
- Gold: `Pseudo-Geto|met|Mahito` and `Yuji|other_verb|rushes`. The second reader has Yuji fought Pseudo-Geto, which is wrong because no attack is stated.
- Why unsure: rushing toward him may be a met by approach (the met table's "approached X"), which would replace the rushes fact. It may instead be the opening of the fight that follows the window, where A145 means no met.
