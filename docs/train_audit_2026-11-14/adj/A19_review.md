# A19 adjudication: fix and unsure windows

## b3164 (Chapter 140 (Online) / Long Summary): fix
- Sentence 6: "Waganma then asks Tareo if Child Emperor saved him, but Tareo declines, stating that it was King and "the uncle" who saved him."
- Gold: event `King|saved|Tareo` (quote `it was King and "the uncle" who saved him`), plus the fact `Tareo|other_verb|stating`.
- Proposed: remove the event. Add `King|other_verb|saved|...|claimed|reported|Tareo`.
- Rule: A113. The rescue appears only in what Tareo says ("stating that"), so it is a claim and gets a claimed fact, not an event. Addendum 4 keeps the event only for factive wording ("revealed that", "made it clear that"), and "stating" is not factive.

## b3187 (Genos/Synopsis / Monster Association Arc): fix
- Sentence 2: "He then gets ready to defibrillate Tanktop Master, but the injured hero's tanktop miraculously tightens, restarting his heartbeat."
- Gold: fact `Tanktop Master|healed|-`, no event.
- Proposed: add `Tanktop Master|awakened|-` (same quote) and remove the healed fact, because an event is never also a fact (section B).
- Rule: the awakened table lists "was revived" and "came back to life". A106 says awakened covers a return from death, and A147 says the revived one gets awakened. The heartbeat had stopped (Genos was about to defibrillate) and then restarted, so this is a revival, not healing.

## b3292 (Junior Centipede / Monster Raid Arc): fix
- Sentence 4: "Junior Centipede is seen laying on the floor severely injured."
- Sentence 5: "He praises Metal Bat for his strength, but still questions Metal Bat about how high Metal Bat is in the food chain."
- Gold: `Metal Bat|defeated|Junior Centipede` with the quote "Junior Centipede is seen laying on the floor severely injured. He praises Metal Bat for his strength". That quote joins sentences 4 and 5.
- Proposed: keep the row (outcome ruling 2026-11-03, as in the reviewer note) and re-quote it inside sentence 4 only.
- Rule: step 7 and B.1. A quote must sit inside one sentence and must never join two sentences.

## b3182 (Forest King / Physical Abilities): unsure
- Sentence 2: "He even managed to restrain Tanktop Master, an S-Class hero who possesses great physical strength, using only one of his numerous branches."
- Gold: `Forest King|defeated|Tanktop Master`. The reviewer note says "restraining is defeated". The second reader has fought.
- Why unsure: the verb table lists restraining someone during a fight under fought, and the captured row's NO column says the same. Defeated needs the fight to end, and the window does not say it ended. On the other side, the context before the window says the Forest King defeated Tanktop Master, so reading the restraint as a subdue is defensible. Changing defeated to fought would need the reviewer's agreement.

## b3103 (Garou/Synopsis / Garou Introduction Arc): unsure
- Sentence 1: "During a meeting in the Hero Association headquarters in the middle of a coalition between a large group of villains and the Hero Association."
- Sentence 5: "...with the exception of Sitch and Speed-o'-Sound Sonic as Sonic had left said meeting pre-haste."
- Sentence 6: "As he leaves proclaiming this was the epic intro of Garou the Human Monster, he promises to come bursting through the front door of the Hero Association in six months time after his training journey was over."
- Gold: `Speed-o'-Sound Sonic|departed|Hero Association headquarters` and `Garou|departed|Hero Association headquarters`.
- Why unsure: neither clause names the place that was left. Sonic "left said meeting", and Garou simply "leaves". A73 says an event is not a place, and the departed table needs a proper-named place to be left, which argues for no row. Against that, sentence 1 sets the meeting inside the named Hero Association headquarters.
