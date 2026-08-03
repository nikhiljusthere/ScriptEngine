# Pipeline triage: where the breakage actually is

19 queries traced end to end through router → retrieval → rerank/validate →
output, on the running code. Every bucket below is assigned from a line in the
trace, not from recollection.

**Two structural facts first, because they bound what this can show:**

* **There is no synthesis stage.** `build_context` (`api/context.py:129`)
  assembles a bundle and returns it; generation happens downstream in the
  writer. The *Synthesis error* bucket is therefore empty **by construction** —
  a wrong final sentence would be the writer's, not this pipeline's.
* **`qa` mode is unreachable from `auto`.** Both `cli.py:699` and
  `api/main.py:153` read `"roster" if looks_like_enumeration(q) else
  "narrative"`. The hybrid BM25+vector+graph+rerank path — the most-engineered
  part of the system — is **never selected automatically**. It only runs if a
  caller names it.

## The map

| query | mode selected | expected | bucket | root cause | fix location |
|---|---|---|---|---|---|
| What grade of sorcerer is Aoi Todo? *(control)* | **roster** | qa | **Misrouted** | `_ENUMERATION` matches `grades? of`, so a fact lookup became a roster of `Aoi Todo Battles` — 5 battles, not a grade | `roster.py:47` `_ENUMERATION` / `cli.py:699` |
| Who killed Ace? | **narrative** | qa | **Misrouted** | qa's shortlist *did* contain Akainu (`Mera Mera no Mi`, rerank 0.974); narrative resolved the subject to `Legendary Hour`, an episode page, and returned 4 beats without the answer | `api/main.py:153`, `cli.py:699` |
| Every Way Sorcerers Can Die in the Culling Game | roster | roster | **Ontology mismatch** | declared phrase `sorcerers` claimed the topic → `Jujutsu Sorcerers`, 68→67; "way/die" are not a set the wiki keeps | `series/jjk/overrides.yaml` |
| Every Instant Kill Domain Expansion | roster | roster | **Ontology mismatch** | declared `domain expansion` → all 14 domains; "instant kill" is a property no page records | `roster.py::_grounded` |
| Every Apocalypse Level Devil | roster | roster | **Ontology mismatch** | declared `devil` → all 88; `apocalypse` ungrounded. **Now flagged** `partial` with a warning | `roster.py::_grounded` |
| Every Kai | roster | roster | **Ontology mismatch** | `Deities` declares `match: [... kai, kais]`, so "Kai" returns 169 deities | `series/db/overrides.yaml` |
| Every member of the Mink Tribe | roster | roster | **Ontology mismatch** | matched `tribe` → `Races and Tribes` (34→1, the race page). "Members *of* a race" is a different question shape from "every race" | `roster.py::build_roster` |
| Every member of the Espada | roster | roster | **Data modelling gap** | category `Espada` holds 25 (18 after subpage folding) for 10 seats; the wiki files every past holder together | source data |
| Every member of the Straw Hat Pirates | roster | roster | **Data modelling gap** | `Straw Hat Pirates Members` includes Nefertari Vivi, a former/honorary member | source data |
| Every island in the Grand Line | roster | roster | **Data modelling gap** | `Grand Line Islands` has 4 members; the wiki files most islands by arc instead. Reports `exact` because the *name* matched | source data |
| What race is Vegeta? | narrative | qa | — **pass** | answer present (`Saiyan`), 17 beats | — |
| What is Zoro's sword called? | narrative | qa | — **pass** | Wado Ichimonji, Enma, Sandai Kitetsu all present | — |
| What is Ichigo's bankai? | narrative | qa | — **pass** | `Tensa Zangetsu` present, though subject resolved to `Zanpakutō` not Ichigo | — |
| What Nen type is Killua? | narrative | qa | — **pass** | `Transmuter` present, subject resolved to `Nen` | — |
| What devil is Power? | narrative | qa | — **pass** | `Blood` present, subject resolved to `Devil` | — |
| Who taught Goku the Kaio-ken? | narrative | qa | — **pass** | `King Kai` top beat | — |
| Every Nen type *(control)* | roster | roster | — **pass** | 6, declared | — |
| Every Apostle *(control)* | roster | roster | — **pass** | 17, declared | — |
| Every Saiyan transformation *(control)* | roster | roster | — **pass** | 160→44, declared | — |

## Bucket frequency

| bucket | failures |
|---|---:|
| **Ontology / category mismatch** | **5** |
| Data modelling gap | 3 |
| Misrouted | 2 |
| Retrieval miss | 0 |
| Rerank / fusion loss | 0 |
| Synthesis error | 0 (n/a — no synthesis stage) |

## Fix this first: ontology / category mismatch

Five of ten failures, and they share one shape: **the declared registry claims a
topic on a single word, then answers with the parent set.** `sorcerers` →
all 67 sorcerers. `devil` → all 88 devils. `kai` → 169 deities. `tribe` → the
races set. `domain expansion` → all 14 domains.

The narrowing part of the topic — *ways to die*, *instant kill*, *apocalypse
level*, *Mink* — is then either ungrounded and dropped, or grounded and
ineffective. Either way the answer is the superset, and four of the five report
`declared`, the highest confidence the system has.

The fix is in two named places, not an architecture change:

1. **`roster.py::_grounded`** — a dropped qualifier already sets `unverified`
   and downgrades confidence, but only when *nothing* was filtered. The Kai and
   Mink cases pass that test and stay `declared`. Widen the condition to "the
   qualifier had no measurable effect", not "nothing was rejected".
2. **The `match:` lists in `series/*/overrides.yaml`** — single common words
   (`kai`, `devil`, `sorcerers`, `tribe`) are too greedy. Longest-phrase already
   resolves collisions when a longer phrase is declared; the missing piece is
   declaring the narrower sets so there is something longer to win.

## What was fixed, and what it measured

**The router is now three-way** (`retrieve/router.py`), called from the one
place both the CLI and the API use. `qa` is reachable. Routing reads the
ontology rather than more regex: a wh-question about a character/item/technique
is a lookup, an event subject or a story verb *at the head of the sentence* is
an account, and "how many" is a set. Every decision carries a `why`, returned
in the bundle as `routed`.

Three bugs surfaced while building it, each caught by a case that had been
passing:

* **`SUBJECT_DEMOTE_TYPES` matches raw infobox ids**, so it demotes `episode` on
  Dragon Ball and misses `episode_box` on One Piece — which is how "Who killed
  Ace?" became a question *about* an episode called `Legendary Hour`. Routing
  now demotes by semantic type, which is one vocabulary across all eight wikis.
* **Subject preference has to consider the question**, not just the type: the
  fix above then hid `Shibuya Incident` behind `Shibuya`. Candidates are ranked
  by how many of the question's words they share, so the incident beats the
  place and `Portgas D. Ace` beats a special that shares no word at all.
* **A story verb inside a relative clause is not a story question.** "the
  strengthened punch that *occurs* when an attack lands" is a description of
  Black Flash; only the head of the sentence votes.

**The confidence test now asks whether the qualifier did anything.** Rejections
are tagged with the rule that produced them, and a qualifier that rejected
nothing downgrades the answer whatever the counts say. The predicate
`pre == post` would have caught 1 of 5; this catches 3 more:

| query | before | after |
|---|---|---|
| Every Way Sorcerers Can Die | 68 → 67, `declared` | `partial`, flagged |
| Every Instant Kill Domain Expansion | 14 → 13, `declared` | `partial`, flagged |
| Every Apocalypse Level Devil | 88 → 88, `partial` | unchanged |
| Every Kai | 218 → 169, `declared` | **9 → 8 Kais**, declared set |
| Every member of the Mink Tribe | 34 → 1 | unchanged — its qualifier *did* apply; this one is question shape, not confidence |

`Every Kai` needed config as well as code: `Deities` declared `match: [... kai]`,
and a declared phrase consumes the whole topic, so there was no qualifier left
for any test to notice. With the word removed, discovery matched the *anime
series* `Dragon Ball Z Kai` and returned four of its songs at `exact` — so the
set is now named outright, the way the Gods of Destruction are.

**The eval suite runs through the router.** It called each path directly, which
is why the Aoi Todo misroute sat at 24/24 while being broken through every real
caller. Cases now carry `expect_mode` and fail when the router disagrees, and
fact cases exist for `db`, `onepiece` and `hxh` for the first time.

Proven to be a net rather than a decoration: flipping one `expect_mode` to a
deliberately wrong value took hxh from 6/6 to 5/6, and restoring it returned
6/6.

Two of the seven cases this initially failed were **my expectations, not the
router**: "Tell me about Todo Aoi." and "What happened to Nanami during the
Shibuya Incident?" are narrative questions, and I had mapped them to `qa` by
kind rather than by reading them.

**Collateral: one count moved across 151 sheet questions** — `Every Kai`,
169 → 8. Tests 419, evals jjk 24/24, db 11/11, onepiece 7/7, hxh 6/6.

## Corrections to the section above

That section was written by the person who wrote the fix, and re-checking it
found two claims that do not hold and one regression it introduced.

**"Routing now demotes by semantic type across all eight wikis" was false.** It
was true of `router.py` only; `roster.py` and `narrative.py` still passed the
raw id list to `rank_subjects`. And that list is JJK-shaped — 11 of its 12 ids
exist on jjk, **1 of 12 on One Piece** — so packaging pages eligible to be
chosen as a question's subject numbered 2,934 on One Piece and 1,547 on Dragon
Ball. Now folded through the shared vocabulary in `rank_subjects` itself:
**every wiki measures 0**.

**The subject-ranking fix had a deeper cause than reported.** Word-overlap
ranking failed 8 of 12 adversarial possessive questions, and the root was not
ranking at all: `_WORD = [\w'’-]+` keeps the possessive, so `link_entities`
built candidates like `"ichigo's"` that match no alias and returned **nothing**
for "What is Ichigo's Zanpakuto?". Candidates are now offered in both spellings.
Overlap also turned out to be the wrong *re-sort* — `rank_subjects` already
ranked Sukuna first, and overlap promoted `Domain Expansion` over him — so the
existing order is kept and only two things move a candidate: a possessive names
its owner, and a candidate sharing no word with the question sinks. 9 of 10 now
resolve correctly.

**The confidence predicate downgraded three correct answers.** "A qualifier that
rejected nothing" is not the same as "a qualifier that means nothing": every
Sternritter *is* a Quincy, and the answer was marked `partial` and told that
`quincy` "names nothing this wiki records" — on a wiki with a 54-member Quincy
set. The predicate now also asks whether the members satisfy the qualifier, and
requires **all** of its words rather than any, because most sorcerer pages
mention the Culling Game and `any` let "Every Way Sorcerers Can Die" back
through as confident. Both directions are asserted: Quincy/Chimera Ant/Logia
return to `declared`; ways-to-die, instant-kill and apocalypse stay `partial`.

**Two eval "corrections" held up, one did not.** "What happened to Nanami…" is
narrative on the evidence — narrative resolves `Kento Nanami` and returns his
death in 14 beats. The Akainu/Sakazuki case was fixed the wrong way: dropping a
name hid that either would do, so `expect_any_text` now exists. And
"Tell me about Todo Aoi." had no independent justification — I set it to what
the router produced, which is fitting the test to the code, so the assertion is
withdrawn rather than tuned.

**Still open after this pass:** `Luffy` is an unresolved alias, so
"What is Luffy's Devil Fruit?" still resolves its subject to a random fruit —
harmless for routing, since both land in `qa`, but wrong. The swallow surface is
now visible via `cli rosters --audit` rather than fixed: 2 of 14 single-word
phrases on jjk claim sets of 40+ members, and the variant where a phrase
consumes the entire topic remains undetectable automatically.

Measured after all of it: **0 of 151 sheet answers moved**, 419 tests, evals
jjk 24/24, db 11/11, onepiece 7/7, hxh 6/6.

## Two things the trace ruled out

**Retrieval and reranking are not the problem.** Across every qa trace the
correct chunk was in the shortlist when one existed, and no case was found where
the answer was retrieved and then dropped by rerank or `top_k`. The
`dropped` list for "Who killed Ace?" holds `Episode 495`, `3D2Y`, `Gol D.
Roger` — nothing that answers the question. Fusion is doing its job: the top
chunks are consistently ones two retrievers agreed on (`lexical,vector`).

**The instrumentation added for this triage changed nothing** — 393 tests and
all four eval sets (db 9/9, jjk 24/24, onepiece 5/5, hxh 5/5) are identical
before and after.

## Worth knowing, outside the buckets

`auto` never picks `qa`. Six fact lookups landed in `narrative` and *still*
produced the answer, which is luck rather than design — narrative walks one
page's sections, so it works when subject resolution lands well and fails when
it does not, which is exactly what happened to "Who killed Ace?". Subject
resolution also preferred the concept page over the character in four of six
(`Zanpakutō` over Ichigo, `Nen` over Killua, `Devil` over Power,
`Legendary Hour` over Portgas D. Ace) without costing the answer in five of
them.
