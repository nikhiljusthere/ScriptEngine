Review 3.

1. Strongest: A — its OBJECTION (drop `\bconnection\b`, router.py:479) is verified: the L475-483 regex fires on 11 page-batch questions where "connection" is prose (e.g. "…Maki her last connection to?", questions/_jjk_page_maki_zenin.json); official banks contain none (verified 0) — gates can't catch it. D's no-fallback finding verified (roster: main.py:228-235, cli.py:1699, writer.py:494; none for relations); its "4 callers" disputed: mcp/server.py:12 proxies /context — 3 sites. E's missing store-free trigger test verified (test_router.py:19 imports no _RELATIONS; new tests skip without csm). C's edges_for=815 disputed (815 is link_entities, 935 is edges_for; D right).

2. Blind spot: B. Placement verified (router.py:656, before 669/735), but "latent" is scoped to official+eval banks; the fix `who (is|was) \S+ to` still matches "Who is left to stand against Mahito" (JJK page-batch) — B endorses an incomplete fix.

3. All five missed: _RELATIONS matches 194 questions in the `_` page-batch banks, mostly OPM/JJK "Who is X to Y" / "relationship between" rows moving qa→relations; a pair with no relation row → empty bundle (no fallback, D) → re-sweep miss → halt. Catch: run the regex over every bank question including `_`-batches and confirm each re-routed pair has non-empty relation rows — A's spot-check, no one ran it.
