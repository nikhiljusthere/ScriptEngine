# NEW SESSION PROMPT — volume loop handoff (2026-08-31)

Paste everything below the line into the new session.

---

You are taking over the JJK character prose pass (the "volume loop") in the
ScriptEngine repo at `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

**Read first, in this order:**
1. `reports/page-campaign/OPENCODE_PROMPT_VOLUME.md` — the full handoff:
   environment setup, the 7-step per-character loop, the error playbook
   (every error class we've hit and exactly how each is fixed), the quality
   bar, the recheck protocol, and the ops reference (server restart, health
   checks, exact commands).
2. `reports/page-campaign/HANDOFF_PROSE_PASS.md` — the method, the
   per-character table (house style for your rows), the open G-n list, and
   the state updates (SU1–SU10).

**State (2026-08-31):**
- **25 of 132** new characters are done. Resume at **`order[36]` = next character** (`reports/page-campaign/jjk_character_order.json`), then continue in order until told to stop.
- G15 (the chunker's 20-word section floor) is FIXED + gated; the jjk index
  was rebuilt (19,497 chunks) and short sections are now indexable — you
  should not hit chunker-floor failures.
- All gates green on the current code: pytest **1072**, eval jjk **24/24**,
  canon-run opm **8/16, 235/237, 78.5% — no change** (report
  `reports/2026-08-31-0924`), pyright **0 errors**. The live server runs the
  current code (start 2026-08-31T09:19:25Z, cuda, 8 series, port 8000).
- The repo is type-clean. A lone "fastmcp could not be resolved" editor
  squiggle is an environment artifact (fastmcp IS installed in the venv) —
  ignore it, never "fix" that import.

**Rules (non-negotiable; details in the plan doc §3–§5):**
- One character at a time, in order. You are the only agent working.
- No engine-code edits during volume. If you find an engine-level gap,
  record a G-n with evidence (question id, routed basis, absent words,
  one-line root cause) and **checkpoint the user** — fixes happen as gated
  releases (named regression test → audit → index → gate triple + pyright 0
  → server restart + freshness → re-verify affected batches).
- Never rephrase to dodge a natural-question failure. Every answer is a
  verbatim substring of the wiki prose (the served kanji-including form for
  Nihongo lines — see the plan doc §5.2 precedents). Retires only for
  cross-page facts or unstated counterfactuals, each with a reason.
- Every `prose:` failure is classified with triage evidence before the
  character closes. Documented-open closes are only for the G14 family with
  triage evidence (Kamo precedent: 91/93 with two recorded).
- Pre-existing page-gen failures: classify, document, leave as-is.
- Write the per-character row in the HANDOFF table (and bump the count)
  before starting the next character.
- Keep a todo list updated as you work.
- No git commits.

**Checkpoint the user on:** a new G-n / engine-level finding (defer or fix
as a release), any gate movement, a missing batch file (a character that was
never page-generated), or before starting any page-type wave (episodes /
battles / techniques — plan doc §8).