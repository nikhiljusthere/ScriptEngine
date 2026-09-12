# Receipt — bar-audit pre-registration authoring (bar_audit_p14_preregistered.json)

Author: authoring subagent (authoring only). Timestamp: 2026-09-12 05:53 UTC (11:23 IST).
Task: author + verify the P1.4 pre-registered bar-audit bank per
`plan/CSM_2PHASE_PLAN.md` P2.2/A21 (close condition d, pre-marker): 6 D6 census
classes, 3–5 cases each, every case anchored on exactly one panel line from
`reports/csm/panel_csm.json`, all expect terms verified model-free against
`series/csm/facts.db`. No oracle authoring beyond this bank, no retrieval, no
model, no `:8000`, no Qdrant — stdlib `json` + `sqlite3` (read-only) only.

## Outputs written

- `reports/csm/bar_audit_p14_preregistered.json` (UTF-8, 2-space indent, valid JSON)
- This receipt: `reports/csm/receipts/bar_audit_p14_author.md`

No other file was modified. `panel_csm.json` (hash
`e3d737205cd07245a8a3677dc03b0eb1f3c08d43ed7d8ab0b308bf97e73ebe6d`, 17,181
lines) was read only.

## Shape

- Top level: `meta` + `items`. `meta` keys per spec: `series`, `generated`,
  `spec`, `classes` (the 6 D6 census classes), `cases_per_class` (`"<3-5>"`),
  `panel_source` (panel path + stored hash), `expect_verified`, `purpose`.
- Item keys: census v1 item shape (`id`, `class`, `subject`, `q`, `expect`,
  `source`) plus `panel_line` = the exact `[page, section, sentence]` triple
  from `panel_csm.json`. `expect` is exactly 3 verbatim phrases; `expect[0]`
  is the anchored panel line verbatim (copied programmatically from the panel
  file, never retyped); `expect[1]`/`expect[2]` are two more verbatim phrases
  from the same page+section (for `abilities`: two other ability names from
  the character's `abilities` rows). `source` = `{page, section}` (full-path
  section string, matching the `panel_line` triple) or
  `{table: "abilities", character}` for the abilities class.
- 26 items: 5 arc-narrative, 4 abilities, 4 state-over-time, 4 appearance,
  5 causality, 4 personality. Ids `csm-bar-<abbr>-NN` (abbr arcn / abl /
  state / appr / caus / pers), unique, NN 01–N per class. No page is reused
  within a class.

## Per-class case table

| class | ids | subjects |
|---|---|---|
| arc-narrative | csm-bar-arcn-01…05 | Denji, Yoru, Power, Chainsaw Man Church, Fake Chainsaw Man |
| abilities | csm-bar-abl-01…04 | Pochita, Power, Falling Devil, Death Devil |
| state-over-time | csm-bar-state-01…04 | Nayuta, Power, Kobeni Higashiyama, Denji |
| appearance | csm-bar-appr-01…04 | Asa Mitaka, Fumiko Mifune, Santa Claus, Locust Devil |
| causality | csm-bar-caus-01…05 | Denji, Yoru, Crambon, Gun Devil, Makima |
| personality | csm-bar-pers-01…04 | Denji, Asa Mitaka, Power, Fami |

Arcs covered: War Devil (arcn 01–02, 04–05), International Assassins (arcn-03),
Control Devil (state 01–02), Eternity Devil (state-03), Bat Devil (state-04),
plus `Synopsis / History` / `Plot / History` for causality.

## Verification result

- **78/78 expect terms verified** (26 items × 3) as exact substrings of
  `series/csm/facts.db` fields `sections.text`, `facts.value`,
  `abilities.name`, `documents.title` — read-only connection,
  `LIKE ? ESCAPE '\'` with `%`/`_`/`\` escaped, plus a stricter
  case-sensitive Python `in` cross-check over the same four fields
  (SQLite `LIKE` is case-insensitive for ASCII; the cross-check rules out a
  case-variant false positive). All 78 pass both.
- **0 terms corrected** to exact DB phrasing during authoring (all terms were
  drafted directly from panel lines / `abilities.name` rows, which are the DB
  phrasing itself).
- **0 panel lines dropped** (no anchored panel sentence failed the DB
  verbatim check).
- All 26 `panel_line` triples exact-match entries of `panel_csm.json`
  (set membership check); `expect[0] == panel_line[2]` for every item; ids
  unique; all 6 classes present with 3–5 cases each; per-class id numbering
  contiguous.
- Two authoring-script anchor prefixes were fixed before the first green run
  (my prefixes, not the data): a straight-apostrophe prefix against the
  panel's curly-apostrophe `Aki’s money` (state-02) and a malformed
  `s main body…` prefix for `Santa Claus’s main body…` (appr-03). Both
  re-resolved to the unique panel sentence; the written JSON is unaffected
  by these (they are prefixes used only to locate panel lines).

## Commands run (all < 15 s, no server, no model, no GPU)

- `python3 -c` JSON load of `panel_csm.json` (shape, hash, 17,181 lines) — ~2 s
- `python3` heredocs over the panel: section-name distribution, per-(page,
  section) counts, candidate line dumps — ~2 s each
- `python3` read-only `sqlite3` queries on `facts.db`: schema, `abilities`
  rows for Pochita/Power/Falling Devil/Death Devil/Makima, section text
  samples (breadcrumb vs title, `(Chapter N)` markers) — ~1 s each
- `python3 /tmp/opencode/bar_audit_author.py` — resolves all anchors/e-prefixes
  to exact panel sentences, builds the 26 items, runs structural checks
  (ids, class counts, panel triple membership, `expect[0]` anchor identity)
  and the 78-term DB verification; writes the JSON only on 0 failures — 0.12 s
- `python3` post-write re-parse + independent re-verification pass on the
  written file (shape, 78/78 terms re-checked against the DB, panel
  membership, meta) — ~2 s

## Note for the parent

- The bank is on disk **before the P1.4 marker**, as P2.2/A21 requires
  (pre-registration). P2.2 proper is mechanical grading only (per JJK 3b:
  ≥2 of 3 expect terms in the served bundle ⇒ GREEN), run against the panel
  400-gate control arm; re-grade only if P2.1's misses change a dimension.
- **Value-style delta vs census v1 (deliberate, flag for the grader):**
  census v1 `source.section` values are leaf names (e.g. `Aging Devil arc`);
  this bank uses the full-path section string that matches the `panel_line`
  triple (e.g. `Synopsis / Academy Saga / War Devil arc`), because the
  pre-registration must stay exactly aligned with `panel_csm.json`. Item
  *shape* (field set) is identical to census v1 + `panel_line`.
- Abilities class: `expect[1]`/`expect[2]` are `abilities.name` rows
  (verified in the `abilities` table: Pochita `Devil Erasure`/`Chain
  Entanglement`; Power `Blood Axe`/`Blood Transfer`; Falling Devil `Area
  Denial`/`Levitation`; Death Devil `Absolute Immortality`/`Resurrection`),
  so the enumeration form `Every ability of <subject>` is graded on real
  roster rows, with `expect[0]` the anchored abilities-section line.
- The DB stores `sections` with leaf `title` + `breadcrumb`; the panel's
  full-path strings align with `breadcrumb` for character `/History` arc
  sections (verified for `Denji/History` War Devil arc and `Power` Devil
  Powers). Verification is field-global (any of the 4 fields), per the
  census v2 method, so section-row layout does not affect the check.
- Any later P2.1 dimension change that re-scopes a class should re-open the
  affected cases here (the panel hash in `meta.panel_source` is the freeze
  point; a panel edit between marker and P2.1 would need the A26
  re-hash).