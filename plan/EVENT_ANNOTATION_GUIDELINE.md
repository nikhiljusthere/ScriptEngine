# Event annotation guideline (gold labels for the student extractor)

Version 1, 2026-09-29. Built from the error classes of the 2026-09-29 JJK judged
sets (`reports/jjk/judged/`). It extends the prompt's verb definitions
(`events.py` `VERB_DEFINITIONS`, prompt `.9`) and must never contradict them. The
gold is the list of events the passage **states**. Every gold label, the Qwen
worker prompt and every adjudication follow this file. When a case is not
covered here, add a rule rather than deciding it ad hoc.

## A. What an event is

1. The passage states it happened, in this passage. It is not planned, intended
   ("in order to", "tries to", "prepares to", "decides to", "plans"),
   hypothetical ("would have"), negated ("couldn't defeat"), wished, remembered
   as a possibility, or only asked about.
2. A **failed attempt** is no event of that verb. "Panda and Atsuya start to
   escape but Sukuna stops them" is no escape. An attack that lands is `fought`
   even if its purpose failed.
3. A flashback or a later summary states an event just as well: "Masaki recalls
   his past defeat at Yuji's hands" → Yuji `defeated` Masaki.
4. Descriptions of powers, appearance, personality, rules and techniques are not
   events. Where such a section narrates a specific occurrence ("he used it in his
   battle with X"), that occurrence is an event.

## B. Who can be an end

5. **Named** characters, creatures (including named shikigami and curses: Mahoraga,
   Nue, Rika), named groups with a proper name (the Hei, the Kukuru Unit, Tokyo
   Team), and named places (for arrived/departed). Write the name as the
   passage writes it: its fullest form in the passage, pronouns resolved only
   where the passage makes the referent unambiguous.
6. **Never an end:** a generic class or unnamed people ("curses", "the soldiers",
   "civilians", "a curse user", "his foes"); a technique, a domain, an attack or an
   item ("Blue", "Granite Blast", "Prison Realm", "the katana"). When a technique,
   weapon or shikigami acting under orders does something, **the user is the
   subject**, unless the passage presents the shikigami itself as the actor with
   its own name (then either is acceptable; prefer the named creature).
7. Titles used as names ("the President", "Principal Yaga") are ends.
8. A group sentence expands: "Yuji and Aoi fought Hanami" → two rows. A list
   expands fully: "Maki annihilates the Hei, including Ranta, Chojuro, Nobuaki
   and Jinichi" → one `killed` row per named member. **But** a clause is never
   expanded to people it does not name or clearly refer to. "They enter the
   room" is no meeting with everyone in the room.

## C. The verbs

| verb | yes | no |
|---|---|---|
| `fought` | an attack, blow, clash, battle, duel, technique used on someone; "engages", "battles", "attacks", "strikes", "pummels"; a named battle between them | a confrontation or face-off with no attack stated; a threat; an argument; a scolding, smack or rebuke in conversation ("lashes out at Panda" verbally); being stopped |
| `defeated` | the passage states the fight **ended** with the object beaten: defeated, beat, bested, won against, lost to (write X defeated Y), knocked out, left unconscious, subdued, incapacitated, "finishes the fight", "dominated/overwhelmed ... in the fight" when presented as its result | a hit, a wound, a throw, knock-back, a Black Flash landing, having the upper hand, "nearly defeats", "overpowers in the initial exchange", "appeared to defeat" |
| `killed` | a stated death caused by the subject (exorcised a curse = killed; "cut down" only when death is stated; destroyed a shikigami = killed) | fatal-looking wounds the object survives; "eliminated from the game"; a death whose doer is not stated |
| `captured` | took the object prisoner or hostage: captured, abducted, kidnapped, held captive, dragged to a cell | trapping in a domain, barrier, ice or sealing object (that is `sealed`); taking or collecting items |
| `sealed` | trapped, sealed or banished the object in a domain, barrier, ice, a sealing object or another world | casting a domain with no one stated as trapped |
| `escaped` | got away from the object's captivity, trap or pursuit: escaped, fled, broke free | dodging or evading an attack (that is `fought`); a failed or attempted escape; leaving calmly |
| `saved` | rescued, freed, protected from harm; carried someone to safety; healed someone who would otherwise die, or treated their injuries | calming someone; helping with a task; wanting or going to save |
| `betrayed` | turned against an ally, defected, double-crossed | deceiving an enemy; misleading; punishing; resenting; leaving; rejecting an ideology |
| `met` | the two **come together** in the passage: a first meeting, a visit, an encounter, a reunion, meeting up, a meeting held between them, someone arriving to confront or talk to people not already with them, introducing oneself | talk between people already together in the scene (companions conversing is not a new meeting); merely being present; noticing, sensing or watching; reporting about someone; helping; a mission together; allying; a goodbye; seeing someone off; an order about someone |
| `arrived` | reached a named place | heading toward a place; "gets closer" |
| `departed` | left a named place or group (the object is the place left, never the destination) | "heads to X" (that is neither) |
| `awakened` | woke up, revived, came back to life, gained a new power or form, evolved; no object | using, activating or reactivating a technique already had; incarnating someone else |

When two verbs both fit, write the more specific one (`defeated` over `fought`,
`killed` over `defeated`). If the passage also states the fight, write both:
"Yuji fought Ko-Guy ... exorcises him" → `fought` + `killed`.

14. **Precision first.** When a case stays genuinely ambiguous after these rules,
    leave it out of the gold. A borderline row the student learns to write is a
    wrong row at 300k-page scale; a borderline row it learns to skip costs
    little.

## D. Rows

9. One row per (subject, verb, object) per window. Choose the quote that states it
   most directly. `fought` and `met` are symmetric: **one row per pair**, with the
   subject the one the clause presents as acting first ("Choso attacks Gojo" →
   Choso fought Gojo; never also Gojo fought Choso).
10. `quote` is copied word for word: the shortest clause that states the event,
    at least 12 characters, no paraphrase.
11. Direction: the subject is the doer. Passive voice: the doer follows "by".
    "Y lost to X" is X `defeated` Y.
12. `awakened` has object `null`. No other verb has a null object, and subject ==
    object only when the passage says the act was self-directed ("stabs himself").
13. An empty list is a correct answer. Most descriptive windows have none.

## E. Rulings (precedents from adjudication, 2026-09-29)

Each is a case the rules above decide; recorded so every annotator decides it the
same way.

- **Travel completed = `arrived`:** "went to X", "enters X", "infiltrates X",
  "descends into X", "returning to the house" → arrived at X. "Heads to X",
  "goes off to X" (no arrival stated) → nothing.
- **"finds / comes across X" + contact = `met`;** "find X and follow him" (no
  contact) → nothing; "located X" → nothing.
- **A class used as a name is still a class:** "a Finger Bearer", "the Finger
  Bearer", "Cursed Spirit", "Curse User", "Jujutsu Sorcerers" → never an end.
- **"dispatching X"** without a stated death → `defeated`, not `killed`.
  **"cut him in half"** without a stated death → `fought`.
- **"came out on top", "outclassed", "effortlessly overpowered" as the result of
  a fight** → `defeated`. "Seemingly victorious", "appears to have exorcised" →
  nothing (the passage says it did not happen).
- **A retreat forced by the finishing blow** ("forces Geto to retreat") → `defeated`.
- **Restrained or held by a captor or their shikigami** ("has Kokun restrained")
  → `captured`. Frozen or trapped in place by a technique → `sealed`.
- **A double, a copy or a body part is not the person:** "kills the double" is
  not a kill of Mahito.
- **A clause cut off at the window edge** ("…ab a katana into the arm") is
  attributed to no one: only what the visible text states.
- **A deceased or incarnated identity** is written as the passage names it
  ("Pseudo-Geto", "Geto"); resolving who that is belongs to the engine, not to
  the label.

## F. Universal amendments (2026-10-04)

These amendments make this guideline universal -- every anime/Fandom wiki,
not only JJK (`plan/UNIVERSAL_DATASET_PLAN.md`, decisions 3-4). They
supersede the JJK-specific wording they name; all other text in this file
stands. JJK stays the worked example.

### F.1 Per-window labels (precedent 6 retired as a label)

The student reads ONE window. Every window is labeled independently: a
window that states a meeting gets its own `met` row even when an adjacent
window states the same meeting. A label that omitted an event the window
itself states would teach omission (a recall bug). The JJK precedent 6
("one `met` per pair per meeting, even across different windows",
`plan/JJK_VERIFY_7000_FINAL.md` §5a) is superseded for labeling: what one
pair-per-meeting merging still governs is the engine, not the annotator --
`events.py` already dedups a page's rows on (label, subject, verb,
object) (its `dedup` drop). The verdict rules of section E (what counts
as a `met` at all) are untouched; only the cross-window merging of labels
is retired.

### F.2 The general entity rule (replaces the JJK shikigami list)

A NAMED individual creature, summon, AI or construct counts as an entity
(a subject or object). A species, a class, a technique, an item or an
unnamed group never does. This supersedes the JJK-only shikigami list in
rules 5-6 (named shikigami and curses: Mahoraga, Nue, Rika): any
fandom's named creature, named summon, named AI or named construct is an
end, and JJK's named shikigami are one instance of the rule. Rule 6's
user-is-the-subject carve-out stands as written: a named creature acting
under orders may be written as the actor when the passage presents it
with its own name.

### F.3 One inventory: the 12 verbs

The table in section C is the ONE verb inventory for every wiki: the nine
shared verbs (`fought`, `killed`, `awakened`, `sealed`, `betrayed`,
`saved`, `arrived`, `departed`, `met`) plus the three outcome verbs
(`defeated`, `captured`, `escaped`). Every wiki now declares the outcome
verbs (its `events: extra_verbs` in `series/<wiki>/overrides.yaml`,
2026-10-04); no wiki runs a smaller or different set. A student trained
across wikis sees one inventory and never has to learn when a verb is
forbidden; the outcome verbs carry the match-up brain goal (the shared
set records that a fight happened, not who won).
