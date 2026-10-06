#!/usr/bin/env python3
"""A minimal OpenAI-compatible /v1/chat/completions server over HF transformers
(train-env), so tools/train/draft_v2.py's multi-pass pipeline can run on the
Qwen3.5-4B student (base + LoRA adapter) exactly as it runs on ninfer.

train-env has no vLLM/SGLang; this exists for the 2026-10-06 owner request
"test the multiple pass verify you did with the 35B model on the 4B model".
Concurrent requests (draft_v2 --workers N) are micro-batched into one
left-padded generate() per (temperature, top_p) group.

    ~/train-env/bin/python tools/train/serve_hf.py --adapter RUN/best [--port 18090]
"""
import argparse
import json
import queue
import re
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from sft_qwen import SNAP, stop_ids  # noqa: E402

THINK = re.compile(r"^.*?</think>\s*", re.S)


def load(model_path, adapter):
    from transformers import AutoTokenizer, AutoModelForImageTextToText
    tok = AutoTokenizer.from_pretrained(model_path)
    m = AutoModelForImageTextToText.from_pretrained(model_path, dtype=torch.bfloat16, device_map="cuda")
    if adapter:
        from peft import PeftModel
        m = PeftModel.from_pretrained(m, adapter)
    m.eval()
    return tok, m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=SNAP)
    ap.add_argument("--adapter")
    ap.add_argument("--port", type=int, default=18090)
    ap.add_argument("--max-batch", type=int, default=8)
    ap.add_argument("--max-new-cap", type=int, default=4096,
                    help="clamp on a request's max_tokens (draft_v2 asks 20,480)")
    a = ap.parse_args()
    tok, model = load(a.model, a.adapter)
    jobs = queue.Queue()

    def worker():
        while True:
            batch = [jobs.get()]
            time.sleep(0.05)  # let the other workers' requests arrive
            while len(batch) < a.max_batch:
                try:
                    batch.append(jobs.get_nowait())
                except queue.Empty:
                    break
            groups = {}
            for j in batch:
                groups.setdefault((j["temperature"], j["top_p"]), []).append(j)
            for (temp, top_p), js in groups.items():
                try:
                    prompts = [tok.apply_chat_template(j["messages"], tokenize=False, add_generation_prompt=True,
                                                       **j["template_kwargs"]) for j in js]
                    tok.padding_side = "left"
                    enc = tok(prompts, return_tensors="pt", padding=True).to(model.device)
                    kw = {"do_sample": temp > 0, "max_new_tokens": max(j["max_tokens"] for j in js),
                          "pad_token_id": tok.pad_token_id or tok.eos_token_id, "use_cache": True,
                          "eos_token_id": stop_ids(tok)}
                    if temp > 0:
                        kw.update(temperature=temp, top_p=top_p)
                    with torch.no_grad():
                        g = model.generate(**enc, **kw)
                    for k, j in enumerate(js):
                        text = tok.decode(g[k][enc["input_ids"].shape[1]:], skip_special_tokens=True)
                        j["result"] = THINK.sub("", text).strip()
                except Exception as e:  # noqa: BLE001
                    for j in js:
                        j["error"] = repr(e)
                for j in js:
                    j["done"].set()

    threading.Thread(target=worker, daemon=True).start()

    class H(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            self.send_response(200); self.end_headers(); self.wfile.write(b'{"status":"ok"}')

        def do_POST(self):
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            # the student was trained thinking-off; a request may opt in
            tkw = {"enable_thinking": bool((body.get("chat_template_kwargs") or {}).get("enable_thinking", False))}
            j = {"messages": body["messages"], "template_kwargs": tkw,
                 "temperature": float(body.get("temperature", 0.0)), "top_p": float(body.get("top_p", 1.0)),
                 "max_tokens": min(int(body.get("max_tokens", 2048)), a.max_new_cap),
                 "done": threading.Event()}
            jobs.put(j)
            j["done"].wait()
            if "error" in j:
                self.send_response(500); self.end_headers(); self.wfile.write(j["error"].encode()); return
            out = {"choices": [{"index": 0, "message": {"role": "assistant", "content": j["result"]},
                                "finish_reason": "stop"}]}
            data = json.dumps(out).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    print(f"serving {a.adapter or a.model} on :{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()


if __name__ == "__main__":
    main()
