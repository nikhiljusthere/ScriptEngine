#!/bin/bash
# serve_35b.sh — Qwen3.6-35B-A3B (groupwise-int) on NInfer, FULL CONTEXT, RTX 5090 32 GB.
#
# This is the JJK gold-verification engine (2026-09-30). It replaces the
# llama.cpp Q8 server (:8090) as the model opencode and the verification
# workers talk to. Chosen because it is ~9x faster at decode:
#
#   decode, single request, structured output   779.6 tok/s  (MTP3)
#   decode, single request, long reasoning      750.6 tok/s
#   prefill @ 7,680 tok                        17,705 tok/s
#   prefill @ 260,096 tok                       5,247 tok/s
#   vs llama.cpp Q8 on the same card:             92 tok/s gen / 3,211 tok/s pp
#
# SETTINGS ARE FROM UPSTREAM MEASUREMENTS, not guesswork. Sources (read
# 2026-09-30, repo master):
#   docs/performance/qwen3.6-35b-a3b.md  — measured 2026-09-07 @ rev 487f897
#   README.md                            — capabilities, kv-capacity semantics
#
# BINARY: use build35/, NOT build/. The artifact downloaded 2026-09-30 is
# NInfer format v3 (magic `NINFER\0\x03`); the Sep-2 binary in build/ only
# accepts v2 and dies with "artifact magic is not NInfer v2". build35/ is the
# current tree (checkout d44ab584, whose tests expect v3 and reject v2) and is
# the only build with the current flag set. The old qwen3_8_27b_nvfp4.ninfer
# artifact is v2, so it needs build/ -- do not "fix" this by pointing back.
#
# WHY THESE VALUES
#   --max-context 262144   the model's own ceiling, and the context ceiling of
#                          every measured run. This IS "full context".
#   --kv-capacity auto     sizes the shared KV pool to the largest legal value
#                          from memory left after weights, keeping 1 GiB head.
#                          This IS "load it on whole": measured 262,144 actual
#                          at C=1 (6.39 GiB free) and 524,288 at C=2 (3.30 GiB
#                          free), i.e. two lanes each at full 262,144.
#   --max-concurrency 2    the upstream-recommended profile. Corpus decode
#                          649.8 -> 921.2 tok/s going C=1 -> C=2. Two lanes lets
#                          the verification workers overlap without a second
#                          model load.
#   --kv-dtype int8        Qwen3.6's native KV path (INT8 group-64); every
#                          published 35B-A3B number was measured with it.
#   --prefill-chunk 1024   matches the perf doc.
#   --spec mtp --draft-tokens 3 --lm-head-draft
#                          MTP3. Chosen over DFlash K=7 deliberately: MTP3 wins
#                          3 of 4 scenario categories and has far higher
#                          acceptance (72.2% vs 46.6% corpus). DFlash K=7 is
#                          faster on Structured alone (906.4 vs 779.6 tok/s,
#                          +16%) but much slower on Story (291.6 vs 465.2,
#                          -37%) and Code (620.6 vs 677.2). A 7,000-window
#                          verification campaign wants the consistent one, not
#                          the peak on one category. Reconsider only if the
#                          workload becomes purely JSON-shaped.
#   --device-state-slots 2 / --host-state-slots 8 / --host-kv-mib 8192
#                          the README's cache tiers: 2 Device checkpoint slots,
#                          8 pinned Host State slots, 8 GiB pinned Host KV
#                          beyond the active StateImages. A 7,000-window
#                          campaign restarting workers should re-prefill as
#                          little as possible. Requires prefix reuse (on by
#                          default) and is incompatible with --spec dflash.
#   --default-max-tokens 20480
#                          NOT omitted on purpose: the default is 8192, and
#                          Qwen has already failed pages by spending 8192 on
#                          reasoning and never answering (see plan/SWITCHPOINT.md
#                          ARCHITECT NOTE 02:0x). ScriptEngine's
#                          SCRIPTENGINE_ANSWER_TOKENS should match this.
#   --preserve-thinking    returns the reasoning so a verification verdict can
#                          be audited.
#
# SAMPLING: left at the model-aware defaults on purpose. --greedy was tried on
# the 27B and produced thinking loops and degenerate repetition. Do not add it.
#
# PORT 18081, not 18080: the ninfer-27b fallback provider owns 18080 in
# opencode.json. Sharing the port would let a "switch to the 27B" silently talk
# to this model instead.
set -euo pipefail
cd /home/goblin/ninfer-work
mkdir -p logs
exec ./ninfer/build35/apps/ninfer-serve models/qwen3_6_35b_a3b.ninfer \
  --host 127.0.0.1 --port 18081 \
  --model-id qwen3.6-35b-a3b \
  --max-context 262144 \
  --kv-capacity auto \
  --max-concurrency 2 \
  --kv-dtype int8 \
  --prefill-chunk 1024 \
  --device-state-slots 2 \
  --host-state-slots 8 \
  --host-kv-mib 8192 \
  --spec mtp --draft-tokens 3 \
  --lm-head-draft \
  --default-max-tokens 20480 \
  --pending-timeout-ms 300000 \
  --preserve-thinking \
  --cors \
  --log-stats-interval-ms 1000 \
  --request-log-jsonl /home/goblin/ninfer-work/logs/requests_35b.jsonl
