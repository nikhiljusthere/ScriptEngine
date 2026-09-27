# Large on-disk artifacts — hash pins (2026-09-27, S5 close-out)

These artifacts live on disk under `reports/marvel/receipts/` and `tools/marvel/`
but are **not committed to git** (size). Each is pinned here by sha256 so the
archive is reproducible/verifiable without bloating the repo. Committed
receipts reference the pins, not the bytes.

## Re-emit backups (F7, 2026-09-26; pre-rewrite originals, the safety net)
| path | files | bytes | manifest sha256 (sorted per-file sha256s) |
|---|---|---|---|
| `reports/marvel/receipts/reemit_f7_marvel_backup/` | 7,930 | 278,125,627 | `eb26bc4793f0ef7fe8d9cde0ac05a6b32bf9a5230673f3f3b8749e398835591d` |
| `reports/marvel/receipts/reemit_f7_mcu_backup/` | 16,706 | 385,773,140 | `48d8d42be3840faf474a7da3b276866b5a9c276e47c0da3f0a53e4a09ae9161a` |

## Parse-diff extracts (G4-style evidence; base = pre-parser-evolution tree 1adb0d42)
| path | bytes | sha256 |
|---|---|---|
| `reports/marvel/receipts/parse_diff_marvel_base.jsonl` | 104,030,364 | `b00de3b9b963153a98b710ea3632f7c1252bc9bb034f7b56e7209b6413d2ea47` |
| `reports/marvel/receipts/parse_diff_marvel_new.jsonl` | 315,063,707 | `d4af72255e5bd116556ca8fdab44868d264f7ee5c1d24ca455a1afd968c7e75c` |
| `reports/marvel/receipts/parse_diff_marvel_new_2026-09-27.jsonl` | 104,030,364 | `2b12582c144496be49cc6201ab46a92a8952e8199e21c6e62dc565ea35f780d4` |
| `reports/marvel/receipts/parse_diff_mcu_base.jsonl` | 7,564,657 | `3e5da1d61ab3bbb0923df46537d27dce786fb983284e3122b6098eec749f22c7` |
| `reports/marvel/receipts/parse_diff_mcu_new.jsonl` | 13,981,658 | `3308ac9f8b0f921f02c8a2c14dae99482814dec3d5b94ab6893eb4a563f2158a` |
| `reports/marvel/receipts/parse_diff_mcu_new_2026-09-27.jsonl` | 7,779,528 | `319248e9d4a09a80bdb5430dada6b4958277f39eb83b547e8578894e127a0c34` (pre-top-up extract; superseded by the committed `parse_diff_mcu_final_2026-09-27.jsonl` = `6092ca9c…`) |
| `reports/marvel/receipts/parse_diff_marvel_final_2026-09-27.jsonl` | 104,066,564 | `eaecdc307c7c21bbe8c37637b6d4092398b3a33b2d08ff73556928192e052697` (G6 gate evidence: 236,720 pages / 3,796,438 facts / 0 exceptions) |

## Crawl/skip logs (Phase A evidence)
| path | bytes | sha256 |
|---|---|---|
| `reports/marvel/receipts/crawl_marvel_nl_429loop_2026-09-25.log` | 20,832,365 | `22b60052f474361d1b8b97cce9069a4edccfe47041978a5a6dfee0aa202f5e15` |
| `reports/marvel/receipts/shard_full.log` | 2,097,675 | `848bd0a54d55db94e98ac40f699f31ee030f3ccd33edc65dc62d2f750ae97957` |
| `reports/marvel/receipts/crawl_marvel_c2_fi_full_done_2026-09-25.log` | 2,097,675 | `848bd0a5…` (identical to shard_full.log — same content, two names) |
| `reports/marvel/receipts/marvel_skipped_full_2026-09-25.jsonl` | 6,858,520 | `b24eef5a596eef72b484550620f14ea630a41eb7c9f35b7e8ce6c1bf62a38ae8` |

## Superseded 09-25 archives (replaced by the committed 09-27 gate lists)
| path | bytes | sha256 |
|---|---|---|
| `reports/marvel/receipts/marvel_all_pages.jsonl` | 7,536,063 | `79b2a30ed69209a5e6132b6aed088c95a1493ba74625155c999764f3ecc13092` |

## Verification recipe
```bash
cd /home/goblin/ScriptEngine
sha256sum reports/marvel/receipts/parse_diff_marvel_base.jsonl
find reports/marvel/receipts/reemit_f7_marvel_backup -type f -print0 \
  | sort -z | xargs -0 sha256sum | sha256sum   # -> manifest hash, table above
```