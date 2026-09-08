# CSM-1b — relations bank validation (2026-09-08)

Bank: `questions/_csm_relations.json` (11 questions, `expect_mode: relations`). Runner: `tools/csm/validate_relations.py` (reuses `canon_gold.ask` — auto-routed `/context`, top_k 8). `routed` is the bundle's own routing decision; the `relations` channel only exists on qa-mode bundles, so a question routed elsewhere cannot be complete.

| question | routed | expected | found | missing |
|---|---|---:|---:|---|
| csm-rel-01 Every documented relationship of Aki Hayakawa | roster | 6 | 0 | Angel Devil, Denji, Himeno, Makima, Power, Taiyo Hayakawa |
| csm-rel-02 Every documented relationship of Asa Mitaka | roster | 5 | 0 | Barem Bridge, Denji, Hirofumi Yoshida, Yoru, Yuko |
| csm-rel-03 Every documented relationship of Chocolate | roster | 2 | 0 | Denji, Power |
| csm-rel-04 Every documented relationship of Death Devil | roster | 7 | 0 | Denji, Fami, Makima, Miri Sugo, Nayuta, Pochita, Yoru |
| csm-rel-05 Every documented relationship of Denji | roster | 12 | 0 | Aki Hayakawa, Asa Mitaka, Barem Bridge, Beam, Fumiko Mifune, Himeno, Hirofumi Yoshida, Makima, Nayuta, Pochita, Power, Reze |
| csm-rel-06 Every documented relationship of Famine Devil | roster | 3 | 0 | Death Devil, Pochita, Yoru |
| csm-rel-07 Every documented relationship of Himeno | roster | 4 | 0 | Aki Hayakawa, Denji, Hirokazu Arai, Makima |
| csm-rel-08 Every documented relationship of Makima | roster | 3 | 0 | Aki Hayakawa, Denji, Pochita |
| csm-rel-09 Every documented relationship of Meowy | roster | 1 | 0 | Power |
| csm-rel-10 Every documented relationship of Power | roster | 4 | 0 | Aki Hayakawa, Denji, Makima, Meowy |
| csm-rel-14 Every documented relationship of Yoru | roster | 5 | 0 | Asa Mitaka, Death Devil, Denji, Famine Devil, Pochita |

**0/11 questions complete** (every expected party present in the bundle's relations).
