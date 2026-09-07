---
name: switchpoint
description: Write the durable resume checkpoint (plan/SWITCHPOINT.md + git commit) before a Qwen mode switch, at council cadence points, and whenever a long session must stay resumable from disk. Use before qwen-switch, at the end of any work sub-list, and whenever the user says "checkpoint".
---

# switchpoint — the resume checkpoint

The rule: **anything I need to continue must be on disk, not in the
transcript.** Transcripts get compacted, discarded, or overflow a smaller
context; `plan/SWITCHPOINT.md` doesn't.

## When

- Before any Qwen mode switch (the `qwen-switch` skill).
- Council cadence points (every 2–3 todos, end of sub-lists, phase gates):
  the commit part. The council record itself goes to
  `reports/comprehension/COUNCIL_<subject>.md`.
- When the user says "checkpoint".

## What

1. **Commit** (named paths, no push): branch `character-scoped-questions`,
   prefix by area (`comprehension:`, `docs:`, `ops:`, …). `series/` stays
   gitignored; dated `reports/` dirs are untracked.
2. **Refresh the hand-written section of `plan/SWITCHPOINT.md`**:
   - mode (current → target, if switching)
   - sha of the clean commit
   - trunk/excursion address (drift_log §4 addressing: `P<n>.<step>` / `X<n>.<step>`)
   - work explanation: done / in-flight / **exact next step** — written so a
     fresh session can act on it with zero transcript
   - open questions / risks
   - first action on resume
3. **If mid trunk/excursion step**: append the drift-log entry too
   (`plan/drift_log.md` §5 format, append-only). The switch itself appends a
   machine line to the switchpoint's switch log via `qwen-switch.sh` — never
   hand-edit that section.

## Quality bar

A fresh pi session, given only `plan/SWITCHPOINT.md` + `plan/drift_log.md` §4,
must be able to continue the work with zero transcript. If it can't, the
explanation is too thin — write more, not less.