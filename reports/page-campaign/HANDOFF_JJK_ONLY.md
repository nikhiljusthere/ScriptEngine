# HANDOFF — ScriptEngine JJK Page Campaign (start here in a fresh session)

## 0. Environment & commands
- Repo: `E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine` (git). Windows PowerShell 5.1; **no `&&`** — use `cmd1; if ($?) { cmd2 }`.
- Python: always call the venv interpreter directly: `& "E:\...\ScriptEngine\scriptengine\.venv\Scripts\python.exe"`, with `$env:PYTHONPATH="E:\VS_CODE\Midnight_Render\Softwares\ScriptEngine"` set first.
- **Always set `$env:PYTHONIOENCODING="utf-8"` before any `page-run`/eval** — Windows cp1252 stdout crashes on macrons (e.g. ū) mid-run; the crash loses all output after that line.
- PowerShell inline `-c` python breaks on quotes → put throwaway scripts in `C:\Users\Nikhil\AppData\Local\Temp\opencode\*.py`.
- Server: start with `python -m scriptengine.api.main` (serves :8000); health at `/health` must show `"device":"cuda"` and the series list incl. `jjk`. The server's `started` timestamp is compared against code mtimes by `canon-run`; **restart it after any engine edit**.
- Core loop: `python -m scriptengine.cli page-run --series jjk --batch <slug>` (loads `questions/_jjk_page_<slug>.json`, scores vs live server, writes `reports/page-campaign/<run>/REPORT.md`). Exit 0 = 100%, 2 = failures remain.
- Gates after any engine change: `python -m scriptengine.cli eval --series jjk` (must stay **24/24**) and `python -m pytest tests/ -q` (baseline **985 passed** as of 2026-08-21; pre-existing LSP type errors in `roster.py` ~898/~3261/~3631 and `test_roster.py:143` are NOT regressions — ignore them).

## 1. What ScriptEngine is (engine mental model)
- Ingests a Fandom wiki via MediaWiki API; **nothing about a series is hardcoded** in `.py`. Type discovery is structural (infobox = template transcluded before first heading with most named params, once per page). Per-wiki vocabulary lives in `series/<name>/overrides.yaml` (rosters, citation grammar, subject ranking/demotions).
- Layout: `ingest/` (crawler, wikitext parser, ontology), `stores/` (SQLite facts+graph+FTS5; Qdrant local vectors), `index/` (section chunking + embeds), `retrieve/` (**router**, hybrid=qa, narrative, roster, citations), `api/` (FastAPI :8000, `/context` is the endpoint that matters), `eval/` (gold bank + scoring).
- **Three retrieval modes return structurally different bundles:**
  - `roster` → `members` list (enumeration)
  - `qa` → hybrid BM25+vector+graph passages + facts, cross-encoder reranked — **this mode is phrasing-invariant for fact lookups** (same content words → same passage)
  - `narrative` → ordered beats walked from the subject's page
- **Router rules** (`scriptengine/retrieve/router.py`, order matters):
  1. `chronology.wants_chronology(query)` → roster
  2. `_COUNT` = `\bhow many\b` anywhere → roster ← **misroute #1**
  3. interrogative (`_WH`: what/who/which/when/where/why/how at start) AND not plural_ask AND not story-verb-in-first-4-words AND subject_type ∉ {event, media} → qa (subject from ontology via `rank_subjects` + possessive-owner boost; no subject → qa anyway)
  4. `looks_like_enumeration(query)` (roster.py `_ENUMERATION`) → roster
  5. `_PLURAL_WH` = `^(who|what|which)\s+(are|were)\b` → roster ← **misroute #2**
  6. interrogative + story verb → narrative; subject_type ∈ {event, media} → narrative
  7. bare name ≤4 words → qa; default → narrative
- `main.py:210`: auto-routed roster with zero members falls back to narrative (safety net, not a strategy).
- **Scoring** (`scriptengine/eval/canon_gold.py`): sets pass when returned members == gold exactly. Facts pass when every gold item is present in the normalized bundle haystack — `norm()` = NFKD-strip diacritics, lowercase, &→and, non-alnum→space, plural-fold; match = **word-boundary containment** (so "December 24th, 2018" ≠ "December 24, 2018"; gold must mirror the page's exact wording). Fact items support `aliases`; `accept:"all"` (default) requires every item present, `accept:"any"` one. **`expect_mode` in batches is metadata only — never used for scoring.**
- Batch schema (`scriptengine/eval/questions.py`): file `_jjk_page_<slug>.json`, fields per question: `id, kind(set|fact), question, subject, tier(wiki), expect_mode, scope, answer[{item, aliases?}], sources[], verified, note?`. Batches are excluded from the official bank by the `_` prefix.

## 2. Campaign state (JJK only — other series come later with their own declarations)
- **SCOPE RESTRICTION: For now, work only on Jujutsu Kaisen (JJK) and its wiki. Do not work on, ingest, test, or optimize any other series/wiki yet. Other wikis are deferred until their own campaign is explicitly started.**
- **Page 1 (Yuji Itadori): DONE 100/100** (`questions/_jjk_page_yuji_itadori.json`; row in `reports/page-campaign/STATUS.md`).
- **Page 2 (Culling Game Arc): IN PROGRESS — last live run 94/100**, all 6 roster sets EXACT. Run folder: `reports/page-campaign/jjk-culling_game_arc-2026-08-19-0545/REPORT.md`.
  - 6 rosters declared in `series/jjk/overrides.yaml` (colony player grids; wiki's category is incomplete — 20 of 31 infobox names). All build perfectly.
  - **6 open fact misses to triage** (gold-error vs engine-gap): "Chapter 143 – Chapter 271" (manga chapters), "lethal battle royale", "he is not the game master" (binding vow), "Tengen's possession" (back of Prison Realm), "Chō Chōfuku Dōka" (Great Merger romaji — check NFKD folding vs page text), "November 14th" (foreign military operation).
- Page order after: Shibuya Incident → Sukuna → Megumi → Gojo → Yuta → Volumes & Chapters → Maki, Story Arcs, Kenjaku, Choso, RCT, Toji, Ten Shadows, Nobara.
- Corpus for gold verification: `series/jjk/wikitext/*.json` (field `wikitext`) — **always verify a gold phrase exists verbatim on the page that will be walked/retrieved before scoring**.

## 3. The plan (JJK-first; each later anime gets its own overrides/declarations, never .py changes)
**Goal:** (a) redesign the Page-2 batch so facts ask for **lists of answers**, **passage like answers** and **reasoning type** not one-word lookups — exactly 100 questions, `accept:"all"`, merge related singletons into compound facts; fold in the 6 misses. (b) Make routing **phrasing-robust**: however a fact is phrased ("How many wards…" vs "What number of wards…") it must return the same accurate result — no wh-specific question design.

**Phase A — router fix, JJK-scoped, guarded.** In `router.py`: rules 2 and 5 currently force roster on *any* "how many" / "who|what|which are|were". Change both so they route to roster **only when a set actually resolves for the subject**; otherwise counting/plural fact questions fall through to rule 3 (`qa`), which is phrasing-invariant. True enumeration ("Who were the players of Tokyo No. 1 Colony?") must stay on roster — that subject enumerates, so it keeps working. Any JJK-specific residue (e.g. a type that should never be a roster subject) goes in `series/jjk/overrides.yaml` with a comment naming the question, **not** in `.py`.
Guard before touching the batch: restart server → `eval --series jjk` stays 24/24 → full pytest green (985) → offline routing audit of all 100 current questions confirms no set flips off roster and no fact lands on an empty roster. If eval regresses, stop and re-scope; do not ship a regression to make one phrasing work.

**Phase B — batch redesign.** Rewrite the 94 facts as multi-part (2–3 items each from the same page/passage), `accept:"all"`, keep total at exactly 100, fix the 6 misses during the rewrite (verify every gold phrase verbatim in `series/jjk/wikitext/`; watch NFKD folding and "th"-suffix date forms). Keep the 6 roster sets as-is.

**Phase C — drive to 100%.** Re-run `page-run` until **100/100** (re-runs are expected and fine — 100% accuracy on JJK is the goal; we have full knowledge of this corpus). Triage each miss: gold error → fix batch; engine gap → declare in `series/jjk/overrides.yaml`. Final gates: eval 24/24 + pytest green. Record page-2 row in `reports/page-campaign/STATUS.md`.

**Deferred (do NOT build now):** typo forgiveness ("yoji itadori" → "I think you meant Yuji Itadori…") — the engine has no spelling-correction layer and natural correction phrasing needs an LLM front-end; record as a follow-up.
