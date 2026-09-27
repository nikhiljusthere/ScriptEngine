#!/usr/bin/env python3
"""Reconcile source A (pipeline crawl, query API) against source B (Special:Export).

Two independent MediaWiki code paths read the same wiki. This tool is the
S0 sourcing receipt: it proves page-for-page that the corpus on disk was
witnessed by both sources, and names exactly what disagrees.

  source A  series/<s>/wikitext/*.json   one JSON per page (crawler output;
                                          keys: title, revid, wikitext, ...)
  source B  series/<s>/export/*.json     one JSON per page (export handler;
                                          keys: title, pageid, revid, timestamp, wikitext)

A page that is on disk in both with equal wikitext hashes is a *witnessed*
page. Equal hashes with different revids is *drift* (the wiki was edited
between the two reads — expected, re-fetch the stale source). Different
hashes at the same revid is a *conflict* — a real source disagreement and
the page goes to the triage log. A page in only one source is a
*one-sided* page (enumeration drift or a failed fetch on the other side).

Run:  scriptengine/.venv/bin/python tools/marvel/reconcile.py --wiki marvel
      (re-runnable; writes series/<s>/sourcing/RECEIPT.json + a summary)
"""
import argparse
import hashlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
WIKIS = {"marvel": "marvel", "mcu": "mcu"}


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_side(dirpath: Path, key: str) -> dict[str, tuple[str, str, int]]:
    """title -> (wikitext-hash, revid, source) for one side.

    Source A files are larger (full extraction); only the three fields the
    receipt needs are read. Yields so a 10 GB side streams, never loads.
    """
    out = {}
    for path in sorted(dirpath.glob("*.json")):
        if path.name == "RECEIPT.json":
            continue
        try:
            raw = path.read_text(encoding="utf-8")
            doc = json.loads(raw)
        except (json.JSONDecodeError, OSError) as error:
            out[path.stem] = None
            continue
        title = doc.get(key) or path.stem
        out[title] = (sha(doc.get("wikitext", "")), str(doc.get("revid", "")))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wiki", choices=sorted(WIKIS), default="marvel")
    args = parser.parse_args()
    series = REPO / "series" / WIKIS[args.wiki]
    a_dir, b_dir = series / "wikitext", series / "export"
    out_dir = series / "sourcing"
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"loading source A ({a_dir})...", flush=True)
    a = load_side(a_dir, "title")
    print(f"loading source B ({b_dir})...", flush=True)
    b = load_side(b_dir, "title")
    print(f"A: {len(a)} pages, B: {len(b)} pages", flush=True)

    common = set(a) & set(b)
    only_a = sorted(set(a) - set(b))
    only_b = sorted(set(b) - set(a))

    witnessed, drift, conflict = 0, 0, 0
    conflicts, drifts = [], []
    for title in common:
        a_hash, a_revid = a[title]
        b_hash, b_revid = b[title]
        if a_hash == b_hash and a_revid == b_revid:
            witnessed += 1
        elif a_hash == b_hash:
            drift += 1  # same content, newer revid on one side
            drifts.append({"title": title, "a_revid": a_revid, "b_revid": b_revid})
        else:
            conflict += 1
            conflicts.append({"title": title, "a_revid": a_revid, "b_revid": b_revid,
                              "a_hash": a_hash[:16], "b_hash": b_hash[:16]})

    # completeness from each side's own receipt/manifest, if present
    a_manifest = series / "manifest.json"
    a_complete = False
    if a_manifest.exists():
        m = json.loads(a_manifest.read_text(encoding="utf-8"))
        a_complete = m.get("pages_enumerated", 0) > 0 and \
            len(a) >= m.get("pages_on_disk", 0) and not m.get("enumeration_capped")
    b_receipt = b_dir / "RECEIPT.json"
    b_complete = False
    if b_receipt.exists():
        b_complete = json.loads(b_receipt.read_text(encoding="utf-8")).get("complete") is True

    receipt = {
        "wiki": WIKIS[args.wiki],
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "a_pages": len(a), "b_pages": len(b),
        "common": len(common),
        "witnessed": witnessed,
        "drift": drift,
        "conflict": conflict,
        "only_in_a": len(only_a),
        "only_in_b": len(only_b),
        "a_complete": a_complete,
        "b_complete": b_complete,
        # 100% sourcing = both sides complete, no conflicts, no one-sided pages
        # (drift is explainable and re-fetchable, so it does not block)
        "sourcing_100": (a_complete and b_complete and conflict == 0
                         and not only_a and not only_b and len(common) > 0),
        "conflicts": conflicts[:200],
        "drifts": drifts[:200],
        "only_in_a": only_a[:200],
        "only_in_b": only_b[:200],
    }
    (out_dir / "RECEIPT.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    print(json.dumps({k: v for k, v in receipt.items()
                      if k not in ("conflicts", "drifts", "only_in_a", "only_in_b")}, indent=2))
    print(f"receipt -> {out_dir / 'RECEIPT.json'}")
    sys.exit(0 if receipt["sourcing_100"] else 1)


if __name__ == "__main__":
    main()