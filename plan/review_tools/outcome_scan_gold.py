#!/usr/bin/env python3
"""Outcome-ruling scan of the gold v2 set (2026-11-03), READ-ONLY.

Owner ruling 2026-11-03 (gold27_system.md, last section): decide every outcome row from the factual state the
passage establishes (who is subdued / in control, does the exchange continue, final or temporary); one act can
carry several true rows. The gold windows were reviewed under narrower rulings, so this lists the windows whose
latest audit rows may miss an outcome row or hold an unsupported one. Every candidate is read by hand; the
heuristics are deliberately broad (recall over precision).

Classes (one window can carry several):
  A_no_outcome   fought event / wounded or attacked fact for a named pair, a cue word (capture, restrain, cut off,
                 subdue, flee, win, beat ...) in the row's quote or the two sentences after it, and no
                 defeated/killed/escaped/captured/sealed row for the pair in either direction
  A_captured     same pair test, but the only outcome row is captured/sealed (whether capture also carries defeated
                 is an owner question; listed, not proposed)
  B_killed_wound killed event whose quote has no death word (a wound or a destroyed body may be all it shows)
  C_wound_end    wounded fact (named pair or victim-only) with an end-of-encounter cue in its sentence or the next
                 two, and no defeated/killed row for the pair
  D_defeat_cont  defeated event whose quote/next sentences show the exchange going on (but, however, recovers,
                 counter, regenerates, escapes ...)

    outcome_scan_gold.sh [--class C] [--list OUT] [--quiet]   -> counts, and "b<n> CLASS,CLASS" lines
    outcome_scan_gold.sh show B [B ...]                       -> full window + events + outcome facts + the hits
    outcome_scan_gold.sh check FILE                           -> parse + gate a proposal file WITHOUT writing

First run 2026-11-03: 639 candidates, all read; 70 proposals in big/gold_v2/outcome/proposed_G901.txt, owner
questions in big/gold_v2/outcome/SUMMARY.md.
"""
import os
import re
import sys
from collections import Counter

os.environ["BV2_SET"] = "gold"  # big_review_v2 reads it at import: gold paths, gold order, gold passages
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/plan/review_tools")
import lint_v2  # noqa: E402

bv = lint_v2.bv
assert bv.GOLD and "gold_v2" in str(bv.AUDIT2), bv.AUDIT2

OUTCOME = {"defeated", "killed", "escaped", "captured", "sealed"}
CUE_A = re.compile(r"captur|restrain|bind|bound\b|seal|trap|disarm|paraly|knock|cut(?:s|ting)? off|sever|subdu|"
                   r"overpower|overwhelm|\bstop|prevent|flee|fled|retreat|escap|surrender|spare|\bwin|\bwon\b|"
                   r"victor|lose|\blost\b|\bloses\b|beat|defeat|unconscious|incapacit|immobili|pin(?:s|ned)\b|"
                   r"kill|slay|slain|finish|crush|impale|decapitat|behead|tear|tore|rip|slice|bisect|in half|"
                   r"collaps|fall(?:s)? unconscious|gives? up|withdr|driv(?:e|es|en) (?:him|her|them|off|away)|"
                   r"repel|rout|outmatch|best(?:s|ed)\b|bested|triumph|forced? (?:him|her|them|to)|chases? off|"
                   r"left for dead|leaves? (?:him|her) |send(?:s)? (?:him|her) flying|blast(?:s|ed)? (?:him|her) away",
                   re.I)
CUE_END = re.compile(r"flee|fled|retreat|escap|surrender|unconscious|collaps|incapacit|defeat|\bwin|\bwon\b|victor|"
                     r"triumph|gives? up|withdr|leaves?\b|left\b|walks? away|spare|ends? the (?:fight|battle)|"
                     r"loses|\blost\b|beat|subdu|overpower|restrain|captur|knock|teach (?:him|her|them) a lesson|"
                     r"finish|dies|died|dead|kill|bleed(?:s|ing)? out|passes out|passed out|faint|helpless",
                     re.I)
DEATH = re.compile(r"kill|slay|slain|slew|murder|death|dies|died|\bdead\b|execut|assassinat|perish|fatal|"
                   r"lifeless|corpse|end(?:s|ed)? (?:his|her|their) li(?:fe|ves)|take (?:his|her) life|"
                   r"took (?:his|her) life|claim(?:s|ed)? (?:his|her) life|life\b|\bdeceased|annihilat|"
                   r"eras(?:e|es|ed)\b|obliterat|exterminat|wip(?:e|es|ed) out|sacrific|shot dead|drown|"
                   r"burn(?:s|ed)? (?:him|her|them) alive|devour|eat(?:s|en)? (?:him|her)|ate\b|consum", re.I)
CONT = re.compile(r"\bbut\b|however|recover|gets? (?:back )?up|stands? (?:back )?up|continu|resum|counter|"
                  r"regenerat|surviv|retaliat|turns? the tables|escap|\bfree(?:s|d)? (?:him|her|them)self|"
                  r"breaks? free|still\b|again\b|rematch|before (?:he|she|they) can|attempt|tries|tried|"
                  r"heals?|healed|revives?|reform|reassembl|unfazed|unharmed|shrugs? off|no effect|fails?\b|"
                  r"failed|in vain|barely|nearly|almost", re.I)
SENT = re.compile(r"(?<=[.!?])\s+|(?<=\))\s+(?=[A-Z])")


def records():
    ids, a2, pas = bv.order(), bv.audit2(), bv.br.passages()
    for b, wid in enumerate(ids, 1):
        if wid in a2:
            yield b, a2[wid], pas[wid]


def sentences(text):
    out, pos = [], 0
    for part in SENT.split(text):
        i = text.find(part, pos)
        out.append((i, i + len(part), part))
        pos = i + len(part)
    return out


def context(quote, text, after=2):
    """The sentence(s) the quote sits in plus `after` sentences following it ('' when the quote is not found)."""
    q = bv.exact_quote(quote or "", text)
    i = text.find(q) if q else -1
    if i < 0:
        return quote or ""
    j = i + len(q)
    ss = sentences(text)
    idx = [k for k, (a, z, _) in enumerate(ss) if z > i and a < j]
    if not idx:
        return q
    lo, hi = idx[0], min(len(ss) - 1, idx[-1] + after)
    return " ".join(s for _, _, s in ss[lo:hi + 1])


def pair(a, b):
    return frozenset((a or "", b or ""))


def scan(b, rec, text):
    ev, fa = rec.get("events") or [], rec.get("facts") or []
    outc = {}
    for e in ev:
        if e["verb"] in OUTCOME and e.get("object"):
            outc.setdefault(pair(e["subject"], e["object"]), set()).add(e["verb"])
    hits = {}

    def hit(cls, why):
        hits.setdefault(cls, []).append(why)
    fights = [(e["subject"], e["object"], e.get("quote") or "", "E fought") for e in ev
              if e["verb"] == "fought" and e.get("object")]
    fights += [(f["subject"], f["object"], f.get("quote") or "", "F " + f["relation"]) for f in fa
               if f.get("relation") in ("wounded", "attacked") and f.get("object")]
    for s, o, q, kind in fights:
        got = outc.get(pair(s, o), set())
        ctx = context(q, text)
        m = CUE_A.search(ctx)
        if not m:
            continue
        if not got:
            hit("A_no_outcome", f"{kind} {s}|{o} cue '{m.group(0)}'")
        elif got <= {"captured", "sealed"}:
            hit("A_captured", f"{kind} {s}|{o} only {sorted(got)}")
    for e in ev:
        if e["verb"] == "killed" and not DEATH.search(e.get("quote") or ""):
            hit("B_killed_wound", f"killed {e['subject']}|{e['object']} quote '{(e.get('quote') or '')[:70]}'")
    for f in fa:
        if f.get("relation") != "wounded":
            continue
        got = outc.get(pair(f["subject"], f.get("object")), set()) if f.get("object") else set()
        if not f.get("object"):  # victim-only wound: any outcome row naming the victim
            got = set().union(*[v for k, v in outc.items() if f["subject"] in k] or [set()])
        if got & {"defeated", "killed"}:
            continue
        m = CUE_END.search(context(f.get("quote"), text))
        if m:
            hit("C_wound_end", f"wounded {f['subject']}|{f.get('object') or '-'} cue '{m.group(0)}'")
    for e in ev:
        if e["verb"] != "defeated":
            continue
        q = e.get("quote") or ""
        ctx = context(q, text, after=1)
        m = CONT.search(ctx)
        if m:
            hit("D_defeat_cont", f"defeated {e['subject']}|{e['object']} cue '{m.group(0)}'")
    return hits


def main():
    a = sys.argv[1:]
    if a and a[0] == "check":
        return check(a[1])
    if a and a[0] == "show":
        return show([int(x.lstrip("b")) for x in a[1:]])
    only = a[a.index("--class") + 1] if "--class" in a else None
    out = a[a.index("--list") + 1] if "--list" in a else None
    n, cnt, lines = 0, Counter(), []
    for b, rec, text in records():
        n += 1
        h = scan(b, rec, text)
        if only:
            h = {k: v for k, v in h.items() if k == only}
        if h:
            cnt.update(h.keys())
            lines.append(f"b{b} {','.join(sorted(h))}  # " + " ; ".join(w for v in h.values() for w in v))
    if "--quiet" not in a:
        print("\n".join(lines))
    print(f"# scanned {n} windows; candidates {len(lines)}; by class {dict(cnt)}", file=sys.stderr)
    if out:
        with open(out, "w") as fh:
            fh.write("\n".join(lines) + "\n")


REL_SHOW = {"wounded", "attacked", "dies", "destroyed", "lost_power", "kidnapped", "transformed_into", "healed",
            "helped", "protected"}


def show(bs):
    """Compact reading view: the full window, every event, and the facts an outcome decision can touch (outcome
    relations, plus other_verb rows whose verb is a cue word). Tags and unrelated facts are left out."""
    want = set(bs)
    for b, rec, text in records():
        if b not in want:
            continue
        print(f"===== b{b} {rec.get('page')} [{rec.get('series')}]")
        print(text)
        for e in rec.get("events") or []:
            print(f"  E {e['subject']}|{e['verb']}|{e['object'] or '-'}|{e.get('quote') or ''}")
        for f in rec.get("facts") or []:
            if f.get("relation") in REL_SHOW or (f.get("relation") == "other_verb" and (
                    CUE_A.search(f.get("object") or "") or CUE_END.search(f.get("object") or ""))):
                mod, cert, ab = f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by") or ""
                tail = "" if (mod, cert, ab) == ("actual", "stated", "") else f"|{mod}|{cert}|{ab or '-'}"
                print(f"  F {f['subject']}|{f['relation']}|{f.get('object') or '-'}|{f.get('quote') or ''}{tail}")
        for k, v in scan(b, rec, text).items():
            print(f"  ? {k}: " + " ; ".join(v))
        print()


def check(path):
    """Dry run of `rv.sh fix`: the same parse (apply_edits) and the same gates, nothing appended anywhere."""
    import importlib.util
    from pathlib import Path
    spec = importlib.util.spec_from_file_location("label_single", Path(bv.__file__).resolve().parent / "label_single.py")
    ls = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ls)
    import verify_row_wiki as vrw
    pas, wikis, v2 = bv.br.passages(), {}, {r["id"]: r for r in bv.jl(bv.V2)}
    ok = bad = 0
    for c in bv.apply_edits(path):
        series = v2.get(c["id"], {}).get("series", "marvel")
        wiki = wikis.setdefault(series, vrw.Wiki(str(bv.ROOT / "series" / series / "facts.db")))
        w = pas[c["id"]]
        for row in c["events"] + c["facts"] + c["tags"]:
            row["quote"] = bv.exact_quote(row.get("quote"), w)
        ek, ed = ls.gate([{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in c["events"]], w, wiki)
        fk, fd = ls.fact_gate_keep(c["facts"], w, wiki)
        tk, td = ls.tag_gate_keep(c["tags"], w)
        why = []
        if not c["kept"]:
            why.append("no keep")
        if ed or len(ek) != len(c["events"]):
            why.append(f"events {[(d.get('subject'), d.get('verb'), d.get('object'), d['why']) for d in ed]}")
        if fd:
            why.append(f"facts {[(d.get('subject'), d.get('relation'), d.get('object'), d['why']) for d in fd]}")
        if td:
            why.append(f"tags {[(d.get('tag'), d['why']) for d in td]}")
        if why:
            bad += 1
            print(f"WOULD REFUSE b{c['b']}: " + " | ".join(why))
        else:
            ok += 1
    print(f"# check {path}: {ok} would apply, {bad} would be refused (nothing written)")


if __name__ == "__main__":
    main()
