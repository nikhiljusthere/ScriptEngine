# Marvel `all`-scope dry-run receipt (R10, 2026-09-28)

`events-extract --series marvel --dry-run --scope all` on the R10 tree
(data commit `6d57723e`, code commit `ace70ab3`), exit 0, 00:45. Read-only:
the census counts what would be read; nothing is extracted. Full CLI output:
`/tmp/se_p2/r10_dryrun_marvel.txt`.

## New totals (R10 item 3)

| | |
|---|---|
| pages in the `all` queue | **179,276** |
| sections read | **51,723** |
| fact passages read (declared keys' prose values, one passage per value) | **225,045** |

## 100% check: per-key `in queue == prose` (R10 item 3)

All **91 concrete keys** the declared patterns reach have every prose value
in queue — `prose == in queue` on every key, **zero gaps** (no
`not 100% in queue` marker in the dry run). The pre-R10 census showed the
gap: `solicit` 935/33,529 in queue, `powers` 3,067/14,817 — fact values on
pages no section rule queued. By family:

| declared family | keys | store values | prose (all in queue) |
|---|---:|---:|---:|
| `history` | 1 | 127,035 | 126,463 (100%) |
| `synopsis*` | 79 | 40,200 | 37,474 (100%) |
| `solicit` | 1 | 33,529 | 33,196 (100%) |
| `powers` | 1 | 14,817 | 11,969 (100%) |
| `abilities` | 1 | 7,319 | 5,511 (100%) |
| `overview` | 1 | 4,119 | 4,108 (100%) |
| `weakness*` | 2 | 3,939 | 3,403 (100%) |
| `personality`, `professionalhistory`, `properties`, `plot`, `alternateversions` | 5 | 3,015 | 2,921 (100%) |
| **all 91 declared keys** | **91** | **233,973** | **225,045 (100%)** |

`synopsis    header` (1 value, 0 prose) is a wiki residue value: counted in
the census, never read. Store-value total cross-checked read-only against
the live store (91 keys, 233,973 values).

## Counted exclusions (R10 item 1)

**176 concrete keys** under the `excluded_fact_keys` patterns — 144,986
store values, 131,762 prose — are deliberately not read as narrative. Each
pattern carries its one-line reason in `overrides.yaml` and the census
reports it: `notes*` (editorial notes, not story beats), `trivia*`,
`pointsofinterest`, `others*` / `related*` (disambiguation rosters), and
`appearances*` / `appearing*`. The `appearances*` / `appearing*` families
(the appears-in rosters, 82,853 rows / 11.8M) are roster/structure (plan
C1), not prose — recorded here per R10: counted, not read. A key the
council later wants read is a one-line move to `narrative_fact_keys`,
never a silence.

## Cross-wiki no-op (R10 item 4)

JJK and CSM declare no narrative fact keys, so `fact_pages` is `[]` for
them and their `all` page list is unchanged: the JJK `all` list is
**966 pages, byte-identical** to the pre-fix tree (computed on the stashed
pre-R10 tree and on the R10 tree, 0 differing lines).

The four gates (pytest, eval jjk, span-recall jjk, canon-run opm) run once
on the final tree, after this commit — recorded in their own receipts.