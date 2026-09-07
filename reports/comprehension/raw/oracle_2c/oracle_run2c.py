"""Phase 2C: re-run plan/ORACLE_v1.yaml under `auto` routing and show the change.

Same held-out oracle and same scorer as 1A (read-only; its sha256 is re-verified
at start). 2C is the gate after 2A (battle outcomes) and 2-prep (fact floor): the
A-group should move from 0/4, the B-group's fact-floor items should move, and the
F-group is unchanged (2B was halted because F1/F2 already passed at 1A). Full
bundles are dumped to /tmp/oracle_2c_bundles/ for audit; per-item detail and a
machine-readable summary are written beside this file for the record.
"""

import hashlib
import json
import pathlib
import re
import urllib.request

import yaml

ORACLE = pathlib.Path("/home/goblin/ScriptEngine/plan/ORACLE_v1.yaml")
EXPECTED_SHA = "a788fa29652a58152edf0f2ce16caea626db35d7e4463ec66176b5635a15935e"
API = "http://127.0.0.1:8000/context"
DUMP_DIR = pathlib.Path("/tmp/oracle_2c_bundles")
OUT_DIR = pathlib.Path(__file__).parent
RESULTS = OUT_DIR / "oracle_2c_results.txt"
SUMMARY = OUT_DIR / "oracle_2c_summary.json"

# The engine's own marker grammar (retrieve/citations.py:42): a citation is an
# optional work prefix + Chapter/Episode/Volume + number, with an optional
# ", Episode N" tail. Only these are stripped before the contains check.
_MARKER = re.compile(
    r"\((?:[A-Z][A-Za-z']*\s+)?(?:Chapter|Episode|Volume)\s+[0-9.\-]+(?:,\s*[^)]*)?\)"
)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def strip_citations(text: str) -> str:
    return _MARKER.sub("", text)


def post(query: str) -> dict:
    body = json.dumps({"series": "jjk", "query": query, "mode": "auto"}).encode()
    req = urllib.request.Request(API, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=300) as resp:
        return json.loads(resp.read())


def bundle_text(bundle: dict) -> str:
    """Everything a writer reading the bundle could quote, as one text."""
    parts = []
    for beat in bundle.get("beats") or []:
        parts.append(beat.get("text", ""))
    for member in bundle.get("members") or []:
        for key, val in member.items():
            if isinstance(val, str):
                parts.append(val)
    for passage in bundle.get("passages") or []:
        parts.append(passage.get("text", ""))
    for fact in bundle.get("facts") or []:
        parts.append(f"{fact.get('field', '')}: {fact.get('value', '')}")
    for edge in bundle.get("relations") or []:
        parts.append(f"{edge.get('source', '')} {edge.get('label', '')} {edge.get('target', '')}")
    return "\n".join(parts)


def locate_section(bundle: dict, page: str, section: str) -> bool:
    want_page, want_sec = norm(page), norm(section)
    pools = []
    for beat in bundle.get("beats") or []:
        pools.append((beat.get("doc_title"), beat.get("breadcrumb")))
    for member in bundle.get("members") or []:
        pools.append((member.get("doc_title") or member.get("name"), member.get("breadcrumb")))
    for passage in bundle.get("passages") or []:
        pools.append((passage.get("doc_title"), passage.get("title")))
    return any(norm(p) == want_page and norm(s) == want_sec for p, s in pools)


def fact_values(bundle: dict, subject: str) -> list:
    return [
        f"{f.get('field')}: {f.get('value')}"
        for f in bundle.get("facts") or []
        if norm(f.get("entity", "")) == norm(subject)
    ]


def check_item(item: dict, bundle: dict) -> dict:
    text = norm(strip_citations(bundle_text(bundle)))
    kind = item["check"]
    detail = {}
    if kind == "contains":
        detail["contains"] = norm(item["ground_truth"]) in text
        ok = detail["contains"]
    elif kind == "value":
        subject = item["source_page"]
        values = fact_values(bundle, subject)
        detail["subject"] = subject
        detail["served_values"] = values
        detail["value_match"] = any(norm(v.split(": ", 1)[-1]) == norm(item["ground_truth"]) for v in values)
        ok = detail["value_match"]
    elif kind == "section":
        detail["section_present"] = locate_section(bundle, item["source_page"], item["source_section"])
        ok = detail["section_present"]
    elif kind == "distinguishes":
        has_gt = norm(item["ground_truth"]) in text
        has_confuse = norm(item["must_not_confuse_with"]) in text
        detail["has_ground_truth"] = has_gt
        detail["confused_with_other"] = has_confuse
        ok = has_gt and not has_confuse
    return {"ok": ok, **detail}


def main() -> None:
    raw = ORACLE.read_bytes()
    actual_sha = hashlib.sha256(raw).hexdigest()
    assert actual_sha == EXPECTED_SHA, f"oracle sha mismatch: {actual_sha}"
    print(f"oracle sha256 verified: {actual_sha}")
    doc = yaml.safe_load(raw)
    items = doc["items"]
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    by_cat: dict[str, list] = {}
    surprises = []
    lines = []
    summary_rows = []
    header = (f"oracle sha256 verified: {actual_sha}\n\n"
              f"{'ID':<4} {'category':<12} {'expect':<5} {'result':<6} {'door':<9} detail\n")
    lines.append(header)
    for item in items:
        bundle = post(item["question"])
        (DUMP_DIR / f"{item['id']}.json").write_text(json.dumps(bundle, indent=2))
        verdict = check_item(item, bundle)
        routed = (bundle.get("routed") or {})
        door = routed.get("mode", bundle.get("mode"))
        result = "PASS" if verdict["ok"] else "FAIL"
        expect = item.get("expect")
        extra = {k: v for k, v in verdict.items() if k != "ok"}
        served = []
        for beat in (bundle.get("beats") or bundle.get("members") or [])[:3]:
            src = beat.get("breadcrumb") or beat.get("title") or beat.get("name")
            served.append(f"{src} :: {norm(beat.get('text', ''))[:110]}")
        facts = [f"{f['field']}: {f['value']}" for f in (bundle.get("facts") or [])[:5]]
        block = [f"{item['id']:<4} {item['category']:<12} {str(expect):<5} {result:<6} {door:<9} {extra}"]
        block.append(f"     served: {' | '.join(served) or '(nothing)'}")
        if facts:
            block.append(f"     facts: {' | '.join(facts)}")
        if expect and (verdict["ok"] != (expect == "pass")):
            surprises.append((item["id"], expect, result))
            block.append(f"   <-- SURPRISE (expected {expect})")
        block.append("")
        lines.append("\n".join(block))
        summary_rows.append({
            "id": item["id"], "category": item["category"], "expect": expect,
            "result": result, "door": door, "detail": extra,
        })
        by_cat.setdefault(item["category"], []).append((item, result, door))
        print("\n".join(block))

    lines.append("\n=== totals by category ===\n")
    cat_totals = {}
    for cat, rows in by_cat.items():
        passed = sum(1 for _, r, _ in rows if r == "PASS")
        cat_totals[cat] = {"passed": passed, "total": len(rows)}
        detail = ", ".join(f"{i}={r}({d})" for i, r, d in rows)
        lines.append(f"{cat:<12} {passed}/{len(rows)}  {detail}")
    lines.append("\n=== surprises vs recorded expect ===\n")
    for sid, exp, got in surprises:
        lines.append(f"{sid}: expected {exp}, got {got}")
    if not surprises:
        lines.append("(none)")

    RESULTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    SUMMARY.write_text(json.dumps(
        {"sha256": actual_sha, "category_totals": cat_totals,
         "surprises": [{"id": s, "expect": e, "got": g} for s, e, g in surprises],
         "rows": summary_rows},
        indent=2), encoding="utf-8")
    print("\n=== totals by category ===")
    for cat, tot in cat_totals.items():
        print(f"{cat:<12} {tot['passed']}/{tot['total']}")
    print("\n=== surprises vs recorded expect ===")
    for sid, exp, got in surprises:
        print(f"{sid}: expected {exp}, got {got}")
    if not surprises:
        print("(none)")
    print(f"\nresults: {RESULTS}\nsummary: {SUMMARY}")


if __name__ == "__main__":
    main()