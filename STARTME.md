# STARTME: ScriptEngine script writing

> Read this file at the start of every session in which the user wants a script
> written. Then read `docs/SCRIPT_STYLE.md`. Then follow the workflow below.

## What this project is

ScriptEngine is a knowledge engine over Fandom wikis. It does **not** write
scripts. It serves ordered, cited research context over HTTP (`POST /context`
on `http://127.0.0.1:8000`). The AI (you) writes the scripts.

Eight series are indexed:

| id | wiki | pages | prose sourced to a chapter |
|---|---|---|---|
| `jjk` | Jujutsu Kaisen | 987 | 55% |
| `hxh` | Hunterpedia | 2,018 | 50% |
| `csm` | Chainsaw Man | 537 | 42% |
| `bleach` | Bleach | 2,252 | 34% |
| `opm` | One-Punch Man | 1,571 | 30% |
| `db` | Dragon Ball | 7,205 | 4% |
| `onepiece` | One Piece | 7,613 | 0% |
| `berserk` | Berserk | 762 | 0% |

**Two series are the exceptions worth knowing before you promise a script.**
Berserk's wiki cites cover art and interviews rather than instalments, so its
prose carries no chapter numbers and a Berserk script cannot be tagged. One Piece
footnotes nothing inline either (0%), but it writes one page per chapter and
episode, so a claim retrieved from the page titled "Chapter 1015" is sourced to
Chapter 1015: sourceable by route two rather than route one. Everything else can
be tagged by at least one route.

The fetched context already carries the writing contract: the house format, the
voice rules and the chapter/episode annotation rules are appended to every
rendered prompt from `scriptengine/api/rules.py`. `docs/SCRIPT_STYLE.md` is the
same contract with the reasoning and the samples attached.

## The three modes

`/context` answers in the shape the topic needs. `mode="auto"` (the default in
`script_writer.ps1`) picks between the first two by reading the topic.

| Mode | For | Returns |
|---|---|---|
| `narrative` | an account: "Shibuya Incident", "19 Days without Satoru Gojo" | beats in story order, each with the chapters and episodes it is sourced to |
| `roster` | a set: "Every Rank of Curse", "Every Apostle", "Every Level of the Abyss" | every member of the set the wiki declares, grouped and ordered, each with its facts and debut |
| `qa` | a question, not a script | the passages nearest the query |

Most published scripts are rosters. A topic starting "Every…", "All…", "Each…"
or naming ranks/levels/types is a roster; anything else is a narrative.

A roster also answers **a fighter's whole fight list**. "Every Fight Mahoraga Has
Ever Been In" (and its question-worded twins, "Who did Mahoraga fight?") come back
as one section per battle page the wiki has for that fighter, each labelled with
their role: a direct combatant, or a tool some side deployed. The sides are read
from this wiki's own infobox vocabulary, so it works on any series that files its
fights as pages.

**Check what a series can enumerate before promising a topic.** Each series
declares the sets it maintains, and a declared set resolves the same way every
time:

```powershell
python -m scriptengine.cli rosters --series opm     # one series' sets
python -m scriptengine.cli catalogue                # every series, regenerated
```

`docs/CATALOGUE.md` is the answer to "what is in the engine": pages, typing,
how much of each wiki's prose can carry a chapter, and every declared set with
its size. It is generated, so run it rather than trusting the copy on disk.

1,545 sets are declared across the eight series: devils, hunters, hybrids and
fiends on Chainsaw Man; apostles, pseudo-apostles and the God Hand on Berserk;
mysterious beings and each hero class on One-Punch Man; the six Nen types, the
Phantom Troupe and the Zoldycks on Hunterpedia; espada, quincy and all thirteen
Gotei divisions on Bleach; cursed spirits, sorcerers, domain expansions and a
battles-in set for every major fighter on Jujutsu Kaisen (1,355 sets in total —
the per-page rosters the chapter/episode tranche declared);
races, transformations and films on Dragon Ball; races, Devil Fruit types and the
Marine rank ladder on One Piece. A topic outside the list still works, it is just
found by search rather than declared.

**A set that comes back is not automatically the right set.** Enumeration
returns the best-scoring candidate on the wiki, so a topic the wiki does not
keep as a set can still come back as a populated list. Every roster bundle
therefore carries `confidence`, and **read it before writing**:

| `confidence` | means | do |
|---|---|---|
| `declared` | the series declares this set by name | trust it |
| `exact` | every word of the set's name was asked for | trust it, check the count |
| `partial` | the set is narrower than the topic; `unmatched` names the extra word | **stop**, usually the wrong set |
| `weak` | nothing in the topic matched the set's name | **stop**, almost certainly wrong |

`warning` spells it out in words. "Every Straw Hat Pirate" returns 14 members,
`partial`, *"Straw Hat Pirates' Creations is narrower than the topic: creations
was not asked for"*. Those are the crew's weapons, not the crew.

`confidence` cannot see an **incomplete** set, so still check the count against
what you expect: `Every island in the Grand Line` reports `exact` and returns
four, and there are hundreds. `docs/RETRIEVAL_SCENARIOS.md` has the full list.

**Members are validated against the topic before you see them.** A category is
what the wiki keeps, not what was asked for. `Transformations` holds Black
Frieza because it *is* one, so each candidate is checked against the topic's
constraints and what fails comes back in `rejected` with a reason:

```
Every Saiyan transformation   candidates 160 → 75 kept
  - Black Frieza   not saiyan
  - Class-up       outside the story (Game: Dragon Ball Heroes)
```

`scope` is **canon by default**: manga, anime and film. Game and spin-off
entries are still in the store and return when the topic asks: "every
transformation **ever**", "**including games**". Nothing is ever deleted.

Ability pages the wiki's own fields cannot settle are classified once at index
time by a local model (`cli classify --series <name>`) and the answer is stored,
so retrieval still just reads a table. That is what keeps Spirit Bomb Super
Saiyan out of the Saiyan forms (*"granted externally by absorbing a Spirit
Bomb"*) while keeping Great Ape, which needs a full moon but only works on a
Saiyan.

**A race set means what only that race can reach**, not what a member of it has
used. Kaio-ken is out of "Every Saiyan transformation" because King Kai invented
it and Krillin knows it; Ultra Ego is in, because Vegeta is its only user. Each
member carries how it is acquired (`race_exclusive`, `character_specific`,
`teachable` or `unknown`), computed from users and inventors, so a second race
learning something reclassifies it on its own.

If validation would empty a set it is skipped instead, so a list is never blank
because a wiki labels its fields unusually.

## The workflow (when the user says "start" or asks for a script)

**There is also a one-shot path.** If you just want the engine to fetch, write,
verify and save in a single call, use `script-gen` instead of steps 4–8:

```powershell
python -m scriptengine.cli script-gen "Every Fight Mahoraga Has Ever Been In" --series jjk --words 6000
```

It routes the topic to a mode, fetches the bundle, asks the writer model for the
script, checks every chapter/episode tag against the raw crawl (repairing any
that fail), and expands or trims until it lands within 500 words of `--words`,
then saves into the production tree. An agent host can do the same thing through
the MCP tools (`research`, `verify_script`, `script_path`) without the HTTP server.
The manual steps below keep a human in the seat on every section and are still
the right choice when you want to shape each part by hand.

1. Read this file and `docs/SCRIPT_STYLE.md`. Skim the samples in
   `sample scripts/` that match the requested topic's style.
2. Ask the user, in order:
   - **Topic**: what the script is about (e.g. "Shibuya Incident",
     "Every Rank of Curse").
    - **Series**: `jjk`, `hxh`, `csm`, `bleach`, `opm`, `db`, `onepiece` or
      `berserk` (default `jjk`).
   - **Intro**: yes or no (the hook paragraph; see the style guide §3).
   - **Length**: target word count (default 3,000 words ≈ 18,000 chars).
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
5. Read `scripts output/current_request.json`. It holds the settings, which
   mode answered (`resolved_mode`), the subject the engine resolved to, and the
   `"prompt"` field: the ordered, cited research context plus the writing rules.
   Check `subject` before writing: if the engine resolved the wrong page, fix the
   `-Question` rather than writing from the wrong material.
6. Write the script per `docs/SCRIPT_STYLE.md`:
   - Bold title line, optional intro hook, `* **Heading**` sections of long
     spoken paragraphs.
   - `VOICE_RULES` and `ANNOTATION_RULES` apply (style guide §5, §6).
    - Only facts in the context; never invent numbers or names.
    - Land inside the length band: target ± 500 words, reached by giving every
      section full treatment with real specifics, not padding. `script-gen`
      enforces this automatically (expanding and trimming until it is in band);
      when writing by hand, count before you finish.
    - The bold title line is the saved filename. Keep it a clean name for the
      topic; if the engine resolves the subject to something longer than the
      video's title, save under the title, not the resolved page name.
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

## Sourcing a script you did not write here

When the user brings a finished script that has no tags, do not re-derive them
by hand and do not rewrite the script to fit the sources:

```powershell
python -m scriptengine.cli cite "<path to the script>" --series jjk
```

It reads each block, retrieves against the index, and appends the locator the
retrieved passages agree on. It never changes a word. It checks that itself
before writing, and refuses if the cited text does not reduce back to the input
exactly. The result is written to `<name> (cited).md` beside the original, which
is left untouched, so the two can be diffed.

Blocks it leaves alone are blocks where the evidence disagreed. That is the
correct outcome, not a gap to fill in by hand.

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
| Series | `jjk`, `db`, `onepiece`, `bleach`, `hxh`, `opm`, `berserk`, `csm` |
| What each can answer | `docs/CATALOGUE.md`, regenerate with `cli catalogue` |
| Known wrong answers | `docs/RETRIEVAL_SCENARIOS.md` |
| Context budget | auto = words × 8, clamped 6,000–60,000 |
| Request file | `scripts output/current_request.json` |
| Scripts | `scripts output/<Title>.md` |
| Style | `docs/SCRIPT_STYLE.md` |
| Rule blocks | `scriptengine/api/rules.py` |
| Samples | `sample scripts/` |
| Server | `python start_scriptengine.py` (repo root) |

**The server holds its code in memory.** Retrieval fixes do not reach a running
server. A live one was still answering "Every race in Dragon Ball" with 150
episode titles hours after that was fixed on disk. Restart it after any change
under `scriptengine/`.

A series' `overrides.yaml` is the exception: it is read from disk on every
request, so a newly declared set answers immediately without a restart.
