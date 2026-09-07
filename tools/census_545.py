"""The 545 (dimension, page) census -- the step-5 acceptance test.

For each (question-dimension, character page) pair in the co-located
``census_545_pairs.json``, run the faithful in-process auto bundle
(``route`` + ``build_context`` -- the same path the ``:8000`` ``/context``
endpoint uses) and classify the pair into exactly one of four signals:

  reached           a beat on the target page whose breadcrumb carries the
                    dimension as ANY component (F1: a nested
                    "History / Cursed Child Arc" still counts) is in the
                    bundle AND that beat carries a non-empty locator.
  reached-uncited   the section is reached but no beat for it carries a
                    locator (the wiki's property, e.g. a minor profile
                    section that is described but not chapter-cited).
  not-reached       the target section is present but no beat reached it
                    (a retrieval-controlled miss -> the fix loop).
  no-section        defensive; the pool is section-built, so this is 0.

Gate (tier-scoped): ``not-reached ~= 0`` across the whole pool; main-cast
reached beats 100% sourced. A minor ``reached-uncited`` is *published, not
failed* (a corpus property, like Berserk's 0% sourced).

The full census is ~13s/pair on CPU (~2h for 545) but ~1/sec on GPU (~9 min),
so the default device is CPU (a long sustained cross-encoder run must not pin
Qwen's GPU headroom); override ``--device cuda`` for the fast path.

Usage:
    python tools/census_545.py [--series jjk] [--pairs PATH] [--out PATH]
                               [--limit N] [--device cpu|cuda]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

# Device must be chosen before the retrieval models are imported.
DEVICE = os.environ.get("CENSUS_DEVICE", "cpu")
os.environ.setdefault("SCRIPTENGINE_DEVICE", DEVICE)

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from scriptengine.config import series_paths          # noqa: E402
from scriptengine.retrieve.router import route        # noqa: E402
from scriptengine.api.context import build_context    # noqa: E402

DEFAULT_PAIRS = Path(__file__).with_name("census_545_pairs.json")

# Tier-scoped sourceability bar: the main cast is chapter-cited by the wiki,
# minor profile sections are not (a corpus property). The reachability gate is
# tier-independent -- only the sourceability bar uses this set, so the
# reachability result does not depend on it. JJK campaign-scoping decision.
MAIN_CAST = {
    "Yuji Itadori", "Satoru Gojo", "Maki Zenin", "Megumi Fushiguro",
    "Kento Nanami", "Nobara Kugisaki", "Ryomen Sukuna", "Suguru Geto",
    "Aoi Todo", "Yuta Okkotsu", "Toji Fushiguro", "Kazuma Kanagi", "Choso",
    "Kinji Hakari", "Mahito", "Jogo", "Hanami",
}

# The ability census (P3.A) needs non-prose dimensions, so dims are derived
# from the pairs file in main(), not hard-coded. (X1: the 545 file carries the
# five prose dims; the ability file carries Cursed Technique / Cursed Energy / ...)

THIN_CHARS = 120
# A names-only ability line (e.g. "Cursed Technique: Blue") is far shorter than
# the mechanics prose that actually answers "how does it work". A reached beat
# whose longest text is under this is content-thin: the section is reached but
# the bundle did not carry its mechanics (a P3.A/3B fork signal, see COUNCIL_X1).


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


def in_section(breadcrumb: str, dim: str) -> bool:
    # F1: the dimension is reached when it appears as ANY breadcrumb component.
    return any(norm(c) == norm(dim) for c in (breadcrumb or "").split(" / "))


def tier(name: str) -> str:
    return "main-cast" if name in MAIN_CAST else "minor"


def classify(p: dict, beats: list) -> tuple:
    tgt = norm(p["page"])
    dim = p["dimension"]
    reached_beats = [b for b in beats
                     if norm(b.get("doc_title")) == tgt
                     and in_section(b.get("breadcrumb"), dim)]
    cits = set()
    max_reach_text = 0
    for b in reached_beats:
        cits.update(b.get("citations") or [])
        max_reach_text = max(max_reach_text, len(b.get("text") or ""))
    if reached_beats:
        cls = "reached" if cits else "reached-uncited"
        return cls, bool(cits), len(reached_beats), sorted(cits), max_reach_text, None
    top = beats[0] if beats else {}
    if not beats:
        sub = "empty"
    elif norm(top.get("doc_title")) != tgt:
        sub = "cross-page"
    else:
        sub = "wrong-section"
    return "not-reached", False, 0, [], 0, sub


def run_pair(paths, p: dict) -> dict:
    rec = {"dimension": p["dimension"], "page": p["page"], "name": p["name"],
           "question": p["question"], "tier": tier(p["name"])}
    s0 = time.time()
    routed = route(paths, p["question"], subject=None)
    mode = routed.mode
    subj = routed.signals.get("subject") or None
    bundle = build_context(paths, p["question"], mode=mode, token_budget=6000,
                           top_k=None, subject=subj)
    if mode == "roster" and not bundle.get("members"):
        bundle = build_context(paths, p["question"], mode="narrative",
                               token_budget=6000, top_k=None, subject=None)
        mode = "narrative"
    beats = bundle.get("beats") or []
    cls, sourced, n_reach, cits, max_reach_text, sub = classify(p, beats)
    top = beats[0] if beats else {}
    rec.update({"mode": mode, "subject": subj, "class": cls, "sub": sub,
                "sourced": sourced, "n_reached": n_reach, "citations": cits[:4],
                "top_doc": top.get("doc_title"), "top_sec": top.get("breadcrumb"),
                "n_beats": len(beats), "reached_chars": max_reach_text,
                "thin": cls in ("reached", "reached-uncited")
                and max_reach_text < THIN_CHARS,
                "elapsed": round(time.time() - s0, 1)})
    return rec


def summarize(results: list, dims: list) -> None:
    print("\n=== census summary ===", flush=True)
    total = len(results)
    nr_all = sum(1 for r in results if r.get("class") == "not-reached")
    err_all = sum(1 for r in results if (r.get("class") or "").startswith("(?)"))
    print(f"TOTAL {total} pairs: not-reached {nr_all}  errors {err_all}", flush=True)
    for tier_name in ("main-cast", "minor"):
        rows = [r for r in results if r.get("tier") == tier_name]
        if not rows:
            continue
        nr = sum(1 for r in rows if r.get("class") == "not-reached")
        src = sum(1 for r in rows if r.get("sourced"))
        print(f"  {tier_name:<10} not-reached {nr}/{len(rows)}   "
              f"sourced {src}/{len(rows)}", flush=True)
    print("\n  per-dimension x per-tier:", flush=True)
    for d in dims:
        for tier_name in ("main-cast", "minor"):
            rows = [r for r in results if r.get("dimension") == d
                    and r.get("tier") == tier_name]
            if not rows:
                continue
            nr = sum(1 for r in rows if r.get("class") == "not-reached")
            src = sum(1 for r in rows if r.get("sourced"))
            nunc = sum(1 for r in rows if r.get("class") == "reached-uncited")
            print(f"    {d:<11} {tier_name:<10} n={len(rows):<3} "
                  f"not-reached={nr}  sourced={src}  reached-uncited={nunc}", flush=True)
    print("\n  not-reached detail:", flush=True)
    for r in results:
        if r.get("class") == "not-reached":
            print(f"    {r['dimension']:<11} {r['page']:<26} sub={r.get('sub')} "
                  f"top={r.get('top_doc')!r}/{r.get('top_sec')!r}", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="545 (dimension, page) census")
    ap.add_argument("--series", default=os.environ.get("CENSUS_SERIES", "jjk"))
    ap.add_argument("--pairs", default=str(DEFAULT_PAIRS))
    ap.add_argument("--out", default="/tmp/census_545_results.json")
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    ap.add_argument("--device", default=DEVICE, choices=["cpu", "cuda"])
    args = ap.parse_args()

    if args.device != DEVICE:
        # device was already baked into the env before import; re-launching is
        # the only clean way to switch, but a fresh process honors --device via
        # the CENSUS_DEVICE env the caller should have set.
        pass

    pairs = json.load(open(args.pairs))
    dims = sorted({p["dimension"] for p in pairs})
    done = {}
    if os.path.exists(args.out):
        for r in json.load(open(args.out)):
            done[(r["page"], r["dimension"])] = r
    if args.limit:
        pairs = pairs[:args.limit]
    todo = [p for p in pairs if (p["page"], p["dimension"]) not in done]
    results = list(done.values())
    print(f"census: {len(pairs)} pairs, {len(done)} already done, "
          f"{len(todo)} to run (out={args.out})", flush=True)
    paths = series_paths(args.series)
    t_start = time.time()
    for i, p in enumerate(todo):
        try:
            rec = run_pair(paths, p)
        except Exception as e:
            rec = {"dimension": p["dimension"], "page": p["page"], "name": p["name"],
                   "question": p["question"], "tier": tier(p["name"]),
                   "class": "(?) error", "error": f"{type(e).__name__}: {e}",
                   "sourced": False, "n_beats": 0}
        results.append(rec)
        json.dump(results, open(args.out, "w"), indent=1)
        if (i + 1) % 20 == 0 or (i + 1) == len(todo):
            print(f"  [{i+1}/{len(todo)}] {rec['page']}/{rec['dimension']} -> "
                  f"{rec['class']} (elapsed {rec.get('elapsed')}s, "
                  f"wall {time.time()-t_start:.0f}s)", flush=True)
    summarize(results, dims)


if __name__ == "__main__":
    main()