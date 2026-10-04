#!/usr/bin/env python3
"""Score the student (base + adapter) on dev windows and the blind
passage-unit test gold (U-WP6, train-env).

    python tools/train/eval_student.py --model <base> --adapter DIR \
        [--dev series/jjk/training/student/dev.jsonl] \
        [--test series/jjk/training/recall_gold_v3/gold_test_v4.gen2.json] \
        [--out preds.jsonl] [--max-new 1536] [--batch 8]
    python tools/train/eval_student.py --baseline-teacher

Window prompts are byte-identical to production (system + user via
events.system_prompt / events._TEMPLATE, enable_thinking=False).
Scoring: (a) dev windows -> window-level event P/R/F1; (b) the test
gold -> every covering window is run, predictions unioned per passage
(tools/eval_extraction.py passage scoring). Both report per-verb
P/R/F1, the verb confusion, JSON-validity, quote-verbatim and
windows/s. --baseline-teacher prints the known teacher numbers for
comparison and scores nothing.
"""
import argparse, json, sys, time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "train"))

from scriptengine.ingest.events import _TEMPLATE, system_prompt  # noqa: E402

SNAP = ("/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-4B/snapshots/"
        "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a")

TEACHER = {
    "note": "known labeler numbers (Qwen 27B/35B via :8091), not re-run here",
    "dev_window_level": {"p": "see plan/JJK_STUDENT_TRAINING.md", "r": "see plan/JJK_STUDENT_TRAINING.md"},
    "teacher_f1_reference": "the 35B labeler's adjudicated-gold agreement from U-WP4/5 receipts",
}


def window_row(unit, w, series="jjk"):
    text = unit["passage"][w["span"][0]:w["span"][1]]
    user = _TEMPLATE.format(series=series, page=unit["page"],
                            section=unit.get("section", ""), passage=text)
    return {"id": w["id"], "page": unit["page"],
            "section": unit.get("section", ""), "passage": text,
            "messages": [{"role": "system", "content": system_prompt(store_free())},
                         {"role": "user", "content": user}]}


_VERBS = None
def store_free():
    """The frozen verb list the set receipt pins (no store needed)."""
    global _VERBS
    if _VERBS is None:
        receipt = json.load(open(ROOT / "series/jjk/training/student/receipt.json"))
        _VERBS = frozenset(receipt["eventive_verbs"])
    return _VERBS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=SNAP)
    ap.add_argument("--adapter")
    ap.add_argument("--dev", default=str(ROOT / "series/jjk/training/student/dev.jsonl"))
    ap.add_argument("--test", default=str(ROOT / "series/jjk/training/recall_gold_v3/gold_test_v4.gen2.json"))
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--out")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=None)
    ap.add_argument("--baseline-teacher", action="store_true")
    a = ap.parse_args()
    if a.baseline_teacher:
        print(json.dumps(TEACHER, indent=1))
        return

    import torch
    from transformers import AutoTokenizer
    try:
        from transformers import AutoModelForImageTextToText as AutoMM
    except ImportError:
        AutoMM = None
    from eval_extraction import load_gold, score
    from sft_qwen import render_prompt, dev_generate

    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    from transformers import AutoModelForCausalLM
    try:
        model = (AutoMM.from_pretrained if AutoMM else AutoModelForCausalLM.from_pretrained)(
            a.model, dtype=torch.bfloat16, device_map="cuda")
    except Exception:
        model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda")
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter)
        model = model.merge_and_unload()
    model.eval()

    report = {}
    if a.dev and Path(a.dev).exists():
        rows = [json.loads(l) for l in open(a.dev)]
        max_new = a.max_new
        if max_new is None:
            longest = max(len(r["messages"][2]["content"]) for r in rows)
            max_new = int(longest * 1.5 / 3) + 32
            max_new = min(max(max_new, 256), 2048)
        t0 = time.time()
        preds, wps = dev_generate(model, tok, rows, batch=a.batch, max_new=max_new)
        s, _ = score(load_gold(Path(a.dev)), preds)
        report["dev"] = {**{k: s[k] for k in ("kind", "f1", "precision", "core_recall",
                                              "per_verb", "confusion", "json_validity",
                                              "quote_verbatim")},
                         "windows_per_s": round(wps, 2)}

    if a.test and Path(a.test).exists():
        gold_units = load_gold(Path(a.test))
        rows, seen = [], set()
        for unit in gold_units.values():
            for w in unit["windows"]:
                if w["id"] in seen:
                    continue
                seen.add(w["id"])
                rows.append(window_row(unit, w, a.series))
        if a.max_new is not None:
            max_new = a.max_new
        else:
            core_lens = [len(json.dumps({"events": u.get("core", []) + u.get("optional", [])}))
                         for u in gold_units.values()]
            max_new = int(max(core_lens or [512]) * 1.5 / 3) + 64
            max_new = min(max(max_new, 256), 2048)
        preds, wps = dev_generate(model, tok, rows, batch=a.batch, max_new=max_new)
        s, _ = score(gold_units, preds)
        report["test_passage_union"] = {**{k: s.get(k) for k in ("kind", "f1", "precision", "core_recall",
                                              "per_verb", "confusion", "json_validity",
                                              "quote_verbatim", "discarded_outside_slice")},
                         "windows_per_s": round(wps, 2), "windows_run": len(rows)}
        if a.out:
            with open(a.out, "w") as f:
                for wid, rec in preds.items():
                    f.write(json.dumps({"id": wid, **rec}) + "\n")

    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
