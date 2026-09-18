"""D6 frozen P/T/A triage + --pages frozen list (council #35, D39).

One-off offline tool: classifies the 134 setrel + 6 abl census rows with
the council's mechanical test (expected-set members in the facts DB [P] /
in the stored-crawl wikitext [T] / absent [A]) and freezes the union page
list for the D6 targeted-extraction window. Writes:

  reports/csm/D6_PTA_TRIAGE.jsonl   one line per row (134 + 6) + _meta
  reports/csm/D6_PAGES_FROZEN.txt   one corpus title per line ('#' ignored)
  reports/csm/D6_PTA_TRIAGE.md      method one-pager + counts

Deterministic; no model, no network; rerun reproduces byte-identical output.
FROZEN the moment it runs — the output is the pre-model-call artifact.
"""

import json
import re
import sqlite3
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "series" / "csm" / "facts.db"
WIKI = ROOT / "series" / "csm" / "wikitext"
BANK = ROOT / "questions"
OUT = ROOT / "reports" / "csm"

LINK = re.compile(r"\[\[([^\]|]+)")


def norm(s) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().replace("\u2019", "'")
    return re.sub(r"\s+", " ", s).strip()


def load_db():
    db = sqlite3.connect(DB)
    in_db = set()
    for table, col in (
        ("aliases", "alias"),
        ("nodes", "name"),
        ("nodes", "label"),
        ("relations", "other"),
        ("relations", "character"),
        ("abilities", "name"),
    ):
        for (v,) in db.execute(f"select {col} from {table}"):
            in_db.add(norm(v))
    slug2title = {
        u.rsplit("/wiki/", 1)[1].lower(): t
        for t, u in db.execute("select title, url from documents")
    }
    title2canon = {norm(t): t for (t,) in db.execute("select title from documents")}
    # census `subject` strings are mangled in places ("Aging Devil S Victim" for
    # "Aging Devil's Victim", "World War Ii Devil" for "World War II Devil");
    # fall back to an alnum-only match so A-row pages resolve to real titles.
    alnum2canon = {re.sub(r"[^a-z0-9]+", "", norm(t)): t for (t,) in db.execute("select title from documents")}
    db.close()
    return in_db, slug2title, title2canon, alnum2canon


def page_bodies():
    bodies = {}
    for p in sorted(WIKI.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        body = (d.get("lead") or "") + "\n" + "\n".join(
            (s.get("text") or "") for s in d.get("sections", [])
        )
        bodies[p.stem] = body
    return bodies


def member_states(members, title, in_db, bodies):
    """members: list of (item, [aliases]). P=db, T=wikitext, A=absent."""
    body = bodies.get(title)
    if body is None:
        return {m: "absent" for m, _ in members}
    links = {norm(x) for x in LINK.findall(body)}
    nbody = norm(body)
    out = {}
    for item, aliases in members:
        names = [norm(item)] + [norm(a) for a in aliases]
        names = [n for n in names if n]
        if any(n in in_db for n in names):
            out[item] = "db"
        elif any(n in links for n in names):
            out[item] = "wikitext-wikilink"
        elif any(n in nbody for n in names):
            out[item] = "wikitext-mention"
        else:
            out[item] = "absent"
    return out


def main():
    in_db, slug2title, title2canon, alnum2canon = load_db()
    bodies = page_bodies()

    def resolve_page(s):
        """corpus title for a (possibly mangled) census subject; raw string if unmatched."""
        n = norm(s)
        t = title2canon.get(n)
        if t:
            return t
        t = alnum2canon.get(re.sub(r"[^a-z0-9]+", "", n))
        return t or s

    census = [json.loads(l) for l in open(OUT / "census_v1_floor_triage.jsonl")]
    setrel = [r for r in census if r["bucket"] == "setrel"]
    abl = [r for r in census if r["bucket"] == "abl"]
    assert len(setrel) == 134 and len(abl) == 6, (len(setrel), len(abl))

    widened = [json.loads(l) for l in open(OUT / "census_widened_csm_results.jsonl")]
    red_subjects = sorted({r["subject"] for r in widened if r["verdict"] == "MECH_RED"})

    rows = []
    a_pages = set()

    for r in setrel:
        slug = r["id"].split("setrel-", 1)[1]
        subject = r["subject"]
        bfile = BANK / f"_csm_page_{slug}.json"
        members, seen = [], set()
        if bfile.exists():
            b = json.loads(bfile.read_text(encoding="utf-8-sig"))
            for q in b.get("questions", []):
                if q.get("kind") == "set" or q.get("expect_mode") == "roster":
                    for a in q.get("answer", []):
                        key = norm(a.get("item", ""))
                        if key and key not in seen:
                            seen.add(key)
                            members.append((a["item"], a.get("aliases") or []))
        states = member_states(members, subject, in_db, bodies) if members else {}
        vals = list(states.values())
        if not vals:
            cls = "NA"
        elif any(v == "absent" for v in vals):
            cls = "A"
        elif any(v in ("wikitext-wikilink", "wikitext-mention") for v in vals):
            cls = "T"
        else:
            cls = "P"
        page = resolve_page(subject)
        if cls == "A":
            a_pages.add(page)
        rows.append(
            {
                "id": r["id"],
                "bucket": "setrel",
                "subject": subject,
                "page": page,
                "members": len(members),
                "states": states,
                "row_class": cls,
                "evidence": (
                    f"bank={bfile.name} set-members={len(members)} "
                    f"db={sum(1 for v in vals if v == 'db')} "
                    f"wiki={sum(1 for v in vals if v.startswith('wikitext'))} "
                    f"absent={sum(1 for v in vals if v == 'absent')}"
                ),
            }
        )

    for r in abl:
        subject = r["subject"]
        abl_name = r["expect"][0]
        n = norm(abl_name)
        if n in in_db:
            cls = "P"
        else:
            body = bodies.get(subject, "")
            links = {norm(x) for x in LINK.findall(body)}
            if n in links or n in norm(body):
                cls = "T"
            else:
                cls = "A"
        page = resolve_page(subject)
        if cls == "A":
            a_pages.add(page)
        rows.append(
            {
                "id": r["id"],
                "bucket": "abl",
                "subject": subject,
                "page": page,
                "members": 1,
                "states": {abl_name: "db" if cls == "P" else ("wikitext" if cls == "T" else "absent")},
                "row_class": cls,
                "evidence": f"ability={abl_name!r} in_db={'abilities/aliases/nodes' if cls == 'P' else 'no'}",
            }
        )

    out_lines = [
        {
            "_meta": {
                "frozen": "pre-model-call artifact of the D6 window (council #35 D39)",
                "method": (
                    "setrel: expected set = union of kind=set/roster answer items "
                    "(+aliases) in questions/_csm_page_<slug>.json; per-member state "
                    "P = member/alias in facts DB (aliases, nodes, relations, "
                    "abilities), T = not in DB but in the subject page's stored "
                    "wikitext (wikilink target or plain mention), A = absent from "
                    "both; row A if any member A, else T if any T, else P; NA when "
                    "the page's bank carries no set question. abl: expect[0] is the "
                    "ability name, same P/T/A test. P,T -> named D7 limit "
                    "'single-candidate enumeration width (retrieval layer)'; "
                    "A -> extraction-gated, subject page in the frozen list (A20 "
                    "void criterion (c) bounds the risk)."
                ),
                "counts": {
                    k: sum(1 for x in rows if x["row_class"] == k)
                    for k in ("P", "T", "A", "NA")
                },
            }
        }
    ]
    out_lines.extend(rows)
    (OUT / "D6_PTA_TRIAGE.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in out_lines) + "\n",
        encoding="utf-8",
    )

    pages = set()
    unmatched, fuzzy = [], []
    for s in red_subjects:
        t = resolve_page(s)
        pages.add(t)
        if norm(s) not in title2canon:
            (fuzzy if re.sub(r"[^a-z0-9]+", "", norm(s)) in alnum2canon else unmatched).append(s)
    pages |= a_pages
    pages.add("Yoru")
    pages.add("Asa Mitaka")
    lines = [
        "# D6 frozen --pages list (council #35 D39), generated by tools/csm/d6_pta_triage.py",
        f"# union of {{69 p23 red subjects ({len(red_subjects)} distinct), setrel A pages "
        f"({len(a_pages)}), 2 CONTENT rows}}; one title per line below",
    ]
    lines += sorted(pages)
    (OUT / "D6_PAGES_FROZEN.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    counts = {k: sum(1 for x in rows if x["row_class"] == k) for k in ("P", "T", "A", "NA")}
    a_rows = [x["id"] for x in rows if x["row_class"] == "A"]
    (OUT / "D6_PTA_TRIAGE.md").write_text(
        "\n".join(
            [
                "# D6 frozen P/T/A triage (council #35 D39)",
                "",
                "Offline, deterministic derivation; frozen before any model call. "
                "Source rows: `census_v1_floor_triage.jsonl` (134 setrel + 6 abl). "
                "Expected sets: per-page banks `questions/_csm_page_<slug>.json` "
                "(kind=set answers, verified 2026-09-09 against raw wikitext). "
                "Member state test: P = in facts DB (aliases/nodes/relations/"
                "abilities, NFKC+case-normalized), T = not in DB but in the "
                "subject page's stored wikitext (wikilink target or mention), "
                "A = absent from both. Row class: A if any member absent, else T "
                "if any member only-in-wikitext, else P; NA when the page's bank "
                "carries no set question (residual is fact/dim-type, owned by the "
                "dim/floor buckets). P/T -> named D7 limit, owning leg D7, retest "
                "via post-rebuild page-run; A -> extraction-gated, subject page "
                "in `D6_PAGES_FROZEN.txt` (A20 void criterion (c): an A-row still "
                "red after D6 voids that row's receipt only).",
                "",
                f"Counts (140 rows): P={counts['P']} T={counts['T']} A={counts['A']} "
                f"NA={counts['NA']}",
                "",
                f"A rows ({len(a_rows)}): " + (", ".join(a_rows) if a_rows else "none"),
                "",
                f"Frozen page list: `D6_PAGES_FROZEN.txt` "
                f"({len(pages)} titles; {len(fuzzy)} red subjects resolved to a "
                f"corpus page via alnum-fuzzy match (mangled census subjects, "
                f"e.g. apostrophe-as-' S '): {fuzzy if fuzzy else 'none'}; "
                f"{len(unmatched)} with no corpus page at all: "
                f"{unmatched if unmatched else 'none'}) — the flag "
                "intersects with the scope queue, so non-corpus titles are "
                "harmlessly dropped at extraction.",
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    print("rows:", len(rows), "counts:", counts)
    print("a pages:", sorted(a_pages))
    print("list size:", len(pages), "| unmatched subjects:", unmatched)


if __name__ == "__main__":
    main()