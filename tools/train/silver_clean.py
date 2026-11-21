"""Deterministic guideline corrections for teacher (silver) targets
(plan/EVENT_ANNOTATION_GUIDELINE.md). Lexical, conservative, measured on the
hand gold before use. A row is corrected only toward what the guideline says:
a symmetric duplicate collapses (rule 9); a `defeated` whose quote states no
win becomes `fought` (C: a hit is not a defeat); a `met` whose quote carries no
coming-together cue goes (C: companions talking is no meeting); an `escaped`
with no flight cue goes (C: dodging is not escaping)."""
import re

WIN = re.compile(r"\b(defeat\w*|beat(s|en)?|best(s|ed)|knock\w* (out|unconscious)|unconscious|lost|lose|loses|win|wins|won|victor\w*|subdu\w*|incapacitat\w*|finish\w* (him|her|them|off|the fight)|outclass\w*|dominat\w*|overwhelm\w*|overpower\w*|dispatch\w*|crush\w*)\b", re.I)
MEET = re.compile(r"\b(meet\w*|met|visit\w*|encounter\w*|confront\w*|introduc\w*|reunit\w*|appear\w*|arriv\w*|join\w*|greet\w*|(came|come|comes) across|r[au]n into|find|finds|found|regroup\w*|approach\w*)\b", re.I)
FLEE = re.compile(r"\b(escap\w*|fle[ed]\w*|flees|flight|broke free|breaks? free|got away|gets away|run(s|ning)? away|ran away|retreat\w*)\b", re.I)
SYM = {"fought", "met"}


def clean(events):
    out, seen = [], set()
    for e in events:
        v = (e.get("verb") or "").lower()
        q = e.get("quote") or ""
        if v == "defeated" and not WIN.search(q):
            e = {**e, "verb": "fought"}; v = "fought"
        if v == "met" and not MEET.search(q):
            continue
        if v == "escaped" and not FLEE.search(q):
            continue
        s, o = (e.get("subject") or "").lower(), (e.get("object") or "").lower()
        k = (v, frozenset((s, o))) if v in SYM else (v, s, o)
        if k in seen:
            continue
        seen.add(k)
        out.append(e)
    return out
