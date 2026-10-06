#!/usr/bin/env python3
"""Untrained-baseline predictions: a base (or base+adapter) Qwen3.5 model on
a window file, one greedy pass, written as {id, events, raw} for
score_subsets.py. Owner 2026-10-07 asked how far the UNTRAINED 9B/4B is
from the trained student on the same gold windows.

    ~/train-env/bin/python tools/train/eval_base.py --model M --in dev_pool.jsonl --out preds.jsonl \
        [--system-file plan/EXTRACTION_PROCEDURE.md --thinking] [--adapter DIR]

--system-file replaces each row's system message (e.g. the procedure doc);
--thinking renders the chat template with enable_thinking=True and parses
the JSON after </think>.
"""
import argparse, json, sys, time
from pathlib import Path
import torch
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
from sft_qwen import stop_ids  # noqa: E402

def parse(text):
    body = text.split("</think>")[-1].strip()
    s, e = body.find("{"), body.rfind("}")
    try:
        d = json.loads(body[s:e + 1]) if s >= 0 and e > s else None
    except ValueError:
        d = None
    ev = d.get("events") if isinstance(d, dict) else None
    return [x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else []

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True); ap.add_argument("--adapter")
    ap.add_argument("--in", dest="inp", required=True); ap.add_argument("--out", required=True)
    ap.add_argument("--system-file"); ap.add_argument("--thinking", action="store_true")
    ap.add_argument("--only-series", default=None, help="comma list, e.g. marvel,mcu")
    ap.add_argument("--batch", type=int, default=8); ap.add_argument("--max-new", type=int, default=1024)
    a = ap.parse_args()
    from transformers import AutoTokenizer, AutoModelForImageTextToText
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
        prompts.append(tok.apply_chat_template(msgs, tokenize=False, add_generation_prompt=True,
                                               enable_thinking=a.thinking))
    order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
    out, t0 = {}, time.time()
    tok.padding_side = "left"
    for b in range(0, len(order), a.batch):
        idx = order[b:b + a.batch]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            g = m.generate(**enc, max_new_tokens=a.max_new, do_sample=False, use_cache=True,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id, eos_token_id=stop_ids(tok))
        for j, i in enumerate(idx):
            text = tok.decode(g[j][enc["input_ids"].shape[1]:], skip_special_tokens=True)
            out[rows[i]["id"]] = {"id": rows[i]["id"], "series": rows[i].get("series"), "events": parse(text), "raw": text[-3000:]}
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(out[r["id"]], ensure_ascii=False) + "\n")
    print(f"{len(rows)} windows in {time.time()-t0:.0f}s -> {a.out}")

if __name__ == "__main__":
    main()
