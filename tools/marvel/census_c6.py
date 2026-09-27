"""C6 — question bank + census (the CSM-method seed), plan MARVEL_100_PLAN.md §4.

The `page-gen` T0 batch (C1: the structured half of every swept page, written
by `page-sweep` as per-page artifacts under `questions/`) becomes a census in
the CSM v1 schema (`class/subject/q/expect/hits/verdict`) with the mechanical
term-count judge, plus the 200-row OOS protocol (a seeded draw from the whole
population, no leak exclusion) and the named-limit register. The bank is the
regression suite; the OOS is the anti-theater arm — the executing agent runs
it and never edits it (a later re-score is a floor, CSM annex: post >= pre - 2,
a drop of 3+ voids).

Subcommands:
  bank          offline: sweep artifacts -> reports/<series>/census_c6_bank.jsonl
                (model-free term verification against the chunk store; no model,
                no :8000, no Qdrant — facts.db is opened read-only)
  census        GPU-only, in-process: the per-class seeded census draw through
                the qa door (the same path the :8000 /context endpoint uses)
  oos-freeze    offline, deterministic, PRE-MODEL-CALL: the seeded 200-row OOS
                draw from the whole bank + the register (rule, seed, counts,
                deviations)
  oos-score     GPU-only, in-process: the OOS pre-score (the anti-theater arm)
  named-limits  offline: the named-limit register (the plan-named caps that
                bound the C6/D2 sets)

House rules followed from the JJK/CSM precedent:
- `tools/census_dimensions.py`: the CSM v1 item shape, the >=2-of-3 mechanical
  judge, the in-process qa door, CENSUS_DEVICE (GPU-only, owner 2026-09-26),
  the per-class seeded draw over id-sorted candidates with ONE rng instance.
- `tools/csm/build_census_widened.py`: expect terms are verified model-free
  under the judge's own matching before they are emitted; terms that fail any
  check are never emitted (counted as residue instead).
- `tools/csm/d6_oos_freeze.py`: the OOS is a seeded draw over the WHOLE
  population (chair lock — no leak exclusion); it stays disjoint from the
  re-run census draw (asserted at build); the register records the rule,
  seed, counts and the pre-scoring method.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

SEED = 20260927          # one seed, one rng, per-class draws first then OOS
OOS_SIZE = 200           # the plan's 200-row OOS protocol
PER_CLASS = 10           # the JJK 14x10 census shape, per class
TEXT_CAP = 3000          # census_dimensions' served-text cap (byte-identical judge)

# The named-limit classes the plan names (D2 blind-fresh, the pre-registered
# caps the C6 register records so a later set can only be bounded by a named
# limit, never by taste):
NAMED_LIMIT_CLASSES = {
    "universe-variant characters": "subjects whose (Earth-XXXX) is not 616/199999",
    "event enumeration": "closed-set event questions (the `battles`/event classes)",
    "issue-level facts": "comic-issue credits/plots (C5 comic rows when scheduled)",
    "state-over-time": "affiliations/roster membership at a date (C5 dimension map)",
}


def norm(text: str) -> str:
    """span_recall's fold: NFC + whitespace, case preserved."""
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def _paths(series: str) -> dict[str, Path]:
    d = ROOT / "reports" / series
    return {
        "bank": d / f"census_c6_bank_{series}.jsonl",
        "meta": d / f"census_c6_bank_meta_{series}.json",
        "census": d / f"census_c6_results_{series}.jsonl",
        "oos": d / f"census_c6_oos_{series}.jsonl",
        "register": d / f"census_c6_oos_register_{series}.md",
        "oos_pre": d / f"census_c6_oos_pre_{series}.jsonl",
        "limits": d / f"census_c6_named_limits_{series}.md",
        "sweep_report": ROOT / "questions" / f"_{series}_page_sweep_a.report.json",
    }


# ── bank ─────────────────────────────────────────────────────────────────────

def _class_of(note: str) -> str:
    """`page-gen:battle:<battle>:<key>` -> `battle`; `page-gen:identity:age` -> `identity`."""
    key = note[len("page-gen:"):] if note.startswith("page-gen:") else note
    return key.split(":", 1)[0]


def _battle_of(note: str) -> str | None:
    """The battle title on `page-gen:battle:<battle>:<key>` notes, else None."""
    key = note[len("page-gen:"):] if note.startswith("page-gen:") else ""
    if key.split(":", 1)[0] != "battle":
        return None
    parts = key.split(":")
    return parts[1] if len(parts) > 2 else None


def _expect_of(question: dict, rid: str) -> list[str]:
    """The CSM v1 expect terms: the answer's own content (item + aliases), capped
    at 3 (the JJK judge's 2-of-3 shape) and whitespace-folded (the judge runs on
    the folded chunk text, so multi-line infobox values must fold to match). Set
    questions sample 3 members deterministically (seeded on the row id) — a
    bundle that carries the subject but fewer than 2 of the 3 sampled members
    is RED."""
    answers = question.get("answer") or []
    if question.get("kind") == "set":
        members = sorted({norm(a.get("item", "")) for a in answers
                          if norm(a.get("item", ""))})
        if not members:
            return []
        if len(members) <= 3:
            return members
        # deterministic 3-of-N sample, seeded on the row id (one hash, a
        # rotation of 3 distinct members — always exactly 3, no set-slicing)
        h = int(hashlib.sha256(rid.encode()).hexdigest(), 16)
        start = h % len(members)
        return [members[(start + i) % len(members)] for i in range(3)]
    terms: list[str] = []
    for a in answers:
        terms.append(norm(a.get("item", "")))
        terms.extend(norm(t) for t in (a.get("aliases") or []))
    return [t for t in dict.fromkeys(terms) if t][:3]


def build_bank(series: str, allow_partial: bool) -> dict:
    from scriptengine.stores.facts import FactStore
    from scriptengine.config import series_paths
    from scriptengine.eval.page_gen import page_set

    p = _paths(series)
    p["meta"].parent.mkdir(parents=True, exist_ok=True)
    artifacts = sorted((ROOT / "questions").glob(f"_{series}_page_*.json"))
    artifacts = [a for a in artifacts if not a.name.endswith(
        (".report.json", ".decl.yaml", ".coverage.json", ".verify.json"))]

    rows: list[dict] = []
    pages = 0
    skipped_no_gen = 0
    residue: list[dict] = []   # rows with an unverifiable expect term (never emitted)
    dup_ids: list[str] = []
    seen_ids: set[str] = set()
    for path in artifacts:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        questions = [q for q in (data.get("questions") or [])
                     if str(q.get("note", "")).startswith("page-gen:")]
        if not questions:
            skipped_no_gen += 1
            continue
        pages += 1
        for q in questions:
            rid = str(q.get("id", ""))
            if rid in seen_ids:
                dup_ids.append(rid)
                continue
            seen_ids.add(rid)
            expect = _expect_of(q, rid)
            if not expect:
                residue.append({"id": rid, "class": _class_of(str(q.get("note", ""))),
                                "reason": "no answer content", "q": q.get("question", "")})
                continue
            row = {
                "id": rid,
                "class": _class_of(str(q.get("note", ""))),
                "subject": q.get("subject", ""),
                "q": q.get("question", ""),
                "expect": expect,
                "source": _battle_of(str(q.get("note", ""))) or q.get("subject", ""),
            }
            rows.append(row)

    # Model-free term verification (build_census_widened's rule, adapted): a term
    # must be stable under the fold AND present, case-insensitively, in the
    # norm-folded chunk text of the page that carries it (the subject's page,
    # plus the battle page for `battle` rows — page-gen's own G3 check only
    # guaranteed the value is chunked SOMEWHERE, never which page).
    settings = None
    from scriptengine.config import get_settings
    settings = get_settings()
    sp = series_paths(series, settings)
    store = FactStore(sp.facts_db)
    tier_total = 0
    try:
        tier_total = len(page_set(store, "a"))
    except Exception:
        pass
    try:
        titles = sorted({r["subject"].lower() for r in rows}
                        | {r["source"].lower() for r in rows if r["source"] != r["subject"]})
        page_text: dict[str, str] = {}
        BATCH = 1000
        for i in range(0, len(titles), BATCH):
            chunk_titles = titles[i:i + BATCH]
            ph = ",".join("?" * len(chunk_titles))
            cur = store.connection.execute(
                f"SELECT doc_title, text FROM chunks WHERE LOWER(doc_title) IN ({ph})",
                chunk_titles)
            for doc_title, text in cur:
                key = (doc_title or "").lower()
                page_text[key] = page_text.get(key, "") + " " + (text or "")
        for key in page_text:
            page_text[key] = norm(page_text[key]).lower()

        def _hay(row: dict) -> str:
            scope = {row["subject"].lower()}
            if row["source"] and row["source"] != row["subject"]:
                scope.add(row["source"].lower())
            return " ".join(page_text.get(t, "") for t in scope)

        def verified(row: dict) -> bool:
            hay = _hay(row)
            return all(norm(t) == t and norm(t).lower() in hay
                       for t in row["expect"])

        emit = []
        for row in rows:
            if verified(row):
                emit.append(row)
            else:
                hay = _hay(row)
                bad = [t for t in row["expect"]
                       if not (norm(t) == t and norm(t).lower() in hay)]
                residue.append({"id": row["id"], "class": row["class"],
                                "reason": f"unverified term(s) {bad!r}", "q": row["q"]})
    finally:
        store.close()

    emit.sort(key=lambda r: r["id"])
    p["bank"].write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in emit))

    # Sweep state: the OOS freeze is only valid over the FULL population, so the
    # meta records whether the tier-a sweep report is complete and error-free.
    # "Complete" = every tier title swept with no error (the tier size comes
    # from the store, NOT from the report: a 93-page report over a 99,591-page
    # tier must read as incomplete, or oos-freeze would draw over a fraction).
    sweep_complete = False
    sweep_pages = 0
    sweep_errors = 0
    if p["sweep_report"].exists():
        rep = json.loads(p["sweep_report"].read_text(encoding="utf-8-sig"))
        sweep_pages = len(rep.get("pages") or [])
        sweep_errors = sum(1 for pg in rep.get("pages") or [] if pg.get("error"))
        no_error = sweep_pages - sweep_errors
        sweep_complete = tier_total > 0 and sweep_errors == 0 and no_error >= tier_total
    meta = {
        "series": series,
        "seed": SEED,
        "sweep_report": str(p["sweep_report"].relative_to(ROOT)),
        "tier_total": tier_total,
        "sweep_pages": sweep_pages,
        "sweep_errors": sweep_errors,
        "sweep_complete": sweep_complete,
        "artifact_pages": pages,
        "rows": len(emit),
        "residue": len(residue),
        "residue_sample": residue[:20],
        "pages_without_generated_rows": skipped_no_gen,
        "duplicate_ids": dup_ids[:20],
        "per_class": dict(sorted(Counter(r["class"] for r in emit).items())),
    }
    p["meta"].write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n")
    if not sweep_complete and not allow_partial:
        print(f"NOTE: sweep report is not complete/error-free "
              f"({sweep_pages} pages, {sweep_errors} errors) — the bank is a "
              f"PARTIAL population; oos-freeze will refuse it without --force",
              file=sys.stderr)
    print(f"bank {series}: {len(emit)} rows from {pages} page artifacts "
          f"({len(residue)} residue, {sweep_pages} sweep pages, "
          f"complete={sweep_complete}); per_class={meta['per_class']}")
    return meta


# ── the seeded draws (one rng, census first, then OOS over the remainder) ────

def _draws(series: str, per_class: int, oos_size: int) -> tuple[list[dict], list[dict], dict]:
    p = _paths(series)
    if not p["bank"].exists():
        sys.exit(f"no bank at {p['bank']} — run `bank` first")
    bank = [json.loads(l) for l in p["bank"].read_text().splitlines() if l.strip()]
    if oos_size > len(bank):
        sys.exit(f"OOS size {oos_size} exceeds the bank ({len(bank)})")

    by_class: dict[str, list[dict]] = {}
    for row in bank:
        by_class.setdefault(row["class"], []).append(row)
    classes = sorted(by_class)
    rng = random.Random(SEED)
    census: list[dict] = []
    per_class_take: dict[str, int] = {}
    for cls in classes:
        cands = sorted(by_class[cls], key=lambda r: r["id"])
        take = rng.sample(cands, min(per_class, len(cands)))
        per_class_take[cls] = len(take)
        census.extend(take)
    census_ids = {r["id"] for r in census}

    # The OOS draw is over (population - census draw): disjoint from the
    # re-run arm (asserted, the JJK chair-lock disjointness), with NO other
    # exclusion — page rows the later prose work improves stay in the pool
    # (the closure test is a floor; they can only rise, never trip it).
    pool = [r for r in bank if r["id"] not in census_ids]
    oos = rng.sample(sorted(pool, key=lambda r: r["id"]), oos_size)
    oos_ids = {r["id"] for r in oos}
    assert not (census_ids & oos_ids), "census/OOS disjointness violated"
    info = {"classes": classes, "per_class_take": per_class_take,
            "pool": len(pool), "census": len(census), "oos": len(oos)}
    return census, oos, info


def run_census(series: str, per_class: int, anchored: bool) -> None:
    # GPU-only (owner 2026-09-26): the in-process qa door loads the embedder +
    # reranker on the named device; never fall back to CPU.
    device = os.environ.get("CENSUS_DEVICE", "cuda")
    os.environ.setdefault("SCRIPTENGINE_DEVICE", device)
    from scriptengine.config import series_paths
    from scriptengine.api.context import build_context
    from scriptengine.eval.span_recall import served_text
    from tools.census_dimensions import judge

    census, _, info = _draws(series, per_class, 0)
    p = _paths(series)
    paths = series_paths(series)
    results: list[dict] = []
    for i, item in enumerate(census, 1):
        try:
            bundle = build_context(
                paths, item["q"], mode="qa",
                subject=item["subject"] if anchored else None)
            rec = judge(item, served_text(bundle))
            rec["error"] = None
        except Exception as e:  # an ERROR row is recorded, never a crash
            rec = {k: item[k] for k in ("id", "class", "subject", "q", "expect")}
            rec.update({"hits": [], "missing": list(item["expect"]),
                        "verdict": "ERROR", "error": f"{type(e).__name__}: {e}",
                        "served": ""})
        rec["anchored"] = anchored
        rec["device"] = device
        results.append(rec)
        if i % 10 == 0 or rec["verdict"] != "MECH_GREEN":
            print(f"  {i:3d}/{len(census)} {rec['id']} [{rec['class']}] "
                  f"{rec['verdict']} {rec.get('missing', [])} {rec['q'][:50]}",
                  flush=True)
    p["census"].write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in results))
    by_cls: dict[str, Counter] = {}
    for r in results:
        by_cls.setdefault(r["class"], Counter())[r["verdict"]] += 1
    green = sum(1 for r in results if r["verdict"] == "MECH_GREEN")
    print(json.dumps({"rows": len(results), "MECH_GREEN": green,
                      "by_class": {c: dict(v) for c, v in sorted(by_cls.items())},
                      "info": info}, indent=2))
    print(f"census {series} -> {p['census'].relative_to(ROOT)}")


def freeze_oos(series: str, oos_size: int, per_class: int, force: bool) -> None:
    p = _paths(series)
    meta = json.loads(p["meta"].read_text()) if p["meta"].exists() else {}
    if not meta.get("sweep_complete") and not force:
        sys.exit(f"sweep report {meta.get('sweep_pages', 0)} pages / "
                 f"{meta.get('sweep_errors', 0)} errors: the OOS draw must be "
                 f"over the FULL population (plan: 'seeded draw from the whole "
                 f"population'). Complete the sweep, re-run `bank`, then "
                 f"`oos-freeze` (or --force for a dev draw).")
    _, oos, info = _draws(series, per_class, oos_size)
    oos_mix = Counter(r["class"] for r in oos)
    rows = [{**r, "set": "oos200", "seed": SEED} for r in oos]
    p["oos"].write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in rows))
    md = f"""# C6 OOS freeze register ({series}, pre-model-call)

Frozen before the C6 GPU window's first model call. Re-grade set = the census
re-run (whole per-class draw) + the {oos_size} OOS rows below. The OOS is the
anti-theater arm: the executing agent runs it and never edits it.

## Rule
- Seed: {SEED} (one `random.Random` instance: the per-class census draws in
  sorted class order first, then the OOS draw over the remaining pool, all
  over id-sorted candidates — the JJK D6 chair-lock shape)
- Population: the whole C6 bank (`{p['bank'].name}`, {meta.get('rows', '?')} rows
  over {meta.get('artifact_pages', '?')} swept pages; census + OOS combined)
- Draws are over the WHOLE population (chair lock): no leak exclusion. Rows on
  pages the later prose work improves stay in the pool — the closure test is a
  score floor (post >= pre - 2, a drop of 3+ voids, CSM annex), so they can
  only rise, never trip the floor
- Disjointness: census draw ∩ OOS = ∅ (asserted at build) — the OOS is a
  holdout; the census draw is the re-run arm and may not leak into it
- Census draw: {info['per_class_take']} rows (per-class {per_class},
  the JJK 14x10 shape), classes = {", ".join(info['classes'])}
- OOS: {len(oos)} rows drawn from (population - census draw), pool
  {info['pool']} rows

## Counts
- OOS class mix: {json.dumps(dict(sorted(oos_mix.items())))}
- bank per-class: {json.dumps(meta.get('per_class', {}))}
- sweep state at freeze: {meta.get('sweep_pages', '?')} pages,
  {meta.get('sweep_errors', '?')} errors (complete={meta.get('sweep_complete')})

## Pre-scoring method (recorded for the pre-baseline)
In-process qa door (`build_context(paths, q, mode="qa", subject=None)` +
`span_recall.served_text` — the same path the `:8000` `/context` endpoint
uses), device `{os.environ.get("CENSUS_DEVICE", "cuda")}` (GPU-only), judged by
`tools.census_dimensions.judge` (the 2/3 rule: a bank of 3 expect terms
needs >= 2, variable-length banks scale to ceil(2n/3); MECH_GREEN).

## OOS ids
{chr(10).join('- ' + r["id"] for r in rows)}
"""
    p["register"].write_text(md)
    print(f"oos frozen {series}: {len(oos)} rows (mix {dict(sorted(oos_mix.items()))}) "
          f"-> {p['oos'].relative_to(ROOT)}; register -> {p['register'].name}")


def score_oos(series: str, out: str = "pre") -> None:
    device = os.environ.get("CENSUS_DEVICE", "cuda")
    os.environ.setdefault("SCRIPTENGINE_DEVICE", device)
    from scriptengine.config import series_paths
    from scriptengine.api.context import build_context
    from scriptengine.eval.span_recall import served_text
    from tools.census_dimensions import judge

    p = _paths(series)
    if not p["oos"].exists():
        sys.exit(f"no frozen OOS at {p['oos']} — run `oos-freeze` first")
    rows = [json.loads(l) for l in p["oos"].read_text().splitlines() if l.strip()]
    paths = series_paths(series)
    results: list[dict] = []
    errors = 0
    for i, row in enumerate(rows, 1):
        try:
            bundle = build_context(paths, row["q"], mode="qa", subject=None)
            rec = judge(row, served_text(bundle))
            rec["error"] = None
        except Exception as e:
            rec = {k: row[k] for k in ("id", "class", "subject", "q", "expect")}
            rec.update({"hits": [], "missing": list(row["expect"]),
                        "verdict": "ERROR", "error": f"{type(e).__name__}: {e}",
                        "served": ""})
            errors += 1
        rec["set"] = row.get("set", "oos200")
        rec["device"] = device
        results.append(rec)
        if i % 25 == 0 or i == len(rows):
            out_path = p["oos_pre"] if out == "pre" else p["oos"].with_name(
                p["oos"].stem + f"_{out}.jsonl")
            out_path.write_text("".join(
                json.dumps(r, ensure_ascii=False) + "\n" for r in results))
            verdicts = Counter(r["verdict"] for r in results)
            print(f"[{i}/{len(rows)}] verdicts={dict(verdicts)} errors={errors}",
                  flush=True)
    out_path = p["oos_pre"] if out == "pre" else p["oos"].with_name(
        p["oos"].stem + f"_{out}.jsonl")
    out_path.write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in results))
    green = sum(1 for r in results if r["verdict"] == "MECH_GREEN")
    print(json.dumps({"rows": len(results), "MECH_GREEN": green,
                      "errors": errors,
                      "green_rate": round(green / max(len(results), 1), 3)},
                     indent=2))
    print(f"oos {out}-score {series} -> {out_path.relative_to(ROOT)}")
    if errors >= 0.1 * len(results):
        sys.exit(3)


def write_named_limits(series: str) -> None:
    p = _paths(series)
    meta = json.loads(p["meta"].read_text()) if p["meta"].exists() else {}
    bank_rows = 0
    variant_rows = 0
    if p["bank"].exists():
        for l in p["bank"].read_text().splitlines():
            if not l.strip():
                continue
            r = json.loads(l)
            bank_rows += 1
            m = re.search(r"\((Earth-)?(\d+)\)$", r.get("subject", ""))
            if m and m.group(2) not in ("616", "199999"):
                variant_rows += 1
    md = f"""# C6 named-limit register ({series})

The plan's named limits, pre-registered (the B2 "named floor (pre-registered)"
shape): a set may be bounded only by a limit named here, never by taste.

| named limit | bound | scope | status |
|---|---|---|---|
| OOS protocol | {OOS_SIZE} rows, seed {SEED} | the whole C6 bank, no leak exclusion | registered; freeze = `oos-freeze` (pre-model-call) |
| census draw | {PER_CLASS} per class | the C6 bank's classes, id-sorted candidates | registered; re-run arm (every gate) |
| universe-variant characters | ~6 (D2 blind-fresh share of the ~24-row fresh set) | subjects (Earth-XXXX) not 616/199999 | registered pre-D2; bank carries {variant_rows} such rows now |
| event enumeration | ~6 (D2 blind-fresh share) | closed-set event questions (`battles`/event classes) | registered pre-D2 |
| issue-level facts | ~6 (D2 blind-fresh share) | comic-issue credits/plots (the C5 comic rows when scheduled) | registered pre-D2; no T0 issue questions in the bank yet |
| state-over-time | ~6 (D2 blind-fresh share) | affiliations/roster membership at a date (the C5 dimension map) | registered pre-D2; needs the C5 consumer |

D2 freezes the ~24-row blind fresh set to `reports/marvel/blind_fresh.jsonl`
(named limit classes per plan §4 D2), corpus-verified expect terms, scored
against the frozen build. The C5 rows schedule only when their consumer names
a real query + failing test (plan §4 C5, the §12 rule verbatim).
"""
    p["limits"].write_text(md)
    print(f"named-limit register -> {p['limits'].relative_to(ROOT)} "
          f"(bank {bank_rows} rows, {variant_rows} universe-variant subjects)")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("bank", "census", "oos-freeze", "oos-score", "named-limits"):
        sp = sub.add_parser(name)
        sp.add_argument("--series", default="marvel")
    sub.choices["bank"].add_argument("--allow-partial", action="store_true")
    sub.choices["census"].add_argument("--per-class", type=int, default=PER_CLASS)
    sub.choices["census"].add_argument("--anchored", action="store_true")
    sub.choices["oos-freeze"].add_argument("--oos-size", type=int, default=OOS_SIZE)
    sub.choices["oos-freeze"].add_argument("--per-class", type=int, default=PER_CLASS)
    sub.choices["oos-freeze"].add_argument("--force", action="store_true",
                                           help="dev draw over a partial bank")
    sub.choices["oos-score"].add_argument("--out", default="pre",
                                          help="pre (the baseline) or post")
    args = ap.parse_args()
    if args.cmd == "bank":
        build_bank(args.series, args.allow_partial)
    elif args.cmd == "census":
        run_census(args.series, args.per_class, args.anchored)
    elif args.cmd == "oos-freeze":
        freeze_oos(args.series, args.oos_size, args.per_class, args.force)
    elif args.cmd == "oos-score":
        score_oos(args.series, args.out)
    elif args.cmd == "named-limits":
        write_named_limits(args.series)


if __name__ == "__main__":
    main()