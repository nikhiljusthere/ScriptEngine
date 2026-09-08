# CSM 5.4 narrative-door pre-check — zero-GPU verdict (plan §5.4)

**Verdict: 2026-09-09, model-free (SQL store reads + code read; no GPU, no
service, every probe < 15 s).** Plan §5.4 — "before extraction: the narrative
door against the existing cheap signals" — and the extraction gate: "extraction
proceeds **only if** the dimension census is red on a structural dimension."

## The cheap signals CSM already has (verified in-store, `series/csm/facts.db`)

| signal | count | source |
|---|---|---|
| `chapter` facts | 232 | `facts` (e.g. `98 - 232, 135 chapters`) |
| `manga_debut` facts | 185 | `facts` |
| `episode` facts | 67 | `facts` |
| `anime_debut` facts | 55 | `facts` |
| `arc` edges | 247 | `edges` |
| `volume` edges | 232 | `edges` |
| `next` / `previous` / `prev` edges | 300 / 299 (599 total) | `edges` — the chronology linked list |
| `story_arcs_box` pages | 14 | `documents.page_type` (each carries `next`+`previous`) |
| `saga_box` pages | 2 | `documents.page_type` (`Academy Saga`, `Public Safety Saga`) |
| `chapter_box` pages with a numeral in the title | 232 / 232 | `documents` (`Chapter 1` … `Chapter 232`) |
| `volume_box` pages with a numeral | 24 / 26 | `documents` |
| `episode` pages with a numeral | 12 / 12 | `documents` |
| character-scoped `<X> arc` sections | many (e.g. `Aging Devil arc` 52, `Control Devil arc` 31) | `sections.title` |

## The verdict

**The narrative door CAN serve CSM's chronological story from the existing cheap
signals. No extraction is required for the door to function.**

The two orderings the narrative door needs (`scriptengine/retrieve/narrative.py`
+ `chronology.py`) are both present in-store:

1. **Across pages** — `chronology.py` walks the `previous`/`next` linked list
   restricted to arc pages ("Every arc in order"). CSM has 16 arc/saga
   `*_box` pages each carrying their `next`/`previous` edges (14
   `story_arcs_box` + 2 `saga_box`; 599 order edges corpus-wide). The chain is
   walkable.
2. **Within / by number** — `narrative.py` sorts numbered instalments. CSM's
   232 `chapter_box` + 24/26 `volume_box` + 12/12 `episode` pages all carry
   numerals in their titles, backed by the 232 `chapter` + 67 `episode` + 232
   `volume` facts. Character-scoped `<X> arc` sections give the per-character
   within-page order.

**Extraction (the `events` / `meaning` layer, the 24k-sentence path) is NOT
triggered by this pre-check.** Per plan §5.4, extraction is a **CONDITION**: it
proceeds *only if* the Wave-2 dimension census (CSM-6 instrument, run in the
orchestrator's model window) comes back **red on a structural dimension**. The
cheap signals above are the "existing" half of the test — the census is the
"red-on-a-structural-dimension" half, and only the orchestrator reads that result.
JJK's `semantics` / `prose.db` remain are the standing warning (built extraction
layers that became corpses); the pre-check keeps extraction gated, not assumed.

## Residual

- The narrative-door *live* quality (does a real ordered bundle read well) is a
  zero-GPU check but still needs the index + a question; that is a closure-loop
  probe, not part of this pre-check. This verdict is about **signal presence**,
  not bundle quality.
- If the census is red on a structural dimension, extraction proceeds and this
  pre-check is the record that the cheap signals were checked first (the §5.4
  gate was satisfied before reaching for the model path).