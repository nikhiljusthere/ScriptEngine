# TERM-RULE leg (arc-terms-kept) — PRE-REGISTRATION (written BEFORE the change)

Root cause (verified): `_qrank` floor ordering strips subject tokens
from query terms. For STORY-page subjects this strips exactly the
arc-title tokens that select the answer sections (arcn-03: Santa /
AssassinsArc section scores 0 because {international, assassins,
arc} are all subject tokens). Character subjects are unaffected
either way (their names repeat meaninglessly); arc questions need
arc terms live.

## Change (qterms line + helper, context.py only)

`qterms = content(query) − content(subject)` becomes: start from
that set, then UNION BACK the tokens of any resolving
arc/chapter/episode/volume title named in the query (detected via
the existing story-pattern matchers over the raw query string,
independent of the derived subject). Net effect by row shape:
- arc-subject rows (arcn/state dim rows): arc terms live →
  arc-named sections (on ANY page in the floor) rank up.
- character-subject rows WITHOUT arc mentions: identical (no arc
  title present to union back).
- character-subject rows WITH arc mentions (arcn-01 and friends):
  arc terms live alongside (already live today — no change).
- box rows (arc-subject): more arc content (already green via arc
  content; monotone direction).

## Predictions (ALL must hold)

- arcn-03 flips RED→GREEN (Santa/AssassinsArc section; gold
  verified there, all 3 terms).
- state-03 flips RED→GREEN (NailFiend/AgingDevil section; gold
  verified there).
- arcn-02/06/08/10, state-02/08/09: RECORDED (may flip if gold sits
  in arc-named sections; must be mechanism-explicable on autopsy —
  unexplained flips re-open diagnosis, never celebrated blindly).
- 0 counter-flips on 486 (esp. arcn-01, arcb-05, chap-01, abl-04,
  org-04/05/06, vol-10, blind-arcn-aki/makima hold).
- Blind 19/19. eval-jjk 31/31 (co-located). OOS floor holds.
  green30 clean.

## KILL (any breach → revert term-rule hunk only)

<2 of (arcn-03, state-03) flipping, OR any counter-flip, OR any
guard breach. Rollback = restore the one-line exclusion (spike +
Q1 + derivation intact).
