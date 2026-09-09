# CSM-1b — relations bank validation (2026-09-08)

Bank: `questions/_csm_relations.json` (11 questions, `expect_mode: relations`). Runner: `tools/csm/validate_relations.py` (reuses `canon_gold.ask` — auto-routed `/context`, top_k 8). `routed` is the bundle's own routing decision; the `relations` channel only exists on qa-mode bundles, so a question routed elsewhere cannot be complete.

| question | routed | expected | found | missing |
|---|---|---:|---:|---|
| csm-rel-01 Every documented relationship of Aki Hayakawa | relations | 6 | 5 | Angel Devil |
| csm-rel-02 Every documented relationship of Asa Mitaka | relations | 5 | 3 | Barem Bridge, Yuko |
| csm-rel-03 Every documented relationship of Chocolate | relations | 2 | 1 | Denji |
| csm-rel-04 Every documented relationship of Death Devil | relations | 7 | 6 | Miri Sugo |
| csm-rel-05 Every documented relationship of Denji | relations | 12 | 4 | Aki Hayakawa, Asa Mitaka, Barem Bridge, Beam, Fumiko Mifune, Himeno, Hirofumi Yoshida, Power |
| csm-rel-06 Every documented relationship of Famine Devil | relations | 3 | 3 | — |
| csm-rel-07 Every documented relationship of Himeno | relations | 4 | 4 | — |
| csm-rel-08 Every documented relationship of Makima | relations | 3 | 3 | — |
| csm-rel-09 Every documented relationship of Meowy | relations | 1 | 1 | — |
| csm-rel-10 Every documented relationship of Power | relations | 4 | 4 | — |
| csm-rel-14 Every documented relationship of Yoru | relations | 5 | 3 | Death Devil, Famine Devil |

**5/11 questions complete** (every expected party present in the bundle's relations).
