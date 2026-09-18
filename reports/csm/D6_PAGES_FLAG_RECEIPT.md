# D6 `--pages` flag — zero-regression receipt (2026-09-18, opencode session)

Council #35 / D39 lock (`2ee7edc`): `events-extract` gains an additive
`--pages <frozen-list>` flag (targeted extraction, D6 window). Pre-registered
proof, run on JJK (baseline-exact reference), offline:

## Gate A — default-absent is byte-identical
`events-extract --series jjk --scope corpus --dry-run` captured on the HEAD
files vs the modified files (HEAD restored via `git show`, same invocation,
both under `scriptengine/.venv`):

```
diff /tmp/d6_dry_before_nf.txt /tmp/d6_dry_after_nf.txt   # empty
```
→ **PASS**: the absent-flag native path is byte-identical to pre-change.

## Gate B — scope-plan identity (full list == absent)
JJK `--scope corpus` queue = **524 pages / 964 sections** (dumped via
`scope_plan` → `/tmp/d6_jjk_corpus_all.txt`). Flag-absent dry-run vs
`--pages /tmp/d6_jjk_corpus_all.txt` dry-run:

```
diff /tmp/d6_dry_after_nf.txt /tmp/d6_dry_after_fl.txt
1c1
< 524 pages / 964 sections would be read (scope=corpus, prompt 
---
> 524 pages / 964 sections would be read (scope=corpus, filter 524, prompt 
```
only the added header note line differs; page + section listing identical →
**PASS**.

## CSM sanity
`--scope corpus` dry-run = **235 pages / 412 sections** (confirms B's
pre-window estimate, council #35). Comment-only list file → `filter 0`,
0 pages considered; missing list file → clean red error, exit 1.

## Implementation
`scriptengine/cli.py` `events_extract`: `--pages` option (one title per
line, `#` lines ignored, clean missing-file error); dry-run filter + the
header note appear only when a filter is present. `scriptengine/ingest/
events.py` `extract_events_series`: new trailing `page_filter: list[str] |
None = None` parameter, intersects the `scope_plan` queue (order preserved);
`None` leaves the native path untouched.

Fallback per the lock: native `--scope corpus` remains available.