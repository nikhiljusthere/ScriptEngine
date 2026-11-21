#!/usr/bin/env python3
"""Two things over a per-line training file whose rows still carry the v2 gold (events, facts, tags):
(1) the project's own gate flags and uncovered sentences on the gold rows, counted by rule;
(2) what the per-line target does to that gold: acts that are plans or claims classed as events, events
    that lose an end, triples with a missing object, fragments treated as sentences.

    <venv python> labels_and_structure.py --tools <repo>/tools FILE.jsonl [--ids-out flagged.json]
"""
import argparse, collections, json, re, sys

ap = argparse.ArgumentParser()
ap.add_argument("--tools", required=True); ap.add_argument("file"); ap.add_argument("--ids-out"); ap.add_argument("--examples", type=int, default=2)
a = ap.parse_args()
sys.path.insert(0, a.tools); sys.path.insert(0, a.tools + "/train")
import fact_gate, fact_coverage, score_layers_v2 as sl  # noqa: E402

GROUP = {r: g for g, rels in sl.GROUPS.items() for r in rels}
rows = [json.loads(l) for l in open(a.file)]
F = collections.Counter(); ex = collections.defaultdict(list); flagged = collections.defaultdict(list)
S = collections.Counter()


def code(flag):
    m = re.search(r"\((A\d+|B\.\d|R\d+|G\.\d)\)", flag)
    if m: return m.group(1)
    for k in ("sentence boundary", "more than one sentence", "is symmetric", "object is null", "verbatim", "crowd", "pronoun"):
        if k in flag: return k
    return re.sub(r"'[^']*'", "'..'", flag.split(":", 1)[-1].strip())[:60]


for r in rows:
    text, ev, fa, tg = r["passage"], r["events"], r["facts"], r["tags"]
    flags, _ = fact_gate.check(fa, text, tags=tg)
    for f in flags:
        c = code(f); F[c] += 1; flagged[r["id"]].append(c)
        if len(ex[c]) < a.examples: ex[c].append(f"[{r['series']}] {r['page']}: {f[:150]}")
    unc = fact_coverage.report(text, ev, fa, tg)["uncovered"]
    for s in unc:
        F["UNCOVERED sentence"] += 1; flagged[r["id"]].append("UNCOVERED")
        if len(ex["UNCOVERED sentence"]) < a.examples: ex["UNCOVERED sentence"].append(f"[{r['series']}] {r['page']}: {s[:130]}")
    # ---- structure
    cands = r["candidates"]; lines = r["target"]["lines"]; sents = fact_gate.sentences(text)
    S["windows"] += 1; S["lines"] += len(lines); S["gold events"] += len(ev); S["gold facts"] += len(fa)
    S["target event triples"] += sum(len(l["events"]) for l in lines)
    on = lambda q, s: bool((q or "").strip()) and ((q or "").strip() in s or s in (q or "").strip())
    for l, s in zip(lines, sents):
        e_on = [e for e in ev if on(e.get("quote"), s)]
        f_on = [f for f in fa if on(f.get("quote"), s)]
        t_on = {t.get("tag") for t in tg if on(t.get("quote"), s)}
        S["class " + l["class"]] += 1
        if len(s.strip()) < 12: S["lines under 12 characters"] += 1
        if l["class"] == "event":
            if not l["people"]: S["event lines with nobody"] += 1
            act = [f for f in f_on if GROUP.get(f.get("relation")) in ("interaction", "knowledge", "other_verb") or f.get("relation") in ("dies", "wounded", "healed", "kidnapped", "born", "transformed_into", "gained_power", "lost_power")]
            if not e_on and not ({"crowd_end", "no_doer"} & t_on) and act and all((f.get("modality") or "actual") != "actual" for f in act):
                S["event lines whose only acts are plans, attempts, orders or claims"] += 1
                if len(ex["plan-as-event"]) < 3: ex["plan-as-event"].append(f"[{r['series']}] {s[:150]}")
            if not e_on and not act and ({"crowd_end", "no_doer"} & t_on): S["event lines that are only a crowd / no-doer tag"] += 1
        for e in l["events"]:
            if e[2] is None and e[0] != "awakened":
                S["triples with no object (verb is not awakened)"] += 1
                if len(ex["null-object"]) < 3: ex["null-object"].append(f"[{r['series']}] {e[0]} by {cands[e[1] - 1]} | {s[:110]}")
        S["gold events on a line"] += len(e_on)
        if len(e_on) > len(l["events"]): S["gold events lost on their line (an end not on the list, or a duplicate)"] += len(e_on) - len(l["events"])
    S["fact rows not actual (plans, attempts, orders, claims, hypotheticals)"] += sum((f.get("modality") or "actual") != "actual" for f in fa)
print(f"== {len(rows)} windows: project gate flags on the gold rows")
for k, v in F.most_common(16):
    print(f"{v:6d}  {k}")
    for e in ex[k]: print(f"            {e}")
print(f"windows with at least one flag: {len(flagged)}")
print("== what the per-line target does")
for k, v in S.most_common(): print(f"{v:6d}  {k}")
for k in ("plan-as-event", "null-object"):
    for e in ex[k]: print(f"   {k}: {e}")
if a.ids_out: json.dump(flagged, open(a.ids_out, "w"))
