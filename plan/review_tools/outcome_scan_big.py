#!/usr/bin/env python3
"""Outcome-row scan of the FINAL big-v2 rows (latest big_audit_v2 record per window), 2026-11-03.

Owner ruling 2026-11-03 (plan/review_tools/gold27_system.md, last section): decide every outcome row from the
factual state the passage establishes -- who is subdued / in control, does the exchange continue, is the state
final or temporary. One act can carry several true rows (b2187 gold: Ultron cuts off Klaue's arm, nothing
continues -> wounded + defeated). The 14k BIG set was reviewed under narrower rulings, so this lists the windows
whose outcome rows may be missing or unsupported, ranked by how strongly the text points at a change.
READ-ONLY: it never writes the audit file; proposals are hand-written fix blocks under big/outcome/.

    python outcome_scan_big.py scan [--out DIR]        ranked candidates -> DIR/candidates.{jsonl,txt}
    python outcome_scan_big.py show B [B ...]          window text + final rows (+ overlap partners)
    python outcome_scan_big.py check FILE              dry-run a fix file: parse + removals + gates, no write

Patterns (score = cue strength x where the cue sits: the row's quote 3, its sentence 2, the next sentence 1):
  P1 fight_no_outcome   fought event / wounded or attacked fact for a pair with an outcome cue (subdue, capture,
                        knock out, cut off, flee, win, ...) and no defeated/killed/escaped/captured/sealed row
                        for that pair in either direction
  P2 killed_no_death    killed event whose quote and sentence state no death (only a wound or a destroyed body)
  P3 wound_then_end     wounded fact next to a stated end of the encounter (fled, defeated, unconscious) with no
                        defeated/escaped row for the pair
  P4 defeat_continues   defeated event whose sentence or the next one shows the exchange continuing or the
                        outcome hedged (nearly, attempted, but recovered, fought back)
Run via the main venv with SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine (as lint.sh does).
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/tools/train")
import big_review_v2 as bv  # noqa: E402

br = bv.br
OUTDIR = bv.BIG / "outcome"
COMP = bv.BIG / "recon" / "components.jsonl"
OUTCOME_EV = {"defeated", "killed", "escaped", "captured", "sealed"}

# (regex, weight, label). Weight = how strongly the cue states a decided outcome.
CUES = [
    (r"\bsubdu\w*", 5, "subdue"), (r"\boverpower\w*", 5, "overpower"), (r"\bknock\w* (?:\w+ )?(?:out|unconscious)", 5, "knock out"),
    (r"\bunconscious\b", 4, "unconscious"), (r"\bincapacitat\w*", 5, "incapacitate"), (r"\bdefeat\w*", 4, "defeat"),
    (r"\b(?:won|wins?|winning)\b", 3, "win"), (r"\bvictor(?:y|ious)\b", 4, "victory"), (r"\bbe(?:at|aten|ats)\b", 3, "beat"),
    (r"\b(?:lost|loses?|losing)\b(?! (?:his|her|their|its) (?:life|lives|memor|powers?|mind))", 2, "lose"),
    (r"\bcaptur\w*", 4, "capture"), (r"\brestrain\w*", 4, "restrain"), (r"\b(?:bound|binds?|binding)\b", 2, "bind"),
    (r"\bseal\w*", 2, "seal"), (r"\btrap\w*", 3, "trap"), (r"\bdisarm\w*", 4, "disarm"), (r"\bparaly[sz]\w*", 4, "paralyse"),
    (r"\bimmobili[sz]\w*", 4, "immobilise"), (r"\bpinned\b", 3, "pin"), (r"\bcut(?:s|ting)? off\b", 4, "cut off"),
    (r"\bsever(?:s|ed|ing|ance)?\b", 4, "sever"), (r"\bdecapitat\w*|\bbehead\w*", 4, "behead"), (r"\bimpal\w*", 3, "impale"),
    (r"\bstop(?:s|ped|ping)?\b", 2, "stop"), (r"\bprevent\w*", 1, "prevent"), (r"\bthwart\w*|\bfoil\w*", 3, "thwart"),
    (r"\bfled\b|\bflee(?:s|ing)?\b", 4, "flee"), (r"\bretreat\w*", 4, "retreat"), (r"\bescap\w*", 3, "escape"),
    (r"\bran (?:away|off)\b", 4, "ran away"), (r"\bdr(?:o|i)ve\w* (?:\w+ )?(?:off|away|back)\b", 4, "drive off"),
    (r"\brepel(?:s|led|ling)?\b|\brepulsed\b", 4, "repel"), (r"\bsurrender\w*", 5, "surrender"), (r"\bspar(?:e|ed|es|ing)\b", 4, "spare"),
    (r"\bfinish\w* (?:\w+ )?off\b", 4, "finish off"), (r"\barrest\w*", 3, "arrest"), (r"\bimprison\w*", 3, "imprison"),
    (r"\bat (?:his|her|their) mercy\b", 5, "at mercy"), (r"\bbested\b", 5, "bested"), (r"\bvanquish\w*", 5, "vanquish"),
    (r"\bneutrali[sz]\w*", 4, "neutralise"), (r"\bforced (?:\w+ )?to (?:flee|retreat|surrender|withdraw|leave)", 5, "forced out"),
    (r"\bwithdr[ae]w\w*", 2, "withdraw"), (r"\bbroke (?:\w+ )?(?:neck|back|spine|arm|leg)s?\b", 3, "break bone"),
    (r"\bsend\w* (?:\w+ )?(?:flying|packing)\b", 1, "send flying"), (r"\btied (?:\w+ )?up\b", 4, "tied up"),
]
CUES = [(re.compile(p, re.I), w, l) for p, w, l in CUES]
HEDGE = re.compile(r"\b(?:tr(?:y|ied|ies|ying) to|attempt\w*|nearly|almost|unable|fail\w*|could not|couldn't|"
                   r"wanted to|plan\w* to|intend\w*|would|threaten\w*|seemingly|apparently|in order to|so as to)\b", re.I)
DEATH = re.compile(r"\b(?:kill\w*|slay\w*|slain|slew|murder\w*|death|dead|die[sd]?|dying|execut\w*|assassinat\w*|"
                   r"fatal\w*|lifeless|corpse|perish\w*|deceased|life|lives|mortally|annihilat\w*|eradicat\w*|"
                   r"incinerat\w*|vaporiz\w*|disintegrat\w*|obliterat\w*|beheaded|decapitat\w*|crush\w* to death|"
                   r"sacrific\w*|end(?:ed|ing)? (?:his|her|their|its)|finish\w* (?:\w+ )?off|eaten|devour\w*|consum\w*)\b", re.I)
WOUNDISH = re.compile(r"\b(?:wound\w*|injur\w*|stab\w*|shot|shoot\w*|destroy\w*|blast\w*|cut|slash\w*|impal\w*|"
                      r"sever(?:s|ed|ing)?|tore|torn|ripp\w*|burn\w*|maim\w*|body|bodies|armor|suit|shell|form)\b", re.I)
CONTINUE = re.compile(r"\b(?:recover\w*|regenerat\w*|fought back|continu\w*|resum\w*|got back up|returned to the fight|"
                      r"rejoin\w*|retaliat\w*|turned the tables|counter\w*|but (?:he|she|they|it) (?:survived|escaped|managed)|"
                      r"managed to (?:escape|survive|break free|recover)|broke free|break free|before (?:he|she|they) could|"
                      r"however|though|although|yet)\b", re.I)
ENDING = re.compile(r"\b(?:fled|flee(?:s|ing)?|retreat\w*|ran (?:away|off)|escap\w*|defeat\w*|unconscious|subdu\w*|"
                    r"surrender\w*|withdr[ae]w\w*|forced (?:\w+ )?to (?:flee|retreat|surrender|withdraw|leave)|"
                    r"collaps\w*|knock\w* (?:\w+ )?out|left (?:him|her|them) for dead|incapacitat\w*|arrest\w*|captur\w*)\b", re.I)
_SPLIT = re.compile(r"(?<=[.!?])[\"')\]]*\s+(?=[A-Z\"'(\[])|\n+")


def sentences(text):
    out, pos = [], 0
    for m in _SPLIT.finditer(text):
        out.append((pos, text[pos:m.start()].strip()))
        pos = m.end()
    out.append((pos, text[pos:].strip()))
    return [(p, s) for p, s in out if s]


def locate(sents, text, quote):
    """index of the sentence holding the quote (its start), or None."""
    if not quote:
        return None
    i = text.find(quote)
    if i < 0:
        return None
    for k, (p, s) in enumerate(sents):
        if p <= i < p + len(s) + 2:
            return k
    return len(sents) - 1


def first_word(name):
    return re.escape((name or "").split(" (")[0].split()[-1]) if name else None


def mentions(s, name):
    if not name:
        return False
    parts = [p for p in re.split(r"[\s\-]+", name.split(" (")[0]) if len(p) > 2 and p[0].isupper()]
    return any(re.search(r"\b" + re.escape(p) + r"\b", s) for p in parts) or name in s


def cue_hits(s):
    return [(w, l, m.group(0)) for rx, w, l in CUES for m in rx.finditer(s)]


def pair_outcomes(ev):
    have = set()
    for e in ev:
        if e["verb"] in OUTCOME_EV and e.get("object"):
            have.add(frozenset((e["subject"], e["object"])))
    return have


def partners():
    p = {}
    if COMP.exists():
        for l in open(COMP):
            c = json.loads(l)
            for w in c["windows"]:
                p[w] = [x for x in c["windows"] if x != w]
    return p


def score_pair(sents, k, quote, a, o):
    """best cue score around one row: quote x3, its sentence x2, next sentence x1 (hedged cues halved)."""
    best, why = 0, None
    zones = [(quote or "", 3)]
    if k is not None:
        zones.append((sents[k][1], 2))
        if k + 1 < len(sents) and (mentions(sents[k + 1][1], a) or mentions(sents[k + 1][1], o)
                                   or re.match(r"(?:He|She|They|It|The|After|Eventually|Ultimately|Finally)\b", sents[k + 1][1])):
            zones.append((sents[k + 1][1], 1))
    for z, mult in zones:
        for w, lab, word in cue_hits(z):
            sc = w * mult
            if HEDGE.search(z):
                sc = sc / 2
            if sc > best:
                best, why = sc, f"{lab}:'{word}'@{'quote' if mult == 3 else 'sent' if mult == 2 else 'next'}"
    return best, why


def scan_window(b, wid, rec, text):
    ev, fa = rec.get("events", []) or [], rec.get("facts", []) or []
    sents = sentences(text)
    have = pair_outcomes(ev)
    out = []
    seen = set()
    # P1: fought events + wounded/attacked facts with an outcome cue, no outcome row for the pair
    rows = [("E", e["subject"], "fought", e.get("object"), e.get("quote")) for e in ev if e["verb"] == "fought"]
    rows += [("F", f.get("subject"), f.get("relation"), f.get("object"), f.get("quote")) for f in fa
             if f.get("relation") in ("wounded", "attacked") and f.get("object") and (f.get("modality") or "actual") == "actual"]
    for lay, s, v, o, q in rows:
        if not o or frozenset((s, o)) in have:
            continue
        key = ("P1", frozenset((s, o)))
        k = locate(sents, text, q)
        sc, why = score_pair(sents, k, q, s, o)
        if sc <= 0:
            continue
        if key in seen:
            continue
        seen.add(key)
        out.append({"b": b, "pat": "P1", "score": sc + (1 if v == "wounded" else 0), "row": f"{s}|{v}|{o}",
                    "cue": why, "quote": q, "sent": sents[k][1] if k is not None else ""})
    # P2: killed with no death word
    for e in ev:
        if e["verb"] != "killed":
            continue
        q = e.get("quote") or ""
        k = locate(sents, text, q)
        sent = sents[k][1] if k is not None else q
        if DEATH.search(q):
            continue
        sc = 6 if not DEATH.search(sent) else 3
        if WOUNDISH.search(q):
            sc += 2
        out.append({"b": b, "pat": "P2", "score": sc, "row": f"{e['subject']}|killed|{e['object']}",
                    "cue": "no death word in quote" + ("" if DEATH.search(sent) else " or sentence"), "quote": q, "sent": sent})
    # P3: wounded facts next to a stated end, no defeated/escaped for the pair
    for f in fa:
        if f.get("relation") != "wounded":
            continue
        s, o, q = f.get("subject"), f.get("object"), f.get("quote") or ""
        k = locate(sents, text, q)
        if k is None:
            continue
        zone = sents[k][1] + (" " + sents[k + 1][1] if k + 1 < len(sents) else "")
        m = ENDING.search(zone)
        if not m:
            continue
        if o and frozenset((s, o)) in have:
            continue
        if not o:  # victim|wounded|- : any outcome row naming the victim?
            if any(e["verb"] in OUTCOME_EV and s in (e["subject"], e.get("object")) for e in ev):
                continue
        sc = 4 if m.start() < len(sents[k][1]) else 2
        if HEDGE.search(zone):
            sc -= 1
        out.append({"b": b, "pat": "P3", "score": sc, "row": f"{s}|wounded|{o or '-'}", "cue": f"end:'{m.group(0)}'",
                    "quote": q, "sent": zone})
    # P4: defeated with the exchange continuing / hedged
    for e in ev:
        if e["verb"] != "defeated":
            continue
        q = e.get("quote") or ""
        k = locate(sents, text, q)
        if k is None:
            continue
        sent = sents[k][1]
        nxt = sents[k + 1][1] if k + 1 < len(sents) else ""
        sc, why = 0, None
        h = HEDGE.search(q)
        if h:
            sc, why = 5, f"hedge in quote:'{h.group(0)}'"
        else:
            c = CONTINUE.search(sent[sent.find(q[:20]) + len(q):] if q[:20] in sent else sent)
            if c:
                sc, why = 3, f"continues in sentence:'{c.group(0)}'"
            elif nxt and (mentions(nxt, e["object"]) or mentions(nxt, e["subject"])):
                c = CONTINUE.search(nxt)
                if c:
                    sc, why = 2, f"continues next:'{c.group(0)}'"
        if sc:
            out.append({"b": b, "pat": "P4", "score": sc, "row": f"{e['subject']}|defeated|{e['object']}", "cue": why,
                        "quote": q, "sent": sent + (" || " + nxt if nxt else "")})
    return out


def load():
    ids = bv.order()
    a2 = bv.audit2()
    return ids, a2, br.passages()


def scan(outdir):
    ids, a2, pas = load()
    part = partners()
    cands, scanned = [], 0
    for b, wid in enumerate(ids, 1):
        rec = a2.get(wid)
        if not rec:
            continue
        scanned += 1
        for c in scan_window(b, wid, rec, pas[wid]):
            c["partners"] = part.get(b, [])
            cands.append(c)
    pri = {"P2": 0.3, "P1": 0.2, "P3": 0.1, "P4": 0.0}  # tie-break: more decisive patterns first
    cands.sort(key=lambda c: (-(c["score"] + pri[c["pat"]]), c["b"]))
    for i, c in enumerate(cands, 1):
        c["rank"] = i
    outdir.mkdir(parents=True, exist_ok=True)
    with open(outdir / "candidates.jsonl", "w") as fh:
        for c in cands:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    with open(outdir / "candidates.txt", "w") as fh:
        for c in cands:
            fh.write(f"{c['rank']:5d} b{c['b']:<6d} {c['pat']} {c['score']:4.1f} {c['row']}  [{c['cue']}]"
                     f"{'  partners ' + str(c['partners']) if c['partners'] else ''}\n")
    from collections import Counter
    print(f"scanned {scanned} windows | candidates {len(cands)} in {len({c['b'] for c in cands})} windows")
    print(" by pattern", dict(Counter(c["pat"] for c in cands)))
    print(" by score>=8", sum(c["score"] >= 8 for c in cands), "score>=6", sum(c["score"] >= 6 for c in cands),
          "score>=4", sum(c["score"] >= 4 for c in cands))
    print(f" written {outdir}/candidates.jsonl and candidates.txt")


def show(bs, notes=None, ctx=None):
    ids, a2, pas = load()
    part = partners()
    for b in bs:
        wid = ids[b - 1]
        rec = a2.get(wid, {})
        print(f"===== b{b} {rec.get('page')}" + (f"  partners {part[b]}" if part.get(b) else ""))
        for n in (notes or {}).get(b, []):
            print("  CAND " + n)
        text = pas[wid]
        if ctx and len(text) > 900:  # --ctx: only the sentences around each candidate's quote (+-2)
            sents = sentences(text)
            keep = set()
            for c in ctx.get(b, []):
                k = locate(sents, text, c.get("quote"))
                if k is not None:
                    keep.update(range(max(0, k - 2), min(len(sents), k + 3)))
            text = " ".join(("" if i - 1 in keep or i == min(keep, default=0) else "[...] ") + sents[i][1]
                            for i in sorted(keep)) if keep else text
        print(text)
        print(" EVENTS", [(e["subject"], e["verb"], e.get("object"), (e.get("quote") or "")[:38]) for e in rec.get("events", [])])
        facts = rec.get("facts", [])
        if ctx:  # --ctx: only the facts that bear on an outcome
            facts = [f for f in facts if f.get("relation") in ("wounded", "attacked", "dies", "lost_power", "healed",
                                                                "helped", "protected", "kidnapped", "other_verb")]
        print(" FACTS", [(f.get("subject"), f.get("relation"), f.get("object"),
                          ("" if (f.get("modality") or "actual") == "actual" else f"{f['modality']}/{f.get('asserted_by')}")
                          + ("" if (f.get("certainty") or "stated") == "stated" else "/" + f["certainty"]),
                          (f.get("quote") or "")[:30]) for f in facts])


def check(path):
    """Dry run of rv.sh fix: the same parse (bv.apply_edits) and the same three gates, nothing written."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    pas, wikis = br.passages(), {}
    v2 = {r["id"]: r for r in bv.jl(bv.V2)}
    nok = nbad = 0
    for c in bv.apply_edits(path):
        series = v2.get(c["id"], {}).get("series", "marvel")
        wiki = wikis.setdefault(series, vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db")))
        w = pas[c["id"]]
        for row in c["events"] + c["facts"] + c["tags"]:
            row["quote"] = bv.exact_quote(row.get("quote"), w)
        ek, ed = ls.gate([{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in c["events"]], w, wiki)
        fk, fd = ls.fact_gate_keep(c["facts"], w, wiki)
        tk, td = ls.tag_gate_keep(c["tags"], w)
        bad = []
        if not c["kept"]:
            bad.append("no keep")
        if ed or len(ek) != len(c["events"]):
            bad.append(f"events {[(d.get('subject'), d.get('verb'), d.get('object'), d['why']) for d in ed]} kept {len(ek)}/{len(c['events'])}")
        if fd:
            bad.append(f"facts {[(d.get('subject'), d.get('relation'), d.get('object'), d['why']) for d in fd]}")
        if td:
            bad.append(f"tags {[(d.get('tag'), d['why']) for d in td]}")
        if bad:
            nbad += 1
            print(f"WOULD REFUSE b{c['b']}: " + " | ".join(bad))
        else:
            nok += 1
    print(f"dry run: {nok} would apply, {nbad} would be refused (nothing written)")


def main():
    a = sys.argv[1:]
    if not a or a[0] == "scan":
        scan(Path(a[a.index("--out") + 1]) if "--out" in a else OUTDIR)
    elif a[0] == "show" and a[1:2] == ["--rank"]:  # show --rank LO-HI: the windows of ranks LO..HI, first-seen order
        lo, hi = map(int, a[2].split("-"))
        cands = [json.loads(l) for l in open(OUTDIR / "candidates.jsonl")]
        # windows whose candidates all rank below LO were already shown by an earlier range: skip them
        first = {}
        for c in cands:
            first.setdefault(c["b"], c["rank"])
        bs, notes = [], {}
        for c in cands:
            if lo <= c["rank"] <= hi and first[c["b"]] >= lo:
                if c["b"] not in notes:
                    bs.append(c["b"])
                notes.setdefault(c["b"], []).append(f"#{c['rank']} {c['pat']} {c['row']} [{c['cue']}]")
        for b in bs:  # every candidate of the window, not only those in range
            notes[b] = [f"#{c['rank']} {c['pat']} {c['row']} [{c['cue']}]" for c in cands if c["b"] == b]
        show(bs, notes, ctx={b: [c for c in cands if c["b"] == b] for b in bs} if "--ctx" in a else None)
    elif a[0] == "show":
        show([int(x.lstrip("b")) for x in a[1:]])
    elif a[0] == "check":
        check(a[1])
    elif a[0] == "summary":  # summary FILE... -> markdown table rows (b, old rows, new rows, reason)
        for path in a[1:]:
            cur = None
            blocks = []
            for line in open(path):
                line = line.rstrip("\n")
                if line.startswith("@"):
                    head, _, why = line[1:].partition(" ")
                    cur = {"b": head, "why": why.replace("outcome 2026-11-03: ", ""), "old": [], "new": []}
                    blocks.append(cur)
                elif cur and line[:2] in ("- ", "f-"):
                    cur["old"].append(line.split(" ", 1)[1])
                elif cur and line[:2] in ("+ ", "f+"):
                    p = line.split(" ", 1)[1].split("|")
                    cur["new"].append("|".join(p[:3]) + ("" if len(p) <= 4 or p[4] in ("", "actual") else f" ({p[4]})"))
            for c in blocks:
                esc = lambda t: t.replace("|", "\\|")  # row strings are S|verb|O: escape for the markdown table
                print(f"| b{c['b']} | {esc('; '.join(c['old']) or '-')} | {esc('; '.join(c['new']) or '-')} | {esc(c['why'])} | {Path(path).name} |")


if __name__ == "__main__":
    main()
