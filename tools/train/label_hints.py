"""Window-specific guidance for the single-pass labeler, distilled from the
hand review of the big windows (plan/BIG_REVIEW_PATTERNS.md).

Part of THE method (plan/WINDOW_METHOD.md). Only Claude edits these hints, and only to mirror
entries of the catalog (owner rule 2026-10-07).

The procedure doc stays the fixed system prompt (prefix-cached). Two small,
targeted additions instead of the whole catalog:

  hints(window)        -> at most MAX_HINTS one-line reminders whose trigger
                          words occur in THIS window (appended to the user turn)
  repair_note(rows, w) -> the review flags that fire on the model's own rows
                          (big_flags.check), as a follow-up turn; None when
                          nothing fires, so clean answers cost nothing extra
"""
import re

MAX_HINTS = 5
MAX_REPAIR = 8

# (trigger on the window text, reminder); ordered by how often the review
# corrected that class on b7-b521, so the cap keeps the commonest ones
HINTS = [
    (r"\b(?:Avengers|X-Men|Fantastic Four|Guardians|Invaders|Defenders|Thunderbolts|Illuminati|New Mutants|"
     r"Runaways|Inhuman Royal Family|Wrecking Crew|Starjammers|Acolytes|Brotherhood|Marauders|Frightful Four|"
     r"Masters of Evil|Excalibur|X-Force|X-Factor)\b",
     "A team that acts while the window names members taking part -> one row per named member, no team row; "
     "a team row only when no member is named."),
    (r"\b(?:revealed (?:to be|as)|was (?:in fact|actually|really)|posing as|in disguise|impersonat\w*|unmasked|"
     r"now named|real name|whose real name|alias|also known as|aka)\b",
     "Identity reveal or codename + real name: use the one real/revealed name in EVERY row (no codename rows)."),
    (r"\b(?:join(?:ed|ing|s)?|rejoin\w*|teamed up|allied|alliance|united with)\b",
     "'joined the team/side', 'teamed up', 'allied' -> no met. Joining specific people where they are "
     "('joined Namor at Utopia', 'was joined by an arriving X') -> met."),
    (r"\b(?:found|discovered|reunited|visited|approached|confronted|greeted|recruited|summoned|gathered|"
     r"assembled|arriv\w+|burst into|walked in|appeared)\b",
     "Meetings are the commonest miss: an arrival/finding/visit/reunion/recruitment/confrontation where people "
     "come together -> met for each named pair (a confrontation with no attack is met, not fought)."),
    (r"\b(?:led by|under the command of|'s (?:men|forces|soldiers|team|agents|army|gang))\b",
     "A group 'led by X' or 'X's men/forces' acting -> X is the doer (rows with X)."),
    (r"\b(?:revived|resurrected|reborn|brought back to life|woke|awoke|regained consciousness|returned to life|"
     r"gained|granted|imbued|transformed into|became the new)\b",
     "Revival, waking, or a NEW power/form gained -> awakened (object null); the reviver also saved him if "
     "done for his sake."),
    (r"\b(?:seemingly|apparently|presumably|possibly|nearly|almost|tried to|attempted to|in order to|so that|"
     r"intending|planned|decided to|wished to|to save|to rescue|to stop|to kill|to capture|to meet|in exchange for)\b",
     "Hedges/plans/attempts: 'seemingly killed' -> defeated; plans, purposes, deals and attempts never made -> "
     "no row, unless the next clause says it happened ('to save him ... saving him')."),
    (r"\b(?:was|were|been) (?:freed|rescued|released|defeated|killed|captured|arrested|tied|chained|imprisoned|"
     r"jailed|taken|knocked out)\b(?! by)",
     "A passive with no 'by X' names no doer -> no row for that act (never supply the doer from context)."),
    (r"\b(?:trapped|imprisoned in|banish\w*|sealed|portal|pocket (?:universe|dimension)|Limbo|Dark Dimension|"
     r"Mirror Dimension|Quantum Realm|Negative Zone|Void|other dimension)\b",
     "Trapped in a dimension/other world, banished, forced through a portal -> sealed (not captured)."),
    (r"\b(?:brainwash\w*|manipulat\w*|possess\w*|mind control\w*|hypnoti\w*|controlled|telepathically|"
     r"stripped .{0,20}powers?|tortur\w*)\b",
     "A power used ON someone (mind control, possession, hypnosis, stripping powers, torture) -> fought."),
    (r"\b(?:fled|escap\w*|broke (?:free|out)|got away|freed (?:him|her)self|retreat\w*)\b",
     "escaped: the object is the named captor/pursuer; the place only when no captor is named. "
     "Helping someone escape captivity -> saved."),
    (r"\b(?:sedat\w*|tranquiliz\w*|knock\w* (?:\w+ )?out|unconscious|incapacitat\w*|subdu\w*|stopped|"
     r"drove (?:\w+ )?(?:away|off)|driven (?:away|off)|thrown (?:out|off)|disposed of|finish\w* off)\b",
     "Knocked out, sedated, subdued, stopped, driven off, thrown off, 'finished off' with no stated death -> "
     "defeated (not captured, not killed)."),
    (r"\b(?:betray\w*|turned on|turned against|defect\w*|double-cross\w*|mole|treachery|coup|severed .{0,15}alliance)\b",
     "betrayed: turned on / broke faith with an ally (a coup, a mole, a defection, breaking a pact). "
     "Leaving, disbanding, or tricking an enemy is not betrayal."),
    (r"\b(?:left the|quit|parted ways|departed|abandon\w*|was kicked out)\b",
     "Leaving a named team/group or a proper-named place -> departed (object = what was left)."),
    (r"\b[A-Z][a-z]+, (?:[A-Z][a-z]+ ?)+\b",
     "'City, State/Country' -> ONE arrived row with the most specific named place."),
    (r"\b(?:Kree|Skrulls?|Shi'ar|Chitauri|Brood|Inhumans|Builders|Olympians|Asgardians|Frost Giants|Sentinels|"
     r"Harpies|Eternals|Deviants|several|some of|the rest of|a group of|the squad|troops|guards|agents)\b",
     "Never an end: species/races, crowds ('several X', 'the rest of the team', 'the squad'), indefinites "
     "('a guard', 'an assailant'), items, vehicles, organisations as places."),
    (r"\b(?:Battle|Siege|War|Invasion|Incident) (?:of|at|in)\b",
     "A battle/war/incident name is an event, not a place: 'joins the Battle of Wakanda' -> no arrived row "
     "(arrived only at the named place itself)."),
    (r"(?i)\b(?:retreat\w*|repel\w*|drove \w+ off|forc\w* \w+ to (?:escape|flee)|restrain\w* .{0,30}from attacking|prevented \w+ from)\b",
     "'forced X to retreat' / 'repelled X' -> defeated X (the fight ended with X beaten). 'restrained X from "
     "attacking her' -> fought X AND saved her. 'prevented X from <doing>' (an encounter that stops X) -> met."),
    (r"(?i)\b(?:missed|instead managing to hit|accidentally (?:hit|shot|struck)|by mistake)\b",
     "Shooting/attacking X and missing -> fought X (an attack made). An ally hit by accident instead -> no row."),
    (r"\b(?:Agent|Subject|Unit|Experiment) \d+\b",
     "'Agent 33' / 'Subject 0' is the whole name: keep the word with the number (never just '33')."),
    (r"(?i)\b\d+(?:st|nd|rd|th) [Cc]entury\b",
     "A century/era is a time, not a place: 'traveled to Earth-691's 31st Century' -> arrived Earth-691."),
    (r"(?i)\b(?:restored to (?:his|her|their) (?:human|normal)|reverted to|changed back)\b",
     "Going back to a form the character already had ('restored to human form') is NOT awakened."),
    (r"(?i)\b(?:made (?:it|their way) out into|out into the streets)\b",
     "'made it out into the streets of Hala' while already on Hala is no arrived row (only a new place reached)."),
    (r"(?i)\b(?:learn\w*|knew|figur\w* out|discover\w*) how to\b",
     "'learning how to defeat X' is knowledge, not the act -> no row unless the window says it was done."),
    (r"(?i)\b(?:destroyed \w+'s (?:first |old )?body|consciousness escaped)\b",
     "Destroying a body the character survives (Ultron's consciousness escapes) -> defeated, not killed."),
    (r"(?i)\bgrabbed \w+(?: \w+)?, threatening\b",
     "Grabbing someone and threatening to hurt them = taking a hostage -> captured (plus fought)."),
    (r"(?i)\b(?:knock\w* \w+(?: \w+)? aside|manhandl\w*|ran away|got (?:his|her|their) powers back)\b",
     "'knocked them aside' mid-fight -> fought (not defeated). An opponent who 'ran away' escaped, not defeated. "
     "Getting one's own powers back is not awakened."),
    (r"(?i)\b(?:into betray\w*|restor\w* (?:a|the) \w+ (?:robot|android|Sentinel|machine))\b",
     "'X manipulated Y into betraying Z' -> Y betrayed Z (not X). 'scientists restored the robot' -> the robot "
     "awakened (not the scientists)."),
    (r"(?i)\bfought (?:with|alongside|beside)\b",
     "'X fought with/alongside Y' against a common enemy -> X and Y each fought the enemy; no row between X and Y."),
    (r"(?i)\b(?:abilities|powers|equipment|weapons|facilities)\b",
     "Descriptive sections still narrate events: one specific occurrence ('he was able to shake off a punch "
     "from Gladiator') is an event; a general ability is not."),
]
_COMPILED = [(re.compile(t), h) for t, h in HINTS]


def hints(window, section=""):
    out = []
    for rx, h in _COMPILED:
        if rx.search(window) or (rx.pattern.startswith("(?i)") and rx.search(section or "")):
            out.append(h)
        if len(out) >= MAX_HINTS:
            break
    if not out:
        return ""
    return "\n\nChecks that matter for THIS window (from reviewed mistakes on similar text):\n" + \
        "\n".join(f"- {h}" for h in out)


def repair_note(rows, window, check):
    """check = big_flags.check; returns a follow-up user turn or None."""
    flags, _ok = check(rows, window)
    flags = [f for f in flags if not f.startswith("MISS?")][:MAX_REPAIR]
    if not flags:
        return None
    return ("Review these points about your answer (each is a warning, not proof: keep a row that is right, fix "
            "or drop a row that is wrong, and add any event the procedure requires that is missing):\n"
            + "\n".join(f"- {f}" for f in flags)
            + "\n\nAnswer with the COMPLETE corrected JSON only, in the same shape.")
