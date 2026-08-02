# STARTME — ScriptEngine script writing

> Read this file at the start of every session in which the user wants a script
> written. Then read `docs/SCRIPT_STYLE.md`. Then follow the workflow below.

## What this project is

ScriptEngine is a knowledge engine over Fandom wikis. It does **not** write
scripts — it serves ordered, cited research context over HTTP (`POST /context`
on `http://127.0.0.1:8000`). The AI (you) writes the scripts.

Six series are indexed:

| id | wiki | pages | prose sourced to a chapter |
|---|---|---|---|
| `jjk` | Jujutsu Kaisen | 987 | 55% |
| `hxh` | Hunterpedia | 2,014 | 50% |
| `csm` | Chainsaw Man | 537 | 42% |
| `bleach` | Bleach | 2,248 | 34% |
| `opm` | One-Punch Man | 1,565 | 31% |
| `berserk` | Berserk | 762 | 0% |

**Berserk is the exception worth knowing before you promise a script.** Its wiki
cites cover art and interviews rather than instalments, so its prose carries no
chapter numbers and a Berserk script cannot be tagged. Everything else can.

The fetched context already carries the writing contract: the house format, the
voice rules and the chapter/episode annotation rules are appended to every
rendered prompt from `scriptengine/api/rules.py`. `docs/SCRIPT_STYLE.md` is the
same contract with the reasoning and the samples attached.

## The three modes

`/context` answers in the shape the topic needs. `mode="auto"` (the default in
`script_writer.ps1`) picks between the first two by reading the topic.

| Mode | For | Returns |
|---|---|---|
| `narrative` | an account — "Shibuya Incident", "19 Days without Satoru Gojo" | beats in story order, each with the chapters and episodes it is sourced to |
| `roster` | a set — "Every Rank of Curse", "Every Apostle", "Every Level of the Abyss" | every member of the set the wiki declares, grouped and ordered, each with its facts and debut |
| `qa` | a question, not a script | the passages nearest the query |

Most published scripts are rosters. A topic starting "Every…", "All…", "Each…"
or naming ranks/levels/types is a roster; anything else is a narrative.

**Check what a series can enumerate before promising a topic.** Each series
declares the sets it maintains, and a declared set resolves the same way every
time:

```powershell
python -m scriptengine.cli rosters --series opm
```

47 sets are declared across the six series — devils, hunters, hybrids and fiends
on Chainsaw Man; apostles and the God Hand on Berserk; mysterious beings and
each hero class on One-Punch Man; the six Nen types, the Phantom Troupe and the
Zoldycks on Hunterpedia; espada, captains, hollows and quincy on Bleach; cursed
spirits, sorcerers and domain expansions on Jujutsu Kaisen. A topic outside the
list still works, it is just found by search rather than declared.

## The workflow (when the user says "start" or asks for a script)

1. Read this file and `docs/SCRIPT_STYLE.md`. Skim the samples in
   `sample scripts/` that match the requested topic's style.
2. Ask the user, in order:
   - **Topic** — what the script is about (e.g. "Shibuya Incident",
     "Every Rank of Curse").
   - **Series** — `jjk`, `hxh`, `csm`, `bleach`, `opm`, `berserk` or `db`
     (default `jjk`).
   - **Intro** — yes or no (the hook paragraph; see the style guide §3).
   - **Length** — target word count (default 3,000 words ≈ 18,000 chars).
3. Make sure ScriptEngine is running: `http://127.0.0.1:8000/health` should
   return `{"status":"ok",...}`. If not, start it:
   ```powershell
   python start_scriptengine.py        # repo root
   ```
4. Fetch the research context. Two ways:
   - **Headless (recommended, you drive it):**
     ```powershell
     powershell -ExecutionPolicy Bypass -File script_writer.ps1 `
       -Headless -Topic "Shibuya Incident" -Series jjk -Question "Shibuya Incident" `
       -Words 3000 -Intro true
     ```
     Add `-Mode roster` or `-Mode narrative` to override the automatic choice.
   - **Interactive:** run `script_writer.ps1` in a terminal and pick menu
     items by number (1 topic, 2 series, 3 question, 4 length, 5 intro,
     6 budget, 7 mode, 8 API).
   Either way the rendered research context lands in
   `scripts output/current_request.json`.
5. Read `scripts output/current_request.json` — it holds the settings, which
   mode answered (`resolved_mode`), the subject the engine resolved to, and the
   `"prompt"` field: the ordered, cited research context plus the writing rules.
   Check `subject` before writing: if the engine resolved the wrong page, fix the
   `-Question` rather than writing from the wrong material.
6. Write the script per `docs/SCRIPT_STYLE.md`:
   - Bold title line, optional intro hook, `* **Heading**` sections of long
     spoken paragraphs.
   - `VOICE_RULES` and `ANNOTATION_RULES` apply (style guide §5, §6).
   - Only facts in the context; never invent numbers or names.
   - Hit the target length — full treatment per section, no padding.
7. Save it into the production tree, not into the repo. Ask the engine where it
   goes rather than guessing, so a rewrite lands back in its own folder instead
   of opening a second one:

   ```powershell
   python -m scriptengine.cli script-path "Every Fight Mahoraga Has Ever Been In" --create
   # E:\Personal\Plot Works\Video 1 - Every Fight Mahoraga Has Ever Been In\Script\...
   ```

   Each video gets one numbered folder named after the script, and the script
   sits in its `Script/` subfolder beside that video's `Audio/`, `Images/`,
   `Prompt File/` and `storyboard/`. An existing folder with the same title is
   reused; a new title takes the next free number. The root is
   `SCRIPTENGINE_SCRIPTS_ROOT` in `.env`.

8. Verify the tags before calling it done. Every `(Chapter N, Episode M)` in the
   finished script has to exist in the crawl:

   ```powershell
   python -m scriptengine.cli verify "<path to the script>" --series jjk
   ```

## Where the chapter and episode on each block come from

Every beat and every roster member carries a `sourced:` line naming the
chapters and episodes its prose comes from, and the prose itself carries inline
`(Chapter N, Episode M)` locators. Both are computed by
`scriptengine/retrieve/citations.py`, which does two things:

- **Reads each reference as covering the sentences before it**, back to the
  previous reference. That is what placing a citation at the end of a paragraph
  means, and it takes the Shibuya Incident page from 12.8% of sentences carrying
  a locator to 99.6%.
- **Fills in the episode from the graph.** Half the wiki's references give a
  chapter and no episode; `Chapter N -anime episode-> Episode M` supplies the
  rest. A chapter the anime never adapted stays `(Chapter N)`.

So: tag every block with its `sourced:` chapters and episodes. Never write a
number that is not in the context, and never write a bare `[1]`-style marker
(the served prompt no longer contains any).

## Follow-ups

- **Toggle the intro** on an existing script: re-fetch with `-Intro false`
  (or the opposite) and rewrite only the title-adjacent part, keeping the
  sections and annotations.
- **Extend/rewrite:** re-fetch with a higher `-Words` (the script raises the
  context budget automatically), then rewrite the sections that need more
  material.
- **References form:** by default scripts carry inline `(Chapter N, Episode M)`
  tags. If the user wants the finished published form, convert the tags into
  per-section `*References:*` blocks (style guide §6).

## Quick reference

| Thing | Value |
|---|---|
| API | `POST http://127.0.0.1:8000/context` |
| Payload | `{"series","query","mode":"auto","token_budget","top_k","words","intro","as_prompt":true}` |
| Modes | `auto`, `narrative`, `roster`, `qa` |
| Series | `jjk`, `db`, `csm` |
| Context budget | auto = words × 8, clamped 6,000–60,000 |
| Request file | `scripts output/current_request.json` |
| Scripts | `scripts output/<Title>.md` |
| Style | `docs/SCRIPT_STYLE.md` |
| Rule blocks | `scriptengine/api/rules.py` |
| Samples | `sample scripts/` |
| Server | `python start_scriptengine.py` (repo root) |
