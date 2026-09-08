"""Line-level reachability: is every sentence in the corpus retrievable?

The gold question bank samples. At the prose pass's calibrated density it asks
about roughly one line in eight, which is excellent regression protection and
an expensive way to *discover* anything -- the whole campaign's hand-authored
bank has averaged one engine finding per few hundred questions written. It also
cannot, arithmetically, deliver the standing mandate of "down to a single line"
at a million words a series.

This module covers the complement mechanically, with no authoring, in two
tiers:

``index_coverage`` (tier 0)
    Is each sentence present, whole, inside some chunk? Pure SQLite, no server,
    a fraction of a second for a whole series. A miss is an indexing or
    chunking defect: the line is invisible to retrieval no matter what anyone
    asks. This is the family the campaign has repeatedly found by hand --
    colon truncation, the gallery body strip, the Trivia chunking gap.

``recall`` (tier 1)
    Does ``/context`` actually serve the line back? Needs the live server, so
    it is sampled rather than exhaustive.

The two tiers report separately on purpose. A tier 0 miss and a tier 1 miss
have different causes and different fixes, and a single blended number would
hide both.
"""

from __future__ import annotations

import hashlib
import json
import random
import re
import time
import unicodedata
import urllib.request
from pathlib import Path
from typing import Any, Callable

from scriptengine.config import Settings
from scriptengine.stores.facts import FactStore

BASE = "http://127.0.0.1:8000"

# Sentence boundaries the wiki's own prose style breaks. Splitting on
# `(?<=[.!?])\s+` alone silently welds sentences together, because the corpus
# hangs its citations directly off the full stop with no space:
# "...into a cliff.(Chapter 151) He thinks...". On the JJK corpus that single
# oversight hid roughly five thousand sentences inside their neighbours.
_SENT_END = re.compile(r'[.!?]["\')\]]*(?:\([^()]{1,80}\))*\s+')

ABBREV = frozenset({
    "mr", "mrs", "ms", "dr", "st", "vs", "jr", "sr", "prof", "lt", "capt",
    "no", "vol", "ch", "ep", "approx", "etc", "inc", "ltd", "co",
})

# The section store and the served beats do not render citations identically:
# a section says "(Chapter 143)" where the beat says "(Chapter 143, Episode
# 49)". Comparing raw text therefore fails on the citation rather than on the
# prose -- measured at 71% of apparent span-misses against under 10% of hits.
# Both sides are stripped before comparison so the test measures what it says.
_CITE = re.compile(
    r"\((?:Chapter|Episode|Volume|Fanbook|Modulo|Movie|OVA|Novel|Databook)"
    r"[^()]*\)"
)

# Link-list scaffolding the indexer leaves out on purpose: interwiki name
# lists, see-alsos, external links. A miss inside one is correct behaviour, and
# counting them buries real findings -- on JJK they alone moved the headline
# from 99.9959% to 99.875%. `References` is deliberately absent: on chapter
# pages it carries real trivia prose, and that is where a genuine gap surfaced.
BOILERPLATE = frozenset({
    "navigation", "site navigation", "see also", "external links",
    "external link", "navigation boxes",
})


class SpanRecallError(RuntimeError):
    """The run could not be trusted -- not merely a low score."""


def norm(text: str) -> str:
    """Whitespace- and unicode-normalised, for substring comparison only.

    Case is deliberately preserved: this engine's contract is verbatim text,
    so a case difference between the section store and the chunk store is a
    defect worth seeing rather than something to normalise away.
    """
    return re.sub(r"\s+", " ", unicodedata.normalize("NFC", text)).strip()


def decite(text: str) -> str:
    """Drop inline citation markers so prose is compared against prose."""
    return re.sub(r"\s+", " ", _CITE.sub("", text)).strip()


def is_boilerplate(breadcrumb: str | None) -> bool:
    return (breadcrumb or "").strip().lower() in BOILERPLATE


def sentences(text: str, min_words: int = 6) -> list[str]:
    """Split into sentences, keeping trailing citations with their sentence.

    Boundaries are found rather than split on, so a citation hanging off a full
    stop stays attached to the sentence it cites. A boundary landing on a known
    abbreviation is not a boundary.

    Fragments and table rows are dropped: a three-word line carries too little
    signal to query with, and a pipe-delimited row is not prose. Both would
    yield false alarms rather than findings.
    """
    flat = norm(text)
    out: list[str] = []
    start = 0
    for match in _SENT_END.finditer(flat):
        candidate = flat[start:match.end()].strip()
        tail = candidate.rstrip(".\"')]").split()
        last = tail[-1].lower().rstrip(".") if tail else ""
        if last in ABBREV:
            continue
        out.append(candidate)
        start = match.end()
    if start < len(flat):
        out.append(flat[start:].strip())
    return [s for s in out if len(s.split()) >= min_words and s.count("|") < 3]


def _facts_path(series: str, settings: Settings | None = None) -> Path:
    settings = settings or Settings()
    return Path(settings.series_root) / series / "facts.db"


def _corpus(series: str, settings: Settings | None = None):
    """Documents, their non-empty sections, and their chunks."""
    path = _facts_path(series, settings)
    if not path.exists():
        raise SpanRecallError(
            f"No index for series {series!r} at {path}. Run `index` first."
        )
    with FactStore(path) as store:
        con = store.connection
        docs = {
            row["id"]: (row["title"], row["url"])
            for row in con.execute("SELECT id, title, url FROM documents")
        }
        secs = [
            (row["document_id"], row["breadcrumb"], row["text"])
            for row in con.execute(
                "SELECT document_id, breadcrumb, text FROM sections "
                "WHERE COALESCE(text,'') <> '' ORDER BY document_id, ordinal"
            )
        ]
        chunks: dict[int, list[str]] = {}
        for row in con.execute(
            "SELECT document_id, text FROM chunks WHERE COALESCE(text,'') <> ''"
        ):
            chunks.setdefault(row["document_id"], []).append(norm(row["text"]))
    return docs, secs, chunks


def index_coverage(series: str, settings: Settings | None = None,
                   min_words: int = 6,
                   include_boilerplate: bool = False) -> dict[str, Any]:
    """Tier 0: every sentence, is it whole inside some chunk of its document?

    Offline and exhaustive. Cheap enough to run after every re-index, which is
    the point -- it is the only check here that covers the whole corpus rather
    than a sample.
    """
    docs, secs, chunks = _corpus(series, settings)
    misses: list[dict[str, Any]] = []
    counted = skipped = 0
    started = time.time()

    for doc_id, breadcrumb, text in secs:
        boiler = is_boilerplate(breadcrumb)
        if boiler and not include_boilerplate:
            skipped += len(sentences(text, min_words))
            continue
        doc_chunks = chunks.get(doc_id, [])
        for sentence in sentences(text, min_words):
            counted += 1
            if not any(sentence in chunk for chunk in doc_chunks):
                title, url = docs.get(doc_id, ("?", ""))
                misses.append({
                    "doc_id": doc_id, "title": title, "url": url,
                    "breadcrumb": breadcrumb, "sentence": sentence,
                    "words": len(sentence.split()),
                    "boilerplate": boiler,
                    "doc_has_chunks": bool(doc_chunks),
                })

    return {
        "series": series,
        "sections": len(secs),
        "sentences": counted,
        "covered": counted - len(misses),
        "missing": len(misses),
        "coverage": (counted - len(misses)) / counted if counted else 1.0,
        "boilerplate_skipped": skipped,
        "elapsed": time.time() - started,
        "misses": misses,
    }


def _ask(query: str, series: str, timeout: float,
         base: str = BASE, door: str | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {"series": series, "query": query}
    if door:
        # The /context mode param forces one retrieval door; the D5 sweep
        # measures each door (qa / roster / narrative) separately, so a dead
        # passage leg cannot be averaged away by the router.
        body["mode"] = door
    request = urllib.request.Request(
        f"{base}/context", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read())


def served_text(bundle: dict[str, Any]) -> str:
    """Everything the caller actually receives, flattened for the substring test."""
    parts: list[str] = []
    # A roster bundle carries its content in members[].text / passages[]
    # with beats: [] -- without the two keys the roster door serves 0 chars
    # and every probe structurally verdicts MISS_DOC (COUNCIL_csm-3 Ruling 1).
    for key in ("beats", "facts", "relations", "participants",
                "members", "passages"):
        value = bundle.get(key)
        if not isinstance(value, list):
            continue
        for item in value:
            if isinstance(item, dict):
                parts.extend(v for v in item.values() if isinstance(v, str))
            elif isinstance(item, str):
                parts.append(item)
    return norm(" \n ".join(parts))


def make_query(sentence: str, mode: str, title: str | None = None) -> str:
    """`verbatim` is the reachability floor; the others isolate one variable.

    `scoped` is the control for this corpus's redundancy -- a wiki narrates the
    same event on the chapter page, the episode page, the character synopsis
    and the battle page, so a bare sentence is genuinely ambiguous about which
    page is wanted. Naming the page separates "cannot find this line" from
    "found the event, picked a sibling page".
    """
    if mode == "scoped":
        return f"{title}: {sentence}" if title else sentence
    if mode == "verbatim":
        return sentence
    keep = [t for t in re.findall(r"[A-Za-z0-9'\-]+", sentence)
            if t.lower() not in _STOP]
    return " ".join(keep[:18]) or sentence


_STOP = frozenset("""a an the of in on at to for with by from as is are was were be been
being and or but if then than that this these those it its his her their our your my he
she they we you i had has have do does did not no so such very can could will would shall
should may might must who whom whose which what when where why how there here also into
out up down over under after before""".split())


def _panel_hash(rows: list[list[str]]) -> str:
    """Stable identity of a pinned panel; stamped in every sweep report.

    A sweep that reports a different hash than the pin it was told to run
    did not run the panel it claims -- the §2a sample-churn trap with a
    name on it.
    """
    payload = json.dumps(rows, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def sweep_ledger_path(folder: Path, door: str, panel_hash: str) -> Path:
    """The pinned-panel sweep ledger, keyed by the panel's 8-char hash.

    A per-series shared name (F-CSM-3b-1) let a heldout-panel run rewrite
    the pinned panel's `sweep_qa.jsonl` with only its own keys while a
    pinned sidecar sat next to it unlinked -- the 168 pinned rows were
    dropped from disk. Each panel keeps its own `<door>_<hash8>.jsonl` pair
    so interleaved runs cannot drop each other's rows (council CSM-3b
    R-CSM3B-2).
    """
    return Path(folder) / f"sweep_{door}_{panel_hash[:8]}.jsonl"


def build_panel(series: str, settings: Settings | None = None,
                min_words: int = 6, seed: int = 42,
                held_out: int = 200) -> dict[str, Any]:
    """Pin the tier-1 probe panel: every tier-0-eligible sentence, once.

    Deterministic `(title, section, sentence)` order instead of a seed-7
    sample, so a chunker fix cannot swap the panel and read its own
    regression as progress (§2a trap 1). The hash is stamped in every sweep
    report. The held-out split is drawn with a fixed seed and written to a
    side file the executing agent never opens -- the sweep that grades a fix
    must not be chosen by the fixer (§9a).

    The `<min_words` floor is a declared measurement boundary, not a silent
    scope: sub-floor lines (chapter-list rows like "Fearsome 163.") carry
    too little signal to query with, and their misses would be ranking
    noise, not reachability defects. The exclusion is recorded in the
    series' audit (per-wiki census, see the series' overrides.yaml).
    """
    docs, secs, chunks = _corpus(series, settings)
    probes: set[tuple[str, str, str]] = set()
    for doc_id, breadcrumb, text in secs:
        if is_boilerplate(breadcrumb):
            continue
        doc_chunks = chunks.get(doc_id, [])
        title = docs.get(doc_id, ("?", ""))[0]
        for sentence in sentences(text, min_words):
            if any(sentence in chunk for chunk in doc_chunks):
                probes.add((title, breadcrumb, sentence))
    ordered = [list(p) for p in sorted(probes)]
    k = min(held_out, len(ordered) // 2)
    if k:
        held = set(random.Random(seed).sample(range(len(ordered)), k))
        held_rows = [ordered[i] for i in sorted(held)]
        sweep_rows = [row for i, row in enumerate(ordered) if i not in held]
    else:
        sweep_rows, held_rows = ordered, []
    return {
        "series": series, "min_words": min_words, "seed": seed,
        "panel": sweep_rows, "held_out": held_rows,
        "hash": _panel_hash(sweep_rows),
        "panel_size": len(sweep_rows), "held_out_size": len(held_rows),
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """Strict reader for the sweep ledger: a line that does not parse
    refuses the resume (Ruling 7 tamper) instead of a raw traceback or a
    silent start-over."""
    rows: list[dict[str, Any]] = []
    if path.exists():
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise SpanRecallError(
                        f"ledger {path} does not parse at line {number} -- "
                        f"corrupted ledger; refusing to resume (restore it "
                        f"from git or delete it and re-probe)") from error
    return rows


def _atomic_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    """Rewrite, never append: a resumed sweep must not duplicate the panel.

    The probe path used to append into the results file with dedupe
    unwired (§2a trap 2, caught live in GATE_REBASELINE's +400-line
    append); each run now rewrites the file from the merged row set.
    """
    payload = "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows)
    tmp = path.with_name(path.name + ".tmp")
    try:
        tmp.write_text(payload, encoding="utf-8")
        tmp.replace(path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def recall(series: str, settings: Settings | None = None, mode: str = "verbatim",
           sample: int = 400, every: int | None = None, seed: int = 7,
           timeout: float = 120.0, min_words: int = 6, base: str = BASE,
           done: set[str] | None = None,
           on_row: Callable[[dict[str, Any]], None] | None = None,
           on_progress: Callable[[int, int, dict[str, int]], None] | None = None,
           panel: list[tuple[str, str, str]] | None = None,
           panel_hash: str | None = None,
           results_path: Path | None = None,
           door: str | None = None,
           limit: int | None = None,
           stamps: dict[str, str] | None = None,
           ) -> dict[str, Any]:
    """Tier 1: does the served bundle actually contain the line?

    Two call shapes:

    - legacy (`panel is None`): a seed-7 sample of tier-0-eligible
      sentences -- the standing 400-probe gate. Behaviour unchanged.
    - pinned (`panel` given): the exhaustive D5 sweep. Probes come from the
      pin (no corpus read, so a re-index cannot swap the panel under a
      running sweep, §2a trap 1), resume is keyed `(title, sentence)` over
      `results_path` (rewritten, never append-duped, §2a trap 2; transient
      ERROR rows are re-probed on resume), and `hit_rate` divides by the
      FULL panel, not the rows this run executed (§2a trap 3).

    Verdicts are split so a number is actionable. ``MISS_DOC`` (the line's own
    page never reached the bundle) is a ranking problem; ``MISS_SPAN`` (the page
    came back without the line) is chunk selection inside the document. Lumping
    them produces a figure nobody can act on.

    Only sentences tier 0 has already cleared are probed -- otherwise an
    indexing gap would be counted twice, once in each tier.
    """
    if panel is not None:
        probes = [tuple(p) for p in panel]
        if panel_hash is None:
            panel_hash = _panel_hash([list(p) for p in probes])
        prior: dict[tuple[str, str], dict[str, Any]] = {}
        sidecar = (Path(results_path).with_name(Path(results_path).name + ".new")
                   if results_path else None)
        for source in filter(None, [results_path, sidecar]):
            for row in _read_jsonl(source):  # the sidecar is newer; it wins
                # Ruling 7 tamper: every ledger row must carry this panel's
                # hash stamp; a row without it (or stamped for another panel)
                # means the file at this key is not this panel's own ledger --
                # refusing beats silently re-probing or double-counting.
                if row.get("panel_hash") != panel_hash:
                    raise SpanRecallError(
                        f"ledger {source} carries a row without this panel's "
                        f"hash stamp -- refusing to resume; restore the "
                        f"ledger from git or delete it and re-probe")
                if row.get("verdict") == "ERROR":
                    continue  # a transient failure is re-probed on resume
                key = (row.get("title"), row.get("sentence"))
                if key[1]:
                    prior[key] = row
        to_run = [p for p in probes if (p[0], p[2]) not in prior]
        if limit:
            to_run = to_run[:limit]

        counts = {"HIT": 0, "MISS_DOC": 0, "MISS_SPAN": 0,
                  "TRUNCATED": 0, "ERROR": 0}
        started = time.time()
        for index, (title, breadcrumb, sentence) in enumerate(to_run, 1):
            query = make_query(sentence, mode, title)
            returned: list[str] = []
            error = None
            bundle: dict[str, Any] = {}
            try:
                bundle = _ask(query, series, timeout, base, door=door)
                text = served_text(bundle)
                returned = [b.get("doc_title") for b in bundle.get("beats", [])
                            if isinstance(b, dict)]
                # a roster bundle returns members/passages with beats: [] --
                # the members' names are the returned docs that door (COUNCIL_csm-3 Ruling 1)
                returned += [m.get("name") for m in bundle.get("members", [])
                             if isinstance(m, dict)]
                if sentence in text or decite(sentence) in decite(text):
                    verdict = "HIT"
                elif bundle.get("truncated"):
                    verdict = "TRUNCATED"
                elif title not in returned:
                    verdict = "MISS_DOC"
                else:
                    verdict = "MISS_SPAN"
            except Exception as exc:  # a probe failing must not end the sweep
                verdict, error = "ERROR", str(exc)[:200]

            counts[verdict] += 1
            row = {
                "verdict": verdict, "title": title, "breadcrumb": breadcrumb,
                "query": query, "sentence": sentence, "door": door,
                "mode_routed": bundle.get("mode"),
                "truncated": bundle.get("truncated"),
                "returned_docs": returned[:8], "error": error,
                # F1 provenance (council CSM-3b R-CSM3B-2): the panel hash is
                # the tamper guard, device/commit the run's provenance stamps.
                "panel_hash": panel_hash, **(stamps or {}),
            }
            if sidecar is not None:
                with sidecar.open("a", encoding="utf-8") as handle:
                    handle.write(json.dumps(row, ensure_ascii=False) + "\n")
            if on_row:
                on_row(row)
            if on_progress and index % 100 == 0:
                on_progress(index, len(to_run), counts)

        # Merge prior rows + this run's sidecar rows, rewrite the results
        # file in panel order (deterministic, idempotent resume).
        if results_path is not None:
            fresh: dict[tuple[str, str], dict[str, Any]] = {}
            for row in _read_jsonl(sidecar) if sidecar else []:
                fresh[(row.get("title"), row.get("sentence"))] = row
            merged: list[dict[str, Any]] = []
            for (title, _breadcrumb, sentence) in probes:
                row = fresh.get((title, sentence)) or prior.get((title, sentence))
                if row:
                    merged.append(row)
            _atomic_jsonl(Path(results_path), merged)
            sidecar.unlink(missing_ok=True)
            counts = {"HIT": 0, "MISS_DOC": 0, "MISS_SPAN": 0,
                      "TRUNCATED": 0, "ERROR": 0}
            for row in merged:
                counts[row["verdict"]] = counts.get(row["verdict"], 0) + 1
            done_count = len(merged)
        else:
            done_count = sum(counts.values())

        return {
            "series": series, "mode": mode, "door": door,
            "probes": done_count, "panel_size": len(probes),
            "panel_hash": panel_hash, "counts": counts,
            # trap 3: the denominator is the panel, not the rows run this
            # invocation -- a resumed sweep must not read its partial run
            # as a better rate.
            "hit_rate": counts["HIT"] / len(probes) if probes else 1.0,
            "elapsed": time.time() - started,
        }

    docs, secs, chunks = _corpus(series, settings)
    probes: list[tuple[str, str, str]] = []
    for doc_id, breadcrumb, text in secs:
        if is_boilerplate(breadcrumb):
            continue
        doc_chunks = chunks.get(doc_id, [])
        title = docs.get(doc_id, ("?", ""))[0]
        for sentence in sentences(text, min_words):
            if any(sentence in chunk for chunk in doc_chunks):
                probes.append((title, breadcrumb, sentence))

    random.Random(seed).shuffle(probes)
    if sample:
        probes = probes[:sample]

    done = done or set()
    counts = {"HIT": 0, "MISS_DOC": 0, "MISS_SPAN": 0, "TRUNCATED": 0, "ERROR": 0}
    rows: list[dict[str, Any]] = []
    started = time.time()

    for index, (title, breadcrumb, sentence) in enumerate(probes, 1):
        if sentence in done:
            continue
        query = make_query(sentence, mode, title)
        returned: list[str] = []
        error = None
        bundle: dict[str, Any] = {}
        try:
            bundle = _ask(query, series, timeout, base)
            text = served_text(bundle)
            returned = [b.get("doc_title") for b in bundle.get("beats", [])
                        if isinstance(b, dict)]
            # same as the pinned branch: roster bundles serve through members
            returned += [m.get("name") for m in bundle.get("members", [])
                         if isinstance(m, dict)]
            if sentence in text or decite(sentence) in decite(text):
                verdict = "HIT"
            elif bundle.get("truncated"):
                verdict = "TRUNCATED"
            elif title not in returned:
                verdict = "MISS_DOC"
            else:
                verdict = "MISS_SPAN"
        except Exception as exc:  # a probe failing must not end the sweep
            verdict, error = "ERROR", str(exc)[:200]

        counts[verdict] += 1
        row = {
            "verdict": verdict, "title": title, "breadcrumb": breadcrumb,
            "query": query, "sentence": sentence,
            "mode_routed": bundle.get("mode"),
            "truncated": bundle.get("truncated"),
            "returned_docs": returned[:8], "error": error,
        }
        rows.append(row)
        if on_row:
            on_row(row)
        if on_progress and every and index % every == 0:
            on_progress(index, len(probes), counts)

    total = sum(counts.values())
    return {
        "series": series, "mode": mode, "probes": total,
        "counts": counts,
        "hit_rate": counts["HIT"] / total if total else 1.0,
        "elapsed": time.time() - started,
        "rows": rows,
    }
