#!/bin/bash
# serve_q8_best.sh — the MEASURED-BEST Qwen3.8-27B Q8_0 config for this 32 GB card.
# Generated 2026-09-30 from tools/train/ops/sweep_q8.sh measurements:
#
#   config                     gen      pp     spec-accept   VRAM
#   -ngl 60  -np 6 (old prod)   19.03    1145    0.680        31,278 MiB
#   -ngl 999 -np 2  (this)      92.52    3211    0.738        31,646 MiB
#
# WHY -np 2 IS THE WHOLE TRICK: the GDN recurrent-state ("rs") cache is ~74.8 MiB PER GDN
# LAYER ON GPU (3591 MiB for 48 layers — proof in q6_server_W2244.log: "failed to allocate
# buffer for rs cache") and it scales with the SLOT COUNT, not just the layer count. At NP=6
# it eats ~3.5 GiB and full offload needs 27.04 (weights) + 2.26 (KV q8_0 @65k) + 3.59 (rs)
# + overhead = 33.6 GiB > 31.84 available, so NGL=999 OOMs and 5 layers fall to the CPU
# (DRAM-bandwidth bound => 19 t/s). Dropping to 2 slots frees the difference: FULL offload
# fits at the same 65k ctx and generation is 4.9x faster. This is why the earlier
# "NGL=999 OOMs, use NGL=60" note in serve_q8.sh was wrong — it was an NP artifact.
#
# Cost of NP=2: only 2 concurrent requests (one opencode session + one other). If a third
# concurrent stream is ever needed, test -np 3 (it may still fit) before going back to 6.
# Spec drafting (native MTP, exact so no quality cost) at n-max 3 / p-min 0.5 as measured;
# --spec-draft-n-max 5 was NOT reached by the sweep, so it is deliberately not set here.
exec ~/llama.cpp/build/bin/llama-server \
  -m /mnt/PROJECTS/models/qwen3.8-27b-q8/Qwen3.8-27B-Q8_0.gguf \
  --alias qwen3.8-27b-q8 --host 127.0.0.1 --port 8090 \
  -ngl 999 -c 65536 -np 2 --kv-unified \
  --cache-type-k q8_0 --cache-type-v q8_0 \
  --spec-draft-type-k q8_0 --spec-draft-type-v q8_0 \
  --spec-type draft-mtp --spec-draft-n-max 3 --spec-draft-p-min 0.5 --spec-draft-ngl all \
  --flash-attn on --jinja \
  --cache-ram 16384 --cache-prompt --cache-reuse 256 \
  --fit off --no-context-shift --no-mmproj \
  --reasoning on \
  --threads 16 --threads-batch 16 -b 2048 -ub 512 \
  --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0.0 \
  --repeat-penalty 1.0 --presence-penalty 0.0 \
  --metrics --perf
