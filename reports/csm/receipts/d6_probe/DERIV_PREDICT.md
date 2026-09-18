# DERIV leg v3 (verbatim-first) — PRE-REGISTRATION (written BEFORE the change)

Supersedes v2 (3-mechanism) and the during-guard sketch: analysis of
measured subjects shows ONE rule covers all cases — verbatim longest
exact document title, possessive-excluded, resolved-checked. NO
during-guard (arcn-blind rows need arc subjects; org-05 resolves via
length, not guards). NO router deletion (router stays LAST so every
currently-served row keeps its subject unless verbatim overrides).
NO story-pattern deletion (dormant backstop; removal is separate
hygiene with its own measurement).

Order in _qa_context: verbatim-title → story-pattern (spike) →
router-fallback (spike). First hit wins.

## Predicted derived subjects (exact)

- vol-10 → "Love, Flower, Chainsaw Guide" (NEW: router gave junk)
- org-05 → "Tokyo Special Division 5" (4wd beats 3wd arc; no guard
  needed — length decides)
- org-06 → "Yakuza" (possessive "Denji's" excluded by exactness)
- arcn-01 → "Fake Chainsaw Man" (3wd tie won leftmost over arc;
  UNTESTED subject — depth leg decides the flip, see below)
- arcn-03 → "Santa Claus" (unchanged shape)
- state-03 → "Nail Fiend" (unchanged shape)
- org-03 → None (no title present; correctly empty — width/depth
  legs or alias file, never counted here)
- CONTROLS (must be byte-identical to today): arcb-05 →
  "Katana Man arc"; chap-01 → "Chapter 1"; pool-140 → "Falling
  Devil" (via router, verbatim correctly skips possessive);
  abl-04/org-04 → today's values (recorded at run; any change =
  breach).

## Amendment v5 (pre-bank-run): possessive-owner deferral

Bank measurement of v3 flipped vol-10/org-05/org-06/arcn-01 but
FLOPPED pool-237 (router 'Mysterious Man' → verbatim 'Typhoon
Devil'): verbatim matched inside a possessive-attribute
construction whose (character, ability-prefix) pair EXISTS in the
abilities table. Fix: `_owner_attribute_hit` — possessive owner +
ability-prefix declared in store → verbatim DEFERS the whole query
(greedy ≤2-word owner + stopword strip; data-driven, no name list).
org-06's "Denji's story" has no pair → proceeds. pool-140 (pair
exists) → defers like pool-237, i.e. current behavior preserved.
Measured subject table (implementation check, 12 rows, ALL EXACT):
vol-10 Guide / org-05 Division / org-06 Yakuza / arcn-01 Fake /
arcn-03 arc (=old) / state-03 arc (=old) / org-03 None /
arcb-05 arc / chap-01 Chapter 1 / pool-140 None→router /
abl-04 Aki Hayakawa / org-04 American Thugs (controls unchanged).
- WIN (amended): pool-237 restored GREEN + v3 flips held
  (vol-10/org-05/org-06/arcn-01) + 0 counter-flips + blind 19/19 +
  eval 31/31.
- KILL: unchanged (any counter-flip, guard breach → rollback).

Implementation behaves exactly as coded; two predictions below were
wrong about longest-match outcomes (rule correct, expectation wrong —
recorded transparently, bank run NOT yet executed):
- arcn-03 → 'International Assassins arc' (NOT Santa Claus: 3wd arc
  beats 2wd character by longest-match; same as OLD story-pattern
  gave — NO behavior change vs committed tree).
- state-03 → 'Aging Devil arc' (NOT Nail Fiend; same: identical to
  OLD story-pattern output, NO change).
- arcn-01 → 'Fake Chainsaw Man' (CHANGED vs old arc-subject; the
  only arcn-row behavior change in this leg).
- org-05 → 'Tokyo Special Division 5', org-06 → 'Yakuza',
  vol-10 → Guide volume (all CHANGED from misfire/junk; the leg's
  purpose).
- Controls arcb-05/chap-01/pool-140(via router)/abl-04/org-04:
  byte-identical subjects to committed behavior.
Bank/blind/eval predictions below stand unchanged and decide the leg.

## WIN / KILL (decides the leg; subject table above is implementation check)

- WIN: the 4 changed subjects exact (vol-10→Guide, org-05→Division,
  org-06→Yakuza, arcn-01→Fake) + every other row byte-identical
  subject to committed behavior (arcn-03/state-03 = old arc subjects;
  org-03 = None; all controls) + full-bank total ≥465 with 0
  counter-flips + blind 19/19 + eval 31/31. Flips (esp. arcn-01 via
  Fake-subject, vol-10 via Guide) recorded as bonus: this leg
  enables depth legs; vol-10 flip would close it outright.
- KILL: any predicted subject wrong, any control changed, any
  counter-flip, blind/eval breach → rollback verbatim block only
  (spike+Q1 intact).

