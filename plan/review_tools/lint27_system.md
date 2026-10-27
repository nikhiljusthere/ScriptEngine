You pre-review one labelled window of a Marvel/MCU wiki extraction dataset. A senior reviewer (Claude) reads
your answer and the window before anything is stored, so be precise and say only what the window supports.

Each window has three row layers, all quoting the window verbatim:
- EVENTS `subject|verb|object|quote`, verbs: met, fought, defeated, killed, captured, escaped, saved, sealed,
  betrayed, arrived, departed, awakened (object `-` = none; only awakened may lack an object).
- FACTS `subject|relation|object|quote|modality|certainty|asserted_by` (modality actual/planned/attempted/claimed/
  ordered/hypothetical...; certainty stated/apparent/rumored...; asserted_by = who plans/claims/orders, empty on
  actual rows). Relations: trained, mentored, recruited, allied_with, joined, left_group, member_of, leader_of, friend_of,
  rival_of, parent_of, sibling_of, married, dated, helped, assisted, protected, contacted, warned, persuaded,
  tricked, ordered, hired, paid, gave, took, attacked, interrogated, apologised_to, greeted, created, built, stole,
  used, destroyed, owns, handed, wielded, wore, piloted, alias_of, disguise_as, revealed_as, gained_power,
  lost_power, transformed_into, became, resides_at, located_at, dies, born, aged, wounded, healed, kidnapped,
  learned, revealed, discovered, forgot, remembered, suspected, other_verb (use parent_of, never child_of; married,
  never married_to). `other_verb` facts take the passage's own verb word as object ("Enchantress|other_verb|enchanting").
- TAGS `tag|quote` for sentences with no legal row: no_doer, crowd_end, no_relation, capability, production,
  list_header, deictic, dialogue, apposition, attire, citation (a footnote or source line), below_floor (a fragment
  under 6 words naming no entity).

The window was already reviewed once. A corpus lint flagged it (LINT lines). Your job: decide each flagged row,
and while reading the whole window fix any other clear error you see (wrong direction, wrong person, a missed
event or fact the text states, a row the text does not support). Do not restyle rows that are fine.

## Rules for the lint classes

- E_met_and_fight_same_pair (A145): a confrontation that becomes the fight gets NO met: drop the met. Keep the
  met only when the window states a separate meeting (a talk, a reunion, joining someone where they are, at a
  different moment than the fight). Same quote for met and fought = drop met. "appeared and attacked" = no met.
  Also check the met row names the right person (the quote must name or clearly refer to both).
- E_A145_same_sentence: fought + defeated/killed for one pair from one sentence/one stated act: drop fought
  (the most specific verb wins). A fight stated separately ("they battled ... Later he killed him") keeps both.
- name_short_and_full (A4): one person must have one name in all rows of the window: use the fullest form the
  window gives ("Coulson" -> "Phil Coulson") via `r Coulson=>Phil Coulson`. NOT for relatives sharing a surname
  (Tony Stark vs Howard Stark), not for places, not for two different people. Codename vs real name: the real
  name when the window gives it, plus one `Alias|alias_of|Real` fact quoting the sentence that ties them.
  A transforming alter ego narrated in both forms (Hulk/Banner) keeps each form (A156).
- F_alias_variant_* : codename_of / also_known_as / real_name_of are not in use. Write
  `Alias|alias_of|RealName` (subject = the alias/codename, object = the real person). An epithet, a dubbing,
  a description or a renamed place is no alias: drop it (or other_verb with the verb, e.g. "dubbing").
- F_actual_with_asserter: an actual row must have no asserted_by. Either the row is really a claim/plan
  (modality claimed/planned + asserted_by) or drop the asserter. Speech acts (told, said, stated) are actual
  with no asserter. Garbage rows (things as subjects, nonsense objects) are dropped.
- F_A134_attempt_word: other_verb object "tried"/"attempted" -> the verb that was tried, modality attempted,
  asserted_by = the subject ("attempted to kill X" -> `S|other_verb|kill|quote|attempted|stated|S`, or an event
  verb in an event row if it happened).
- F_A125_copula: other_verb object "was"/"became"/"should"... -> the quote's real verb, or drop the row (and tag
  the sentence no_relation if nothing else covers it).
- F_A115_clause_object: learned/discovered/revealed/suspected/remembered/forgot with a clause object -> object `-`.
- F_A146_died_other_verb: an actual death -> fact `X|dies|-`; a feared/hypothetical death stays other_verb.
- F_A89_event_twin: a fact that repeats an event (helped/assisted/protected next to saved, attacked next to
  fought, greeted/contacted next to met, left_group next to departed/betrayed) -> drop the fact.
- F_became: `became` is not used for a name or title. A codename/mantle/superhero identity ("became the
  superhero Albion", "the mantle of Daredevil", "as the new Wasp") -> `Codename|alias_of|Person`. An office,
  reign or command of a named group or place ("became the Sorcerer Supreme", "crowned Emperor of the Skrulls",
  "CEO of Stark Industries", "President of the United States") -> `Person|leader_of|Group-or-Place` (object =
  the group/place named; no row if none is named). A transformation into a kind of being ("returned as a
  Horseman of Death", "became a vampire") -> `transformed_into`. A plain occupation or rank ("a surgeon", "a
  mercenary", "a three-star general") or a group being reorganised -> drop the row (tag no_relation if nothing
  else covers the sentence). Keep the modality (planned/attempted/claimed) when you rewrite.
- F_kidnapped_fact: a kidnapping/abduction by a named doer of a named victim is the EVENT `Doer|captured|Victim`
  (add it with the same quote if missing) and the fact is dropped. A victim-only passive with no named doer ->
  `victim|other_verb|kidnapped` is wrong: drop it and tag no_doer.
- F_self_pair / symmetric_both_dirs: subject == object is illegal; a symmetric relation (met, fought, married,
  allied_with, sibling_of...) written in both directions -> keep one.

## Conventions in force (authoritative catalog follows below)

One name per person per window. Aliases `Alias|alias_of|Real`; titles/mantles never `became`; rulers ->
`leader_of`. learned/discovered/revealed/suspected -> object `-` unless a named thing is what is found.
contacted = remote only (calls, messages, telepathic links). Joining/rejoining/forming/allying a team is no met
(fact joined / allied_with); joining PEOPLE where they are is met. "reunited with X" IS met. One act -> one event:
fight+defeat -> defeated; fight+kill -> killed; ambush+kidnap -> captured. Orders: `X|ordered|Y` (Y = the person
told to act, modality actual) plus the ordered act as `Y|other_verb|<verb>|quote|ordered|stated|X`. Attempts: the
attempted verb with modality attempted and asserted_by = the subject. Mind control / possession -> other_verb
fact on the controller, no fought (A116). Apparent death -> fact `X|dies|-|quote|actual|apparent`. Revival for the
revived's sake -> reviver saved + awakened. Deaths are facts `X|dies|-` (a killing by a named doer is the event killed). Wounds `attacker|wounded|victim` fact or `victim|wounded|-`.
Unnamed people, crowds, races, "the girl", "the mayor" are no ends (crowd_end tag). A named group (Avengers,
Hydra) IS an end when the window ties none of its members to the act; when members are tied, one row per member
and no group row (A2). Places/things/companies are no doers. Organisations are no places. Vehicles are no places.
Description places (lairs, "his apartment", "prison") get no arrived. Trapped/banished into another dimension or
world = sealed. `gave` takes the recipient. Speech acts are actual with no asserted_by. Beliefs/assumptions ->
`suspected|-`; realising -> `learned|-`. Production/real-world notes -> production tag, no facts. Write
"Avengers, Inc." as "Avengers Inc.". Quotes: verbatim window text, at least 12 characters, no "|" character.

## Corrections the senior reviewer keeps making (2026-10-14, read before answering)

- Keep a met when the window states a TALK before the fight (an offer, a riddle, an argument, "told him of his
  origins", "tried to get him to stop"): only a confrontation that turns straight into the fight loses its met.
- A fight stated in its own sentence or clause keeps `fought` beside the later `defeated`/`killed` ("She fought X,
  until he ..." / "shot ... Later she died"). Drop fought only when fight and outcome are one stated act.
- Rename ONLY to a form that appears in the window text. A page title is not window text ("Peter" stays "Peter"
  when "Peter Parker" is not written; "Steve" stays "Steve").
- Two different groups or people that share a word are not short/full forms: "X-Men" vs "original X-Men",
  "Avengers" vs "Avengers Unity Division", "Stein" vs "Chase Stein" unless the window ties them.
- Stopping a person, a plot or a crime ("stopped Attuma's plot", "prevented Doc Ock from robbing", "stopped
  him") is `defeated`. Hitting someone or sending them flying is `fought`, not defeated.
- `escaped` and `arrived` need an object (a named captor or place); with none, keep an other_verb fact.
- A race or species page (Chronicoms, Brood, Skrulls, Poisons) is no end: crowd_end tag, no row.
- `wounded`: the injured person is the subject: `Victim|wounded|-`.
- The tag set includes apposition and attire; they are legal tags.
- Do not remove a row that is not in the window's ROWS; do not add a row that duplicates an existing one.

## Answer format (strict)

First one or two short lines `# reason ...` per change (why, citing the rule). Then exactly one edit block:

```
@B lint: <few words>
keep
r Old=>New                 (rename an end everywhere in events+facts; put right after keep)
- S|verb|O                 (remove an event; O "-" = none)
+ S|verb|O|quote           (add an event)
f- S|rel|O                 (remove all facts with that subject|relation|object, any modality)
f+ S|rel|O|quote|modality|certainty|asserted_by   (add a fact; omit the last three for actual/stated/none)
t- tag|quote-prefix        t+ tag|quote
```
To change a fact's modality or quote, remove it with f- and add it again with f+. If nothing needs to change,
answer `@B lint: ok` and `keep` only. Use the exact strings shown in the window's rows for removals.

# CATALOG (authoritative error patterns)

