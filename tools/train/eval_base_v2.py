#!/usr/bin/env python3
"""v2 predictions (events + facts + tags) of a base or base+adapter Qwen3.5 model on a window file, one
greedy pass, written as {id, series, events, facts, tags, valid, raw} for score_layers_v2.py (and, for
the event layer, score_subsets.py, which reads `events`).

eval_base.py stays as it was for the v1 runs. It cannot serve v2: it parses the event layer only and
keeps raw[-3000:] (the head of a long v2 answer, where the events are, is cut), and its --max-new 1024
is below the v2 test answers (2026-11-03 dry run, 9B tokenizer: test answer p99 1,732, max 2,884 tokens;
15 of 292 over 1,024). Default --max-new here is 4096.

    ~/train-env/bin/python tools/train/eval_base_v2.py --model M --adapter BEST --in test.jsonl --out preds.jsonl \
        [--only-series marvel,mcu] [--system-file F] [--batch 8] [--max-new 4096]

GPU-only (the four-gate GPU rule); written 2026-11-03 without a GPU run: smoke it on a few windows first.
"""
import argparse
import json
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
LAYERS = ("events", "facts", "tags")


def parse(text):
    """Model text -> ({events, facts, tags}, valid). Same body rule as sft_qwen.dev_generate: the text
    after </think>, code fences stripped, first '{' to last '}'. valid = a JSON object with three lists."""
    body = (text or "").split("</think>")[-1].strip()
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
    s, e = body.find("{"), body.rfind("}")
    try:
        d = json.loads(body[s:e + 1]) if s >= 0 and e > s else None
    except ValueError:
        d = None
    if not isinstance(d, dict):
        return {k: [] for k in LAYERS}, False
    out = {k: [x for x in d.get(k) or [] if isinstance(x, dict)] if isinstance(d.get(k), list) else []
           for k in LAYERS}
    return out, all(isinstance(d.get(k), list) for k in LAYERS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--system-file")
    ap.add_argument("--only-series", default=None, help="comma list, e.g. marvel,mcu")
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=4096)
    a = ap.parse_args()
    import torch
    from transformers import AutoTokenizer, AutoModelForImageTextToText
    from sft_qwen import render_prompt, stop_ids
    rows = [json.loads(l) for l in open(a.inp)]
    if a.only_series:
        keep = set(a.only_series.split(","))
        rows = [r for r in rows if r.get("series") in keep]
    sysmsg = Path(a.system_file).read_text() if a.system_file else None
    tok = AutoTokenizer.from_pretrained(a.model)
    m = AutoModelForImageTextToText.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda")
    if a.adapter:
        from peft import PeftModel
        m = PeftModel.from_pretrained(m, a.adapter)
    m.eval()
    prompts = []
    for r in rows:
        msgs = r["messages"][:2]
        if sysmsg:
            msgs = [{"role": "system", "content": sysmsg}, msgs[1]]
        prompts.append(render_prompt(tok, msgs))  # enable_thinking=False, the render the student trained on
    order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
    out, t0, cut = {}, time.time(), 0
    tok.padding_side = "left"
    for b in range(0, len(order), a.batch):
        idx = order[b:b + a.batch]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            g = m.generate(**enc, max_new_tokens=a.max_new, do_sample=False, use_cache=True,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id, eos_token_id=stop_ids(tok))
        for j, i in enumerate(idx):
            new = g[j][enc["input_ids"].shape[1]:]
            n_new = int((new != (tok.pad_token_id if tok.pad_token_id is not None else -1)).sum())
            cut += n_new >= a.max_new
            text = tok.decode(new, skip_special_tokens=True)
            layers, valid = parse(text)
            out[rows[i]["id"]] = {"id": rows[i]["id"], "series": rows[i].get("series"), **layers,
                                  "valid": valid, "raw": text}
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(out[r["id"]], ensure_ascii=False) + "\n")
    print(f"{len(rows)} windows in {time.time() - t0:.0f}s -> {a.out}; "
          f"valid {sum(v['valid'] for v in out.values())}/{len(out)}; hit --max-new {cut}")


if __name__ == "__main__":
    main()
