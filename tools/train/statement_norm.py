#!/usr/bin/env python3
"""One statement, one encoding (step 2b of docs/9B_STUDENT_ANALYSIS_2026-11-14.md, worktree
9b-model-extraction-analysis-a7e9c9). A deterministic map from a v2 row (event or fact) to a canonical
statement (subject, class, object, actual?) so that two LEGAL encodings of the same statement compare equal:
`learned` / `discovered` / other_verb "realized"; `located_at` / `resides_at`; a typed relation against
other_verb with that relation's own verb; `saved` against `helped`; `escaped` against `departed`.

Built from three sources: the 48 same-statement groups of the blind audit (verdicts.txt), the verb table in
the analysis (realized/discovered/believed/questioned/noticed) and rule A133 of EXTRACTION_PROCEDURE_V2.md.
It is a transform applied at scoring and compose time; no gold file on disk is edited.
"""
import re

IRREG = {"made": "make", "took": "take", "gave": "give", "told": "tell", "saw": "see", "seen": "see",
         "found": "find", "thought": "think", "brought": "bring", "caught": "catch", "left": "leave",
         "sent": "send", "held": "hold", "kept": "keep", "fought": "fight", "met": "meet", "came": "come",
         "went": "go", "gone": "go", "ran": "run", "knew": "know", "known": "know", "became": "become",
         "began": "begin", "begun": "begin", "felt": "feel", "led": "lead", "lost": "lose", "won": "win",
         "stole": "steal", "stolen": "steal", "wore": "wear", "worn": "wear", "struck": "strike", "hid": "hide",
         "hidden": "hide", "chose": "choose", "chosen": "choose", "rose": "rise", "fell": "fall", "said": "say",
         "paid": "pay", "built": "build", "bought": "buy", "taught": "teach", "spoke": "speak", "woke": "wake",
         "woken": "wake", "awoke": "wake", "drove": "drive", "driven": "drive", "threw": "throw", "shot": "shoot",
         "bit": "bite", "flew": "fly", "froze": "freeze", "forgot": "forget", "forgotten": "forget",
         "understood": "understand", "overheard": "overhear", "sought": "seek", "swore": "swear", "tore": "tear",
         "betrayed": "betray", "slew": "slay", "slain": "slay", "died": "die", "dies": "die", "dying": "die",
         "used": "use", "uses": "use", "using": "use", "lied": "lie", "lies": "lie", "lying": "lie", "tied": "tie", "ties": "tie", "tying": "tie"}


def lemma(w):
    w = (w or "").lower().strip().split()[0] if (w or "").strip() else ""
    w = re.sub(r"[^a-z]", "", w)
    if w in IRREG:
        return IRREG[w]
    for suf, rep in (("ies", "y"), ("ied", "y"), ("ying", "y")):
        if w.endswith(suf) and len(w) > 4:
            return w[: -len(suf)] + rep
    for suf in ("ing", "ed", "es", "s"):
        if w.endswith(suf) and len(w) - len(suf) >= 3:
            b = w[: -len(suf)]
            if suf in ("ing", "ed") and len(b) >= 3 and b[-1] == b[-2] and b[-1] not in "ls":
                b = b[:-1]                                  # stopped -> stop, planning -> plan
            elif suf in ("ing", "ed") and b[-1:] in "vcuz" or b.endswith(("at", "iz", "ag", "rg", "rs")):
                b = b + "e"                                 # realized -> realize, used -> use, forced -> force
            elif suf == "es" and not b.endswith(("sh", "ch", "x", "ss", "z")):
                b = w[:-1]                                  # notices -> notice
            return b
    return w


# canonical classes. A relation, an event verb or an other_verb lemma maps to one class.
REL = {
    "learned": "KNOW", "discovered": "KNOW", "revealed": "REVEAL", "suspected": "BELIEVE",
    "located_at": "AT", "resides_at": "AT", "interrogated": "QUESTION", "attacked": "ATTACK",
    "allied_with": "ALLY", "helped": "HELP", "assisted": "HELP", "protected": "PROTECT",
    "member_of": "MEMBER", "joined": "JOIN", "wielded": "USE", "used": "USE", "handed": "GIVE", "gave": "GIVE",
    "stole": "STEAL", "took": "TAKE", "created": "MAKE", "built": "MAKE", "wounded": "WOUND", "dies": "DIE",
    "trained": "TRAIN", "mentored": "TRAIN", "tricked": "TRICK", "ordered": "ORDER", "contacted": "CONTACT",
    "warned": "WARN", "persuaded": "PERSUADE", "kidnapped": "CAPTURE", "transformed_into": "TRANSFORM",
    "gained_power": "GAIN_POWER", "lost_power": "LOSE_POWER", "healed": "HEAL", "remembered": "REMEMBER",
    "forgot": "FORGET", "destroyed": "DESTROY", "recruited": "RECRUIT", "hired": "HIRE", "leader_of": "LEAD",
}
EVENT = {"fought": "FIGHT", "defeated": "DEFEAT", "killed": "KILL", "captured": "CAPTURE", "escaped": "LEAVE",
         "departed": "LEAVE", "saved": "HELP", "betrayed": "BETRAY", "sealed": "SEAL", "met": "MEET",
         "arrived": "ARRIVE", "awakened": "WAKE"}
OV = {  # other_verb lemma -> class (only where the lemma IS the typed relation/event, rule A133 and the audit)
    "realize": "KNOW", "learn": "KNOW", "discover": "KNOW", "notice": "KNOW", "find": "KNOW", "figure": "KNOW",
    "recognize": "KNOW", "deduce": "KNOW", "sense": "KNOW", "know": "KNOW", "uncover": "KNOW",
    "believe": "BELIEVE", "suspect": "BELIEVE", "think": "BELIEVE", "assume": "BELIEVE", "see": "BELIEVE",
    "question": "QUESTION", "interrogate": "QUESTION", "attack": "ATTACK", "assault": "ATTACK",
    "affiliate": "ALLY", "ally": "ALLY", "team": "ALLY", "help": "HELP", "assist": "HELP", "aid": "HELP",
    "rescue": "HELP", "save": "HELP", "protect": "PROTECT", "defend": "PROTECT", "guard": "PROTECT",
    "join": "JOIN", "use": "USE", "wield": "USE", "steal": "STEAL", "take": "TAKE", "make": "MAKE",
    "create": "MAKE", "build": "MAKE", "wound": "WOUND", "injure": "WOUND", "stab": "WOUND", "die": "DIE",
    "train": "TRAIN", "trick": "TRICK", "deceive": "TRICK", "order": "ORDER", "command": "ORDER",
    "warn": "WARN", "persuade": "PERSUADE", "convince": "PERSUADE", "kidnap": "CAPTURE", "capture": "CAPTURE",
    "abduct": "CAPTURE", "transform": "TRANSFORM", "heal": "HEAL", "remember": "REMEMBER", "recall": "REMEMBER",
    "forget": "FORGET", "destroy": "DESTROY", "recruit": "RECRUIT", "hire": "HIRE", "lead": "LEAD",
    "fight": "FIGHT", "battle": "FIGHT", "clash": "FIGHT", "defeat": "DEFEAT", "beat": "DEFEAT",
    "kill": "KILL", "murder": "KILL", "slay": "KILL", "escape": "LEAVE", "flee": "LEAVE", "leave": "LEAVE",
    "depart": "LEAVE", "betray": "BETRAY", "seal": "SEAL", "meet": "MEET", "encounter": "MEET",
    "arrive": "ARRIVE", "visit": "ARRIVE", "reach": "ARRIVE", "come": "ARRIVE", "wake": "WAKE", "awaken": "WAKE",
    "reveal": "REVEAL", "tell": "SAY", "say": "SAY", "state": "SAY", "explain": "SAY", "inform": "SAY",
    "ask": "ASK", "inquire": "ASK", "demand": "ASK",
}
# the analysis' X rows: a class pair that is NOT the same statement stays apart (fought vs defeated, etc.)


def statement(row, layer):
    """-> (subject, class, object_or_None, actual: bool) for an event or fact row; None for a tag."""
    if layer == "events":
        v = row.get("verb")
        return (row.get("subject"), EVENT.get(v, "EV:" + str(v)), row.get("object"), True)
    rel = row.get("relation")
    actual = (row.get("modality") or "actual") == "actual"
    if rel == "other_verb":
        lm = lemma(row.get("object"))
        return (row.get("subject"), OV.get(lm, "OV:" + lm.rstrip("e")), None, actual)
    return (row.get("subject"), REL.get(rel, "R:" + str(rel)), row.get("object"), actual)
