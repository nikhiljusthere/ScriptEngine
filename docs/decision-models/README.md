# Decision models (Jev and its open alternatives) for ScriptEngine

Research notes from a 2026-09-24 session. It covers: what "System One" decision models are, which
open-weights ones exist and what their model cards actually say, all 485 builds on
[madewithjev.com](https://madewithjev.com), which 30 of them matter for ScriptEngine, and how they
would run on this machine's **NInfer** setup (Qwen3.8-27B, :18080).

- Full build list: [ALL_BUILDS.md](ALL_BUILDS.md) (485 rows, generated from the site's sitemap, the
  30 picks marked).
- Nothing here is implemented yet. [The plan](#implementation-plan) is at the bottom.

---

## 1. What Jev is

Jev is TypeSafe AI's hosted **"System One" model**. It does not generate text. You send a `state`
(text, JSON, a DOM, an email) and typed questions:

- `choice`: pick one of up to 255 options
- `score`: an ordinal level
- `noul`: yes/no

It returns a calibrated probability for every option from a single forward pass, through
`POST /v1/systemone`. Output is roughly one token, so latency is dominated by prefill.

- **API only.** Weights unpublished. $0.042 per million input tokens, output free, no free tier.
  Reachable through TypeSafe, OpenRouter, Vercel AI Gateway and Cloudflare Workers.
- **We will not use it.** `~/.claude/CLAUDE.md` forbids cloud inference. Everything below is about
  the open-weights alternatives, and about tools written for Jev that accept a different endpoint.

The pattern is the useful part: **"LLM plans or writes, the decision model decides, code acts."**
Wherever a pipeline asks a model a question with a fixed, enumerable answer, a decision model
answers it in tens of milliseconds, returns a probability instead of text to parse, and cannot
hallucinate an option that was not offered.

## 2. Open-weights decision models

These were checked against the Hugging Face API and model cards. A summary pasted into the session
got several details wrong; the corrections are marked. All were uploaded between 2026-09-16 and
2026-09-20, and every number is self-reported.

| Model | License | What the model card says | Correction to the pasted summary |
|---|---|---|---|
| [convaiinnovations/laya](https://huggingface.co/convaiinnovations/laya) | Apache-2.0 | English checkpoint on ModernBERT-large (~840 MB). Multilingual checkpoint on mmBERT-base (322M, 100+ languages). 32.8 ms on a T4 (multilingual), 39.5 ms (English), 193–464 ms on CPU. Ships `laya-serve` (Jev-compatible `/v1/systemone`), an MCP server, LangChain integration and `laya-ts`. | RLCD stands for "RL for **Calibrated Decisions**", not Constitutional AI. The English checkpoint collapses on non-Latin scripts (Khmer: 0% accuracy at 95% confidence), so let its `Router` pick the checkpoint. |
| [wfzyx/von](https://huggingface.co/wfzyx/von) | Apache-2.0 | 395M on ModernBERT-large plus an Option-Marker head. 8k context. `von serve` gives `/v1/systemone`. Runs on CPU. | **The "91.23%" figure is not on the card.** It reports JevBench easy 93.8% but **hard multi-hop 35–37%, near chance**, and warns against unsupervised multi-hop use. Calibration was fitted on the same public items it reports, so those numbers are in-sample. |
| [openjev/openjev](https://huggingface.co/openjev/openjev) | **CC-BY-NC-4.0** | 84.0% vs hosted Jev's 85.4% on 10k questions. Ties Jev on 100 MiniWoB browser tasks. About 210 ms per web decision on an H100. Speaks Jev's wire API. Served through vLLM. 54 GB in bf16, 29 GB in FP8, MLX builds exist. | **Not DiffusionGemma.** `config.json` is a dense `Qwen3_5ForConditionalGeneration` (64 layers, hidden 5120, about 27B). Needs an 80 GB GPU for the recommended recipe. Non-commercial license. |
| [com-kotobalabs/open-jev-deberta-v3-large](https://huggingface.co/com-kotobalabs/open-jev-deberta-v3-large) | Apache-2.0 | DeBERTa-v3-large, English only, **512-token context**, trained on three narrow domains. | An unrelated independent project, not part of OpenJev. Too small for this work. |
| [Mapika/decider-2b](https://huggingface.co/Mapika/decider-2b) | Apache-2.0 | Qwen3.5-2B-Base, 3.5 GB in bf16, about 4 ms per request with CUDA graphs. Fine-tuned on about 95 decision datasets including Mind2Web element choice, then RL. Reports 93% on live browser tasks. `decider.serve` gives `/v1/systemone`, and the official `typesafe-sdk` works against it through `TYPESAFE_BASE_URL`. Family: 0.8B (1.4 GB), 4B, 35B-A3B (65 GB, NVFP4 19.6 GB), 2B-vision. | Accurate. |
| [iapp/OpenThai-SystemOne](https://huggingface.co/iapp/OpenThai-SystemOne) | Apache-2.0 | 0.8B on Qwen3.5-0.8B-Base, Thai and English, 256-way slot head, Jev-compatible server. About 40 ms on an H100. | Accurate, but irrelevant unless Thai is needed. |

Others found through Hugging Face search, not evaluated:

- `apus-ailab/APUS-OpenJev-v1` in 4B, 9B and 35B-A3B (plus a 9B GGUF)
- `ZefanCai/Open-Jev-{2B,9B,27B}`
- `pngwn/system-one-qwen3.5-4b-scorer` (with an ONNX build)
- `chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF`
- `malevrigns/agent-jev` (0.6B)
- `KaLM-Embedding/KaLM-Jev`

**Security note.** decider, laya and the kotobalabs model ship custom Python (`decider/`,
`rl_common.py`, `typed_decisions/`). Read that code before `trust_remote_code` or `pip install`.
These are week-old repos from unknown authors.

## 3. NInfer cannot serve decisions directly (measured)

Tested live against `qwen3.8-27b-ninfer` on :18080 (engine `d6f3fcc4`):

| Probe | Result |
|---|---|
| `logprobs: true, top_logprobs: 5` | Silently ignored. No `logprobs` field in the response. Grepping the source finds no logprobs code. |
| `response_format: {type: json_schema}` | `400 response_format_not_supported: only response_format {type:text} is supported` |
| `chat_template_kwargs.enable_thinking` | `400 chat_template_option_not_supported` |
| `POST /v1/completions` | Empty response |
| Thinking | Always on (serve flag). The first generated token was `reasoning_content: "We"`. |
| VRAM | 30,340 of 32,607 MiB used. About 2.2 GB free, at the ~900 MiB slack comfort line. |

Every runtime that turns an ordinary LLM into a decision model reads the logits at the last prefill
position. That includes simple-jev, AnyJev, LLM2Jev, logjev, jev-rs, jev-compatible-sglang-vllm and
rizzo-flow. **None of them can run on NInfer as it is.** There are two ways out:

1. **Patch NInfer** to return option logprobs (C++). That would be a second local patch to
   maintain, next to `qwen38-nvfp4-local.patch`, which `git pull` already breaks. Park it unless
   the deep lane below proves too slow.
2. **Split the work into two lanes** (chosen):

```
                     ┌─ FAST lane: small decision model on CPU, :8017, POST /v1/systemone
tools ─► gateway ────┤     von / decider-0.8b / rizzo 1.7B GGUF: ~50–500 ms, calibrated
       (hearim or    │
        a shim)      └─ DEEP lane: NInfer Qwen3.8-27B, :18080, text answer parsed to a choice
                           seconds per call (thinking is on), smart, no probabilities
```

- **The fast lane runs on CPU** to leave VRAM to NInfer and ComfyUI. The 9950X3D is enough for a
  sub-1B model.
- **Deep-lane constraint** (from the NInfer notes): lane eviction is lane-driven, not pool-driven.
  Four small side calls evict a 229k opencode session and force a ~73 s re-prefill. Deep-lane batch
  jobs must run **with concurrency 1, and never while an opencode session is live**.

## 4. The 485 builds

The site has 485 builds, 112 guides/resources and 9 category ("use case") pages. The guides are
articles and videos, not code, so they were not scored. Builds by category:

| Category | Builds | Useful here |
|---|---:|---:|
| Tools and apps | 148 | 19 |
| Agents and browsers | 82 | 1 |
| Research and data | 79 | 9 |
| Content and growth | 61 | 4 |
| Games and real-time | 54 | 0 |
| Triage and routing | 29 | 0 |
| Robotics and devices | 14 | 0 |
| Trading and markets | 11 | 0 |
| UI | 7 | 0 |

The "useful" column counts the 33 marked pages in [ALL_BUILDS.md](ALL_BUILDS.md). That is 30 items,
because `instant-compaction` is the X post announcing `fast-jev-compaction`, and two pairs are
counted as one item each.

**Why the rest were skipped:**

- Games (54), trading (11), robotics (14): no overlap with this work.
- About 60 X/ads/SEO/marketing builds and about 30 email/ticket triage builds: no overlap.
- About 70 browser, desktop and voice agents: ScriptEngine reads the MediaWiki API, not a browser.
- About 25 compaction and routing builds for **Pi, Codex, DeepSeek Harness, omp or Hermes** only.
  We use Claude Code and opencode.
- `jev-router`, `codex-jev-router` and similar: they route between paid cloud models.
- About 40 opinion posts with no code, and about 30 SDKs for other languages (Ruby, Elixir, Swift,
  Laravel, Spring, Go).

### The 30, by lane

Endpoint column:

- ✅ = the README mentions a local or custom endpoint (`baseUrl`, `TYPESAFE_BASE_URL`,
  `JEV_API_BASE_URL`, Ollama, llama.cpp, and so on).
- ⚙️ = no mention. Tools built on the official `typesafe-sdk` probably honour `TYPESAFE_BASE_URL`
  (decider's model card says so), but this is untested.

#### A. Runtimes: what provides `/v1/systemone`

| Build | Repo | Endpoint | Lane | Role |
|---|---|:-:|---|---|
| rizzo-flow | [Rizzo-AI-Academy/rizzo-flow](https://github.com/Rizzo-AI-Academy/rizzo-flow) | ✅ | Fast | llama.cpp with GGUF (Spark-X2.5 1.7B/4B), PowerShell examples, `:8017`. The most Windows-friendly option. Runs on the CPU build of llama.cpp. |
| von | [wfzyx/von](https://github.com/wfzyx/von) | ✅ | Fast | 395M, CPU, 1–2 GB RAM, `von serve`. |
| laya | [NandhaKishorM/laya](https://github.com/NandhaKishorM/laya) | ✅ | Fast | `laya-serve`, CPU 193–464 ms. |
| simple-jev / AnyJev | [featherless-ai/simple-jev](https://github.com/featherless-ai/simple-jev), [nokia-applied-research/AnyJev](https://github.com/nokia-applied-research/AnyJev) | ✅ | Fast | Any Hugging Face model becomes a decision endpoint, with no training. Only with a small model on CPU, not NInfer. |
| hearim | [ziozzang/hearim](https://github.com/ziozzang/hearim) | ✅ | Gateway | Go, multi-backend `/v1/systemone` gateway (Ollama, llama.cpp, OpenAI-compatible, SGLang, vLLM). Could route fast vs deep. **Unverified:** whether it can use plain text answers, which NInfer requires. |
| jev-compatible-sglang-vllm | [David-Lolly/Jev-Compatible](https://github.com/David-Lolly/Jev-Compatible) | ✅ | ❌ | Needs SGLang or vLLM. SGLang was removed from this machine on 2026-08-22. |
| jev-rs | [yijunyu/jev-rs](https://github.com/yijunyu/jev-rs) | ✅ | ❌ | Needs logits from llama.cpp, vLLM or SGLang. Not NInfer. |
| logjev | (X post) | – | ❌ | Built on logprobs, which NInfer lacks. |

Not on the site but found on GitHub and Hugging Face, and relevant:

- **Mapika/decider** (the decider-2b family). The strongest candidate for the fast lane if 0.8B
  runs acceptably on CPU.
- **Yinsongxu/LLM2Jev**: prefill-only scoring over SGLang, Transformers or MLX.

#### B. Context compaction: fewer tokens per agent turn

| Build | Repo | Endpoint | Agent | What it does |
|---|---|:-:|---|---|
| fast-jev-compaction (= instant-compaction) | [tamaratran/fast-jev-compaction](https://github.com/tamaratran/fast-jev-compaction) | ✅ `baseUrl` | Claude Code | Scores every tool call and result, and deletes the spent ones word-for-word instead of writing a summary. 6.5k★. |
| yoshi | [compozy/yoshi](https://github.com/compozy/yoshi) | ✅ `base_url` | Claude Code, Codex | Context-pruning proxy. |
| winnow | [GhalebDweikat/winnow](https://github.com/GhalebDweikat/winnow) | ⚙️ | Claude Code | Splits each large Read/Bash/Grep result into blocks. Blocks judged unneeded become a stub with a recall key. The judge is `typesafe` or `adapter` (Haiku), so it needs a patch. |
| jev-pruner | [tamaratran/jev-pruner](https://github.com/tamaratran/jev-pruner) | ⚙️ | Claude Code | Trims long Bash output before the model reads it. |
| jev-rules | [EliaAlberti/jev-rules](https://github.com/EliaAlberti/jev-rules) | ⚙️ | Claude Code | Loads only the rules that apply to the current task. ScriptEngine's CLAUDE.md is large. |
| compact-adviser | [kunchenguid/compact-adviser](https://github.com/kunchenguid/compact-adviser) | ⚙️ | Claude Code | Says when a session is at a safe point to compact. |
| jev-picks-the-memories / perfectrecall | [arslanr-com/perfectrecall](https://github.com/arslanr-com/perfectrecall) | ⚙️ | Claude Code, Codex | Chooses which memories get recalled into context. |

**For opencode, which is what actually runs on NInfer** (not on the site; found on GitHub):

- [hoshinodis/opencode-context-pruner](https://github.com/hoshinodis/opencode-context-pruner): a
  port of fast-jev-compaction for OpenCode v2 beta.
- [christian-taillon/opencode-jev-compactor](https://github.com/christian-taillon/opencode-jev-compactor)
- [indiejoseph/opencode-jev-pruner](https://github.com/indiejoseph/opencode-jev-pruner): Bash output
  trimming. Its default path needs an OpenCode Zen key.
- [kaiyes/fast-jev-compaction-laya](https://github.com/kaiyes/fast-jev-compaction-laya): opencode
  compaction on local Laya weights. It is MLX, so Mac only; useful as a porting reference.

These matter most for NInfer. Smaller prompts mean less prefill and fewer lane evictions.

#### C. ScriptEngine: index-time judgment, research

| Build | Repo | Endpoint | Lane | Maps to |
|---|---|:-:|---|---|
| jev-curate | [AkashPriyadarshii/jev-curate](https://github.com/AkashPriyadarshii/jev-curate) | ⚙️ | Deep | Streams JSONL rows and scores them to keep or drop. This is the **precision filter**: index-time labels for `generic_trait` / `wrong_kind` / `not_subject` / `non_canon` wrong members (precision 58.8%, see `PRECISION_PLAN.md`). |
| jev-mcp | [jkudish/jev-mcp](https://github.com/jkudish/jev-mcp) | ✅ `JEV_PROVIDER=compatible` + `JEV_API_BASE_URL` | Deep | Claim checks for the question bank: does the cited page say what the bank claims? Automates the "re-fetch and grep" rule. |
| jevgraph | [chenmingtang830/jevgraph](https://github.com/chenmingtang830/jevgraph) | ⚙️ | Deep | Knowledge graph from typed relation decisions, with the evidence kept. The same shape as `ingest/relations.py`, with a closed `RELATIONS` vocabulary as the options. |
| jev-reviewer | [choxos/jev-reviewer](https://github.com/choxos/jev-reviewer) | ✅ | Deep | Extraction where every answer is a verbatim quote. Matches the "name must appear in the passage" guard in `abilities.py` and `narrative_abilities.py`. |
| neo4jev | [jexp/neo4jev](https://github.com/jexp/neo4jev) | ⚙️ | Deep | Each node's relationships become the options of a `choice`, and the goal check rides in the same request. A reference for graph walks over the SQLite graph (`linked_from` / `owned_by`). |
| jev-search-mcp | [mukiwu/jev-search-mcp](https://github.com/mukiwu/jev-search-mcp) | ✅ | Fast | Web search where the model picks the sources. For bank research instead of `opencode run` web sweeps. |
| jev-sift | [kbhuw/jev-sift](https://github.com/kbhuw/jev-sift) | ⚙️ | Fast | Classify first, then read selectively. |

Also relevant, not on the site: [dorkitude/webctl](https://github.com/dorkitude/webctl). SearXNG
(optional) → dedupe → relevance scoring → `--scrape --filter-chunks` returns only the relevant
chunks. Needs a Jev key, and no local-URL setting was found, so it needs a patch.

#### D. Script voice

| Build | Repo | Endpoint | Lane | Maps to |
|---|---|:-:|---|---|
| snifftest | [DanRWilloughby/snifftest](https://github.com/DanRWilloughby/snifftest) | ⚙️ | Fast lint, deep audit | Regex rules plus model judgment for AI-writing tells. Almost exactly `docs/ANTI_AI_SCRIPTING.md` + `VOICE_RULES` in `scriptengine/api/rules.py`. |
| clarity-judge | [TypeSafeAI/clarity-judge](https://github.com/TypeSafeAI/clarity-judge) | ✅ | Fast lint, deep audit | Official TypeSafe tool: writing checked on separate named axes, each with its own verdict. |
| slop-grader-cli | (X post) | – | Fast | Audits text against your own rulesets. |
| hookmeter-jev | [ehui1226/hookmeter-jev](https://github.com/ehui1226/hookmeter-jev) | ⚙️ | Fast | Scores viral hooks. For YouTube script intros. |

#### E. Glue

| Build | Repo | Endpoint | Lane | Role |
|---|---|:-:|---|---|
| jev-calibrate | [smkrv/jev-calibrate](https://github.com/smkrv/jev-calibrate) | ✅ `--base-url` | Both | Tunes questions against your own labels, then confirms on held-out data. The 984-item canon bank is the label set: it sets fast-lane thresholds and measures fast vs deep agreement. |
| daf-jev | [docxology/daf-jev](https://github.com/docxology/daf-jev) | ✅ `JEV_BASE_URL` | Both | Python toolkit: question builders, confidence gates, calibration. The client ScriptEngine would call. |
| prompt2jev | [sumleo/prompt2jev](https://github.com/sumleo/prompt2jev) | ⚙️ | Deep | Converts an existing prompt into a typed decision. Start with `ingest/classify.py`. |
| jev-test-filter | [mizchi/jev-test-filter](https://github.com/mizchi/jev-test-filter) | ✅ `TYPESAFE_BASE_URL` | Fast | Scores each test against a git diff and runs only the relevant ones (626 tests). |

**Totals:** 3 blocked, 8 in the deep lane (NInfer), 19 in the fast lane (CPU model).

## 5. Where decisions fit ScriptEngine, and where they must not

- **Query path: never.** Retrieval stays model-free; that decision was made on 2026-08-14. Every
  use below runs at index time, eval time, or on the writing side.
- **`ingest/classify.py`** is already a closed question ("a form the body reaches, or a stacked
  form?"). It is the most direct swap from generation to a typed `choice`.
- **The extraction passes** (`abilities.py`, `relations.py`, `narrative_abilities.py`) still need
  generation to *name* things. A decision model can *verify* each extracted row afterwards (is this
  the subject's? is it canon? is it an ability rather than a trait?). It is an extra guard, not a
  replacement.
- **The precision filter** is the biggest measurable lever. The intruder buckets from
  `eval/diagnose_intruders.py` are the labels. Measure with `canon-run --skip-eval`.
- **The question-bank citation gate** is the only thing that has caught fabricated items (13 of
  795, about 2%). A claim check on NInfer would automate it.
- **Script voice.** The fast lane lints drafts, and the deep lane runs the final audit before
  `cli verify`.

## Implementation plan

**Phase 0: fast lane (no NInfer, no VRAM).**

- Benchmark on CPU: `von`, `decider-0.8b`, and `rizzo-flow` with a 1.7B/4B GGUF.
- Test set: about 100 already-labelled intruders from `diagnose_intruders`, plus a slice of the
  bank's canon items as positives.
- Record accuracy, calibration (ECE) and p50/p95 latency.
- Serve the winner on `127.0.0.1:8017/v1/systemone`.
- Budget: Windows has about 5 GB of RAM outside the 26 GB WSL cap, so prefer a model under 2 GB.

**Phase 1: gateway.**

- Use hearim if it can use plain text answers; otherwise write a ~100-line Python shim.
- `fast` goes to :8017. `deep` goes to NInfer :18080 with temperature 0, a one-letter answer
  format, and the letter parsed after the reasoning.
- The deep lane refuses to run while opencode holds a session, and runs with concurrency 1.
- The deep lane returns `confidence: null`. Do not pretend a text answer is calibrated.

**Phase 2: compaction.**

- Point `fast-jev-compaction` (Claude Code) and `opencode-context-pruner` (opencode) at :8017.
- Measure in NInfer's `requests.jsonl`: prompt tokens per turn, `prefix_cache_hit_tokens`, and
  `LRU evicting` counts, before and after.

**Phase 3: ScriptEngine.**

- Build the precision filter as an index-time table, the same shape as `classify.py`: stored
  answers, one-line reason, reject or annotate, never add.
- Run `canon-run`. Target: precision above 58.8% with recall unchanged.
- Only if the deep lane is too slow at corpus scale, write the NInfer logprobs patch.

**Phase 4: script voice and glue.** Add snifftest / clarity-judge rules from `VOICE_RULES`,
jev-calibrate against the bank, and jev-test-filter in the dev loop.

## Caveats

- Every build is under two weeks old, and every speed or accuracy number is the author's own.
- Endpoint support is confirmed from README text for the ✅ rows only. No build has been run yet.
- Most compaction tools are TypeScript plugins that run with the agent's permissions. Read them
  before installing.

## Method and sources

- Build list: `https://madewithjev.com/sitemap.xml` has 701 URLs, of which 485 are `/builds/`,
  110 `/resources/`, 63 `/community/` and 9 `/categories/`. Every build page was downloaded, and
  its meta description and first non-site outbound link extracted. See [ALL_BUILDS.md](ALL_BUILDS.md).
- Additional GitHub search terms: `jev compaction`, `jev context`, `jev pruner`, `jev claude code`,
  `jev opencode`, `jev token`, `context-diet`.
- Model facts: the Hugging Face `api/models/<id>` endpoint, plus each `README.md` and `config.json`.
- NInfer facts: live requests to :18080 on 2026-09-24, and a grep of `/root/ninfer-work/ninfer`
  at `d6f3fcc4`.
