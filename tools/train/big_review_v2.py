#!/usr/bin/env python3
"""Claude's ONE-pass review of the v2 windows: events + facts + tags together (owner 2026-10-10:
"the fact layer should be handled along with the event layer so that we don't have to work on
every window again").

State never edits labels*.jsonl or big_audit.jsonl. Corrections go to big_audit_v2.jsonl as the
COMPLETE final rows of a window ({id, events, facts, tags, why}; latest per id wins); the cursor is
review_cursor_v2.txt. Order = the b-numbers of the v1 review (labels.jsonl lines 1-5405), then the
remaining labels_v2.jsonl ids in file order.

Base rows of a window: big_audit_v2 if present; else events = Claude's v1-reviewed rows
(big_audit.jsonl, frozen, shown as [reviewed]) when b <= the v1 cursor, otherwise the v2 row's;
facts/tags = the v2 row's.

    big_review_v2.py view N [--from B]     window + rows + event flags + fact flags + UNCOVERED
    big_review_v2.py fix EDITS.txt         gated (event gate, fact gate, tag gate); REFUSED = resubmit
    big_review_v2.py mark B | status

EDITS format, one block per corrected window (unmentioned windows are accepted as shown):
    @<b> <why>
    keep | keepe | keepf          start from both layers / events only / facts+tags only (else empty)
    r Old=>New                    rename an end in events, facts and asserted_by
    + S|verb|O|quote   - S|verb|O                       event rows (O '-' = null)
    f+ S|rel|O|quote[|modality|certainty|asserted_by|canon]   f- S|rel|O   fact rows
    t+ tag|quote       t- tag[|quote-prefix]                     tag rows
"""
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("SCRIPTENGINE_ROOT", Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(ROOT / "tools" / "train"))
import big_review as br  # noqa: E402  (main checkout: passages, v1 audit, v1 cursor)
# the v2 code (label_single v2, fact_gate, fact_coverage, big_flags) lives on this branch: it must win
sys.path.insert(0, str(Path(__file__).resolve().parent))
import big_flags  # noqa: E402
# big_flags pushes the main checkout's tools/train back to the front: re-pin this branch's copy
sys.path.insert(0, str(Path(__file__).resolve().parent))
for _m in ("label_single", "fact_gate", "fact_coverage"):
    sys.modules.pop(_m, None)
import fact_coverage  # noqa: E402
import fact_gate  # noqa: E402

BIG = br.BIG
V2, AUDIT2 = BIG / "labels_v2.jsonl", BIG / "big_audit_v2.jsonl"
# BV2_CURSOR=backfill -> the facts backfill over b1-b1161 (events already reviewed) keeps its own cursor
CURSOR2 = BIG / ("review_cursor_v2%s.txt" % ("_" + os.environ["BV2_CURSOR"] if os.environ.get("BV2_CURSOR") else ""))
SYM = ("fought", "met")


def jl(p):
    out = []
    if Path(p).exists():
        for l in open(p):
            l = l.strip("\x00\n ")
            if l:
                out.append(json.loads(l))
    return out


def cursor2():
    try:
        return int(CURSOR2.read_text().strip())
    except (OSError, ValueError):
        return 0


def order():
    v1 = [r["id"] for r in br.jl(br.LABELS)][:5405]
    seen = set(v1)
    return v1 + [r["id"] for r in jl(V2) if r["id"] not in seen and not seen.add(r["id"])]


def state():
    v2 = {r["id"]: r for r in jl(V2)}
    a2 = {a["id"]: a for a in jl(AUDIT2)}
    a1 = {a["id"]: a["after"] for a in br.jl(br.AUDIT)}
    v1 = {r["id"]: r for r in br.jl(br.LABELS)}
    return v2, a2, a1, v1, br.cursor()


EVENT_STEMS = ("captur", "escap", "saved", "save", "rescu", "freed", "kill", "slain", "slew", "murder",
               "defeat", "fought", "fight", "battl", "met", "meet", "arriv", "depart", "sealed", "betray",
               "awak", "reviv", "imprison", "arrest", "kidnap")
STOP = {"was", "were", "had", "has", "have", "been", "being", "the", "and", "with", "from", "for",
        "his", "her", "their", "its", "into", "that", "this", "who", "which", "as", "they", "them",
        "would", "could", "should", "there", "it's", "not", "a", "an", "to", "of", "on", "in", "be"}
TWINS = {"helped": "saved", "assisted": "saved", "protected": "saved", "attacked": "fought",
         "kidnapped": "captured", "dies": "killed"}


def normalize_facts(facts, events, text):
    """Deterministic clean-up of the 35B's fact rows before Claude reads them (2026-10-10).

    Only what a rule can decide: (1) `other_verb` whose object is a phrase -> the quote's own word
    sharing a stem with it (B.3); unresolvable rows stay for review; (2) `other_verb` that is a
    disguised event verb ("captured", "escape") -> dropped: the event layer or a tag owns it;
    (3) a leading "The " on a capitalised end; (4) a fact twin of an event with the same ends
    ("helped" next to "saved", "dies" next to "killed"): B says no twin rows.
    """
    evk = {(e["subject"], e["verb"], e["object"]) for e in events}
    # (5) a composite end "Fitz and Simmons" / "A, B and C" -> one row per named part (A59, B.6)
    split = []
    for f in facts:
        for k in ("subject", "object"):
            v = f.get(k)
            parts = re.split(r",\s*(?:and\s+)?|\s+and\s+", v) if isinstance(v, str) and " and " in v else []
            if len(parts) > 1 and all(p[:1].isupper() for p in parts if p) and all(parts):
                split += [{**f, k: p} for p in parts]
                break
        else:
            split.append(f)
    facts = split
    out = []
    for f in facts:
        f = dict(f)
        for k in ("subject", "object", "asserted_by"):
            v = f.get(k)
            if isinstance(v, str) and v[:4].lower() == "the " and v[4:5].isupper():
                f[k] = v[4:]
            if v in ("null", "None", "none"):
                f[k] = None
        rel, o, q = f.get("relation"), f.get("object"), f.get("quote") or ""
        if rel == "other_verb" and o:
            low = q.lower()
            if o.lower() not in low:
                words = re.findall(r"[A-Za-z']+", q)
                hit = None
                for w in re.findall(r"[A-Za-z']+", o):
                    if len(w) < 3 or w.lower() in STOP:
                        continue
                    stem = w.lower()[:max(4, len(w) - 3)]
                    hit = next((x for x in words if x.lower().startswith(stem)), None)
                    if hit:
                        break
                if hit:
                    f["object"] = hit
            # a literal multi-word phrase ("asked him to turn around") -> its first content word (B.3)
            ws = [w for w in re.findall(r"[A-Za-z'-]+", f["object"]) if w.lower() not in STOP]
            if len(f["object"].split()) >= 2 and ws and ws[0].lower() in low:
                f["object"] = ws[0]
            if any(f["object"].lower().startswith(s) for s in EVENT_STEMS):
                continue
        tw = TWINS.get(rel)
        if tw and (f.get("subject"), tw, o) in evk:
            continue
        if rel == "dies" and any(e["verb"] == "killed" and e["object"] == f.get("subject") for e in events):
            continue
        out.append(f)
    return out


def base(wid, b, v2, a2, a1, v1, c1):
    """(events, facts, tags, events_reviewed, row) for one window."""
    r = v2.get(wid) or v1.get(wid) or {}
    if wid in a2:
        a = a2[wid]
        return a["events"], a["facts"], a["tags"], True, r
    if b <= c1:
        ev, rev = a1.get(wid, (v1.get(wid) or {}).get("events", [])), True
    else:
        ev, rev = r.get("events", []), False
    return ev, normalize_facts(r.get("facts", []) or [], ev, ""), r.get("tags", []) or [], rev, r


def view(n, start):
    ids, (v2, a2, a1, v1, c1), pas = order(), state(), br.passages()
    end = min(start + n, len(ids))
    for b in range(start + 1, end + 1):
        wid = ids[b - 1]
        if wid not in v2 and wid not in a2:
            print(f"===== b{b} [no v2 row yet: stop here]")
            end = b - 1
            break
        ev, fa, tg, rev, r = base(wid, b, v2, a2, a1, v1, c1)
        text = pas[wid]
        print(f"===== b{b} {r.get('page')} / {r.get('section')}")
        print(text[:4000])
        print(" EVENTS" + (" [reviewed]" if rev else ""),
              [(e["subject"], e["verb"], e["object"]) + (() if rev else ((e.get("quote") or "")[:45],))
               for e in ev] or "[]")
        print(" FACTS", [(f.get("subject"), f.get("relation"), f.get("object"),
                          "" if f.get("modality", "actual") == "actual" else f"{f['modality']}/{f.get('asserted_by')}",
                          "" if f.get("certainty", "stated") == "stated" else f["certainty"],
                          (f.get("quote") or "")[:32]) for f in fa] or "[]")
        if tg:
            print(" TAGS", [(t.get("tag"), (t.get("quote") or "")[:40]) for t in tg])
        for k in ("dropped", "fact_dropped", "tag_dropped"):
            if r.get(k) and wid not in a2:
                print(f" {k.upper()}", [(d.get("subject"), d.get("verb") or d.get("relation") or d.get("tag"),
                                         d.get("object"), d.get("why")) for d in r[k]][:8])
        if not rev:
            fl, _ = big_flags.check(ev, text)
            for f in fl:
                print("  " + ("" if f.startswith("MISS?") else "FLAG ") + f)
        ff, _ = fact_gate.check(fa, text, tags=tg)
        for f in ff:
            if "is symmetric" not in f and "object is null" not in f and "sentence boundary" not in f \
                    and "more than one sentence" not in f:
                print("  FFLAG " + f)
        cov = fact_coverage.report(text, ev, fa, tg)
        for s in cov["uncovered"]:
            print("  UNCOVERED " + s[:160])
    print(f"[printed b{start + 1}..b{end} of {len(ids)}; mark with: mark {end}]")


def parse_row(spec, n):
    p = [x.strip() for x in spec.split("|", n - 1)] if n else [x.strip() for x in spec.split("|")]
    return p


def apply_edits(path):
    ids, (v2, a2, a1, v1, c1) = order(), state()
    out, cur = [], None
    for line in open(path):
        line = line.rstrip("\n")
        if not line.strip():
            continue
        if line.startswith("@"):
            head, _, why = line[1:].partition(" ")
            b = int(head)
            wid = ids[b - 1]
            ev, fa, tg, _, _ = base(wid, b, v2, a2, a1, v1, c1)
            cur = {"b": b, "id": wid, "why": why.strip(), "base": (ev, fa, tg), "events": [], "facts": [], "tags": []}
            out.append(cur)
            continue
        op, _, rest = line.strip().partition(" ")
        ev, fa, tg = cur["base"]
        if op in ("keep", "keepe"):
            cur["events"] = [dict(e) for e in ev]
        if op in ("keep", "keepf"):
            cur["facts"], cur["tags"] = [dict(f) for f in fa], [dict(t) for t in tg]
        if op == "r":
            old, new = [x.strip() for x in rest.split("=>")]
            for e in cur["events"]:
                for k in ("subject", "object"):
                    if e.get(k) == old:
                        e[k] = new
            for f in cur["facts"]:
                for k in ("subject", "object", "asserted_by"):
                    if f.get(k) == old:
                        f[k] = new
        elif op == "+":
            s, v, o, q = parse_row(rest, 4)
            cur["events"].append({"quote": q, "subject": s, "verb": v, "object": None if o == "-" else o})
        elif op == "-":
            s, v, o = parse_row(rest, 0)[:3]
            o = None if o == "-" else o
            cur["events"] = [e for e in cur["events"] if (e["subject"], e["verb"], e["object"]) != (s, v, o)]
        elif op == "f+":
            p = parse_row(rest, 0)
            s, rel, o, q = p[:4]
            mod, cert, ab, canon = (p[4:] + ["actual", "stated", "", ""][len(p) - 4:])[:4]
            cur["facts"].append({"quote": q, "subject": s, "relation": rel, "object": None if o == "-" else o,
                                 "modality": mod or "actual", "certainty": cert or "stated",
                                 "asserted_by": ab or None, "canon": canon or None})
        elif op == "f-":
            s, rel, o = parse_row(rest, 0)[:3]
            o = None if o == "-" else o
            cur["facts"] = [f for f in cur["facts"] if (f.get("subject"), f.get("relation"), f.get("object")) != (s, rel, o)]
        elif op == "t+":
            t, q = parse_row(rest, 2)
            cur["tags"].append({"tag": t, "quote": q})
        elif op == "t-":
            p = parse_row(rest, 2)
            cur["tags"] = [t for t in cur["tags"]
                           if not (t.get("tag") == p[0] and (len(p) == 1 or (t.get("quote") or "").startswith(p[1])))]
    for c in out:
        # the gate refuses exact and symmetric duplicates: drop them here (mkfix did the same)
        seen, ev = set(), []
        for e in c["events"]:
            k = (e["verb"], *sorted([e["subject"], e["object"] or ""])) if e["verb"] in SYM else (e["subject"], e["verb"], e["object"])
            if k not in seen:
                seen.add(k)
                ev.append(e)
        c["events"] = ev
        seen, fa = set(), []
        for f in c["facts"]:
            k = (f["subject"], f["relation"], f["object"], f.get("modality"))
            if k not in seen:
                seen.add(k)
                fa.append(f)
        c["facts"] = fa
    return out


def fix(path):
    import importlib.util
    spec = importlib.util.spec_from_file_location("label_single", Path(__file__).resolve().parent / "label_single.py")
    label_single = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(label_single)  # this branch's v2 labeller (fact/tag gates), never main's v1
    import verify_row_wiki as vrw
    pas, wikis = br.passages(), {}
    v2 = {r["id"]: r for r in jl(V2)}
    for c in apply_edits(path):
        r = v2.get(c["id"], {})
        series = r.get("series", "marvel")
        wiki = wikis.setdefault(series, vrw.Wiki(str(ROOT / "series" / series / "facts.db")))
        w = pas[c["id"]]
        ek, ed = label_single.gate([{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in c["events"]], w, wiki)
        fk, fd = label_single.fact_gate_keep(c["facts"], w, wiki)
        tk, td = label_single.tag_gate_keep(c["tags"], w)
        bad = []
        if ed or len(ek) != len(c["events"]):
            bad.append(f"events {[(d.get('subject'), d.get('verb'), d.get('object'), d['why']) for d in ed]} kept {len(ek)}/{len(c['events'])}")
        if fd:
            bad.append(f"facts {[(d.get('subject'), d.get('relation'), d.get('object'), d['why']) for d in fd]}")
        if td:
            bad.append(f"tags {[(d.get('tag'), d['why']) for d in td]}")
        if bad:
            print(f"REFUSED b{c['b']} {c['id']}: " + " | ".join(bad))
            continue
        with open(AUDIT2, "a") as fh:
            fh.write(json.dumps({"id": c["id"], "b": c["b"], "series": series, "page": r.get("page"),
                                 "events": ek, "facts": fk, "tags": tk, "why": c["why"]}, ensure_ascii=False) + "\n")
        print(f"FIXED b{c['b']} (ev {len(ek)} facts {len(fk)} tags {len(tk)})")


def main():
    a = sys.argv[1:]
    if not a or a[0] == "status":
        ids = order()
        print(f"v2 windows {len(ids)} | reviewed (v2 cursor) {cursor2()} | corrected {len({x['id'] for x in jl(AUDIT2)})}")
    elif a[0] == "view":
        start = int(a[a.index("--from") + 1]) if "--from" in a else cursor2()
        view(int(a[1]), start)
    elif a[0] == "fix":
        fix(a[1])
    elif a[0] == "mark":
        # accepted windows are recorded too, so big_audit_v2 alone is the reviewed truth (the shown,
        # normalised rows, gated exactly like a fix; anything the gate drops is reported)
        import tempfile
        ids, (v2, a2, a1, v1, c1) = order(), state()
        lo, hi = cursor2(), int(a[1])
        todo = [b for b in range(lo + 1, hi + 1) if ids[b - 1] not in a2 and ids[b - 1] in v2]
        if todo:
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as fh:
                fh.write("".join(f"@{b} accepted as shown\nkeep\n" for b in todo))
            fix(fh.name)
        CURSOR2.write_text(a[1])
        print(f"v2 reviewed through {a[1]} ({len(todo)} accepted as shown)")


if __name__ == "__main__":
    main()
