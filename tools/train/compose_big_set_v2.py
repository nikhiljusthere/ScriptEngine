#!/usr/bin/env python3
"""Compose the v2 student set: events + facts + tags (owner 2026-10-13: "events + facts + tags").

Train = the gold train windows (gold_in `splits` == train: the student_clean train, 3,315, which already
excludes the JJK earned empties; gold v2 = their events re-checked plus reviewed facts/tags) + the reviewed
big windows (big v2, all 14,000 Claude-reviewed, lint-clean). Dev / dev_pool / test = the gold v2 splits
(gold_in.jsonl `splits`; dev_pool is a subset of dev by design: the non-JJK dev windows that pick the
checkpoint). Every row is the LATEST audit record of its window with big_review_v2.audit2()'s rule: the
audits are append-only, latest wins, and a {"id", "void": true} line withdraws the record before it
(2026-10-10, b501-b540).

The assistant turn is {"events": [...], "facts": [...], "tags": [...]} in EXTRACTION_PROCEDURE_V2.md's
shape and key order: events {quote, subject, verb, object}; facts {quote, subject, relation, object,
modality, certainty, asserted_by, canon} (all eight keys on every fact, canon null when unset: one fixed
shape is what the student learns and the parser reads); tags {quote, tag} (quote first, as the procedure
writes it; the audit files store {tag, quote}). Serialised with json.dumps(ensure_ascii=False), the same
serialisation as v1's assistant_content, so the event layer's text is unchanged.

System prompt: the short three-layer instruction (SHORT_SYSTEM, the default; v1's --short-system arm, the
one the owner trains first; the 17.6K-token procedure doc is far too long to train on). --system-file
replaces it for an alternative arm.

Empty share (owner/council 2026-10-06/07: 30% of the big windows, hard empties ~75% of them). --empty-def
picks what counts as an empty answer: `all` (default: events AND facts AND tags empty, stage-8b spec),
`events+facts` (tag-only answers count as empty), or `events` (v1's definition: no event row). When the
big set holds more empties than --empty-share allows, the cap keeps a seeded sample, hard empties (big_in
kind == trigger: event wording, no event) first up to --hard-share of the kept empties. The cap applies to
the big windows, as in v1; the receipt also reports every definition's share over the whole train split.

Compose FAILS (writes nothing) on: a quote that is not verbatim in its passage; a verb/relation/tag/
modality/certainty/canon outside the vocabulary; a retired relation (codename_of, also_known_as,
real_name_of, became, child_of, married_to; the last two are normalised first, as lint M5 did); an
actual fact with an asserter, or a non-actual non-hypothetical fact without one (B.4 lets a hypothetical
have none); an empty subject; a gold window with no audit record (unless --allow-unreviewed-gold, dry
runs only); a JJK earned-empty window anywhere; a window id, exact page or passage shared between train,
dev and test; dev_pool not inside dev; a big window on a gold page. Reported, not fatal (receipt
`warnings`): base-page shares ("Denji" vs "Denji/History"; the gold ones are inherited from v1's split)
and exact-sentence overlap; --drop-base-page-overlap leaves out the big windows on a dev/test base page.
Always left out (receipt `big_dropped_sentence_overlap`): a big window repeating a >=40-char dev/test
sentence word for word.

    scriptengine/.venv/bin/python tools/train/compose_big_set_v2.py --out-dir DIR
        [--empty-share 0.30] [--hard-share 0.75] [--empty-def all|events+facts|events]
        [--snapshot DIR]          (read the four audit/gold files from a frozen copy instead of the live ones)
        [--system-file FILE] [--allow-unreviewed-gold]
"""
import argparse
import hashlib
import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAIN = Path("/home/goblin/ScriptEngine")  # the main checkout: the gitignored data lives there
DATA = MAIN / "series/universal/training"
sys.path.insert(0, str(ROOT / "tools" / "train"))
import fact_gate  # noqa: E402

VERBS = ("fought", "defeated", "killed", "captured", "escaped", "saved", "betrayed",
         "sealed", "met", "arrived", "departed", "awakened")
# retired by the review (lint M5: child_of -> parent_of, married_to -> married; F_alias_variant: the
# three alias spellings -> alias_of; F_became: became -> transformed_into / member_of / other_verb)
RETIRED = {"codename_of", "also_known_as", "real_name_of", "became", "child_of", "married_to"}
RELATIONS = tuple(r for r in fact_gate.RELATIONS if r not in RETIRED) + ("other_verb",)
CANON = tuple(c for c in fact_gate.CANON if c)
SPLITS = ("train", "dev", "dev_pool", "test")
SEED = 20261014
EVENT_KEYS = ("quote", "subject", "verb", "object")
FACT_KEYS = ("quote", "subject", "relation", "object", "modality", "certainty", "asserted_by", "canon")
TAG_KEYS = ("quote", "tag")
SHORT_SYSTEM = (
    "You extract what a fiction-wiki passage states, in three layers. Answer with JSON only, exactly: "
    '{"events": [...], "facts": [...], "tags": [...]}.\n'
    'events: {"quote", "subject", "verb", "object"} for each act that happened; verb is one of: '
    + ", ".join(VERBS) + " (awakened has a null object). An act these verbs express is an event, "
    "never also a fact.\n"
    'facts: {"quote", "subject", "relation", "object", "modality", "certainty", "asserted_by", "canon"} '
    "for every other statement of who is what to whom; relation is one of: " + ", ".join(RELATIONS) +
    ". other_verb puts the passage's own verb in object; object is null when the relation takes none. "
    "modality: " + ", ".join(fact_gate.MODALITY) + "; certainty: " + ", ".join(fact_gate.CERTAINTY) +
    "; asserted_by is the named character who planned, ordered, controlled, claimed or imagined it (null when "
    "modality is actual); canon: " + ", ".join(CANON) + " or null.\n"
    'tags: {"quote", "tag"} for each sentence that states no legal row; tag is one of: ' +
    ", ".join(fact_gate.TAGS) + ".\n"
    "Every quote is copied word for word from the passage, inside one sentence. Use one name per person, "
    "the passage's fullest form; never a crowd, a species or a pronoun as an end.")


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip("\x00\n ")] if Path(p).exists() else []


def latest(path):
    """big_review_v2.audit2(): latest record per id; a void line withdraws the record before it."""
    st = {}
    for a in jl(path):
        if a.get("void"):
            if st.get(a["id"]):
                st[a["id"]].pop()
        else:
            st.setdefault(a["id"], []).append(a)
    return {k: v[-1] for k, v in st.items() if v}


def passage_of(user):
    return user.split("Passage:\n", 1)[1]


def base_page(page):
    return (page or "").split("/", 1)[0].strip().lower()


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm_fact(f):
    f = dict(f)
    if f.get("relation") == "child_of" and f.get("object"):
        f["subject"], f["object"], f["relation"] = f["object"], f["subject"], "parent_of"
    if f.get("relation") == "married_to":
        f["relation"] = "married"
    out = {k: f.get(k) for k in FACT_KEYS}
    out["modality"] = out["modality"] or "actual"
    out["certainty"] = out["certainty"] or "stated"
    out["asserted_by"] = out["asserted_by"] or None
    out["canon"] = out["canon"] or None
    return out


def answer(rec, passage, wid, errors):
    """The v2 answer of one audit record, validated; problems go to `errors`."""
    events = [{k: e.get(k) for k in EVENT_KEYS} for e in rec.get("events") or []]
    facts = [norm_fact(f) for f in rec.get("facts") or []]
    tags = [{"quote": t.get("quote"), "tag": t.get("tag")} for t in rec.get("tags") or []]

    def verbatim(kind, q):
        if not isinstance(q, str) or not q or q not in passage:
            errors.append(f"{wid}: {kind} quote not verbatim: {q!r}")

    for e in events:
        verbatim("event", e["quote"])
        if e["verb"] not in VERBS:
            errors.append(f"{wid}: bad verb {e['verb']!r}")
        if not isinstance(e["subject"], str) or not e["subject"].strip():
            errors.append(f"{wid}: event with no subject")
        if e["verb"] != "awakened" and not e["object"]:
            errors.append(f"{wid}: event {e['subject']}|{e['verb']} has no object")
    for f in facts:
        verbatim("fact", f["quote"])
        if f["relation"] not in RELATIONS:
            errors.append(f"{wid}: relation {f['relation']!r} {'retired' if f['relation'] in RETIRED else 'unknown'}")
        if not isinstance(f["subject"], str) or not f["subject"].strip():
            errors.append(f"{wid}: fact with no subject")
        if f["object"] is not None and not isinstance(f["object"], str):
            errors.append(f"{wid}: fact object {f['object']!r}")
        if f["modality"] not in fact_gate.MODALITY or f["certainty"] not in fact_gate.CERTAINTY:
            errors.append(f"{wid}: modality/certainty {f['modality']}/{f['certainty']}")
        if f["canon"] is not None and f["canon"] not in CANON:
            errors.append(f"{wid}: canon {f['canon']!r}")
        if f["modality"] == "actual" and f["asserted_by"]:
            errors.append(f"{wid}: {f['subject']}|{f['relation']} actual with asserted_by {f['asserted_by']!r}")
        if f["modality"] not in ("actual", "hypothetical") and not f["asserted_by"]:
            errors.append(f"{wid}: {f['subject']}|{f['relation']} {f['modality']} without asserted_by")
    for t in tags:
        verbatim("tag", t["quote"])
        if t["tag"] not in fact_gate.TAGS:
            errors.append(f"{wid}: tag {t['tag']!r}")
    return {"events": events, "facts": facts, "tags": tags}


EMPTY = {"all": lambda a: not a["events"] and not a["facts"] and not a["tags"],
         "events+facts": lambda a: not a["events"] and not a["facts"],
         "events": lambda a: not a["events"]}


def row(wid, meta, passage, user, ans, source, split, system):
    return {"id": wid, "series": meta.get("series"), "page": meta.get("page"), "section": meta.get("section"),
            "passage": passage, **ans, "source": source, "split": split,
            "messages": [{"role": "system", "content": system}, {"role": "user", "content": user},
                         {"role": "assistant", "content": json.dumps(ans, ensure_ascii=False)}]}


def earned_empty_ids():
    """JJK earned empties (rule-inferred from old annotations; council: never train on them)."""
    out = set()
    for s in SPLITS:
        for r in jl(DATA / "student" / f"{s}.jsonl"):
            if r.get("earned_empty") or str(r.get("source", "")).startswith("earned_empty"):
                out.add(r["id"])
    return out


def compose(a):
    """-> (final splits, receipt, errors)."""
    errors = []
    snap = Path(a.snapshot) if a.snapshot else None
    gold_in = snap / "gold_in.jsonl" if snap else DATA / "big/gold_v2/gold_in.jsonl"
    gold_audit = snap / "gold_audit_v2.jsonl" if snap else DATA / "big/gold_v2/gold_audit_v2.jsonl"
    gold_base = snap / "gold_labels_v2.jsonl" if snap else DATA / "big/gold_v2/gold_labels_v2.jsonl"
    big_audit = snap / "big_audit_v2.jsonl" if snap else DATA / "big/big_audit_v2.jsonl"
    big_in = {s: MAIN / "series" / s / "training/labels/big_in.jsonl" for s in ("marvel", "mcu")}
    system = Path(a.system_file).read_text() if a.system_file else SHORT_SYSTEM
    earned = earned_empty_ids()

    # gold: every window of every split, from its latest gold-v2 audit record
    gin = jl(gold_in)
    gaud = latest(gold_audit)
    gbase = latest(gold_base) if a.allow_unreviewed_gold else {}
    splits = {s: [] for s in SPLITS}
    unreviewed = 0
    for w in gin:
        rec = gaud.get(w["id"])
        if rec is None:
            unreviewed += 1
            rec = gbase.get(w["id"], {})
        if w["id"] in earned:
            errors.append(f"{w['id']}: a JJK earned empty in gold_in")
        user = w["messages"][1]["content"]
        ans = answer(rec, passage_of(user), w["id"], errors)
        if not w["splits"] or any(s not in SPLITS for s in w["splits"]):
            errors.append(f"{w['id']}: splits {w['splits']!r}")
        for s in w["splits"]:
            splits[s].append(row(w["id"], w, passage_of(user), user, ans, "gold_v2", s, system))
    if unreviewed and not a.allow_unreviewed_gold:
        errors.append(f"{unreviewed} of {len(gin)} gold windows have no gold-v2 audit record (review them first)")
    stray = set(gaud) - {w["id"] for w in gin}
    if stray:
        errors.append(f"{len(stray)} gold audit ids not in gold_in")

    # big: every reviewed window (latest big_audit_v2 record), in big_audit `b` order
    src = {}
    for s, p in big_in.items():
        for r in jl(p):
            src[r["id"]] = {**r, "series": s}
    baud = latest(big_audit)
    gold_pages = {(r["series"], r["page"]) for s in SPLITS for r in splits[s]}
    held_base_gold = {(r["series"], base_page(r["page"])) for s in ("dev", "test") for r in splits[s]}
    # a big window that repeats a dev/test sentence word for word is a content leak even on another page
    # (2026-11-03 dry run: "Iron Man/A.I.M. Operative Controller" repeats a sentence of the test window on
    # "Iron Monger/A.I.M. Operative Controller"): always left out, counted in the receipt
    held_sent = {x for s in ("dev", "test") for r in splits[s] for x in fact_gate.sentences(r["passage"])
                 if len(x) >= 40}
    eventful, empties, dropped_base, dropped_sent = [], [], 0, []
    for wid, rec in sorted(baud.items(), key=lambda kv: kv[1].get("b", 0)):
        w = src.get(wid)
        if w is None:
            errors.append(f"{wid}: audit record with no big_in window")
            continue
        if (w["series"], w["page"]) in gold_pages:
            errors.append(f"{wid}: big window on gold page {w['page']!r}")
        if a.drop_base_page_overlap and (w["series"], base_page(w["page"])) in held_base_gold:
            dropped_base += 1
            continue
        if any(x in held_sent for x in fact_gate.sentences(passage_of(w["messages"][1]["content"]))):
            dropped_sent.append(f"{rec.get('b')}:{w['page']}")
            continue
        if wid in earned:
            errors.append(f"{wid}: a JJK earned empty in the big set")
        user = w["messages"][1]["content"]
        ans = answer(rec, passage_of(user), wid, errors)
        r = row(wid, {**w, "page": rec.get("page", w["page"])}, passage_of(user), user, ans,
                "big_v2_reviewed", "train", system)
        r["kind"] = w.get("kind")
        (empties if EMPTY[a.empty_def](ans) else eventful).append(r)
    n_big_used = len(eventful) + len(empties)
    missing = set(src) - set(baud)
    if missing:
        errors.append(f"{len(missing)} big_in windows have no big audit record")

    # the empty cap over the big windows (hard empties first)
    rng = random.Random(SEED)
    cap = int(len(eventful) * a.empty_share / (1 - a.empty_share))
    empties_avail = len(empties)
    if len(empties) > cap:
        hard = [r for r in empties if r["kind"] == "trigger"]
        plain = [r for r in empties if r["kind"] != "trigger"]
        n_hard = min(len(hard), round(cap * a.hard_share))
        n_plain = min(len(plain), cap - n_hard)
        n_hard = min(len(hard), cap - n_plain)  # top up from hard when plain runs out
        empties = rng.sample(hard, n_hard) + rng.sample(plain, n_plain)
    big_rows = eventful + empties
    hard_taken = sum(1 for r in empties if r["kind"] == "trigger")
    for r in big_rows:
        r.pop("kind", None)
    train = splits["train"] + big_rows
    rng.shuffle(train)
    final = {"train": train, **{s: splits[s] for s in ("dev", "dev_pool", "test")}}

    # leakage: dev_pool inside dev; train / dev / test disjoint by id, page, base page and passage
    dev_ids = {r["id"] for r in final["dev"]}
    if not {r["id"] for r in final["dev_pool"]} <= dev_ids:
        errors.append("dev_pool is not a subset of dev")
    keys = {"id": lambda r: r["id"], "page": lambda r: (r["series"], r["page"]),
            "passage": lambda r: hashlib.sha1(r["passage"].encode()).hexdigest()}
    leaks = {}
    for kname, k in keys.items():
        sets = {s: {k(r) for r in final[s]} for s in ("train", "dev", "test")}
        for x, y in (("train", "dev"), ("train", "test"), ("dev", "test")):
            n = len(sets[x] & sets[y])
            leaks[f"{kname}:{x}&{y}"] = n
            if n:
                errors.append(f"{n} {kname} values shared by {x} and {y}")
    # reported, not fatal: a subpage of the same entity ("Denji" vs "Denji/History") on both sides. The
    # gold splits were cut by exact page in v1 (student_clean), so gold-vs-gold shares are inherited and
    # frozen with the test; the big-vs-gold ones are listed so the owner can drop them
    # (--drop-base-page-overlap). The content measure is the exact-sentence overlap below.
    warnings = {}
    held_base = {s: {(r["series"], base_page(r["page"])) for r in final[s]} for s in ("dev", "test")}
    for src_name, rows in (("gold_train", splits["train"]), ("big", big_rows)):
        for s in ("dev", "test"):
            hit = sorted({r["page"] for r in rows if (r["series"], base_page(r["page"])) in held_base[s]})
            warnings[f"base_page:{src_name}&{s}"] = {"windows": sum(1 for r in rows if (r["series"], base_page(
                r["page"])) in held_base[s]), "pages": hit}
    warnings["base_page:dev&test"] = len(held_base["dev"] & held_base["test"])
    sent = {s: {x for r in final[s] for x in fact_gate.sentences(r["passage"]) if len(x) >= 40}
            for s in ("train", "dev", "test")}
    for x, y in (("train", "dev"), ("train", "test"), ("dev", "test")):
        warnings[f"sentence>=40ch:{x}&{y}"] = len(sent[x] & sent[y])
    ids = [r["id"] for r in train]
    if len(ids) != len(set(ids)):
        errors.append(f"duplicate ids in train: {len(ids) - len(set(ids))}")

    def share(rows, d):
        return round(sum(1 for r in rows if EMPTY[d](r)) / max(len(rows), 1), 4)
    rec = {"inputs": {str(p): sha(p) for p in (gold_in, gold_audit, big_audit, *big_in.values())},
           "snapshot": str(snap) if snap else None,
           "empty_def": a.empty_def, "empty_share_cap": a.empty_share, "hard_share": a.hard_share,
           "gold_windows": len(gin), "gold_audited": len(gin) - unreviewed, "gold_unreviewed": unreviewed,
           "big_windows": len(baud), "big_eventful": len(eventful), "big_empty_available": empties_avail,
           "big_empty_taken": len(empties), "big_hard_empty_taken": hard_taken,
           "big_taken": len(big_rows), "big_dropped_by_cap": n_big_used - len(big_rows),
           "big_dropped_sentence_overlap": dropped_sent,
           "big_empty_share": round(len(empties) / max(len(big_rows), 1), 4),
           **{s: len(final[s]) for s in SPLITS},
           "train_empty_share": {d: share(train, d) for d in EMPTY},
           "big_empty_share_by_def": {d: share(big_rows, d) for d in EMPTY},
           "train_rows": {k: sum(len(r[k]) for r in train) for k in ("events", "facts", "tags")},
           "train_by_series": dict(sorted(Counter(r["series"] for r in train).items())),
           "train_by_source": dict(sorted(Counter(r["source"] for r in train).items())),
           "train_verbs": dict(Counter(e["verb"] for r in train for e in r["events"]).most_common()),
           "train_relations": dict(Counter(f["relation"] for r in train for f in r["facts"]).most_common()),
           "train_tags": dict(Counter(t["tag"] for r in train for t in r["tags"]).most_common()),
           "train_other_verb_share": round(sum(f["relation"] == "other_verb" for r in train for f in r["facts"]) /
                                           max(sum(len(r["facts"]) for r in train), 1), 4),
           "leaks": leaks, "warnings": warnings, "big_dropped_base_page_overlap": dropped_base,
           "earned_empty_ids_checked": len(earned),
           "system_prompt_chars": len(system), "system_prompt_sha256": hashlib.sha256(system.encode()).hexdigest()}
    return final, rec, errors


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--snapshot", default=None)
    ap.add_argument("--empty-share", type=float, default=0.30)
    ap.add_argument("--hard-share", type=float, default=0.75)
    ap.add_argument("--empty-def", choices=tuple(EMPTY), default="all")
    ap.add_argument("--system-file", default=None)
    ap.add_argument("--short-system", action="store_true", help="the default; kept for the handoff commands")
    ap.add_argument("--allow-unreviewed-gold", action="store_true")
    ap.add_argument("--drop-base-page-overlap", action="store_true",
                    help="leave out big windows whose base page (before '/') is a gold dev/test base page")
    a = ap.parse_args()
    final, rec, errors = compose(a)
    if errors:
        print("COMPOSE FAILED:\n" + "\n".join(errors[:40]) + f"\n... {len(errors)} total")
        return 1
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    for name, rs in final.items():
        with open(out / f"{name}.jsonl", "w") as f:
            for r in rs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    rec["outputs"] = {f"{n}.jsonl": sha(out / f"{n}.jsonl") for n in final}
    (out / "receipt.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False))
    print(json.dumps({k: v for k, v in rec.items() if k not in ("train_relations", "inputs")}, indent=1,
                     ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
