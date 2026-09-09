Review 5.

1. Strongest: A. Load-bearing claim — `\bconnection\b` (router.py:479) misroutes 11 qa-pinned questions — verified: `questions/_*.json` holds 20 "connection" lines (11 unique), e.g. "What is the sword Mai left Maki her last connection to?"; official-bank sweep: 0 hits, so gates 2/4 cannot catch it. Drop-alt-4 fix: bank-safe (verified: CSM bank uses "relationship"; no test pins it).

2. Blind spot: B. B verified the what-branch steal (8 hits) but its who-(is|was)-X-to fix is false: the who-branch alone matches 65 `_`-batch rows, ~55 qa lookups ("Who is left to stand against Mahito, per Chapter 131?", `_jjk_page_chapter_131.json`). B hand-checked two positives, never swept the corpus. C's "gate-catchable" is likewise false (0 official-bank hits, verified).

3. All five missed the who-branch class. Catching check: full 5-alternative dry-run of `_RELATIONS` (router.py:475-482) over `questions/_*.json` + official banks, asserting mode-invariance on qa rows; the new tests (test_router.py:122-145) never exercise "who … to".

Claim checks — A over-match: verified (router.py:479; questions/_jjk_page_*). B placement: verified (router.py:656-666). B fix: disproven. C floor/dedup: verified (context.py:396, context.py:429). D no-relations-fallback: verified (main.py:228, cli.py:1699, writer.py:494); "4 callers" wrong on mcp/server.py (HTTP client, L94). E test absence: verified (test_router.py:19); record-claim unverifiable.