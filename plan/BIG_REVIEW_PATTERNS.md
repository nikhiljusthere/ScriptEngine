# Big-window review: error and confirm patterns

> **OWNERSHIP (owner 2026-10-07): only Claude adds new rules, and only Claude edits this file and
> `tools/train/big_flags.py`.** The canonical make-and-verify method is `plan/WINDOW_METHOD.md`.

Companion to `plan/BIG_REVIEW_HANDOFF.md` (rulings R1-R25). Built from the corrections in
`series/universal/training/big/big_audit.jsonl` (b1-b131, 2026-10-07). `big_flags.py` turns
most of these into automatic FLAG / MISS? / DUP lines. **Flags are prompts, not verdicts: every
window is still read in full.** Measured on b7-b131: the row and window flags covered 113 of the
114 35B rows that had to change. MISS? cues fired in 62 of the 82 windows with a missed event,
and 13 of 98 rows marked OK still needed a change. Skipping full reads would therefore let
roughly one error in five through.

## A. Wrong-answer patterns (35B row -> correct answer)

| # | pattern (how it shows) | correct | rule | freq b7-b131 |
|---|---|---|---|---|
| A1 | missed event in a window that has other rows: rescues, escapes, "left the team", "found X", recruits, betrayal nouns ("Magik's betrayal"), attacks in passing ("having hurt Broo"), powers used on someone as an attack (mind control, possession and brainwashing are facts, not fought: A116, 2026-10-12) | add the row | step 8.1, R8, R18 | most windows (82/125 needed additions) |
| A2 | group end ("Avengers", "X-Men", "the group") when the window ties named members to the event | one row per tied member, no group row | G.2, R19 | very common |
| A3 | met from joining/allying ("joined the team", "joining X and Y", "teamed up", "allied", "rejoined", "united with the Runaways" b941) | no met; fact: `joined` (or `allied_with`), actual | R4, R12 | common |
| A4 | two names for one person in the window (codename + real name, alias pairs, disguise reveals "revealed to be", "posing as", "was really", "unmasked") | the real / revealed name in every row | step 6, R10 | common |
| A5 | crowd, indefinite or species end ("several Avengers", "former Avengers", "a Kree armada", "the police", "a Space Phantom", "Skrulls", "Inhumans", "Builders") | drop the row (or the named member if one is tied) | step 6, R11 | common |
| A6 | confrontation with no stated attack written as fought ("confronted Whirlwind", "confronted the robot Computo") | met | R2 | occasional |
| A7 | trapped in a dimension / other world written as captured ("imprisoned in Limbo", "ensnared in Mojoverse", "pocket universe", "forced through a portal") | sealed | R3, R13, R20 | occasional |
| A8 | passive with no doer filled from context ("where he was defeated", "were freed", "Moira being rescued", "arrested due to his connection to Orchis") | no row | step 4, R17 | occasional |
| A9 | rank/title or short form as the name ("Captain Stacy", "Dr. Ellis", "Shaw" when "Sebastian Shaw" is in the window, "Gaunt", "Burch", "the Reaper", "The Crippler") | strip rank; fullest form; no article | step 6 | occasional |
| A10 | description used as a place ("Reavers' Australian base", "the mansion" when unnamed) or heading as arrival ("while taking ... back to") | no arrived/departed | table: arrived | occasional |
| A11 | hedged or prevented acts ("seemingly slew" -> defeated, "attack ... was prevented" -> no fought, "nearly kill" -> fought) | per hedge | step 3 | occasional |
| A12 | "helped X when ..." written as saved | no saved; fact: `helped` (or `assisted`), actual | R23 | rare |
| A13 | leaving/disbanding written as betrayed ("abandoned him to die", "the Avengers were disassembled by") | no betrayed (departed if a named place); fact: `left_group` when a named person leaves a named group, else `other_verb` with the passage's verb | R14, R24 | rare |
| A14 | wrong pronoun referent ("he had captured a Space Phantom" = Kang, not Immortus; "before he escaped the police" = Castle) | re-resolve by meaning | step 4 | rare, only reading catches it |
| A15 | broken end string ("X" for Professor X) | the full name | step 6 | rare |
| A16 | "<group> led by X" as doer | X | R21 | rare |
| A17 | self-directed death (suicide) | no row (gate refuses subject==object) | R16 | rare |
| A18 | two characters sharing a name merged ("the Variant" / "Variant Loki" ambushes while the TVA's Loki sits with B-15) | separate ends ("Variant" vs "Loki") | step 6 | rare, reading only |
| A19 | purpose clause as event ("traveled to NYC to meet with X", "planning to fight") | only the part that happened (arrived), no met/fought; the purpose clause is a fact: `planned`/`claimed` with `asserted_by` when both ends are nameable | step 3 | occasional |
| A21 | killing through a possessed body ("used his powers of body possession to cause Dolan to murder Craft") / a victim who "survived his own murder" | possessor fought the host and the victim; no killed when he survived | step 4, 3 | rare |
| A22 | "finishing off X" with no stated death written as killed | defeated | table: defeated | rare |
| A23 | deals and exchanges as events ("agreed to help in exchange for teleporting them all back") | no row for the promised act; the promise itself is a fact: `planned`/`claimed` with `asserted_by` | step 3 | rare |
| A24 | a vehicle as a place ("carried Pixie to the Blackbird") | no arrived/departed | table: arrived NO "the car" | rare |
| A25 | a pantheon or race as an end ("the Kami", "the Olympians", "Sentinels", "Quantumnauts") | no row | step 6 | occasional |
| A26 | a reported confirmation misread for its speaker ("Gao confirmed that she had fought beside him ... before her death and later rebirth": she = Elektra) | re-resolve by meaning | step 4 | rare, reading only |
| A27 | the Watcher "visited"/"went to" a version of someone (What If narration = observing a universe) | no met | table: met NO watching | rare |
| A28 | "X had A and B abduct Z" written only for A and B | X captured Z too (the one who had it done) | table: captured | rare |
| A29 | "sedated him" / "knocked him out" written as fought | defeated | table: defeated | occasional |
| A30 | "terminating X" about a file/record (X alive later in the window) written as killed | no row | step 3 | rare |
| A31 | a self-assigned task as an event ("joined Daredevil's side and worked to stop Fisk") | no row (R4 + purpose); facts: `joined` (actual) plus the task as `planned`/`ordered` with `asserted_by` | step 3 | occasional |
| A32 | an abilities/powers section narrating specific hits ("shake off a punch from Gladiator", "has taken multiple punches from Namor") left empty | fought rows (step 1: one specific occurrence is an event) | step 1 | occasional |
| A33 | "X revived him" written only as awakened | also X saved him (revived someone who would otherwise die) — only when the revival is for his sake (Merlyn); a corpse revived as a tool or a threat (the Mad Thinker's "living weapon", Cable reviving Apocalypse) is no saved | table: saved | occasional |
| A48 | "joined" disambiguation: joining a team/side/cause ("joined the X-Men", "joined Daredevil's side") vs joining specific people where they are ("Sif joined Coulson and May when they traveled", "joined Namor at Utopia", "joined by an arriving Spider-Man") | team/side -> no met (R4); people where they are -> met; team/side -> fact `joined`; people where they are -> `met` event AND `joined` fact | R4, table: met | common |
| A34 | a team member's own team as "met" target after rescuing/arriving ("arrived in time to save Daisy and May") missed | met each person reached + saved | table: met | occasional |
| A35 | a purpose clause that the next clause fulfils ("traveled to Genosha to confront Magneto ... In the resulting battle", "runs to save him ... stopping them both from falling") left out | write it (met/fought, saved): the PURPOSE flag is a prompt, check the following sentence | step 3 | occasional |
| A36 | "defended by X" in words (X told the accuser he was wrong) written as saved | no row; fact: `warned` or `persuaded`, actual | table: saved | rare |
| A37 | escorting a prisoner ("in charge of taking Venom to a helicarrier cell") left out | captured (brought as a prisoner) | table: captured | rare |
| A38 | "disposed of by X" / "dispatched" with no stated death written as killed | defeated | table: defeated | rare |
| A39 | a company or weapon as the killer ("killed by a Stark Industries missile") | no row (an item is never the doer; its user is unnamed) | step 4 | rare |
| A40 | "jumped into action" against X written as met | fought (an attack made) | table: fought | rare |
| A41 | a plural referent resolved to the wrong people ("the two young heroes" = Johnny and Bobby Drake, not Doris who was also on the cruise) | re-resolve by meaning (heroes = the ones with powers) | step 4 | rare, flagged as a prompt |
| A42 | "the ship was attacked by X" written as X fought the people aboard | no fought (an attack on a vehicle/building only) | table: fought NO | rare |
| A43 | a reunion phrased as feeling ("delight at seeing his dearest friends once again") left out | met | table: met | occasional |
| A44 | "X turned on them" (allies of the moment, e.g. after teaming up) left out or only fought | betrayed + fought (table: betrayed YES "turned on") | table: betrayed | rare |
| A45 | arrivals the other side cannot perceive (Reyes invisible to Mackenzie and May) written as met | no met; met only those who see him ("could see him") | table: met | rare |
| A46 | a later "they" that includes someone already out of the scene ("Hammerhead shot him point-blank" then "They were ambushed" written for Slyde) | only those still present | step 4 | rare, reading only |
| A47 | "were tied to a post" / "chained" / "locked" with no captor written for the last attacker | no captured (R17, example 9) | step 4 | occasional |
| A49 | an unnamed attacker/kidnapper ("their mysterious kidnapper") revealed later in the window ("their real aggressor, the Stranger") left without rows | rows with the revealed name (R10) | R10 | rare |
| A50 | escaped with a place object although the window names the captor ("cut herself free" from Dreykov's operation, written as escaped Red Room Academy) | the captor is the object; the place only when no captor is named | table: escaped | occasional |
| A51 | "A, B and C attended a meeting at <named place>" left out | each arrived + met per pair (a meeting held between them) | table: met/arrived | rare |
| A52 | "an assailant", "a lesser demon", "an impostor" as ends | no row (indefinite) | step 6 | occasional |
| A53 | "used his powers to kill it" where "it" is a symbiote/armor/item on a host who appears alive later ("Virus was arrested") written as the host killed; also "Thor destroyed Ultron's first body" while his consciousness escapes (b966) | fought the host; a body destroyed with the character surviving -> defeated | step 4 | rare, reading only |
| A54 | breaking an agreement ("abandoned his covenant with her and Xavier") | betrayed (broke faith) — unlike plain leaving (A13), which is no betrayal | table: betrayed | rare |
| A55 | "the trio stopped Egghead" written as captured | defeated (the fight ended; no capture stated) | table: defeated | occasional |
| A56 | "had thrown Loki and Thor out of the Bifrost" left out | defeated (thrown off ends the fight, as "pushed him off the truck") | table: defeated | rare |
| A57 | descriptive crowd groups ("the squad", "the rest of the Guardians") as ends | the named members the window ties to the act, else no row | step 6, R11 | occasional |
| A58 | "if not for the intervention of X" against a plot (no attack stated) written as fought; "Iron Man stopped Attuma's plot" written as defeated (b978) | met (an encounter that stops him) | table: met "stops X" | rare |
| A59 | composite end strings ("Dark Phoenix / Cyclops (Scott Summers)") | the real name only ("Scott Summers") | step 6 | rare |
| A60 | "X had his men attack the house, and in the following explosion, Y got killed" written as X killed Y | no killed (an ordered killing; the table excludes the order-giver); fact: `ordered` + `asserted_by` (order-giver and intended victim) | table: killed NO | rare |
| A61 | "managed to escape with the help of X" flagged as R23 'helped' | saved stays (helping an escape from captivity is a release, as b21 Carol Danvers); R23 covers only help with non-danger | R23 | occasional |
| A62 | "grabs Pangan for protection" / shielding someone written as fought | saved | table: saved | rare |
| A63 | "Rawlins' soldiers" / "X's men" attacking (possessive group with a named head) left out or as a crowd | X fought the targets (as "Luke Cage's team" -> Luke Cage) | G.2, R21 | occasional |
| A64 | "X sent Y to attack Z" written with the sender as the doer | Y fought Z (the sender only ordered it); fact: the sender `ordered` + `asserted_by` | table: killed NO ordering | occasional |
| A65 | an organisation as a place ("returned to the FBI", "joined S.H.I.E.L.D.") | no arrived (not a proper-named place); fact: `member_of` (or `joined`) when a named person joins it | table: arrived | rare |
| A66 | "became a mole infiltrated in <team>" left out | betrayed the team (a mole breaks faith with the team she is in) | table: betrayed | rare |
| A67 | a remote appearance ("joined the podcast remotely and greeted host X", a call, a hologram) written as met | no met; fact: `contacted` and/or `greeted` | table: met NO phone/video | rare |
| A68 | "The latter two ..." resolved to the wrong pair (Dracula and Miles instead of the last two named, Brielle and Miles) | the last two named | step 4 | rare, reading only |
| A69 | "destroyed Nimrod's bodies ... prevented him from transferring his consciousness" written as defeated | killed (a named robot/AI destroyed) | table: killed | rare |
| A70 | "trapped in an impenetrable energy dome created by X" left out | X sealed the named ones trapped (a barrier); deactivating it = saved | table: sealed | rare |
| A71 | training sparring between allies ("tasked with training Scott Lang ... he punched van Dyne") written as fought | no row (practice, not a conflict); fact: `trained`/`mentored` — a real punch inside the lesson still gets its `fought` event | table: fought NO playful/friendly contact | rare |
| A72 | "turned on both A and B" where B was already his enemy written as betrayed B | betrayed only the ally (A) | table: betrayed | rare |
| A73 | a battle/war/incident name as an arrived place ("joins the Battle of Wakanda, arriving with Groot and Rocket", b850) | no arrived (an event is not a place); arrived only when the named place itself is stated | table: arrived | rare |
| A74 | "forced Mordo to retreat" / "repelled" / "drove X off" / "force Pilgrim to escape the scene" (b1002) left out (b858) | defeated (the fight ended with X beaten, as A55 "stopped"); plus X escaped the one who forced it | table: defeated | occasional |
| A75 | "restrained the demon from attacking her" written only as fought (b869) | fought the attacker AND saved the one protected (an intercepted attack) | table: saved | rare |
| A76 | "firing wildly, Bishop missed Cable, instead managing to hit Professor Xavier" written as fought Xavier (b925) | fought the intended target (an attack made); no row for the ally hit by accident | table: fought NO accidental | rare |
| A77 | a numbered name with its word stripped as a rank ("Agent 33" -> "33", b912) | the whole name ("Agent 33") | step 6 | rare |
| A78 | a time as a place ("Earth-691's 31st Century", b932) | arrived the proper place only ("Earth-691") | table: arrived | rare |
| A79 | "they made it out into the streets of Hala" (escaping within Hala) written as arrived Hala (b955) | no arrived (not a new place reached) | table: arrived | rare |
| A80 | "the Mole Man was restored to human form" / "he got his powers back" (b1021) / "the Techno-Troid hatched" (b1034) written as awakened (b940) | no row (a form he already had) | table: awakened NO | rare |
| A81 | "learning how to psychically defeat Ahab for good" written as defeated (b971) | no row (knowledge of how, not the act) | step 3 | rare |
| A82 | "Faustus grabbed Peggy, threatening to break her spine if Cap came closer" written only as fought (b1003) | captured too (a hostage taken) | table: captured "hostage" | rare |
| A83 | "manhandled them and knocked them all aside" during an encounter written as defeated (b1029) | fought (+ met for the encounter); defeated only when the fight ends | table: defeated NO | occasional |
| A84 | "defeated all his opponents. The Chameleon ran away" written as defeated the Chameleon (b1021) | the one who ran: escaped, not defeated | table: escaped | rare |
| A85 | "Gideon manipulated her into betraying her friends" written as Gideon betrayed Karma (b1042) | the one manipulated is the betrayer (object = the friends; none if unnamed); the manipulator gets no betrayed | table: betrayed | rare |
| A86 | "scientists ... restore a Sentinel robot" written as the scientists awakened (b1042) | the restored machine is the awakened one; the restorers get no awakened | table: awakened (machine reactivated) | rare |
| A87 | "Stick fought with the Defenders as Elektra easily bested them all" written as Stick fought the Defenders (b1131) | "fought with X" next to a common enemy = alongside X: rows against the enemy, none between allies | table: fought | occasional |
| A88 | fact `other_verb` whose object is a phrase or a name ("were vehemently hostilized by Senator Craddock", "Hive", "Malick") (b21, b132) | the passage's own verb word, literally in the quote ("hostilized", "told", "thanked") | B.3 | very common (fact layer) |
| A89 | an event written again as a fact (`helped`/`assisted` next to `saved`, `contacted`/`greeted` next to `met`, `attacked` next to `fought`, `other_verb captured/escaped`, `left_group` next to `departed`) (b4, b139) | the event row only; no twin fact row | B intro | very common (fact layer) |
| A90 | a composite end in a fact ("Fitz and Simmons", "Captain America and Captain Marvel", "Mojo and Spiral") (b34, b285) | one row per named part | A59, B.6 | common (fact layer) |
| A91 | `contacted` for talking in person ("Burrows told him", "Steve told him") (b204, b395) | `contacted` only for calls, messages and remote links; in person = the met event (or no row) | table: met NO phone | common (fact layer) |
| A92 | `joined` with a person as object ("Nadeem joined Daredevil", "Thanos joined Warlock") (b179, b39) | `allied_with` (joined is for a group/team/organisation) | B.2 | common (fact layer) |
| A93 | a reversed fact direction ("Brian trained Nightcrawler" for "received training by Nightcrawler", "Avengers recruited Warlock" for "recruited by Warlock", "Belova contacted Melina" for "contacted by Melina") (b264, b39, b333) | the doer of the passive "by X" is the subject | step 4 | common (fact layer) |
| A94 | a crowd or descriptive group as a fact end ("the team", "his cellmates", "the Russians", "anonymous hijackers", "a Variant of Wolverine") (b200, b244, b285) | no fact row; tag the sentence `crowd_end` | B.6, R11 | common (fact layer) |
| A95 | the person in "he said/she snapped" resolved to the nearest name ("He said that she did not make him take the drug" = Ducasse; "he insisted" = Mahoney) (b315, b399) | resolve by meaning (who speaks to whom) | step 4, A14 | occasional (fact layer) |
| A96 | an actual act marked `planned`/`attempted` because a purpose word sits near it ("decided to accept an offer" and did; "Thanos proposed"; "made the poor decision to hide out"; "staying to destroy the buildings", which were damaged) (b520, b544, b546, b539) | `actual`: only an act the passage says did not (yet) happen is planned/attempted | B.4 | common (fact layer) |
| A97 | `gave`/`handed` with the item as object ("Koenig gave S.H.I.E.L.D. Lanyard", "Cyclopes gave Trident", "T'Challa handed CIA") (b530, b572, b647) | `gave` takes the recipient ("Koenig gave Ward"); `handed` takes what was handed (the person/item), never the receiving body | B.2 | common (fact layer) |
| A98 | a facts row for a production/game/real-world note ("Captain America was added to Fortnite", "John Byrne designed a new costume", release dates per country) (b651, b678, b636) | no fact; tag `production` (release-date lists `list_header`) | B.7 | occasional (fact layer) |
| A99 | both directions of one kinship as two rows (`Ahura child_of Black Bolt` + `Black Bolt parent_of Ahura`) or alias direction reversed (`Otto alias_of Elliot Tolliver`, `Cal'syee alias_of Deathbird`, `Sentry real_name_of Bob`) (b679, b563, b595, b557) | one row; `alias_of` subject = the alias/codename, object = the real person | B.2 | common (fact layer) |
| A100 | an identity name kept beside the real name in facts (Dark Phoenix/Lightchilde/Darkchylde/Mysterio/"Ultron iteration"/"Professor X" next to Jean Grey/Illyana/Beck/Ultron/Xavier) (b521, b671, b639, b554, b560) | one name per person in every row (A4/A9), plus one `alias_of` row when the window states the alias | A4, A9 | common (fact layer) |
| A101 | a narration line with a named doer tagged `no_relation`/`deictic`/`no_doer`/`dialogue` instead of written as a fact ("Masaryk watches the news report", "Johnny believed it was too good to be true", "Stane tells Stark he is being naive", "Walker deduced ...") (b821-b900, very frequent on the v2-labelled windows b807+) | a fact row with the passage's own verb (`other_verb watches`); tags only when no nameable doer exists | B.3, SECTION C | very common (v2 labeller) |
| A102 | `left_group` twinned with a `betrayed`/`departed` event for the same defection ("Jade Dragon defected from China Force", "Venompool defecting") (b861, b726) | the event row only (A89) | B intro | common (fact layer) |
| A103 | a passive with "thanks to"/"by" read with the wrong doer ("the Frightful Four was defeated thanks to the combined efforts of the Fantastic Four" -> Frightful Four defeated Fantastic Four; "broken out of Seagate by Jackson Norriss" -> Slattery escaped Norriss) (b1456, b1461) | the "thanks to/by" party is the subject: Fantastic Four defeated Frightful Four; Norriss saved Slattery | A93, R17 | occasional |
| A104 | helping someone in a fight read as fighting them ("he helped the Korbinite and Skurge in a bar fight" -> Pip fought Beta Ray Bill) (b1518) | helped/allied_with only; a fought row needs a named opponent | R2 | occasional |
| A105 | `wounded` with a body part or "injury" as object, or subject == object ("Cable wounded bicep/ear/hip bone", "Gamora wounded Gamora", "Torch wounded Hulk" for the Torch's own injuries) (b1488, b1479, b1545) | `victim|wounded|-` (or attacker->victim); one row for a list of old injuries | A90 | common (fact layer) |
| A106 | waking from sleep/dream/machine labelled `awakened` ("Strange was awoken by Morbius' nightmare", "Fitz and Simmons awoke in the Cerebral Fusion Machine") (b1453, b1490) | no event for ordinary sleep, a dream or a machine session; `awakened` is a return from death or stasis AND regaining consciousness (coma, knockout, blackout, tranquilizer: procedure B.1 "woke up, regained consciousness") — the 2026-10-12 audit restored 36 rows reviewers had removed by over-reading this row | R-verbs | occasional |
| A107 | events from implanted memories, dreams, fantasy sequences or an impostor read as real ("implanted with new memories that they had received injuries during their escape" -> escaped/wounded; "defeat Deadpool in a fantasy fight"; the Skrull "Phoenix" dying as Jean Grey) (b1834, b1566, b1573) | no event or fact for the person; the impostor gets the row under its own name or a `no_doer` tag | R10 | occasional |
| A108 | `ordered` with a noun/gerund/clause as object ("ordered imprisonment", "ordered burn the village down", "ordered passage to the Dark Gate", "Sitwell ordered Triskelion/Quinjet") (b1505, b1748, b1783) | `ordered` takes the PERSON told to act; otherwise `other_verb` with the passage's verb ("authorized", "demanded") | B.3 | common (fact layer) |
| A109 | heading toward a place read as arrival ("On his way back to America", "As they flew to the Cybertek Manufacturing Facility") (b1728, b1758) | no `arrived` row until the passage says they got there | step 3 | occasional |
| A110 | the PATIENT of a doer-less passive, or a non-agent thing, written as the subject ("Luke was hurled into the Bronx" -> Luke|other_verb|hurled; "J.A.R.V.I.S. had been reprogrammed"; "Love, the resurrected daughter"; "The incident traumatized May"; "Category 8 hurricane destroyed Haven Hills"; "radio circuitry alerted him") (b2335, b2366, b2338, b2324, b2383, b2406) | the doer from "by X" (A93/A103); with no named agent, no row (a `no_doer` tag) | A93 | common (fact layer) |
| A111 | an infinitive or relative clause pinned on the wrong actor: the object of an earlier verb, the speaker, or the loser ("Talbot was not in position... so he would now... destroy S.H.I.E.L.D." -> Talbot|destroy, it is Ward; "at the behest of Professor X to monitor" -> Professor X|monitor; "Hope, who was trying to kill Bishop" -> Bishop|attacked|Hope; "Ronan, who was forced to flee after losing the battle" -> Ronan|defeated|FF) (b2393, b2400, b2635, b2627) | find the grammatical subject of that verb; the one who loses/flees is the object of `defeated` | step 3 | common |
| A112 | a codename or "her father" resolved to a real name the window never gives ("Ant-Man and the Wasp" in a 1963 story -> Scott Lang / Janet van Dyne; "the Hulk" -> Bruce Banner; "her father" -> Scott Lang; "Kate's father" -> named) (b2750, b2551, b2579) | keep the name the window uses (Ant-Man, Wasp, Hulk); an unnamed relative stays a tag (A20) | step 6 | occasional |
| A113 | an episode known only from a character's later claim or recounting written as events ("Spider-Man has since claimed that he battled the Hulk ... he was rescued by Captain America" -> saved/defeated rows; "Allegedly Chthon guided Marie Laveau") (b3339, b3249) | no event; a fact with `claimed`, `reported` and the claimant as asserted_by | A107 | occasional |
| A114 | capability wording in a powers section written as an event ("enough to overpower even Thor and Vision", "capable of trading blows with Juggernaut") (b3267, b3164) | no row (a `capability` tag); only a narrated occurrence ("Ultron punched Thor hard enough to make him bleed") is an event | step 1 | occasional |
| A115 | `revealed`/`learned`/`discovered` with the listener or a clause as the object ("Wilkes revealed Carter" for "revealed that Frost wanted a bomb"; "Moira revealed Xavier"; "Harry discovered Spider-Man's secret identity"; "Rogue learned government agent") (b3836, b3731, b3371, b3675) | object `-` (`revealed|-`, `learned|-`); a named object only when that named thing is what is revealed or found | B.3 | common (fact layer) |
| A116 | possession or mind control written as `fought` ("Fisk was possessed by the entity of Greed" -> Greed|fought|Fisk; "the Demon God, which possessed Xaltana" -> fought) (b3218, b3323, b3517) | fact `other_verb|possessed` with the possessor as subject; `fought` only for a stated attack | R2 | occasional |
| A117 | breaking someone OUT of jail/prison/a cell written as a `helped` fact or left out ("Toomes then proceeded to break Drago out of jail" -> Toomes|helped|Drago, b3981); "Hammer had previously arranged the escape of Vanko" left out, b4004) | `saved` event (a release from imprisonment, whoever the prisoner is); the one who breaks out alone gets `escaped` only when a captor or named place is stated, else `other_verb broke` | table: saved | occasional |
| A118 | a telepathic interruption, message or link written as `fought` ("He was interrupted telepathically by Xavier, who informed Franklin of the discovery" -> Xavier|fought|Franklin, b4018) | no event; fact `contacted` (a remote link) plus `revealed|-` for what was told; `fought` only for a mental ATTACK (a blast, a probe, an assault) | table: fought / met NO phone | rare |
| A119 | defeating an illusion, projection, drone swarm or construct written as defeating the one who controls it ("order all the projector drones to self-destruct, thereby defeating the so-called Elemental" -> Peter|defeated|Beck, b4046) | no `defeated` for the controller (fought stays if he is attacked); a named robot/AI body counts as the character itself (A53/A69) | table: defeated | rare |
| A120 | a passive whose "by" names a POWER or ATTACK of a named character ("killed by Thanos' Snap", "struck down by Thor's lightning") tagged `no_doer` like an item (A39) (b4064) | the owner of the power is the doer (Thanos|killed|Yelena Belova); A39 stays for an item, company or weapon whose user is unnamed | step 4 | occasional |
| A121 | `sealed` with the PLACE as object ("Warlock banished the Magus into Soul World" -> Warlock|sealed|Soul World, b4097) | the one sealed away is the object (Warlock|sealed|Magus); the place goes nowhere in the event (an `arrived` only if the window says the sealed one reached it) | table: sealed | rare |
| A122 | a specific narrated occurrence in an abilities/powers/equipment section tagged `capability` ("Toomes was able to plan and execute the Attack on the Damage Control truck", "Rogers played ... Captain America in live shows", "Kahhori sprinted to her village") (b4184, b3990, b4083) | the event (A32) or an `other_verb` fact with the doer; `capability` only for general ability wording ("can", "is able to", no specific occasion) | A32, SECTION C | common (fact layer) |
| A123 | a comma place written as TWO movement rows ("went to Cairo, Egypt" -> arrived Cairo + arrived Egypt; "surfaced in Newell, California") (b4314, b4326, b4137) | one row with the most specific named place (R1); the gate splits a merged string, so the 35B splits it too | R1 | common |
| A124 | a staged or mock battle labelled `fought` ("Johnny joined the Thing, Medusa and Thundra in a staged battle against the rehabilitated Namor", "these was merely a mock battle that was staged") (b4652, b4661) | no fought/defeated rows; an other_verb fact for the participants (fantasy and illusion fights are no events either) | R-verbs | occasional |
| A125 | other_verb object is a copula/modal or a proper noun lifted from the quote ("Medusa|other_verb|was", "total|other_verb|should", "Amy Minoru|other_verb|Wizard" from "Wizard Computers") (b5249, b5334, b5094, b5119) | the quote's real verb (hacked, absorbed); nothing done -> no_relation tag (fact_gate flags it) | B.3 | frequent |
| A126 | `transformed_into` with the transformer as subject or a description as object ("Odin|transformed_into|Loki", "Arachne|...|creature with a spider body", "Steve Rogers|...|Captain America") (b5047, b5134, b5137, b5146) | transformer -> other_verb; first new form -> `awakened`; named alter ego -> `alias_of`; a described form ("steel form", "being of solid sound") is a legal object; judged by hand, no flag (a flag was measured and withdrawn) | R-verbs, A99 | frequent |
| A127 | "the two teams fought" expanded as a cross product with the wrong sides (Hawkeye given fights against his own teammates) (b5044) | pair only opponents the window sets against each other | G.2 | occasional |
| A128 | (withdrawn 2026-10-12 after measurement) "X insisted/told/promised that ..." written as claimed/planned + asserted_by is the procedure's claim row (B.4), not an error: 190 hits on approved windows were legitimate claims | keep claimed rows; actual only when the row states the act itself, not its content | B.4 | n/a |
| A129 | infobox lines that narrate events tagged list_header only (CauseOfDeath "Killed by ...", "(while possessed by Varnae)", "homeschooled by Jamal Afari") (b4821, b4840) | rows for the narrated acts (killed, awakened/saved, possessed fact); the tag stays on the field name | B.1 | occasional |
| A130 | the page-title name written for a window that uses another name ("Harvey Elder" for "Mole Man", "Bentley Wittman" for "the Wizard") (b4820, b4839, b4868) | the window's own name (A112 extended to page titles) | step 6 | occasional |
| A131 | non-agent subjects: spell, curse, hologram, computer, elevator, war, city, country ("The spell allowed", "Computer contacted Fury") (b4814, b4841, b4852, b4879) | the named user/caster as subject, else a no_doer tag (flagged; A110) | A110 | frequent |
| A132 | "found / tracked / spotted X in <place>" labelled `arrived` (b5179, b5284, b5326) | `located_at` the place (+ `met` for the finder); no arrival unless the window says they got there | R-verbs, A109 | occasional |
| A133 | knowledge relations with a clause or snake_case object ("Reed|discovered|creature_power_source", "Rocket|suspected|being released") (b5262, b5284, b5314) | `learned|-` / `revealed|-`, or other_verb with the quote's verb (flagged; A115) | A115 | frequent |
| A134 | other_verb object is the attempt word itself ("Thor|other_verb|attempted" for "attempted to keep peace", "Mephisto|other_verb|tried") (b5761, b5819, b5845) | object = the verb tried (keep, kill, escape) with modality attempted; "an attempt on X's life" with no verb stays (flagged; measured 80/92 approved rows) | A125 | frequent |
| A135 | an unconscious, frozen or dead body that is "found" or "happened upon" written as met ("Namor and the Avengers met Captain America" while he was still frozen) (b5755, b5835) | no met (only one party is present); keep the saved / awakened rows | R2 | occasional |
| A136 | doer and receiver swapped on recruited / helped / tricked ("Air-Walker|recruited|Galactus", "Bobby|helped|Romeo" when Romeo rescued Bobby, "Ultron|tricked|Yellowjacket") (b6231, b6271, b6375, b6396, b6420) | subject = the one who recruits / helps / tricks, object = the one recruited / helped / tricked | A103 | common (fact layer) |
| A137 | joining someone for one trip, clash or infiltration written as membership ("Peter Parker|joined|Fantastic Four" for a camping trip, "Lyja|member_of|Fantastic Four" for an infiltration) (b6366, b6408, b6411, b6413, b6737, b6748) | no joined / member_of; allied_with for a shared fight, nothing for a trip | R4 | common (fact layer) |
| A138 | a sent / returned object, or the sender, written as the arriver ("the Watcher returned the group to Earth" as Watcher|arrived|Earth, "Mjolnir|arrived|Earth") (b6302, b6307, b6425) | the one carried arrives; a thing is no arriver (A131); the sender gets no arrived row | A131 | occasional |
| A139 | `transformed_into` for a return to a form the person already had ("reverted to human form", "settling back into his classic Thing form") (b6473, b6481, b6482, b6487, b6607) | no transformed_into; other_verb reverted, or nothing | A80 | common (fact layer) |
| A140 | `gained_power` with a null object for regained powers or ability prose ("regain his lost powers", "gained the following abilities") (b6428, b6476, b6499, b6533, b6544, b6610, b6619) | name the new power when a first one is gained; otherwise no row | B.2 | common (fact layer) |
| A141 | a page subject's name given to another character on that page (Sleeper's acts as "Eddie Brock"; "Carnage" = Norman vs "Dark Carnage" = Kasady) (b6438, b6455, b6522) | the actor named in the sentence; never the page subject by default | A130 | occasional |
| A142 | plural asserted_by ("Kitty, Storm, and Marvel Girl", "Gwen and MJ") (b6557, b6577, b6596) | one row per asserter | B.4 | occasional |
| A143 | a title, reign name or spelling variant written as `became` ("Karl Haasen\|became\|Baron Karl Hassen", "Rudolfo Haasen\|became\|Rudolfo I", "Vladimir\|became\|king") (b7302, b7316, b7327) | `leader_of` the realm for a reign, `alias_of` for a codename, otherwise no row; `became` is for a new state or form only | A126 | occasional |
| A144 | two acts told side by side, one given to the other's subject ("Cyclops' optic blast" as Dracula\|defeated\|Blade; "Werner had Boris promise" as Werner promised; Captain America\|disguise_as\|Yellowjacket when Teddy posed as him in Cap's plan) (b7280, b7282, b7288, b7323, b7326, b6912, b6913) | each act to its own grammatical subject; the planner of an impersonation gets no disguise_as | A111 | occasional |
| A145 | one stated act written as several events ("overthrew the King, killing him" -> fought + defeated + killed; group-vs-group fights next to the named leaders' rows) (b7323, b7315, b7324) | the most specific verb only (`killed` over `defeated`); `fought` too only when the fight is stated separately (procedure step 5); no group rows when members are tied (A2) | step 5, A2 | occasional |
| A146 | a death written as `other_verb died/perished` ("Zuras\|other_verb\|died", Makkari's death missing) (b7163, b7167, b7172) | `dies\|-` (actual); a feared or hypothetical death stays other_verb with its modality (measured 2026-10-13: 40 of 52 raw rows removed by review, the 12 kept were mostly "would die"; no flag, no auto-repair) | B.2 | occasional |
| A147 | a revival written as `X\|other_verb\|resurrected` with the revived person as subject, or as the reviver "saving" (b7116, b7169, b7176) | `awakened` for the revived; `saved` too when a named reviver does it for the person's sake (A33) | A33 | occasional |
| A148 | a nickname for a group or a description filed as an alias ("Cletus\|also_known_as\|Axis of Evil" for "dubbing them the 'Axis of Evil'"; "Mother\|alias_of\|interdimensional parasite") (b6973, b6932) | `alias_of` only for a name a person goes by; a dubbing is `other_verb dubbing`; a description is no alias | A99, A100 | rare |
| A149 | `revealed_as` with a description subject, the wrong person, or for a disguise unmasked ("witch\|revealed_as\|Baba Yaga", "Billy\|revealed_as\|physical manifestation of the Demiurge", "Teddy\|revealed_as\|Morgan Le Fay") (b6916, b6917, b6922) | subject = the name shown before, object = the true identity, both named; a disguise is `disguise_as` from the impostor's side | A4, A99 | occasional |
| A150 | a portal, gem or realm boundary as an arrival or escape end ("arrived Siege Perilous", "Cletus\|escaped\|regular universe" for "escape to the regular universe") (b6943, b6969) | `arrived` only at a named place reached; `escaped` takes the captor or place left, never the destination | A24, A50 | rare |
| A151 | "In <place>, X did Y" or "X was next seen in <place>" written as `arrived` (Rome, Tarnington, India, Timbuktu) (b7545, b7567, b7572) | `located_at` the place; `arrived` only when the passage says X went or came there (A109, A132) | A132 | occasional |
| A152 | a list entry that names a duplicate or variant after another hero ("Deadpool - One of a group of dupes", "Hulk - ...") written with the bare famous name, so its acts land on that hero (b8068, b8069) | the page's own entry form ("Deadpool Dupe", "Hulk Dupe", as "Bartender Dupe"); never the bare name of the other hero | A18, A141 | rare |
| A153 | a person whose name is also a wiki place page refused or dropped as a place ("CIA agents China and Barrett", "Lord Carteret", "Carol Danvers") (b8137, b8141) | the person: the event gate now spares a name the window introduces with a first name, title or "agents" | R22, step 6 | rare |
| A154 | a rivalry or contest phrased with a fight verb ("the teenage Prime and Prototype fought over who could form a better group, and who could do it first") written as `fought` (b9403, b9409) | no event (no attack is stated); fact `rival_of` (or `other_verb` with the passage's verb); `fought` only when a blow, shot or power is used on the other | R2, A6 | rare |
| A155 | a future, older or legacy holder of a title resolved to the title's best-known holder ("the future Captain America" -> Steve Rogers in a window that says Steve Rogers is dead and that the man "has the same eyes" as Bucky; Jeff Mace "replacement" of Nasland written as a Bucky; a Bucky-era "Barnes ... to pose as Bucky") (b9535, b9545, b9531) | the window's own name for that person ("Captain America"), or the named holder the sentence ties to the mantle (`Captain America\|alias_of\|Jeff Mace`); never the famous holder by outside knowledge | A112, A143 | occasional |
| A20 | an unnamed relative resolved to a named one by outside knowledge ("saved by her father" -> Paxton, who is the stepfather) | the definite description ("Lang's father") | step 4/6 | rare, reading only |

> **FACT-LAYER ROUTES (2026-10-08, owner-authorised council).** When a ruling here says "no row",
> it means no **event** row. The sentence is still covered by v2: a `facts` row when both ends
> are nameable, otherwise a `tags` row from this closed set —
> `no_doer` (A8, A39, A47: passive with no 'by', item as doer, tied with no captor),
> `crowd_end` (A5, A25, A52, A57: crowd/species/indefinite/descriptive-group ends),
> `no_relation` (A17, A27, A30, A42, A45: stated, but no legal event AND no legal fact).
> An event-layer flag never justifies deleting a fact or tag row.

## B. Confirm patterns (35B usually right; one look suffices)

- quote literally states subject-verb-object: "Stark defeated Bullski", "Thanos kidnapped Nebula and Starfox" (OK lines in big_flags)
- "Back to <named place>" / "returned to <named place>" -> arrived
- "found X" / "was greeted by X" / "visited X" / "reunited with X" -> met
- "attacked by X" / "battled X" -> X fought the object
- "X was murdered by Y" / "Y slew X" -> killed
- lists, credits, trivia, dialogue windows -> empty (still skim for one narrated occurrence)
- **The commonest residual error on OK rows is A4 (alias / disguise names) and A2 (group expansion).** Check those two even on OK rows.

## C. Exact duplicates

The same text appears on several sections/pages (b8=b23, b2=b33, b62=b88), or cut at another offset
(b365 = b188's tail). big_flags prints `DUP of bK` (same opening) or `OVERLAP with bK (n/m sentences
shared)` with bK's final rows: reuse them for the shared part and read only the rest.
`tools/train/big_consistency.py` checks every reviewed overlapping pair for diverging rows
(b1-b371: 4 pairs, 0 inconsistent); run it before composing the training set.

## D. Gate quirks

- symmetric met/fought pairs are deduped by the gate; a correction with both "A met B" and
  "B met A" is refused with `dropped []` and `kept n-1/n`.
- "Rachel" and "Jude" are classed as places: refused as objects (R22).
- "Zemo" is classed as an episode page: every Zemo row is refused (both ends).
- "Donovan" is classed as a music page: refused as an end (b880).
- a place name containing "and" ("El Monte Junk and Salvage") is split by the gate like a comma place (refused as `kept n+1/n`); keep the first named part and drop the fragment (b1080).
- "the Other" (Chthon's demon) is refused as a class word ("Other"); no legal row (b1133).
- item pages are refused as ends even when they act like characters: "the Destroyer" (armor), Cerebro (AI).
- subject == object is refused (R16).
- a place with a comma ("Washington, D.C.") is split by the gate into two rows (refused as `kept n+1/n`);
  write the most specific part ("Washington", R1).

## E. Resume notes (2026-10-07 01:59)

- Cursor: see series/universal/training/big/review_cursor.txt (the live value; b7-b431+ reviewed 2026-10-07).
- Rulings R24/R25 (not yet in the handoff): "abandoned him to die" -> no betrayed; "<person> posing as <hero>"
  -> the impostor's name; "found themselves transported to <place> by X" -> X captured them + they arrived.
- Loop: `SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine python tools/train/big_flags.py 15` (from this worktree),
  write compact edits, `python tools/train/big_mkfix.py edits.txt bfix.json`, then
  `/home/goblin/ScriptEngine/tools/train/big_review.py --fix bfix.json` and `--mark N`.

## F. Labeler recipe change (2026-10-07 ~04:50) — the 35B now gets these patterns

The owner asked to give the 35B the flagger and this catalog, not as a prompt dump. Done as:
- `--hints` (tools/train/label_hints.py): at most 5 one-line reminders whose trigger words occur in the
  window (mean 2.6; none on 13%), appended to the user turn; the procedure doc stays the cached prefix.
- `--repair`: big_flags.check() runs on the gated rows; only when flags fire, ONE follow-up turn lists
  them (max 8) and asks for the complete corrected JSON (fires on ~36% of windows).
- Measured on 96 hand-reviewed windows (eval_hints.py; gold = final reviewed rows), same server:
  base P .694 R .436 F1 .535 exact 38 | hints .707/.503/.588 37 | hints+repair .769/.532/.629 44.
  hints+repair vs base: +.093 F1, paired bootstrap 95% [-.008, +.196].
- The runner was paused (owner-approved, PID 471097 stopped at 5,206 labeled) and restarted with
  `--hints --repair` at ~04:48: PID 512679, launched from this worktree with
  SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine (gate modules + data from the main checkout, so the
  gate is unchanged). Rows written from then on carry `"hinted": true`, `repair_note`, `first_rows`;
  the first 5,206 rows are the plain recipe (mixed provenance; every window is still reviewed).
- If the runner dies, resume with the same flags from this branch (label_single.py here has
  --hints/--repair; the main checkout's copy does not):
    cd .claude/worktrees/big-review-flags && SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine \
    setsid nohup /home/goblin/ScriptEngine/scriptengine/.venv/bin/python tools/train/label_single.py \
      --in $R/series/marvel/training/labels/big_in.jsonl --in $R/series/mcu/training/labels/big_in.jsonl \
      --out $R/series/universal/training/big/labels.jsonl --workers 8 --shuffle --hints --repair \
      >> $R/series/universal/training/big/label_run.log 2>&1 < /dev/null &      (R=/home/goblin/ScriptEngine)

## G. Fact-layer gate quirks (big_review_v2, 2026-10-10) — fact_gate._end_ok bugs to fix in one tested change
- "President of the United States" is stripped as a rank prefix and refused (b4).
- "Guardians of the Galaxy" is refused as a crowd end (the crowd regex matches inside the name; b16).
- "Beast" is refused as a species/race end (b17).
FIXED 2026-10-10 in fact_gate.py (crowd 'of the' only after a quantity word; Beast removed from SPECIES; RANK skips 'X of ...'); 54 fact tests pass. b4/b16/b17 were submitted with the tag workaround before the fix.
FIXED 2026-10-10: "She-Hulk" (b1029) and "He Who Remains" (b1286) were refused as pronouns.
OPEN: "King Arthur" is stripped as a rank prefix in facts (the event layer keeps it; b921).
OPEN: "Agent Venom" (a codename) is stripped as a rank prefix and refused (b726); dropped.
OPEN: "The Others" (a cult's proper name) is refused as a crowd end (R11 crowd word "others"; b573) — sentence tagged `no_relation` as a workaround.
OPEN: the event gate splits "Washington, D.C." into two places (Washington / D.C.) so a merged `arrived` row is refused as "kept 4/3" (b1445); the split rows were left in place.
OPEN: "MJ" is refused as too short to be a name (b1407); the row was dropped.
OPEN: the A101 flag still fires on passives with a named patient and no doer ("Slattery was arrested", "Morbius was fooled by a demon", "Hill had her injuries treated") — those `no_doer` tags are correct.
OPEN: "Lady Torch" is stripped as a rank prefix in facts (b1549); "Destroyer" alone resolves to an item page so "The Destroyer" keeps its article (b1761); "Curse", "Demon" and "Inhumans" are refused as class/race ends (b1632, b1805, b1668).
OPEN: the event gate splits any place name with " and " or ", " ("Land Between Night and Day", b2001; "Washington, D.C.", b1445) and refuses the merged row as "kept 3/2".
OPEN: "guard" as an other_verb object is refused as a crowd word (b2010); a different literal verb was used.
OPEN: the edit-file parser splits on "|", so an infobox quote like "{{m|Champions}} (Leader)" cannot be sent; quote the part after the pipe ("Champions}} (Leader)", b2495).
OPEN: "Rachel" resolves to a place page ("place 'Rachel' as the object of killed", b2612); "Him" (the Enclave's creation) is refused as a bare pronoun (b2627); "King Arthur" is refused as a rank prefix in facts (b2470). The rows were dropped or rewritten with the stripped name.
OPEN: races are refused as `created` objects too ("Celestials created Deviants/Eternals", b2419); the capability tags were kept.
OPEN: "Karolina" alone resolves to a music page (b2789, b2785); rows with it were dropped.
OPEN: "Jude" as an end resolves to a place (b3420: Amanda|killed|Jude refused); write `Jude|dies|-` instead.
OPEN: "King Cobra" is refused as a rank-prefixed name (b3878); the gate strips "King" though it is part of the codename.
FIXED 2026-10-12 in big_review_v2.normalize_facts: a company/institution name with "and" ("Republic Oil and Gas Company", b3972) was split into two ends; names ending in Company/Corporation/Industries/Inc/Institute/... stay whole.
OPEN: "Gao" alone resolves to a place ("place 'Gao' as the object of fought", b4013); the page name "Madame Gao" passes.
OPEN: a surname that is a quantity word is refused as a crowd end ("Jennifer Many", b4082); the sentence was tagged no_relation.
OPEN: "US" is refused as too short to be a name (b4105), like "MJ" (b1407); the US declaration sentence stays covered by the Germany row.
FIXED 2026-10-12: a firm named after partners ("the law firm Landman and Zack", b4195) is no longer split when the quote says firm/company/corporation.
OPEN: "Taloa" resolves to an episode page ("end is a episode page", b4255); her met row is refused, the visit is an other_verb fact.
OPEN: "Captain U.K." is stripped as a rank prefix in facts (b4286), like King Cobra / Agent Venom / Lady Torch; the sentence was tagged no_relation.
NOTE 2026-10-12: a wiki-resolution exception for rank-prefixed codenames does NOT work: "General Ross" resolves exactly like "King Cobra"/"Captain U.K."/"Agent Venom"; a fix needs an explicit codename allow-list (fact_gate.RANK lookahead, like Deathstrike/Mastermind).
FIXED 2026-10-12 in fact_gate.RANK: codenames King Cobra, Captain U.K., Agent Venom, Lady Torch, King Arthur, Captain Hydra are no longer stripped as rank prefixes (explicit allow-list; General Ross / Agent Coulson still are). 64 fact tests pass.
FIXED 2026-10-12 in fact_gate.RANK: numbered names ("Agent 33", "Agent 13") keep their word (A77), as the event layer does.
FLAGS 2026-10-12: big_flags now flags A116 (mind control/possession/hypnosis written as fought) and A106 (waking from sleep/a dream/a trance written as awakened) for the repair turn; both were still common in b4400-b4526.

GATE AUDIT 2026-10-12 (owner: "some rules could be legit and you are missing facts/events"): every row
the gates ever dropped over all 14,000 windows was re-counted. Fixed in fact_gate/label_single:
normalise() repairs shape instead of dropping (201 `died` deaths -> dies; ~690 plans with no asserted_by
-> the subject; certainty words in the modality slot; rank prefix stripped, not refused);
split_event_facts() moves event-verb facts into events; codename allow-list (Captain Carter, Lord Dark
Wind, Lady Lotus, Queen Goblin, Doctor Sun, Lord Chaos, King in Black...); "The Thing"/"The Other";
names the window uses mid-sentence pass crowd/pronoun/length rules (Him, Former Thrall, MJ, Li, Po);
other_verb objects skip name rules ("go"); music/episode/item pages no longer refuse event ends
(Karolina, Zemo, Miss Minutes, K.E.V.I.N., Destroyer); a place page refuses an object only with no
character namesake (Madame Gao, Lincoln Campbell). The review view printed `fact_dropped`/`tag_dropped`
but the labeller writes `dropped_facts`/`dropped_tags`: dropped facts were never shown -- fixed.
Still refused by design: races/species (R11/A25), countries as fight ends, unnamed crowds, escapes
with no pursuer (needs an object). Recovery of the dropped rows: tmp recover.py (base rows for
unviewed windows; viewed windows listed in big/recovered_reviewed.jsonl for a hand pass).

- 2026-10-12 A101 flag: a leading participle phrase ("Having his memories erased, Nightcrawler returned",
  "Mastering genetics, they…") was reported as the doer. The flag now matches the doer after the phrase's
  comma (15/281 approved hits were affected; the real doer is reported, phrase-only lines no longer flag).
- 2026-10-12 event gate: draft_v2.CLASS_WORDS is case-insensitive, so names spelled like class words
  ("known only as Him", "The Other", "the Guard", "The Allies") were refused as unnamed ends. label_single
  now overrides it: a capitalised class word the window uses mid-sentence, or "The <Capital>", passes;
  "He" opening a sentence and "The two" stay refused (measured: 13 of 16 refused capitalised class ends
  were names). The main checkout's draft_v2 is untouched.

2026-10-13 (b6847-b7426: gaps closed by reviewers J/K/L/M, coordinator b7087-7106 + b7347-7426; cursor 7426):
- FIXED fact_gate.RANK: "Empress Brood" / "Queen Brood" were stripped to the race word "Brood" and refused (b7136;
  2 refused rows over all 14,000 windows, both the character); `Brood` joins the codename allow-list.
- FLAG widened (A125): an other_verb object that is an adverb ("gravely", "increasingly"), a determiner/adjective
  ("some", "certain", "similar") or a possessive ("Coulson's") is flagged. Measured on 7,503 approved windows:
  7 raw 35B hits in reviewed windows, all 7 removed by review; 1 left in an approved row (b139 "certain").
- FIXED (was OPEN, below): quotes are repaired to the window's exact substring when they differ only in whitespace
  (big_review_v2.exact_quote, label_single._exact_quote, all three gates). Measured: 45 of the 629 historical
  "not verbatim" drops pass (7 events, 16 facts, 22 tags); the other 584 are paraphrases and stay refused. b8083.
- (superseded) OPEN: a non-breaking space in the window text makes a typed quote fail the verbatim check (b6933 "sons of the
  Scarlet Witch"). Measured: 24 of 14,000 windows contain one; 21 rows (9 facts, 5 tags, 7 events) were dropped for
  that reason alone. Left as is (a whitespace-tolerant check would change every downstream quote lookup); a
  reviewer quotes the part without the space.
- OPEN by design: "the Asgardian" as Billy Kaplan's codename is refused as a race end (b6919); the alias row was dropped.
- NOTE: "Nur" ("the alien race, the Nur", b7143) passes the event gate as a fight end; the race list cannot know
  every race, so races are removed by hand (A25).
- NOTE (A130/A141): on the Nova page the 35B wrote "Richard Rider" in windows that only say "Nova"/"Rider"
  (b7109-b7124); a group led by a named head ("B'rute's hive", "the forces of Apocalypse", "Phraug's Deviants",
  b7144/b7147/b7157) was tagged crowd_end instead of acting through the head (R21/A63).
- NOTE (A53): a vampire "destroyed" and revived later in the window is `defeated`, not `killed` (b7573, b7580).
- FIXED big_review_v2 view: it printed only the first 4000 characters of a window (b7569 reviewer). 4 of 14,000
  windows are longer; the two already reviewed (b4531 credits list, b6909 infobox relatives) had no narrated
  row past the cut. The view now prints the whole window.
- FIXED build_prompt.py: SECTION F cut every rule at its first pipe (an inline row "Medusa|other_verb|was",
  `victim|wounded|-`, or an escaped \|), so the 35B was served half-rules (A105, A125, A134, A136...). Cells are
  now split on spaced pipes only.
- 2026-10-13 later: reviewers P/Q/R/S stopped at the account's session limit; P b7627-7666, R's refused b7830
  and the rest were finished inline by the coordinator. Cursor 7846.
- FIXED 2026-10-13 (owner: "check if you are rejecting events/facts based on prior rules"): the fact layer cut a
  rank word off a codename the window presents as a name ('equipped with the mantle of "Captain Krakoa"' became
  "Krakoa", the island nation: a silent wrong entity, not a refusal; b8007). strip_rank() and _end_ok() now keep the
  rank when the window shows the full string quoted or as a mantle/codename/alias/"calling himself"/"known as";
  normalise() gets the window from label_single.fact_gate_keep. Measured on 14,000 windows: 1 of 61 rank-prefixed
  fact ends is kept ("Agent McGuffin"), the 60 titles (Senator Kelly, Doctor Midas, General Ross) are still stripped;
  approved rows damaged before the fix: 1 (b8007, resubmitted). Test: test_rank_word_kept_when_the_window_names_the_codename.
- FIXED 2026-10-13: a list-entry heading is a name too ("Lieutenant Madrox - Emperor Prime's second-in-command",
  b8054): NAMED_AS also matches a line that starts with the rank+name and a dash/colon. Re-measured: still 60/61
  titles stripped. Before, the dupe's empire and invasion facts were pinned on "Madrox" (silent wrong entity).
- FIXED 2026-10-13: the crowd-word rule refused item/thing/form/power OBJECTS that merely contain a crowd word
  ("ability to entrance others with music", b8055; "powers of the Scarlet Witch", "Book of the Darkhold",
  "Staff of One", "army of Dragon Men"). Thing-type objects (NON_PERSON_OBJECT item/thing/form, gained/lost_power)
  skip it, except `gave` (its object is the recipient, A97) and quantity-led objects ("many deities", "several of
  them"). Measured: 57 of the historical crowd drops on such objects now pass; spot-read they are things.
  Test: test_crowd_word_inside_a_thing_object_is_no_crowd.
- NOTE (A141/A18): on a duplicating-character page "Emperor Prime" (the Bunker Dupe) is not "Jamie Prime" (the
  original, dead in that window); the 35B wrote "Prime Jamie" for the Emperor (b8054).
- NEW A152 (b8068, b8069): a list entry that names a duplicate/variant after another hero ("Deadpool - One of a group of
  dupes", "Hulk - ...") written with the bare famous name -> the rows land on Wade Wilson / Bruce Banner. Write the
  page's own entry form ("Deadpool Dupe", "Hulk Dupe", like "Bartender Dupe"); never the bare name of the other hero.
- GATE AUDIT 2026-10-13 (27B, stage 1 deterministic): re-gating every row dropped in labels_v2 with today's gates:
  1,099 recovered by the 2026-10-12/13 fixes (989 facts, 88 events, 22 tags); 2,681 still refused in 88 reason
  classes (largest: relation not in vocabulary 435, of which ~290 are event verbs that split_event_facts moves;
  not verbatim 579; bare pronoun 248; unnamed/class 235; race page 235+211; escaped needs an object 133).
- FIXED 2026-10-13: the modality written as the relation ("Strange|planned|learn magic", "Peter|claimed|...") was
  dropped by REL_FIX; normalise() now keeps it as other_verb + that modality + asserted_by, the object being the
  planned verb (only "to <verb>" or a gerund in the quote) or the claim/plan word as a verb. 39 of 94 repaired, the
  rest have no verb in the quote. Test: test_modality_written_as_relation_becomes_other_verb.
- FIXED 2026-10-13 (27B gate audit, stage 2 verdicts "WRONG_REFUSAL"): (1) a race/kind as the OBJECT of a classifying
  relation is a fact about the individual ("Black Bolt leader_of Inhumans", "Gorgon member_of Inhumans", "Craddock
  revealed_as Skrull", "Illyana transformed_into demon", "Athena member_of Olympians"); races stay refused as actors
  ("Skrulls invaded", 27B: correct refusal) and as person ends. (2) SPECIES matches only the plural "Gods": "God" is
  a named deity ("to ask God forgiveness"). Measured: 29 of the 242 still-refused race fact rows pass, all
  classifications or God. Test: test_race_as_classifying_object_and_god_as_name.
- FIXED 2026-10-13 (event gate, label_single._personal_use): a person whose name is also a place page was refused as
  "place X as the object of" ("CIA agents China and Barrett", "Lord Carteret", "Carol Danvers"; b8137/b8141). The
  place refusal now spares an end the window introduces with a first name, title or "agents". Measured on the 52
  still-refused place-object rows: the 6 passing rows are all people; countries/cities/realms stay refused
  (Whitehall without a first name in its window is still missed).
- NOTE (A33, b8142): a resurrection done to use the revived ("the Legion took Frank's body and Morbius resurrected him
  ... to help them against the Hunter") written as saved -> awakened only (A33 tool revival), as Mandarin/Killmonger.
- FIXED 2026-10-13 (27B gate audit): knowledge relations (learned/discovered/revealed/suspected/remembered/forgot)
  with a described or clause object were dropped as indefinite/crowd ends ("Avengers learned the X-Mansion had been
  attacked", "discovered a cure", "the truth"); normalise() now applies the A115/A133 route itself (object -).
  Measured: 245 of 306 still-refused knowledge rows pass; the rest fail on race/crowd/pronoun subjects (correct).
  Test: test_knowledge_relation_with_clause_object_becomes_dash. 27B verdicts so far (89): races as actors, crowds and
  indefinite person ends are confirmed correct refusals; the wrong ones were God, Olympians (fixed) and these.
- RECOVERY 2026-10-13: rows the old gates dropped that today's gates pass were put back into labels_v2 (tmp recover2.py,
  rows marked `recovered_2026_10_13`; backup labels_v2.jsonl.bak-pre-recovery-2026-10-13): unviewed windows (b>8164)
  got 4 events, 78 facts, 4 tags in their base rows, so the forward pass reviews them like any labeller row. Reviewed
  windows are NOT changed: their 202 events + 826 facts that the final rows lack are queued in
  big/recovered_reviewed_2026-10-13.jsonl (710 windows); many were removed on purpose, so the 27B screens each against
  the window and the reviewed rows (tmp screen_recovered.py, ACCEPT/REJECT) and Claude hand-checks the ACCEPTs.
- FIXED 2026-10-13 (A101 flag): a doer-less passive on a no_doer tag ("Lorna was calmed", b8170; "Lang was captured")
  was flagged as naming its doer; the name is the patient. The flag now skips "X was/were <participle>" on no_doer
  tags. Measured: 135 approved no_doer tags carried the false flag, all passives; no_relation/deictic still flagged
  ("Gao was forced to watch" stays a hint). Test: test_a101_doerless_passive_on_no_doer_tag_is_no_flag.
- 27B AUDIT STAGE 2 READING (2026-10-13, 289/391 judged): most "WRONG_REFUSAL" verdicts are artifacts of the audit
  prompt, which told the 27B that proper places are legal ends: `escaped`/`arrived` with no object (our schema needs
  the pursuer / the place), a city or planet `saved` (a `protected` fact here, b8145) and nation-vs-nation `fought`.
  Not changed. Real misses: Whitehall/Danvers/Lord Carteret as places (fixed earlier by _personal_use, Whitehall
  without a first name still missed), God/Olympians (fixed), clause objects of knowledge relations (fixed).
- FIXED 2026-10-13 (fact gate normalise): the labeller's literal "no object" `-` was refused as "end '-' is too
  short to be a name" (Stark|remembered|-, Ward|wounded|-); `-`/none/null now mean no object. Measured: 47 of 56
  historical refusals of that class pass; all spot-read correct learned|-/revealed|-/wounded|- rows.
- FIXED 2026-10-13: "Agent 33"/"Agent 13" stripped by older code to the bare "33"; normalise puts the rank back
  when the window writes "<rank word> <number>" (RANK never strips before a digit now). 6 more rows pass (53/56).
- NEW GATE 2026-10-13 (A59): a comma list of people as one end ("Reed, Ben and Johnny", "May, Rodriguez, and
  Mackenzie") passed the fact gate; now refused ("one row per person"). Measured: 80 kept label rows refused (all
  lists), 0 approved rows; a company with "&", number commas ("1,000,000 BC") and place/thing/power objects and
  born places stay legal. Test: test_dash_object_list_end_and_agent_number.
- RECOVERY 2 (2026-10-13, after the `-`/Agent-number fixes): 49 more facts + 3 tags put into unviewed windows
  (b>8344, marker counts accumulate; backup labels_v2.jsonl.bak-pre-recovery-2026-10-13.2); the reviewed-window
  queue was rebuilt at cursor 8344 (708 windows, 202 events + 824 facts).
- FIXED 2026-10-13 (fact gate, label_single._whole_short_unit): the 12-char quote floor refused infobox list lines
  ("Avengers", "Ned Leeds", "Vision †", "{{M|Hydra}}", "Sokovia"; "Pizza Dog" at b8359). A short quote now passes when
  it is a whole line or a whole sentence of the window and names one of the row's ends; other_verb rows excluded
  (an occupation line "teacher" is no act). Measured: 7 of 24 historical refusals pass, all list lines; fragments
  ("lost", "he was next", "to kill him") stay refused. Test: test_short_quote_whole_list_line_passes.
- FIXED 2026-10-13 (fact gate, 27B stage 2): a possessive before a PLACE/ITEM/THING/FORM object was refused as a bare
  pronoun ("Kingpin|wore|his father's cufflinks", "Matt|located_at|his apartment", "Winter Soldier|destroyed|her
  ship"); B.8 already allows it. Now legal for those object types only (not titles: "their deadliest assassin"; not a
  person tail: "his abusive father"). Measured: the bare-pronoun class goes 95 -> ~145 of 285 passing; the 55
  possessive rows spot-read as places/items. Test: test_possessive_thing_object_is_no_bare_pronoun.
- 27B STAGE 2 FINAL (401 judged): CORRECT_REFUSAL 197, WRONG_REFUSAL 98, ROW_WRONG_ANYWAY 33, unparsed 73. The wrong
  refusals fell into: places as ends (prompt artifact, schema kept), intransitive escaped/arrived/departed (schema
  kept), `-` objects (fixed), knowledge clause objects (fixed), possessive thing objects (fixed), short list-line
  quotes (fixed), China/Danvers/Carteret people named like places (fixed), God/Olympians (fixed).
- RECOVERY 3 (2026-10-13, cursor 8494): 18 more facts into unviewed windows (backup ...-2026-10-13.3); reviewed-window
  queue rebuilt (732 windows). recover2 did not dedupe tags, so its re-runs re-added 3 tags each time: 6 duplicate
  tags removed, and the script now skips a tag the window already has.
- 27B STAGE 3 (name changes, 118 approved windows with a stated rename/mantle; 49 OK, 26 LOST_ALIAS, 43 unparsed):
  most LOST_ALIAS verdicts are the one-name rule working (Peter Parker/Spider-Man, Kate/Hawkeye, Brian/Captain Britain
  keep the window's one name; the alias lives on the infobox/overview windows). 9 were real misses: a rename the
  window states with "rechristened", "later X", "went under the name of", "reform ... as", "took on the guise of",
  "transformed into the X", "became known as", "As <title>" and no alias_of/disguise_as row. Added (b7303, b7307,
  b1159, b566, b3884, b6511, b5422, b1875, b4810, b5423). No rule refused these rows; the reviewer (me) skipped them,
  so the rule is a review habit: every stated rename gets its alias row even when the window's rows use one name (A146).
- RECOVERED ROWS IN REVIEWED WINDOWS (27B stage 4 + hand check, 2026-10-13): 1,026 queued rows screened: 303 ACCEPT,
  708 REJECT, 15 unparsed. Hand check of the 303: ~150 added (learned|-/revealed|-/suspected|- knowledge rows,
  race/group membership, reigns as leader_of, attempts as verbs, a few events), normalised to the catalog forms;
  ~150 refused: machines/cities/documents as doers, saved places (protected instead), crowds, production notes,
  hypothetical plans, garbage objects. 27B precision on ACCEPT ~50%: its screen narrows, it does not decide.
- FIXED 2026-10-13 (row flags, big_flags.check): `{{r|...}}` citation templates were read as narrative, so citation
  titles raised "fuller name in window for 'Ares': ['Ares Vol']" and "window has both 'Spider-Man' and 'Peter'"
  (b8933: "Peter Parker, The Spectacular Spider-Man Vol 1 100" is a source, not a second name). Measured on all 97
  citation windows: 17 name flags disappear, all false (titles only); no flag on narrative text is lost; MISS? cues
  only renumber. check() now strips citations first. Test: test_citation_titles_raise_no_name_flags.
- RULE CHECK 2026-10-13 (rank prefix, flag only): "Dr. Steve" (b8927) and "Emperor Yan"/"Emperor Huang" (b8850) are
  the names those characters go by; stripping the rank would leave "Steve"/"Yan", which is the Po mistake again.
  Keep the title when the window never gives the bare name; the flag stays a hint, not a rule.
- RULE CHECK 2026-10-13 (A106, Fin Fang Foom b8838/b8842): a dragon kept dormant for centuries by a herb is not
  ordinary sleep; his waking stays `awakened` and the flag is overridden (ruling: A106 = ordinary sleep only).
- FIXED 2026-10-13 (event gate, label_single.gate): draft_v2.check_rows splits every comma end as a list (G.2), so
  "Washington, D.C." became "arrived Washington" + "arrived D.C." (b8951 refused the hand row as 13 -> 15). Measured
  over big v2: 13 rows in 8 windows carried a bare "D.C." end, all splits of "Washington, D.C."; in window text the
  comma-initialism forms are D.C. (39) but also S.H.I.E.L.D. (24), A.I.M. (11), M.O.D.O.K. (9) in real lists. So
  only a comma before a trailing TWO-letter initialism (D.C., N.Y., U.S.) joins one place; longer ones still split.
  Done in label_single (this branch), not draft_v2, which label_single loads from the main checkout on purpose.
  Reviewed windows: b5507 re-pointed to "Washington, D.C."; b2550/b2744/b2929 were already corrected; unreviewed
  b10889/b12584/b13350 carry "D.C." rows to fix on arrival. Test: test_comma_before_two_letter_initialism_is_one_place.
- FIXED 2026-10-13 (row flag R4/R12, big_flags.JOIN): "united with" matched inside "reunited with", so every
  "X reunited with Y" met row was flagged as met-from-joining, though the catalog rules "reunited with X" -> met.
  Measured on approved rows: 266 met rows flagged, 131 only by "reunited" (all kept as met in review); the regex now
  skips "reunited". Test: test_reunited_is_no_joining_flag.
- FIXED 2026-10-13 (row flag "description/garbage end", big_flags.check): any end of <= 2 characters was flagged as
  garbage, the Po mistake again: "MJ" (b8989/b8990/b8991). Measured on approved rows: 26 short ends, all kept in
  review (MJ 17, Ox 3, Wu 2, US 2, Li 1, M 1). A short end that starts with a capital is now read as a name; only
  short non-capitalised ends stay flagged. Test: test_short_capitalised_end_is_a_name.
- TOOL 2026-10-13 (big_review_v2 fix): a "-"/"f-"/"t-" line that matched nothing passed silently, so after
  "r Toomes=>Adrian Toomes" the possessive end "Toomes' lair" survived a removal written against the renamed form
  (b8992, also b8988, b8980). Such lines now print UNMATCHED.
- MEASURED, NOT CHANGED 2026-10-13 (quote gate, raw wiki links): 16 windows keep raw "[[Page (Earth-616)|Name]]"
  markup (Adrian Toomes, b2865/b2866, b9179-b9184). The labeller quoted the rendered text, so 11 rows fail "quote is
  not verbatim" (3 in reviewed windows). Too few for a link-tolerant matcher; on review, re-add the row with a
  pipe-free verbatim stretch of the window (e.g. "abducted by the mercenaries [[Anthony Masters (Earth-616)").
- NOTE 2026-10-13 (GPU): the 27B Qwen server was unloaded at the owner's request after the stage 2-4 audits
  (ninfer-stop.sh, mode=off); review work needs no model.
- MEASURED, NOT CHANGED 2026-10-13 (event gate, " and " inside a place name; was OPEN since b2001): draft_v2.check_rows
  splits every end on " and " (G.2 lists), so "Land Between Night and Day" became "arrived Land Between Night" +
  "arrived Day" (b9565). Measured over all 14,000 windows (linear scan of the 3,862 wiki titles with " and "): 109
  windows name such a one-page title, but most are real pairs of people that must split ("Cloak and Dagger" 16,
  "Nelson and Murdock" 16, "Ant-Man and the Wasp" 12, "Percy and Barton Grimes"); location pages occur in 11 windows
  and only ~4 event rows carry a broken fragment (Land Between Night and Day x2, Bethesda Terrace and Fountain,
  Heavy Hitters Hotel and Casino). A general join would merge pairs of people; a location-only join would fix ~4
  rows. Left as is: on review keep the specific named part or record the whole name as a `located_at` fact (b9565).
