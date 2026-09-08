# CSM — eight-verb coverage measurement

- Date: 2026-09-09 (the CSM-6 instrument unit, zero-GPU; no model run — the
  sample was read and classified by the worker, mirroring JJK's method).
- Premise check: `EVENTIVE_VERBS` in `scriptengine/ingest/events.py:43-54` is
  the closed set **fought / killed / awakened / sealed / betrayed / saved /
  arrived / departed / met** — nine verbs, not eight: the JJK COUNCIL_1 1C
  ruling widened the set with `met` only (JJK's `PHASE1B_VERB_COVERAGE.md`
  "1C ruling: widen with `met` only"). The job's "eight-verb" is the §12
  design name; this measurement runs against the **live** set, because that
  is what a CSM extraction would use.
- Corpus slice: CSM's JJK-Summary equivalent — the 243 `Summary` sections on
  `chapter_box` (231, 73,481 words) + `episode` (12, 16,940 words) pages =
  90,421 words, 4,330 sentences ≥20 chars under the engine's own splitter
  (`chunker.split_sentences`). This is the densest plot slice, not the
  population (the per-character arc sections, 112,628 words, are excluded —
  quote the number as "of the chapter/episode Summary slice").
- Sample: 100 sentences, `random.seed(20260909)`, `random.sample` over the
  sentence list in (document_id, section_id) order. Reproduce with the seed;
  the sample is appended in full with its classifications.

## The rule (mirrors the JJK record)

A sample sentence is **covered** iff its main eventive content can be
rephrased as `S V (O)` (or passive) with V in the live set, without changing
the main described event:

- a conflict of any wording (battle, fight, combat, clash, duel,
  confrontation, counterattack, a clash of domains) expresses `fought` — an
  opponent or an ongoing conflict must be in the sentence;
- movement to a location (visits, goes to, heads into, returns, jumps into
  the fray, is brought to, travel to, rushes around the corner) expresses
  `arrived` / `departed`;
- rescuing expresses `saved`; slaying/devouring-alive expresses `killed`; a
  defection expresses `betrayed`; a power coming online expresses
  `awakened`; a first contact expresses `met` (the widened cell).

Purpose/motive clauses ("in order to…", "so he can…") do not count.
Descriptions, states, feelings, decisions, observations, explanations,
rhetorical questions and recollections are **not covered** — the closed set
working as designed.

## Result

**24/100 covered, 76/100 (76%) cannot be held by the live verb set — of the
CSM chapter/episode Summary slice.** JJK's number on its own slice was 61%
uncovered; CSM's slice is dialogue-denser (chapter summaries quote a lot of
conversation), so the uncovered share is higher. The covered count is
contested within a **22–26/100 band** (borderline calls: 053/065 movement-
subordinate vs main-clause-governs; 068/099 subordinate-movement).

Covered, by verb:

| verb | count | items |
|------|-------|-------|
| fought | 9 | 001 009 016 019 028 065 075 094 096 |
| arrived | 7 | 003 007 018 021 053 079 091 |
| killed | 5 | 010 024 036 057 090 |
| departed | 3 | 017 031 095 |
| saved | 0 | — |
| met | 0 | — |
| sealed | 0 | — |
| betrayed | 0 | — |
| awakened | 0 | — |

### Composition of the 76 uncovered

- **69 are pure description** (state, feeling, decision, observation,
  explanation, recollection, offer, rhetorical question) — correctly outside
  the set by design; not a gap. Items: 002 004 005 006 008 011 012 014 015
  020 022 023 026 027 029 030 032 033 034 037 038 039 040 041 042 044 045 046
  047 049 050 051 052 054 055 056 058 059 060 061 062 063 064 066 067 068 069
  070 071 072 074 076 077 078 080 081 082 083 084 085 086 087 088 089 092 093
  097 098 099 100 (040 the dogs bounding into the room is a subordinate
  movement under a description main clause; 071 "decides to save" is a
  decision, not a rescue; 099 "approaches" a person in the same room is not
  location movement).
- **3 are fight-adjacent but not eventive** — technique/progression or
  habit with no stated conflict in the sentence (closest: fought): 013 025
  073.
- **3 are kill-intentions** (closest: killed): 035 043 048.
- **1 is a save-decision** (closest: saved): 071 (counted once, in the
  description bucket above as a decision; listed here for the closest-verb
  census).

**Neither `met` nor any other widened cell recurred as a true gap: 0
first-contact events in this slice** (mid-series chapters — the meetings
happened earlier in the series). `betrayed`/`awakened`/`sealed` were never
used by the sample either. On this slice the live set is over-specified in
five cells and has no recurring under-specification — the JJK `met/
encountered` gap did not transfer to CSM.

## Reading

The 76% is *not* a defect in the verb set: 69 points of it are description
the set deliberately refuses, and CSM's chapter summaries are conversation-
heavy. On the ~7 eventive-but-uncovered sentences the set is thin for the
same reason as JJK (wiki prose states intentions and progressions rather than
placed events). Per the 1C rule ("high uncovered fraction → the verb set is
widened before any further extraction"), the decision for the council at the
Phase-2 extraction gate: **no widening is demanded by the CSM sample** (no
recurring true eventive gap; the one candidate, `met`, is already in the set
and unused here). What the number does decide: a CSM extraction at the live
set would place roughly a quarter of the Summary slice's sentences as
ordered events — the extraction's yield, not its quality, is the Phase-2
question.

## Sample and classifications (seed 20260909)

| # | source | sentence | verdict | verb / closest |
|---|--------|----------|---------|----------------|
| 001 | Chapter 146 | Devil Hunters begin engaging in combat with the now-transformed followers in the streets, and Nayuta states that she finally realizes Fami's plan to slay the Death Devil… | **covered** | fought |
| 002 | Chapter 135 | She reveals that Chainsaw Man has given up on fighting devils, but due to his heart, he can't be an ordinary human. | uncovered | description (reveals) |
| 003 | Chapter 185 | Denji heads back to Asa, only to see her distraught and dishevelled. | **covered** | arrived |
| 004 | Chapter 164 | Haruka lets Denji know that if Nayuta isn't here, then there's nothing else that they can do to help. | uncovered | description |
| 005 | Episode 4 | She wonders why Denji saved her, as she attempted to kill him. | uncovered | description (wonders; closest saved/killed) |
| 006 | Chapter 105 | As they are now besties, Yuko decides she will "handle" Asa's bullying problem and tells her not to come to school tomorrow. | uncovered | description (decides) |
| 007 | Chapter 45 | Suddenly, Nomo rushes around the corner, requesting their aid. | **covered** | arrived |
| 008 | Chapter 1 | Makima then gives him two choices: be killed by her or become her pet, and as a pet she would feed him. | uncovered | description (offer; closest killed) |
| 009 | Chapter 232 | Their moment is interrupted when a chain strikes them, followed by an apology from the attacker, who had mistaken the woman for the Zombie Devil. | **covered** | fought |
| 010 | Episode 3 | He then attempts to punch Denji, but Denji just cuts his arm and kills the Bat Devil, disembowling him. | **covered** | killed |
| 011 | Chapter 90 | Power asks who he is before quickly making the connection that he was Pochita… | uncovered | description (asks/realizes) |
| 012 | Episode 2 | Denji gets excited, but feels anaemic again and collapses. | uncovered | description (state) |
| 013 | Chapter 206 | Yoru warns her that they'd be damaged by the blast but she ignores her warning and fires anyway. | uncovered | fought (fires, no opponent stated) |
| 014 | Chapter 183 | Since it couldn't have come from his stomach, Denji concludes that his body must be linked with Pochita's in the real world… | uncovered | description (concludes) |
| 015 | Chapter 43 | The next day, the two hang out at the festival. | uncovered | description (hanging out) |
| 016 | Chapter 8 | Denji ignores him, and punches him, yelling he will open him up and touch those boobs. | **covered** | fought |
| 017 | Episode 11 | After dropping off Aki at the Public Safety, Yutaro tosses a canned drink at his head… | **covered** | departed |
| 018 | Chapter 206 | Miraculously, she doesn't sustain major damage and she rushes up the rubble to jump up and grab onto Denji… | **covered** | arrived |
| 019 | Chapter 109 | Yuko notices Asa passed out, and lashes out at Asa's last bully. | **covered** | fought |
| 020 | Episode 6 | Aki states that if necessary, he will use his sword, but Himeno forbids him. | uncovered | description (states/forbids) |
| 021 | Episode 12 | He stands up and takes his sword and walks towards the devil. | **covered** | arrived (walks towards) |
| 022 | Chapter 230 | Denji refuses, protesting that he was on the verge of achieving his long-awaited goal. | uncovered | description (refuses) |
| 023 | Chapter 79 | As Denji returns to his human form in shock, the Future Devil appears and laughs, commenting on how Aki "Died in the worst way possible… | uncovered | description (appears/comments) |
| 024 | Episode 7 | Denji is surprised to see that the fight is already over, but slices the devil's heart and kills it. | **covered** | killed |
| 025 | Chapter 25 | With each attack, Himeno loses more of her body. | uncovered | fought (progression) |
| 026 | Episode 4 | She finds saving Meowy a foolish reason as she loves blood. | uncovered | description (finds) |
| 027 | Episode 5 | The devil hunters keep looking for the devil inside the hotel. | uncovered | description (searching) |
| 028 | Chapter 209 | The War Devil then reappears on her back, impaling her with one of her swords, though the Falling Devil retaliates by firing a blast behind her. | **covered** | fought |
| 029 | Chapter 24 | Aki calls out to Power, who recommends getting Himeno to a doctor. | uncovered | description (recommends) |
| 030 | Chapter 132 | Denji refuses, saying that he wants to have it both ways, as by being Chainsaw Man, people pay attention to him. | uncovered | description (refuses/saying) |
| 031 | Chapter 192 | She humours the idea and he leads her away from the growing mob, biting her finger somewhat to prevent any more deaths. | **covered** | departed |
| 032 | Chapter 132 | Yoshida informs Denji of the whereabouts of Asa… | uncovered | description (informs) |
| 033 | Episode 2 | Denji wonders why and Aki explains he is trying to be nice, since people who start this job without thinking will always end up dead. | uncovered | description (explains) |
| 034 | Chapter 53 | Makima asks Aki to be part of Denji's protection, before telling him they plan to hunt the Gun Devil in the next year… | uncovered | description (orders; fought intention) |
| 035 | Episode 5 | She believes since Denji is special, he can kill it and if he does, she will grant him one wish. | uncovered | killed (belief, conditional) |
| 036 | Chapter 102 | Ultimately, Chainsaw Man decides to aim for the Devil's head, splitting its head in half, while neglecting to save either of his two choices in order to save a cat that was nearby instead. | **covered** | killed |
| 037 | Chapter 121 | Yoru quickly takes over, demanding Asa stays back, as she looks up to see every occupant of the complex outside their doors, staring directly down at them. | uncovered | description (takes over/observation) |
| 038 | Chapter 169 | The boy tells him that he doesn't want to be responsible for paying the group's bill, to which Haruka calls him weird. | uncovered | description (tells) |
| 039 | Chapter 148 | At Asa's apartment, Yoshida expresses shock due to Asa withstanding his blade using her left arm. | uncovered | description (expresses shock) |
| 040 | Chapter 119 | She kisses him, much to Denji's shock… the door opens, and seven dogs start bounding into the room. | uncovered | description (kiss/scene; subordinate arrived) |
| 041 | Chapter 196 | Sighing, he tells her that he could tell that due to her coming from out of town, she was probably involved in some devil-related tragedy. | uncovered | description (tells) |
| 042 | Chapter 165 | He asks Asa if she understands, but she mistakes his story for metaphor and she asks him to tell it to her straight. | uncovered | description (asks) |
| 043 | Episode 6 | Aki yells that he doesn't care if Denji gets killed, but Denji wants to kill the Gun Devil too, and Aki knows he can't do it alone. | uncovered | killed (intention) |
| 044 | Episode 4 | Aki recalls that there were reports of people wanting to thank the Chainsaw Devil as it saved them. | uncovered | description (recalls; closest saved) |
| 045 | Chapter 159 | He spots a door and assumes it's an exit, but it's instead a cell filled with pseudo-Chainsaw Men. | uncovered | description (spots/assumes) |
| 046 | Episode 11 | Yutaro heard that Aki is after the Gun Devil and asks him if he really believes he can take him down… | uncovered | description (asks) |
| 047 | Chapter 81 | As she once again orders him to open the door, her words are shown to be covering Pochita's orders from Denji's nightmares: 'Don't open it'. | uncovered | description (orders) |
| 048 | Episode 6 | Hirokazu also comes out and suggest they kill Denji or they will die too. | uncovered | killed (suggestion) |
| 049 | Chapter 131 | She asks the Justice Devil how they find the taste of humans that were steeped in fear, only for the latter to vomit, regurgitating both Asa and Denji. | uncovered | description (asks) |
| 050 | Chapter 15 | Aki notes that all the clocks have stopped at 8:18, theorizing that the floor is trapped in time… | uncovered | description (notes/theorizes) |
| 051 | Chapter 23 | The group overhears the gunshot but assumes they're merely drum beats. | uncovered | description (overhears/assumes) |
| 052 | Chapter 55 | The eldest brother laughs, before changing his face to match Kurose's. | uncovered | description (laughs/changes) |
| 053 | Chapter 41 | As he enters, Reze comments he's eaten there everyday that week. | **covered** | arrived (enters) |
| 054 | Chapter 69 | However, Denji emerges from the wreckage, cloaked entirely in flames, still pulling on the chain. | uncovered | description (emerges; closest arrived) |
| 055 | Chapter 212 | As Death stops exposing her belly and sits back down, Denji is told to rest in the nurse's office in preparation for the upcoming battle. | uncovered | description (told to rest) |
| 056 | Episode 11 | Akane mentions that even if they run, there is no place that is safe from Makima. | uncovered | description (mentions) |
| 057 | Chapter 199 | A murder of crows is summoned, devouring Famine and the Fake Chainsaw Man alive. | **covered** | killed |
| 058 | Chapter 36 | Denji repeats he felt nothing. | uncovered | description (repeats) |
| 059 | Episode 7 | He ends up waking up at night wanting water. | uncovered | description (waking from sleep is not `awakened`) |
| 060 | Chapter 22 | Upset, Denji comments on how poor his first-kiss was, expressing a worry that all future kisses will remind him of vomit. | uncovered | description (comments) |
| 061 | Chapter 51 | As the smoke clears, it is revealed that Denji managed to keep the arm attached to his torso by placing a chain between his shoulder and forearm. | uncovered | description (revealed) |
| 062 | Chapter 231 | He admits he does not know what will happen to the world afterward, but believes it is the only way forward. | uncovered | description (admits) |
| 063 | Episode 4 | Denji tries to reach for the apples that Aki was cutting, but Aki pulls them away. | uncovered | description (reaches/pulls) |
| 064 | Chapter 224 | Yoru announces her plan to Denji, declaring her intent to transform the American flag on the moon into a spear… | uncovered | description (announces intent) |
| 065 | Chapter 35 | However, he is quickly overwhelmed by the many arms of the Ghost Devil, and is soon being strangled by the creature. | **covered** | fought |
| 066 | Chapter 82 | She goes on further, stating that Denji killed his abusive and alcoholic father in self-defense… | uncovered | description (stating a past kill; closest killed) |
| 067 | Chapter 27 | Tendo informs Kurose that due to her high ranking, the nature of the Devil Makima has a contract with is kept classified. | uncovered | description (informs) |
| 068 | Chapter 212 | Though initially skeptical of Fumiko's motives upon realizing she is lying to him, Denji is given a nude photo of her before she leaves the scene. | uncovered | description (closest departed) |
| 069 | Chapter 165 | He then tells Denji that they should skip the sushi joint because he knows a place that will cheer any man up in an instant; a soaplands. | uncovered | description (tells) |
| 070 | Episode 7 | Usually Makima travels a lot, but lately she is staying in Tokyo and Himeno wonders if it's because of Denji and if she knows his secret. | uncovered | description (wonders) |
| 071 | Chapter 102 | Asa weighs her options, but she ultimately decides to save her. | uncovered | saved (decision) |
| 072 | Chapter 93 | His mind is soon filled with memories of his time with Public Safety as he thinks back on the encounter with the Darkness Devil… | uncovered | description (memories) |
| 073 | Episode 6 | As those family members can't take their grief out on the devil, they usually turn on the devil hunters. | uncovered | fought (habitual) |
| 074 | Chapter 182 | Moved, he asks her how she got over it, to which she answers that she hasn't… | uncovered | description (asks/answers) |
| 075 | Chapter 62 | Inside the building, Galgali fights off swarms of Dolls, as Kobeni looks down in despondence at her destroyed vehicle. | **covered** | fought |
| 076 | Chapter 104 | He then asks Denji if he's trying to expose his identity in order to get a girlfriend, to which he confirms. | uncovered | description (asks) |
| 077 | Chapter 91 | Kishibe asks him if he was either Denji or the Chainsaw Devil, and states that if he was truly Denji then he would help give him some way to escape from Makima. | uncovered | description (asks/states) |
| 078 | Chapter 96 | She tells him that they'd be together forever, and that they'd eat a lot together, sleep together, and live a happy life together. | uncovered | description (tells) |
| 079 | Chapter 36 | Denji and Power arrive in the headquarters using an elevator. | **covered** | arrived |
| 080 | Episode 8 | Aki pulls out his sword and tells Power to stop Himeno's bleeding. | uncovered | description (tells) |
| 081 | Episode 7 | While looking at the menu, Denji recalls his promised kiss from Himeno, and she tells him that she will give him one when she gets a bit drunker. | uncovered | description (recalls/tells) |
| 082 | Chapter 142 | Fumiko comments on Denji's decision of rejecting the Chainsaw Man Church, with him solemnly admitting that he will do what Yoshida says and not transform into Chainsaw Man again. | uncovered | description (comments/admits) |
| 083 | Chapter 127 | Asa asks what that desire is, to which Denji enthusiastically replies that it's sex. | uncovered | description (asks/replies) |
| 084 | Episode 12 | Katana Man then explains that Akane had done some changes on him and replaced his heart with the Katana Devil, however he couldn't sleep when he accidentally killed a zombie. | uncovered | description (explains; closest killed, backstory) |
| 085 | Episode 5 | A door then opens and a head with a hand and a foot comes out. | uncovered | description (comes out; closest arrived) |
| 086 | Chapter 208 | Denji accepts his fate, as he believes that by being turned into a "badass weapon" as long as some of his sins can be lightened. | uncovered | description (accepts/believes) |
| 087 | Chapter 40 | As he walks, Denji thinks of Makima, and how her words were able to calm his pent-up concerns. | uncovered | description (thinks) |
| 088 | Chapter 16 | The Eternity Devil mocks the group, before offering them a contract; promising to release them in return for allowing it to eat Denji. | uncovered | description (offers) |
| 089 | Chapter 212 | Fumiko attempts to convince Denji that the Death Devil is only using him and questions what'll happen if the War Devil were to be defeated. | uncovered | description (attempts to convince) |
| 090 | Chapter 223 | Before Yoru can fully grasp his words, she watches in horror as Denji devours the Moray Eel Devil, mockingly remarking on its taste. | **covered** | killed |
| 091 | Chapter 39 | Makima shows up and reveals the pair are going to have a movie marathon at a local cinema, non-stop until midnight. | **covered** | arrived (shows up) |
| 092 | Chapter 153 | This causes the young Devil to realise that Denji is only telling her to run away because he loves her. | uncovered | description (realises) |
| 093 | Chapter 189 | The floorbound Fumiko tells Yoshida that he can have her heart, and Yoshida immediately orders the Octopus Devil to devour it. | uncovered | killed (order) |
| 094 | Chapter 8 | Denji cuts off the Bat Devil's arm, and the two crash through a building. | **covered** | fought |
| 095 | Chapter 204 | Spotting Falling Devil in the distance, she goes after her, but not before telling him that if he doesn't deal with the Fake Chainsaw Man before she gets back then she'll do it herself… | **covered** | departed (goes after) |
| 096 | Episode 8 | As the Katana Man stands, Aki pierces him with his sword, and a devil states "Three." | **covered** | fought |
| 097 | Episode 4 | Aki gets a call from Makima, who tells him that she wants to put Power under his care too, just like Denji. | uncovered | description (gets a call) |
| 098 | Chapter 168 | Denji is left speechless as she tells him she's hungry, leaving him confused and alone in the alleyway. | uncovered | description (tells) |
| 099 | Episode 6 | Aki then approaches her and asks for the cigarette, so she gives it to him. | uncovered | description (asks; closest arrived) |
| 100 | Chapter 18 | Aki decides to use 'The Sword' to get them out, however Himeno binds him, explaining that using such a weapon will massively shorten his lifespan. | uncovered | description (decides; closest fought) |