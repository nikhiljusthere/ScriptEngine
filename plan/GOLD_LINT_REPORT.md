# Gold v2 lint report (stage 8a, 2026-11-03)

Read-only lint of the gold v2 set, using the latest `gold_audit_v2.jsonl` record per window. Nothing was applied.
The audit, the label files and the fix files were not written: two review agents were still finishing
b1841-b1849 and b2187-b2236.

**Snapshot linted:** `big/gold_v2/gold_audit_v2.jsonl`, 3,868 lines, sha1 `2f0dd315…`, last write 12:40:24.
All 3,822 gold windows have an audit record (at 12:30 13 were still missing, b2224-b2236; the agents finished
them before the final runs). If an agent appends more records, re-run the commands in §6. The tools rebuild
from the audit as it is at that moment.

## 1. How the big-set lint tools behave with `BV2_SET=gold`

| tool | gold behaviour | verdict |
|---|---|---|
| `lint.sh` (lint_v2.py) | works read-only. When a window has no audit record it lints the 35B label rows instead, and it then prints `missing 0`, so an unfinished review looks complete. `--regate` works on all nine series. | usable, but a gold wrapper was written so unreviewed windows show up |
| `lint_fix.sh` (lint_fix.py) | built for the *unreviewed* gold set (2026-10-14). It **skips every window that has a gold audit record** and rewrites `gold_labels_v2.jsonl` for the rest. On the reviewed set it does nothing useful, and run without `--dry` it rewrites the label base | not usable for stage 8a |
| `lint_work.sh` (lint_work.py) | `build` reads audit records only (no proposal overlay) and writes **`big/lint/work_{app,term}.txt`**, which overwrites the big-set reading lists. `show B` works | do not run `build` with gold |

New gold-only copies in `plan/review_tools/`. The originals are unchanged, so the big set behaves as before.

- `lint_gold.py` / `lint_gold.sh [--regate] [--show CHECK] [--json OUT]`. Runs lint_v2's checks and adds:
  - the count of unreviewed windows;
  - lint_work's filtered classes `name_short_and_full_person` and `E_A145_same_sentence`;
  - overlap checks `R_overlap_inconsistent` / `R_overlap_cross_split` (via recon_lib; the gold set never had a recon pass);
  - advisory `X_*` classes for open rulings;
  - a re-gate with progress output (75 s).
  It writes only the `--json` file.
- `lint_gold_fix.py` / `lint_gold_fix.sh build | apply [--yes] [--allow-missing] | build --raw-m2`. Runs lint_fix's M1-M6
  on the latest gold audit record, with the same fact and tag gates as `rv.sh fix`.
  - `build` writes a proposal and never touches the audit.
  - `apply` without `--yes` is a dry check. It refuses while any gold window has no audit record. It also refuses any proposal
    whose window got a newer record after the build (`base_sha` check).
  - `apply --yes` backs the audit up to `.bak-pre-gold-lint-<time>`, then appends the records with `why: "lint M…"`.
  - M2 is narrowed to the same act (see §3).
- `lint_gold_work.py` / `lint_gold_work.sh build [--regate JSON] | show B`. Builds the reading list from lint_work's READ classes.
  - It works on the audit with the mechanical proposal overlaid, so rule-decided rows are not read twice.
  - It adds `M_refused`, `R_overlap_inconsistent`, `REGATE_*` and `UNREVIEWED` classes.
  - Overlap partners are grouped. Output is one file, `gold_v2/lint/work_gold.txt`, in the big-set line format `b<n> G<group> CLASS,...`.

Output files: `series/universal/training/big/gold_v2/lint/` (main checkout, new directory). This directory holds
`lint_gold.json`, `lint_gold_regate.json`, `proposed_mechanical{,_refused}.jsonl`,
`proposed_mechanical_diff.txt`, the `*_rawM2.*` measurement files and `work_gold.txt`.

## 2. Lint classes on the reviewed gold set

R = needs reading (on the reading list). M = rule-decidable. I = informational, not an error by itself. A = advisory,
waiting on an open ruling (§5).

| class | rows | windows | kind | example windows |
|---|---:|---:|---|---|
| E_met_and_fight_same_pair | 80 | 67 | R (A145: a confrontation that becomes the fight gets no met) | b39 b104 b110 b264 b537 b627 b647 b704 b738 b905 |
| E_A145_same_sentence | 43 | 32 | R (fought + defeated/killed quoted in one sentence; drop fought only for one coordinated act) | b825 b1048 b1074 b1082 b1098 b1116 b1233 b1292 b1299 b1322 |
| E_A145_fought_and_defeat (raw) | 205 | 158 | I (the same-sentence subset above is the reading class; separately stated fights stay) | b30 b105 b131 b185 b190 b288 b298 b317 |
| name_short_and_full_person | 42 | 36 | R (A4 one name per person). Most hits are legitimate distinct entities: Future Goku/Goku, Goku Black, Cell Juniors, Sōkyoku Hill, Mecha Frieza. Real candidates: b1071 Naoya/Naoya Zenin, b830 Cold/King Cold | b358 b830 b875 b907 b931 b944 b1015 b1062 b1071 b1790 |
| name_short_and_full (raw) | 52 | 45 | I (includes place-like pairs) | |
| F_A89_event_twin | 16 | 15 | R (quote-blind M2 would delete them; all 16 are a different act, see §3) | b289 b1183 b1686 b2125 b2245 b2297 b2326 b2459 b2638 b3095 |
| R_overlap_inconsistent | 8 pairs | 15 | R (shared sentences carry different rows; partners grouped) | b190/b3346, b1084/b1256, b1201/b1223 (`Live` vs `live`), b1432/b1521/b1711 (`Gojo` vs `Satoru Gojo`; `Sukuna\|wounded\|-` vs `Satoru Gojo\|wounded\|Sukuna`), b1485/b1675, b1854/b2155 (sibling_of direction), b3723/b3728 (test) |
| R_overlap_cross_split | 1 pair | 2 | I/owner: **b190 (train) and b3346 (dev+dev_pool) share 2 sentences** | b190 b3346 |
| F_self_pair | 3 | 3 | R, all real errors: b893 `Vegeta\|parent_of\|Vegeta` ("King Vegeta and his son Vegeta"), b3543 `Mizuki\|alias_of\|Mizuki` ("hero alias Captain Mizuki"), b1875 `Cain\|alias_of\|Cain` | b893 b1875 b3543 |
| F_A125_copula | 5 | 4 | R: b1407 "had a total 190 points" (no act), b3822 "had an argument" (x2), b1262 / b2584 causative "has" | b1262 b1407 b2584 b3822 |
| F_A134_attempt_word | 2 | 2 | R, both probably keeps: b162 "try it on" is the verb itself; b1847 "trying out haircuts" | b162 b1847 |
| F_symmetric_both_dirs | 2 | 2 | R: b1908 `helped` both ways for "work together" (allied_with?); b1813 a planned mutual-help deal | b1813 b1908 |
| F_kidnapped_fact | 1 | 1 | R: b2816 "seems to have been captured by the Caribou Pirates" (a named group doer -> `captured` event, hedged) | b2816 |
| F_kinship_parent_of / F_married | 104 / 24 | 77 / 24 | I (the canonical forms after M5; legal) | |
| nbsp_quote | 25 | 9 | I (the quotes are verbatim and include the window's own NBSP; the gates accept them) | b908 b2482 b2719 b2774 b2824 b2838 b2998 b3095 b3655 |
| X_end_absent | 109 | 40 | A: the end's words never occur in the window. Mostly page-title subjects of pronoun windows (b46 "he" -> `Zondark\|met\|Guts`, b33 "was the home of the elves" -> `Elfhelm\|located_at\|…`, b674 `Pochita\|killed\|…` x8, b140 Holy Iron Chain Knights) | b33 b42 b46 b118 b140 b163 b214 b223 b237 b278 |
| X_end_partial | 136 | 36 | A: a full name built from parts the window gives separately ("Maki" -> `Maki Zenin` b1048, `Nobara Kugisaki` b1033, `Marechiyo Ōmaeda` b416); 13 of the 36 windows are JJK | b314 b402 b416 b482 b487 b556 b677 b1033 b1048 b1058 |
| X_tag_quote_pipe | 4 | 3 | A: b3199 `list_header` "Below Wolf \| A threat …" (two fields in one tag); b2152 / b2264 are `citation` tags on `{{r\|…}}` templates (the pipe belongs to the template) | b2152 b2264 b3199 |

Zero hits, so already clean: E/F/T_quote_not_verbatim, E_self_pair, E/F/T_duplicate, E_symmetric_both_dirs,
F_ordered_rel_nonactual, F_actual_with_asserter, F_nonactual_no_asserter, F_A115_clause_object, F_A146_died_other_verb,
F_alias_variant_*, F_became, F_kinship_both_dirs, F_married_twins, `child_of`, `married_to`.

## 3. Mechanical (rule-decidable) fixes: none

`lint_gold_fix.sh build` ran M1-M6 on the reviewed audit:

- **M1, M3, M4, M5, M6: 0 windows.** The 2026-10-14 mechanical lint of the labels and the review together already
  removed these forms.
- **M2 (A89 event twins): lint_fix's quote-blind rule would write 12 records and drop 13 facts.** These are listed in
  `proposed_mechanical_diff_rawM2.txt`. lint_v2 flags 16 rows; the other 3 are reverse twins of non-symmetric verbs that
  M2 does not reach. I read all 16. **None of them is the event written again.** Each quotes a separate act:
  - a phone call next to a later in-person meeting: b2297 "called Layla" / "the two were reunited"; b3795; b2326;
    b2459 "was called by Tina … and came to the Minoru Mansion";
  - online contact before meeting: b3095 "met them online";
  - help in an investigation next to a rescue from drowning: b2245;
  - "backed up" next to "helps free": b1686;
  - "helps him split up their opponents" next to "rescues": b3498;
  - "assisted … to defeat the Chitauri" next to a later rescue from an explosion: b2638.

  The reviewers kept them on purpose (why: "the call is remote contact"). The big-set lint's closing note does the
  same ("directional helped/contacted pairs" are decided keeps). So the gold fixer's M2 drops a twin only when the fact
  and the event quote the identical string. **That gives 0 records.**

`proposed_mechanical.jsonl` is therefore empty, and so is `_refused`. `apply` is a no-op today. It is still the path for
any M-class rows that late audit appends bring in (§6).

## 4. Gate re-check (`--regate` equivalent)

`lint_gold.sh --regate` re-ran today's event, fact and tag gates on every final gold record. Output:
`gold_v2/lint/lint_gold_regate.json`, 12:56, final snapshot, all nine series' `facts.db`.
- **Events refused: 0. Facts refused: 0. Tags refused: 0. Facts re-normalised: 0.**

An earlier lint_v2 `--regate` at 12:29-12:40 gave the same result. It ran on 3,809 audit records plus 13 label windows.

## 5. Reading list and rulings needed

`gold_v2/lint/work_gold.txt`: **170 windows in 162 groups.**
- Overlap partners come first, grouped: G1711 = b1432/b1521/b1711.
- Then single windows: E_met_and_fight 67, name_short_and_full 36, E_A145_same_sentence 32, F_A89_event_twin 15,
  R_overlap_inconsistent 15, F_A125 4, F_self_pair 3, F_A134 2, F_symmetric 2, F_kidnapped 1.

Read a window with `BV2_SET=gold bash plan/review_tools/pre27.sh show B` plus `bash plan/review_tools/lint_gold_work.sh
show B`, which gives the classes and the overlap diff. Submit as for the review: `@<b> gold: lint <reason>` blocks,
then `BV2_SET=gold bash plan/review_tools/rv.sh fix FILE`. Edit overlap partners identically. Never `mark`. New fix
numbers: the GL001+ series, to keep them apart from G-files.

The advisory X_* classes are **not** on the list. They wait on these decisions (owner or Claude; they are from the open
rulings in `RESUME_HANDOFF_2026-10-28.md`, last update):

1. **Page-title ends absent from the window (X_end_absent, 40 windows).** The open ruling says such subjects are dropped,
   with deictic/crowd_end tags instead. Many of these rows are the original gold events (`Zondark|met|Guts`), and
   compose and the test score depend on them. Decide whether the ruling applies to gold events, which would change the
   test set and the .602 bar comparison, or only to facts.
2. **Full names assembled from parts (X_end_partial, 36 windows; JJK-heavy).** "Maki" -> "Maki Zenin". Keep (one
   canonical name) or use the window's form (A112/A130)?
3. **Overlap across the split line.** b190 (train) and b3346 (dev+dev_pool) share 2 sentences. Decide whether to
   de-duplicate before compose, or accept it.
4. **Gate quirks behind two self pairs.** "King Vegeta" (b893) and "Captain Mizuki" (b3543) are stripped as rank
   prefixes, so the row becomes subject == object. This is like "Lady Danu" in the big set. The fix is a fact_gate.RANK
   allow-list entry, or the window's own form. Gate changes are Claude-only, so this was not touched here.
5. **Infobox tag quotes with a pipe (X_tag_quote_pipe, 3 windows).** Open ruling: one tag per field, pipe-free. Citation
   templates (`{{r|…}}`) have an inherent pipe. Exempt them?
6. **M2 on reviewed data.** Confirm the narrowing: A89 is the same act only (a call next to a meeting stays). Then
   write it into `BIG_REVIEW_PATTERNS.md` / `gold27_system.md`. That is not done here, because the catalog is not edited
   in this stage.

## 6. After the review agents finish

```bash
cd /home/goblin/ScriptEngine/.claude/worktrees/big-review-flags
G=/home/goblin/ScriptEngine/series/universal/training/big/gold_v2/lint
bash plan/review_tools/lint_gold.sh --regate --json $G/lint_gold_regate.json   # ~75 s; must say UNREVIEWED 0
bash plan/review_tools/lint_gold_fix.sh build                                  # rebuild the proposal on the final audit
bash plan/review_tools/lint_gold_fix.sh apply                                  # dry check: STALE 0, missing 0
bash plan/review_tools/lint_gold_fix.sh apply --yes                            # only if the proposal is non-empty
bash plan/review_tools/lint_gold.sh --json $G/lint_gold.json
bash plan/review_tools/lint_gold_work.sh build --regate $G/lint_gold_regate.json   # refresh work_gold.txt
```
