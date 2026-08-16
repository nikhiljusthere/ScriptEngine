# Extraction audits

An audit answers one question: **did the extractor actually understand this
wiki, or did it just produce output?**

The distinction matters because a broken extractor is silent. The previous
pipeline's section detector never once matched a heading. It looked for a bare
`appearance` while the corpus contained `## Appearance`, and it reported no
error. Every document collapsed into a single unnamed section and the pipeline
carried on. That is the failure mode audits exist to catch.

```powershell
python -m scriptengine.cli audit --series jjk --sample 50
```

Writes `series/<name>/audit/report.json` and prints a summary.

## What it reports

### Coverage

| Metric | Healthy | What a bad number means |
|---|---|---|
| Pages typed | ≥95% | The infobox template map missed templates this wiki uses |
| Infobox parsed | ≥95% of typed pages | The wikitext parser is failing on this wiki's syntax |
| Sections captured | >1 per page | Section extraction is broken: the exact bug that killed the old pipeline |
| Facts per page | 10–40 for characters | Near zero means infoboxes are being read but not converted |
| Citations extracted | >0 on prose pages | `{{Ref}}` variants unhandled; citation text will leak into chunks |

### Sourcing

What a script can actually put a chapter and episode on. Measured the way
`/context` measures it, through `scriptengine/retrieve/citations.py`, so the
number is the one the writer will see rather than a count of `{{Ref}}` templates
that may not have survived extraction.

| Metric | Healthy | What a bad number means |
|---|---|---|
| Cited directly | >5% | The wiki's references are not reaching the prose at all |
| Sentences w/ chapter | ≥25% corpus-wide, ~99% on a narrative page | References are being captured and then dropped downstream |
| Sentences w/ episode | close to the chapter figure | The chapter/episode map is empty; check the `anime episode` and `adapted from` edges |
| Chapters mapped to episodes | most adapted chapters | Episode pages were skipped by the crawl, or their infobox changed |

The gap between "cited directly" and "sentences w/ chapter" is the inheritance:
a reference covers the sentences before it. On Jujutsu Kaisen that is 14.6%
against 54.7% corpus-wide, and 12.7% against 99.6% on the Shibuya Incident page,
reference lists, episode tables and trivia sections carry no citations and never
will, which is why the corpus-wide threshold is low.

This exists because the failure already happened once: `{{Ref|chap=143}}` became
a structured `Citation` and then vanished from every downstream text, so scripts
had nothing to cite and no number moved.

### Graph integrity

| Metric | Healthy | What a bad number means |
|---|---|---|
| Edges resolved | ≥90% | Wikilink targets are not matching crawled page titles, usually redirects |
| Dangling edges | <10% | Links point outside the crawl. Some is normal; a lot means an incomplete crawl |
| Orphan nodes | low | Entities appear in no relationship: extraction produced isolated names |

### Rejections

Every page the extractor declined, with a reason. **Read this list.** It is where
both kinds of error surface: real content wrongly discarded, and junk wrongly
kept.

The old corpus contained `LICENSES.chromium.txt`, `angular.txt`, `tslib.txt` and
a `test.txt` that the crawler itself wrote on every run: Angular and Chromium
documentation, embedded and indexed alongside Jujutsu Kaisen.

## Reading a report

```jsonc
{
  "series": "jjk",
  "sampled": 50,
  "types": {"character": 31, "technique": 8, "battle": 6, "arc": 3, "unknown": 2},
  "coverage": {
    "typed": 0.96,
    "with_infobox": 0.97,
    "mean_sections": 7.4,
    "mean_facts": 22.1,
    "citations": 1840
  },
  "sourcing": {
    "sentences": 48752,
    "chapter_episode_map": 181,
    "cited_directly": 0.146,
    "with_chapter": 0.547,
    "with_episode": 0.389
  },
  "graph": {"edges": 1204, "resolved": 0.93, "dangling": 84, "orphans": 11},
  "rejected": [
    {"page": "File:Todo.png", "reason": "non-content namespace"}
  ],
  "warnings": [
    {"page": "Angel", "issue": "infobox template not in discovered vocabulary"}
  ]
}
```

The single most important line is `mean_sections`. If it is at or near 1, section
extraction has failed and nothing downstream is trustworthy: chunks will have no
section metadata, parent expansion will return whole documents, and retrieval
will degrade in a way that looks like a model problem rather than a parsing one.

## Fixing what an audit finds

Work in this order:

1. **Unknown page types** → the infobox vocabulary missed a template. Check
   whether it exists in the `Template:` namespace under a different name.
2. **Dangling edges** → usually redirects. The crawler follows `redirects=1`, but
   a link to an uncrawled page stays dangling; widen the crawl or accept it.
3. **Low section counts** → the section tree comes from the API, so this means
   the API response was not consumed. A parser bug, not a wiki quirk.
4. **Wrongly rejected pages** → adjust `skip_categories` in
   `series/<name>/overrides.yaml`. Not in Python. See
   [ADDING_A_SERIES.md](ADDING_A_SERIES.md).
5. **Low sourcing** → the wiki cites but the locators are not reaching the
   prose. Check `wikitext._citation_marker` against this wiki's `{{Ref}}`
   parameter names, and `collect_ref_definitions` if its references are defined
   once and reused by name.

Re-run the audit after each change. Iterate until the numbers stop improving,
then index the full corpus.

## Audit before you index

Indexing is the expensive step, since embedding runs over every chunk. Auditing 50
pages takes seconds and catches the failures that would otherwise surface as
inexplicably poor answers hours later.
