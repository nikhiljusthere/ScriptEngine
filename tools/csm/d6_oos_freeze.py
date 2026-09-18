"""D6: freeze the 30-row green stability sample and the 200-row OOS holdout.

Offline, deterministic, pre-model-call (council #35 chair lock, GATE D6 L695-745):
- population = the 486-row p23 widened grade (census_widened_csm_results.jsonl)
- green30 = 5 MECH_GREEN rows per dim class (the six classes holding
  >=5 greens: ability-pool, personality, appearance, causality, organization,
  state-over-time), seeded draws, disjoint from OOS
- oos200 = seeded draw of 200 from (population - green30), mixed verdicts;
  the closure test is a score floor (post >= pre - 2, drop of 3+ voids), so
  window-page rows stay in the pool: they can only rise, never trip the floor
- rows whose subject page is in the 72-page window plan are NOT excluded from
  the draws (chair-lock spec: draws are over the whole population); they are
  flagged "in_window" so the post analysis can slice window vs non-window

Outputs:
  reports/csm/D6_OOS_FREEZE.jsonl   230 rows: original fields + "set" + "in_window"
  reports/csm/D6_OOS_FREEZE.md      the register: rule, seed, counts, deviations
  reports/csm/D6_PAGE134_SLUGS.txt  134 setrel slugs for the page-run baseline
"""

import json
import random
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "reports/csm/census_widened_csm_results.jsonl"
WINDOW_PLAN = ROOT / "reports/csm/D6_DRYRUN_PLAN_WINDOW.txt"
CENSUS_V1 = ROOT / "reports/csm/census_v1_floor_triage.jsonl"
OUT_JSONL = ROOT / "reports/csm/D6_OOS_FREEZE.jsonl"
OUT_MD = ROOT / "reports/csm/D6_OOS_FREEZE.md"
OUT_SLUGS = ROOT / "reports/csm/D6_PAGE134_SLUGS.txt"

SEED = 20260918
GREEN_PER_DIM = 5
OOS_SIZE = 200


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", s or "").lower()
    return re.sub(r"[^0-9a-z]+", " ", s).strip()


def main() -> None:
    rows = [json.loads(l) for l in RESULTS.read_text().splitlines() if l.strip()]
    plan_titles = [l for l in WINDOW_PLAN.read_text().splitlines()
                   if l.strip() and not l.startswith("#")]
    plan_norm = {norm(t) for t in plan_titles}

    def in_window(r: dict) -> bool:
        return norm(r["subject"]) in plan_norm

    # green30: 5 MECH_GREEN per dim class, drawn over ALL greens (no leak
    # exclusion -- the draws are over the whole population, chair lock)
    by_class: dict[str, list[dict]] = {}
    for r in rows:
        if r["verdict"] == "MECH_GREEN":
            by_class.setdefault(r["class"], []).append(r)
    dim_classes = sorted(c for c, rs in by_class.items() if len(rs) >= GREEN_PER_DIM)

    rng = random.Random(SEED)
    greens: list[dict] = []
    deviations: list[str] = []
    per_class_take: dict[str, int] = {}
    for cls in dim_classes:
        cands = by_class[cls]
        take = rng.sample(sorted(cands, key=lambda r: r["id"]), min(GREEN_PER_DIM, len(cands)))
        per_class_take[cls] = len(take)
        if len(take) < GREEN_PER_DIM:
            deviations.append(f"{cls}: only {len(cands)} greens, took all")
        greens.extend(take)
    green_ids_set = {g["id"] for g in greens}

    # oos200: draw from (population - green30); window-page rows stay in the
    # pool (the closure test is a floor, post >= pre - 2, so they can only rise)
    oos_pool = [r for r in rows if r["id"] not in green_ids_set]
    oos = rng.sample(sorted(oos_pool, key=lambda r: r["id"]), OOS_SIZE)
    oos_ids = {r["id"] for r in oos}
    assert not (green_ids_set & oos_ids), "green/OOS disjointness violated"

    out_rows = []
    for g in greens:
        out_rows.append({**g, "set": "green30", "in_window": in_window(g)})
    for r in oos:
        out_rows.append({**r, "set": "oos200", "in_window": in_window(r)})
    OUT_JSONL.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in out_rows))

    slugs = sorted({l["id"].split("-", 1)[1] for l in
                    (json.loads(x) for x in CENSUS_V1.read_text().splitlines() if x.strip())
                    if l.get("id", "").startswith("setrel-")})
    OUT_SLUGS.write_text("\n".join([f"# D6 page-run baseline: {len(slugs)} setrel slugs (census v1 setrel rows)"] + slugs) + "\n")

    oos_verdicts = {v: sum(1 for r in oos if r["verdict"] == v) for v in
                    {r["verdict"] for r in oos}}
    in_win = {
        "green30": sum(1 for r in greens if in_window(r)),
        "oos200": sum(1 for r in oos if in_window(r)),
    }
    md = f"""# D6 OOS/green freeze register (pre-model-call)

Frozen before the D6 GPU window's first model call. Re-grade set = 69 p23 reds
(whole-bank re-grade) + the 30 green rows below + the 200 OOS rows below.

## Rule
- Seed: {SEED} (one `random.Random` instance; per-class green draws in sorted
  class order first, then the OOS draw over the remaining pool, all over
  id-sorted candidates)
- Population: {len(rows)} widened-result rows (`reports/csm/census_widened_csm_results.jsonl`)
- Draws are over the WHOLE population (chair lock): no leak exclusion. The 72-page
  window plan (`reports/csm/D6_DRYRUN_PLAN_WINDOW.txt`, alnum-normalized compare)
  does not shrink the pool; window-page rows are flagged `"in_window"` so the
  post analysis can slice window vs non-window. Rationale: the closure test is a
  score floor (post >= pre - 2, a drop of 3+ voids), so a window row that the
  extraction improves can only rise, never trip the floor; and a green row on a
  window page is the stricter check (the fix must not regress it).
- green30: {GREEN_PER_DIM} MECH_GREEN rows per dim class, classes = the six with
  >=5 greens in the population: {", ".join(dim_classes)}
- oos200: {OOS_SIZE} rows drawn from (population - green30), mixed verdicts
- Disjointness: green30 ∩ oos200 = ∅ (asserted at build)

## Counts
- green30: {len(greens)} -- per class: {json.dumps(per_class_take, sort_keys=True)}; in_window: {in_win["green30"]}
- oos200: {len(oos)} -- verdict mix: {json.dumps(oos_verdicts, sort_keys=True)}; in_window: {in_win["oos200"]}
- oos200 pool size after green30 removal: {len(oos_pool)}

## Deviations
{chr(10).join('- ' + d for d in deviations) if deviations else '- none (every dim class had >=5 greens)'}

## Pre-scoring method (recorded for the pre-baseline)
POST http://127.0.0.1:8000/context {{series: "csm", query: <q>, mode: "qa"}}
(P2.3 shape: no subject, endpoint-default budget/top_k) with `:8000` up;
verdict = `tools/census_dimensions.judge` over `scriptengine.eval.span_recall.served_text`
of the returned bundle -- identical to `tools/csm/p23_grader.py`'s in-process
grade minus the in-process model load, so `:8000` stays the single model holder.

## Green30 ids
{chr(10).join('- ' + i for i in sorted(green_ids_set))}
"""
    OUT_MD.write_text(md)
    print(f"rows={len(rows)} green={len(greens)} oos={len(oos)} "
          f"slugs={len(slugs)} dims={dim_classes} in_window={in_win} "
          f"deviations={len(deviations)}")


if __name__ == "__main__":
    sys.exit(main())