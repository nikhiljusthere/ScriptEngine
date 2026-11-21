# A09 adjudication — fix and unsure windows

## b1065 — Chapter 215 / Plot Details — FIX
Sentences:
- s3 "Uraume has appeared and they make themselves known by activating Frost Calm at it's maximum cursed energy output."
- s4 "This creates a large mass of ice that incases Yuji and Maki without harming Sukuna."

Gold: no events; facts `Uraume|used|Frost Calm`, `Uraume|other_verb|creates`; note says "encasing in ice is no sealing".
Proposed: `+ Uraume|sealed|Yuji`, `+ Uraume|sealed|Maki` (s4), `+ Uraume|met|Sukuna` (s3); `f- Uraume|other_verb|creates`.
Rule: event table, sealed YES "trapped, sealed or banished the object: in a dimension, ice, a barrier" (and captured NO lists ice under sealed); A120 makes the power's owner the doer. Addendum 6: a named character who appears where a named ally is gets `met`; no met with Yuji/Maki, whom she then seals (A145). This goes against the reviewer's note, so the supervisor should confirm that the table's "ice" line takes precedence.

## b1640 — Chapter 222 / Plot Details — FIX
Sentences:
- s3 "Gojo appears before them completely devoid of his normally annoying persona."
- s4 "His intense aura even intimidates Yuta, Maki, and Hakari."
- s5 "Yuji however, isn't intimidated in the slightest and tells his sensei that the Infinity is in the way of a proper pat on the back."

Gold: `Satoru Gojo|other_verb|appears` fact, no met.
Proposed: `+ Satoru Gojo|met|Yuta`, `|Maki`, `|Hakari`, `|Yuji` (quote s3); `f- Satoru Gojo|other_verb|appears`.
Rule: Addendum 6 (shows up where named companions are = met with each named person there; the met replaces the other_verb shows/appears fact). In s1 Gojo and the students are apart, so they are not "already together".

## b1076 — Chapter 246 / Plot Details — FIX
Sentence: s2 "Having awakened as a jujutsu sorcerer only less than two months ago, Higuruma's extraordinary growth with jujutsu sorcery fascinates Sukuna."
Gold: fact `Higuruma|other_verb|awakened`; note says "awakening as a sorcerer is no awakened".
Proposed: `+ Higuruma|awakened|-` (quote "Having awakened as a jujutsu sorcerer only less than two months ago"); `f- Higuruma|other_verb|awakened`.
Rule: event table, awakened YES "gained a new power or form for the FIRST time"; step 3 (a past event mentioned in passing counts); section B / A89 (an event is never also a fact). This goes against the reviewer's note. Related open point: b1731, marked unsure below.

## b1593 — Chapter 251 / Plot Details — FIX
Sentence: s1 "Back in the present, as Yuji and Rika restrain Sukuna, Yuta activates Maximum Output: Jacob's Ladder and a pillar of light shines down upon the King of Curses, engulfing Sukuna in its destructive brilliance."
Gold: facts `Yuji|other_verb|restrain`, `Rika|other_verb|restrain`; fought only for Yuji and Yuta.
Proposed: `+ Rika|fought|Sukuna` (quote "as Yuji and Rika restrain Sukuna"); `f- Rika|other_verb|restrain`.
Rule: event table, fought YES "pinning, grabbing, restraining or choking someone during a fight". Yuji's restrain fact is left alone because Yuji already has a fought row from s3.

## b1422 — Chapter 254 / Plot Details — FIX
Sentences:
- s2 "As Ui Ui arrives to teleport him away, Sukuna suddenly appears behind them and remarks on how irritating Ui Ui's presence has been."
- s3 "Ui Ui vanishes instantly, causing Sukuna’s attack to miss."

Gold: Miguel met Sukuna, Miguel saved Ui Ui; there is no row between Ui Ui and Kusakabe or between Sukuna and Ui Ui.
Proposed: `+ Ui Ui|met|Kusakabe` (quote "As Ui Ui arrives to teleport him away"); `+ Sukuna|fought|Ui Ui` (quote s3).
Rule: met YES "X arrived where Y was" plus Addendum 6; fought YES "any attack MADE on someone, even if blocked, dodged or failed". No met for Sukuna, because his encounter becomes the attack (A145). Kusakabe is left out of the fought row because the window ties the missed attack only to Ui Ui's vanishing (A127).

## b1668 — Chapter 29 / Plot Details — FIX
Sentences:
- s1 "Suddenly, Yuji appears from the roof, revealing he mercifully killed his adversaries."
- s2 "Yuji lands on Mahito's enlarged hand, freeing Nanami."

Gold: `Yuji|saved|Nanami`, fact `Yuji|other_verb|appears`, no met.
Proposed: `+ Yuji|met|Nanami` (quote "Suddenly, Yuji appears from the roof"); `f- Yuji|other_verb|appears`.
Rule: Addendum 6 together with A34 (met each person reached + saved). This is the same shape as the applied b1229 "Nanami|met|Yuji beside the saved and fought rows". No met with Mahito, whom Yuji fights (A145).

## b1307 — Chapter 75 / Plot Details — FIX
Sentence: s1 "Toji stretches his arm and confirms that the energy wave Satoru used didn't break any of his bones."
Gold: only `Toji|defeated|Satoru` ("despite having lost their previous fight").
Proposed: `+ Satoru|fought|Toji` (quote "the energy wave Satoru used didn't break any of his bones").
Rule: step 3 (an attack told in passing counts) and table fought YES (a power used on someone). The wave belongs to the current fight, a separate act from the earlier fight Toji won, so A145 does not merge them.

## b1078 — Chapter 212 / Plot Details — UNSURE
Sentence: s1 "Back when Tsumiki first woke up, Megumi went to visit her in the hospital."
Gold: `Megumi|met|Tsumiki`, no awakened.
Why unsure: "first woke up" in a hospital points to a waking from coma, which counts as `awakened` under the table ("woke up") and A106 (coma). But the window never says coma, and A106 excludes ordinary sleep. The context before the window also says an incarnated sorcerer has been impersonating Tsumiki (A107). A possible fix would be `+ Tsumiki|awakened|-|Back when Tsumiki first woke up`.

## b1731 — Chapter 257 / Plot Details — UNSURE
Sentences:
- s3 "At this point, Yuji possesses two cursed techniques: Blood Manipulation, obtained by absorbing Death Painting Wombs Nos."
- s4 "4–9, and Shrine, which was engraved into him through Sukuna’s incarnation and drawn forth by the awakened state induced through repeated Black Flashes."

Gold: `gained_power` facts for Blood Manipulation and Shrine; the second reader writes `Yuji|awakened`.
Why unsure: the table counts a first new power as `awakened`, but this gold records first powers as `gained_power` facts, and the sentence mainly states possession. Converting them is a systemic decision for the whole gold (compare the b1076 fix), not something to settle from one window.

## b1775 — Chapter 266 / Plot Details — UNSURE
Sentence: s3 "A young Megumi appears in Yuji's mind, posing him the same question he once asked when they first met Satoru Gojo: \"what's with that look?\"."
Gold: tags the sentence `no_relation` ("an imagined Megumi is no person").
Why unsure: the clause may narrate a real past first meeting with Satoru Gojo (step 3, past events in passing; met YES "a first meeting"). However, "he" could be Megumi or Gojo, and "they" cannot be firmly resolved from the window (B.7). If the supervisor resolves "they" to include Megumi, the fix would be `+ Megumi|met|Satoru Gojo`.

## b1507 — Culling Game/Colonies / Tokyo No. 2 Colony — UNSURE
Sentence: s4 "Not far is a shipping yard next to the ocean where Hakari and Panda were able to locate Kashimo."
Gold: facts `Hakari|other_verb|locate`, `Panda|other_verb|locate`.
Why unsure: met YES includes "found X" with contact, and A132 adds "+ met for the finder". But "were able to locate" on a location-description page does not clearly state that they reached Kashimo. A possible fix would be `+ Hakari|met|Kashimo` and `+ Panda|met|Kashimo`, minus the two locate facts.
