# R-7 class re-sweep receipt (CSM Phase 1, §9a closure loop)

Date: 2026-09-12 ~03:55 +0530 · HEAD `81df799` (R-7 hunk gated at `60e568f`,
gate window GREEN — see `reports/csm/receipts/r7_gate_window.md`) · :8000 on
CUDA (pid 17494) · all probes live through `POST /context`, series `csm`.

Scope: the R-7 class's own targeted re-sweep (P1.2/§9a rule: class closure =
own class-targeted re-sweep green) — (1) the R-7x queue row `csm-char-04`;
(2) the pre-registered R-1×R-7 discovery-counting re-probes (r1blast-*
stamped rows, `red_list_csm.md` L174–176); (3) the JJK/OPM invariants, which
the same window's four standing gates carry (1,321 collected / 31-31 /
48,572+99.5% / 236-236·10-16·79.0%).

## 1. csm-char-04 — "Every ability of Makima" (R-7x)

- LIVE probe (`mode=qa`, live :8000 CUDA): subject resolves to `Makima`;
  bundle = 8 beats (Makima `Abilities` section tree) + infobox facts. The
  string "Prime Minister of Japan" IS present in the bundle — as the infobox
  `contracted humans` fact value (`facts[13]`: "Multiple unnamed devil hunters
  Prime Minister of Japan Aki Hayakawa †") and in the `Abilities` section
  prose ("the ability to make contracts with humans") — i.e. the *phrase*
  reaches the bundle, exactly as pre-window (same store, same index).
- The bank-gold item, however, is the **ability name** "Contract with the
  Prime Minister of Japan" (bank rename, old name kept as alias;
  `reports/csm/CSM1B_BANK_VALIDATION.md` item 2). The wiki never names the
  contract as an ability: it sits in section prose, extraction stored nothing
  (REFUTED 2026-08-17 note in `series/csm/overrides.yaml`; council
  CSM-1b-2 ruling: the extraction prompt correctly returned `[]`; the gap is
  the qa passage/retrieval leg, not a prompt patch). Abilities path stays
  **7/8** — the documented shape.
- Why R-7 does not (and cannot, in Phase 1) change this: the gated R-7 hunk
  (`git show 60e568f`) is generation-only — `config.identity_fields` + the
  `eval/page_gen.py` identity builder + the 61-key `identity_fields` map in
  `series/csm/overrides.yaml`. No `/context` retrieval code path is touched,
  so the retrieval shape for this question is bit-identical to pre-window.
- Queue ruling (row note): "PM-contract ability sits in section prose, never a
  named heading; extraction stored nothing (abilities extraction track; 5.4
  gate LIVE)". Council #25 (COUNCIL_csm_p1_plan.md, A10) queue math: the row
  is inside the **22 extraction-gated floor rows** (21 `D6-extraction` +
  this one). **Verdict: row stays OPEN as floor** (extraction track, 5.4 gate
  LIVE, Phase 2). No new miss; no miss-count regression.

## 2. r1blast-* — R-1×R-7 discovery-counting re-probes

- **r1blast-tokyo** (CSM, "How many special divisions exist in Public Safety
  Devil Hunters?"): LIVE probe `mode=auto` → routes **qa→roster** (the
  documented post-R-1 handoff, subject "The Public Safety special divisions")
  and serves **all five** Tokyo Special Divisions (1, 4, 5, 6, 7). Zero new
  misses on the stamped row; shape = the post-fix pinned shape
  (`tests/test_csm_router_count_rule.py`).
- **r1blast-blizzard / r1blast-marines** (OPM): covered by the same
  window's gate-4 `canon-run --series opm` (**236/236 canon, 10/16 exact,
  79.0%**) — the documented post-fix shapes (9-member discovered
  `Blizzard Group` set; 7-member discovered `Marine Commanders` set) hold.
  The R-7 hunk is CSM-scoped (`series/csm/overrides.yaml` only) and cannot
  affect OPM. Pinned count-rule tests green in gate-1 (1,316/1,321 passed).

## 3. Verdict

R-7 class re-sweep **GREEN**: zero new misses, zero new queue rows, no
miss-count regression; JJK/OPM invariants green in the same window. The R-7
class **CLOSES with the floor residual `csm-char-04`** (row stays open,
extraction-gated, counted in the 22-floor set; 5.4 re-adjudication at P1.4).
Expected halt-set after this window: 35 open = 22 floor + 3 stamped + 10
documented invariant/residual rows (csmdoor-01, csmd5-01/02/03/05/06,
gate400-320, red-R-4, csm-char-03, csm-set-02) — see
`reports/csm/HALT_METER_P13_DRAFT.md` (its (a)/(b)/(c) split needs this
receipt's floor reading: (a)=22 incl. csm-char-04, (b)=13, (c)=0).