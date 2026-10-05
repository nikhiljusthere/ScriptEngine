"""Score an event extractor's per-window output against the hand-annotated
recall gold. Offline, zero-LLM.

    python tools/eval_extraction.py --series jjk --pred PRED.jsonl
    python tools/eval_extraction.py --series jjk --legacy-v4 --pred PRED.jsonl
    python tools/eval_extraction.py --series hxh \
        --gold series/hxh/training/testpool/hxh_test.jsonl --pred PRED.jsonl

PRED.jsonl: one {"id": <window id>, "events": [...]} per line, the shape
tools/train/infer.py writes ({... "raw": <the model's answer text>}
optional -- the raw text is what the JSON-validity rate is measured on).

Three gold shapes (load_gold auto-detects the file's; --legacy-v4 forces
the oldest one from the gold dir):

* PASSAGE units (the gen-2 re-keyed test gold, gold_test_v4.gen2.json,
  `shape: "passage"`): one entry per annotated passage (the old 4,000-
  char slice the blind annotator read), its core + optional triples
  unchanged, and the ordered gen-2 windows covering the passage, each
  with its read span (char offsets inside the passage; `partial` = the
  window extends past the slice). The student is run on EVERY covering
  window; its predictions are UNIONED, a prediction whose quote is not
  inside the passage slice is DISCARDED (the text beyond the slice was
  never annotated), duplicates (same subject, verb, object) are
  collapsed, and the result is matched to the unit's gold with the name
  rule below.
* WINDOW records (the per-wiki labeled test pools, JSONL -- the future
  pools' shape): one record per window, the gold events carry their
  `quote`; a prediction matches a gold event only while it also sits at
  the same place -- the two quotes' character spans in the window text
  must overlap (the plan's event match: (subject, verb, object) with the
  quote overlapping the gold quote).
* LEGACY (the old W-indexed v4 shape, behind --legacy-v4): one entry per
  old-grid window id, triples without quotes, the original per-window
  scoring (kept so the pre-gen-2 numbers stay reproducible).

Recall is on the gold's core events; a predicted event that matches
neither a core nor an optional gold event counts against precision.
Names match when they share a word of three letters or more (the model
writes "Yuji", the gold "Yuji Itadori"), or one word is a 4+-letter
prefix of the other ("Maru", "Marulu"); `fought` and `met` are
symmetric, every other verb is directional. One gold event is matched
at most once; a duplicate of an already-matched event is neither a hit
nor an error.

Report (one JSON line): the wiki's P/R/F1 (per-wiki: run once per
series), per-verb P/R/F1, the verb confusion matrix (each FP's predicted
verb vs the gold verb of the event its names matched; fought vs
defeated first), the JSON-validity rate of the model's raw answers, and
the quote-verbatim rate (a predicted event's quote located verbatim in
the window text it came from -- the engine's own verbatim predicate).
"""
from __future__ import annotations

import argparse, json, re, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# The engine's own verbatim predicate (the window-level G1's check): a
# quote is "in the text" under fold + whitespace collapse, located onto
# the text's sentence grid -- one predicate, never a private re-
# implementation (C8).
from scriptengine.ingest.windows import quote_grid_span, sentence_spans  # noqa: E402

SYMMETRIC = {"fought", "met"}
STOP = {"the", "and", "of", "no"}

# The passage-unit gold's non-unit keys (the v4 file's meta).
META_KEYS = {"version", "gen", "shape", "guideline", "note", "note_gen2"}


def words(name):
    return {w for w in re.findall(r"[a-z0-9'-]+", (name or "").lower()) if len(w) >= 3 and w not in STOP}


# Optional alias resolver (--resolve-aliases): name -> set of wiki pages it
# resolves to. Two names that share no word still match when they resolve to
# the same page ("the King of Curses" / "Sukuna") -- the engine resolves
# participants the same way, so a label it would resolve correctly is right.
ALIAS_RESOLVER = None
# --quote-match: "overlap" (the plan's default: the prediction's quote must
# overlap the gold quote) or "window" (same window + same triple, the
# prediction's quote only verbatim in the window: the guideline keeps ONE row
# per (subject, verb, object) per window, so which valid quote was chosen is
# not an error).
QUOTE_MATCH = "overlap"


def same(a, b):
    if a is None or b is None:
        return a is None and b is None
    # The same name written the same way: "Ui Ui" has no 3+ letter word,
    # so the word rule below can never match it (found on the blind v6
    # test, where "Ui Ui fought ..." scored as both a miss and an FP).
    if " ".join(str(a).lower().split()) == " ".join(str(b).lower().split()):
        return True
    wa, wb = words(a), words(b)
    if wa & wb:
        return True
    # A short form of a name: "Maru" for "Marulu Val Vol Yelvori".
    if any(len(x) >= 4 and len(y) >= 4 and (x.startswith(y) or y.startswith(x))
           for x in wa for y in wb):
        return True
    if ALIAS_RESOLVER is not None:
        ra, rb = ALIAS_RESOLVER(a), ALIAS_RESOLVER(b)
        return bool(ra and rb and ra & rb)
    return False


def match(p, g):
    s, v, o = p
    gs, gv, go = g
    if v != gv:
        return False
    if gv == "awakened":
        return same(s, gs)
    if same(s, gs) and same(o, go):
        return True
    return v in SYMMETRIC and same(s, go) and same(o, gs)


def _names_only(p, g):
    """match() minus the verb equality: the name rule only, for the
    confusion matrix (a wrong-verb FP whose names still match a gold
    event says which verb the model confused)."""
    s, pv, o = p
    gs, gv, go = g
    if gv == "awakened":
        return same(s, gs)
    if same(s, gs) and same(o, go):
        return True
    if pv in SYMMETRIC or gv in SYMMETRIC:
        return same(s, go) and same(o, gs)
    return False


def _triple(e):
    """An event dict -> the scorer's (subject, verb, object): verb
    lowercased, `awakened` objectless (the model may still write an
    object for it; the rule ignores it)."""
    s, v, o = e.get("subject"), (e.get("verb") or "").lower(), e.get("object")
    return (s, v, None if v == "awakened" else o)


def _dup_key(t):
    """The duplicate-collapse key (passage union): same subject, verb,
    object -- case- and trim-insensitive (the name rule is too, so two
    spellings that match one gold are one prediction)."""
    s, v, o = t
    return (str(s or "").strip().lower(), v, str(o or "").strip().lower())


def _quote_span(text, quote):
    """The quote's character span in `text` under the engine's verbatim
    predicate, or None (not verbatim: the window-level G1's own
    failure). Offsets come from the grid's sentence spans, so two
    quotes overlap iff their character ranges intersect."""
    span = quote_grid_span(text or "", quote)
    if span is None:
        return None
    a, b = span
    spans = sentence_spans(text)
    return (spans[a][0], spans[b][1])


def _overlaps(s1, s2):
    return s1 is not None and s2 is not None and s1[0] < s2[1] and s2[0] < s1[1]


def _json_ok(raw):
    """Whether a raw model answer parses to the required JSON shape
    (infer.py's own lenient parse: think block and code fences
    stripped, the outer { ... } object, an `events` list)."""
    # The thinking-block end marker, spelled as a join so this source
    # file never carries the literal token.
    end = "<" + "/think" + ">"
    body = (raw or "").strip()
    if end in body:
        body = body.split(end)[-1]
    body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body.strip()).strip()
    s, e = body.find("{"), body.rfind("}")
    if s < 0 or e <= s:
        return False
    try:
        d = json.loads(body[s:e + 1])
    except ValueError:
        return None
    return isinstance(d, dict) and isinstance(d.get("events"), list)


def load_gold(path, legacy=False):
    """The gold, normalised to {key: unit}.

    A DIR (a series' recall_gold_v3/): the gen-2 PASSAGE file
    (gold_test_v*.gen2.json, the newest by name, the *.pre-*/
    *.old-grid archives do not match the pattern) unless `legacy`,
    which reads the OLD W-indexed v4 shape through the file's
    `windows` key (window ids resolved; the original indirection,
    unchanged).

    An explicit FILE: the gen-2 passage JSON (units under the W keys),
    a per-wiki window-level JSONL (one record per window: id/page/
    section/passage + `events` carrying their `quote` -- the future
    labeled test pools' shape), or a JSON list of such records."""
    path = Path(path)
    if path.is_dir():
        if legacy:
            return _load_legacy_dir(path)
        files = sorted(p for p in path.glob("gold_test_v*.json")
                       if "gen2" in p.name)
        if not files:
            sys.exit(f"no gen-2 test gold in {path} (gold_test_v*.gen2."
                     f"json); --legacy-v4 reads the old W-indexed shape")
        return _norm_passage(json.loads(files[0].read_text(encoding="utf-8")))
    text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
    except ValueError:
        # One record per line (JSONL): the labeled test pools' shape.
        units = {}
        for line in text.splitlines():
            if line.strip():
                r = json.loads(line)
                units[r["id"]] = _norm_window_record(r)
        if not units:
            sys.exit(f"{path}: no window records")
        return units
    if isinstance(data, list):
        units = {r["id"]: _norm_window_record(r) for r in data}
        if not units:
            sys.exit(f"{path}: no window records")
        return units
    if "id" in data and ("events" in data or "passage" in data):
        return {data["id"]: _norm_window_record(data)}  # a single record
    return _norm_passage(data)


def _load_legacy_dir(path):
    """The old W-indexed v4 shape (the original indirection, unchanged):
    the newest versioned file's W entries, window ids resolved through
    its `windows` key. The gen-2 files are excluded by name so a
    re-keyed dir still reads the old shape behind the flag."""
    gold, wfile = {}, "windows_40.json"
    files = [p for p in sorted(Path(path).glob("gold_test_v*.json"))
             if "gen2" not in p.name]
    for f in files[-1:]:
        data = json.loads(f.read_text(encoding="utf-8"))
        wfile = data.get("windows", wfile)
        for k, v in data.items():
            if k.startswith("W"):
                gold[int(k[1:])] = v
    wins = json.loads((Path(path) / wfile).read_text(encoding="utf-8"))
    return {wins[i]["id"]: {"core": g["core"],
                            "optional": g.get("optional") or []}
            for i, g in gold.items()}


def _norm_passage(data):
    units = {k: v for k, v in data.items()
             if k not in META_KEYS and isinstance(v, dict)
             and isinstance(v.get("windows"), list)}
    if not units:
        sys.exit("not a passage-unit gold (no W units with covering "
                 "windows); is this a window-level pool?")
    return units


def _norm_window_record(r):
    """A labeled test pool's window record: the gold events carry their
    `quote` (the match needs it); `optional` = the borderline tier."""
    return {"id": r["id"], "page": r.get("page") or "",
            "section": r.get("section") or "", "passage": r.get("passage") or "",
            "core": r.get("events") or [], "optional": r.get("optional") or []}


def _score_unit(preds, core, opt, gmatch=None):
    """The scorer's match rule on one unit.

    `preds`: a list of (triple, dup-key, pred-quote-span). `core`/
    `opt`: lists of (triple, gold-quote-span). `gmatch(p, g, gspan,
    pspan)` is the event-match predicate: the plain rule (passage /
    legacy units: the gold carries no quote) or the rule + quote
    overlap (window records: a match must sit at the gold's place).
    A core event is consumed at most once, then an optional; a
    duplicate of an already-matched event is neither a hit nor an
    error; anything else is an FP, and a name-matched wrong-verb FP
    feeds the confusion matrix. Returns (hit, n_pred, fp, confusions,
    per-verb counters)."""
    used_c, used_o = set(), set()
    hit = fp = 0
    conf = []
    pv_pred, pv_tp, pv_core = Counter(), Counter(), Counter()
    for p, _dk, pspan in preds:
        pv = p[1]
        pv_pred[pv] += 1

        def hitc(g, gspan):
            return gmatch(p, g, gspan, pspan) if gmatch else match(p, g)
        ci = next((i for i, (g, gspan) in enumerate(core)
                   if i not in used_c and hitc(g, gspan)), None)
        if ci is not None:
            used_c.add(ci); hit += 1
            pv_tp[pv] += 1; pv_core[pv] += 1
            continue
        oi = next((i for i, (g, gspan) in enumerate(opt)
                   if i not in used_o and hitc(g, gspan)), None)
        if oi is not None:
            used_o.add(oi); pv_tp[pv] += 1
            continue
        matched = [core[i] for i in used_c] + [opt[i] for i in used_o]
        if any(hitc(g, gspan) for g, gspan in matched):
            pv_tp[pv] += 1
            continue  # a duplicate of an already-matched gold event is neither
        fp += 1
        for g, gspan in list(core) + list(opt):
            if g[1] != pv and _names_only(p, g):
                conf.append((pv, g[1]))
                break
    return hit, len(preds), fp, conf, pv_pred, pv_tp, pv_core


def _f1(p, r):
    if p is None or r is None:
        return None
    return round(2 * p * r / (p + r), 3) if p + r > 0 else 0.0


def score(gold, preds):
    """Score `preds` ({window id -> record or event list}) against
    `gold` (any of the three shapes, auto-detected). Returns
    (summary, per-unit); the summary carries the legacy fields
    (core_recall/core/hit/pred/fp/precision) plus the U-WP5 report:
    per-wiki P/R/F1, per-verb P/R/F1, the verb confusion (fought vs
    defeated first), JSON-validity and quote-verbatim rates."""
    kind = "legacy"
    for u in gold.values():
        if isinstance(u, dict) and isinstance(u.get("windows"), list) \
                and u.get("passage"):
            kind = "passage"
            break
    if kind == "legacy":
        # A window record carries the window's own text (the match
        # needs it for the quote overlap); a legacy unit is bare
        # triples with no passage.
        for u in gold.values():
            if isinstance(u, dict) and u.get("passage") and "id" in u:
                kind = "window"
                break

    def _evts(rec):
        ev = (rec or {}).get("events") or [] if isinstance(rec, dict) else (rec or [])
        return [e for e in ev if isinstance(e, dict)]
    pred_events = {wid: _evts(rec) for wid, rec in preds.items()}

    # The JSON-validity rate: over the records that carry the model's
    # raw answer (infer.py's shape); None while no record does.
    raw_recs = [r for r in preds.values()
                if isinstance(r, dict) and "raw" in r]
    json_validity = None
    if raw_recs:
        ok = sum(1 for r in raw_recs if _json_ok(r["raw"]))
        json_validity = round(ok / len(raw_recs), 4)

    win_to_units = {}
    if kind == "passage":
        # window id -> [(unit, the window's gold-known text)]: the READ
        # span in the passage (a partial window's unread tail is
        # unknown to the scorer, so a quote there conservatively
        # counts as not verbatim).
        for unit in gold.values():
            passage = unit["passage"]
            for w in unit["windows"]:
                a, b = w["span"]
                win_to_units.setdefault(w["id"], []).append((unit, passage[a:b]))

    pv_gold = Counter()
    pv_pred_all, pv_tp_all, pv_core_all = Counter(), Counter(), Counter()
    conf_all = []
    hit_total = n_pred_total = fp_total = 0
    discarded = 0
    per = {}
    for key in sorted(gold):
        unit = gold[key]
        if kind == "passage":
            # The student is run on every covering window: UNION the
            # predictions, drop the ones whose quote is not inside the
            # annotated slice (the text beyond it was never read),
            # collapse duplicates (same subject, verb, object), then
            # the existing match rule.
            seen, upreds = set(), []
            n_disc = 0
            for w in unit["windows"]:
                for e in pred_events.get(w["id"], []):
                    if _quote_span(unit["passage"], e.get("quote")) is None:
                        n_disc += 1
                        continue
                    t = _triple(e)
                    dk = _dup_key(t)
                    if dk in seen:
                        continue
                    seen.add(dk)
                    upreds.append((t, dk, None))
            discarded += n_disc
            core = [(tuple(t), None) for t in unit["core"]]
            opt = [(tuple(t), None) for t in unit["optional"]]
            hit, npred, fp, conf, vpr, vtp, vpc = _score_unit(
                upreds, core, opt)
            pv_gold.update(t[1] for t, _s in core)
        else:
            wid = unit.get("id") or key
            ptext = unit.get("passage") or ""
            upreds = [(_triple(e), _dup_key(_triple(e)), _quote_span(ptext,
                                                                    e.get("quote")))
                      for e in pred_events.get(wid, [])]
            if kind == "window":
                # The labeled pools' records carry the gold events
                # under `events` (load_gold normalises them to `core`;
                # an in-memory gold may be the raw shape).
                core = [(_triple(g), _quote_span(ptext, g.get("quote")))
                        for g in (unit.get("core") or unit.get("events") or [])]
                opt = [(_triple(g), _quote_span(ptext, g.get("quote")))
                       for g in (unit.get("optional") or [])]
                # The plan's event match: (subject, verb, object) with
                # the quote overlapping the gold quote.
                def gmatch(p, g, gspan, pspan, _t=ptext):
                    if QUOTE_MATCH == "window":
                        return match(p, g) and pspan is not None
                    return match(p, g) and _overlaps(pspan, gspan)
            else:
                core = [((a, b, None if b == "awakened" else c), None)
                        for a, b, c in unit["core"]]
                opt = [((a, b, None if b == "awakened" else c), None)
                       for a, b, c in unit["optional"]]
                gmatch = None
            hit, npred, fp, conf, vpr, vtp, vpc = _score_unit(
                upreds, core, opt, gmatch)
            pv_gold.update(t[1] for t, _s in core)
        pv_pred_all.update(vpr); pv_tp_all.update(vtp); pv_core_all.update(vpc)
        conf_all.extend(conf)
        hit_total += hit; n_pred_total += npred; fp_total += fp
        per[key] = {"core": len(unit.get("core") or unit.get("events") or []),
            "hit": hit, "pred": npred, "fp": fp}
        if kind == "passage":
            per[key]["discarded"] = n_disc

    n_core_total = sum(pv_gold.values())
    recall = round(hit_total / n_core_total, 3) if n_core_total else None
    precision = round((n_pred_total - fp_total) / n_pred_total, 3) \
        if n_pred_total else None
    summary = {
        # the legacy shape (calib_score et al. read these):
        "core_recall": recall, "core": n_core_total, "hit": hit_total,
        "pred": n_pred_total, "fp": fp_total, "precision": precision,
        # the U-WP5 report:
        "kind": kind, "units": len(gold),
        "f1": _f1(precision, recall),
        "per_verb": {},
        "confusion": [],
        "json_validity": json_validity,
        "quote_verbatim": None,
    }
    if kind == "passage":
        summary["discarded_outside_slice"] = discarded

    # Per-verb P/R/F1 (the search's tie-breaks and vetoes read these):
    # precision over the verb's predictions (a match of any tier, or a
    # duplicate of one), recall over the verb's core events.
    for v in sorted(set(pv_gold) | set(pv_pred_all)):
        g, pd, tp = pv_gold[v], pv_pred_all[v], pv_tp_all[v]
        p = round(tp / pd, 3) if pd else None
        r = round(pv_core_all[v] / g, 3) if g else None
        summary["per_verb"][v] = {
            "gold": g, "pred": pd, "tp": tp,
            "precision": p, "recall": r, "f1": _f1(p, r)}

    # The confusion matrix: each FP's predicted verb vs the gold verb
    # of the (name-matched) event it should have been. fought vs
    # defeated first (the plan's first-row rule), then by count.
    cf = Counter(conf_all)

    def _cf_key(item):
        (pv, gv), n = item
        return (0 if {pv, gv} == {"fought", "defeated"} else 1, -n, pv, gv)

    summary["confusion"] = [[pv, gv, n]
                            for (pv, gv), n in sorted(cf.items(),
                                                       key=_cf_key)[:20]]

    # The quote-verbatim rate: a predicted event's quote located
    # verbatim (the engine's predicate) in the window text it came
    # from. Over every attributable prediction event; a window on no
    # gold unit is unattributable (its text is unknown to the scorer).
    v_total = v_hits = 0
    if kind == "passage":
        for wid, entries in win_to_units.items():
            _u, wtext = entries[0]
            for e in pred_events.get(wid, []):
                q = e.get("quote")
                if not q:
                    continue
                v_total += 1
                if _quote_span(wtext, q) is not None:
                    v_hits += 1
    elif kind == "window":
        for key in gold:
            wid = gold[key].get("id") or key
            ptext = gold[key].get("passage") or ""
            for e in pred_events.get(wid, []):
                q = e.get("quote")
                if not q:
                    continue
                v_total += 1
                if _quote_span(ptext, q) is not None:
                    v_hits += 1
    summary["quote_verbatim"] = round(v_hits / v_total, 4) if v_total else None
    return summary, per


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--series", default="jjk",
                    help="the wiki being scored (the report label and "
                         "the default gold dir's series)")
    ap.add_argument("--pred", required=True)
    ap.add_argument("--gold-dir", default=None,
                    help="default series/<series>/training/recall_gold_v3")
    ap.add_argument("--gold", default=None,
                    help="an explicit gold file: the gen-2 passage "
                         "JSON, or a per-wiki window-level JSONL "
                         "(records with quotes, the labeled test "
                         "pools' shape)")
    ap.add_argument("--legacy-v4", action="store_true",
                    help="read the OLD W-indexed v4 shape (window-level, "
                         "no quotes) from --gold-dir, not the gen-2 "
                         "passage file")
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--quote-match", choices=("overlap", "window"), default="overlap",
                    help="window records: 'overlap' (quote spans overlap) or "
                         "'window' (same window + same triple, quote verbatim)")
    ap.add_argument("--resolve-aliases", action="store_true",
                    help="names also match when they resolve to the same "
                         "wiki page (series facts.db, the verifier's resolver)")
    a = ap.parse_args()
    global QUOTE_MATCH, ALIAS_RESOLVER
    QUOTE_MATCH = a.quote_match
    if a.resolve_aliases:
        sys.path.insert(0, str(ROOT / "tools" / "train"))
        import verify_row_wiki as _vrw
        _wiki = _vrw.Wiki(str(ROOT / "series" / a.series / "facts.db"))
        _cache = {}

        def ALIAS_RESOLVER(name):  # noqa: N802 -- module hook
            if name not in _cache:
                hit = _wiki.resolve(name)[:1]
                if not hit:
                    # "the King of Curses" -> "King of Curses": the leading
                    # article is not part of the alias the wiki records
                    bare = re.sub(r"(?i)^(the|a|an)\s+", "", name.strip())
                    hit = _wiki.resolve(bare)[:1] if bare != name else []
                _cache[name] = set(hit)
            return _cache[name]
        globals()["ALIAS_RESOLVER"] = ALIAS_RESOLVER

    gold_path = Path(a.gold) if a.gold else \
        Path(a.gold_dir or f"series/{a.series}/training/recall_gold_v3")
    gold = load_gold(gold_path, legacy=a.legacy_v4)
    preds = {}
    for line in open(a.pred):
        if line.strip():
            r = json.loads(line)
            preds[r["id"]] = r
    s, per = score(gold, preds)
    s = {"series": a.series, "gold": str(gold_path), **s}
    print(json.dumps(s))
    if a.show:
        for k, v in per.items():
            print(k, v)
    return 0


if __name__ == "__main__":
    sys.exit(main())