# RED LIST — expected-failing questions (JJK)

Regenerated 2026-09-05 (Final-campaign Step 1). Every row is a question
expected to **fail** on a live run, with the gap it evidences. This file
must never be empty: an empty red list while gaps are open means the
evidence was dropped.

**Basis.** Last recorded page-runs (2026-09-03, GPU server) for the active
bank rows; the 2026-09-04 G28/G29/G30 fixes (none touches the G25/G26/G27
paths or the G31 scope); the 2026-09-04 content-pages probe notes (G31).
**Re-verify every row on the next live run** (CPU or GPU, `:8000` is
currently down and the GPU is held by Qwen). A row that now passes is
closed against its gap and struck from this list — never silently dropped.

## 1. Active bank questions (failing under `auto`)

| question id | question (verbatim) | gap | last recorded state |
|---|---|---|---|
| `jjk-pg-yuji_itadori_synopsis-111` | Who has started the culling game for those involved with jujutsu, as Megumi reveals? | **G25** | failing (2026-09-03 page-run; routed narrative, answer absent from the episode stream) |
| `jjk-pg-shoko_ieiri_synopsis-009` | Why did Shoko start smoking again during the Shibuya Incident? | **G25** | failing (2026-09-03 page-run; same who-agent story-verb shape, instance 2) |
| `jjk-pg-panda_synopsis-012` | What happened to Panda during his fight with Kashimo? | **G26** | failing (2026-09-03; served only under forced qa — pure misroute) |
| `jjk-pg-panda_synopsis-015` | What happened to Panda in 2035? | **G26** | failing (2026-09-03; same, instance 2) |
| `jjk-pg-maki_zenin_synopsis-015` | What happened to Maki after the Culling Game? | **G27** | failing at tb≤12000 (2026-09-03; present at tb=30000 — assembly/budget, not storage) |
| `jjk-pg-megumi_fushiguro_synopsis-011` | Did Megumi die by 2087? | **G27** | failing at tb≤12000 (2026-09-03; stricter than instance 1 — the 4,301-w Culling Game section pushes the tail past 12000) |

Note: Toji Fushiguro #001 (G25 instance 3) was rephrased at authoring and
**passes** — it is not a red row. The G25 regression set is the two
active failures above.

## 2. G31 natural plural phrasings (probe cases — not in the bank)

The bank carries the passing avoidances (singular / "consist of" forms);
the natural plurals are the expected failures. Live re-probe deferred
(server down, GPU held by Qwen) — basis is the recorded 2026-09-04 CUDA
probe notes.

| phrasing (natural) | page | gap | basis |
|---|---|---|---|
| What are the Big Three Families? | `sorcerer_clan` | **G31** | probe note (Q001): "plural 'What are...' misroutes to roster; 'consist of' phrasing used" |
| What are Non-Curse Users? | `curse_user` | **G31** | probe note (Q002): "p1 plural 'What are Non-Curse Users?' hits the roster; singular phrasing used" |
| What are cursed tools? | `cursed_tool` | **G31** | class-consistent avoidance (authored Q001 "What is a cursed tool?"); unprobed |
| What are cursed corpses? | `cursed_corpse` | **G31** | class-consistent avoidance (authored Q001); unprobed |
| What are cursed objects? | `cursed_object` | **G31** | class-consistent avoidance (authored Q001); unprobed |

Boundary case (NOT red): "What are the Big Three Sorcerer Families?" (the
exact declared-roster name) passes on the roster door — canon run
2026-09-01-0645, `declared`, 3/3.

## 3. Retired rows (expected to fail until the item-6 corpus-wide re-index)

| question id | question (verbatim) | reason_class | state |
|---|---|---|---|
| `jjk-pg-episode_41-015` | On what does Sukuna stand while looking over the destroyed remains of Shibuya, per Episode 41? | parser-gap (colon-truncation; stored corpus truncates `[[Maximum: Meteor]]` to "Meteor") | RETIRED (State 66); un-retire + gold-update after the `index --series jjk` re-parse/re-embed |
| `jjk-pg-episode_37-066` | What is the clip caption in Episode 37? | parser-gap (gallery-body-strip) | RETIRED; un-retire after the parser gallery-body retention fix + re-index |

## 4. Canon bank

| query (jjk canon) | state | gap |
|---|---|---|
| Every cursed technique of Yuta Okkotsu | conf-wrong: `declared` confidence, found 1/9, recall 0.111 (last observed 2026-09-01-0645) | declared roster under-return; reconcile against the canon 9 (triage item 5) |

## Totals

- 6 active bank rows (G25 ×2, G26 ×2, G27 ×2)
- 5 G31 natural plural phrasings (2 probed, 3 class-consistent)
- 2 retired parser-gap rows (ep41-015, ep37-066)
- 1 canon conf-wrong row

**14 expected failures.** Re-running all 14 green is the exit condition
for the filed gaps (G25/G26/G27/G31 + item 5); the 2 retired rows
additionally require the item-6 re-index before un-retiring.