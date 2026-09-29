"""Qwen worker: exhaustive, guideline-driven event candidates for gold
annotation (plan/EVENT_ANNOTATION_GUIDELINE.md). Thinking on. Candidates only:
every gold label is adjudicated by a human-level judge afterwards.

    python tools/train/qwen_worker.py --data rows.jsonl --out cand.jsonl [--ids ids.json]

`rows.jsonl` is the export's format (messages[1] is the extractor's user
message). Runs in the engine venv against the Q6 llama.cpp server on :8090 (/tmp/jjk100/serve_q8.sh).
"""
import argparse, json, re, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = (ROOT / "plan" / "EVENT_ANNOTATION_GUIDELINE.md").read_text(encoding="utf-8")
GUIDE = GUIDE[GUIDE.index("## A."):]

SYSTEM = """You are a meticulous annotator. You list EVERY event a fiction-wiki passage states, following the annotation guideline below exactly. Read the whole passage sentence by sentence; do not stop at the first few events. Apply the guideline's "no" column strictly: precision matters as much as completeness.

Allowed verbs (exactly these words): {verbs}

Answer with JSON only, in this shape:
{{"events": [{{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}}]}}
If the passage states no event, answer {{"events": []}}.

GUIDELINE
""" + GUIDE


def parse(text):
    body = (text or "").strip()
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return None
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return None
    ev = d.get("events") if isinstance(d, dict) else None
    return [x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else None


def ask(system, user, url, model, max_tokens, temperature=0.6, effort=None):
    kwargs = {"enable_thinking": True}
    if effort:
        kwargs["reasoning_effort"] = effort
    body = {"model": model, "temperature": temperature, "top_p": 0.95, "max_tokens": max_tokens,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
            "chat_template_kwargs": kwargs}
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            r = json.loads(urllib.request.urlopen(req, timeout=1800).read())
            m = r["choices"][0]["message"]
            ev = parse(m.get("content"))
            if ev is not None:
                return ev, m.get("content"), len(m.get("reasoning_content") or ""), r["choices"][0]["finish_reason"]
        except Exception as err:  # noqa: BLE001
            last = str(err)
    return None, None, 0, "failed"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--verbs", default="fought, defeated, killed, captured, escaped, saved, betrayed, sealed, awakened, met, arrived, departed")
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    ap.add_argument("--temperature", type=float, default=0.6)
    ap.add_argument("--effort", default=None, help="reasoning_effort: xhigh (default) | medium | low")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=14000)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.data)]
    if a.ids:
        want = set(json.load(open(a.ids)))
        rows = [r for r in rows if r["id"] in want]
    done = set()
    if Path(a.out).exists():
        # only a window that succeeded is done: a failed one (server crash,
        # 2026-09-29 CUDA watchdog timeout) is retried; readers keep its last line
        done = {r["id"] for r in map(json.loads, open(a.out)) if r.get("ok")}
    rows = [r for r in rows if r["id"] not in done]
    system = SYSTEM.format(verbs=a.verbs)

    def job(r):
        ev, raw, rlen, fin = ask(system, r["messages"][1]["content"], a.url, a.model, a.max_tokens,
                                 a.temperature, a.effort)
        return {"id": r["id"], "events": ev if ev is not None else [], "ok": ev is not None,
                "finish": fin, "reasoning_chars": rlen}

    with ThreadPoolExecutor(a.workers) as pool, open(a.out, "a") as f:
        for n, res in enumerate(pool.map(job, rows), 1):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            if n % 25 == 0:
                print(f"{n}/{len(rows)}", flush=True)
    print("done", len(rows))


if __name__ == "__main__":
    sys.exit(main())
