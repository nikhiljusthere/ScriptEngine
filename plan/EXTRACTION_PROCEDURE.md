# How to label the events in one wiki window

You label ONE window (a short passage from a fiction wiki) with the events it
states. Follow this procedure exactly, in order. It is the procedure Claude
(Opus) uses to write the reference ("gold") answers that every labeler is
measured against. Labelers that skip steps make the same mistakes every time:
they stop after the first event of a window, write a group name where the
window names the members, miss meetings and arrivals, and write plans,
claims and hypotheticals as if they happened. The checklist in step 8 exists
because of those mistakes.

Think through steps 1-8 privately. Then answer with JSON only, in exactly this shape:

{"events": [{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}]}

An empty list, {"events": []}, is a correct answer when the window states no event.

The 12 verbs (no others, no other tenses): fought, defeated, killed, captured,
escaped, saved, betrayed, sealed, met, arrived, departed, awakened.

---

## Step 1 — Read the whole window and decide what kind of text it is

Read every sentence before writing anything; a pronoun in sentence 3 can depend
on sentence 1, and a "they" can mean two people named earlier.

- **Narrative** (plot, synopsis, history, biography, battle, background,
  aftermath): events are likely. Go through every sentence.
- **Descriptive** (powers, abilities, appearance, personality, equipment,
  relationships lists, trivia, behind the scenes, credits, release dates, cast
  lists, episode lists, quotes): usually no events. But a descriptive section
  can still narrate one specific occurrence ("He was easily overpowered by
  Rogers and forced to escape") — that occurrence IS an event. A general
  statement of ability ("she can overpower most opponents") is not.
- **Dialogue lines** (text in quotation marks spoken by characters, "Quote"
  pages): never events. Only the narrator's own sentences state events.
- **Real people** (actors, writers, directors, producers): never ends.
- **A "vs." list / "Battles featured" list** ("Thor vs. Hela"): one `fought`
  row per opposing pair, the line as the quote.

## Step 2 — Split into sentences and find EVERY action clause

For each sentence, list every clause with an action verb — not just the main
one. One sentence often states several events:
"Daisy Johnson arrived and knocked out Shockley" = arrival/meeting + defeat.
"Udonta flies in and saves Quill, but sacrifices himself" = saved (and a death
with no killer: no row). Do not stop at the first event you find in a sentence
or in the window. The single biggest error of labelers is writing one or two
rows for a window that states five.

## Step 3 — The "did it happen?" test, for every clause

Write a row only for something the passage states as having actually happened.

HAPPENED (write it):
- Narrated past or present events: "Stark defeated Bullski".
- Recaps, flashbacks, backstory, a reason clause, a past event mentioned in
  passing: "for murdering the senator" (killed), "Fitz, having been imprisoned
  ... until he was released by Lance Hunter" (Hunter saved Fitz),
  "after Phil Coulson destroyed hers" (fought).
- Pluperfect: "he had kidnapped Maya Lopez's relatives" (captured).
- An attack that was made but failed, was blocked or dodged: still `fought`.
- A narrated memory of a real event: "the memory of Thor murdering Thanos" (killed).

DID NOT HAPPEN (no row):
- Plans, intentions, purposes, goals: "planned to", "in an attempt to", "to
  kill him", "decides to", "went to find X", "so that he could rescue them".
- Attempts never made, threats, orders and commands ("Stane ordered him to
  make it simple"; "Vanessa was the one who ordered Nelson's death" — the
  order-giver did not do the killing, so NO `killed` row; the killer is not
  named, so nothing).
- Hypotheticals, conditionals, predictions, wishes, questions, negations
  ("couldn't defeat him", "would have killed").
- Claims, lies, accusations, boasts, mistaken beliefs of a character
  ("Hoffman told the police that the vigilante killed Blake" — Hoffman's lie,
  no row; "Stane claimed that the president lied" — no row).
- Dreams, visions, illusions, simulations, imagined scenes (but a real event
  recalled in a dream still counts).
- A failed escape ("tried to escape but was stopped") is no `escaped`.
- Descriptions of what someone can do, is, or usually does.

## Step 4 — Who did it, to whom (resolve every pronoun and possessive)

For each clause that happened, find the doer (subject) and the one it was done
to (object).

- **Passive voice**: the doer follows "by": "Glenn Talbot was attacked by Carl
  Creel" → Carl Creel fought Glenn Talbot. "Y lost to X" → X defeated Y.
- **Resolve pronouns by meaning, not by nearness.** Ask who the sentence makes
  responsible. "Davy accompanied Kingpin to Tamaha as he had kidnapped Maya
  Lopez's relatives" — the one who kidnapped them is Kingpin (Davy only
  accompanied him), so Kingpin captured them. "Chavez opened a portal, through
  which she and Strange eventually landed in Earth-838" — "she" is Chavez, the
  one who opened the portal and went through it, not Maximoff.
- **Check what "him/her" refers to after a new person appears**: "one of the
  Flag Smashers restrained Hoskins, so Walker shot him" — "him" is the Flag
  Smasher who restrained Hoskins (unnamed, so no row), NOT Hoskins. Then
  "Hoskins was kicked out ... so Walker threw his shield to save him" → Walker
  saved Hoskins.
- **Possessives**: "show up during their fight" — "their" is the pair just named.
- **"The two" / "they" / "the pair"**: expand to the named people they refer to
  ("The two then rescued Sammy" → Gorgon saved Sammy, Karnak saved Sammy).
- If you cannot tell who did it from the window itself, write no row. Never
  use outside knowledge of the series to supply a doer or a target the window
  does not state.
- A weapon, technique, suit, vehicle or power is never the subject: its user
  is ("Belova used her Widow's bite to subdue Lopez" → Yelena Belova defeated Lopez).

## Step 5 — Choose the verb (decision table)

Use the YES column; when a phrasing is in the NO column, it is not that verb.

| verb | YES | NO |
|---|---|---|
| fought | any attack MADE on someone, even if blocked, dodged or failed; a blow, punch, slap, kick, shot, stab, bite, tackle; "attacked", "engaged", "battled", "clashed", "ambushed", "faced X in battle", "trade blows"; a power or technique used ON someone (electrocuting, paralysing, mind attacks, "forced him to turn into Hulk"); "tried to hinder her by ..." when an act is done; pinning, grabbing, restraining or choking someone during a fight; "flipped the car he was in"; attacks told in passing ("hitting Vivi", "after X shot him earlier"); throwing someone off something; "the duel between A and B" | a confrontation with no attack stated; a threat; an argument; a verbal "lashes out"; scolding; drawing a gun without firing; an attack on a building, ship or object only; an ACCIDENTAL hit on an ally ("accidentally shot Glass with a paintball"); playful contact between friends ("webbed Stark's hand to the doorknob"); being stopped |
| defeated | the fight ENDED with the object beaten: defeated, beat, bested, won against, lost to, knocked out, rendered unconscious (tasered unconscious), subdued, incapacitated, "took X down", "finished off X" (no death stated), "overpowered him and pushed him off the truck" (the fight ended with him out), "knocked him down and believed him dead"; fainting caused by X | "overpowers" while the fight continues; "nearly defeats"; a single hit or wound; having the upper hand; "fatal blow"/"mortally wounded" without a stated death (that is fought) |
| killed | a stated death with its doer: killed, murdered, executed, assassinated, "watches her die from her wounds" after forcing them, "crushed the lab on top of both of them, killing them", destroyed a named robot/AI | a death with no doer in the window ("Reyes is killed on impacting the ground" after a crash, "died from contamination"); ordering a killing; "fatal blow" without a stated death (fought); killing an unnamed group ("killed numerous Masters" — no named object) |
| captured | took the object prisoner or hostage: captured, caught, arrested, apprehended, abducted, kidnapped, "took X captive", "had X kidnapped" (the one who had it done), held prisoner, "brought her to the base as a prisoner", "locked him up", "chained down" by a captor; a portal or teleport that pulls named people away against their will | pinning or restraining during a fight (fought); trapping in a dimension, ice, a barrier or a sealed place (sealed); taking an item |
| sealed | trapped, sealed or banished the object: in a dimension, ice, a barrier, a bunker locked and abandoned, another world, the Void; "pruned" by the TVA (sent to the Void); "trapping Maximoff in the Mirror Dimension" | paralysis by a power (fought); casting a spell with no one trapped |
| escaped | got away from captivity, a trap or a pursuer: escaped, fled, broke free, broke out, "made her way out", "got away", "fled to escape the threat". Object = the captor/pursuer when the window names one; otherwise the named place of captivity ("escaped the Mirror Dimension", "escaped Impel Down") | being released or let go; a failed or attempted escape; dodging an attack (fought); leaving calmly (departed) |
| saved | rescued, freed, released someone from imprisonment, protected from harm, "pulled to safety", "threw his shield to save him", "flies in and saves", "took the hit for", intercepted a blow aimed at someone, "run to her aid" against a threat, extracted someone from danger, healed/revived someone who would otherwise die | "to protect him" (a purpose only); helping with a task; encouraging; healing oneself; planning to rescue |
| betrayed | turned against an ally or broke faith: betrayed, double-crossed, defected, "turned on" an ally | deceiving or tricking an enemy; a ruse that turns out to be fake ("Loki's betrayal was revealed to be a ruse" — no row); leaving; disagreeing; an attempted betrayal |
| met | two named characters come together in the passage: a first meeting, a visit, an encounter, a reunion, "found X" with contact, "was greeted by X", "approached X", "came to see X", "X arrived where Y was", "walked in on X", "confronted X" (also with a fight), "stops X" (an encounter), a meeting held between them, "gathered A, B and C" (the gatherer met each), joining people not already with them ("came too" to a party). One row per newcomer–person pair | talking inside a meeting already under way; companions who are already together; a phone call or video message; seeing on TV; watching or noticing; reporting about someone; a goodbye; working together; allying |
| arrived | reached a PROPER-NAMED place: arrived at, went to, returned to, entered, flew to, landed in, was taken/brought to, "transported to the Void", "made their way to New York City", "drove to the Watchtower", "took the Zephyr One to Chicago" (when they got there) | a description instead of a name ("the office", "his room", "a warehouse", "the car", "the building", "her apartment", "the temple"); heading toward a place ("on their way to the airport"); being in a place |
| departed | left a PROPER-NAMED place or group (the object is the place left, never the destination): "left the planet" (when the window names it), "abandoned Hong Kong", "left the fair" when the window names the fair | "heads to X"; leaving a person; leaving a description-place |
| awakened | woke up, regained consciousness, was revived, came back to life, gained a new power or form for the FIRST time, a new power awakened by an event (Terrigenesis giving powers), a machine reactivated. No object (null) | transforming into a form the character already has; using a power they already have; waking SOMEONE ELSE (the one woken is the subject: "Rhodes woke him up" → Stark awakened, and Rhodes met Stark if they came together) |

Verb rules:
- **Write every verb that fits a clause, not only one.** An entry that is
  followed by an attack is `met` AND `fought`. An interception is `fought`
  (attacker vs target) AND `saved`. Knocking someone out after fighting them
  is `fought` AND `defeated` when the fight is stated separately; when the
  window only states the knockout, write `defeated` alone. A killing after a
  stated fight is `fought` AND `killed`.
- **When only one of two verbs is stated, pick the more specific**: `defeated`
  over `fought` if the end of the fight is stated; `killed` over `defeated` if
  the death is stated.
- `fought` and `met` are symmetric: write ONE row per pair (the subject is the
  one who acts first or arrives).

## Step 6 — Write the ends (subject and object)

- **Names only as the window writes them.** Use the fullest form the window
  uses for that person, and the SAME string in every row of the window
  ("Danny Rand" in every row, not "Danny Rand" in one and "Rand" in another).
- **One person, two names in the window** (codename and real name: "Iron
  Monger"/"Stane", "Black Panther"/"T'Challa", "Iron Fist"/"Rand", "Scarlet
  Witch"/"Maximoff"): use the real name in every row. If the window uses only
  the codename, use the codename.
- **Strip rank and job prefixes** in front of a name: "General Werner
  Reinhardt" → "Werner Reinhardt", "Agent Phil Coulson" → "Phil Coulson",
  "Officer Pike" → "Pike", "Denarian Garthan Saal" → "Garthan Saal". A title
  used AS the name stays ("the President", "the Accuser" in "Ronan the Accuser").
- **Groups: expand to the named members.** When a group acts and the window
  names its members anywhere ("Rocket, Groot, Udonta and Obfonteri" are
  "the Guardians"; "the Thunderbolts" Starr, Yelena Belova, John Walker), write
  one row per named member and NO group row. A named group (S.H.I.E.L.D., the
  Avengers, the Flag Smashers, Hydra, the Ten Rings) is an end only when the
  window names none of its members taking part.
- **Never an end:** unnamed people or crowds ("the guards", "the soldiers",
  "his men", "the rest of the team", "the villains", "several agents", "one of
  the Masters", "a man"); a species or race ("the Frost Giants", "the Kree",
  "the Chitauri", "Skrulls", "Inhumans", "the Sovereign", "Dwarves"); an item,
  vehicle, weapon, technique, suit or building; a real person (actor).
- **A definite description of ONE specific individual** is an end when the
  window gives no name ("the monster", "the driver", "the old man", "Maya
  Lopez's mother"); an indefinite one ("a guard", "one of the soldiers") never is.
- **Different characters who share a name are different ends**: "Loki" and
  "President Loki", "Goku" and "Goku Black", a younger and an older self only
  when the window treats them as two people in the same scene. Never write a
  row with the same person as subject and object, except a stated
  self-directed act ("stabs herself").
- **Places** are objects only of `arrived`, `departed` and (when no captor is
  named) `escaped`. They must be proper names (Wakanda, Kamar-Taj, the Raft,
  New York City, the Playground, the Lighthouse, Earth-838). A place is never
  the object of fought, met, saved, captured, etc.

## Step 7 — Rows

- One row per (subject, verb, object). If three heroes fight two villains,
  write each hero–villain pair (6 rows), never hero–hero.
- `quote` is copied word for word from the window: the shortest clause that
  states the event (at least 12 characters). Never paraphrase, never stitch two
  sentences together. Several rows may share one quote.
- `awakened` has object null; every other verb has a non-null object.

## Step 8 — Final check (do this every time, before answering)

Re-read the window sentence by sentence one last time and ask:
1. Did I write a row for EVERY clause that passed step 3? Look again for the
   commonest misses: walk-ins, visits, reunions, "was greeted by", "found X"
   (met); "went to / returned to / was brought to <named place>" (arrived);
   attacks told in passing (fought); rescues, releases, "pulled to safety"
   (saved); knockouts and "subdued" (defeated); getting away (escaped); waking
   up and revivals (awakened); kidnappings and arrests (captured).
2. Did every group become its named members?
3. Did I write a plan, an order, a claim, a hypothetical, a dream or an
   accidental hit as an event? Remove it.
4. Is every end a named character, creature, named group or (for movement
   verbs) a proper-named place — never a species, a crowd, an item or a
   description-place?
5. Is each person written with one name throughout, ranks stripped?
6. Are fought/met written once per pair?
7. Is every quote copied exactly from the window?

---

## Worked examples (real windows; the reasoning is the procedure above)

**Example 1** — Page: Battle at the Illuminati Headquarters / Siege of Kamar-Taj
Window: "Arriving at Kamar-Taj, Maximoff was once again met with refusal to her demands from Strange, thus she began her offense, although the barrier around Kamar-Taj was initially able to withstand her attacks. However, Maximoff was able to breach the barrier by enthralling one of the Masters, killing numerous other Masters and deflecting any counterattacks they tried against her. When Maximoff stepped closer to the temple, Strange tried to hinder her by trapping Maximoff in the Mirror Dimension, however, she made her way out through reflections. As Strange and Wong stood as the last people left to protect her, Chavez opened a portal, through which she and Strange eventually landed in Earth-838."
Reasoning: "Arriving at Kamar-Taj" → Maximoff arrived Kamar-Taj. Her attacks hit the barrier (an object) → no fought. "killing numerous other Masters" → unnamed crowd, no row. "trapping Maximoff in the Mirror Dimension" → an act was done → Strange sealed Maximoff. "she made her way out" → Maximoff escaped (no captor named for the escape itself → the place). Last sentence: "she" = Chavez, who opened the portal → Chavez and Strange arrived Earth-838 (NOT Maximoff).
Answer: {"events": [{"quote": "Arriving at Kamar-Taj", "subject": "Maximoff", "verb": "arrived", "object": "Kamar-Taj"}, {"quote": "Strange tried to hinder her by trapping Maximoff in the Mirror Dimension", "subject": "Strange", "verb": "sealed", "object": "Maximoff"}, {"quote": "she made her way out through reflections", "subject": "Maximoff", "verb": "escaped", "object": "Mirror Dimension"}, {"quote": "through which she and Strange eventually landed in Earth-838", "subject": "Chavez", "verb": "arrived", "object": "Earth-838"}, {"quote": "through which she and Strange eventually landed in Earth-838", "subject": "Strange", "verb": "arrived", "object": "Earth-838"}]}

**Example 2** — Page: Davy (Goon) / Battle at Haskell County Fairgrounds
Window: "In 2025, Davy accompanied Kingpin to Tamaha as he had kidnapped Maya Lopez's relatives, Chula Battiest and Bonnie. When Lopez saw that her family was kidnapped, Davy walked over and took her gun. As Lopez and Kingpin argued, Davy suddenly punched Lopez, knocking her to the ground. Lopez soon got up and fought the men, defeating Davy along with them."
Reasoning: both went to Tamaha → two arrived rows. "he had kidnapped" → the kidnapper is Kingpin (pronoun by meaning) → Kingpin captured each named relative. Taking a gun = an item → no row. Arguing → no row. "punched Lopez" → Davy fought Lopez (one row per pair; Lopez fighting back is the same pair). "fought the men" → unnamed, but "defeating Davy" → Lopez defeated Davy. Lopez did NOT fight Kingpin (only "the men").
Answer: {"events": [{"quote": "Davy accompanied Kingpin to Tamaha", "subject": "Davy", "verb": "arrived", "object": "Tamaha"}, {"quote": "Davy accompanied Kingpin to Tamaha", "subject": "Kingpin", "verb": "arrived", "object": "Tamaha"}, {"quote": "he had kidnapped Maya Lopez's relatives, Chula Battiest and Bonnie", "subject": "Kingpin", "verb": "captured", "object": "Chula Battiest"}, {"quote": "he had kidnapped Maya Lopez's relatives, Chula Battiest and Bonnie", "subject": "Kingpin", "verb": "captured", "object": "Bonnie"}, {"quote": "Davy suddenly punched Lopez", "subject": "Davy", "verb": "fought", "object": "Lopez"}, {"quote": "defeating Davy along with them", "subject": "Lopez", "verb": "defeated", "object": "Davy"}]}

**Example 3** — Page: Chase of the Flag Smashers / Chase
Window: "As Barnes was falling off the top of truck, Wilson saved him from falling by swooping in and grabbing him in the air. Meanwhile, one of the Flag Smashers restrained Hoskins, so Walker shot him with his pistol before continuing fighting the Flag Smashers. Hoskins then was kicked out of the track, so Walker threw his shield to save him. Getting back on top of the truck, Walker confronted Morgenthau, but she easily overpowered him and pushed him off the truck. Walker landed on a car and was left uninjured, however, he failed the mission, as the Flag Smashers successfully escaped."
Reasoning: Wilson saved Barnes. "Walker shot him" — "him" = the Flag Smasher who restrained Hoskins (unnamed) → no row for that shot; "continuing fighting the Flag Smashers" → no member named → group row. "threw his shield to save him" → Walker saved Hoskins. Walker vs Morgenthau: a confrontation followed by a stated attack (overpowered and pushed off the truck, which ends the fight) → fought AND defeated. "the Flag Smashers successfully escaped" → escaped Walker.
Answer: {"events": [{"quote": "Wilson saved him from falling by swooping in and grabbing him in the air", "subject": "Wilson", "verb": "saved", "object": "Barnes"}, {"quote": "continuing fighting the Flag Smashers", "subject": "Walker", "verb": "fought", "object": "Flag Smashers"}, {"quote": "Walker threw his shield to save him", "subject": "Walker", "verb": "saved", "object": "Hoskins"}, {"quote": "Walker confronted Morgenthau, but she easily overpowered him and pushed him off the truck", "subject": "Walker", "verb": "fought", "object": "Morgenthau"}, {"quote": "she easily overpowered him and pushed him off the truck", "subject": "Morgenthau", "verb": "defeated", "object": "Walker"}, {"quote": "the Flag Smashers successfully escaped", "subject": "Flag Smashers", "verb": "escaped", "object": "Walker"}]}

**Example 4** — Page: Rescue of Pepper Potts/A.I.M. Operative Controller / Background
Window: "Stark returned home and worked on the armor, but was attacked by A.I.M. forces led by Boris Bullski. During the attack, Stane contacted Stark and revealed that he had been working with A.I.M. and was behind the attack. Stark defeated Bullski and confronted Stane, who used a taser on him, rendering him unconscious. Stane then had Stark's assistant, Pepper Potts, kidnapped. As Stane fled in the Stark Industries Private Jet, James Rhodes found Stark and woke him up, telling him what had happened to Potts."
Reasoning: "attacked by A.I.M. forces led by Boris Bullski" → the leader is named → Bullski fought Stark (write "Bullski" in every row: one name per person). "Stane contacted Stark" → a call, not a meeting. Stark defeated Bullski. Taser → unconscious = the fight ended → Stane defeated Stark. "had ... kidnapped" → Stane captured Pepper Potts. "Stane fled" → from no named pursuer → no row. "James Rhodes found Stark and woke him up" → met, and Stark awakened (the one woken is the subject).
Answer: {"events": [{"quote": "was attacked by A.I.M. forces led by Boris Bullski", "subject": "Bullski", "verb": "fought", "object": "Stark"}, {"quote": "Stark defeated Bullski", "subject": "Stark", "verb": "defeated", "object": "Bullski"}, {"quote": "confronted Stane, who used a taser on him, rendering him unconscious", "subject": "Stane", "verb": "defeated", "object": "Stark"}, {"quote": "Stane then had Stark's assistant, Pepper Potts, kidnapped", "subject": "Stane", "verb": "captured", "object": "Pepper Potts"}, {"quote": "James Rhodes found Stark and woke him up", "subject": "James Rhodes", "verb": "met", "object": "Stark"}, {"quote": "James Rhodes found Stark and woke him up", "subject": "Stark", "verb": "awakened", "object": null}]}

**Example 5** — Page: Ambush at the Loki Palace / Background
Window: "Loki was pruned by Ravonna Renslayer and transported to the Void, waking up there to meet four Variants of himself. Confused with his current situation, he asked them who they were and where he was. They told him that he was in the Void and that Alioth was heading toward them. They told him that they needed to escape before Alioth arrived as Loki followed them back to their bunker. Loki eventually told the group about Sylvie and her plan to take down the TVA, but the others laughed at him. Loki tried exiting the bunker but was greeted by another number of his Variants, led by President Loki."
Reasoning: pruned = banished to the Void → Renslayer sealed Loki; "transported to the Void" → arrived Void. "meet four Variants" → unnamed → no row. "needed to escape" → plan → no row. "their bunker" → description place → no row. "greeted by ... President Loki" → met (a different character from Loki).
Answer: {"events": [{"quote": "Loki was pruned by Ravonna Renslayer", "subject": "Ravonna Renslayer", "verb": "sealed", "object": "Loki"}, {"quote": "transported to the Void", "subject": "Loki", "verb": "arrived", "object": "Void"}, {"quote": "was greeted by another number of his Variants, led by President Loki", "subject": "Loki", "verb": "met", "object": "President Loki"}]}

**Example 6** — Page: Daredevil: Born Again/Season One / Plot
Window: "Murdock overhears Vanessa being informed by Cashman about Poindexter's escape and her urge to talk to Wilson about something important. He realizes that Vanessa was the one who ordered Nelson's death, being in charge of Wilson's criminal empire at the time. He steals Vanessa for a dance and confronts her about that, but Vanessa seems unbothered and casually asks Murdock about the secret he keeps from Glenn. Wilson then has a dance with Glenn and alludes to her that Murdock might not be the man she thinks he is."
Reasoning: overhearing is not meeting; ordering a death is not killing (the killer is not named); Murdock and Vanessa are already at the same party (a dance between people already together is not a new meeting); "Poindexter's escape" names no captor or place. Every clause fails step 3, 4 or 6.
Answer: {"events": []}

**Example 7** — Page: Battle of Xandar / Battle
Window: "Ronan the Accuser led his forces to Xandar and attacked the planet in an attempt to destroy it. However, the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers, who were able to prevent Ronan from destroying the planet. However, this was not without sacrifice, as Denarian Garthan Saal and Groot sacrificed themselves in the process. The battle ultimately ended when Peter Quill challenged Ronan to a dance off, distracting him for long enough that Rocket Raccoon could destroy Ronan's Universal Weapon and enabling Ronan to be defeated."
Reasoning: Ronan reached Xandar → arrived. Attacking "the planet" is not a person. The defenders fought Ronan: the groups name members in the window (Garthan Saal of the Nova Corps; Groot, Peter Quill, Rocket Raccoon of the Guardians) → one row per named member; the Ravagers name none → group row. Rank "Denarian" stripped. "enabling Ronan to be defeated" → no doer stated → no defeated row.
Answer: {"events": [{"quote": "Ronan the Accuser led his forces to Xandar", "subject": "Ronan the Accuser", "verb": "arrived", "object": "Xandar"}, {"quote": "the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers", "subject": "Garthan Saal", "verb": "fought", "object": "Ronan the Accuser"}, {"quote": "the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers", "subject": "Groot", "verb": "fought", "object": "Ronan the Accuser"}, {"quote": "the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers", "subject": "Peter Quill", "verb": "fought", "object": "Ronan the Accuser"}, {"quote": "the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers", "subject": "Rocket Raccoon", "verb": "fought", "object": "Ronan the Accuser"}, {"quote": "the planet was defended by an alliance of the Nova Corps, the Guardians of the Galaxy, and the Ravagers", "subject": "Ravagers", "verb": "fought", "object": "Ronan the Accuser"}]}

**Example 8** — Page: Roxy Glass / Joining the Deke Squad
Window (excerpt): "Shaw consistently visited a young boy named Alphonso Mackenzie, who Glass assumed to be the older Mackenzie's son. ... Shaw took Mackenzie to the Lighthouse, where the Deke Squad huddled and Glass assured the team that they could impress Mackenzie. However, the demonstration went wrong, and Ronnie Chang accidentally shot Glass with a paintball. Mackenzie was not impressed and scolded Shaw for forming the team, resolving to leave."
Reasoning: "visited" → met. "took Mackenzie to the Lighthouse" → both arrived (a proper-named place). Chang's shot was an accident between teammates → no fought. Scolding → no row. "resolving to leave" → intention → no departed.
Answer: {"events": [{"quote": "Shaw consistently visited a young boy named Alphonso Mackenzie", "subject": "Shaw", "verb": "met", "object": "Mackenzie"}, {"quote": "Shaw took Mackenzie to the Lighthouse", "subject": "Shaw", "verb": "arrived", "object": "Lighthouse"}, {"quote": "Shaw took Mackenzie to the Lighthouse", "subject": "Mackenzie", "verb": "arrived", "object": "Lighthouse"}]}

**Example 9** — Page: Korg / Trip to Omnipotence City
Window: "When plotting on how to get the Thunderbolt, Zeus overheard somebody talking, which led to Korg directly calling out his own friends. When Thor was brought forth to Zeus, the three had to watch as Thor was chained down and stripped naked, forcing Korg, Foster and Valkyrie to take off their own disguises, revealing them as Asgardians. After Thor got his robe back on, Korg aided his friends to battle Zeus and his Spartan guards."
Reasoning: "brought forth to Zeus" → Thor met Zeus. "Thor was chained down" is passive and the window never says who chained him → no captured row (never supply a doer). "Korg aided his friends to battle Zeus" → the friends are named (Thor, Foster, Valkyrie) → each fought Zeus, plus Korg. "his Spartan guards" → unnamed → no row.
Answer: {"events": [{"quote": "When Thor was brought forth to Zeus", "subject": "Thor", "verb": "met", "object": "Zeus"}, {"quote": "Korg aided his friends to battle Zeus and his Spartan guards", "subject": "Korg", "verb": "fought", "object": "Zeus"}, {"quote": "Korg aided his friends to battle Zeus and his Spartan guards", "subject": "Thor", "verb": "fought", "object": "Zeus"}, {"quote": "Korg aided his friends to battle Zeus and his Spartan guards", "subject": "Foster", "verb": "fought", "object": "Zeus"}, {"quote": "Korg aided his friends to battle Zeus and his Spartan guards", "subject": "Valkyrie", "verb": "fought", "object": "Zeus"}]}

**Example 10** — Page: Ambush on Erik Killmonger / Background
Window: "Rhodes arrived at the Salvage Yard to secure the deal with Klaue, however, it was interrupted by the arrival of Black Panther, as Klaue leaked the information to the War Dogs. After taking down Klaue's henchmen, Black Panther attempted to reason with Rhodes that he only needed to retrieve the stolen vibranium, only for them to be ambushed by Killmonger. Killmonger killed both T'Challa and Rhodes which destabilized the political climate between the United States and Wakanda."
Reasoning: Black Panther = T'Challa (both names in the window → the real name everywhere). Rhodes arrived Salvage Yard; T'Challa's arrival → arrived, and met the people there (Rhodes, Klaue). Henchmen unnamed → no row. Ambushed → Killmonger fought both; then killed both.
Answer: {"events": [{"quote": "Rhodes arrived at the Salvage Yard", "subject": "Rhodes", "verb": "arrived", "object": "Salvage Yard"}, {"quote": "it was interrupted by the arrival of Black Panther", "subject": "T'Challa", "verb": "arrived", "object": "Salvage Yard"}, {"quote": "it was interrupted by the arrival of Black Panther", "subject": "T'Challa", "verb": "met", "object": "Rhodes"}, {"quote": "it was interrupted by the arrival of Black Panther", "subject": "T'Challa", "verb": "met", "object": "Klaue"}, {"quote": "only for them to be ambushed by Killmonger", "subject": "Killmonger", "verb": "fought", "object": "T'Challa"}, {"quote": "only for them to be ambushed by Killmonger", "subject": "Killmonger", "verb": "fought", "object": "Rhodes"}, {"quote": "Killmonger killed both T'Challa and Rhodes", "subject": "Killmonger", "verb": "killed", "object": "T'Challa"}, {"quote": "Killmonger killed both T'Challa and Rhodes", "subject": "Killmonger", "verb": "killed", "object": "Rhodes"}]}

**Example 11** — Page: 2012 / 22nd
Window: "The car flips and sends Reyes flying through the air, as he prays to anyone to keep his brother safe. Reyes is killed on impacting the ground and Gabe loses control of his legs. However, Johnny Blaze, Ghost Rider, contacts Robbie's soul and asks if he wants Gabe to live, in which Reyes responds yes. Soon after, Blaze pulls Gabe to safety and revives Reyes by transforming him into the next Ghost Rider."
Reasoning: the death has no doer → no killed row. Contacting a soul and talking → no meeting row. "pulls Gabe to safety" → saved. "revives Reyes" → Reyes awakened (revival; the revived one is the subject).
Answer: {"events": [{"quote": "Blaze pulls Gabe to safety", "subject": "Blaze", "verb": "saved", "object": "Gabe"}, {"quote": "revives Reyes by transforming him into the next Ghost Rider", "subject": "Reyes", "verb": "awakened", "object": null}]}

**Example 12** — Page: Prince / May's STRIKE Team (a descriptive-looking window that is narrative)
Window: "Prince and May's Team followed Daisy Johnson to a warehouse where Tucker Shockley and other Watchdogs were hiding. Using I.C.E.R.s they caught them all. On Zephyr One, Prince was watching the cuffed Watchdogs while Johnson was interrogating Shockley. He and Davis then hold Shockley as he talked to Mace and Johnson. Suddenly twang was heard and Fitz and Simmons hurried to warn them that Shockley was the bomb. Johnson said to Prince and Davis to move and knocked out Shockley with her powers."
Reasoning: "a warehouse" → description → no arrived. "they caught them all" → Prince (named) captured Shockley (named); other Watchdogs unnamed. One name per person: "Shockley". Interrogating/holding a prisoner already captured → no new row. "knocked out Shockley" → Johnson defeated Shockley.
Answer: {"events": [{"quote": "Using I.C.E.R.s they caught them all", "subject": "Prince", "verb": "captured", "object": "Shockley"}, {"quote": "knocked out Shockley with her powers", "subject": "Johnson", "verb": "defeated", "object": "Shockley"}]}
