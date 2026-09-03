# OPENCODE PROMPT — Release R1 (engine gap closure)

Paste everything below the line into opencode.

---

You are continuing the JJK page campaign in `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

**Read first, in this order:**
1. `reports/page-campaign/PLAN_NEXT_PHASE.md` — the analysis and the root causes. This is your spec.
2. `reports/page-campaign/HANDOFF_PROSE_PASS.md` — the method, the gates, the commands (§4), the server procedure (§10 step 2), and the ENGINE GAPS section.

**Your task is Release R1 + R2 only.** Do NOT author new character pages in this run. Stop after the report.

## Standing rules (non-negotiable, from the handoff's METHOD CORRECTION)
- Never reword a question to dodge a failure. Fix the engine.
- Every answer must stay a verbatim substring of the wiki text.
- Every engine change ships with a named regression test, modelled on `TestPandaGaps`.
- Do not commit unless explicitly asked.

## Environment
```powershell
$env:PYTHONPATH="E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
$env:PYTHONIOENCODING="utf-8"
$py = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe"
```
PowerShell 5.1: use `;` not `&&`. Inline `python -c` breaks on quotes — write temp `.py` files. `>` writes UTF-16 — write files from Python.

## Work items

### R1-a — yes/no interrogatives (`scriptengine/retrieve/router.py`, `_is_interrogative`, ~L96)
`_is_interrogative` recognises wh-words only, so auxiliary-fronted questions fall through to the narrative default. Verified in-process today:
```
interrog=False  Was Suguru Geto dependent on his curses in battle?          (G8a)
interrog=False  Can Suguru Geto cast Curtain over a weaker sorcerer's barrier?  (G8d)
interrog=False  Does Shoko have an innate cursed technique?                 (G9a)
interrog=False  Can Shoko teach someone how to use reverse cursed technique?  (G9c)
interrog=False  Is it easier for Shoko to heal herself or others?           (G9d)
```
Add an aux-fronted branch (`is/are/was/were/do/does/did/can/could/will/would/has/have/had/should/may/might/must`). Guard it so a yes/no question with a *story* verb at the head stays narrative (`Did Sukuna kill Nanami?` is an account, not a lookup). Reuse the existing `_NARRATIVE_VERBS` / `_EFFECT_ON` machinery rather than inventing a parallel one.

### R1-b — thread `subject` into the router (highest leverage)
`scriptengine/api/main.py:204` calls `route(paths, request.query)`. `request.subject` (the page the question was authored against — the scorer sends it, the G3a fix) is passed only to `build_context` at `:213`, and inside `scriptengine/api/context.py` only the **qa** path uses it (`:154`, `:336`). So the mode decision is blind to the authored page.

Add `subject: str | None = None` to `route()` and pass `request.subject` from `main.py:204`. When an explicit subject is supplied and its type is **not** a story type, it takes precedence over `_subject()`'s inference for the mode decision. Keep it a *precedence* rule, not a hard override, and keep the wide search intact — same shape as the G3a recall fix.

This is what fixes:
- **G8b** `What was the true goal of the Night Parade of a Hundred Demons?` — currently routes narrative because the subject resolves to the *event*, and the Geto page is never considered.
- **G8d** — currently `_subject()` resolves **`Jujutsu Sorcerer` (organization)** off the possessive "a weaker **sorcerer's** barrier" instead of Suguru Geto. Confirm this with a route probe before and after.

### R1-c — `wants_chronology` word boundaries (`scriptengine/retrieve/chronology.py:589`)
```python
if any(word in lowered for word in ("in order", "chronolog", "timeline", "sequence")):
```
This substring-matches **"sequence" inside "con-sequence-s"**, so G8c (`Under what condition can Suguru Geto absorb a curse with no consequences?`) routes to a 0-beat roster with the reason "asks for the story in order". Fix with word boundaries — e.g. `\b(in order|chronolog\w*|timeline|sequences?)\b`. Latent corpus-wide for `consequence(s)`, `consequently`, `subsequent`; one live hit today (`jjk-pg-suguru_geto-073`).

### R1-d — partial-confidence roster guard
Extend the G6 guard (`_resolves_a_set`, ~L430) to the *partial-confidence / "did not narrow"* roster case, so a question like G8c cannot walk a roster that renders nothing. Belt-and-braces behind R1-c.

### R2 — G10, CJK encoding (independent of the router work)
The stored kanji answer for `mei_mei` Q001 is garbled bytes (UTF-8 read as cp1252 in the batch-writing path), so the scorer's word-boundary match can never succeed and the question was retired. Fix the batch **write path** (`ensure_ascii=False`, verified `utf-8-sig` round-trip on write), correct the stored answer, un-retire Q001, and add a CJK round-trip regression test. Verify `norm()` preserves kanji end-to-end.

### G9b — DO NOT ATTEMPT in this release
`What happened to Ijichi and Ino if they had not been treated by Shoko?` is deliberately narrative: the past "what happened to" form guards the eval gold row `What happened to Nanami during the Shibuya Incident?`. It needs a negated-conditional discriminator and carries the highest regression risk. Leave it OPEN and documented.

## Gate (all three must pass before the server restart)
```powershell
& $py -m pytest tests/ -q                      # expect >= 1046 passing
& $py -m scriptengine.cli eval --series jjk    # expect 24/24
& $py -m scriptengine.cli canon-run --series opm   # expect baseline: 8/16 exact, 235/237 canon, 78.5% precision
```
If `canon-run --series opm` drops below baseline, R1-a is over-claiming: narrow the yes/no branch to questions whose subject is a character/thing rather than an event, and re-gate.

## Verify (after gates pass, restart the server per handoff §10 step 2)
Kill stale `scriptengine.api.main` processes first (uv-cache python children show an empty command line — match by parent/PID), start with `SCRIPTENGINE_MODEL_IDLE_UNLOAD_SECONDS=3600`, confirm `curl http://127.0.0.1:8000/health` returns 200, device `cuda`, all 8 series. The page-run stale guard rejects a server started before your edit.

Then:
```powershell
& $py -m scriptengine.cli page-run --series jjk --batch suguru_geto   # expect 94/94
& $py -m scriptengine.cli page-run --series jjk --batch shoko_ieiri   # expect 34/34
& $py -m scriptengine.cli page-run --series jjk --batch mei_mei       # expect 32/32 after the un-retire
& $py -m scriptengine.cli page-run --series jjk --batch toge_inumaki  # expect 84/86 UNCHANGED (its 2 are retrieval, not routing)
```
Whole re-run bill is about two minutes of GPU. If a number comes back short, triage with `prose_triage.py <slug> "<Name>"` (the faithful scorer replica: `mode=auto`, `token_budget=60000`, `norm()`, word-boundary) and root-cause it — do not rephrase.

## Then: R3 adversarial probe batch
The corpus has only **9 yes/no questions out of 21,521 (0.04 %)**. The question bank has been self-selecting toward wh-forms the router already handles, which is why five of the eight open gaps appeared the moment Shoko and Geto were authored naturally. Before more volume, prove the fix generalises.

Build a **separate probe batch** (not inside the page batches, so a failure surfaces a gap without blocking any page's exit 0). For each of the 21 characters already done, author ~6 questions against facts already proven to be on that page, one per form:

1. yes/no — `Does/Is/Can/Was …?`
2. comparative — `Is X easier than Y …?`
3. negated conditional — `What would have happened if X had not …?`
4. scope-phrase — `… in battle`, `… during the Shibuya Incident`
5. event-name scope — `… of the Night Parade of a Hundred Demons`
6. possessive-noun bait — `a weaker sorcerer's barrier` (the G8d subject trap)

Score it (~2 minutes). Every failure gets a root cause and a G-n number in the handoff's ENGINE GAPS section — the same treatment as G8/G9. Do not fix newly found classes in this run unless the fix is a one-liner of the same family; document them for the next release.

## Report — write this before you stop
Write `reports/page-campaign/R1_ENGINE_RELEASE/REPORT.md` covering:
- what changed, file by file, with line references and the reasoning comment style the repo already uses;
- the before/after route for all 8 gap questions (in-process probes, table form);
- the three gate results verbatim;
- the four re-run scores;
- the R3 probe batch: total, passed, failed, and a root-caused table of every failure with a proposed G-n;
- anything left OPEN (G9b, G5/R4, plus whatever R3 surfaced), with a one-line fix plan each.

Then update `reports/page-campaign/HANDOFF_PROSE_PASS.md`: mark G8a–d, G9a/c/d and G10 as FIXED + gated (or record why one did not close), add a **State update 6**, and set the exact resume pointer — `jjk_character_order.json` `order[21]` = **Tengen**, `order[22]` = **Hanami** (0-based).

**Stop there and report back. Do not start the 125-character volume in this run.**
