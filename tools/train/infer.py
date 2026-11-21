"""Run a (base or LoRA-adapted) causal LM over dataset windows; write
{"id", "events", "raw"} per line. Uses the dataset's own system + user
messages, thinking off, greedy. Runs in ~/train-env (not the engine venv).

    python tools/train/infer.py --model <hf id or path> [--adapter DIR] \
        --data series/jjk/training/v1/test.jsonl --ids ids.json --out pred.jsonl
"""
import argparse, json, re, sys, time
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


def parse(text):
    body = text.strip()
    if "</think>" in body:
        body = body.split("</think>")[-1]
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body.strip()).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return [], False
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return [], False
    ev = d.get("events") if isinstance(d, dict) else None
    return ([x for x in ev if isinstance(x, dict)] if isinstance(ev, list) else []), isinstance(ev, list)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--adapter")
    ap.add_argument("--data", required=True)
    ap.add_argument("--ids")
    ap.add_argument("--out", required=True)
    ap.add_argument("--batch", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=1536)
    a = ap.parse_args()
    rows = [json.loads(l) for l in open(a.data)]
    if a.ids:
        want = set(json.load(open(a.ids)))
        rows = [r for r in rows if r["id"] in want]
    tok = AutoTokenizer.from_pretrained(a.model)
    tok.padding_side = "left"
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda")
    if a.adapter:
        from peft import PeftModel
        model = PeftModel.from_pretrained(model, a.adapter)
        model = model.merge_and_unload()
    model.eval()
    prompts = [tok.apply_chat_template(r["messages"][:2], tokenize=False, add_generation_prompt=True,
                                       enable_thinking=False) for r in rows]
    order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
    out, valid, t0, gen_tok = {}, 0, time.time(), 0
    for b in range(0, len(order), a.batch):
        idx = order[b:b + a.batch]
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True).to("cuda")
        with torch.no_grad():
            g = model.generate(**enc, max_new_tokens=a.max_new, do_sample=False,
                               pad_token_id=tok.pad_token_id or tok.eos_token_id)
        for j, i in enumerate(idx):
            new = g[j][enc["input_ids"].shape[1]:]
            gen_tok += int((new != (tok.pad_token_id or tok.eos_token_id)).sum())
            text = tok.decode(new, skip_special_tokens=True)
            ev, ok = parse(text)
            valid += ok
            out[rows[i]["id"]] = {"id": rows[i]["id"], "events": ev, "raw": text}
    secs = time.time() - t0
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(out[r["id"]], ensure_ascii=False) + "\n")
    print(json.dumps({"windows": len(rows), "json_valid": valid, "secs": round(secs, 1),
                      "windows_per_s": round(len(rows) / secs, 2), "gen_tokens": gen_tok}))


if __name__ == "__main__":
    sys.exit(main())
