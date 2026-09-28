# R13: extraction model trial, same 160-page Marvel sample (2026-09-29, architect)

Sample: 160 seeded-random pages of the 179,276-page Marvel `all` queue (seed 20260929; `/tmp/se_p2/marvel_tput_pages.txt`), 285 passages (62 section / 6 lead / 217 fact). Workers 8 (server slots in brackets). Row sets: `/tmp/se_p2/marvel_tput_rows_{ninfer,unc,uncmtp,35b}.json`. Extraction precision = the architect's judgment of a seeded 30-row sample per run (seed 11): does the quote state that subject–verb–object? Resolution is judged separately (it is the resolver's, not the model's).

| run | server | wall (s) | s/passage | rows | ambiguous | bad verb / dedup drops | failed pages | extraction precision (30) |
|---|---|---:|---:|---:|---:|---|---:|---:|
| Qwen3.8-27B NVFP4, thinking **low** | ninfer, MTP [8] | 1,150 | 4.04 | 471 | 210 | 0 / 44 | 0 | 27/30 (90%) |
| Qwen3.8-27B **uncensored** NVFP4, thinking **off** | SGLang [8] | 358 | 1.26 | 481 | 301 | 0 / 47 | 1 | 26/30 (87%) |
| same + native **MTP** (NEXTN, accept len ~3.8–4.0) | SGLang [6] | **203** | **0.71** | 481 | 271 | 0 / 39 | 2 | 27/30 (90%) |
| Qwen3.6-35B-A3B MoE, thinking **off** | ninfer, MTP [8] | 127 | 0.45 | 801 | 507 | 27 / 125 | 0 | 24/30 (80%) |

Reading: on 30-row samples (±~10 pts) the three 27B runs are level on extraction precision; the 35B-A3B is fastest but over-generates (801 rows, 27 invalid verbs, 125 dups) with visibly worse precision (wrong subjects: "Beast killed Mystique" from "Attacked by Mystique, she … before dying"; verb abuse: "Black Bolt killed Attilan", a city). The uncensored 27B with MTP and thinking off is 5.7× the ninfer thinking-low run at equal precision. The failed pages are empty replies (`returned no content`) on Roxelana and Katherine Bishop (TRN1636): retry at a larger budget; they must reach `failed: 0` in any full run.

Ninfer cannot serve the uncensored weights: its converter needs a BF16 base of the same model plus a vLLM-layout FP8/NVFP4 export; the fleetml release is a single modelopt NVFP4 checkpoint, and substituting stock-Qwen BF16 tensors would make a hybrid, not the uncensored model. SGLang's native MTP on the same weights is the equivalent. On a 32 GB card, MTP costs memory: 6 concurrent at most (Mamba state + draft), KV pool 16k tokens.

Resolver (independent of the model; the 35B/MTP runs store raw mentions since `df0c1066`): mention "Beast" → `Henry McCoy (Clone) (Earth-616)`, "Dark Beast" → `Henry McCoy (Earth-616)`, "Hank" → `Blast-Hands (Hank)`. R12 fixes 1–3 are required before any full run, whichever model runs it.

K2-Horizon-MoVA-36B-A4B (owner-requested fifth model): pending.
