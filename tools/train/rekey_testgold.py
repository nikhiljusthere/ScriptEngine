#!/usr/bin/env python3
"""Re-key the blind TEST gold (recall_gold_v3) onto the gen-2 sentence
grid and rebuild the drift probes (windowing-100 WP3, 2026-10-04).

The v4 test gold's W<n> entries carry [subject, verb, object] triples for
the 4,000-char slices of windows_100.json, and WP1's content-addressed
ids made those slices' old window ids dead. Each entry maps onto the
current grid the way rekey_gold.py maps a record: its passage (from
windows_100.json by index) located on the section's (or lead's) grid,
and the windows whose sentence spans INTERSECT it (the slice's read
span, not a containment of the whole passage -- on the gen-2 grid
69/100 passages span several windows) take the entry's events over.

The events carry no quote (they were listed blind for the whole old
slice), so an event's anchor in a window is a mention of its subject or
object in the window's READ part -- the overlap of the window's
sentence span and the passage's span: a window can extend past the
slice (windows_100.json is not a full tiling: 10 sections carry one
4,000-char slice of a longer section), and the slice was the only text
the blind annotator read, so a mention in the window's unread tail
never anchors. The mention test is the scorer's own name rule
(tools/eval_extraction.py): any 3+ letter word of the name (STOP set
removed), folded; a full name span in the overlap implies its tokens
are in it, so this single rule is the union of a name-span and a token
stage. An event no window anchors is dropped and reported (expected 0:
an in-passage name always lands in some intersecting window).

A FULLY-READ window (its span inside the passage's span) no event maps
to is a GENUINE empty: the passage was annotated blind, so the events
it did list are anchored elsewhere, and the window really has none
(unlike gold600's contaminated empties, whose carry text was never
read -- those are the `reread` status). Keep it as an empty entry. A
window that intersects the passage but extends past its edge is flagged
`partial`: its remaining text was never read, so its emptiness is not
earned and it never supplies an empty probe. Flag an entry `straddle`
when an event anchors in two of the windows (multi-window coverage of
the passage itself is not flagged -- it is the norm, not a defect).

Output: recall_gold_v3/gold_test_v4.gen2.json -- the old per-entry shape
(core/optional triples), keyed by the gen-2 window id instead of W<n>
(one entry per intersecting window), plus the per-window passage, the
straddle and partial flags, and the source W index. The hand-annotated v4 source
stays put (like gold600.jsonl, the old-grid annotations are the source
of truth; only the DERIVED gen-2 file is written new), and
windows_100.json stays put too -- emit_windows.holdout_pages unions
its pages. NOTE: tools/eval_extraction.py load_gold still reads the
W-indexed v4 shape (and sorted-name-wise picks it OVER the gen-2
file); the scorer switch to the gen-2 file is a later WP's job, not
this re-key's.

With --probes, also rebuild the drift probes (opencode/golden_probes.
jsonl, old file -> .pre-wp3b): 24 lines, pool shape plus `expected`.
The 20 POSITIVE lines come from gold600.gen2 + the pilot gen2 records
with status `kept` or `reexpressed` (never `reread` -- the contaminated
empties, the 35B re-read owns them), each carrying 1-4 rows, picked to
cover every verb at least once and preferring the hard distinctions
(killed vs defeated, captured vs sealed, met vs fought, arrived vs
departed, passive voice), none on a holdout page. The 4 EARNED EMPTIES
are covering windows of reexpressed records that carry no event: the
adjudicator listed every event of the whole old passage, so a new
window that sits fully inside that annotated span and got no row is a
genuine empty (unlike gold600's reread empties, whose old windows were
contaminated). NEVER from the test gold: the labeler must stay blind to
the student's test set, so no test-gold window may appear in a probe.
"""
import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from scriptengine.ingest.windows import (  # noqa: E402
    CURRENT_GEN,
    build_windows,
    quote_grid_span,
    sentence_spans,
)
from scriptengine.ingest.verbatim import fold  # noqa: E402
from scriptengine.stores.facts import FactStore  # noqa: E402

from emit_windows import build_universe_windows, holdout_pages, universe  # noqa: E402,F401
from rekey_gold import grid_texts_for, passage_of  # noqa: E402

# The scorer's own name rule (tools/eval_extraction.py): an event the
# scorer could match is the one we attribute -- its tokens are the 3+
# letter words of the name, minus the stop set.
STOP = {"the", "and", "of", "no"}

# WP3b-1 (2026-10-04): the hard verb distinctions the probe stratify
# prefers -- pairs the student confuses (killed vs defeated: did the
# fight END; captured vs sealed: a person vs a containment; met vs
# fought: a stated encounter vs a clash; arrived vs departed: the
# place reached vs the one left).
HARD_PAIRS = {frozenset(p) for p in (
    ("killed", "defeated"), ("captured", "sealed"),
    ("met", "fought"), ("arrived", "departed"))}


def name_tokens(name):
    return {w for w in re.findall(r"[a-z0-9'-]+", (name or "").lower())
            if len(w) >= 3 and w not in STOP}


def map_event(text, spans, ps, pe, covering, ev):
    """The intersecting windows an event maps to, mechanically.

    A hit is a mention of the subject or object in the window's READ
    part -- the overlap of the window's sentence span and the passage's
    span (ps:pe). The overlap, not the window's whole text: a window
    can extend past the slice, and the slice was the only text the
    blind annotator read. The mention test is the scorer's own name
    rule (tools/eval_extraction.py): any 3+ letter word of the name
    (STOP set removed), folded; a full name span in the overlap implies
    its tokens are in it, so this single rule is the union of a
    name-span and a token stage. Returns the hit windows: [] = no
    anchor (dropped, reported -- expected 0), 2+ = the event anchors in
    two siblings (a straddle)."""
    subject = str(ev[0]).strip() if len(ev) > 0 and ev[0] else ""
    object = str(ev[2]).strip() if len(ev) > 2 and ev[2] else ""
    toks = name_tokens(subject) | name_tokens(object)
    if not toks:
        return []
    hits = []
    for w in covering:
        lo, hi = max(w.s_start, ps), min(w.s_end, pe)
        overlap = text[spans[lo][0] : spans[hi][1]]
        if any(t in fold(overlap).lower() for t in toks):
            hits.append(w)
    return hits


def rekey_testgold(store, gold_path, windows_path, out_path, report_path,
                   dry_run):
    gold = json.loads(gold_path.read_text(encoding="utf-8"))
    wins = json.loads(windows_path.read_text(encoding="utf-8"))
    entries = {int(k[1:]): gold[k]
               for k in gold if k.startswith("W") and k[1:].isdigit()}
    if len(entries) != len(wins):
        sys.exit(f"W-index indirection broken: {len(entries)} W entries "
                 f"vs {len(wins)} windows ({gold_path.name} x "
                 f"{windows_path.name})")

    grids = {}

    def grids_for(page, label, text):
        key = (page, label, text)
        if key not in grids:
            # The section's own window grid AND its sentence spans: the
            # overlap text below slices the raw section by span offsets.
            grids[key] = (build_windows(page, label, text, gen=CURRENT_GEN),
                          sentence_spans(text))
        return grids[key]

    out = {}
    # Pre-seeded so the receipt names every counter even at zero (the
    # plan's "kept vs dropped (expected 0 dropped)" must be readable).
    tally = Counter({
        "multi_window_entries": 0, "unmapped_entries": 0, "shared_ids": 0,
        "core_kept": 0, "core_dropped": 0,
        "optional_kept": 0, "optional_dropped": 0,
        "straddled_events": 0, "partial_window_entries": 0,
        "empty_entries": 0, "genuine_empties": 0,
    })
    dropped = []
    for n in sorted(entries):
        wrec = wins[n]
        page = (wrec.get("page") or "").strip()
        label = (wrec.get("section") or "").strip() or "lead"
        passage = (wrec.get("passage") or "").strip()
        evs = entries[n]
        evs_all = (evs.get("core") or []) + (evs.get("optional") or [])

        # Which grid text the passage was cut from (a same-titled section
        # can carry it too): the one whose windows anchor the most
        # events -- rekey_gold's rule for the ambiguous case. Intersecting
        # (not containing) windows: the slice was what was read, and on
        # the gen-2 grid a slice spans several windows.
        best = None
        for text in grid_texts_for(store, wrec):
            wins_g, spans = grids_for(page, label, text)
            span = quote_grid_span(text, passage)
            if span is None or not spans:
                continue
            ps, pe = span
            covering = [w for w in wins_g
                        if w.s_start <= pe and w.s_end >= ps]
            if not covering:
                continue
            anchored = sum(1 for ev in evs_all
                           if map_event(text, spans, ps, pe, covering, ev))
            if best is None or anchored > best[0]:
                best = (anchored, text, spans, covering, ps, pe)
        if best is None:
            tally["unmapped_entries"] += 1
            dropped.append({"w": n, "page": page, "section": label,
                            "why": "passage not in the store's texts"})
            continue
        _anch, text, spans, covering, ps, pe = best

        if len(covering) > 1:
            tally["multi_window_entries"] += 1
        buckets = {kind: {w.id: [] for w in covering} for kind in
                   ("core", "optional")}
        ambiguous = set()
        for kind in ("core", "optional"):
            for ev in evs.get(kind) or []:
                hits = map_event(text, spans, ps, pe, covering, ev)
                if not hits:
                    tally[f"{kind}_dropped"] += 1
                    dropped.append({"w": n, "page": page, "kind": kind,
                                    "event": ev})
                    continue
                tally[f"{kind}_kept"] += 1
                if len(hits) > 1:
                    tally["straddled_events"] += 1
                    ambiguous.update(w.id for w in hits)
                for w in hits:
                    buckets[kind][w.id].append(ev)

        for w in covering:
            core = buckets["core"][w.id]
            opt = buckets["optional"][w.id]
            # A window that extends past the read slice (its span
            # outlives the passage's) is partial: the part beyond the
            # slice was never read, so an empty entry there is not an
            # earned empty.
            partial = not (ps <= w.s_start and w.s_end <= pe)
            prev = out.get(w.id)
            if prev is None:
                out[w.id] = {
                    "core": core,
                    "optional": opt,
                    "passage": w.text,
                    "straddle": w.id in ambiguous,
                    "partial": partial,
                    "w": n,
                }
            else:
                # Two consecutive slices' 300-char carries can share a
                # window: both annotations are gold on that text, so
                # union the events (deduped), never let one overwrite.
                # OR the flags: never claim an earned empty where one of
                # the two annotations left an unread part (conservative
                # direction: sharing only shrinks the earned-empty set,
                # never grows it).
                prev["core"] += [e for e in core if e not in prev["core"]]
                prev["optional"] += [e for e in opt if e not in prev["optional"]]
                prev["straddle"] = prev["straddle"] or w.id in ambiguous
                prev["partial"] = prev["partial"] or partial
                tally["shared_ids"] += 1

    n_empty = sum(1 for v in out.values() if not v["core"] and not v["optional"])
    tally["empty_entries"] = n_empty
    tally["genuine_empties"] = sum(
        1 for v in out.values()
        if not v["core"] and not v["optional"] and not v["partial"])
    tally["partial_window_entries"] = sum(
        1 for v in out.values() if v["partial"])
    receipt = {
        "gold": str(gold_path), "windows": str(windows_path),
        "out": str(out_path), "gen": CURRENT_GEN,
        "entries_in": len(entries), "entries_out": len(out),
        **dict(tally),
        "dropped_events": sum(1 for d in dropped if "event" in d),
        "note": ("kept counts are events, not event-window pairs; an "
                 "event anchored in two siblings counts once; events "
                 "anchor by the scorer's token rule in the window's "
                 "READ part (span ∩ passage span); genuine_empties = "
                 "empty AND fully-read (probe-eligible earned empties), "
                 "partial empties are never earned; shared_ids counts "
                 "windows claimed by two sibling entries (unioned)"),
    }

    data = {
        "version": gold.get("version"),
        "gen": CURRENT_GEN,
        "guideline": gold.get("guideline"),
        "note": gold.get("note"),
        "note_gen2": ("gen-2 rekey (2026-10-04, tools/train/rekey_testgold"
                      ".py): entries keyed by gen-2 window id, one per "
                      "intersecting window (the 4,000-char slice was what "
                      "was read; the windows whose spans intersect it take "
                      "its events); events anchor by the scorer's 3+ "
                      "letter token rule in the window's READ part only "
                      "(a window's unread tail never anchors); `partial` = "
                      "the window extends past the read slice, so its "
                      "empty is not earned; `straddle` = an event anchors "
                      "in two windows; the old-grid v4 source stays put "
                      "(annotations are the source of truth) -- this file "
                      "is the derived re-key"),
        **out,
    }

    if not dry_run:
        out_path.write_text(json.dumps(data, indent=1, ensure_ascii=False)
                            + "\n", encoding="utf-8")
        if report_path:
            report_path.write_text(
                json.dumps({"receipt": receipt, "dropped": dropped},
                           indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
    print(json.dumps(receipt, indent=2, ensure_ascii=False))
    if tally["unmapped_entries"]:
        sys.exit(f"{tally['unmapped_entries']} entries unmapped (store "
                 f"drift): {json.dumps(dropped, ensure_ascii=False)[:500]}")
    return out


def build_probes(store, paths_root, gold600_path, pilot_path, gold600_src,
                 pilot_src, gold600_report, pilot_report, test, probes_path,
                 dry_run):
    """The 24 drift probes (WP3b-1, 2026-10-04): pool shape + `expected`.
    paths_root is the SERIES root (series/<s>): holdout_pages resolves
    training/v1/* and training/recall_gold_v3/* under it (the repo root
    finds neither and the holdout gate would pass vacuously).

    20 POSITIVE lines from gold600.gen2 + the pilot gen2 records with
    status kept/reexpressed (never reread -- the contaminated empties,
    the 35B re-read owns them), each carrying 1-4 rows, none on a
    holdout page, picked by greedy set-cover over the verbs with the
    tie-breaks the planner asked for: the hard distinctions (HARD_PAIRS)
    first, then passive renderings of the line's own verbs, then the
    shorter line. 4 EARNED EMPTIES: covering windows of reexpressed
    records that carry no event -- the adjudicator listed every event of
    the whole old passage, so a new window that sits fully inside that
    annotated span and got no row is a genuine empty. Derived from the
    ORIGINAL records (a gen-2 user message carries the new window text,
    not the old passage) via the report's per-old-record status +
    new_ids, and never from the test gold (the labeler must stay blind
    to the student's test set), never from a window any gen-2 record
    claims under any status, never on a holdout page."""
    holdout = holdout_pages(paths_root)
    uni = universe(store)
    windows, _, _ = build_universe_windows(store, uni)
    by_id = {w.id: w for w in windows}

    # The test gold's window ids: a probe on one of them would un-blind
    # the labeler to the student's scoreboard (WP3b-1 ruling).
    test_ids = set(test)

    def verbs_of(evs):
        return {(e.get("verb") or "").lower() for e in evs}

    def passive_hits(passage, evs):
        # A passive rendering of one of the line's own verbs inside its
        # passage ("Vos was knocked out by Kade" carries `defeated`):
        # the hard case the stratify prefers (WP3b-1).
        n = 0
        for e in evs:
            v = (e.get("verb") or "").lower()
            if v and re.search(rf"\b(?:was|were|is|are|been)\s+"
                               rf"{re.escape(v)}\b", fold(passage)):
                n += 1
        return n

    def pair_bonus(verbs):
        return sum(1 for p in HARD_PAIRS if p <= verbs)

    cands = []
    for path in (gold600_path, pilot_path):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            if rec["rekey"]["status"] not in ("kept", "reexpressed"):
                continue  # reread = contaminated empty, 35B re-read owns it
            events = json.loads(rec["messages"][2]["content"]).get("events") or []
            if not (1 <= len(events) <= 4):
                continue  # WP3b-1: probe lines carry 1-4 rows
            if rec["page"] in holdout or rec["id"] in test_ids:
                continue  # no holdout page, no test-gold window (blind)
            cands.append({"id": rec["id"], "page": rec["page"],
                          "section": rec["section"], "events": events})
    for c in cands:
        c["verbs"] = verbs_of(c["events"])
        c["passage"] = by_id[c["id"]].text  # == the record's user passage
    target = set().union(*(c["verbs"] for c in cands)) if cands else set()

    chosen, used = [], set()
    covered = set()
    # Greedy set-cover over the verbs, up to 20 picks; the key IS the
    # preference: most newly-covered verbs, then hard-pair coverage,
    # then passive renderings, then the shorter line, then the id
    # (deterministic).
    while len(chosen) < 20 and covered < target:
        best, best_key = None, None
        for c in cands:
            if c["id"] in used:
                continue
            newv = c["verbs"] - covered
            if not newv:
                continue
            key = (len(newv), pair_bonus(c["verbs"]),
                   passive_hits(c["passage"], c["events"]),
                   -len(c["events"]), c["id"])
            if best_key is None or key > best_key:
                best, best_key = c, key
        if best is None:
            break
        chosen.append(best)
        used.add(best["id"])
        covered |= best["verbs"]
    if len(chosen) < 20:  # under budget after full coverage: richest lines
        rest = [c for c in cands if c["id"] not in used]
        rest.sort(key=lambda c: (len(c["verbs"]), pair_bonus(c["verbs"]),
                                 passive_hits(c["passage"], c["events"]),
                                 -len(c["events"]), c["id"]), reverse=True)
        chosen.extend(rest[:20 - len(chosen)])

    def empty_candidates(src, report_path):
        """The new windows fully inside a reexpressed record's annotated
        old passage that got no row of that record (its earned empties)."""
        orig = {json.loads(l)["id"]: json.loads(l)
                for l in Path(src).read_text(encoding="utf-8").splitlines()
                if l.strip()}
        grids = {}
        out = set()
        for rec in json.loads(
                Path(report_path).read_text(encoding="utf-8"))["records"]:
            if rec["status"] != "reexpressed":
                continue
            o = orig.get(rec["old_id"])
            if o is None:
                continue
            page = (o.get("page") or "").strip()
            label = (o.get("section") or "").strip() or "lead"
            passage = passage_of(o)
            for text in grid_texts_for(store, o):
                key = (page, label, text)
                if key not in grids:
                    grids[key] = build_windows(page, label, text,
                                               gen=CURRENT_GEN)
                span = quote_grid_span(text, passage)
                if span is None:
                    continue
                ps, pe = span
                with_rows = set(rec["new_ids"])
                for w in grids[key]:
                    # Fully inside the annotated span: the window's whole
                    # text was read and listed. A window that extends
                    # past the passage (WP3.2's `partial`) has an unread
                    # tail -- its empty is not earned.
                    if ps <= w.s_start and w.s_end <= pe and w.id not in with_rows:
                        out.add(w.id)
        return out

    # A candidate the gold files already claim (any status, either file)
    # carries rows of SOME record -- it is not an event-free window.
    claimed = set()
    for path in (gold600_path, pilot_path):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                claimed.add(json.loads(line)["rekey"]["new_id"])
    cands_empty = (empty_candidates(gold600_src, gold600_report) |
                   empty_candidates(pilot_src, pilot_report))
    # A window on a holdout page is out too (split by page, never by row).
    empties = sorted(cands_empty - claimed - test_ids
                     - {i for i in cands_empty
                        if i in by_id and by_id[i].page in holdout})
    by_page = {}
    for i in empties:
        by_page.setdefault(by_id[i].page, []).append(i)
    empty_chosen, pages = [], sorted(by_page)
    # Page-diverse four: round-robin over id-sorted pages (one per page
    # per round) -- four windows on four pages beat four on one for
    # drift coverage.
    while len(empty_chosen) < 4 and any(by_page[p] for p in pages):
        for p in pages:
            if by_page[p] and len(empty_chosen) < 4:
                empty_chosen.append(by_page[p].pop(0))

    lines = []
    for i, c in enumerate(chosen + [{"id": k, "page": None, "section": None,
                                     "events": []} for k in empty_chosen]):
        w = by_id.get(c["id"])
        if w is None:
            sys.exit(f"probe id {c['id']} is not a builder id")
        lines.append({
            "n": i, "id": c["id"], "page": w.page,
            "section": "" if w.section == "lead" else w.section,
            "passage": w.text, "gen": w.gen, "sub": w.sub,
            "expected": c["events"],
        })

    # The WP2-style gate: the probe set is what it claims to be.
    n_empty = sum(1 for r in lines if not r["expected"])
    pos = [r for r in lines if r["expected"]]
    all_v = set()
    for r in lines:
        all_v.update((e.get("verb") or "").lower() for e in r["expected"])
    probe_ids = [r["id"] for r in lines]
    checks = [
        (len(lines) == 24, "24 probes (20 positive + 4 earned empties)"),
        (len(pos) == 20, "20 positive probes"),
        (n_empty == 4, "4 earned empties"),
        (all(1 <= len(r["expected"]) <= 4 for r in pos),
         "positive lines carry 1-4 rows"),
        (all_v == target, f"all {len(target)} verbs covered"),
        (len(set(probe_ids)) == len(probe_ids), "probe ids unique"),
        (not set(probe_ids) & test_ids, "no test-gold window in the probes"),
        (not {r["page"] for r in lines} & holdout, "no probe page in holdout"),
    ]
    bad = [msg for ok, msg in checks if not ok]
    if bad:
        sys.exit("probe gate FAILED: " + "; ".join(bad))

    if not dry_run:
        old = probes_path.with_name(probes_path.name + ".pre-wp3b")
        if probes_path.exists() and not old.exists():
            probes_path.rename(old)  # supersede, don't salvage (WP3b-1)
        probes_path.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines),
            encoding="utf-8",
        )
    hist = Counter()
    for r in lines:
        for e in r["expected"]:
            hist[(e.get("verb") or "").lower()] += 1
    print(json.dumps({
        "probes": len(lines), "empty_probes": n_empty,
        "verbs": sorted(all_v), "verb_histogram": dict(hist),
        "out": str(probes_path),
    }, indent=2, ensure_ascii=False))
    return lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--series", default="jjk")
    ap.add_argument("--gold",
                    default="series/jjk/training/recall_gold_v3/gold_test_v4.json")
    ap.add_argument("--windows",
                    default="series/jjk/training/recall_gold_v3/windows_100.json")
    ap.add_argument("--out",
                    default="series/jjk/training/recall_gold_v3/gold_test_v4.gen2.json")
    ap.add_argument("--report", default=None)
    ap.add_argument("--probes", action="store_true",
                    help="also rebuild the 24 drift probes (20 positive + "
                         "4 earned empties, WP3b-1)")
    ap.add_argument("--gold600",
                    default="series/jjk/training/gold600/gold600.gen2.jsonl")
    ap.add_argument("--pilot",
                    default="series/jjk/training/gold/gold_pilot_all.gen2.jsonl")
    ap.add_argument("--gold600-src",
                    default="series/jjk/training/gold600/gold600.jsonl")
    ap.add_argument("--pilot-src",
                    default="series/jjk/training/gold/gold_pilot_all.jsonl")
    ap.add_argument("--gold600-report",
                    default="series/jjk/training/gold600/gold600.gen2.report.json")
    ap.add_argument("--pilot-report",
                    default="series/jjk/training/gold/gold_pilot_all.gen2.report.json")
    ap.add_argument("--probes-out",
                    default="series/jjk/training/opencode/golden_probes.jsonl")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    db = ROOT / "series" / a.series / "facts.db"
    if not db.exists():
        sys.exit(f"{a.series} is not indexed (no {db}); run `index` first")
    with FactStore(db) as store:
        test = rekey_testgold(
            store, Path(a.gold), Path(a.windows), Path(a.out),
            Path(a.report) if a.report else None, a.dry_run)
        if a.probes:
            # paths_root is the SERIES root: holdout_pages resolves
            # training/v1/* and training/recall_gold_v3/* under it (the
            # repo root would find neither and the holdout gate would
            # pass vacuously). The -src/-report pairs are the ORIGINAL
            # records + per-record rekey report: the earned empties are
            # the reexpressed records' event-free sub-windows, and only
            # the originals carry the old passage.
            build_probes(store, ROOT / "series" / a.series, Path(a.gold600),
                         Path(a.pilot), Path(a.gold600_src), Path(a.pilot_src),
                         Path(a.gold600_report), Path(a.pilot_report),
                         test, Path(a.probes_out), a.dry_run)


if __name__ == "__main__":
    sys.exit(main())