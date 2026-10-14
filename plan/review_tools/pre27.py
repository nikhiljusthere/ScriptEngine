#!/usr/bin/env python3
"""27B pre-review for the lint reading pass (2026-10-14, owner: "Use 27B ... You will have to review their answers
anyways"). The 27B gets the lint rules + catalog section A as a cached system prompt and one window per request
(text, every row with its full quote, the LINT classes) and answers with one `rv.sh fix` edit block. Nothing is
submitted from here: Claude reads each window and each answer (`show`) and writes the corrected edit file.

    pre27.sh run LISTFILE [--workers 2] [--url URL]   -> big/lint/pre27/b<n>.txt (skips existing)
    pre27.sh show B [B ...]                           -> window + rows + LINT + the 27B answer
    pre27.sh next LISTFILE [N]                        -> show the next N answered, unreviewed windows
"""
import concurrent.futures as cf
import json
import re
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lint_work  # noqa: E402

bv = lint_work.bv
OUT = bv.BIG / "lint" / "pre27"
URL = "http://127.0.0.1:18080/v1/chat/completions"


def system_prompt():
    cat = (HERE.parent / "BIG_REVIEW_PATTERNS.md").read_text().split("\n")
    a, z = next(i for i, l in enumerate(cat) if l.startswith("## A.")), next(i for i, l in enumerate(cat) if l.startswith("## C."))
    return (HERE / "lint27_system.md").read_text() + "\n".join(cat[a:z]) + "\n"


def rows(rec):
    out = []
    for e in rec.get("events", []):
        out.append(f"E {e['subject']}|{e['verb']}|{e['object'] or '-'}|{e.get('quote') or ''}")
    for f in rec.get("facts", []):
        mod, cert, ab = f.get("modality") or "actual", f.get("certainty") or "stated", f.get("asserted_by") or ""
        tail = "" if (mod, cert, ab) == ("actual", "stated", "") else f"|{mod}|{cert}|{ab or '-'}"
        out.append(f"F {f.get('subject')}|{f.get('relation')}|{f.get('object') or '-'}|{f.get('quote') or ''}{tail}")
    for t in rec.get("tags", []):
        out.append(f"T {t.get('tag')}|{t.get('quote') or ''}")
    return out


_CACHE = {}


def ctx():
    if not _CACHE:
        _CACHE["ids"], _CACHE["a2"], _CACHE["pas"] = bv.order(), bv.audit2(), bv.br.passages()
    return _CACHE["ids"], _CACHE["a2"], _CACHE["pas"]


def render(b, full_quotes=True):
    ids, a2, pas = ctx()
    wid = ids[b - 1]
    rec, text = a2[wid], pas[wid]
    lint = lint_work.window_classes(b, rec, text)
    head = f"===== b{b} {rec.get('page')}"
    body = [head, text, "ROWS:"] + ["  " + r for r in rows(rec)]
    body += [f"LINT {k}: {v}" for k, v in lint.items()] or ["LINT (none: overlap partner of a flagged window)"]
    return "\n".join(body)


def ask(sysmsg, user, url, model):
    body = {"model": model, "temperature": 0.6, "top_p": 0.95, "max_tokens": 24000,  # the 27B thinks by default (it refuses chat_template_kwargs)
            "messages": [{"role": "system", "content": [{"type": "text", "text": sysmsg,
                                                         "prompt_cache_breakpoint": {"mode": "explicit"}}]},
                         {"role": "user", "content": user}]}
    req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
    m = json.loads(urllib.request.urlopen(req, timeout=3600).read())["choices"][0]["message"]
    return m.get("content") or ""


def run(listfile, workers, url):
    OUT.mkdir(parents=True, exist_ok=True)
    bs = [int(m) for m in re.findall(r"^b(\d+)", Path(listfile).read_text(), re.M)]
    todo = [b for b in bs if not (OUT / f"b{b}.txt").exists()]
    model = json.loads(urllib.request.urlopen(url.replace("/chat/completions", "/models")).read())["data"][0]["id"]
    sysmsg = system_prompt()
    print(f"todo {len(todo)} of {len(bs)}; model {model}", flush=True)

    def one(b):
        for _ in range(3):  # an empty answer (thinking ran past max_tokens) is retried (b13, 2026-10-14)
            ans = ask(sysmsg, render(b) + f"\n\nAnswer with the edit block for b{b}.", url, model)
            ans = re.sub(r"<think>.*?</think>", "", ans, flags=re.S).strip()
            if "@" in ans:
                break
        (OUT / f"b{b}.txt").write_text(ans + "\n")
        return b
    n = 0
    with cf.ThreadPoolExecutor(workers) as ex:
        for b in ex.map(one, todo):
            n += 1
            print(f"done b{b} ({n}/{len(todo)})", flush=True)


def reviewed():
    """b's Claude has decided: an @-block in big/lint/fixes/*.txt or a line in big/lint/ok.txt (no change)."""
    done = set()
    for p in (bv.BIG / "lint" / "fixes").glob("*.txt"):
        done |= {int(m) for m in re.findall(r"^@(\d+)", p.read_text(), re.M)}
    ok = bv.BIG / "lint" / "ok.txt"
    if ok.exists():
        done |= {int(m) for m in re.findall(r"\d+", ok.read_text())}
    return done


def nxt(listfile, n):
    """The next n windows of LISTFILE (in order) that have a 27B answer and are not reviewed yet."""
    bs = [int(m) for m in re.findall(r"^b(\d+)", Path(listfile).read_text(), re.M)]
    done = reviewed()
    todo = [b for b in bs if b not in done]
    ready = [b for b in todo if (OUT / f"b{b}.txt").exists()]
    print(f"# reviewed {len(bs) - len(todo)}/{len(bs)}; answered and waiting {len(ready)}")
    show(ready[:n])


def show(bs):
    for b in bs:
        print(render(b))
        p = OUT / f"b{b}.txt"
        print("--- 27B:")
        print(p.read_text().strip() if p.exists() else "(no answer yet)")
        print()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "run":
        run(a[1], int(a[a.index("--workers") + 1]) if "--workers" in a else 2,
            a[a.index("--url") + 1] if "--url" in a else URL)
    elif a[0] == "next":
        nxt(a[1], int(a[2]) if len(a) > 2 else 10)
    else:
        show([int(x.lstrip("b")) for x in a[1:]])
