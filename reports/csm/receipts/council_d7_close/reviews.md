# COUNCIL RECORD — peer review round (D7 close council, #37)

**Members:** 5 peer reviewers (R1–R5), each reviewing ALL FIVE advisor
responses (`advisors.md`), deployed strictly sequentially (owner rule
2026-09-08), fresh-context, GPU-free, read-only. Then the chairman
rules on the full record.

**Letter↔session map (reviewers):**
| Letter | Focus | opencode task session |
|---|---|---|
| R1 | Fact-checker | `ses_f449500b1ffeGK3VyCZ0aM2k3m` |
| R2 | Consistency auditor | `ses_f448c8073ffexf972RlUPtz1ig` |
| R3 | Majority attacker | `ses_f4489c36fffecpwkLJPzIcDBhN` |
| R4 | Ritual critic | `ses_f448760b1ffe9cYJX4Q1IR1dzL` |
| R5 | Integrator | `ses_f44846304ffeJb9qKgTaIglHP1` |

**Chairman:** verdict in `chairman.md`.

---
---

## REVIEWER R1 — Fact-checker

# REVIEWER R1 (Fact-checker)

## Verified fact table

**1. The 2 unattributed flips = {csm-dim-chap-01, csm-dim-arcn-07}
(Q1-L1) — VERIFIED.** Git census: 463-era (`3c047604`) = 23 reds;
469-era (`20d6da4e`) = 17 reds; closed-6 = 4 deriv {arcn-01, org-05/06,
vol-10} + the pair; 0 new reds. Drift D57:2093 ("bank 465, flip set ==
stamped CONFIRM + chap-01/arcn-07"), D61:2204; B/C/E concur.

**2. The 13 reds @473 = {csm-abl-pool-140/358} + 11 dim ⊂ register-22 —
VERIFIED.** 469's 17 reds − Leg A {arcn-02/10, org-03, state-08} = 13
(`LEGA_p23.log`: "W 473/486"). Register-22 (`census_v1_floor_triage.
jsonl`, extraction-gated class) = 21 dim + csm-char-04; the 11 dim reds
all sit in it; pool rows ∉ (triage: "retrieval-ranking (D6-close
finding)…", owner "D7 (ranking leg)"). FLOOR16 (`check_targets.py:42-
49`) = 2 pool + 14 dim; 13 = FLOOR16 − {arcn-02/10, state-08}. Pool
rows are `csm-abl-pool-*` (abl family).

**3. Meter — literal text supports only 35 = 22+10+3 (P1.4 stamp).**
GATE.md:83-87 / HALT_METER_P13 (FINAL): "halt residual 35 = 22 floor +
10 residual + 3 r1blast-* stamps". 37 = 24+10+3 (B/C) = same formula
with the floor register re-stamped 22→24 (pool → floor) — a re-stamp,
not the text. 26 = 13+10+3 (D) re-bases on p23 reds — not the text (the
rule counts queue rows). A's 27 (:62-64) = live open rows. Staleness:
10 of the 22 floor rows are green @473 (abl-04/05/06, appr-06,
arcn-01/02/07/10, state-01/08; 3 of them flag-ON-only), so 35
overstates live open by 10.

**4. Flag-OFF = 20d6da4e behavior — VERIFIED (code level).** Diff
`20d6da4e..4a8616bd` context.py (52 lines): ABILWIDTH (:638-643)
short-circuits on flag "0" (:591) — no store, no top_k change; TIERED
(:652-657) leaves tier2=[], so ordered (:861-866) is identical;
unconditional additions inert (import os, defs, pure set/list
construction) — no I/O/state/logging under flag-off. Gate-relevant
diff `4a8616bd..HEAD` empty. Caveat: invariance proof from the diff,
not an executed byte comparison; HEAD is now `ea9a541c` (docs-only) —
the framing's "HEAD = 0c8cc953" is stale.

**5. A20's 3 void triggers — VERIFIED.** D6_CLOSE_A20.md:40-41: "gate
regression / flips / A-row closes-still-red"; literal set GATE.md:731-
735; `d6_flip.py` = trigger 2 (rc=2 on a green30 flip or oos200 drop ≥
3).

**6. Halt rule + register-22 — VERIFIED.** 22 = 21 D6-extraction +
csm-char-04 (GATE.md:75-78; HALT_METER_P13:50-70; GATE_LEDGER
p14_close). pool-140/358 ∉ register-22 ⇒ halt condition unmet @473 as
registered; met only after a stamped re-registration (GATE.md:1046-
1050 defers the call to this council).

## Errors found in the advisor records

- **A** (:62-65): "10 of (a) green… 7 via the committed D6 spike" —
  attribution loose: the 7 = deriv (arcn-01) + Q1-L1 (arcn-07) + D6-
  spike five (abl-04/05/06, appr-06, state-01); the 3 tiered closes
  are flag-ON-only.
- **A/C** (:84-85, :210): recast void trigger 3 "A-row closes-still-
  red" as "A-row register = the 13" — not the literal (A20:40-41,
  GATE.md:733).
- **B** (:146): "469/473 are flag-ON grades" — wrong for 469: the
  flags didn't exist at 20d6da4e (added at 4a8616bd); 469 is pre-
  flag. B:145 "asserted, not proven" is stale after item 4.
- **D**: no material errors; "register rows… not floor" (:270) loose —
  pool rows sit in the A20 D7-holdout register, not the 22-row floor
  register.
- **E** (:368): "root_cause = qa-door ranking" is a paraphrase of the
  triage string; E's VOID formal (d6_flip rc=0, :402-403) covers
  trigger 2 only — trigger 3 unaddressed (gap shared with A).
- **Framing**: "HEAD = 0c8cc953" stale (HEAD = ea9a541c, docs-only;
  gate-relevant diff still empty).

## What the chairman must adjudicate (on facts)

1. **Denominator.** The literal rule stamps 35 (= 22+10+3). Live
   candidates: 27 (A, open rows) / 37 (B/C, re-stamp) / 26 (D, p23
   re-base). The text supports none as written; whichever is chosen
   must be stamped, and the 10 now-green floor rows (item 3) struck
   from the register.
2. **pool-140/358.** As registered (D7 holdouts, "width"), halt is
   unmet @473; closing now needs a council/owner-stamped floor re-
   registration (B/C), an owner re-scope (D), or a new pre-registered
   width leg.
3. **VOID ritual.** A20 trigger 3 (GATE.md:733) has no pre-registered
   artifact in any advisor's ritual; pre-register one (model-free
   re-grade of A20's 46 closed rows @473) or rule the 2-trigger ritual
   (gates + d6_flip) sufficient.

---

## REVIEWER R2 — Consistency auditor

# REVIEWER R2 (Consistency auditor)

## Internal contradictions (per advisor)

**A** — Q1's flat "Halt rule met" (advisors.md:37) vs A's own "re-
register pool-140/358 as width-class Phase-2 floor" (:39): the halt
rule is *not* met as registered (pool rows ∉ register-22;
`census_v1_floor_triage.jsonl` owning_phase = "D7 (ranking leg)";
GATE.md:1046–1050 defers the call to this council). The re-
registration is precisely what *makes* the rule met. Weaker: the flat
sentence. Also :41 "close defers one wave" vs item 3 "only if ordered
post-close" (:90) — the qualifier resolves it; "defers one wave" is the
leftover.

**B** — Q5 "official suite = a close re-grade from the committed tree"
(:140) vs Q2 "Byte-identity needs no new re-run… gates green at
0c8cc953" (:134): the re-grade's 4-gate component is already discharged
by reboot_rule. B's stated justification (assumption 2, :145: "flag-
OFF = 20d6da4e behavior asserted, not proven") is stale — R1 item 4
verified it code-level. B's own fully-attributed chain (Q4, :138)
makes a fresh p23 a stability re-check with known expectation (469
flag-OFF / 473 flag-ON): zero new information. Stronger: Q2; the re-
grade survives only as an optional red-list stability check.

**C** — "meter 35→37" (:178, :202) vs the 10 now-green floor rows (R1
item 3: 7 flag-OFF-green + 3 flag-ON-only): 37 = 24+10+3 keeps 10
stale rows in a queue-row meter — not exact for the flag-OFF product
state. Same wart as B's. Stronger: strike the 7 provable flag-OFF
greens.

**D** — No true contradiction. "No council-authored re-registration"
(:348–349) vs step (1) "relabel FLOOR16" (:321): the relabel fixes
the *instrument's* mislabel (check_targets.py:41–42 "16 Phase-2 floor
rows") to match the A20 register (pool = holdout, D6_CLOSE_A20.md:33–
38) — bookkeeping, not re-scope. The re-scope (22→24 re-stamp) is what
D reserves to the owner (:324–325). D must state the distinction; B/C's
"35→37" is exactly the re-registration D reserves.

**E** — Q1 "residue is registered ⇒ Phase-2" (:369) vs the register:
owning_phase = "D7 (ranking leg)", closer = "D7 ranking-leg fix",
retest = None — *not* Phase-2. E's own Q4 stamp "Tier 2 → Phase-2
ranking leg" (:396–397) proves a fresh stamp is owed; "registered" is
an unsupported inference (weaker side). Also Q5(3) lists a "TIERED-
flip record" inside the D7-era amendment (:404–406) while the flip is
endgame step 2, post-close (:412–415): pre-flip the file can carry
only a pre-registration, not a record.

## Cross-advisor adjudications needed

1. **Who re-registers pool-140/358**: (a) council-stamped floor re-
   registration (B:132, C:170, A:39 implicit, E:396 effective) vs (b)
   owner re-scope (D:324–328, 348–349 — "the council records, it does
   not re-scope") vs (c) a new pre-registered width leg that bypasses
   the question (D step 2; A item 3; B:132 alt; E step 3). Chairman
   must rule (a) vs (b); (c) is live only if a leg runs, and a
   Phase-1 leg triggers #34 floor-moving (E:370–371).
2. **Ritual: re-run the p23 grade or cite receipts**: cite camp (A:70–
   71 "cite the existing green"; C:205–206 "§9a bars re-grading your
   own sweep") vs re-grade camp (B:140; D:306–310 "close must produce
   its own receipts… fresh p23 flag-OFF, expect 469, 0 self-flips").
   Re-run ⇒ close is not docs-only (needs a :8000 window). E is split
   (gate cites + live d6_flip + one probe, :399–411).
3. **Claim-scope line**: B:136 ("grade flag-ON 473; shipped product
   flag-OFF") vs E step 2 (:412–415) flipping the default post-close,
   making 473 *the* product behavior — erasing the "flag-OFF" half.
   Either/or: permanent line (B) vs time-stamped line the flip amends
   (B+E merge). A file carrying both B's line and E's pre-registered
   flip is self-contradictory as written.
4. **Meter base**: A 27 (strikes 10, :62–64) vs B/C 37 (no strike) vs
   D 26 (p23 re-base, :313–314) vs E "FLOOR16 denominator, 22
   historical" (:389). Text supports only 35 = 22+10+3 (GATE.md:85–
   86). Chairman picks base + strike rule.

## Constraint violations flagged

- **#34 floor-moving**: A:41 "close defers one wave" + item 3 pre-
  register a new width leg as a Phase-1 wave — a new fix class after
  the freeze, exactly #34's floor-mover (E:370–371, 439–440). D's pre-
  close leg (D:322–324) has the same exposure; D's owner-re-scope
  path is the clean one. B/C's 35→37 re-stamp is the compliant vehicle
  for a council stamp.
- **Owner-word (governance gap, not a text violation)**: B/C/E stamp
  pool-row ownership via council action in a docs-only close; the
  written rule (engine commits only on green + owner word) is
  untouched, but if campaign re-scoping is an owner act (D:348–349),
  the council stamp exceeds council authority — flag for the chairman.
- **JJK-100% (ambiguity)**: all five gate the flip on 4 gates flag-ON
  incl. JJK (compliant), but the flip *changes* JJK behavior (tier-2
  in JJK bundles, D:293–294) — E's own "no `context.py` change
  breaking JJK no-op-by-construction invariance" (E:446–447) is broken
  by E's step 2 unless read hunk-specific.
- **D59 / CSM-centric**: clean — all five bar Leg B re-tuning; every
  "new leg" is a new pre-registered instrument; close diffs docs-only
  (A:117–118).

## Pseudo-conflicts to merge

1. **A + C = cite camp**: "cite the existing green" = "cite the green
   receipts" — one ruling.
2. **B + D = re-grade camp**: D's flag-OFF "expect 469, 0 self-flips"
   is a stability *addition* to B's list (D:311 cites flag-ON as cross-
   check). Merge as B's list + D's check; the real fork is camp-vs-
   camp (adjudication 2).
3. **D's "no close" = close-now with an owner condition** (D:326–328)
   — merges into the 4-vs-1 majority; the real fork is adjudication
   1's mechanism.
4. **Keep-ABILWIDTH-dead is unanimous (A–E)**; the split is
   justification only (liability/trap D:282–285 vs P6 seed A:47–48,
   E:377–379). Action settled; chairman picks the close-file wording.
5. **B's scope line + E's flip = one time-stamped ruling**
   (adjudication 3): true as of the stamp, amended by the flip if
   ordered.

---

## REVIEWER R3 — Majority attacker

# REVIEWER R3 (Majority attacker)

## The weakest link

The pool-140/358 re-registration (ruling shape (ii)) is a re-scope
dressed as bookkeeping, and the majority executes it as a council act.
Facts: the halt rule (GATE.md:74–87) enumerates the floor explicitly —
21 D6-extraction + csm-char-04 + 10 invariant residuals + 3 r1blast
stamps; the pool rows are **not** in it, and A20 keeps them in "the D7
named limit (…pool-140/358 width)" (D6_CLOSE_A20.md:35–38). The kill-
clause text ("rows stay floor-registered", GATE.md:1021–1024) presumes
a floor registration the register never granted (R1 item 6). E's "the
width class ran to its pre-registered outcome" (advisors.md:364–366)
is true of **Leg B's kill clause and false of the class**: D57 and Leg
B killed two *global* width predicates; the class-scoped top_k=30
vehicle D57 itself names as fallback — which B/C/E all pre-register as
the Phase-2 spec — was never run. Leg A (TIERED) flipped **zero** pool
rows; it is non-evidence about the class, not exhaustion evidence.
"Exhausted" is argued from one failed probe plus one non-probe. D59
closes the *leg*; it never closed the *class*.

So the close only works by moving a live, in-corpus, in-chunks, owner-
visible defect (gold ranks 12–47, cut at 8) into Phase-2 debt — a re-
scope. D's "the council records, it does not re-scope" (advisors.md:
348–349) and R2's governance-gap flag say that is an owner act. R2's
distillation leaves fork (ii) unresolved, but a close that takes the
council-stamp variant without owner sign-off closes on authority the
council doesn't hold.

**Strongest rebuttal:** (1) the charter pre-registers halt-at-floor,
and the floor is a council-stamped moving register (register-22
stamped at #34) — a re-stamp is in-band, not a re-scope; (2) the kill-
clause outcome (RED ⇒ rows go floor) was pre-registered, so the close
merely executes pre-registration; (3) a new vehicle inside Phase 1 =
new fix-class = floor-moving per council #34, correctly excluded.
**Verdict:** (3) holds; (2) half-holds — pre-registration of the
*outcome* is not pre-registration of the *authority*, and the register
("holdout") vs kill-clause ("floor-registered") conflict is only
adju-dicable by a re-scope; (1) fails — register-22 stamped a triage
of *existing* rows, never admitted new ones. The link breaks as
"council stamp", survives as "close after owner sign-off".

## Attacks on the ritual

- **"Official suite" (cite camp, A/C) is ceremony.** The cited
  receipts already live in the ledger; its one load-bearing element —
  the reboot-rule diff check — is already in GATE_LEDGER (last_green
  bump). The B/D re-grade camp adds a fresh p23 that R2 calls zero-
  information (expectations 469 flag-OFF / 473 flag-ON known in
  advance), at the cost of a :8000 window. **Cut:** the re-grade; keep
  cite + ledger diff-check only.
- **"VOID formal" carries the real safety weight — but as specified it
  is incomplete.** Trigger 1 (no gate regression) is trivially true
  given the empty diff — ceremony. Trigger 2 (d6_flip rc=0: 0 green30
  flips, oos200 drop < 3) is the only product-relevant failing check,
  and E's ritual covers trigger 2 *only* (R1 error note); A/C's "A-
  row register = the 13" is a recast of trigger 3 ("A-row closes-
  still-red"), not the literal (R1 must-adjudicate 3 — no pre-
  registered artifact exists). **Add (one item):** pre-register the
  real trigger-3 artifact — model-free re-grade of A20's 46 closed
  rows at 473, receipted in `VOID_FORMAL.md` pre-stamp; fire ⇒ no
  close, reconvene.

## What the owner's "100%" actually survives as

One sentence: *"CSM Phase 1 closed at the stamped floor: campaign
grade 473/486 flag-ON; shipped product (flag-OFF) 469/486; 13 known
reds — 11 extraction-gated (Phase 2), 2 width-class (pool-140/358)
with a pre-registered, owner-triggerable Phase-2 retest; JJK remains
100%."* Acceptable **only with addendum**: the owner's re-scope sign-
off recorded in the close commit + the width-leg trigger line + B's
claim-scope line time-stamped (per R2 pseudo-conflict 5 it self-
contradicts E's pre-registered flip unless timestamped). Without sign-
off the owner can truthfully say only "closed at floor with two known
in-chunks defects deferred without sign-off" — not the standing
directive. Cheapest survival package: sign-off line + trigger line +
time-stamped claim-scope line, in one docs-only commit.

## Verdict

**Close after owner sign-off on the re-scope** (variant (b) of shape
(ii); D's condition). The sign-off, the trigger line, and the VOID
trigger-3 artifact land in the close commit itself — same docs-only
act, no GPU.

**Switch condition:** if the owner's "commit" word at the close
explicitly carries the re-scope approval (pool-140/358 → Phase-2
width floor + leg trigger), sign-off and close are the same act — I
switch to **close now**.

---

## REVIEWER R4 — Ritual critic

# REVIEWER R4 (Ritual critic)

## Executability table

| Ritual | Cost class | What actually must run | What can be cited |
|---|---|---|---|
| **A** | docs-only, CPU | 3 offline set/diff checks + doc diffs | ledger `legA` (473, "d6_flip rc 0"), gates @`0c8cc953` |
| **B** | **:8000 window** (GPU co-loc or CPU service) | p23 486 flag-ON re-grade + blind 19 + 4 gates ≈ the D7 gate phase | nothing — that's the point |
| **C** | docs-only | same class as A; trigger 3 = paper derivation | ledger greens |
| **D** | **:8000 window** | fresh p23 486 flag-OFF grade (expect 469); rest (registry scan, diff, meter, files) offline | gate cites |
| **E** | docs-only **possible** | `d6_flip.py` verified offline (git show + 2 local files; no API/model/GPU). But "live" d6_flip today = **469v469** (live census = Leg B's grade — verified: 469 greens on disk and @HEAD): vacuous for 473, meaningful only as the product-state check. "One probe window" (endgame 1) = :8000 only if the span probe is re-run — unnecessary, 398/400 is in the committed ledger | gate cites @`0c8cc953` |

Secret :8000 needs: **B and D only**. A/C genuinely docs-only. E's "live
d6_flip" is a mislabel — it needs no server, but measures the wrong
state (469, not 473).

## Auditability gaps

- **All five**: the 473-era census is **not in the tree**. The tracked
  census path holds Leg B's 469 (overwritten by the last leg). 473
  exists as (a) ledger `legA` + GATE.md prose, (b) `LEGA_*.log` —
  gitignored (`.gitignore:132 *.log`). Fresh clone: 473 is a claim,
  re-derivable only as 13 = 17 (committed 469 census) − FLIPS A
  (`check_targets.py`, committed) — or by re-grading.
- **A/C**: trigger-2 raw evidence (d6_flip rc=0 *at 473*) = ignored log
  → vanishes; ledger assertion survives, not the measurement.
- **B**: closes the gap — re-graded census lands on the tracked census
  path, committed. But `gate_*.log` are ignored → raw gate receipts
  vanish unless force-added; values live in the ledger.
- **D**: flag-OFF re-grade census committed ✓; but d6_flip's census
  pre-state must be declared, else it silently runs 469v469.
- **E**: "probe ≥390" — its cited run dir `reports/2026-09-20-*/`
  **does not exist**; the canon re-run dir `reports/2026-09-19-2004/`
  is **untracked, not committed** → raw canon receipts absent from any
  fresh clone (value survives in the ledger only).

## VOID-trigger coverage

A20's 3 triggers (D6_CLOSE_A20.md:40-41) × advisors:

| Trigger | A | B | C | D | E |
|---|---|---|---|---|---|
| T1 no gate regression | ✓ diff | ✓ 4 gates | ✓ cite | ✓ diff+scan | ✓ cite |
| T2 flips (d6_flip) | ✓ cite | ✓ fresh | ✓ cite | ◐ live-469 only | ◐ 469 state |
| T3 A-46 closes-still-red | ✗ recast ("register=13") | ✗ (4th item = A18 "0 new gap IDs", not the 46) | ✗ recast | ◐ pointer, no artifact | ✗ (trigger 2 only) |

**B's 4th item is "0 new gap IDs" (A18 floor-not-moving) — it does
NOT cover T3.** No advisor pre-registers the literal T3 artifact (R1's
gap confirmed). Minimal complete VOID formal (all model-free, pre-
stamp → `VOID_FORMAL.md`): **(1)** reboot_rule: gate-relevant diff
`4a8616bd..HEAD` empty + last_green green @`0c8cc953`; **(2)**
d6_flip rc=0 with census state *declared* (campaign: 469→473 per
ledger legA; product: live 469); **(3)** `CONFIRM_FLIPS.json` 46-set
(committed) ∩ 13-reds @473 = ∅, 13 derived as 17 − FLIPS A from
committed data. Any fire → no close, reconvene.

## The minimal consistent stamp set

1. **`receipts/council_d7_close/VOID_FORMAL.md`** (new; the 3 checks,
   pre-stamp).
2. **GATE.md** — new D7-CLOSE section: 13 reds = 11 ⊂ register-22 + 2
   width-ratified; meter 37; FLOOR16 relabel 14+2; ABILWIDTH stays
   dead (kill clause, P6 seed); TIERED flip = separate owner decision
   with pre-registered bar (4 gates flag-ON + p23 473 repro).
3. **GATE_LEDGER.json** — `d7_close` entry: register 22→24 (pool-
   140/358 ratified: defect width, owner P2 width leg, retest = class-
   scoped top_k campaign, 0 counter-flips vs {pool-149/252}, blind
   19/19); meter 35→37; claim-scope line (campaign flag-ON 473 =
   derived 469+flips; product flag-OFF 469 live; JJK 4/4 @`0c8cc953`);
   receipts list **incl. committing `reports/2026-09-19-2004/`**.
4. **plan/drift_log.md** — D65 (append-only).
5. **PHASE_A_COMPLETE_AT_FLOOR.md** — *amend* (P1.4 section stands as
   historical 22-row stamp, per E): D7 re-stamp — tree `0c8cc953`,
   meter 37, floor 24, 13 reds, P2 handoff 24+10+3, width-trigger
   line, TIERED pre-registration.
6. **reports/master-work/phase_status.txt** — append marker (p14
   pattern: gate-tree `0c8cc953` + stamp commit + meter 37 + claim-
   scope).
7. **Auditability fix (rule into the close commit)**: `git add
   reports/2026-09-19-2004/` (canon receipts, untracked) + commit the
   473 evidence (force-add `LEGA_p23.log`/`LEGA_flip.log`, or a
   derived `LEGA_SUMMARY.json` with red-set + OOS 168→198 + blind
   19/19) — 473 must stop being claim-only.

**Meter: 37 = 24+10+3.** A's 27 and D's 26 break the fixed-register
semantics P1.3 itself established (the meter counts register rows; 6
of the 22 were already green at P1.4 without striking). R2's "10
stale rows" is a note, not a re-stamp. **FLOOR16: relabel (D) +
ratify as the 473-era denominator (E) — the two converge only after
the 22→24 ratification; register-22 stays the historical P1.4 stamp.**

**The single ordering (chairman's rule): VOID_FORMAL (fire ⇒ stop) →
ratification re-stamp (register/meter/FLOOR16) → the five doc diffs
as one docs-only commit → owner "commit" word carrying the re-scope
sign-off (pool rows → P2 width floor + trigger line; R3's switch
condition).** Hazard avoided: stamping before the owner word — a
council-ratified re-scope fossilized in a closed book without owner
authority (R3's weakest link). Secondary hazard: the `d7_close`
ledger entry must land *in* the closing commit (it describes gate-
tree `0c8cc953`, never its own hash) — a prior-commit bump is a
phantom anchor; and if B/D's re-grade is ordered, d6_flip runs at its
declared census state *before* the next grade overwrites the census
file.

---

## REVIEWER R5 — Integrator

# REVIEWER R5 (Integrator)

## The ruling set (proposed)

**Q1 — Close now, via a provisional re-stamp** (A/B/C/E close-now +
D constraint + R3 shape). Halt rule unmet as registered (pool-140/358
∈ A20 D7 holdout register, ∉ register-22; D: 13 = 11 floor + 2
holdout); the council re-stamps register 22→24, meter 35→37, pool
rows → P2 width floor, marking the re-scope **provisional (council-
ratified, owner-ratified-by-return, void on veto)** — the standing
directive can run the docs-only close without claiming re-scope
authority (R3). No P1 width leg (#34; D59 closed the leg, not the
class).

**Q2 — Keep ABILWIDTH dead behind its default-OFF flag; no standalone
revert** (unanimous). Flag-OFF is byte-inert (R1 item 4); a revert is
gate-invalidation for a no-op, burns the P6 seed. Close file carries
D's trap-stamp (measured RED, counter-flips {pool-149,252}; enable
only via new pre-registered leg + 4 gates) + A's P6-seed line;
optional revert rides the TIERED-flip window (E).

**Q3 — TIERED default-flip: YES, post-close, its own gated owner
decision** (unanimous; R5-deferred). One-char commit (context.py:583)
+ 4 gates at flag-ON (eval 31/31, span 48,572+probe, canon 236/236,
pytest 1,331) + p23 473 repro; RED → no flip. The flip changes JJK
(tier-2 in bundles); flag-ON gates prove JJK non-regression (R2's
flag). Owner option 3, outside close.

**Q4 — Bookkeeping** (R1's facts; R4's meter; D's relabel; E's
ratification). (a) Attribution: 463→469 closed-6 = 4 deriv
{arcn-01, org-05/06, vol-10} + 2 Q1-L1 {chap-01, arcn-07} (drift
D57:2093); "2 unattributed" = ledger artifact (D61/63 tracked the
deriv leg only). (b) Meter at close = **37 = 24+10+3** (R4's fixed-
register; 35 = P1.4, superseded); 10 now-green rows (3 flag-ON-only)
= staleness note, not a strike (P2). (c) FLOOR16: **relabel 14 floor
+ 2 ratified-width** (D; bookkeeping, not re-scope), **ratify as the
473-era denominator** (E); register-22 = historical P1.4 stamp.

**Q5 — Close ritual: fully docs-only; no :8000, no GPU** (R4's A/C/E
camp; R3 cut; fills R1's trigger-3 gap). "Official suite" = cite
ledger greens @0c8cc953 (flag-OFF = 20d6da4e, R1 item 4) + reboot-
rule diff `4a8616bd..HEAD` empty (HEAD now ea9a541c, docs-only).
"VOID formal" = R4's 3 model-free checks, pre-stamp → `VOID_FORMAL.
md`: (1) reboot_rule diff + last_green; (2) d6_flip rc=0, census
state declared (live = 469; campaign 473 via committed LEGA
evidence); (3) A20's 46-row CONFIRM_FLIPS.json ∩ 13 reds @473 = ∅.
Any fire → no close, reconvene. Stamp set = R4's 7 items (amended
below).

## Amendments to R4's skeleton

1. **Demote ordering step 4 (the owner word) from gate to
   ratification.** Owner is away; the standing directive authorizes a
   docs-only close. The standing session runs VOID_FORMAL →
   ratification re-stamp → five doc diffs + auditability fix (item 7)
   as one docs-only commit; the re-scope stamp is provisional ("owner-
   ratified-by-return; void on veto"). The stamp is conditional on the
   word, not prior to it (R3's weakest link; R2's governance flag).
2. **Add "no re-grade" to the ordering** (Q5): cite + diff-check
   only.
3. **Add to item 2: D's trap-stamp + R2's time-stamped claim-scope
   line** ("campaign flag-ON 473/486; product flag-OFF 469/486; 13
   reds = 11 extraction P2 + 2 width P2 (provisional, owner-
   ratified-by-return); JJK remains 100%" — time-stamped, E's pre-
   registered flip).

## D's surviving share

Binding, not a footnote: (1) the close is **not "met as
registered"** — the ruling records halt-rule unmet-as-registered, met-
via-provisional-stamp; D's arithmetic (13 = 11 floor + 2 holdout) is
the close-file register; (2) the stamp is **authority-provisional** —
"the council records, it does not re-scope" (D:348-349) survives as
the void-on-veto clause + owner options 2/4; (3) **width class not
exhausted** (D59 closed the leg, not the class; class-scoped top_k=30
never run — R3): the pre-registered trigger line (class-scoped top_k,
0 counter-flips vs {pool-149,252}, blind 19/19, owner-triggerable P2
retest) lands in the close file; (4) the close is **machine-auditable
from a fresh clone** (D's receipts demand) — via R4's item 7 (commit
LEGA 473 evidence + reports/2026-09-19-2004/).

## Owner's decision set

On return, four bounded choices (docs-only close commit with the
provisional stamp already landed):
1. **"Commit" (routine)** = ratify close + re-scope (pool-140/358 →
   P2 width floor, trigger line live) → stamp final; 100% claim =
   "campaign flag-ON 473/486, product flag-OFF 469/486, 13 reds (11
   extraction P2 + 2 width P2, owner-ratified); JJK remains 100%".
2. **"Commit without sign-off"** = close stands as a council stamp;
   re-scope pending owner re-adjudication → the 2 pool rows stay
   "holdout-pending-ratification"; claim demoted to "closed at floor,
   two in-chunks width defects deferred unsigned"; P2 re-adjudicates.
3. **"TIERED flip word"** (post-close, gated) = authorize flipping
   `SCRIPTENGINE_TIERED_RECALL` default to "1" → one-char commit + 4
   gates flag-ON + p23 473 repro; 473/486 becomes default product
   behavior; claim-scope line amended; optional ABILWIDTH revert
   rides it.
4. **"None — status quo"** → provisional stamp voided (docs-only
   reversal); close reverts to "D7 window closed, close deferred";
   pool rows revert to D7 holdouts; council reconvenes or P2 opens
   them.
