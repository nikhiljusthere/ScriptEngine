"""Shared helpers for reconciling overlapping big-v2 windows (2026-10-13).

Windows that share >=2 sentences longer than 60 chars must carry the same final rows
(events, facts, tags) for the shared part. Run with the main venv and
SCRIPTENGINE_ROOT=/home/goblin/ScriptEngine (recon.sh does both)."""
import sys
from collections import Counter
sys.path.insert(0, "/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags/tools/train")
import big_review_v2 as bv  # noqa: E402

bf, br = bv.big_flags, bv.br
RECON = bv.BIG / "recon"


def load():
    ids = bv.order()
    pas = br.passages()
    sents = {b: bf.sentences(pas[i]) for b, i in enumerate(ids, 1)}
    return ids, sents


def overlap_pairs(sents):
    sent_of = {}
    for b, ss in sents.items():
        for x in ss:
            if len(x) > 60:
                sent_of.setdefault(bf.norm(x), set()).add(b)
    pairs = Counter()
    for lst in sent_of.values():
        lst = sorted(lst)
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                pairs[(lst[x], lst[y])] += 1
    return {p: n for p, n in pairs.items() if n >= 2}


def layer_keys(rec, shared):
    inq = lambda q: bool(q) and any(q in s for s in shared)
    ev = {(e["subject"], e["verb"], e["object"]) for e in rec.get("events", []) if inq(e.get("quote"))}
    fa = {(f["subject"], f["relation"], f["object"], f.get("modality"), f.get("asserted_by"))
          for f in rec.get("facts", []) if inq(f.get("quote"))}
    tg = {(t["tag"], bf.norm(t["quote"])[:40]) for t in rec.get("tags", []) if inq(t.get("quote"))}
    return ev, fa, tg


def pair_diff(a, b, ids, sents, a2):
    """[(layer, only_a, only_b)] for the shared sentences of windows a<b (empty = consistent)."""
    nb = {bf.norm(y) for y in sents[b]}
    sa = [x for x in sents[a] if bf.norm(x) in nb]
    na = {bf.norm(x) for x in sa}
    sb = [y for y in sents[b] if bf.norm(y) in na]
    ka = layer_keys(a2.get(ids[a - 1], {}), sa)
    kb = layer_keys(a2.get(ids[b - 1], {}), sb)
    return [(n, sorted(x - y, key=str), sorted(y - x, key=str))
            for n, x, y in zip(("events", "facts", "tags"), ka, kb) if x != y]
