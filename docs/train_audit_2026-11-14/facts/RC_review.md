# Row check RC (2026-11-14)

- Windows: 59
- Rows checked: 442 (71 events, 232 facts, 139 tags)
- Rows in error: 2
- Missing rows: 0
- Debatable rows: 20
- Windows with no error and no missing row: 57

## Errors

### b1560 — Megumi Fushiguro vs. Noritoshi Kamo / Battle
Sentence: "Megumi follows up by summoning Nue, who strikes Noritoshi with a fly by swipe of its electro-shock wings."
Gold row: event `Nue|fought|Noritoshi`
Wrong: Nue is the shikigami Megumi summons into the fight against Noritoshi. A creature a named master sends against a target leaves the fought row with the master (catalog A63, rulings Addendum 5; the same gold credits Dagon for his shikigami's bites at b1413).
Rule: A63 / Addendum 5.
Correction: `- Nue|fought|Noritoshi`, `+ Megumi|fought|Noritoshi|Megumi follows up by summoning Nue, who strikes Noritoshi with a fly by swipe of its electro-shock wings`. `Noritoshi|defeated|Nue` (S5, immobilising the shikigami) is left as is and counted debatable.

### b1377 — Playful Cloud / Toji Fushiguro
Sentence: "It even destroyed Dagon's water shield in a single hit, a technique that withstood blows from Naobito Zenin, Kento Nanami, and Maki at the same time."
Gold row: fact `Toji|other_verb|destroyed` (actual, stated)
Wrong: `destroyed` is in the closed relation list (B.2, possession/creation). other_verb is only for a verb no listed relation covers (B.3). The object should be the thing destroyed, which is an item and a legal fact end (B.1, B.6).
Rule: B.2 / B.3.
Correction: `f- Toji|other_verb|destroyed`, `f+ Toji|destroyed|Dagon's water shield|It even destroyed Dagon's water shield in a single hit`.

## Missing rows

None.

## Debatable rows (counted, not errors)

- b110: `Zodd|met|Guts` comes before their fight. A talk stands between the meeting and the fight, and the reviewer kept the met. `Guts|other_verb|save|ordered` is written from advice.
- b18: a no_relation tag where `Band of the Falcon|other_verb|recaptures|Doldrey` could be written.
- b138: "I feel sorry for that" is tagged deictic; production would also fit.
- b413: a capability tag for "strong enough to impale a younger Yhwach".
- b572: a no_relation tag where `located_at` "their hideout" could be written.
- b565: crowd_end for a debt sentence whose only end is the unnamed father.
- b761: `Nomo|fought|Bomb Hybrid` from "being up against".
- b701: `Fami|other_verb|ruined` is claimed with certainty stated.
- b934: "pummeling Goku" is tagged production in a movie comparison.
- b1419: `Sukuna|other_verb|kicks` sits beside the pair's fought row.
- b1336: a no_relation tag where Yuki destroyed Jujutsu High could be written.
- b1642: Akari "drives off" from Yasohachi Bridge could be `departed`.
- b1560: `Noritoshi|defeated|Nue`.
- b1377: `Toji|other_verb|devastated` sits beside the pair's fought row.
- b1460: `Naoya|other_verb|punches` sits beside the pair's fought row.
- b2913: in "when she organized a plan", "she" is resolved to Nami.
- b3040: `Burgess|fought|Sabo` from "tried to kill Sabo".
- b3042: `Luffy|saved|Law` from "came to rescue him".
- b3073: met from "confronting the likes of", plus a redundant crowd_end tag on a covered sentence.
