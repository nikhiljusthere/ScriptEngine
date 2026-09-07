---
name: qwen-switch
description: Switch the local Qwen 3.8 27B (ninfer, :18080) between context modes — 262k exploratory, 100k service, or a dial-down — to free or reclaim GPU headroom, autonomously, mid-plan. Use when the next phase needs the :8000 embedder+reranker on CUDA alongside Qwen, or 2 parallel subagents, and when the GPU phase ends and full context is wanted again.
---

# qwen-switch — autonomous Qwen context-mode switching

Full doc: `docs/ops/QWEN_MODES.md` (repo = /home/goblin/ScriptEngine).
Switcher: `/home/goblin/ninfer-work/qwen-switch.sh` (has `--dry-run`, `--api`, `--force`).

## When to switch — decide at phase boundaries, not per step

Each flip costs a 30–60 s model reload + a cold re-prefill. One switch per
phase boundary; never thrash.

- **SWITCH DOWN (262k → 100k / dial-down)** when the upcoming phase needs,
  *simultaneously*: Qwen alive (I keep working) **and** the `:8000`
  embedder+reranker on CUDA (~5.3 GB — live span-recall probes, page-runs,
  `/context` work) **or** up to 2 parallel subagents.
- **NO SWITCH for a heavy Qwen LLM batch** (`events-extract` / 27B
  extraction). The hard rule is the opposite: stop `:8000` (or run it on CPU),
  Qwen owns the card. Context mode is irrelevant there.
- **SWITCH BACK (→ 262k)** when the GPU phase ends and the remaining work is
  linear/exploratory (full context; `:8000` returns to CPU).

## Pre-flight (model alive — before the switch call)

1. **Checkpoint** (see the `switchpoint` skill): `git commit` + refresh
   `plan/SWITCHPOINT.md` (mode, sha, position, in-flight, exact next step).
2. **Fit guard**: the current transcript must fit the target context:
   ```bash
   echo $(( $(wc -c < "$PI_SESSION_FILE") / 4 ))   # est. tokens of THIS session
   ```
   If it exceeds the target (102400 for 100k): the switcher hard-refuses
   (exit 2). Do a full checkpoint, re-run with `--force`, and hand the user
   the fresh-session one-liner (below). `--force` is only for a deliberate
   handoff — never a dodge.
3. **No extraction in flight**: `pgrep -af 'events[-_]extract'` empty (the
   script refuses too).

## The switch — ONE atomic tool call

```bash
cd /home/goblin/ninfer-work && ./qwen-switch.sh 100k
```

- Invoke via the `bash` tool with **`timeout: 300000`** (ms). The default
  120 s is shorter than the reload; a timeout is *fine* — the load is
  detached and survives, then poll `curl -s -m 2 http://127.0.0.1:18080/v1/models`
  with a bounded status-printing loop.
- **Never split pkill / reload / verify across tool calls**: the harness makes
  a model call between calls, and that call dies mid-reload.
- During the call: no model, no thinking, no editing — by design. The pi
  process survives; only the model server recycles (same model-id, same port).

## Post-flight (model back)

1. `cat /home/goblin/ninfer-work/qwen_mode.txt` (mode, ctx, free MiB, api device).
2. `nvidia-smi` sanity. The script already placed `:8000` on the right device
   (CUDA iff headroom ≥ 6 GiB, else CPU).
3. Continue the plan from the switchpoint. First turn is a cold prefill (~1–2 min).

## The overflow handoff (transcript did not fit)

After a `--force` down-switch the current session is done (its transcript
overflows the new cap). Everything is on disk — hand off with:

> "Switched to 100k; the transcript didn't fit, so this session ends here.
> Open a fresh `pi` in the project dir and say: *Read plan/SWITCHPOINT.md
> and continue from there.*"

## Never

- Switch before the checkpoint is complete.
- `--force` past a fit refusal without a full checkpoint + handoff.
- Rely on pi's compaction to make the transcript fit — the declared context in
  config is larger than the server's real cap; measure the transcript myself.