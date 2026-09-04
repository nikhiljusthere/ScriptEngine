# Character Synopsis Wave Ledger (density-switched 2026-09-03, State 105)

Protocol (2026-09-03 17:38, current — see event log): **one to two questions
per non-empty section** (skip `Navigation` / `References` / `See Also` /
`External Links`), ~1.5 per section; every section gets at least one, a
second only where it carries two genuinely distinct facts. **One dispatch per
page group** (25–40 questions, section-count-descending order, D1–D16 below);
strictly sequential, one subagent at a time. The "lose nothing" guard —
span-recall sees verbatim lines, so each question must earn its place on what
it structurally cannot see: (1) **natural human phrasing** (how a person
actually asks, not a reworded lift), (2) **tight answer span** (the specific
verbatim span, not the whole sentence containing it), (3) roster /
closed-set — **N/A for this wave** (verified 2026-09-03: all 835 roster/set
questions sit on character/technique/event pages, page-gen-generated, zero on
character_synopsis; standing check before any future page type — the chapter
tranche is flagged). At most one R5 yes/no per page; no double-barrelled
questions. Verbatim-only (the `add` gate enforces it); per-dispatch
checkpoint = orchestrator verbatim re-check vs facts.db + `page-run` (GPU)
for **every page touched**, to 100% (or diagnose the root cause: gold error
→ fix the batch; engine gap → document in HANDOFF's ENGINE GAPS + continue,
question stays active and failing). **Never reword a question to dodge a
failure.** Session loop: at the start of each session run
`python -m scriptengine.cli span-recall --series jjk` (offline, <1 s, no
server); exit 2 with only the two known `Chapter 239 / References` lines =
expected (the known Trivia/References chunking gap), anything else = the
index changed under the wave → stop and report. **The Yuji (280) and Mai (16)
pages are frozen — never retire or rewrite their questions; they stay as
regression coverage.**

## Yuji Itadori (24,555 w) — slug `yuji_itadori_synopsis`, batch `questions/_jjk_page_yuji_itadori_synopsis.json` — **PAGE COMPLETE (280 questions, 12/12 units; final page-run 279/280, the 1 miss = #111 G25) — FROZEN (old-protocol historical record; questions stay as regression coverage)**

| unit | section | words | status | ids | q's |
|---|---|---:|---|---|---:|
| 1 | Fearsome Womb Arc + History | 2,389 | **done** | 001–027 | 27 (24 Fearsome Womb + 3 History; R5 = #027) — orchestrator re-check: 27/27 verbatim vs facts.db, gate first-run pass |
| 2 | Vs. Mahito Arc | 868 | **done** | 028–037 | 10 — orchestrator re-check: 10/10 verbatim vs facts.db, gate first-run pass |
| 3 | Kyoto Goodwill Event Arc | 710 | **done** | 038–045 | 8 — orchestrator re-check: 8/8 verbatim vs facts.db, gate first-run pass |
| 4 | Death Painting Arc | 705 | **done** | 046–053 | 8 — 8/8 verbatim; whole-batch `page-run` **53/53** @16:52 (68 s on GPU — CUDA smoke test passed) |
| 5 | Shibuya Incident Arc | 3,311 | **done** | 054–091 | 38 — 38/38 verbatim; whole-batch `page-run` **91/91** @16:56 (102 s on GPU) |
| 6 | Culling Game Arc (sub 1/3) | 3,263 | **done** | 092–129 | 38 — 38/38 verbatim; whole-batch `page-run` **128/129** @17:06 (175.5 s on GPU; the 1 miss = #111, router gap **G25 (OPEN)** documented in HANDOFF's ENGINE GAPS — question stays active, fails on every run until the router fix) |
| 7 | Culling Game Arc (sub 2/3) | 3,271 | **done** | 130–166 | 37 — 37/37 verbatim (orchestrator re-check vs facts.db) |
| 8 | Culling Game Arc (sub 3/3) | ~3,287 | **done** | 167–203 | 37 — 37/37 verbatim (orchestrator re-check vs facts.db; #167's answer opens at the recorded 3/3 boundary) |
| 9 | Shinjuku Showdown Arc (sub 1/2, P1–P10) | 2,502 | **done** | 204–231 | 28 — 28/28 verbatim (orchestrator re-check vs facts.db) |
| 10 | Shinjuku Showdown Arc (sub 2/2, P11–P20) | 2,166 | **done** | 232–256 | 25 — 25/25 verbatim (orchestrator re-check vs facts.db) |
| 11 | Epilogue | 81 | **done** | 257 | 1 — 1/1 verbatim (orchestrator re-check vs facts.db) |
| 12 | Modulo | 1,998 | **done** | 258–280 | 23 — 23/23 verbatim (orchestrator re-check vs facts.db) → completion page-run **279/280** @17:30 (GPU; the 1 miss = #111, G25) |

Sub-chunk boundaries (first fragment of sub 2/3, 3/3, 2/2) recorded here by
the unit that starts the arc:

- Culling Game 2/3 starts at: `After the pair accept the deal, Yuji tells Megumi that all the bluffing he's done was risky, who tells Yuji that it isn't.` (paragraph 23/64; sub 1/3 = paragraphs 1–22, 3,263 w)
- Culling Game 3/3 starts at: `Now inside the barrier, Yuji falls from the sky and wonders where Megumi is.` (paragraph 47/64; sub 2/3 = paragraphs 23–46, 3,271 w; chosen by unit 6 at authoring time, recorded here)
- Shinjuku 2/2 starts at: `Sukuna then asked if there was a point to seeing any of these memories but Yuji stated there were a few places he wanted to go.` (paragraph 11/20; sub 1/2 = P1–P10, 2,502 w; sub 2/2 = P11–P20, 2,166 w; recorded from the unit 9/10 authoring)

## Later pages — DISPATCH PLAN D1–D16 (70 pages, 312 sections, ~469 questions; SUPERSEDES the old per-page unit lists)

One dispatch = one subagent, strictly sequential. Per dispatch: author every
page in the group (1–2 questions per non-empty section), `add` each (gated),
orchestrator re-check, then `page-run` (GPU) for **each page** touched.
Slugs: `<name>_synopsis`; batches: `questions/_jjk_page_<name>_synopsis.json`
(ids continue per page from its current max — all 70 are 0, except none).

| D | pages (sections) | planned q's | status |
|---|---|---:|---|
| 1 | Maki Zenin (10), Panda (10) | 30 | **done** (17+17 = 34 q's; page-runs 16/17 + 15/17 — the 3 misses = documented-open **G26** (Panda #012, #015: past-tense "what happened to <character>" routes narrative) + **G27** (Maki #015: qa section-order budget truncation of tail sections; Maki #015 also G26's trigger). Orchestrator re-check: 34/34 verbatim vs facts.db, structure clean, ids sequential 001–017 each. Gaps in HANDOFF ENGINE GAPS; questions stay active+failing) |
| 2 | Satoru Gojo (10), Shoko Ieiri (10) | 30 | **done** (16+12 = 28 q's; page-runs 16/16 (Gojo, 100%) + 11/12 (Shoko — the 1 miss = #009, a **G25 instance 2**: "Why did Shoko start smoking…?" — the question's "start" hits `_NARRATIVE_VERBS`, character subject keeps the narrative read, episode stream omits the Synopsis prose; served under forced qa). Orchestrator re-check: 28/28 verbatim vs facts.db, structure clean, ids sequential 001–016 / 001–012) |
| 3 | Kenjaku (8), Kiyotaka Ijichi (8), Mahito (8) | 36 | **done** (12+10+11 = 33 q's; page-runs **12/12 + 10/10 + 11/11 = 33/33, clean sweep — three consecutive 100% pages**; Mahito's Modulo question #011 passed at the default budget, no G27 trigger. Orchestrator re-check: 33/33 verbatim vs facts.db, structure clean, ids sequential 001–012 / 001–010 / 001–011) |
| 4 | Masamichi Yaga (8), Megumi Fushiguro (8), Nobara Kugisaki (8) | 36 | **done** (10+11+10 = 31 q's; page-runs 10/10 + 10/11 + 10/10 — the 1 miss = Megumi #011 "Did Megumi die by 2087?" (Modulo, 13 w), a **G27 instance 2**: even forced qa at tb=12000 (50 beats) doesn't reach Modulo on this 4,301-w-Culling-Game page; present at tb=30000 (107 beats). Nobara's Epilogue + Modulo questions (G27-watch) both PASSED. Orchestrator re-check: 31/31 verbatim vs facts.db, structure clean, ids sequential 001–010 / 001–011 / 001–010) |
| 5 | Sukuna (8), Yuta Okkotsu (8), Aoi Todo (7) | 35 | **done** (12+12+10 = 34 q's; page-runs **12/12 + 12/12 + 10/10 = 34/34, second clean sweep** — every G27-watch tail question passed at the default budget: Sukuna #011/012 inside the 10,083-w Shinjuku section, Yuta's Epilogue + Modulo, Aoi's Modulo. Orchestrator re-check: 34/34 verbatim vs facts.db, structure clean, ids sequential 001–012 / 001–012 / 001–010) |
| 6 | Choso (6), Kasumi Miwa (6), Mei Mei (6), Momo Nishimiya (6) | 36 | **done** (9+7+8+8 = 32 q's; page-runs **9/9 + 7/7 + 8/8 + 8/8 = 32/32, third clean sweep**. Orchestrator re-check: 32/32 verbatim vs facts.db, structure clean, ids sequential 001–009 / 001–007 / 001–008 / 001–008) |
| 7 | Toge Inumaki (6), Utahime Iori (6), Yoshinobu Gakuganji (6), Kento Nanami (5) | 35 | **done** (8+7+8+7 = 30 q's; page-runs **8/8 + 7/7 + 8/8 + 7/7 = 30/30, fourth clean sweep** — the G25-watch (nanami-004) and G27-watch (nanami-007, tail on a short page) both passed. Orchestrator re-check: 30/30 verbatim vs facts.db, structure clean, ids sequential 001–008 / 001–007 / 001–008 / 001–007) |
| 8 | Kokichi Muta (5), Noritoshi Kamo (5), Takuma Ino (5), Tsumiki Fushiguro (5) | 32 | **done** (7+7+7+6 = 27 q's; page-runs **7/7 + 7/7 + 7/7 + 6/6 = 27/27, fifth clean sweep** — Tsumiki's G27-watch tail passed on its short page. Orchestrator re-check: 27/27 verbatim vs facts.db, structure clean, ids sequential 001–007 / 001–007 / 001–007 / 001–006) |
| 9 | Uraume (5), Akari Nitta (4), Atsuya Kusakabe (4), Hana Kurusu (4), Hanami (4) | 32 | **done** (7+5+6+6+5 = 29 q's; page-runs **7/7 + 5/5 + 6/6 + 6/6 + 5/5 = 29/29, sixth clean sweep** — Hana's G27-watch Modulo question passed on its short page. Orchestrator re-check: 29/29 verbatim vs facts.db, structure clean, ids sequential 001–007 / 001–005 / 001–006 / 001–006 / 001–005) |
| 10 | Jogo (4), Kinji Hakari (4), Riko Amanai (4), Suguru Geto (4), Tengen (4) | 30 | **done** (6+7+5+6+5 = 29 q's; page-runs **6/6 + 7/7 + 5/5 + 6/6 + 5/5 = 29/29, seventh clean sweep** — Riko's G27-watch tail passed on its short page. Orchestrator re-check: 29/29 verbatim vs facts.db, structure clean, ids sequential 001–006 / 001–007 / 001–005 / 001–006 / 001–005) |
| 11 | Toji Fushiguro (4), Ui Ui (4), Yu Haibara (4), Yuki Tsukumo (4), Charles Bernard (3) | 28 | **done** (6+6+4+5+4 = 25 q's; page-runs **6/6 + 6/6 + 4/4 + 5/5 + 4/4 = 25/25, eighth clean sweep** — the single first-run miss (toji-001) was a **G25-class** story-verb misroute ("end up" hits `_NARRATIVE_VERBS`) fixed by the house static-qa rephrase (Ogi Q133 / geto-002 precedent); all G27-watch tails passed on their short pages. Orchestrator re-check: 25/25 verbatim vs facts.db, structure clean, ids sequential 001–006 / 001–006 / 001–004 / 001–005 / 001–004) |
| 12 | Dagon (3), Eso (3), Fumihiko Takaba (3), Hagane Daido (3), Hajime Kashimo (3) | 25 | **done** (4+4+4+5+5 = 22 q's; page-runs **4/4 + 4/4 + 4/4 + 5/5 + 5/5 = 22/22, ninth clean sweep** — first-run, zero misses; all G27-watch tails (dagon-004, eso-004, fumihiko-004, kashimo-004/005) passed. Orchestrator re-check: 22/22 verbatim vs facts.db, structure clean, ids sequential 001–004 / 001–004 / 001–004 / 001–005 / 001–005) |
| 13 | Haruta Shigemo (3), Hiromi Higuruma (3), Kechizu (3), Mimiko Hasaba (3), Nanako Hasaba (3) | 25 | **done** (4+6+4+4+4 = 22 q's; page-runs **4/4 + 6/6 + 4/4 + 4/4 + 4/4 = 22/22, tenth clean sweep** — first-run, zero misses; all G27-watch tails (hiromi-005/006 in a ~3.3k-w page tail, mimiko-004/nanako-004 in ~0.9k-w tails) passed — even the ~3.3k-w Hiromi page served its tail beats, reinforcing the G27 pattern. Orchestrator re-check: 22/22 verbatim vs facts.db, structure clean, ids sequential 001–004 / 001–006 / 001–004 / 001–004 / 001–004) |
| 14 | Naobito Zenin (3), Rika Orimoto (3), Rokujushi Miyo (3), Toshihisa Negi (3), Yorozu (3) | 25 | **done** (5+5+4+4+4 = 22 q's; page-runs **5/5 + 5/5 + 4/4 + 4/4 + 4/4 = 22/22, eleventh clean sweep** — first-run, zero misses; all G27-watch tails (rika-005 Modulo 22 w, miyo-004 Shinjuku 110 w, toshihisa-003/004 Shibuya 178 w, yorozu-004 Culling Game 343 w) passed on their short pages. Orchestrator re-check: 22/22 verbatim vs facts.db, structure clean, ids sequential 001–005 / 001–005 / 001–004 / 001–004 / 001–004. Slug note: `rika_orimoto_synopsis` (not `rika_oremoto`).) |
| 15 | Dabura Karaba (2), Jiro Awasaka (2), Junpei Yoshino (2), Kirara Hoshi (2), Kou Usami (2), Kurourushi (2), Manami Suda (2), Miguel Oduol (2), Naoya Zenin (2) | 27 | **done** (4+2+3+3+3+3+2+2+3 = 25 q's over 9 pages; page-runs **4/4 + 2/2 + 3/3 + 3/3 + 3/3 + 3/3 + 2/2 (D15a+D15b @1847) + 2/2 + 3/3 (D15c @1849) = 25/25, thirteenth clean sweep** — first-run, zero misses; all G27-watch tails (naoya-002/003 in a ~1.75k-w page, kirara-003, kou-002/003, kurourushi-002/003, dabura-004, junpei-002/003, jiro-002, manami-002, miguel-002) passed. Orchestrator re-check: 25/25 verbatim vs facts.db, structure clean, ids sequential per page. Note: D15a (Dabura+Jiro+Junpei) + D15b (Kirara+Kou+Kurourushi+Manami) + D15c (Miguel+Naoya) ran as three subagents; D15a/D15b verified+ran first, then D15c appended to complete the 9-page D15.) |
| 16 | Ogami (2), Ogi Zenin (2), Reggie Star (2), Ryu Ishigori (2), Takako Uro (2), Tsurugi Okkotsu (1) | 17 (tail) | **done** (2+2+3+3+3+2 = 15 q's; page-runs **2/2 + 2/2 + 3/3 + 3/3 + 3/3 + 2/2 = 15/15, fourteenth clean sweep** — first-run, zero misses; all G27-watch tails (reggie-002/003 in a ~1.45k-w page, takako-002/003, ryu-003, ogami-002, ogi-002) passed. Orchestrator re-check: 15/15 verbatim vs facts.db, structure clean, ids sequential per page. takako_uro page's stored "Synoposis" breadcrumb typo handled (spec used the normal L3 section titles). Tsurugi (single-section page) carries 2 q's. **D16 is the final dispatch — the character_synopsis prose wave is COMPLETE.**) |

**Standing roster check (before any future page type, not just this one):**
confirm the type has no closed-set sections, or that page-gen roster coverage
already exists for it, before reducing density on it. **Chapter pages have
`Characters in Order of Appearance` and `Battles & Events` (closed sets) —
the chapter tranche (304 pages / 1,689 sections / ~2,500 questions at
1.5/section) does not start (on the old or the new density) until that check
is done for it.**

## Event log (append-only)

- 2026-09-03 16:50 — API restarted on **CUDA** (PID 11367; health
  `"device":"cuda"`). Basis: ninfer-serve (Qwen 27B, PID 3574) holds
  25,546/32,607 MiB but at 0% utilization with a PREALLOCATED KV cache
  (--kv-capacity 181248) — a fixed ceiling that cannot grow into the ~6.8 GB
  free; ScriptEngine's embedder (bge-large ~335M) + reranker
  (bge-reranker-v2-m3 ~568M) need ~2 GB (NATIVE_MIGRATION_HANDOFF.md:57).
  Protocol reverted: whole-character `page-run` after **every** unit (GPU).
  If a run OOMs: immediate CPU relaunch + note here, carry on; re-check CUDA
  availability at each page boundary.
- 2026-09-03 — authoring preference from unit 4 onward (001–045 stay as-is):
  **no double-barrelled questions** — two single-fact questions test more
  than one compound question.
- 2026-09-03 — units 1–3 of Yuji verified against the corpus distribution
  (answer length median 13 vs battle-page narrative precedent 15; the Mai
  pilot's 3.8 was the dense-page outlier, not the standard). Pattern PASSED,
  no rework.
- 2026-09-03 17:06 — unit 6 complete: 38/38 verbatim, ids 092–129. Whole-batch
  `page-run` **128/129** (175.5 s on GPU; REPORT
  `jjk-yuji_itadori_synopsis-2026-09-03-1706`). The 1 miss = #111 ("Who has
  started the culling game…?") — diagnosed and re-verified live as router gap
  **G25 (OPEN)** (who-agent story-verb → narrative; the 103-beat episode stream
  omits the Synopsis prose; siblings #110/#112 route `qa` and pass).
  Documented in HANDOFF_PROSE_PASS.md ENGINE GAPS (G25) + State update 102.
  Question stays **active and un-reworded**: it fails on every subsequent Yuji
  page-run until the router fix lands.
- 2026-09-03 — Culling Game sub-chunk boundaries recorded (measured by unit 6
  at authoring, facts.db 64-paragraph section): 2/3 = paragraphs 23–46,
  **3,271 w**, starts "After the pair accept the deal, Yuji tells Megumi that
  all the bluffing he's done was risky, who tells Yuji that it isn't."; 3/3 =
  paragraphs 47–64, ~3,287 w, starts "Now inside the barrier, Yuji falls from
  the sky and wonders where Megumi is."
- 2026-09-03 — **Deviation (unit 7 dispatch):** the unit-7 subagent continued
  past its brief and completed units 7–12 (the whole page) in one run — 151
  questions (130–280), all `add`s gate-passed. Orchestrator re-verified
  independently vs facts.db: all 151 new answers verbatim (raw substring,
  whitespace-normalized), pre-130 re-check clean, ids sequential 001–280,
  structure (kind/note/expect_mode/single-source) clean, sub-chunk boundaries
  honoured (#167's answer opens at the recorded 3/3 boundary; #232's at the
  recorded Shinjuku 2/2 boundary). The per-unit page-runs for units 7–11 are
  collapsed into the page-completion run (the protocol's page-completion
  checkpoint) — the final state is the one that matters, and it scored clean.
  Future briefs state "stop after this unit" more explicitly.
- 2026-09-03 17:30 — **API restarted on CUDA again** (old PID 11367 → new
  **PID 25690**; health `"device":"cuda"`). Reason: the CLI's
  newer-source-than-server guard refused the page-run (the uncommitted
  span-recall feature — `scriptengine/cli.py` + `scriptengine/eval/span_recall.py`,
  mtimes 17:16/17:26 UTC — is CLI/eval-only, not in the API's import path, so
  the 16:50:47 server's `/context` behaviour was unchanged; the restart just
  makes the guard pass and measures the current tree). Re-check health at each
  page boundary as before.
- 2026-09-03 17:30 — **Yuji Itadori PAGE COMPLETE:** 12/12 units, **280
  questions** (001–280). Completion page-run **279/280** on GPU (REPORT
  `jjk-yuji_itadori_synopsis-2026-09-03-1730`); the single miss = #111, the
  documented-open **G25** (it will stay the page's one failure until the
  router fix lands). Section distribution: Fearsome Womb 24 · History 3 ·
  Vs. Mahito 10 · Kyoto 8 · Death Painting 8 · Shibuya 38 · Culling Game 112 ·
  Shinjuku 53 · Epilogue 1 · Modulo 23. **Next page: Sukuna** (15,342 w, 10
  units; halfway page-run after unit 5), unit 1 = History (433 w).
- 2026-09-03 17:38 — **PROTOCOL SWITCH (user directive, State 105):** density
   now **1–2 questions per non-empty section** (~1.5/section; skip Navigation/
   References/See Also/External Links), not per 1,000 words — the span-recall
   harness (State 103) proved prose is stored verbatim with or without a
   question (JJK tier 0: 48,473 substantive sentences, 99.9959% in chunks),
   and the engine serves whole sections as beats, so word-count density
   re-tested the same retrieval unit. The split protocol collapses: **one
   dispatch per page group (25–40 q's, section-count-descending), D1–D16,
   70 pages / 312 sections / ~469 questions** (old rule implied ~1,900).
   Yuji (280) + Mai (16) frozen as regression coverage — never retire or
   rewrite. Quality bar = the "lose nothing" guard: natural human phrasing,
   tight answer span, roster/closed-set (N/A this wave — verified all 835
   roster/set questions are page-gen on character/technique/event pages,
   zero on character_synopsis; **standing check before any future page type;
   chapter tranche flagged** for its closed-set sections and does not start
   until that check passes). At most one R5 per page, no double-barrels,
   verbatim gate + per-dispatch page-run per page touched + never reword to
   dodge a failure — all unchanged. Session loop: `span-recall --series jjk`
   at session start (offline, <1 s); exit 2 with only the two known
`Chapter 239 / References` lines = expected (verified 17:38, exit 2, both
    misses = Chapter 239/References). Next: **D1** (Maki Zenin + Panda, ~30 q's).
- 2026-09-03 17:44 — **D1 COMPLETE** (Maki Zenin + Panda; subagent specs
   `temp_py_scripts/_d1_maki_zenin_synopsis.json` + `_d1_panda_synopsis.json`;
   17 q's each = 34 total vs 30 planned, +4 within the 25–40 band).
   Orchestrator re-check: 34/34 answers verbatim vs facts.db (raw substring,
   whitespace-normalized), structure clean, ids sequential 001–017 per page
   (both batches start fresh at 001). Page-runs on GPU (REPORT
   `jjk-maki_zenin_synopsis-2026-09-03-1741` 16/17 ·
   `jjk-panda_synopsis-2026-09-03-1742` 15/17): the 3 misses are two new
   documented-open engine gaps — **G26** (past-tense fate question "What
   happened to <character>?" routes narrative by the G4b `ed` exclusion;
   Panda #012 + #015, both served under forced qa — a pure misroute) and
   **G27** (qa subject-focus assembles beats in section order and the default
   6000-token budget truncates the tail sections of long pages; Maki #015's
   Epilogue answer is absent even under forced qa, present at
   token_budget=30000 — a truncation, not a misroute; Maki #015 also carries
   G26's trigger on the auto route). Full records + fix plans in HANDOFF's
   ENGINE GAPS. All 3 questions stay **active and un-reworded**; each page
   carries its documented failures until the fixes land. Next: **D2** (Gojo +
   Shoko Ieiri, ~30 q's).
- 2026-09-03 17:50 — **D2 COMPLETE** (Satoru Gojo + Shoko Ieiri; subagent
   specs `temp_py_scripts/_d2_satoru_gojo_synopsis.json` +
   `_d2_shoko_ieiri_synopsis.json`; 16 + 12 = 28 q's vs 30 planned, within
   band; the Shoko page caps at 12 because 8 of its 10 sections are 31–133 w
   = one question each). Orchestrator re-check: 28/28 verbatim vs facts.db,
   structure clean, ids sequential (001–016, 001–012). Page-runs on GPU
   (REPORT `jjk-satoru_gojo_synopsis-2026-09-03-1747` **16/16** ·
   `jjk-shoko_ieiri_synopsis-2026-09-03-1747` **11/12**): the single miss is
   Shoko #009 ("Why did Shoko start smoking again during the Shibuya
   Incident?") — diagnosed live as **G25 instance 2** (the question's "start"
   hits `_NARRATIVE_VERBS` → narrative; the character subject keeps the
   narrative read; the 10-beat Shibuya episode stream omits the Synopsis
   prose; a forced qa at the default budget serves it). The G25 ENGINE GAPS
   record was extended: the trigger shape is any wh-agent interrogative with
   a story-verb head ("Why did X start…?", "Who has started…?"), and the fix
   plan now covers who/why-agent forms. Question stays active + failing
   under G25. First 100% page under the new protocol: Satoru Gojo (16/16).
   Next: **D3** (Kenjaku + Kiyotaka Ijichi + Mahito, ~36 q's).
- 2026-09-03 17:56 — **D3 COMPLETE** (Kenjaku + Kiyotaka Ijichi + Mahito;
   subagent specs `temp_py_scripts/_d3_kenjaku_synopsis.json` +
   `_d3_kiyotaka_ijichi_synopsis.json` + `_d3_mahito_synopsis.json`; 12 + 10
   + 11 = 33 q's vs 36 planned — Ijichi caps at 10 because 5 of its 8
   sections are ≤ 82 w = one each; within band). All three `add`s
   gate-passed first-run (answers byte-extracted from facts.db by
   `temp_py_scripts/_gen_d3_spec.py` to dodge the straight/curly apostrophe
   mix in stored text — kept for audit). Orchestrator re-check: 33/33
   verbatim vs facts.db, structure clean, ids sequential. Page-runs on GPU
   (REPORTs `jjk-kenjaku_synopsis-2026-09-03-1754` **12/12** ·
   `jjk-kiyotaka_ijichi_synopsis-2026-09-03-1755` **10/10** ·
   `jjk-mahito_synopsis-2026-09-03-1755` **11/11**): **clean sweep — 33/33,
   the first dispatch with zero misses**; Mahito #011 (Modulo, a tail section)
   passed at the default 6000-token budget, so no G27 instance. Next:
   **D4** (Yaga + Megumi + Nobara, 8/8/8, ~36 q's).
- 2026-09-03 18:01 — **D4 COMPLETE** (Masamichi Yaga + Megumi Fushiguro +
   Nobara Kugisaki; subagent specs `temp_py_scripts/_d4_masamichi_yaga_synopsis.json`
   + `_d4_megumi_fushiguro_synopsis.json` + `_d4_nobara_kugisaki_synopsis.json`;
   10 + 11 + 10 = 31 q's vs 36 planned, within band; the subagent
   pre-probed facts.db — these three pages store only straight apostrophes,
   and answers were asserted as raw substrings via
   `temp_py_scripts/_gen_d4_spec.py`; wiki typos "Gakugaji" (Yaga #009) and
   "relunctantly" (Megumi #008) preserved verbatim). Orchestrator re-check:
   31/31 verbatim vs facts.db, structure clean, ids sequential. Page-runs on
   GPU (REPORTs `jjk-masamichi_yaga_synopsis-2026-09-03-1759` **10/10** ·
   `jjk-megumi_fushiguro_synopsis-2026-09-03-1759` **10/11** ·
   `jjk-nobara_kugisaki_synopsis-2026-09-03-1759` **10/10**): the single miss
   is Megumi #011 ("Did Megumi die by 2087?", Modulo 13 w) — diagnosed live as
   **G27 instance 2** (auto → narrative, 11 episode-stream beats, Synopsis
   prose omitted; forced qa default = 26 beats ending at Shibuya; qa
   tb=12000 = 50 beats, Modulo STILL absent; qa tb=30000 = 107 beats, marker
   present — the 4,301-w Culling Game section pushes the tail past even the
   12000 budget, stricter than instance 1). G27's ENGINE GAPS record extended
   with instance 2. Notably, Nobara's Epilogue (#009) + Modulo (#010)
   tail questions — flagged G27-watch in the brief — both PASSED at the
   default budget, so G27 bites only on the longest pages. Question stays
   active + failing under G27. Next: **D5** (Sukuna + Yuta + Aoi Todo,
   8/8/7, ~35 q's).
- 2026-09-03 18:09 — **D5 COMPLETE** (Sukuna + Yuta Okkotsu + Aoi Todo; subagent
   specs `temp_py_scripts/_d5_sukuna_synopsis.json` +
   `_d5_yuta_okkotsu_synopsis.json` + `_d5_aoi_todo_synopsis.json`; 12 + 12 +
   10 = 34 q's vs 35 planned, within band; spans resolved via the
   quote-variant resolver in `temp_py_scripts/_gen_d5_spec.py`). Orchestrator
   re-check: 34/34 verbatim vs facts.db, structure clean, ids sequential.
   Page-runs on GPU (REPORTs `jjk-sukuna_synopsis-2026-09-03-1805` **12/12** ·
   `jjk-yuta_okkotsu_synopsis-2026-09-03-1805` **12/12** ·
   `jjk-aoi_todo_synopsis-2026-09-03-1805` **10/10**): **second clean
   sweep — 34/34**. Notably every G27-watch tail question PASSED at the
   default 6000-token budget — Sukuna #011/012 (deep inside the 10,083-w
   Shinjuku section), Yuta #011 (Epilogue) + #012 (Modulo), Aoi #010 (Modulo).
   G27 so far has bitten only twice (Maki #015, Megumi #011), both on pages
   where the tail question asked about a *fate/absent* state the episode
   stream can't cover; the subagent also sidestepped G26's "What happened
   to" shape by phrasing Yuta's Modulo question "When did Yuta die?". No new
   engine gaps. Next: **D6** (Choso + Kasumi Miwa + Mei Mei + Momo, 6
   sections each, ~36 q's).
- 2026-09-03 18:16 — **D6 COMPLETE** (Choso + Kasumi Miwa + Mei Mei + Momo
   Nishimiya; subagent specs `temp_py_scripts/_d6_choso_synopsis.json` +
   `_d6_kasumi_miwa_synopsis.json` + `_d6_mei_mei_synopsis.json` +
   `_d6_momo_nishimiya_synopsis.json`; 9 + 7 + 8 + 8 = 32 q's vs ~36 planned;
   spans resolved via `temp_py_scripts/_gen_d6_spec.py`). Orchestrator
   re-check: 32/32 verbatim vs facts.db, structure clean, ids sequential.
   Page-runs on GPU (REPORTs `jjk-choso_synopsis-2026-09-03-1809` **9/9** ·
   `jjk-kasumi_miwa_synopsis-2026-09-03-1810` **7/7** ·
   `jjk-mei_mei_synopsis-2026-09-03-1810` **8/8** ·
   `jjk-momo_nishimiya_synopsis-2026-09-03-1810` **8/8**): **third clean
   sweep — 32/32**. G25-shaped questions authored as-is (choso-004/009,
   kasumi-002/004, mei_mei-002/007) all PASSED — the "start"-type trigger has
   not re-fired since D2, and G26 was sidestepped by phrasing Choso's death
   "Why did Choso sacrifice himself…?" No new engine gaps. Next: **D7** (Toge
   Inumaki + Utahime Iori + Yoshinobu Gakuganji + Nanami, 6/6/6/5 sections).
- 2026-09-03 18:22 — **D7 COMPLETE** (Toge Inumaki + Utahime Iori + Yoshinobu
   Gakuganji + Kento Nanami; subagent specs `temp_py_scripts/_d7_toge_inumaki_synopsis.json`
   + `_d7_utahime_iori_synopsis.json` + `_d7_yoshinobu_gakuganji_synopsis.json`
   + `_d7_kento_nanami_synopsis.json`; 8 + 7 + 8 + 7 = 30 q's; spans resolved
   via `temp_py_scripts/_gen_d7_spec.py`; Nanami's 2-w Navigation section
   skipped per protocol). Orchestrator re-check: 30/30 verbatim vs facts.db
   (incl. the curly-apostrophe "Gojo's Past Arc" title on Utahime), structure
   clean, ids sequential. Page-runs on GPU (REPORTs `jjk-toge_inumaki_synopsis-2026-09-03-1813`
   **8/8** · `jjk-utahime_iori_synopsis-2026-09-03-1813` **7/7** ·
   `jjk-yoshinobu_gakuganji_synopsis-2026-09-03-1813` **8/8** ·
   `jjk-kento_nanami_synopsis-2026-09-03-1813` **7/7**): **fourth clean
   sweep — 30/30**. G25-watch (nanami-004, wh-subject story-verb head) and
   G27-watch (nanami-007, tail of a short page) both passed — G27's pattern
   (tail beat truncated on long pages) does not apply here. G26 sidestepped
   on all three fate-adjacent facts (toge-006, nanami-006, gakuganji-006).
   No new engine gaps. Next: **D8** (Kokichi + Noritoshi + Takuma + Tsumiki,
   5/5/5/5 sections).
- 2026-09-03 18:24 — **D8 COMPLETE** (Kokichi Muta + Noritoshi Kamo + Takuma
   Ino + Tsumiki Fushiguro; subagent specs `temp_py_scripts/_d8_kokichi_muta_synopsis.json`
   + `_d8_noritoshi_kamo_synopsis.json` + `_d8_takuma_ino_synopsis.json` +
   `_d8_tsumiki_fushiguro_synopsis.json`; 7 + 7 + 7 + 6 = 27 q's; spans
   resolved via `temp_py_scripts/_gen_d8_spec.py`). Orchestrator re-check:
   27/27 verbatim vs facts.db, structure clean, ids sequential. Page-runs on
   GPU (REPORTs `jjk-kokichi_muta_synopsis-2026-09-03-1816` **7/7** ·
   `jjk-noritoshi_kamo_synopsis-2026-09-03-1816` **7/7** ·
   `jjk-takuma_ino_synopsis-2026-09-03-1816` **7/7** ·
   `jjk-tsumiki_fushiguro_synopsis-2026-09-03-1816` **6/6**): **fifth clean
   sweep — 27/27**. Tsumiki's G27-watch tail question (Shinjuku, 18 w) passed
   — G27's pattern keeps holding: tail beats only drop when the page is long
   enough for the default budget to truncate them. G26 sidestepped on
   Tsumiki's cremation fact ("What did Shoko Ieiri do with Tsumiki's body…?").
   No new engine gaps. Next: **D9** (Uraume + Akari + Atsuya + Hana +
   Hanami, 5/4/4/4/4 sections).
- 2026-09-03 18:31 — **D9 COMPLETE** (Uraume + Akari Nitta + Atsuya Kusakabe
   + Hana Kurusu + Hanami; subagent specs `temp_py_scripts/_d9_uraume_synopsis.json`
   + `_d9_akari_nitta_synopsis.json` + `_d9_atsuya_kusakabe_synopsis.json`
   + `_d9_hana_kurusu_synopsis.json` + `_d9_hanami_synopsis.json`; 7 + 5 +
   6 + 6 + 5 = 29 q's; spans resolved via `temp_py_scripts/_gen_d9_spec.py`).
   Orchestrator re-check: 29/29 verbatim vs facts.db, structure clean, ids
   sequential. Page-runs on GPU (REPORTs `jjk-uraume_synopsis-2026-09-03-1820`
   **7/7** · `jjk-akari_nitta_synopsis-2026-09-03-1820` **5/5** ·
   `jjk-atsuya_kusakabe_synopsis-2026-09-03-1820` **6/6** ·
   `jjk-hana_kurusu_synopsis-2026-09-03-1820` **6/6** ·
   `jjk-hanami_synopsis-2026-09-03-1820` **5/5**): **sixth clean sweep —
   29/29**. Hana's G27-watch Modulo question passed (short page, matching the
   nanami/tsumiki counter-examples). No new engine gaps. Next: **D10** (Jogo
   + Hakari + Riko + Geto + Tengen, 4 sections each).
- 2026-09-03 18:38 — **D10 COMPLETE** (Jogo + Kinji Hakari + Riko Amanai +
   Suguru Geto + Tengen; subagent specs `temp_py_scripts/_d10_jogo_synopsis.json`
   + `_d10_kinji_hakari_synopsis.json` + `_d10_riko_amanai_synopsis.json`
   + `_d10_suguru_geto_synopsis.json` + `_d10_tengen_synopsis.json`; 6 + 7 +
   5 + 6 + 5 = 29 q's; spans resolved via `temp_py_scripts/_gen_d10_spec.py`;
   one G25-shaped draft (geto-002 "Why did Geto massacre…?") was rephrased to
   a natural non-triggering form "What did Geto do to the villagers…?" —
   allowed by protocol since the natural alternative existed). Orchestrator
   re-check: 29/29 verbatim vs facts.db, structure clean, ids sequential.
   Page-runs on GPU (REPORTs `jjk-jogo_synopsis-2026-09-03-1823` **6/6** ·
   `jjk-kinji_hakari_synopsis-2026-09-03-1823` **7/7** ·
   `jjk-riko_amanai_synopsis-2026-09-03-1823` **5/5** ·
   `jjk-suguru_geto_synopsis-2026-09-03-1824` **6/6** ·
   `jjk-tengen_synopsis-2026-09-03-1824` **5/5**): **seventh clean sweep —
   29/29**. Riko's G27-watch tail (Shinjuku, 13 w) passed — the G27
   counter-example set now has five members. No new engine gaps. Next:
**D11** (Toji + Ui Ui + Haibara + Yuki + Charles Bernard, 4/4/4/4/3
    sections).
 - 2026-09-03 18:41 — **D11 COMPLETE** (Toji Fushiguro + Ui Ui + Yu Haibara +
    Yuki Tsukumo + Charles Bernard; first integrated-subagent attempt died
    mid-way with nothing on disk — re-dispatched as D11a (Toji + Ui Ui +
    Haibara) and D11b (Yuki + Charles Bernard) in parallel; subagent specs
    `temp_py_scripts/_d11_toji_fushiguro_synopsis.json` +
    `_d11_ui_ui_synopsis.json` + `_d11_yu_haibara_synopsis.json` (D11a) and
    `_d11_yuki_tsukumo_synopsis.json` + `_d11_charles_bernard_synopsis.json`
    (D11b); 6 + 6 + 4 + 5 + 4 = 25 q's; spans resolved via
    `temp_py_scripts/_gen_d11_spec.py` + `_gen_d11b_spec.py`). Orchestrator
    re-check: 25/25 verbatim vs facts.db, structure clean, ids sequential.
    First page-runs on GPU: `jjk-ui_ui_synopsis-2026-09-03-1828` **6/6** ·
    `jjk-yu_haibara_synopsis-2026-09-03-1828` **4/4** ·
    `jjk-yuki_tsukumo_synopsis-2026-09-03-1828` **5/5** ·
    `jjk-charles_bernard_synopsis-2026-09-03-1828` **4/4** ·
    `jjk-toji_fushiguro_synopsis-2026-09-03-1828` **5/6** (toji-001 "How did
    Toji end up with the scar on his lip?" routed **narrative** — "end" in
    "end up" hits `_NARRATIVE_VERBS`, the character subject keeps the
    narrative read, and Toji's narrative stream omits the History beat even at
    tb=30000, while the answer is fully served under forced qa at the default
    budget: a **G25-class** story-verb misroute, instance 3). Fixed by the
    house static-qa rephrase (Ogi Q133 / Wasuke Q171 / geto-002 precedent):
    "What caused the scar on Toji's lip?" — same verbatim answer, routes qa;
    re-run `jjk-toji_fushiguro_synopsis-2026-09-03-1830` **6/6**:
    **eighth clean sweep — 25/25**. All three G27-watch tails (toji-006
    Shinjuku 10 w, ui_ui-006 Modulo 218 w, yu_haibara-004 Shinjuku 18 w)
    passed on their short pages — the G27 counter-example set now has eight
    members. charles_bernard-003 (wh + fight-verb head, G25-watch) routed qa
    and passed, clearing that watch. No new engine gaps. Next: **D12** (Dagon
    + Eso + Fumihiko + Hagane + Kashimo, 3 sections each).
 - 2026-09-03 18:47 — **D12 COMPLETE** (Dagon + Eso + Fumihiko Takaba + Hagane
    Daido + Hajime Kashimo; re-dispatch pattern carried over from D11 — D12a
    (Dagon + Eso + Fumihiko) and D12b (Hagane + Kashimo) ran in parallel;
    subagent specs `temp_py_scripts/_d12_dagon_synopsis.json` +
    `_d12_eso_synopsis.json` + `_d12_fumihiko_takaba_synopsis.json` (D12a) and
    `_d12_hagane_daido_synopsis.json` + `_d12_hajime_kashimo_synopsis.json`
    (D12b); 4 + 4 + 4 + 5 + 5 = 22 q's; spans resolved via
    `temp_py_scripts/_gen_d12_spec.py`). Orchestrator re-check: 22/22 verbatim
    vs facts.db, structure clean, ids sequential. Page-runs on GPU (REPORTs
    `jjk-dagon_synopsis-2026-09-03-1834` **4/4** ·
    `jjk-eso_synopsis-2026-09-03-1834` **4/4** ·
    `jjk-fumihiko_takaba_synopsis-2026-09-03-1834` **4/4** ·
    `jjk-hagane_daido_synopsis-2026-09-03-1834` **5/5** ·
    `jjk-hajime_kashimo_synopsis-2026-09-03-1835` **5/5**): **ninth clean
    sweep — 22/22, first-run, zero misses**. All G27-watch tails (dagon-004,
    eso-004, fumihiko-004, kashimo-004/005) passed; kashimo-004/005 sit in the
    tail of a ~3.2k-w page and still passed — the G27 pattern (truncation
only on the longest pages) holds. No new engine gaps. Next: **D13**
     (Shigemo + Hiromi + Kechizu + Mimiko + Nanako, 3 sections each).
  - 2026-09-03 18:52 — **D13 COMPLETE** (Haruta Shigemo + Hiromi Higuruma +
     Kechizu + Mimiko Hasaba + Nanako Hasaba; D13a (Shigemo + Hiromi + Kechizu)
     and D13b (Mimiko + Nanako) ran in parallel; subagent specs
     `temp_py_scripts/_d13_haruta_shigemo_synopsis.json` +
     `_d13_hiromi_higuruma_synopsis.json` + `_d13_kechizu_synopsis.json`
     (D13a) and `_d13_mimiko_hasaba_synopsis.json` +
     `_d13_nanako_hasaba_synopsis.json` (D13b); 4 + 6 + 4 + 4 + 4 = 22 q's;
     spans resolved via `temp_py_scripts/_gen_d13_spec.py`). Orchestrator
     re-check: 22/22 verbatim vs facts.db, structure clean, ids sequential.
     Page-runs on GPU (REPORTs
     `jjk-haruta_shigemo_synopsis-2026-09-03-1839` **4/4** ·
     `jjk-hiromi_higuruma_synopsis-2026-09-03-1839` **6/6** ·
     `jjk-kechizu_synopsis-2026-09-03-1839` **4/4** ·
     `jjk-mimiko_hasaba_synopsis-2026-09-03-1839` **4/4** ·
     `jjk-nanako_hasaba_synopsis-2026-09-03-1839` **4/4**): **tenth clean
     sweep — 22/22, first-run, zero misses**. All G27-watch tails
     (hiromi-005/006 in a ~3.3k-w page tail, mimiko-004/nanako-004 in ~0.9k-w
     tails) passed — even the ~3.3k-w Hiromi page served its tail beats,
     reinforcing the G27 pattern. No new engine gaps. Next: **D14**
     (Naobito Zenin + Rika Orimoto + Rokujushi Miyo + Toshihisa Negi +
     Yorozu, 3 sections each).
  - 2026-09-03 18:46 — **D14 COMPLETE** (Naobito Zenin + Rika Orimoto +
     Rokujushi Miyo + Toshihisa Negi + Yorozu; D14a (Naobito + Rika + Miyo)
     and D14b (Toshihisa + Yorozu) ran in parallel; subagent specs
     `temp_py_scripts/_d14_naobito_zenin_synopsis.json` +
     `_d14_rika_orimoto_synopsis.json` + `_d14_rokujushi_miyo_synopsis.json`
     (D14a, resolver `_gen_d14_spec.py`) and
     `_d14_toshihisa_negi_synopsis.json` + `_d14_yorozu_synopsis.json`
     (D14b, resolver `_gen_d14b_spec.py`); 5 + 5 + 4 + 4 + 4 = 22 q's).
     Slug note: the Rika page slug is `rika_orimoto_synopsis` (not the
     `rika_oremoto` typo first tried). Orchestrator re-check: 22/22 verbatim
     vs facts.db, structure clean, ids sequential. Page-runs on GPU (REPORTs
     `jjk-naobito_zenin_synopsis-2026-09-03-1843` **5/5** ·
     `jjk-rika_orimoto_synopsis-2026-09-03-1843` **5/5** ·
     `jjk-rokujushi_miyo_synopsis-2026-09-03-1843` **4/4** ·
     `jjk-toshihisa_negi_synopsis-2026-09-03-1843` **4/4** ·
     `jjk-yorozu_synopsis-2026-09-03-1843` **4/4**): **eleventh clean
     sweep — 22/22, first-run, zero misses**. All G27-watch tails (rika-005
     Modulo 22 w, miyo-004 Shinjuku 110 w, toshihisa-003/004 Shibuya 178 w,
     yorozu-004 Culling Game 343 w) passed on their short pages. One stored
     verbatim quirk: naobito-002 carries the source typo "technqiue"
     verbatim (correct — lose nothing). toshihisa-004 is the page's one R5
     yes/no; its death-beat span was dropped because the stored text has no
     space before `(Chapter 115, Episode 40)`. No new engine gaps. Next:
     **D15** (9 two-section pages, Dabura Karaba…Naoya Zenin, ~27 q's).
  - 2026-09-03 18:51 — **D15 COMPLETE** (Dabura Karaba + Jiro Awasaka +
     Junpei Yoshino + Kirara Hoshi + Kou Usami + Kurourushi + Manami Suda +
     Miguel Oduol + Naoya Zenin; 9 two-section pages; split across three
     subagents D15a (Dabura+Jiro+Junpei) + D15b (Kirara+Kou+Kurourushi+
     Manami) + D15c (Miguel+Naoya); specs
     `temp_py_scripts/_d15_*.json`, resolvers `_gen_d15_spec.py` (D15a/b) +
     `_gen_d15c_spec.py` (D15c); 4+2+3+3+3+3+2+2+3 = 25 q's). D15a/D15b
     verified + page-run first (@1847), then D15c appended (@1849) to
     complete the 9-page D15. Orchestrator re-check: 25/25 verbatim vs
     facts.db, structure clean, ids sequential per page. Page-runs on GPU
     (REPORTs `jjk-dabura_karaba_synopsis-2026-09-03-1847` **4/4** ·
     `jjk-jiro_awasaka_synopsis-2026-09-03-1847` **2/2** ·
     `jjk-junpei_yoshino_synopsis-2026-09-03-1847` **3/3** ·
     `jjk-kirara_hoshi_synopsis-2026-09-03-1847` **3/3** ·
     `jjk-kou_usami_synopsis-2026-09-03-1847` **3/3** ·
     `jjk-kurourushi_synopsis-2026-09-03-1847` **3/3** ·
     `jjk-manami_suda_synopsis-2026-09-03-1847` **2/2** ·
     `jjk-miguel_oduol_synopsis-2026-09-03-1849` **2/2** ·
     `jjk-naoya_zenin_synopsis-2026-09-03-1849` **3/3**): **thirteenth
     clean sweep — 25/25, first-run, zero misses**. All G27-watch tails
     (naoya-002/003 in a ~1.75k-w page, plus every other page's tail
     section) passed. No G25/G26 trigger shapes used. No new engine gaps.
     Next: **D16** (the final 6 pages — Ogami + Ogi Zenin + Reggie Star +
     Ryu Ishigori + Takako Uro (2 sections each) + Tsurugi Okkotsu
     (1 section), ~17 q's).
  - 2026-09-03 18:55 — **D16 COMPLETE (FINAL DISPATCH)** (Ogami + Ogi
     Zenin + Reggie Star + Ryu Ishigori + Takako Uro + Tsurugi Okkotsu;
     D16a (Ogami+Ogi+Reggie) and D16b (Ryu+Takako+Tsurugi) ran in parallel;
     specs `temp_py_scripts/_d16_*.json`, resolvers `_gen_d16_spec.py`;
     2+2+3+3+3+2 = 15 q's). Orchestrator re-check: 15/15 verbatim vs
     facts.db, structure clean, ids sequential per page. Page-runs on GPU
     (REPORTs `jjk-ogami_synopsis-2026-09-03-1852` **2/2** ·
     `jjk-ogi_zenin_synopsis-2026-09-03-1852` **2/2** ·
     `jjk-reggie_star_synopsis-2026-09-03-1852` **3/3** ·
     `jjk-ryu_ishigori_synopsis-2026-09-03-1852` **3/3** ·
     `jjk-takako_uro_synopsis-2026-09-03-1852` **3/3** ·
     `jjk-tsurugi_okkotsu_synopsis-2026-09-03-1852` **2/2**):
     **fourteenth clean sweep — 15/15, first-run, zero misses**. All
     G27-watch tails (reggie-002/003 in a ~1.45k-w page, takako-002/003,
     ryu-003, ogami-002, ogi-002) passed. The `takako_uro` page's stored
     "Synoposis" breadcrumb typo was handled — spec used the normal L3
     section titles ("History" / "Culling Game Arc"), not the typo. Tsurugi
     (the one single-section page) carries 2 q's. No G25/G26 trigger shapes
     used. No new engine gaps. **The character_synopsis prose wave (D1–D16)
     is COMPLETE: all 72 non-frozen synopsis pages carry 1–2 questions per
     non-empty section, every `add` gate-passed, every `page-run` clean
     (fourteen consecutive first-run clean sweeps, ~470 q's total). The 2
     frozen pages (Yuji 280 q's, Mai 16 q's) remain untouched by
     design.** Next standing item: the chapter-tranche roster check
     (`reports/page-campaign/CHAPTER_TRANCHE_ROSTER_CHECK.md`) must be
     decided before any chapter work begins.