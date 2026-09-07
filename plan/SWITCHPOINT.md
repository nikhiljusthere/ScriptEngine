# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)

- mode: 262k (current) → **100k** (target — the CUDA co-location window for
  X2.d/X2.e: pytest suite on CUDA, `:8000` embedder+reranker on CUDA beside
  Qwen, the door censuses + measurement batch)
- git: `6abb05b` (clean work commit: R4 in-text-citation placement) + this
  switchpoint commit
- trunk/excursion address (drift_log §4): **X2 open** (d6-completion, JJK
  only, halt before P6) — X2.a council done (D9), X2.b door pre-check done
  + X2.c R4 done (D10); **X2.d is next**
- work explanation (what's done, what's in flight, the exact next step):
  - X2.b: roster + narrative doors verified callable on the live `:8000`
    (CPU by measured decision — 262k left ~4 GB < 5.3 GB).
  - X2.c (R4): 90 of the 154 unplaced events placed by the new in-text-
    citation signal (`timeaxis.py`); the 64 remainder triaged with
    machine-derived reasons (`comprehension-gate --triage`). Cross-page gate
    107 → 109; temporal 2,594 → 2,684. 3 new tests; targeted suite green.
  - In flight — the CUDA window, in order: (1) full `pytest tests/ -q` on
    CUDA (expect 1,243; the 6 `test_context.py` failures under 262k are
    GPU-contention OOM artifacts, not code); (2) launch `:8000` on CUDA and
    re-run the standing gates (eval jjk 31/31 · span-recall 48,572/48,572
    rc=0 · canon opm 10/16 · 236/236 · 79.0%); (3) **X2.d** — the door
    censuses (roster 100 + narrative 100 fixed questions, post-R4 corpus,
    ≥99% bar, every miss triaged), in-process `CENSUS_DEVICE=cuda` harness
    (the `tools/census_545.py` pattern) or through `:8000`; (4) **X2.e** —
    the measurement batch (8-verb 100-sentence sample; 140-question
    per-dimension retrieval test incl. outcomes + causality; 50-question
    open-ended census; placement-gate false-negative audit).
- open questions / risks:
  - The 6 `test_context.py` failures are a *contention hypothesis*, not yet
    confirmed: if any stay red on CUDA, isolate before accepting the
    baseline (re-run with the R4 change stashed; if still red, diagnose as a
    real regression).
  - 100k subagent policy: ≤2 parallel (council stays 5 — standing
    exception). When the CUDA window ends (after X2.e): switch **back to
    262k** — unless X2.f triggers a heavy Qwen LLM batch, which is the
    *opposite* rule (stop `:8000`, Qwen owns the card, context mode
    irrelevant).
  - The return switch (100k → 262k) needs **no session handoff**: the fit
    guard only refuses a *down* switch (target < transcript), and 262k is
    bigger. Keep the window's transcript slim — big batch outputs (census,
    X2.e) go to files, read summaries only — so the session never nears the
    100k cap mid-window and the return switch keeps its margin.
  - `:8000` is currently down (was stopped after the X2.b CPU pre-check).
- first action on resume:
  - **No session handoff needed** — the seeded session's real context (~56k
    per pi's own count; the fit guard's 149k is its conservative bytes/4)
    fits the 100k cap, so the CUDA window runs in that session. If it dies
    anyway: open fresh `pi`, "Read plan/SWITCHPOINT.md and continue from
    there." Overflow mid-work self-handles (ninfer 400
    context_length_exceeded → pi auto-compacts + retries; see
    `docs/ops/QWEN_MODES.md`).
  - verify the switch: `cat /home/goblin/ninfer-work/qwen_mode.txt` +
    `nvidia-smi` (expect 100k mode, ~7–8 GB free).
  - `python -m pytest tests/ -q` on CUDA (default device) → **done 2026-09-07
    22:3x: 1,242 passed in 176s** (baseline was 1,239 pre-R4 + 3 new R4
    tests; the 6 `test_context.py` failures under 262k were confirmed GPU-
    contention OOM artifacts — all green on CUDA).
  - launch `:8000` on CUDA (detached: `setsid nohup python -m
    scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 < /dev/null &`,
    no `SCRIPTENGINE_DEVICE` override), then `eval --series jjk` +
    `canon-run --series opm` + `span-recall --series jjk` (the post-R4
    standing-gate re-run).
  - X2.d census per the council's D1/D2 definitions
    (`COUNCIL_d6-completion.md`): roster = 100 fixed enumeration questions
    stratified characters/techniques/organizations/items; narrative = 100
    fixed chronological queries stratified characters/arcs, on the post-R4
    timeline (it is — R4 is done).
  - X2.e measurement batch, then **switch back to 262k** (`./qwen-switch.sh
    262k` — in place, no handoff; target > transcript, the guard passes
    without `--force`), then X2.f/g per the drift log.
- done this turn (2026-09-07, post-switch infra): `qwen-switch.sh` now syncs
  `~/.pi/agent/models.json` contextWindow per mode (header + proactive
  auto-compact threshold honest); overflow is self-handling (pi-ai matches
  ninfer's 400 context_length_exceeded → auto compact-and-retry). Updated:
  `qwen-switch.sh`, `docs/ops/QWEN_MODES.md`, the qwen-switch skill.

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
