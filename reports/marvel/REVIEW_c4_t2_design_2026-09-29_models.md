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

## Final table (all five runs, same 160 pages / 285 passages, workers 8)

Token figures: ninfer runs from the server request log (exact); SGLang from its decode log (40-step interval × running requests × MTP accept length, approximate); llama.cpp from per-request eval timings. "Peak" = steady full-batch aggregate decode rate; "avg" = total output tokens / wall (the single-slot Beast tail drags every run's average down). Precision = architect judgment of 30 seeded rows (±~10 pts). "Common pages" = rows on the 155 pages no run failed.

| model (serving, thinking) | slots | wall s | s/passage | peak out tok/s | avg out tok/s | out tok / call | rows | rows on common pages | both ends resolved (common) | ambiguous | bad-verb / dup drops | failed pages | precision |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---:|---:|
| Qwen3.8-27B NVFP4 (ninfer + MTP, low) | 8 | 1,150 | 4.04 | ~1,265 | 417 | 1,400 | 471 | 208 | 164 | 210 | 0 / 44 | 0 | 27/30 (90%) |
| Qwen3.8-27B uncensored NVFP4 (SGLang, off) | 8 | 358 | 1.26 | ~624 | ~136 | ~142 | 481 | 192 | 141 | 301 | 0 / 47 | 1 | 26/30 (87%) |
| same + native MTP (SGLang NEXTN, off; accept 3.87) | 6 | **203** | **0.71** | ~922 | ~215 | ~135 | 481 | 207 | 157 | 271 | 0 / 39 | 2 | **27/30 (90%)** |
| Qwen3.6-35B-A3B MoE (ninfer + MTP, off) | 8 | 127 | 0.45 | ~1,229 | 567 | 210 | 801 | 297 | 218 | 507 | 27 / 125 | 0 | 24/30 (80%) |
| K2-Horizon-MoVA-36B-A4B Q4_K_M (llama.cpp IFM fork, low; can't be off) | 8 × 8K | 313 | 1.10 | n/a | 313 | 373 | 127 | 127 | 93 | 36 | 15 / 6 | 3 (truncated at 6,144) | 24/30 (80%) |

K2 notes: the 22 GB Q4 weights leave room for 8 × 8K slots only, so its answers were capped at 6,144 tokens and three pages (Henry McCoy, Madrox (Cortex), Rinehart) truncated; its yield on the common pages is still the lowest (127 vs 192–297). Its errors: `arrived` with a person as object, self-objects, an object as killer ("warehouse killed Julia Starr"), intentions read as events.
