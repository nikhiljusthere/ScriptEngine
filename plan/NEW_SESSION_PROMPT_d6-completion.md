# NEW_SESSION_PROMPT — JJK D6-completion (session-seeding prompt)

**Checkpoint:** 2026-09-07, HEAD `8b6633e`. The last working checkpoint came
from an opencode session (state quoted in §2 below). This prompt re-grounds
from disk first — **disk wins over this prompt** wherever they disagree.

**Use:** fresh pi session in `/home/goblin/ScriptEngine` (trust the project
once, so `.pi/skills/` loads). Paste §1 as the first message, or just say:
*"Read `plan/NEW_SESSION_PROMPT_d6-completion.md` and execute it."*

---

## 1. The prompt

You are continuing the **Jujutsu Kaisen D6-comprehension campaign** in
`/home/goblin/ScriptEngine`. **Mandate: JJK only. Halt before P6** (no
cross-corpus work — `Plan_to_perfection.md` §7 / Wave-0 is explicitly out of
scope for this plan). Read `pi.md` §1 (startup ritual) and do step 0 below
before acting on anything in this prompt.

### 0. Ground first (disk over prompt, always)

- `plan/drift_log.md` §4 (live position) + §3 ledger (last entries)
- `reports/comprehension/GATE.md` (gate state) + `COMPREHENSION_REMAINDER.md`
- `plan/Plan_to_perfection.md` **§12 (dimension map — R1–R5 retired)** and
  **§13 (durable-key precondition — verify the current state of the events
  remap / `build.py` reset guard**); §7 is P6 — do not enter it
- `reports/comprehension/P3A_ABILITY_CENSUS.md` (all five ability dims
  3C-GREEN) + `STEP5_CENSUS_545.md` (D5 545-pair census: 540/545 = 99.1%,
  5 retrieval-controlled not-reached, fixed + tracked @ `a5e93c3`)
- `plan/SWITCHPOINT.md` + `ninfer-work/qwen_mode.txt` + `nvidia-smi`
  (which Qwen context mode is live; where `:8000` belongs)
- `git log --oneline -15` (what landed since the opencode checkpoint)

### 1. Grounded state at the last checkpoint (opencode, 2026-09-07 —
re-verify each line in step 0; the repo has moved since)

- **D5 (reachability):** ~99.1% on the 545-pair census (5 residual
  retrieval misses, fixed + tracked); **roster and narrative doors still
  unmeasured**. Tier-0 span-recall 48,572/48,572 (rc=0).
- **D6 (comprehension):** the 5-phase mechanism is built (events table,
  time axis, the three-check gate, continuity scaffold). The checkpoint's
  numbers (714 events / 38 disagreements / 154 unplaced) are the
  **pre-corpus-widening baseline**; the live store per `GATE.md` is
  **2,748 events (2,594 placed), 107 cross-page disagreements (27.4% of
  multi-page groups; 92% touch section-placed rows), 154 unplaced,
  abilities 594/94 chars, relations 821/136 (298 era-bearing), semantics 0**.
- `COMPREHENSION_REMAINDER.md` still carries **R1–R5 + B5**, but
  `Plan_to_perfection.md` **§12 retires them as a narrow read of the goal**
  (owner: *"I did not mean only those 3 things, I meant everything"*). The
  replacement is the **dimension map** (~106,000 words of character prose
  across 12 dimensions, + 3 the map must also cover: state-over-time — P4
  closed a bounded version via `extra_facts`, 4B wiki-wide model deferred —,
  outcomes, causality). §12's two governing tests: (a) **the eight-verb
  coverage precondition** (sample 100 plot-summary sentences; model-free —
  nothing schedules off the map until it is measured), and (b) the
  **retrieval-not-extraction test** per "NONE" dimension (10 questions;
  bundle serves the paragraph → no extraction owed; it doesn't → chunking
  defect, not a missing table).
- **P3.A:** all five ability dimensions 3C-GREEN (retrieval suffices; no
  widen/extract owed). **P4 closed** (state-over-time durable via
  `extra_facts`, D8, `61311c2`). **P6 not started** — and stays out of scope
  for this plan.
- **The goal:** full D6 comprehension + the dimension map, JJK only. Its
  "done" criterion and sequencing are a genuine fork → per standing rule 1,
  the next action is **the council** (todo 2), not a self-chosen plan.

### 2. Standing rules (hold for the entire run — `plan/STANDING_RULES.md`)

1. **No user input.** Every fork / ambiguous result / blocked step /
   judgement call → **run `llm-council`**, act on its verdict, record it.
   No asking which option or whether to proceed; no stopping to report and
   wait. The only stop is the halt path in `flow.md` (council first).
   Council claims are **DB-verified before recording** — a council that
   cannot be verified did not happen.
2. **The GPU is available — do not default to CPU.** Check `nvidia-smi`
   first; short retrieval jobs co-locate with Qwen; a sustained 27B
   extraction batch takes the card to itself (stop `:8000` / run it on CPU
   first). CPU is a measured decision, not a habit.
3. **Council cadence.** (a) every 2–3 completed todos — review the fixes
   just made; (b) end of every sub-list, **before the return pointer
   fires**; (c) every phase gate. Each council →
   `reports/comprehension/COUNCIL_<subject>.md`, committed with the work it
   reviewed. **If it is not on disk, it did not happen.**

Plus the `CLAUDE.md` working agreements (summary; read the full file):
`audit` before `index`, `span-recall` after `index`, `eval` after touching
chunking/fusion/retrieval/parser, verify against the live wiki output, no
series names in `.py` (`overrides.yaml` is the only per-wiki surface),
never guess a citation parameter's meaning, no dependency without a caller,
"no third corpse" (a new table ships with the door that reads it),
commit discipline (branch `character-scoped-questions`, named paths,
area-prefixed messages, no push). And the `pi.md` kit rules:
checkpoint-first (`switchpoint`), drift discipline (`P`/`X` addressing,
return pointers written when the excursion opens), docs as live artifacts.

### 3. Skills (load on demand; `/skill:<name>` to force)

| skill | when it fires |
|---|---|
| **llm-council** | every fork, big build, phase gate. **Owner rule (2026-09-08): 5 advisors one at a time, then 5 peer reviewers one at a time, then the chairman synthesis** — sequential in any mode (the 5-parallel convention is retired: at 262k the children fight the shared KV pool for answering). Verdict → `COUNCIL_<subject>.md`, claims DB-verified, committed. |
| **qwen-switch** | when a phase needs the CUDA `:8000` (reranker co-location) or 2 parallel subagents: `switchpoint` checkpoint → fit check (`$PI_SESSION_FILE` bytes/4 < target ctx; a fresh session is tiny, so 100k is seamless) → **one atomic** `bash` call `cd /home/goblin/ninfer-work && ./qwen-switch.sh 100k` (`timeout: 300000`) → verify (`qwen_mode.txt` + `nvidia-smi`) → continue. Switch **back to 262k** when the GPU phase ends. A heavy Qwen LLM batch is the *opposite* rule (stop `:8000`, no switch). |
| **switchpoint** | before every switch, at council cadence points, at the end of significant work: commit + `plan/SWITCHPOINT.md` (a fresh session must be able to continue from disk alone). |
| **scriptengine-gates** | after any build / before calling a pass done: `audit → index → span-recall` ordering + the four standing gates at baseline (pytest **1,239** · eval jjk **31/31** · span-recall jjk **48,572/48,572 rc=0** · canon opm **10/16 · 236/236 · 79.0%**) + `comprehension-gate` / `continuity` for D6. |

Four skills are the right inventory — no more: the campaign's work is
plan-driven (council), checkpoint-driven (switchpoint), gate-driven
(scriptengine-gates), and mode-driven (qwen-switch).

### 3b. Installed capabilities (on request — not plan-critical)

- **`workflow` tool** (pi-dynamic-workflows, auto-loads) — fan-out
  subagents; e.g. run the 5+5 council as one workflow. Keep fan-out inside
  the active mode's subagent policy (≤ 2 in 100k; 5 = council exception).
- **ponytail** (pi-extension, auto-loads; `/ponytail`) — minimal-code
  discipline for any code this plan writes; keep its safety tier.
- **`headroom`** (`~/.local/bin/headroom`) — compress big tool outputs / JSON
  before re-feeding the model (68% measured on a 191 KB JSON payload); slows
  transcript growth so the 100k fit guard stays green longer.
- **`agent-reach`** (`~/.local/bin/agent-reach`) — `agent-reach get
  rss.feed|youtube.<cmd>` for research outside the wikis (skill:
  `~/.pi/agent/skills/agent-reach/SKILL.md`).

### 4. Todos (continue from the checkpoint)

- [✓] Ground live D5/D6 state from on-disk docs (drift_log,
  COMPREHENSION_REMAINDER, P3A, STEP5, GATE) — **re-run as step 0**; disk
  has moved since the opencode checkpoint.
- [•] **Run llm-council on the JJK D6-completion plan:** definition of
  *"done"* + sequencing — the §12 dimension map (incl. its two preconditions:
  the eight-verb coverage sample and the retrieval-not-extraction test) vs
  the retired R1–R5/B5 remainder, **plus the two unmeasured D5 doors
  (roster, narrative)**. The 107-disagreement corpus (key-refinement
  diagnostic per B5's re-scope) feeds the plan's evidence. Record to
  `reports/comprehension/COUNCIL_d6-completion.md` + commit.
- [ ] Execute the council's plan: dimension-map work + D6 remainder items +
  D5 door measurement (JJK only, stop before P6).
- [ ] Re-run standing gates: eval jjk 31/31, span-recall jjk 48,572/48,572,
  pytest ~1,239, canon opm 79.0%.
- [ ] **Halt before P6** (no cross-corpus work).

### 5. Halt condition

The plan ends when the council's "done" definition is met on JJK and the
standing gates re-run green. P6 / cross-corpus (Wave-0, `Plan_to_perfection.md`
§7) is **out of scope** regardless of momentum — the user's mandate is JJK
D6-completion only.

---

## 2. What this prompt deliberately does NOT carry

- No plan of its own for "what to build" — that is the council's output
  (todo 2). A self-chosen plan would violate standing rule 1.
- No P6/Wave-0 content, despite `COUNCIL_p6-kickoff.md` existing on disk —
  the mandate is JJK-only, halt before P6.
- No transcript — a fresh session seeded by this file starts small, so the
  first 100k switch (if the council's plan needs CUDA `:8000`) is seamless.