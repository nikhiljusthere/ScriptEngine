# Council brief — the "fact layer": stop losing plot facts in the event windows (2026-10-07)

You are the opencode agent (ninfer 27B, :18080) in the worktree
`/home/goblin/ScriptEngine/.claude/worktrees/big-review-flags` (branch `big-review-flags`).
Claude (the reviewing agent) wrote this brief on the owner's instruction and will VERIFY every
step you complete. Do the steps in order and STOP where it says STOP.

## Your task, step 1 of the programme: run an LLM council (sequential, one agent at a time)

Use the `llm-council` skill (in ~/.config/opencode/skills/llm-council). Project convention
(CLAUDE.md, owner rule 2026-09-08): **5 advisors one at a time, then 5 peer reviewers one at a
time, then the chairman — never in parallel**; each sub-agent starts with a fresh context and
never sees another's answer (the peer reviewers see the anonymised advisor answers, as the skill
specifies). Give every advisor this whole brief (sections A-F below) as the question.

The council question: **"What is the best way to make the event-labelled windows a COMPLETE,
verifiable record of every fact the wiki text states (the owner's 'complete MCU brain'), fix every
window already labelled and reviewed, and keep the result flawless and checkable — given the
proposal in section D? Accept, amend, or replace each part of the proposal; name what is missing;
give the order of work and how each step is verified."**

Write the full council record (each advisor's answer, each peer review, the chairman's verdict,
and a final numbered implementation plan with a verification check per step) to
`plan/FACT_LAYER_COUNCIL.md`, commit it with an explicit pathspec
(`git commit -- plan/FACT_LAYER_COUNCIL.md`), then **STOP and wait**. Do not write or change any
other code until Claude has verified the council record and tells you which step to implement.

## A. The owner's words (verbatim, in order)

1. (asked after reading pattern A71 in plan/BIG_REVIEW_PATTERNS.md)
   > also I want you to stop here now. Don't continue any more verifications. Just tell me that this
   > line "| A71 | training sparring between allies ("tasked with training Scott Lang ... he punched
   > van Dyne") written as fought | no row (practice, not a conflict) | table: fought NO
   > playful/friendly contact | rare |" will this event not be recorded at all? are we loosing some
   > context here in the final MCU brain that we are trying to achieve? is this a cause of our only
   > 12 verbs rule?

2. > "Lost: a structured fact that Hope trained Scott, and that he's her student. A brain answering
   > "who trained Ant-Man?" or reasoning about their relationship can't get that from the event
   > rows": so we are loosing crucial details about the plot, I don't want that, I want a complete
   > MCU brain. What can we do to fix this and all the previous windows as well. Each line
   > constitues to some fact whether it is crucial to the larger narrative or not, but it is there
   > for a reason because it was either in a movie/series or manga/comic. Tell me a way in which we
   > can fix all of these things.

3. > Yep, i understand the cost, but it is necessary. Cover everything you have stated here as a
   > fix. I want you to stop ninfer 35B. load 27B model and tell it to do everything (write code or
   > fix things) you just plan and verify after it completed each step. First make it run an llm
   > council on this to verify the best way to get this right. Tell the council everything from my
   > prompt to what you proposed as a fix. sequential council one by one, in opencode, in a new
   > terminal. Now

4. Standing owner rules from the same day (binding, from plan/WINDOW_METHOD.md):
   > Also record this to be the best way to make and verify the windows (remove all previous
   > methods of making windows), but add an explicit rule that only claude can add new rules for
   > now and only claude can update the two files.
   (the two files = `tools/train/big_flags.py` and `plan/BIG_REVIEW_PATTERNS.md`). So: you (the 27B)
   may write other code; any change to those two files, and any new labelling rule, is PROPOSED to
   Claude, who decides and applies it.

## B. Claude's answer to message 1 (verbatim)

> Yes, under A71 that sparring session gets no event row, and yes, it's a direct consequence of the
> 12-verb rule. Why: the inventory is fought, defeated, killed, captured, escaped, saved, betrayed,
> sealed, met, arrived, departed, awakened — all adversarial or plot-moving acts. None of them means
> "trained", "mentored", or "sparred". The only candidate is fought, and the procedure defines
> fought as an attack in a conflict (its NO column excludes friendly/playful contact). Writing
> "Scott Lang fought van Dyne" would tell the structured layer they clashed as opponents, which
> would mislead exactly the reasoning the brain is for (enemies, match-ups, "who would win"). So
> the review chose to drop the event rather than record a false one.
> Are we losing context? Not the text — the sentence stays in the indexed wiki corpus, so retrieval
> can still find and cite "Hope trained Scott and they sparred." What's lost is a structured fact:
> there's no event row saying Hope trained Scott, or that he's her student. A brain answering "who
> trained Ant-Man?" or reasoning about their relationship can't get that from the event rows.
> It's not just A71. The same schema limit drops other relationship facts the review correctly
> discarded under the current rules: R4/R12 (joining a team, allying), A67 (calls/holograms/remote
> appearances), R23 (helped), A36 (defending someone in words). Each was right under the 12 verbs,
> but together they mean the event layer captures conflict and movement well and relationships
> poorly.

## C. The current system (what exists today)

- Procedure (the 35B's system prompt and the gold's definition): `plan/EXTRACTION_PROCEDURE.md` —
  12 verbs, a "did it happen?" test that DROPS plans/claims/hypotheticals/orders/dreams, ends must
  be named characters/named groups (never crowds/species/items), places only for
  arrived/departed/escaped, groups expanded to named members, one name per person.
- Rulings R1-R25: `plan/BIG_REVIEW_HANDOFF.md`; error catalog A1-A72 + gate quirks:
  `plan/BIG_REVIEW_PATTERNS.md` (Claude-only file).
- THE window method: `plan/WINDOW_METHOD.md` — 35B single pass (`tools/train/label_single.py`) with
  review-derived hints (`tools/train/label_hints.py`) + one flag-driven repair turn
  (`tools/train/big_flags.py` check()), then Claude reviews every window (`big_flags.py`,
  `big_mkfix.py`, `big_review.py --fix/--mark`, `big_consistency.py`). Measured on 96 reviewed
  windows (`tools/train/eval_hints.py`): plain .535 F1 -> hints+repair .629 (P .769, R .532).
- Data (main checkout, gitignored): 14,000 Marvel/MCU windows `series/{marvel,mcu}/training/labels/
  big_in.jsonl`; 35B labels `series/universal/training/big/labels.jsonl` (5,405 written; labelling
  paused now); Claude's corrections `series/universal/training/big/big_audit.jsonl` (latest per id
  wins); review cursor 806 (`review_cursor.txt`) — b7-b806 reviewed, ~70% needed correction.
- What the review deliberately dropped (each is now a fact the owner wants kept): sparring/training
  (A71), joining/allying/teaming up (R4/R12/A31/A48), calls and remote appearances (A67), "helped"
  (R23), verbal defence (A36), plans/attempts/orders/claims/hypotheticals/dreams (step 3,
  A19/A23/A35/A60/A64), hedged events ("seemingly", A11), group rows once members are named (G.2),
  codename/disguise identities collapsed to one name (R10), description places ("his apartment",
  vehicles, organisations as places: A10/A24/A65), crowds/species/indefinites (R11/A5/A52/A57),
  behind-the-scenes / trivia / real people.
- Downstream: a Qwen3.5-9B student is to be trained on the reviewed 12-verb windows
  (`tools/train/compose_big_set.py --reviewed`); the ScriptEngine engine (SQLite facts/graph/FTS,
  Qdrant) indexes the full wiki text, so sentences remain retrievable; the "brain" goal is
  `franchise_kit/RUNBOOK_100.md` §0 / `plan/MARVEL_100_PLAN.md` (every line understood, recallable,
  traceable, plus grounded reasoning).
- Constraints: GPU-only (CUDA); one model on the 32 GB card at a time (27B now on :18080); kill
  processes by exact PID only; switchpoint entry in plan/SWITCHPOINT.md before any model switch;
  commit with explicit pathspecs only; never commit the owner's files (plan/JJK_VERIFY_7000_*.md,
  tools/train/verify_monitor.py, owner hunks in verify_row_wiki.py / qwen_worker.py,
  tools/train/infer.py, the `D series/{berserk,bleach,db,hxh,onepiece}/overrides.yaml` deletions).

## D. Claude's proposed fix (verbatim)

> Yes — the current setup loses facts, and you're right to want that fixed. The root cause is that
> the event layer was built as a **filter** (keep only 12 conflict/movement verbs, drop everything
> uncertain). A complete brain needs the opposite: a **coverage** guarantee — every narrated line
> produces a fact, or an explicit reason why not. Here's how I'd fix it, including the windows
> already done.
>
> ### 1. Keep the 12 verbs; add a second "fact" layer beside them
> Don't stretch `fought`/`met` to absorb everything — that would corrupt the clean conflict data
> the 9B and match-up reasoning rely on. Instead every window gets two kinds of rows:
> - **Event rows (unchanged):** the 12 verbs, as now.
> - **Fact rows (new):** `subject | relation | object | qualifiers | quote`, with the relation from
>   a controlled but much wider vocabulary:
>   - relationships: trained/mentored, recruited, allied with, joined/left (team), member of,
>     dated/married, parent/child, friend, rival
>   - interaction: helped/assisted, protected (non-lethal), contacted/called, warned,
>     persuaded/tricked, ordered, hired
>   - possession/creation: created/built, gave, stole, used (item), destroyed (object/place)
>   - identity: alias of / codename of / revealed as, posed as
>   - state/change: gained power, lost power, transformed, became (role/title), resides at
>   - knowledge: learned, revealed (secret), discovered
>   - plus an open `other` relation with a free-text verb, so nothing is ever forced into silence
>     (recurring `other` verbs get promoted into the vocabulary)
>
> ### 2. Turn "drop it" into "keep it with a label"
> | today (dropped) | fact layer (kept) |
> |---|---|
> | plans, attempts, orders, claims, lies, dreams, hypotheticals (step 3) | `modality: planned / attempted / ordered / claimed / dreamed / hypothetical` |
> | hedged deaths ("seemingly killed") | killed with `certainty: apparent` |
> | group with named members → members only | members' rows **plus** `X member of Group` |
> | codename ↔ real name, disguise reveals (R10) | `Valkyrie alias of / revealed as Enchantress` |
> | description places ("his apartment", "the Bus") | `location` qualifier |
> | sparring, calls, joining, helping (A71, A67, R4, R23) | `trained`, `contacted`, `joined`, `helped` facts |
> | behind-the-scenes, trivia, cast lists | separate **production** fact type — kept, not mixed into plot |
>
> ### 3. Make "complete" checkable: sentence coverage
> "Every line is a fact" has to be verifiable or "flawless" means nothing. New mechanical gate:
> every narrative sentence must be covered by ≥1 event or fact row, or carry an explicit tag
> (dialogue, list header, …). This is the flagger's MISS? cue turned into a hard requirement;
> uncovered sentences get reported per window, so recall becomes measurable, not a judgment call.
>
> ### 4. Fix all previous windows
> Nothing is lost at the source — every window's text is stored, and the 12-verb rows already
> reviewed (b7–b806) stay valid as a subset of the new schema. Repairing the past is an
> **add-only pass**:
> 1. For the 806 reviewed windows: the 35B gets the window + the final reviewed rows and is asked
>    only for the missing fact rows and qualifiers. Claude's corrections log records many drop
>    decisions (R4, A67, A71, …) with reasons, which helps target that pass. Claude reviews only
>    the additions — far cheaper than re-reviewing everything.
> 2. For the rest of the 14k (labelled or still running): the same add-only pass after the event
>    rows, then the same review.
> 3. Beyond the 14k: the same procedure applies to every narrative section of every Marvel/MCU
>    page, since the brain is the whole corpus, not just the training sample.
>
> ### 5. Order of work
> 1. Decide the schema once, before reviewing further, so nothing gets reviewed twice — write
>    schema v2 (fact vocabulary, qualifiers, coverage rule, worked examples), using the windows
>    already seen as test cases (Hope/Scott sparring, the Invaders joining, the podcast call).
> 2. Measure it on ~50 reviewed windows with the same eval tooling (precision/recall of facts +
>    coverage rate).
> 3. Then run the add-only pass and resume the review under the expanded rules; the pattern
>    catalog and flagger get a facts section (still Claude-only, per the owner's rule).
> 4. Training: the 9B can keep training on the 12-verb events now; the fact layer feeds the brain
>    directly and can become a second training target later.
> Cost, honestly: probably 2–3× more rows per window, so review takes longer per window; the
> add-only design and the coverage check keep that bounded and measurable. The labeller can keep
> running: its 12-verb output stays valid and gets extended later, not redone.

## E. What the owner decided after reading D

Message 3 above: cost accepted ("it is necessary"); cover EVERYTHING in D as the fix; the 27B
implements every step (code and fixes), Claude verifies after each step; first this council.
(Claude stopped the 35B labelling — labels kept, resumable — and loaded the 27B at 262k.)

## F. What the council must decide (minimum)

1. Two layers (12-verb events + fact layer) vs. one widened inventory vs. something else — and why,
   given the 9B training set and the brain's reasoning needs.
2. The fact schema: relation vocabulary (closed list + `other`), qualifiers (modality, certainty,
   location, time, source/production), how aliases/memberships/items/places are represented, and
   how the existing gate (verbatim quote, end checks) extends to facts.
3. The coverage rule: what counts as a sentence/clause, what may be tagged instead of covered,
   and how the check is implemented and measured.
4. Repair of the past: the add-only pass over b7-b806 and the other labelled windows; whether the
   35B, the 27B, or which model drafts it; how Claude's review is kept tractable and complete.
5. The order of work, the verification for each step (what Claude checks, which numbers on which
   reviewed windows), stop/rollback criteria, and what stays unchanged (the 12-verb gold, the 9B
   plan, the owner rules above).
