# RECEIPT — wave A / d4-open50 author (fresh-context subagent 'd4-open50-author')

Date: 2026-09-09 · series: csm · set: d4_open50 (frozen; executor runs, never edits)

## File
- `reports/csm/d4_open50_csm.json` — 50 items, ids Q01..Q50.

## meta block (as written in the file)
- seed: 20260909 (used to derive the 5 spot-check ids)
- revid_fetched: "2026-09-09"
- item count: 50
- source_pages count: 54
- author: "fresh-context subagent 'd4-open50-author' (worker, CSM Wave-2 wave A, 2026-09-09); frozen by the orchestrator's unit-1 commit; the executor runs it, never edits it (git-blame checkable)"
- revids: carried from questions/csm.json revid_stamp (fetched 2026-09-08); null where unstamped.

## Five spot-checks (seed 20260909 → ids Q10, Q19, Q28, Q37, Q46)
1. Q10 (Katana Man attack plan; 30 convicts; shrine; grandfather's death): grounded in
   `series/csm/facts.db` — documents "Katana Man arc" / section "Synopsis" (read: Makima in
   Kyoto requests 30 life-sentence convicts, crushed the Gun Devil's henchmen at the shrine)
   and documents "Katana Man/History" / section "History" (Katana Man believes Denji killed his
   Yakuza grandfather; actually the Zombie Devil).
2. Q19 (Pochita vs Four Horsemen/Weapon Devils in Hell; Horsemen arrive on Earth, part ways):
   grounded in documents "Pochita/History" / "History" (the final Hell battle, Pochita's
   vanished "near death form") and "Makima/History" / "History" ("the Horsemen arrived on
   Earth as well, apparently parting ways").
3. Q28 (Falling Devil at Asa's apartment complex; Yoru keeping Asa alive): grounded in
   documents "Falling Devil arc" / "Synopsis" (occupants staring out, corpses merging, Yoru
   fleeing, Asa's Crambon flashback handing back control, the gravity reversal under a building).
4. Q37 (why both Asa and Yoru care about Denji; "both of us like him"): grounded in
   documents "War Devil arc" / "Synopsis" ("Yoru adds that both her and Asa like him, which
   causes Denji to tear up of joy that someone still likes him").
5. Q46 (Four Horsemen scattered on Earth — Control=Makima, War=Asa, Famine=Fami, Death under
   Fami's alias): grounded in documents "Makima/History" / "History" (Control Devil assumed the
   identity "Makima"), "Yoru/History" / "History" (Yoru to Earth for a new body, revenge on
   Chainsaw Man), "Famine Devil/History" / "History" (Death Devil uses her sister's name as
   alias) and the "Four Horsemen" organization page.

## Self-check
1. `python -m json.tool reports/csm/d4_open50_csm.json` → valid; 50 items; ids == Q01..Q50 (program-verified).
2. Dupes vs the 39-question seed bank (questions/csm.json, incl. retired): none (normalized exact + containment).
3. JJK-bleed scan (word-boundary, JJK-only names): none.
4. Spread: Q01–Q23 = Part 1 / Public Safety, Q24–Q50 = Part 2 / Academy; subjects cover Denji,
   Power, Aki, Himeno, Kobeni, Makima, Kishibe, Angel Devil, Pochita, Katana Man, Reze,
   Quanxi, Fumiko, Yoshida, Asa, Yoru, Nayuta, Fami + devils (Bat/Leech, Eternity, Gun,
   Bomb, War, Justice, Falling, Famine, Death, Aging, Loneliness Fiend, Four Horsemen).

## Command audit (all read-only class)
- read/grep/ls/wc on plan/, reports/, questions/, series/csm/overrides.yaml (no edits)
- `scriptengine/.venv/bin/python` + stdlib sqlite3: SELECT/PRAGMA only on series/csm/facts.db, each <15 s
- `scriptengine/.venv/bin/python -m json.tool` on the deliverable (json validation)
- zero engine-model commands (no pytest/eval/span-recall/canon-run/transcripts, no :8000, no embedder/reranker loads)

## Shortfalls
None.
