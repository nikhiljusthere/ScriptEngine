Review 1.

**1. Strongest: A.** Verified: `\bconnection\b` (router.py:481) matches 11+ qa-pinned questions with prose answers in the `_`-batches ("What is Flashy Flash's connection to the Ninja Village in OPM?", questions/_opm_page_flashy_flash.json, expect_mode qa; "the sword Mai left Maki her last connection to?", _jjk_page_maki_zenin.json). All 8 official banks have 0 matches of the full regex, so no standing gate can see the regression.

**2. Blind spot: B.** It calls `connection` "lower-risk, acceptable" — disputed: A's list is the over-match. And B's alt-5 fix (`who (is|was) X to`) is insufficient: "Who is left to stand against Mahito, per Chapter 131?" (qa-pinned, _jjk_page_chapter_131.json) still matches it. Disputed. A also slips: it clears alt-5, but "What is enough to leave King winded" (qa, _opm_page_king.json) matches the what-branch.

**3. All five missed the who-branch steals** ("Who was chosen to be Yuji's executioner") — nobody swept the corpus with the actual regex. The catching check: E's missing store-free boundary test (tests/test_router.py:19 imports only `_NARRATIVE_VERBS, _WH, Route, route`; R-5 tests skip without a csm index) plus a `_`-batch sweep — neither exists.

Also verified: D's missing relations fallback (main.py:228 roster-only; mcp proxies, so "four callers" is off by one); E's alias inheritance (facts.py:872-878); C's rank shape (roster.py:2429-2432).