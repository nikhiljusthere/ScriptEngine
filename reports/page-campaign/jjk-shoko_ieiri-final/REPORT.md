# Shoko Ieiri — Character Prose Pass Report

**Status:** 30/34 pass — 4 engine gaps  
**Wiki:** https://jujutsu-kaisen.fandom.com/wiki/Shoko_Ieiri  
**Covered sections:** Personality (6 Qs), Overview (7 Qs), Intelligence (5 Qs), Cursed Energy (4 Qs), Cursed Technique (4 Qs), Trivia (8 Qs) = 34 total  
**Skipped sections:** Appearance (descriptive roster), Battles & Events (enumeration list only), Quotes (dialogue), References, Navigation  

## Results

| Metric | Value |
|---|---|
| Triples authored | 34 (IDs jjk-pg-shoko_ieiri-001 through -034) |
| Batch before | 0 questions |
| Batch after | 34 fact questions |
| Retired | 0 |
| Page-run score | **30/34 passed** |
| Gold errors | 0 |
| Engine gaps | 4 |

## Auto-generated scoring report

Page-run produced: `reports/page-campaign/jjk-shoko_ieiri-2026-08-26-2331/REPORT.md`

Headline: 30/34 questions passed. All 30 passing answers verified as verbatim substrings of wiki prose.

## Failures — 4 engine gaps (not gold errors)

All 4 failures route to `narrative` instead of `qa`, meaning the router recognizes these are QA-style questions but the retriever does not serve relevant passages in the narrative context bundle. The answer text IS present verbatim on the page; the retrieval simply misses it.

### Gap 1: Negated conditional question
- **ID:** 013
- **Question:** What happened to Ijichi and Ino if they had not been treated by Shoko?
- **Answer on page:** "Ijichi and Ino both would have died if they weren't immediately treated by her during the Shibuya Incident."
- **Symptom:** routed `narrative`, absent words: `weren`. Retrieval finds some passage but cannot match "weren't" within it.
- **Pattern:** Questions with negated conditionals ("if they had not been...") appear difficult for the retriever. This is also related to the known G8 router gap (Geto-related wh-anchor pattern, now extended to negation patterns).

### Gap 2: Yes/no style question about absence/negation
- **ID:** 019 (note: triage shows this as ID 020 due to batch renumbering)
- **Question:** Does Shoko have an innate cursed technique?
- **Answer on page:** "Shoko has remarkable control over her cursed energy despite not possessing an innate technique."
- **Symptom:** routed `narrative`, absent words: `remarkable`. Full-sentence answer still fails.
- **Pattern:** "Does..." yes/no format questions trigger narrative routing. The retriever sees this as non-event question. Other similar pages may need coverage via "What kind of cursed technique..." phrasing.

### Gap 3: Abstract capability question with pronoun reference
- **ID:** 022 (triage: 023)
- **Question:** Can Shoko teach someone how to use reverse cursed technique?
- **Answer on page:** "However, when asked how it works, Shoko is unable to put it into proper words that could effectively teach someone else how to use it."
- **Symptom:** routed `narrative`, absent words: [] (empty — no passage matched at all).
- **Pattern:** Long answers starting with "However," containing pronoun "it" rather than explicit noun phrase. The retriever likely matches on "reverse cursed technique" + "teach" but the passage's ranking doesn't surface the specific sentence.

### Gap 4: Comparative question
- **ID:** 024 (triage: 025)
- **Question:** Is it easier for Shoko to heal herself or others?
- **Answer on page:** "Although healing herself is more efficient and less difficult to perform than healing others."
- **Symptom:** routed `narrative`, absent words: [] (empty — no passage matched at all).
- **Pattern:** "Is it easier/more efficient" comparative questions trigger narrative routing. Answer starts with "Although," a discourse marker that weakens semantic match.

## Common thread

All 4 failures share:
1. Routed to `narrative` instead of `qa` — the router classifies them away from the Q/A code path
2. Either empty absent-words (no relevant passage retrieved) or absent-keyword matches
3. Answers contain discourse markers (However, Although) or negation patterns that weaken BM25/semantic match

This appears to be a systematic router+retrieval interaction: questions framed as yes/no, negated conditionals, or abstract comparisons get classified as narrative-context questions, where the chronology-based retrieval loses factual sentences not anchored to named events.

## Recommendations for future engine work

1. **Router fix:** "Does...", "Can...", "Is it..." interrogatives should remain in qa scope even when they probe character attributes rather than events.
2. **Retriever fix:** Discourse markers (However, Although) at sentence start shouldn't degrade relevance scores.
3. **Chunk-level fix:** Negation-heavy sentences may need boosted weight for keywords like "died", "wouldn't".

No changes made to triplets (answers are verified verbatim substrings). These are genuine engine gaps to be addressed in a subsequent engine pass, not something solvable by rephrasing questions.