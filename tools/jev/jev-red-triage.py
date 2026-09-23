#!/usr/bin/env python3
"""Red-row triage for the CSM 486-bank (23 reds = 7 D7 holdouts + 16 floor).

For every red row, the census `expect` items are searched verbatim (case- and
whitespace-normalized) across the crawled CSM wiki in facts.db. This is the
model-free core of claim_check's citation question — "does a crawled page
support the gold?" — without needing the bank's `sources` field, which the
census rows do not carry:

- item found on the row's subject page  -> gold supported; the red is a
  RETRIEVAL gap (the engine should have surfaced what the page already has).
- item found only on other pages        -> gold supported but NOT on the
  subject page; a subject-routing / focus defect candidate.
- item found on no crawled page         -> gold NOT supported by the corpus;
  an EXTRACTION or crawl gap (Phase-2 territory), or a bank defect.

The database check is the record; nothing here grades or writes the bank.
An optional `--model` pass asks the local fast lane (via the Jev gateway)
whether the closest pages support items that exact-match missed — a
paraphrase net, clearly marked as model-judged.

Usage:
    python tools/jev/jev-red-triage.py                 # all 23 rows
    python tools/jev/jev-red-triage.py --model          # + fast-lane paraphrase net
    python tools/jev/jev-red-triage.py --out report.md
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import urllib.request
from pathlib import Path

# 23 reds: 7 D7 holdouts (plan/CSM_100_CLOSE.md) + 16 floor rows (union of the
# D7-window leg grades, reports/csm/receipts/d7_window/{LEGA,LEGB}_p23.log).
REDS = [
    # holdouts
    ("csm-dim-chap-01", "holdout", "numeric collision"),
    ("csm-dim-org-03", "holdout", "Prophecy / Nostradamus"),
    ("csm-dim-org-05", "holdout", "Tokyo Div 5"),
    ("csm-dim-org-06", "holdout", "Yakuza"),
    ("csm-dim-vol-10", "holdout", "guidebook"),
    ("csm-abl-pool-140", "holdout", "Body Control width"),
    ("csm-abl-pool-358", "holdout", "Biru Ken width"),
    # floor
    ("csm-dim-arcn-02", "floor", "arc-narrative"),
    ("csm-dim-arcn-03", "floor", "arc-narrative"),
    ("csm-dim-arcn-04", "floor", "arc-narrative"),
    ("csm-dim-arcn-06", "floor", "arc-narrative"),
    ("csm-dim-arcn-08", "floor", "arc-narrative"),
    ("csm-dim-arcn-10", "floor", "arc-narrative"),
    ("csm-dim-state-02", "floor", "state-over-time"),
    ("csm-dim-state-03", "floor", "state-over-time"),
    ("csm-dim-state-08", "floor", "state-over-time"),
    ("csm-dim-state-09", "floor", "state-over-time"),
    ("csm-dim-abl-01", "floor", "abilities"),
    ("csm-dim-abl-02", "floor", "abilities"),
    ("csm-dim-abl-09", "floor", "abilities"),
    ("csm-dim-caus-03", "floor", "causality"),
    ("csm-abl-pool-149", "floor", "width"),
    ("csm-abl-pool-252", "floor", "width"),
]

JEV_URL = "http://127.0.0.1:8018/v1/systemone"


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip().lower()


def repos() -> list[Path]:
    return [Path.home() / "ScriptEngine", Path.cwd()]


def load_census(repo: Path) -> dict:
    out = {}
    for line in (repo / "reports/csm/census_widened_csm_results.jsonl").open(encoding="utf-8"):
        d = json.loads(line)
        out[d["id"]] = d
    return out


def load_sections(repo: Path):
    con = sqlite3.connect(f"file:{repo / 'series/csm/facts.db'}?mode=ro", uri=True)
    try:
        rows = con.execute(
            "SELECT d.title, s.title, s.text FROM sections s "
            "JOIN documents d ON d.id = s.document_id WHERE s.text IS NOT NULL"
        ).fetchall()
    finally:
        con.close()
    # (doc, section, normalized text)
    return [(doc, sec, norm(text or "")) for doc, sec, text in rows]


def page_of_subject(sections, subject: str) -> set[str]:
    """Document titles that are the subject's own page(s)."""
    subj = norm(subject or "")
    if not subj:
        return set()
    return {doc for doc, _sec, _t in sections if norm(doc) == subj}


def find_items(item: str, sections, pages: set[str]) -> dict:
    """Exact normalized-substring search of an item across all sections."""
    needle = norm(item)
    if len(needle) < 6:  # too short to be a reliable verbatim signal
        return {"found_docs": [], "found_sections": [], "too_short": True}
    probe = needle[:120]  # items are long quoted sentences; 120 chars is enough
    found_docs: list[str] = []
    found_sections: list[str] = []
    for doc, sec, ntext in sections:
        if probe in ntext:
            found_docs.append(doc)
            found_sections.append(f"{doc} / {sec}" if sec and sec != doc else doc)
    return {"found_docs": found_docs, "found_sections": found_sections, "too_short": False}


def model_support(item: str, sections, pages, k: int = 3) -> dict:
    """Fast-lane paraphrase net over the k closest pages (by shared words)."""
    words = {w for w in re.findall(r"[a-z]{4,}", norm(item))
             if w not in {"what", "during", "which", "that", "this", "with", "have", "does"}}
    scored, seen_docs = [], set()
    for doc, sec, ntext in sections:
        if doc in seen_docs or not words:
            continue
        overlap = sum(1 for w in words if w in ntext)
        if overlap >= max(2, len(words) // 3):
            scored.append((overlap, doc, sec, ntext))
            seen_docs.add(doc)
    scored.sort(key=lambda t: -t[0])
    verdicts = []
    question = "Does this section text support or state the item (possibly paraphrased)?"
    for _ov, doc, sec, ntext in scored[:k]:
        body = json.dumps({"model": "jev-latest",
                           "state": {"item": item, "text": ntext[:2_000]},
                           "questions": {"q": {"type": "noul", "instructions": question}}}).encode()
        try:
            req = urllib.request.Request(JEV_URL, data=body, headers={
                "Content-Type": "application/json", "Authorization": "Bearer local"})
            with urllib.request.urlopen(req, timeout=120) as r:
                p = json.loads(r.read())["answers"]["q"]["noul"]
            verdicts.append({"page": doc, "p": round(p, 3), "supports": p >= 0.3})
        except Exception as e:
            verdicts.append({"page": doc, "error": str(e)[:80]})
    return {"candidates": verdicts}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--model", action="store_true", help="fast-lane paraphrase net for exact-match misses")
    ap.add_argument("--out", default="csm-red-triage", help="report base name (writes .md + .jsonl in cwd)")
    args = ap.parse_args(argv)

    repo = next((p for p in repos() if (p / "series/csm/facts.db").exists()), None)
    if not repo:
        print("no ~/ScriptEngine or ./series/csm/facts.db found", file=sys.stderr)
        return 1
    census = load_census(repo)
    sections = load_sections(repo)
    print(f"loaded {len(sections)} sections; judging {len(REDS)} rows", file=sys.stderr)

    rows = []
    for rid, group, label in REDS:
        c = census.get(rid)
        if not c:
            rows.append({"id": rid, "group": group, "label": label, "verdict": "no_census_row"})
            continue
        items = c.get("expect") or []
        subject = c.get("subject") or ""
        subj_pages = page_of_subject(sections, subject)
        item_rows = []
        for item in items:
            f = find_items(item, sections, subj_pages)
            row = {"item": item[:120], **f}
            if not f["found_docs"] and args.model and not f["too_short"]:
                row["model"] = model_support(item, sections, subj_pages)
            if f["found_docs"]:
                on_subj = subj_pages and (set(f["found_docs"]) & subj_pages)
                row["triage"] = "supported_on_subject_page" if on_subj else "supported_on_other_pages"
            elif row.get("model", {}).get("candidates"):
                sup = [v for v in row["model"]["candidates"] if v.get("supports")]
                row["triage"] = "model_says_supported" if sup else "not_supported"
            elif f["too_short"]:
                row["triage"] = "too_short_to_probe"
            else:
                row["triage"] = "not_in_corpus"
            item_rows.append(row)
        n_ok = sum(1 for r in item_rows if r["triage"].startswith(("supported", "model_says")))
        if not item_rows:
            verdict = "no_expect_items"
        elif n_ok == len(item_rows):
            verdict = "gold_supported (engine/retrieval gap)"
        elif n_ok == 0:
            verdict = "gold_unsupported (extraction/crawl gap or bank defect)"
        else:
            verdict = "mixed"
        rows.append({"id": rid, "group": group, "label": label, "q": c.get("q"), "subject": subject,
                     "items": item_rows, "verdict": verdict})

    base = Path(args.out)
    base.with_suffix(".jsonl").write_text(
        "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")

    lines = ["# CSM red-row triage (23 reds) — gold-support vs crawled corpus",
             "", "Model-free DB check (record) + optional fast-lane paraphrase net. "
             "Generated by tools/jev/jev-red-triage.py.", ""]
    for r in rows:
        if r.get("verdict") == "no_census_row":
            lines.append(f"- **{r['id']}** — no census row; check the ledger.")
            continue
        lines.append(f"## {r['id']} ({r['group']} · {r['label']})")
        lines.append(f"Q: {r.get('q')} (subject: {r.get('subject')})")
        for ir in r["items"]:
            mark = "✓" if ir["triage"].startswith(("supported", "model_says")) else "✗"
            where = ", ".join(sorted(set(ir["found_docs"]))[:4]) or (
                "model: " + ", ".join(f"{v['page']} p={v.get('p')}" for v in ir.get("model", {}).get("candidates", [])) or "nowhere")
            lines.append(f"  {mark} {ir['item'][:80]} — {where}")
        lines.append(f"  → **{r['verdict']}**")
        lines.append("")
    lines.append("## Totals")
    for v in ("gold_supported (engine/retrieval gap)", "gold_unsupported (extraction/crawl gap or bank defect)", "mixed"):
        lines.append(f"- {v}: {sum(1 for r in rows if r.get('verdict') == v)}")
    md = "\n".join(lines)
    base.with_suffix(".md").write_text(md, encoding="utf-8")
    print(md)
    print(f"\nreports: {base}.md / {base}.jsonl", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())