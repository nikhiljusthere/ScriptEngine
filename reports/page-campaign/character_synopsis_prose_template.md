# Character Synopsis Prose Template — JJK (72 pages)

Prepared for the **character_synopsis** wave of the prose pass (the last page
type of the character phase). Census independently re-derived from
`series/jjk/facts.db` (2026-09-03): 72 `character_synopsis` documents, all
level-2/3 section text, `split()` word counts (identical to the store's
`sections.word_count` column). Calibrated against the **Mai Zenin pilot**
(`jjk-mai_zenin_synopsis-2026-09-03-1214`): 1,402 words → 16 questions →
**16/16 verified**, ~38 s machine time, comfortably inside one dispatch.

The wave plan's census numbers run +1 word per page (a different word-counting
method); the packing result is unaffected — no wave boundary moves. This
template uses the facts.db counts.

## PROTOCOL REVISION 2026-09-03 (density switch — SUPERSEDES the density rule,
the split protocol, the Tier 1 unit plan, the Tier 2 wave table, and the
"Numbers to expect" table below; read this before authoring anything)

**New density rule: one to two questions per section, not per 1,000 words.**
~1.5 per non-empty section, skipping `Navigation` / `References` /
`See Also` / `External Links`. Every section gets at least one question; a
second only where it carries two genuinely distinct facts. Rationale: the
span-recall harness (State 103) proved prose is stored verbatim whether or not
a question targets it (JJK tier 0 = 48,473 substantive sentences, 99.9959%
inside chunks), and the engine serves whole sections as beats — density tied to
word count re-tests the same retrieval unit 28× on the Yuji page.

**The split protocol is collapsed entirely.** Sub-chunking existed only to
manage authoring volume. One section = one beat = one or two questions, so
**one dispatch per page (or a small group of pages)**. No per-arc dispatches,
no sub-chunks. The 74-unit Tier 1 ledger and the 26-wave Tier 2 table are
superseded.

**Frozen pages (never retire or rewrite; they stay as regression
coverage):** Yuji Itadori (280 questions, 12 units, old density) and Mai Zenin
(16, pilot).

**Remaining work: 70 pages, 312 sections, ~468 questions** (the old rule
implied ~1,900). Order by section count descending, grouped into dispatches
of ~25–40 questions → **16 dispatches (D1–D16)**, one subagent at a time,
strictly sequential (plan in the unit ledger, `character_synopsis_unit_ledger.md`):

| D | pages (sections) | q's | | D | pages (sections) | q's |
|---|---|---:|---|---|---|---:|
| 1 | Maki Zenin (10), Panda (10) | 30 | | 9 | Uraume (5), Akari Nitta (4), Atsuya Kusakabe (4), Hana Kurusu (4), Hanami (4) | 32 |
| 2 | Satoru Gojo (10), Shoko Ieiri (10) | 30 | | 10 | Jogo (4), Kinji Hakari (4), Riko Amanai (4), Suguru Geto (4), Tengen (4) | 30 |
| 3 | Kenjaku (8), Kiyotaka Ijichi (8), Mahito (8) | 36 | | 11 | Toji Fushiguro (4), Ui Ui (4), Yu Haibara (4), Yuki Tsukumo (4), Charles Bernard (3) | 28 |
| 4 | Masamichi Yaga (8), Megumi Fushiguro (8), Nobara Kugisaki (8) | 36 | | 12 | Dagon (3), Eso (3), Fumihiko Takaba (3), Hagane Daido (3), Hajime Kashimo (3) | 25 |
| 5 | Sukuna (8), Yuta Okkotsu (8), Aoi Todo (7) | 35 | | 13 | Haruta Shigemo (3), Hiromi Higuruma (3), Kechizu (3), Mimiko Hasaba (3), Nanako Hasaba (3) | 25 |
| 6 | Choso (6), Kasumi Miwa (6), Mei Mei (6), Momo Nishimiya (6) | 36 | | 14 | Naobito Zenin (3), Rika Orimoto (3), Rokujushi Miyo (3), Toshihisa Negi (3), Yorozu (3) | 25 |
| 7 | Toge Inumaki (6), Utahime Iori (6), Yoshinobu Gakuganji (6), Kento Nanami (5) | 35 | | 15 | Dabura Karaba (2), Jiro Awasaka (2), Junpei Yoshino (2), Kirara Hoshi (2), Kou Usami (2), Kurourushi (2), Manami Suda (2), Miguel Oduol (2), Naoya Zenin (2) | 27 |
| 8 | Kokichi Muta (5), Noritoshi Kamo (5), Takuma Ino (5), Tsumiki Fushiguro (5) | 32 | | 16 | Ogami (2), Ogi Zenin (2), Reggie Star (2), Ryu Ishigori (2), Takako Uro (2), Tsurugi Okkotsu (1) | 17 (tail) |

**The "lose nothing" guard** — gold questions are now spent on what
span-recall structurally *cannot* see. Exactly three things:

1. **Roster / closed-set mode.** span-recall is blind to `expect_mode: roster`.
   **For this wave it does not apply** (verified 2026-09-03): all 835
   roster/set questions in the bank sit on `character` / `technique` /
   `event` pages, zero on `character_synopsis`, and every one is
   `page-gen`-generated, not hand-authored; synopsis pages are 100% narrative
   arc sections with no lists or closed sets. **Standing check (not an
   assumption):** before reducing density on any *future* page type, confirm
   that type has no closed-set sections or that page-gen roster coverage
   already exists for it. **Chapter pages have `Characters in Order of
   Appearance` and `Battles & Events` — closed sets — so the chapter tranche
   gets this check done properly before it starts (on neither the old nor the
   new density until it passes).**
2. **Natural human phrasing.** The harness probes with verbatim lines; gold
   must probe how a person actually asks — not a lightly reworded lift of the
   sentence. This is now the main thing gold buys.
3. **Answer-span precision.** The answer is the specific verbatim span, not
   the whole sentence containing it (the harness only asks "is the line in the
   bundle?").

With 1–2 questions per section, each question must earn its place against
those three. Keep at most **one R5 yes/no per page**. Still no
double-barrelled questions.

**Unchanged:** verbatim substrings only (the `add` gate enforces it), the
gated atomic write, whole-batch `page-run` (100%, or diagnose the root cause),
and **never reword a question to dodge a failure** (gold error → fix the
batch; engine gap → document in HANDOFF's ENGINE GAPS + continue, question
stays active). G25 (Yuji #111) stays open and documented.

**Session loop (added 2026-09-03):** run
`python -m scriptengine.cli span-recall --series jjk` once at the start of
each session (offline, <1 s, no server). Exit 2 with only the two known
`Chapter 239 / References` lines = expected (the known Trivia/References
chunking gap). Exit 2 with *any other* line = the index changed under the
wave → stop and report.

**After the synopsis wave closes:** report; do **not** start the chapter
tranche (304 pages / 1,689 sections / ~2,500 questions at 1.5/section) until
guard #1's roster check is done for chapter pages.

## Page anatomy

`page_type = character_synopsis`; every page is titled `<Character>/Synopsis`
(72/72). All 72 batch scaffolds exist:
`questions/_jjk_page_<slug>.json` where slug = character name lowercased,
spaces → underscores, + `_synopsis` (e.g. *Akari Nitta/Synopsis* →
`_jjk_page_akari_nitta_synopsis.json`). 71 carry 0 questions; Mai Zenin carries
the pilot's 16. The tool's slug → title/url resolution (LIKE fallback, `_`
acting as a wildcard) was verified for all 72 slugs.

Section inventory (non-empty, level 2/3, of 72):

| section | pages | shape | role in the pass |
|---|---:|---|---|
| `Synopsis / <Arc>` L3 | 72 (5–9 arcs each) | the story-arc subsections | **the wave's core**; one question set per arc |
| `History` L2/L3 | 65 | birth / backstory | per-section entries |
| `Cursed Child Arc` L3 | 20 | prequel-arc prose | per-section entries |
| `Modulo` L3 | 11 | post-story sequel prose, `(Modulo Chapter N)` markers | per-section entries |
| `Epilogue` L3 | 5 | post-Culling Game (Volume 30+) | per-section entries |
| `Gojo's Past Arc` L3 | 1 (Gojo) | under `History /` | per-section entries |
| `References` | all | empty body | skip |
| `Navigation` | 72 | 2–4-word navbox artifact | **skip** |

The L2 `Synopsis` section itself has an empty body (0 words) on every page;
its L3 children carry the prose. Non-arc sections (History, Cursed Child,
Modulo, Epilogue, Gojo's Past) come **before** the Synopsis arcs in ordinal
order, so in the split protocol they attach to the page's first arc dispatch
(each is < 4,000 w, so the attachment stays under the cap). Inline citations
are route-one shaped: `(Chapter N, Episode M)`, `(Fanbook)`, `(Volume N)`,
`(Modulo Chapter N)` — resolve through the graph; do not "fix" them.

## Census (72 pages, level-2/3 words, largest first)

| # | words | page | | # | words | page |
|--:|---:|---|--|--:|---:|---|
| 1 | 24,555 | Yuji Itadori | *** SPLIT | 37 | 1,401 | Mai Zenin *(pilot done 16/16)* |
| 2 | 15,342 | Sukuna | *** SPLIT | 38 | 1,397 | Kasumi Miwa |
| 3 | 10,378 | Satoru Gojo | *** SPLIT | 39 | 1,359 | Uraume |
| 4 | 9,813 | Megumi Fushiguro | *** SPLIT | 40 | 1,298 | Masamichi Yaga |
| 5 | 8,268 | Yuta Okkotsu | *** SPLIT | 41 | 1,294 | Junpei Yoshino |
| 6 | 6,530 | Maki Zenin | *** SPLIT | 42 | 1,254 | Momo Nishimiya |
| 7 | 5,927 | Choso | *** SPLIT | 43 | 1,246 | Kiyotaka Ijichi |
| 8 | 4,816 | Kinji Hakari | *** SPLIT | 44 | 1,239 | Hana Kurusu |
| 9 | 4,770 | Nobara Kugisaki | *** SPLIT | 45 | 1,207 | Fumihiko Takaba |
| 10 | 4,538 | Kenjaku | *** SPLIT | 46 | 1,019 | Takako Uro |
| 11 | 3,557 | Mahito | | 47 | 996 | Eso |
| 12 | 3,292 | Hiromi Higuruma | | 48 | 991 | Utahime Iori |
| 13 | 3,182 | Hajime Kashimo | | 49 | 989 | Dagon |
| 14 | 3,152 | Panda | | 50 | 942 | Rokujushi Miyo |
| 15 | 2,884 | Yuki Tsukumo | | 51 | 859 | Hanami |
| 16 | 2,792 | Tengen | | 52 | 832 | Rika Orimoto |
| 17 | 2,700 | Aoi Todo | | 53 | 825 | Kurourushi |
| 18 | 2,526 | Mei Mei | | 54 | 788 | Haruta Shigemo |
| 19 | 2,203 | Atsuya Kusakabe | | 55 | 785 | Nanako Hasaba |
| 20 | 1,962 | Kento Nanami | | 56 | 774 | Naobito Zenin |
| 21 | 1,942 | Jogo | | 57 | 771 | Ryu Ishigori |
| 22 | 1,897 | Kokichi Muta | | 58 | 764 | Miguel Oduol |
| 23 | 1,831 | Noritoshi Kamo | | 59 | 761 | Mimiko Hasaba |
| 24 | 1,811 | Kirara Hoshi | | 60 | 755 | Akari Nitta |
| 25 | 1,750 | Naoya Zenin | | 61 | 737 | Riko Amanai |
| 26 | 1,708 | Suguru Geto | | 62 | 701 | Hagane Daido |
| 27 | 1,615 | Toji Fushiguro | | 63 | 674 | Yorozu |
| 28 | 1,600 | Shoko Ieiri | | 64 | 601 | Kechizu |
| 29 | 1,546 | Toge Inumaki | | 65 | 564 | Tsumiki Fushiguro |
| 30 | 1,538 | Charles Bernard | | 66 | 511 | Jiro Awasaka |
| 31 | 1,526 | Dabura Karaba | | 67 | 482 | Ogi Zenin |
| 32 | 1,482 | Yoshinobu Gakuganji | | 68 | 406 | Manami Suda |
| 33 | 1,457 | Takuma Ino | | 69 | 377 | Ogami |
| 34 | 1,454 | Kou Usami | | 70 | 354 | Tsurugi Okkotsu |
| 35 | 1,453 | Ui Ui | | 71 | 308 | Yu Haibara |
| 36 | 1,449 | Reggie Star | | 72 | 295 | Toshihisa Negi |

Total: **179,802 words** across 72 pages; 10 pages exceed the split
threshold.

## Split / no-split threshold

> **SUPERSEDED (2026-09-03 revision, State 105):** see the PROTOCOL REVISION section above. Section count no longer drives a split decision; 1–2 questions per section per dispatch.

**~4,000 words per dispatch.** Derived from the Mai Zenin pilot: 1,402 words /
16 questions / ~38 s machine time sat comfortably inside one subagent
dispatch, so a 4,000-word payload (~3× the pilot, ~45 questions) stays inside
the dispatch budget with margin; above that, a single dispatch risks running
out of steam mid-page. Consequence:

- **Tier 1 = the 10 pages > 4,000 w** → split into per-story-arc dispatches
  (protocol below).
- **Tier 2 = the 62 pages ≤ 4,000 w** → whole pages, batched into waves
  (table below). Mai Zenin is excluded from wave 18 (pilot, 16/16).
- An **arc** inside Tier 1 that is itself > 4,000 w is sub-split at paragraph
  level into ≤ 4,000 w chunks, in order. Five such arcs:

| page | arc | words |
|---|---|---:|
| Yuji Itadori | Culling Game | 9,821 |
| Yuji Itadori | Shinjuku Showdown | 4,668 |
| Sukuna | Shinjuku Showdown | 10,083 |
| Satoru Gojo | Shinjuku Showdown | 5,107 |
| Megumi Fushiguro | Culling Game | 4,301 |

Never split mid-arc except at that sub-split; arcs are the natural
boundaries (breadcrumb `Synopsis / <Arc>`, level 3).

## Tier 1 — per-arc dispatch plan (largest page first; sequential, one dispatch at a time)

> **SUPERSEDED (2026-09-03 revision, State 105):** no per-arc dispatches or sub-chunks; one dispatch per page/group — see the D1–D16 plan in the PROTOCOL REVISION section.

The ledger's Yuji section (units 1–12) is historical record of the old protocol.

Non-arc sections attach to the page's first arc dispatch (History block sizes:
Yuji 264, Sukuna 433*, Gojo 2,112, Megumi 124, Yuta 2,068, Maki 342, Choso 111,
Hakari 72, Nobara 240, Kenjaku 532 — *Sukuna's History is the
`Synopsis / History` L3 and dispatches as its own unit). `Navigation`
(2–4-word navbox) is skipped everywhere.

| page (total) | dispatch units in ordinal order (words) |
|---|---|
| Yuji Itadori (24,555) | Fearsome Womb + History (2,389) · Vs. Mahito (868) · Kyoto (710) · Death Painting (705) · Shibuya (3,311) · **Culling Game (9,821 → 3 sub-chunks)** · **Shinjuku (4,668 → 2 sub-chunks)** · Epilogue (81) · Modulo (1,998) — 12 dispatches |
| Sukuna (15,342) | History (433) · Fearsome Womb (661) · Vs. Mahito (215) · Kyoto (21) · Death Painting (99) · Shibuya (932) · Culling Game (2,898) · **Shinjuku (10,083 → 3 sub-chunks)** — 10 dispatches |
| Satoru Gojo (10,378) | Fearsome Womb + History block (3,254) · Vs. Mahito (47) · Kyoto (463) · Death Painting (283) · Shibuya (1,145) · Culling Game (77) · **Shinjuku (5,107 → 2 sub-chunks)** — 8 dispatches |
| Megumi Fushiguro (9,813) | Fearsome Womb + History (1,519) · Kyoto (673) · Death Painting (627) · Shibuya (1,411) · **Culling Game (4,301 → 2 sub-chunks)** · Shinjuku (1,269) · Modulo (13) — 8 dispatches |
| Yuta Okkotsu (8,268) | Fearsome Womb + History/Cursed Child (2,127) · Shibuya (238) · Culling Game (3,705) · Shinjuku (2,114) · Epilogue (44) · Modulo (40) — 6 dispatches |
| Maki Zenin (6,530) | Fearsome Womb + History block (616) · Kyoto (538) · Death Painting (24) · Shibuya (589) · Culling Game (3,171) · Shinjuku (1,410) · Epilogue (63) · Modulo (119) — 8 dispatches |
| Choso (5,927) | Kyoto + History (127) · Death Painting (57) · Shibuya (1,107) · Culling Game (3,809) · Shinjuku (827) — 5 dispatches |
| Kinji Hakari (4,816) | Fearsome Womb + History (112) · Culling Game (3,810) · Shinjuku (894) — 3 dispatches |
| Nobara Kugisaki (4,770) | Fearsome Womb + History (1,085) · Kyoto (570) · Death Painting (872) · Shibuya (845) · Shinjuku (866) · Epilogue (183) · Modulo (349) — 7 dispatches |
| Kenjaku (4,538) | Fearsome Womb + History (761) · Vs. Mahito (151) · Kyoto (127) · Death Painting (86) · Shibuya (1,690) · Culling Game (1,192) · Shinjuku (531) — 7 dispatches |

74 dispatches in total. **Protocol:** pages largest → smallest; within a
page, ordinal arc order; one subagent dispatch per unit, **strictly
sequential** (wait for the previous unit's gate output + re-run before
starting the next — never parallel).

Per-unit correctness check is two-layered: (1) the `add` verbatim-gate
output (added-count + section-counts) — a non-verbatim answer aborts the
whole add and writes nothing (exit 2), which is what catches authoring
errors; (2) a whole-character `page-run` (retrieval check) immediately
after, **after every unit** while the API is on the GPU: ninfer's 27B holds
~25.5 GB but its KV cache is preallocated (a fixed ceiling, not a floor) and
sits idle, leaving ~6.8 GB genuinely free, and the embedder + reranker need
~2 GB (NATIVE_MIGRATION_HANDOFF.md:57) — so per-unit re-runs are cheap
again. If the GPU is unavailable or a run OOMs, fall back to the CPU
protocol: gate-only per unit, plus a whole-character `page-run` at the
**halfway unit of the four biggest pages only** (Yuji 6/12, Sukuna 5/10,
Gojo 4/8, Megumi 4/8) and at page completion, detached + polled; re-check
whether CUDA is available again at each page boundary. Question style:
**no double-barrelled questions** from unit 4 onward (two single-fact
questions test more than one compound question); 001–045 predate the
preference and stay as-is. Checkpoint after each unit: the ledger entry
names which units of the page are done and which remain.

## Tier 2 — wave table (26 waves, 4,000-w cap, largest first)

> **SUPERSEDED (2026-09-03 revision, State 105):** waves no longer exist; these 62 pages are inside the D1–D16 dispatch plan (section-count order), 1–2 questions per section.

Greedy packing of the 62 non-split pages (Mai keeps its sort position; the
pilot removed it from wave 18 without repacking). Words = live (non-skipped)
pages, facts.db counts.

| wave | pages (words) |
|---|---|
| 1 | Mahito (3,557) |
| 2 | Hiromi Higuruma (3,292) |
| 3 | Hajime Kashimo (3,182) |
| 4 | Panda (3,152) |
| 5 | Yuki Tsukumo (2,884) |
| 6 | Tengen (2,792) |
| 7 | Aoi Todo (2,700) |
| 8 | Mei Mei (2,526) |
| 9 | Atsuya Kusakabe (2,203) |
| 10 | Kento Nanami, Jogo (3,904) |
| 11 | Kokichi Muta, Noritoshi Kamo (3,728) |
| 12 | Kirara Hoshi, Naoya Zenin (3,561) |
| 13 | Suguru Geto, Toji Fushiguro (3,323) |
| 14 | Shoko Ieiri, Toge Inumaki (3,146) |
| 15 | Charles Bernard, Dabura Karaba (3,064) |
| 16 | Yoshinobu Gakuganji, Takuma Ino (2,939) |
| 17 | Kou Usami, Ui Ui (2,907) |
| 18 | Reggie Star (1,449) — *Mai Zenin skipped, pilot 16/16* |
| 19 | Kasumi Miwa, Uraume (2,756) |
| 20 | Masamichi Yaga, Junpei Yoshino, Momo Nishimiya (3,846) |
| 21 | Kiyotaka Ijichi, Hana Kurusu, Fumihiko Takaba (3,692) |
| 22 | Takako Uro, Eso, Utahime Iori, Dagon (3,995) |
| 23 | Rokujushi Miyo, Hanami, Rika Orimoto, Kurourushi (3,458) |
| 24 | Haruta Shigemo, Nanako Hasaba, Naobito Zenin, Ryu Ishigori, Miguel Oduol (3,882) |
| 25 | Mimiko Hasaba, Akari Nitta, Riko Amanai, Hagane Daido, Yorozu (3,628) |
| 26 | Kechizu, Tsumiki Fushiguro, Jiro Awasaka, Ogi Zenin, Manami Suda, Ogami, Tsurugi Okkotsu, Yu Haibara, Toshihisa Negi (3,898, 9 pages) |

Waves run in table order; within a wave, pages largest → smallest; a wave may
be one subagent run per page (several small pages can share a run when they
fit the 4,000-w budget together). Checkpoint every wave; a new engine finding
triggers an extra checkpoint (standing rule).

## Authoring protocol (per page / per dispatch unit)

- **Tool:** `temp_py_scripts/character_synopsis_wave_tool_dump_add.py`
  (`dump <slug>` / `add <slug> <spec.json>`; staged, verbatim-gated,
  G10-hardened atomic write — a failed `add` writes nothing, exit 2).
- **Source of truth:** section text from `facts.db` (the index store), never
  the crawl cache (it drifts from the current parser).
- **Question style:** natural, specific, subject-named — the questions a
  curious reader of that arc asks ("Who did Mai pair up with to assist Momo
  during the Spirit Bash Race?"). Answers are **verbatim** substrings of the
  section text (the gate enforces this: the exact answer string must occur in
  the facts.db section; a miss aborts the whole add).
- **Density:** ~11.4 questions / 1,000 words (pilot: 16 / 1,402 w). Every
  section with substantive prose gets at least one question; `Navigation` is
  skipped. Small sections (20–100 w) fold their one question into the
  adjacent arc's dispatch.
- **R5:** at most **one** natural yes/no question per page, only where the
  prose supports it (pilot: "Did Mai keep her cursed technique a secret
  before firing the seventh bullet at Maki?").
- **Batch record:** `kind: fact`, `expect_mode: qa`,
  `note: "prose: <Section>"` (section title, e.g. `prose: Culling Game Arc`,
  `prose: History`), single Fandom source, `verified` = authored date, ids
  `jjk-pg-<slug>-NNN`.
- **Failure rule (non-negotiable):** a miss is triaged as a **gold error**
  (answer is not what the page documents → fix the batch) or an **engine
  gap** (routing/chunking → diagnose and fix the root cause, or declare it in
  `series/jjk/overrides.yaml` naming this question). **Never reword the
  question to dodge a failure.**

## Verification loop and orchestrator checks

Per page (Tier 2) / per unit + whole-character re-run (Tier 1):

1. `dump <slug>` → author the spec JSON at the section level (verbatim
   answers only; no double-barrelled questions from unit 4 onward).
2. `add <slug> spec.json` → the verbatim-gate output (added-count +
   section-counts) **is** the per-unit authoring check. A miss aborts the
   whole add (writes nothing, exit 2) → fix the spec, re-add.
3. `page-run --series jjk --batch <slug>` (retrieval check) → **100% or
   diagnose the root cause.** On the GPU: after **every** unit (Tier 1) and
   per page (Tier 2). CPU fallback: Tier 1 only at the halfway unit of the
   four biggest pages (Yuji 6/12, Sukuna 5/10, Gojo 4/8, Megumi 4/8) and at
   page completion; Tier 2 per page as before; re-check CUDA at each page
   boundary.
4. Write the page report under `reports/page-campaign/jjk-<slug>-<ts>/REPORT.md`
   (the pilot's shape: headline table, failures to triage, all-questions table).

**Orchestrator (after every wave / checkpoint, not the subagent):**

- Batch-file question counts must match what the subagent claimed
  (re-read the JSON, don't trust the transcript).
- Independently re-run **at least one** page of the wave against the live
  server before writing it up as done.
- Health-check `:8000` at the start of every session.

Server note: while the GPU is held by another job the API runs on
`SCRIPTENGINE_DEVICE=cpu`; CPU page-runs are slow (~14 s/question) — a
200-question batch takes ~45 min, so kick them off detached and poll rather
than blocking.

## Numbers to expect

> **SUPERSEDED (2026-09-03 revision, State 105):** see the PROTOCOL REVISION section above. Total is now ~468 questions over 70 pages / 312 sections (16 dispatches).

| class | pages | questions (≈ 11.4 / 1,000 w) |
|---|---:|---:|
| Tier 1 (split, 10 pages, 94,937 w) | 10 | ~1,082 |
| Tier 2 (waves, 61 pages, 83,464 w) | 61 | ~952 |
| pilot already done (Mai, 1,401 w) | 1 | 16 (done) |
| **total** | **72** | **~2,050** |

## Standing rules (unchanged)

- The 5 deferred opens stay out of scope (1 conf-wrong on the jjk canon run;
  parser colon-truncation re-index, 17 workaround items; OOA Scroll Box;
  gallery-body-strip gap ep37-066; Trivia chunking gap).
- No edits to `scriptengine/` engine code, `overrides.yaml`, or any batch file
  outside the current wave's pages (except a `prose:` question on a page of
  this wave).
- Checkpoint on genuinely new engine findings (a router/retrieval gap), not
  on a fixed wave count.
- Nothing gets committed unless explicitly asked; the uncommitted router
  `against` fix from the technique wave stays as-is.

## Resume steps

> **SUPERSEDED (2026-09-03 revision, State 105):** see the PROTOCOL REVISION section above. The wave table and unit lists below are historical; the live plan is the D1–D16 dispatch table in the PROTOCOL REVISION section.

1. Health-check `:8000` (`curl -s -m 5 http://127.0.0.1:8000/health`); if
   down and the GPU is held, relaunch detached on CPU:
   `SCRIPTENGINE_DEVICE=cpu setsid nohup ./scriptengine/.venv/bin/python -m
   scriptengine.api.main > /tmp/scriptengine_api.log 2>&1 < /dev/null &`.
2. Tier 1, Yuji Itadori first: dispatch unit 1 (Fearsome Womb + History,
   `dump yuji_itadori_synopsis`), author, `add`, confirm the gate output,
   whole-character `page-run` (GPU) or the CPU-fallback timing, checkpoint.
   Then the remaining 73 units in table order.
3. Tier 2: waves 1 → 26 in table order; wave 18 is Reggie Star only.
4. After Tier 1 completes: checkpoint with the full unit ledger (done /
   pending per page). After Tier 2: wave ledger + final census re-scan
   (`temp_py_scripts/character_synopsis_census_scan.py` — its batch-prose
   coverage section should then read 72/72).