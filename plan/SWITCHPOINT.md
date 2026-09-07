# SWITCHPOINT — the resume file for Qwen mode switches

pi's model is the Qwen server: while the server is reloading the agent has no
model, and after reopening pi the *transcript* may be discarded (small
contexts compact fast). So everything needed to continue must live here, on
disk, **before** `qwen-switch.sh` runs. Fill the hand-written section before
every switch; `qwen-switch.sh` appends machine lines to the switch log — never
edit those.

## Current position (hand-written — fill BEFORE every switch)

- mode: **100k (current; the 2026-09-07 23:32 switch, `--force` — file-bytes
  guard overstates, live context well under; `:8000` back on CUDA, headroom
  9002 MiB)** → the CSM campaign runs its CUDA windows in 100k; return to 262k
  at the campaign's close (no handoff needed — 262k > transcript, reloads
  in place).
- git: `281fe2e` (CSM Wave-0 + two standing rules) on the campaign trail
  `6abb05b` (R4) → `0d1425f` (ops/gates) → `87fe80c` (X2.d + 3a/3b/3d) →
  `8ffce8e` (3c) → `1b6fba3` (X2.g/X2.h) → `14eaae3` (JJK close checkpoint) →
  `281fe2e` (CSM Wave-0).
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
  - **In flight: llm-council on the CSM campaign plan** (5 advisors → 5
    reviewers → chairman; async). It must decide (a) whether the T0–T4
    question-bank build is necessary for CSM 100% (owner: skip it if not
    necessary), (b) item scope/order, (c) which JJK learnings to port from
    day one. Verdict lands in `reports/csm/COUNCIL_csm-campaign.md`.
  - **New standing rules (owner, 2026-09-07, persisted in CLAUDE.md):**
    no CPU job >15 min (switch Qwen to 100k and run CUDA instead; or run on
    GPU whenever faster); polling loops print a status line every 10–15 s
    and every bash call carries an explicit `timeout`; a tool that doesn't
    work on both JJK and CSM gets a CSM-specific script (never mutate
    JJK-verified tooling; per-wiki config in `series/csm/overrides.yaml`).
  - **Exact next step: read the council verdict, restructure the CSM todos
    to its revised plan, then work the revised items** (Phase-0 blockers
    §5.1–5.6 and archetype mapping §6 are the likely first items; the
    D1–D6 gap-closure loop §9a follows; done-declaration + final gates
    close it).
- open questions / risks:
  - The council verdict decides the question-bank question; if it says
    KEEP, the bank must be CSM-generated (fresh, seeded, frozen — never
    copied from JJK's fixed data) and every question tier justified by a
    D1–D6 requirement.
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
- first action on resume:
  1. `git log --oneline -3` (expect `281fe2e` head; clean tree).
  2. Read `reports/csm/COUNCIL_csm-campaign.md` (the council verdict; if
     the run died before the chairman wrote it, restart the council and
     keep Wave-0 as the done item).
  3. Restructure the CSM todos to the verdict's revised plan; start the
     first revised item. Standing gates after any build: pytest / eval jjk
     / span-recall jjk / canon opm.
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
