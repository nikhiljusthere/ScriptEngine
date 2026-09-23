# CSM × JEV acceleration layer (2026-09-24, opencode session)

Local JEV stack wired to the CSM 100% close plan (`plan/CSM_100_CLOSE.md`).
Everything here is **local-only**: fast lane = decider-0.8b on CPU (`:8017`
via the `:8018` gateway); deep lane = NInfer `:18080` (refuses while any
opencode process runs — by design; it protects this campaign's prefix cache).
Stack control: `~/tools/jev/bin/jev-up|jev-down|jev-status`.

## What is installed and verified

- **opencode v2 compaction pruner** — `~/.config/opencode/plugins/jev-context-pruner.ts`
  (auto-discovered globally; every opencode session gets it). Compaction-only
  mode: it prunes only the transcript OpenCode is about to summarize, so every
  normal request is untouched and NInfer's prefix cache survives. Stale tool
  results are judged by the fast lane (one plain question per old call,
  keep ≥ 0.3) and truncated to a 300-char head + marker. Verified end-to-end:
  a 166k-char stale result judged p=0.12 → truncated to 392 chars.
- **opencode v2 bash pruner** — `~/.config/opencode/plugins/jev-bash-pruner.ts`.
  Trims shell tool results > ~16k chars (v2's shell tool already tail-caps
  near 10k tokens; the pruner adds *smart* retention + a project-local
  archive at `<project>/.opencode/fast-jev-output/` with a recovery footer).
  Verified: 36,980-char pytest output → 1,596 chars, FAILURES block kept,
  full output archived; repeat model calls hit a local cache (0 ms).
- **P2-extract section pre-filter** — `tools/jev/jev-prefilter.py` (fast lane,
  one plain question per wiki section). JJK validation (7,601 sections,
  ground truth = the 2,748 kept `events` rows) is the adoption gate:
  sensitivity against event sections must be ≥ 99% — a wrongly dropped
  section is lost content. Probe (200 sections): 100% hit, 49% keep rate,
  clean p-separation (event 0.63–0.85 vs dropped ≤ 0.29).
- **Red-row triage** — `tools/jev/jev-red-triage.py` (model-free DB check;
  the model is an opt-in paraphrase net). Run 2026-09-24:
  **23/23 red rows' gold is supported by the crawled corpus**
  (`~/tools/jev/reports/csm-red-triage.md`) — all 23 are engine gaps
  (retrieval/extraction/width), zero bank/crawl defects. No bank edits owed
  by triage; the closure path stays the plan's P2-extract + width legs.

## Step → tool map (what to use where)

| CSM step | JEV tool | note |
|---|---|---|
| every step, every council | context-pruner (auto) | biggest win: shrinks what compaction re-sends; R-5 measured 3.76M prompt tokens for 110k output at 6.1% cache hit |
| any step with big shell output | bash-pruner (auto) | pytest/SQL/log output; first trim costs ~3–30 s on the fast lane, then cached |
| P2.3 D6 extraction (the 16 floor rows) | `jev-prefilter.py` | after JJK validation passes: judge CSM's 3,917 sections (~12 min fast lane), 27B extraction pass runs only on kept sections. Never replaces the plan's three exact-match checks on extracted rows |
| D7b dev loop | `pytest_filter.py` smoke runs | never replaces the pinned full gates (1,331) |
| future CSM video script drafts | `voice_lint.py` / slop-grader before humanscope Mode B | off the 100% critical path |
| red-row sorting | `jev-red-triage.py` | done (23/23 supported); re-run only if the red set changes |

## Must NOT use (plan constraints, unchanged)

- **Grading**: p23, the blind set, the OOS set, green30 stay mechanical with
  no model judge; the executing agent must not write its own grader. A model
  grader would also make old/new scores incomparable.
- **`precision_filter.py` and bank calibration**: chance-level on the 0.8B
  (57.5% accuracy; 0.47 AUC). Not wired into the pipeline.
- **Deep lane during campaign work**: it refuses while opencode runs, and
  running it would fight the councils for NInfer's cache. Quiet windows only.
- **Councils and question writing**: `llm-council` is a standing rule;
  decision models never generate question text.

## Measurement protocol (before declaring any win)

1. Council cost: NInfer `requests.jsonl` prompt tokens + full-prompt re-reads
   per council, with and without the pruners.
2. Pruner behavior: `~/.config/opencode/jev-context-pruner/decisions.jsonl`
   and `~/.config/opencode/jev-bash-pruner/decisions.jsonl` (every judgment,
   trim, and error is logged; `hook_error` lines = fail-open, transcript
   left verbatim).
3. Pre-filter: the jsonl report carries per-section p + keep + has_events;
   the summary line carries sensitivity/selectivity.

## Kill switches

- `JEV_CONTEXT_PRUNER=off` / `JEV_BASH_PRUNER=off` (env of the opencode
  service), or delete the two files from `~/.config/opencode/plugins/`.
- Fast lane down → both pruners fail open (no mutation, logged).
- Pre-filter is opt-in per run (`jev-prefilter.py`); nothing in the engine
  changed.

## Known pre-existing issue (not JEV)

opencode 2.0.15 rejected both `@dietrichgebert/ponytail` and
`cbm-augment.ts` (v1-style plugins: "Plugin must export a default definition
with an id and an effect or setup function"). They load-fail under v2 and
their hooks never fire. The JEV v2 plugins are the native-format replacements
for the compaction job; ponytail itself needs a v2 port by its owner.

## Receipts

- JJK pre-filter full run: `~/tools/jev/reports/jjk-prefilter-full.{jsonl,log}`
- Red triage: `~/tools/jev/reports/csm-red-triage.{md,jsonl}`
- v2 plugin source + patches: `~/tools/jev/opencode-plugins-v2/`,
  `~/tools/jev/patches/opencode-jev-pruner.{local-output-tweaks,local-question}.patch`