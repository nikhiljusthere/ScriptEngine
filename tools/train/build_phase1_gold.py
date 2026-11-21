"""Convert verify_row_wiki.py output + candidate files into export-shaped gold
records suitable for build_trainset.py.

For each window in the verifier output:
- All rows answered, ≥1 ok=yes → write gold window with only yes rows, tier=gold.
- All rows answered, 0 events → write gold window with empty events (tier=gold).
- Any unanswered row → mark as pending.

Usage:
    python tools/train/build_phase1_gold.py \
      --verify <verifier.jsonl> \
      --cand <cand_files...> \
      --data <train.jsonl> \
      --out <gold.jsonl> [--stats]
"""
import argparse, json, sys
from collections import Counter
from pathlib import Path


def load_cands(cand_paths):
    """Load candidate events indexed by id."""
    result = {}
    for cp in cand_paths:
        for l in open(cp):
            r = json.loads(l)
            # Accept both pre-verified (ok:true) and raw drafts (no ok field)
            if "ok" not in r or r["ok"] is True:
                result[r["id"]] = r["events"]
    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", required=True)
    ap.add_argument("--cand", nargs="+", required=True)
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()

    cands = load_cands(a.cand)
    rows_data = {json.loads(l)["id"]: json.loads(l) for l in open(a.data)}

    gold_windows = []
    empty_gold = []
    pending = []
    unanswered_total = 0
    stats = Counter()

    for l in open(a.verify):
        v = json.loads(l.strip())
        wid = v["id"]
        ver_rows = v.get("rows", [])
        orig_events = cands.get(wid, [])

        if not ver_rows:
            # No candidates at all — write as verified empty window
            orig = rows_data.get(wid, {})
            msgs = list(orig.get("messages", []))
            if len(msgs) >= 3:
                msgs[2]["content"] = json.dumps({"events": []}, ensure_ascii=False)
            else:
                # Ensure 3-message structure
                while len(msgs) < 3:
                    msgs.append({"role": ["assistant"][len(msgs)-1], "content": ""})
            
            gold_window = {
                "id": wid,
                "tier": "gold",
                "messages": msgs,
            }
            gold_windows.append(gold_window)
            empty_gold.append(wid)
            stats["windows_empty_gold"] += 1
            continue

        yes_rows = []
        all_answered = True
        for vr in ver_rows:
            idx = vr["n"]
            evt = orig_events[idx] if idx < len(orig_events) else {}
            if vr.get("ok") == 1:
                yes_rows.append(evt)
                stats["verb_yes"] += 1
            elif vr.get("ok") == 0:
                stats["verb_no"] += 1
            else:
                all_answered = False
                unanswered_total += 1

        if not all_answered:
            pending.append(wid)
            stats["windows_pending"] += 1
            continue

        if yes_rows:
            stats["windows_with_events"] += 1
        else:
            stats["windows_rejected_to_empty"] += 1
            empty_gold.append(wid)

        orig = rows_data.get(wid, {})
        msgs = list(orig.get("messages", []))
        
        # Keep only the four canonical event fields (strip verify artifacts)
        CLEAN_FIELDS = {"quote", "subject", "verb", "object"}
        clean_yes = [{k: e[k] for k in CLEAN_FIELDS if k in e} for e in yes_rows]
        
        msgs[2]["content"] = json.dumps({"events": clean_yes}, ensure_ascii=False)
        
        gold_window = {
            "id": wid,
            "tier": "gold",
            "messages": msgs,
        }
        gold_windows.append(gold_window)

    # Deduplicate by id (first occurrence wins)
    seen = set()
    unique = []
    for g in gold_windows:
        if g["id"] not in seen:
            seen.add(g["id"])
            unique.append(g)

    with open(a.out, "w") as f:
        for g in unique:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

    print(f"Gold windows written: {len(unique)}")
    print(f"Pending (unanswered): {len(pending)}")
    print(f"Stats: yes={stats['verb_yes']}, no={stats['verb_no']}, unanswered={unanswered_total}")
    print(f"  Windows with events: {stats['windows_with_events']}")
    print(f"  Windows empty (originally empty): {stats['windows_empty_gold']}")
    print(f"  Windows empty (rejection cleanup): {stats['windows_rejected_to_empty']}")

    if a.stats and stats["verb_yes"] + stats["verb_no"] > 0:
        total = stats["verb_yes"] + stats["verb_no"]
        print(f"\nRow acceptance: {stats['verb_yes']}/{total} = {stats['verb_yes']/total*100:.1f}%")


if __name__ == "__main__":
    main()
