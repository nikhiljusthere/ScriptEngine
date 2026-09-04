# JJK Chapter Prose — Wave 1 (55 numbered + pre-chapters)

Status: **COMMITTED.** All 55 batches at 100% (**166/166**). The last open
item, `chapter_20` Q3 (**G29**), was diagnosed, fixed, and committed in
`063c7c4` (narrowed `_SINGLE_VALUE_PREDICATE` + `bool()`-wrapped
`asks_single_field`); `chapter_20` is back to 3/3 and the whole wave re-scored
166/166 on the fresh CUDA API.

## Scope

- **Pages (55):** `Chapter 0-1…0-4` (4 pre-chapters) + `Chapter 1…51` — the wiki's
  own reading order, wave 1 of the 6-wave plan in `chapter_prose_template.md`.
- **Questions: 166** (prose-only, hand-authored). Per-chapter: 1 `Summary` +
  1–2 `Plot Details`, +1 `Trivia` where the page has one.
- **Per-section density:** `Summary` 55 (1/chapter) · `Plot Details` 109 ·
  `Trivia` 2 (`Chapter 27`, `Chapter 51`).
- **Out of scope (by template):** `Characters in Order of Appearance` +
  `Battles & Events` (declared rosters, commit 7 — ride the roster path, not
  prose); `Locations` / `Jujutsu` (waived, State 122); `Author's Comment`
  (content gap, TODO 8); `4-Koma Bonus` (Modulo-only, wave 6).

## Result

| | |
|---|---:|
| batches | 55 |
| prose questions | 166 |
| batches at 100% | **55 / 55** |
| questions passed | **166 / 166** |
| failures | 0 (the sole first-run 2/3, `chapter_20` Q3, cleared by **G29** in `063c7c4`) |

Run on **CUDA** (`:8000` restarted off `SCRIPTENGINE_DEVICE=cpu`; 6.5 GiB free
was enough for the reranker — no OOM). Per-batch wall clock ~3–5 s vs ~45–64 s
on CPU. Batch files: `questions/_jjk_page_chapter_<N>.json` (+ `chapter_0_<N>`
for the 4 pre-chapters). Every gold is a verbatim substring of the cited
section (enforced at authoring time by the helper, re-checked on write).

## Triage (1) — REJECTED as a reword-dodge; restored + filed as G29

`chapter_20` Q3 *"What are the curses at Kinema Cinema actually revealed to be,
per Chapter 20?"* (gold `ex-humans that have had their bodies transmogrified
by cursed energy`) fails first run: `_PLURAL_WH` ("What are…") sets
`plural_ask`, the G17 single-field guard is field-only and does not see a
copular characterization predicate, `has_set` resolves a **partial** "Cursed
Spirits" roster, so rule 5 misroutes to `roster` and the prose fact is absent
(`routed roster / partial`).

The wave-1 pass initially "fixed" this by **rewording** the question ("What did
the victims found at Kinema Cinema turn out to be…", which flips `plural_ask`
to false and lands in `qa`). **That was the mistake** — a fact reachable by
other wordings while one natural wording fails is the definition of an engine
gap, not a phrasing issue. The reword was **reverted** (Q3 is back to its
original wording, failing 2/3 on `page-run`) and filed as **G29**
(`CHECKPOINT_ROSTER_BUILD.md`): diagnosed, drafted on a scratch copy, then
collateral-scanned over the full 15,798-question bank (exactly **1** route
change — this case, `roster → qa`; no set enumeration broken), and **applied
+ committed in `063c7c4`** (narrowed `_SINGLE_VALUE_PREDICATE` +
`bool()`-wrapped `asks_single_field`). `chapter_20` is back to 3/3 and the
whole wave re-scored 166/166.

The other 54 batches passed first run. **Step-4 audit (all 55):** no other
question in wave 1 was reworded after a failure, and no gold was changed —
every current batch file matches its earliest authored report (only `chapter_20`
ever diverged, in the intermediate 0828/0830 runs, since restored).

## Notes / open items carried forward

- **Trivia chunking gap (template §4) did not bite here:** the 2 Trivia
  questions were authored to name the bullet's subject (e.g. "What is notable
  about the Japanese title of this chapter?"), which serves. The generic-question
  Trivia miss remains a known open gap; diagnose, don't dodge, if it recurs in a
  later wave.
- **Display-form gold rule (template §7):** Plot Details battle/technique names
  were golded from the section's rendered **display text**, not the linked
  page title (e.g. `Divergent Fist`, `Coffin of the Iron Mountain`, `Boogie
  Woogie`).
- **Next:** waves 2–6 — `Chapter 52…271` (waves 2–5, 55 each) then the 29
  non-numbered pages incl. Modulo `4-Koma Bonus` (wave 6). G29 is cleared, so
  the reword-dodge risk is gone: any failure in waves 2–6 goes to
  `CHAPTER_PROSE_TRIAGE.md` (gold error → fix inline; engine gap → log + keep
  the original wording), never reworded to dodge.

## Resume

```bash
# API on CUDA (already up): verify device
curl -s http://localhost:8000/health   # "device":"cuda"
# re-score a wave:
#   bash /tmp/opencode/run_wave1.sh     # loops the 55 slugs in /tmp/opencode/wave1_slugs.txt
# single batch:
./scriptengine/.venv/bin/python -m scriptengine.cli page-run --series jjk --batch chapter_52
```