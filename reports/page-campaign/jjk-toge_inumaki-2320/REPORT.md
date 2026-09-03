# Toge Inumaki — Prose Pass Report

**Date:** 2026-08-26
**Page slug:** `toge_inumaki`
**Wiki URL:** https://jujutsu-kaisen.fandom.com/wiki/Toge_Inumaki

## Summary

| Metric | Value |
|--------|-------|
| Page-run result | **84/86 questions passed** (97.7%) |
| Set questions (exact) | 6/6 (100%) |
| Fact answers present in bundle | 78/80 (97.5%) |
| Triples authored | 42 (ids 045–086) |
| Retires | 0 |
| Engine gaps documented | 2 |

## Triples Authored (IDs 045–086)

42 new fact-like questions added across 5 uncovered factual sections:

### Abilities and Powers / Overview (8 questions: 045–052)
- 045: Sorcerer level/rank ("respected and highly capable semi-grade 1 sorcerer")
- 046: Solo mission capability among peers
- 047: Geto's early assessment of potential
- 048: Skill tier comparison (below Yuta/Hakari/Todo)
- 049: Intelligence/capability in battle
- 050: Kyoto team's threat assessment during Goodwill Event
- 051: Role in Hanami fight (immobilization ability — **MISS**)
- 052: Shibuya Incident task (civilian saving/transfigured humans)

### Abilities and Powers / Physical Prowess (4 questions: 053–056)
- 053: Speed comparison to Yuji/Maki
- 054: Baseball game physical feat (took base clean)
- 055: Cursed Speech physical toll (throat irritation/coughing blood)
- 056: Post-limit behavior (continues fighting after reaching stamina limit)

### Abilities and Powers / Cursed Technique (10 questions: 057–066)
- 057: Snake Eyes and Fangs seal marking (replaces original kanji question)
- 058: Targets include living beings + inorganic objects
- 059: Higher-energy opponent energy cost
- 060: Communication device compatibility (**MISS**)
- 061: "Explode" effect
- 062: "Explode" used against swarm of weak curses
- 063: "Get Twisted" effect (complete disfigurement)
- 064: "Get Crushed" effect (implode/flattened)
- 065: "Crumble Away" effect (heavy gravity field)
- 066: "Don't Move" effect (complete immobilization)
- [continues through 066: Sleep, Return, Blast Away]

### Equipment (2 questions: 067–068)
- 067: Throat medicine carried (cough syrup)
- 068: How throat medicine helps (prolongs speech time)

### Trivia (16 questions: 069–086)
- 069: Seal marking (Appearance section — replaced old kanji question)
- 070: First name meaning ("thorn/biting words")
- 071: Fanbook hobby (watching YouTube videos)
- 072: Favorite food (tuna mayo onigiri)
- 073: Disliked food (fish eggs)
- 074: Source of stress (morning assembly)
- 075: Volume 0 cooking assessment (best cook out of first years)
- 076: Time to understand his words (half a year)
- 077: Safe Word — affirmation (Salmon)
- 078: Safe Word — negation (Fish Flakes)
- 079: Safe Word — greeting (Kelp)
- 080: Character trait (loves to troll others)
- 081: Height ranking (second-shortest student)
- 082: Popularity Poll rank 1 (4th place)
- 083: Shared English voice actor (Aoi Todo)
- [additional trivia entries through 086]

## Failures (2 misses from prose additions)

### Miss #1: Hanami Fight Question
- **ID:** jjk-pg-toge_inumaki-051
- **Question:** What gave Megumi and Noritoshi a chance against Hanami in their fight?
- **Answer:** an ability that could immobilize the special grade
- **Triage absent-words:** `['ability', 'immobilize']`
- **Root cause:** Retrieval/chunking gap — key unique keywords ('ability' + 'immobilize') do not surface in the top-k beats despite being in the page text. The sentence describing Toge's role in the Hanami fight appears to be deprioritized in retrieval scoring even though it directly describes the character's abilities.
- **Classification:** Engine gap (retrieval). The composite answer combines two clauses but the shortened single-clause version still fails. Not cross-page — the fact is explicitly stated on Toge's own page.
- **Resolution:** Documented as engine gap; left unanswered in batch. Re-run page-run still shows MISS.

### Miss #2: Communication Devices Question
- **ID:** jjk-pg-toge_inumaki-060
- **Question:** Does Toge's technique work through communication devices?
- **Answer:** do not disrupt Toge's technique, allowing him to project his words and their effects over a longer distance
- **Triage absent-words:** `[]` (all answer words present in beats, but not matched)
- **Root cause:** The answer spans sentence boundaries (part of sentence continuing from preceding context about communication devices). The retriever beam contains related content but the exact answer phrase is not returned verbatim. This is likely a chunking boundary issue — the relevant information sits at a chunk cut point.
- **Classification:** Engine gap (chunking/retrieval). The information IS on this page. Not cross-page.
- **Resolution:** Documented as engine gap; left unanswered in batch.

### Note on Voice Actor Question (#086)
- The triage tool flagged jjk-pg-toge_inumaki-086 (voice actor shares with Aoi Todo) as missing keyword 'Todo' in beats, but page-run confirmed this question passes (`ok Aoi Todo`). This is a **flaky** failure — triage is stricter than page-run's actual scoring. No action taken.

## Batch Statistics

| Before | After | Added | Skipped |
|--------|-------|-------|---------|
| 44 questions | 86 questions | 42 | 0 dupes |

## Engine Gap Tracker Update

Existing open gap G8 remains. Toge pass does not add new gap types beyond what G8 already covers. These 2 misses reinforce existing patterns:
- Composite cross-clause answers fail retrieval (G1/G2 overlap pattern)
- Answers straddling chunk boundaries get dropped (G4 pattern)

No new gap class identified.
