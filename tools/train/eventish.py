#!/usr/bin/env python3
"""Event-likelihood proxy (zero-LLM) for the universal dataset (U-WP3,
plan/UNIVERSAL_DATASET_PLAN.md, 2026-10-04).

Six wikis (bleach, hxh, opm, db, onepiece, berserk) carry no teacher
event rows, so the C6 evidence stratification the 3x500 JJK pools use
is impossible there. U-WP4 pools them at an eventish/non-eventish 50/50
split instead, and this tool IS that flag: a gen-2 window is
`eventish` when its text carries a verb-lexicon hit at a word boundary
(case-folded). The proxy only sets sampling weights for the pool split
-- it never labels -- so the acceptance bar is RECALL on the JJK gen-2
gold (>= 0.95 of the gold's non-empty windows flagged), measured
against the three re-keyed golds (gold600.gen2 kept/reexpressed +
pilot gen2 kept/reexpressed + the covering windows of gold_test_v4.gen2's
non-empty passage units (U-WP5 shape)) and
reported alongside the proxy-positive share of the gold's earned
empties (test-gold genuine empties + the golden probes' empty probes)
and of every wiki's universe (emit_windows.universe + build_windows
gen=CURRENT_GEN, seeded sample of at most --cap windows).

The lexicon is one constant (LEXICON below) and nothing else: the
twelve-verb inventory in every inflection (the verbs the brain's
match-up goal answers with, so their tenses must all flag), plus the
event stems the U-WP3 brief names (battle/fight/clash/.../ambush) in
their inflections, plus the generic combat/encounter/movement wording
the missed-JJK-gold audit surfaced (punch/slash/trap/unconscious/
reunite/...): every one of those later words occurs in a missed gold
window's passage and is JJK-agnostic. JJK-specific wording (cursed,
domain, shikigami, character names) is deliberately ABSENT -- the
lexicon must serve all ten wikis, and a JJK name would flag nothing
on Berserk while flagging a JJK page type on no other wiki.

    python tools/train/eventish.py                          # JJK gold validation + JJK universe share
    python tools/train/eventish.py --universes all          # + every other wiki's universe share
    python tools/train/eventish.py --universes berserk,bleach,marvel --no-validate
    python tools/train/eventish.py --seed 20261004 --cap 30000 --missed-out FILE.jsonl

Exit 0 while recall >= --recall-min (0.95); 1 otherwise (the brief's
rule: on a miss, extend the lexicon ONLY from the missed windows'
wording -- the receipt's `missed` list is the input to that round --
and re-report before/after).
"""
import argparse
import json
import random
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scriptengine.ingest.windows import CURRENT_GEN, build_windows  # noqa: E402

# WHY this exact set (U-WP3, 2026-10-04): the proxy must flag a gold
# window when it STATES an event, and the gold's 12 verbs are the whole
# event space the student answers in -- so every inflection of the 12
# verbs is in the lexicon (a window that says "Gojo kills him" must
# flag even though the gold verb is `killed`). The stems the brief
# names (battle/.../ambush) are the synonyms JJK prose uses for those
# verbs ("a battle", "the clash", "he beat him", "overpower", "an
# ambush"); their inflections join the base forms. The final block is
# the audit round: the missed JJK-gold windows' wording, JJK-agnostic
# words only (punch/slash/stab/trap/knock/unconscious/... for
# fought/killed/sealed, reunite/greet/approach/visit for met, wake/
# revive for awakened, ran/fled-adjacent for escaped) -- each word
# occurs in at least one missed gold passage (the receipt's `missed`
# list is the standing input: extend ONLY from there, re-measure, and
# keep recall >= 0.95 without inflating the earned-empties share).
LEXICON = frozenset({
    # the 12-verb inventory (events.EVENTIVE_VERBS + extra_verbs), every inflection:
    "arrive", "arrives", "arriving", "arrived",
    "awaken", "awakens", "awakening", "awakened",
    "betray", "betrays", "betraying", "betrayed",
    "capture", "captures", "capturing", "captured",
    "defeat", "defeats", "defeating", "defeated",
    "depart", "departs", "departing", "departed",
    "escape", "escapes", "escaping", "escaped",
    "fight", "fights", "fighting", "fought",
    "kill", "kills", "killing", "killed",
    "meet", "meets", "meeting", "met",
    "save", "saves", "saving", "saved",
    "seal", "seals", "sealing", "sealed",
    # the U-WP3 brief's extra stems (the event synonyms), with inflections:
    "battle", "battles", "battling",
    "clash", "clashes", "clashing", "clashed",
    "duel", "duels", "dueling", "duelling", "duelled", "dueled",
    "slay", "slays", "slaying", "slain", "slayed",
    "murder", "murders", "murdering", "murdered", "murderer", "murderers",
    "die", "dies", "dying", "died",
    "death", "deaths",
    "beat", "beats", "beating",
    "overpower", "overpowers", "overpowering", "overpowered",
    "encounter", "encounters", "encountering", "encountered",
    "reach", "reaches", "reaching", "reached",
    "enter", "enters", "entering", "entered",
    "return", "returns", "returning", "returned",
    "leave", "leaves", "leaving", "left",
    "flee", "flees", "fleeing", "fled",
    "abduct", "abducts", "abducting", "abducted",
    "kidnap", "kidnaps", "kidnapping", "kidnapped",
    "imprison", "imprisons", "imprisoning", "imprisoned",
    "rescue", "rescues", "rescuing", "rescued",
    "protect", "protects", "protecting", "protected",
    "attack", "attacks", "attacking", "attacked",
    "ambush", "ambushes", "ambushing", "ambushed",
    # audit round 1 -- the generic combat wording of the missed gold
    # windows (fought/killed/sealed expressed without a lexicon verb):
    "strike", "strikes", "striking", "struck",
    "hit", "hits", "hitting",
    "punch", "punches", "punching", "punched",
    "slash", "slashes", "slashing", "slashed",
    "stab", "stabs", "stabbing", "stabbed",
    "crush", "crushes", "crushing", "crushed",
    "throw", "throws", "throwing", "threw",
    "trap", "traps", "trapping", "trapped",
    "lock", "locks", "locking", "locked",
    "knock", "knocks", "knocking", "knocked",
    "parry", "parries", "parrying", "parried",
    "block", "blocks", "blocking", "blocked",
    "guard", "guards", "guarding", "guarded",
    "swing", "swings", "swinging", "swung",
    "confront", "confronts", "confronting", "confronted",
    "engage", "engages", "engaging", "engaged",
    "subdue", "subdues", "subduing", "subdued",
    "overwhelm", "overwhelms", "overwhelming", "overwhelmed",
    "damage", "damages", "damaging", "damaged",
    "victory", "victorious",
    "sever", "severs", "severing", "severed",
    "slice", "slices", "slicing", "sliced",
    "unconscious",
    "blast", "blasts", "blasting", "blasted",
    "blow", "blows", "blowing", "blown",
    "appear", "appears", "appearing", "appeared",
    "wake", "wakes", "waking", "woke", "woken",
    "incapacitate", "incapacitates", "incapacitating", "incapacitated",
    "immobilize", "immobilizes", "immobilizing", "immobilized",
    "ensnare", "ensnares", "ensnaring", "ensnared",
    # audit round 1 -- the generic encounter wording (met/movement
    # events the gold states without "meet"):
    "visit", "visits", "visiting", "visited",
    "approach", "approaches", "approaching", "approached",
    "greet", "greets", "greeting", "greeted",
    "reunite", "reunites", "reuniting", "reunited",
    "introduce", "introduces", "introducing", "introduced",
    "converse", "converses", "conversing", "conversed",
    "conversation", "conversations",
    "interrupt", "interrupts", "interrupting", "interrupted",
    "escort", "escorts", "escorting", "escorted",
    "discuss", "discusses", "discussing", "discussed",
    "talk", "talks", "talking", "talked",
    "contact", "contacts", "contacting", "contacted",
    # audit round 2 -- the remaining missed windows' wording, the
    # JJK-agnostic half of it (zero earned-empties cost each on JJK):
    "hold", "holds", "holding", "held",
    "show", "shows", "showed", "showing", "shown",
    "search", "searches", "searching", "searched",
    "inform", "informs", "informing", "informed",
    "ran", "runs", "running",
    "jump", "jumps", "jumping", "jumped",
    "free", "frees", "freeing", "freed",
    "unseal", "unseals", "unsealed", "unsealing",
    "interview", "interviews", "interviewing", "interviewed",
    "unleash", "unleashes", "unleashing", "unleashed",
    "hunt", "hunts", "hunting", "hunted",
    "teach", "teaches", "teaching", "taught",
    "negotiate", "negotiates", "negotiating", "negotiated",
    "survive", "survives", "surviving", "survived",
    "seize", "seizes", "seizing", "seized",
    "confine", "confines", "confining", "confined",
    "guide", "guides", "guiding", "guided",
    "remind", "reminds", "reminding", "reminded",
    "engulf", "engulfs", "engulfing", "engulfed",
    "revive", "revives", "reviving", "revived",
    "restore", "restores", "restoring", "restored",
    "secure", "secures", "securing", "secured",
    "kick", "kicks", "kicking", "kicked",
    "decapitate", "decapitates", "decapitating", "decapitated",
    "consult", "consults", "consulting", "consulted",
    "injure", "injures", "injury", "injured", "injuring",
    "sacrifice", "sacrifices", "sacrificing", "sacrificed",
    "fighter", "fighters",
    "slaughter", "slaughters", "slaughtering", "slaughtered",
    "defend", "defends", "defending", "defended",
    "separate", "separates", "separating", "separated",
    "apprehend", "apprehends", "apprehending", "apprehended",
    "bite", "bites", "biting", "bitten",
    "prevent", "prevents", "preventing", "prevented",
    "threaten", "threatens", "threatening", "threatened",
    "restrain", "restrains", "restraining", "restrained",
    "combat", "melee", "combatant", "combatants",
    "assault", "assaults", "assaulting", "assaulted",
    "weapon", "weapons",
    "find", "finds", "finding", "found",
    "train", "trains", "training", "trained",
    "blitz", "blitzes", "blitzing", "blitzed",
    "retreat", "retreats", "retreating", "retreated",
    "move", "moves", "moving", "moved",
})

# The match is case-folded + word-boundary: a lexicon word glued to
# other letters (battlefield, unmet, leftover) is NOT a hit, and the
# alternatives run longest-first so "battles" reports as "battles",
# not "battle". The \b does the prefix/suffix work; the casefold is
# the brief's "case-folded".
_HIT = re.compile(
    r"\b(?:"
    + "|".join(sorted((re.escape(w) for w in LEXICON), key=len, reverse=True))
    + r")\b"
)


def hit_words(text):
    """The lexicon words present in `text` at word boundaries, case-
    folded, sorted and de-duplicated (a window that says "battle"
    twice reports one "battle")."""
    return tuple(
        sorted({m.group(0) for m in _HIT.finditer((text or "").casefold())})
    )


def is_eventish(text):
    """The U-WP3 flag: True when the window's text carries any
    lexicon word at a word boundary. This is the pool-split signal,
    never a label."""
    return _HIT.search((text or "").casefold()) is not None


def _assistant_events(record):
    """The record's adjudicated gold rows (the assistant message's
    `events`; [] for an empty adjudication) -- rekey_gold.rows_of's
    rule, inlined so the tool has no cross-tool import surface."""
    try:
        return json.loads(record["messages"][2]["content"]).get("events") or []
    except (json.JSONDecodeError, ValueError, AttributeError, KeyError):
        return None  # unparseable: refuse, never guess


def _user_passage(record):
    """The record's read passage: everything after `Passage:\n` in the
    user message (the campaign's own message shape)."""
    user = record["messages"][1]["content"]
    at = user.find("Passage:\n")
    return user[at + len("Passage:\n"):].strip() if at >= 0 else ""


def gold_positives(series):
    """The JJK gen-2 POSITIVE windows: every window whose gold states
    >= 1 event. Sources (plan U-WP3): gold600.gen2 and the pilot gen2
    with rekey status kept/reexpressed only (the reread records are the
    35B re-read's, not adjudicated gold) and the covering windows of
    gold_test_v4.gen2's non-empty passage units (U-WP5 shape: a unit's
    core or optional events make its covering windows positive). De-duplicated by
    window id -- a window in two sources is one positive; the first
    source's passage/verbs win (the window's text is the window's text).
    Returns (rows, per_source_counts): rows is a list of
    {source, id, page, section, passage, verbs} dicts."""
    root = ROOT / "series" / series / "training"
    rows = {}
    counts = {}

    def add(source, rid, page, section, passage, verbs):
        if rid in rows:
            return
        rows[rid] = {
            "source": source, "id": rid, "page": page,
            "section": section, "passage": passage, "verbs": verbs,
        }

    for source, name in (("gold600", "gold600/gold600.gen2.jsonl"),
                         ("pilot", "gold/gold_pilot_all.gen2.jsonl")):
        path = root / name
        n = 0
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if (record.get("rekey") or {}).get("status") not in ("kept", "reexpressed"):
                continue  # reread/straddle: the 35B re-read owns those windows
            events = _assistant_events(record)
            if not events:
                continue  # an empty adjudication is not a positive
            add(source, record["id"], record.get("page") or "",
                record.get("section") or "", _user_passage(record),
                [str(e.get("verb") or "") for e in events])
            n += 1
        counts[source] = n

    testgold = root / "recall_gold_v3" / "gold_test_v4.gen2.json"
    data = json.loads(testgold.read_text(encoding="utf-8"))
    n = 0
    for key, unit in data.items():
        if not (re.fullmatch(r"W\d+", key) and isinstance(unit, dict)
                and isinstance(unit.get("windows"), list)):
            continue  # the meta keys are not units (U-WP5 passage shape)
        core = unit.get("core") or []
        optional = unit.get("optional") or []
        if not (core or optional):
            continue  # the empty units are the NEGATIVES (see earned_empties)
        # A positive window is a covering window of a non-empty unit:
        # the proxy scans the window's READ text (its read span in the
        # passage), and a window on two sources is one positive (the
        # first source's passage/verbs win, as before).
        passage = unit.get("passage") or ""
        for w in unit["windows"]:
            a, b = w["span"]
            add("testgold", w["id"], unit.get("page") or "",
                unit.get("section") or "", passage[a:b],
                [str(e[1]) for e in core] + [str(e[1]) for e in optional])
            n += 1
    counts["testgold"] = n
    return [rows[k] for k in rows], counts


def earned_empties(series):
    """The JJK gen-2 NEGATIVE windows: the ADJUDICATED empties only.
    (a) the test gold's GENUINE empties -- a covering window of a
    unit with no core or optional event that is NOT `partial` (a
    partial window's unread tail was never read, so its emptiness is
    not earned and it never supplies a negative; the annotator read
    the whole slice and listed every event in it, so a fully-read
    window of that slice with no listed event is a genuine empty);
    (b) the golden probes' empty probes (expected == [] in
    series/<s>/training/opencode/golden_probes.jsonl -- the drift
    probes rebuilt on kept/reexpressed gold). De-duplicated by id (a
    probe that re-states a test-gold window is one negative). Returns
    (passages_by_id, counts)."""
    root = ROOT / "series" / series / "training"
    neg = {}
    data = json.loads(
        (root / "recall_gold_v3" / "gold_test_v4.gen2.json").read_text(encoding="utf-8")
    )
    test_neg = {}
    for key, unit in data.items():
        if not (re.fullmatch(r"W\d+", key) and isinstance(unit, dict)
                and isinstance(unit.get("windows"), list)):
            continue  # the meta keys are not units (U-WP5 passage shape)
        if unit.get("core") or unit.get("optional"):
            continue  # non-empty units are not negatives
        passage = unit.get("passage") or ""
        for w in unit["windows"]:
            if w.get("partial"):
                continue  # an unread tail: not an earned empty
            a, b = w["span"]
            test_neg[w["id"]] = passage[a:b]
    for wid, txt in test_neg.items():
        if wid not in neg:
            neg[wid] = txt
    test_n = len(test_neg)
    probe_n = 0
    probes = root / "opencode" / "golden_probes.jsonl"
    for line in probes.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        probe = json.loads(line)
        if probe.get("expected"):
            continue  # a probe WITH events is not a negative
        if probe["id"] not in neg:
            neg[probe["id"]] = probe.get("passage") or ""
            probe_n += 1
    return neg, {"testgold_genuine_empties": test_n, "probe_empties": probe_n}


def _universe_id_map(series):
    """The series' gen-2 window id -> (page, section-label) map (the
    brief's construction: emit_windows.universe + build_windows
    gen=CURRENT_GEN, first-read copy of a collapsed id). The test gold
    files carry no page/section -- entries are keyed by window id -- so
    the receipt's missed list resolves them here (recomputed, never
    read: the stored ids are only valid until the next store change).
    Empty map while the series has no store."""
    from emit_windows import universe  # lazy: the store is the heavy half

    from scriptengine.stores.facts import FactStore

    db = ROOT / "series" / series / "facts.db"
    if not db.exists():
        return {}
    with FactStore(db) as store:
        uni = universe(store)
    seen = set()
    mapping = {}
    for page, label, text in uni:
        for w in build_windows(page, label, text, gen=CURRENT_GEN):
            if w.id in seen:
                continue  # identical text under one (page, label): one window
            seen.add(w.id)
            # Pool-line shape (emit_windows): section "" means the lead.
            mapping[w.id] = (w.page, "" if w.section == "lead" else w.section)
    return mapping


def validate(series, recall_min=0.95):
    """The U-WP3 acceptance: the proxy's RECALL on the JJK gen-2 gold
    (>= recall_min of the positive windows flagged) and the proxy-
    positive share of the earned empties (reported, not gated -- the
    share is the proxy's false-positive signal on windows a teacher
    read and found empty). Also lists every MISSED positive window
    (page, section, first 150 chars, its gold verbs) -- the standing
    input to a lexicon-extension round."""
    pos_rows, pos_counts = gold_positives(series)
    neg, neg_counts = earned_empties(series)
    hit_ids = {r["id"] for r in pos_rows if is_eventish(r["passage"])}
    hit_neg = sum(1 for t in neg.values() if is_eventish(t))
    # The U-WP5 test gold's rows carry page/section (the unit's); the
    # id map is a leftover safety net for a row that lacks them.
    id_map = _universe_id_map(series)
    missed = [
        {
            "source": r["source"], "id": r["id"],
            "page": r["page"] or id_map.get(r["id"], ("", ""))[0],
            "section": r["section"] or id_map.get(r["id"], ("", ""))[1],
            "first150": r["passage"][:150],
            "verbs": r["verbs"],
        }
        for r in pos_rows if r["id"] not in hit_ids
    ]
    recall = len(hit_ids) / len(pos_rows) if pos_rows else 0.0
    return {
        "positives": {**pos_counts, "unique_windows": len(pos_rows)},
        "recall": {
            "hit": len(hit_ids), "total": len(pos_rows),
            "recall": round(recall, 4), "threshold": recall_min,
            "pass": recall >= recall_min,
        },
        # the same ratio, named as the brief asks for it:
        "proxy_positive_share": {
            "among_positives": round(recall, 4),
            "among_earned_empties": (round(hit_neg / len(neg), 4) if neg else None),
        },
        "earned_empties": {**neg_counts, "unique_windows": len(neg)},
        "missed": missed,
    }


def universe_share(series, seed=20261004, cap=30000):
    """The proxy-positive share of one wiki's WHOLE gen-2 universe
    (emit_windows.universe + build_windows gen=CURRENT_GEN, the brief's
    construction). Universes over `cap` are seeded-reservoir-sampled
    to exactly `cap` windows (Algorithm R, one pass, deterministic for
    a seed) -- a sample of the universe, never a sample of pages, so
    the share is an unbiased read of the flag on that wiki."""
    from emit_windows import universe  # lazy: the store is the heavy half

    from scriptengine.stores.facts import FactStore

    db = ROOT / "series" / series / "facts.db"
    if not db.exists():
        raise SystemExit(f"{series} is not indexed (no {db}); run `index` first")
    t0 = time.time()
    with FactStore(db) as store:
        uni = universe(store)
    rng = random.Random(f"{seed}-eventish-{series}")
    seen = set()
    total = 0
    reservoir = []  # window texts of the (reservoir-)sample
    for page, label, text in uni:
        for w in build_windows(page, label, text, gen=CURRENT_GEN):
            if w.id in seen:
                continue  # identical text under one (page, label): one window
            seen.add(w.id)
            total += 1
            if total <= cap:
                reservoir.append(w.text)
            else:
                j = rng.randrange(total)
                if j < cap:
                    reservoir[j] = w.text
    hits = sum(1 for t in reservoir if is_eventish(t))
    return {
        "series": series,
        "gen": CURRENT_GEN,
        "universe_windows": total,
        "sampled_windows": len(reservoir),
        "sampled": total > cap,
        "eventish_windows": hits,
        "eventish_share": round(hits / len(reservoir), 4) if reservoir else None,
        "seed": seed,
        "cap": cap,
        "seconds": round(time.time() - t0, 1),
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk",
                    help="the series whose gen-2 gold validates the "
                         "proxy (default jjk: the only wiki with three "
                         "re-keyed golds)")
    ap.add_argument("--universes", default=None,
                    help="comma list of wikis to measure the universe "
                         "share on (default: --series only; 'all' = the "
                         "ten wiki stores)")
    ap.add_argument("--no-validate", action="store_true",
                    help="skip the gold validation (universe shares only)")
    ap.add_argument("--no-universe", action="store_true",
                    help="skip the universe share (gold validation only)")
    ap.add_argument("--seed", type=int, default=20261004,
                    help="the seeded sampler for universes over the cap")
    ap.add_argument("--cap", type=int, default=30000,
                    help="sample at most this many windows per wiki "
                         "(the brief's 30k)")
    ap.add_argument("--recall-min", type=float, default=0.95,
                    help="the brief's acceptance (exit 1 below it)")
    ap.add_argument("--missed-out", default=None,
                    help="also write the missed-positives list here (JSONL)")
    a = ap.parse_args()

    ALL_WIKIS = ["jjk", "berserk", "bleach", "csm", "db", "hxh",
                 "onepiece", "opm", "marvel", "mcu"]
    universes = (ALL_WIKIS if a.universes == "all"
                 else (a.universes.split(",") if a.universes else [a.series]))

    receipt = {
        "series": a.series,
        "lexicon_words": len(LEXICON),
        "gen": CURRENT_GEN,
        "validation": None,
        "universes": {},
    }
    if not a.no_validate:
        v = validate(a.series, a.recall_min)
        receipt["validation"] = v
        if a.missed_out:
            out = Path(a.missed_out)
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(
                "".join(json.dumps(m, ensure_ascii=False) + "\n"
                        for m in v["missed"]),
                encoding="utf-8")
    for series in universes:
        receipt["universes"][series] = universe_share(series, a.seed, a.cap)

    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    if a.no_validate:
        return 0
    return 0 if receipt["validation"]["recall"]["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())