# Outcome ruling 2026-11-03 -- gold v2 proposals (NOT submitted)

Ruling: `plan/review_tools/gold27_system.md`, section "Owner ruling 2026-11-03". Every outcome row is decided from the
factual state the passage establishes (who is subdued / in control, does the exchange continue, final or temporary);
one act can carry several true rows.

- Scan: `plan/review_tools/outcome_scan_gold.py` (wrapper `outcome_scan_gold.sh`), read-only. `--list OUT` writes the
  candidate list, `show B..` prints a compact reading view (full window + events + outcome facts + the hits),
  `check FILE` parses and gates a proposal file exactly like `rv.sh fix` but writes nothing.
- Snapshot: latest record per window in `gold_audit_v2.jsonl` as of 2026-11-03 ~12:40 (3,868 lines). One record was
  added during the pass (b2187, the owner's own worked example, not a candidate any more); no proposed window changed.
  Re-run `outcome_scan_gold.sh check outcome/proposed_G901.txt` before applying: on 2026-11-03 it reports
  70 would apply, 0 refused, no UNMATCHED removal.
- Scanned 3,822 windows; 639 candidates (`CANDIDATES.txt`): A_no_outcome 449, D_defeat_cont 163, C_wound_end 97,
  B_killed_wound 63, A_captured 28 (one window can carry several). All 639 were read in full (b6 .. b3821).
- Proposals: 70 windows in `proposed_G901.txt` (+defeated 51, +killed 3, -fought 27 where fight and outcome are one
  act per A145, -defeated 3 where the exchange continues, +fought 2 to keep the fight row there, f+wounded 33,
  f- dies 3 (twin of a new killed), f+other_verb 1).

Conventions used (so the owner can check them in one place):
- Added `defeated` only when the passage shows the encounter ending with that side subdued (knocked out, cut down and
  out of the fight, restrained/disarmed with nothing continuing, beaten and replaced, a stated loss/victory).
- Dropped `fought` only when its quote is the same act as the new outcome (A145); a fight stated in its own clause
  keeps `fought` beside the new row (e.g. b320, b1446, b1453, b3608).
- Removed `defeated` when the same passage shows the defeated side fighting on (b850 Buu, b1126 Sukuna "appears as
  if Gojo has won until", b3519 Naoya); the act is then `fought` + `wounded`.
- Added `wounded` only for an injury the text states (cut off, severed, impaled, bleeding, injure/harm, made to spit
  blood); "nearly killed", "beat up", "sent flying", "knocked down" alone got no wounded row. Never added a second
  wounded row for a pair that already has one, never rewrote `Victim|wounded|-` into the attacker form.
- `killed` was proposed only where a named doer's act causes a death the window states (b30, b348, b1351); destroyed
  bodies with an apparent or unstated death stay `defeated` (b791, b1584, b2669, b3432).

## Proposed changes (b, rows for the pair before -> after, reason)

- b30: old `E Guts|fought|Dante; E Guts|fought|Errol; F Dante|dies|-; F Errol|wounded|-` -> new `E Guts|killed|Dante; E Guts|defeated|Errol; F Errol|wounded|-` -- the attackers are cut down (Dante's lethal blow, Errol's lost arm) and the attack ends in retreat: killed + defeated, one act each (A145)
- b105: old `E Guts|fought|Crow; F Crow|wounded|-` -> new `E Guts|defeated|Crow; F Crow|wounded|-` -- slicing the Crow's throat ends his part (he collapses, nothing continues): defeated, one act (A145)
- b166: old `E Guts|fought|Mandragoran Tree` -> new `E Guts|defeated|Mandragoran Tree` -- cutting out the tree's heart ends the tree's defence (Eriza flees with it): defeated, one act (A145)
- b245: old `E Guts|fought|Kundalini` -> new `E Guts|defeated|Kundalini` -- the blast dematerialises the Kundalini's body (a destroyed body = defeated), one act (A145)
- b320: old `E Izuru|fought|Dalk` -> new `E Izuru|fought|Dalk; E Izuru|defeated|Dalk` -- Izuru's strikes leave Dalk unable to move and the fight ends there: defeated beside the separately stated fight
- b348: old `E Driscoll Berci|fought|Sasakibe; F Sasakibe|wounded|-; F Sasakibe|dies|-` -> new `E Driscoll Berci|fought|Sasakibe; E Driscoll Berci|killed|Sasakibe; F Sasakibe|wounded|-` -- Driscoll's attack leaves Sasakibe mortally wounded and he succumbs to those wounds: a killing by a named doer (killed; the dies twin goes)
- b497: old `E Ichigo|fought|Renji; F Renji|wounded|-` -> new `E Ichigo|defeated|Renji; F Renji|wounded|-` -- Ichigo's attack severs Zabimaru and the injured Renji sits down and steps aside: the attack ends his fight (defeated, one act per A145)
- b532: old `E Mantis Devil|fought|Power` -> new `E Mantis Devil|fought|Power; F Mantis Devil|wounded|Power` -- the sickle slashes Power's side open (a stated wound) but does not stop her: wounded, no defeated
- b609: old `E Aki|fought|Kobeni; E Himeno|fought|Kobeni` -> new `E Aki|defeated|Kobeni; E Himeno|defeated|Kobeni` -- Aki disarms Kobeni and Himeno knocks her down: her attack ends there (disarm + takedown = defeated, one act per A145)
- b631: old `E Darkness Devil|fought|Quanxi; E Darkness Devil|fought|Pingtsi` -> new `E Darkness Devil|fought|Quanxi; E Darkness Devil|fought|Pingtsi; F Darkness Devil|wounded|Quanxi; F Darkness Devil|wounded|Pingtsi` -- the Darkness Devil removes everyone's hands: Quanxi and Pingtsi each lose their hands (wounded); no end of the encounter is stated for them
- b647: old `(none)` -> new `F Kobeni|wounded|Aki` -- Kobeni's stab lands on Aki, who shields Denji and bleeds: wounded (doer Kobeni)
- b652: old `E Barem|fought|Pochita; E Whip|fought|Pochita; E Spear|fought|Pochita; F Spear|wounded|Pochita` -> new `E Barem|fought|Pochita; E Whip|fought|Pochita; E Spear|fought|Pochita; E Pochita|defeated|Barem; E Pochita|defeated|Whip; E Pochita|defeated|Spear; F Spear|wounded|Pochita` -- Pochita cuts Makima and the four hybrids (Barem, Whip, Spear, Reze, all named in the window) into pieces: each is defeated, beside their separately stated attacks
- b717: old `E Nayuta|fought|Yoru` -> new `E Nayuta|fought|Yoru; F Nayuta|wounded|Yoru` -- the chain impales Yoru's forehead (a stated wound); the window leaves the encounter open: wounded only
- b724: old `E Kato|fought|Reze; E Tanabe|fought|Reze; F Reze|wounded|-` -> new `E Kato|fought|Reze; E Tanabe|fought|Reze; F Reze|wounded|-; F Kato|wounded|Reze; F Tanabe|wounded|Reze` -- the mold grown in Reze's heart and intestines makes her cough up blood (a stated injury by the two hunters); she retaliates, so no defeated
- b791: old `E Frieza|fought|Vegeta; F Frieza|wounded|Vegeta` -> new `E Frieza|defeated|Vegeta; F Frieza|wounded|Vegeta` -- the beaten Vegeta is mortally wounded by the Death Beam and takes no further part: wounded + defeated (one act, A145); his death is not stated in the window
- b850: old `E Goku|defeated|Super Buu` -> new `E Goku|fought|Super Buu; F Goku|wounded|Super Buu` -- cut in half, Super Buu pulls himself back together and fights on: the cut is a wound, not a defeat (the exchange continues)
- b868: old `E Kid Buu|fought|Vegeta` -> new `E Kid Buu|defeated|Vegeta` -- Vegeta is no match, Buu beats him and is about to finish him when Goku takes over: Vegeta is beaten (defeated, one act per A145)
- b908: old `E Krillin|fought|Dium; F Dium|attacked|Krillin` -> new `E Krillin|fought|Dium; F Dium|attacked|Krillin; F Krillin|wounded|Dium` -- the Destructo Disc cuts Dium's wings (a stated wound); Roshi's Kamehameha ends it (defeated already)
- b1035: old `E Yuta|fought|Sukuna; E Yuji|fought|Sukuna` -> new `E Yuta|fought|Sukuna; E Yuji|fought|Sukuna; F Yuta|wounded|Sukuna; F Yuji|wounded|Sukuna` -- the passage states the injuries: minor cuts on Sukuna's face (Yuta) and a severed leg (Yuji); no end of the encounter is stated
- b1048: old `E Megumi Fushiguro|fought|Hanami` -> new `E Megumi Fushiguro|fought|Hanami; F Megumi Fushiguro|wounded|Hanami` -- Megumi harms Hanami with the staff (a stated injury); the fight goes on
- b1056: old `F Sukuna|attacked|Yuji` -> new `F Sukuna|attacked|Yuji; F Sukuna|wounded|Yuji` -- the punch pierces Yuji's gut (a stated wound); the incapacitation is stated as temporary, so no defeated
- b1113: old `E Yuta|fought|Ryu` -> new `E Yuta|fought|Ryu; F Yuta|wounded|Ryu` -- the blow makes Ryu spit up blood (a stated injury); no end of that exchange is stated
- b1126: old `E Gojo|defeated|Sukuna; E Gojo|fought|Sukuna` -> new `E Gojo|fought|Sukuna; F Gojo|other_verb|incapacitates` -- the incapacitation is a pause: "It appears as if Gojo has won until" Mahoraga retakes the field, so the exchange continues (no defeated; the blow stays as its own fact)
- b1134: old `E Nue|fought|Momo` -> new `E Nue|fought|Momo; E Nue|defeated|Momo` -- Nue's electro-shock wings paralyse Momo and she is out of that encounter (taunted where she landed): defeated beside the separately stated attack
- b1200: old `E Geto|fought|Maki; F Geto|wounded|Maki` -> new `E Geto|defeated|Maki; F Geto|wounded|Maki` -- Geto mortally wounds Maki and she is out (Yuta heals her and fights on): wounded + defeated, one act per A145 (Panda's and Toge's injuries alone do not state their fight ended)
- b1217: old `E Yuji|fought|Yuta; F Yuta|wounded|Yuji; F Yuji|dies|-` -> new `E Yuji|fought|Yuta; E Yuta|defeated|Yuji; F Yuta|wounded|Yuji; F Yuji|dies|-` -- restrained by Rika, Yuji is stabbed through the heart and bleeds out (apparent death): the stab is a wound that ends him (wounded + defeated, Klaue pattern)
- b1227: old `E Sukuna|fought|Yuta; F Sukuna|wounded|Yuta` -> new `E Sukuna|defeated|Yuta; F Sukuna|wounded|Yuta` -- Dismantle cuts through Yuta's arm and body and he is cut down with Rika and Yuji (their rows are defeated): wounded + defeated, one act per A145
- b1299: old `E Toji|fought|Megumi; E Shigemo|fought|Megumi; F Megumi|wounded|-` -> new `E Toji|fought|Megumi; E Shigemo|fought|Megumi; F Megumi|wounded|-; F Toji|wounded|Megumi; F Shigemo|wounded|Megumi` -- the passage states the injuries each doer dealt: Toji's stab punctures Megumi's abdomen, Shigemo grievously injures him; Megumi fights on, so no defeated
- b1306: old `E Kokun|fought|Riko` -> new `E Kokun|defeated|Riko` -- Kokun's attack blasts an unconscious Riko out of the room and Geto has to rescue her: knocked out = defeated, one act per A145
- b1322: old `E Satoru|fought|Hanami` -> new `E Satoru|fought|Hanami; F Satoru|wounded|Hanami` -- ripping out Hanami's roots is a stated injury; no end is stated: wounded
- b1351: old `E Ranta|fought|Maki; F Ranta|wounded|-; F Ranta|dies|-` -> new `E Ranta|fought|Maki; E Maki|killed|Ranta; F Ranta|wounded|-` -- Maki breaks the paralysis, causing the bleeding Ranta succumbs to: a death caused by a named doer's act (killed; the dies twin goes; the attempted restriction stays as the fight)
- b1357: old `E Satoru|fought|Hanami` -> new `E Satoru|fought|Hanami; F Satoru|wounded|Hanami` -- ripping the branches out of Hanami's face (their weak points) is a stated injury; the fight goes on: wounded
- b1388: old `E Yuji|fought|Mahito` -> new `E Yuji|fought|Mahito; F Yuji|wounded|Mahito` -- Yuji deals damage to Mahito's soul (a stated injury); the immobilisation is not stated to end the fight: wounded only
- b1446: old `E Nanami|fought|Haruta Shigemo; F Haruta Shigemo|attacked|Nanami` -> new `E Nanami|fought|Haruta Shigemo; E Nanami|defeated|Haruta Shigemo; F Haruta Shigemo|attacked|Nanami` -- Nanami is in control throughout (his attacks do nothing, Nanami grabs and hits him) and the encounter ends with Haruta sent through a building as Nanami leaves: defeated beside the separately stated fight
- b1453: old `E Masaki|fought|Tsurugi; F Masaki|wounded|Tsurugi` -> new `E Masaki|fought|Tsurugi; E Masaki|defeated|Tsurugi; F Masaki|wounded|Tsurugi` -- two needles into his torso critically injure Tsurugi and take him out (Maru takes over): wounded + defeated, as Yuka's incapacitation is
- b1527: old `E Mahito|fought|Nobara; F Mahito|wounded|Nobara; F Nobara|dies|-` -> new `E Mahito|defeated|Nobara; F Mahito|wounded|Nobara; F Nobara|dies|-` -- the mortal wound concludes their battle (Nobara seemingly murdered): wounded + defeated, one act per A145
- b1531: old `E Nobara|fought|Mahito; F Mahito|wounded|-` -> new `E Nobara|fought|Mahito; F Mahito|wounded|-; F Nobara|wounded|Mahito` -- Resonance makes nails burst out of Mahito's chest (a stated injury by Nobara) and stops him finishing Yuji; the fight goes on: wounded, no defeated
- b1584: old `(none)` -> new `E Nobara|defeated|Kechizu; F Nobara|wounded|Kechizu` -- Nobara's Black Flash sends a nail clean through Kechizu's head, the attack she was making on him: wounded + defeated (his death is not stated in this window)
- b1587: old `E Naoya|fought|Maki; F Naoya|wounded|-` -> new `E Naoya|fought|Maki; E Maki|defeated|Naoya; F Naoya|wounded|-` -- Maki's blows leave Naoya injured and bleeding on the ground while she stands over him (the exchange ends there): defeated
- b1596: old `E Aoi|fought|Hanami` -> new `E Aoi|fought|Hanami; F Aoi|wounded|Hanami` -- Aoi's swap gets Hanami impaled by its own attack (a stated injury Aoi causes); the fight goes on
- b1657: old `E Haruta Shigemo|fought|Megumi; F Megumi|wounded|-; F Haruta Shigemo|wounded|Megumi` -> new `E Haruta Shigemo|defeated|Megumi; F Megumi|wounded|-; F Haruta Shigemo|wounded|Megumi` -- the sneak-attack slash drops Megumi to the ground and nothing continues in the passage: wounded + defeated (Klaue pattern), one act per A145
- b1827: old `E Reed Richards|fought|Frightful Four; E Invisible Girl|fought|Frightful Four; E Thing|fought|Frightful Four; E Human Torch|fought|Frightful Four` -> new `E Reed Richards|fought|Frightful Four; E Invisible Girl|fought|Frightful Four; E Thing|fought|Frightful Four; E Human Torch|fought|Frightful Four; E Reed Richards|defeated|Frightful Four; E Invisible Girl|defeated|Frightful Four; E Thing|defeated|Frightful Four; E Human Torch|defeated|Frightful Four` -- the fight the Fantastic Four fought against the Frightful Four has a stated end ("the Frightful Four were defeated", after they broke free): fought + defeated for each member who fought
- b1970: old `E Quicksilver|fought|Mister X; F Quicksilver|wounded|Mister X` -> new `E Quicksilver|defeated|Mister X; F Quicksilver|wounded|Mister X` -- Quicksilver maims Mister X in the same breath as "Ant-Man finished Grizzly", and the villains' side falls: wounded + defeated, one act per A145
- b1986: old `E Thor|fought|Union Jack` -> new `E Thor|fought|Union Jack; F Thor|wounded|Union Jack` -- the lightning blast nearly kills Union Jack and Thor later restores him to health: a stated injury (wounded); no defeat is stated
- b1989: old `E Mockingbird|fought|Taskmaster; F Taskmaster|wounded|-; F Mockingbird|wounded|Taskmaster; F Taskmaster|dies|-` -> new `E Mockingbird|defeated|Taskmaster; F Taskmaster|wounded|-; F Mockingbird|wounded|Taskmaster; F Taskmaster|dies|-` -- shot in the head, Taskmaster is left in a vegetative state and left behind for dead: wounded + defeated, one act per A145
- b2026: old `E Marc|fought|Jigsaw` -> new `E Marc|defeated|Jigsaw` -- Jigsaw walks into the trap and Marc beats him until Andrea stops him: Jigsaw is subdued and the encounter ends (defeated, one act per A145)
- b2088: old `E Bucky|fought|Logan; F Bucky|wounded|Logan` -> new `E Bucky|defeated|Logan; F Bucky|wounded|Logan` -- Bucky's shot through the chest ends the forced duel and Logan is left to die: wounded + defeated, one act per A145 (the Nazis' flight is already defeated)
- b2232: old `E Thanos|fought|Eitri; F Thanos|wounded|Eitri` -> new `E Thanos|defeated|Eitri; F Thanos|wounded|Eitri` -- Thanos forces Eitri to work, kills the other Dwarves and fuses off Eitri's hands; nothing continues and Thanos is in control (the Klaue pattern): wounded + defeated, one act per A145
- b2455: old `E Winter Soldier|fought|Howard Stark; E Winter Soldier|fought|Maria Stark` -> new `E Winter Soldier|defeated|Howard Stark; E Winter Soldier|defeated|Maria Stark` -- Winter Soldier shoots the car down and the crash leaves the Starks unconscious while he prepares to execute them: knocked out = defeated, one act per A145
- b2572: old `E Elektra|fought|Shaft; F Elektra|wounded|Shaft` -> new `E Elektra|defeated|Shaft; F Elektra|wounded|Shaft` -- Elektra stabs Shaft through the chest and escapes; Rand is left to deal with the stricken Shaft: wounded + defeated, one act per A145
- b2603: old `E Yelena Belova|fought|Clint Barton; E Yelena Belova|escaped|Clint Barton` -> new `E Yelena Belova|fought|Clint Barton; E Yelena Belova|escaped|Clint Barton; E Yelena Belova|defeated|Clint Barton` -- the Widow's bite that subdues Lopez (defeated) is used on Barton too and ends the fight as Belova escapes: defeated beside the separately stated fight and her escape
- b2617: old `E Thor|fought|Imir` -> new `E Thor|defeated|Imir` -- electrocuting Imir ends his hold (the Dwarves are liberated): defeated, one act per A145
- b2669: old `E Deathlok|fought|Garrett` -> new `E Deathlok|defeated|Garrett` -- Deathlok's "supposedly fatal blow" ends Garrett's fight (the death is only apparent, so no killed): defeated, one act per A145
- b2778: old `E Peter Quill|fought|Ronan the Accuser; E Rocket Raccoon|fought|Ronan the Accuser` -> new `E Peter Quill|fought|Ronan the Accuser; E Rocket Raccoon|fought|Ronan the Accuser; E Peter Quill|defeated|Ronan the Accuser; E Rocket Raccoon|defeated|Ronan the Accuser` -- the battle has a stated end: Quill's distraction and Rocket's destruction of the Universal Weapon end it "enabling Ronan to be defeated": defeated for the two named in that final act, beside their fight rows
- b2952: old `E Law|fought|Blackbeard` -> new `E Law|fought|Blackbeard; F Law|wounded|Blackbeard` -- Law's attack stabs and zaps Blackbeard from the inside and Augur names the resulting injuries; Blackbeard refuses to retreat and fights on: wounded only
- b2957: old `E Usopp|captured|Neptune; E Nami|captured|Neptune; E Brook|captured|Neptune; E Zoro|captured|Neptune; E Usopp|fought|Neptune; E Nami|fought|Neptune; E Brook|fought|Neptune; E Zoro|fought|Neptune` -> new `E Usopp|captured|Neptune; E Nami|captured|Neptune; E Brook|captured|Neptune; E Zoro|captured|Neptune; E Usopp|fought|Neptune; E Nami|fought|Neptune; E Brook|fought|Neptune; E Zoro|fought|Neptune; E Usopp|defeated|Neptune; E Nami|defeated|Neptune; E Brook|defeated|Neptune; E Zoro|defeated|Neptune` -- the four "subdued and tied up Neptune": subduing is the stated outcome of the battle (defeated) and the tying up is the capture; one act, two true rows
- b3100: old `E Saitama|fought|Garou; F Saitama|wounded|Garou` -> new `E Saitama|defeated|Garou; F Saitama|wounded|Garou` -- the blow obliterates Garou's monster head, his monster form crumbles away and the talk turns to whether he should be left alive: the fight is over (wounded + defeated, one act per A145)
- b3167: old `E Tanktop Master|fought|Garou` -> new `E Tanktop Master|fought|Garou; E Garou|defeated|Tanktop Master` -- Tanktop Master intervenes against Garou and "the defeat of Mumen Rider and Tanktop Master" is stated; the Hero Hunter is the only opponent: fought + defeated
- b3268: old `E Mumen Rider|fought|Deep Sea King` -> new `E Mumen Rider|fought|Deep Sea King; E Deep Sea King|defeated|Mumen Rider` -- Mumen Rider "falls" in his futile attempt and has to be caught by Saitama; everyone who goes against the Sea King is stated to be defeated: fought + defeated
- b3292: old `E Metal Bat|fought|Junior Centipede; F Junior Centipede|wounded|-` -> new `E Metal Bat|fought|Junior Centipede; E Metal Bat|defeated|Junior Centipede; F Junior Centipede|wounded|-` -- after the fight Junior Centipede lies severely injured, praising Metal Bat, who is about to finish him: Metal Bat won the fight (defeated beside the stated fight)
- b3361: old `E Yoruichi|fought|Ichigo` -> new `E Yoruichi|fought|Ichigo; F Yoruichi|wounded|Ichigo` -- the claw slash across Ichigo's face makes him scream in pain (a stated injury by Yoruichi): wounded
- b3410: old `E Magneto|fought|Wolverine` -> new `E Magneto|fought|Wolverine; F Magneto|wounded|Wolverine` -- ripping all the Adamantium out of Wolverine is a stated injury (lost part of the body); his state after it is not stated, so no defeated
- b3432: old `E Count Nefaria|fought|Maya; F Maya|dies|-` -> new `E Count Nefaria|defeated|Maya; F Maya|dies|-` -- Nefaria's optic blast "seemingly killed" Echo and ends her part in the fight (Moon Knight attacks in revenge); the death is apparent (fact kept), the outcome is defeated, one act per A145
- b3471: old `E Toji|fought|Suguru` -> new `E Toji|fought|Suguru; F Toji|wounded|Suguru` -- Toji's longsword slices Suguru several times (a stated wound; the blood is described as the next window opens); the knockout comes after: wounded here
- b3476: old `E Sukuna|fought|Hana Kurusu` -> new `E Sukuna|fought|Hana Kurusu; F Sukuna|wounded|Hana Kurusu` -- Sukuna ripped off Hana's arm with Megumi's body (a lost limb, the injury Megumi takes responsibility for): wounded
- b3504: old `E Megumi|fought|Awasaka; E Yuji|fought|Awasaka; E Yuji|defeated|Awasaka` -> new `E Megumi|fought|Awasaka; E Yuji|fought|Awasaka; E Yuji|defeated|Awasaka; F Megumi|wounded|Awasaka; F Yuji|wounded|Awasaka` -- the passage states that both keep injuring Awasaka before Yuji defeats him: wounded for each doer (Yuji's defeated row stays)
- b3519: old `E Daido|defeated|Naoya Zenin` -> new `E Daido|fought|Naoya Zenin; F Daido|wounded|Naoya Zenin` -- slashed in half, Naoya's human form climbs out of the lower half and casts his Domain Expansion: the fight continues, so the cut is a wound, not a defeat
- b3608: old `E Guts|fought|Zodd; F Guts|wounded|Zodd; F Zodd|wounded|Guts` -> new `E Guts|fought|Zodd; E Zodd|defeated|Guts; F Guts|wounded|Zodd; F Zodd|wounded|Guts` -- completely outclassed, Guts is thrashed around and nearly crushed until Griffith and the Band intervene and take over: Guts is beaten (defeated beside the separately stated fight; the wound row stays)
- b3656: old `E Fu|fought|Cumber` -> new `E Fu|fought|Cumber; F Fu|wounded|Cumber` -- cutting off Cumber's tail is a stated injury (a lost body part) inside an exchange that is not stated to end: wounded
- b3744: old `E Logan|fought|Col Blooded` -> new `E Logan|fought|Col Blooded; F Logan|wounded|Col Blooded` -- Logan fights his way off by severely maiming several of the Col Blooded (a stated injury to the group, no member named): wounded

## Ambiguous: the owner decides (no fix block written)

- A_captured class (28 windows): fought + captured/sealed for the same pair with no defeated (b1113 b1156 b1168 b1295
  b1314 b1384 b1439 b1556 b1598 b1609 b1644 b1659 b1701 b1703 b1704 b1810 b1861 b2007 b2041 b2287 b2593 b3187 b3262
  b3281 b3520 b3524 b3771; b2957 was proposed because the text says "subdued and tied up"). The ruling says capturing /
  trapping is `defeated` "when the encounter ends there", but the standing convention is one act -> one event
  (ambush+kidnap -> captured; trapped in a domain/dimension -> sealed). Does a final capture/seal also carry
  `defeated`? Left unchanged pending a ruling; if yes, most of the 28 qualify (domain seals that the victim escapes,
  e.g. b1295 b1598 b1609 b1644, would not).
- Ally restraints: b529 (Himeno binds Aki to stop him using the Sword), b647 (Himeno's devil stops Aki), b3361
  (Yoruichi's slash leaves Ichigo motionless to stop him; wounded proposed, defeated not). Is a friend stopping a
  friend `defeated` (old "stopping a person = defeated") or not an outcome at all?
- Possession as an outcome: b1120, b1616 (Sukuna interrupts Megumi, forces the finger on him and takes his body).
  A116 says possession -> other_verb, no fought; the rows keep `Sukuna|fought|Megumi`. Defeated, or drop the fought?
- b768: `Denji|killed|Spear Hybrid` for "brutally bisected and cannibalized" -- a hybrid, death not stated (b707 has Whip
  telling Denji to spit him out). Killed or defeated?
- b2692: `Peter Quill|killed|Ego` for "Ego's corporeal form was destroyed" -- whether Ego survives is not stated.
- b1530: Mahito has crushed Yuji's body and goes for the kill when Todo swaps in; b1527 (same moment) holds
  `Mahito|defeated|Yuji`. Add defeated here too, or is the rescue a continuation?
- b1533: `Sukuna|defeated|Mahito` for "Sukuna stops him" (Mahito's soul touch is stopped, the Yuji-Mahito fight goes
  on). Kept under the old "stopping = defeated"; the new pause test would remove it.
- b1609: Nanami "accepts his defeat" inside Mahito's domain (sealed exists; Yuji breaks in later). Add defeated?
- b1310: Toji rips Playful Cloud from Maki, "lost in a battle of strength" -- a lost tug-of-war inside a fight that goes
  on. Defeated?
- b2027: Rictor is wounded in the First Horsemen's ambush and dies later in the Healing Gardens: `First Horsemen|killed|
  Rictor` as b348/b1351? The only quote naming the attack contains '|' (the "• --|A|-- •" name), so no legal quote.

## New patterns seen (for the catalog, not applied)

- Wound-then-collapse/out with nothing continuing in the window (b105, b1200, b1227, b1453, b1527, b1657, b1989, b2088,
  b2232, b2572): the Klaue pattern is common and was written as `fought` only.
- Group outcome sentences that name the members elsewhere in the window ("Makima and the four hybrids", "the Frightful
  Four were defeated", "the defeat of Mumen Rider and Tanktop Master", "the battle ultimately ended ... enabling Ronan to
  be defeated"): the fight rows exist per member but the outcome was never distributed (b652, b1827, b2778, b3167).
- `defeated` on a destroyed or cut-in-half body whose owner regenerates and fights on in the same window (b850, b3519)
  and on an incapacitation the text marks as only apparent (b1126): the reverse error.
- Death caused by a named doer's act but narrated passively ("sustains mortal wounds ... succumbs", "causing Ranta's eyes
  to bleed ... succumbed"): written as `fought` + `dies` (b348, b1351, b2027).
- Stated injuries kept only as `fought` or `other_verb` (tore/rip/impale/severed/harm) with no wounded row (b532, b717,
  b1035, b1322, b1357, b1596, b3476, b3656 ...).
- Knocked out by a crash or blast the doer caused (b1306, b2455): the knockout is the doer's outcome, not a no_doer state.
