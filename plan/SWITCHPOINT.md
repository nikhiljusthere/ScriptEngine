# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)
- **2026-09-17 ~09:40 (Claude session C — owner-directed switch 100k → 262k full context):**
  - **Switch:** `qwen-switch.sh 262k --force` (the fit guard reads the dead
    2026-09-12 pi transcript, ≈264k > 262,144; no pi process alive). At 262k
    `:8000` runs on CPU (≈3.5 GiB headroom). Configs synced to 262144: pi
    `~/.pi/agent/models.json` + repo `opencode.json` (by the script) + global
    `~/.config/opencode/opencode.jsonc` (by hand — the script does not sync it;
    it was stale at 174080). A running opencode session keeps its start-time
    limit until reopened.
  - **CSM position unchanged since the entry below:** P2.1 measured
    (`reports/csm/p21_sweep_2026-09-17/REPORT.md`), tree clean at `fb20145`.
    FIRST ACTION ON RESUME: the REPORT.md "Owed / for A" list.
- **2026-09-17 ~09:35 (Claude GPU session C — post-sweep switch off → 100k, plan A19):**
  - **Switch:** Qwen `off` → `100k` (`qwen-switch.sh 100k --force`). The fit
    guard refused on the newest pi transcript (2026-09-12 session, ≈264k
    tokens) — no pi/opencode process is alive, so that transcript is dead;
    **the next pi/opencode session must start FRESH** (resume from this entry +
    `reports/master-work/work_log.md` newest lines). `:8000` is restarted by
    the switch on CUDA if the 100k headroom allows (≥ 6 GiB), else CPU.
  - **CSM position: Phase 2 P2.1 MEASURED.** R-8 gate window green @`4b60043`
    (pytest 1,331 / eval jjk 31/31 / span-recall jjk 48,572 + 398/400 / canon
    opm 236/236; `GATE_LEDGER.json` last_green = R-8). P2.1 sweep runner exit
    0: **qa 98.48 %** (≥ 97.5 % bar, 261-row miss file), narrative 10.74 %,
    roster 0.77 %, **auto 15.43 % — fails the bar** (heldout 14.00 %); R-8
    moved 0/100 auto routes — the second misroute sends 89 % of line lookups
    to narrative. Report: `reports/csm/p21_sweep_2026-09-17/REPORT.md`.
    Widened census bank (Q1/Q2): `reports/csm/census_widened_csm.json`.
  - **Clean commit sha:** `93043d6` (sweep + census) → this checkpoint commit.
  - **FIRST ACTION ON RESUME:** read the REPORT.md "Owed / for A" list —
    (1) the second-misroute decision, (2) qa miss-file triage, (3) narrative /
    roster residual triage, (4) P2.2 bar audit never graded (A7 open),
    (5) A14 / P2.3 grader for the widened bank, (6) GATE.md + CLAUDE.md pin
    stamps (1,321 → 1,331).
- **2026-09-16 ~22:5x (opencode session — CSM coding-only; GPU work handed to Claude, no Qwen switch in this session):**
  - **No mode switch happened** — this is a coding-only opencode session on
    tree `852916e`. Mode/dial state is whatever the last recorded switch left
    (120k ctx=122880 per the 09-14 entry). Qwen (27B, `:18080`) resident on
    the card; `:8000` down.
  - **CSM position: Phase 1 CLOSED (extraction-gated floor, marker
    `407c016`); Phase 2 (P2.1 sweep) pre-baked, GPU leg unstarted.** All
    detail on disk: `plan/COMPACTION_PROOF.md` (newest dated note 2026-09-16
    ~22:50 — READ THIS FIRST on resume) + `reports/master-work/work_log.md`
    (newest line, R-8 gate-debt window) + `reports/csm/GATE.md` (R-8 landed
    section at the bottom).
  - **What landed this session (all committed):** (1) the P2.1 sweep runner
    `tools/csm/p21_sweep.sh` — pre-checks (frozen A26 hashes / row counts /
    `:8000` /health / Qwen-down → exit 10/11/12), stamp-based A18 pre-wipe
    (HEAD-stamped rows resume; pre-R-8 `f2a611d` sanity ledgers wipe), qa →
    narrative → roster → auto + 200-row auto-heldout, 30 s watchdog, halt
    codes exit 4/5/20+rc/30, receipts under `reports/master-work/`; (2) the
    env-mc test fix (`test_research_bare_character_name_is_qa`, count-neutral);
    (3) GATE.md / work_log / COMPACTION_PROOF stamps.
  - **Owed GPU work (Claude session, Qwen DOWN, whole 32 GB for `:8000`):**
    (1) R-8 gate window: 4 standing gates + `eval --series jjk` 31/31 at the
    post-R-8 pin **1,331** (the 407c016 window is pre-R-8; `GATE_LEDGER.json`
    `last_green` still R-7 `60e568f`); (2) launch the sweep:
    `setsid nohup bash tools/csm/p21_sweep.sh > /dev/null 2>&1 < /dev/null &`
    (wall ≈ 2.7 h + ~4 min heldout; poll `p21_sweep_<stamp>_run.log` +
    `nvidia-smi`); (3) on GREEN receipt: P2.3 widened census authoring (Q1–Q4
    rulings, `tools/census_dimensions.py`) + D6 extraction (Qwen owns the
    card) → completion declaration + pilot memo (A24 receipt).
  - **Clean commit sha:** below (this checkpoint).
  - **FIRST ACTION ON RESUME:** (1) `cat plan/COMPACTION_PROOF.md` (newest
    note) + `reports/master-work/work_log.md` tail; (2) `git log --oneline
    407c016..HEAD` (expect `aada154` + this checkpoint only); (3)
    `nvidia-smi` (Qwen only on the card, `:8000` down); (4) run the R-8 gate
    window, then the sweep.
- **2026-09-14 ~03:3x (owner-directed: 174k → 120k, PI session — Creator Research campaign; CSM parked):**
  - **Mode: 174k (ctx 174080) → 120k (ctx 122880, raw-token dial-down).** Pre-switch
    card state: `qwen_mode.txt` = `mode=174080 ctx=174080 qwen_pid=42381
    ts=2026-09-14T03:11:11+05:30 api=off free_mib=4293`; `:8000` off, no
    extraction in flight. Expected headroom ≈ 6.2–6.3 GB (measured 6,303 MiB
    at 122880 on 2026-09-12). `:8000` stays off (no `--api`).
  - **This is a PI session** — the agent runs the switch as ONE blocking bash
    call (`cd /home/goblin/ninfer-work && ./qwen-switch.sh 122880`,
    timeout 300 s; the autonomous protocol, QWEN_MODES.md §3). The model is
    back on the turn after the reload; this session's transcript (≈10–15k
    tokens) fits 122880, fit guard passes without `--force`.
  - **Owner directive: update BOTH json configs** — `qwen-switch.sh` does both
    automatically: `~/.pi/agent/models.json` (ninfer-27b `contextWindow` →
    122880) + `/home/goblin/ScriptEngine/opencode.json` (ninfer-27b
    `limit.context` → 122880). The ninfer-35b provider (229376) is untouched.
    VERIFY both files after the switch.
  - **Campaign state unchanged: Creator Research (opencode, outside the repo)
    — full resume state in `/home/goblin/Creator Research/HANDOFF.md`** (§6:
    finish the candidate analysis w/ india-free keywords + 12-worker capped
    parallel scan). CSM parked (Phase 1 at the extraction-gated floor, D23
    `407c016`; JJK baseline 100%).
  - **Clean commit sha:** below (this checkpoint).
  - **FIRST ACTION ON RESUME / POST-FLIGHT:** (1) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect mode=122880 ctx=122880,
    api=off, free ≈ 6.2 GB); (2) `nvidia-smi` (Qwen only on the card); (3)
    verify BOTH json files now read 122880 (models.json ninfer-27b +
    opencode.json ninfer-27b); (4) continue whatever work the owner points at
    (Creator Research HANDOFF §6 if none).
- **2026-09-13 ~15:3x (owner-directed: 262k → 170k, NEW opencode session — Creator Research campaign continues; CSM parked):**
  - **Mode: 262k (ctx 262144) → 170k (ctx 174080, raw-token dial-down).** Pre-switch
    card state: `qwen_mode.txt` = `mode=262k ctx=262144 qwen_pid=65114 api=off
    free_mib=1613`; `:8000` off, no extraction in flight. The 170k profile is
    auto-generated (`serve_ctx_174080.sh` from the serve.sh template, kv=174080,
    expected headroom ≈ 5 GiB). Switch: `qwen-switch.sh 174080 --force`
    (fit guard trips on the stale 09-13 pi transcript ≈293k tokens > 174080;
    force is safe — this commit is the full checkpoint).
  - **This is an OPENCODE session, not pi** — the in-flight turn dies
    mid-reload (expected). The owner continues in a **NEW opencode session**
    (owner directive 15:3x: "continue this experiment in a new session").
  - **Campaign: Creator Research (outside the repo) — full resume state in
    `/home/goblin/Creator Research/HANDOFF.md` (§6, updated this session).**
    CSM parked (Phase 1 at the extraction-gated floor; JJK baseline 100%).
  - **Done in this opencode session (all on disk, none in the transcript):**
    (1) 262-creator mapping analyzed (online `Analysis_262` tab);
    (2) 15-day reel+brand research: all 218 IG creators (905 in-window reels,
    371 brand rows) + 44 YT-only creators (47 uploads) — online campaign
    sheet `1JScUInkANwXKZTEXhbnzh2taafraTXRiz-0Wud3_59Y`;
    (3) expansion discovery wave 1: 8 accepted creators; new sheet
    **"Expansion Creators Reels 15D & Brands (2026-09-13)"**
    (`1dk6VUjeYW49kp3Y_SUAEhN4usM6l65KVTJlWXoK2Lgw`, Creator folder) with 21
    in-window reels / 2 brand rows / per-creator summary;
    (4) parallel-worker experiment: `reel_parallel.py` (per-reel CDP workers,
    1 persistent tab each; 16-worker wall ~29 s; 32-worker runs degrade IG
    hydration → data-quality recipe = 12 workers × up to 3 passes with a 24 s
    hydration poll; **hard cap MAX_TABS=12 + end-of-job tab cleanup** per
    owner rules "reduce the limit / PC is lagging").
  - **EXACT NEXT STEPS (new session, in order):** (1) read
    `/home/goblin/Creator Research/HANDOFF.md` §6; (2) launch Brave (CDP
    `--remote-debugging-port=9222 --remote-allow-origins=*`, wipe session-
    restore files first to avoid window duplication); (3) **finish the
    candidate analysis of the mapping sheet**: discovery with `india` removed
    from the search keywords (owner rule 15:0x — "don't search india, it will
    most probably show you indian shorts already"), 4-worker discovery
    (expand_driver.py, per-worker state files), then `reel_parallel.py` scan
    of all accepted expansion creators (12-tab cap), merge + sheet
    consolidation; (4) report the final per-category coverage
    (targets: Tech 16, C&E 30, H&B 31, Business 38, Other 41, Entertainment 48
    still short of 50).
  - **Open risks:** IG checkpoint wall (abort → owner re-login in Brave);
    OpenCLI bridge drops when the daemon restarts (restart Brave to
    reconnect); Brave session-restore respawns stale windows (wipe
    `Sessions/` while stopped).
  - **Clean commit sha:** below (this checkpoint).
- **2026-09-13 ~04:5x (owner-directed: 100k → 262k full-context switch, OPENCODE session — Creator Research work; CSM parked):**
  - **Mode: 100k (ctx 102400) → 262k (ctx 262144), "full context".** Pre-switch
    card state: Qwen 100k pid 108527 (up ~7 min, **serving this opencode
    session**), `:8000` on CUDA pid 53671 (up ~91 min), GPU 25,783/32,607 MiB
    used @100 % util. `qwen_mode.txt` was STALE (`mode=off` @04:46:42); the
    03:23 100k switch's bash script (pid 53669) sat stuck in `do_wait` 91 min
    @0 % CPU — killed before this switch (its :8000 child is in its own
    session and survived).
  - **This is an OPENCODE session, not pi** — the in-flight opencode turn dies
    mid-reload (expected; same as the 03:4x entry). The opencode process
    survives; the owner resumes with `opencode -c` (or `-s <id>`). Fit guard:
    262k is the max ctx and the opencode session is not a pi session; if the
    newest pi transcript still trips the guard, `--force` is safe (this commit
    is a full checkpoint; the opencode session auto-compacts on
    context_length_exceeded).
  - **Campaign: PARKED, nothing pending.** CSM Phase 1 §9a closure loop DONE
    (halted at the extraction-gated floor, D23 `407c016`); JJK baseline 100 %.
  - **Active work (opencode session, outside the repo):** the online
    Google-sheet reorg — state + re-run recipe in
    `/home/goblin/Creator Research/HANDOFF.md` §5 (Instagram values written;
    `mergeCells` 400 fix pending: drop the `"fields"` key; the other 5 tabs
    untouched; scans in `/tmp/scan_<tab>.json`).
  - **Clean commit sha:** below (this checkpoint). Switch: `qwen-switch.sh 262k
    --api` (262k exploratory: ~3.4 GiB headroom → `:8000` lands on CPU;
    `--force` only if the fit guard trips).
  - **FIRST ACTION ON RESUME (opencode -c):** (1) `cat
    ~/ninfer-work/qwen_mode.txt` (expect mode=262k ctx=262144, api=cpu, free
    ≈ 3.4 GB); (2) `nvidia-smi` (Qwen only on the card); (3) `curl -s
    localhost:8000/health` (expect device=cpu); (4) tail this file's switch log
    for the machine line; (5) HANDOFF.md §5 → finish the sheet reorg.
- **2026-09-13 ~03:4x (owner-directed: 262k → 100k, OPENCODE session — Creator Research work; CSM parked):**
  - **Mode: 262k (ctx 262144) → 100k (ctx 102400).** Pre-switch card state: qwen
    pid 23351, 30,673 MiB used / 1,430 MiB free; `:8000` up on CPU (pid 23419);
    no extraction in flight (the script refuses anyway while an
    events-extract batch holds the card).
  - **This is an OPENCODE session, not pi** — opencode runs on this same Qwen
    server, so the in-flight turn dies mid-reload (expected; the script header
    says never switch inside an agent session). The opencode process survives;
    the owner resumes with `opencode -c` (or `-s <id>`). If the fit guard
    refuses on a stale pi session file (the 09-13 02:33 pi transcript, ~150k
    est. tokens), `--force` is safe: this commit is a full checkpoint and the
    opencode session auto-compacts to 100k on overflow.
  - **Campaign: PARKED, nothing pending.** CSM Phase 1 §9a closure loop DONE
    (halted at the extraction-gated floor, D23 `407c016`); Phase 2 unstarted;
    JJK baseline at 100%. HEAD `aada154` + this checkpoint commit.
  - **Active work (opencode session, outside the repo) — read
    `/home/goblin/Creator Research/HANDOFF.md` first:** §2 a–c fixed (Tech-sheet
    second/third tables, dedupe pop bug + min-7 1-to-1 prefix rule) and
    `Creator_Mapping.xlsx` formatted (262 creators, 8 categories, colored
    headers, content-based widths, zebra, tab colors); §3 WriterAgent 0.8.75
    installed (`~/.config/libreoffice/4/user/`), Qwen endpoint pre-configured in
    `writeragent.json` (`mcp.mcp_enabled=true`, :18765); opencode MCP entry
    `writeragent` in `~/.config/opencode/opencode.jsonc`.
  - **OPEN ISSUE at switch time:** the WriterAgent MCP server never bound
    :18765 under the LO 26.8 deb build (`~/Applications/LibreOffice`, python
    bootstrap warning "Could not find platform independent libraries" → the
    extension's Python never bootstrapped, no writeragent_debug.log). Next step
    queued: try the system LO 24.2 (`/usr/bin/soffice`) with the xlsx open and
    poll :18765; if it still doesn't bind, check LO's python loader next.
  - **Clean commit sha:** below (this checkpoint). Switch: `qwen-switch.sh 100k
    --api` (100k service profile: ~7-8 GiB headroom → `:8000` co-locates on
    CUDA; `--force` only if the fit guard trips on the stale pi transcript).
  - **FIRST ACTION ON RESUME (opencode -c):** (1) `cat
    ~/ninfer-work/qwen_mode.txt` (expect mode=100k ctx=102400, api=cuda, free
    ≈ 7 GB); (2) `nvidia-smi` (Qwen only on the card); (3) `curl -s
    localhost:8000/health` (expect device=cuda); (4) tail this file's switch log
    for the machine line; (5) continue the open MCP issue above.
- **2026-09-13 ~02:5x (owner-directed: 100k → 262k full-context switch, then Creator Research work):**
  - **Mode: 100k (ctx 102400) → 262k (ctx 262144).** Pre-switch card state: qwen
    pid 7760, 6,996 MiB free, `:8000` off, no extraction in flight
    (`pgrep events[-_]extract` empty).
  - **Fit guard: PASSES without FORCE.** Session file 600,029 B ≈ 150,007 est.
    tokens (bytes/4, conservative) < 262144 target.
  - **Processes (verified live):** pi **5378** (serves this session 01a09753)
    ← bash **5364** ← gnome-terminal-server **3432** ⇒ helper args
    old_pi=5378, old_shell=5364. Single pi on the machine.
  - **In-tree before switch:** R-8 fix-class landed + committed at `aada154`
    (wants_chronology_set in chronology.py, router split: set-in-order → roster,
    one-subject order → narrative; 152 router tests green).
  - **Owner directive for after the switch (Creator Research, non-campaign work
    — todos #1–#5 in the session's todo panel):** (1) make a "Creator Research"
    working folder OUTSIDE the ScriptEngine repo; (2) map creators by
    niche/category from three sources — Google sheet 1 (id
    `1-zkuoTRLIEfkDJk1SWfW2WfOwlt15nZTD6aSLDMgupc`, public, already fetched to
    `/tmp/sheet1.xlsx`), Google sheet 2 (id `19G2vQFv6tV0oUQ4F6CSRcIZUXBm4bCM5xcW0WgRBOHs`,
    behind Google sign-in → fetch through the OpenCLI browser bridge on the
    user's Brave session, profile `m4e85p8v`; opencli `download` step forwards
    browser cookies to the `/export?format=xlsx` URL), and the local
    `/home/goblin/Downloads/Finnet Media Exclusive Roster .xlsx`;
    (3) build one new Excel sheet of the category mapping (LibreOffice already
    installed at /usr/bin/libreoffice; openpyxl in venv /tmp/xlsxenv). The
    opencli instagram `user` adapter is locally overridden (works via rendered-
    grid fallback; `~/.opencli/clis/instagram/user.js`, undo = rm the dir).
  - **Clean commit sha:** `aada154` (this checkpoint).
  - **FIRST ACTION ON RESUME (new pi, same session):** post-flight — (1) status
    line shows the new window (`/262k`); (2) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect ctx=262144, api=off, free
    ≈1.5 GiB); (3) `tail /tmp/switch_restart3.log` (part3 answered, new pi pid,
    old pi gone, relaunch_term done); (4) `pgrep -P 3432` — only the new pi's
    window remains. THEN, per owner directive, proceed straight into Creator
    Research todos #1–#5 (do not stop and wait).
- **2026-09-12 02:4x (owner-directed: 262k → 120k mode switch — switchpoint BEFORE the 3-part flow):**
  - **Mode: 262k → 120k (ctx 122880).** Pre-switch card state: ninfer pid 7190 on the
    262k profile (30,344 MiB used / 1,533 MiB free), `:8000` off. `qwen-switch.sh
    122880 --api` generates `serve_ctx_122880.sh` from the `serve.sh` template
    (kv=ctx, no --vision). Expected headroom ≈ 6.3 GB → `:8000` should land on
    CUDA (the --api headroom rule decides; 100k-era precedent = CUDA).
  - **Fit guard: PASSES without FORCE.** This session file 77,336 B ≈ 19.3k est.
    tokens (conservative bytes/4) << 122880 target. No extraction in flight
    (`pgrep events[-_]extract` empty).
  - **Processes (verified live, 02:4x):** single pi = **7263** (serves this
    session 01a09247, started under 262k). Window chain: gnome-terminal-server
    3394 → bash **3406** → pi 7263 ⇒ helper args old_pi=7263, old_shell=3406.
  - **Campaign position UNCHANGED by this switch** (work parked since the
    2026-09-10 power loss): CSM Phase 1 after P1.2 — R-5 closed + committed
    (`ec60587`/`35c16c9`/`3ee6bd0`), census v2 authored + committed
    (`60e568f`), **R-7 in-tree but UNGATED** (owes gates + stamps + its own
    commit), miss queue 38 open / 20 closed of 58. R-6/P1.3/P1.4/Phase 2
    unstarted. Restart ritual unchanged: READ
    `reports/master-work/POWER_CHECKPOINT.md` FIRST, then
    `reports/master-work/HANDOFF_STATE.md`.
  - **Clean commit sha:** below (this checkpoint). Switch helper (agent's last
    act, detached): `setsid nohup bash tools/master-work/switch_restart3.sh
    122880 <session_file> 7263 3406 … &`; log `/tmp/switch_restart3.log`;
    `qwen-switch.sh` appends the machine line to the switch log below.
  - **FIRST ACTION ON RESUME (new pi, same session, post-flight per the
    qwen-switch skill):** (1) status line shows the new window (≈ `/120k` —
    this pi is freshly spawned, so its window is trustworthy); (2) `cat
    /home/goblin/ninfer-work/qwen_mode.txt` (expect ctx=122880, free ≈ 6.3 GB,
    api=cuda); (3) `tail /tmp/switch_restart3.log` — part3 LLM answered, new
    pi pid, old pi gone, relaunch_term done; (4) report ONE line + **STOP**.
    Then resume the CSM parked ritual (POWER_CHECKPOINT + HANDOFF_STATE) when
    the owner speaks. Note: any OTHER pi alive before this switch holds a
    stale window snapshot — `exit` + `pi -c` it (none known 2026-09-12).
- **2026-09-10 POWER LOSS — work stopped mid-run. READ
  `reports/master-work/POWER_CHECKPOINT.md` FIRST, then
  `reports/master-work/HANDOFF_STATE.md`.** Phase 1, after P1.2.
  R-5 closed + committed (`ec60587`/`35c16c9`/`3ee6bd0`); miss queue 38 open /
  20 closed. Census v2 authored + committed (`60e568f`) = close-council Q1's
  artifact. **R-7 is in the tree but UNGATED** (same commit, gates not run,
  no queue stamps) — it owes gates + stamps before it counts. R-6, P1.3, P1.4,
  Phase 2 unstarted. Restart ritual: single terminal (A/B bay retired), fresh
  `pi`, read ONLY those two files (lean boot = 23.8% context vs 61.3% verbose),
  rebuild the 8-item todo panel. Qwen + `:8000` will both need restarting —
  verify, never trust the recorded pids.
- **2026-09-09 (CSM Phase 1 under the A/B bay — 262k→100k switch now; drift D20):**
  - **00:5x addendum (directing session pi 53523):** the bay was opened 00:38–00:39
    (tmux `control` = A, `work` = B + `csm-control.sh` monitor) and terminated on
    owner direction — the visible pilot windows would not scroll (tmux `mouse off`
    → the wheel fell through to pi; wheel-up showed the previous prompt in the
    entry field). Fixed at the root: `~/.tmux.conf` `set -g mouse on` (live
    server set as well) + rule lines in the terminal-pilot / ab-bay skills;
    wheel = tmux copy-mode scrollback, `Esc` = live pane. Owner then directed:
    demo 262k→100k switch pair (both inline; session fit 85k est < 102k), then
    re-launch A/B per ab-bay step 5 with the fixed windows.
  - **Owner mandate 2026-09-10 (supersedes the 2026-09-08 "never ask the
    owner to restart" convention):** EVERY context switch = exit the pi
    agent, then relaunch into the same session — the agent never chats
    across a model recycle (the 00:5x inline 100k switch died mid-reload;
    the owner restored 262k by hand, then restarted it). The qwen-switch
    skill made this MANDATORY (commit 8f3b0c5: "the agent always exits, the
    owner relaunches"); `switch_restart.sh` is the only sanctioned path.
    The 262k→100k demo therefore runs: `switch_restart.sh 100k
    /tmp/resume_msg.txt 53523` (my pid; the owner's pi 53686 untouched),
    resume line = stop-and-wait.
  - **Owner directive (this session, 2026-09-09 night):** (1) switch to the
    100k context by reloading ninfer (qwen-switch skill); (2) close this pi
    agent + session as ninfer restarts (pi_restart.sh, grace ≤10 s — the
    owner convention: the agent never asks the owner to restart); (3) come
    back to this session; (4) from here launch the A/B bay — A continuously
    watches every shell B launches, B works. **Phase A is GPU-only for
    shells (owner 2026-09-09 night):** every model-bearing shell runs on
    CUDA; if B's shell is caught on CPU, A stops it immediately and sends
    the standard instruction ("Control A killed your shell (pid …). Re-run
    on GPU: …") — B auto-reruns on CUDA (the 2026-09-07 convention, now
    documented in the ab-bay skill §"The CPU-kill → auto-rerun
    convention"). B works **Phase 1 only** (plan v2.2 P1.1–P1.4).
  - **Phase-boundary gate (owner: "prepare a checking/reviewer that will
    check the phase 1's end, then only will move to phase 2"):**
    `reports/master-work/PHASE1_CLOSE_REVIEW.md` — a fresh-context
    reviewer re-runs the four standing gates on the committed tree +
    verifies every P1.4 close condition + the marker-at-floor; **Phase 2
    starts only on its PASS + the owner's go.** B never starts Phase 2 on
    its own.
  - **State at handoff:** Qwen 262k (pid 3584, ~30.5 GB / ~1.6 GB free),
    `:8000` down, no tmux bay (the 150k-era bay is gone with the reboot).
    CSM = plan `plan/CSM_2PHASE_PLAN.md` **v2.2** (P1 council 14 amendments
    + P2 council 13, ledger #25/#26) is the working plan; the 9-file
    R-2/R-3 package is on disk, uncommitted (its gate legs = P1.1 step 3);
    `/tmp/csm_iter1_records` was lost in the reboot → P1.1 step 1
    (model-free rebuild). Miss queue 58 rows (33 fixable / 22 floors / 3
    stamped); census 39/60 (21 red, extraction-gated floor).
  - **This session's sequence (2026-09-09 night → 09-10 00:3x):** (a)
    ab-bay skill updated with the CPU-kill → auto-rerun convention; (b)
    `reports/master-work/PHASE1_JOB.md` (B's spec) +
    `reports/master-work/PHASE1_CLOSE_REVIEW.md` (the close gate) on disk
    (commit `958ce93`); (c) **the 100k switch was run INLINE from this
    ~400k session (00:1x) and STRANDED it** — the reloaded 100k model
    could not serve it (242k prepared prompt > 102k cap; the auto-compact
    itself did not fit), the turn died, and the restart helper never
    launched. **The owner restored 262k by hand at 00:30**
    (`ninfer-start-262k --force`; qwen pid 53071, free 1607 MiB, `:8000` on
    CPU — current state). Root cause + the fix: the safe order is kill pi
    FIRST, then switch, then relaunch pi — one detached helper
    (`tools/master-work/switch_restart.sh`, new, repo-committed); both
    skills updated (ab-bay step 2; qwen-switch "the switch" + "overflow"
    sections + Never list).
  - **NEXT (this session's final act, scripted):** launch the helper
    detached — `setsid nohup bash tools/master-work/switch_restart.sh 100k
    /tmp/resume_msg.txt $(pgrep -x pi | head -1) < /dev/null > /dev/null
    2>&1 &`. It: kills this pi (grace 5 s) → `qwen-switch.sh 100k --api
    --force` (30–60 s; `:8000` lands on CUDA at 100k per the headroom
    rule) → launches `pi` in tmux `pi-csm` → types the resume line from
    `/tmp/resume_msg.txt` → verifies via capture-pane (log
    `/tmp/switch_restart.log`). The new pi (attach: `DISPLAY=:0 setsid
    gnome-terminal -- tmux attach -t pi-csm`) reads THIS section and opens
    the bay per the ab-bay skill: A boot line (tmux `control`,
    `csm-control.sh` monitor on B's pid, the GPU-only-shell rule, the
    standard kill message), B boot line (tmux `work`,
    `reports/master-work/PHASE1_JOB.md`); the directing session (the new
    pi) stands down and relays.
  - **Next (the new session, in order):** boot A + B per ab-bay step 5 (A
    boot line carries the live-verified state snapshot + the monitor
    launch; B boot line carries the job spec + the contract). B's first
    units: P1.1 step 0 (zero-GPU baseline re-verify) + step 1 (model-free
    rebuild) → A brings `:8000` to CUDA → the four gate legs → C1/C2/C3
    (path-limited adds, `git add .` banned) → P1.2 R-5 wave (council per
    the kept trigger) → P1.3 halt meter (33 fixable only) → P1.4 close +
    marker (floor only) → **the phase-close reviewer gate** → owner go →
    Phase 2 (P2.1 step 0 sanity-100 first — the 51-GPU-h number is
    unmeasured and must not be spent before it).
- **2026-09-09 (Gojo script v2 — ESSENCE-driven; machine powers off at end of that session):**
- **2026-09-09 (Gojo script v2 — ESSENCE-driven; machine powers off at end of this session):**
  - **Gojo script rewritten per owner essence** (`E:\Personal\Plot Works\Video 2 - Gojo\Script\Gojo.md`,
    3,780 w tagged / 3,126 w clean, 56 tags / 30 distinct, verify-clean): dark open
    (the morning the world learns Gojo is sealed — E34 "Pandemonium" facts, no
    fabricated "19 days" number: the corpus's only 19-day fact is the Culling
    Game inactivity rule, Ch 158, used as the slow "days" beat); slow pacing;
    the bad things in between (Toji, Geto's break/kill, Jogo, Shibuya);
    resolution close per owner: "even the strongest, you were overpowered —
    the King beat the title, not the man" (thematic, not literal, per owner's
    "don't take this literally"). Clean companion regenerated.
  - **Standing rule (owner 2026-09-09): for ALL future scripts, ask the owner
    for the ESSENCE before drafting** (opening, pacing, resolution, the
    tragedies in between); offer options when asked; anime scripts pace slowly.
    Implemented in the engine: `scriptengine/api/rules.py` `ESSENCE_RULES`
    (folded into `writing_rules()` → travels with `script-gen` + `/context`),
    + CLAUDE.md working agreement.
  - **Toji script state (owner-directed):** `Toji.md` = the 6,520-word
    Gojo-quote-open version (the one that opened on "since he has no cursed
    energy, I can't read his presence" [E27 14:17]); the "I'm glad." rewrite
    (6,530 w) and all backups deleted on owner instruction — the Script dir
    holds only `Toji.md` + `Toji-clean.md` (5,658 w).
  - Next on the owner's list: nothing pending — **the owner powers the
    machine off at the end of this session** (Qwen 262k + :8000 CPU API die
    with it; the CSM campaign todos below stay parked until the next session).
- **2026-09-08 (Toji script rewrite COMPLETE, owner-directed — drift D14):**
- **2026-09-08 (Toji script rewrite COMPLETE, owner-directed — drift D14):**
  - The owner-directed autonomous rewrite of the Toji Fushiguro script
    (`E:\Personal\Plot Works\Video 1 - Toji\Script\Toji.md`) is done and
    **verify-clean: 104 tags / 29 distinct, every tag checks out against the
    raw wiki** (`cli verify --series jjk`), 6,037 words (was 4,044 / 91 tags;
    ~46 min at 132 wpm — the owner's ~45-min target).
    Method: `humanscope` Mode A structure sheet before drafting, Mode B
    30-feature audit before/after, citation discipline (one tag per
    (chapter, episode) run, tag every sentence on source change), `cli verify`
    before calling it done. Cut the explaining closing (theme-restate
    “in one breath …” paragraph deleted; ending now lands on the
    unexplained afterlife image); removed “not X, it is Y” reframes /
    rule-of-three / -ing-tail / weasel wording; kept plain emotion words.
    Added verbatim citation clusters from the D13 transcript store, then
    expanded to the ~45-min target with sourced material (not padding): a
    full Arsenal section (Split Soul Katana, Inverted Spear of Heaven,
    Chain of a Thousand Miles, the inventory curse, Playful Cloud, the
    broadsword/knives/handgun), a How-he-hunts/tactics section (bounty
    design, the boat-race/Shiu beat, the infiltration, the read-and-counter
    method), deeper mechanics (Physically Gifted, footprint/odor tracking,
    long-fight endurance), the Naobito Dagon beat, and more Geto/Gojo
    dialogue. The 5 key citation clusters: Gojo
    “since he has no cursed energy, I can't read his presence” (cold-open,
    Ch 71/E27); Dagon-fight narrator VO “he had become a murder machine, his
    fangs constantly directed toward the strongest” (Ch 110/E39); Gojo
    “any last words?” (Ch 75/E28); Gojo-to-Megumi “the ultimate card that
    his dad kept on hand against the Zen'in clan” (Ch 79/E29); plus the
    already-woven Toji verbatim lines. Original backed up as
    `Toji.md.orig-20260908-2343` (alongside the file, untracked).
  - **Timestamps added (same session):** all 21 verbatim quotes now carry a
    `[E<n> mm:ss]` timestamp (exact `ts` pulled from `transcripts.db`), so
    the editor can find each line's footage. The JJK0 movie (M1) was already
    imported + embedded with timestamps (D12/D13), but **Toji does not
    appear in it (0 mentions)**, so there are no movie quotes in this script
    (the movie's timestamps are ready for a Yuta/Okkotsu video). No new
    fixing run was needed, so no council (owner fallback). `cli verify`
    still clean (104 tags / 29 distinct); 6,082 words.
- **2026-09-08 (transcript Phase 2 + bay closed + dial-back, owner-directed):**
  - JJK transcript Phase 2 COMPLETE (drift D13, commit `f86ed7a`): all
    **16,226 lines embedded** (separate `series/jjk/qdrant-transcripts/` dir,
    CUDA, BAAI/bge-large-en-v1.5 1024-d, `embed_meta.json` staleness
    marker); CLI doors `transcripts-embed` + `transcript-search` (episode
    filter, stale warnings); `(Movie <name>)` verify branch + 3 tests; plan
    + drift D13. Read doors: `transcript` (time-window) / `dialogue`
    (per-character FTS) / `transcript-search` (semantic).
  - A/B bay CLOSED (~23:3x): machine monitor (csm-control.sh, generalized @
    `c81be85`) + tmux `control` (A) + tmux `work` (B) all killed; visible
    windows gone. Skills: `ab-bay` (new) + `terminal-pilot` (user-level,
    outside repo); `qwen-switch` use-case-3 committed with this checkpoint.
  - Owner directive (this switch): Qwen **100k → 262k** (full context);
    `:8000` → **CPU** (262k steady state, ~3.5 GiB headroom).
- **Next task (owner-authorized):** CSM (Chainsaw Man) campaign — the next
  owner-authorized work after the JJK campaign closed (D11). Live state: see
  the “Campaign todos” section below + `reports/csm/`. (The Toji rewrite
  above was the owner-directed intermission; it is now complete, D14.)
- **Resume / post-switch steps (a fresh session executes these in order):**
  1. `cat /home/goblin/ninfer-work/qwen_mode.txt` (expect mode=262k) +
     `nvidia-smi` (Qwen only on the card, ~25 GB used) +
     `curl -s -m 3 localhost:8000/health` (expect device=cpu).
  2. The owner's pi (this session) is restarted by the owner: fresh `pi` in
     /home/goblin/ScriptEngine, then *Read plan/SWITCHPOINT.md and
     continue from there*.
  3. Read `plan/drift_log.md` §4 (current position) + this file. The Toji
     rewrite is done (D14, verify-clean). Next owner-authorized work is the
     CSM campaign — pick up from the “Campaign todos” section below (Wave-2
     pre-step + the two parallel Wave-2 subs, or whichever the owner points
     at).
- git: the Toji script is untracked (`E:\...` dir is intentionally outside
  git); the plan checkpoint for this session (SWITCHPOINT + drift_log D14)
  is committed. (Previous head before this session: `998c673`.)
- Campaign state: JJK campaign CLOSED (D11, 2026-09-07). CSM campaign =
  next owner-authorized work (CSM-1/1b/2 + councils done; CSM-3 is the next
  unit — see the "Campaign todos" section below + `reports/csm/`).
  Transcript work is campaign-neutral (D12/D13).
- Toji script (D14 addendum 5, same session): the owner corrected the
  cast-list range to cite **Toji's appearance** in each arc (not the arc's
  full span). The inline `[range:]` notes + end-glossary are gone; the
  passage pass is now a **`[covers X-Y]` block after every 3 passages**
  (9 blocks: after passages 3, 6, 9, …, 24, and the lone 25th), each citing
  the distinct events/battles + ch/ep ranges those 3 passages draw on. Toji
  in Gojo's Past = Ch 66-75/Ep 25-28; Toji in Shibuya = Ch 95-113/Ep 35-40.
  `Toji-clean.md` (5,589 words, pure narrative; strips the `[covers X-Y]`
  + `·` lines). Ranges sourced from the wiki's `anime episode` edges in
  `series/jjk/facts.db`, never invented. `cli verify --series jjk` still clean
  (104 tags; the `[covers X-Y]` blocks are a new human-curated format, not
  verify-checked).
- Toji conventions made **permanent in the pipeline** (D15, same session):
  `rules.py` `ANNOTATION_RULES` now states all four conventions (timestamps,
  `[covers X-Y]` after every 3 passages, words-only companion, cite-the-thing
  not-the-arc); `writer.py` always writes `<title>-clean.md` and a
  `ensure_covers_blocks` backstop rebuilds the `[covers]` lines from the tags
  if the model omits them; `docs/SCRIPT_STYLE.md` §6 + a `CLAUDE.md`
  working-agreement quote the rules. 6 new script-gen tests (47 green).

## gpu-gate3 handoff (2026-09-08 — A=01a08064 (fresh CSM session; retargeted from the retired 01a07ff0) → chain → C on 100k → A resume)

**DONE 15:30 local — chain complete (state=done, no STALLED, typed RESUME
15:30:08; C transcript trashed after the report was read; `:8000` back on CPU
via the 262k switch-back, pid 80967, /health device=cpu).** All 4 gates PASS
on CUDA on the 1,249 tree (receipts `reports/csm/GATE_REBASELINE_2.md`):
pytest **1,249/1,249** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe · canon
opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + gates-skill baselines
re-baselined 1,242 → 1,249; the 1,242 `GATE_REBASELINE.md` record is
superseded; the CSM gate section is now open in
`reports/comprehension/GATE.md` as the live record.

**Gate re-baseline, round 2 (council blocker, COUNCIL_csm-1b-2).** The
GATE_REBASELINE record (1,242, git `9e13815`) predates CSM-2's +7 tests
(`42aa296` → suite 1,249): the "JJK baseline" is no longer reproducible and
CSM-3's gate re-verification would start broken. Same tier-2 chain as
gpu-live2: `gpu-handoff.sh --tier2 plan/gpu_gate3.spec` flips 262k→100k,
opens C (visible terminal, fresh 100k pi) which runs the four standing gates
**on CUDA on the 1,249 tree** per `plan/gpu_gate3_task.md` (pytest full —
the 6 VRAM-sensitive `test_context` cases must pass; eval jjk; span-recall
jjk offline + --probe 400 on a CUDA `:8000`; canon opm --skip-eval) →
`reports/csm/GATE_REBASELINE_2.md`, flips back 262k, typed RESUME into A's
window (51286464).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE_2.md` (C's 1,249-tree re-baseline).
2. Restore `:8000` to CPU (C leaves it on CUDA; 262k co-location rule).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_gate3.
{log,stalled,typed}` + `/tmp/gpu_gate3_chain.log`; a `STALLED` flag =
   inspect, then replay the same setsid line (gates are idempotent).
4. Trash C's transcript (`…/gpu_handoff_state/c_session`) — only AFTER
   reading the report.
5. Rewrite the CLAUDE.md + gates-skill baselines (1,242 → 1,249 + run
   timestamps; the record's 1,242 line is superseded), open the CSM gate
   section in `reports/comprehension/GATE.md` as the live record (council
   peer-C finding: the campaign's designated live gate record did not exist),
   commit — then start **CSM-3** (item 3 scope + the addendum in
   `reports/csm/COUNCIL_csm-campaign.md`).

## gpu-live2 handoff (2026-09-08 — A=01a07ff0 → chain → C on 100k → A resume)

**DONE 13:57 local — chain complete (state=done, no STALLED; C transcript
trashed after the report was read; `:8000` back on CPU, pid 62983).** All 4
gates PASS on CUDA (receipts `reports/csm/GATE_REBASELINE.md`):
pytest **1,242/1,242** (the 6 OOM cases pass on GPU) · eval jjk **31/31** ·
span-recall jjk **48,572/48,572** offline + **390/400 (97.5%)** probe ·
canon opm **10/16 exact, 236/236, 79.0%**. CLAUDE.md + the gates skill
baseline updated with these numbers + run timestamps (the 1,239-vs-1,242
stale pair is resolved: the suite is 1,242).

Second live run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live2.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live2`, fresh 100k pi) which runs the
**standing-gates re-baseline** per `plan/gpu_live2_task.md` (pytest full on
CUDA incl. the 6 OOM cases, eval jjk, span-recall jjk offline + --probe 400
on a CUDA :8000, canon opm --skip-eval) → `reports/csm/GATE_REBASELINE.md`,
flips back 262k, and the gated typer types the resume line into A's window
(51768426). A sits idle at its prompt meanwhile (frozen context, zero cost).
Context: CSM-1b (owner directive 2026-09-08) is DONE + committed — bank
validation + 4 in-place gold fixes + relations runner + 4 numbered engine
gaps (G-CSM-1..4); the gate re-baseline moved to this side session (owner
correction: 262k holds the card → 100k+CUDA, never CPU fallback).

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/csm/GATE_REBASELINE.md` (C's re-baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 1,604 MiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live2.{log,stalled,typed}`
   + `/tmp/gpu_live2_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live2.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. Update CLAUDE.md's stale gate values with the re-baselined numbers + run
   timestamps (the 1,239 vs 1,242 self-contradiction), commit, then resume
   **CSM-2** (scoreboard/classification, council item 2 — its grounding data
   is in `plan/SWITCHPOINT.md`'s CSM-1b todo note / `reports/csm/`).

## gpu-live1 handoff (2026-09-08 — A=01a07f33 → chain → C on 100k → A resume)

First LIVE run of the gpu-handoff chain (docs/ops/PC_GPU_HANDOFF.md):
`gpu-handoff.sh --tier2 plan/gpu_live1.spec` flips 262k→100k, opens C
(visible terminal `GPU-gpu_live1`, fresh 100k pi) which runs the JJK gate
baseline per `plan/gpu_live1_task.md` (→ `reports/master-work/GPU_LIVE1_REPORT.md`),
flips back 262k, and a gated plain-shell typer types the resume line into A's
window (50331658). A sits idle at its prompt meanwhile (frozen context, zero
cost). Engine was untouched by today's MASTER_WORK deploy, so the baseline
should hold (eval 31/31, span-recall 100%); a deviation is a real signal.

**On resume (the typed RESUME line is my next user message):**
1. Read `reports/master-work/GPU_LIVE1_REPORT.md` (C's baseline).
2. Restore `:8000` to CPU (C left it on CUDA; 262k co-location rule —
   headroom 3.5 GiB < 6 GiB).
3. Check chain state: `reports/master-work/gpu_handoff_state/gpu_live1.{log,stalled,typed}`
   + `/tmp/gpu_live1_chain.log`. A `STALLED` flag = inspect, then replay:
   `setsid nohup bash tools/master-work/gpu-handoff.sh --tier2 plan/gpu_live1.spec >/dev/null 2>&1 &`
   (gates are idempotent).
4. Trash C's transcript (`reports/master-work/gpu_handoff_state/c_session`)
   — only AFTER reading the report (deleting it earlier poisons the
   switch-back fit guard).
5. CSM resume remains on hold (owner-paused; the stuck session 01a07cab
   resumption is a separate, later flip).

## Campaign todos (live list — every CSM session rebuilds its todo panel from this section and syncs it back after each status change; the panel is per-session volatile state, disk is the tiebreaker)

- [x] 0. Wave-0 tier-0 reachability — 439→0 unreachable, span-recall csm rc=0 (record only; 6-word floor note in the audit)
- [x] 1. Seed-bank inventory + revid-stamp (CSM-1 — `064093e`)
- [x] 2. Classify every CSM page type + generalize the scoreboard (CSM-2 — `42aa296`; 14 unknowns resolved, JJK output byte-identical)
- [x] Standing-gate re-baselining ×2 — gpu-live2 (`GATE_REBASELINE.md`, 1,242) + gpu-gate3 (`GATE_REBASELINE_2.md`, 1,249; CLAUDE.md + gates-skill baselines updated, `2c80867`)
- [x] 3. D5 measurement infrastructure (CSM-3 — `f93d396`: pinned hashed panel + held-out split, csm panel pinned hash e3d73720… (17,181 + 200); wired (title,sentence) resume, jsonl rewritten; full-denominator hit_rate; three doors + --sanity dead-door halt; tier-0 rename `chunk-containment` (alias kept); <6-word floor recorded (775-line census, exclusion stands); pytest 1,253)
- [x] 3b. CSM-3b post-council (COUNCIL_csm-3 Rulings 1/7): roster-door fix (`served_text` flattens members/passages; member names = returned docs; roster-shaped test) + panel-hash recompute/enforce (exit 1) + bare-list held-out load + named consumer (`tools/csm/panel_heldout.py`) — `bc73795` (close-out: exit-code recheck + JJK tier-0 unchanged + commit, wave 1 fresh 100k B session 2026-09-08); standing gates + 39-question seed bank receipt (worker 2 gates, worker 3 close-out): `reports/csm/CSM3B_GATES.md` @ `78b5cf3`
- [ ] 4. D5 exhaustive tier-1 × 3 doors (**PHASE 2 — extraction**; GPU-h pending measured s/probe — sanity runs measure it first, COUNCIL_csm-3 Ruling 4; batched via the gpu-handoff chain in Qwen quiet windows, smaller dial if VRAM demands; standing 400-probe gate stays)
- [x] 5. Phase-0 remainder (**PHASE 1 — Wave 2, sub 4 — DONE** `waveB_csm5_remainder.md`: 5.3 CSM fixtures / 5.5 no-LLM-judge generator-sliced gold + held-out declaration / 5.4 door-first pre-check (zero GPU; the 34 s one-copy 5.4 re-adjudication ran at the P1.4 close, `reports/csm/receipts/census_5_4_readjudication_p14.md` — 21/21 reds identical to 09-09, 0 closed, no de-scope) / §13 awareness line / the twenty-failures set (`waveA_twenty_failures_author.md`))
- [x] 6. D6 oracle + bounded instrument (**PHASE 1 — instrument half DONE** `waveB_csm6_instrument.md` + census authoring (`3dbc3ef` v2 50-item; v1 60-item bank): CSM dimension map, frozen census sets (seeded + revid-stamped, D4 fresh-context authored), T0 pilot 843/843, cross-page census 10,889/11,261; **PHASE 2 — extraction half** pending: P2.3 D6 extraction, only on the 21 red dimensions (floor stands post 5.4 re-adjudication))
- [x] 7. §9a closure loop (D1–D6; **PHASE 1 iteration 1 DONE** — one class per fix, never reword to pass: R-1 router / R-2 passage-leg / R-3 roster-scoping / R-5 relations / R-6 subject_aliases / R-7 identity_fields all green; halt-meter converged `407c016` (D23: 35 open = 22 floor + 13b + 0c; halt condition met, no regression / no no-reduction iterations fired))
- [ ] 8. Done-declaration + pilot memo (**PHASE 2**; pasted raw output + the four pilot numbers; JJK baseline diff-empty; halt before P6)
- Standing items (whole campaign): council every 2–3 todos — **one agent at a time** (owner rule 2026-09-08); raw receipts, never "100%" prose; `coverage_report` regenerated after every commit; the four standing gates before any pass is declared done; per-wiki handling in `series/csm/overrides.yaml` / `tools/csm/` only; JJK baseline untouched; **Phase 1 (owner rule 2026-09-08): all model/GPU work on CUDA at the 100k dial (live CSM dial since the P1.1 boundary; the 150k draft was superseded per council #24/#25), no CPU shell command >15 s, 2-subagent waves; the gpu-handoff switching plan is Phase 2 only**.

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:53:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=3513MiB
- 2026-09-07T23:32:51+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=9002MiB
- 2026-09-08T10:14:37+05:30 qwen-switch: ctx=135168 (owner manual +--vision; profile = serve_ctx_135168.sh), api=cpu, free=5575MiB
- 2026-09-08T12:51:22+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7072MiB
- 2026-09-08T12:56:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1604MiB
- 2026-09-08T13:47:15+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6932MiB
- 2026-09-08T13:56:00+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1488MiB
- 2026-09-08T15:18:32+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6699MiB
- 2026-09-08T15:29:18+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1202MiB
- 2026-09-08T16:50:27+05:30 qwen-switch: ctx=150000 (mode 150000), api=cpu, free=5182MiB
- 2026-09-08T17:37:25+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=6820MiB
- 2026-09-08T18:30:37+05:30 manual (worker 3): CSM-3b gate cycle complete — worker 2 (gates-bank-cuda) froze at 18:20, worker 3 close-out @ `78b5cf3`; 4 standing gates = 15:22–15:26 re-baseline (pytest 1,254 / eval jjk 31/31 / span-recall jjk 48,572+390/400 / canon opm 10/16·236/236·79.0%); seed bank no new FAILs (G-CSM-1/G-CSM-2 persist); heldout sanity-4 4/4 HIT (Ruling-7 green); F-CSM-3b-1 (ledger sidecar shared per series, not per panel) recorded for the council
- 2026-09-08T19:05:00+05:30 manual (orchestrator): council CSM-3b complete (workflow 5dcd56b8, 11 sequential agents, one-agent-at-a-time per owner rule) — record `reports/csm/COUNCIL_csm-3b.md` + artifacts `reports/csm/council_csm-3b/` @ `ccd4523`; **verdict: RATIFY the CSM-3b close**; rulings R-CSM3B-1..7 on disk; ledger row #20 in `reports/comprehension/COUNCIL_HISTORY.md`; GATE.md Phase-2 pre-flight lines (R-CSM3B-6) + self-contained receipt header (R-CSM3B-7) same commit; next = Wave 2 pre-step (R-CSM3B-2 F1 ledger fix + R-CSM3B-3 live roster probe, sequential, orchestrator-graded) → the two parallel Wave-2 subs (CSM-6 instrument + CSM-5 remainder) → §9a closure loop iteration 1
- 2026-09-08T19:45:00+05:30 manual (orchestrator): Wave-2 pre-step GRADED PASS (live interleaved 2-panel survival: pinned 168->172 + heldout 9->13, both keyed ledgers retain their own rows, all stamped cuda+commit+panel_hash; log /tmp/prestep_grade.log) + pre-step committed; F1 (R-CSM3B-2) and roster probe (R-CSM3B-3: 31/88 members, 16,231 chars, 0 pre-fix) closed; next = deploy the 2 parallel Wave-2 subs (CSM-6 instrument + CSM-5 remainder + R-CSM3B-4 pre-checks) -> §9a closure loop iteration 1
- 2026-09-08T21:47:43+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1464MiB
- 2026-09-08T22:41:06+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6967MiB
- 2026-09-08T23:35:06+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1486MiB
- 2026-09-09T01:53:56+05:30 qwen-switch: ctx=150000 (mode 150000), api=off, free=5397MiB
- 2026-09-09T22:03:52+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1563MiB
- 2026-09-09T23:29:19+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1606MiB
- 2026-09-10T00:29:26+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7077MiB
- 2026-09-10T00:30:38+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1607MiB
- 2026-09-10T00:37:25+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7084MiB
- 2026-09-10T00:52:47+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
- 2026-09-10T00:54:16+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1610MiB
- 2026-09-10T00:58:08+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7080MiB
  - **01:0x (owner-directed):** 100k→262k return switch via the same
    `switch_restart.sh` helper (resume line = report 262k state to the owner,
    then stop). Helper bug fixed + committed (new-pi detection was `head -1`
    = oldest surviving pi → typed into the owner's pi; now `sort -n | tail -1`
    = newest = the spawned one).
- 2026-09-10T01:01:47+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
  - **01:0x (helper hardening, commit pending→done):** two latent defects
    found via the 01:01 262k run — (a) the "new pi pid" log label raced the
    pane's spawn (pgrep before exec) and printed the owner's pi 53686;
    (b) the fixed 12 s pre-type sleep lost the TUI race both times, so the
    typed resume line was swallowed and the owner had to type the first
    message that landed. Fix: label from the pane pid (wait comm=pi) + poll
    for the TUI status line (model name) before typing. Next switch's
    resume line should land unassisted.
  - **01:1x (owner ruled the 262k return FAILED — "context is still 102k"):** root cause — the /102k the owner saw was the owner's OWN terminal pi (53686, started 00:38:31 in the 100k era), not the helper-restarted pane pi. pi snapshots the model's contextWindow at startup and never re-reads `models.json`, so any pi alive before a switch keeps the old window in memory (status line + auto-compact threshold). The pane pi (restarted 01:01:47) had shown /262k all along (capture-pane proof 01:02:07: `8.1%/262k`). Fixes (all committed): (1) `switch_restart.sh` now prints `WARNING: stale pi(s) on the pre-switch window` (pgrep diff — every pi that survived the switch holds the old window and needs a manual `exit` + `pi -c`); (2) qwen-switch skill: new "The window is per pi-process" section + a Never item; (3) per the owner's order ("fix this issue, update your skill, then restart") the helper flow was re-run (262k re-switch, same session, fully self-contained). The owner's 53686 stays a manual owner step: `exit` + `pi -c` in the project dir.
- 2026-09-10T01:11:16+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1608MiB
  - **01:2x (owner's new idea — the model-driven switch flow, TRIED this turn):** "when you switch and see the model loaded, send a call to the llm through that shell; that call tells the model to terminate this shell and restart the pi agent." Implemented as `tools/master-work/switch_restart2.sh <mode> <old_pi_pid>` + `tools/master-work/relaunch_pi.sh <old_pid> <resume_msg>`: (1) the detached switch shell switches Qwen and waits for the model to load — the pi agent STAYS ALIVE through the switch (requires the session to fit the target context; a not-fitting down-switch stays on the legacy kill-first `switch_restart.sh`); (2) the shell types an LLM call into the directing pane (tmux send-keys) instructing the model to (a) pkill the switch shell, (b) launch `relaunch_pi.sh` (grace-kill self → tmux relaunch → TUI-ready poll → typed resume line → capture-pane proof); (3) the model executes the call with its own tools and ends its turn — it dies at the grace by design; (4) the switch shell waits bounded (600 s) for the pkill, else self-exits. The model (not a blind bash loop) does the restart. First live try: 262k re-switch, directing pid 56461, launched ~01:2x.
- 2026-09-10T01:18:01+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1609MiB
  - **01:2x (owner: "model reloads in 3-7 s, why wait this long — show a perfect 100k"):** tightened relaunch_pi.sh (GRACE 5->2 s, TUI poll 2 s->1 s, post-resume blind sleep 8 s->2 s — the slow parts were my sleeps, not the model) + made the LLM-call text mode-agnostic. Re-running the model-driven flow for a REAL mode change 262k->100k (:8000 lands on CUDA per the headroom rule), directing pid 56926 (session ~4k tokens, fits 100k). Target: whole switch ~10-20 s wall, verified by capture-pane, zero owner input.
- 2026-09-10T01:21:08+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7081MiB
- 2026-09-10T01:36:52+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1610MiB
- 2026-09-10T01:42:55+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=7060MiB
- 2026-09-12T02:29:15+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1535MiB
- 2026-09-12T02:34:50+05:30 qwen-switch: ctx=122880 (mode 122880), api=cuda, free=6303MiB
- 2026-09-13T02:00:23+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=6996MiB
- 2026-09-13T02:34:53+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1437MiB
- 2026-09-13T03:23:02+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6902MiB
- 2026-09-13T04:57:03+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=847MiB
- 2026-09-13T14:15:33+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1534MiB
- 2026-09-13T15:15:08+05:30 qwen-switch: ctx=262144 (mode 262k), api=off, free=1613MiB
- 2026-09-13T15:31:47+05:30 qwen-switch: ctx=174080 (mode 174080), api=off, free=4539MiB
- 2026-09-14T03:11:11+05:30 qwen-switch: ctx=174080 (mode 174080), api=off, free=4293MiB
- 2026-09-16T22:26:58+05:30 qwen-switch: ctx=122880 (mode 122880), api=off, free=6279MiB
- 2026-09-17T09:25:43+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=6928MiB
- 2026-09-17T09:38:40+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=1477MiB
