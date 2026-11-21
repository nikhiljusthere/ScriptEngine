# A01 adjudication: fix and unsure windows

## b39 (Fantasia Arc / Paradise and Pandemonium): FIX

- S1: "Once the mass concludes, Griffith and his inner circle settle themselves in a gazebo to enjoy the tea and cake Charlotte made before Locus arrives with Rickert standing nearby on a small bridge."
- S2: "Parting from the others, Griffith meets Rickert for a private discussion."
- Gold has `Griffith|met|Rickert` and `Rickert|fought|Griffith`, and records Locus's arrival only as the fact `Locus|other_verb|arrives`.
- Proposed: `+ Locus|met|Griffith|before Locus arrives with Rickert standing nearby on a small bridge` and `f- Locus|other_verb|arrives`.
- Rule: table met YES "X arrived where Y was"; Addendum 6 says a named character who shows up where a named person is gets `met`, and the `met` replaces the `other_verb` fact (section B). Locus and Rickert came together, so there is no Locus-Rickert row. The inner circle is unnamed, so no other rows. The gazebo is a description place, so there is still no `arrived`.

## b29 (Episode 148 (Manga) / Summary): UNSURE

- S2: "Before they can climb narrow path to the cave's exit, however, the goat-man charges once more, ramming Guts with its enormous horns, but the Black Swordsman manages to block the hit with the Dragon Slayer."
- Gold has no event and tags the clause `crowd_end`. The reviewer's note calls the goat-man an unnamed creature, so it gets no end.
- Possible row: `the goat-man|fought|Guts|the goat-man charges once more, ramming Guts with its enormous horns`. Step 6 makes a definite description of one specific individual an end ("the monster"), and a blocked attack is still `fought`.
- Why unsure: the reviewer made a deliberate ruling, it is unclear whether "goat-man" names one individual or a kind, and the event gate may refuse the end. The same question comes up at b195.

## b204 (Episode 205 (Manga) / Summary): UNSURE

- S2: "Morgan watches the boy walk off before noticing Guts standing behind him."
- S3: "He tells the Black Swordsman of his suspicions of Isidro admiring him, but Guts doesn't respond."
- Gold has no event, and the facts `Morgan|discovered|Guts` and `Morgan|other_verb|tells`. The second reader has `Guts|met|Morgan`.
- Why unsure: the two then talk in person, which reads like table met "found X with contact" or A132 "met for the finder". But table met NO lists "watching or noticing", Guts's arrival is never narrated, and the reviewer marked the window "ok".

## b214 (Flora / Abilities): UNSURE

- S3: "Her greatest display of magic was when she conjured a massive wall of fire to stop the apostles from chasing Guts' new party, a force which not even the \"Flame Dragon Knight\" Grunbeld had sway over."
- Gold has no event and the fact `Flora|other_verb|conjured`. The second reader has `Flora|saved|Guts`.
- Why unsure: A35 says a purpose clause is a prompt to check whether the act succeeded. The following clause implies the wall held, which would make it table saved "protected from harm". But the one protected is "Guts' new party", whose only named member here is Guts, and the rescue is implied rather than stated.

## b203 (Human / Falconia): UNSURE

- S2: "The ascent of a mercenary named Griffith, and his storied successes in Midland's wars against Tudor and the Kushan Empire, climaxes with the merging of the physical and astral realms and consequent influx of astral entities into the world of man."
- Gold has no event and tags the clause `no_relation`. The second reader has `Griffith|fought|Tudor` and `Griffith|fought|Kushan`.
- Why unsure: step 3 counts a past act told in passing, so `Griffith|fought|Tudor` and `Griffith|fought|Kushan Empire` are possible. But "war" is not in the fought table, the clause is a nominal summary, and the gold consistently treats wars between nations as no event (b133).

## b195 (Mayor of Koka / Black Swordsman Arc): UNSURE

- S1: "When he arrives, the Snake Lord welcomes him in a manner that elicits more fear from the mayor, prompting him to ask for forgiveness."
- Gold has no event and the fact `Snake Lord|other_verb|welcomes`. The reviewer's note says "the mayor" is unnamed, so he gets no end. The second reader has `Mayor of Koka|met|Snake Lord`.
- Possible row: `the mayor|met|Snake Lord|the Snake Lord welcomes him` (table met "was greeted by X"), written with the window's form "the mayor" (A130) and with the `welcomes` fact removed.
- Why unsure: step 6 allows a definite description of one specific individual as an end ("the old man"), but the reviewer ruled otherwise, and the gate may refuse "the mayor". This is the same question as b29.
