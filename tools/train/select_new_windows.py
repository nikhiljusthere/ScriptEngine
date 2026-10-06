#!/usr/bin/env python3
"""Select NEW Marvel/MCU windows from the biggest unused pages for the
single-pass 35B labeling run (owner 2026-10-06: "run the ninfer 35B again on
a new set of MCU/Marvel and their biggest pages ... prepare a dataset of
12000 windows").

Every window is a production read unit (emit_windows.build_universe_windows,
the extractor's own read set). Excluded, so every page is new: the series'
held-out pages, every pool_in/test_in page and window, every page of the
universal student splits, and any window whose text already appears in a
labeled set. Pages are ranked by their window count (biggest first); each
page contributes at most --cap-trigger windows that carry an event trigger
word and --cap-plain that do not (seeded), so the biggest pages do not
swamp the set. Trigger windows are ~72% eventful and plain ones ~14% on the
reviewed Marvel/MCU pools, so the default 12,000 + 2,000 mix leaves room to
compose ~8,400 eventful + ~3,600 empty after labeling.

    scriptengine/.venv/bin/python tools/train/select_new_windows.py \
        [--trigger 12000] [--plain 2000] [--marvel-share 0.55]
        -> series/<s>/training/labels/big_in.jsonl (+ big_receipt.json)
"""
import argparse
import json
import random
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools" / "train"))
from emit_windows import build_universe_windows, holdout_pages  # noqa: E402
from scriptengine.ingest.events import _TEMPLATE  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

SEED = 20261007
TRIG = re.compile(
    r"\b(attack\w*|fought|fights?|battl\w*|clash\w*|defeat\w*|kill\w*|murder\w*|slain|execut\w*|"
    r"captur\w*|kidnap\w*|abduct\w*|arrest\w*|imprison\w*|hostage|escap\w*|fled|flee\w*|rescu\w*|"
    r"sav(e|ed|es|ing)\b|freed|betray\w*|seal\w*|trapp\w*|confront\w*|encounter\w*|met\b|meets|"
    r"visit\w*|arriv\w*|return(ed|s)? to|travel\w* to|went to|left\b|depart\w*|awak\w*|woke|"
    r"reviv\w*|knock\w* out|overpower\w*|ambush\w*|stabb\w*|shot\b|shoots|punch\w*|strik\w*|"
    r"struck|subdu\w*|caught)", re.I)


def jl(p):
    return [json.loads(l) for l in open(p)] if Path(p).exists() else []


def used(series):
    """Pages, ids and texts already labeled anywhere for this series."""
    lab = ROOT / "series" / series / "training" / "labels"
    pages, ids, texts = set(), set(), set()
    for name in ("pool_in.jsonl", "test_in.jsonl"):
        for r in jl(lab / name):
            pages.add(r["page"]); ids.add(r["id"])
            texts.add(r["messages"][1]["content"].split("Passage:\n", 1)[1].strip())
    for split in ("train", "dev", "test"):
        for r in jl(ROOT / "series/universal/training/student" / f"{split}.jsonl"):
            if r["series"] == series:
                pages.add(r["page"]); ids.add(r["id"]); texts.add(r["passage"].strip())
    pages |= holdout_pages(ROOT / "series" / series)
    return pages, ids, texts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trigger", type=int, default=12000)
    ap.add_argument("--plain", type=int, default=2000)
    ap.add_argument("--marvel-share", type=float, default=0.55)
    ap.add_argument("--cap-trigger", type=int, default=40)
    ap.add_argument("--cap-plain", type=int, default=8)
    ap.add_argument("--min-chars", type=int, default=60)
    # "biggest pages" means the long narrative ones: index/list/gallery/
    # credit/quote pages are big only because they enumerate (Marvel's
    # "Character Index/C" ranked 2nd by size) and teach nothing but empties
    ap.add_argument("--exclude-title", default=r"(?i)(index|listing|\blist of\b|/gallery|/credits|"
                    r"/quote|/appearances|release order|/trivia|/behind the scenes|/images|"
                    r"/soundtrack|/transcript|/recap|/members|disambiguation)")
    a = ap.parse_args()
    receipt = {}
    for series, share in (("marvel", a.marvel_share), ("mcu", 1 - a.marvel_share)):
        need_t, need_p = round(a.trigger * share), round(a.plain * share)
        system = jl(ROOT / "series" / series / "training/labels/pool_in.jsonl")[0]["messages"][0]["content"]
        bad_pages, bad_ids, bad_texts = used(series)
        with FactStore(ROOT / "series" / series / "facts.db") as store:
            windows, _by_key, _dups = build_universe_windows(store)
        by_page = defaultdict(list)
        seen_text = set(bad_texts)
        for w in windows:
            t = w.text.strip()
            if w.page in bad_pages or w.id in bad_ids or t in seen_text or len(t) < a.min_chars:
                continue
            seen_text.add(t)
            by_page[w.page].append(w)
        title_bad = re.compile(a.exclude_title)
        ranked = sorted((p for p in by_page if not title_bad.search(p)), key=lambda p: (-len(by_page[p]), p))
        rng = random.Random(f"{SEED}-{series}")
        picks, n_t, n_p, pages_used = [], 0, 0, []
        for page in ranked:
            if n_t >= need_t and n_p >= need_p:
                break
            ws = by_page[page]
            trig = [w for w in ws if TRIG.search(w.text)]
            plain = [w for w in ws if not TRIG.search(w.text)]
            take_t = rng.sample(trig, min(len(trig), a.cap_trigger, max(0, need_t - n_t)))
            take_p = rng.sample(plain, min(len(plain), a.cap_plain, max(0, need_p - n_p)))
            if not take_t and not take_p:
                continue
            pages_used.append((page, len(ws), len(take_t), len(take_p)))
            for w, kind in [(w, "trigger") for w in take_t] + [(w, "plain") for w in take_p]:
                section = "" if w.section == "lead" else w.section
                user = _TEMPLATE.format(series=series, page=w.page, section=section, passage=w.text)
                picks.append({"id": w.id, "page": w.page, "section": section, "kind": kind,
                              "page_windows": len(ws),
                              "messages": [{"role": "system", "content": system},
                                           {"role": "user", "content": user}]})
            n_t += len(take_t); n_p += len(take_p)
        out = ROOT / "series" / series / "training/labels/big_in.jsonl"
        with open(out, "w") as f:
            for r in picks:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        receipt[series] = {"windows": len(picks), "trigger": n_t, "plain": n_p,
                           "pages": len(pages_used), "candidate_pages": len(ranked),
                           "biggest_pages": pages_used[:10],
                           "smallest_page_used_windows": pages_used[-1][1] if pages_used else None,
                           "out": str(out)}
        print(series, json.dumps({k: v for k, v in receipt[series].items() if k != "biggest_pages"}), flush=True)
    (ROOT / "series/mcu/training/labels/big_receipt.json").write_text(json.dumps(receipt, indent=1))


if __name__ == "__main__":
    main()
