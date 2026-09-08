# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)

- mode: **100k + `--vision` (2026-09-08: owner added the vision flag to the
  serve profiles — `serve_100k.sh` + the `serve.sh` 262k template — for a
  local-LLM PC-control experiment; the reload keeps ctx 102400. Pre-reload
  headroom was 9002 MiB with `:8000` on CUDA — re-check `nvidia-smi` AFTER
  the reload: the fixed vision GPU allocation eats into that headroom; if
  free < 6 GiB, move `:8000` to CPU)** → CSM is paused (owner, 2026-09-08);
  its CUDA windows still run in 100k when it resumes; 262k at the
  campaign's close (no handoff needed — 262k > transcript, reloads in
  place).
- git: `8f8ffdb` (council verdict: SKIP T0–T4 bank, 8-item revised plan) on the
  campaign trail `281fe2e` (CSM Wave-0) → `4e7c304` (checkpoint: wave-0 closed,
  council in flight) → `8f8ffdb` (verdict). Untracked: `tools/csm/` (CSM-1's
  revid-stamp tool, committed with this checkpoint).
- trunk/excursion address (drift_log §4): **X2 CLOSED** (JJK D6-completion
  done, D11) · trunk P6 not-started by owner directive (JJK-only halt).
  **Next authorized work: the CSM (Chainsaw Man) campaign to 100% per
  `plan/Plan_to_perfection.md`** (todo #9; owner-authorized 2026-09-07).
- work explanation (what's done, what's in flight, the exact next step):
  - **JJK D6 is closed** (`reports/comprehension/DONE_DECLARATION.md`). All
    standing gates green: pytest 1,242, eval jjk 31/31, canon opm 236/236 ·
    79.0%, span-recall jjk offline 0 unreachable. The 400-probe CPU re-run
    **completed** — full live verbatim sweep: 1,366/1,407 HIT (97.1%, 18
    MISS_DOC / 21 MISS_SPAN / 2 TRUNCATED — the established [qa] noise band,
    consistent with the 390/400 CUDA probe); 285 records carry `urlopen`
    errors (the CPU `:8000` instance died mid-run) — a run-hygiene artifact,
    not a corpus signal. D3's tier-1 number stands.
  - **CSM campaign started — Wave-0 (plan §7 reachability pre-pass) is
    DONE**: 439 unreachable lines → **0 (100.0000%)**. Diagnosis: the CSM
    index predated the G15 chunker fix (422/439) + 17 lines in `Notes`
    (8 episode diff-note sections) and 2 `References` (crawler-filed alias
    blocks) that the chunker's MediaWiki-wide skip set treats as boilerplate
    but the oracle treats as content. Fix = re-index + `content_sections:
    [Notes, References]` in `series/csm/overrides.yaml` (the sanctioned
    per-wiki mechanism, zero engine changes; JJK precedent). Gates green on
    the new store: pytest 1,242, eval jjk 31/31, canon opm 236/236 · 79.0%,
    span-recall jjk 390/400, span-recall csm rc=0.
  - **Council verdict landed (`8f8ffdb`): SKIP the T0–T4 question-bank build;
    8-item revised plan CSM-1..8** (text in `reports/csm/COUNCIL_csm-campaign.md`;
    n=4 stable sample; the existing bank `questions/csm.json` (39 questions,
    zero revid stamps) must be inventoried + revid-stamped (CSM-1), never
    clobbered — council point 3 / §5.6).
  - **Owner paused the CSM campaign (2026-09-08)** — CSM-1 stays in flight
    but on hold; todos re-created when it resumes. Current activity: a
    local-LLM PC-control experiment — vision on the 27B via ninfer's
    `--vision` flag (was off; the API returned 400 `vision_disabled`);
    the box is an X11 session (tty2) so xdotool is the input path; survey
    (Reddit/web, 2026-09-08): off-the-shelf = bytedance/UI-TARS-desktop
    (34k★, local VLM, "Remote Computer Operator"), or the DIY loop
    screenshot → VLM (`:18080` now multimodal) → xdotool actions.
  - **New standing rules (owner, 2026-09-07, persisted in CLAUDE.md):**
    no CPU job >15 min (switch Qwen to 100k and run CUDA instead; or run on
    GPU whenever faster); polling loops print a status line every 10–15 s
    and every bash call carries an explicit `timeout`; a tool that doesn't
    work on both JJK and CSM gets a CSM-specific script (never mutate
    JJK-verified tooling; per-wiki config in `series/csm/overrides.yaml`).
  - **Exact next step: finish CSM-1, then CSM-2** (classify every CSM page
    type + generalize the scoreboard: 5.1 + archetypes).
- open questions / risks:
  - The verdict decided the bank question: SKIP. The seed bank survives as
    CSM-1's inventory target (fresh stamps, never copied from JJK's fixed
    data).
  - CSM is smaller and differently shaped than JJK (537 pages vs ~1,500;
    infobox `Character` family; positional `{{Ref|m|216|3-4}}` citations
    already mapped). Per-wiki handling stays in `series/csm/overrides.yaml`
    or CSM-specific scripts — the closed JJK baseline (1,242 tests) is
    untouchable.
  - 5-parallel council children on shared Qwen KV produce 60 s no-activity
    nudges (false positives; the KV pool serializes them). Do not steer or
    interrupt on those; only act on a child that is failed/stale for >5 min.
  - `:8000` is on CUDA with 9 GB headroom (100k profile). Long LLM batches
    still follow the hard rule: dedicate the GPU (stop `:8000` or CPU it
    first).
  - **`--vision` (2026-09-08)**: now in `serve_100k.sh` + `serve.sh`
    (262k template). VRAM delta unknown until reload (fixed vision GPU
    allocation) — check `nvidia-smi` after; rollback = drop the flag and
    re-run the profile. Pre-existing generated `serve_ctx_*.sh` profiles do
    NOT carry the flag (regenerated from the template only when the file is
    recreated). ninfer-work is not a git repo — the flag lives in those two
    files only.
- first action on resume (**fresh session — overflow handoff, 2026-09-08**:
  the 100k session died on `context_length_exceeded` 102518 > 102400 and
  summarization recovery failed too; pi.md §5.5 — a fresh transcript always
  fits, this file is the resume):
  1. Recreate the CSM-1..8 todos from `reports/csm/COUNCIL_csm-campaign.md`
     (the per-session todo panel was lost with the dead session).
  2. `git log --oneline -3` (expect `6a87479` head, clean tree — the
     overflow-handoff checkpoint committed the switchpoint +
     `tools/csm/stamp_revids.py`).
  3. Finish CSM-1 (revid-stamp state of `questions/csm.json` via
     `tools/csm/stamp_revids.py`; commit), then CSM-2.
  Standing gates after any build: pytest / eval jjk / span-recall jjk /
  canon opm.
- done this turn (2026-09-07 23:3x, CSM Wave-0 + campaign start): CSM
  grounded (537 pages, 5,081 facts, 11 types, audit 5/5 PASS, span-recall
  rc=2 with 439 unreachable) → diagnosed (pre-G15 index + Notes/References
  divergence) → fixed (re-index + `content_sections`) → verified (0
  unreachable, 100.0000%; all standing gates green on CUDA, 1,242 pytest).
  Two new owner rules persisted in CLAUDE.md (GPU >15 min; 10–15 s polling
  + explicit timeout). CSM campaign todos created (#11–#15). Council on
  the CSM plan launched. Committed `281fe2e`.

## Switch log (machine-appended by qwen-switch.sh)

- (none yet)- 2026-09-07T22:05:09+05:30 qwen-switch: ctx=102400 (mode 100k), api=off, free=8988MiB
- 2026-09-07T22:17:58+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:19:34+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=8986MiB
- 2026-09-07T22:53:45+05:30 qwen-switch: ctx=262144 (mode 262k), api=cpu, free=3513MiB
- 2026-09-07T23:32:51+05:30 qwen-switch: ctx=102400 (mode 100k), api=cuda, free=9002MiB
