# A20 adjudication: fix and unsure windows

## b3214 (fix) — Monster Association Arc / Invading the Monster Association: The Heroes Attack
- Sentence 1: "Gyoro Gyoro contemplates over Saitama's attack before Tatsumaki appears."
- Gold has: `Saitama|fought|Gyoro Gyoro` (quote "contemplates over Saitama's attack"), plus the fact `Gyoro Gyoro|other_verb|contemplates`.
- Proposed: remove `Saitama|fought|Gyoro Gyoro`. The window never says whom Saitama attacked. The text just before the window says Saitama punched Overgrown Rover and the punch shook the whole HQ. Sentence 1 stays covered by the contemplates fact.
- Rule: step 4 (no doer or target from outside the window), A8.

## b3169 (fix) — Puri-Puri Prisoner vs. Baquma / Battle
- Sentence 2: "Puri-Puri Prisoner tells Baquma that if the latter wants to fight those heroes, he will have to surpass the "ordinary man" standing in front of him."
- Gold has: `Puri-Puri Prisoner|met|Baquma` (quote "Puri-Puri Prisoner tells Baquma").
- Proposed: remove it. The window only narrates talk inside a battle that is already under way: Baquma has already fired a beam at him, and sentence 1 has Prisoner "respond" to Baquma. The window states no coming-together. Sentence 2 stays covered by the `tells` fact.
- Rule: met table NO column ("talking inside a meeting already under way"), A145.

## b3144 (fix) — Saitama / Physical Abilities
- Sentence 1 (part): "Superhuman Eyesight: Saitama's eyesight is superhuman; after being kicked to the Moon by Boros, he could see, pinpoint the location of the giant spaceship, and land back on it from lunar distance."
- Gold has: `Boros|fought|Saitama`. It has no arrival row.
- Proposed: add `Saitama|arrived|Moon|after being kicked to the Moon by Boros`. This is a narrated occurrence, not ability wording. Saitama is sent to a proper-named place and reaches it: he lands back "from lunar distance". The giant spaceship is a description, so it gets no row.
- Rule: arrived table YES ("was taken/brought to", "transported to the Void"), A138 (the one carried arrives), A122.

## b3100 (fix) — Saitama vs. Awakened Garou (Webcomic) / Aftermath
- Sentence 3: "Frustrated, Saitama tells him he doesn't know, reiterating that it's just a hobby, and smashes his fist down on Garou's head."
- Sentence 4: "This obliterates the top of Garou's monster head and horns, allowing light to penetrate and reveal a pair of human eyes still visible within the monster's body."
- Gold has: `Saitama|defeated|Garou` with the quote "smashes his fist down on Garou's head. This obliterates the top of Garou's monster head and horns". That quote is stitched across two sentences.
- Proposed: keep the row and re-quote it inside sentence 3 as "smashes his fist down on Garou's head". This is done with a remove followed by an add of the same S|V|O; the removal must apply before the add. The defeated row itself (A145 outcome ruling) and `Zombieman|met|Saitama` are unchanged.
- Rule: step 7 / B.1 (a quote stays inside one sentence; never stitch two).

## b3174 (fix) — Zakos / Super Fight Arc
- Sentence 2 (part): "Zakos was later present at the closing ceremony when it was suddenly interrupted by The Three Crows and Gouketsu, who tells them that they will become monsters." Later: "Zakos was then knocked out by the crows with the rest of the martial artists."
- Gold has: no met. It has the facts `The Three Crows|other_verb|interrupted` and `Gouketsu|other_verb|interrupted`.
- Proposed: add `Gouketsu|met|Zakos|it was suddenly interrupted by The Three Crows and Gouketsu` and remove `Gouketsu|other_verb|interrupted` (an event is never also a fact). Do not add a met for The Three Crows: they are the ones who later knock Zakos out.
- Rule: met table YES ("X arrived where Y was", "walked in on X"), Addendum 6, section B; A145 / Add.6 (no met with the one the newcomer then fights).

## b3262 (unsure) — Nyan / Monster Association Arc
- Sentence 3: "When it targets the fleeing Futoshi and Waganma, Gearsper intervenes by collapsing buildings on Nyan with his psychic powers, then collapses."
- Sentence 4: "Believing the monster defeated, Futoshi is caught off guard when Nyan reemerges, takes him down, and captures Waganma, intending to finish its game by killing him in front of the fallen heroes."
- Gold has: `Gearsper|fought|Nyan` and no saved rows.
- Why unsure: Gearsper's intervention against an attack on two named people could be A75 (an intercepted attack also gets saved), which would mean `Gearsper|saved|Futoshi` and `Gearsper|saved|Waganma`. But the very next sentence has Nyan beat Futoshi and capture Waganma, so the end state the passage reaches is not a rescue.

## b3155 (unsure) — Phoenix Space / Overview
- Sentence 6 (part): "If someone's willpower is strong enough, they can force themselves out of it, as shown by Child Emperor."
- Sentence 7: "After leaving, Child Emperor was surprised to discover that only three seconds had passed outside despite the seemingly much longer conversation inside the Phoenix Space."
- Gold has: the fact `Child Emperor|other_verb|force`. It has no escaped or departed row.
- Why unsure: this may be `Child Emperor|escaped|Phoenix Space` (he broke out of a named place) or a departed row. But the window never states he was held there against his will, and the reviewer deliberately chose a fact.

## b3261 (unsure) — Royal Ripper / Monster Association Arc
- Sentence 4: "After threatening the boy, he decides to begin the torture before he is interrupted by Garou who breaks through the wall and quickly kills Royal Ripper by punching off his head and using the Whirlwind Iron Cutting Fist to rip his body apart."
- Gold has: `Garou|killed|Royal Ripper` and `Royal Ripper|captured|Tareo`.
- Why unsure: Garou breaks into the cell and kills Tareo's torturer before the torture begins. That could be `Garou|saved|Tareo` (protected from harm), with `Garou|met|Tareo` under A34. But the window states no rescue and no release, only the interruption. The second reader's arrival at "the Monster Association base" looks like a description-place, so it gets no arrived row (arrived table NO).

## b3065 (unsure) — Tareo / Monster Association Arc
- Sentence 2: "Waganma mentions that he was captured the day before and that he was fed only bread and water."
- Sentence 4: "Waganma comments on Tareo's uselessness and the monster's stupidity for capturing him as his father is an important figure to the Hero Association."
- Gold has: `Royal Ripper|captured|Waganma` (quote "the monster's stupidity for capturing him").
- Why unsure: Waganma's own capture has no doer in the window ("captured the day before"). The capture by "the monster" sits inside Waganma's comment (A113), and the window never ties it to Royal Ripper, so the row may break A8. On the other hand, Royal Ripper is the only monster the window names. The other rows are fine: Royal Ripper's met rows and `Royal Ripper|captured|Tareo` (A37).
