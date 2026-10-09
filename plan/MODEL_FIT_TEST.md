# Model fit test — can Haiku or Sonnet review the big windows instead of Opus? (2026-10-10)

Run by Claude session 14e42d0b on 2026-10-10 ~02:40-02:53 per `plan/RESUME_REVIEW_HANDOFF_2026-10-10.md`
§8; that session adjudicated Set B and submitted it (review cursor 806 -> 836) but did not write this
report. Numbers below were recomputed by the next session from its saved files
(`/tmp/claude-1000/-home-goblin/14e42d0b-*/scratchpad/fit/`: `ref_*.jsonl`, `cand_*_{A,B}.jsonl`,
`score2.py`). Candidates: Haiku 4.5, Sonnet 5.5, Opus 5.5 subagents, all at effort medium, identical
prompt + inputs, launched in parallel.

## Set B — blind, 30 fresh windows b807-b836 (primary; reference = Opus main-session adjudication)

| reviewer | P | R | F1 | exact | added-row recall | 35B errors removed | misses | wall | tokens |
|---|---|---|---|---|---|---|---|---|---|
| 35B raw (no review) | .578 | .260 | .359 | 10/30 | 0/74 | 0/19 | 61 | — | — |
| Haiku 4.5 | .846 | .550 | .667 | 15/30 | 29/74 = .392 | 14/19 | 37 | 416 s | 194,541 |
| Sonnet 5.5 | .859 | .670 | .753 | 18/30 | 41/74 = .554 | 14/19 | 29 | 322 s | 136,088 |
| Opus 5.5 (control) | .912 | .830 | .869 | 20/30 | 61/74 = .824 | 18/19 | 9 | 367 s | 131,889 |

## Set A — 60 already-reviewed windows (secondary; catalog leaks in the candidates' favour)

| reviewer | P | R | F1 | exact | added-row recall |
|---|---|---|---|---|---|
| 35B raw | .704 | .515 | .595 | 25/60 | 0/83 |
| Haiku 4.5 | .804 | .696 | .746 | 33/60 | 32/83 = .386 |
| Sonnet 5.5 | .852 | .772 | .810 | 35/60 | 44/83 = .530 |
| Opus 5.5 | .846 | .865 | .855 | 37/60 | 60/83 = .723 |

mkfix warnings (name/short-form mix): Opus 1, Haiku 0, Sonnet 0. Error buckets in `score2.py`
(miss = missed event, the dominant 35B error class A1/A34/A35).

## Verdict

**Neither Haiku nor Sonnet is fit** against the proposed bar (F1 >= .95, added-row recall >= .90,
exact within 5 points of Opus). Their weakness is exactly the job's core: they confirm the 35B rows
but add only 39% (Haiku) / 55% (Sonnet) of the missing events, against Opus 82%. Haiku is also the
most expensive in tokens. Even the Opus subagent at medium effort misses ~1 in 6 added rows, so the
main review stays with Opus at full effort, reading every window. Caveat: the Set B reference was
adjudicated by Opus, which favours the Opus control somewhat; Set A (independent reference from the
earlier review) shows the same order.
