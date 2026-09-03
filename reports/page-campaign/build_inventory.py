"""Build the classified wrong-answer inventory for campaign round 2.

Sources:
- reports/page-campaign/<series>-<cluster>-*/scores.json  (every fact that
  ever failed a run: query, expected, missing, routed)
- questions/_*_page_*.json `retired` fields (questions dropped with reasons)

Output: reports/page-campaign/WRONG_ANSWERS.md
"""
import json, re
from pathlib import Path
from collections import defaultdict

_here = Path(__file__).resolve()
# Repo root: two levels up from `reports/page-campaign/` when this file lives
# there, else the fixed machine path (the throwaway copy in Temp).
root = _here.parents[2] if _here.parent.name == "page-campaign" else Path(r"E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine")
pc = root / "reports" / "page-campaign"
qdir = root / "questions"

def verb_form_mismatch(expected: list, missing: list) -> bool:
    """smashed/smashe, ripped/rip: expected ends in -ed and missing is the bare stem."""
    for e in expected:
        for m in missing:
            el, ml = e.strip().lower(), m.strip().lower()
            if el.endswith("ed") and el[:-2] == ml:
                return True
            if el.endswith("s") and el[:-1] == ml:
                return True
    return False

MODES = [
    ("battle-result", re.compile(
        r"result of the battle|result of the fight|what (did|does) \w+ do to |"
        r"what happens when|what (did|does) \w+ do after", re.I)),
    ("relationship", re.compile(r"relationship to|who is \w+ (to|for)|rival of|friend of", re.I)),
    ("japanese-name", re.compile(
        r"japanese name|romaji|kanji|viz (translation|name)|original (japanese )?name", re.I)),
    ("ability-what", re.compile(r"what (does|did) \w+'?s .+ (allow|do)|what can .+ do", re.I)),
    ("quote-statement", re.compile(
        r"what (did|does|will) \w+ (say|call|declare|claim|warn|promise)|say about|what did \w+ say", re.I)),
    ("arc-structure", re.compile(
        r"which arc (follows|precedes)|last (chapter|episode) of|first (chapter|episode) of|number of (story )?arcs", re.I)),
    ("chapter-title", re.compile(r"what is the title of chapter", re.I)),
    ("isbn", re.compile(r"isbn", re.I)),
    ("chapter-locator", re.compile(r"in which (chapter|episode)", re.I)),
    ("plural-wh", re.compile(r"^(who are|what are)\b", re.I)),
    ("count-routing", re.compile(r"\bhow many\b|what number of", re.I)),
    ("set-enumeration", re.compile(r"every |all the |every battle", re.I)),
    ("plot-detail", re.compile(
        r"what (happened|did|was) \w+ (to|do|choose|in |after|during)|what (did|does) \w+ (do|use|want|not want)", re.I)),
]

# collect all runs, grouped by (series, cluster)
runs = defaultdict(list)
for d in sorted(pc.iterdir()):
    if not d.is_dir() or not re.match(r"^(jjk|opm)-", d.name):
        continue
    series, cluster = d.name.split("-", 1)
    m = re.match(r"^(jjk|opm)-(.+)-\d{4}-\d{2}-\d{2}-\d{4}$", d.name)
    if not m:
        continue
    cluster = m.group(2)
    sc = d / "scores.json"
    if sc.exists():
        runs[(series, cluster)].append((d.name, json.loads(sc.read_text(encoding="utf-8"))))

inventory = []  # (series, cluster, run, id, query, expected, missing, routed, mode)
seen = set()
for (series, cluster), rs in sorted(runs.items()):
    # every run's failures (dedupe by question id within a cluster)
    for run_name, data in rs:
        for f in data.get("facts", []):
            if f.get("passed"):
                continue
            qid = f.get("id", "")
            key = (series, cluster, qid)
            if key in seen:
                continue
            seen.add(key)
            query = f.get("query", "")
            expected = f.get("expected", [])
            missing = f.get("missing", [])
            mode = None
            for name, rx in MODES:
                if rx.search(query):
                    mode = name
                    break
            if mode is None and verb_form_mismatch(expected, missing):
                mode = "verb-form"
            if mode is None:
                mode = "other"
            inventory.append({
                "series": series, "cluster": cluster, "run": run_name,
                "id": qid, "query": query, "expected": expected,
                "missing": missing, "routed": f.get("routed", "-"), "mode": mode,
            })

# retired questions
retired_rows = []
for p in sorted(qdir.glob("_*page_*.json")):
    data = json.loads(p.read_text(encoding="utf-8"))
    series = "opm" if p.name.startswith("_opm_") else "jjk"
    slug = p.stem.replace(f"_{series}_page_", "")
    for r in data.get("retired", []):
        if isinstance(r, dict):
            retired_rows.append({
                "series": series, "cluster": slug,
                "question": r.get("question", ""),
                "reason": r.get("reason", ""),
            })
        else:
            retired_rows.append({"series": series, "cluster": slug,
                                 "question": str(r), "reason": ""})

# write the report
out = [
    "# Wrong-answer inventory (campaign round 2)",
    "",
    "Every fact answer the engine got wrong across all OPM + JJK cluster runs, plus every",
    "retired question. Regenerated by `C:\\Users\\Nikhil\\AppData\\Local\\Temp\\opencode\\build_inventory.py`.",
    "",
    "## Classification by failure mode",
    "",
]
by_mode = defaultdict(list)
for row in inventory:
    by_mode[row["mode"]].append(row)
order = ["battle-result", "relationship", "japanese-name", "ability-what",
         "quote-statement", "arc-structure", "chapter-title", "isbn",
         "count-routing", "set-enumeration", "plot-detail", "verb-form", "other"]
for mode in order:
    rows = by_mode.get(mode, [])
    if not rows:
        continue
    out.append(f"### {mode} ({len(rows)})")
    out.append("")
    for r in rows[:12]:
        exp = " / ".join(r["expected"][:3])
        mis = " / ".join(r["missing"][:3])
        out.append(f"- [{r['series']}/{r['cluster']} {r['id']}] {r['query']}")
        out.append(f"  - expected: {exp}  | missing: {mis}  | routed: {r['routed']}")
    if len(rows) > 12:
        out.append(f"- … {len(rows) - 12} more (see appendix)")
    out.append("")

out += [
    "## Retired questions (dropped from batches, with reasons)",
    "",
    f"Total: {len(retired_rows)}",
    "",
]
by_cluster = defaultdict(list)
for r in retired_rows:
    by_cluster[(r["series"], r["cluster"])].append(r)
for (series, cluster), rows in sorted(by_cluster.items()):
    out.append(f"### {series}/{cluster} ({len(rows)})")
    for r in rows:
        out.append(f"- {r['question']}")
        if r["reason"]:
            out.append(f"  - reason: {r['reason'][:300]}")
    out.append("")

out += [
    "## Appendix: full table of first-failure per question",
    "",
    "| series | cluster | id | query | expected | missing | routed | mode |",
    "|---|---|---|---|---|---|---|---|",
]
for r in inventory:
    out.append("| {s} | {c} | {i} | {q} | {e} | {m} | {r} | {mo} |".format(
        s=r["series"], c=r["cluster"], i=r["id"],
        q=r["query"].replace("|", "/")[:110],
        e=" / ".join(x.replace("|", "/") for x in r["expected"][:3])[:80],
        m=" / ".join(x.replace("|", "/") for x in r["missing"][:3])[:80],
        r=r["routed"], mo=r["mode"]))
out.append("")
out.append(f"Totals: {len(inventory)} distinct failed questions, {len(retired_rows)} retired.")

dest = pc / "WRONG_ANSWERS.md"
dest.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {dest}")
print(f"failed-question rows: {len(inventory)}")
for mode in order:
    if by_mode.get(mode):
        print(f"  {mode}: {len(by_mode[mode])}")
print(f"retired rows: {len(retired_rows)}")