#!/usr/bin/env python3
"""S2 of the per-line side test: re-project v2 window labels onto the per-line target of `meaning`
(reports/comprehension/COMPREHENSION_REMAINDER.md §5: per sentence a class, whether it is an event, and who
takes part). Input to the model: the numbered sentences and a numbered candidate list from the series store
(perline_candidates.candidates). Output, JSON only:
  {"lines": [{"n": 1, "class": "event", "people": [3, 7], "events": [["fought", 3, 7]]}, ...]}
No free-text names: an end not on the candidate list is dropped (S1: 98.0% of JJK gold ends are on it).

Re-projection (deterministic, from the window's own rows on that sentence):
  class  event          an event row, or a fact in the interaction / knowledge / other_verb groups, or a
                        state-change relation (dies, wounded, healed, kidnapped, born, transformed_into,
                        gained_power, lost_power) with modality actual; or a crowd_end / no_doer tag
         standing state any other fact row (relationship, identity, possession, located_at, resides_at, aged)
         trait          a capability / attire / apposition tag
         trivia         every other sentence (production, citation, list_header, dialogue, deictic, no_relation)
  people every candidate number matching an end of those rows; events: [verb, subject#, object# or null].

    python3 tools/train/perline_build.py --train-src student_v2_short/train.jsonl --jjk-holdout DIR/holdout.jsonl \
        --jjk-train-ids DIR/train_ids.json --stores /home/goblin/ScriptEngine/series --jjk-db COPY.db --out DIR
"""
import argparse, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools")); sys.path.insert(0, str(ROOT / "tools" / "train"))
import eval_extraction as ee  # noqa: E402
import fact_gate  # noqa: E402
import score_layers_v2 as sl  # noqa: E402
from perline_candidates import candidates, load_store  # noqa: E402

GROUP = {r: g for g, rels in sl.GROUPS.items() for r in rels}
CHANGE = {"dies", "wounded", "healed", "kidnapped", "born", "transformed_into", "gained_power", "lost_power"}
SYSTEM = ("You read a fiction-wiki passage line by line. For every numbered sentence give its class (event, "
          "standing state, trait, trivia), the people and things that take part as numbers from the candidate "
          "list, and each act among fought, defeated, killed, captured, escaped, saved, betrayed, sealed, met, "
          "arrived, departed, awakened as [verb, subject number, object number or null]. Answer JSON only: "
          "{\"lines\": [{\"n\": 1, \"class\": \"...\", \"people\": [...], \"events\": [...]}, ...]}. "
          "Use only numbers from the list; leave out anyone not on it.")


def on(q, s):
    q = (q or "").strip()
    return bool(q) and (q in s or s in q)


def project(row, cands, forms):
    sents = fact_gate.sentences(row["passage"])
    def num(name):
        if not name: return None
        for i, fs in enumerate(forms, 1):
            if any(ee.same(name, x) for x in fs): return i
        return None
    lines = []
    for n, s in enumerate(sents, 1):
        ev = [e for e in row["events"] if on(e.get("quote"), s)]
        fa = [f for f in row["facts"] if on(f.get("quote"), s)]
        tg = [t.get("tag") for t in row["tags"] if on(t.get("quote"), s)]
        if ev or any(GROUP.get(f.get("relation")) in ("interaction", "knowledge", "other_verb")
                     or (f.get("relation") in CHANGE and (f.get("modality") or "actual") == "actual") for f in fa) \
                or {"crowd_end", "no_doer"} & set(tg):
            cls = "event"
        elif fa:
            cls = "standing state"
        elif {"capability", "attire", "apposition"} & set(tg):
            cls = "trait"
        else:
            cls = "trivia"
        people = []
        for nm in [e.get(k) for e in ev for k in ("subject", "object")] + [f.get("subject") for f in fa] + \
                  [f.get("object") for f in fa if f.get("relation") != "other_verb"]:
            k = num(nm)
            if k and k not in people: people.append(k)
        evs = []
        for e in ev:
            sn, on_ = num(e.get("subject")), num(e.get("object"))
            if sn and [e["verb"], sn, on_] not in evs: evs.append([e["verb"], sn, on_])
        lines.append({"n": n, "class": cls, "people": sorted(people), "events": evs})
    user = (f"Series: {row['series']}\nPage: {row['page']}\nSection: {row.get('section', '')}\n\nCandidates:\n" +
            "\n".join(f"{i}. {c}" for i, c in enumerate(cands, 1)) + "\n\nSentences:\n" +
            "\n".join(f"[{i}] {s}" for i, s in enumerate(sents, 1)))
    return {"lines": lines}, user


def build(row, store, names_of):
    cand_ids = candidates(row, store)
    names, al = store[0], store[1]
    cands = [names[n] for n in cand_ids]
    forms = [{names[n]} | al.get(n, set()) for n in cand_ids]
    target, user = project(row, cands, forms)
    out = {k: row[k] for k in ("id", "series", "page", "section", "passage", "events", "facts", "tags")}
    out.update(candidates=cands, target=target, split=row.get("split", "train"),
               messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user},
                         {"role": "assistant", "content": json.dumps(target, ensure_ascii=False)}])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train-src", required=True); ap.add_argument("--jjk-holdout", required=True)
    ap.add_argument("--jjk-train-ids", required=True); ap.add_argument("--stores", required=True)
    ap.add_argument("--jjk-db", required=True); ap.add_argument("--out", required=True)
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    jjk_keep = set(json.load(open(a.jjk_train_ids)))
    stores, n, skipped = {}, 0, {}
    def store_for(s):
        if s not in stores:
            db = a.jjk_db if s == "jjk" else f"{a.stores}/{s}/facts.db"
            try:
                stores[s] = load_store(f"{db}?immutable=1" if s != "jjk" else db)
            except Exception as e:
                stores[s] = None; skipped[s] = str(e)[:120]
        return stores[s]
    with open(out / "train.jsonl", "w") as w:
        for l in open(a.train_src):
            r = json.loads(l)
            if r["series"] in ("marvel", "mcu") or r["source"] != "gold_v2": continue
            if r["series"] == "jjk" and r["id"] not in jjk_keep: continue
            st = store_for(r["series"])
            if st is None: continue
            w.write(json.dumps(build(r, st, None), ensure_ascii=False) + "\n"); n += 1
    m = 0
    with open(out / "holdout.jsonl", "w") as w:
        for l in open(a.jjk_holdout):
            r = json.loads(l); w.write(json.dumps(build(r, store_for("jjk"), None), ensure_ascii=False) + "\n"); m += 1
    rep = {"train": n, "holdout": m, "stores": {s: v is not None for s, v in stores.items()}, "store_errors": skipped}
    json.dump(rep, open(out / "build_report.json", "w"), indent=1); print(json.dumps(rep))


if __name__ == "__main__":
    main()
