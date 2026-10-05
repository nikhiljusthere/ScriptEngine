# UNIVERSAL EXTRACTOR DATASET — preparation plan (2026-10-04)

Goal (owner, 2026-10-04): one small student model that extracts events from
**every** anime/Fandom wiki — not MCU only — as fast and as accurately and
precisely as possible ("do whatever is necessary"). This file is the
self-contained brief for the opencode worker; Claude plans and grades.
Prerequisite done: windowing-100 finish, commit `578b53a9` (gen-2 grid, unique
ids, leak-free pools, `tools/train/dataset_gates.py`, four gates exact).

Do ONE work package (U-WP) per turn, then STOP and report the receipt asked
for. Standing rules of `plan/WINDOWING_100_FINISH.md` apply (explicit
pathspecs, GPU-only, exact-PID kills, supersede-don't-delete, comments say why,
no commits unless the WP says so). Every number in a receipt comes from a
script, never an estimate.

**Test scope (2026-10-04, after a worker ran the whole suite unasked):** a
U-WP runs ONLY its own tests (`pytest tests/test_<its files>.py`) plus
`tools/train/dataset_gates.py`. Never `pytest tests/` — at 262k the 27B holds
30 of 32 GB, so the suite's CUDA model tests cannot get the card (they OOM,
GPU-only rule forbids CPU), and tools-only changes cannot move it anyway. The
full four-gate run is Claude's, in a 100k CUDA window, only when engine code
(`scriptengine/`) changes.

## Decisions (taken by Claude under the owner's 2026-10-04 authorization)

1. **One verb inventory everywhere: the 12 verbs.** Seven wikis (berserk,
   bleach, csm, db, hxh, onepiece, opm) run the shared 9; jjk/marvel/mcu add
   `defeated`, `captured`, `escaped` via `events: extra_verbs`
   (`scriptengine/ingest/events.py:eventive_verbs`). The brain goal is
   match-ups for EVERY franchise, and those verbs carry the outcome. A student
   that sees two inventories must learn when a verb is forbidden — one
   inventory removes that failure class.
2. **Hunter x Hunter is the held-out wiki** — never in any train pool; a
   test pool only. It is the honest measure of "a fandom the student never
   saw". Every other wiki also gets a page-disjoint test pool.
3. **Precedent 6 is retired for labels** ("one `met` per pair per meeting,
   even across windows"). The student reads ONE window; a label that omits an
   event the window states teaches omission (a recall bug). Label every
   window independently; the engine already dedups a page's rows on
   (label, subject, verb, object) (`events.py`, the `dedup` drop).
4. **The guideline must be universal.** JJK-only rules (the named-shikigami
   list, JJK precedents) become general rules with JJK as examples.
5. **Era balance for the Marvel franchise** (owner): pages from the old
   comics era (pre-2010), the middle (2010–2020) and new (2021+), across the
   Marvel comics wiki (`marvel`, 236,720 docs) AND the MCU wiki (`mcu`,
   43,250 docs, films from 2008).
6. **Exact production prompt in every record** (`events.system_prompt` +
   `events._TEMPLATE`), so the student is a drop-in; speed comes from serving
   (prefix cache: the ~1,366-token system prompt is ~95% of every call's input
   — median window 221–356 chars), not from a different prompt.

## Measured facts (2026-10-04)

| wiki | docs | teacher event rows | verbs today |
|---|---|---|---|
| jjk | 987 | 8,491 | 12 |
| mcu | 43,250 | 13,194 (1,794 pages) | 12 |
| marvel | 236,720 | 9,004 (1,705 pages) | 12 |
| csm | 537 | 333 (59 pages) | 9 |
| bleach / hxh / opm / db / onepiece / berserk | 2,252 / 2,018 / 1,571 / 7,205 / 7,613 / 762 | none | 9 |

Era signals: marvel `year` (76,400 facts), `releasedate` (64,127), `first`
(131,160 — a first-appearance issue title, e.g. "Daredevil Vol 1 242");
mcu `release`/`released`/`first aired`/`date` (free-text dates, e.g.
"November 10, 2017").

## U-WP1 — one verb inventory + universal guideline

1. Add `events:\n  extra_verbs: [defeated, captured, escaped]` to
   `series/<s>/overrides.yaml` for berserk, bleach, csm, db, hxh, onepiece,
   opm (merge into an existing `events:` block if one exists; comment why:
   this plan, decision 1). NOTE: berserk/bleach/db/hxh/onepiece are symlinked
   to `/mnt/PROJECTS/ScriptEngine-offload/series/` — edit through the symlink;
   git shows those five as deleted symlink artefacts, never commit them.
2. Verify: `eventive_verbs(store)` == the 12 for all ten wikis (script line
   per wiki).
3. Append a section "Universal amendments (2026-10-04)" to
   `plan/EVENT_ANNOTATION_GUIDELINE.md` (do not rewrite existing text):
   decision 3 (per-window labels; precedent 6 superseded for labeling), the
   general entity rule replacing the JJK shikigami list ("a NAMED individual
   creature/summon/AI/construct counts as an entity; a species, class,
   technique, item or unnamed group never does"), and the 12-verb table as
   the one inventory.
4. Run `scriptengine/.venv/bin/python tools/train/dataset_gates.py --series
   jjk` (must stay all-PASS: the jjk prompt is unchanged).
Commit: the two committable overrides (`series/csm/overrides.yaml`,
`series/opm/overrides.yaml` — check `git ls-files` first; skip any that are
gitignored) + the guideline. Report the 10 verb lines.

## U-WP2 — era stamp (Marvel franchise)

New `tools/train/era_stamp.py --series marvel|mcu` → `series/<s>/training/
era.json` {page: {"year": int|null, "era": "old"|"mid"|"new"|"undated",
"source": "<fact key or rule>"}}. Rules, in order: the page's own date fact
(marvel: `year`, then `releasedate`/`release date`; mcu: `release`,
`released`, `first aired`, `date`, `release1`) parsed to a year (4-digit
regex; reject years < 1930 or > 2030); else the page's `first` fact resolved
to that issue page's year; else `undated`. Eras: old < 2010, mid 2010–2020,
new ≥ 2021. Report per store: counts per era × page_type (top 8 types), %
undated, 10 random spot rows per era (title, year, source) for Claude to
check.

## U-WP3 — event-likelihood proxy (zero-LLM) for wikis without teacher rows

Six wikis have no teacher rows, so the C6 evidence stratification is
impossible there. Proxy: a window is `eventish` when it contains a verb-lexicon
hit (inflections of the 12 verbs + battle/fight/kill/die/defeat/meet/encounter/
arrive/leave/escape/capture/seal/save/rescue/betray/awaken, word-boundary,
case-folded). Validate on JJK first: proxy recall on the gen-2 gold
non-empty windows (gold600.gen2 + pilot gen2, kept/reexpressed) and the
proxy-positive share of the gold's earned empties. Report recall/precision.
Acceptance: recall ≥ 0.95 (it only sets sampling weights, never labels).

## U-WP4 — universal pools

Extend `tools/train/emit_windows.py` (JJK + MCU behaviour byte-identical,
cmp-proven) to emit, per wiki, a train pool and a page-disjoint test pool
(test pages recorded in `series/<s>/training/holdout_pages.json` FIRST):

| wiki | train | test | strata |
|---|---|---|---|
| marvel + mcu (Marvel franchise) | 1,200 (600 marvel + 600 mcu) | 150 (75 + 75) | era thirds (old/mid/new; mcu "old" = 2008–2009 + undated-by-rule) × read/never-read (mcu/marvel read pages = ≥1 event row), rare×3 inside read |
| csm, bleach, opm, db, onepiece, berserk | 300 each | 50 each | eventish/non-eventish 50/50 (U-WP3 proxy); csm read pages stratified by evidence |
| hxh (HELD-OUT WIKI) | 0 | 150 | eventish/non-eventish 50/50, ≥ 60 pages |
| jjk | existing 3×500 pools + gold (unchanged) | existing holdout | unchanged |

Then `dataset_gates.py` per wiki (all PASS / SKIP-on-absent) + a new
cross-wiki check D8: no hxh window id or page in any train pool; no test id in
any train pool, per wiki. Receipt per wiki: counts per stratum, distinct
pages, page-type mix, era mix (Marvel franchise).

## U-WP4d — core stratum: biggest pages + their links (owner idea, 2026-10-04)

Owner: "first check the biggest pages from all wikis and then the links on
those big pages that lead to further pages — wide variety, the most important
pages covered, and you learn how they are formatted." Adopted as a STRATUM next
to the random strata, not a replacement (link-snowballing concentrates on the
main cast; production — e.g. MCU's ~290k windows — is mostly small pages, and
an all-core test would measure the neighbourhood, not production).

Per wiki, inside the production read set (U-WP4c):
1. **Seeds** = top pages by `documents.word_count` (top 1% of read pages,
   min 20, max 200), recorded in `series/<s>/training/core_pages.json`.
2. **Hop-1** = pages the seeds link to through the store's pre-resolved links
   (chunk_nodes / edges), ranked by how many seeds link to them, capped per
   page_type (no type > 40% of hop-1), only read-set pages.
3. **Split first, page-disjoint:** seeds and hop-1 pages are split train/test
   (80/20, seeded) BEFORE any sampling; test core pages join holdout_pages.json.
4. **Pool mix:** ~40% of each train pool is drawn from the core stratum (seeds +
   hop-1, windows spread across pages, cap per page), ~60% from the existing
   random strata; test pools carry a `stratum: core|random` field and the scorer
   reports core vs random separately (never one blended number only).
5. **Format census** of the seeds (report + `series/<s>/training/format_census.json`):
   section-heading frequency, list-vs-prose share, fact-passage share, window
   size distribution, sub-topic counts — feeds the per-wiki notes of the
   labeling guideline.
6. Coverage receipt: distinct page_types, distinct section headings and pages
   hit by the pools WITH vs WITHOUT the core stratum.

## U-WP5 — student eval on gen 2 + multi-wiki

`tools/eval_extraction.py` `load_gold` must read `gold_test_v4.gen2.json`
(fix described in `plan/JJK_VERIFY_GEN2_ADDENDUM.md` §5) and accept a
`--series` so each wiki's test gold scores separately; report per-wiki and
per-verb P/R/F1 + the verb confusion matrix (fought vs defeated first).
Add a test pinning the gen-2 loader. Run its tests; commit tool + test.

## Labeler choice: a bake-off, not an assumption (owner 2026-10-04)

Owner: "why 35B, why not 27B — 27B is smarter; prove the 35B before using it."
Evidence on hand: Q6-27B blind on the 100-window test gold 77.2 R / 77.1 P
(teacher 62.8 / 73.0); the 35B has only a 75-window VERIFIER-role audit
(1 disagreement in 91 rows) — not a labeling measurement. The Q6 GGUF was
deleted 2026-09-29; **Qwen3.8-27B-Q8_0** (`/mnt/PROJECTS/models/qwen3.8-27b-q8/`,
`tools/train/ops/serve_q8.sh`, llama.cpp :8090) is on disk — higher precision
than Q6, no download. Bake-off before any labeling: 27B-Q8 vs 35B (27B-NVFP4 as
reference), identical labeling prompt + guideline, on the blind JJK passage
test gold (100 passages, 173 core), scored by `tools/eval_extraction.py`
passage scoring (P/R/F1, per verb, quote-verbatim). **Default labeler =
27B-Q8**; the 35B only if it beats it on F1 AND precision. Table shown to the
owner before labeling starts.

**Superseded the same evening (owner 2026-10-04 ~22:1x):** "we managed to make
our verification window part robust to be using 35B for speed (if verification
passes of 35B's work is still not robust, make it) so we should definitely use
it only." => **the labeler is the 35B** (`tools/train/ops/serve_35b.sh`, build35,
`:18081`). The bake-off becomes a **35B acceptance test**: 35B drafts
(`qwen_worker.py`, same prompt/guideline) -> the verification pass
(`verify_row_wiki.py`) -> final rows, scored per passage on the blind JJK test
gold, raw draft and post-verification both reported, with the 27B-NVFP4 run
as a reference number only (the Q8 arm is dropped). If post-verification
precision or recall is weak (bar: >= the Q6-27B's blind 77 R / 77 P, and
precision >= 0.90 after verification), the verification layer is hardened
(e.g. two independent 35B passes with agreement, stricter row check) and
re-measured BEFORE any pool is labeled — never a model swap.

## Labeler + verification protocol (owner 2026-10-04 ~22:3x — supersedes the bake-off/acceptance text above)

**Superseded 2026-10-05:** the drafter is the **ninfer 35B** with drafter v2
(owner: "run only the 35B ninfer model as a drafter"), frozen config in
`plan/FLAWLESS_LABELING_PLAN.md` §11 (blind F1 .812), served at 64k / 8 lanes
(`tools/train/ops/serve_35b_64k.sh`). Pool verification brief:
`plan/VERIFY_POOLS_BRIEF.md`. The CyberTiel text below is history.

**Labeler model (2026-10-04, superseded):** `Cyber-Tiel-Coder-35B-A3B-MTP-UD-Q5_K_XL.gguf`
(peculiar-ragdoll/Cyber-Tiel-Coder-35B-A3B-GGUF-MTP @ `fa19d4f3`, MIT, 26.98 GB,
`/mnt/PROJECTS/models/cybertiel-35b-mtp/`), served by llama.cpp
(`~/llama.cpp/build/bin/llama-server`, build 11074 `26394b4e6`, has draft-mtp):
`-ngl 99 -fa on -ctk q8_0 -ctv q8_0 --jinja --spec-type draft-mtp
--spec-draft-n-max 1 --temp 0.6 --top-p 0.95 --top-k 20 --min-p 0`, context =
the largest that keeps every layer on the GPU (measured at load; `--n-cpu-moe`
only if it cannot fit, never above 40). Owner: "maximum speed with highest
quality". Card caveat recorded: the model trades world knowledge for coding
(MMLU-Pro "bird-brained") — the labels come from the passage + wiki pages, and
the acceptance numbers decide whether that matters. NOT the ninfer 35B.

**Verification = manual, inline, one window at a time, in opencode sessions
(owner):** no automation, no loops of LLM calls. For each window: read the
window + the 35B's draft rows; open the exact wiki page(s) for every
character / arc / event / ability involved (local crawl, read in <=500-char
chunks); decide keep / fix / reject per row and add missed events; log it.
**Log doc** per pool: `series/<s>/training/verify_log/<pool>.md` (human) +
`<pool>_verified.jsonl` (machine): window id, page/section, passage, every draft
row with verdict + one-line reason, pages+sections consulted, added rows, final
labels. **Claude audits** the doc and re-verifies a sample itself (~5% random +
every hard case: direction, killed vs defeated, passive, class-vs-name) from
the same pages, logging its verdicts beside the worker's; >3% disagreement
stops the run until the rules are fixed. Drafting (the 35B writing candidate
rows per window) runs as a batch, as the VERIFY-7000 drafts did — assumption
stated to the owner.

## Later (not this brief): the labeling run

The 35B inline-verify protocol (`plan/JJK_VERIFY_7000_FINAL.md` rules +
decisions 3–4 above) over the new pools; per-wiki golden probes once a wiki
has ≥ 50 verified windows; a blind 5% re-annotation by Claude to measure the
dataset's own error; training mix capped so no wiki exceeds 35% of windows.
Needs the 27B → 35B model takeover — owner's go.

## Student model trial (owner 2026-10-04: Qwen3.5-4B, BF16, accuracy over speed; the 3B is OUT)

Model: **Qwen/Qwen3.5-4B** (4.66B incl. vision tower, Apache-2.0), pinned revision
`851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a`, cached in `/mnt/PROJECTS/hf_home`
(9.34 GB). Chosen 2026-10-04 from a 3B-8B survey (exact HF param counts): best
in-range instruction/structure base (IFEval 89.8, IFBench 59.2, BFCL-v4 50.3,
structured-extraction KIE 86.0 vs Gemma-4-E4B 11.1). Granite-4.2-3B is dropped
from the trial (owner); its old v4 numbers (54.9 R / 57.9 P) are history, not a
gate. Qwen3-4B-Instruct-2507 is a fallback ONLY if Qwen3.5-4B hits a hard
blocker (tooling/instability), never a parallel arm. Serving: **BF16 only**
(owner: no NVFP4 for a 4B — full strength).

Known traps (Qwen3.5): hybrid Gated-DeltaNet (train-env transformers 5.17 has
`qwen3_5`); thinking by default -> train AND infer with `enable_thinking=False`
(the empty think block) through the model's own chat template; LoRA targets
must include the DeltaNet projections (derive from `named_modules()`, never a
default list); vision tower, embeddings, lm_head frozen; loss blow-ups reported
at r64 with lr >= 3e-4.

Labels/scoring: the labeler (Qwen 27B/35B) and the student share a family, so
every label is adjudicated, a blind 5% re-annotation measures the dataset's own
error, and the student is scored only on adjudicated gold.

### Splits (by page, per wiki)
train = the verified train-pool windows; **dev** = 5% of each wiki's train
PAGES (seeded) — the ONLY data any hyper-parameter is chosen on; **test** = the
per-wiki holdout pools + hxh (never used for a decision, scored once at the end).

### The search: broad, then tight (selection = dev micro event-F1)
Event match = (subject, verb, object) with the quote overlapping the gold quote;
a precision floor (dev P >= 0.90) and the per-verb gates (killed / betrayed /
captured precision >= 0.95) break ties and veto.

- **Stage A — broad** (fixed 2,000-window dev-free subset, 1 epoch, greedy dev
  eval): lr {3e-5, 6e-5, 1e-4, 2e-4} x LoRA rank {16, 64, 128} (alpha = 2r,
  rsLoRA, dropout 0.05) = 12 runs, + 1 full-fine-tune probe (lr 1e-5, 8-bit
  AdamW, grad checkpointing). Keep the top 3 by dev F1.
- **Stage B — tight** (full train set, top-3 configs): lr x {0.7, 1.0, 1.4},
  dropout {0, 0.05}, rare-verb repeat {x1, x3}, epochs up to 5 with per-epoch
  dev-F1 early stopping (patience 1). Keep the best.
- **Stage C — final**: the best config x 3 seeds -> mean +/- sd per wiki on the
  test sets (variance is part of the result, not noise to hide). Ship the
  seed closest to the mean.
- Fixed everywhere: bf16, effective batch 16-32, cosine schedule, warmup 3-5%,
  loss on the assistant turn only, packing OFF, byte-identical production
  prompt, greedy decode, max new tokens sized from the longest gold answer.
- Reported per run: dev P/R/F1, per-verb P/R, verb confusion (fought vs
  defeated first), JSON validity (no constrained decoding), quote-verbatim
  rate, windows/s.

### Disk policy (both disks are ~90-99% full)
Adapters only (no merged copies until the final), `save_total_limit=1` per run,
non-best Stage-A adapters deleted after Stage B starts; the final merged bf16
model (~9.3 GB) is written once.

### Order
Labels first (35B inline-verify over the U-WP4 pools; needs the 27B unloaded),
then the search (needs the whole card). Prep that runs now (U-WP6, no GPU):
`tools/train/sft.py` for Qwen3.5 (template thinking-off, DeltaNet-aware targets,
rsLoRA, per-epoch dev event-F1 callback, Stage A/B/C driver, disk policy) +
a CPU-only template/tokenization check on 20 gold records (prompt token count,
assistant-only label mask correct).

## Engine defects found during dataset prep (not fixed here — each needs its own gated work item)

- **MCU infobox params lost after a `<ref>` (2026-10-04).** `Iron Man (film)`
  stores 4 facts and no `release`, while its raw `{{Movie ...}}` infobox carries
  every param; the `writer` value holds a `<ref>[url ...]</ref>` and the params
  after it are missing. Other films (The Avengers, Black Panther) keep
  `release`. Affects any wiki whose infobox values carry `<ref>` with brackets.
  Workaround in `era_stamp.py` (raw-infobox tier for media pages); the real fix
  is the wikitext infobox parser + re-index + the four standing gates.
  Root cause (U-WP2d): `scriptengine/ingest/wikitext.py` `split_params` — a
  `<ref>` whose external-link URL ends in `]` produces `]]`, corrupting the
  `[[`/`]]` depth count so later top-level `|` no longer split (also
  `Ant-Man (film)`, `Avengers: Infinity War` lose `release`).
- **MCU TV infoboxes date with a `dates` range param** (43 series) that no
  tier reads; they are dated via their episodes instead (41).

### Trainer config research (2026-10-05, agent-reach; apply next session)
- OOM root: full 248k-vocab logits. Fix options: TRL `SFTTrainer` default
  `loss_type="chunked_nll"` (lm_head only on supervised positions, 256 at a
  time; keep lm_head out of LoRA) — or our `completion_loss` (logits_to_keep,
  committed fb44a123: 6 steps 500s -> 68s; residual OOM-retry warnings remain:
  drop the `.float()` upcast / chunk the CE).
- Load text-only: `AutoModelForCausalLM.from_pretrained(..., attn_implementation="sdpa")`
  (qwen3_5 -> Qwen3_5ForCausalLM, skips model.visual.* and mtp.*).
- Published LoRA: Unsloth r16/a16/lr2e-4/dropout 0; ms-swift r8/a32/lr1e-4
  all-linear; axolotl r16-32/lr2e-4 + DeltaNet in_proj_qkv/in_proj_z/out_proj
  (published recipes skip in_proj_a/in_proj_b). Stage A grid should include r16.
- group_by_length, pad to a multiple of 64/128, grad checkpointing
  use_reentrant=false, adamw_torch_fused, PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True.
- NO packing / padding_free (GatedDeltaNet leaks state across packed samples
  without cu_seq_lens; ms-swift #9618). Same think/nothink template at train
  and inference. Check logs for "falling back to its reference PyTorch
  implementation" (fla import failure = >10x slower). fla Blackwell autotune
  hang fix (fla PR #1000) — sm_120 coverage UNVERIFIED.

### LoRA vs full fine-tune (owner 2026-10-05: "I want the best results")

Not assumed — raced. Stage A (`tools/train/sweep.py`) = the 12 LoRA arms
(rsLoRA, lr {3e-5..2e-4} x rank {16,64,128}) + 2 FULL fine-tune arms (lr 1e-5,
2e-5): language layers only (vision tower, embed_tokens, lm_head frozen),
paged AdamW 8-bit (`bitsandbytes` 0.50.2 installed in ~/train-env, an
optimizer step verified on the 5090 / CUDA 13), gradient checkpointing.
Dev F1 picks the arm; Stage B/C carry the winner (LoRA or full) forward.
Before Stage A: a 20-step full-FT smoke to confirm it fits in 32 GB (GPU is
busy drafting/verifying now). Training data = the VERIFIED universal pools
(+ JJK verified), rebuilt by `build_student_set.py` — the sweep's current
TRAIN/DEV paths still point at the old JJK student set and are switched when
the verified set exists.
