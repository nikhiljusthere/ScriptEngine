"""Draft rows from other sources, in the Q6 worker's candidate format
({"id", "events", "ok"}), so they go through the same correct-and-verify loop
(owner 2026-09-29: every training entry verified; drafts may come from anyone).

    opencode  <model>_out.jsonl (opencode annotators) -> cand file. ALL rows go in,
              the annotator's "no" rows too: the corrector judges each one again,
              and an over-strict "no" is how a correct row gets lost.
    teacher   the stored teacher rows of a window (export target) -> cand file
    merge     stage-1 corrector output (verify_rows.py) -> stage-2 cand file: the
              draft rows the corrector kept + the events it found missing, each
              with a passage-exact quote (a row whose quote cannot be matched is
              left for the adjudicator, never guessed)

    python tools/train/drafts.py opencode --model mimo --out cand.jsonl
    python tools/train/drafts.py teacher --data train.jsonl --ids ids.json --out cand.jsonl
    python tools/train/drafts.py merge --data train.jsonl --cand draft.jsonl --verify stage1.jsonl --out stage2.jsonl
"""
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
from gold_tools import check, passage  # noqa: E402

OC = ROOT / "series" / "jjk" / "training" / "opencode"
FIELDS = ("quote", "subject", "verb", "object")


def opencode(a):
    with open(a.out, "w") as f:
        for l in open(OC / f"{a.model}_out.jsonl"):
            r = json.loads(l)
            ev = [{k: e.get(k) for k in FIELDS} for e in r.get("events") or []]
            f.write(json.dumps({"id": r["id"], "events": ev, "ok": True, "source": a.model}, ensure_ascii=False) + "\n")


def teacher(a):
    want = set(json.load(open(a.ids)))
    with open(a.out, "w") as f:
        for l in open(a.data):
            r = json.loads(l)
            if r["id"] in want:
                ev = json.loads(r["messages"][2]["content"])["events"]
                f.write(json.dumps({"id": r["id"], "events": ev, "ok": True, "source": "teacher"}, ensure_ascii=False) + "\n")


def merge(a):
    rows = {json.loads(l)["id"]: json.loads(l) for l in open(a.data)}
    draft = {}
    for c in a.cand:
        for l in open(c):
            r = json.loads(l)
            draft[r["id"]] = r
    n_keep = n_add = n_badq = 0
    with open(a.out, "w") as f:
        for l in open(a.verify):
            v = json.loads(l)
            if not v.get("ok") or v["id"] not in draft:
                continue
            text = passage(rows[v["id"]])
            keep = {x["n"] for x in v["verdicts"] if x["ok"] == 1}
            ev = [e for n, e in enumerate(draft[v["id"]]["events"]) if n in keep]
            n_keep += len(ev)
            for e in v.get("missed") or []:
                c = check(e, text)
                if c is None:
                    n_badq += 1
                    continue
                ev.append(c); n_add += 1
            f.write(json.dumps({"id": v["id"], "events": ev, "ok": True, "source": draft[v["id"]].get("source")},
                               ensure_ascii=False) + "\n")
    print(json.dumps({"kept": n_keep, "added_missed": n_add, "missed_with_bad_quote": n_badq}))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["opencode", "teacher", "merge"])
    ap.add_argument("--model")
    ap.add_argument("--data")
    ap.add_argument("--ids")
    ap.add_argument("--cand", nargs="*")
    ap.add_argument("--verify")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    {"opencode": opencode, "teacher": teacher, "merge": merge}[a.cmd](a)


if __name__ == "__main__":
    main()
