# How to label one wiki window — schema v2 (event layer + fact layer)

> **This is the system prompt for the v2 labeller** (`tools/train/label_single.py --schema v2`).
> Owner 2026-10-07; scope: everything in `plan/FACT_LAYER_COUNCIL_BRIEF.md` §D as amended by the
> committed council verdict `plan/FACT_LAYER_COUNCIL.md`.
>
> **The owner complained that the 12-verb filter silently DROPS real plot facts** — "Hope trained
> Scott" produced no row, so a brain answering "who trained Ant-Man?" could not get it. v2 keeps the
> event layer EXACTLY as it was and adds a **fact layer** beside it, so that every narrated line
> produces a row or an explicit allowed reason why not.
>
> **SECTION A below is a verbatim copy of `plan/EXTRACTION_PROCEDURE.md`.** The event layer does not
> change in v2. `tests/test_fact_layer.py::test_event_section_is_verbatim` fails if the two ever
> drift, so if Claude edits the event procedure, re-copy SECTION A.

Answer with JSON only, no prose, no code fences. Think through the steps privately, then answer in
exactly this shape:

```
{"events": [{"quote": "...", "subject": "...", "verb": "...", "object": "... " or null}],
 "facts":  [{"quote": "...", "subject": "...", "relation": "...", "object": "...", "modality": "actual",
             "certainty": "stated", "asserted_by": null, "canon": null}],
 "tags":   [{"quote": "...", "tag": "..."}]}
```

- `events` — the 12-verb layer, SECTION A. Unchanged. `{"events": [], "facts": [], "tags": []}` is a
  correct answer for a window that states nothing at all (a bare list header, a dialogue page).
- `facts` — the new layer, SECTION B. One row per non-event fact the window states.
- `tags` — SECTION C. One row per sentence you deliberately did NOT turn into a row, with the
  allowed reason. Tags are the escape hatch that makes the coverage rule honest; never use a tag to
  silence a fact you could have written.

A window can have facts and no events ("Hope was tasked with training Scott Lang"), events and no
facts, or both. They are independent: **write an event row AND a fact row when the text states
both** (e.g. "Hope punched Scott during the lesson" = `fought` event AND `trained` fact).

---

# SECTION A — THE EVENT LAYER (unchanged)

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


---

# SECTION B — THE FACT LAYER (new in v2)

A **fact row** is anything the passage states about the world that the 12 verbs cannot express:
relationships, teaching, communication, orders, possessions, identity, states of being, knowledge.
The event layer asks *"what act happened?"*; the fact layer asks *"what is true of whom?"*.

Write a fact row for EVERY such statement, including the ones the event layer deliberately drops.
This is the whole point of v2: a dropped fact was the owner's complaint.

An event the 12 verbs express STAYS an event. Do not move it into facts, and do not write both:
a `fought` row never gets a fact twin with relation `attacked`; an `arrived` row never gets
`located_at` for the same move. The two layers partition the text.

## B.1 The row shape

| field | required | meaning |
|---|---|---|
| `quote` | yes | copied **word for word** from the passage, ≥12 chars, **inside ONE sentence** (never a paragraph, never two sentences) |
| `subject` | yes | the one the fact is about, written as the passage's fullest form for that entity |
| `relation` | yes | one of the vocabulary in B.2, or `other_verb` (B.3) |
| `object` | yes | the other end. May be a person, a named group, an item, a place, an organisation, a title, or `null` when the relation takes no object (`gained_power`, `learned`, `died`, `other_verb` with no object) |
| `modality` | yes | closed enum: `actual`, `planned`, `attempted`, `ordered`, `claimed`, `dreamed`, `hypothetical` |
| `certainty` | yes | closed enum: `stated`, `reported`, `apparent`, `denied` |
| `asserted_by` | when `modality != "actual"` | the **named character** who claimed/planned/ordered/imagined it. Never `null` when modality is not `actual` |
| `canon` | no | `mcu`, `comics`, `alternate`, `anime`, `production`, or `null` when the passage does not say |

`object` may be a place, item or organisation **even though the event layer forbids that** — that
rule exists because `fought`/`arrived` need person ends; a fact about a place is normal
(`resides_at`, `located_at`, `holds`, `destroyed`).

## B.2 The relation vocabulary (closed list; use `other_verb` for anything else)

**relationship** — `trained`, `mentored`, `recruited`, `allied_with`, `joined`, `left_group`,
`member_of`, `leader_of`, `friend_of`, `rival_of`, `parent_of`, `child_of`, `sibling_of`,
`married`, `dated`, `married_to`
**interaction** — `helped`, `assisted`, `protected`, `contacted`, `warned`, `persuaded`, `tricked`,
`ordered`, `hired`, `paid`, `gave`, `took`, `attacked`, `interrogated`, `apologised_to`, `greeted`
**possession / creation** — `created`, `built`, `stole`, `used`, `destroyed`, `owns`, `handed`,
`wielded`, `wore`, `piloted`
**identity** — `alias_of`, `disguise_as`, `revealed_as`, `codename_of`, `also_known_as`, `real_name_of`
**state / change** — `gained_power`, `lost_power`, `transformed_into`, `became`, `resides_at`,
`located_at`, `dies`, `born`, `aged`, `wounded`, `healed`, `kidnapped`
**knowledge** — `learned`, `revealed`, `discovered`, `forgot`, `remembered`, `suspected`

Two rules that decide most rows:

- **`trained` vs `fought`.** A lesson or a practice bout is `trained`, never `fought`. Sparring
  between allies is not a conflict (catalog A71). If the passage says "Hope punched Scott while
  teaching him", write the `fought` event **and** the `trained` fact — both are true and they are
  different claims.
- **`joined` / `allied_with` vs `met`.** Joining a team is not a meeting (R4/R12). A `joined` fact
  records it; the event layer correctly has no `met` row for it. "Sif joined Coulson and May where
  they already were" IS a meeting — that is a `met` event *and* a `joined` fact.

## B.3 `other_verb` (the escape hatch)

If a statement is a real fact but no listed relation fits, use `"relation": "other_verb"` and put the
actual verb of the passage in `object` — e.g.
`{"subject": "Hope van Dyne", "relation": "other_verb", "object": "trained", ...}` only if `trained`
were absent; normally the verb itself is the relation.

- The `other_verb` **verb must appear literally in the `quote`**.
- `other_verb` rows are real facts and are kept, but they are a **vocabulary-failure signal**: they
  are logged and reviewed so recurring verbs get promoted into the list. Aim for **fewer than 10%**
  of your fact rows.
- Never use `other_verb` to avoid choosing between two listed relations.

## B.4 Modality — the rule that replaces the event layer's "did it happen?" drop

v1 step 3 DROPPED plans, orders, claims, dreams, hypotheticals. v2 keeps them, **labelled**:

| passage | modality | asserted_by | certainty |
|---|---|---|---|
| "Van Dyne had been tasked with training Lang" | `actual` (the task happened) | — | `stated` |
| "Van Dyne planned to train Lang" | `planned` | `Van Dyne` | `stated` |
| "Loki ordered the Destroyer built" | `ordered` | `Loki` | `stated` |
| "Stane claimed he had been working with A.I.M." | `claimed` | `Stane` | `denied` (he was lying) or `reported` |
| "The Watcher dreamed of a world where…" | `dreamed` | `The Watcher` | `apparent` |
| "If he had trained harder he could have won" | `hypothetical` | `null` allowed here | `apparent` |
| "He tried to open the portal" | `attempted` | — | `stated` |

**A non-`actual` row is never world-truth.** It is what someone said, wanted, ordered or imagined.
That distinction is the entire reason for the field: without it the brain asserts Loki's lies.

## B.5 Certainty

`stated` (the passage states it flatly) · `reported` (someone reports it, and it may well be true) ·
`apparent` ("seemingly slew", "presumably died" — the passage hedges) · `denied` (the passage says it
is not so). Use `apparent` rather than dropping a hedged event: "the team seemingly slew Arnim Zola"
is `defeated` (event) with `certainty: apparent`, not `killed`.

## B.6 Ends: what may be subject or object

**Allowed:** a named character, a named group (Avengers, Hydra, S.H.I.E.L.D.), an item or weapon by
name, a proper-named place, an organisation, a title/role ("the President", "Ronan the Accuser"), a
definite description of one specific individual ("Hope's mother").

A **named group or organisation is written as the passage writes it, article included**: "the
X-Men", "the Avengers", "the FBI" are legal ends for `joined` / `member_of` / `left_group`. What
makes an end an indefinite is that it names nobody — "a Space Phantom", "an assailant", "the
squad" — and those stay refused. (The gate accepts an article-prefixed end only when the wiki
knows it as a real page.)

**Not allowed** (same rule as the event layer, R11): crowds ("the guards", "several Avengers",
"his men"), species/races ("the Kree", "Skrulls", "mutants"), indefinite descriptions ("a man",
"an assailant"), bare pronouns ("she", "they", "him") — see B.7.

Write one person with **one name** throughout, the passage's fullest form: if the passage writes both
"Iron Monger" and "Stane", use **Stane** in every row. Strip ranks: "General Werner Reinhardt" →
"Werner Reinhardt". For a revealed identity write the **revealed/real** name: "Valkyrie was
revealed to be Enchantress" → `Enchantress`.

## B.7 Coreference (a hard rule, because fact rows expose pronouns)

Event rows can hide a pronoun inside the quote; a fact row must name it. **Resolve every pronoun,
possessive and "they" to a named entity before writing the row.**

- "he had kidnapped Maya Lopez's relatives" → the one responsible is the subject the sentence makes
  responsible, not the one nearest the pronoun.
- "Loki was pruned by Ravonna Renslayer" → `Renslayer` sealed `Loki`; "she and Strange landed in
  Earth-838" → "she" is **Chavez**, the one who opened the portal.
- If you genuinely cannot resolve it from the passage alone, **do not write the row**. Do not supply
  the answer from outside knowledge of the series.

## B.8 Items, places, aliases, membership, production

- **item:** `Scott Lang used the Ant-Man Suit` → `{subject: Scott Lang, relation: used, object: Ant-Man Suit}`. Items are legal fact ends.
- **place:** `Van Dyne resides at` / `The fight occurred_at San Francisco` → `{subject, relation: resides_at, object: San Francisco}`. A description-place ("his apartment", "the Bus", "the mansion") is legal for `resides_at` / `located_at` but the passage's wording must be the object.
- **alias / disguise:** keep them apart. "Valkyrie alias of Enchantress" is permanent identity; "Valkyrie disguise_as Enchantress" is a temporary deception. A reveal writes `revealed_as`.
- **membership:** a group with named members gets the members' rows **plus** `X member_of Group`. `member_of` may carry the time in the quote, not in a field.
- **production:** behind-the-scenes notes, trivia, cast lists, release dates and credits are real facts too, but they are **not plot**. Give them `"canon": "production"` so they never contaminate a plot answer.

## B.9 What is still not a fact row

- **Dialogue in quotation marks.** Only the narrator's sentences state facts. `"I trained him," she
  said` is dialogue: tag it (`dialogue`), and if the narrator's own sentence already states the fact,
  write that row.
- **List furniture, headers, table rows, infobox lines** — tag them (`list_header`).
- **A general ability, not an occurrence.** "She can overpower most opponents" is a description, not
  an event; it is also not a fact about something that happened, so tag it (`attire`/`list_header`
  family is wrong — use `capability`) unless the passage states a specific occurrence.
- **Purely transitional text** ("The following day", "Meanwhile") — tag `deictic`.
- **Real people** (actors, writers, directors) as *plot* subjects. They are legitimate subjects for
  `canon: production` facts only.

---

# SECTION C — THE COVERAGE RULE

> Every **narrative sentence** must be covered by ≥1 event row or ≥1 fact row, or carry exactly one
> `tags` row with an allowed reason. Coverage is how the owner gets a *complete* brain instead of a
> filtered one.

Allowed tags (closed set — nothing else is accepted):

| tag | use for |
|---|---|
| `dialogue` | text inside quotation marks (a Quote page, a spoken line) |
| `list_header` | a heading, a list entry, a table row, a bullet, an infobox line |
| `production` | behind the scenes, trivia, cast/crew, release dates, credits |
| `citation` | a footnote, a reference marker, a source line |
| `apposition` | "Hope van Dyne, the Yellowjacket, ..." restating an identity already written |
| `attire` | clothing/appearance description ("wearing his helmet") |
| `capability` | a general ability/power description, not a specific occurrence |
| `deictic` | transitional text with no claim ("the next morning", "meanwhile") |
| `below_floor` | shorter than 6 words and naming no entity |
| `no_doer` | a passive with no "by" ("where he was defeated", "were freed"), an item as the doer ("killed by a Stark missile"), someone tied up with no captor |
| `crowd_end` | every end is a crowd, species, indefinite or descriptive group ("the squad", "several Avengers", "the Inhumans", "an assailant") |
| `no_relation` | the sentence states something real, but no event verb and no fact relation can say it (the Watcher observing a universe, "terminated the record", an attack on a building) |

**Write the `quote` of a tag row as the exact sentence (or the exact list entry) you did not cover.**

Two rules that keep this honest:

1. **A tag is never a way to avoid work.** If you can state the fact, state it. A window full of tags
   is a failed window, and coverage is checked per window. The three new tags exist for the
   sentences the catalog names (`plan/BIG_REVIEW_PATTERNS.md`): use `no_relation` only for a ruling
   the catalog names — if you simply cannot think of a relation, keep looking or use `other_verb`.
2. **One sentence may carry several rows.** "Hope trained Scott and later fought him" = one `trained`
   fact, one `fought` event, one `met` event. Covering a sentence with one row does not license
   dropping the others.

---

# SECTION D — WORKED EXAMPLES (real reviewed windows)

## Example 1 — the owner's own case: sparring that v1 threw away (catalog A71)

Passage: "Van Dyne had been tasked with training Scott Lang on how to fight with the Ant-Man Suit to
cause the most effective but non-lethal damage. Lang initially scoffed at the idea as he claimed that
his three years in prison had taught him how to fight and to prove this he punched van Dyne but she
easily blocked the attack and called him out for the poor attempt. Lang challenged her to show him
how to punch, which she did by easily punching him in the face despite his attempts to block. Lang
accepted van Dyne's help after this and together, they trained hard, fighting each other without
holding back until van Dyne was satisfied with his abilities."

Reasoning: v1 produced ONE row — `Scott Lang fought Van Dyne` — and the review deleted it (A71:
practice, not conflict). v2 keeps the training as facts. The practice bouts are `trained`, not
`fought`; "she easily punched him" and "Lang punched van Dyne" are real attacks inside a lesson, so
they are events, each pair written once.

Answer:
```
{"events": [{"quote": "he punched van Dyne but she easily blocked the attack", "subject": "Scott Lang", "verb": "fought", "object": "Van Dyne"},
            {"quote": "she did by easily punching him in the face", "subject": "Van Dyne", "verb": "fought", "object": "Scott Lang"},
            {"quote": "she did by easily punching him in the face", "subject": "Van Dyne", "verb": "defeated", "object": "Scott Lang"}],
 "facts":  [{"quote": "Van Dyne had been tasked with training Scott Lang", "subject": "Van Dyne", "relation": "trained", "object": "Scott Lang", "modality": "actual", "certainty": "stated"},
            {"quote": "together, they trained hard, fighting each other without holding back", "subject": "Van Dyne", "relation": "trained", "object": "Scott Lang", "modality": "actual", "certainty": "stated"},
            {"quote": "Lang accepted van Dyne's help after this", "subject": "Scott Lang", "relation": "mentored", "object": "Van Dyne", "modality": "actual", "certainty": "stated"},
            {"quote": "his three years in prison had taught him how to fight", "subject": "Scott Lang", "relation": "other_verb", "object": "taught", "modality": "claimed", "certainty": "denied", "asserted_by": "Scott Lang"}],
 "tags":   []}
```

## Example 2 — joining a team (R4/R12) and a remote call (A67)

Passage: "Slattery was later brought onto the new podcast Bad Actors, with the assurance that focus
would be on his upcoming role as Barnaby in Wonder Man rather than his past as the Mandarin. Slattery
joined the podcast remotely and greeted host Ben Mankiewicz after Mankiewicz finished introducing the
podcast. Mankiewicz started by asking what life was like for him in prison."

Reasoning: v1 produced **nothing** — a remote appearance is not a `met` (A67). v2 records the joining
and the greeting as facts. "would be on his upcoming role" is a plan → `planned` with `asserted_by`.

Answer:
```
{"events": [],
 "facts":  [{"quote": "Slattery was later brought onto the new podcast Bad Actors", "subject": "Slattery", "relation": "joined", "object": "Bad Actors", "modality": "actual", "certainty": "stated"},
            {"quote": "Slattery joined the podcast remotely and greeted host Ben Mankiewicz", "subject": "Slattery", "relation": "contacted", "object": "Ben Mankiewicz", "modality": "actual", "certainty": "stated"},
            {"quote": "Slattery joined the podcast remotely and greeted host Ben Mankiewicz", "subject": "Slattery", "relation": "greeted", "object": "Ben Mankiewicz", "modality": "actual", "certainty": "stated"},
            {"quote": "with the assurance that focus would be on his upcoming role as Barnaby", "subject": "Slattery", "relation": "became", "object": "Barnaby", "modality": "planned", "certainty": "reported", "asserted_by": "Slattery"}],
 "tags":   [{"quote": "Mankiewicz started by asking what life was like for him in prison", "tag": "dialogue"}]}
```

## Example 3 — a plan, an order and a hedged death (step 3, A11)

Passage: "After a clash with Iron Cross, U-Man, Master Man, and Warrior Woman, the team seemingly
slew Arnim Zola and destroyed his rocket containing the virus. Realizing the villagers had been
infected and they could spread the virus all over town, the Invaders made the tough decision to kill
all the villagers."

Reasoning: "seemingly slew" → the fight ended, no stated death → `defeated` (A11). "made the tough
decision to kill" is an intention, so it is a `planned` fact with `asserted_by` — v1 dropped it
entirely, which is exactly the loss the owner objected to. Two ends here are **not** legal:
"the team" and "the villagers" are crowds (B.6), and `killed` is not a fact relation — it is an
EVENT verb (B.2). So both extra statements use `other_verb`, whose `object` is the passage's own
verb (B.3), with the named Invader the window ties the act to as the subject.

Answer:
```
{"events": [{"quote": "After a clash with Iron Cross", "subject": "Bucky", "verb": "fought", "object": "Iron Cross"},
            {"quote": "the team seemingly slew Arnim Zola", "subject": "Bucky", "verb": "defeated", "object": "Arnim Zola"}],
 "facts":  [{"quote": "the team seemingly slew Arnim Zola", "subject": "Bucky", "relation": "other_verb", "object": "slew", "modality": "actual", "certainty": "apparent"},
            {"quote": "the Invaders made the tough decision to kill all the villagers", "subject": "Bucky", "relation": "other_verb", "object": "kill", "modality": "planned", "certainty": "stated", "asserted_by": "Bucky"}],
 "tags":   []}
```

## Example 4 — a disguise reveal and a group with named members (R10, G.2)

Passage: "Returning to the Avengers Mansion, the Wasp was surprised to find it occupied by the
Liberators, an all-female group led by the powerful Valkyrie, who wished to bring male supremacy
down. ... The victorious Valkyrie led her team to overpower both groups, but was eventually revealed
to be Enchantress in disguise, causing the dissolution of the Liberators. She then manipulated Arkon
into joining her..."

Reasoning: one name per person — the reveal makes her **Enchantress** in every row (R10), but the
fact layer additionally records the identity itself with `revealed_as` and `alias_of`, which v1 threw
away. `disguise_as` is temporary, `alias_of` is permanent; keep them apart. "led her team" → the
named members act, and `member_of` records the Liberators.

Answer:
```
{"events": [{"quote": "led her team to overpower both groups", "subject": "Enchantress", "verb": "defeated", "object": "Wasp"}],
 "facts":  [{"quote": "was eventually revealed to be Enchantress in disguise", "subject": "Enchantress", "relation": "revealed_as", "object": "Valkyrie", "modality": "actual", "certainty": "stated"},
            {"quote": "was eventually revealed to be Enchantress in disguise", "subject": "Enchantress", "relation": "disguise_as", "object": "Valkyrie", "modality": "actual", "certainty": "stated"},
            {"quote": "an all-female group led by the powerful Valkyrie", "subject": "Enchantress", "relation": "member_of", "object": "Liberators", "modality": "actual", "certainty": "stated"},
            {"quote": "an all-female group led by the powerful Valkyrie", "subject": "Enchantress", "relation": "leader_of", "object": "Liberators", "modality": "actual", "certainty": "stated"},
            {"quote": "She then manipulated Arkon into joining her", "subject": "Enchantress", "relation": "tricked", "object": "Arkon", "modality": "actual", "certainty": "stated"},
            {"quote": "who wished to bring male supremacy down", "subject": "Enchantress", "relation": "other_verb", "object": "wished", "modality": "planned", "certainty": "stated", "asserted_by": "Enchantress"}],
 "tags":   []}
```

## Example 5 — a window that genuinely states nothing (hard empty)

Passage: a cast-list table ("Chris Hemsworth | Thor | 2011"), a quote page, a list of appearances.

Answer: `{"events": [], "facts": [], "tags": [{"quote": "Chris Hemsworth | Thor | 2011", "tag": "list_header"}]}`

---

# SECTION E — FINAL CHECK (do this every time, before answering)

Re-read the passage **sentence by sentence** and, for each sentence, point at the row or tag that
covers it:

1. **Coverage.** Every narrative sentence has an event row, a fact row, or a tag with an allowed
   reason. Sentences you skipped are the failure mode the owner is paying to fix — go back.
2. **Did I keep what v1 dropped?** training/teaching, joining and allying, calls and remote
   appearances, "helped", verbal defence, plans, orders, claims, orders, dreams, hypotheticals,
   hedged events. Each is a fact row now (B.4).
3. **Is every non-`actual` row carrying `asserted_by`?** A plan with nobody planning it is a bug.
4. **Is every quote verbatim, ≥12 characters, and inside ONE sentence?** A paragraph quote is a bug.
5. **Is every pronoun resolved** to a named entity (B.7)? Unresolvable → no row.
6. **One name per person**, ranks stripped, the revealed name after a reveal.
7. **Are crowds, species and indefinite descriptions absent from both ends** of every row?
8. **Did I avoid stretching the 12 verbs?** `fought` is still only a real attack (not a lesson, not
   friendly contact); `met` is still only people coming together (not joining a team, not a call).
9. **Are `other_verb` rows under 10%** of my facts, and does their verb appear in the quote?

---

<!-- F:BEGIN (generated by tools/train/build_prompt.py) -->

---

# SECTION F — THE REVIEW PATTERN CATALOG (served to every window)

These are the settled rulings from Claude's hand review of the big windows
(`plan/BIG_REVIEW_PATTERNS.md`). Roughly a quarter of them are also checked mechanically on your
repair turn (`big_flags.check()` fires on about 19 of the 72 codes); the rest are read by you,
and a ruling you break is corrected, so treat every line as binding.

**"no row" always means no row in `events`.** The sentence is still yours to record: write a
`facts` row when both ends are nameable, and when no end is nameable write a `tags` row from
this closed set — `no_doer` (a passive with no "by", an item as the doer, someone tied up with
no captor), `crowd_end` (crowd, species, indefinite or descriptive-group ends), `no_relation`
(stated, but with no legal event AND no legal fact). Where a ruling names a fact route, that
route IS the answer: e.g. A71 sparring -> no `fought`, but `trained` as a fact. An event-layer
ruling never justifies deleting a fact or tag row.

A-patterns: what your row must have been. G/R: structural rules for every row you write.

- **A1** — add the row
- **A2** — one row per tied member, no group row
- **A3** — no met; fact: `joined` (or `allied_with`), actual
- **A4** — the real / revealed name in every row
- **A5** — drop the row (or the named member if one is tied)
- **A6** — met
- **A7** — sealed
- **A8** — no row
- **A9** — strip rank; fullest form; no article
- **A10** — no arrived/departed
- **A11** — per hedge
- **A12** — no saved; fact: `helped` (or `assisted`), actual
- **A13** — no betrayed (departed if a named place); fact: `left_group` when a named person leaves a named group, else `other_verb` with the passage's verb
- **A14** — re-resolve by meaning
- **A15** — the full name
- **A16** — X
- **A17** — no row (gate refuses subject==object)
- **A18** — separate ends ("Variant" vs "Loki")
- **A19** — only the part that happened (arrived), no met/fought; the purpose clause is a fact: `planned`/`claimed` with `asserted_by` when both ends are nameable
- **A21** — possessor fought the host and the victim; no killed when he survived
- **A22** — defeated
- **A23** — no row for the promised act; the promise itself is a fact: `planned`/`claimed` with `asserted_by`
- **A24** — no arrived/departed
- **A25** — no row
- **A26** — re-resolve by meaning
- **A27** — no met
- **A28** — X captured Z too (the one who had it done)
- **A29** — defeated
- **A30** — no row
- **A31** — no row (R4 + purpose); facts: `joined` (actual) plus the task as `planned`/`ordered` with `asserted_by`
- **A32** — fought rows (step 1: one specific occurrence is an event)
- **A33** — also X saved him (revived someone who would otherwise die) — only when the revival is for his sake (Merlyn); a corpse revived as a tool or a threat (the Mad Thinker's "living weapon", Cable reviving Apocalypse) is no saved
- **A48** — team/side -> no met (R4); people where they are -> met; team/side -> fact `joined`; people where they are -> `met` event AND `joined` fact
- **A34** — met each person reached + saved
- **A35** — write it (met/fought, saved): the PURPOSE flag is a prompt, check the following sentence
- **A36** — no row; fact: `warned` or `persuaded`, actual
- **A37** — captured (brought as a prisoner)
- **A38** — defeated
- **A39** — no row (an item is never the doer; its user is unnamed)
- **A40** — fought (an attack made)
- **A41** — re-resolve by meaning (heroes = the ones with powers)
- **A42** — no fought (an attack on a vehicle/building only)
- **A43** — met
- **A44** — betrayed + fought (table: betrayed YES "turned on")
- **A45** — no met; met only those who see him ("could see him")
- **A46** — only those still present
- **A47** — no captured (R17, example 9)
- **A49** — rows with the revealed name (R10)
- **A50** — the captor is the object; the place only when no captor is named
- **A51** — each arrived + met per pair (a meeting held between them)
- **A52** — no row (indefinite)
- **A53** — fought the host; a body destroyed with the character surviving -> defeated
- **A54** — betrayed (broke faith) — unlike plain leaving (A13), which is no betrayal
- **A55** — defeated (the fight ended; no capture stated)
- **A56** — defeated (thrown off ends the fight, as "pushed him off the truck")
- **A57** — the named members the window ties to the act, else no row
- **A58** — met (an encounter that stops him)
- **A59** — the real name only ("Scott Summers")
- **A60** — no killed (an ordered killing; the table excludes the order-giver); fact: `ordered` + `asserted_by` (order-giver and intended victim)
- **A61** — saved stays (helping an escape from captivity is a release, as b21 Carol Danvers); R23 covers only help with non-danger
- **A62** — saved
- **A63** — X fought the targets (as "Luke Cage's team" -> Luke Cage)
- **A64** — Y fought Z (the sender only ordered it); fact: the sender `ordered` + `asserted_by`
- **A65** — no arrived (not a proper-named place); fact: `member_of` (or `joined`) when a named person joins it
- **A66** — betrayed the team (a mole breaks faith with the team she is in)
- **A67** — no met; fact: `contacted` and/or `greeted`
- **A68** — the last two named
- **A69** — killed (a named robot/AI destroyed)
- **A70** — X sealed the named ones trapped (a barrier); deactivating it = saved
- **A71** — no row (practice, not a conflict); fact: `trained`/`mentored` — a real punch inside the lesson still gets its `fought` event
- **A72** — betrayed only the ally (A)
- **A73** — no arrived (an event is not a place); arrived only when the named place itself is stated
- **A74** — defeated (the fight ended with X beaten, as A55 "stopped"); plus X escaped the one who forced it
- **A75** — fought the attacker AND saved the one protected (an intercepted attack)
- **A76** — fought the intended target (an attack made); no row for the ally hit by accident
- **A77** — the whole name ("Agent 33")
- **A78** — arrived the proper place only ("Earth-691")
- **A79** — no arrived (not a new place reached)
- **A80** — no row (a form he already had)
- **A81** — no row (knowledge of how, not the act)
- **A82** — captured too (a hostage taken)
- **A83** — fought (+ met for the encounter); defeated only when the fight ends
- **A84** — the one who ran: escaped, not defeated
- **A85** — the one manipulated is the betrayer (object = the friends; none if unnamed); the manipulator gets no betrayed
- **A86** — the restored machine is the awakened one; the restorers get no awakened
- **A87** — "fought with X" next to a common enemy = alongside X: rows against the enemy, none between allies
- **A88** — the passage's own verb word, literally in the quote ("hostilized", "told", "thanked")
- **A89** — the event row only; no twin fact row
- **A90** — one row per named part
- **A91** — `contacted` only for calls, messages and remote links; in person = the met event (or no row)
- **A92** — `allied_with` (joined is for a group/team/organisation)
- **A93** — the doer of the passive "by X" is the subject
- **A94** — no fact row; tag the sentence `crowd_end`
- **A95** — resolve by meaning (who speaks to whom)
- **A96** — `actual`: only an act the passage says did not (yet) happen is planned/attempted
- **A97** — `gave` takes the recipient ("Koenig gave Ward"); `handed` takes what was handed (the person/item), never the receiving body
- **A98** — no fact; tag `production` (release-date lists `list_header`)
- **A99** — one row; `alias_of` subject = the alias/codename, object = the real person
- **A100** — one name per person in every row (A4/A9), plus one `alias_of` row when the window states the alias
- **A101** — a fact row with the passage's own verb (`other_verb watches`); tags only when no nameable doer exists
- **A102** — the event row only (A89)
- **A103** — the "thanks to/by" party is the subject: Fantastic Four defeated Frightful Four; Norriss saved Slattery
- **A104** — helped/allied_with only; a fought row needs a named opponent
- **A105** — `victim
- **A106** — no event; `awakened` is a return from death or stasis
- **A107** — no event or fact for the person; the impostor gets the row under its own name or a `no_doer` tag
- **A108** — `ordered` takes the PERSON told to act; otherwise `other_verb` with the passage's verb ("authorized", "demanded")
- **A109** — no `arrived` row until the passage says they got there
- **A20** — the definite description ("Lang's father")

<!-- F:END -->