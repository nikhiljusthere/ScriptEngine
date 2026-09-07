# Qwen3.8-27B-NVFP4 + NInfer + OpenCode

Local model runbook: how the NInfer server is built, patched and launched, how opencode talks
to it, how thinking is controlled, and what it actually benchmarks at.

Everything here was measured live on this machine on **2026-08-22**. This replaces
[`qwen38_sglang_opencode_working_config.md`](./qwen38_sglang_opencode_working_config.md)
(SGLang, port 30000) which is retired and deleted.

> **Text-only. Vision is deliberately off** — the server never gets `--vision` and
> opencode advertises `"input": ["text"]`.

---

## 1. Baseline

| Component | Version / value |
|---|---|
| GPU | NVIDIA RTX 5090, 32,607 MiB, **sm_120** (compute capability 12.0, Blackwell) |
| Driver | 610.47 (CUDA UMD 13.3) |
| CPU / RAM | Ryzen 9 9950X3D, 32 threads; 31.1 GB host DDR5 |
| WSL | WSL 2.6.3.0, Ubuntu 24.04.4, kernel 6.6.87.2-microsoft-standard-WSL2 |
| WSL limits | `memory=26GB`, `swap=8GB`, `autoMemoryReclaim=gradual` |
| CUDA toolkit | **13.1.115** at `/usr/local/cuda-13.1` (NInfer requires 13.1+) |
| Compiler | gcc/g++ 13.3.0 |
| Build | CMake 3.28.3 + Ninja 1.11.1 |
| NInfer | upstream commit `feaf4dd0983fdaeb2ba4c06eec6da350e644fb3a` + local patch |
| **PyTorch** | **not installed, and not needed** |

NInfer is pure C++20/CUDA. Torch is only imported by the optional maintainer tool
`tools/artifact/inspect.py`; nothing on the serving path touches it. Do not install it.

`.wslconfig` (`C:\Users\Nikhil\.wslconfig`) — note `autoMemoryReclaim` must be under
`[experimental]`, not `[wsl2]`, or WSL 2.6.3 prints
`Unknown key 'wsl2.autoMemoryReclaim'` and ignores it:

```ini
[wsl2]
memory=26GB
swap=8GB

[experimental]
autoMemoryReclaim=gradual
```

26 GB, not 28 GB: measured need is ~21.5 GB (18 GB model + 1.5 GB server + overhead), and
28 GB would leave Windows only ~3.1 GB. Changing this needs `wsl --shutdown`.

---

## 2. Model location, and why it is there

```
/root/ninfer-work/models/qwen3_8_27b_nvfp4.ninfer
```

| Property | Value |
|---|---|
| Size | 18,324,067,840 bytes (matches HF `x-linked-size` exactly) |
| SHA-256 | `eaf8ad124256d0a0c1ebbbca442ca58eee4f97ab34a60a0b4d57e2b41e2c56d2` (verified) |
| Filesystem | **native ext4** on `/dev/sdd` |
| Identity | `{"model_id":"qwen3.8-27b","weights_id":"nvfp4"}` |
| Contents | 721 tensors + 6 resources; 16.78 GiB of weights uploaded to GPU |
| Source | `Ostfralla/Qwen3.8-27B-NVFP4-NInfer` |

**Keep it on ext4.** The Reddit post that started this said the model was on a "WSL2 mounted
drive". Taken literally (`/mnt/c`, `/mnt/e`) that is the *slow* option: those are 9p/drvfs
mounts with `msize=65536`, poor for large sequential reads and with weak `mmap` semantics.
ext4 is a direct block device.

Measured, on ext4:

- model load: 18.32 GB in **5.37 s ≈ 3.4 GB/s**
- `sha256sum` of the same file: 19.1 s — this is **CPU-hash bound, not I/O bound**, so don't
  read 958 MB/s as the disk speed.

Startup is ~5.4 s whether or not the file is in page cache — a `wsl --shutdown` (which drops
the cache entirely) still gave 5.51 s. So RAM sizing is *not* a startup-time lever here.

The artifact is one self-contained blob (weights + tokenizer + chat template), so there is no
conversion or copy step to optimise, and no HF cache layout that matters.

---

## 3. The engine patch — read this before any `git pull`

The model **will not load** on stock upstream. It fails instantly with:

```
error: tensor descriptor does not match target contract: text/token_embedding
```

Cause: upstream commit `5d2c1f55` added a dedicated `WeightsProfile::Qwen38Nvfp4` whose
`endpoint_format()` expects `FP8_E4M3FN_ROW_BF16S` vocabulary endpoints and a **fused**
`gdn/a_b_projection`. The published artifact is actually laid out the Qwen3.6 way:

| Tensor | In the artifact | `Qwen38Nvfp4` expects |
|---|---|---|
| `text/token_embedding` | `W8G32_F16S` | `FP8_E4M3FN_ROW_BF16S` |
| `gdn` control projection | split `a_projection` + `b_projection` `[48,5120]` | fused `a_b_projection` `[96,5120]` |
| `gdn/query_key_value_z` | `NVFP4` | FP8 |

So upstream has moved ahead of the published artifact. The `qwen38-nvfp4-support.patch` shipped
in the model repo no longer applies (its context is stale).

**Fix**, in `src/targets/qwen3_6_27b/impl/package.cpp`, `resolve_weights()` — route the identity
to the Qwen3.6 NVFP4 profile, which matches the artifact byte-for-byte:

```cpp
if (identity.model_id == qwen3_8_model_id && identity.weights_id == "nvfp4") {
    return WeightsProfile::Qwen36Nvfp4;   // was: Qwen38Nvfp4
}
```

Saved as `/root/ninfer-work/qwen38-nvfp4-local.patch`; original file backed up at
`/root/ninfer-work/package.cpp.orig`; pinned commit in `/root/ninfer-work/ninfer-commit.txt`.
Sampling defaults still resolve through `model_id`, so Qwen3.8's own presets are preserved.

Related upstream issue: <https://github.com/Neroued/ninfer/issues/25>

### Rebuilding after a pull

```bash
cd /root/ninfer-work/ninfer
git apply /root/ninfer-work/qwen38-nvfp4-local.patch   # re-apply; expect conflicts if HEAD moved
cmake --build build --parallel
```

---

## 4. Starting the server

Canonical launcher, `/root/ninfer-work/serve.sh`:

```bash
#!/bin/bash
cd /root/ninfer-work
mkdir -p logs
exec ./ninfer/build/apps/ninfer-serve models/qwen3_8_27b_nvfp4.ninfer \
  --host 0.0.0.0 --port 18080 \
  --model-id qwen3.8-27b-ninfer \
  --max-context 262144 \
  --kv-capacity 278528 \
  --max-concurrency 3 \
  --pending-timeout-ms 120000 \
  --default-max-tokens 20480 \
  --prefill-chunk 4096 \
  --kv-dtype int8 \
  --spec mtp --draft-tokens 3 --lm-head-draft \
  --greedy \
  --host-kv-cache-mib 14336 \
  --cors \
  --log-stats-interval-ms 1000 \
  --request-log-jsonl /root/ninfer-work/logs/requests.jsonl
```

Two deliberate changes from the original (2026-08-24, both measured — see §6):

- **`--greedy` added.** The model card says to let Qwen3.8's built-in sampler presets apply, and
  that advice was followed originally. It costs 15% of decode throughput here, because
  temperature 1.0 tanks speculative draft acceptance (40.1% → 50.5% at temp 0). Output becomes
  deterministic, which for agent work is a feature.
- **`--preserve-thinking` removed.** Thinking is still generated every turn; prior turns'
  reasoning is simply no longer replayed into later prompts.

Previous config is kept at `/root/ninfer-work/serve.sh.bak-preTune`.

### From Windows PowerShell / cmd

**Start** — one command, blocks ~6 s until the model is loaded, then returns:

```powershell
wsl -d Ubuntu-24.04 -- bash /root/ninfer-work/start_server.sh
```

It is idempotent: if the server is already up it prints `already running on :18080`
and does nothing.

> **Do not** try to background it from Windows like
> `wsl -d Ubuntu-24.04 -- bash -c "nohup ./serve.sh &"`.
> That silently fails. When `wsl.exe` exits, WSL tears the session down and kills
> the child *before* it finishes loading — you get an empty `serve.log` and no
> process. Even `setsid nohup ... &` dies this way. The launching script **must
> stay alive until the server answers**, which is exactly what `start_server.sh`
> does. Once it has answered, the server survives fine after `wsl.exe` exits.

Check health:

```powershell
curl.exe -s http://127.0.0.1:18080/v1/models
```

Tail the log:

```powershell
wsl -d Ubuntu-24.04 -- tail -f /root/ninfer-work/logs/serve.log
```

Stop:

```powershell
wsl -d Ubuntu-24.04 -- pkill -f ninfer-serve
```

A healthy start looks like:

```
ninfer-serve: model loaded in 5.36846 s
ninfer-serve: KV capacity explicit resolved=294912 tokens pages=4608/12288 runtime=11.71 GiB
              free-after-weights=13.42 GiB free-after-startup=1.79 GiB
ninfer-serve: listening on http://0.0.0.0:18080 (model id: qwen3.8-27b-ninfer, auth: disabled)
```

Endpoints served: OpenAI Chat Completions + Responses, and Anthropic Messages.

---

## 5. Flags that do NOT exist

The widely-copied Reddit launch line **will not start this server**. Verified against the binary:

| Flag as posted | Reality |
|---|---|
| `--spec` + `--mtp` | `--spec` takes a value. Server: `invalid speculative backend: --mtp`. Correct: `--spec mtp`. There is no `--mtp` flag. |
| `--host-kv-cache 1` | Not a real flag **in any version**. But the *feature* is real and we now run it — it arrived in upstream PR #64 as **`--host-kv-cache-mib N`** (a MiB budget, not a boolean). Merged 2026-08-24; see §6a. The Reddit line is from an early revision of that PR. |
| `--request-log-json` | Real flag is `--request-log-jsonl`. |
| `--vision` | Exists, but is not needed for a text-only artifact and costs fixed GPU allocations. Omitted. |

Real, useful flags the Reddit line omits: `--kv-capacity N|auto`, `--no-prefix-reuse`,
`--cors`, `--api-key`, `--reasoning-effort` (CLI binary only, *not* `ninfer-serve`).

---

## 6z. Current target: ONE agent at maximum context (2026-08-24)

The 2-agent configuration was abandoned deliberately. 152k per agent forces opencode to compact
at ~110-120k, and that depth is not useful enough to justify halving the context. **Tuned for a
single agent at the model's true ceiling instead.**

| Setting | Value | Why |
|---|---|---|
| `limit.context` | **229376** | +32768 output = 262,144 exactly, the model's native max |
| `--kv-capacity` | **278528** | one request needs ≤262,144; +16,384 for opencode side-calls |
| `--host-kv-cache-mib` | **14336** | a parked 229k session is ~8.7 GB; comfortably inside 15.03 GB |
| `--draft-tokens` | **3** | re-verified under `--greedy`; 4 is worse (see below) |

Shrinking the pool from 319,488 (which existed only to fit *two* 152k sequences) returned
**1.5 GB of VRAM**: free VRAM 145 MiB → **1,706 MiB**, slack 916 MiB → **2.26 GiB**. Decode
unchanged (162.5 vs 166.8 tok/s, inside run-to-run variance). This is a strictly better place to
sit — the display shares this GPU and 145 MiB was uncomfortably tight.

**Trade-off to remember:** at `--kv-capacity 278528` two 152k agents no longer fit. Restore
319,488 *and* `limit.context: 152000` together if you ever want concurrent agents back.

### `--draft-tokens` re-verified under `--greedy`

The original tuning (3 beats 4/5) was done at temperature 1.0. Since `--greedy` raised acceptance,
longer draft windows were re-tested — the expectation was that 4 would now win. It does not:

| `--draft-tokens` | Decode | tokens/pass | Accept |
|---|---|---|---|
| **3** | **166.8 tok/s** | 2.59 | **53.1%** |
| 4 | 163.6 tok/s | 2.64 | 40.9% |

Acceptance falls faster than tokens/pass rises, so the extra verification is not repaid.
**3 remains correct at any temperature.**

---

## 6a. Host-KV cache (PR #64) — 27x faster agent follow-ups

**The single biggest win measured on this box.** Merged 2026-08-24 from upstream
`Neroued/ninfer` PR #64. Flag: **`--host-kv-cache-mib N`**.

### What it does

When a sequence's GPU lane is needed by another request, its KV is **parked in pinned host RAM**
instead of being discarded. When that session returns, it is **restored** instead of re-prefilled.

### Measured, this box, identical scenario

One 150k session → four small (~6k) one-off requests → the big session returns:

| | Follow-up TTFT |
|---|---|
| `--host-kv-cache-mib 0` (disabled) | **36.74 s** |
| `--host-kv-cache-mib 12288` | **1.36 s** |

**27x.** Confirmed in `serve.log` as an actual restore, not prefix reuse:

```
parked lane 0 to host: 5,077,991,424B text + 317,374,464B backend + 307,888,128B gdn, 150261 tokens
restored lane 0 from host: 150140 tokens (entry 8)
```

The control matters: with the cache **off**, four *tiny* 6k requests are still enough to cycle all
three lanes and evict the big session, forcing a full 150k re-prefill. Ordinary in-VRAM prefix
caching does not save you here — that is exactly the "agents take turns and feel slow" symptom.

### Sizing — this is a RAM feature, budget it properly

A parked 150k session costs **~5.7 GB** of pinned host RAM (~5.1 GB text + 0.3 GB backend +
0.3 GB gdn). A 120k one-off costs ~4.6 GB.

`--host-kv-cache-mib 12288` (12 GiB) holds roughly **two** large sessions. The startup line
reports the real limit:

```
host KV cache enabled: budget_bytes=12884901888
  max_parked_sequence_bytes=9719926784 (holds 1 max-size sequences)
```

**Undersizing the budget is worse than useless — it silently evicts the session you care about.**
First attempt here used four *120k* evictors (~18 GB of parking pressure against a 12 GiB budget);
LRU threw out the measured session and the result was a flat 0% improvement:

```
host KV LRU evicting entry 0 (150258 tokens) to make room
```

Watch `serve.log` for `LRU evicting` on sessions you expected to survive — that means grow the
budget or reduce concurrent session sizes.

### Costs and constraints

- **Startup: 5.6 s → 13.8 s.** Allocating 12 GiB of pinned RAM is not free.
- Pinned RAM is locked and non-swappable; it comes out of the WSL2 ceiling (26 GB here).
- **Requires prefix reuse** — rejected with `--no-prefix-reuse` (would be write-only caching).
- **Incompatible with `--spec dflash`** — DFlash's lane-affine draft caches are not captured.
  We use `--spec mtp`, so this is fine.
- Sequences larger than the budget silently fall back to re-prefill.

### Measured ceiling: 14336 works, 16384 does not

Bisected on this box:

| `--host-kv-cache-mib` | Result |
|---|---|
| 12288 | starts |
| **14336** | **starts — current setting** (`budget_bytes=15,032,385,536`) |
| 16384 | `cudaHostAlloc failed (out of memory)` |
| 18432 | `cudaHostAlloc failed (out of memory)` |

Pinned pages must be physically locked; the 26 GB WSL2 ceiling (`.wslconfig memory=26GB`) on a
31.1 GB host cannot satisfy 16 GiB. Note `ulimit -l` is 64 MB but is **not** the constraint —
the server runs as root and CUDA pinned allocations bypass it.

**A failed start leaves you with no server**, so verify startup after any change to this value.

### Is host-KV worth it? Only when a session is actually EVICTED

This is the whole decision. Host-KV does nothing for a session that stays resident — the built-in
`restore_turn_checkpoint` path (which predates PR #64) already handles those follow-ups for free.

Measured A/B, two agents at 152k where **both stay resident**:

| | host-KV ON | host-KV OFF |
|---|---|---|
| tokens prefilled | 304,102 | **304,101** |
| follow-up TTFT | 0.35 s | **0.35 s** |

**Identical — zero benefit.** Now the same A/B where the session **is** evicted (four small ~6k
side-calls cycle all three lanes):

| Session size | host-KV OFF | host-KV ON | Gain |
|---|---|---|---|
| 150k | 36.74 s | 1.36 s | **27x** |
| **229k** | **73.71 s** | **1.72 s** | **43x** |

**The payoff scales with context**, because it is exactly the re-prefill being avoided.

**Verdict for the single-agent max-context setup: keep it on.** At 229,376 context, any eviction
costs ~74 s without it. Eviction is driven by *lanes*, not pool space — four tiny 6k requests are
enough to evict a 229k session even with the pool nearly empty, and opencode continuously fires
small side-calls (titles, summaries, subagent one-offs). Cost is 14 GiB of pinned RAM and ~8 s of
extra startup. For long sessions that is a very good trade.

Corollary: had the 2-agent-at-152k config been kept, host-KV would have been nearly worthless.

### Does host-KV let you run bigger contexts? Measured: no, not past ~152k

Two agents, three turns each, same scenario, `--host-kv-cache-mib 12288`:

| | 152k / agent | 200k / agent |
|---|---|---|
| tokens actually prefilled | **304,102** | **800,157** |
| follow-up TTFT | **0.35 s** | **61.8 s** |
| total server time | **161 s** | **433 s** |

**200k per agent is 2.7x worse, not better.** Two failures compound:

1. `2 x 200k = 400k` exceeds the 319,488 VRAM pool, so they can never co-reside.
2. A 200k session needs **7.49 GB** to park, and the 12 GiB budget fits only one:

```
park lane 0 FAILED: no budget room for 7493304320 bytes
                    (largest free range 5393895424 bytes)
```

The second agent cannot park, so it re-prefills 200k every single turn.

**Raising the budget does not rescue this.** Re-ran 200k at `--host-kv-cache-mib 14336`
(15.03 GB): byte-identical outcome — 799,968 tokens prefilled, 433 s total, follow-up TTFT 61.7 s.
It misses by 262 MB:

```
park lane 0 FAILED: no budget room for 7491006464 bytes
                    (largest free range 7228874752 bytes)
```

Two 200k sessions need 14.99 GB of *contiguous* ranges; after parking the first, only 7.23 GB
remains contiguous. **The ceiling is squeezed from both sides: 14 GiB allocates but is not enough,
16 GiB would be enough but will not allocate.** 2 x 200k is unreachable on this hardware — that is
a RAM limit, not a tuning problem.

At **152k** both agents stay resident, and all four follow-up turns prefill just **22 tokens**
(`restore_turn_checkpoint`, TTFT 0.35 s). That is the sweet spot on this hardware — which is why
`limit.context` is 152000 and should stay there until there is more RAM.

Parked-session cost scales linearly: ~5.7 GB at 150k, ~7.5 GB at 200k (~37.5 KB/token).

### This is the real argument for more system RAM

Host-KV converts spare system RAM directly into agent responsiveness, at ~5.7 GB per parked
150k session. Current box: 31.1 GB system, 26 GB WSL ceiling, 12 GiB budget ≈ 2 warm sessions.
At 64 GB system RAM a ~32 GB budget would keep roughly 5–6 large sessions warm — i.e. every
subagent's context stays instantly restorable instead of being re-prefilled at ~36 s each.

### Rebuilding

PR #64 fast-forwards cleanly from `feaf4dd0` and does **not** touch our patched
`src/targets/qwen3_6_27b/impl/package.cpp` (only a test file in that directory). Pre-PR binary is
backed up at `/root/ninfer-work/ninfer-serve.prePR64` — restore it to roll back. Rebuild took
~2 min incremental on 32 cores.

---

## 6. Tuning — measured, not assumed

### Speculative decoding (MTP)

CLI, 39-token prompt, `--max-new 400`, `--no-thinking`, `seed 1234`, KV int8, single stream:

| Config | Decode tok/s | Acceptance | Accept length |
|---|---|---|---|
| MTP off | 80.4 | — | — |
| `--draft-tokens 2 --lm-head-draft` | 159.8 | 64.2% | 2.28 |
| **`--draft-tokens 3 --lm-head-draft`** | **185.5** | 55.6% | 2.66 |
| `--draft-tokens 4 --lm-head-draft` | 165.4 | 41.1% | 2.64 |
| `--draft-tokens 5 --lm-head-draft` | 167.4 | 38.3% | 2.89 |
| `--draft-tokens 3` (no lm-head) | 151.7 | 58.4% | 2.75 |
| `--draft-tokens 4` (no lm-head) | 166.7 | 53.6% | 3.13 |

**3 draft tokens + `--lm-head-draft` wins.** The model card suggests 4 — that is measurably
worse here. `--lm-head-draft` is worth ~+22% on its own. Valid MTP range is 1–5.

### Prefill chunk

129,039-token prompt, MTP3, KV int8:

| `--prefill-chunk` | Prefill tok/s | Total elapsed |
|---|---|---|
| 1024 (NInfer default) | 3,952 | 32.85 s |
| 2048 | 4,542 | 28.64 s |
| **4096** | 4,556 | 28.53 s |
| 8192 | 4,674 | 27.82 s |

4096 is the sweet spot; the default 1024 is clearly worst. 8192 is ~2.5% faster but enlarges the
prefill scratch arena. Must be a multiple of 128.

### Concurrency

Single-stream decode, 1500 tokens, thinking off, `--kv-capacity 262144`, 3 runs each:

| `--max-concurrency` | Single-stream decode | VRAM | Free after startup |
|---|---|---|---|
| 3 | 171.7 tok/s (173.8 / 170.9 / 170.3) | 28,964 MiB | 2.89 GiB |
| 1 | 172.2 tok/s (173.2 / 172.3 / 171.1) | 28,350 MiB | 3.42 GiB |

**Concurrency 3 costs nothing for a single user** (0.3%, inside noise) and enables 412 tok/s
aggregate. Keep it at 3.

### KV cache

`--kv-dtype int8` (reported as `int8-group64`) is required, not optional: 262,144 tokens of KV
is ~8.9 GiB on top of 16.78 GiB of weights. bf16 KV roughly doubles that and will not fit in
32 GB alongside the weights.

### `--greedy` — +26% acceptance, added 2026-08-24

Measured A/B, identical prompts, 13 requests per config, thinking ON both sides:

| Config | Decode tok/s | Prefill tok/s | Accept | tok/pass |
|---|---|---|---|---|
| temperature 1.0 (was) | 124.1 | 4,346 | 40.1% | 2.21 |
| **`--greedy`** | **143.3** | 4,295 | **50.5%** | 2.52 |

**+15.5% decode, prefill unchanged.** Speculative acceptance is temperature-sensitive: every
rejected draft token wastes a verified forward pass, so temp 1.0 was throwing away throughput.

This has to be set **on the server**. `opencode.json` sets `reasoning_effort: "none"` and it is
silently dropped by `@ai-sdk/openai-compatible` — 6,847 of 6,847 logged tool-bearing requests ran
`enable_thinking=True, temperature=1.0`. `sampling_defaults.server_overrides.*` are all null, so
nothing else clamps it. Client-side sampling config on this stack is not load-bearing.

Side effect: output becomes deterministic (exact argmax). For agent work that is a feature.

### `--kv-capacity` — 319,488 is the sweet spot; there is a cliff past it

KV costs **35,905 bytes per token**. Raising capacity consumes the engine's *workspace slack* —
the arena prefill chunks and CUDA graph capture allocate from. `free-after-startup` is always
`0.00 MiB`; `slack=` on the startup line is the number that matters.

Swept, thinking on + `--greedy`, identical prompts, 13 requests each:

| `--kv-capacity` | Slack | Decode tok/s | Prefill tok/s |
|---|---|---|---|
| 294,912 | 1.72 GiB | 143.3 | 4,295 |
| 311,296 | 1.17 GiB | 141.7 | 4,303 |
| **319,488** | **916 MiB** | **143.3** | **4,247** |
| 331,776 | 496 MiB | **131.6** | **3,561** |

Everything down to ~916 MiB of slack is **free** — flat within noise. Below that it falls off a
cliff: **−12% decode and −18% prefill** at 496 MiB.

**319,488 is set.** Stopping there rather than creeping closer to the cliff, because
`graphs=0.00 MiB/246.00 MiB` in every benchmark — CUDA graphs never captured during testing.
Under sustained real load they can claim up to 246 MiB from slack, so 916 MiB leaves ~670 MiB of
genuine margin while 496 MiB would leave ~250 MiB.

Rule of thumb: **keep `slack=` above ~900 MiB**, and re-measure *prefill* as well as decode after
any change — decode alone would have hidden most of the 331,776 regression.

Extra KV is inert unless something consumes it, so `limit.context` was raised to 152000 to match
(see §9). Verified: two concurrent 152,048-token requests finish with a 1.01 time ratio
(= co-resident). Their combined 304,170 tokens exceed the old 294,912 pool, so that pair would
have serialized before this change.

### Retained thinking (`--preserve-thinking`) — dropped 2026-08-24

Reasoning is still generated every turn; what changed is that *prior* turns' reasoning is no
longer replayed into later prompts. Retaining it was a significant driver of the 112k median
prompt size, and prompt size is what pushes concurrent agents past the KV pool.

---

## 7. Benchmarks

All via HTTP on the running server. Conditions stated per row.

### Decode

| Scenario | Prompt | Generated | Thinking | Concurrency | Result |
|---|---|---|---|---|---|
| Sustained single stream | 24 tok | 1500 | off | 1 | **178.1 tok/s** |
| Short single stream | 28 tok | 600 | off | 1 | 146–152 tok/s |
| Thinking on | 68 tok | 600 | **on** | 1 | 130–136 tok/s |
| 3 parallel streams | 28 tok | 600 each | off | 3 | 140–144 each, **412 tok/s aggregate** |

Longer generations score higher — fixed per-request overhead amortises.

### Prefill (derived from TTFT, thinking off, 16 output tokens)

| Prompt tokens | TTFT | Prefill tok/s |
|---:|---:|---:|
| 879 | 82 ms | 10,689 |
| 3,532 | 303 ms | 11,656 |
| 14,074 | 1,295 ms | 10,864 |
| 56,132 | 7,847 ms | 7,153 |
| 129,039 | 28.3 s | 4,556 |

This is the whole explanation for the quoted "5,000–12,000 tok/s" figure: it is simply the range
for prompts of roughly 400–20,000 tokens. It is **not** achievable at 129k, where the honest
number is ~4,600. A second user in that same Reddit thread reported 90–120 tok/s and
3,000–5,000 prefill, which is consistent with these curves.

### System under sustained load

| Metric | Value |
|---|---|
| GPU utilisation | 98% |
| Power | 587 W (of 600 W cap) |
| Temperature | 55 °C |
| SM clock | 2,835 MHz |
| VRAM | 30,197 MiB / 32,607 MiB |
| Server RSS | 1.49 GiB |
| Startup | 5.51 s cold / 5.37 s model load |

98% util at near-TDP means decode is **memory-bandwidth bound on the weights** — which is
exactly why MTP more than doubles it. Further gains need a smaller artifact or higher
acceptance, not more flags.

---

## 8. Thinking / reasoning control

NInfer accepts `reasoning_effort` on `/v1/chat/completions`:

| Value | Accepted? | Effect |
|---|---|---|
| `none` | yes | **Thinking fully off** — `reasoning_content` = 0 chars |
| `low` | yes | Nominally throttled — see the measurement below |
| `medium` | yes | Larger budget |
| `xhigh` | yes | Largest exposed budget |
| `high` | **no** | HTTP 400 `reasoning_effort_not_supported` |
| omitted | — | Chat template default (thinking on) |

Server-level switches: `--no-thinking` (default thinking off for every request) and
`--preserve-thinking` (keep closed-turn reasoning in later prompts — currently enabled).

### `low` does not actually reduce thinking — measured

Two rounds, 4 prompts each, `max_tokens: 1500`, mean `reasoning_content` characters:

| Round | default (unset) | `low` | `none` |
|---|---|---|---|
| 1 | 615 | **913** | 0 |
| 2 | 1,372 | 1,251 | 0 |

`low` is *higher* than default in round 1 and lower in round 2 — i.e. **within sampling noise**
at temperature 1.0. It does not reliably throttle anything, and it was slower in round 1
(3.31 s vs 2.55 s mean latency). Only `none` is deterministic: **0 reasoning characters in all
8 samples**, and consistently fastest (2.51–2.55 s vs 4.03–4.10 s).

There is **no hard thinking-token cap in NInfer.** The SGLang setup had one via
`--enable-custom-logit-processor` + a dill-serialised `Qwen3ThinkingBudgetLogitProcessor`;
NInfer has no equivalent mechanism, so a "512-token thinking budget" is not implementable here.

**Conclusion: use `none`.** Of low / hard-cap / off, only off does what "keep reasoning minimal"
actually asks for.

---

## 9. OpenCode wiring

### The one rule that matters

Carried over from the SGLang work and still true:

- `provider.<name>.options.body` — **silently dropped.** opencode spreads provider options into
  `createOpenAICompatible({...})`, which only reads `baseURL`/`headers`/`query`/`fetch`. Config
  validates fine, so this fails silently.
- `provider.<name>.models.<id>.options` — **this is the supported path.** Every key here is
  wrapped as `providerOptions.<name>` and the AI SDK spreads unknown providerOptions straight
  into the chat-completions JSON body.

So `reasoning_effort` goes under the **model's** `options`, never the provider's.

### Current `opencode.json`

```json
{
  "$schema": "https://opencode.ai/config.json",
  "model": "ninfer/qwen3.8-27b-ninfer",
  "provider": {
    "ninfer": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "NInfer - Qwen3.8-27B-NVFP4",
      "options": {
        "baseURL": "http://127.0.0.1:18080/v1",
        "apiKey": "ninfer"
      },
      "models": {
        "qwen3.8-27b-ninfer": {
          "name": "Qwen3.8-27B-NVFP4 (NInfer)",
          "id": "qwen3.8-27b-ninfer",
          "modalities": { "input": ["text"], "output": ["text"] },
          "limit": { "context": 229376, "output": 32768 },
          "options": { "reasoning_effort": "none" }
          // NOTE: reasoning_effort is silently DROPPED by @ai-sdk/openai-compatible.
          // It has never reached the server. Kept only as documentation of intent —
          // thinking and sampling are controlled by serve.sh flags.
        }
      }
    }
  },
  "mcp": {
    "scriptengine": {
      "type": "local",
      "command": [".\\scriptengine\\.venv\\Scripts\\python.exe", "-m", "scriptengine.mcp.server"]
    }
  }
}
```

Notes on each change from the SGLang version:

- `id` is now the literal string `qwen3.8-27b-ninfer`, matching `--model-id`. SGLang used a
  filesystem path as the model name; NInfer does not, and that path would now 404.
- `apiKey` is a placeholder — the server runs with `auth: disabled`. The SDK just requires a
  non-empty value.
- `modalities.input` is `["text"]` only. **Vision off.**
- `reasoning_effort: "none"` per section 8.
- The `mcp.scriptengine` block is unchanged.

**opencode caches config at startup — restart it after editing `opencode.json`.**

### Context limit caveat

262,144 is the model's native limit and the *total* per request — **prompt plus generation**.
So `context` and `output` must sum to at most 262,144; advertising `context: 262144` alongside
`output: 32768` would mean a full-depth prompt has no room left to answer.

Hence the split had been **`context: 229376` (224K) + `output: 32768` = exactly 262,144** —
the largest context that still guarantees a full-length reply.

**Lowered to `context: 152000` on 2026-08-24 — this is the parallel-subagent fix.** See
"The KV pool is what serializes parallel agents" below. 224K was single-request-optimal but
made two concurrent agents impossible.

152000 is paired with `--kv-capacity 278528`: two agents take 304,000 of the 319,488 pool,
leaving 15,488 for opencode's small side-calls (titles, summaries) so they don't queue.
**If you change one, change the other** — `2 × limit.context` must stay under `--kv-capacity`.

`--kv-capacity 294912` (rather than 262144) is set for a *different* reason: the KV pool is
shared across concurrent requests. At 294,912 a maxed-out main request can consume the full
262,144 and still leave 32,768 tokens of pool for opencode's small side-calls (titles,
summaries) instead of making them queue against `--pending-timeout-ms`.

**Raising `--kv-capacity` cannot affect output quality.** It is purely an allocation size — it
changes no numerics, no quantization and no sampling. The only KV setting that touches precision
is `--kv-dtype int8`, which is unchanged. The cost of 294,912 is VRAM only: 30,197 MiB used and
~1.79 GiB free, versus 29,152 MiB and 2.88 GiB free at 262,144.

If that headroom ever proves too tight (the display runs on this GPU too), drop back to
`--kv-capacity 262144` — concurrent side-calls will queue occasionally, but nothing breaks.
Lowering `limit.context` to `131072` also halves worst-case TTFT (~29 s measured, vs ~50 s at
224K).

### The KV pool is what serializes parallel agents

Symptom: two subagents run in parallel, produce output *in turns*, and feel very slow.

That is not a scheduler bug — it is the KV pool running out. Arithmetic from
`server_start`: KV costs **35,905 bytes per token**, and the pool is 294,912 tokens.

| Two agents at… | KV needed | Fits in 319,488? |
|---|---|---|
| 112k each (measured p50) | 224k | yes |
| **152k each (current setting)** | **304k** | **yes — verified, 1.01 time ratio** |
| 160k each | 320k | no — just over |
| 178k each (measured p90) | 356k | no — one waits |
| 200k each | 400k (14.4 GiB) | no, and impossible on 32 GB |

Evidence from 85,569 one-second scheduler samples in `requests.jsonl`:

- `running=1`: 80,491 intervals · `running=2`: 551 · `running=3`: 72
- `waiting≥1`: 4,093 intervals (~68 min cumulative queued)
- decode batch size was **1 in 99.4% of all active intervals**

So the server almost never batched, despite `--max-concurrency 3`. Reproduced directly: two
180k requests ran 58.2 s and 115.4 s — exactly 1× and 2×, i.e. serialized. Two 140k requests
both finished at ~66 s, i.e. genuinely concurrent.

Batching is worth having — measured aggregate at ~100-token context:

| Concurrent requests | Aggregate tok/s |
|---|---|
| 1 | 170 |
| 2 | 293 (1.7×) |
| 3 | 657 (3.9×) |

**Hence `limit.context: 140000`.** Two 140k agents = 280k, which fits with headroom. It trades
context depth for the ability to actually run agents in parallel.

Two 200k agents cannot be made to work on one 32 GB card by any flag — that needs a second GPU
(data-parallel, one agent per GPU, each with its own full KV pool).

### ScriptEngine's own LLM endpoints are unchanged

`scriptengine/config.py` still points the extraction and writer pipelines at LM Studio:

```python
llm_base_url:    str = "http://localhost:1234/v1"   # line 133
writer_base_url: str = "http://localhost:1234/v1"   # line 149
```

This was left alone deliberately — only opencode was migrated. To point a pipeline run at
NInfer for one shell:

```powershell
$env:SCRIPTENGINE_LLM_BACKEND  = "local"
$env:SCRIPTENGINE_LLM_BASE_URL = "http://127.0.0.1:18080/v1"
$env:SCRIPTENGINE_LLM_MODEL    = "qwen3.8-27b-ninfer"
```

---

## 10. Verification

```powershell
# 1. Server identity
curl.exe -s http://127.0.0.1:18080/v1/models
# -> {"data":[{"id":"qwen3.8-27b-ninfer","object":"model","owned_by":"ninfer"}],...}

# 2. Generation
wsl -d Ubuntu-24.04 -- curl -s http://127.0.0.1:18080/v1/chat/completions `
  -H "Content-Type: application/json" `
  -d '{\"model\":\"qwen3.8-27b-ninfer\",\"messages\":[{\"role\":\"user\",\"content\":\"Name the capital of Japan in one word.\"}],\"max_tokens\":512,\"reasoning_effort\":\"none\"}'
```

Then confirm from the server log that speculation is genuinely running — this is the line that
proves MTP is active rather than merely accepted as a flag:

```powershell
wsl -d Ubuntu-24.04 -- grep "speculative=mtp" /root/ninfer-work/logs/serve.log | tail -3
```

```
[req 1] done finish=stop_token prompt=61 gen=29 cache=0 reuse=full_reset ttft=27ms
        prefill=2275.3tok/s decode=198.5tok/s wall=0.17s speculative=mtp 3.22tok/round (74.1%)
```

Other things worth checking in a healthy startup line: `weights nvfp4` (NVFP4 really in use, no
silent fallback), `kv cache dtype int8-group64` (INT8 KV active), `mtp fallback steps 0`.

Per-request records with full precision are appended to
`/root/ninfer-work/logs/requests.jsonl`.

---

## 11. Troubleshooting

**`tensor descriptor does not match target contract: text/token_embedding`**
The local patch is missing or was reverted by a `git pull`. See section 3.

**Server starts, then something else on the GPU OOMs.**
VRAM sits at ~29 GB of 32.6 GB with the display also on this card. Lower `--kv-capacity`
(each 32,768 tokens ≈ 1.15 GiB) or close GPU-heavy desktop apps.

**18 GB of download traffic on every WSL boot.**
A previous bring-up installed three systemd units. All three are now **disabled**:
`ninfer-model-download.service`, `ninfer-cuda-install.service`, `ninfer-build.service`.
The download unit re-fetches the entire model if re-enabled. Check with:

```powershell
wsl -d Ubuntu-24.04 -- systemctl is-enabled ninfer-model-download.service
```

**opencode ignores a config change.** It reads config only at startup. Restart it.

**A request field seems ignored.** If it was set under the *provider's* `options`, it was
dropped. Move it under the model's `options`. See section 9.

---

## 12. SGLang removal record (2026-08-22)

SGLang was fully removed. Deleted:

| Path | Reclaimed |
|---|---|
| `E:\models\sglang-nvfp4` (`RadixArk/Qwen3.8-27B-NVFP4` weights) | 20.44 GB |
| `/home/nikhil/sglang-qwen38` (repo + venv) | 8.6 GB |
| `/home/nikhil/.cache/uv` (build cache for that venv) | 8.4 GB |
| `/root/ninfer-work/models/.cache` (an 8.67 GB `.incomplete` HF blob) | 8.1 GB |
| `/home/nikhil/.cache/{flashinfer,sglang,tvm-ffi}`, `.triton`, `.nv`, SGLang logs | ~40 MB |

**Total this pass: ~37.3 GB** (20.4 GB on `E:`, 16.9 GB inside WSL), plus 9.5 GB of duplicate
`.hf-partials` removed earlier.

Verified before deleting: `E:\models\` contained nothing but `sglang-nvfp4`, and LM Studio keeps
its models in `C:\Users\Nikhil\.lmstudio\models` — it was not touched and still runs on port 1234.
The empty `E:\models\` directory was left in place.

---

## 13. Key settings snapshot

- Model: `Ostfralla/Qwen3.8-27B-NVFP4-NInfer` at `/root/ninfer-work/models/qwen3_8_27b_nvfp4.ninfer` (ext4)
- Engine: NInfer `feaf4dd0` + `qwen38-nvfp4-local.patch`, CUDA 13.1.115
- Server: `0.0.0.0:18080`, model id `qwen3.8-27b-ninfer`, auth disabled, CORS on
- Context: `--max-context 262144`, **`--kv-capacity 278528`**; opencode advertises **229376** + 32768 output
  (= 262,144 exactly, the model's native max — single-agent config, see §6z)
- KV cache: `int8` (`int8-group64`) — **35,905 bytes per token**
- Speculation: `--spec mtp --draft-tokens 3 --lm-head-draft`
- Sampling: **`--greedy`** (server-side; client sampling config is silently ignored)
- Prefill chunk: `4096`
- Concurrency: `3`, pending timeout 120 s, default max tokens 20,480
- Thinking: **on** (generated every turn). `--preserve-thinking` **removed** — prior turns'
  reasoning is no longer replayed. `reasoning_effort` from opencode does not reach the server.
- Vision: **off**
- Host-KV cache: **`--host-kv-cache-mib 14336`** (PR #64, merged 2026-08-24) — parks evicted
  sessions in pinned RAM. **27x faster agent follow-ups** (36.7 s → 1.4 s). 14336 is the measured
  max; 16384 fails to allocate. See §6a.
- Engine: now at `d6f3fcc4` (was `feaf4dd0`) + our patch. Rollback binary:
  `/root/ninfer-work/ninfer-serve.prePR64`
- Startup: **~13.8 s** (was 5.4 s — the extra ~8 s is pinned host-KV RAM allocation)
- VRAM: ~31.3 GB / 32.6 GB, `slack=916 MiB` — **keep above ~900 MiB**; below that decode and
  prefill both fall off a cliff (see §6)
- Host RAM: 14 GiB pinned for host-KV, inside the 26 GB WSL2 ceiling (~10 GB left free in WSL)

Measured 2026-08-24 (identical prompts, 13 requests per config, unique prompts = 0% prefix cache):

| | Decode | Prefill | Accept |
|---|---|---|---|
| Before (temp 1.0) | 124.1 tok/s | 4,346 tok/s | 40.1% |
| **After (`--greedy`)** | **143.3 tok/s** | 4,295 tok/s | **50.5%** |

Older headline figures in this doc (171–178 tok/s decode, 10.7–11.7k tok/s prefill) are
**short-prompt best cases**. Against real prompt sizes the curve is:

| Prompt tokens | Decode |
|---|---|
| 0–4k | 171 tok/s |
| 64k–131k | 142 tok/s |
| 131k–196k | 130 tok/s |
| 196k–262k | 117 tok/s |

Production p50 prompt is ~112k, so ~140 tok/s is the number to plan around, not 178.
Prefix caching saves **93.6%** of prefill in real use (715M of 764M tokens), so TTFT stays
~0.5 s even at 130k+ — prefill is not the bottleneck; KV pool capacity is.
