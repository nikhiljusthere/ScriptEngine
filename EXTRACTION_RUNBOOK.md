# Extraction runbook — the model pass

Everything measured on 2026-08-15 while getting the ability-extraction pass to
run at a sane speed. Written so none of it has to be discovered twice.

Retrieval never calls a model. This document is only about the two index-time
passes — `ingest/abilities.py` and `ingest/classify.py` — and almost entirely
about the first.

---

## TL;DR — the working setup

LM Studio serving `qwen/qwen3.8-27b` on `:1234`, loaded with the
**`No thinking 27b`** preset:

| setting | wrong value | correct value |
|---|---|---|
| **context length** | **262,144** (default) | **8,192** |
| Enable Thinking | on | **off** |
| Reasoning Effort | Extra High | **low** |
| `SCRIPTENGINE_ANSWER_TOKENS` | 32,000 | **2,048** |
| seed | random | **fixed** |
| Keep Model in Memory | — | **on** |
| Offload KV Cache to GPU | — | **on** |
| GPU Offload | — | 65 (all layers) |
| Max Concurrent | — | 4, matched by `--workers 4` |

```powershell
$env:SCRIPTENGINE_LLM_BACKEND  = "local"
$env:SCRIPTENGINE_LLM_BASE_URL = "http://localhost:1234/v1"
$env:SCRIPTENGINE_LLM_MODEL    = "qwen/qwen3.8-27b"
$env:SCRIPTENGINE_ANSWER_TOKENS = "2048"
$env:SCRIPTENGINE_LLM_TIMEOUT_SECONDS = "900"
python -u -m scriptengine.cli abilities --series jjk --refresh --workers 4
```

**Per call: 90.8s → 3.1s.** Two identical calls returned byte-identical output.

Preset lives at
`C:\Users\Nikhil\.lmstudio\config-presets\No thinking 27b.preset.json`. The
model-specific keys encode the model id with `/`→`.` and `-` dropped, so
`qwen/qwen3.8-27b` becomes `qwen.qwen3.827b`:

```json
"ext.virtualModel.customField.qwen.qwen3.827b.enableThinking": false,
"ext.virtualModel.customField.qwen.qwen3.827b.reasoningEffort": "low",
"llm.prediction.systemPrompt": "{%- set enable_thinking = false %}",
"llm.load.contextLength": 8192
```

The `systemPrompt` Jinja directive does **not** clobber the system message the
client sends — verified, the reply still came back in the `{"abilities": [...]}`
shape that only our own system prompt defines.

---

## The one setting that mattered

Context length defaulted to **262,144**. That allocates roughly 32x the KV cache
this workload needs, filling the 5090 (31,957 of 32,607 MiB) and making every
prefill crawl. It alone accounted for the 90.8s → 3.1s difference.

The prompts are small. Measured over 316 real extraction prompts:

| | chars | tokens |
|---|---|---|
| median | 2,462 | ~703 |
| p95 | 5,302 | ~1,514 |
| max | 5,796 | ~1,656 |

Windows are capped at 4,000 chars with 300 overlap (`_windows`), so no prompt
can grow beyond that. 8,192 gives ~2x headroom over prompt + answer and leaves
VRAM for concurrency.

**Never raise context to "be safe".** It is the KV cache allocation, and this
pass cannot use it.

---

## Why local, not opencode

| | opencode | local (LM Studio) |
|---|---|---|
| shape | CLI subprocess, an *agent* | OpenAI HTTP endpoint |
| per call | 89s | 3.1s |
| parallelism | network-bound, 16 workers fine | GPU-bound, matched to Max Concurrent |
| failure modes | rate limits, silent hangs, orphaned children | none seen |

opencode wraps an agent around each call — process spawn, scaffolding, NDJSON
stream, teardown. With the model local there is nothing to buy with that
overhead: the grounding that once justified opencode is enforced in
`abilities.py`, not by opencode.

It also violates the repo owner's standing "no cloud inference" preference,
which local satisfies.

---

## Dead ends — do not re-test

**`opencode/deepseek-v4-flash-free` was dead on 2026-08-15.** A one-word probe
("Reply with the single word OK") returned nothing in **400s**; a jjk run
finished **0 extracted, 8 timed out at 600s**. It *hangs* rather than erroring,
so `LLMRateLimited` — which only inspects failed output — never fires. Probe it
before trusting it.

Free-model probe, same trivial prompt:

| model | response |
|---|---|
| `opencode/laguna-s-2.1-free` | 4s |
| `opencode/nemotron-3.5-lightning-free` | 8s |
| `opencode/nemotron-3-ultra-free` | 49s |
| `opencode/mimo-v2.5-free` | timeout >100s |
| `opencode/hy3-free` | timeout >100s |
| `opencode/deepseek-v4-flash-free` | timeout >400s |

**Unloading/reloading the model between reads does not help.** Every extraction
call is stateless — a fresh `messages` array with one system and one user
message. No conversation history accumulates, so there is nothing to clear;
unloading frees VRAM, not "tokens". A 27B is 16-30GB off disk per load. The
repeated loading seen in LM Studio was JIT + idle-TTL churn, and it cost time.

**Do not trim the level-0 infobox/lead card from passages.** It looks like waste
— 26.7% of hxh passage text, 14.2% of jjk — but it is load-bearing:

| series | share of stored ability rows from that card |
|---|---|
| berserk | 32.7% |
| hxh | 28.6% |
| opm | 24.7% |
| bleach | 10.2% |

Killua's `Godspeed`, `Whirlwind` and `Speed of Lightning` come from exactly
there. None has a page, a node, a category or a `users` edge — that infobox line
is the *only* place the wiki records them.

---

## Operational traps

**The API server and the model cannot share the GPU.** The server loads
`bge-large` and `bge-reranker-v2-m3` onto the same card. With the 27B resident
that exhausts 32GB and LM Studio answers `500 Internal Server Error` to every
request: a csm run recorded three failures and no rows, and the only visible
symptom was an idle GPU. Extraction runs fine only because no server is up —
stop it first. The runner refuses to start while one is running.

Measured: 23.3GB with the model alone at 8,192 context, 31.8GB with the server
too, on a 32.6GB card.

**A scoring run needs the server; an extraction run needs it gone.** They are
mutually exclusive on one machine. Score the coverage banks through
`build_roster` in-process instead — roster mode is pure SQLite and touches
neither.

**JIT auto-load silently undoes the preset.** Any stray API request will load
the model with *default* config — context back to 262,144, thinking back on. A
probe did this and cost a bogus 90.8s measurement. Disable auto-load in LM
Studio's developer/server settings.

**Killing a run's python parent orphans its opencode children.** They keep
running and keep consuming the provider's quota. 16 orphans starved a live run
until they were found. Kill by process name, not just the parent:

```powershell
Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
  Where-Object { $_.CommandLine -match 'scriptengine' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
Get-Process opencode | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-6) } |
  Stop-Process -Force
```

**`Tee-Object` buffers until the process exits.** Every early run looked frozen
because the per-series log was empty. Redirect with `>` instead; `python -u`
then streams properly.

**`canon-run` refuses a server older than the newest `.py`.** Restart the API
server before measuring, and use `--skip-eval`.

---

## Cost model

Calls scale with *windows*, not characters:

| series | characters | calls/char |
|---|---|---|
| berserk | 92 | 3.5 |
| jjk | 121 | 4.1 |
| bleach | 283 | ~6 |
| csm | 158 | ~4 |
| db | 203 | ~6 |
| hxh | 393 | 3.5 |
| opm | 475 | ~5 |
| **onepiece** | **1,640** | **12.5** |
| **total** | **3,365** | **~28,600 calls** |

One Piece is ~20,500 of those — **70% of the whole corpus on one wiki**.

`--bank-only` restricts to the characters the question bank names: **65
characters, ~353 calls, a 98.8% reduction**. Use it for a fast scoring loop
only. The bank is a benchmark, not the goal — full coverage is what the project
actually needs, so it is not the default. Note it also leaves the store on two
prompt versions, since unscoped characters keep their existing rows.

---

## What the model actually does

Reads one window of a character's declared ability sections, plus the section
breadcrumb, character name, series, and the allowed `kinds`. Returns one line
per ability: name, kind, evidence. That is all — it is span-selection, not
reasoning, which is why Reasoning Effort should be as low as the model allows.

Four guards run *after* the reply, so a weak model costs recall rather than
truth:

- **the name must appear verbatim in the passage shown** (`_grounded_in`) —
  caught 91 invented names across 2,841 rows (`Cero Barrage`,
  `Ghostly Wolf Summoning`);
- lower-case names dropped;
- declared `ability_stopwords` dropped;
- names longer than 5 words dropped — beyond that it is describing, not naming.

Rows cache on page `revid` + `PROMPT_VERSION`. Bumping `PROMPT_VERSION`
invalidates all eight wikis at once, which is what forces a full re-extraction.

---

## When the answer field comes back empty

The model answers without a field it was asked for if the JSON shape is split
across lines. Adding `acquired` on a second line produced replies with no
`acquired` at all — every row would have defaulted to `innate` and Yuta's copied
techniques would have been indistinguishable from his own. On one line it
answers correctly.

Omitting a field where the passage says nothing about it is right, and the store
defaults those. What is not right is never being asked.

## What the cross-window limit costs

A window is 4,000 characters, and the model only knows what is in the one it is
shown. Yuta's page says `Copy: Yuta's innate technique allows him to copy the
innate techniques of people who had their body parts consumed by Rika` in one
section and names `Limitless` in another, so `acquired` came back `innate` for
all 570 jjk rows. The field works — given a passage that states the copying, it
returns `copied` with the right reason — but it cannot join two windows.

Anything needing evidence from two places on a page needs either a wider passage
or a second pass over what the first one stored.

## Related

- `PRECISION_PLAN.md` — what has been refuted by measurement
- `ANSWER_QUALITY_REVIEW.md` — the retrieval-side causes
- `RELATION_GAPS.md` — per-wiki inventory of discarded relations
