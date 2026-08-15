"""Score a coverage bank through `build_roster` -- no server, no GPU."""
import json, sys, collections
sys.path.insert(0, r"E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from scriptengine.config import series_paths
from scriptengine.retrieve.roster import build_roster
from scriptengine.eval.canon_gold import norm

series = sys.argv[1]
root = r"E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
bank = json.loads(open(f"{root}/questions/_{series}_battles.json", encoding="utf-8").read())
paths = series_paths(series)
tot = collections.Counter()
by = collections.defaultdict(collections.Counter)
worst = []
for q in bank["questions"]:
    gold = [a["item"] for a in q["answer"]]
    try:
        r = build_roster(paths, q["question"])
        members = [m.name for m in r.members] if r else []
    except Exception:
        members = []
    seen = {norm(m) for m in members}
    hit = [g for g in gold if norm(g) in seen]
    shape = "battles" if q["question"].startswith("Every battle") else "techniques"
    for k, v in (("hit", len(hit)), ("gold", len(gold)),
                 ("match", len({norm(g) for g in hit})), ("ret", len(members))):
        tot[k] += v; by[shape][k] += v
    worst.append((len(hit)/max(1,len(gold)), q["question"], len(hit), len(gold), len(members)))
print(f"[{series}] recall {tot['hit']}/{tot['gold']} = {100*tot['hit']/max(1,tot['gold']):.1f}%"
      f"   precision {tot['match']}/{tot['ret']} = {100*tot['match']/max(1,tot['ret']):.1f}%")
for shape, c in by.items():
    print(f"   {shape:11} recall {c['hit']}/{c['gold']} = {100*c['hit']/max(1,c['gold']):5.1f}%"
          f"   precision {c['match']}/{c['ret']} = {100*c['match']/max(1,c['ret']):5.1f}%")
worst.sort()
print("\nworst:")
for rec, q, h, g, n in worst[:6]:
    print(f"   {rec:5.0%}  {h}/{g:<3} n={n:<4} {q[:56]}")
