# F2 gate — `/Synopsis` subpage bridge + History probe (step 4)

Closes the F2 branch of the step-4 pilot (COUNCIL_PHASE5_NEXT_MOVE.md step 4):
the council said "fix F2 (retrieval: subpage not in qa floor), gate on a 20–30q
History probe + eval, then census." This is the bridge, the probe, and — new —
the F2b gap the probe exposed.

## 1. The bridge (implemented, gated)

`FactStore.synopsis_subpage_passages(subject)` (`scriptengine/stores/facts.py`,
next to `passages_for_subject`) resolves the subject to its character node, finds
the **sibling `character_synopsis` document titled `<name>/Synopsis`**, and
returns its level-2+ passages. Structural (no hardcoded names): only a character
with a `character_synopsis` node returns anything — battles, techniques and
subpage-less characters return `[]` — so the bridge is inert outside the case it
exists for.

Wired into the qa floor in `build_context` (`scriptengine/api/context.py`,
`_qa_context`): the subpage passages are appended to `passages_for_subject`, with
a **section-title de-dup** — a subpage section already present on the main page
is dropped, so the "no double-serve" the F3 council ordered (tier-scoped gate)
holds at the floor.

Corpus fact (facts.db): 100 History pairs = **68 on the `/Synopsis` subpage, 32
on the main page, and zero characters have both** — so for JJK the de-dup is a
defensive no-op; it matters on a wiki that repeats a section on both pages.

Gates: `pytest tests/` → 1239 passed; `eval --series jjk` → **31/31 (100%)**
(run on GPU/CUDA — Qwen's pinned 24.7 GB leaves ~7 GB; the cross-encoder +
embedder fit in the headroom and Qwen survived the whole run). No B1 regression.

Store-level verification: Hakari 40 subpage passages (History reached), Mahito 26,
Gojo 89 (History reached — it lives only on the subpage), Toge 0 (no subpage),
battle subject 0 (not a character).

## 2. The History probe (F2 gate)

23 questions, mixed tier, in-process auto bundle on GPU
(`PYTHONPATH=/home/goblin/ScriptEngine ./.venv/bin/python
/tmp/opencode/history_probe.py`), F1-correct matcher. 15 subpage-target
(`X/Synopsis`) + 8 main-page-control subjects. The gate is tier-scoped (F3):
minor tier needs reached; main-cast needs reached **and** sourced.

### F1 fix that the probe surfaced (baked into the probe, still to bake into the census)

`reached` must test whether the dimension appears as **any** breadcrumb
component (the council's alias-set check), not just the *last* component.
`Michizane Sugawara / History / Cursed Child Arc` is a genuine History beat, but
its last component is "Cursed Child Arc" — the last-component matcher
(`reanalyze_pilot.py`) miscounted it as a miss. Corrected matcher:
`any(norm(c)==norm(dim) for c in breadcrumb.split(" / "))`.

### Results (corrected matcher)

| tier | reached | sourced |
|---|---|---|
| subpage (F2 target, 15) | 7/15 | 6/15 |
| main-page control (8) | 8/8 | 8/8 |
| all (23) | 15/23 | 14/23 |

The **minor tier is cleared** (Hakari, Mahito, Jiro Awasaka, Yuki Tsukumo, Hanami,
Geto, Todo all reached; 6/15 subpage-sourced). The main-page control is 8/8. The
failures are **all high-degree subjects** — Jogo, Yuji, Gojo, Maki, Megumi,
Nanami, Nobara, Sukuna.

## 3. F2b — the gap the probe exposed (NEW, class (a))

The bridge puts the subpage History in the floor, but for high-degree subjects it
still is not served. Root cause (Yuji ground-truth, `build_context` dump):

- Final bundle = 31 beats / 5985 tokens (budget 6000), **no Yuji/Synopsis History**.
- The 8 beam beats are cross-page (top = `Jujutsu Kaisen (Anime)/Plot` — the
  cross-encoder ranks the anime's plot above the subject's own History).
- The 23 floor beats are **all Yuji's main-page sections**, walked in wiki order
  and heavily duplicated (Appearance ×4, Personality ×8, Abilities/Physical
  Prowess ×7). They consume the entire budget (5985/6000) before the subpage
  History (the 15th floor beat, walked after every main-page section) is reached.

So F2b = **floor-ordering + budget eviction**: the R6 floor serves the subject's
main page in wiki order (with per-section duplication), so for a "history"
question the irrelevant Appearance/Personality beats are paid before the
relevant History beat, and the hard break drops the History. The History **is** in
the corpus and in the floor — this is class (a) *retrievable-but-not-served*, not
a content or citation gap.

Minor characters clear it (shallow page, small beam → the History fits); the
main-cast do not (deep page + busy cross-page beam → eviction).

### F2b resolved (council 14, gated)

Council #14 (`COUNCIL_f2b-floor-ordering.md`) verified the 23 "duplicated" floor
beats are **chunker fragments** (facts.db: Yuji's Personality is 8 distinct
chunks [ordinal 9-16], his /Synopsis Culling Game arc 63; main page 62 + subpage
158 level-2 chunks), not beam-dups or a main/subpage overlap. Verdict: two-stage,
floor-side, query-independent, B1-safe (beam untouched, no beam-trim):

1. **Cap the floor to section granularity** — one leading chunk per section, not
   every fragment (bounds the 220-passage footprint to the section count).
2. **Order the capped floor by query-term overlap** — a "history" question ranks
   the History section ahead of Appearance/Personality. Fixed rule (content-terms
   of the query, subject name excluded, vs the section title; wiki order is the
   tiebreaker), not a per-question knob.

Both land in `_qa_context` (`scriptengine/api/context.py`): `_cap_sections` on
the floor and subpage, and a `_qrank` sort of `floor_fill` (beam still walked
first, unchanged).

**Gate (all pass):** `pytest tests/` → 1239; `eval --series jjk` → 31/31
(re-gated, not assumed); F2 History probe re-run → subpage **reached 15/15**
(was 7/15), all **23/23 reached** — the eight high-degree MISSes (Jogo, Yuji,
Gojo, Maki, Megumi, Nanami, Nobara, Sukuna) all reach their History beat now; the
only non-reached-sourced is Suguru Geto, **reached-uncited** (the section is in
the bundle but the wiki did not cite it readably — a citation-shape state, not a
retrieval miss). Targeted non-history re-probe (Riko personality, Todo
appearance, Toji abilities, Yuta overview) shows no over-ranking of irrelevant
sections. Qwen (`:18080`) survived the co-located CUDA eval + probe (~7 GB
headroom, pinned allocation unchanged).