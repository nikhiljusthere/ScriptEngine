"""Review aid for the 14k big-window review (plan/BIG_REVIEW_HANDOFF.md).

Prints the next N windows from the cursor like `big_review.py --next`, plus:
  DUP     the window text repeats an already-reviewed window -> its final rows
  FLAG    a 35B row matching a known error pattern (BIG_REVIEW_PATTERNS.md)
  MISS?   a sentence with an event cue that no row quote touches
  OK      a row whose quote states its own verb plainly (fast confirm)
Flags are prompts, never verdicts: every window is still read in full.

usage: python big_flags.py N [--chars 4000]   (SCRIPTENGINE_ROOT overrides the checkout)
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SCRIPTENGINE_ROOT", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import big_review as br  # noqa: E402

GROUPS = re.compile(r"^(Avengers|New Avengers|Mighty Avengers|West Coast Avengers|Secret Avengers|X-Men|New X-Men|"
                    r"X-Force|X-Factor|New Mutants|Fantastic Four|Guardians of the Galaxy|Illuminati|Inhumans|Defenders|"
                    r"Thunderbolts|Starjammers|Liberators|Invaders|Revengers|Brotherhood.*|Masters of Evil|Marauders|"
                    r"Acolytes|Hellfire Club|Morlocks|Reavers|S\.H\.I\.E\.L\.D\.|Hydra|A\.I\.M\.|Wildboys|Exceptional|"
                    r"Phoenixes|.*'s team|the team|the group|.* team)$")
CROWD = re.compile(r"(?<!-)\b(police|former|active|several|some|many|students|heroes|villains|guards|soldiers|forces|army|"
                   r"armada|fleet|thugs|men|agents|refugees|cultists|people|the group|the team)\b|^(a|an|the) ", re.I)
SPECIES = re.compile(r"^(Kree|Skrulls?|Shi'ar|Inhumans|Chitauri|Brood|Builders|Frost Giants|Dwarves|Sovereign|"
                     r"Atlanteans|mutants|humans|Kami|Olympians|Asgardians|Eternals|Deviants|Sentinels|"
                     r"Quantumnauts|Wolf-Men|Elder Gods|Harpies|Frost Giants|Dark Elves|Chitauri|Kree|Skrull)$")
VEHICLE = re.compile(r"\b(Blackbird|Quinjet|Helicarrier|Zephyr|Bus|Milano|Benatar|Starjammer|Stratojet|ship|jet|"
                     r"plane|car|truck|submarine|Ark)\b")
RANK = re.compile(r"^(?:Dr\.|Doctor|Brigadier General|Brigadier|General|Agent|Officer|Senator|Prelate|Empress|Emperor|Mayor|Detective|Sergeant|"
                  r"Colonel|Major|Lieutenant|Commander|Captain|Warlord|Professor|Chancellor|Director)\s"
                  r"(?!America\b|Marvel\b|Britain\b|Universe\b|Doom\b|Strange\b|Druid\b|Octopus\b|X\b|Xavier\b)")
# one person, two names: pairs corrected in review (extend as new ones appear)
ALIASES = [("Professor X", "Xavier"), ("Cap", "Captain America"), ("Ms. Marvel", "Carol Danvers"),
           ("Captain Marvel", "Mar-Vell"), ("Shadowcat", "Kitty Pryde"), ("Iron Man", "Tony Stark"),
           ("Black Panther", "T'Challa"), ("Scarlet Witch", "Maximoff"), ("Spider-Man", "Peter"),
           ("Goliath", "Hawkeye"), ("Freedom Ring", "Curtis"), ("Virtue", "Ethan Edwards"),
           ("Phoenix", "Jean Grey"), ("Crusader", "Z'Reg"), ("Black Queen", "Phoenix"), ("Kuurth", "Juggernaut"),
           ("Mole Man", "Harvey"), ("Torch", "Johnny"), ("Adam", "Warlock"), ("Abomination", "Blonsky"),
           ("Daredevil", "Matt Murdock"), ("Daredevil", "Murdock"), ("Falcon", "Wilson"), ("U.S.Agent", "John"),
           ("Strong Guy", "Guido"), ("Mr. Fantastic", "Richards"), ("Mr. Fantastic", "Reed"), ("Rain Boy", "Carl Aalston"),
           ("Human Torch", "Johnny Storm"), ("Captain Britain", "Brian"), ("Iron Monger", "Stane"),
           ("Black Panther", "T'Challa"), ("Ms. Marvel", "Kamala"), ("Spider-Woman", "Jessica"), ("White Queen", "Emma Frost"),
           ("Wolverine", "Logan"), ("Cyclops", "Scott"), ("Marvel Girl", "Jean"), ("Thing", "Ben"), ("Invisible Woman", "Sue"),
           ("Hulk", "Banner"), ("She-Hulk", "Walters"), ("Hawkeye", "Clint"), ("Black Widow", "Natasha"),
           ("Winter Soldier", "Barnes"), ("Scarlet Witch", "Wanda"), ("Quicksilver", "Pietro"), ("Vision", "Vis")]
DISGUISE = re.compile(r"revealed (?:to be|as|himself|herself)|was (?:in fact|actually|really)|posing as|masquerad|"
                      r"in disguise|impersonat|unmasked|now named|true identity|alias", re.I)
LEAD = ("When|After|Before|As|While|Then|Meanwhile|However|Although|Though|Once|Since|During|With|Without|"
        "Following|Upon|Using|Back|In|On|At|There|Here|Together|Both|Later|Soon|Eventually|Finally|Despite|The|A|An|His|Her|Their|Its|"
        "Captain America|Iron Man|Spider-Man")
PURPOSE = re.compile(r"\b(?:to|in order to|intending to|planning to|hoping to|attempt(?:ed|ing)? to|tried to|"
                     r"decided to|wished to|wanted to|so (?:that )?(?:he|she|they) could) (?:meet|find|rescue|save|stop|"
                     r"kill|capture|free|defeat|fight|attack|destroy|confront|recover|retrieve)\b", re.I)
JOIN = re.compile(r"\bjoin|teamed up|allied|alliance|rejoin", re.I)
TRAP = re.compile(r"imprison\w* in|trapped|ensnared|Limbo|Dimension|Realm|Void|Mojoverse|pocket universe", re.I)
HEDGE = re.compile(r"seemingly|nearly|almost|apparently|attempt|tried to|would have", re.I)
CUES = re.compile(r"\b(rescu\w*|saved?|saving|freed|free (?:him|her|them)|releas\w*|escap\w*|fled|flee|broke (?:free|out)|"
                  r"kidnap\w*|abduct\w*|captur\w*|arrest\w*|apprehend\w*|imprison\w*|detain\w*|prisoner|killed|slew|slain|"
                  r"murder\w*|assassinat\w*|defeat\w*|knock\w* (?:out|unconscious)|subdu\w*|"
                  r"overpower\w*|incapacitat\w*|attack\w*|battl\w*|fought|fight\w*|clash\w*|ambush\w*|confront\w*|"
                  r"betray\w*|turned (?:on|against)|met|meet\w*|found|visit\w*|recruit\w*|assembl\w*|gather\w*|greeted|"
                  r"arriv\w*|returned to|went to|traveled to|travelled to|brought (?:\w+ )?to|taken to|left the|"
                  r"woke|awak\w*|reviv\w*|resurrect\w*|reborn|brainwash\w*|manipulat\w*|possess\w*|sealed|banish\w*|"
                  r"trapp\w*)\b", re.I)
PLAIN = {"fought": r"attack|fought|fight|battl|clash|ambush|struck|punch|shot|stabb|wound",
         "defeated": r"defeat|knock|subdu|beat|overpower|incapacitat", "killed": r"kill|slew|slain|murder|assassinat",
         "captured": r"captur|kidnap|abduct|arrest|apprehend|prisoner|captive", "saved": r"sav|rescu|freed",
         "escaped": r"escap|fled|flee|broke free", "met": r"\bmet\b|found|visit|greeted|encounter|reunit",
         "arrived": r"arriv|returned to|went to|travel|landed|back to|took .* to", "departed": r"\bleft\b|depart|abandon",
         "awakened": r"woke|awak|reviv|resurrect|reborn|regain", "betrayed": r"betray|turned on", "sealed": r"seal|trap|banish"}


def norm(t):
    return re.sub(r"\W+", " ", t).strip().lower()


def sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+|\n+", t) if len(s) > 20]


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    chars = int(sys.argv[sys.argv.index("--chars") + 1]) if "--chars" in sys.argv else 4000
    rows, c, pas = br.jl(br.LABELS), int(os.environ.get("BF_FROM", br.cursor())), br.passages()
    final = {a["id"]: a["after"] for a in br.jl(br.AUDIT)}
    seen = {}
    for i, r in enumerate(rows[:c], 1):
        seen.setdefault(norm(pas[r["id"]])[:400], (i, r["id"]))
    for i, r in enumerate(rows[c:c + n], c + 1):
        text = pas[r["id"]][:chars]
        ev = r["events"]
        print(f"===== b{i} {r['page']} / {r['section']}" + ("" if r["ok"] else "  [PARSE FAIL]"))
        key = norm(pas[r["id"]])[:400]
        dup = seen.get(key)
        if dup:
            prev_rows = final.get(dup[1], rows[dup[0] - 1]["events"])
            same = norm(pas[r["id"]]) == norm(pas[dup[1]])
            print(f" DUP of b{dup[0]} ({'identical text' if same else 'same opening, text differs: read the tail'})"
                  f" final rows: {[(e['subject'], e['verb'], e['object']) for e in prev_rows]}")
        seen.setdefault(key, (i, r["id"]))
        print(text)
        print(" ROWS", [(e["subject"], e["verb"], e["object"], e["quote"][:50]) for e in ev] or "[]")
        if r.get("dropped"):
            print(" GATE-DROPPED", [(d.get("subject"), d.get("verb"), d.get("object"), d.get("why")) for d in r["dropped"]])
        flags, ok = [], []
        # multi-word names; a sentence-initial word ("When Loki") or a trailing "the" is not part of the name
        names = {re.sub(r"^(?:%s) " % LEAD, "", m) for m in
                 re.findall(r"\b[A-Z][\w'-]+(?: (?:of |the |de |von )?[A-Z][\w'-]+)+", text)}
        names = {m for m in names if " " in m}
        for e in ev:
            s, v, o, q = e["subject"], e["verb"], e["object"], e["quote"]
            tag = f"{s}|{v}|{o}"
            for end in (s, o):
                if not end:
                    continue
                if GROUPS.match(end):
                    flags.append(f"{tag}: group end '{end}' -> named members tied to the event? (G.2/R19)")
                if CROWD.search(end):
                    flags.append(f"{tag}: crowd/indefinite end '{end}' (R11)")
                if SPECIES.match(end):
                    flags.append(f"{tag}: species end '{end}'")
                if RANK.match(end):
                    flags.append(f"{tag}: rank prefix in '{end}' -> strip")
                longer = sorted(nm for nm in names if nm != end and not RANK.match(nm)
                                and (nm.endswith(" " + end) or nm.startswith(end + " ")))
                if longer:
                    flags.append(f"{tag}: fuller name in window for '{end}': {longer}")
                if (end[:1].islower() and not re.match(r"(?:van|von|de|del|da|di|le|la|al|el) [A-Z]", end)) \
                        or "'s " in end or "' " in end or len(end) <= 2 or end.startswith("version of"):
                    flags.append(f"{tag}: description/garbage end '{end}' -> a named or definite individual?")
                for a_, b_ in ALIASES:
                    if end in (a_, b_) and re.search(rf"\b{re.escape(a_)}\b", text) and re.search(rf"\b{re.escape(b_)}\b", text):
                        flags.append(f"{tag}: window has both '{a_}' and '{b_}' -> one name per person")
            if v == "met" and JOIN.search(q):
                flags.append(f"{tag}: met from joining/allying (R4/R12)")
            if v == "captured" and TRAP.search(q):
                flags.append(f"{tag}: trapped in a dimension/place -> sealed? (R20)")
            if v == "fought" and re.search(r"confront|faced", q, re.I) and not re.search(PLAIN["fought"], q, re.I):
                flags.append(f"{tag}: confrontation without a stated attack -> met (R2)")
            if v in ("killed", "defeated", "captured", "escaped", "saved") and HEDGE.search(q):
                flags.append(f"{tag}: hedged/attempt wording '{HEDGE.search(q).group(0)}'")
            if re.search(r"\b(was|were|been) (defeated|freed|rescued|released|killed|captured|arrested|tied|chained|locked|imprisoned|jailed|taken)\b", q) \
                    and " by " not in q:
                flags.append(f"{tag}: passive with no 'by' -> doer stated? (R17)")
            if re.search(r"in exchange for|agreed to|promised to|offered to", q, re.I):
                flags.append(f"{tag}: deal/offer wording -> the promised act did not happen (A23)")
            if v == "met" and re.search(r"Watcher|Uatu", s) and re.search(r"visit|watch|observ|went to", q, re.I):
                flags.append(f"{tag}: the Watcher observing a universe is not a meeting (A27)")
            if v in ("fought", "captured") and re.search(r"sedat|knock\w* (?:him|her|them) out|unconscious", q, re.I):
                flags.append(f"{tag}: sedated/knocked out -> defeated (A29)")
            if v == "killed" and re.search(r"\bkill(?:ed)? it\b|destroy(?:ed)? it\b", q, re.I):
                flags.append(f"{tag}: killed 'it' -> the host or a thing on him? (A53)")
            if v == "killed" and re.search(r"finish\w* off|survive|possess|terminat", q, re.I):
                flags.append(f"{tag}: 'finished off'/survived/possession -> defeated or fought? (A21/A22)")
            if v == "killed" and (re.search(r"dispos\w* of|took (?:him|her) out|dispatched", q, re.I)
                                  or re.search(r"Industries|Corporation|Corp\b|missile|bomb", s)):
                flags.append(f"{tag}: 'disposed of' with no death -> defeated; a company/item is no doer (A38/A39)")
            if PURPOSE.search(q) and not re.search(r"(?:managed|able|succeeded|in time|went on) to", q, re.I):
                flags.append(f"{tag}: purpose clause '{PURPOSE.search(q).group(0)}' -> did it happen? (step 3)")
            if v == "fought" and re.search(r"(?:ship|boat|plane|car|truck|train|building|base|city|planet)\b.{0,15}"
                                           r"(?:was|were) attacked|attacked the (?:ship|boat|plane|base|city|planet)", q, re.I):
                flags.append(f"{tag}: an attack on a vehicle/building/place is not fought (A42)")
            if re.search(r"\b(?:the two|the pair|both|the duo|the trio|they|them)\b", q, re.I) and v != "met":
                flags.append(f"{tag}: plural referent in quote -> who exactly? (A41)")
            if v == "saved" and re.search(r"\bdefended\b", q, re.I):
                flags.append(f"{tag}: 'defended' -> physical protection or only words? (A36)")
            if v == "saved" and re.search(r"\bhelp", q, re.I) and not re.search(PLAIN["saved"], q, re.I):
                flags.append(f"{tag}: 'helped' is not a rescue (R23)")
            if v == "arrived" and re.search(r"while taking|on (?:his|her|their) way|heading|in order to|hoping", q, re.I):
                flags.append(f"{tag}: heading/purpose, not an arrival")
            if v == "betrayed" and re.search(r"abandon|left|disassembl|drove", q, re.I):
                flags.append(f"{tag}: leaving/disbanding is not betrayal (R14/R24)")
            if v == "escaped" and o and re.search(r"Academy|Prison|Base|Facility|Room|Dimension|Realm|Raft|Asylum|"
                                                  r"Hospital|Mansion|Tower|Island|Limbo|Hell|Vault|Cell|Building", o):
                flags.append(f"{tag}: escaped a place -> does the window name the captor? (A50)")
            if v in ("arrived", "departed", "escaped") and o and ", " in o:
                flags.append(f"{tag}: comma in place '{o}' -> R1 most specific part (gate splits it)")
            if v == "awakened" and re.search(r"\b(?:revived|resurrected|brought back)\b(?! by)", q) and \
                    not re.search(r"^(?:\w+ )?(?:was|were) ", q):
                flags.append(f"{tag}: someone revived him -> also '<reviver> saved' (A33)")
            if v in ("arrived", "departed") and o and VEHICLE.search(o):
                flags.append(f"{tag}: '{o}' is a vehicle, not a place (A24)")
            if v in ("arrived", "departed") and o and (o[:1].islower() or "'s " in o):
                flags.append(f"{tag}: description place '{o}'")
            if v in PLAIN and re.search(PLAIN[v], q, re.I) and not any(f.startswith(tag) for f in flags):
                ok.append(tag)
        if DISGUISE.search(text):
            flags.append(f"identity reveal in window ('{DISGUISE.search(text).group(0)}') -> one name per person (R10)")
        if re.search(r"\bled by\b", text):
            flags.append("window has 'led by' -> a group led by a named leader acts through the leader (R21)")
        quotes = [e["quote"] for e in ev]
        for k, sent in enumerate(sentences(text), 1):
            if sent.lstrip()[:1] in '"“':
                continue
            cues = sorted({m.group(0).lower() for m in CUES.finditer(sent)})
            if cues and not any(q in sent or sent in q for q in quotes):
                flags.append(f"MISS? s{k} [{', '.join(cues)}]")
        for f in flags:
            print("  " + ("" if f.startswith("MISS?") else "FLAG ") + f)
        if ok:
            print("  OK:", ok)
    print(f"[printed b{c+1}..b{min(c + n, len(rows))} of {len(rows)}; mark with --mark {min(c + n, len(rows))}]")


if __name__ == "__main__":
    main()
