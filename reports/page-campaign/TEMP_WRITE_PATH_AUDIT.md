# Temp script write-path audit — 2026-09-02

User-directed stop: fix the campaign's temp tooling (kanji write-safety) before
authoring kanji-bearing technique content (145/149 pages carry kanji: technique
names, Domain Expansion terms in Usage prose, infobox kanji fields).

## Reference standard

`scriptengine/eval/page_gen.py:1065-1080` (`write_batch`), hardened for **G10**
(Mei Mei Q001, 2026-08-27): a kanji answer (`冥冥`) was stored garbled as
`å†¥å†¥` — UTF-8 bytes read as cp1252 in a path that did not name its encoding.
The hardened write: (1) temp file in the same dir, (2) `utf-8-sig` (self-
describing BOM), (3) round-trip assert `json.loads(tmp) == batch`, (4) schema
validate, (5) atomic `tmp.replace(batch_path)`, (6) unlink tmp on failure.

## What was checked

- `battle_prose_add_verbatim_gated.py` (add_prose.py) — battle/roster prose adder
- `technique_wave_tool_list_dump_add.py` (tech_wave.py) — technique-wave adder
- `battle_prose_dump_l2_sections.py` (dump_prose.py) — battle section dumper
- `battle_wave_progress_done_vs_pending.py` (battle_progress.py) — progress tool
- Read-through of the rest of `temp_py_scripts/`: census 01-08, scan/dump pagenote
  tools, `battle_spec_jujutsu_sorcerers_vs_sukuna.py` (all read-only or spec-only)

## Actually wrong

1. **Both add scripts wrote in place.** `json.dump(batch, open(path, 'w', …))`
   truncates the live batch before writing; a crash mid-write loses the whole
   batch (all identity + battle + prose questions), not just the new entries.
   No temp file, no atomic replace, no round-trip proof, no BOM.
2. **add_prose.py read with plain `utf-8`.** Any batch carrying the G10 BOM
   (written by page_gen since 2026-08-27) would crash it. Corpus is currently
   mixed: 175 BOM / 399 no-BOM batches (see audit below), so this was a live
   landmine, not theoretical.
3. **battle_progress.py had an unguarded `json.load`.** A corrupted batch would
   crash the tool. Also: "done = any prose note present" is only sound if the
   batch file is always complete — which the in-place write did not guarantee.

Not wrong (confirmed): the census/scan/dump tools are read-only;
`battle_spec_jujutsu_sorcerers_vs_sukuna.py`'s `find_exact` normalizes curly→
straight quotes for *matching* but writes back the original-encoded substring,
which is correct for verbatim sourcing.

## Changed (all re-synced into `temp_py_scripts/`)

- `technique_wave_tool_list_dump_add.py` + `battle_prose_add_verbatim_gated.py`:
  write block now mirrors the G10 hardening — temp file, `utf-8-sig`, flush +
  `os.fsync`, round-trip assert (full dict equality **and** CJK-char count, the
  explicit G10 sentinel), atomic `os.replace`, tmp unlinked on failure.
  All batch/spec/wikitext/order reads switched to `utf-8-sig` (tolerates BOM and
  no-BOM alike).
- `battle_prose_dump_l2_sections.py`: reads → `utf-8-sig` (BOM no longer fatal).
- `battle_wave_progress_done_vs_pending.py`: guarded load — an unreadable batch
  is now reported under a `CORRUPT (re-verify)` flag instead of crashing, so a
  partial write can never count as "done".
- `technique_spec_precheck_verbatim_diagnostic.py` (new, replaces the broken
  tech_diag): read-only spec pre-check — longest-prefix divergence point,
  inline `(Chapter N)` citation-marker hint, curly-quote/whitespace
  normalization hint.
- `batch_integrity_audit_jjk_pages.py` (new): corpus-wide batch audit — strict
  parse, BOM census, CJK survival, G10 mojibake scan (Latin-1 residue outside
  the 4 legit chars é á ñ ½, plus †/€ anywhere; list/dict answer items scanned).

## Re-verification

- **All 574 `_jjk_page_*` batches** (90 battle + 484 technique/character/
  episode/other; 35,590 questions; 1,715 CJK chars): **CLEAN** — zero parse
  failures, zero mojibake flags. Non-ASCII inventory is all legit (romaji
  macrons ō ū ā ī ē, Séance's é, ½ heights).
- **Battle progress re-run after the fix:** 90/90 authored, PENDING 0, no
  CORRUPT flags.
- **New write-path smoke test:** kanji batch (冥冥, 領域展開：蒼の巨獣) through
  the new block — BOM present, 9/9 CJK chars round-tripped, atomic replace OK.

Forward note: every batch written from now on carries the BOM; all readers in
the repo (`page_gen` lines 918/977, the temp tools) already use `utf-8-sig`, so
the corpus converges to self-describing UTF-8.