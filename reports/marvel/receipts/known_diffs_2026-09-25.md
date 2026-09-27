# Known diffs — Marvel/MCU campaign (2026-09-25, zero-egress audit)

Source of the numbers: `tools/marvel/title_drift_audit.py` (untracked;
outputs `reports/marvel/receipts/title_drift_audit_{marvel,mcu}_2026-09-25.json`).
This file is the single record of the known, bounded, non-blocking diffs
between the campaign's on-disk state and the same-day wiki enumeration —
council `COUNCIL_gate_A_download.md` (Record corrections section) and the
owner wall (`OWNER_WALL_2026-09-25.md`, RECORD CORRECTION block) both
point here. Untracked, never committed (campaign receipt).

## F2 — title drift (the "46" figure is dead)

The council round's "46 stale titles / 46-title rename map" is **not
reproducible under any metric** against the same-day 279,133 enumeration
(V1 stored-title ∉ enum = 1; V2 vs the 15:21 enumeration = 20; V3
sanitized = 1; V4 filename = 1; MCU = 0). The actual drift:

- **1 orphan file:** `series/marvel/pages/Elizabeth Tyne (Earth-33263).json`
  — the title was dropped from the wiki between the 15:21 and 18:58
  enumerations (`E_old − E_new` = exactly the 2 `Elizabeth Tyne`
  variants). The file stays on disk (content is valid; the page was
  deleted/renamed wiki-side after its crawl).
- **23 net-new titles:** the enumeration grew 279,112 → 279,133 (net +21
  = 23 added − 2 dropped) between the 15:21 and 18:58 lists; the
  reconciliation catch-up wrote all 48 (23 net-new + the earlier failed
  page + re-verified tail).

Consequences wired into the plan: (1) there is no 46-title rename map to
maintain — the "rename map" reduces to recording the 1 orphan + the
net-new titles; (2) the next revid spot-check must include renamed titles
(once revids are stamped, re-validation switches from title-diffing to
revid compare — the orphan will surface there as a wiki-side deletion,
not a content change).

## F3 — collision groups (4 titles → 2 files)

Two collision groups where distinct wiki titles sanitize to the same
on-disk filename (zero-egress confirmed):

| on-disk file | titles that map to it |
|---|---|
| `series/marvel/pages/What If_ Thor Vol 1.json` | `What If: Thor Vol 1` + `What If? Thor Vol 1` |
| `series/marvel/pages/What If_ Thor Vol 1 1.json` | `What If: Thor Vol 1 1` + `What If? Thor Vol 1 1` |

Action (egress batch, post-F1): re-crawl the 4 titles under
disambiguated filenames so each title owns its file; the new files stamp
`revid` natively (the F1 `rvprop=ids|content` fix is landed, `664796b2`).

## F7 — stray-`'` in cleaned fields (root-caused, fixed, gated)

Audit (naive all-string walk excluded by design — `raw` carries
legitimate quotes; a naive walk = 1.87M false artifacts):

- **Blast radius:** 16,933 stray-`'` occurrences in **5,295 Marvel files
  (2.2%)**; 397 occ in **311 MCU files (0.9%)**.
- **Root cause:** `'''{{Conjecture|X}}'''` — `Conjecture` was not in
  `TRANSPARENT_TEMPLATES` (def @ `wikitext.py:208`), so `_strip_templates`
  emptied the template; the wrapping emphasis collapsed to six merged
  quotes; `_QUOTES = r"'{2,5}"` (@~290) strips at most 5 → one stray `'`
  **and the name was lost** (proof: MCU `series/mcu/wikitext/Ajax.json`
  stored lead `"' was a mutant … codename '."` — Francis Freeman + Ajax
  both missing from the source `'''{{Conjecture|Francis Freeman}}'''` …
  `'''{{Conjecture|Ajax}}'''`).
- **Fix (committed `06d39c94`, named paths, 2026-09-26):** `_QUOTES` →
  `r"'{2,}"` (unbounded — well-formed emphasis is ≤ 3 quotes, so longer
  runs are only template-strip residue) **and** `"conjecture": "first"`
  in `TRANSPARENT_TEMPLATES`. Four standing gates GREEN (receipt
  `reports/marvel/receipts/gates_f7_wikitext_2026-09-25/`).
- **Zero-egress verification:** `reextract` on the stored Ajax wikitext
  (`crawler.py:852` `load_extracted`; script `/tmp/verify_f7_ajax.py`) →
  lead now `"Francis Freeman was a mutant who fought Wade Wilson and went
  under the codename Ajax."` (names restored, 0 stray quotes).
- **Still owed (own gated commit):** the O*N*E-class regression fixture is
  **not yet in `tests/`**. Plan: one-line fixture feeding a
  `'''{{Conjecture|<redacted-name>}}'''`-shaped input through the cleaner
  and asserting (a) no stray quote survives, (b) the first positional arg
  (the name) is preserved in prose. Landing it moves the pytest pin
  (1,345 passed → +1) → its own gated commit (new pin + four standing
  gates). Note: the corpus's O*N*E hits are the campaign's intentional
  redaction convention (real-world identities anonymized), **not** F7
  residue — the fixture uses the same shape, not the corpus string.
- **Re-emit (zero egress) — LANDED 2026-09-26 (tool
  `tools/marvel/reemit_f7.py`, full streaming pass, enriched ontology
  exactly as `load_extracted` builds it; per-file backup + atomic rename;
  receipts `reports/marvel/receipts/reemit_f7_{mcu,marvel}_*_2026-09-26.json`):**
  the changed set is *larger than the F7-only estimate* because the pass
  re-extracts with the **current** parser (L2 hooks + F7), which is what
  `load_extracted` does by design:
  - **MCU (done 09:11):** 16,706/35,209 files (47.4%) rewritten;
    key-diff census — `facts` 16,024, `page_type` 15,243,
    `infobox_template` 15,125, `edges` 14,716, `aliases` 1,499,
    `lead` 566, `sections` 525; **`preserved_key_violations: []`**
    (title/url/pageid/revid/wikitext/fetched_at/categories/templates/
    redirects untouched in every file). F7 effect: stray-`'` rescan
    256 occ → **2 occ** (99%); the council exemplar `Ajax.json` now
    carries *Francis Freeman* in the on-disk lead. 16,706 pre-write
    backups: `reports/marvel/receipts/reemit_f7_mcu_backup` (401M).
  - **Marvel (done 09:38–10:04, two passes):** the first pass
    (09:12) was killed by a host restart at ~65.5% (5,261 files written +
    backed up); the pass is a deterministic fixed-point re-extraction, so
    a second full pass (09:38) re-verified the first 65% (0 changes) and
    wrote the remainder (2,668). **Total 7,929/236,628 (3.35%) rewritten**;
    pass-2 key census — `facts` 2,394, `page_type` 460, `sections` 378,
    `edges` 277, `infobox_template` 205, `lead` 2, `aliases` 1;
    **`preserved_key_violations: []`**; 0 `.tmp` residue; 7,929 pre-write
    backups: `reports/marvel/receipts/reemit_f7_marvel_backup` (282M).
    Post-re-emit stray rescan: **14,429 occ / 5,285 files → 176 occ /
    144 files (98.8% / 97.2% down)**; the residual is NOT F7 residue —
    it is the campaign's O\*N\*E redaction convention (empty link targets
    like `…stop the ' attempts to take over .`), space-apostrophe source
    quality (`Ben Parker ' s wife`), and single-`'` placeholder leads.
    Bookkeeping delta CLOSED: dry run predicted 7,930; 7,929 written; final
    fixed-point verify pass (21:05, receipt `reemit_f7_marvel_verify_2026-09-26.json`)
    = `changed=0`, 0 preserved-key violations, 0 unreadable — the corpus is a
    fixed point of the current parser; re-emit closed. The
    plan's "5,295" was the F7-stray-only estimate; the extra delta is
    parser evolution since the Marvel crawl (same class as the MCU 47%).
- **F7-residual family — `{{WPS|…}}` possessives (known diff, bounded,
  NOT the F7 Conjecture case):** after the MCU re-emit, 2 strays remain,
  both a possessive `'` *in the wikitext source* sitting after a
  non-transparent `{{WPS|…}}` link template (WPS ∉ TRANSPARENT_TEMPLATES,
  so the template is stripped and the `'` is orphaned):
  `Arlene.json` lead `…like a {{WPS|Beatles}}' {{WPS|Come Together|song}}`
  and `Assassination of Abraham Erskine.json` lead `…the
  {{WPS|Allied Powers|Allies}}' only defense…`. Bounded at 2 files /
  2 occ; a fix (adding `wps` to TRANSPARENT_TEMPLATES) is its own
  gated commit — owner call, not a scope extension of F7.

## Standing

JJK + CSM corpora are baselines, never touched. MCU is in-campaign (the
311-file F7 figure rides the same re-emit + gates). Nothing in this file
blocks GATE A (verdict: PASS, conditional) or the Phase C entry beyond the
already-scheduled items above.