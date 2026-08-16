# Extraction runbook — the model pass

Everything measured on 2026-08-15 while getting the ability-extraction pass to
run at a sane speed. Written so none of it has to be discovered twice.

Retrieval never calls a model. This document is only about the two index-time
passes — `ingest/abilities.py` and `ingest/classify.py` — and almost entirely
about the first.

---

## TL;DR — the working setup

LM Studio serving `qwen/qwen3.8-27b` on `:1234`:

```powershell
nvidia-smi -pl 600      # elevated; the card shipped capped below its own maximum
lms load qwen/qwen3.8-27b -c 36864 --parallel 8 --ttl 7200 --speculative-draft-mtp -y
```

| setting | wrong value | correct value |
|---|---|---|
| **context length** | 262,144 (default) / **8,192** | **36,864** (sized to parallel) |
| **`--parallel`** | 4 while power-capped | **8**, matched by `--workers 8` |
| **GPU power limit** | 570 W | **600 W** (the card's max) |
| Enable Thinking | on | **off** (see below — the preset will not do it) |
| Reasoning Effort | Extra High | **low** |
| `SCRIPTENGINE_ANSWER_TOKENS` | 32,000 / 2,048 | **3,072** |
| speculative decoding | off | **MTP on** |
| CPU Thread Pool | 16 | **8–12** |
| seed | random | **fixed** |
| Keep Model in Memory | — | **on** |
| Offload KV Cache to GPU | — | **on** |
| GPU Offload | — | 65 (all layers) |

```powershell
$env:SCRIPTENGINE_LLM_BACKEND  = "local"
$env:SCRIPTENGINE_LLM_BASE_URL = "http://localhost:1234/v1"
$env:SCRIPTENGINE_LLM_MODEL    = "qwen/qwen3.8-27b"
$env:SCRIPTENGINE_ANSWER_TOKENS = "3072"
$env:SCRIPTENGINE_LLM_TIMEOUT_SECONDS = "1800"
python -u -m scriptengine.cli abilities --series jjk --refresh --workers 4
```

**Per call: 90.8s → 3.1s** against the 262,144 default. Two identical calls
returned byte-identical output.

**8,192 was this document's own recommendation until 2026-08-16 and it is
wrong for any run with `--parallel > 1`.** It cost 115 consecutive failures.
See *Context is a shared pool* below, which supersedes it.

---

## Turning thinking off so it stays off

**`lms load` has no preset flag.** Every CLI reload therefore comes up with
thinking *on*, whatever the GUI last showed — the failure mode that silently
returned after a reload on 2026-08-16 and burned 91% of the output budget:

| | thinking on | thinking off |
|---|---|---|
| reasoning tokens | 82 of 90 completion tokens | **0** |
| per call | 3.8s | **2.7s** |

The durable fix is a **per-model default config**, which LM Studio applies at
load time including from the CLI. Model-specific keys encode the model id with
`/`→`.` and `-` dropped, so `qwen/qwen3.8-27b` becomes `qwen.qwen3.827b`:

`C:\Users\Nikhil\.lmstudio\.internal\user-concrete-model-default-config\qwen\qwen3.8-27b.json`

```json
{
  "preset": "",
  "operation": {
    "fields": [
      {"key": "ext.virtualModel.customField.qwen.qwen3.827b.enableThinking", "value": false},
      {"key": "ext.virtualModel.customField.qwen.qwen3.827b.reasoningEffort", "value": "low"}
    ]
  },
  "load": { "fields": [{"key": "llm.load.contextLength", "value": 20480}] }
}
```

Two fields from the `No thinking 27b` preset are deliberately **not** copied
here:

* **`llm.prediction.systemPrompt`** — the client sends its own system message
  and a config-injected one is a needless risk to it. It also buys nothing; see
  the refutation below.
* **`llm.load.contextLength: 8192`** — that is the undersizing itself. `-c` on
  the command line overrides whatever this file says, so the run stays
  controllable per-invocation while thinking stays off.

Verify after every load, because this is the setting that comes back:

```python
usage["completion_tokens_details"]["reasoning_tokens"]   # must be 0
```

The GUI's chat-panel thinking toggle reflects the *app's* UI state and does not
govern API requests. Do not read it as the answer; probe the endpoint.

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
can grow beyond that. Confirmed again on 2026-08-16 over 48 real relation
windows: **max prompt 1,463 tokens, max completion 1,306.**

---

## Context is a shared pool, not a per-slot budget

This is the correction to "never raise context to be safe", which was the advice
here and is only true at `--parallel 1`.

**`-c` sets one KV pool that every concurrent slot draws from.** With
`--parallel N` each slot gets roughly `context / N`, so the requirement is:

```
parallel x (max_prompt + max_tokens)  <=  context
```

At the settings above: `4 x (1463 + 3072) = 18,140 <= 20,480`. ✓

Getting this wrong does not look like a sizing error. On 2026-08-16 a run at
`-c 5120 --parallel 6` with `max_tokens 3072` needed `6 x (1735 + 3072) =
28,842` and produced **115 consecutive failures**, logged as:

```
E srv send_error: task id = 1729, error: Context size has been exceeded.
I slot release: id 1 | task 1729 | stop processing: n_tokens = 1199, truncated = 0
```

The trap is `n_tokens = 1199` — far *below* 5,120, which reads as "the context is
not the problem" and argues for lowering it further. The number is one slot's
usage; the pool was exhausted by the other five. **The fix for
`Context size has been exceeded` is almost always more total context, not less.**
The earlier thrash at `8192 --parallel 4` was the same fault (needed 15,132).

Both bounds still hold, so size it, do not maximise it:

* too small → `Context size has been exceeded`, in bulk;
* too large → KV cache eats the card, prefill crawls, and the log fills with
  `making room for prompt cache entry, removing oldest entry (823 MiB)`.

VRAM cost measured on a 32,607 MiB card, weights 17.74 GB:

| context | parallel | VRAM |
|---|---|---|
| 20,480 | 4 | 24,435 MiB |
| 28,672 | 6 | 25,913 MiB |

That is ~0.33 MiB per token of KV. `lms load --estimate-only` reported 16.52 GiB
for both and is **not** usable for this — it ignores the KV growth. Measure with
`nvidia-smi` after loading.

---

## Concurrency: 8 — but the answer depends on the power cap

Measured twice on 2026-08-16, and **the two runs disagree**, which is the useful
part. Both used a fixed workload of 48 real relation windows with identical
prompts and `max_tokens 3072`.

**First, while the card was power-capped at 570 W with other GPU apps running:**

| config | windows/min | median | p95 |
|---|---|---|---|
| 4 @ 20,480 | 27.5 | 7.6s | 14.6s |
| 6 @ 28,672 | **26.4** | 12.3s | 23.5s |
| 4 @ 20,480 + MTP | **27.9** | 7.2s | 11.8s |

That said 4 was the ceiling and more slots only queued. It was true *under those
conditions* and wrong as a general rule.

**Then, after raising the power limit to 600 W and closing other GPU apps:**

| config | windows/min | median | p95 | VRAM |
|---|---|---|---|---|
| 4 @ 20,480 | 32.6 | 7.0s | 11.3s | 20.5 GB |
| 6 @ 28,672 | 34.1 | 10.2s | 16.4s | 23.1 GB |
| **8 @ 36,864** | **35.2** | 12.9s | 21.4s | 24.5 GB |
| 10 @ 46,080 | 35.6 | 16.8s | 27.3s | 26.0 GB |

Every config ran 48/48 with zero truncations. 8 is the knee: 10 buys 1.1% for
30% more latency.

**Check `clocks_throttle_reasons` before concluding anything about concurrency.**
While `SW Power Cap` is active the GPU cannot use extra slots and they only add
latency; once it is not, they help. The whole reversal above is that one
variable.

**The benchmark understates the real gain.** In production the same change was
worth far more than 8%:

| | rows/min |
|---|---|
| 4 workers | 33.8 |
| **8 workers** | **52.0** (+54%, sustained over 15 min) |

The fixed-workload benchmark feeds a flat list of uniform windows. A real run
also parallelises per-character work — `passages()`, window splitting, the store
write — and overlaps characters whose sizes differ by two orders of magnitude,
which more slots absorb. **Benchmark to compare configs; measure the real run to
size the job.**

**Measure throughput in rows/min, not characters/min.** Window counts per
character run from 2 to 332, so characters/min swings with whatever the queue
happens to be chewing. It reported a 20% gain from closing GPU apps that
rows/min showed as zero.

**`--workers` also sets the commit batch.** `relations.py` chunks the queue at
`workers * 4`, and `pool.map` yields in order, so one heavy character at the head
of a chunk holds back every commit behind it. At 8 workers that is 32 characters
per commit: progress arrives in larger, less frequent jumps, and an abort loses
up to 32 characters of work. A five-minute gap with no new rows is normal — check
GPU utilisation, not the row count.

**Speculative decoding (MTP) is free and slightly better.** Throughput is within
noise but p95 improves 14.6s → 11.8s, so leave `--speculative-draft-mtp` on.

**CPU Thread Pool: 8-12, not 16.** The model is fully GPU-offloaded, so the CPU
only tokenises and samples. The 9950X3D is dual-CCD — 8 cores with 3D V-Cache,
8 without — and a pool above 8 spans both dies and pays cross-CCD latency on
every sync. Threads above that also compete with the extraction workers, since
llama.cpp thread pools spin-wait rather than sleep.

---

## The GPU settings that did and did not matter

Measured on an ASTRAL LC RTX 5090, liquid-cooled, 41-57C throughout — thermals
were never the limit.

| change | rows/min | verdict |
|---|---|---|
| baseline | 30.25 | — |
| closed other GPU apps | 29.8 | **no throughput gain** |
| power limit 570 → 600 W | 33.2 | **+11%** |
| memory clock +500 | 33.8 | +2%, noise |
| 4 → 8 workers | **52.0** | **+54%** |

**The power limit was set below the card's own maximum.** `power.limit 570 W`
against `power.max_limit 600 W`, with `SW Power Capping` accumulating. Raising it
needs an elevated shell:

```powershell
nvidia-smi -pl 600
```

After that the cap stopped engaging entirely and draw settled at 355-478 W —
i.e. it then had headroom, which is what made 8 slots pay off. There is no 110%:
`power.default_limit` and `power.max_limit` are both 600 W, so 100% in a tuning
tool *is* the ceiling.

**Closing other GPU applications freed 2.9 GB of VRAM but did not speed anything
up.** Worth doing — it is what let the wider KV pool fit — but not a throughput
change, and the apparent 20% gain was a characters/min artefact.

**Memory overclocking is not worth chasing here.** +500 on the effective rate is
+250 MHz actual on 13,801, a 1.8% bandwidth increase, and it measured as noise.
It was stable — 400 rows written under it, zero outside the closed vocabulary,
zero empty quotes — so it does no harm. The lever is real for a bandwidth-bound
workload; the magnitude available is too small to matter.

**Do not raise GPU voltage.** While power-limited, more voltage spends more of a
fixed budget per clock and makes throughput worse.

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

**Thinking cannot be turned off from the request.** All four request-side
methods were measured on 2026-08-16 against the same prompt and **every one was
ignored**:

| attempt | reasoning tokens |
|---|---|
| plain (control) | 96 |
| `{%- set enable_thinking = false %}` in the system message | 97 |
| `/no_think` appended to the system message | 108 |
| `"chat_template_kwargs": {"enable_thinking": false}` | 96 |

`enableThinking` is a virtual-model field resolved when the model is **loaded**,
so nothing sent per-call can reach it. This also means the preset's
`llm.prediction.systemPrompt` Jinja directive is inert over the API — it is not
what was disabling thinking. Use the per-model default config above.

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

**JIT auto-load silently undoes the load settings.** Any stray API request will
load the model with *default* config — context back to 262,144, thinking back
on. A probe did this and cost a bogus 90.8s measurement. Disable auto-load in LM
Studio's developer/server settings, and note that the per-model default config
above fixes the thinking half of this but not the context: an auto-load takes no
`-c`. Probe with `scriptengine.eval.model_health` rather than assuming.

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

**An empty log does not mean a stalled run.** `Tee-Object` buffers until the
process exits, and `>` through `Start-Process` buffers too — so a healthy run
can show a 0-byte log for many minutes even under `python -u`. On 2026-08-16
this was misread as a stall on a run that was working correctly.

Judge liveness from things that cannot buffer:

```powershell
nvidia-smi --query-gpu=utilization.gpu,memory.used --format=csv,noheader  # 80-98% while extracting
```

plus a row count against the series `facts.db` taken twice a few minutes apart.

**Two python PIDs is normal, and the parent shows 0 CPU.**
`.venv\Scripts\python.exe` is a shim that re-execs the real uv-managed
interpreter, so `relations --series db` appears twice: the parent idles at zero
CPU time waiting on its child, which does the work. Both have the *same* start
time — that is how to tell this from a genuine orphan, which will be older. Do
not kill the "idle" one thinking it is stuck.

**`canon-run` refuses a server older than the newest `.py`.** Restart the API
server before measuring, and use `--skip-eval`.

---

## A misconfigured run does not leave bad data

Worth knowing before paying for a full re-extraction after any config mistake.
Context size decides whether a call **succeeds**, not what a successful call
**says**: at `temperature 0` the same prompt returns the same answer at 8,192 as
at 20,480. Undersizing fails *loudly*, and every failure mode drops the row
rather than storing a damaged one:

* `Context size has been exceeded` → raises → nothing stored;
* `finish_reason == "length"` → the truncation guard in `llm/client.py` raises
  rather than storing half-parsed JSON;
* a name or quote not present verbatim in the passage → dropped by the
  groundedness gate.

So a botched run costs **completeness, not correctness**, and completeness
self-heals: rows cache on `revid` + `PROMPT_VERSION`, a failed character stored
no rows, and `needs_relations` therefore hands it back on the next run.

Verify rather than assume, with a vocabulary check — anything outside the closed
set would be the signal to re-extract:

```sql
SELECT relation, COUNT(*) FROM relations GROUP BY relation ORDER BY 2 DESC;
```

After the 115 failures this returned 1,700 rows across exactly the 12 valid
relations, so none of that work needed redoing.

One caveat to record: `PROMPT_VERSION` does not encode the thinking setting, so
rows extracted with thinking on and off coexist. Both passed the groundedness
gate and are checkable against the source, and a `--refresh` re-extraction
normalises them.

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

**Never estimate a run from the head of its queue.** Window counts per character
are extremely skewed, and `needs_relations` returns the biggest characters
first, so a sample of the first N is a sample of the worst case. Measured on db
relations, 1,057 characters remaining:

| | windows |
|---|---|
| Goku | 332 |
| Vegeta | 263 |
| Gohan | 242 |
| **mean** | **7.1** |
| **median** | **2** |
| **total** | **7,515** |

Extrapolating the first 25 characters (109 windows each) gave ~115,000 windows
and a **25-30 hour** estimate. Counting all of them gave 7,515 and **~4.5
hours** — the real figure was off by 15x. Count the whole queue; it is one cheap
pass over passages and needs no model:

```python
sum(len(_windows(t)) for who in needs_relations(store, ov)
    for _s, t in passages(store, who, ov))
```

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
