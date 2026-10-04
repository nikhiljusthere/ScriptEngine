#!/bin/bash
# serve_cybertiel.sh — the labeler (owner 2026-10-04): Cyber-Tiel-Coder-35B-A3B
# MTP UD-Q5_K_XL (26.98 GB GGUF, peculiar-ragdoll/...-GGUF-MTP @ fa19d4f3) on
# llama.cpp, "maximum speed with highest quality".
#
# Settings follow the model card (read 2026-10-04), not guesses:
#   -ngl 99                 every layer on the GPU; if it does not fit, raise
#                           NCPUMOE (routed experts to CPU, ~0.5 GB each), never
#                           lower -ngl, never NCPUMOE > 40 (block 40 = MTP head).
#   -fa on -ctk/-ctv q8_0   only 11/41 blocks carry attention: ~0.8 GB KV @ 64k,
#                           ~1.6 GB @ 128k; f16 KV would double it.
#   --spec-type draft-mtp   turns the grafted MTP head on (dead weight otherwise);
#   --spec-draft-n-max 1    the card's fastest setting: 1.21x, 82% accepted
#                           (n-max 3: 1.17x; 8: 0.57x).
#   sampling                card's agentic settings: temp 0.6, top-p 0.95,
#                           top-k 20, min-p 0; no reasoning budget cap (the card:
#                           a low budget degrades quality, not speed).
#
#   CTX=131072 NP=1 tools/train/ops/serve_cybertiel.sh     # inline verification
#   CTX=131072 NP=4 tools/train/ops/serve_cybertiel.sh     # batch drafting (32k/slot)
set -u
MODEL=/mnt/PROJECTS/models/cybertiel-35b-mtp/Cyber-Tiel-Coder-35B-A3B-MTP-UD-Q5_K_XL.gguf
CTX=${CTX:-131072}
NP=${NP:-1}
NCPUMOE=${NCPUMOE:-0}
PORT=${PORT:-8091}
EXTRA=()
[ "$NCPUMOE" -gt 0 ] && EXTRA+=(--n-cpu-moe "$NCPUMOE")
exec ~/llama.cpp/build/bin/llama-server -m "$MODEL" \
  --alias cybertiel-35b \
  --host 127.0.0.1 --port "$PORT" \
  -ngl 99 "${EXTRA[@]}" \
  -fa on -ctk q8_0 -ctv q8_0 \
  --ctx-size "$CTX" --parallel "$NP" \
  --jinja \
  --spec-type draft-mtp --spec-draft-n-max 1 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0 \
  --metrics
