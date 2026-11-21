# Open questions for the owner after the audit of the 2,150 training passages (2026-11-14)

Nothing here was changed in the gold. Each item is a point where the rulebook and the reviewers' practice
disagree, or where two careful readers still read the passage differently. Window numbers are `b` numbers in
`gold_v2/gold_in.jsonl`; the reasoning for each is in `adj/Axx_review.md` (A04's is in the session scratch
folder, summarized in STATE.md). Recommendations are mine.

## 1. A single unnamed individual as a participant ("the mayor", "the Hollow", "the imposter")
The rulebook allows a definite description of one specific individual as an end (step 6, B.6, A20). The
reviewers never used one, in every series. I kept the reviewers' practice, so those acts have no row.
- Waiting on it: b29 b195 b357 b281 b97 b66, and 21 more windows judged "gold is right" only because of this
  practice (b609 b740 b767 b990 b1436 b1390 b1209 b1299 b1350 b1486 b1786 b1639 b1550 b1512 b1046 b1471 b1240
  b1751 b3242 b3171 b3148).
- Recommendation: keep the practice (an end is a name) and say so in the rulebook, so the two agree.

## 2. A first new form or first new power: the event `awakened`, or a fact
The verb table says `awakened` for "a new power or form for the FIRST time" (A126). The gold writes
`transformed_into` for 78 of 82 transformations and `gained_power` for first powers; reviewers wrote "no
awakened" in their notes. I struck every proposed swap.
- Waiting on it: b105 b169 b69 b1076 b1381 b1308 b1598 b1439 b1609 b1731 b1170 b2878; 11 more left as they
  are on this practice (b716 b653 b905 b825 b789 b832 b932 b1287 b1656 b1708 b1460).
- Recommendation: keep the fact (it names the form or power; `awakened` cannot) and narrow the table line to
  waking, revival and regaining consciousness.

## 3. Coming back: is it `awakened`?
- A heart stops and restarts or is healed at once: b3187, b1247.
- Waking where the knockout is stated only in the text before the passage: b1292. Waking from a
  technique-induced trance: b1732. "First woke up" in a hospital: b1078.

## 4. A devil eaten by Pochita: `killed`, `defeated`, or a fact
b751 and b567 write it as a fact; b674 writes eight eaten devils as `killed`. One answer should cover all three.

## 5. Meetings without a stated arrival, at a distance, or by a hostile arrival that leads to no fight
b204 b325 b737 b3174 b792 b1605 b1188 b1179 b1238 b1710 b2920 b3002 b1142 b1384 b1621 b1210 b742 (Kishibe)
b1060 b2995 (Kizaru) b1088 b723. The applied rule so far: `met` when the passage says someone arrives where a
named person is (Addendum 6), no `met` for noticing, for a purpose clause, or when only one party is conscious.

## 6. A defeat or kill in the passive whose doer is only implied by the passage or the page
b1408 b1048 b1100 b1254 b1337 b3065 b1448. The strict reading (Addendum 5: implied doer, no row) would remove
these rows; the reviewers read the doer from the scene. I left them.

## 7. Single verb questions
- War between nations as `fought`: b203 b133. Group against group with members tied: b185.
- A rescue stated only as a purpose, or interrupted: b214 b625 b3261 b3262 b1762 b1517 b1705.
- An actual attack written as the fact `attacked` on an ally or by accident: b299 b652 (the gold uses that
  fact for attacks on things; on a person it is normally `fought`).
- Killing an immortal in training; a master who makes unnamed minions kill: b537 b728 b1061.
- Restraining as `defeated`: b3182. Reneging on a deal as `betrayed`: b1715. "Subjugated": b1038.
- Exorcising a named spirit, massacring a named clan, slashing a hostage, a lunge before the kill: b1170 b1368
  b1678 b1568. Possessor tearing out the shared body's heart: b1528.
- Fled, forced his way out, drove off: `escaped`, `departed` or a fact: b412 b3155 b1642 b3103.
- "Was sent to", "brought an army", "Orochi's palace" as `arrived`: b945 b2985 b2982.
- A `met` kept after an opening attack: b1144. An attack on a phone or on a shield: b1360 b1377.
- Others: b804 b992 b1450 b1775 b1507 b1669 b1214 b1145, and b887 (a game's story arc tagged `production`
  while the game section of b926 is written as plot).

## 8. Left from the dev-set audit and the script checks
- b3467: the kill inside "Toji reveals he killed Satoru Gojo". b3518: its last sentence has no label.
- b3110: "According to Genus, ..." is written `other_verb states`, but the sentence has no such verb.
- b1538: two sentences say "Reggie tells"; the writer keeps one fact per subject, relation and object, so the
  second was written "told". A tool limit, not a label choice.
- Three "shows up" cases that are not companions (b1088 b2995 b723), listed in Addendum 6.

## Not label questions
- 22 passages carry holes where the parser dropped a term (17 on Bleach): `passages_with_text_holes.json`.
  Fix in the parser or its overrides and re-window; the labels are not at fault.
- 30 passages whose text needs a person to compare with the page: `FINDINGS.md` section 1.
- The per-line training format has structural defects: `FINDINGS.md` section 2.
- Not covered by this audit: the other 150 JJK holdout windows; the 14k big set; fact rows were checked by
  script and by a sample, not re-read one by one (see `FINDINGS.md` section 4 for what the sample found).
