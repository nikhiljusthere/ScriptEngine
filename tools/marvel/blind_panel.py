#!/usr/bin/env python
"""D2 blind-fresh set — sealed candidate panel (plan MARVEL_100 §5 Phase D-D2).

The ~24-row blind fresh set (CSM Step 0 shape) is authored by someone OTHER
than the executing agent (Plan_to_perfection D4). This tool prepares the
sealed half of that: a hash-pinned draw of candidate subjects, one panel per
named-limit class, that the authoring party writes questions against. The
executing agent never sees authoring choices and never writes the questions;
the author never sees the corpus (subjects come sealed; expect terms are
corpus-verified by the tool after authoring).

Zero egress: read-only facts.db + committed receipts. Hash-pinned (the §2a
trap: no mutable RNG state — the panel is a pure function of the tree:
sha256(seed:class:title)), so re-running on the same tree reproduces the
same panel byte-for-byte.

Disjointness: the panel subject is kept OUT of the campaign's SCORED probe
sets — the census re-run draw + the OOS re-score draw (seed 20260927, both
offline). It is NOT kept out of the complete bank: the bank is the census
SEED (a population, not a scored suite), and the blind questions are novel
(authored by the non-executing party; expect terms corpus-verified by this
tool). See the build_panel comment for the CSM Step 0 reasoning.

Protocol (the executing agent runs the tooling; a NON-executing party
authors the questions):
  1. `panel`    (default) — seal the candidate panel after the post-sweep
     chain's `bank` step. Writes reports/marvel/blind_panel_<date>.jsonl.
  2. AUTHOR     — the authoring party (corpus-blind) writes at most one
     question per panel subject: a JSONL draft of
     {"class", "subject", "q", "expect"[]}. They never see the corpus;
     expect terms are their own prior knowledge.
  3. `validate --draft <file>` — enforces the seal (every row's
     (class, subject) is a panel row for that class), applies the bank's
     model-free expect-term rule (norm-stable, present in the norm-folded
     chunk text of the subject's page, read-only facts.db), and freezes
     the VERIFIED rows to reports/marvel/blind_fresh.jsonl. Failing terms
     are named per row (the author re-guesses, still corpus-blind). Pass
     needs >= 4 verified rows per class (16 total); the frozen file is
     then the D4 held-out probe set — the executing agent never edits it.
  4. `score`    — GPU in-process, the oos-score judge path: score the
     frozen set, write reports/marvel/blind_fresh_scored.jsonl + the
     green-rate summary. The D4 threshold is declared in the protocol
     doc (plan §5 D2: "fixes that move only the bank fail against it").

Run AFTER the post-sweep chain's `bank` step (it needs the COMPLETE marvel
bank + the offline census/OOS draws for the disjointness assertions):

    scriptengine/.venv/bin/python tools/marvel/blind_panel.py --series marvel

Writes reports/marvel/blind_panel_2026-09-27.jsonl (the sealed panel) and
prints the seal block (panel sha256 + tree stamp) for the protocol doc.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from census_c6 import SEED, _draws, _paths  # house draw logic, one source

ROOT = Path(__file__).resolve().parents[2]

# The named-limit classes (the D2 blind-fresh shares registered pre-D2 in the
# named-limit register; ~6 each of the ~24-row set). Eligibility is measured
# against the store, never against taste.
CLASSES = {
    "universe-variant": {
        "quota": 6,
        "where": ("page_type='character' and title like '__(Earth-%)' "
                  "and the universe is not 616/199999"),
        "sql": ("select id, title from documents where page_type='character' "
                "and title like '%(Earth-%)'"),
        "filter": lambda t: _universe(t) not in NON_PRIMARY_UNIVERSES,
    },
    "event-enumeration": {
        "quota": 6,
        "where": "page_type='event' (closed-set event questions)",
        "sql": "select id, title from documents where page_type='event'",
        "filter": lambda t: True,
    },
    "issue-level": {
        "quota": 6,
        "where": "page_type='comic' (issue credits/plots)",
        "sql": "select id, title from documents where page_type='comic'",
        "filter": lambda t: True,
    },
    "state-over-time": {
        "quota": 6,
        "where": ("page_type='character' with a populated affiliation fact "
                  "(roster membership at a date; the C5 dimension map)"),
        "sql": ("select d.id, d.title from documents d join facts f on "
                "f.node_id=d.id where d.page_type='character' and "
                "f.key='affiliation' and f.value<>''"),
        "filter": lambda t: True,
    },
}
NON_PRIMARY_UNIVERSES = ("616", "199999")
# The verified-set floor (validate): >= 4 questions per named-limit class,
# 16 total. The register's ~6/class is the ideal; 4/class is the floor at
# which the D4 threshold is meaningful.
MIN_PER_CLASS = 4


def _universe(title: str) -> str:
    # "Peter Parker (Earth-616)" -> "616"; no marker -> ""
    if title.endswith(")"):
        open_idx = title.rfind("(Earth-")
        if open_idx != -1 and title[open_idx:open_idx + 8] == "(Earth-":
            return title[open_idx + 7:-1]
    return ""


def _pin(cls: str, title: str) -> int:
    return int(hashlib.sha256(f"{SEED}:{cls}:{title}".encode()).hexdigest(), 16)


def build_panel(series: str) -> dict:
    p = _paths(series)
    if not p["meta"].exists():
        sys.exit(f"no bank meta at {p['meta']} — run the post-sweep chain's "
                 "`bank` step first")
    meta = json.loads(p["meta"].read_text())
    if not meta.get("sweep_complete"):
        sys.exit(f"bank at {p['bank']} is from an INCOMPLETE sweep "
                 f"(sweep_pages {meta.get('sweep_pages')}/{meta.get('tier_total')}); "
                 "the panel seals against the complete bank only")

    con = sqlite3.connect(
        f"file:{ROOT / 'series' / series / 'facts.db'}?mode=ro", uri=True)
    # Disjointness: the panel subject may not appear in any SCORED campaign
    # probe set — the census re-run draw + the OOS re-score draw (seed 20260927,
    # both offline; the OOS rescore is the campaign's tracked movement arm,
    # post >= pre - 2). The panel must be an independent held-out signal, so
    # no scored arm can be moved "for" it. The COMPLETE BANK is not in this
    # set: it is the census SEED (the population), not a scored suite — the
    # CSM Step 0 "different subjects than any bank row" wording applies when
    # the bank is the scored regression suite (JJK's 486 rows); here subject
    # overlap with the seed is allowed because the blind questions are novel
    # (authored by the non-executing party; expect terms corpus-verified by
    # this tool, never by taste).
    census, oos, draw_info = _draws(series, per_class=10, oos_size=200)
    seen = {r["subject"] for r in census} | {r["subject"] for r in oos}

    panel = []
    for cls, spec in sorted(CLASSES.items()):
        rows = con.execute(spec["sql"]).fetchall()
        cands = [r for r in rows if spec["filter"](r[1])
                 and r[1] not in seen]  # sealed disjointness
        cands.sort(key=lambda r: _pin(cls, r[1]))
        take = cands[:spec["quota"]]
        if len(take) < spec["quota"]:
            sys.exit(f"class {cls}: only {len(take)} disjoint candidates "
                     f"(quota {spec['quota']}) — widen the register, do not "
                     "lower the disjointness rule")
        for doc_id, title in take:
            panel.append({
                "class": cls, "subject": title, "doc_id": doc_id,
                "pin": f"{_pin(cls, title):032x}", "eligibility": spec["where"],
            })
    con.close()
    return {"panel": panel, "meta": meta, "draw_info": draw_info,
            "disjoint_from": {"census": len(census), "oos": len(oos),
                              "scored_subjects": len(seen)},
            "class_counts": dict(Counter(r["class"] for r in panel))}


def _panel_path(series: str) -> Path:
    return ROOT / "reports" / series / \
        f"blind_panel_{date.today().isoformat()}.jsonl"


def _frozen_path(series: str) -> Path:
    return ROOT / "reports" / series / "blind_fresh.jsonl"


def _scored_path(series: str) -> Path:
    return ROOT / "reports" / series / "blind_fresh_scored.jsonl"


def _panel_rows(series: str) -> list[dict]:
    path = _panel_path(series)
    if not path.exists():
        sys.exit(f"no sealed panel at {path} — run `panel` first")
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def validate_draft(series: str, draft: Path) -> None:
    """Enforce the seal + the bank's expect-term rule; freeze verified rows."""
    from census_c6 import norm
    from scriptengine.stores.facts import FactStore
    from scriptengine.config import series_paths, get_settings

    panel = _panel_rows(series)
    allowed: dict[str, set] = {}
    for r in panel:
        allowed.setdefault(r["class"], set()).add(r["subject"])
    rows = [json.loads(l) for l in draft.read_text().splitlines() if l.strip()]
    for r in rows:
        for k in ("class", "subject", "q", "expect"):
            if k not in r:
                sys.exit(f"draft row missing {k!r}: {r!r}")
        if r["class"] not in allowed:
            sys.exit(f"row class {r['class']!r} is not a panel class")
        if r["subject"] not in allowed[r["class"]]:
            sys.exit(f"SEAL VIOLATION: {r['class']}/{r['subject']} is not in "
                     f"the sealed panel for that class — the author may only "
                     "question panel subjects")
        if not isinstance(r["expect"], list) or not r["expect"] or \
                not all(isinstance(t, str) and t for t in r["expect"]):
            sys.exit(f"row {r['subject']}: expect must be a non-empty "
                     f"list of strings")
    seen_pairs: set[tuple[str, str]] = set()
    for r in rows:
        key = (r["class"], r["subject"])
        if key in seen_pairs:
            sys.exit(f"duplicate draft row for {key} — one question per "
                     "panel subject")
        seen_pairs.add(key)

    # The bank's model-free expect-term rule (build_bank, census_c6.py): a
    # term must be norm-stable AND present case-insensitively in the
    # norm-folded chunk text of the page that carries it.
    p = _paths(series)
    settings = get_settings()
    sp = series_paths(series, settings)
    store = FactStore(sp.facts_db)
    try:
        titles = sorted({r["subject"].lower() for r in rows})
        page_text: dict[str, str] = {}
        BATCH = 1000
        for i in range(0, len(titles), BATCH):
            chunk_titles = titles[i:i + BATCH]
            ph = ",".join("?" * len(chunk_titles))
            cur = store.connection.execute(
                f"SELECT doc_title, text FROM chunks WHERE "
                f"LOWER(doc_title) IN ({ph})", chunk_titles)
            for doc_title, text in cur:
                key = (doc_title or "").lower()
                page_text[key] = page_text.get(key, "") + " " + (text or "")
        for key in page_text:
            page_text[key] = norm(page_text[key]).lower()
        verified: list[dict] = []
        residue: list[dict] = []
        for r in rows:
            hay = page_text.get(r["subject"].lower(), "")
            bad = [t for t in r["expect"]
                   if not (norm(t) == t and norm(t).lower() in hay)]
            base = {"id": hashlib.sha256(
                        f"{SEED}:{r['class']}:{r['subject']}:{r['q']}".encode()
                    ).hexdigest()[:16],
                    "class": r["class"], "subject": r["subject"],
                    "q": r["q"], "expect": list(r["expect"]),
                    "set": "blind"}
            if bad:
                residue.append({**base, "reason": f"unverified term(s) {bad!r}"})
            else:
                verified.append(base)
    finally:
        store.close()

    out = _frozen_path(series)
    verified.sort(key=lambda r: r["id"])
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("".join(
        json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n"
        for r in verified))
    digest = hashlib.sha256(out.read_bytes()).hexdigest()
    # The floor is judged over ALL panel classes: a class with zero verified
    # rows must trip it too (not just classes with a positive-but-short count).
    tally = Counter(r["class"] for r in verified)
    short = {c: tally.get(c, 0) for c in sorted(allowed)
             if tally.get(c, 0) < MIN_PER_CLASS}
    print(f"validated {len(rows)} draft rows -> {len(verified)} verified, "
          f"{len(residue)} unverified")
    print(f"  per-class verified: {dict(sorted(tally.items()))} "
          f"(floor {MIN_PER_CLASS}/class)")
    for rr in residue:
        print(f"  RESIDUE {rr['class']}/{rr['subject']}: {rr['reason']}")
    if short:
        for c, n in short.items():
            print(f"  SHORT {c}: {n}/{MIN_PER_CLASS} — the author fixes the "
                  f"named terms (still corpus-blind) and re-runs; the frozen "
                  "file holds only verified rows")
        sys.exit(1)
    print(f"frozen blind set -> {out} ({len(verified)} rows)")
    print(f"  blind_fresh sha256: {digest}")
    print(f"  panel: {_panel_path(series).name} ({len(panel)} subjects)")
    print("the executing agent never edits the frozen file; D4 scores it")


def score_blind(series: str) -> None:
    """GPU in-process: score the frozen blind set (the oos-score judge path)."""
    import os
    device = os.environ.get("CENSUS_DEVICE", "cuda")
    os.environ.setdefault("SCRIPTENGINE_DEVICE", device)
    from scriptengine.config import series_paths
    from scriptengine.api.context import build_context
    from scriptengine.eval.span_recall import served_text
    from tools.census_dimensions import judge

    p = _frozen_path(series)
    if not p.exists():
        sys.exit(f"no frozen blind set at {p} — run `validate` first")
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    paths = series_paths(series)
    results: list[dict] = []
    errors = 0
    out_path = _scored_path(series)
    for i, row in enumerate(rows, 1):
        try:
            bundle = build_context(paths, row["q"], mode="qa",
                                   subject=None)
            rec = judge(row, served_text(bundle))
            rec["error"] = None
        except Exception as e:  # an ERROR row is recorded, never a crash
            rec = {k: row[k] for k in ("id", "class", "subject", "q", "expect")}
            rec.update({"hits": [], "missing": list(row["expect"]),
                        "verdict": "ERROR",
                        "error": f"{type(e).__name__}: {e}", "served": ""})
            errors += 1
        rec["set"] = row.get("set", "blind")
        rec["device"] = device
        results.append(rec)
        if i % 6 == 0 or i == len(rows):
            out_path.write_text("".join(
                json.dumps(r, ensure_ascii=False) + "\n" for r in results))
            verdicts = Counter(r["verdict"] for r in results)
            print(f"[{i}/{len(rows)}] verdicts={dict(verdicts)} "
                  f"errors={errors}", flush=True)
    out_path.write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in results))
    green = sum(1 for r in results if r["verdict"] == "MECH_GREEN")
    print(json.dumps({"rows": len(results), "MECH_GREEN": green,
                      "errors": errors,
                      "green_rate": round(green / max(len(results), 1), 3),
                      "per_class": {
                          c: [r["verdict"] for r in results
                              if r["class"] == c]
                          for c in sorted({r["class"] for r in results})}
                      }, indent=2))
    print(f"blind-score {series} -> {out_path.relative_to(ROOT)}")
    if errors >= 0.1 * len(results):
        sys.exit(3)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd")
    for name in ("panel", "validate", "score"):
        sp = sub.add_parser(name)
        sp.add_argument("--series", default="marvel")
    sub.choices["validate"].add_argument("--draft", required=True)
    args = ap.parse_args()
    cmd = args.cmd or "panel"
    if cmd == "panel":
        out = _panel_path(args.series)
        result = build_panel(args.series)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w") as fh:
            for row in result["panel"]:
                fh.write(json.dumps(row, sort_keys=True) + "\n")
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        print(f"sealed panel -> {out} ({len(result['panel'])} subjects)")
        print(f"  classes: {result['class_counts']}")
        print(f"  disjoint from scored arms: census "
              f"{result['disjoint_from']['census']} + OOS "
              f"{result['disjoint_from']['oos']} draws (seed {SEED}); "
              f"{result['disjoint_from']['scored_subjects']} scored subjects")
        print(f"  panel sha256: {digest}")
        print("seal block for the protocol doc:")
        print(f"  {out.name} sha256 {digest} · seed {SEED} · bank meta "
              f"sweep_complete true "
              f"({result['meta'].get('sweep_pages')}/{result['meta'].get('tier_total')})")
    elif cmd == "validate":
        validate_draft(args.series, Path(args.draft))
    else:
        score_blind(args.series)


if __name__ == "__main__":
    main()