#!/usr/bin/env python3
"""Drafter v2 — the guideline APPLIED, not piled into one prompt
(plan/FLAWLESS_LABELING_PLAN.md section 6b, owner-approved 2026-10-05):

1. show, don't tell: the k worked examples closest to THIS window's wording
   are retrieved from the example bank (leave-page-out: a window never sees
   an example from its own page);
2. decompose: the model reads the window sentence by sentence — done or only
   attempted/planned? who? to whom? which verb? — under guideline A-G;
3. a separate missed-event pass (recall): the listed rows are shown back and
   only events NOT yet listed are asked for;
4. mechanical row checks, no model: verbatim quote, verb in the inventory,
   shape (objects), unnamed-class ends, group ends split, ends that resolve
   to a technique/item/chapter page dropped, per-window dedup.

Any OpenAI-compatible server (ninfer :18081 by default).

    python tools/train/draft_v2.py --data IN.jsonl --out PRED.jsonl
        [--url ...] [--model ...] [--k 6] [--workers 4] [--no-missed-pass]
        [--no-template-kwargs] [--series jjk]
"""
import argparse
import json
import math
import re
import sys
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
GUIDE = (ROOT / "plan" / "EVENT_ANNOTATION_GUIDELINE.md").read_text(encoding="utf-8")
GUIDE = GUIDE[GUIDE.index("## A."):]
VERBS = ["fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "awakened", "met", "arrived", "departed"]
NEEDS_OBJECT = set(VERBS) - {"awakened"}
# Never an end (guideline B6, G.2): unnamed people, crowds, pronouns.
CLASS_WORDS = re.compile(
    r"^(the |a |an |some |several |many |all |two |three |four |numerous )?"
    r"(civilians?|people|humans?|transfigured humans?|higher-?ups|curses?|cursed spirits?|"
    r"sorcerers?|soldiers?|members?|opponents?|enemies|guards?|lookouts?|players?|"
    r"students?|others?|everyone|them|they|he|she|him|her|it|both sides|the two|the three|"
    r"national governments?|allies)$", re.I)

SYSTEM = """You are a meticulous event annotator for fiction-wiki passages. You label ONE window. Precision and completeness matter equally: every event the window states, and nothing it does not state.

Follow the annotation guideline below exactly, especially section G (v2), which lists the phrasings that ARE and are NOT each verb, the end rules and the shape rules.

METHOD — do this in your reasoning before answering:
1. Split the window into sentences. For EVERY sentence, ask:
   a. Is an action stated as DONE? (Not planned, intended, attempted-and-not-made, hypothetical, negated, threatened, or only asked about.) An attack that was MADE counts even if it was blocked, dodged or failed.
   b. Who does it, and to whom? Resolve pronouns only inside this window; use the name the window gives; split groups into one row per named member.
   c. Which verb? Use the G.1 table and the decision order (killed > defeated > fought; write fought too when the fight is stated separately).
2. Check each candidate row against G.2 (ends), G.3 (window) and G.4 (shape). Drop any row that fails.
3. Re-read the whole window once more looking ONLY for events you have not listed (arrivals to people = met, takes X away = saved, freezing/trapping = sealed, blocked or failed attacks = fought, pronoun defeats, named creatures acting).

Allowed verbs (exactly these words): """ + ", ".join(VERBS) + """

Answer with JSON only:
{"events": [{"quote": "<verbatim from the window, at least 12 characters>", "subject": "...", "verb": "...", "object": "..." or null}]}
If the window states no event, answer {"events": []}.

GUIDELINE
""" + GUIDE

MISSED = """Below is a window you already labeled, followed by the rows you wrote. Re-read the window sentence by sentence and list ONLY events the window states that are NOT already in the rows — check especially: arrivals/appearances to people (met), "takes X away"/"intercepts"/"takes the hit" (saved), freezing or trapping (sealed), attacks that were blocked, dodged or failed (fought), pronoun defeats ("she beat him"), named creatures acting, group sentences that need one row per named member. Apply the same guideline. If nothing is missing, answer {"events": []}.

ROWS ALREADY WRITTEN:
%s

THE WINDOW:
%s"""


# Round 2 (2026-10-05): the round-1 error review (gold_v5/errors_r1.jsonl)
# found the misses concentrated in trigger families the model under-reads;
# the missed pass now walks each family explicitly.
MISSED_V2 = """Below is a window you already labeled and the rows you wrote. Do a TRIGGER CHECK: go through the window once for EACH family below, quote every phrase in the window that matches it, and write a row for every match that is NOT already in the rows. Apply guideline section G for ends, names and shape (one row per named person; name the person when the window names them).

1. MEET (verb met): arrives / suddenly arrives / appears / approaches / emerges / shows up / enters the fray / makes an entry / joins up with / comes across / encounters / finds X (and they interact) / meets / visits / greets / comes to face / comes face to face / stops them / confronts — a row with EVERY named person they come to who was not already with them (e.g. "The second-year students arrive to find them" -> each named second-year met each named person in "them"; "approaches the group" -> met each named member).
2. STATED FIGHT (verb fought): "X's battle / fight / clash / duel with Y", "the fight between X and Y", "X vs. Y" (also a bare title or list item), "in her battle with Y", "surviving his attack", "almost killed him", "a kick/punch/strike towards Y", "uses <technique> on Y", "rejoins the fight", "tries to ambush Y" (an attack made, even if it fails), "Y's attack is blocked/stopped". Never pair two ALLIES fighting on the same side.
3. OUTCOMES: wakes up / evolves / receives a new body or full power -> awakened (no object); exorcise(s) / execute(s) / murdering / assassinated / "falls to the ground dead" -> killed; beat / bested / incapacitated / eliminate(s) / takes X out -> defeated; rescues / frees / takes X away / intercepts the blow / takes the hit for -> saved; traps in a domain or barrier / freezes -> sealed; takes hostage / drags to a cell or chamber -> captured; breaks out of a trap / escapes while X tries to stop him -> escaped (object = the trapper or pursuer).

Answer with JSON only: {"events": [...]} holding ONLY the new rows (quote verbatim from the window), or {"events": []}.

ROWS ALREADY WRITTEN:
%s

THE WINDOW:
%s"""

VERIFY_V2 = """You are the VERIFIER for one labeled window. Be as thorough as the annotator: re-read the whole window sentence by sentence, then judge EVERY row.

A row is KEPT only if the window itself states it under the guideline (sections A-G). DROP a row when, for example:
- the act is a capability or habit ("can strike", "could exorcise"), a plan, an intent ("to protect", "plans on"), an attempt that was never made, a threat, a hypothetical, a teaser ("Hunted down by ...", "must overcome") or a future event ("has an interview with");
- the verb is wrong: "overpowers / overwhelms" while the fight continues is fought, not defeated; being released is not escaped; "fled with X in pursuit" then a clash is not escaped; helping is not saved;
- the ends are wrong: two allies paired as fighting; a pronoun or description resolved to the wrong person ("his student" is the person the window means); an unnamed class; a place for arrived/departed that the clause does not name;
- the quote does not state the event.
Then list any event the window states that NO row covers (same trigger families as the annotator: arrivals/appearances to named people = met, stated battles = fought, outcomes).

Answer with JSON only:
{"verdicts": [{"i": <row index>, "keep": true|false, "rule": "<one short sentence>"}], "add": [{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}]}

ROWS (index: row):
%s

THE WINDOW:
%s"""


VERIFY_V3 = """You are the VERIFIER for one labeled window. Re-read the whole window sentence by sentence, then judge EVERY row. The worked examples above show correct answers under the guideline.

KEEP a row by default. DROP a row ONLY when you can name the exact guideline rule it breaks, from this list (cite the code):
- NOT-DONE: the window states a capability/habit ("can strike"), a plan or intent ("to protect", "plans on"), a threat, a hypothetical, a teaser ("Hunted down by...", "must overcome"), or a future event — NOT an act that happened. (An attack that was MADE but blocked, dodged, missed or failed IS done: keep it as fought.)
- WRONG-VERB: e.g. "overpowers/overwhelms" while the fight continues is fought not defeated; being released is not escaped; "fled with X in pursuit" then a clash is not escaped; helping is not saved; a fatal blow with no stated death is not killed.
- WRONG-END: two allies on the same side paired as fighting; a pronoun or description resolved to the wrong person; an unnamed class or crowd; arrived/departed with a place the clause does not name.
- NOT-STATED: no sentence of the window states this event at all.
Stated fights you must KEEP: "X vs. Y", "the battle/fight/clash/duel between X and Y", "the two of them clash", "X's battle with Y", "engaged in a beam struggle", any hit/strike/blast/punch/kick/stab aimed at someone (landed or not), a technique used on someone.
Then list any event the window states that NO row covers.

Answer with JSON only:
{"verdicts": [{"i": <row index>, "keep": true|false, "code": "NOT-DONE|WRONG-VERB|WRONG-END|NOT-STATED|", "rule": "<one short sentence>"}], "add": [{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}]}

%s

ROWS (index: row):
%s

THE WINDOW:
%s"""


FAMILY = {
    "meet": ({"met"}, """FOCUSED PASS — MEET ONLY. Read the window and find EVERY time someone comes together with a named person they were not already with: arrives / suddenly arrives / appears / approaches / emerges / shows up / enters the fray / makes an entry / joins up with / comes across / encounters / finds X and they interact / meets / visits / greets / comes to face / comes face to face / stops them / confronts / is harassed by. Write one `met` row per (newcomer, named person) pair — expand every group: "Yuji Itadori and Aoi Todo show up and rescue the two" = Yuji met Maki, Yuji met Megumi, Aoi met Maki, Aoi met Megumi when "the two" are Maki and Megumi; "until they come across A and B" = each of "they" met A and B; "she's harassed by Naoya and her mother" = Naoya met her, her mother met her. NOT met: talk inside a meeting already in progress, a phone call, noticing/watching, a future interview, joining a group. Name people as the window names them ("The newcomer is Fumihiko Takaba" -> Fumihiko Takaba)."""),
    "fight": ({"fought"}, """FOCUSED PASS — STATED FIGHTS ONLY. Find EVERY fight the window states, including inside descriptive text: "X vs. Y" (also a bare title or list item), "the fight/battle/clash/duel between X and Y", "watched the fight between X and Y", "his fight with Y", "X's battle with Y", "the two of them clash", "engaged in a beam struggle", "surviving his attack", "almost killed him", any hit/strike/blast/punch/kick/stab aimed at someone (landed, blocked, dodged, missed or failed — "the Infinity stops Jogo's punch" is still fought), "redirect X's kick towards Y" (X fought Y), "uses <technique> on Y", "uses Z's cursed speech on Y" (the user fought Y), a named creature acting ("a barrage from Yuta and Rika" = Rika fought Uro too), "rejoins the fight", "tries to ambush Y", "early onslaught". Write `fought` rows (one per opposing pair; never pair two allies). NOT fought: a threat, "prepares to", "tries to use" with nothing made, a face-off with no attack."""),
    "outcome": ({"killed", "defeated", "saved", "sealed", "captured", "escaped", "awakened", "betrayed", "arrived", "departed"}, """FOCUSED PASS — OUTCOMES ONLY. Find EVERY outcome the window states: killed (exorcise(s) / exorcised it / executes / murdering / assassinated / "falls to the ground dead"); defeated (beat — "she beat him" resolves inside the window — bested, incapacitated, eliminate(s), takes X out, finishes the fight); saved (rescues, frees, takes X away from danger, intercepts the finishing blow aimed at X, takes the hit for X, heals someone who would otherwise die); sealed (traps in a domain/barrier/ice, freezes someone in place); captured (hostage, drags to a cell/chamber); escaped (breaks out of a trap, escapes while X tries to stop him -> object = the trapper/pursuer); awakened (wakes up, evolves, receives a new body/power; no object); arrived/departed (a NAMED place only). One row per named person."""),
}

FAMILY_PROMPT = """%s

Rows already written for this window (do not repeat them):
%s

Answer with JSON only: {"events": [...]} holding ONLY new rows for this family (quote verbatim from the window), or {"events": []}.

%s

THE WINDOW:
%s"""


def ask_json(url, model, system, user, template_kwargs, max_tokens=20480):
    """Like ask(), for a free-form JSON object answer (the verifier)."""
    body = {"model": model, "temperature": 0.6, "top_p": 0.95, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if template_kwargs:
        body["chat_template_kwargs"] = {"enable_thinking": True}
    for _ in range(3):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=3600).read())["choices"][0]["message"]
            t = re.sub(r"^```[a-z]*\n?|\n?```$", "", (m.get("content") or "").strip()).strip()
            d = json.loads(t[t.find("{"):t.rfind("}") + 1])
            if isinstance(d, dict):
                return d
        except Exception:  # noqa: BLE001
            pass
    return None


def tokens(s):
    return set(re.findall(r"[a-z]{3,}", s.lower()))


class Bank:
    def __init__(self, path):
        self.items = [json.loads(l) for l in open(path)]
        df = Counter(t for b in self.items for t in set(b["tokens"]))
        n = len(self.items)
        self.idf = {t: math.log((n + 1) / (c + 0.5)) for t, c in df.items()}

    def nearest(self, window, page, k, verbs=None):
        q = tokens(window)
        scored = []
        for b in self.items:
            if b["page"] == page:
                continue  # leave-page-out: never the window's own page
            if verbs is not None and not any(r["verb"] in verbs for r in b["rows"]):
                continue  # a family pass shows only that family's examples
            common = q & set(b["tokens"])
            score = sum(self.idf.get(t, 0) for t in common) / (1 + math.sqrt(len(b["tokens"])))
            scored.append((score, b))
        scored.sort(key=lambda x: -x[0])
        picked = [b for _, b in scored[:k]]
        if verbs is None and picked and not any(not b["rows"] for b in picked):  # always show one earned empty
            empties = [b for s, b in scored if not b["rows"]]
            if empties:
                picked[-1] = empties[0]
        return picked


def render_examples(examples):
    out = []
    for i, b in enumerate(examples, 1):
        rows = json.dumps({"events": b["rows"]}, ensure_ascii=False)
        out.append(f"EXAMPLE {i} — Page: {b['page']} / Section: {b['section'] or '(lead)'}\n"
                   f"Window:\n{b['window']}\nCorrect answer: {rows}\nWhy: {b['why']}")
    return "\n\n".join(out)


def parse(text):
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", (text or "").strip()).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return None
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return None
    ev = d.get("events") if isinstance(d, dict) else None
    return [x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else None


def ask(url, model, system, user, template_kwargs, max_tokens=20480):
    body = {"model": model, "temperature": 0.6, "top_p": 0.95, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}]}
    if template_kwargs:
        body["chat_template_kwargs"] = {"enable_thinking": True}
    for _ in range(3):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=3600).read())["choices"][0]["message"]
            ev = parse(m.get("content"))
            if ev is not None:
                return ev, m.get("content") or ""
        except Exception:  # noqa: BLE001
            pass
    return None, ""


def check_rows(rows, window, wiki, bad_end):
    """Mechanical checks (no model). Returns (kept, dropped-with-reason)."""
    kept, dropped, seen = [], [], set()
    for r in rows:
        s = str(r.get("subject") or "").strip()
        v = str(r.get("verb") or "").strip().lower()
        o = r.get("object")
        o = None if o in (None, "", "null", "None") else str(o).strip()
        q = str(r.get("quote") or "").strip()
        why = None
        if v not in VERBS:
            why = "verb not in the inventory"
        elif not q or q not in window:
            why = "quote not verbatim in the window"
        elif v in NEEDS_OBJECT and not o:
            why = f"{v} needs an object"
        elif v == "awakened" and o:
            o = None
        if why is None:
            for end in ([s] + ([o] if o else [])):
                if CLASS_WORDS.match(end) or not end:
                    why = f"unnamed/class end: {end!r}"
                    break
                if wiki is not None:
                    # Exact-name page only, and never `technique`: this wiki
                    # files NAMED shikigami (Divine Dog: Totality, Great
                    # Serpent) as technique pages, and those are allowed ends
                    # (B5/G.2) -- techniques are left to the model.
                    exact = [p for p in wiki.resolve(end) if p.lower() == end.lower()]
                    label = wiki.label.get(exact[0]) if exact else None
                    if label in (bad_end - {"technique"}):
                        why = f"end is a {label} page"
                        break
        if why is None and v in ("arrived", "departed") and o and re.match(r"^the [a-z]", o):
            why = "arrived/departed object is a description, not a named place"
        if why:
            dropped.append({**r, "why": why})
            continue
        # group ends: one row per named member (G.2)
        subs = [x.strip() for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", s) if x.strip()]
        objs = [x.strip() for x in re.split(r",\s*(?:and\s+)?|\s+and\s+", o)] if o else [None]
        for ss in subs:
            for oo in objs:
                key = (ss.lower(), v, (oo or "").lower())
                sym = (( oo or "").lower(), v, ss.lower())
                if key in seen or (v in ("fought", "met") and sym in seen):
                    continue
                seen.add(key)
                kept.append({"quote": q, "subject": ss, "verb": v, "object": oo})
    return kept, dropped


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--bank", default=str(ROOT / "series/jjk/training/gold_v5/example_bank.jsonl"))
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    ap.add_argument("--k", type=int, default=6)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--no-missed-pass", action="store_true")
    ap.add_argument("--missed-prompt", choices=("v1", "v2"), default="v1",
                    help="v1 = round 1 (generic); v2 = round 2 trigger checklist")
    ap.add_argument("--family-passes", action="store_true",
                    help="round 4: separate MEET / FIGHT / OUTCOME passes, each with that family's examples")
    ap.add_argument("--verify-votes", type=int, default=1,
                    help="verifier samples; a row is dropped only when ALL samples drop it with a code")
    ap.add_argument("--samples", type=int, default=1,
                    help="independent draft samples, unioned (stability)")
    ap.add_argument("--verify-prompt", choices=("v2", "v3"), default="v2",
                    help="v3 = conservative verifier: drop only with a cited NO-rule, sees the examples")
    ap.add_argument("--verify-pass", action="store_true",
                    help="round 2: the thorough verifier pass (keep/drop every row + add)")
    ap.add_argument("--no-template-kwargs", action="store_true")
    ap.add_argument("--series", default="jjk")
    a = ap.parse_args()

    bank = Bank(a.bank)
    try:
        import verify_row_wiki as vrw  # the wiki resolver + BAD_END page types
        wiki, bad_end = vrw.Wiki(str(ROOT / "series" / a.series / "facts.db")), vrw.BAD_END
    except Exception as err:  # noqa: BLE001
        print(f"wiki resolver unavailable ({err}); end page-type check off", file=sys.stderr)
        wiki, bad_end = None, set()
    rows = [json.loads(l) for l in open(a.data)]
    done = set()
    if Path(a.out).exists():
        done = {json.loads(l)["id"] for l in open(a.out)}
    rows = [r for r in rows if r["id"] not in done]
    tk = not a.no_template_kwargs

    def job(r):
        user = r["messages"][1]["content"]
        window = user.split("Passage:\n", 1)[1]
        ex = bank.nearest(window, r.get("page", ""), a.k)
        prompt = ("Worked examples (correct answers under the guideline):\n\n" + render_examples(ex)
                  + "\n\nNOW LABEL THIS WINDOW:\n" + user)
        samples, raw = [], ""
        for _s in range(max(1, a.samples)):
            evs, raw_s = ask(a.url, a.model, SYSTEM, prompt, tk)
            if evs is not None:
                samples.append(evs); raw = raw or raw_s
        ok = bool(samples)
        ev, seen_keys = [], set()
        for evs in samples:  # union of the samples, first occurrence wins
            for e in evs:
                k = (str(e.get("subject", "")).lower(), str(e.get("verb", "")).lower(),
                     str(e.get("object", "")).lower())
                if k not in seen_keys:
                    seen_keys.add(k); ev.append(e)
        added = []
        if ok and not a.no_missed_pass:
            listed = json.dumps({"events": ev}, ensure_ascii=False)
            tmpl = MISSED_V2 if a.missed_prompt == "v2" else MISSED
            more, _ = ask(a.url, a.model, SYSTEM, tmpl % (listed, user), tk)
            added = more or []
        fam_added = {}
        if ok and a.family_passes:
            for fam, (fverbs, finstr) in FAMILY.items():
                listed = json.dumps({"events": ev + added + [r for v in fam_added.values() for r in v]}, ensure_ascii=False)
                fex = bank.nearest(window, r.get("page", ""), 4, verbs=fverbs)
                fexs = ("Worked examples for this family:\n\n" + render_examples(fex)) if fex else ""
                more, _ = ask(a.url, a.model, SYSTEM, FAMILY_PROMPT % (finstr, listed, fexs, user), tk)
                fam_added[fam] = [x for x in (more or []) if str(x.get("verb", "")).lower() in fverbs]
        verdicts, v_added = [], []
        rows_all = ev + added + [r for v in fam_added.values() for r in v]
        pre_verify = list(rows_all)
        if ok and a.verify_pass:
            listing = "\n".join(f"{i}: {json.dumps(r, ensure_ascii=False)}" for i, r in enumerate(rows_all)) or "(no rows)"
            if a.verify_prompt == "v3":
                vprompt = VERIFY_V3 % ("Worked examples:\n\n" + render_examples(ex), listing, user)
            else:
                vprompt = VERIFY_V2 % (listing, user)
            votes = [ask_json(a.url, a.model, SYSTEM, vprompt, tk) for _ in range(max(1, a.verify_votes))]
            votes = [vd for vd in votes if vd is not None]
            if votes:
                drops = []
                for vd in votes:
                    vv = vd.get("verdicts") or []
                    verdicts.append(vv)
                    d = set()
                    for x in vv:
                        if not (isinstance(x, dict) and x.get("keep") is False):
                            continue
                        if a.verify_prompt == "v3" and not str(x.get("code") or "").strip():
                            continue  # v3: a drop without a cited rule code is not a drop
                        try:
                            d.add(int(x.get("i")))
                        except (TypeError, ValueError):
                            pass
                    drops.append(d)
                # a row goes only when EVERY verifier vote drops it (round 4:
                # single-vote drops struck as many true rows as false ones)
                drop = set.intersection(*drops) if drops else set()
                rows_all = [r for i, r in enumerate(rows_all) if i not in drop]
                v_added = [x for x in (votes[0].get("add") or []) if isinstance(x, dict)]
                rows_all += v_added
        kept, dropped = check_rows(rows_all, window, wiki, bad_end)
        return {"id": r["id"], "events": kept, "ok": ok, "raw": raw,
                "n_draft": len(ev), "n_missed_pass": len(added), "dropped": dropped,
                "verdicts": verdicts, "n_verify_added": len(v_added),
                "stages": {"samples": samples, "missed": added, "families": fam_added, "pre_verify": pre_verify,
                           "verify_added": v_added},
                "examples": [b["id"] for b in ex]}

    with ThreadPoolExecutor(a.workers) as pool, open(a.out, "a") as f:
        for n, res in enumerate(pool.map(job, rows), 1):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            if n % 25 == 0:
                print(f"{n}/{len(rows)}", flush=True)
    print("done", len(rows))


if __name__ == "__main__":
    sys.exit(main())
