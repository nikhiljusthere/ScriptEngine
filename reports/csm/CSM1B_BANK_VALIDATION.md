# CSM-1b — stamped-bank validation against the current index (2026-09-08)

Owner directive (2026-09-08): validate the just-stamped seed bank against the
current index (post-G15 re-index); fix stale gold expectations in place with
the reason recorded in the campaign record; **no new questions in this pass**.
Raw receipts only.

## Bank runs (live store: re-indexed post-G15; `:8000` on CPU, code-fresh)

| run | command | result |
|---|---|---|
| pre-fix | `cli canon-run --series csm` | `reports/2026-09-08-0746` — 11/19 exact, 138/146 canon (94.5%), 2 questions at recall 0, facts 17/18 |
| post-fix | `cli canon-run --series csm` | `reports/2026-09-08-0752` — 11/19 exact, 138/148 canon (93.2%), 2 at recall 0, facts 17/18 |
| relations bank | `tools/csm/validate_relations.py` | `reports/csm/CSM1B_RELATIONS_BANK.md` — 0/11 complete (see G-CSM-4) |

The relations bank (`questions/_csm_relations.json`, 11 questions,
`expect_mode: relations`) is underscore-prefixed, so it stays out of the
official canon bank (`questions.load_all` skips `_` files) — the runner is the
validation path for it.

## In-place gold fixes (4) — each reason also recorded in the bank's `note`

1. **`csm-set-02` "Every ability of Power"** — dropped the `Blood Weaponization`
   item. Evidence: the current Power page documents no such item (live wikitext
   2026-09-08, revid 44435, last edit 2026-07-11) — weapon formation is
   documented under `Blood Manipulation`, whose seven named weapon items the
   engine returns in full; **0 store hits** for the term. Item is a 2026-08-04
   authoring artifact. *Effect: recall 13/14 → 13/13 (exact).*
2. **`csm-char-04` "Every ability of Makima"** — renamed `Prime Minister
   Contract` → `Contract with the Prime Minister of Japan` (old name kept as
   alias). Evidence: the wiki and store never name it `Prime Minister Contract`
   (**0 store hits**); the Contract page's Occurred-Contracts table and the
   Makima prose say `a contract with the Prime Minister of Japan`. The
   underlying fact is unchanged; the abilities path still does not return it
   (engine gap, G-CSM-2 — not tuned around in this pass).
3. **`csm-fact-06` "What is Denji's hybrid transformation trigger?"** —
   expected phrase `Pulling the cord on his chest` → `Pulling a cord on his
   chest`. Evidence: corpus wording on the Denji page (live wikitext and
   store: `can become the Chainsaw Man by pulling a cord on his chest`); the
   fact scorer is word-boundary containment, so the article difference was a
   guaranteed miss. Still misses post-fix — the qa bundle is empty for this
   question (engine gap, G-CSM-2).
4. **`csm-set-14` "How many special divisions exist in Public Safety Devil
   Hunters?"** — canon was 2 (Tokyo Special Division 4/5): the original
   expectation counted what its single source page (Makima) mentioned. The
   2026-08-15 roster audit (`series/csm/overrides.yaml`, declared roster
   `The Public Safety special divisions`) found **five** divisions named in the
   corpus (TSD 1/4/5/6/7) and the wiki states no total. Answer now matches the
   declared roster; source moved to the Public Safety Devil Hunters page (a
   redirect to `Devil Hunter`, revid 44432 — re-stamped). Recall is 0/5 until
   the engine gap G-CSM-1 is closed.

Re-stamp after the source change: `tools/csm/stamp_revids.py` (redirect
handling fixed this pass — see below) → **19 pinned pages, 0 unpinnable**;
`questions/csm.json` 39/39 active stamped, `questions/_csm_relations.json`
11/11 stamped. CSM-1's inventory (18-page revid map) is superseded by this.

## Engine gaps (numbered; deferred to CSM-3 / CSM-7; no retriever tuning in
this pass — standing rule)

- **G-CSM-1 — count phrasings bypass the declared-roster door.** The router
  sends both count questions to `qa` (entity hits: 'Devil', organization
  'Four Horsemen'); the QA bundle then carries 0 members, so
  `csm-set-14` (0/5) and `csm-set-15` (0/4) sit at recall 0. The roster door
  itself answers both correctly — `build_roster` returns the 5 declared
  divisions and the 4 Horsemen for the exact question texts (verified in
  process). Fix belongs to CSM-3's door work.
- **G-CSM-2 — the qa passage leg returns nothing on CSM for subject-named
  questions.** "What is Denji's hybrid transformation trigger?" returns
  **0 passages even with explicit `subject: "Denji"`**; the bundle is
  answered by facts (23–30) + relations (20) channels alone. Facts documented
  only in prose (the Denji trigger; Makima's PM contract) are unreachable.
- **G-CSM-3 — section-scoped intruders on "Every ability of X"** (known
  class, from the 2026-09-08-0746 run: "Every ability of Aki Hayakawa" 7
  intruders, mostly `Abilities / Antemortem Abilities / Devil Contracts`;
  "Who are the members of Tokyo Special Division 4?" 7 intruders).
  Chunker/skip-set work — CSM-3's item.
- **G-CSM-4 — the relations door is unreachable through auto-routing.** All
  11 relations-bank questions route to `roster` ("asks for a set"); the
  `relations` channel exists only on qa-mode bundles, and no router mode
  satisfies the bank's declared `expect_mode: relations`. Raw per-question
  table: `reports/csm/CSM1B_RELATIONS_BANK.md`.

## Tool fixes committed with this pass (`tools/csm/stamp_revids.py`)

- Fandom 403 on the bare urllib UA → the crawler's UA (`config.py user_agent`).
- tuple-unpack swap wrote the empty *prev* map and **wiped the questions
  lists** (restored from git before the fix; the bug is named in the code).
- CRLF bank files were rewritten LF (whole-file diff churn) → the file's own
  line endings are preserved; `indent_of` now measures the file instead of
  computing a wrong indent.
- **redirects**: the redirect chain was read from `query.normalized`
  (underscore/space spellings — a different field), so a source URL that
  redirects (Public Safety Devil Hunters → Devil Hunter) reported "no page
  found" and its revid landed under the target key; fixed to read
  `query.redirects` and alias the requested title to the target's entry.

## Gate re-baseline

Deferred to the **gpu-live2 side session** (owner correction, 2026-09-08:
262k holds the card → 100k+CUDA side session, never a CPU fallback for
GPU-beneficial work): `plan/gpu_live2.spec` + `plan/gpu_live2_task.md` →
report `reports/csm/GATE_REBASELINE.md` (pytest full on CUDA, eval jjk,
span-recall jjk offline + `--probe 400` on a CUDA `:8000`, canon opm).

Diagnostic only (not the re-baseline): under 262k+vision the pytest suite
OOMed on CUDA for 6 cases in `tests/test_context.py` (Qwen holds ~29.6 GiB;
~1.6 GiB free < the ~5.3 GiB the embedder needs) and passed 1242/1242 with
`SCRIPTENGINE_DEVICE=cpu` (265 s). The 6 cases are listed in the live-2
brief and must pass on GPU.