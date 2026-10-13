"""recon_rows.py b [b...] -> the final rows of those windows with full quotes, in edit-file syntax
(E = event, F = fact, T = tag); quotes inside a sentence shared with another window of the same
component are marked with *."""
import sys
from recon_lib import bv, load
ids, sents = load()
a2 = bv.audit2()
bs = [int(x) for x in sys.argv[1:]]
for b in bs:
    others = {bv.big_flags.norm(s) for o in bs if o != b for s in sents[o] if len(s) > 60}
    shared = [s for s in sents[b] if bv.big_flags.norm(s) in others]
    mk = lambda q: "*" if q and any(q in s for s in shared) else " "
    r = a2.get(ids[b - 1], {})
    print(f"--- rows b{b}")
    for e in r.get("events", []):
        print(f" {mk(e['quote'])}E {e['subject']}|{e['verb']}|{e['object'] or '-'}|{e['quote']}")
    for f in r.get("facts", []):
        q = f"|{f.get('modality')}|{f.get('certainty')}|{f.get('asserted_by') or '-'}" if f.get("modality") not in (None, "actual") or f.get("asserted_by") or f.get("certainty") not in (None, "stated") else ""
        print(f" {mk(f['quote'])}F {f['subject']}|{f['relation']}|{f['object'] or '-'}|{f['quote']}{q}")
    for t in r.get("tags", []):
        print(f" {mk(t['quote'])}T {t['tag']}|{t['quote'][:90]}")
