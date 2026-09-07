# STEP 2 — 3-way failure taxonomy (codified) + classification of the open 2C miss

Date 2026-09-07. Step 2 of the next-move sequence
(`COUNCIL_phase5-next-move.md`, #11). Delivers the failure taxonomy the census
(step 5) will classify every miss against, and applies it to the one open 2C
oracle miss (C1; A4 was closed by `6af92ca`).

## The 3-way scheme

Every open miss is assigned to **exactly one** class. The rule from the
writing method stands: *diagnose the class and fix the gap — never rephrase the
question to dodge it.*

| class | definition | how to prove it | the fix (retrieval-only) |
|-------|-----------|-----------------|--------------------------|
| **(a) retrievable-but-not-served** | the answer **is** in the corpus (a chunk / a structured fact) but retrieval did not surface it for the question | locate the fact: the ground-truth string (or its structured field) is present in `facts.db` / a crawl chunk; a correct answer is reachable | fix the retriever / router / roster / chunker / fusion that lost it |
| **(b) absent-from-corpus / cross-page** | the answer lives on a *different* page than the question's subject, or is not in the wiki at all | the fact is not on the subject page (only on another page / nowhere); cross-page | re-scope the item to the page that holds it, or retire it as cross-page |
| **(c) gold/oracle item wrong** | the ground truth is mis-stated, or the question is unanswerable as phrased | the stated ground truth is false / the phrasing has no determinate answer | fix or retire the item (a *finding*, recorded — the oracle is never silently edited) |

Decision order: first ask **(c)** (is the item even valid?), then **(b)** (is
the fact in the corpus at all, and where?), then **(a)** (it's here but not
served — fix retrieval). A miss is only class (a) once (b) and (c) are ruled
out.

## Classification of the open 2C miss

**Only C1 is open** (A4 closed by `6af92ca`; C2/C3 pass; all other 18-item
groups pass; in-process oracle 17/18).

### C1 — class (a): retrievable-but-not-served (repeat-encounter / first-clash disambiguation)

- **Item:** "When do Todo and Yuji first fight each other?" · check
  `distinguishes` (place at `Kyoto Goodwill Event Arc`, must NOT confuse with
  `Shibuya Incident`) · `expect: fail`.
- **2C result:** `{'has_ground_truth': False, 'confused_with_other': True}` —
  the qa door served the **Shibuya** beats (Mahito, "11:14 P.M. – 11:36 P.M.
  Shibuya Station") instead of the Goodwill first clash.

**Ruled out (c):** the ground truth is valid — Todo and Yuji's *first* clash is
the Goodwill Event (their Shibuya appearance is the later, repeat encounter).
Not a mis-stated item.

**Ruled out (b):** the answer **is** in the corpus. The battle page
`Yuji Itadori vs. Aoi Todo` (node 960, `page_type = battle`) carries 13
structured facts in `facts.db`, including the exact ground-truth field:

```
arc       = 'Kyoto Goodwill Event'
chapters  = 'Chapter 34 - 37'
episodes  = 'Episode 15 - 16'
outcome   = 'Interrupted by Hanami.'
side1     = 'Yuji Itadori'    side2 = 'Aoi Todo'
```

(Also corroborated by the "Synopsis / Kyoto Goodwill Event Arc" section on
`Aoi Todo/Synopsis`.) So the fact is stored and reachable by the battle/roster
retrieval path.

**Therefore (a):** the correct first-clash fact is present but the qa/relevance
door surfaced the more prominent Shibuya repeat-encounter and confused the two.
This is the **repeat-encounter / first-clash disambiguation** gap — the same
family the earlier councils flagged (B5 premise: repeat-encounter / boundary
groups; the oracle's C-section).

## Fix direction (retrieval-only; scheduled for the census/fix loop, step 5)

When a question carries a *first / earliest / before* chronology cue and names
two fighters, the qa path should rank the candidates **chronologically by
chapter** (via the battles-in roster path) and surface the **earliest** battle
page (`Yuji Itadori vs. Aoi Todo`, ch. 34–37), not the highest-relevance later
encounter; and it should flag/suppress the Shibuya confusion. **No 27B
extraction** — the data is already a structured fact. C1 stays a known open
item (a documented expected-fail) until that disambiguation lands; it is *not*
retired and *not* rephrased.

## Census application (step 5)

For each of the 545 (dimension, character) census misses, run the decision
order above and record `class ∈ {a,b,c}` + the evidence (the located fact / the
absent page / the invalid ground truth). Class (a) → retrieval fix; class (b) →
re-scope/retire cross-page; class (c) → fix/retire the item as a finding.
Report the census split by class, not as a single aggregate.