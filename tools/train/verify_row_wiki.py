"""Row-by-row verifier with wiki evidence (owner 2026-09-29: Q6 extracts every
window from scratch, then the same Q6 checks every row one at a time against the
passage AND the wiki's own data). Thinking on.

For each row the verifier sees the passage, the row, the window's other rows (for
duplicates), and an evidence card read from the series store: the wiki page each
end resolves to (page type, infobox status and race) and every battle page whose
sides name both ends, with its outcome. The card is background: a row must still
be stated by the passage, but a "killed" row whose object the wiki lists as Alive,
or an end that resolves to a technique page, is caught here.

    python tools/train/verify_row_wiki.py --series jjk --data train.jsonl --cand cand.jsonl --out out.jsonl [--ids ids.json]

Output per window: {"id", "rows": [{"n", "ok": 1|0|null, "rule", "card"}], "ok": bool}
"""
import argparse, json, re, sqlite3, sys, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GUIDE = (ROOT / "plan" / "EVENT_ANNOTATION_GUIDELINE.md").read_text(encoding="utf-8")
GUIDE = GUIDE[GUIDE.index("## A."):]

SYSTEM = """You check ONE event row extracted from a fiction-wiki passage, under the annotation guideline below. Assume nothing about the row is right until the passage proves it.

The row is correct only if ALL hold:
1. the passage states the event happened (not a plan, attempt, hypothetical, false claim or negation);
2. the verb is right under the guideline table, including its "no" column;
3. the direction is right: the subject is the doer;
4. both ends are named entities the guideline allows (never a generic class, unnamed people, a technique, a domain or an item); pronouns resolve only where the passage makes them unambiguous;
5. it is not a duplicate of one of the other rows listed (fought and met are symmetric: one row per pair).

WIKI EVIDENCE is read from the wiki's own pages. Use it to check that each end is the right kind of thing (a character page, not a technique or chapter page) and that the row does not contradict the wiki (a "killed" row whose object the wiki lists as Alive is wrong unless the passage itself states the death). A `status (end of series)` fact is the character's state at the end of the series, not at the passage's moment: an early-story row about a character who is later Deceased does not contradict it. The evidence never makes a row correct on its own: the passage must state it. WIKI FLAGS are warnings, not verdicts: a "species" page is a class (never an end); this wiki files named shikigami (Mahoraga, Nue, Moon Dregs) under technique pages, and a named shikigami IS an allowed end, while an attack, technique or domain is not.

Answer with JSON only: {"ok": "yes" or "no", "rule": "<the rule or guideline line that decides it, one short sentence>"}

GUIDELINE
""" + GUIDE

BAD_END = {"technique", "species", "item", "chapter", "episode", "volume", "music", "blu_ray_dvd", "game",
           "novel", "anime", "series", "stage_play", "story_arcs"}


class Wiki:
    def __init__(self, db):
        c = sqlite3.connect(db)
        self.label = dict(c.execute("select name, label from nodes"))
        self.by = {}
        for n in self.label:
            self.by.setdefault(n.lower(), set()).add(n)
        for a, n in c.execute("select a.alias, n.name from aliases a join nodes n on n.id = a.node_id"):
            self.by.setdefault(a.lower(), set()).add(n)
        self.facts = {}
        for n, k, v in c.execute("select n.name, f.key, f.value from facts f join nodes n on n.id = f.node_id "
                                 "where f.key in ('status','race','outcome','side1','side2')"):
            self.facts.setdefault(n, {})[k] = v
        self.battles = [(n, f) for n, f in self.facts.items() if self.label.get(n) == "battle" and "side1" in f]

    def resolve(self, name):
        if not name:
            return []
        key = name.strip().lower()
        if key in self.by:
            return sorted(self.by[key])
        words = set(re.findall(r"[a-z0-9'-]+", key))
        hits = [n for n in self.label if words and words <= set(re.findall(r"[a-z0-9'-]+", n.lower()))
                # a partial name never lands on a page ABOUT the entity (the "Yasohachi
                # Bridge Curse" row resolved to the battle page naming it, 2026-09-29)
                and self.label[n] not in ("chapter", "episode", "volume", "battle", "event",
                                          "story_arcs", "character_synopsis")]
        return sorted(hits, key=lambda n: (self.label[n] != "character", len(n)))[:3]

    def describe(self, name):
        pages = self.resolve(name)
        if not pages:
            return f'"{name}": no wiki page found', None
        out = []
        for p in pages:
            f = self.facts.get(p, {})
            # The infobox `status` is the character's END-OF-SERIES state
            # ("Deceased" for a killer of an early-story row). The card
            # must not assert it as the state at the passage's moment
            # (council correction #3, 2026-09-30): label it end-of-series
            # so the cross-check ("a killed row whose object the wiki
            # lists as Alive") keeps working without contaminating
            # early-story context. The chapter-scoped
            # status-as-of-chapter-N lookup is the separate track.
            # `race` is time-invariant and stays unscoped.
            extra = "; ".join(
                f"{'status (end of series)' if k == 'status' else k} {f[k]}"
                for k in ("status", "race") if k in f
            )
            out.append(f"{p} ({self.label[p]}{'; ' + extra if extra else ''})")
        bad = self.label[pages[0]] if len(pages) == 1 and self.label[pages[0]] in BAD_END else None
        return f'"{name}" -> ' + " | ".join(out), bad

    def battles_of(self, a, b):
        ka = {w for x in self.resolve(a)[:1] for w in x.lower().split() if len(w) > 2}
        kb = {w for x in self.resolve(b)[:1] for w in x.lower().split() if len(w) > 2}
        if not ka or not kb:
            return []
        out = []
        for n, f in self.battles:
            s1, s2 = f.get("side1", "").lower(), f.get("side2", "").lower()
            if (ka & set(s1.split()) and kb & set(s2.split())) or (kb & set(s1.split()) and ka & set(s2.split())):
                out.append(f'battle page "{n}": outcome: {f.get("outcome", "?")}')
        return out[:3]

    def card(self, e):
        lines, flags = [], []
        d, bad = self.describe(e.get("subject"))
        lines.append("subject " + d)
        if bad:
            flags.append(f"subject is a {bad} page")
        if e.get("object") is not None:
            d, bad = self.describe(e.get("object"))
            lines.append("object " + d)
            if bad:
                flags.append(f"object is a {bad} page")
            lines += self.battles_of(e.get("subject"), e.get("object"))
        return "\n".join(lines), flags


def passage(row):
    return row["messages"][1]["content"].split("Passage:\n", 1)[1]


def fmt(e):
    return f'{e.get("subject")} ={e.get("verb")}=> {e.get("object")} | quote: "{e.get("quote")}"'


def ask(url, model, user, effort):
    kwargs = {"enable_thinking": True}
    if effort:
        kwargs["reasoning_effort"] = effort
    # The answer budget ESCALATES on retry (2026-09-30, Qwen3.6-35B-A3B). This
    # model reasons by default and will spend a small budget entirely on
    # reasoning, then return empty content with finish_reason=length. Measured:
    # a one-sentence question came back empty at 2,048 tokens (1,142 spent on
    # reasoning) and correct at 20,480.
    #
    # An empty reply is NOT a rejection, and never becomes one: the parse below
    # raises on it, the loop retries, and a row that never answers stays `None`
    # ("unanswered") -- a third state that downstream code carries separately and
    # never trains on. Retrying at the SAME budget just burns the same wall
    # clock again, so the retries get more room.
    for budget in (10000, 20480, 20480):
        body = {"model": model, "temperature": 0.6, "top_p": 0.95, "max_tokens": budget,
                "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}],
                "chat_template_kwargs": kwargs}
        try:
            req = urllib.request.Request(url, json.dumps(body).encode(), {"Content-Type": "application/json"})
            m = json.loads(urllib.request.urlopen(req, timeout=3600).read())["choices"][0]["message"]
            t = (m.get("content") or "").strip()
            d = json.loads(t[t.find("{"):t.rfind("}") + 1])
            ok = str(d.get("ok", "")).lower()
            if ok in ("yes", "no"):
                return (1 if ok == "yes" else 0), d.get("rule", "")
        except Exception:  # noqa: BLE001
            pass
    return None, "unanswered"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--data", required=True)
    ap.add_argument("--cand", required=True, nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--url", default="http://127.0.0.1:18081/v1/chat/completions")
    ap.add_argument("--model", default="qwen3.6-35b-a3b-ninfer")
    ap.add_argument("--effort", default="medium")
    ap.add_argument("--workers", type=int, default=3)
    a = ap.parse_args()
    wiki = Wiki(ROOT / "series" / a.series / "facts.db")
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

    def twin_of(evs, n):
        """The earlier row this one duplicates: same (s, v, o), or the reverse of a
        symmetric pair. Checked one at a time, each twin saw the other and rejected
        itself, losing the event (2026-09-29 pilot), so duplicates are settled here."""
        s, v, o = [(evs[n].get(k) or "").strip().lower() for k in ("subject", "verb", "object")]
        for m in range(n):
            s2, v2, o2 = [(evs[m].get(k) or "").strip().lower() for k in ("subject", "verb", "object")]
            if v2 == v and ((s2, o2) == (s, o) or (v in ("fought", "met") and (s2, o2) == (o, s))):
                return m
        return None

    def job(i):
        evs, out = cand[i], []
        dup = {n: twin_of(evs, n) for n in range(len(evs))}
        for n, e in enumerate(evs):
            card, flags = wiki.card(e)
            if dup[n] is not None:
                out.append({"n": n, "ok": 0, "rule": f"duplicate of row {dup[n]} (one row per pair), dropped mechanically",
                            "card": card, "flags": flags})
                continue
            others = "\n".join(f"- {fmt(x)}" for m, x in enumerate(evs) if m != n and dup[m] is None) or "(none)"
            user = (f"Passage:\n{passage(rows[i])}\n\nROW TO CHECK:\n{fmt(e)}\n\nOther rows from this passage:\n{others}"
                    f"\n\nWIKI EVIDENCE:\n{card}" + (f"\nWIKI FLAGS: {'; '.join(flags)}" if flags else ""))
            ok, rule = ask(a.url, a.model, user, a.effort)
            out.append({"n": n, "ok": ok, "rule": rule, "card": card, "flags": flags})
        return {"id": i, "rows": out, "ok": all(r["ok"] is not None for r in out)}

    with ThreadPoolExecutor(a.workers) as pool, open(a.out, "a") as f:
        for n, res in enumerate(pool.map(job, want), 1):
            f.write(json.dumps(res, ensure_ascii=False) + "\n"); f.flush()
            if n % 25 == 0:
                print(f"{n}/{len(want)}", flush=True)
    print("done", len(want))


if __name__ == "__main__":
    sys.exit(main())
