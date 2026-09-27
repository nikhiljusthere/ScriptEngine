#!/usr/bin/env python3
"""B1 pilot — S6 subtitle-database CC/SDH fetch (owner decision 2026-09-27:
websites first, T-YT dropped for lack of speaker labels).

Tonight's tier reality (re-measured 2026-09-27, egress FI #214):
  * T-A7 addic7ed   200, anonymous download works (this tool)
  * T-OS opensub    403 -> valid free API key required (owner setup item)
  * T-SC subscene   403 -> bot-protected, needs the plan §1a ladder
  * T-PN podnapisi  000 -> blocked from this host

Pilot (bounded, ~6 titles, S01E01-focused):
  1. search.php?search=<q>  -> 302 -> /show/<id> (all-language table)
  2. parse rows: S|E|Title|Lang|Version|Completed|HI|Crctd|HD|DL
     (each file appears twice: HI=Y row + HI=· row)
  3. pick English rows, prefer HI=Y (SDH file), else English normal
  4. GET /updated/<a>/<fileid>/<variant> (text/srt, no login needed)
  5. store verbatim: series/marvel/cc/raw/<slug>.srt
     manifest row: series/marvel/cc/manifest.jsonl
     parsed model: series/marvel/cc/parsed/<slug>.json
        lines {t, speaker, text, kind: line|sign}  (JJK model)
  6. receipt: reports/marvel/receipts/b1/b1_pilot_<date>.json
     headline metric = fraction of dialogue lines carrying a speaker label
     (the owner's hard requirement), plus SDH sign-cue counts.

Egress budget: ~30 small requests, 1.5 s polite delay. Different host from
Fandom — zero interaction with the running F1/F3/F5 batch.
"""
import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CC = REPO / "series/marvel/cc"
RAW = CC / "raw"
PARSED = CC / "parsed"
MANIFEST = CC / "manifest.jsonl"
REC = REPO / "reports/marvel/receipts/b1"

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0 Safari/537.36"
BASE = "https://www.addic7ed.com"

PILOT = [
    # (catalog title, search query, season, episode)
    ("WandaVision", "wandavision", 1, 1),
    ("The Punisher", "the punisher", 1, 1),
    ("Iron Fist", "iron fist", 1, 1),
    ("Daredevil", "daredevil", 1, 1),
    ("Loki", "loki", 1, 1),
    ("Avengers: Endgame", "avengers endgame", None, None),  # movie probe
]

ROW = re.compile(r'<tr class="ep(?:even|odd)[^"]*">(.*?)</tr>', re.S)
TD = re.compile(r"<td[^>]*>(.*?)</td>", re.S)
DL_LINK = re.compile(r'href="(/updated/\d+/\d+/\d+)"')
STRIP = re.compile(r"<[^>]+>")
SRT_BLOCK = re.compile(
    r"^\s*(\d+)\s*\n\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,.]\d{3})\s*\n(.*?)(?=\n\n|\n\s*\d+\s*\n|$)",
    re.M | re.S,
)
SPEAKER = re.compile(
    r"^\[?([A-Z][A-Za-z' .&-]{1,25}?)\]?\s*:\s*(.*)$", re.S
)
SIGNISH = re.compile(r"^\s*(\[[^\]]{1,40}\]|\(.*\)|♪|♪.*♪|\*.*\*)\s*$")
CREDIT = re.compile(r"(addic7ed|synced|corrected by|subtitles by|subs by|www\.)", re.I)


def get(url, referer=None):
    from curl_cffi.requests import get as cget

    r = cget(
        url, impersonate="chrome136", timeout=30,
        headers={"User-Agent": UA, **({"Referer": referer} if referer else {})},
    )
    return r.status_code, r.text, r.url


def slugify(s):
    return re.sub(r"[^A-Za-z0-9]+", "_", s).strip("_").lower()


def parse_srt(text):
    """verbatim text -> [{t, speaker, text, kind}] + stats."""
    text = text.lstrip("\ufeff").replace("\r\n", "\n")
    lines = []
    for m in SRT_BLOCK.finditer(text):
        idx, t0, t1, body = m.group(1), m.group(2), m.group(3), m.group(4)
        raw_lines = [STRIP.sub("", l) for l in body.split("\n")]
        raw_lines = [re.sub(r"\s+$", "", l) for l in raw_lines if l.strip()]
        if not raw_lines:
            continue
        joined = "\n".join(raw_lines)
        speaker, text_l = None, joined
        sm = SPEAKER.match(joined.split("\n")[0]) if raw_lines else None
        if sm and not SIGNISH.match(sm.group(1)):
            speaker = sm.group(1).strip()
            rest = sm.group(2).strip()
            text_l = "\n".join([rest] + raw_lines[1:]) if rest else "\n".join(raw_lines[1:])
        if not text_l.strip():
            continue
        is_sign = bool(
            CREDIT.search(joined)
            or SIGNISH.match(raw_lines[0])
            or all(SIGNISH.match(l) for l in raw_lines if l.strip())
            or "♪" in joined
        )
        lines.append(
            {
                "t": [t0.replace(",", "."), t1.replace(",", ".")],
                "speaker": speaker,
                "text": text_l,
                "kind": "sign" if is_sign else "line",
            }
        )
    n_lines = sum(1 for l in lines if l["kind"] == "line")
    n_labeled = sum(1 for l in lines if l["kind"] == "line" and l["speaker"])
    n_sign = sum(1 for l in lines if l["kind"] == "sign")
    stats = {
        "srt_cues": len(lines),
        "dialogue_cues": n_lines,
        "speaker_labeled": n_labeled,
        "speaker_label_rate": round(n_labeled / n_lines, 3) if n_lines else None,
        "sign_cues": n_sign,
    }
    return lines, stats


def parse_show_page(html):
    rows = []
    for row_html in ROW.findall(html):
        tds = TD.findall(row_html)
        if len(tds) < 9:
            continue
        clean = [STRIP.sub("", c).replace("&#10004;", "Y").replace("&#10008;", "N") for c in tds]
        clean = [re.sub(r"\s+", " ", c).strip() for c in clean]
        dl = DL_LINK.search(row_html)
        if not dl:
            continue
        rows.append(
            {
                "s": clean[0], "e": clean[1], "title": clean[2],
                "lang": clean[3], "version": clean[4], "completed": clean[5],
                "hi": clean[6], "corrected": clean[7], "hd": clean[8],
                "url": BASE + dl.group(1),
            }
        )
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="comma-separated catalog titles to run")
    a = ap.parse_args()
    sel = [p for p in PILOT if not a.only or p[0] in a.only.split(",")]

    RAW.mkdir(parents=True, exist_ok=True)
    PARSED.mkdir(parents=True, exist_ok=True)
    REC.mkdir(parents=True, exist_ok=True)

    receipt = {
        "date": str(datetime.now().date()),
        "tier": "T-A7 (addic7ed)",
        "decision": ("owner 2026-09-27: S6 websites primary; T-YT dropped "
                     "(no speaker labels)"),
        "egress_note": ("different host from Fandom; zero interaction with "
                        "the running F1/F3/F5 batch"),
        "titles": [],
    }

    for title, query, season, ep in sel:
        entry = {"catalog_title": title, "query": query, "season": season,
                 "episode": ep}
        try:
            code, html, final = get(f"{BASE}/search.php?search={query.replace(' ', '+')}")
            time.sleep(1.5)
            entry["search_status"] = code
            entry["search_final_url"] = final
            if "/show/" not in final:
                entry["result"] = "no show page (movie/unknown tier gap)"
                receipt["titles"].append(entry)
                continue
            rows = parse_show_page(html)
            entry["show_page"] = final
            entry["rows_total"] = len(rows)
            cand = [r for r in rows if r["lang"] == "English"
                    and (season is None or r["s"] == str(season))
                    and (ep is None or r["e"] == str(ep))]
            hi = [r for r in cand if r["hi"] == "Y"]
            pick = (hi or cand)
            if not pick:
                entry["result"] = "no english row for target"
                receipt["titles"].append(entry)
                continue
            row = pick[0]
            entry["picked"] = {k: row[k] for k in
                               ("s", "e", "title", "version", "hi", "url")}
            dcode, srt, durl = get(row["url"], referer=final)
            time.sleep(1.5)
            if dcode != 200 or not srt.strip():
                entry["result"] = f"download failed ({dcode})"
                receipt["titles"].append(entry)
                continue
            slug = slugify(f"{title}_s{row['s']}_e{row['e']}"
                           if season else title)
            (RAW / f"{slug}.srt").write_text(srt, encoding="utf-8")
            lines, stats = parse_srt(srt)
            (PARSED / f"{slug}.json").write_text(
                json.dumps(
                    {"title": title, "show": row["title"], "s": row["s"],
                     "e": row["e"], "source": "T-A7 addic7ed",
                     "version": row["version"], "hi": row["hi"] == "Y",
                     "url": row["url"], "lines": lines},
                    ensure_ascii=False, indent=1))
            m = {
                "title": title, "show": row["title"], "s": row["s"],
                "e": row["e"], "language": row["lang"],
                "version": row["version"], "hi": row["hi"] == "Y",
                "url": row["url"], "sha256": hashlib.sha256(
                    srt.encode("utf-8")).hexdigest(),
                "credits": next((l["text"] for l in lines
                                  if CREDIT.search(l["text"])), None),
                "source": "T-A7 addic7ed",
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "stats": stats,
            }
            with MANIFEST.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(m, ensure_ascii=False) + "\n")
            entry["result"] = "ok"
            entry["manifest"] = {k: m[k] for k in
                                 ("hi", "version", "sha256", "stats", "credits")}
        except Exception as ex:  # noqa: BLE001 - pilot: record and continue
            entry["result"] = f"error: {type(ex).__name__}: {ex}"
        receipt["titles"].append(entry)
        print(json.dumps(entry, ensure_ascii=False)[:400], flush=True)

    rec_path = REC / f"b1_pilot_{datetime.now().date()}.json"
    rec_path.write_text(json.dumps(receipt, indent=1), encoding="utf-8")
    print(f"\n[b1-pilot] receipt -> {rec_path}")
    for t in receipt["titles"]:
        if t.get("manifest"):
            st = t["manifest"]["stats"]
            print(f"  {t['catalog_title']:22s} {st['dialogue_cues']:5d} dialogue "
                  f"{st['speaker_labeled']:5d} labeled "
                  f"({st['speaker_label_rate']}) {st['sign_cues']:4d} sign")
        else:
            print(f"  {t['catalog_title']:22s} {t.get('result')}")


if __name__ == "__main__":
    main()