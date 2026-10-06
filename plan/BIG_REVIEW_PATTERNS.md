# Big-window review: error and confirm patterns

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
| A1 | missed event in a window that has other rows: rescues, escapes, "left the team", "found X", recruits, betrayal nouns ("Magik's betrayal"), attacks in passing ("having hurt Broo"), power/mind use ("brainwashed", "possessed", "manipulated by") | add the row | step 8.1, R8, R18 | most windows (82/125 needed additions) |
| A2 | group end ("Avengers", "X-Men", "the group") when the window ties named members to the event | one row per tied member, no group row | G.2, R19 | very common |
| A3 | met from joining/allying ("joined the team", "joining X and Y", "teamed up", "allied", "rejoined") | no met | R4, R12 | common |
| A4 | two names for one person in the window (codename + real name, alias pairs, disguise reveals "revealed to be", "posing as", "was really", "unmasked") | the real / revealed name in every row | step 6, R10 | common |
| A5 | crowd, indefinite or species end ("several Avengers", "former Avengers", "a Kree armada", "the police", "a Space Phantom", "Skrulls", "Inhumans", "Builders") | drop the row (or the named member if one is tied) | step 6, R11 | common |
| A6 | confrontation with no stated attack written as fought ("confronted Whirlwind", "confronted the robot Computo") | met | R2 | occasional |
| A7 | trapped in a dimension / other world written as captured ("imprisoned in Limbo", "ensnared in Mojoverse", "pocket universe", "forced through a portal") | sealed | R3, R13, R20 | occasional |
| A8 | passive with no doer filled from context ("where he was defeated", "were freed", "Moira being rescued", "arrested due to his connection to Orchis") | no row | step 4, R17 | occasional |
| A9 | rank/title or short form as the name ("Captain Stacy", "Dr. Ellis", "Shaw" when "Sebastian Shaw" is in the window, "Gaunt", "Burch", "the Reaper", "The Crippler") | strip rank; fullest form; no article | step 6 | occasional |
| A10 | description used as a place ("Reavers' Australian base", "the mansion" when unnamed) or heading as arrival ("while taking ... back to") | no arrived/departed | table: arrived | occasional |
| A11 | hedged or prevented acts ("seemingly slew" -> defeated, "attack ... was prevented" -> no fought, "nearly kill" -> fought) | per hedge | step 3 | occasional |
| A12 | "helped X when ..." written as saved | no saved | R23 | rare |
| A13 | leaving/disbanding written as betrayed ("abandoned him to die", "the Avengers were disassembled by") | no betrayed (departed if a named place) | R14, R24 | rare |
| A14 | wrong pronoun referent ("he had captured a Space Phantom" = Kang, not Immortus; "before he escaped the police" = Castle) | re-resolve by meaning | step 4 | rare, only reading catches it |
| A15 | broken end string ("X" for Professor X) | the full name | step 6 | rare |
| A16 | "<group> led by X" as doer | X | R21 | rare |
| A17 | self-directed death (suicide) | no row (gate refuses subject==object) | R16 | rare |
| A18 | two characters sharing a name merged ("the Variant" / "Variant Loki" ambushes while the TVA's Loki sits with B-15) | separate ends ("Variant" vs "Loki") | step 6 | rare, reading only |
| A19 | purpose clause as event ("traveled to NYC to meet with X", "planning to fight") | only the part that happened (arrived), no met/fought | step 3 | occasional |
| A21 | killing through a possessed body ("used his powers of body possession to cause Dolan to murder Craft") / a victim who "survived his own murder" | possessor fought the host and the victim; no killed when he survived | step 4, 3 | rare |
| A22 | "finishing off X" with no stated death written as killed | defeated | table: defeated | rare |
| A23 | deals and exchanges as events ("agreed to help in exchange for teleporting them all back") | no row for the promised act | step 3 | rare |
| A24 | a vehicle as a place ("carried Pixie to the Blackbird") | no arrived/departed | table: arrived NO "the car" | rare |
| A25 | a pantheon or race as an end ("the Kami", "the Olympians", "Sentinels", "Quantumnauts") | no row | step 6 | occasional |
| A26 | a reported confirmation misread for its speaker ("Gao confirmed that she had fought beside him ... before her death and later rebirth": she = Elektra) | re-resolve by meaning | step 4 | rare, reading only |
| A27 | the Watcher "visited"/"went to" a version of someone (What If narration = observing a universe) | no met | table: met NO watching | rare |
| A28 | "X had A and B abduct Z" written only for A and B | X captured Z too (the one who had it done) | table: captured | rare |
| A29 | "sedated him" / "knocked him out" written as fought | defeated | table: defeated | occasional |
| A30 | "terminating X" about a file/record (X alive later in the window) written as killed | no row | step 3 | rare |
| A31 | a self-assigned task as an event ("joined Daredevil's side and worked to stop Fisk") | no row (R4 + purpose) | step 3 | occasional |
| A32 | an abilities/powers section narrating specific hits ("shake off a punch from Gladiator", "has taken multiple punches from Namor") left empty | fought rows (step 1: one specific occurrence is an event) | step 1 | occasional |
| A33 | "X revived him" written only as awakened | also X saved him (revived someone who would otherwise die) | table: saved | occasional |
| A34 | a team member's own team as "met" target after rescuing/arriving ("arrived in time to save Daisy and May") missed | met each person reached + saved | table: met | occasional |
| A35 | a purpose clause that the next clause fulfils ("traveled to Genosha to confront Magneto ... In the resulting battle", "runs to save him ... stopping them both from falling") left out | write it (met/fought, saved): the PURPOSE flag is a prompt, check the following sentence | step 3 | occasional |
| A36 | "defended by X" in words (X told the accuser he was wrong) written as saved | no row | table: saved | rare |
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
| A20 | an unnamed relative resolved to a named one by outside knowledge ("saved by her father" -> Paxton, who is the stepfather) | the definite description ("Lang's father") | step 4/6 | rare, reading only |

## B. Confirm patterns (35B usually right; one look suffices)

- quote literally states subject-verb-object: "Stark defeated Bullski", "Thanos kidnapped Nebula and Starfox" (OK lines in big_flags)
- "Back to <named place>" / "returned to <named place>" -> arrived
- "found X" / "was greeted by X" / "visited X" / "reunited with X" -> met
- "attacked by X" / "battled X" -> X fought the object
- "X was murdered by Y" / "Y slew X" -> killed
- lists, credits, trivia, dialogue windows -> empty (still skim for one narrated occurrence)
- **The commonest residual error on OK rows is A4 (alias / disguise names) and A2 (group expansion).** Check those two even on OK rows.

## C. Exact duplicates

The same text appears on several sections/pages (b8=b23, b2=b33, b62=b88). big_flags prints
`DUP of bK (identical text)` with bK's final rows: reuse them and check only the differing tail.

## D. Gate quirks

- symmetric met/fought pairs are deduped by the gate; a correction with both "A met B" and
  "B met A" is refused with `dropped []` and `kept n-1/n`.
- "Rachel" is classed as a place: refused as an object (R22).
- item pages are refused as ends even when they act like characters: "the Destroyer" (armor), Cerebro (AI).
- subject == object is refused (R16).
- a place with a comma ("Washington, D.C.") is split by the gate into two rows (refused as `kept n+1/n`);
  write the most specific part ("Washington", R1).
