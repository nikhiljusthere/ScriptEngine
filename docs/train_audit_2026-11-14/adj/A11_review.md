# A11 adjudication: fix and unsure windows

## b1528 (unsure): Fearsome Womb Arc / The Detention Center Case
- S3: "Free with Yuji's body, Sukuna snatches his heart out and takes Yuji's body hostage."
- Gold: `Sukuna|captured|Yuji` plus the fact `Sukuna|other_verb|snatches`.
- Second reader adds `Sukuna|fought|Yuji`.
- Why unsure: A21 says the possessor fought the host, so tearing out the shared body's heart might be a `fought`. But this is a single act on the body both of them share, and the gold records it as a body act beside the hostage-taking. The window does not settle which reading is right.

## b1059 (fix): Gojo's Past Arc / Escorting the Star Plasma Vessel
- S1: "While Satoru and Suguru are occupied, Kuroi gets kidnapped by the Time Vessel Association and taken to Okinawa."
- Gold: `Time Vessel Association|captured|Misato Kuroi`, with no arrival for Kuroi.
- Proposed: `+ Misato Kuroi|arrived|Okinawa`, quoting "Kuroi gets kidnapped by the Time Vessel Association and taken to Okinawa".
- Rule: the arrived table says YES for "was taken/brought to", and A138 says the one carried arrives.

## b1254 (fix): Hajime Kashimo vs. Sukuna / Aftermath
- S7: "Following Kashimo's defeat, Hakari's domain barrier shatters, releasing him and Uraume."
- S8: "At the same time, Yuji Itadori and Hiromi Higuruma descend from the sky to face Sukuna next."
- Gold: `Sukuna|defeated|Kashimo`, quoting "Following Kashimo's defeat".
- Proposed: `- Sukuna|defeated|Kashimo`. The defeat is a noun with no stated doer. Sukuna is only implied by "face Sukuna next" and by the page title. S7 is already covered by its `no_relation` tag.
- Rule: A8 strict reading (Add.4/Add.5: an implied doer gets no row) and A110.

## b1576 (fix): Hana Kurusu/Synopsis / Culling Game Arc
- S5 (part): "Hana quickly regains consciousness and casts "Jacob's Ladder" to try to strip Sukuna away from Megumi, but is fooled when the King of Curses pretends to be Megumi to lure her into an embrace,(Chapter 213) whereupon Sukuna critically wounds and dispatches the girl, causing her to fall off the rooftop they were on."
- Gold: `Sukuna|defeated|Hana`, the fact `Hana|other_verb|casts`, and the fact `Hana|other_verb|strip` (attempted). There is no `fought` row.
- Proposed: `+ Hana|fought|Sukuna`, quoting 'casts "Jacob's Ladder" to try to strip Sukuna away from Megumi', and `f- Hana|other_verb|casts`. The attempted strip fact stays.
- Rule: the fought table says YES for "a power or technique used ON someone", and step 3 counts an attack that was made but failed. The cast is a separate act from Sukuna's defeat of Hana, so A145 does not merge them.
- Notes:
  - If the supervisor prefers "first actor" as the subject, the pair row can be flipped to `Sukuna|fought|Hana`.
  - Not proposed: in S3, "the group ... meet up with Tsumiki". Gold credits only Hana. Maki, Megumi and Yuji are also present in the window, but the window never lists the group, so I left this alone (A57).

## b1323 (fix): Haruta Shigemo/Synopsis / Shibuya Incident Arc
- S3: "As Nobara got up, Haruta prepared to attack her but stopped when Kento Nanami showed up.(Chapter 99, Episode 36) Seeing Nanami approach them, Haruta attempted to hold Akari hostage but noticed that she has gotten away."
- Gold: `Kento Nanami|met|Haruta`, with no meeting with Nobara.
- Proposed: `+ Kento Nanami|met|Nobara`, quoting "Haruta prepared to attack her but stopped when Kento Nanami showed up".
- Rule: Addendum 6. A named character who "shows up" where a named ally is meets each named person there. Akari is left out because she may already have gone.

## b1292 (fix): Haruta Shigemo/Synopsis / Shibuya Incident Arc
- S1 (part): "Later, Haruta woke up and came across an injured Megumi Fushiguro, who he critically wounded with a sneak attack."
- Context: the text just before the window ends with "Nanami sent Haruta flying into another building, knocking him out", so this is not ordinary sleep.
- Gold: the fact `Haruta|other_verb|woke`.
- Proposed: `+ Haruta|awakened|-`, quoting "Later, Haruta woke up and came across an injured Megumi Fushiguro", and `f- Haruta|other_verb|woke`.
- Rule: A106 counts regaining consciousness after a knockout as awakened, and the awakened table says YES for "woke up". Section B says an event is never also a fact.

## b1381 (fix): Hiromi Higuruma/Synopsis / History
- S3: "Hiromi, once again faced with the injustice of the legal system and his client's disappointed look, was filled with rage and awakened his cursed technique."
- Gold: the fact `Hiromi|other_verb|awakened`. The reviewer's note reads "awakening a technique is no awakened".
- Proposed: `+ Hiromi|awakened|-`, quoting "was filled with rage and awakened his cursed technique", and `f- Hiromi|other_verb|awakened`.
- Rule: the awakened table says YES for "gained a new power or form for the FIRST time, a new power awakened by an event" (A126). S2 shows the capacity was newly given to him, so this is not a power he already had (A80 does not apply).
- This goes against the reviewer's note, so the supervisor should confirm it.

## b1344 (fix): Jujutsu Sorcerers vs. Dagon / Aftermath
- S1: "Toji surprises everyone by coming through the hole into the coastal domain."
- S2: "Maki is surprised to see another human jujutsu sorcerer and Dagon is confused as to why they would let someone else in rather than escape."
- S4: "She and Naobito are both shocked by his pure speed."
- Gold: `Toji|met|Maki` and the fact `Toji|other_verb|coming`.
- Proposed: `+ Toji|met|Naobito`, `+ Toji|met|Dagon`, and `f- Toji|other_verb|coming`. Both new rows quote S1.
- Rule: the met table says YES for "X arrived where Y was", and A45 gives met to those who see him. Naobito and Dagon both react to his entry. A145 does not block Dagon, because Toji does not fight him in this window.

## b1057 (fix): Jujutsu Sorcerers vs. Dagon / Battle
- S1: "Dagon calls Megumi a fool for entering the domain voluntarily and motions to attack him."
- S2: "Maki stops him by swinging Playful Cloud and attacking from behind."
- Gold: `Maki|fought|Dagon` and the fact `Dagon|other_verb|attack` (planned).
- Proposed: `+ Maki|saved|Megumi`, quoting S2's clause.
- Rule: A75 treats an intercepted attack as fought plus saved, and Add.3 says intercepting a blow on a named person is saved.

## b1666 (fix): Kento Nanami/Synopsis / Shibuya Incident Arc
- S1 (part): "When Megumi manages to create an exit, Nanami gives the signal to retreat but they are shocked when Toji Fushiguro comes through the portal.(Chapter 109)"
- Gold: the fact `Toji Fushiguro|other_verb|comes`, and no met rows.
- Proposed: `+ Toji Fushiguro|met|Nanami`, `+ Toji Fushiguro|met|Megumi`, and `f- Toji Fushiguro|other_verb|comes`. Both new rows quote "they are shocked when Toji Fushiguro comes through the portal".
- Here "they" means Nanami and Megumi, the two who were retreating.
- Rule: the met table ("X arrived where Y was") and A45. Toji fights only Dagon here, so A145 does not apply. Section B requires dropping the fact once the event is written.

## b1214 (unsure): Kinji Hakari/Synopsis / Culling Game Arc
- S4: "Megumi and Panda want to ensure that Yuji's meeting goes smoothly and they sneak past all the security measures only to be caught by Kirara."
- Gold: the fact `Kirara Hoshi|other_verb|caught`, and no met rows. The reviewer notes it is no capture.
- Second reader adds `Kirara Hoshi|met|Megumi` and `Kirara Hoshi|met|Panda`.
- Why unsure: an in-person catch would be met (A58, an encounter that stops them). But S2 has Kirara watching "on the monitors", so the catch may have been made on camera. The window does not say which.

## b1402 (fix): Kirara Hoshi/Synopsis / Culling Game Arc
- S6: "On November 16, Kirara checked up on Choso following his battle with Kenjaku.(Chapter 211)"
- Gold: `Kirara|met|Choso` only.
- Proposed: `+ Choso|fought|Kenjaku`, quoting "Kirara checked up on Choso following his battle with Kenjaku".
- Rule: step 3 counts a past event mentioned in passing, and the fought table includes "attacks told in passing" and "the duel between A and B".
