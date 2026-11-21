#!/bin/bash
# Qwen3.8-27B UD-Q6_K_XL on llama.cpp with native MTP drafting (owner 2026-09-29:
# the worker model for gold annotation; ninfer and the uncensored Qwen stay untouched).
# Config after https://huggingface.co/unsloth/Qwen3.8-27B-GGUF/discussions/14 (RTX 5090 ~100 t/s),
# text-only (no mmproj), q8_0 KV (the only safe KV quant reported), NP parallel slots.
NP=${NP:-4}; CTX=${CTX:-98304}
exec ~/llama.cpp/build/bin/llama-server \
  -m /mnt/PROJECTS/models/qwen3.8-27b-gguf/Qwen3.8-27B-UD-Q6_K_XL.gguf \
  --alias qwen3.8-27b-q6 --host 127.0.0.1 --port 8090 \
  -ngl 999 --flash-attn on --jinja \
  --ctx-size $CTX -np $NP --kv-unified \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --spec-type draft-mtp --spec-draft-n-max 3 \
  --threads 16 --threads-batch 16 -b 2048 -ub 512 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0
