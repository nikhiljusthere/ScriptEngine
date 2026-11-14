#!/usr/bin/env python3
"""S4 of the per-line side test, label-free: does the series store state the same event on ANOTHER page?
gate.cross_page_agreement groups events by (verb, participant pair as a node set) across pages; it needs a full
extraction to have groups. On a 214-window holdout the predictions form almost no groups among themselves, so each
predicted event triple [verb, s#, o#] is mapped to store nodes (the candidate name is a node name) and looked up in
the store's events (prompt .9 extraction, read-only copy): corroborated = the same (verb, pair) is stated by a store
row whose doc_title is a different page; of those, `agreeing` = the store rows of that group sit in one arc_index.
Self-events (object null) are matched on (verb, subject). Run for the gold projection and for each system.

    python3 tools/train/perline_corroborate.py --data s2data/holdout.jsonl --db COPY.db --perline RUN/holdout_preds.jsonl --v2 seed2.jsonl
"""
import argparse, collections, json, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import score_layers_v2 as sl  # noqa: E402
from perline_build import project  # noqa: E402
from perline_candidates import Resolver  # noqa: E402
from perline_score import parse_lines  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True); ap.add_argument("--db", required=True)
    ap.add_argument("--perline"); ap.add_argument("--v2", action="append", default=[])
    a = ap.parse_args()
    data = [json.loads(l) for l in open(a.data)]
    c = sqlite3.connect(f"file:{a.db}?mode=ro", uri=True)
    node = {nm: i for i, nm in c.execute("select id, name from nodes")}
    R = Resolver(a.db)
    groups = collections.defaultdict(list)
    for v, s, o, page, arc in c.execute("select verb, subject_node, object_node, doc_title, arc_index from events where subject_node is not null"):
        key = (v, frozenset([s, o]) if o is not None else frozenset([s]))
        groups[key].append((page, arc))
    systems = {"gold": ("gold", None)}
    if a.perline:
        systems["perline"] = ("perline", {json.loads(l)["id"]: json.loads(l).get("raw", "") for l in open(a.perline)})
    for p in a.v2:
        systems["v2:" + Path(p).stem] = ("v2", sl.load(p))
    for name, (kind, preds) in systems.items():
        for split in ("all", "dev"):
            C = collections.Counter()
            for r in data:
                if split != "all" and r["split"] != split: continue
                cands = r["candidates"]
                if kind == "gold":
                    lines = r["target"]["lines"]
                elif kind == "perline":
                    lines = list(parse_lines(preds.get(r["id"], ""))[0].values())
                else:
                    p = preds.get(r["id"], {"events": [], "facts": [], "tags": []})
                    lines = project(dict(r, **{k: p[k] for k in ("events", "facts", "tags")}), cands, r["candidate_ids"], R)[0]["lines"]
                for ln in lines:
                    for t in ln.get("events") or []:
                        if not (isinstance(t, list) and len(t) == 3): continue
                        v, s, o = t
                        try:
                            sn = node.get(cands[int(s) - 1]); on = node.get(cands[int(o) - 1]) if o else None
                        except (ValueError, IndexError, TypeError):
                            C["bad_number"] += 1; continue
                        C["triples"] += 1
                        if sn is None or (o and on is None): C["no_node"] += 1; continue
                        g = groups.get((v, frozenset([sn, on]) if on else frozenset([sn])), [])
                        other = [x for x in g if x[0] != r["page"] and x[0].split("/")[0] != r["page"].split("/")[0]]
                        if other:
                            C["corroborated"] += 1
                            C["agreeing"] += len({x[1] for x in g if x[1] is not None}) <= 1
            t = max(C["triples"], 1)
            print(f"{name:28s} {split:4s} triples {C['triples']:4d}  corroborated on another page {C['corroborated']:4d} "
                  f"({C['corroborated']/t:.3f})  of those in one arc {C['agreeing']}  no node {C['no_node']}  bad number {C['bad_number']}")


if __name__ == "__main__":
    main()
