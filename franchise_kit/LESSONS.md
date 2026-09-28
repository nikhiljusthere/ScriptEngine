# Traps already paid for (Marvel/MCU 2026-09-25..28, plus JJK/CSM/OPM)

Each row: the symptom as it first appeared, how to detect it in minutes, and the fix. Most are caught by `tools/survey_wiki.py` before any GPU time is spent.

## Structure and typing

| trap | detect | fix |
|---|---|---|
| Infobox named something other than "Infobox" (`Character`, `Marvel Database:Character Template`) → pages typed `unknown`, zero facts | survey S1 `unknown` share; `audit` | `type_aliases` (template-name colon folding landed in A1c) |
| Main articles typed `list` (MCU `Infobox List`: Daredevil 72,901 words, Iron Man, Thanos) | survey S1 "large pages typed list/hub" | `type_aliases`; re-index |
| Slash-titled pages read as subpages (Marvel comic crossovers `Avengers/Defenders War Vol 1 1` → junk types) | survey S1 "junk page-type ids" | generic separator rule (declarable); re-index |
| Tabber wrapper hides the real infobox (OPM `parent_tab` → Saitama, Garou "unknown") | playbook §1 | `semantic_types` / category fallback |
| A type folded to `event`/`media` can never be a roster member | playbook §1 (`NEVER_MEMBERS`) | `semantic_types` |

## Where the text lives (understanding)

| trap | detect | fix |
|---|---|---|
| Story in **infobox fact values**, not sections (Marvel `history` 127k rows, `synopsis1..N`, `solicit`, `powers`…) → a sections-only extractor reads ~5% | survey S2 | `events.narrative_fact_keys`: every long prose key |
| Heading allow-list (`History`/`Synopsis`/"… arc") misses story-named sub-sections (MCU `Biography` → "Battle of Sokovia"): 90% of MCU prose unread | survey S3 | heading-agnostic prose scope + an explicit, counted furniture list |
| Word floors hide real sentences (a 20-word floor hid 21,010 MCU + 3,497 Marvel sentences) | compare against `span_recall.sentences(min_words=6)` | prose test = "contains ≥1 panel-eligible sentence" (the D3 denominator) |
| "≥2 characters" filter silently drops single-entity sections (MCU 2,333) | dry-run per-class counts | route them; they yield standing-state rows or a counted reason |
| Rejections logged at INFO → "0 events" ambiguous (Civil War II, Spider-Verse …) | per-reason counters in the report | count every drop by reason; account every zero-row page |

## Entities, placement, time

| trap | detect | fix |
|---|---|---|
| Bare names resolve to **disambiguation hubs** or wrong-reality variants (Marvel: 48% of event rows; Conan → Earth-16356) | survey S7; SQL on stored rows | reality-aware resolver (disambiguation `main_articleN` + page partition; ambiguous = counted class) |
| Placement types named differently (MCU `conflict`, `war`; Marvel `story_arc`) → placement set too small | survey S4 | `events.placement_types` |
| Manga-shaped time axis (arc chain / `arc` / `chapters`) orders nothing (Marvel 20/1,149, MCU 0/6,053 on the axis) | survey S5; `sum(temporal)` | `events.axis` (date / chain / order / partition), re-derive on stored rows |
| Two orders for the same thing (Marvel on-sale `releasedate` vs cover `month/year`) | survey S5 samples | the council picks; never guess |
| `previous`/`next` chains cross types (MCU conflict → event) | chain walk measurement | treat the wiki's placement types as one axis |

## Extraction runs

| trap | detect | fix |
|---|---|---|
| A reasoning model burns the 8,192-token answer budget ("never answered" / truncated JSON) | run report `failed` | retry failed pages at `SCRIPTENGINE_ANSWER_TOKENS=20480`; name any still failing |
| A duplicate extraction on the same pages (a worker ad-hoc run plus its own chain) | `pgrep -af events-extract` | one `events-extract` per series; the watcher reports every new process |
| The extraction LLM env silently defaults to LM-Studio `:1234` | `get_settings()` printout | always export `SCRIPTENGINE_LLM_*` → `:18080` |
| A worker's long uncommitted turn ends mid-reasoning | worker session idle with a dirty tree | commit checkpoints per sub-task |
| Extraction before declaration → re-resolve / re-derive later | — | declare everything in Phase S first |

## Retrieval speed and the D3 sweep

| trap | detect | fix |
|---|---|---|
| "GPU-bound" sweep is ~100% SQLite (Marvel 8.9 s/probe) | per-statement SQL timing of one `/context` | NOCASE indexes, `CROSS JOIN` plan pin, a hop-1 fast path, store memos; prove byte-identity |
| 12 uvicorn workers OOM (reranker ~4 GB each) | `nvidia-smi` | 6 CUDA workers for qa; a model-free stack for narrative/roster |
| Two supervisors race on the tier-0 temp file | rc=1 FileNotFoundError | per-process temp names (fixed `1677c994`) |
| Sweeping a build that extraction will change | — | D3 only on the final build; re-probe diff after any change |
| Probes/s vs s/probe confusion in reports | — | always s/probe plus the speed-up factor |

## Operations

| trap | detect | fix |
|---|---|---|
| `pkill -f <pattern>` kills your own shell (the pattern is in its argv) | exit 144 | kill by PID from `ss -ltnp` / `/proc` |
| `setsid … & echo $!` records the wrapper, not the server | `kill` says no such process | read the listener PID from `ss -ltnp` |
| `FORCE_COLOR=3` in the shell breaks a pytest that asserts on plain text | `test_page_gen` ANSI failure | `env -u FORCE_COLOR` for gates |
| `canon-run` refuses a `:8000` older than the source | "restart it" message | restart `:8000` after edits, before gates |
| A date-dependent test (`blind_panel`: `date.today()`) | fails the day after sealing | pin dates in tests |
| Typing into opencode with `xdotool type --window` is silently ignored | the message is not in `session_message` | activate the window, then type without `--window`, only when idle; verify in the DB |
