# OPENCODE PROMPT — Release R5 (counterfactual + subject-ranking), then resume volume

Paste everything below the line into opencode.

---

You are continuing the JJK page campaign in `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

**Read first, in this order:**
1. `reports/page-campaign/R1_ENGINE_RELEASE/REPORT.md` — what shipped last release and what it left open.
2. `reports/page-campaign/PLAN_NEXT_PHASE.md` — the analysis, the root-cause framing, the ordered work queue.
3. `reports/page-campaign/HANDOFF_PROSE_PASS.md` — the method, gates, commands (§4), server procedure (§10 step 2), ENGINE GAPS, State update 6.

R1+R2 was verified independently: `pytest` 1059/1059 and `eval --series jjk` 24/24 both reproduced, the CJK fix is clean corpus-wide (0 mojibake, `mei_mei` 32/32 with `冥冥`), and all five `run.json` artifacts match the reported scores. Good work. This release closes what R1 deliberately deferred.

## CONCURRENCY RULE (applies to everything below)

**Run only ONE subagent at a time.** The single exception: when the work is an eval, a server run, a `page-run`, or anything else that produces **one result output**, you may run **two agents in parallel**. Never more than two, and never two agents that are both authoring or both editing engine code.

## Standing rules (unchanged, non-negotiable)
- Never reword a question to dodge a failure. Fix the engine.
- Every answer stays a verbatim substring of the wiki text.
- Every engine change ships with a named regression test (`TestPandaGaps` / `TestGetoGaps` house style).
- Do not commit unless explicitly asked.

## Environment
```powershell
$env:PYTHONPATH="E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
$env:PYTHONIOENCODING="utf-8"
$py = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe"
```
PowerShell 5.1: `;` not `&&`. Inline `python -c` breaks on quotes — write temp `.py` files. `>` writes UTF-16 — write files from Python.

---

## R5-a — G9b, the negated conditional / counterfactual (router)

**This is now the largest open class, not a curiosity.** The R3 probe batch proved it spans **7 of the 21 completed characters** (Yuji, Yuta, Choso, Toji, Naoya, Toge, Shoko), plus the `shoko_ieiri` `020` miss. Every remaining character page has natural counterfactual facts, so leaving it open means all 125 remaining characters will author counterfactuals that fail and need re-runs. Fix it before the volume resumes.

Failing shapes, from the R3 table:
```
What happened to Ijichi and Ino if they had not been treated by Shoko?
What would Yuji have become if he had not become a sorcerer?
What would have happened if Yuta had not pretended to kill Yuji?
What would have happened to Megumi if Toji had not committed suicide to protect him?
What would have happened if Naoya's domain had been able to detect Maki?
What would have happened if Maki had not taken over the battle against Hanami?
What would have happened if Shoko had not sutured Gojo's body for Yuta?
```
All route `narrative`, where the factual sentence is never served.

**The discriminator is the conditional clause, not the head verb.** A counterfactual carries an `if` clause in past perfect (`if X had (not) …`, `if X hadn't …`, `if X were not …`) and/or a `would have` / `would `+ past participle main clause. The eval gold row that must stay narrative — `What happened to Nanami during the Shibuya Incident?` — has no conditional clause at all, so the two separate cleanly. Build the discriminator on the clause, and route the hypothetical form to `qa` while the past-factual form keeps its narrative read.

Regression tests: `TestShokoGaps::test_the_negated_conditional_stays_narrative` currently asserts the OPEN behaviour — **invert it** and add the other six R3 shapes. Keep an explicit test that the Nanami eval row stays narrative, and one that a plain past account (`What happened to Gojo during the Shibuya Incident?`) stays narrative.

**Highest regression risk in the campaign so far.** If `canon-run --series opm` drops, narrow the branch (e.g. require both the `if` clause *and* a resolvable non-story subject) and re-gate rather than loosening the guard.

## R5-b — G12, possessive subject-ranking (new gap, open it in the handoff)

R1 reported G8d as closing to `qa` without the hint. That is mode-only. Verified on the shipped code:

```
Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?
  hint=None          mode=qa   subj=Jujutsu Sorcerer      <- wrong page
  hint=Suguru Geto   mode=qa   subj=Suguru Geto
```

`_subject()` takes the organization `Jujutsu Sorcerer` off the possessive "a weaker **sorcerer's** barrier" even though the sentence names Suguru Geto outright as the agent. `page-run` passes because the scorer sends the hint; a bare user query lands on the wrong page focus, which the NORTH STAR does not allow.

Fix in `_subject()` / `subject_ranking`: a possessive that is the **topic** of the question must keep winning (`What is Sukuna's Domain Expansion?`), but a possessive buried inside a prepositional object must not outrank an entity named as the question's agent. **`tests/test_router.py::test_a_possessive_names_the_subject` asserts the topic case — it must keep passing.** Add a G12 regression for the object case.

Open **G11** stays untouched this release (retrieval-quality, G5/R4 family). Do not attempt it here.

## R5-c — clear the standing LSP diagnostics

The editor reports LSP errors across this repo continuously while you work, and they have been ignored long enough that real problems are now hidden in the noise. Clear them.

**Run this as its own sequential pass — after R5-a/R5-b are gated and the three re-runs pass, before the report.** Not as a parallel agent: it touches the same engine files R5 edits, and the concurrency rule forbids two agents editing engine code.

Method:
1. **Enumerate first, fix second.** Collect the full diagnostic list from your LSP across `scriptengine/` and `tests/` and write it down before changing anything, grouped by rule/code with a count each. The distribution tells you what is one systemic issue versus what is fifty separate ones.
2. **Fix causes, not symptoms.** A blanket `# type: ignore` / `# noqa` is not a fix. Where a suppression is genuinely correct (a dynamic import, a third-party stub gap), make it specific to the rule and add a one-line comment saying why — the repo's comment style already explains *why*, not *what*.
3. **Behaviour must not change.** This is a diagnostics pass, not a refactor. Do not rename public functions, reorder routing rules, change default arguments, or "clean up" logic you find on the way. If a diagnostic points at a genuine latent bug (an unreachable branch, a shadowed name, a wrong type that would fail at runtime), **do not silently fix it** — fix it, and call it out separately in the report as a found defect, because that is a campaign finding, not a lint fix.
4. **Re-gate after.** `pytest tests/ -q` (>= 1059), `eval --series jjk` 24/24, `canon-run --series opm` at baseline. A diagnostics pass that moves any of those three has changed behaviour and must be narrowed.
5. If the diagnostics are dominated by missing type stubs or a checker misconfiguration rather than by real defects, say so and fix the configuration instead of annotating hundreds of call sites. Report the count you cleared and the count you deliberately left, with the reason.

---

## Gate (all three, before any server restart)
```powershell
& $py -m pytest tests/ -q                            # expect >= 1059
& $py -m scriptengine.cli eval --series jjk          # expect 24/24
& $py -m scriptengine.cli canon-run --series opm     # expect baseline: 8/16 exact, 235/237 canon, 78.5%
```

## Verify (restart the server per handoff §10 step 2, then)
```powershell
& $py -m scriptengine.cli page-run --series jjk --batch shoko_ieiri   # expect 34/34 (G9b was the sole miss)
& $py -m scriptengine.cli page-run --series jjk --batch suguru_geto   # expect 94/94 unchanged
& $py -m scriptengine.cli page-run --series jjk --batch probe_r3      # expect 124/126 (the 2 remaining = G11)
```
If a number comes back short, triage with `prose_triage.py <slug> "<Name>"` and root-cause it. Never rephrase to dodge.

---

## Parallel work — no GPU, no engine edits (use the concurrency rule)

These two produce one result output each, so they may run as the second parallel agent while an eval or page-run is in flight.

### P1 — `retire_ledger.json`
339 retires sit inside 48 batch files with nothing linking a retire to the page that owes the answer, so the techniques pass (149 pages) cannot know what it is supposed to absorb. Scan the batches and write `reports/page-campaign/retire_ledger.json`, one row per retire:
```json
{"batch": "...", "id": "...", "question": "...", "reason": "...", "owed_by_page": "...", "absorbed": false}
```
Infer `owed_by_page` from the retire reason where it names a page (e.g. Mahito `108` → `Black Flash`); leave it `null` and flag the row where it does not. Each later page-type pass flips `absorbed` to `true` when it authors the owning question, and the final sweep asserts zero unabsorbed cross-page retires.

### P2 — episode-template study
Characters are the least uniform and most expensive page type. Episodes (59), chapters (304) and volumes (35) are highly templated, and the 304-chapter block is only affordable if the per-page cost drops. Study the section shapes of ~6 episode pages in `series/jjk/wikitext/`, then write `reports/page-campaign/episode_prose_template.md`: which sections are factual vs. dialogue/roster, what the uncovered-section dump looks like for an episode, and where the character template's assumptions break. **Study and template only — do not author episode questions in this run.**

---

## Report — write this before starting the volume

Write `reports/page-campaign/R5_COUNTERFACTUAL/REPORT.md`:
- what changed, file by file, with line references and repo comment style;
- before/after route for all 8 counterfactual shapes plus the two narrative controls (Nanami eval row, plain past account), in-process probe table;
- before/after subject resolution for the G12 possessive case, with and without the hint;
- the three gate results verbatim;
- the three re-run scores;
- **R5-c**: the diagnostic counts before and after, grouped by rule; any genuine defect the diagnostics exposed, called out separately; anything deliberately left, with the reason; and confirmation the gate triple is unmoved;
- anything still OPEN (G11, G5/R4, `toge_inumaki` 051), one-line fix plan each.

Update `HANDOFF_PROSE_PASS.md`: mark G9b FIXED + gated (or record why it did not close), add **G12** with its outcome, add **State update 7**, refresh §9 gate status.

---

## Then: resume the character volume

After the report is written, resume the 132-character pass at `jjk_character_order.json` `order[21]` = **Tengen**, then `order[22]` = **Hanami**, then Mai Zenin `order[23]`, Kinji Hakari `order[24]`, … on the same FAST loop (`prose_dump.py` → author verbatim triples → `prose_bulk_add.py` → `page-run` → `prose_triage.py` on any `prose:` failure → fix the root cause). Run until told to stop, honouring the concurrency rule above.

**Two additions to the per-character loop, both cheap:**

1. **Author the adversarial forms inline.** R3 proved the bank was self-selecting toward wh-shapes (9 yes/no in 21,521 questions). For every character from Tengen on, include at least one yes/no, one comparative, and one counterfactual among its authored questions, against facts on that character's own page. That keeps the corpus honest instead of needing another retro-fit probe batch later.
2. **Authoring lint before `page-run`.** Reject a question whose answer string appears inside the question text (`024` on Mei Mei: "What degree of control … making her a master?" → "cursed energy control"), reject a wh-word that is not at the front (`030`: "Mei Mei uses Black Bird Manipulation to imbue crows with what …?"), and require a numeric answer for a "how many" question (`018` answered with names). These pass the scorer and still fail the NORTH STAR.

Checkpoint with the user on any engine-level finding (a new G-n), not per character.
