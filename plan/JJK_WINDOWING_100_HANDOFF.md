# JJK WINDOWING-100 — Day 2/3 HANDOFF (2026-09-30)

The single self-contained brief for a fresh session to continue the windowing-100
work. Written to be followed with no transcript. Read this, then
`plan/COUNCIL_WINDOWING_100_DEFINITION.md` §"The Recommendation" (the authoritative
spec), then the top entries of `plan/SWITCHPOINT.md` (the machine state log).

## 1. What this is

The 2026-09-30 windowing council (full transcript: `plan/COUNCIL_WINDOWING_100_DEFINITION.md`;
chairman's verdict = the spec) settled: **windows are VIEWS over the index's sentence
grid, never character slices.** One sub-topic per window, packed to a 2,000-char cap
with a 250-char whole-sentence carry ⇒ every quote ≤ 1,750 chars is G1-safe across
every cut (gold's longest quote is 231 — zero boundary loss; anything longer fails
the window-level G1 loudly instead of being attributed to sentences that don't cover it).
Window ids are gen-scoped 16-hex (stable within a generation; the re-keyable invariant
is a window's `hashes` list, not the id).

- **Day 1 — DONE, committed `1397ec34`:** `scriptengine/ingest/windows.py` (pure
  builder: sub-topic itemization, greedy pack, `CURRENT_GEN = 2`) +
  `tests/test_windows.py` (22 tests incl. the strict G1 envelope) +
  `tools/train/window_delta_report.py` (zero-LLM process gate: JJK real store,
  5,507 sections / 49,392 sentences, 0 gaps; **6,025 old (4000/300 char-sliced) →
  14,987 new grid windows (+8,962, ~2.5×)** — the scale-out cost delta).
- **Day 2 — engine integration: NOTHING written** (section 3.1 below).
- **Day 3 — data tooling: NOTHING written** (section 3.2). The from-scratch
  windowing *run* (35B A3B, pools + 333/2,265 empty re-reads) is the data phase
  AFTER Day 2+3 code is green; the owner's standing plan is the 35B takeover
  then (section 5).

## 2. State at handoff (measured 2026-09-30 ~07:35)

- **Model: 27B NVFP4 on `:18080`, FULL 262k profile** — `qwen_mode.txt` =
  `mode=262k ctx=262144 qwen_pid=554468`, `:18080/health` ok. Owner directive this
  morning: "update the opencode json to full context" ⇒ `ninfer-27b`
  `limit.context` = **262,144** in BOTH `ScriptEngine/opencode.json` and
  `~/.config/opencode/opencode.jsonc` (committed `5ef0cef9`; the switcher
  `qwen-switch.sh` re-syncs both on every switch).
  Consequence: 262k's ~3.4 GiB headroom is below the ~5.3 GiB the CUDA
  embedder+reranker need, so **`:8000` stays OFF at 262k** — the canon gate has
  to run at 100k (`~/ninfer-work/qwen-switch.sh 100k` re-co-locates `:8000`).
- Q8 `:8090` DOWN (watchdog killed at the Q8→NVFP4 switch). 35B `:18081` DOWN and
  its watchdog (`tools/train/ops/ninfer35_watchdog.sh`) STOPPED — do not restart
  it while the 27B holds the card.
- **Day-2 gate baseline captured** (`reports/2026-09-30T0720_day2-baseline/`):
  - pytest: **9 failed / 1,481 passed / 2 xpassed** — the 9 are PRE-EXISTING
    (test_blind_panel_universe 1, test_continuity 3, test_mcp_server 3,
    test_timeaxis 2 — caused by the owner's in-progress tree, not the builder;
    pass count = pre-builder baseline + 22 window tests).
  - eval jjk: **31/31 (100%)** (CPU; the QdrantClient `__del__` traceback in the
    log tail is a harmless interpreter-shutdown warning).
  - span-recall jjk: **48,572/48,572 · 0 unreachable · 100%** — byte-saved under
    `reports/2026-09-30T0720_day2-baseline/span_recall_jjk/` for the post-change
    byte-diff (it must come out BYTE-IDENTICAL after the engine change).
  - **canon opm: NOT RUN** — needs `:8000` (down). Baseline target
    10/16 · 236/236 · 79.0%; get it at 100k before declaring the gates done.
- Git: `5ef0cef9` (switchpoint + 262k record) on `character-scoped-questions`.
  The working tree carries the OWNER'S in-progress work — always commit with an
  explicit pathspec, never `git add -A`.

## 3. The remaining work (exact list)

### 3.1 Day 2 — engine integration (no code written yet)

The builder API (`scriptengine/ingest/windows.py`):
`build_windows(page, section, text, *, gen=1, cap_chars=2000, carry_chars=250)
-> list[Window]`; `Window(id, gen, page, section, sub, s_start, s_end, hashes,
text)` with `.chars`, `.quote_span`; plus `quote_sentence_span(text, quote)` /
`quote_grid_span(text, quote)` (verbatim quote → grid ordinals; `None` when the
quote isn't verbatim — the window-level G1's point) and `sentence_spans` /
`section_subtopics`.

1. **Replace `_windows` (4000/300 char slice, `abilities.py:472`) with grid
   windows at every engine caller:**
   - `abilities.py:392` — the extraction loop in `extract_from_passages`
     (`passage=window` in the prompt).
   - `relations.py:320` — its window loop + the window-level `_quoted_in` check
     (moves to grid windows automatically).
   - `narrative_abilities.py:136, 212` — the report's window loop.
   - `events.py:2421` — the packed-reads branch: **retire the pack entirely**
     (`_pack_chars()` defaults to 0 = the path is already dormant; the council
     ruled "smaller pages can be read in whole" is superseded) ⇒ every passage
     is read as its own labeled grid windows; the stored row shape is unchanged
     (a packed read stored the same shape as a per-passage one).
   - `cli.py:456, 469` — the cost estimator must count grid windows, not
     4,000-char windows.
   - `tools/train/window_delta_report.py:26` KEEPS its `_windows` import —
     deliberate (it reports old-vs-new). Keep it working during the transition;
     delete `_windows` + `tests/test_ability_extraction.py`'s `TestWindows`
     block + the delta tool together only after the pools are superseded.
   - Bump the prompt version(s) whose passage semantics changed (events'
     `PROMPT_VERSION`; check the abilities/relations `_TEMPLATE`s).
2. **G1 → window level.** The quote-verbatim check must run against the WINDOW
   text actually read, not the passage:
   - `events.py` `validate_phase1_rows` (~line 606) and the row-anchoring step
     (~line 2544: the holder's anchor matches the row's quote against the
     *passage* text — must match against the *window* text; attribute onto
     sentences via `quote_sentence_span` → the row's `quote_span`).
   - `tools/events_gates.py` G1 (`quoted_in`, ~line 73) — same change at the
     gate level. G5 (20-char soft floor) is report-only, unchanged.
3. **Re-spec the two pack tests** `tests/test_events_tgap.py:203, 222`
   (pack retired ⇒ always read per-passage).
4. **The small mechanical wiki_card fix (council correction #3, "fix now"):**
   `tools/train/verify_row_wiki.py` — its `describe()` unconditionally joins the
   live `status`/`race` facts, so the card says end-of-series status ("Deceased")
   even for early-story passages. Fix the mechanical leak now (the card must not
   assert end-of-series status into early-story context); the chapter-scoped
   status lookup (status-as-of-chapter-N) is a separate track and does NOT block.
5. **The four standing gates, baseline-exact** (`scriptengine-gates` skill):
   pytest 9F/1481P/2XP · eval jjk 31/31 · span-recall jjk BYTE-IDENTICAL to
   `reports/2026-09-30T0720_day2-baseline/span_recall_jjk/` · canon opm
   10/16 · 236/236 · 79.0% (baseline it at 100k first — see section 2).

### 3.2 Day 3 — data tooling (no code written yet)

6. **`tools/train/emit_windows.py`** — regenerate the 3×500 verify pools from
   the new grid (labeled grid windows, the pools the 35B campaign reads).
   **Supersede, don't salvage**: ~117/1,500 "verified" rows are unproven on the
   old grid — re-running those 117 verifications is cheaper than proving
   salvage safe.
7. **`tools/train/rekey_gold.py`** — re-key the gold rows by
   `sentence_content_hash` (chunker.py:137; the builder mirrors it in
   `Window.hashes`) so gold survives re-ingests; the 333 empty adjudications
   get re-read (they were judged on contaminated multi-topic windows) — that
   re-read is the 35B data phase, not coding.

## 4. Standing rules & traps

- **Gates:** the four standing gates (`scriptengine-gates` skill) before
  declaring any pass done and after any engine change, baseline-exact on JJK;
  span-recall is byte-saved + byte-diffed, never eyeballed.
- **GPU is single-tenant:** the 27B holds the card. Never load a second model
  beside it. To run the canon gate: `~/ninfer-work/qwen-switch.sh 100k`
  (re-co-locates `:8000`), gate, then back to `262k`.
- **35B takeover (after Day 2+3 green):** unload the 27B
  (`~/ninfer-work/ninfer-stop.sh` — it writes `mode=off`, preventing poller
  resurrection), `tools/train/ops/serve_35b.sh` (**build35** binary — the
  v3-artifact trap: `ninfer/build/` refuses it with "artifact magic is not
  NInfer v2"), restart `tools/train/ops/ninfer35_watchdog.sh`, and REBIND THE
  SESSION ROW to `ninfer-35b/qwen3.6-35b-a3b-ninfer` (opencode resumes the model
  STORED ON THE ROW, not the config default). The 35B answer-budget trap still
  applies: empty content + `finish_reason: length` ⇒ RAISE the budget (20,480),
  never lower it. (Switch steps from the 06:0x/04:0x switchpoint entries.)
- **Kill discipline:** by exact PID, watchdog FIRST; never a broad `pkill -f`
  (it has killed the controlling shell before).
- **Model names live in the serve scripts** — copy, never retype.
- **Git hygiene:** owner's in-progress tree — explicit pathspecs only; the
  `D series/{berserk,bleach,db,hxh,onepiece}/overrides.yaml` in `git status`
  are symlink artefacts, byte-identical to HEAD — NEVER commit those deletions;
  `opencode.json` is gitignored (the switchpoint is the on-disk record).
- **Switchpoint:** add a hand-written entry (and commit) BEFORE any model
  switch; `qwen-switch.sh` appends its machine line afterwards.

## 5. First actions on resume

1. `curl -s http://127.0.0.1:18080/health` + `cat ~/ninfer-work/qwen_mode.txt`
   (expect `{"status":"ok"}` + `mode=262k ctx=262144`; if dead: `tail
   ~/ninfer-work/logs/serve.log`, relaunch `cd ~/ninfer-work && setsid nohup
   ./serve.sh > logs/serve.log 2>&1 &` — 262k is `serve.sh` itself; 100k is
   `./serve_100k.sh`).
2. Read this doc + `plan/COUNCIL_WINDOWING_100_DEFINITION.md` §"The
   Recommendation" + the top entries of `plan/SWITCHPOINT.md`.
3. If the owner says continue: **Day 2 item 1 first, TDD** — a test that pins
   the new behavior at one caller, then the replacement, caller by caller
   (abilities → relations → narrative_abilities → events → cli), gates after
   each slice, span-recall byte-diff at the end. Then item 2 (G1), 3 (pack
   tests), 4 (wiki_card), 5 (four gates baseline-exact), then Day 3 (6, 7).
4. Day 2+3 complete AND gates green ⇒ the owner's standing plan: 35B A3B on
   `:18081` for the windowing-from-scratch run (section 4 takeover steps).