# A06 adjudication — fix and unsure windows

Totals: 26 gold_ok, 4 fix, 6 unsure (36 windows).

## Fix

### b721 — Episode 7 / Summary (fix, Addendum 6 / A6)
- S1: "Makima shows up and overhears Denji and wonders if he will be kissing anyone."
- S3: "Himeno then wonders if he no longer wants her kiss, but Denji states he does wants it."
- S6: "Aki adds that more devils with Gun Devil's pieces are appearing and one even targeted Denji."
- S8–S9: "Makima states she will tell him, if he can outdrink her." / "Himeno decides to join them and the three start drinking beer after beer."
- Gold: `Makima|met|Denji` only.
- Proposed: `+ Makima|met|Aki` and `+ Makima|met|Himeno` (quote "Makima shows up and overhears Denji"). Addendum 6 says someone who shows up gets a `met` with each named person there. Aki and Himeno take part in the same conversation at the party, and neither fights her.

### b551 — Galgali / International Assassins arc (fix, A113 with Addendum 4)
- S3: "He explains that he can't remember much except that Makima saved him."
- Gold: event `Makima|saved|Galgali`.
- Proposed: `- Makima|saved|Galgali`; `f+ Makima|other_verb|saved|except that Makima saved him|claimed|reported|Galgali`. The rescue is known only from what Galgali explains he remembers. Addendum 4 lists "explains" among the report verbs that A113 covers: no event, only a claimed fact. (The page context also says his background "might be fabricated" by Makima.)

### b567 — Yoru / Nightjar Fiend (fix, A53 + WBY + A89)
- S1: "Following the battle with the Four Horsemen and Weapon Devils, Yoru was also reduced to a “near-death state”, due to Pochita consuming most of her body."
- Gold: no event. Facts `Yoru|wounded|-` and `Pochita|other_verb|consuming`.
- Proposed: `+ Pochita|defeated|Yoru` (quote "due to Pochita consuming most of her body"); `f- Yoru|wounded|-` → `f+ Pochita|wounded|Yoru` (WBY: the sentence names who did it); `f- Pochita|other_verb|consuming`, which is the new event's twin (A89, section B).
- Rule: A53 says a body destroyed while the character survives is `defeated`. Eating most of her body and leaving her near death ends her fight. The second reader's `awakened` for taking over the bird body stays out (gold note; settled transformation practice).

### b926 — Android 17/Biography / Kakarot (fix, step 5 / A145)
- S3: "Future Trunks arrives seeking Magidemia seeds, which Android 17 obtains for him after the two have a battle - which 17 wins."
- Gold: `Android 17|defeated|Future Trunks` only.
- Proposed: `+ Future Trunks|fought|Android 17` (quote "the two have a battle"). The text states the battle ("have a battle") and its result ("which 17 wins") as two separate clauses. Step 5 and A145 then call for `fought` and `defeated`. No `met`, because the encounter becomes the fight (A145).

## Unsure

### b737 — Haruka Iseumi / Aging Devil arc
- S3: "However, Yoru deduces that the grunt was actually distracting them as Katana Man and the Nail Fiend arrive to stop Fami's group from proceeding any further.(Chapter 159)"
- Gold: no event. Planned `stop` facts. Reviewer note: "a hostile arrival is no meeting".
- Why unsure: the table makes "X arrived where Y was" and "confronted X (also with a fight)" a `met` (see also A58). No fight follows (a truce comes after the window), so A145 does not apply, which would give Katana Man and Nail Fiend a `met` with Yoru, Haruka and Nobana. Against that, A19 says a purpose arrival gets "no met/fought", and the reviewer ruled on it explicitly. A supervisor should decide.

### b537 — Katana Man arc / Synopsis
- S3: "As Power is semi-immortal and Denji immortal, Kishibe's training is brutal, and he constantly nearly-kills Power and kills Denji."
- Gold: `Kishibe|defeated|Denji`. The note cites the outcome ruling: a body destroyed while its owner survives is defeated, not killed.
- Why unsure: Addendum 4 keeps `killed` (+ `awakened`) when a named doer kills and the victim later returns (clinical-death ruling, b9585). The window states only "Denji immortal" and narrates no return, and the kills are habitual training (A71). It is not clear which ruling governs.

### b728 — Zombie Devil / Intro arc
- S2: "He then called Denji to an abandoned building and made his new zombies kill him, since he hates devil hunters.(Chapter 1)"
- S3: "When Denji came back to life, he was surprised that he still lived and told his zombies to eat him."
- Gold: no row for the Zombie Devil against Denji. The note says the causative is "covered by 'called'".
- Why unsure: Addendum 5 / A63 say that when a named master sends unnamed minions, the master keeps the fought/defeated row, so a row seems to be missing. The verb is unsettled: `killed` is barred for an order-giver (A60), and A145 makes it either `fought` alone or the outcome alone. Candidates are `Zombie Devil|fought|Denji` and/or `Zombie Devil|defeated|Denji` (quote "made his new zombies kill him").

### b753 — Zombie Devil / War Devil arc
- S1: "In a new reality where Pochita never existed, the Zombie Devil and the Debt Collector attempt to kill Denji after the latter backstabs him like in the original timeline."
- Gold: `Denji|fought|Zombie Devil` (quote "the latter backstabs him"), so gold reads "the latter" as Denji.
- Why unsure: "the latter" most naturally means the second of the pair just named, the Debt Collector, with "him" = Denji. "Backstabs" may also mean a betrayal rather than an attack (the second reader wrote `Debt Collector|betrayed|Denji`). A14 says to resolve by meaning, but the window alone does not settle it. If the reading is Debt Collector, the gold row is wrong and the replacement verb (fought or betrayed) still needs a ruling.

### b887 — Android 21 Arc / Enter Android 17! A Powerful Ally!
- S1: "18 returns to the room, only to have 17 comment about her attire."
- S2: "She is surprised, for it has been a very long time since she has heard anything from her twin."
- Gold: all five sentences tagged `production` ("a game story arc is production").
- Why unsure: B.8 defines production as behind-the-scenes material, trivia, cast and release data. A game's story is plot from another canon. In this batch, b926 (the Kakarot game section) is labelled as plot with events. If this arc is plot, S1–S2 give a reunion, `Android 18|met|Android 17` (window form "18"/"17"), and facts for the rest. That is a policy question, not one window.

### b792 — Black Star Dragon Ball / Baby Saga
- S1–S2 (split at "Mr."): "As Goku, Trunks and Pan return from space and gave the Black Star Dragon Balls to Dende and Mr. Popo, Goku decide not to use them ..."
- Gold: `gave` facts only (Goku, Trunks, Pan → Dende, Mr. Popo).
- Why unsure: returning from space and handing the balls over in person reads as a reunion ("X arrived where Y was", table `met` YES). That would add six `met` rows (Goku, Trunks and Pan, each with Dende and with Mr. Popo). But the window only implies that they came together; it never says so. The reviewer looked at this sentence ("the composite givers") and wrote only facts.
