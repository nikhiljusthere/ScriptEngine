# COUNCIL_p6-kickoff — Phase boundary P4→P6: is the Wave-0 plan the right P6 kickoff?

**Verdict: KICK OFF Wave-0 with the offline cause table first — not per-wiki fixes, not
a re-index.** The plan's Wave-0 is the right shape (reachability pre-pass on all seven
before any prose) but its kickoff is mis-ordered: (1) the cross-corpus cause
classification is free (span-recall is offline, <1s/corpus, and the per-line miss
files already exist from the Sep-5 baseline) and it re-orders the fix work — causes
are shared, one `content_sections` override can collapse N corpora into one fix;
(2) every re-index is a **full** re-embed (`build.py:490` `vectors.recreate()`), so
the GPU queue is sized by corpus page count, not by the number of fixed lines —
db+onepiece are sustained-load batches that cannot co-locate with the resident 27B
Qwen and must go CPU or a genuinely quiet window, while the small five can borrow
the short-borrow exception; (3) the per-wiki gate is `span-recall` 0-unreachable
(or a cause-attached, documented floor — no catch-all floors) + `audit` + `pytest`
+ `eval` where a bank exists (db/hxh/onepiece) or `canon-run` (opm), with a
`span-recall --probe 400` before/after as the live-regression substitute for the
four corpora with no gold bank (csm/berserk/bleach, plus opm's eval half). The CSM
pilot starts as soon as CSM's own Wave-0 gate passes — it is the plan's sensor and
does not have to wait for the other six. `extra_facts` stays the durable shape; 4B
stays deferred behind a tripwire (~10–12 declared facts on JJK ⇒ build the
extractor). Sourcing is a Wave-0 check too: reachability ≠ sourceability (Berserk
sources 0% by wiki quirk), so each corpus's `audit` sourceability is recorded, not
assumed.

- **Subject:** P6 kickoff — Wave-0 (reachability pre-pass on the seven non-JJK
  corpora, 20,655 unreachable lines at the Sep-5 baseline) vs. the plan's
  smallest-first ordering; the `extra_facts` durability call; GPU contention with
  the resident 27B Qwen session on the shared 32 GB card.
- **Date:** 2026-09-07
- **Council:** 5 advisors (Contrarian, First-Principles, Expansionist, Outsider,
  Executor) → 5 anonymized peer reviewers → chairman synthesis, all rounds in
  parallel (the council working agreement in `CLAUDE.md`). Phase-boundary gate
  per standing rule 3 (P4 closed at D7/D8, P6 is the next phase). De-anonymized
  mapping: A=Outsider, B=Expansionist, C=Executor, D=Contrarian, E=First-Principles.
- **DB-verified before recording** (standing rule 1). Facts checked on disk:
  `scriptengine/index/build.py:490` (`vectors.recreate(embedder.dimensions)` — full
  re-embed every index, not a diff); `scriptengine/eval/gold_*.json` (jjk, db, hxh,
  onepiece, continuity — so csm/berserk/bleach have no eval bank and opm's live
  gate is `canon-run`); `reports/span-recall/{csm,db}/index_misses.jsonl` (per-line
  miss dumps from the Sep-5 baseline, fields `breadcrumb`, `doc_has_chunks`,
  `boilerplate` — the cause table is a group-by, not new instrumentation);
  `series/*/overrides.yaml` present for all seven.

## Gate question

Phase P4 (JJK interval facts) is closed and verified: the two hand-inserted
Culling-Game state facts are now declared under `extra_facts:` in
`series/jjk/overrides.yaml` and re-landed by a generic builder step on every
`index` (commit `61311c2`); S-group 4/4, eval 31/31, span-recall 0 unreachable,
2,748 events remapped. Phase P6 (cross-corpus, `plan/Plan_to_perfection.md` §7)
proposes: Wave-0 reachability pre-pass on all seven corpora (smallest-first:
csm 537 → berserk 762 → opm 1,571 → hxh 2,018 → bleach 2,252 → db 7,205 →
onepiece 7,613 pages; break unreachable lines down by cause, fix per-wiki in
`overrides.yaml`, gate = 0 unreachable + pytest + eval), then a CSM pilot to
calibrate four cost numbers. Standing rules: no user input (forks come to this
council), GPU-first with the hard rule that sustained LLM/embedding batches keep
the card for Qwen, per-wiki data in `overrides.yaml` never engine code.

## Where the Council Agrees

- **`extra_facts` is the right durable shape; 4B stays deferred.** All five
  endorsed keeping it (declarative YAML re-landed by a generic builder; P4's 4/4 +
  2,748-remap is the proof it survives re-indexing). The Contrarian's caveat was
  accepted as a recorded limitation, not a blocker: it is durable against
  re-*indexing*, not re-*crawling* (YAML and wiki prose coexist unchecked). A
  tripwire was agreed by the First-Principles and Outsider advisors: ~10–12
  declared interval facts on JJK makes the 4B extractor no longer deferrable.
- **The first action is offline and zero-GPU.** Four of five advisors independently
  landed on it: run the diagnosis across all seven and group the 20,655 misses by
  cause before touching any `overrides.yaml` or the GPU. `span-recall` tier 0 is a
  sub-second SQLite sweep; the per-line miss dumps already exist
  (`reports/span-recall/<s>/index_misses.jsonl`, fields include `breadcrumb` and
  `doc_has_chunks`), so the cause table is a group-by, not new code.
- **GPU contention is the binding constraint on the fix phase, not the 20,655
  lines.** Every re-index is a full re-embed (verified `build.py:490`). The small
  corpora (csm 537, berserk 762, opm 1,571) fit the short-borrow co-location
  exception in a Qwen quiet window; db (7,205) and onepiece (7,613) are sustained
  loads that the hard rule forbids co-locating — CPU, or a dedicated quiet window.
  One corpus at a time, smallest first, is correct for the re-embed queue.
- **The gate is tighter than the plan's wording.** "0 unreachable or a documented
  floor" was rejected as a catch-all (the floor must be cause-attached and
  provably non-content); `audit` was added to the gate (standing rule: audit
  before index — a chunker/skip-set change can silently break extraction); the
  eval half of the gate only exists for db/hxh/onepiece (+ opm via canon-run), so
  csm/berserk/bleach need a `span-recall --probe 400` before/after as their
  live-regression check.

## Where the Council Clashes

- **Ordering of the fix phase: smallest-first vs. cause-first vs. defer the big two.**
  The Expansionist: causes are shared across corpora (one D5 `content_sections`
  gap can hit three or four at once), so order fixes by *cause* — one override
  fixes N corpora. The First-Principles: the pilot is the plan's *sensor*, so it
  should start right after CSM's own gate, not after all seven. The Outsider: the
  two big corpora (75% of the unreachable lines) are the riskiest and least
  predictable (the other agent's session state), so decide now whether the small
  five go first and the big two defer, or the big two go CPU with a time estimate.
  **Resolution:** cause-first for the *fixes* (they're offline and shared), then
  the *re-embed queue* smallest-first with the big two deferred to CPU/quiet
  windows, and the CSM pilot starts as soon as CSM's gate passes. None of this
  blocks the offline cause table, which is done first regardless.
- **How much of the 20,655 is content.** The Expansionist framed the unreachable
  lines as a "~15–20% content win" the plan undersells; the reviewers flagged that
  figure as unmeasured — some of the misses may be deliberately-skipped
  non-content (which is exactly what the cause-attached floor is for). The cause
  table settles it: the breakdown says whether Wave-0 is a content win or mostly
  housekeeping.

## Blind Spots the Council Caught

- **The diff-embed assumption is false.** Two advisors assumed a chunking fix
  only re-embeds the newly-included sections. The reviewers verified in code
  (`build.py:490`, `vectors.recreate`) that every index run recreates the whole
  vector store — each corpus pays full-corpus embedding. The measured CSM CPU
  embedding time is therefore the gating number for the whole wave plan.
- **No one put `audit` in the gate.** Wave-0 changes are chunker/skip-set
  changes; a silently broken extractor is exactly what `audit` catches.
- **Reachability ≠ sourceability.** All five responses gated on reachability
  alone. The prose deliverable also needs the sourcing layer (per-wiki
  `CitationGrammar`): Berserk sources 0% because it cites interviews/cover art,
  not instalments, and One Piece is sourceable by route two. A "0 unreachable"
  gate would otherwise flood context bundles with lines a writer cannot trace to
  a chapter. Each corpus's `audit` sourceability is recorded during Wave-0.
- **The gold-bank state was contested and is now settled on disk.** One advisor
  said five of seven lack a gold bank, another asserted (incorrectly, no such
  files exist) that all seven have question banks. Disk check: eval gold banks
  exist for jjk, db, hxh, onepiece, continuity only; opm is gated by canon-run.
  Gate design follows the verified set.
- **A "0 unreachable" gate can flood bundles with junk.** The D5-class fix makes
  oracle-counted sections reachable without auditing whether they are usable
  prose — the `audit`-in-gate point above is the counterweight.

## The Recommendation

Keep the plan's Wave-0 scope (all seven, pre-prose) and the `extra_facts`/4B-defer
decisions, but re-order the kickoff:

1. **Cause table (offline, today):** regenerate `index_misses.jsonl` for all
   seven, group by cause — `doc_has_chunks` false (no chunks at all for the doc),
   D5-class (`breadcrumb` in a section the oracle counts but the chunker skips),
   Trivia-bullet gap (opm/bleach known), other. One cross-corpus table drives all
   seven fix jobs; a single `content_sections` override may collapse several
   corpora into one fix. In parallel, **measure CSM's CPU embedding time** — the
   device-choice number for every subsequent re-embed.
2. **Fixes cause-first, per-wiki in `overrides.yaml`** (engine code only for the
   Trivia chunker gap, which is a real bug, not per-wiki data).
3. **Re-embed queue smallest-first:** csm → berserk → opm → hxh → bleach on the
   short-borrow exception (Qwen quiet window, check Qwen alive right after);
   db and onepiece on CPU or a dedicated quiet window (sustained load, hard rule).
   Per-corpus gate: `span-recall` 0 (or cause-attached documented floor) +
   `audit` + `pytest` + `eval` (db/hxh/onepiece) / `canon-run` (opm) +
   `span-recall --probe 400` before/after for csm/berserk/bleach.
4. **CSM pilot starts after CSM's gate** — its four cost numbers calibrate the
   remaining six; it does not wait for the whole wave.
5. **Record sourceability per corpus** (from `audit`) during Wave-0 so the prose
   phase knows which corporas source 0% by wiki quirk before it is surprised.

## The One Thing to Do First

Regenerate the seven `index_misses.jsonl` files (offline, seconds total) and
group them by cause into one cross-corpus table — zero GPU, no coordination with
the other agent, and it decides the fix ordering before a single `overrides.yaml`
is touched.