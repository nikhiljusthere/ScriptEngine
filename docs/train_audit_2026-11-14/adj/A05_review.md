# A05 adjudication: fix and unsure windows

Totals: 32 windows. 26 gold_ok, 4 fix, 2 unsure.

## Fix

### b623, Chapter 15 / Summary
- s1: "The small fleshy creature leaps at Kobeni, but is locked in place by Himeno and the power of the Ghost Devil."
- Gold: no events. Facts include `Himeno|other_verb|locked`. Tag `crowd_end` on the leap.
- Proposed: `+ Himeno|saved|Kobeni` with the quote "is locked in place by Himeno and the power of the Ghost Devil". The creature's attack on Kobeni is stopped before it lands, so this is an intercepted attack: A75, and Addendum 3 (intercepting a blow on a named person is `saved`). The creature is unnamed, so it gets no `fought` row. The `locked` fact, whose object is the creature, stays because it records the act on the creature, not the protection of Kobeni.

### b742, Control Devil arc / Synopsis
- s1: "Power defies Makima as she thinks of her friendship with Denji and runs away with him, while slaughtering multiple devil hunters in her way."
- s5: "Kishibe is shown sitting next to him and asks him if he's Denji or the Chainsaw Devil to which he answers with a peace sign."
- Gold: no events. Facts include `Power|other_verb|defies` and `Kishibe|other_verb|asks`.
- Proposed:
  - `+ Power|escaped|Makima` and `+ Denji|escaped|Makima`. The escaped table covers getting away from a pursuer, and the object is the pursuer the window names. Denji is named in the same clause ("with him"), so he gets the same row under the TEAM rule.
  - `+ Kishibe|met|Denji`. Kishibe newly appears where Denji is, which matches the met table's "X arrived where Y was" and Addendum 6.
- Facts are unchanged; the defies and asks facts record different acts.
- Weakest part: the `met` row, because "is shown sitting next to him" is a scene reveal rather than a stated arrival. The supervisor may drop that line and keep the escapes.

### b695, Control Devil arc / Synopsis
- s1: "After the fierce battle with Makima, he is ultimately defeated, as she rips out his heart from him and mocks him for not living up to being Chainsaw Man."
- Gold: `Makima|defeated|Chainsaw Man`, with no fought row for this pair.
- Proposed: `+ Makima|fought|Chainsaw Man` with the quote "After the fierce battle with Makima, he is ultimately defeated". The battle is stated separately from the defeat, so `fought` is written as well: step 5 and A145.
- Side note, not proposed: s4 reveals that the one Makima fought "was a Pochita he tore off his heart". A4/A49 (the revealed name) might call for `Pochita` in place of `Chainsaw Man` in this pair's rows. The window never ties the two names cleanly, so I left the gold's form.

### b751, Devil / Fear Empowerment
- s4: "Pochita eating the Death Devil resulted in the empowerment of various Devils embodying pest species like insects, bats and cockroaches, as without death the offspring of these high fertility species aren't culled via natural selection and live forever, leading to rapid overpopulating and swarming the world consuming all life to fuel their own reproduction."
- Gold: no events. Fact `Pochita|other_verb|eating`.
- Proposed: `+ Pochita|killed|Death Devil` with the quote "Pochita eating the Death Devil resulted in the empowerment of various Devils", and `f- Pochita|other_verb|eating`. The sentence narrates one occurrence inside a descriptive section, which A32/A122 make an event. This gold writes Pochita consuming a named devil as `killed`: b674 ("he has consumed various devils ... such as the AIDS Devil" gives 8 killed rows, reviewer "ok") and b695 ("Denji cooks Makima and eats her whole" is killed). Section B says an event is never also a fact, so the eating fact goes.
- Risk: the killed table wants a stated death, and the window states the eating and its result ("without death"), not the death in so many words. If consumption is not a kill on this wiki, the gold stands, but then b674 has the same problem.

## Unsure

### b652, Control Devil arc / Synopsis
- s2: "He then gets attacked by Whip, but she gets blasted away by Reze's explosions."
- Gold: fact `Reze|attacked|Whip`, with no event.
- Second reader: `Reze|fought|Whip`.
- An attack by one named character on another is `fought`, and section B forbids an `attacked` twin. However, the window does not say whether Reze aimed the blast at Whip or hit an ally by accident; both fight Pochita here, and A76 gives no row for an ally hit by accident. That would explain the reviewer's choice of a fact. I cannot settle it from the window: either the fact becomes `fought`, or it stays.

### b625, Power/History / Bat Devil arc
- s1: "Power offers Denji three squeezes, in exchange for saving Meowy, killing the Bat Devil and covering for her in front of Aki."
- s5: "She states that there is no reason for her to be a devil hunter since Meowy has been rescued."
- Gold: no events. Fact `Power|other_verb|offers`, and tag `no_doer` on "Meowy has been rescued".
- Second reader: `Denji|saved|Meowy` and `Denji|killed|Bat Devil`.
- Step 3 counts a past act mentioned in passing ("for murdering the senator"), and s5 confirms the rescue happened, which supports both rows. But the gerunds have no stated subject: Denji is the doer only because he is the one being paid. Addenda 4 and 5 confirm the strict A8 reading ("implied doer = A8 no row"), which may rule that out. I am not adding the rows without a ruling on whether an exchange's recipient counts as a stated doer.
