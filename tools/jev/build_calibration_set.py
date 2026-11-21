"""Build a jev-calibrate project from the canon bank and the diagnosed intruders.

Positives are canon items from `questions/<series>.json` (the online-canon bank,
every item verified against its cited page). Negatives are the intruders
`scriptengine/eval/diagnose_intruders.py` found: members a roster returned that
the bank does not hold, with the bucket that explains why.

One noul is calibrated, `canon_member`: does this item belong in the answer to
this roster question? It is the index-time precision filter's question, so its
threshold is the one the filter would act on. The filter may reject or
annotate, never add (the classify.py contract), so only its false-reject rate on
canon items and its catch rate on intruders matter.

Caveat carried into every number: an intruder is "not in the bank", and the bank
can be incomplete, so a few negatives may really be canon.

    python tools/jev/build_calibration_set.py --limit 50           # small slice
    python tools/jev/build_calibration_set.py --series opm --limit 50 --out tools/jev/calibration
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

QUESTIONS = {
    "questions": {
        "canon_member": {
            "type": "noul",
            "instructions": "Does `candidate.item` belong in the answer to `roster.question` about "
            "`roster.subject`? Judge the item against the question as the wiki's own canon would answer it.",
            "criteria": {
                "true": "The item is one of the subject's own techniques, abilities, forms or members that the question asks for, in the series' canon.",
                "false": "The item is someone else's, a generic trait or category rather than the kind of thing asked for, a section heading, or not canon for the subject.",
            },
        }
    },
    "decisions": {"canon_member": {"threshold": 0.5}},
    "settings": {
        "holdoutFraction": 0.5,
        "minPerClass": 5,
        "targets": {"precision": 0.9, "recall": 0.8, "auc": 0.85, "accuracy": 0.9, "coverage": 0.5},
    },
}


def state(series: str, question: str, subject: str, item: str) -> str:
    return json.dumps(
        {"roster": {"series": series, "question": question, "subject": subject}, "candidate": {"item": item}},
        ensure_ascii=False,
    )


def latest_intruders() -> Path:
    files = glob.glob(str(ROOT / "reports" / "*" / "canon_scores_intruders.json"))
    if not files:
        raise SystemExit("no reports/*/canon_scores_intruders.json; run diagnose_intruders first")
    return Path(max(files, key=os.path.getmtime))


def build(series: str | None, limit: int, seed: int, intruders_path: Path) -> list[dict]:
    intruders = json.loads(intruders_path.read_text(encoding="utf-8"))["items"]
    if series:
        intruders = [i for i in intruders if i["series"] == series]
    questions_asked = {(i["series"], i["question"]) for i in intruders}

    positives = []
    for path in sorted(glob.glob(str(ROOT / "questions" / "[a-z]*.json"))):
        bank = json.loads(Path(path).read_text(encoding="utf-8"))
        for q in bank["questions"]:
            if (bank["series"], q["question"]) not in questions_asked:
                continue
            for entry in q.get("answer", []):
                positives.append((bank["series"], q["question"], q.get("subject", ""), entry["item"], q["id"]))

    rng = random.Random(seed)
    rng.shuffle(positives)
    rng.shuffle(intruders)
    half = limit // 2
    examples = []
    for n, (s, question, subject, item, qid) in enumerate(positives[:half], 1):
        examples.append({"id": f"canon-{n:03d}", "state": state(s, question, subject, item),
                         "labels": {"canon_member": True}, "group": qid})
    for n, i in enumerate(intruders[: limit - len(examples)], 1):
        examples.append({"id": f"intruder-{n:03d}", "state": state(i["series"], i["question"], i["subject"], i["item"]),
                         "labels": {"canon_member": False}, "group": f"{i['series']}:{i['question']}",
                         "bucket": i["bucket"]})
    return examples


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--series")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--intruders", type=Path)
    ap.add_argument("--out", type=Path, default=ROOT / "tools" / "jev" / "calibration")
    a = ap.parse_args()

    src = a.intruders or latest_intruders()
    examples = build(a.series, a.limit, a.seed, src)
    a.out.mkdir(parents=True, exist_ok=True)
    (a.out / "questions.json").write_text(json.dumps(QUESTIONS, indent=2) + "\n", encoding="utf-8")
    with (a.out / "examples.jsonl").open("w", encoding="utf-8") as fh:
        for e in examples:
            e = {k: v for k, v in e.items() if k != "bucket"}
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    pos = sum(1 for e in examples if e["labels"]["canon_member"])
    print(f"{len(examples)} examples ({pos} canon, {len(examples) - pos} intruders) from {src.relative_to(ROOT)} -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
