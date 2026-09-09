# Council R-5 advisor 1/5 (adv_A) — final ruling

Recovered from the framework-persisted oracle transcript (run 27796232-d473-404b-8be2-37036e376cec, agent=oracle, ts=1788991498511).
The parent council workflow (429d9efa) was cancelled to enforce one-member-at-a-time council concurrency;
this advisor's work was recovered from disk rather than re-run.

---

I have a complete picture for the TRIGGER PRECISION focus. Key facts established:

- `load_all()` loads only the 8 **official** banks (`jjk.json`, `opm.json`, `csm.json`, …); the `_`-prefixed page batches are excluded. **All 8 official banks contain zero relationship/connection questions** — so the four gates (eval jjk 31, canon opm 236) cannot catch a trigger over-match. The trigger's precision is the *only* safety net.
- `\bconnection\b` (router.py:479) over-matches **11 qa-pinned, non-relationship questions** (mechanism/prose usages) that would misroute to the relations door and miss their prose answers.
- The CSM R-5 bank (all 11) uses "relationship" — never "connection". No test asserts `connection`→relations.
- OPM/JJK/CSM all have relation tables (OPM 359 / JJK 821 / CSM 748 rows), so the re-route of relationship phrasings is structurally plausible, but pair-coverage is a separate (builder) concern.

## Council Advisor 1/5 — TRIGGER PRECISION

**Primary finding — `\bconnection\b` over-matches (router.py:479).**

The five-alternative `_RELATIONS` regex is precise on four of the five cues; the fifth (`\bconnection\b`) is the over-matcher. "connection" in this corpus is a **mechanism/prose** word, not a relationship word, and the trigger captures 11 qa-pinned questions whose answers are prose facts the relations door (relation rows) does not hold:

| series | qa-pinned question the trigger would misroute |
|---|---|
| JJK | "What is the sword Mai left Maki her last connection to?" |
| JJK | "…Megumi's connection to the school, in the Death Painting Arc" |
| JJK | "During the Jogo arc, what connection does Ohaguro have to Jogo's appearance?" |
| JJK | "Did Sukuna lose something that broke his connection to Megumi's soul?" |
| JJK | "How long can Yuta maintain a sustained connection with Rika?" |
| OPM | "What is Flashy Flash's connection to the Ninja Village in OPM?" (answer: "44th Graduation Class" — a prose fact, not a relation row) |
| OPM | "What is God's connection to in One-Punch Man?" |

Each of these, once re-routed to `relations`, would serve the relation table for the named character and **miss** the prose answer — a genuine regression in the OPM/JJK page-batch coverage. It is *latent with respect to the four gates* (I verified all 8 official banks have no relationship/connection questions, so `eval jjk` 31/31 and `canon opm` 236/236 would stay green even with the bug), which is precisely why it has to be caught here: the gates structurally cannot see it.

**The fix is a one-line deletion (router.py:479).** Dropping `r"|\bconnection\b"` is:
- **Bank-safe** — all 11 CSM R-5 questions use "relationship" (I checked: none use "connection"); the OPM/JJK relationship questions use "relationship" / "related" / "relate" / "who is X to Y".
- **Test-safe** — no test asserts `connection`→relations (grep of `tests/test_router.py`, `tests/test_context.py` is clean).
- **Zero recall loss** — no relationship question in the corpus uses bare "connection" as its cue; the four surviving alternatives (`relationship(s)`, `how is/are … related`, `how does … relate`, `who/what is … to`) already cover every relationship phrasing present.

**The other four alternatives are sound.** `relationship(s)` is the dominant, precise cue. `how is/are X related` and `how does X relate` are relationship-specific. The `who/what is \S+ to` guard (single `\S+` before `to`) correctly rejects "what is the key to X" (two words between *is* and *to*) while catching the OPM "Who is Saitama to King" idiom — that guard is doing its job.

**Two minor flags for the builder/reviewer (not blockers):**
1. `r"\bhow\s+does\s+\w+\s+relate\b"` (line ~478) uses single-word `\w+` — a multi-word subject ("how does a new character relate") under-matches. Low priority; no gold question needs it.
2. **Series-agnostic re-route recall risk:** the trigger re-routes ~109 OPM + a batch of JJK relationship questions (page batches, outside the gates) from `qa`→`relations`. That is safe *only if* the relation tables cover those pairs (OPM has 359 relation rows). If a re-routed pair has no row, the relations door returns an empty bundle where `qa`'s prose "Relationships" section would have answered. Recommend the builder spot-check that the OPM/JJK re-routed pairs have relation rows before committing.

**Why this is a blocker, not a note:** the R-5 fix's own stated blast radius includes "JJK/OPM invariant pins" — introducing 11 new OPM/JJK regressions (however latent) violates that. The deletion is trivial, reversible, and removes the only over-matching cue.

OBJECTION: delete `router.py:479` (`r"|\bconnection\b"`) — it misroutes 11 qa-pinned mechanism/prose questions ("Megumi's connection to the school", "Sukuna's connection with Megumi's soul", "Flashy Flash's connection to the Ninja Village", …) to the relations door and they'd miss their prose answers; every relationship question in the CSM R-5 bank and the OPM/JJK pages uses "relationship"/"related"/"who is X to" (never bare "connection"), so the deletion loses zero recall, breaks no test, and no gate catches it — i.e., exactly the over-match this council exists to catch.
