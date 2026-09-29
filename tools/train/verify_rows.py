"""Verifier pass: a second, independent Q6 reading of each window's extracted rows
(owner 2026-09-29: Q6 extracts, Q6 verifies, and only verified data trains the
student). Thinking on. Per window the verifier sees the passage and the numbered
rows, rules on every row under plan/EVENT_ANNOTATION_GUIDELINE.md, and lists
events the extraction missed. It never edits a row: disagreements go to the
adjudicator.

    python tools/train/verify_rows.py --data train.jsonl --cand cand.jsonl --out verify.jsonl [--ids ids.json]

Output per window: {"id", "verdicts": [{"n", "ok": 1|0, "rule"}], "missed": [event...], "ok": bool}
"""
import argparse, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = (ROOT / "plan" / "EVENT_ANNOTATION_GUIDELINE.md").read_text(encoding="utf-8")
GUIDE = GUIDE[GUIDE.index("## A."):]

SYSTEM = """You are a strict verifier of event rows extracted from a fiction-wiki passage, under the annotation guideline below. Another annotator produced the rows; assume nothing they wrote is right until the passage proves it.

A row is correct only if ALL hold:
1. the quote is copied from the passage and states the event (not a plan, attempt, hypothetical, claim that turns out false, or negation);
2. the verb is right under the guideline table, including its "no" column;
3. the direction is right: the subject is the doer;
4. both ends are named entities the guideline allows (never a generic class, unnamed people, a technique, a domain or an item), and pronouns resolve only where the passage makes them unambiguous;
5. it is not a duplicate of another row (fought/met are symmetric: one row per pair).

Then list every event the passage states that the rows miss, in the same shape.

Answer with JSON only:
{"verdicts": [{"n": <row number>, "ok": "yes" or "no", "rule": "<the rule or guideline line that decides it, one short sentence>"}],
 "missed": [{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}]}
Give one verdict for every row number. If there are no rows, answer with an empty verdicts list.

GUIDELINE
""" + GUIDE


def passage(row):
    return row["messages"][1]["content"].split("Passage:\n", 1)[1]


def user_msg(row, events):
    lines = [f'{n}. {e.get("subject")} ={e.get("verb")}=> {e.get("object")} | quote: "{e.get("quote")}"'
             for n, e in enumerate(events)]
    return "Passage:\n" + passage(row) + "\n\nExtracted rows:\n" + ("\n".join(lines) or "(none)")


def ask(url, model, user, effort, n_rows):
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
    for budget in (14000, 20480, 20480):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=3600).read())["choices"][0]["message"]
            t = re.sub(r"^```[a-z]*\n?|\n?```$", "", (m.get("content") or "").strip()).strip()
            d = json.loads(t[t.find("{"):t.rfind("}") + 1])
            verdicts = []
            for v in d.get("verdicts") or []:
                ok = str(v.get("ok", "")).lower()
                if ok in ("yes", "no"):
                    verdicts.append({"n": int(v["n"]), "ok": 1 if ok == "yes" else 0, "rule": v.get("rule", "")})
            # a verdict for every row, or the answer is incomplete and asked again
            if sorted(v["n"] for v in verdicts) == list(range(n_rows)):
                return verdicts, [e for e in d.get("missed") or [] if isinstance(e, dict)]
        except Exception:  # noqa: BLE001
            pass
    return None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--cand", required=True, nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    rows = {json.loads(l)["id"]: json.loads(l) for l in open(a.data)}
    cand = {}
    for c in a.cand:
        for l in open(c):
            r = json.loads(l)
            if r.get("ok"):
                cand[r["id"]] = r["events"]
    want = [i for i in (json.load(open(a.ids)) if a.ids else cand) if i in cand and i in rows]
    done = set()
    if Path(a.out).exists():
        # only a window that succeeded is done: a failed one (server crash,
        # 2026-09-29 CUDA watchdog timeout) is retried; readers keep its last line
        done = {r["id"] for r in map(json.loads, open(a.out)) if r.get("ok")}
    want = [i for i in want if i not in done]

    def job(i):
        v, missed = ask(a.url, a.model, user_msg(rows[i], cand[i]), a.effort, len(cand[i]))
        return {"id": i, "verdicts": v or [], "missed": missed or [], "ok": v is not None}

    with ThreadPoolExecutor(a.workers) as pool, open(a.out, "a") as f:
        for n, res in enumerate(pool.map(job, want), 1):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            if n % 25 == 0:
                print(f"{n}/{len(want)}", flush=True)
    print("done", len(want))


if __name__ == "__main__":
    sys.exit(main())
