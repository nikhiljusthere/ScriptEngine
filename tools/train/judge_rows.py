"""Judge B: a second, independent judge of extracted event rows under
plan/EVENT_ANNOTATION_GUIDELINE.md (Qwen Q6, thinking on). Sees exactly the
context judge A saw. Writes {"key", "verdict": 1|0|null, "reason"} per row.

    python tools/train/judge_rows.py --sheet reports/jjk/judged/final_p9_150.json --out judgeB.jsonl
"""
import argparse, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = (ROOT / "plan" / "EVENT_ANNOTATION_GUIDELINE.md").read_text(encoding="utf-8")
GUIDE = GUIDE[GUIDE.index("## A."):]
SYSTEM = """You judge one extracted event row against the passage excerpt it was read from, under the annotation guideline below. The row is correct only if ALL hold: the excerpt states the event (not a plan, attempt, hypothetical or negation); the verb is right under the guideline table; the direction is right (subject is the doer); both ends are the right, named entities (a generic class, a technique or an item as an end is wrong; resolve pronouns only where the excerpt makes them clear). Canonical names given in brackets are the wiki page each end was filed under: a wrong page is a wrong row.

Answer with JSON only: {"verdict": "yes" or "no", "reason": "<one short sentence>"}

GUIDELINE
""" + GUIDE


def rows_of(sheet):
    data = json.load(open(sheet))
    out = []
    for i, x in enumerate(data):
        if "context" in x:
            ctx = x["context"]
        else:
            ctx = f'{x["pre"]}<<{x["quote"]}>>{x["post"]}'
        out.append((str(i), x, ctx))
    return out


def ask(url, model, user, effort):
    kwargs = {"enable_thinking": True}
    if effort:
        kwargs["reasoning_effort"] = effort
    body = {"model": model, "temperature": 0.6, "top_p": 0.95, "max_tokens": budget,
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
            "chat_template_kwargs": kwargs}
    # Budget escalates on retry: this model reasons by default and returns
    # EMPTY content with finish_reason=length when the budget is too small.
    # Empty is never a verdict here -- the parse raises, and a row that never
    # answers stays None, which downstream carries as a third state.
    for budget in (8000, 20480, 20480):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=1800).read())["choices"][0]["message"]
            t = (m.get("content") or "").strip()
            s, e = t.find("{"), t.rfind("}")
            d = json.loads(t[s:e + 1])
            v = str(d.get("verdict", "")).lower()
            if v in ("yes", "no"):
                return (1 if v == "yes" else 0), d.get("reason", "")
        except Exception:  # noqa: BLE001
            pass
    return None, "unanswered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--effort", default=None)
    a = ap.parse_args()
    done = set()
    if Path(a.out).exists():
        done = {json.loads(l)["key"] for l in open(a.out)}
    todo = [r for r in rows_of(a.sheet) if r[0] not in done]

    def job(r):
        key, x, ctx = r
        sub = x.get("subject_node") or x.get("subject")
        obj = x.get("object_node") or x.get("object")
        user = (f'Page: {x["page"]}\n\nExcerpt (the quote is marked << >>):\n{ctx}\n\n'
                f'Row: SUBJECT=[{sub}] VERB={x["verb"]} OBJECT=[{obj}]\nQuote: "{x["quote"]}"\n\n'
                "Is this row correct under the guideline?")
        v, why = ask(a.url, a.model, user, a.effort)
        return {"key": key, "verdict": v, "reason": why}

    with ThreadPoolExecutor(a.workers) as pool, open(a.out, "a") as f:
        for res in pool.map(job, todo):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
    print("done", len(todo))


if __name__ == "__main__":
    sys.exit(main())
