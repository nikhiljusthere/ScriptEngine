# A16 adjudication: fix and unsure windows

## Fixes

### b1637 (Ui Ui/Synopsis, Shibuya Incident Arc), fix
- s6: "Smallpox Deity tries to use his attack on Ui Ui, but it doesn't work since Ui Ui used simple domain to block the effects of Smallpox Deity's ability."
- Gold: `Smallpox Deity|sealed|Ui Ui` (s5) and the fact `Smallpox Deity|other_verb|use` (attempted). No fought.
- Proposed: `+ Smallpox Deity|fought|Ui Ui` and `f- Smallpox Deity|other_verb|use`. The attack was made and its effects were blocked.
- Rule: step 5, fought YES "any attack MADE on someone, even if blocked, dodged or failed"; section B (an event is never also a fact). fought next to sealed for one pair is normal in this gold (CAPT class).

### b1189 (Utahime Iori, Abilities and Powers), fix
- s3: "...Utahime was also fast enough to run in front of Kasumi Miwa to protect her from Kenjaku's point-blank Maximum: Uzumaki, with Momo Nishimiya immediately stating that Utahime shouldn't be in the frontlines."
- Gold: `Utahime|saved|Kasumi Miwa` only.
- Proposed: `+ Kenjaku|fought|Kasumi Miwa` (quote "protect her from Kenjaku's point-blank Maximum: Uzumaki").
- Rule: step 5 verb rules, "An interception is `fought` (attacker vs target) AND `saved`"; A75.

### b1252 (Vs. Mahito Arc, "I'm Gonna Kill You!"), fix
- s1: "Before Nanami is slain, Yuji breaks into the Domain from the outside."
- Gold: the fact `Yuji|other_verb|breaks`. No met.
- Proposed: `+ Yuji|met|Nanami` and `f- Yuji|other_verb|breaks`. Yuji arrives where his ally Nanami is. Saved is not proposed because the window never states the rescue.
- Rule: met table "X arrived where Y was"; Addendum 6 (a companion who shows up gets met, and the met replaces the other_verb fact); section B.

### b1107 (Vs. Mahito Arc, Underground Clash! Nanami VS Mahito), fix
- s1-2: "While Nanami struggles underground, Yuji and Ijichi track down Junpei skipping school." / "He's caught by his teacher, Sotomura, and Ijichi plans to use a fly-head curse to test Junpei's awareness."
- Gold: the fact `Sotomura|other_verb|caught`. No Sotomura-Junpei met.
- Proposed: `+ Sotomura|met|Junpei` and `f- Sotomura|other_verb|caught`. "He" is Junpei, whom the teacher comes upon.
- Rule: met table "found X" with contact; A93 (the doer of the passive "by X" is the subject); section B.

### b1638 (Yuji Itadori, Overview), fix
- s3: "...It was demonstrated again when Yuji resisted the effects of Eso and Kechizu's Decay.(Chapter 61, Episode 24)"
- Gold: `Yuji|fought|Junpei Yoshino` for the first occasion. For this one there is only the fact `Yuji|other_verb|resisted`, so the attack itself is unrecorded.
- Proposed: `+ Eso|fought|Yuji` and `+ Kechizu|fought|Yuji`. The resisted fact stays, because it records Yuji's own act.
- Rule: A32 (one specific occurrence is an event); A122; fought YES "a power or technique used ON someone".

### b1199 (Yuji Itadori vs. Yuta Okkotsu, Aftermath), fix
- s1: "Yuta takes Yuji's body to the area where the fight began and finds Naoya defeated by Choso."
- Gold: the fact `Yuta|other_verb|finds`. No met.
- Proposed: `+ Yuta|met|Naoya` and `f- Yuta|other_verb|finds`. Yuta-Choso stays defeated alone, since the encounter becomes the knockout (A145).
- Rule: met table "found X"; A132 (+ met for the finder); section B.

## Unsure

### b1621 (Sukuna/Synopsis, Culling Game Arc), unsure
- s4: "Ryu decided to confront Sukuna as the King of Curses asked if he was going to step aside.(Chapter 216) After effortlessly killing after a short one-sided scuffle, Sukuna spotted Yorozu noted how Sukuna has switched vessels..."
- Gold: no Ryu-Sukuna row. The confrontation is a planned fact. The killed victim is unnamed, which is right under A8.
- Open: Sukuna asks Ryu a question in person, which suggests they came together (met, table "confronted X"). The gold reads "decided to confront" as a plan (step 3). The supervisor decides.

### b1337 (Sukuna/Synopsis, Shinjuku Showdown Arc), unsure
- s5: "A massive net of Dismantle is already closing in to end his life.(Chapter 238)"
- Gold: `Sukuna|killed|Kashimo` on this sentence.
- Open: "closing in to end his life" may be a purpose or an impending act with no stated death. If so it is not killed (table killed NO "fatal blow without a stated death"; step 3 "to kill him"), and the existing fought row is enough. Kashimo's death is only narrated in the next window ("post-mortem fantasy").

### b1061 (Takako Uro/Synopsis, Culling Game Arc), unsure
- s1: "After Yuta sent Rika to occupy Ryu, he personally confronted Uro." s5: "She was then punched by Yuta and sent back to the area where Ryu and Rika were battling."
- Gold: no row for the Ryu-Rika battle, and no `Yuta|ordered|Rika`.
- Open: the battle is stated, but the rulings point three ways. It could be a plain `Rika|fought|Ryu`, an ordered act (Addendum 2: `Rika|other_verb|...|ordered|stated|Yuta` plus `Yuta|ordered|Rika`), or the master keeping the fought row (Addendum 5 / A63).

### b1439 (Time Cell Moon Palace, Usage), unsure
- s1: "Naoya expanded his domain for the first time when he was pushed to his limits as a vengeful cursed spirit while fighting Maki Zenin, Hagane Daido, and Rokujushi Miyo."
- Gold: the fact `Naoya|other_verb|expanded`. The second reader has `Naoya awakened`.
- Open: the awakened table includes "gained a new power ... for the FIRST time". This gold, however, writes first Domain Expansions as facts (b1609 gained_power), and A106 reads awakened as return from death or stasis plus regaining consciousness. This needs one decision covering b1439 and b1609.

### b1609 (Vs. Mahito Arc, "I'm Gonna Kill You!"), unsure
- s2-3: "This allows him to feel death's embrace and receive its inspiration." / "Staring his defeat in the eyes, Mahito goes beyond his limits and unleashes his very own Domain Expansion."
- Gold: `Mahito|gained_power|-` and `Mahito|other_verb|unleashes`. No awakened.
- Open: the same question as b1439 (first new power = awakened, or a fact). The `Mahito|defeated|Nanami` row follows the 2026-11-04 ruling and stands.

### b1210 (Toji Fushiguro/Synopsis, Gojo's Past Arc), unsure
- s1: "After taking care of Gojo, Toji used footprints and his enhanced senses to track Riko and the others to the Tombs of the Star."
- s3: "When a shocked Geto asked how Toji was there, he said that he killed Gojo, causing Geto to attack in anger."
- Gold: no Toji-Gojo row and no Toji-Geto met. It has `Toji|fought|Geto` and `Toji|defeated|Geto`.
- Open, two candidates:
  1. `Toji|defeated|Gojo` on "After taking care of Gojo". This would be a recap read as "took X down". It rests on an idiom, and "killed Gojo" is only Toji's claim.
  2. `Toji|met|Geto` on "a shocked Geto asked how Toji was there". A talk comes before the attack, the same pattern the reviewer kept met for in b1211 and b1148, but the encounter is only implied.
