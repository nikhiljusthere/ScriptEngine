# Blind second reading: rules

You label wiki passages sentence by sentence. You are an independent second reader: your labels will be
compared with an existing set to find its errors, so your own careful reading is the whole point.

For each window you get: the page and section, `page_text_before` and `page_text_after` (the page's text on
either side, context only, never labelled), a numbered `candidates` list (the entities this page links or
names), and numbered `sentences`.

For every sentence give:

- `class`, one of:
  - `event`: the sentence narrates an act or an occurrence: something done, said, decided, noticed, suffered
    or happening, whoever does it, named or not.
  - `standing state`: it states a lasting relation, identity, membership, possession or location, and no act.
  - `trait`: it describes an ability, a power, an appearance or restates who someone is.
  - `trivia`: production notes, citations and reference markers, headings and list entries, quoted dialogue
    lines, pure transitions, and anything that states none of the above.
- `real`: `false` when everything the sentence states is only planned, attempted and failed, ordered,
  claimed, imagined or hypothetical, so nothing in it is stated as having happened. Otherwise `true`.
- `people`: the candidate numbers of everyone and everything named that takes part in what the sentence
  states, as doer, receiver or object (a wielded item, a place reached). Resolve pronouns and descriptions
  ("the two", "his teacher") to the named entity. Use the window first; use the page text before it only to
  resolve a pronoun the window leaves open. Leave out anyone not on the list. Unnamed people and crowds have
  no number.
- `events`: one `[verb, subject number, object number or null]` for each act below that the sentence states
  as having actually happened, with a named doer. Twelve verbs only:
  - `fought`: an attack made on someone, even if blocked or dodged; a technique used on someone. Not a
    threat, an argument, or drawing a weapon. One per pair.
  - `defeated`: the fight ended with the object beaten, knocked out, subdued or incapacitated.
  - `killed`: a stated death with its doer. `killed` replaces `defeated` and `fought` for the same act.
  - `captured`: took prisoner, kidnapped, arrested, tied up, pulled away against their will.
  - `sealed`: trapped in a barrier, a domain, a dimension or a sealed place.
  - `escaped`: got away from a captor, a trap or a pursuer (object: the captor, else the named place).
  - `saved`: rescued, freed, protected from a blow, healed someone who would otherwise die.
  - `betrayed`: turned on an ally.
  - `met`: two named characters come together: a first meeting, a visit, a reunion, arriving or showing up
    where the other is, a confrontation with no attack. One per pair. Not when that encounter is itself the
    fight, not for companions who never parted, not for a call.
  - `arrived` / `departed`: reached or left a proper-named place (the place is the object).
  - `awakened`: regained consciousness, was revived, or gained a new power or form for the first time. Not
    waking from ordinary sleep. Object is null.
  Rules: a line of a battles list such as "A vs. B" or "A and B vs. C" is an `event` line with one
  `fought` per opposing pair. The doer of a passive is the one after "by"; a passive with no doer gets no event. A weapon or a
  technique is never the doer, its user is. A group named with its members becomes one triple per member.
  Never supply a doer or a name from outside the window and the page text given.

Output: one JSON object per window, one per line, in the order given:
`{"id": "...", "lines": [{"n": 1, "class": "event", "real": true, "people": [3, 7], "events": [["fought", 3, 7]]}, ...]}`
Every sentence number must appear. Use only numbers from that window's candidate list.
