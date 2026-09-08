# C task brief — gpu-live1 (100k + CUDA gate baseline)

You are C — the GPU-step agent of the cross-session handoff
(docs/ops/PC_GPU_HANDOFF.md, tier 2). Qwen was just flipped to 100k service
mode by the chain; the embedder+reranker MAY now co-locate on the GPU.

Work from /home/goblin/ScriptEngine with `scriptengine/.venv/bin/python`.
Run EXACTLY this:

1. Move `:8000` from CPU to CUDA (the documented 100k co-location case):
   - find the PID listening on :8000 via `ss -ltnp | grep :8000`
     (NEVER `pgrep -f 'scriptengine.api.main'` — the pattern self-matches)
   - `kill <pid>`, then
     `setsid nohup scriptengine/.venv/bin/python -m scriptengine.api.main > /tmp/scriptengine_api_cuda.log 2>&1 < /dev/null &`
     (default device = CUDA; lazily loads embedder+reranker ~5.3 GB)
   - poll http://127.0.0.1:8000/health in a bounded status loop (≤ ~3 min,
     a line every 15 s) until 200.
   - If it cannot start on CUDA (OOM in `nvidia-smi` / log): fall back to
     `SCRIPTENGINE_DEVICE=cpu` for the whole task and note it in the report.
2. `... cli span-recall --series jjk`            (offline, <1 s)
3. `... cli span-recall --series jjk --probe 400` (live :8000; ~4 min on CUDA)
4. `... cli eval --series jjk`                    (CLI loads the embedder
   itself on CUDA; :8000 must be idle at this point so its models are
   unloaded — ONE copy of embedder+reranker in VRAM at a time; if VRAM is
   tight, stop :8000, run eval, restart :8000 on CUDA)
   Order matters: probe (step 3) BEFORE eval (step 4).
5. Write /home/goblin/ScriptEngine/reports/master-work/GPU_LIVE1_REPORT.md:
   - header: `C: gpu-live1 — 100k+CUDA gate baseline (2026-09-08)`
   - per gate: result + key numbers (span-recall % / unreachable lines;
     probe hit rate; eval X/31 + any failing gold questions)
   - notes: `canon opm deferred to A`, and `:8000 left on CUDA — A restores
     it to CPU on resume (262k co-location rule)` (or the fallback you used)
   - if a gate fails: record the failure verbatim. Do NOT fix it — you are
     the measurer, A is the decider.

End your turn after the report is written.