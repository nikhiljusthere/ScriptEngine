#!/usr/bin/env python3
"""Compose the 12k single-pass set + the verified universal set into one
student training set (owner 2026-10-06/07).

Train = the verified universal train WITHOUT the JJK earned empties
(student_clean, 3,315 windows; gold) + N windows labeled by the ninfer 35B
in ONE pass reading plan/EXTRACTION_PROCEDURE.md (label_single.py; silver).
Dev / dev_pool / test stay the verified gold splits: checkpoints are picked
on dev_pool (non-JJK) and the exam is test. Every 35B window sits on a page
no gold split uses (select_new_windows.py excluded them; re-checked here).

Empty share (council 2026-10-06): the old mix was 57% empty and, with the
per-micro-batch loss, taught "answer empty" (62/123 eventful dev windows
answered []). Target --empty-share 0.30 of the N new windows; empties are
taken first from windows that carry an event trigger word ("hard" empties:
plans, claims, hypotheticals, descriptions of abilities), then plain ones.

--short-system rewrites every split's system message to a ~70-token
instruction (context distillation, the council Expansionist's arm): the
1,373-token production system prompt is identical in every row, so dropping
it cuts training and inference tokens ~7x; the student learns the
conventions from the labels instead of the definitions.

    scriptengine/.venv/bin/python tools/train/compose_big_set.py \
        [--n 12000] [--empty-share 0.30] [--short-system] [--out-dir DIR]
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
from build_student_set import assistant_content  # noqa: E402

VERBS = {"fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "met", "arrived", "departed", "awakened"}
SEED = 20261007
SHORT_SYSTEM = (
    "You extract the events a fiction-wiki passage states. Answer with JSON only, exactly: "
    '{"events": [{"quote": "...", "subject": "...", "verb": "...", "object": "..." or null}]}. '
    "verb is one of: fought, defeated, killed, captured, escaped, saved, betrayed, sealed, met, "
    "arrived, departed, awakened (awakened has a null object). quote is copied word for word from "
    'the passage. If the passage states no event, answer {"events": []}.')


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", default=str(ROOT / "series/universal/training/big/labels.jsonl"))
    ap.add_argument("--gold-dir", default=str(ROOT / "series/universal/training/student_clean"))
    ap.add_argument("--n", type=int, default=12000)
    ap.add_argument("--empty-share", type=float, default=0.30)
    ap.add_argument("--short-system", action="store_true")
    ap.add_argument("--out-dir", default=None)
    a = ap.parse_args()
    out = Path(a.out_dir or ROOT / ("series/universal/training/student_big" + ("_short" if a.short_system else "")))
    out.mkdir(parents=True, exist_ok=True)
    gold = {s: jl(Path(a.gold_dir) / f"{s}.jsonl") for s in ("train", "dev", "dev_pool", "test")}
    src = {r["id"]: r for s in ("marvel", "mcu") for r in jl(ROOT / "series" / s / "training/labels/big_in.jsonl")}
    labels = [r for r in jl(a.labels) if r.get("ok")]
    errors = []
    held_pages = {(r["series"], r["page"]) for s in ("dev", "test") for r in gold[s]}
    ev = [r for r in labels if r["events"]]
    em = [r for r in labels if not r["events"]]
    rng = random.Random(SEED)
    n_ev = min(len(ev), round(a.n * (1 - a.empty_share)))
    n_em = min(len(em), a.n - n_ev)
    take_ev = rng.sample(ev, n_ev)
    hard = [r for r in em if r.get("kind") == "trigger"]
    plain = [r for r in em if r.get("kind") != "trigger"]
    n_hard = min(len(hard), round(n_em * 0.75))
    take_em = rng.sample(hard, n_hard) + rng.sample(plain, min(len(plain), n_em - n_hard))
    big = []
    for r in take_ev + take_em:
        w = src[r["id"]]
        user = w["messages"][1]["content"]
        passage = user.split("Passage:\n", 1)[1]
        events = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in r["events"]]
        for e in events:
            if e["verb"] not in VERBS:
                errors.append(f"{r['id']}: bad verb {e['verb']!r}")
            if not e["quote"] or e["quote"] not in passage:
                errors.append(f"{r['id']}: quote not verbatim")
        if (r["series"], r["page"]) in held_pages:
            errors.append(f"{r['id']}: page {r['page']!r} is on a gold dev/test page")
        big.append({"id": r["id"], "series": r["series"], "page": r["page"], "section": r["section"],
                    "passage": passage, "events": events, "source": "big35b_single", "split": "train",
                    "messages": [w["messages"][0], w["messages"][1],
                                 {"role": "assistant", "content": assistant_content(events)}]})
    train = gold["train"] + big
    ids = [r["id"] for r in train + gold["dev"] + gold["test"]]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate ids: {len(ids) - len(set(ids))}")
    if errors:
        print("COMPOSE FAILED:\n" + "\n".join(errors[:30]) + f"\n... {len(errors)} total")
        return 1
    splits = {"train": train, "dev": gold["dev"], "dev_pool": gold["dev_pool"], "test": gold["test"]}
    for name, rows in splits.items():
        with open(out / f"{name}.jsonl", "w") as f:
            for r in rows:
                if a.short_system:
                    r = {**r, "messages": [{"role": "system", "content": SHORT_SYSTEM}] + r["messages"][1:]}
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rec = {"labels_ok": len(labels), "labels_eventful": len(ev), "labels_empty": len(em),
           "big_taken": len(big), "big_eventful": len(take_ev), "big_empty": len(take_em),
           "big_hard_empty": n_hard, "big_empty_share": round(len(take_em) / max(len(big), 1), 3),
           "train": len(train), "train_empty_share": round(sum(1 for r in train if not r["events"]) / len(train), 3),
           "dev": len(gold["dev"]), "dev_pool": len(gold["dev_pool"]), "test": len(gold["test"]),
           "train_by_series": Counter(r["series"] for r in train),
           "train_verbs": Counter(e["verb"] for r in train for e in r["events"]),
           "short_system": a.short_system}
    (out / "receipt.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
