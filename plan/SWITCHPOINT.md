# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)
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
- [ ] 5. Phase-0 remainder (**PHASE 1 — Wave 2, sub 4**) — 5.3 pilot fixtures / 5.5 no-LLM-judge / 5.4 door-first (extraction only on red) / §13 awareness line / the twenty-failures set (named author)
- [ ] 6. D6 oracle + bounded instrument (**PHASE 1 — instrument half**: parameterize the two jjk-hardcoded tools, CSM dimension map, eight-verb sample, frozen census sets (seeded + revid-stamped, D4 authored by a fresh-context subagent), T0 pilot, cross-page fact census; **PHASE 2 — extraction half**, only on red census)
- [ ] 7. §9a closure loop (D1–D6; **PHASE 1 iteration 1**: one class per fix, never reword to pass, halt on regression / two no-reduction iterations)
- [ ] 8. Done-declaration + pilot memo (**PHASE 2**; pasted raw output + the four pilot numbers; JJK baseline diff-empty; halt before P6)
- Standing items (whole campaign): council every 2–3 todos — **one agent at a time** (owner rule 2026-09-08); raw receipts, never "100%" prose; `coverage_report` regenerated after every commit; the four standing gates before any pass is declared done; per-wiki handling in `series/csm/overrides.yaml` / `tools/csm/` only; JJK baseline untouched; **Phase 1 (owner rule 2026-09-08): all model/GPU work on CUDA at the 150k dial, no CPU shell command >15 s, 2-subagent waves; the gpu-handoff switching plan is Phase 2 only**.

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
