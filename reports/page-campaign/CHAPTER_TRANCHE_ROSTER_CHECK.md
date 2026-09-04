# Chapter Tranche — Roster / Closed-Set Check (guard #1)

**Status: PENDING.** Run before any chapter-tranche authoring. Precondition: the
`character_synopsis` wave (D1–D16) is closed. Created 2026-09-03 from the
"lose nothing" guard on the density switch (HANDOFF State 105): the switch from
per-1,000-word to per-section density must not silently drop coverage of
closed-set (enumeration) content, because span-recall is line-level and blind
to set-level answers.

## Why this check exists

On `character_synopsis`, guard #1 was verified N/A: all 835 roster/set
questions at switch time sat on `character`/`technique`/`event` pages (page-gen
698 + legacy 137), zero on synopsis pages, and synopsis pages carry no closed
sets. Chapter pages are the **first page type with their own closed-set
sections**, so the standing check must actually run here: confirm the
closed-set sections are covered — or explicitly waived — before authoring at
the new density.

## Inventory (2026-09-03, `series/jjk/facts.db`)

304 chapter pages. Non-empty L2/L3 sections = 1,706 (the ~1,689 prose-tranche
figure is this minus the 17 `Navigation` sections).

| family | instances | kind |
|---|---|---|
| `Summary` | 304 (~22 w) | narrative |
| `Plot Details` | 303 (~281 w) | narrative |
| `Trivia` | 22 (~25 w) | narrative |
| `4-Koma Bonus` | 6 (~66 w) | narrative |
| one-offs (`Yuko Ozawa`, `Uraume`, `The Miracle Generation`, `Taste Test`, `Panda`, `Pan`, `Nobara Kugisaki`, `Mei`, `References`) | ~9 | narrative |
| `Locations` / `Location` | 294 (~2 w) | **closed set** |
| `Jujutsu` | 276 (~12 w) | **closed set** |
| `Battles & Events` / `Battles and Events` | 254 (~4 w) | **closed set** |
| `Character(s) in Order of Appearance(s)` (4 title variants) | 221 (~8–17 w) | **closed set** |
| `Navigation` | 17 | skip |

≈ **1,045 closed-set sections** across the 304 pages. The prose rule
(1–2 questions per narrative section) is unaffected by this check; the check
governs only the list sections.

## Current coverage (2026-09-03)

- Question bank: **1,418 roster-mode** questions across 352 files (plus 55,106
  other-mode). Every roster-mode file targets a `character`/`technique`/
  `event`/arc page — **zero target the 304 chapter pages**.
- `questions/_jjk_page_volumes_chapters.json` (101 q's, 5 roster) targets the
  `Volumes & Chapters` hub page, not the chapter pages.
- `series/jjk/overrides.yaml` (`rosters:` key, line 95): 4 declared volume
  rosters ("Every chapter in Volume 0/1/25/30") — volume→chapter membership
  only, no chapter-internal lists.
- Roster-mode answers resolve from **declared members** (`scriptengine/retrieve/roster.py`,
  `load_rosters` / `_declared_members`, used by `eval/catalogue.py` and the
  harness membership scoring) — a chapter-internal roster question therefore
  needs its member list declared, not auto-read from section wikilinks, unless
  the resolver is extended.

**Conclusion: the ~1,045 chapter-internal closed-set sections are currently
uncovered at the set level.** (Their individual lines remain reachable —
span-recall tier 0 covers them — but "give me the full list of X in Chapter N"
has no set-level answer today.)

## The decision (make it here, before authoring)

Per closed-set family (or as a single package), choose:

- **A — author roster questions mechanically.** One roster-mode question per
  chapter page × family (~1,200 q's): "Which characters appear in Chapter N?"
  / "Which locations appear in Chapter N?" / "Which jujutsu techniques appear
  in Chapter N?" / "What battles and events happen in Chapter N?". Members =
  the section's wikilink list, generated mechanically, gated by the same
  verbatim/add gate as the prose wave. Cost: ~1,200 declared-member entries in
  `series/jjk/overrides.yaml` (or extend the roster resolver to read section
  links — a router/retrieval change, which then also needs the eval gates).
- **B — explicit waiver.** The chapter-internal lists are not prose; their
  members stay line-level reachable; set-level questions are out of scope for
  this pass. Record the waiver below with the per-family counts.
- **Hybrid allowed.** E.g. roster-author the two highest-signal families
  (Characters, Battles & Events) and waive `Locations`/`Jujutsu`.

## Gate

1. Write the decision + per-family counts into **RESULTS** below, and a
   HANDOFF state entry.
2. If any family is (A): author + gate-add the roster questions **first**
   (they are the harness-blind content), page-run a sample, then start the
   prose tranche at 1.5/section on the narrative sections only.
3. Re-run `python -m scriptengine.cli span-recall --series jjk` after any
   reindex; the two known `Chapter 239` / `References` lines remain the
   expected exit-2 misses.

## Open questions to resolve at run time

- Roster answer source: declared members vs auto-resolved from section
  wikilinks — confirm what the verifier actually reads before generating
  (see `scriptengine/retrieve/roster.py`, `scriptengine/eval/harness.py:222`).
- Family title variants: `Locations`/`Location`, `Battles & Events`/
  `Battles and Events`, and 4 `Character(s) in Order of Appearance(s)`
  spellings — roster question templates must key on the page's actual section
  title.
- `Jujutsu` family (276 instances): confirm what the list actually contains
  (techniques used in the chapter?) on a sample of section texts before
  writing its template.

## RESULTS

**Decision: Hybrid — roster `Characters in Order of Appearance` + `Battles &
Events`; waive `Locations` + `Jujutsu` — gated behind the `{{Scroll box
|content=}}` parser fix below (which lands first, and is worth doing regardless
of the roster choice).**

Count reconciliation: the reviewer addendum's **83** is correct. An independent
whole-page search for `{{scroll box|content=` returns 84, but that includes one
non-chapter page (`Ao no Sumika`, an episode page). Restricted to the 304 chapter
pages' `Characters in Order of Appearance` sections, the addendum's exact repro
returns `{'scroll_pop': 48, 'scroll_EMPTY': 83, 'plain_pop': 172}` — 83 empty,
confirmed. The 83 empty sections are exactly the named-`content=` form.

### The parser fix (PROPOSED — not applied; ingest code is execution-tier-forbidden)

**Root cause** (`scriptengine/ingest/wikitext.py`): the transparent-template
branch at line 920 builds its `candidates` list from `positional` **only**:

```python
elif lowered in TRANSPARENT_TEMPLATES:
    candidates = [p for p in positional if p and not p.startswith("[[Category")]
```

`parse_template` (line 379) routes a `|content=` argument into `named`, leaving
`positional` empty, so `candidates` is empty and the whole character list is
dropped. The positional form (`{{Scroll box| *[[A]] }}`) works because its
content is positional.

**Param census** (all `{{Scroll box}}` invocations in the JJK corpus): `content`
(95, the prose list) vs `height`/`width`/`name` (12/4/2, layout only). So the
fix must pull the named `content` value **specifically** — not every named
param, or a box's `height`/`name` would leak into prose. (Bare `{{Scroll}}` is a
different citation-shaped template, `chap`/`page`/`ep`, and carries no list —
excluded.)

**Proposed diff:**

1. New declaration next to `TRANSPARENT_TEMPLATES` (~line 223):

```python
# A transparent template's prose can sit in a *named* parameter, not only a
# positional one. Fandom's {{Scroll box}} takes its character list either
# positionally or as |content=; the named form left `positional` empty, so 83
# chapter "Characters in Order of Appearance" sections (~830 names) were
# dropped at index time. Only `content` is prose; the box's height/width/name
# are layout and stay out.
TRANSPARENT_NAMED_PARAMS: dict[str, set[str]] = {
    "scroll box": {"content"},
}
```

2. In the transparent branch, gather the declared prose named-params alongside
   the positional args:

```python
elif lowered in TRANSPARENT_TEMPLATES:
    named_prose = TRANSPARENT_NAMED_PARAMS.get(lowered, ())
    candidates = [p for p in positional if p and not p.startswith("[[Category")]
    candidates += [
        named[k] for k in sorted(named_prose & named.keys())
        if named[k] and not named[k].startswith("[[Category")
    ]
    if candidates:
        ...  # unchanged strategy select + _strip_templates(kept)
```

(Compile note: the comprehension is a single `[ ... ]` — it closes with the `]` on
its own last line, and the `)` after `"[[Category"` closes `startswith`. An
earlier draft added a stray `]` on the `startswith` line, which raised
`SyntaxError: unmatched ']'` on import; the form above is the corrected one.)

**Verification (run against the live parser, no ingest file touched):**
- Bug reproduced: named form → `positional=[]`, `named={'content': ...}` →
  current code keeps nothing.
- Proposed logic recovers all 9 names on `Chapter 59` (Megumi Fushiguro,
  Sukuna, Takeda, Tsumiki Fushiguro, Satoru Gojo, Nobara Kugisaki, Eso, Yuji
  Itadori, Kechizu).
- **Blast radius via scratch-copy diff** (patched copy imported under a second
  name, both parsers run over all 987 cached pages): **changed=91,
  added=979, removed=1, leaks=0.** The single removal is a **blank line on
  `Chapter 57`** replaced by six character names (content gain, not loss). The
  91 pages are a superset of the 83 empty chapter OOA sections — recovery also
  reaches `Aizo` (+47 names) and `Ao no Sumika` (+13), and every added line is a
  character name with zero `height`/`width`/`name` layout leaks.
- **Zero regression:** all **533** positional `{{Scroll box}}` boxes produce
  identical output before vs after (no named param, so nothing added).

**After approval (still not done):** apply the **corrected** diff →
**`index --series jjk` (no re-crawl — `index` re-parses the stored wikitext, so
it reproduces exactly this 91-page change and nothing else; a re-crawl would pull
today's wiki and move ~55k golds for unrelated reasons)** → `span-recall
--series jjk` (expect only the two known `Chapter 239 / References` exit-2
misses) → `pytest tests/ -q` + `eval --series jjk` (additive text can't
invalidate a verbatim gold but can shift chunk boundaries on the 91 pages —
confirm, don't assume). **Then** the Hybrid roster build (~550 declared-member
entries in `overrides.yaml` — also propose-and-approve) and the narrative
remainder (`Summary`, `Plot Details`) at 1.5/section.

---

## Reviewer addendum (2026-09-04) — two findings that change the options

Verified independently against `series/jjk/facts.db` and `series/jjk/wikitext/`.
Both are reproducible below. If your numbers disagree, yours win — say so and
stop.

### 1. `page-gen` cannot produce these rosters. Do not plan around it.

Dry-run of `generate_structured` (no files written) on three chapter pages —
`Chapter 0-1`, `Chapter 12`, `Bonus Manga`:

```
Chapter 0-1: 2 questions, 0 rosters  {'identity': 2}
   Q: What is the Japanese spelling of Chapter 0-1's name?  => '呪いの子'
   Q: What is the romaji of Chapter 0-1's name?             => 'Noroi no Ko'
   uncovered: ['Summary','Plot Details','Characters in Order of Appearance',
               'Locations','Battles & Events','Jujutsu','Color Spread']
```

`Chapter 12` has populated `Locations` and `Jujutsu` sections and still produced
**0 rosters**. No builder reads a chapter-shaped section list into a roster;
`_declared_battles` / `_declared_list` read declared members out of
`overrides.yaml`, which confirms this file's own resolver finding. This also
corrects an earlier version of this document, which recommended "run `page-gen`
across all 304 chapter pages" as the cheap mechanical path — that step does not
work and should not be attempted.

Reproduce (writes nothing):

```python
from scriptengine.config import get_settings, load_overrides, series_paths
from scriptengine.eval.page_gen import generate_structured
s = get_settings(); p = series_paths('jjk', s); ov = load_overrides(p)
r = generate_structured(p, "Chapter 12", ov, None, {})
print(len(r.questions), "questions,", len(r.rosters), "rosters")
print("uncovered:", (r.coverage or {}).get("uncovered"))
```

### 2. 83 of the 304 `Characters in Order of Appearance` sections are EMPTY

The inventory above counts 221 instances of this family as if all were
populated. They are not:

| | pages |
|---|---:|
| section populated | 220 |
| **section present but stored empty** | **83** |
| no such section | 1 |

No page carries two variants, so these are not duplicate headings — the content
is genuinely absent from the store. **Root cause, and it is exact:**

| wikitext form | pages | stored |
|---|---:|---|
| `{{Scroll box\| *[[A]] *[[B]] }}` (anonymous param) | 48 | parsed fine |
| `{{Scroll box \|content= *[[A]] *[[B]] }}` (named param) | **83** | **empty** |
| plain `*[[A]]` bullet list | 172 | parsed fine |

Perfect correlation: every empty section uses the `|content=` named-parameter
form, and no other form is ever empty. `Chapter 1` loses 9 named characters this
way (Megumi Fushiguro, Satoru Gojo, Yuji Itadori, Nobara Kugisaki, Sukuna,
Setsuko Sasaki, Takeshi Iguchi, Takagi, Wasuke Itadori). Across the 83 pages,
**~830 character names are absent from the corpus.**

This is standing open **"OOA (Scroll Box) non-blocking"** — recorded from a
single episode-page gold, where non-blocking was the right call. On the chapter
tranche it is 27% of the pages and it is not non-blocking.

Reproduce:

```python
import json, sqlite3, re
con = sqlite3.connect('series/jjk/facts.db'); con.row_factory = sqlite3.Row
tab = {}
for r in con.execute("SELECT d.title, LENGTH(COALESCE(s.text,'')) n "
                     "FROM documents d JOIN sections s ON s.document_id=d.id "
                     "WHERE d.page_type='chapter' AND s.breadcrumb LIKE '%Order%'"):
    d = json.load(open(f"series/jjk/wikitext/{r['title']}.json", encoding='utf-8'))
    txt = d if isinstance(d, str) else (d.get('wikitext') or d.get('text') or '')
    m = re.search(r'==+\s*Characters? in Order of Appearances?\s*==+\n(.*?)(?=\n==[^=]|\Z)',
                  txt, re.S | re.I)
    body = m.group(1) if m else ''
    key = ('scroll' if re.search(r'\{\{\s*scroll box', body, re.I) else 'plain')
    tab[f"{key}_{'EMPTY' if r['n'] == 0 else 'pop'}"] = \
        tab.get(f"{key}_{'EMPTY' if r['n'] == 0 else 'pop'}", 0) + 1
print(tab)   # expect {'plain_pop': 172, 'scroll_EMPTY': 83, 'scroll_pop': 48}
```

### What this does to the decision

Option **A** as written ("Members = the section's wikilink list") **cannot be
executed on 83 pages** — the wikilinks are not in the store. Authoring those
rosters from `wikitext/` instead would put gold answers into the bank that are
not verbatim substrings of indexed text, which breaks THE KEY RULE. Option **B**
(waiver) is defensible for `Locations` and `Jujutsu`, but applying it to the
Characters family would file a parser content-loss bug under a scope waiver.

Suggested order, and the first step is not a roster decision at all:

1. **Fix the `{{Scroll box |content=}}` parse and re-index the chapter pages.**
   This is `scriptengine/` ingest code — **forbidden to the execution tier**, so
   propose the fix and stop for approval; do not apply it. It is worth doing
   regardless of what is decided about rosters, because ~830 names are missing
   from the corpus itself, not merely untested. Re-run `span-recall --series jjk`
   after the re-index; expect the two known `Chapter 239 / References` misses and
   nothing else.
2. **Then** take the roster decision, with the Characters family actually
   present. Hybrid (Characters + `Battles & Events`; waive `Locations` +
   `Jujutsu`) is the reviewer's recommendation: `Locations` and `Jujutsu` are
   largely generic terminology links with low question value, while the other two
   are what a reader actually asks a chapter about.
3. **Then** the narrative remainder (`Summary`, `Plot Details`) at the
   section-based density.

Note for whichever roster option is chosen: because members resolve from
declarations, a per-chapter roster means ~550 (hybrid) or ~1,200 (full) entries
added to `series/jjk/overrides.yaml`, currently 308 KB. That file is on the
execution tier's forbidden list, so the roster build is a propose-and-approve
step too, not an autonomous one.

---

## Reviewer verification of the proposed parser fix (2026-09-04)

Independently reproduced by patching a **scratch copy** of
`scriptengine/ingest/wikitext.py` in `$CLAUDE_JOB_DIR/tmp/` and diffing
`strip_markup()` output against the live parser over all 987 cached wikitext
pages. The ingest file itself was not touched.

**The design is correct and I recommend approving it.** `scroll box` uses
strategy `"all"`, so positional and named `content` concatenate rather than one
shadowing the other; `TRANSPARENT_NAMED_PARAMS.get(lowered, ())` is safe because
`tuple & dict.keys()` is a valid set operation returning `[]`, so every other
transparent template is untouched.

| check | result |
|---|---|
| pages changed | **91** (matches the proposal exactly) |
| pages byte-identical | 896 |
| lines added | 979 |
| **lines removed** | **1 — and it is an empty string** (`Chapter 57`, a blank line replaced by 6 names). Zero content loss. |
| layout-param leaks (`height`/`width`/`px;`/`background:`) | **0** |
| existing tests pinning the current behaviour | **none** — `tests/test_templates.py:54` only asserts bare `{{Scroll box}}` with no params is furniture, which stays true (no positional, no `content` → no candidates → nothing emitted) |

Param census confirms the proposal's scoping: `{{scroll box}}` 633 uses, of which
`content` (95) is the only prose param against `height` (12) / `width` (4);
`{{scroll}}` 218 uses, **all positional** — it has no `content` param at all, so
excluding it is right.

Recovery is not chapter-only: `Aizo` gains 47 character names and
`Ao no Sumika` 13, alongside the 83 chapter OOA sections.

### Two corrections before this is applied

1. **The diff in RESULTS is a syntax error as written** — the list comprehension
   closes with `")]` and is then followed by a second `]`. Compiling it raises
   `SyntaxError: unmatched ']'`, which would break the ingest module on import,
   i.e. the entire pipeline. Apply this form (verified to compile and to produce
   the table above):

   ```python
   elif lowered in TRANSPARENT_TEMPLATES:
       named_prose = TRANSPARENT_NAMED_PARAMS.get(lowered, ())
       candidates = [p for p in positional if p and not p.startswith("[[Category")]
       candidates += [
           named[k] for k in sorted(named_prose & named.keys())
           if named[k] and not named[k].startswith("[[Category")
       ]
   ```

2. **Re-index; do not re-crawl.** The plan says "re-crawl/re-index chapter
   pages". A re-crawl pulls whatever the wiki says *today*, which can move
   content underneath ~55k existing gold answers for reasons unrelated to this
   fix. `index` parses the **stored** wikitext (this is the stated premise of
   `resolve-templates`), and the 91-page delta above was measured against that
   same cached wikitext — so a re-index alone reproduces exactly this change and
   nothing else. Re-crawl only as a separate, separately-gated decision.

`resolve-templates` was considered as a lower-risk alternative and does **not**
apply: it splices in `Template:`-namespace pages the crawler skips, whereas this
content is already inline in the page's own wikitext.

### After applying

Additive text cannot invalidate a verbatim gold answer, but it can move chunk
boundaries on the 91 changed pages, so run the gates rather than assuming:
`span-recall --series jjk` (expect only the two known `Chapter 239 / References`
misses), `pytest tests/ -q`, and `eval --series jjk`.
