# FLAWLESS LABELING — plan to drive event labels to 1.0 R / 1.0 P (2026-10-04)

Owner (2026-10-04 ~23:5x): "fix everything for ALL the windows, not just the 34
that all 3 models missed. We should have enough examples or guidelines so that
we don't miss anything at all or label wrong things. Make a robust plan, then
run only the ninfer 35B as the drafter — its intelligence can be increased to
reach 1.0/1.0/1.0. Take all 5 improvement points into the plan; it will serve
the 4B training as well. We just need enough guidelines."

The same guideline + example bank that makes the 35B drafter flawless is the
definition of every training label the 4B learns: one fix, both consumers.

## 0. Where we stand (blind JJK passage test gold, 100 passages, 173 core events)

| run | R | P | F1 | note |
|---|---|---|---|---|
| teacher (stored rows) | 0.601 | 0.755 | 0.669 | baseline |
| CyberTiel 35B draft | 0.699 | 0.842 | 0.764 | 3 windows failed |
| ninfer 27B @150k draft | 0.757 | 0.873 | 0.811 | 1 failed |
| ninfer 35B draft | 0.642 | 0.762 | 0.697 | 0 failed, ~3.5x faster |
| CyberTiel + 35B verifier | 0.676 | 0.948 | 0.789 | FP 31 -> 8 |
| union of the 3 drafts | 0.798 | 0.744 | 0.770 | recall ceiling of today's prompts |

34 core events are missed by ALL three drafters. Sampled causes: implicit
phrasing ("had to face" = fought, "cuts down his daughter" = fought, "take Megumi
and Maki away" = saved, "Shoko arrives ... asks Gojo" = met), and gold rows that
are judgment calls ("freezes everyone" = sealed?). The gold is quote-less and was
annotated on old 4,000-char slices, so part of today's "error" is the gold's.

## 1. The measurement rules (so 1.0 means something)

- **Never tune on the test.** Prompt/guideline/example work uses a DEV set
  only: the verified gen-2 gold (gold600 + pilot, kept/reexpressed, quoted —
  `series/jjk/training/student/{train,dev}.jsonl` windows, ~1,950) plus, as they
  are verified, the universal pools' labels. The blind test gold (100 passages)
  is scored only at the end of each round, reported, never inspected for fixes
  after gold v5 is frozen.
- **Match rule** = `tools/eval_extraction.py` (names share a 3+ letter word,
  fought/met symmetric, quote overlap for window-level gold).
- **A round** = run the drafter on the dev set -> taxonomy of every FN and FP
  (§3) -> fix the guideline / examples / prompt (§4-6) -> re-run. A fix is kept
  only if dev F1 does not drop on any verb (per-verb regression check).
- **Stop rule:** dev R = P = 1.0 on two consecutive rounds, or two rounds with
  < 0.5 point gain (then the residual list goes to the owner as the honest
  ceiling with its causes).

## 2. Point 1 — settle the gold (gold v5, Claude adjudicates)

1. **Test gold v5:** for all 100 passages, Claude adjudicates passage-only under
   the guideline every gold core/optional row AND every row any of the 6 runs
   proposed that the gold lacks (the union of disagreements), writing each
   event with its verbatim QUOTE and window id, plus a one-line reason. Output
   `recall_gold_v3/gold_test_v5.json` (window-level, quoted) + an adjudication
   log; report the gold error rate (rows the old gold had wrong / missed).
   Frozen once written; fixes after that go to dev only.
2. **Dev gold audit:** the same adjudication on every dev window where the
   35B's draft disagrees with the verified label (FN or FP), so the dev labels
   the guideline is tuned against are themselves right.

## 2b. Gold v5 — built 2026-10-05 (and what it means for the test)

`tools/train/build_gold_v5.py` -> `series/jjk/training/gold_v5/gold_test_v5.jsonl`:
258 windows (11 partial windows excluded: only their read part was
adjudicated), 266 core + 5 optional events, 132 earned empties, every quote
verbatim (hard failure otherwise). Adjudication log with every reason, model
FP/FN and taxonomy class: `gold_v5/decisions_001.jsonl` (100 units).

Re-scored on gold v5 (window-level, quote overlap required):

| run | R | P | F1 |
|---|---|---|---|
| CyberTiel draft / + 35B verify | 0.605 / 0.541 | 0.837 / 0.936 | 0.702 / 0.686 |
| ninfer 27B draft / + 35B verify | 0.665 / 0.583 | 0.886 / 0.951 | 0.760 / 0.723 |
| ninfer 35B draft / + 35B verify | 0.526 / 0.477 | 0.761 / 0.921 | 0.622 / 0.628 |
| union of the 3 drafts | 0.763 | 0.753 | 0.758 |

The row-stamping verifier now LOSES F1 (it rejects true rows on the fuller
gold) — exactly why the verifier must be as thorough as the drafter and add
rows, not only strike them (section 6b).

**Honesty rule:** Claude read every test window while adjudicating, so gold v5
is now DEV, not test. Guideline v2 + the example bank are tuned on it; once
they are frozen, Claude adjudicates a FRESH, never-seen 100-window JJK test
(holdout pages, blind to model output, same method) and the final numbers are
reported only on that.

## 3. The error taxonomy (every FN and FP gets exactly one class)

| class | example |
|---|---|
| IMPLICIT-VERB | "had to face", "cuts down", "clash", "take X away" (saved), "freezes" |
| DIRECTION / PASSIVE | "Y lost to X", "was killed by" |
| ATTEMPT / PLAN / HYPOTHETICAL / NEGATION | "tries to kill", "plans to seal", "would have died" |
| CLASS-VS-NAME / TECHNIQUE-AS-END | species, groups, techniques, domains as ends |
| PRONOUN / CONTEXT (antecedent outside window) | "he" with the page subject |
| VERB CONFUSION | fought vs defeated vs killed, met vs fought, captured vs sealed |
| DUPLICATE / SYMMETRY | two rows for one fight/meeting |
| MOVEMENT OBJECT | arrived/departed object must be a named place/group |
| GOLD WRONG | the gold row is not stated / the model row is right |
| OTHER | named in the log, becomes a new class if it recurs |

## 4. Point 2 — guideline v2 (universal, explicit, with negatives)

Append `## G. Guideline v2` to `plan/EVENT_ANNOTATION_GUIDELINE.md` (append-only):
- per verb: the **YES phrasings** (including every implicit form found in §3 —
  "face/confront in battle/clash/cut down/strike" = fought when an exchange
  happens; "take X away from danger/pull X out" = saved; "freeze/imprison" =
  captured unless the wiki calls it sealing) and the **NO phrasings** (attempt,
  plan, threat, hypothetical, flashback-only mention, negation), each with one
  passage-shaped example;
- the decision order when two verbs fit (killed > defeated > fought; captured
  vs sealed; met only when no more specific verb);
- the entity rules (F.2) with examples from several wikis (JJK, Marvel, MCU,
  an anime wiki), never JJK-only wording;
- context rule: the page title is the default antecedent of "he/she" on a
  character page; otherwise an unresolved pronoun is NOT an end.

## 5. Point 3 — the example bank (few-shot, from DEV only)

`plan/event_examples.jsonl`: 40-60 curated (window, gold rows, one-line why)
examples covering every taxonomy class and every verb, positives AND hard
negatives (earned empties with tempting verbs), across wikis as pools get
labeled. Built from dev windows only (never the test). Rendered into the
drafter prompt (and, if measured to help, into the verifier prompt).

## 6. Point 4 — the ninfer 35B drafter, made smarter (levers, each measured on dev)

1. prompt = production system prompt + guideline v2 + example bank;
2. thinking budget: effort high vs medium (the 35B is fast: ~9 min / 269 windows);
3. **missed-event pass**: a second call per window — "here are the rows already
   listed; list ONLY events the passage states that are not listed" — targeted
   at the IMPLICIT-VERB patterns (recall lever);
4. self-consistency: k=3 samples, keep rows that appear in >= 2 (precision) or
   the union + verifier (recall) — whichever dev says;
5. **the 35B verifier** row by row with the wiki card (measured tonight: FP 31 ->
   8 on CyberTiel's draft at -4 hits) — rows it rejects are re-checked against
   the guideline before deletion when the reject reason is "not stated";
6. per-verb checklist pass for the weak verbs (met, arrived, captured, escaped).
The combination with the best dev F1 (no per-verb regression) becomes the
production drafter; speed is recorded for every lever.

## 6b. Owner-approved method (2026-10-05 ~00:1x) — how the guideline is APPLIED

Better than piling rules into one prompt:
1. **Show, don't tell.** Worked examples teach meaning ("intercepts the
   finishing blow" protects someone -> saved). Per window, RETRIEVE the k bank
   examples closest to the window's own wording (BM25/embedding over the
   example bank) instead of one static list.
2. **Decompose.** For every event-like sentence the 35B answers, in order: is
   an action stated as DONE (not attempted / planned / hypothetical / negated)?
   who does it, to whom? which verb (decision order)? — the "what does this
   sentence mean" pass, run by the 35B itself.
3. **Mechanical checks, no model** (`tools/train/row_checks.py`): every end
   resolves (store aliases/nodes) to a character / group / creature page, never
   a technique / item / class page; an `arrived`/`departed` object resolves to a
   place or group page; the quote is verbatim AND inside the window's READ part;
   group objects are split into one row each; `awakened` has a null object and
   no other verb does; JSON schema with the verb enum enforced at decoding.
4. **Recall:** a separate missed-event pass, plus 2 samples keeping what agrees.

**The verifier is as thorough as the drafter (owner):** it does not stamp rows.
Per window it (a) re-reads the WHOLE window sentence by sentence with the same
decomposition, (b) checks every drafted row against the guideline + the
retrieved examples + the wiki card (each end's page type / status) + the
mechanical checks, (c) runs its own missed-event pass and proposes additions,
and (d) only then declares the window verified, with a reason per row and per
addition. Long, explicit checks are the point; speed comes from the 35B's
~500 tok/s, never from skipping a check. The ninfer 35B runs at full context
(`serve_35b.sh`: --max-context 262144, kv-capacity auto = 2 lanes x 262,144).

## 7. Point 5 — manual inline verification + the residual measurement

- Training labels: the drafter output -> MANUAL inline verification in opencode
  (one window at a time, exact pages, per-pool log; owner's protocol) -> Claude
  audits ~5% + every hard case; > 3% disagreement stops the run.
- Residual: Claude re-annotates a random 5% of finished windows BLIND; the
  disagreement rate is the dataset's measured error — the number that says how
  close to flawless the training labels are.

## 8. How this serves the 4B

- The 4B learns exactly these labels (guideline v2 + examples define them).
- The production system prompt (`events.system_prompt`) may gain the guideline
  v2 rules only through a gated engine change (PROMPT_VERSION bump + the four
  standing gates); the student is then trained on that same prompt.
- The example bank doubles as a curated high-weight training slice.

## 9. Schedule (GPU single-tenant; swaps take ~1 min)

1. now: finish the 6-way measurement (35B verifier on the 27B + 35B drafts).
2. Claude: gold v5 adjudication + dev taxonomy (CPU) — while the GPU runs the
   4B Stage A sweep on today's verified set (pipeline + hyper-parameter
   selection transfer to the final labels).
3. Round 1: 35B drafter + guideline v2 + examples on dev -> taxonomy -> fixes.
4. Rounds 2..n until the stop rule; then the frozen test v5 score.
5. Label the universal pools with the winning drafter; inline verification;
   retrain the 4B on the verified universal set.

## 10. Round log (dev = gold v5.x, window match + wiki alias resolution)

| round | change | R | P | F1 |
|---|---|---|---|---|
| r1 | guideline v2 + retrieved examples + decomposition + missed pass | .757 | .963 | .848 |
| r2 | missed-pass v2 (trigger checklist) + verifier v2 | .761 | .972 | .854 |
| r3 | 2 samples + verifier v3 (drop only with a cited code) | .831 | .946 | .885 |
| r4 | MEET / FIGHT / OUTCOME family passes + 2-vote verifier | .879 | .942 | .909 |
| r4 replay | gold v5.3 (W20 amend) + scorer article strip + zero-loss checks (2026-10-05) | .879 | .953 | .915 |
| r5 | + numbered-sentence pass with the hinted G.1 rows beside each sentence | .896 | .959 | .926 |
| r6v | verifier only, on r5's stored drafts: mechanical checks BEFORE the verifier, rows both samples wrote skip it, plural-crowd ends, self-row drop, name-subset dedup | .917 | .970 | .943 |
| r7 | + G.5 (tense never removes an event; one sentence, several events) in the guideline, METHOD and sentence pass | running | | |

Gold versions: v5.4 = the entry-rule consistency sweep (all 37 gold windows
with entry wording read; "an entry to people not already present = met even
when a fight follows", precedents W82/W97/Ch149/W20/W31; +5 core, +4
optional); v5.5 = W55 "jumping up on debris to eliminate her" demoted to
optional (capability frame + purpose clause), two G.2-valid alternate-name
rows added as optional (neutral, never recall). r5 and r6v are scored on
v5.5; r1-r4 on the gold of their day. Every amendment is logged in
`gold_v5/decisions_00{2,3,4}.jsonl` with its reason — and because dev gold
moves with Claude's reading, only the blind test (gold_v6_blind) gives the
reportable number.

**Noise:** the two draft samples differ run to run (r4 sample1 205 hits, r5
193); a single full run moves ~1-2 pt by sampling alone. r6v isolates the
verifier change by replaying r5's stored drafts (`--reverify`), so its +1.5
pt is not sampling noise. Rows written by BOTH samples were 182 true / 1
false in r5.

**Offline rule replay** (`tools/train/replay_rules.py`, no GPU): a candidate
no-model rule is kept only at ZERO true-row losses on dev. Kept (now in
`check_rows`): bare capability modal ("Nue can strike repeatedly"; a negated
modal or one beside a past-tense report stays); `defeated` without a defeat
lexeme -> `fought` ("Sukuna overpowers Megumi"). Rejected: "arrived/departed
place must appear in the quote" — gold takes the place from the window
("Mahito was here but he already left" -> departed B5F). Bug found by the
replay: `check_rows` dropped "the curse" as a class although G.2 allows a
singular anaphoric description — pre-verify recall +0.8 pt after the fix.

**r4 residual (33 FN):** 25 never drafted — mostly phrasings G.1 already lists
(the rule was in the prompt but not applied to that sentence; r5's lever) — and
8 struck by the verifier. Gold rows re-checked against G.1 and kept: "arrive
in Shibuya where Yuji notices Panda" (arrival to people = met), "finds ... asks
how old they are" (finds + contact = met), "lure the girl into disengaging her
technique" (technique used on someone = fought), "bisects her father's head"
(no stated death = fought; the window never names Ogi, so the end is "her
father").
