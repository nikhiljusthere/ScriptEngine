# PEER REVIEW R5 — process & operational safety (Phase 1C gate, round 2)

Reviewer: `r5_process_safety` · 2026-09-06 · branch `character-scoped-questions` @ `94909d2`
Weighting: evidence durability, halt logging, commit hygiene, operational state.
Live store read-only; no commits/pushes; `:8000` untouched. Every load-bearing
claim below was re-verified against the live store / process table / VCS this
session; commands + outputs are in the appendix.

## Verdict

**PROCEED-WITH-CHANGES.** The 1C gate is green: both reports are on disk, the
oracle's category splits (which flow.md's gate actually reads) are internally
consistent, and both plan-altering outcomes are identified (2B refuted; the
five subjective sections' extraction contested only by 1B's uncovered
fraction). The changes below are **record-blocking** (they must be satisfied
at/for the Phase-1 commit), not gate-blocking: NR1 (the "14/18" headline is
wrong — it is 11/18), NR2 (the 1B headline number is contested and must be
carried explicitly), P18 (promote the 20 /tmp evidence files + sha256 pins),
P19 (two missing halt-log entries), P21 (exact commit list — modified).

## Rulings on P1–P27

| item | ruling | reason (evidence inline) |
|------|--------|--------------------------|
| P1 | ACCEPT | Verified against the raw bundles: B2 `routed.why` = "question about 'Suguru **Geto**', a character"; B4 = "…'Satoru Gojo'…". Report A:96-97 quotes "Suguru Gojo" — a typo. Non-blocking; fix the quote when the council record is written. |
| P2 | ACCEPT | Clarification only: with `subject=None` the R6 floor is `if subject else []`, so B1 reached the bundle via the ranked beam. One-line clarification in the record. |
| P3 | ACCEPT (with a process note) | Fix the runner for future oracle runs. Process note: the promoted evidence (P18) is the **as-run** runner — pin its sha256 as-run; the fixed runner goes to the repo as a separate file, noted in COUNCIL_1 as post-hoc (no ground truth depended on relation rows, so verdicts stand). |
| P4 | ACCEPT | Non-blocking for the gate; load-bearing for 2A: the outcome join must bind the outcome to the specific fight (event level), not surface any battle infobox. |
| P5 | ACCEPT | Record **both**: ~42,500 words off the build list per the 1C rule **and** Phase 5 closed in full per its own gate (flow.md:236-243). |
| P6 | ACCEPT | flow.md:236 is Phase 5's "This phase may not exist." Report A:82-83 cites "Phase 4 personality extraction (flow.md:236)" — miscite; personality extraction is Phase 5 scope. Correct the citation in the record. |
| P7 | ACCEPT | The 1B corpus is the Summary slice (363 sections / 949 sentences), not the population. Quote as "61% of the Summary slice." |
| P8 | ACCEPT | Verified in-sample: row 047's main clause is "Nobara and Akari **encounter** Haruta Shigemo on the way" (PHASE1B:150 classifies it "fought (encounter + assessment)") — same event type as 008/018, so the met/encountered gap is 3/100, not 2/100. The pack's live corroboration figures (163 sections / 64 instances) are **not** independently verified by this reviewer — see Unverified. |
| P9 | ACCEPT | Rows 073 (covered, PHASE1B:176) vs 085 (uncovered, PHASE1B:188) are asymmetric under one rule. Record the 38–40/100 band; tighten the rule wording ("the main clause's eventive content governs"). |
| P10 | ACCEPT | DB-verified: the live `events` table (all 2,748 rows, every one under `events-2026-09-05.2`) has **93 `awakened`** and **4 `betrayed`** rows. The report's "Gojo's Prison Realm is `sealed`" justification is indeed no evidence for those two verbs. Rewrite the justification to cite the live rows. |
| P11 | ACCEPT | DB-verified: live `events` = **2,748** rows (2,594 is the `temporal=1` = `arc_index NOT NULL` subset); orphans in `location`/`organizations`/`item`/`technique` page types = 15+12+3+2 = **32** rows, outside `PLACEMENT_TYPES` and the character families. Quote 2,748 in the record; determine the 32 orphans' provenance before any `--refresh`. |
| P12 | ACCEPT | Reword "the same split the extractor sees" → "the engine's own sentence splitter" (the extractor reads windows, `events.py:1002`; the index uses `chunker.split_sentences`). |
| P13 | ACCEPT | DB-verified: the plan's own per-section list (42,533+14,180+16,731+15,887+11,595) sums to **100,926**; live `sections.word_count` = Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 / History 17,169 = **117,251**. flow.md:243's "~106,000" matches neither. Do not record "~106,000"; carry the live-verified number or note the staleness. |
| P14 | ACCEPT | E1–E4 are all `category: personality`; Appearance/Overview/Trivia/History leave the build list by the **gating condition** (Phase 5 never opens), not by section-specific evidence. The record must say so; a future phase needing one brings its own oracle evidence. |
| P15 | ACCEPT | DB-verified: **98** `outcome` rows exist in `facts` (key/label `%outcome%`: 96 `Outcome` + 2 empty-label), and all four A ground truths are in-store verbatim ("Nanami withdraws." chunks 1 / facts 1; "Sukuna is victorious." sections 3 / chunks 13 / facts 7; "Uraume commits suicide." chunks 1 / facts 1; "The jujutsu sorcerers are victorious." chunks 1 / facts 1). 2C-blocking, not 1C: 2A's spec must state the serving channel, or the fact-slice fix becomes a 2C precondition. |
| P16 | ACCEPT | With 2B refuted (F1/F2 pass at 1A) there is no F extraction, so the "F-group re-run" measures nothing. Reduce 2C to "A-group shows 2A's change; F-group unchanged (already passing at 1A)." |
| P17 | ACCEPT | The verb widening edits the events prompt's verb-rule list, so prompt v1 must be re-frozen **post**-widening against the widened set, with its own `PROMPT_VERSION` bump. Verified: all 2,748 cached rows sit under `events-2026-09-05.2` and stay untouched. The 24k pass remains not-runnable (1/4 green). |
| P18 | ACCEPT | Verified: `/tmp` is disk-backed ext4 (`/dev/nvme0n1p6`, not tmpfs) but systemd-tmpfiles reaps it at 30 days (`D /tmp 1777 root root 30d`); evidence = runner 8K + log 20K + 18 bundles 360K ≈ 390K; the repo already tracks raw gate output (`reports/comprehension/raw/`, 7 files). Promote all 20 files to `reports/comprehension/raw/oracle_1a/` and pin sha256s in COUNCIL_1 (manifest below). **Blocking for the record, not for the gate.** |
| P19 | ACCEPT | Verified: `plan/deviation_reasons.md` carries exactly two entries (pre-run cherry-pick; 0A meaning DDL) — no 2B halt, no Phase-5 premise refutation. Add two entries with raw evidence (2B: the F1/F2 PASS rows of PHASE1A_ORACLE.md:48-49 + the promoted raw paths; Phase 5: the E1–E4 PASS rows :44-47 + flow.md:236-243). **Process note:** the Phase-5 entry must not propagate "~106,000" (P13) — record "plan list 100,926 / live store 117,251; flow.md:243's ~106,000 matches neither." **Blocking for the record** (the halt is what makes the step real on disk; the gate does not wait on it). |
| P20 | ACCEPT | COUNCIL_1 must re-state the 24k status: 1/4 green (retention only, via 0C / `94909d2`), pass does not run (flow.md:96-97). |
| P21 | **MODIFY** | The pack's list is incomplete and the brief's "untracked" framing is partly wrong. Exact list below. |
| P22 | ACCEPT | Verified: PID 94330 started 2026-09-05 23:33:22 (+0530) = **18:03:22Z**; commit `94909d2` at **18:01:34Z** — the server serves committed code (report A:5 says 18:03:23Z; the 1s is process-start rounding, NR3). `SCRIPTENGINE_DEVICE=cpu` in `/proc/94330/environ` and the API log; Qwen (PID 3664, `ninfer-serve`) owns the GPU (24,670/32,607 MiB, single compute process). 2C control: after Phase-2 code lands, restart `:8000` on CPU and record server-start > commit in the 2C record, exactly as 1A did. |
| P23 | ACCEPT | Targets located and line-anchored: `main.py:207` (`route(..., subject=request.subject)`), `main.py:216/228` (subject passed into the builders), `context.py:225` (`_subject_facts(..., limit=24)`), `context.py:392` (the flat `result.facts[:30]` qa slice). `hybrid.py` untouched. |
| P24 | ACCEPT | Defer as a data ticket (alias-table over-match; audit single-token generic aliases at harvest; report same-alias collisions in `audit`; leave the `Grade` concept recall). |
| P25 | ACCEPT | State in the 2-prep task spec: the anchor is the router's `signals["subject"]`, not `rank_subjects()[0]` (which ranks "Hana Kurusu" first for both items). |
| P26 | ACCEPT | Re-anchor 4C (B-group holds + interval state table non-empty and cited by /context; any time-indexed-state probe is a new ORACLE_v2 item). Apply at 4C, record at 1C. ORACLE_v1 stays frozen. |
| P27 | ACCEPT | Verified: no `meaning` table exists in the live store (table list). P27's own live figures check out: events 2,748 ✓, `arc_index NOT NULL` 2,594 ✓, chapter/episode docs `temporal=1` 885 ✓. The "1,748 chapter-anchored rows" pilot population stays plan-side and unverified — state provenance; recompute when the `meaning` table is created; do not let it gate anything on faith. |

**Tally: 26 ACCEPT · 1 MODIFY (P21) · 0 REJECT.**

### P21 — MODIFY: the exact Phase-1 commit list

The pack's list omits `PEER_REVIEW_PACK_phase1.md`, and the brief's
"untracked paths" framing is wrong for two of them: `COUNCIL_HISTORY.md` and
`plan/deviation_reasons.md` are **tracked** (verified `git ls-files
--error-unmatch`) and arrive as modifications; `COUNCIL_1.md` **does not exist
yet** — it is the synthesis deliverable and must be created before the commit.
`events.py` has **no diff on disk** (`git diff --stat scriptengine/ingest/events.py`
is empty), so nothing of the verb widening belongs in this commit — it is
Phase-2 work (P17).

**Phase-1 commit (stage these named paths only):**

| path | status |
|------|--------|
| `reports/comprehension/PHASE1A_ORACLE.md` | A (with the NR1 heading fix: "Results — 11/18") |
| `reports/comprehension/PHASE1B_VERB_COVERAGE.md` | A (carrying NR2: 3/100 + the 38–40 band) |
| `reports/comprehension/PEER_REVIEW_PACK_phase1.md` | A (with the NR1 header fix: "11/18") |
| `reports/comprehension/COUNCIL_1.md` | A (created by the synthesizer before the commit) |
| `reports/comprehension/raw/oracle_1a/` (20 files: runner, log, 18 bundles) | A (P18; sha256s pinned in COUNCIL_1) |
| `reports/comprehension/COUNCIL_HISTORY.md` | M (append row #9 — the ledger's next number) |
| `plan/deviation_reasons.md` | M (append the 2B + Phase-5 entries, P19) |

**Excluded:** `reports/index.md` (tracked-M on disk; its diff adds five rows
referencing the untracked canon-run dirs `reports/2026-09-05-{1026,1041,1056,
1159,1751}/` — exclude and note in COUNCIL_1); `scriptengine/ingest/events.py`
(no diff on disk); and the ~700 other untracked paths (canon-run dirs,
`page-campaign/*`, `questions/*`, repo-root scratch incl. two `.deb` files,
`.claude/`, `opencode.json`). Standing rule flow.md:279: **named paths only —
never `git add -A` — and no push.**

## New defects

### NR1 — the "14/18" gate headline is wrong; the correct number is 11/18 (blocking-record)

Report A's heading `## Results — 14/18` (PHASE1A_ORACLE.md:28) contradicts its
own tables. The per-row table (:32-49) contains **11 PASS** (B1, B3, C2, C3,
D1, E1–E4, F1, F2) and **7 FAIL** (A1–A4, B2, B4, C1); the "Totals by
category" table (:53-61) sums to 0/4 + 2/4 + 2/3 + 1/1 + 4/4 + 1/1 + 1/1 =
**11/18** — the two tables agree with each other and contradict the heading.
The pack header (PEER_REVIEW_PACK:4-12) repeats "14/18" while listing the
same category splits, which sum to 11. "14" matches no defensible aggregate:
passes = 11, as-expected = 16 (18 − the 2 surprises B1/B4),
pass-and-as-expected = 10.

Impact: the gate verdict does not change — flow.md's gate reads the category
splits, and those are correct — but a wrong aggregate is exactly what COUNCIL_1
and every downstream record will inherit. Fix both headings before the commit.

### NR2 — the 1B headline is contested and must be carried explicitly (blocking-record)

Report B's headline "39/100 covered … `met/encountered` (2/100)" (PHASE1B:41,
:76) is contested by P8 (→ 3/100) and P9 (→ 38–40/100 band). Both corrections
are verifiable in-sample from the committed report itself (row 047's main
clause is "encounter"; rows 073/085 are asymmetric). As written, the Phase-1
commit would freeze the contested numbers into VCS. Before commit, either
report B (or COUNCIL_1) must explicitly carry P8's 3/100 and P9's 38–40 band,
or the rule is tightened and the sample reclassified. Do not silently carry
39/100 + 2/100. (The live corroboration figures in P8 are unverified — see
Unverified.)

### NR3 — 1A's server-start timestamp is off by a second (note, no action)

Report A:5 records server start `2026-09-05T18:03:23Z`; the process table
gives 23:33:22 (+0530) = 18:03:22Z. Both are after the commit (18:01:34Z), so
the "serving committed code" conclusion is unaffected and P22's control is
unchanged. If COUNCIL_1 cites the 1A server-start, use the ps-verified
18:03:22Z.

## sha256 manifest for COUNCIL_1 (P18)

Computed at review time (2026-09-06) from `/tmp`; recompute at promotion and
the values must match:

```
b42d1f4f584e88708fb6dfa3e8752c6f8efd3060ce27a5999072f88a2e5989fb  oracle_run1a.py
d273dc0124da799b82745ef07536bae029263ddb1f65548081219eb52fba9a4b  oracle_1a_results.txt
6e386eec6b283ac73309e6b258644b9f1d80984a680c00118350a9f0aff584cb  A1.json
ac114825bf5867e333c7f33f2587ea054b16e7573417c8192d84e03ac72887a1  A2.json
9a0c9281d531eb6b3d504e15b590cf543e9b2fffd1ed255ab97a8aef64f52250  A3.json
16dc0b506ab32ba6e360d42c3117368f060628dafc21359171a062e55ecc0661  A4.json
5a63041f97cac3fc838eb59c35cb5d0e17cd652db00e4962d99c817238ed7815  B1.json
d9aedff1c9920f9ef21c07ecbccfd0d745ddb87c64cbc256221581e3fbacf51c  B2.json
bb98a822d2017959e3a3316c702ef70ac9c9ccca4257308948081fe2ce006273  B3.json
1d66bccfecbe98ff93a35994413594e136d7623aa60e77ff9bf2873192b12310  B4.json
19c3ab7815917e4ddb9f0cc2d136be69322fc931eb2f3187ef3ab83ed51a79d7  C1.json
51cfa9fd2969c405de5167a83e6f5816f97aa9d3b7860c163fca7ea6143ee824  C2.json
25864505aad9cd6d7cac5dbbb307b33ecffe7253a77cd4b8158212e6b94cf18b  C3.json
40f3d9dfbe65a7778069547ee3b147480a16b333ccbd490e28c20b9caa53f46d  D1.json
cf41bf13cd84bfd0f2d45dd744474f1c876425084c08ec8db527df079a7c1501  E1.json
5a0a5cd1b1189b924b63e568002d4a5f2eeae101cbd4b7fe2f6c70d7f83ad6bf  E2.json
2ce66843c0256a9303d9f5f4ce3e95c57503778792821ca1f640a7d6c38da077  E3.json
7437cf8b1d2b4ce6bfad1ce7a08776e28fbb19c4f9012d3922d1b4c4fa30828b  E4.json
60bafa963b34f8c6d81591d0b31537fd08739add2725fbc4ea8754a6c94e9b7f  F1.json
5e05eab1bda323cabe7a06a627e8db4b06cd7a56f004facfffd09747fa0c72ef  F2.json
```

## Unverified claims (not independently checked by this reviewer)

- P8's live corroboration: 163 extraction-family sections carry
  encounter/crosses-paths/first-contact wording (64 sentence-level
  instances, lower bound). The in-sample basis of the correction (row 047)
  is verified; the corroboration figures are carried as the pack states them.
- P3's "all 18 verdicts were re-scored without effect" — an assertion about
  the runner's audit-text bug; consistent with the fact that no ground truth
  is a relation row, but the re-scoring itself was not reproduced here.
- P15's "the battle-page prepend path (hybrid.py:213-225) is immune" — the
  data side (98 outcome rows, four ground truths in-store) is verified; the
  retrieval-path immunity claim was not traced line by line.

## Appendix — verification commands and outputs

All store queries: `python3` + `sqlite3` in `file:series/jjk/facts.db?mode=ro`
(read-only URI; no `sqlite3` CLI on this machine).

1. **/tmp durability (P18).** `df -T /tmp` → `/dev/nvme0n1p6 ext4` (disk-backed,
   not tmpfs). `grep tmp /usr/lib/tmpfiles.d/tmp.conf` → `D /tmp 1777 root
   root 30d` (systemd-tmpfiles reaps after 30 days). `du -sh` → bundles 360K,
   runner 8K, log 20K (≈390K). `ls /tmp/oracle_1a_bundles` → 18 files
   (A1–A4, B1–B4, C1–C3, D1, E1–E4, F1, F2). Precedent: `git ls-files
   reports/comprehension/raw/` → 7 tracked raw gate outputs.
2. **ORACLE integrity.** `sha256sum plan/ORACLE_v1.yaml` →
   `a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e` = the
   frozen hash at flow.md:152-153 and PHASE1A_ORACLE.md:4.
3. **Git state (P21).** `git status --short` → the only tracked modification
   is `M reports/index.md`; its diff adds five rows referencing untracked
   `reports/2026-09-05-{1026,1041,1056,1159,1751}/`. `git ls-files
   --error-unmatch reports/comprehension/COUNCIL_HISTORY.md
   plan/deviation_reasons.md` → both tracked (unmodified). `COUNCIL_1.md`
   absent. `PEER_REVIEW_PACK_phase1.md`, `PHASE1A_ORACLE.md`,
   `PHASE1B_VERB_COVERAGE.md` untracked. `git diff --stat
   scriptengine/ingest/events.py` → empty (no verb-widening diff on disk).
   `git log -1 --format=%ci 94909d2` → `2026-09-05 23:31:34 +0530`
   (= 18:01:34Z).
4. **Server / GPU (P22).** `ps -o lstart= -p 94330` → `Sat Sep 5 23:33:22 2026`
   (= 18:03:22Z; after the commit). `ss -ltnp` → `:8000` = PID 94330.
   `tr '\0' '\n' < /proc/94330/environ` → `SCRIPTENGINE_DEVICE=cpu`;
   `/tmp/scriptengine_api.log` → "loading BAAI/bge-large-en-v1.5 on cpu".
   `nvidia-smi` → 24,693/32,607 MiB used, 100% util; compute-apps → single
   process PID 3664 (ninfer-serve Qwen 27B, 24,670 MiB). The `:8000` API is
   not on the GPU.
5. **Live store.** `events` COUNT = 2,748; every row under
   `prompt_version = events-2026-09-05.2`; `temporal=1` = 2,594 =
   `arc_index IS NOT NULL`. Verb distribution: fought 1,200 / arrived 526 /
   killed 314 / saved 289 / departed 288 / awakened **93** / sealed 34 /
   betrayed **4** (P10). Orphans by page type: location 15, organizations 12,
   item 3, technique 2 → **32** (P11). No `meaning` table in the store
   (P27). `facts` schema `(id, node_id, key, label, value, citation)`;
   outcome rows (key/label `LIKE %outcome%`) = **98** (96 `Outcome` + 2
   empty-label) (P15). Ground-truth presence: "Nanami withdraws." (chunks 1,
   facts 1); "Sukuna is victorious." (sections 3, chunks 13, facts 7);
   "Uraume commits suicide." (chunks 1, facts 1); "The jujutsu sorcerers are
   victorious." (chunks 1, facts 1) — all four in-store verbatim (P15).
   Geto: `occupation = "Jujutsu Sorcerer (Former) Curse User"`,
   `status = Deceased`; Gojo: `class = "Special Grade"`, `status = Deceased`
   (B2/B4 mechanism, Finding 3). Live `sections.word_count` for the five
   subjective sections: Personality 42,533 / Appearance 14,180 / Overview
   18,357 / Trivia 25,012 / History 17,169 = **117,251** (plan list sums to
   100,926) (P13). Chapter/episode docs: 923 events total, **885** with
   `temporal=1` (P27's figure).
6. **Bundle quotes (P1).** `json.load(/tmp/oracle_1a_bundles/B2.json)` →
   `routed.why = "question about 'Suguru Geto', a character"`; B4 →
   `"question about 'Satoru Gojo', a character"`.
7. **The 11/18 arithmetic (NR1).** From PHASE1A_ORACLE.md:32-49: PASS =
   {B1, B3, C2, C3, D1, E1, E2, E3, E4, F1, F2} = 11; FAIL = {A1–A4, B2, B4,
   C1} = 7. From :53-61: 0+2+2+1+4+1+1 = 11. Both tables contradict the
   :28 heading and the pack header's "14/18".
8. **Deviation log (P19).** `plan/deviation_reasons.md` → template + exactly
   two entries (pre-run cherry-pick; 0A meaning DDL); no 2B halt, no Phase-5
   refutation. flow.md:192-193 (2B premise / "IF REFUTED: HALT. Log to
   deviation_reasons.md with the raw output."); flow.md:236-243 (Phase 5 "may
   not exist" / "IF REFUTED: close the phase, record that ~106,000 words need
   no extraction" — the ~106,000 is the P13 figure). flow.md:279 (named paths
   only, never `git add -A`, no push).
9. **Ledger (P21).** `reports/comprehension/COUNCIL_HISTORY.md` → 8 rows,
   newest #8 (`COUNCIL_0`); the new row is **#9**.
10. **Code anchors (P23).** `main.py:207` `route(paths, request.query,
    subject=request.subject)`; `main.py:216/228` `subject=request.subject`;
    `context.py:225` `def _subject_facts(store, narrative, limit: int = 24)`;
    `context.py:392` `for fact in result.facts[:30]`.

## Notes for the chair (max 5)

1. 1C is green — the gate reads the category splits, and those are
   internally consistent; but the "14/18" headline in both report A and the
   pack is wrong (it is 11/18); fix both before the commit (NR1).
2. The 1B headline (39/100, met/encountered 2/100) is contested by P8 (→
   3/100) and P9 (→ 38–40 band); the committed record must carry the
   corrections explicitly, not freeze the contested numbers (NR2).
3. Record-blocking before commit: promote the 20 /tmp evidence files to
   `reports/comprehension/raw/oracle_1a/` with the sha256 pins (manifest in
   this ruling) and append the 2B + Phase-5 halt entries to
   `plan/deviation_reasons.md` — without carrying "~106,000" (use plan 100,926
   / live 117,251).
4. Phase-1 commit = the 7-item list in the P21 MODIFY (A×5 incl. the pack and
   COUNCIL_1, M×2); exclude `reports/index.md`; `events.py` has no diff on
   disk and is not in this commit; named paths only, never `git add -A`, no
   push.
5. Operational handoff: `:8000` = PID 94330 on CPU, serving `94909d2` since
   18:03:22Z; Qwen owns the GPU. Before any 2C re-run: restart `:8000` on
   CPU after the Phase-2 code lands and record server-start > commit (P22).