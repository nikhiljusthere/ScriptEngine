"""Anime closed-caption corpus for a series (JJK only, for now).

Phase 1 of ``plan/JJK_TRANSCRIPTS_PLAN.md``: download the SubArchivist
per-season plaintext exports, parse them into per-episode JSON plus a
separate SQLite dialogue store (``transcripts.db``), and keep a hash
manifest for idempotent re-import.

Campaign-neutral by construction (council ruling 2026-09-08): this touches
neither ``facts.db`` nor the four standing gates, and transcripts never
enter the D6 comprehension denominator.

Speaker labels are the archive's best effort and are stored verbatim.
``normalize_speaker`` applies one deterministic rule (the archive marks
flashback lines ``(Flashback) X`` — same person, contextual marker) plus a
small explicit variant map of 100%-identity merges. Nothing here guesses.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

# The SubArchivist JJK book. The anime currently ends at E47 (Gojo sealed),
# the same frontier as the wiki; re-import when the archive adds episodes.
EXPORTS = [
    {
        "key": "season-1",
        "season": "S1",
        "url": "https://subs.yakuaru.com/books/jujutsu-kaisen/chapter/season-1/export/plaintext",
    },
    {
        "key": "season-2",
        "season": "S2",
        "url": "https://subs.yakuaru.com/books/jujutsu-kaisen/chapter/season-2/export/plaintext",
    },
    {
        "key": "movie",
        "season": "M",
        "url": "https://subs.yakuaru.com/books/jujutsu-kaisen/chapter/movie/export/plaintext",
    },
]

_UA = "Mozilla/5.0 (X11; Linux x86_64; rv:130.0) Gecko/20100101 Firefox/130.0"
# NBSP: the archive indents continuation lines and pads SIGN lines with
# U+00A0, not spaces. A parser that matches on spaces silently drops
# every continuation line.
_NBSP = "\u00a0"

_EP_HEADER = re.compile(r"^(E\d+|M\d+)\s*-\s*(.+)$")
_TS_LINE = re.compile(r"^\[(\d{1,2}:\d{2}(?::\d{2})?)\]\s*(\S.*)$")
_SIGN = re.compile(r"^SIGN[\s\u00a0]*(.*)$")

# Deterministic identity merges only (checked against the 368-label
# inventory, 2026-09-08). Deliberately NOT merged: "Fushiguro" (the label
# covers both Megumi and Toji — merging would fabricate an identity) and
# every generic label (Student, Woman, Plate ...).
# ponytail: variant map is a closed list; a new archive misspelling stays
# its own label until someone adds a verified merge.
VARIANT_MAP = {
    "itadori": "Yuji",
    "muta": "Mahito",
    "mei": "Mei Mei",
    "meimei": "Mei Mei",
    "uiui": "Ui",
    "pandra": "Panda",
    "nanamni": "Nanami",
    "narration": "Narrator",
}
_FLASHBACK = re.compile(r"^\(Flashback\)\s*", re.IGNORECASE)


def normalize_speaker(label: str) -> str:
    """Archive label -> canonical name. Rules, not judgement."""
    label = _FLASHBACK.sub("", label).strip()
    return VARIANT_MAP.get(label.lower(), label)


def fetch(url: str, retries: int = 5) -> str:
    """GET with the browser UA. The origin 520s intermittently (Cloudflare)."""
    last: Exception | None = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": _UA})
            with urllib.request.urlopen(req, timeout=90) as response:
                body = response.read().decode("utf-8")
            if len(body) < 1000:
                raise RuntimeError(f"suspiciously small response ({len(body)} bytes)")
            return body
        except Exception as exc:  # noqa: BLE001 - retry any transport error
            last = exc
            detail = getattr(exc, "code", None) or (exc.reason if hasattr(exc, "reason") else None)
            print(f"fetch attempt {attempt + 1}/{retries} failed: {type(exc).__name__} {detail or exc}")
            time.sleep(8 + 4 * attempt)
    raise RuntimeError(f"fetch failed after {retries} attempts: {url} (last: {type(last).__name__} {last})") from last


def parse_export(text: str, season: str) -> list[dict]:
    """One season's plaintext export -> one doc per episode."""
    docs: list[dict] = []
    current: dict | None = None
    open_line: dict | None = None
    pending_ts: str | None = None

    def close_line() -> None:
        nonlocal open_line
        open_line = None

    for raw in text.splitlines():
        line = raw.replace(_NBSP, " ").rstrip()
        if not line.strip():
            close_line()
            continue
        header = _EP_HEADER.match(line.strip())
        if header:
            close_line()
            current = {
                "episode": header.group(1),
                "season": season,
                "title": header.group(2).strip(),
                "source": "",
                "credits": {},
                "lines": [],
            }
            docs.append(current)
            continue
        if current is None:
            continue
        if line.startswith("Source:"):
            current["source"] = line.split(":", 1)[1].strip()
            continue
        credit_field = next(
            (f for f in ("Translator", "Editor", "Timer", "QC") if line.startswith(f"{f}:")),
            None,
        )
        if credit_field is not None:
            value = line.split(":", 1)[1].strip()
            if value:
                current["credits"][credit_field.lower()] = value
            close_line()
            continue
        if line.startswith("(") and line.endswith(")"):
            # The archive's best-effort disclaimer paragraph.
            close_line()
            continue
        ts = _TS_LINE.match(line.strip())
        if ts:
            close_line()
            pending_ts = ts.group(1)
            open_line = {
                "ts": pending_ts,
                "speaker": ts.group(2).strip(),
                "text": "",
                "kind": "line",
            }
            current["lines"].append(open_line)
            continue
        sign = _SIGN.match(line.strip())
        if sign:
            close_line()
            current["lines"].append(
                {
                    "ts": pending_ts,
                    "speaker": None,
                    "text": sign.group(1).strip(),
                    "kind": "sign",
                }
            )
            continue
        if line[0].isspace() and open_line is not None:
            # Continuation of the open utterance.
            open_line["text"] += _join(open_line["text"], line.strip())
            continue
        if line[0].isspace() and current["lines"]:
            # Continuation of the previous SIGN entry (special-feature blocks
            # write their text indented under the sign line).
            current["lines"][-1]["text"] = _join(current["lines"][-1]["text"], line.strip())
            continue
        # Anything else inside the episode block is an unrecognised line;
        # keep it attached to the utterance it follows so nothing is lost.
        if open_line is not None:
            open_line["text"] += (" " if open_line["text"] else "") + line.strip()
        else:
            current["lines"].append(
                {"ts": pending_ts, "speaker": None, "text": line.strip(), "kind": "sign"}
            )
        close_line()

    for doc in docs:
        doc["n_lines"] = sum(1 for l in doc["lines"] if l["kind"] == "line")
    return docs


def _join(base: str, part: str) -> str:
    """Merge a continuation fragment. The archive spells out SFX one syllable
    per line (B / i / n / g); glue single letters, join words with a space.
    Subtitles sometimes rewrite the line in full on the next row ("Do you
    know..." / "Do you know how much...") — keep only the fuller text."""
    if not base:
        return part
    if len(base) >= 4 and base.lower() in part.lower():
        return part
    sep = "" if len(part) == 1 and part.isalpha() and base[-1].isalpha() else " "
    return base + sep + part


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def import_series(paths, refresh: bool = False) -> dict:
    """Download (hash-compare first), parse, and (re)build the store."""
    base: Path = paths.transcripts
    raw_dir = base / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    base.mkdir(parents=True, exist_ok=True)

    manifest_exports = []
    all_docs: list[dict] = []
    for export in EXPORTS:
        raw_path = raw_dir / f"{export['key']}.txt"
        if raw_path.exists() and not refresh:
            text = raw_path.read_text(encoding="utf-8")
        else:
            text = fetch(export["url"])
            raw_path.write_text(text, encoding="utf-8")
        data = text.encode("utf-8")
        docs = parse_export(text, export["season"])
        for doc in docs:
            stem = f"ep{doc['episode'][1:].zfill(3)}" if doc["episode"].startswith("E") else "movie"
            out = base / f"{stem}.json"
            out.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
            all_docs.append(doc)
        manifest_exports.append(
            {
                "url": export["url"],
                "sha256": _sha256(data),
                "season": export["season"],
                "episodes": [d["episode"] for d in docs],
            }
        )

    manifest = {
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "subs.yakuaru.com (SubArchivist - Anime Subtitle Archive)",
        "note": (
            "Fan-sub closed captions; speaker labels are the archive's best "
            "effort. Personal local corpus; source and sub-team credits are "
            "recorded per episode, any derived use must carry that provenance."
        ),
        "exports": manifest_exports,
    }
    (base / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    build_db(paths)
    return {
        "episodes": len(all_docs),
        "lines": sum(d["n_lines"] for d in all_docs),
        "signs": sum(len(d["lines"]) - d["n_lines"] for d in all_docs),
        "db": str(paths.transcripts_db),
    }


def _connect(paths) -> sqlite3.Connection:
    db: Path = paths.transcripts_db
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db)
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS lines(
            id INTEGER PRIMARY KEY,
            episode TEXT NOT NULL,
            season TEXT NOT NULL,
            ts TEXT,
            speaker TEXT,
            text TEXT NOT NULL,
            kind TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_lines_episode ON lines(episode);
        CREATE INDEX IF NOT EXISTS idx_lines_speaker ON lines(speaker);
        CREATE VIRTUAL TABLE IF NOT EXISTS lines_fts USING fts5(
            text, content='lines', content_rowid='id'
        );
        CREATE TRIGGER IF NOT EXISTS lines_ai AFTER INSERT ON lines BEGIN
            INSERT INTO lines_fts(rowid, text) VALUES (new.id, new.text);
        END;
        CREATE VIEW IF NOT EXISTS speakers AS
            SELECT COALESCE(speaker, '(sign)') AS speaker, COUNT(*) AS n
            FROM lines GROUP BY speaker;
        CREATE TABLE IF NOT EXISTS speaker_aliases(
            alias TEXT PRIMARY KEY, canonical TEXT NOT NULL
        );
        """
    )
    return conn


def build_db(paths) -> None:
    """Rebuild transcripts.db from the per-episode JSON (idempotent)."""
    base: Path = paths.transcripts_db
    if base.exists():
        base.unlink()
    conn = _connect(paths)
    rows: list[tuple] = []
    for file in sorted(paths.transcripts.glob("*.json")):
        if file.name == "manifest.json":
            continue
        doc = json.loads(file.read_text(encoding="utf-8"))
        for line in doc["lines"]:
            rows.append(
                (
                    doc["episode"],
                    doc["season"],
                    line["ts"],
                    line["speaker"],
                    line["text"],
                    line["kind"],
                )
            )
    conn.executemany("INSERT INTO lines(episode, season, ts, speaker, text, kind) VALUES (?,?,?,?,?,?)", rows)
    aliases = [(a, c) for a, c in VARIANT_MAP.items()]
    conn.executemany("INSERT OR REPLACE INTO speaker_aliases(alias, canonical) VALUES (?,?)", aliases)
    conn.commit()
    conn.close()


def load_episode(paths, episode: str) -> dict | None:
    stem = f"ep{episode.zfill(3)}" if episode.isdigit() else "movie"
    path = paths.transcripts / f"{stem}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def transcript_text(paths, episode: str, from_t: str | None, to_t: str | None) -> str:
    """Render one episode for reading, [ts] speaker: text."""
    doc = load_episode(paths, episode)
    if doc is None:
        return ""

    def key(ts: str | None) -> str:
        return ts or ""

    out = [f"{doc['episode']} - {doc['title']}  (source: {doc['source'] or 'unknown'})"]
    for line in doc["lines"]:
        ts, speaker, text, kind = line["ts"], line["speaker"], line["text"], line["kind"]
        if from_t and key(ts) < from_t:
            continue
        if to_t and key(ts) > to_t:
            continue
        if kind == "sign":
            out.append(f"  {ts or ''} [SIGN] {text}")
        else:
            out.append(f"[{ts}] {speaker}: {text}")
    return "\n".join(out)


def dialogue_lines(paths, character: str, episode: str | None, limit: int) -> list[tuple]:
    """A character's lines, alias-aware (same normalisation as the labels)."""
    canonical = normalize_speaker(character)
    conn = _connect(paths)
    try:
        query = "SELECT episode, ts, speaker, text FROM lines WHERE kind='line'"
        args: list = []
        if episode is not None:
            # The store keys episodes as the archive's header ids (E14, M1).
            ep_key = f"E{episode}" if episode.isdigit() else episode.upper()
            query += " AND episode=?"
            args.append(ep_key)
        aliases = [tuple(r) for r in conn.execute("SELECT alias, canonical FROM speaker_aliases")]
        names = {canonical, character}
        for alias, canon in aliases:
            if alias == canonical or canon == canonical:
                names.add(alias)
                names.add(canon)
        names.discard("")
        query += f" AND lower(speaker) IN ({','.join('?' for _ in names)})"
        query += " ORDER BY episode, ts"
        args.extend(n.lower() for n in sorted(names))
        if limit > 0:
            query += " LIMIT ?"
            args.append(limit)
        return conn.execute(query, args).fetchall()
    finally:
        conn.close()