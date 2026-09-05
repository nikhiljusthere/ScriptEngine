# Phase 1B — eight-verb coverage measurement

- Date: 2026-09-05 (IST)
- Premise check (done): `EVENTIVE_VERBS` in `scriptengine/ingest/events.py:43-54`
  is exactly the closed set `fought / killed / saved / arrived / departed /
  awakened / sealed / betrayed`. Premise holds.
- Corpus: the live JJK store's `Summary` sections (363 sections — the
  per-chapter/episode plot summaries; 949 sentences ≥20 chars after the
  engine's own sentence splitter, `chunker.split_sentences` — the *index's*
  splitter; the extractor reads section text in windows, `events.py:1002`, so
  the ≥20-char unit is the right one for this question, not the extractor's
  own unit (P12)).
- Sample: 100 sentences, `random.seed(20260905)`, `random.sample`. Reproduce
  with the seed; the sample is appended below in full with its classifications.
- Method: no model. Each sentence was read and classified against the rule
  below.

## The rule

A sample sentence is **covered** iff its main eventive content can be
rephrased as `S V (O)` (or passive) with V in the eight-verb set, without
changing the main described event:

- a conflict of any wording (battle, fight, clash, duel, confrontation,
  fistfight, stand, vs., counterattack, a clash of domains) expresses
  `fought` — an opponent or an ongoing conflict must be in the sentence;
- movement to a location (visits, goes to, heads into, descends into,
  returns, jumps into the fray, is brought to, travel to) expresses
  `arrived` / `departed`;
- rescuing expresses `saved`; slaying expresses `killed`; being put in the
  Prison Realm expresses `sealed`; a defection expresses `betrayed`;
  a power coming online expresses `awakened`.

Purpose/motive clauses ("in order to save…", "so he can kill…") do not
count. Time expressions ("the promised day arrives") and non-participant
subjects do not count. Descriptions, states, feelings, decisions,
observations, explanations and rhetorical questions are **not covered** —
that is the closed set working as designed (`events.py`: "a verb outside the
set is a description, not an event, and descriptions never order a
timeline").

## Result

**39/100 covered, 61/100 (61%) cannot be held by the eight verbs — of the
Summary slice** (P7: 363 sections / 949 sentences is the densest plot slice,
not the population — it excludes `Plot Details` on the same pages, the
character narrative sections and the placement scope — so quote the number as
"61% of the Summary slice"). The covered count is contested within a
**38–40/100 band** (P9: row 073 covered while 085 uncovered is the uneven
application — under a main-clause-governs reading both drop out, 38; under
the rule as written 085 is covered, 40).

Covered, by verb:

| verb | count | items |
|------|-------|-------|
| fought | 22 | 003 005 006 014 019 040 041 043 055 056 057 062 063 064 071 073 075 081 082 084 095 099 |
| arrived | 7 | 007 015 022 026 044 048 092 |
| departed | 6 | 036 059 060 069 087 094 |
| saved | 2 | 024 039 |
| killed | 1 | 011 |
| sealed | 1 | 091 |
| betrayed | 0 | — |
| awakened | 0 | — |

### Composition of the 61 uncovered

- **41 are pure description** (state, feeling, decision, observation,
  explanation, rhetorical question) — correctly outside the set by design;
  not a gap. Items: 001 002 009 013 016 020 021 027 029 030 031 032 033 035
  037 038 042 045 046 049 053 054 058 065 066 067 068 072 074 076 077 078 079
  080 083 086 088 090 096 097 100 (002 "argue" is listed here: an argument is
  a state of a confrontation, and "argued" is not a timeline-placing event in
  this corpus).
- **13 are fight-adjacent but not eventive** — intentions, progressions or
  techniques with no conflict stated in the sentence (closest: fought):
  004 010 017 025 028 034 052 061 070 085 089 093 098.
- **2 are kill-intentions** (closest: killed): 050 051.
- **3 are meetings** (closest: `met/encountered` — not in the set; P8): 008
  ("make first contact"), 018 ("crosses paths with"), 047 ("encounter
  Haruta Shigemo" — re-bucketed from fight-adjacent).
- **1 is a rescue purpose clause** (closest: saved): 012.
- **1 is a time expression** ("the promised day arrives"; closest: arrived,
  but no participant subject): 023.

**The only recurring true eventive gap outside the set is
`met/encountered` (3/100: rows 008, 018, 047 — P8).** `betrayed` and
`awakened` were never used by
the sample even though both are in the set — on this slice of the corpus the
set is over-specified in two cells and under-specified in one.

## Reading

The headline 61% is *not* a defect in the eight verbs: 41 points of it are
description the set deliberately refuses. On the ~20 eventive-but-uncovered
sentences the set is thin — mostly because wiki summary prose states
*intentions and progressions* ("decides to try and defeat", "ready to stand
against") rather than placed events, and because `met/encountered` — a real
placed event ("the sorcerers make first contact with the Simurians") — has no
cell.

Per the 1C rule ("1B shows high uncovered fraction → the verb set is widened
before any further extraction"), the decision for the council: widen the set
before the 24k pass. The sample supports adding **`met` / `encountered`**
(the one recurring true gap) and, optionally, **`defeated`** as an outcome
verb — noting Phase 2A's battle-outcome join will already serve `Result`
fields (victory/defeat/suicide), so `defeated` as an *event* row may be
redundant with 2A's structured outcomes. `betrayed`/`awakened` stay, on the
live evidence (P10): under `events-2026-09-05.2` the `events` table carries
**93 `awakened` rows and 4 `betrayed` rows** — the earlier `sealed` example
(Gojo's Prison Realm) was a miscite. *1C ruling, COUNCIL_1.md: widen with
`met` only; `encountered` and `defeated` are not added.*

## Sample and classifications (seed 20260905)

| # | source | sentence | verdict | verb / closest |
|---|--------|----------|---------|----------------|
| 001 | Ch 5 | Elsewhere, a cursed womb begins to nurse a special grade curse. | uncovered | description |
| 002 | Ch 18 | Mai and Maki argue over which of them is lower class than the other, but Maki believes they're both at the bottom. | uncovered | description (argue) |
| 003 | Ch 117 | He forces Shigemo into an unbeatable exorcism ritual against the out-of-control shikigami Mahoraga! | **covered** | fought |
| 004 | Ch 95 | The jujutsu sorcerers want to get the fighting over quickly, but the curse users have a few tricks of their own. | uncovered | fought (want) |
| 005 | Ch 48 | Yuji and Aoi take over the fight against Hanami. | **covered** | fought |
| 006 | Ch 28 | Unable to depend on Sukuna, Yuji taps into his anger and attacks Mahito with everything he has. | **covered** | fought |
| 007 | Ch 195 | Just as things look dire for Noritoshi, a swordsman with no katana and a sumo enthusiast with no one to wrestle jump into the fray. | **covered** | arrived |
| 008 | Modulo Ch 2 | The jujutsu sorcerers make first contact with other representatives of the Simurian race. | uncovered | met/encountered |
| 009 | Ch 258 | The reason for Yuji's accelerated growth as a sorcerer is...! | uncovered | description |
| 010 | Ch 123 | Yuji quickly loses the upper hand while Nobara uses Mahito's overconfidence against him. | uncovered | fought (progression) |
| 011 | Ep 28 | The escort mission takes a disastrous turn when Satoru and Riko have both been slain by the Sorcerer Killer. | **covered** | killed |
| 012 | Ep 1 | In order to save his friends, Yuji teams up with jujutsu student, Megumi Fushiguro, to exorcise the curses and recover the cursed object: Ryomen Sukuna. | uncovered | saved (purpose) |
| 013 | Ch 72 | The escort team nearly completes their mission until the former member of the Zenin Clan changes everything. | uncovered | description |
| 014 | Ch 163 | Megumi is escorted by someone as well, but Remi leads him into a confrontation with another player named Reggie instead. | **covered** | fought |
| 015 | Ch 104 | Yuji struggles to fend Choso off, but Mechamaru returns to lend his advice. | **covered** | arrived (returns) |
| 016 | Ch 189 | As the battle presses on, Kashimo shows he's willing to take risks in order to achieve victory as well. | uncovered | description (willingness) |
| 017 | Ch 157 | Before Megumi's able to ask for help, Hakari's conflict with Yuji reaches its climax. | uncovered | fought (progression) |
| 018 | Ch 13 | After leaving his session with Yuji, Satoru Gojo crosses paths with the unregistered special grade cursed spirit, Jogo. | uncovered | met/encountered |
| 019 | Ch 109 | The sorcerers are able to mount a counterattack against the curse without the domain's automatic hit active. | **covered** | fought |
| 020 | Ch 42 | She resents Maki for leaving the Zenin Clan and feels the pressure of living up to be better than her. | uncovered | description (feeling) |
| 021 | Ch 162 | Regardless of being separated, Yuji and Megumi work finding on Hiromi Higuruma. | uncovered | description (searching) |
| 022 | Ch 103 | Yuji has made it inside Shibuya Station, but Choso proves to be more than a match for the Jujutsu High student. | **covered** | arrived / fought |
| 023 | Ch 82 | The Evening Festival reaches its conclusion and the promised day in Shibuya finally arrives. | uncovered | arrived (time expression) |
| 024 | Ch 0-1 | They find the two kids inside and Yuta harnesses Rika's power to save everyone. | **covered** | saved |
| 025 | Modulo Ch 20 | Yuji has no desire to help the jujutsu sorcerers defeat Dabura but agrees to handle the cursed spirits fleeing Tokyo. | uncovered | fought (intention) |
| 026 | Ep 8 | The Kyoto Principal visits the Tokyo Campus to discuss the upcoming Goodwill Event. | **covered** | arrived |
| 027 | Ch 160 | Those who were already inside a barrier colony when the Culling Game began on November 1st were given one chance to escape. | uncovered | description (rule) |
| 028 | Ch 50 | Thanks to Aoi's simple and effective cursed technique, he and Yuji are able to gain the upper hand on Hanami. | uncovered | fought (progression) |
| 029 | Ch 84 | That being said, the strongest jujutsu sorcerer doesn't go down so easily. | uncovered | description |
| 030 | Ch 48 | Mastering this move will allow Yuji to grow stronger than ever before! | uncovered | description |
| 031 | Ch 143 | With Yuji and Choso both having been dealt with, Yuta offers Naoya a deal he can't refuse. | uncovered | description (offer) |
| 032 | Ep 3 | When faced with the life of another in her hands, Nobara looks back to her past. | uncovered | description (flashback) |
| 033 | Ch 158 | Hakari is surprised by what occurred in Shibuya and agrees to help, but only on the condition that they return the favor in the future. | uncovered | description (agreement) |
| 034 | Ch 69 | To ensure the safety of the Star Plasma Vessel, Satoru unleashes the powers of his Limitless technique. | uncovered | fought (technique, no opponent stated) |
| 035 | Ch 20 | Meanwhile, the culprit, Mahito, and the only known witness, Junpei discuss the origin of curses. | uncovered | description (discuss) |
| 036 | Ep 52 | Yuji and Fushiguro go to Hakari's fight club, intent on recruiting him to help them stop the Culling Game. | **covered** | departed |
| 037 | Ch 76 | At the same time, Suguru begins to fall into self isolation, constantly questioning his morals when it comes to non-sorcerers. | uncovered | description |
| 038 | Ep 32 | The Shibuya Incident begins! | uncovered | description |
| 039 | Ch 47 | Before the situation becomes any dire, an unexpected duo comes to the rescue. | **covered** | saved |
| 040 | Ch 104 | He gambles on Mechamaru's plan to even the playing field between the two combatants, devolvingtheir duel into a fist fight. | **covered** | fought |
| 041 | Ch 120 | He makes his last stand against a swarm of transfigured humans and reluctantly reunites with a familiar foe. | **covered** | fought |
| 042 | Ep 17 | Kasumi Miwa learns that the rank does not reflect the strength of the sorcerer when it comes to Maki Zenin. | uncovered | description (learns) |
| 043 | Ch 226 | The barrier of Unlimited Void is crushed by the relentless slashes of Malevolent Shrine! | **covered** | fought (domain clash) |
| 044 | Ep 41 | On the verge of death, Megumi desperately heads toward Dogenzaka crossing and summons a certain shikigami with his Ten Shadows Technique. | **covered** | arrived |
| 045 | Ch 62 | Meanwhile, Choso, Mahito, and Pseudo-Geto gain wind of the incident. | uncovered | description |
| 046 | Ch 106 | However, before he can avenge his brothers, Choso's mind is invaded by a memory of something that never happened. | uncovered | description |
| 047 | Ch 99 | Nobara and Akari encounter Haruta Shigemo on the way, and he's surprisingly powerful. | uncovered | fought (encounter + assessment) |
| 048 | Ep 32 | After learning Mahito is involved, Yuji descends into the station only to find a "clever" enemy guarding the curtain. | **covered** | arrived |
| 049 | Ch 78 | Suguru has made his decision to reject non-sorcerers. | uncovered | description (decision) |
| 050 | Ch 187 | Kashimo enjoys the challenge and decides to try and defeat someone who's effectively immortal. | uncovered | killed (intention) |
| 051 | Ch 129 | The cursed spirit desperately tries to take Todo out of the equation so he can focus on killing Yuji. | uncovered | killed (intention) |
| 052 | Ch 235 | The fight will ultimately be decided if Unlimited Hollow carves its way through Shinjuku again. | uncovered | fought (prediction) |
| 053 | Ch 50 | Powerful, smart, and misunderstood, Aoi was bored with the world in his youth. | uncovered | description |
| 054 | Ch 10 | They agree to get stronger for Yuji, but is he truly gone? | uncovered | description |
| 055 | Ch 43 | Megumi's Ten Shadows Technique clashes with Noritoshi's Blood Manipulation! | **covered** | fought |
| 056 | Ch 102 | Meanwhile, trapped inside a graveyard domain, Mei Mei and Ui Ui put their lives on the line to exorcise Pseudo-Geto's special grade disease curse. | **covered** | fought |
| 057 | Modulo Ch 13 | When Japan refuses, they challenge the Earthlings to a duel. | **covered** | fought |
| 058 | Ch 30 | With that gratitude lifting any uncertainty from his soul to this day, Nanami is ready to die with no regrets... | uncovered | description |
| 059 | Ch 222 | When December 24th arrives, the Jujutsu High students do their best to encourage their sensei as he heads into the most important fight of his life. | **covered** | departed |
| 060 | Modulo Ch 3 | Yuka, Tsurugi, and Maru head to the forest for a wild encounter with a man-eating shark! | **covered** | departed |
| 061 | Ch 97 | Meanwhile, Megumi deduces the nature of Jiro Awasaka's technique and devises a counter-attack. | uncovered | fought (devising) |
| 062 | Ch 108 | Locked inside the Horizon of the Captivating Skandha domain, the jujutsu sorcerers fight for their lives against Dagon's endless swarm of man-eating fish shikigami. | **covered** | fought |
| 063 | Ch 148 | Maki walks right into their trap and is forced to face down her own father. | **covered** | fought |
| 064 | Modulo Ch 6 | An unconscious Maru battles Masaki Takeda and overpowers the elderly curse user with his unusual cursed technique! | **covered** | fought |
| 065 | Ch 155 | Before Yuji can get a word in, communications suddenly break down when Kirara is able to get a warning to Hakari. | uncovered | description |
| 066 | Modulo Ch 2 | Can the earthling sorcerers coexist with their alien visitors? | uncovered | rhetorical question |
| 067 | Ch 39 | At the same time, Kasumi learns about Maki's true power. | uncovered | description (learns) |
| 068 | Ch 12 | Megumi and Nobara focus on improving their weaknesses with Maki, while Gojo sensei hopes that he can improve on Yuji's strengths. | uncovered | description |
| 069 | Ch 18 | Aoi Todo breaks up the argument and leaves with Mai. | **covered** | departed |
| 070 | Ch 237 | Kashimo not only seeks to defeat Sukuna, but to learn what it truly means to be the strongest. | uncovered | fought (seeks) |
| 071 | Ch 39 | Armed with the powers of his older brother, Panda turns the tide of the battle against Mechamaru. | **covered** | fought |
| 072 | Ch 156 | Megumi and Panda want to convince Kirara they're not enemies so that negotiations with Hakari go smoothly. | uncovered | description |
| 073 | Ep 7 | However, the battle that ensues proves to the volcanic curse Jogo that Satoru Gojo's abilities are on a higher level than his own. | **covered** | fought |
| 074 | Ch 111 | Before he can finish them off for good, Jogo notices Sukuna's presence in Shibuya. | uncovered | description (notices) |
| 075 | Ch 103 | Choso uses every move in his arsenal to take revenge on his younger brothers, pushing Yuji closer to the edge of defeat. | **covered** | fought |
| 076 | Ch 164 | Instead, Yuji finds himself on trial against the lawyer and the judgement may be fatal! | uncovered | description (trial) |
| 077 | Ch 23 | Just when Mahito believes he's won, the former salaryman gets serious when he begins working overtime. | uncovered | description |
| 078 | Ch 38 | But is Panda... truly a Panda? | uncovered | rhetorical question |
| 079 | Ep 24 | Meanwhile, Choso, Geto and Mahito gain wind of this event. | uncovered | description |
| 080 | Ch 195 | They are two incarnations without an outlet for their passions because Japanese culture has left them in the past. | uncovered | description |
| 081 | Ch 198 | In the climax of the battle in the Sakurajima Colony, Naoya unleashes his devastating domain expansion! | **covered** | fought |
| 082 | Ep 13 | Yuji and Nanami engage in the climatic battle against Mahito. | **covered** | fought |
| 083 | Modulo Ch 25 | Mifuyu Okkotsu reprimands her children for their reckless behavior, but expresses her pride in giving birth to them. | uncovered | description |
| 084 | Ch 28 | Yuji vs. Mahito, a fierce battle begins! | **covered** | fought |
| 085 | Ch 226 | While Satoru Gojo can use reverse cursed technique to survive, his allies watching the fight know this situation doesn't fair well for even the strongest. | uncovered | fought (observation) |
| 086 | Ch 102 | Yuji reveals Eso and Kechizu's last words to Choso, surfacing the fury of the proud elder brother. | uncovered | description |
| 087 | Ch 146 | Everyone is given a role to execute and they move out to stop the ritual. | **covered** | departed |
| 088 | Ch 120 | Yuji regains control over his body only to witness the aftermath of all the destruction from Sukuna's merciless rampage. | uncovered | description |
| 089 | Ch 176 | Takako Uro makes her move and unleashes a technique that controls the sky. | uncovered | fought (technique, no opponent stated) |
| 090 | Ch 70 | They decide to spend the rest of their time relaxing while waiting out the time limit of the bounty. | uncovered | description |
| 091 | Ch 90 | Confronted by his dead best friend that he killed himself, Satoru learns the shocking truth and falls into the clutches of Prison Realm. | **covered** | sealed (and killed) |
| 092 | Ch 3 | Yuji is brought to the mountains of Tokyo to enroll in Tokyo Jujutsu High. | **covered** | arrived |
| 093 | Ch 156 | However, Kirara refuses to believe Megumi and Panda aren't spies for Jujutsu High, and resists them. | uncovered | fought (resists) |
| 094 | Ch 3 | Afterward, Yuji and Megumi travel to pick up the last remaining first-year, Nobara Kugisaki. | **covered** | departed |
| 095 | Ep 41 | After being severely injured in his fight against Toji, Megumi suffers a surprise attack from Shigemo. | **covered** | fought |
| 096 | Ch 268 | Despite the triumph, there are still trials and tribulations for the jujutsu sorcerers overcome. | uncovered | description |
| 097 | Ch 182 | Now he wishes to draw Kinji Hakari's blood as well as manga. | uncovered | description (wish) |
| 098 | Ch 266 | However, Yuji's struggle has breathed new life into his friend, who is ready to return the favor and stand against the King of Curses! | uncovered | fought (ready to) |
| 099 | Ch 141 | Meanwhile, Choso continues to clash with Naoya but struggles against his overwhelming speed. | **covered** | fought |
| 100 | Ch 259 | Following a tragic sacrifice, Yuji resonates with yet another brother to open a path to victory! | uncovered | description (resonates) |