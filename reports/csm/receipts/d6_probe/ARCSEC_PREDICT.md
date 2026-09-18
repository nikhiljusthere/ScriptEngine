# ARCSEC leg — PRE-REGISTRATION (written BEFORE the change)

Root cause (verified in code + corpus): `_qa_context` builds floor
section ranks from query content-terms MINUS the subject's own terms
(`context.py`, "the subject's own name ... discriminates nothing").
Correct for character subjects — fatal for STORY-page subjects: with
subject='War Devil arc', the terms {war, devil, arc} are stripped, so
arc-named sections ("Synopsis / War Devil arc" on character pages,
where the gold lives) score 0 and stay buried. The exclusion exists
because a name repeats on its own page; but an arc name on a
CHARACTER page is precisely discriminative.

## Change (5 lines + comment, `_qa_context` only)

Keep subject-term exclusion for non-story subjects; SKIP it when the
resolved subject page is a story container (arc/chapter/episode/
volume — structural page_type check, no series names). Then arc terms
rank arc-named sections up through the existing `_qrank` + lead-guard
machinery (no new sort, no new budget rule). Character-subject
queries: byte-identical behavior. Beam untouched.

## Predictions (ALL must hold)

- arcn-01 flips RED→GREEN (gold all in Fake/WarDevilArc section;
  verified in chunks).
- arcn-03 flips RED→GREEN (gold in Santa/AssassinsArc section).
- 0 counter-flips on the full 486 bank.
- All other moves recorded individually (any extra flip must be
  same-mechanism explicable: story-subject + gold in arc-named
  section — else it re-opens diagnosis, not celebrated blindly).
- Blind stays 19/19 (incl. blind-arcn-aki, whose arc-subject floor
  already serves it — must HOLD).
- eval-jjk stays 31/31 (co-located). OOS floor holds. green30 clean.

## KILL (any breach → revert to exclusion-always, keep Q1+spike)

<2 target flips, any counter-flip, blind <19/19, eval <31/31, OOS
below floor, green30 flip. Rollback = restore the two-line
exclusion (git checkout the hunk).
