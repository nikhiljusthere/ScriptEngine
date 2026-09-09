# P1.5 — MCP bridge (receipts)

**Owner directive 2026-09-10 (`[STEER]`):** P1.5 was reassigned from B to the
directing session. B skips it entirely and, after the Phase-1 close council
passes, goes straight to Phase 2 — the P1.5 dependency on Phase-2 start is
waived (`plan/CSM_2PHASE_PLAN.md` §P1.5, `reports/master-work/PHASE1_JOB.md`).

Executed by the directing session while A and B ran the P1.2 R-5 council.
Campaign-neutral by construction: no `facts.db` write, no chunking/fusion/
retrieval/parser change, no four-gate re-run owed (the MCP surface only).
B's in-flight R-5 files (`router.py`, `api/context.py`, `api/main.py`, the two
test files) were read but never edited, and never staged.

## P1.5.1 — MCP client installed

`pi install -l npm:pi-mcp-extension` → rc=0, "added 93 packages … Installed
npm:pi-mcp-extension". `.pi/settings.json` packages list now carries
`npm:pi-mcp-extension` alongside `pi-subagents@0.66.0` and
`@juicesharp/rpiv-todo@2.9.0`.

## P1.5.2 — `research` is an HTTP delegate

`scriptengine/mcp/server.py`: `research()` no longer calls `build_context` in
process. It POSTs to `http://{api_host}:{api_port}/context` (settings' own
values — no new config key) with `as_prompt: true`, so the prompt is rendered
server-side, and returns the service's bundle verbatim. The
`scriptengine.api.context` and `scriptengine.script.writer` imports are gone;
`httpx` (already in the venv, 0.28.1) is the only new import. `verify_script`
and `script_path` are unchanged.

The delegation also deletes duplicated logic rather than moving it: `/context`
already does the `auto` routing, the roster→narrative empty fallback and the
`as_prompt` render, so the tool no longer keeps its own copy of any of the
three.

**Measured effect of removing the in-process model leg:**

| | before | after |
|---|---|---|
| `import scriptengine.mcp.server` | pulled the retrieval stack | **0.40 s** |
| heavy modules resident (`torch`, `transformers`, `sentence_transformers`, `qdrant_client`) | loaded on first `research` | **NONE** |

A pi session that only calls `script_path` or `verify_script` now pays no
model cost at all, and the MCP server can never become the second copy of the
embedder/reranker while Qwen owns the card (the one-copy rule).

## P1.5.3 — registered in `.pi/mcp.json`

Project scope, stdio transport, `lifecycle: lazy` (spawned on demand — no
session-startup cost, no port), exactly as the plan specifies.

## P1.5.4 — end-to-end over real MCP stdio

Driven through `fastmcp.Client` + `StdioTransport` spawning the server with
the **exact command, args and env `.pi/mcp.json` declares**, against the live
CUDA `:8000` (pid 58239) with Qwen (pid 58178) up at the 100k dial:

```
[tools/list]    3: ['research', 'script_path', 'verify_script']
[script_path]   'E:\Personal\Plot Works/Video 3 - MCP Bridge Smoke/Script/MCP Bridge Smoke.md'   (0.02s)
[verify_script] passed=True tags=1 distinct=1 findings=0                                        (0.14s)
[research]      15.04s  mode=qa routed=qa prompt_chars=30600 beats=32
                prompt head: "# What is Sukuna's plan?\n\n## Established facts\n- Sukuna, name: Sukuna\n- Sukuna, Kanji: 両面宿儺 …"
```

`script_path` computed `Video 3` without creating it — the scripts directory
still holds only `Video 1 - Toji` and `Video 2 - Gojo` (checked after the run).

**Both error paths, checked explicitly (the spec's "never an in-process
fallback"):**

- service down — server spawned with `SCRIPTENGINE_API_PORT=9` (a dead port,
  so the live `:8000` was never touched): `ValueError: The ScriptEngine API is
  not answering on http://127.0.0.1:9/context. Start it with: python -m
  scriptengine.api.main` — returned immediately, no model load attempted.
- unindexed series: `POST /context returned 503: {"detail":"Series
  'not_a_series' is not indexed. Run: python -m scriptengine.cli index
  --series not_a_series"}` — the service's own 503 surfaced intact, replacing
  the check the tool used to duplicate locally.

**Campaign health after the probes:** Qwen 58178 alive (24,874 MiB, `:18080`
ok), `:8000` 58239 alive (`device=cuda`). The service's footprint rose
4,110 → 6,072 MiB across the one `research` call — the reranker warming
alongside the embedder, the documented lazy-load behaviour; it releases when
idle. GPU 30,946 / 32,607 MiB at the peak, Qwen's pre-reserved KV pool
unaffected.

## Deliberately not done, with the reason

- **The fresh-pi `/mcp` visual check** (the plan's "one fresh pi, ~20 min"
  wording). A fresh pi would have been a third concurrent consumer of Qwen's
  KV pool while B's R-5 council was mid-flight, which is the contention the
  one-agent-at-a-time council rule exists to prevent. The protocol-level e2e
  above is the stronger check of the same claim — it spawns the server through
  the same stdio contract pi uses, from `.pi/mcp.json`'s own command line — but
  it does not prove pi's *extension* loads the file. **Owner check, ~1 min, in
  any fresh pi once the council is done:** `/mcp` should list `scriptengine`
  with its three tools.
