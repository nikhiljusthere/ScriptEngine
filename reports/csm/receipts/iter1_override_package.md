# Receipt — CSM override package, iteration 1 (2026-09-09, unit-3 serial-fix closure)

Worker: fresh-context subagent, zero-GPU / model-free (Qwen 27B @ 150k
inherited, untouched). No :8000 calls, no span-recall, no index/crawl, no
git add/commit, no JJK files touched. Every shell command bounded < 15 s.
Companion work record: `reports/csm/override_fixes_iter1.md`.

## Facts (verified on disk)

1. **13 d5 line-miss rows (csmd5-01..07 + gate400-188/189/211/320/490/542)
   are all R-2, none OVERRIDABLE.** For every row: the target section exists
   in `series/csm/facts.db` `sections`, is chunked (one level-1 section chunk
   + N level-2 passage chunks whose word counts sum exactly to the section's
   `word_count`), the target line sits inside a level-2 chunk (verified by
   substring), and the section title is not in the CSM effective skip set
   (`chunker.py` `BOILERPLATE_SECTIONS` {references, navigation, external
   links, see also, site navigation, gallery, image gallery, notes} minus the
   CSM override's `content_sections: [Notes, References]` → {navigation,
   external links, see also, site navigation, gallery, image gallery};
   target titles are Plot Summary, Story Arcs, Devil Powers, Aging Devil arc,
   Plot points introduced, Synopsis, Devil Contract, Bomb Girl arc, Eternity
   Devil arc). The miss is retrieval-side (MISS_DOC = document not in the
   retrieved set; MISS_SPAN = passage omitted from the bundle — the G-CSM-2
   "bundle leg (budget/ranking)" shape). `content_sections` can only
   *promote* engine-boilerplate sections to content (COUNCIL_d5-close
   mechanism), so it has no surface here.
2. **R-6 (door-nar-Introduction / Bomb Girl / International Assassins):
   engine hook pending.** Canonical pages verified in `documents`/`nodes`:
   `Introduction arc` / `Bomb Girl arc` / `International Assassins arc`
   (all `story_arcs_box`, resolved). The narrative door resolves by exact
   phrase lookup in the `aliases` table (`stores/facts.py:link_entities`,
   `a.alias IN (query n-grams)`); the bare display names are not aliases
   (only the full `… arc` titles are). No per-wiki alias-map field is
   consulted by the retrieval path: the only overrides fields the
   subject-resolution path reads are `subject_demote_types` /
   `subject_type_priority` (`config.subject_ranking`); the `aliases` table is
   populated at index time from wiki-side data only. Missing field:
   `subject_aliases:` (display name → canonical node name) in
   `series/csm/overrides.yaml`, consulted in `scriptengine/retrieve/
   narrative.py` (`NarrativeRetriever.timeline`'s `rank_subjects(link_
   entities(subject), …)` step; seam: `config.subject_ranking`). Not built
   (engine change = council); no unread field added.
3. **R-7 (62-key infobox gap): engine hook pending.** The page-sweep
   identity builder (`scriptengine/eval/page_gen.py`, `_identity_builder`)
   matches fact keys against the engine-level `IDENTITY_FIELDS` (:49) +
   `UNCHECKED_KEYS` (:71); it receives `overrides` but consults only
   `_declared_list`. No per-wiki key-map override field is referenced
   anywhere in the tree (grepped `identity_fields|key_map|infobox_map|
   fact_keys` across `scriptengine/` + `series/`). Missing field:
   `identity_fields:` (CSM key → question template), consulted in
   `scriptengine/eval/page_gen.py` ahead of the engine dict (one-line
   engine merge, still council + four gates). The frozen JSON
   `reports/csm/t0_pilot_csm.json` `meta.unmatched_csm_infobox_keys` holds
   61 keys (report text says 62; JSON is authoritative). Near-miss seed for
   the four T0-named keys recorded in the work record; full 61-key map
   deferred to hook approval.
4. **Nothing applied.** `series/csm/overrides.yaml` untouched: no row was
   overridable, and both candidate hooks are absent. Reindex flag: **not
   set** (no chunking change). Expected queue rows closed by this package:
   **0** (13 R-2 + 3 R-6 rows stay open on engine classes; R-7 lever stays
   pending).

## Commands run (all < 15 s, zero-GPU)

| # | command | result |
|---|---|---|
| 1 | read `reports/csm/COUNCIL_unit3_sweep.md`, `miss_queue_csm_iter1.jsonl` (55 rows), `red_list_csm.md`, `T0_PILOT_CSM.md`, `CSM6_INSTRUMENT.md`, `reports/comprehension/COUNCIL_d5-close.md`, `series/csm/overrides.yaml` | ok |
| 2 | `python3 -c 'import sqlite3…'` read-only `file:series/csm/facts.db?mode=ro`: schema + counts (documents 537 / sections 3917 / chunks 7797 / facts 5081) | ok |
| 3 | SQL: sections for `Academy Saga`, `Aging Devil`, `Aki Hayakawa`, `Akane Sawatari`; all `Aging Devil arc`-titled sections; `%History%` / `%Aging%` / `%Academy%` documents; sections of docs 2/4/10 | ok |
| 4 | SQL: per-row chunk coverage (L1/L2 counts, word sums) + target-line containment in section text and L2 chunks for all 13 rows (initial `LIKE` without wildcards was a false negative — bare LIKE is whole-string anchored; re-verified with `instr(text, frag) > 0` and `%frag%` — see risk note) | ok |
| 5 | read `scriptengine/index/chunker.py` (BOILERPLATE_SECTIONS, `effective_boilerplate_sections`), `scriptengine/config.py` (`load_overrides`, `subject_ranking`), `scriptengine/retrieve/narrative.py`, `scriptengine/stores/facts.py` (`link_entities`), `scriptengine/eval/page_gen.py` (IDENTITY_FIELDS, `_identity_builder`) | ok |
| 6 | `grep -rn "overrides.*\.get(" scriptengine/retrieve stores script api` — full list of override fields the retrieval path reads (no alias/key-map field) | ok |
| 7 | SQL: `story_arcs_box` documents (14 arc pages); `aliases`/`nodes` for introduction / bomb girl / international (bare display names absent; only `… arc` titles) | ok |
| 8 | `python3 -c 'import yaml; yaml.safe_load(open("series/csm/overrides.yaml"))'` → parses, 11 top-level keys | passed |
| 9 | `git status --porcelain series/csm/overrides.yaml` → empty | passed (unmodified) |
| 10 | read `reports/csm/t0_pilot_csm.json` `meta.unmatched_csm_infobox_keys` (61 keys) | ok |

No model loaded; no server; no writes outside the two report paths.

## Files changed

- `reports/csm/override_fixes_iter1.md` (new) — per-row verdict table
  (13 d5 rows + 3 R-6 rows + R-7 check), hook-pending records with exact
  missing fields + consulting files, near-miss key-map seed, applied=nothing,
  reindex flag not set, expected closures 0.
- `reports/csm/receipts/iter1_override_package.md` (new) — this receipt.
- `series/csm/overrides.yaml` — **unchanged** (deliverable conditional on
  an applied override; none qualified).

## Validation output

```
$ python3 -c "import yaml; d=yaml.safe_load(open('series/csm/overrides.yaml')); print(sorted(d))"
['ability_kinds', 'ability_sections', 'ability_stopwords', 'archetypes',
 'citation_positional', 'content_sections', 'page_scope',
 'relation_sections', 'remainder_note', 'rosters', 'unknown_pages']

$ git status --porcelain series/csm/overrides.yaml   # (no output)
```

Containment spot-check (row csmd5-01, section 11 `Academy Saga / Plot
Summary`): section text and the L1 + L2 chunks all carry
`…tries to "accidentally" expose his identity as Chainsaw Man…`
(`instr(text, 'expose his identity as Chainsaw Man') > 0` → L1 hits 1,
L2 hits 1).

## Residual risks / notes

- **False-negative trap in the first containment pass:** a bare
  `text LIKE 'fragment'` (no `%` wildcards) matches whole strings only, so
  the first check read 0 hits for fragments that are present. Corrected with
  `instr(text, frag) > 0` / `'%frag%'`; the verdict table above rests on the
  corrected check. (The project's own `page_gen.chunked()` uses the
  `%…%` form — consistent.)
- csmd5-03's queue `q` field is truncated (`"\"`); the verdict uses the row's
  `src_page` line instead.
- The "62 keys" figure in `T0_PILOT_CSM.md` / `CSM6_INSTRUMENT.md` is 61 in
  the frozen JSON list; B may want the report text aligned to 61 at commit.
- R-6 canonical names were verified in the *current* db (docs 376/32/375);
  if the R-6 hook lands as DB alias rows, one reindex materializes them
  (override-read-at-query-time needs none).