# C task brief — gpu-gate3 (100k + CUDA standing-gates re-baseline, round 2)

You are C — the GPU-step agent of the cross-session handoff
(docs/ops/PC_GPU_HANDOFF.md, tier 2). Qwen was just flipped to 100k service
mode by the chain; the embedder+reranker MAY now co-locate on the GPU.

Why this run exists: the previous re-baseline (`reports/csm/GATE_REBASELINE.md`,
pytest 1,242, git `9e13815`) predates CSM-2's +7 tests (`42aa296`) — the
suite is now **1,249**, so the standing "1,242" baseline no longer
reproduces on the current tree (council finding, `reports/csm/
COUNCIL_csm-1b-2.md`). Re-measure all four gates on the 1,249 tree, on CUDA.

Work from /home/goblin/ScriptEngine with `scriptengine/.venv/bin/python`.

**VRAM rule: ONE copy of the embedder+reranker in VRAM at a time.** In-process
model loads (pytest, `eval`) and the `:8000` server (lazy per-request models)
are two such copies. Sequence accordingly: server down during pytest + eval;
server up (CUDA) for the HTTP gates; `canon-run` with `--skip-eval` while the
server holds the models.

Run EXACTLY this:

1. **Stop the `:8000` server** (currently on CPU):
   - find the PID listening on :8000 via `ss -ltnp | grep :8000`
     (NEVER `pgrep -f 'scriptengine.api.main'` — the pattern self-matches)
   - `kill <pid>`
2. **`pytest` full suite on CUDA** (default device — do NOT set
   `SCRIPTENGINE_DEVICE`; ~5 min). The 6 cases that OOMed under the 262k
   profile (Qwen owned the card) must pass on GPU:
   - `tests/test_context.py::TestBattleFactsReachTheQaBundle::test_a_battle_field_answer_is_in_the_bundle`
   - `tests/test_context.py::TestBattleFactsReachTheQaBundle::test_a_low_ranked_named_fight_outcome_still_leads_the_facts`
   - `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-kechizu-036-…]`
   - `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-toge_inumaki-051-…]`
   - `tests/test_context.py::TestQaRecallFloor::test_a_sub_beam_answer_is_served_when_the_subject_resolves[jjk-pg-tsumiki_fushiguro-129-…]`
   - `tests/test_context.py::TestQaRecallFloor::test_an_unresolvable_subject_leaves_the_ranked_beam_alone`
   (… = the parametrized suffix; run the full file, don't hand-type the ids.)
   Expect **1249/1249**. Record the tail of the run.
3. **`... cli eval --series jjk`** (in-process, CUDA; `:8000` still down —
   one copy). Record X/31 + any failing gold question verbatim.
4. **Start `:8000` on CUDA:**
   `setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main > /tmp/scriptengine_api_cuda.log 2>&1 < /dev/null &`
   (default device; lazily loads embedder+reranker ~5.3 GB). Poll
   `http://127.0.0.1:8000/health` in a bounded status loop (≤ ~3 min, a line
   every 15 s) until 200. If it cannot start on CUDA (OOM in `nvidia-smi` /
   the log): fall back to `SCRIPTENGINE_DEVICE=cpu` for the rest of the task
   and note it in the report.
5. **`... cli span-recall --series jjk`** (offline, <1 s — record rc +
   reachable/total) **then `... cli span-recall --series jjk --probe 400`**
   (live `:8000`; ~4 min on CUDA). Order matters: offline first, then probe.
   **Probe append-dup trap (known, fix lands in CSM-3(b)):** the probe path
   writes in APPEND mode into `reports/span-recall/jjk/recall_verbatim.jsonl`
   with dedupe/`done` unwired. After the probe: save the appended block as
   the raw receipt (`git diff reports/span-recall/jjk/recall_verbatim.jsonl`
   → append it, verbatim, to your report), then restore the file with
   `git checkout -- reports/span-recall/jjk/recall_verbatim.jsonl` so the
   tree stays clean. Do NOT leave the append in the tree.
6. **`... cli canon-run --series opm --skip-eval`** (HTTP; `--skip-eval` is
   the one-copy rule — the server holds the embedder, an in-process eval would
   be a second copy; the canon numbers are unaffected). Record the summary
   table (exact answers, canon recall, precision).
7. **Write `/home/goblin/ScriptEngine/reports/csm/GATE_REBASELINE_2.md`:**
   - header: `C: gpu-gate3 — 100k+CUDA standing-gates re-baseline, round 2 on
     the 1,249 tree (2026-09-08)`
   - per gate: the raw tail of the run + key numbers + start/end timestamps
   - a **new-numbers table**: pytest (n passed — expect 1249), eval jjk
     (X/31), span-recall jjk (offline + probe), canon opm (exact / canon /
     precision)
   - the 6 OOM cases named, each marked PASS-on-CUDA
   - the probe's appended jsonl block (verbatim, step 5)
   - notes: `:8000 left on CUDA — the campaign session restores it to CPU on
     resume (262k co-location rule)` (or the fallback you used)
   - if a gate fails: record the failure verbatim. Do NOT fix it — you are the
     measurer, the campaign session is the decider.

End your turn after the report is written.