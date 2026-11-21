"""Gold adjudication helpers.

render: print windows with numbered candidates (union of Q6 worker + teacher
        target, deduped) for a judge to adjudicate.
build:  validate adjudicated gold (verbatim quotes via the store's own
        `quoted_in`, legal verbs, null object only for `awakened`) and write
        training records in the export's shape.

    python tools/train/gold_tools.py render --data train.jsonl --cand cand.jsonl --ids ids.json --start 0 --n 20
    python tools/train/gold_tools.py build --data train.jsonl --cand cand.jsonl --gold gold_dir --out gold.jsonl
    python tools/train/gold_tools.py silver --data train.jsonl --cand q6.jsonl --gold-jsonl gold.jsonl --out silver_v2.jsonl
silver: the student's warm-up set -- every train window labelled by the Q6 worker,
        gold windows taken from the adjudicated gold instead. A window whose rows
        cannot all be validated is dropped whole: dropping one row would teach
        the student to omit it.
Gold file (JSON): {"<window id>": [ "c3", ["quote","subject","verb","object|null"], ... ], ...}
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scriptengine.ingest.verbatim import quoted_in  # noqa: E402

VERBS = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "awakened", "met", "arrived", "departed"}


_QUOTES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'})


def repair_quote(q, text):
    """The passage's own span for a quote that differs only in apostrophe or
    quote-mark style (a model writes ' for the wiki's \u2019). The stored quote
    is always the passage's characters, never the model's."""
    nq, nt = q.strip().translate(_QUOTES), text.translate(_QUOTES)
    at = nt.find(nq)
    if at < 0 or len(nt) != len(text):
        return None
    span = text[at:at + len(nq)]
    return span if quoted_in(span, text) else None


def key(e):
    return ((e.get("subject") or "").strip().lower(), (e.get("verb") or "").strip().lower(),
            (e.get("object") or "").strip().lower() if e.get("object") else None)


def candidates(row, cand, teacher_rows=True):
    teacher = json.loads(row["messages"][2]["content"])["events"] if teacher_rows else []
    worker = cand.get(row["id"], [])
    out, seen = [], set()
    for src, evs in (("W", worker), ("T", teacher)):
        for e in evs:
            k = key(e)
            if k in seen:
                for o in out:
                    if key(o) == k:
                        o["src"] += src
                continue
            seen.add(k)
            out.append({**e, "src": src})
    return out


def passage(row):
    return row["messages"][1]["content"].split("Passage:\n", 1)[1]


def load(a):
    rows = {json.loads(l)["id"]: json.loads(l) for l in open(a.data)}
    cand = {}
    if a.cand:
        for c in a.cand:
            for l in open(c):
                r = json.loads(l)
                if r.get("ok", True):
                    cand[r["id"]] = r["events"]
    return rows, cand


def render(a):
    rows, cand = load(a)
    ids = json.load(open(a.ids))[a.start:a.start + a.n]
    ver = {}  # verdicts keyed by the row itself: the verifier numbered the draft file, not this union
    for vf in a.verify or []:
        for l in open(vf):
            v = json.loads(l)
            src = cand.get(v["id"], [])
            ver[v["id"]] = {key(src[x["n"]]): x for x in v["rows"] if x["n"] < len(src)}
    for n, i in enumerate(ids, a.start):
        r = rows[i]
        print(f"##### G{n} id={i} [{r['page']} / {r['section']}]")
        print(passage(r))
        for j, c in enumerate(candidates(r, cand, not a.no_teacher)):
            v = ver.get(i, {}).get(key(c))
            tag = "" if v is None else f"  <<Q6 {'YES' if v['ok'] == 1 else 'NO' if v['ok'] == 0 else '??'}: {v['rule'][:140]}" + (f" FLAGS {v['flags']}" if v.get("flags") else "") + ">>"
            print(f"  c{j} [{c['src']}] {c.get('subject')} ={c.get('verb')}=> {c.get('object')} | {c.get('quote')}{tag}")
        print()


def build(a):
    rows, cand = load(a)
    gold = {}
    for f in sorted(Path(a.gold).glob(a.glob)):
        gold.update(json.load(open(f)))
    out, problems = [], []
    for i, items in gold.items():
        r = rows[i]
        cs = candidates(r, cand, not a.no_teacher)
        text = passage(r)
        events = []
        for it in items:
            if isinstance(it, str):
                c = cs[int(it[1:])]
                q, s, v, o = c.get("quote"), c.get("subject"), c.get("verb"), c.get("object")
            else:
                q, s, v, o = it
            v = (v or "").lower()
            if v == "awakened":
                o = None
            if v not in VERBS or not s or (o is None and v != "awakened"):
                problems.append((i, "shape", it)); continue
            if not quoted_in(q or "", text):
                fixed = repair_quote(q or "", text)
                if fixed is None:
                    problems.append((i, "quote", q)); continue
                q = fixed
            events.append({"quote": q, "subject": s, "verb": v, "object": o})
        rec = dict(r)
        rec["tier"] = "gold"
        rec["messages"] = r["messages"][:2] + [{"role": "assistant", "content": json.dumps({"events": events}, ensure_ascii=False)}]
        out.append(rec)
    with open(a.out, "w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps({"windows": len(out), "events": sum(len(json.loads(r["messages"][2]["content"])["events"]) for r in out), "problems": len(problems)}))
    for p in problems:
        print("PROBLEM", p)


def check(e, text):
    """One row validated as `build` does; the row with its passage-exact quote, or None."""
    q, s, v, o = e.get("quote") or "", e.get("subject"), (e.get("verb") or "").lower(), e.get("object")
    if v == "awakened":
        o = None
    if v not in VERBS or not s or (o is None and v != "awakened"):
        return None
    if not quoted_in(q, text):
        q = repair_quote(q, text)
        if q is None:
            return None
    return {"quote": q, "subject": s, "verb": v, "object": o}


def silver(a):
    rows, _ = load(a)
    gold = {json.loads(l)["id"]: json.loads(l) for l in open(a.gold_jsonl)}
    q6 = {}
    for c in a.cand:
        for l in open(c):
            r = json.loads(l)
            q6[r["id"]] = r
    out, stat = [], {"gold": 0, "q6": 0, "q6_failed": 0, "bad_row_window": 0, "unlabelled": 0}
    for i, r in rows.items():
        if i in gold:
            out.append(gold[i]); stat["gold"] += 1; continue
        c = q6.get(i)
        if c is None:
            stat["unlabelled"] += 1; continue
        if not c.get("ok"):
            stat["q6_failed"] += 1; continue
        text = passage(r)
        events = [check(e, text) for e in c["events"]]
        if any(e is None for e in events):
            stat["bad_row_window"] += 1; continue
        rec = dict(r)
        rec["tier"] = "silver_q6"
        rec["messages"] = r["messages"][:2] + [{"role": "assistant", "content": json.dumps({"events": events}, ensure_ascii=False)}]
        out.append(rec); stat["q6"] += 1
    with open(a.out, "w") as f:
        for rec in out:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    stat["written"] = len(out)
    print(json.dumps(stat))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["render", "build", "silver"])
    ap.add_argument("--gold-jsonl")
    ap.add_argument("--no-teacher", action="store_true", help="number only the --cand rows (review of drafts)")
    ap.add_argument("--verify", nargs="*", help="row-by-row verifier output to show beside each row")
    ap.add_argument("--glob", default="gold_*.json", help="adjudication files to build from")
    ap.add_argument("--data", required=True)
    ap.add_argument("--cand", nargs="*")
    ap.add_argument("--ids")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--gold")
    ap.add_argument("--out")
    a = ap.parse_args()
    {"render": render, "build": build, "silver": silver}[a.cmd](a)


if __name__ == "__main__":
    main()
