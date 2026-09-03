# OPENCODE PROMPT — VOLUME LOOP (character prose pass, handed off 2026-08-31)

You are continuing the JJK page-campaign character prose pass. **25 of 132 new
characters are done; 107 remain: `order[36]` → `order[142]`** in
`reports/page-campaign/jjk_character_order.json` (first: next character after
Uraume).
Work them **in order, one at a time, until told to stop**. You are the only
agent working. Do NOT edit any file under `scriptengine/`, do NOT commit
anything, do NOT touch other characters' batches.

This document is self-contained. Read the two handoff files before the first
character (house style lives there): `HANDOFF_PROSE_PASS.md` (METHOD
CORRECTION + per-character table) and the `prose_pass_template.md` in the
temp toolchain directory.

## 0. State snapshot (as of 2026-08-31, ~14:30 local)

- **G15 (chunker 20-word section floor) is FIXED + gated.** `chunker.py:299`
  no longer drops short non-item sections; the jjk index was rebuilt
  (19,497 chunks, +2,698 short). The narrative-route floor was deliberately
  kept (it protects the `sourcing-01` contract). Short Personality/Trivia
  sections are now indexed — you should NOT hit chunker-floor failures. If
  one still appears, it is a different gap: diagnose + record, never
  rephrase.
- **Gate baseline on the final code (LSP pass, 2026-08-31):** re-run only
  after engine changes, not per character: `pytest` **1072 passed**;
  `eval --series jjk` **24/24**; `canon-run --series opm` **8/16, 235/237,
  78.5% — no change** (report `reports/2026-08-31-0924`).
- **Type-clean:** the whole repo is **pyright-clean (0 errors)** as of the
  2026-08-31 LSP pass (79 baseline errors fixed: annotations, None-guards,
  one latent `LLMClient.base_url` → `settings.llm_base_url` error-message
  bug). Re-verify after any engine change:
  `npx -y pyright --pythonpath <scriptengine\.venv\Scripts\python.exe> scriptengine tests`
  (must stay 0; the `--pythonpath` is what makes it see the venv's
  fastmcp/playwright types). A "fastmcp could not be resolved" squiggle in
  the editor is a Pylance-environment artifact (fastmcp 3.4.7 IS installed
  in the venv) — ignore it, don't "fix" the import.
- **Server:** the live server on port 8000 runs the LSP-pass code (start
  2026-08-31T09:19:25Z, cuda, 8 series; **restarted 2026-08-31T12:37:27Z
  for SU11 — no engine changes since, gates still hold**). Freshness rule:
  the server's `started` must be newer than the newest
  `scriptengine/**/*.py` mtime.
  `page-run` hits the live server, so if any engine file changed (it
  shouldn't — you don't edit engine code), restart the server before running
  (restart recipe in §7.4).
- **Open G-n (known, un-fixed — do not try to fix these during volume):**
  G14 (Atsuya `045`), G13 (probe_r3-105), G11 (2×probe_r3), G5/R4 (deferred
  retrieval-quality pass — the G14-family list folds into it), toge_inumaki
  `051`, plus unnumbered router-edge observations (G4b `end up` head-check,
  G1 subordinate-clause set-noun, G8a-adjacent yes/no battle-verb shape,
  G5-family drafting-time collision). All are recorded in
  `HANDOFF_PROSE_PASS.md` (ENGINE GAPS + State updates 8/9).
- **Done so far (SU11 re-baseline, 2026-08-31): 60 of 146 order-list
  entries (14 redos + 45 new + 1 duplicate entry; 86 undone, starting at
  order[56]).** Breakdown: pre-campaign probes order[0]–[20]; 7 pre-R5
  (Mahito, Panda, Geto, Inumaki, Jogo, Shoko Ieiri, Mei Mei); order[21]–[30]
  (Tengen, Hanami, Mai Zenin, Kinji, Atsuya, Ijichi, Miwa, Yaga, Kamo 91/93
  with 2 documented-opens, Yuki Tsukumo); parallel-session order[143]–[145]
  (Kaito, Sara, Hanako 23/23 post-G15); the fast-model session did
  order[31]–[55] (24 characters, HANDOFF rows 142–165) **but skipped
  Momo Nishimiya (order[34]) and left Rika Orimoto (order[55])
  incomplete — both completed in SU11, plus data recovery: 5 characters had
  on-page facts wrongly retired (Ui Ui 16 questions re-authored, Hiromi 051,
  Yuka 087/088, Rika 136, Gakuganji 067 restored)**. Three documented-opens
  stand (Yuka 088, Ui Ui 033 battles-route over-match — G16 candidate,
  Gakuganji 067 affiliations edge). **Resume: order[56] Ryu Ishigori.**
  Full audit: SU11 in `HANDOFF_PROSE_PASS.md`.

## 1. Environment (Windows PowerShell 5.1)

```powershell
$env:PYTHONPATH = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
$env:PYTHONIOENCODING = "utf-8"
$py = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe"
```

- Use `;` never `&&`. Quote paths with spaces.
- Inline `python -c` with quotes breaks in this shell → **write temp `.py`
  files** and run them.
- PowerShell `>` writes UTF-16 → never pipe Python output to `>` for data;
  write files from Python (the bulk-add tool does this).
- Long jobs: run in background with `Start-Process … -RedirectStandardOutput`
  + poll the log. Never delete existing files; use fresh timestamped names.
- Repo root: `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine`.

## 2. Toolchain (temp dir `C:\Users\Nikhil\AppData\Local\Temp\opencode`)

| tool | usage | what it does |
|---|---|---|
| `prose_params.py "Name"` | `& $py C:\...\prose_params.py "Kokichi Muta"` (from repo root) | prints slug, batch size, max id, wiki file, uncovered sections, wiki URL |
| `prose_dump.py "Name"` | `& $py C:\...\prose_dump.py "Kokichi Muta"` (from repo root) | dumps every section's path + first ~500 chars of its text |
| `prose_bulk_add.py slug triples.json` | `& $py C:\...\prose_bulk_add.py kokichi_muta C:\...\kokichi_muta_triples.json` | bulk-adds authored triples to `questions/_jjk_page_<slug>.json` (generic: derives subject + source URL from the first existing question; appends `; +N prose pass (R5, <date>)` to the note; single-BOM utf-8-sig write) |
| `prose_triage.py slug "Name"` | `& $py C:\...\prose_triage.py kokichi_muta "Kokichi Muta"` | replicates the scorer per failing question: routed basis, n_beats, absent answer content-words |
| `prose_pass_template.md` | read | the method (dump → author → bulk-add → page-run → faithful triage) |

If a temp tool is missing, recreate it from the spec above (they are short
scripts; `prose_bulk_add.py` is the longest — ~110 lines, behavior fully
specified in its docstring/notes in the handoff).

## 3. The per-character loop (7 steps)

For `Name` = the next character in `jjk_character_order.json`:

1. **Params + state.** `prose_params.py "Name"`. Record slug, current batch
   size, max id, uncovered sections. If `_jjk_page_<slug>.json` does not
   exist, the character was never page-generated: **stop and checkpoint the
   user** (that is a structured-pass gap, not this loop's scope).
2. **Dump.** `prose_dump.py "Name"` → save to
   `C:\Users\Nikhil\AppData\Local\Temp\opencode\prose_<slug>.txt` (fresh
   name if one exists).
3. **Author.** Per uncovered prose section, one or more natural fan
   questions with a **verbatim** answer substring of the section text + the
   section path. Apply the standing rules (§5.1) and the CJK gotcha (§5.2).
   **R5 additions — every character gets:**
   - ≥1 **yes/no**, ≥1 **comparative**, ≥1 **counterfactual**, all against
     facts on this character's OWN page. Counterfactuals route `qa` (G9b
     fixed) but the answer must still be verbatim on the page; if the page
     states no hypothetical outcome, RETIRE it: "Not stated on the page:
     …" (Mai Zenin / Atsuya / Yaga precedent). Never invent the resolution.
   - **Authoring lint before running:** reject any question whose answer
     string appears inside the question text; reject a wh-word that is not
     at the front of the question; require a numeric answer for any
     "how many" question.
   Write the triples to `C:\...\<slug>_triples.json` (array of
   `{"question": …, "answer": …, "section": "… / …"}`).
4. **Bulk-add.** `prose_bulk_add.py <slug> <triples.json>`. Verify the batch
   re-loads with `utf-8-sig` (the tool writes a single BOM — a double-BOM
   bug was found and fixed on the Tengen pass; if reload fails, that is the
   bug recurring).
5. **Page-run.** `& $py -m scriptengine.cli page-run --series jjk --batch <slug>`
   (allow ~15 min; background + poll is fine).
6. **Faithful triage of every `prose:` failure** — `prose_triage.py
   <slug> "Name"`, then classify per §5 (gold error → fix in-lane + re-run;
   cross-page → retire with reason; engine gap → record G-n, no rephrase;
   G14-family → documented-open with evidence per Kamo precedent;
   pre-existing page-gen → classify + document + leave).
7. **Close + log.** Record: final score, report dir, ids added (range),
   which are the adversarial forms, retires (id + reason), any G-n with
   evidence, any pre-existing page-gen left. Write the per-character row in
   `HANDOFF_PROSE_PASS.md`'s table (house style — copy the shape of the
   Tengen/Hanami/Miwa/Yaga/Kamo/Tsukumo rows) and bump the
   "N of 132 done" count. Then next character.

## 4. Quality bar (what "done" means for one character)

All of these, or the character is NOT done:

1. `page-run` finished; every `prose:` failure is classified per §5 with
   evidence (triage output quoted in your report) — nothing hand-waved.
2. All `prose:` questions pass the gate, EXCEPT genuinely diagnosed
   non-blocking retrieval-quality gaps (G14 family), which may close
   documented-open (Kamo precedent: 91/93 with 2 recorded).
3. Zero rephrase-to-dodge: no natural question was reworded to dodge a
   failure (in-lane authoring fixes are allowed only when the FIRST
   phrasing was your own stilted construction AND a natural alternate was
   probed live — Kinji `079`, Yaga `036`, Tsukumo `083`/`086` precedent).
4. Every answer is a verbatim substring of the wiki prose (served form for
   Nihongo lines, §5.2).
5. Retires carry a reason (cross-page: name the owing page; counterfactual:
   "Not stated on the page: …").
6. Batch file integrity: single BOM, valid `utf-8-sig` reload, ids
   continue from max, note appended (not rewritten).
7. The handoff table row is written (count bumped, report dir named).

## 5. The error-handling playbook (how each error class is fixed)

### 5.1 Standing rules (non-negotiable)
- Never reword a question to dodge a failure of a NATURAL question. Root
  cause only: gold error → fix the answer in-lane; cross-page fact →
  retire with reason; engine gap → record G-n (id, routed basis, absent
  words, one-line root cause) — **do not edit engine code, do not fix G-n's
  in-lane**; checkpoint the user with the finding + a defer-or-fix
  recommendation (that is what happened with G15: it was fixed as its own
  gated release, not inside a character pass).
- Natural questions: the ones a fan would actually ask, per section.

### 5.2 Gold errors (the answer string is wrong) — the common class
- **Nihongo/CJK (the biggest one):** for lines containing `{{Nihongo}}`
  markup, the STORED section text has NO kanji, but the served bundle
  renders meaning + kanji + romaji (e.g. `"night, evening" 夜 ya and "moth"
  蛾 ga`). Gold the **served kanji-including form** and verify the exact
  codepoints against the live bundle before the run (a 1-char
  near-homograph escape cost a re-gold on Hanami `070`: 花 U+82B1 not
  U+82B2). Precedents: Kenjaku `羂索`, Shoko `夏/ge 油/tō`, Mei Mei `冥冥`
  (G10), Tengen `070`, Hanami `070`, Mai Zenin `142`/`143` (`禪 zen / 院 in
  / 真 ma / 依 i`), Atsuya `047`/`055`/`056` (`抜刀`, `日下部`, `篤也`),
  Ijichi `048` (`伊 地 知 潔 高`), Yaga `090` (`夜 蛾 正 道`), Kamo
  `092`/`093` (`加 茂 憲 紀`), Tsukumo `091` (`九 十 九 由 基`). If a plain
  meaning/body substring matches BOTH stored and served forms, plain is fine
  (Miwa `059`–`061`) — no codepoint risk.
- **Answer too long / absent tail:** the served beat carries less than the
  stored text (e.g. Kamo `071` dropped the simile tail "similar to blood
  doping"; Jogo Q44 shortened to the keyword "Ohaguro"). Shorten to what
  the bundle actually serves; probe before re-running.
- **Answer not on the page at all:** if it truly lives on another page →
  retire (cross-page, §5.3), not a gold error.

### 5.3 Retires
- **Cross-page fact:** the answer is canonical on a dedicated page (e.g.
  technique definitions with their own pages — Mahito `108`/`116`/`117`;
  other characters' data — Mahito `141`). Reason names the owing page.
- **Counterfactual not stated:** §3 step 3.

### 5.4 Engine gaps (G-n)
Record, don't fix, don't dodge. A G-n needs: question id, the routed basis
(`qa`/`narrative`/roster name), n_beats, absent content-words, and a
one-line root cause. Known families you will KEEP seeing (leave them;
they fold into the G5/R4 retrieval-quality pass):
- **G14-family (low keyword overlap):** the verbatim answer is in the
  top-50 beam (gate passes) but below the writer's top-8; or a dedicated
  technique page's differently-worded beat out-ranks the character-page
  line (Kamo `072` "What does Crimson Binding do?"); or a fanbook bullet
  sits outside the top-8 (Kamo `088` "What is Noritoshi's hobby?").
  Documented-open close is acceptable with the triage evidence (Kamo
  precedent).
- **G13/G11:** counterfactual-phrasing / location-scoped outcome sentences
  below the beam (same family).
- **Router edges (avoid these phrasings; if a natural question needs one
  and it fails, record it):** `end up` in the first 4 words (G4b
  story-verb head check — Kinji `079` observation); set-noun in a
  subordinate temporal clause ("when they were students" → the declared
  Students roster, 0 beats — Yaga `036`); yes/no battle-verb form ("Can
  X fight…?" → narrative — Tsukumo `083`, G8a covers scope-words not the
  battle-verb shape); past-tense "what happened to X" (deliberate G4b
  narrative design — Tsukumo `086`; prefer the wh-form "What stripped
  away…").
- If a NEW gap class appears: number it G-next (current max: G15), write
  the ENGINE GAPS entry, **stop the loop and checkpoint the user** with
  the finding + recommendation (defer to G5/R4 or fix as a release).

### 5.5 Pre-existing page-gen failures
Non-prose (`page-gen`) questions that fail for a non-engine reason (e.g.
the Nanami-alias set-gold class: gold is a comma-joined technique list, the
runtime serves the whole battle's interleaved roster — Mai Zenin `027`).
Classify, document in the character's report + handoff row, leave as-is.
They are outside this pass's scope. The character's bar is: **all `prose:`
questions pass** (modulo §5.4 documented-open).

### 5.6 Infrastructure errors
- **Server dead/stale:** restart recipe §7.4. If `scriptengine/` files
  changed since the server started, the server is stale — restart before
  any verification.
- **Double-BOM batch file:** reload with `utf-8-sig` after every
  bulk-add/retire edit; if it fails, strip the leading BOM and rewrite.
- **PowerShell:** §1 (temp `.py` files; UTF-16 from `>`; `;` not `&&`).
- **Type-check:** the repo is pyright-clean (see §0). After any engine edit,
  `npx -y pyright --pythonpath <venv python> scriptengine tests` must stay at
  0 errors. A lone "fastmcp could not be resolved" editor squiggle is a
  Pylance-environment artifact, not a defect.

## 6. Recheck protocol (how to keep the same quality)

- **Per character:** the §4 checklist is the exit gate. No character closes
  with an unclassified failure.
- **Every 5 characters (drift check):** re-run `page-run` on (a) the most
  recently completed character and (b) one random earlier character from
  the 20 done (e.g. `masamichi_yaga`, `kasumi_miwa`). Scores must NOT
  regress vs the handoff table; if one does, STOP and diagnose (server
  staleness, batch corruption, or index drift) before continuing.
- **After ANY engine change** (only happens when the user approves a G-n
  fix as a release — not during volume): the full gate procedure, in
  order: (1) named regression test in `tests/` (house style: one class per
  gap, sentence-named tests, the comment names the bug it guards);
  (2) `python -m scriptengine.cli audit --series jjk` (always before
  index); (3) `index --series jjk` (only if chunking/parsing changed —
re-parses stored wikitext, no re-crawl); (4) the gate triple —
   `pytest tests/ -q` (≥1072), `eval --series jjk` (24/24),
   `canon-run --series opm` (8/16, 235/237, 78.5%, "no change"), plus
   pyright 0 errors (`npx -y pyright --pythonpath <venv python> scriptengine
   tests`); (5)
  restart the server + freshness check; (6) re-verify the affected
  batches (for G15 that was: Kaito Yuki live probes + Hanako re-run →
  23/23). An engine change that drops any gate number is not done.
- **Server health one-liner** (venv python; poll, don't guess):
  ```powershell
  & $py -c "import urllib.request,json; h=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=120)); print(h['status'], h['device'], len(h['series']), h['started'])"
  ```
  Freshness: `started` (UTC) must be newer than the newest
  `scriptengine/**/*.py` mtime (compare against the local-time listing).
- **Handoff is the source of truth:** every character row, every G-n, every
  state update goes into `HANDOFF_PROSE_PASS.md` in house style. A
  character is "done" when its row exists.

## 7. Operations reference

### 7.1 Character order
`reports/page-campaign/jjk_character_order.json` → `order[31]` … `order[142]`
(112 characters; 0-based). Next 12: Kokichi Muta, Hiromi Higuruma, Uraume,
Momo Nishimiya, Takuma Ino, Ui Ui, Rika, Hana Kurusu, Yoshinobu
Gakuganji, Tsumiki Fushiguro, Naobito Zenin, Utahime Iori.

### 7.2 Commands (exact)
```powershell
& $py C:\Users\Nikhil\AppData\Local\Temp\opencode\prose_params.py "Kokichi Muta"
& $py C:\Users\Nikhil\AppData\Local\Temp\opencode\prose_dump.py "Kokichi Muta"
& $py C:\Users\Nikhil\AppData\Local\Temp\opencode\prose_bulk_add.py kokichi_muta C:\Users\Nikhil\AppData\Local\Temp\opencode\kokichi_muta_triples.json
& $py -m scriptengine.cli page-run --series jjk --batch kokichi_muta
& $py C:\Users\Nikhil\AppData\Local\Temp\opencode\prose_triage.py kokichi_muta "Kokichi Muta"
```
(page-run / triage from the repo root.)

### 7.3 Reports
Each `page-run` writes `reports/page-campaign/jjk-<slug>-<utcstamp>/`
(`REPORT.md` + `scores.json`). Name the final one in the handoff row.

### 7.4 Server restart recipe (only if dead or stale)
```powershell
Get-CimInstance Win32_Process -Filter "Name like 'python%'" | Where-Object { $_.CommandLine -like '*scriptengine.api.main*' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
$env:PYTHONPATH = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"
$env:PYTHONIOENCODING = "utf-8"
$env:SCRIPTENGINE_MODEL_IDLE_UNLOAD_SECONDS = "3600"
$py = "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine\scriptengine\.venv\Scripts\python.exe"
$p = Start-Process -FilePath $py -ArgumentList "-m","scriptengine.api.main" -WorkingDirectory "E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine" -RedirectStandardOutput "C:\Users\Nikhil\AppData\Local\Temp\opencode\server_<ts>.log" -RedirectStandardError "C:\Users\Nikhil\AppData\Local\Temp\opencode\server_<ts>.err.log" -WindowStyle Hidden -PassThru
Start-Sleep -Seconds 120
& $py -c "import urllib.request,json; h=json.load(urllib.request.urlopen('http://127.0.0.1:8000/health',timeout=180)); print(h['status'], h['device'], len(h['series']), h['started'])"
```
GPU model load takes 1–4 min — poll health, don't declare it stuck before
~2 min. Verify: status ok, cuda, 8 series, `started` > newest `.py` mtime.

## 8. After the 132 (not now — user decision)
The campaign's remaining page types: **episodes (59 pages — template ready
at `reports/page-campaign/episode_prose_template.md`: uniform 11-section
layout, Plot Details is the 402 KB prose mass but EMPTY on Ep 53–59,
route-two title sourcing)**, battles (90), techniques (149), other.
Only start a wave when told to.

## 9. Resume right now
`order[31]` = **Kokichi Muta**. Its batch (`questions/_jjk_page_kokichi_muta.json`)
is untouched — a previous subagent was cancelled before adding anything
(verify with `prose_params.py`: expect 0 prose questions). Then
`order[32]` Hiromi Higuruma, `order[33]` Uraume, … in order, until told to
stop. Checkpoint the user ONLY on engine-level findings (a new G-n, or a
proposed engine fix) — never per character, and never for the routine
work above.