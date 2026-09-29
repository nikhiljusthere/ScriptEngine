#!/bin/bash
# Qwen3.8-27B Q8_0 on llama.cpp (owner 2026-09-29: replaces Q6 as the worker/judge model).
# Q8_0 model + Q8_0 KV (owner advice 2026-09-29: f16 KV does not fit — the hybrid
# GDN recurrent-state cache is pinned to the model device, so 65k ctx + NGL=999 OOMs
# even on a clear card; q8_0 K/V halves the full-attention KV and the --cache-ram cap
# keeps the rest in system RAM).
#
# 2026-09-30 CORRECTION — the "NGL=999 OOMs on a clear card" claim above is WRONG, and it
# cost a full NGL ladder (999->60->52->44) plus a switchpoint built on the false premise.
# Measured by tools/train/ops/sweep_q8.sh: the GDN recurrent-state cache is ~74.8 MiB PER
# GDN LAYER ON GPU (3591 MiB / 48 layers) and it scales with the SLOT COUNT. At NP=6 full
# offload needs 27.04 + 2.26 + 3.59 = 33.6 GiB > 31.84 and OOMs; at NP=2 it fits and runs
# FULLY offloaded: 92.52 t/s (and 88.50 on re-verify) vs 19.03 t/s for the NGL=60 fallback
# this file's default produced. USE serve_q8_best.sh (-ngl 999 -np 2) INSTEAD of this file.
# This file is kept only as the conservative NP=6 fallback.
# 65,536-token context shared by NP slots, native MTP drafting, -ub 512 so no
# single kernel trips the display GPU's watchdog.
NP=${NP:-6}; CTX=${CTX:-65536}; NGL=${NGL:-999}
exec ~/llama.cpp/build/bin/llama-server \
  -m /mnt/PROJECTS/models/qwen3.8-27b-q8/Qwen3.8-27B-Q8_0.gguf \
  --alias qwen3.8-27b-q8 --host 127.0.0.1 --port 8090 \
  -ngl $NGL --flash-attn on --jinja \
  --ctx-size $CTX -np $NP --kv-unified \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --spec-draft-type-k q8_0 --spec-draft-type-v q8_0 \
  --cache-ram 16384 \
  --cache-prompt --cache-reuse 256 \
  --spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-p-min 0.5 --spec-draft-ngl all \
  --fit off --no-context-shift --no-mmproj \
  --reasoning on \
  --threads 16 --threads-batch 16 -b 2048 -ub 512 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --repeat-penalty 1.0 --presence-penalty 0.0 \
  --metrics --perf
