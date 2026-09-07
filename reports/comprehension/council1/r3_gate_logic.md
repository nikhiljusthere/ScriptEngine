# PEER REVIEW R3 — gate logic (1C, round 2)

## Verdict

PROCEED-WITH-CHANGES — "continue into Phase 2 on green" (flow.md:171-172) holds: every refuted premise (2B, Phase 5) resolves inside the plan (record + close; flow.md:47-50), so no flow.md:53 stop is required; proceed subject to the recorded amendments (2C reduction, 4C re-anchor as a pending owner decision, P19 log entries, P18 evidence promotion, P13 figure correction).

## Rulings on P1–P27

| Item | Ruling | One-line reason |
|---|---|---|
| P1 | ACCEPT | The 1A report misquotes the B2 oracle ground truth: the raw bundle says "Suguru Geto" (`/tmp/oracle_1a_bundles/B2.json` `why: "Suguru Geto"`), the report quotes "Suguru Gojo"; non-blocking quote typo, record the correction. |
| P2 | ACCEPT | R6's passage floor was inactive as run: `context.py:380` `passages = store.passages_for_subject(subject) if subject else []`, and the 1A items ran with `subject=None`; `B1.json` contains zero floor passages (no score-0.0 rows). |
| P3 | ACCEPT | The 1A runner's `bundle_text` reads `edge.get('label','')`, but B2's relation edges carry keys `[confidence, era, quote, relation, source, target]` (no `label`), so relation names were silently dropped from the bundle; fix the runner before any reuse. |
| P4 | ACCEPT | A4's ground truth "Sukuna is victorious" is not in `A4.json`; the bundle instead carries `('Sukuna vs. Jogo','Outcome','Sukuna is victorious.')` — a different battle's outcome fact; A1–A3 have no outcome facts at all. |
| P5 | ACCEPT | The 1A report records only the 42,500-word Personality leave (line 122) and omits that the whole Phase 5 closed per its gate; both must be in the record. |
| P6 | ACCEPT | The 1A report cites "Phase 4" for the personality extraction; personality is a Phase 5 item (flow.md:231-243; Phase 4 is state-over-time, 214-227) — miscite, record the correction. |
| P7 | ACCEPT | 1B's 61% uncovered figure covers only the Summary slice: live, the 363 chapter/episode pages carry Summary 363 sections/16,194 words vs Plot Details 363 sections/241,855 words on the same pages — the slice point stands, the figure's scope must be stated. |
| P8 | MODIFY | The 2/100 → 3/100 correction is right (row 047 "encounter Haruta Shigemo" was bucketed fight-adjacent as "fought (encounter + assessment)"; 008/018/047 are the same event type), but the live corroboration is uncitable: see replacement. |
| P9 | ACCEPT | 073 (covered, fought) vs 085 (uncovered, "fought (observation)") is an uneven application of the same governing-main-clause reading; record the 38–40/100 band and tighten the rule wording, not just the headline. |
| P10 | ACCEPT | 1B's keep-`awakened`/`betrayed` justification cites a `sealed` usage (line 98) — the wrong verb; live rows (93 `awakened`, 4 `betrayed`) show the verbs carry real rows; re-quote the right evidence. |
| P11 | MODIFY | The 2,748 total and the 32 orphans are verified, but the stated loss mechanism is wrong under the current code; see replacement. |
| P12 | ACCEPT | The extractor windows prose with its own splitter (`events.py:34` import, `:1002` call) while the index chunks with `chunker.split_sentences` (`chunker.py:107`) — the two sides see different sentence boundaries. |
| P13 | ACCEPT | "~106,000" is stale twice: plan's own section list sums to 100,926; live sums to 117,251; record the live figure. |
| P14 | ACCEPT | E1–E4 are all `category: personality` in ORACLE_v1; no oracle item covers the other four Phase-5 sections, which leave by the gating condition (flow.md:236) because the phase never opens, and the phase closes per its gate (243) — the pack's reading follows from the text; say so in the record. |
| P15 | MODIFY | The coupling (2A spec states its serving channel, or the fact-slice fix becomes a 2C precondition; blocking for 2C not 1C) is the minimal faithful resolution and is verified — but the item's cross-reference is wrong; see replacement. |
| P16 | ACCEPT | With 2B refuted there is no F extraction, so 2C's "F-group re-run showing the change" is vacuous as written; reduce 2C to "A-group shows 2A's change; F-group is a no-change regression check (F1/F2 passed at 1A and must hold)" — a gate repair (flow.md:56-63), not a re-interpretation of the 2B halt. |
| P17 | ACCEPT | Widening EVENTIVE_VERBS (events.py:43-54, injected at `:1008` into the prompt rule at `:640-641`) edits the prompt, so it re-freezes precondition 2 with a PROMPT_VERSION bump (currently `events-2026-09-05.2`, events.py:620); all 2,748 rows are cached under that version (verified) and untouched; the 24k pass stays 1/4 green. |
| P18 | ACCEPT | The gate evidence (runner, log, 18 bundles, ~390K) sits in `/tmp`, which here is ext4, not tmpfs (`findmnt /tmp` → `/dev/nvme0n1p6`); the repo already tracks raw gate output in `reports/comprehension/raw/`; promote + sha256-pin before 2C. Blocking for the record. |
| P19 | ACCEPT | The step contract (flow.md:15-16), condition 3 (line 71) and the standing rule (line 280) require `deviation_reasons.md` entries for the 2B halt and the Phase-5 premise refutation; the file currently holds only Pre-run + 0A. Blocking for the record; exact entries below. |
| P20 | ACCEPT | flow.md:96-97 makes the 24k precondition state a record item: Phase 1 touched nothing on preconditions 2–4 and the verb widening (P17) re-opens precondition 2, so COUNCIL_1 must restate 1/4 green (retention only), matching COUNCIL_0's ledger. |
| P21 | ACCEPT | The commit list is right and checkable: `git status` confirms `reports/index.md` is the tracked-modified file and the `reports/2026-09-04-*` / `2026-09-05-0333*` dirs are untracked; the list must also carry the P19 entries and the P18 promotion, and exclude `index.md`. |
| P22 | ACCEPT | The stale-server trap is real and precedented: PID 94330 runs `SCRIPTENGINE_DEVICE=cpu` with lstart `Sat Sep 5 23:33:22 2026` local = `18:03:23Z`, matching 1A line 5's note ("server start … after the commit, so the committed code served every item"); restart `:8000` on CPU before 2C and record server-start > commit again. |
| P23 | ACCEPT | The 2-prep fix is correctly shaped: `main.py:89/207/216/228` passes only `request.subject` (never `signals['subject']`); `facts_for` is a plain `n.name` match (facts.py:1077-1083); `result.facts[:30]` slices flat (context.py:391) while the battle-page prepend (hybrid.py:213-225) is immune; gate = 18-item re-run + standing gates. |
| P24 | ACCEPT | The alias table confirms the over-match: `sorcerer` → Hana Kurusu AND Jujutsu Sorcerer; `gojo` → Satoru Gojo AND Sorcerer Clan; `geto`/`pseudo-geto` → Kenjaku (and `geto` also Suguru Geto); live `rank_subjects` for B2 ranks Kenjaku 2nd ahead of Suguru Geto — defer as a data-quality ticket; after P23 no oracle item depends on it. |
| P25 | ACCEPT | `rank_subjects(link_entities(q), demote, priority)[0]` returns "Hana Kurusu" first for both the B2 and B4 questions (verified live) — type-priority, not question relevance; the correct anchor is the router's `signals['subject']` (Suguru Geto / Satoru Gojo), which the 1A bundles show working. |
| P26 | MODIFY | 4C does go vacuous (B1 PASS at 1A; B2 expected green after 2-prep), but the re-anchor is not inside the council's authority to apply — it amends a future gate's criterion, which condition 7 (flow.md:78) reserves to the owner; see replacement. |
| P27 | MODIFY | The "1,748" point stands (no `meaning` table exists in the live store; nothing on disk equals 1,748), but the item's own corroborating figure is wrong; see replacement. |

Tally: 22 ACCEPT / 5 MODIFY / 0 REJECT.

### Replacement texts (MODIFY items)

**P8** — keep "The met/encountered gap is 3/100, not 2/100 (rows 008, 018, 047; 047 was bucketed 'fought (encounter + assessment)')". Replace the corroboration sentence with: "Live corroboration: 112 sections in the placement ∪ character families carry encounter/crosses-paths/first-contact wording (135 phrase occurrences; query: `lower(text) LIKE '%encounter%' OR LIKE '%crosses paths%' OR LIKE '%first contact%'` over `page_type IN PLACEMENT_TYPES OR page_type LIKE '%character%'`)". The original "163 sections / 64 instances" is not reproducible without its query; state the query or soften to the verified counts.

**P11** — keep "Live events = 2,748 rows (2,594 is the `temporal=1` subset, all arc_index NOT NULL); 32 rows (1.2%) sit in location/organizations/item/technique page types (15+12+3+2) in neither PLACEMENT_TYPES (events.py:59) nor the character families (events.py:834-840)". Replace "A `--refresh` under the current scope would drop them — a latent derived-row-loss exposure" with: "A `--refresh` under the current scope does NOT touch those pages (`save_events` replaces per-arc only, facts.py:1782; `scope_plan` events.py:886 excludes them), so the 32 rows persist as dead weight; the exposure is (a) a scope change that covers those pages, where per-arc replacement then drops any rows the new extraction does not re-prove (condition 4, flow.md:72-73), or (b) a rebuild that orphans their sections. Determine the 32 orphans' provenance (presumably an earlier, broader scope) before any such run."

**P15** — in "or the fact-slice fix (P24) becomes a 2C precondition", replace "(P24)" with "(P23)": the fact-slice fix is P23 (the 2-prep sub-step); P24 is the linker over-match.

**P26** — keep the finding (4C "B1 and B2 must move", flow.md:226, is vacuous: B1 already PASS at 1A and B2 is expected green after 2-prep). Replace "Apply at 4C, record at 1C" with: "Record at 1C as a PENDING OWNER DECISION, not a council-applied amendment: the plan grants the council authority to repair a halt (flow.md:56-63) but not to amend a future gate's criterion, and condition 7 (flow.md:78) reserves out-of-file scope to the owner. The plan text must gain, at 4C (flow.md:226): 'B-group holds (no regression against the 1A baseline) and the interval state table (4A's output) is non-empty and cited by /context; true time-indexed probes only via a council-approved ORACLE_v2 — ORACLE_v1 is frozen (plan/ORACLE_v1.yaml header; flow.md:158-159)'. The deviation_reasons entry's 'what would unblock it' is: owner approval of the 4C re-anchor (a decision, not an action)."

**P27** — replace "events in Chapter/Episode docs 885" with "events in chapter/episode docs 923 (629 chapter + 294 episode; `SELECT count(*) FROM events e JOIN documents d ON d.title=e.doc_title WHERE d.page_type IN ('chapter','episode')` → 923)". Keep: no `meaning` table exists in the live store; nothing on disk equals 1,748; state the provenance (or recompute when the table lands) rather than gating on it.

### P19 — exact deviation_reasons.md entries (blocking for the record)

```markdown
## 2B — "oracle F1/F2 failed at 1A" refuted 2026-09-06
- **premise as written:** (flow.md:192) "oracle F1/F2 failed at 1A (i.e. retrieval does not already serve these)"
- **verified on tree:** branch character-scoped-questions, HEAD 94909d2; engine state per PHASE1A_ORACLE.md line 5 (:8000 on CPU, server start 2026-09-05T18:03:23Z, after the commit)
- **what the check returned:** 1A table rows (PHASE1A_ORACLE.md lines 48-49): F1 PASS ("Todo Equipment section served (Playful Cloud entry)"), F2 PASS ("Todo Quotes section served"); raw bundles (post-P18 promotion) reports/comprehension/raw/oracle_1a/F1.json, F2.json; oracle sha256 a788fa… verified against plan/ORACLE_v1.yaml
- **why the step cannot proceed as written:** retrieval already serves Equipment and Quotes in plain phrasing; the extraction premise is false, so the step's IF REFUTED branch (flow.md:193) applies: "no extraction owed — halt and record"
- **what is now blocked:** nothing — the 3,782 + 1,518-word extraction is not owed; the step halts without substitution (deviation_reasons.md header: "A deviation is a refusal")
- **what would unblock it:** nothing to unblock; an ORACLE_v2 item showing retrieval failing on Equipment/Quotes would be new owner scope, not a re-opening of this step

## Phase 5 — "E1–E4 failed, and the failure is retrieval-shaped" refuted 2026-09-06
- **premise as written:** (flow.md:241) "E1–E4 failed, and the failure is retrieval-shaped rather than chunking-shaped"
- **verified on tree:** branch character-scoped-questions, HEAD 94909d2
- **what the check returned:** E1–E4 all PASS (PHASE1A_ORACLE.md lines 44-47; bundles reports/comprehension/raw/oracle_1a/E1–E4.json) → the phase-opening condition (flow.md:236 "opens only if oracle E1–E4 failed at 1A") is false
- **why the step cannot proceed as written:** IF REFUTED (flow.md:243): "close the phase, record that ~106,000 words need no extraction" — the phase closes per its own gate
- **what is now blocked:** nothing — the subjective set leaves the build list. Word count, live-verified: 117,251 (`SELECT sum(word_count) FROM sections GROUP BY title`: Personality 42,533 / Appearance 14,180 / Overview 18,357 / Trivia 25,012 / History 17,169); flow.md:233-234's list sums to 100,926 and line 243's "~106,000" is stale (Overview/Trivia/History grew since the plan was written) — record the live figure, not the plan's
- **what would unblock it:** nothing; the phase is closed, not substituted. Any future need for these sections must bring its own oracle evidence (ORACLE_v1 is frozen)
```

Plus the P26 pending-decision note in the same file: "**what would unblock it:** owner approval of the 4C re-anchor (flow.md:226) — a decision, not an action."

## New defects (NR1..NRn)

**NR1 — P15's internal cross-reference is wrong** (blocking-record / note). The pack's P15 says "the fact-slice fix (P24) becomes a 2C precondition", but the fact-slice fix is P23 (pack: "P23 — The fact-slice fix shape (new 2-prep sub-step, before 2A)"); P24 is "The linker over-match". Evidence: PEER_REVIEW_PACK_phase1.md lines ~121-125 vs ~173-174 vs ~188-189. Disposition: note — corrected in the P15 replacement above.

**NR2 — P27's corroborating count 885 is wrong; live value is 923** (note). `SELECT count(*) FROM events e JOIN documents d ON d.title=e.doc_title WHERE d.page_type IN ('chapter','episode')` → 923 (629 chapter + 294 episode). The substantive P27 point (1,748 unverified, no `meaning` table) stands. Disposition: note — corrected in the P27 replacement above.

**NR3 — P8's live corroboration is not checkable as written** (note). "163 sections / 64 sentence-level instances" does not reproduce from a plain query; my LIKE query (three phrases, placement ∪ character families) yields 112 sections / 135 phrase occurrences. The standing rule (flow.md:266-271) requires checkable evidence. Disposition: note — the P8 replacement supplies the query.

## Unverified claims

1. P18's "systemd-tmpfiles reaps /tmp at 30 days" — not checked (no systemd config inspection); the load-bearing part (not tmpfs, survives reboot) is verified via `findmnt /tmp` → `/dev/nvme0n1p6` ext4.
2. P11's 32-orphans provenance (how `events-2026-09-05.2` extracted rows on out-of-scope pages — presumably an earlier broader scope) — not established; that is precisely the point of the required action (determine before any scope-affecting run).
3. P7's "~13,115 more sentences" in Plot Details — sentence count not computed (splitting is the index's job); the slice point is corroborated by word counts (Plot Details 241,855 words vs Summary 16,194 on the same 363 pages).
4. P23's predicted gate outcomes (B2 green post-fix) — a prediction; the fix is not yet implemented, so it cannot be verified at 1C.
5. P8's original 163/64 figures (see NR3).

## Notes for the chairman

1. Every flow.md citation in the pack checks out (15-16, 47-50, 56-63, 71, 78, 89-90, 96-97, 171-178, 184-186, 192-193, 195-196, 226, 236, 241-243, 280); the 1A/1B miscitations (P1, P6, P10, P13) are real and must be fixed in the record, not waved through.
2. The 2B halt and the Phase-5 closure are both in-plan (flow.md:193; 243) and their `deviation_reasons.md` entries are blocking-for-the-record (P19, exact text supplied); the 2C reduction (P16) and the 1C auto-actions are in-plan authority; the 4C re-anchor (P26) is NOT in-plan — condition 7 (flow.md:78) — record it at 1C as a pending owner decision with the exact plan-text addition supplied.
3. The 24k pass remains 1/4 green (retention only); the verb widening re-opens precondition 2 (re-freeze + PROMPT_VERSION bump, post-widening); all 2,748 event rows are cached under `events-2026-09-05.2` and untouched.
4. No flow.md:53 stop is required: every refuted premise resolves inside the plan (record + close), so "continue into Phase 2 on green" (171-172) holds subject to the recorded amendments.
5. Tally 22 ACCEPT / 5 MODIFY / 0 REJECT; 3 NR (NR1–NR3, all note-class, none gate-blocking); before 2C: P19 entries, P18 promotion to `reports/comprehension/raw/oracle_1a/`, CPU restart of `:8000` with a server-start > commit note (P22), and the P13 live figure (117,251, not ~106,000) in the record.