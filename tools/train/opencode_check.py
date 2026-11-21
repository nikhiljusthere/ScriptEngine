"""Validate an opencode annotator's output file (series/jjk/training/opencode/).

    scriptengine/.venv/bin/python tools/train/opencode_check.py --model spacebunny

Checks every line of <model>_out.jsonl against <model>_windows.jsonl: known id,
one line per window, every row's quote copied word for word from that window's
passage, a legal verb, object null only for `awakened`, a wiki card, a verdict and
a rule. Prints progress, the next window to do, and every problem; exit 1 on any.
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "train"))
from scriptengine.ingest.verbatim import quoted_in  # noqa: E402
from gold_tools import VERBS, repair_quote  # noqa: E402

D = ROOT / "series" / "jjk" / "training" / "opencode"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    a = ap.parse_args()
    wins = {w["id"]: w for w in map(json.loads, open(D / f"{a.model}_windows.jsonl"))}
    order = sorted(wins.values(), key=lambda w: w["n"])
    out = D / f"{a.model}_out.jsonl"
    problems, seen, rows, kept = [], set(), 0, 0
    if out.exists():
        for ln, line in enumerate(open(out), 1):
            try:
                r = json.loads(line)
            except ValueError:
                problems.append(f"line {ln}: not valid JSON"); continue
            i = r.get("id")
            if i not in wins:
                problems.append(f"line {ln}: unknown id {i!r}"); continue
            if i in seen:
                problems.append(f"line {ln}: window n={wins[i]['n']} written twice"); continue
            seen.add(i)
            text = wins[i]["passage"]
            for k, e in enumerate(r.get("events") if isinstance(r.get("events"), list) else [None]):
                where = f"n={wins[i]['n']} row {k}"
                if not isinstance(e, dict):
                    problems.append(f"{where}: events must be a list of objects"); continue
                rows += 1
                v = str(e.get("verb", "")).lower()
                if v not in VERBS:
                    problems.append(f"{where}: verb {e.get('verb')!r} is not one of the 12")
                if (e.get("object") is None) != (v == "awakened"):
                    problems.append(f"{where}: object must be null for awakened and only for awakened")
                q = e.get("quote") or ""
                if len(q) < 12 or not (quoted_in(q, text) or repair_quote(q, text)):
                    problems.append(f"{where}: quote is not copied word for word from the passage: {q[:80]!r}")
                if not e.get("subject"):
                    problems.append(f"{where}: missing subject")
                if not e.get("wiki"):
                    problems.append(f"{where}: missing wiki (run tools/train/wiki_card.py for this row)")
                if str(e.get("verdict", "")).lower() not in ("yes", "no"):
                    problems.append(f"{where}: verdict must be yes or no")
                elif str(e["verdict"]).lower() == "yes":
                    kept += 1
                if not e.get("rule"):
                    problems.append(f"{where}: missing rule")
    todo = [w["n"] for w in order if w["id"] not in seen]
    print(f"{a.model}: {len(seen)}/{len(wins)} windows written, {rows} rows ({kept} verdict yes)")
    print("next window to do: n=" + (str(todo[0]) if todo else "none, all done"))
    for p in problems[:60]:
        print("PROBLEM", p)
    if len(problems) > 60:
        print(f"... and {len(problems) - 60} more")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
