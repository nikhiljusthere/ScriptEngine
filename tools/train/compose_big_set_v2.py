#!/usr/bin/env python3
"""Compose the v2 student set: events + facts + tags (owner 2026-10-13: "events + facts + tags").

Train = the gold train windows (student_clean train, 3,315; gold v2 = their verified events re-checked plus
reviewed facts/tags) + the reviewed big windows (big v2, all 14,000 Claude-reviewed, lint-clean).
Dev / dev_pool / test = the gold v2 splits (gold_in.jsonl `splits`). Every row is the LATEST audit record of
its window (append-only audits, latest wins): big_audit_v2.jsonl and gold_v2/gold_audit_v2.jsonl.

The assistant turn is {"events": [...], "facts": [...], "tags": [...]}: events {quote, subject, verb,
object}; facts {quote, subject, relation, object, modality, certainty, asserted_by[, canon when set]}; tags
{tag, quote}. Every split gets the short three-layer system prompt (v1's --short-system arm, the one the owner
trains first; the 17.6K-token procedure doc is far too long to train on).

Compose-time normalisations (mechanical, already applied by lint M5, repeated so compose is idempotent):
`A|child_of|B` -> `B|parent_of|A`; `married_to` -> `married`. Everything else must already be clean: compose
FAILS on a quote that is not verbatim, a verb/relation/tag/modality/certainty outside the vocabulary, an
actual row with an asserter or a non-actual row without one, a retired relation (codename_of, also_known_as,
real_name_of, became), a big window on a gold dev/test page, or a duplicate id.

Empty share: a window whose answer has no events and no facts (tags only) teaches "answer nothing"; v1's
council cap (30%) applies to those. Windows with facts but no events are not empty answers.

    scriptengine/.venv/bin/python tools/train/compose_big_set_v2.py [--empty-share 0.30] [--out-dir DIR]
        [--allow-unreviewed-gold]   (dry runs only: gold windows without an audit record use their 35B rows)
"""
import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = Path("/home/goblin/ScriptEngine/series/universal/training")  # the main checkout's gitignored data
sys.path.insert(0, str(ROOT / "tools" / "train"))
import fact_gate  # noqa: E402

VERBS = ("fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "met", "arrived", "departed", "awakened")
RETIRED = {"codename_of", "also_known_as", "real_name_of", "became", "child_of", "married_to"}
RELATIONS = tuple(r for r in fact_gate.RELATIONS if r not in RETIRED) + ("other_verb",)
SEED = 20261014
SHORT_SYSTEM = (
    "You extract what a fiction-wiki passage states. Answer with JSON only, exactly: "
    '{"events": [...], "facts": [...], "tags": [...]}. '
    'An event is {"quote", "subject", "verb", "object"}; verb is one of: ' + ", ".join(VERBS) +
    " (awakened has a null object). "
    'A fact is {"quote", "subject", "relation", "object", "modality", "certainty", "asserted_by"}; relation is one of: '
    + ", ".join(RELATIONS) + " (other_verb takes the passage's own verb as object; object null when none). "
    "modality: " + ", ".join(fact_gate.MODALITY) + "; certainty: " + ", ".join(fact_gate.CERTAINTY) +
    "; asserted_by names who plans, claims or orders (null on actual rows). "
    'A tag is {"tag", "quote"} for a sentence that states no legal row; tag is one of: ' + ", ".join(fact_gate.TAGS) +
    ". Every quote is copied word for word from the passage. Use one name per person.")


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def latest(path):
    out = {}
    for r in jl(path):
        out[r["id"]] = r
    return out


def norm_fact(f):
    f = dict(f)
    if f.get("relation") == "child_of" and f.get("object"):
        f["subject"], f["object"], f["relation"] = f["object"], f["subject"], "parent_of"
    if f.get("relation") == "married_to":
        f["relation"] = "married"
    out = {k: f.get(k) for k in ("quote", "subject", "relation", "object")}
    out["modality"] = f.get("modality") or "actual"
    out["certainty"] = f.get("certainty") or "stated"
    out["asserted_by"] = f.get("asserted_by") or None
    if f.get("canon"):
        out["canon"] = f["canon"]
    return out


def answer(rec, passage, wid, errors):
    events = [{k: e.get(k) for k in ("quote", "subject", "verb", "object")} for e in rec.get("events", [])]
    facts = [norm_fact(f) for f in rec.get("facts", [])]
    tags = [{"tag": t.get("tag"), "quote": t.get("quote")} for t in rec.get("tags", [])]
    for e in events:
        if e["verb"] not in VERBS:
            errors.append(f"{wid}: bad verb {e['verb']!r}")
        if not e["quote"] or e["quote"] not in passage:
            errors.append(f"{wid}: event quote not verbatim: {e['quote']!r}")
        if e["verb"] != "awakened" and not e["object"]:
            errors.append(f"{wid}: event {e['subject']}|{e['verb']} has no object")
    for f in facts:
        if f["relation"] not in RELATIONS:
            errors.append(f"{wid}: relation {f['relation']!r} {'retired' if f['relation'] in RETIRED else 'unknown'}")
        if not f["quote"] or f["quote"] not in passage:
            errors.append(f"{wid}: fact quote not verbatim: {f['quote']!r}")
        if f["modality"] not in fact_gate.MODALITY or f["certainty"] not in fact_gate.CERTAINTY:
            errors.append(f"{wid}: modality/certainty {f['modality']}/{f['certainty']}")
        if (f["modality"] == "actual") == bool(f["asserted_by"]):
            errors.append(f"{wid}: {f['subject']}|{f['relation']} modality {f['modality']} asserted_by {f['asserted_by']!r}")
    for t in tags:
        if t["tag"] not in fact_gate.TAGS:
            errors.append(f"{wid}: tag {t['tag']!r}")
        if not t["quote"] or t["quote"] not in passage:
            errors.append(f"{wid}: tag quote not verbatim: {t['quote']!r}")
    return {"events": events, "facts": facts, "tags": tags}


def row(wid, meta, passage, user, ans, source, split):
    return {"id": wid, "series": meta.get("series"), "page": meta.get("page"), "section": meta.get("section"),
            "passage": passage, **ans, "source": source, "split": split,
            "messages": [{"role": "system", "content": SHORT_SYSTEM}, {"role": "user", "content": user},
                         {"role": "assistant", "content": json.dumps(ans, ensure_ascii=False)}]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--big-dir", default=str(DATA / "big"))
    ap.add_argument("--empty-share", type=float, default=0.30)
    ap.add_argument("--out-dir", default=str(DATA / "student_v2_short"))
    ap.add_argument("--allow-unreviewed-gold", action="store_true")
    a = ap.parse_args()
    big = Path(a.big_dir)
    errors = []

    # gold: every window of every split, from its latest gold-v2 audit record
    gin = jl(big / "gold_v2" / "gold_in.jsonl")
    gaud = latest(big / "gold_v2" / "gold_audit_v2.jsonl")
    gbase = latest(big / "gold_v2" / "gold_labels_v2.jsonl")
    splits = {s: [] for s in ("train", "dev", "dev_pool", "test")}
    unreviewed = 0
    for w in gin:
        rec = gaud.get(w["id"])
        if rec is None:
            unreviewed += 1
            rec = gbase.get(w["id"], {"events": [], "facts": [], "tags": []})
        user = w["messages"][1]["content"]
        passage = user.split("Passage:\n", 1)[1]
        ans = answer(rec, passage, w["id"], errors)
        for s in w["splits"]:
            splits[s].append(row(w["id"], w, passage, user, ans, "gold_v2", s))
    if unreviewed and not a.allow_unreviewed_gold:
        errors.append(f"{unreviewed} of {len(gin)} gold windows have no gold-v2 audit record (review them first)")

    # big: every reviewed window, latest big_audit_v2 record
    src = {r["id"]: r for s in ("marvel", "mcu") for r in jl(DATA.parent.parent / s / "training/labels/big_in.jsonl")}
    baud = latest(big / "big_audit_v2.jsonl")
    held = {(r["series"], r["page"]) for s in ("dev", "dev_pool", "test") for r in splits[s]}
    gold_ids = {w["id"] for w in gin}
    rows, empties = [], []
    for wid, rec in baud.items():
        w = src.get(wid)
        if w is None:
            errors.append(f"{wid}: audit record with no big_in window")
            continue
        user = w["messages"][1]["content"]
        passage = user.split("Passage:\n", 1)[1]
        if (rec.get("series"), rec.get("page")) in held:
            errors.append(f"{wid}: page {rec.get('page')!r} is on a gold dev/test page")
        if wid in gold_ids:
            errors.append(f"{wid}: big window is also a gold window")
        ans = answer(rec, passage, wid, errors)
        r = row(wid, rec, passage, user, ans, "big_v2_reviewed", "train")
        (empties if not ans["events"] and not ans["facts"] else rows).append(r)
    rng = random.Random(SEED)
    cap = int(len(rows) * a.empty_share / (1 - a.empty_share))
    if len(empties) > cap:
        empties = rng.sample(empties, cap)
    train = splits["train"] + rows + empties
    rng.shuffle(train)
    ids = [r["id"] for r in train] + [r["id"] for s in ("dev", "test") for r in splits[s]]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate ids across train/dev/test: {len(ids) - len(set(ids))}")
    if errors:
        print("COMPOSE FAILED:\n" + "\n".join(errors[:40]) + f"\n... {len(errors)} total")
        return 1
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    final = {"train": train, **{s: splits[s] for s in ("dev", "dev_pool", "test")}}
    for name, rs in final.items():
        with open(out / f"{name}.jsonl", "w") as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    def empty(r):
        return not r["events"] and not r["facts"]
    rec = {"gold_unreviewed": unreviewed, "big_windows": len(baud), "big_taken": len(rows) + len(empties),
           "big_empty_answers": len(empties),
           "train": len(train), "train_empty_answer_share": round(sum(map(empty, train)) / len(train), 3),
           "train_no_event_share": round(sum(1 for r in train if not r["events"]) / len(train), 3),
           **{s: len(final[s]) for s in ("dev", "dev_pool", "test")},
           "train_rows": {"events": sum(len(r["events"]) for r in train), "facts": sum(len(r["facts"]) for r in train),
                          "tags": sum(len(r["tags"]) for r in train)},
           "train_by_series": Counter(r["series"] for r in train),
           "train_verbs": Counter(e["verb"] for r in train for e in r["events"]),
           "train_relations": Counter(f["relation"] for r in train for f in r["facts"]),
           "system_prompt_chars": len(SHORT_SYSTEM)}
    (out / "receipt.json").write_text(json.dumps(rec, indent=1))
    print(json.dumps(rec, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
