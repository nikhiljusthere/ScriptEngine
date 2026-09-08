#!/usr/bin/env python3
"""Score the CSM relations bank (questions/_csm_relations.json) against the
live server. CSM-specific by the standing rule: the underscore-prefixed file
stays out of the official canon bank (`questions.load_all` skips `_` files),
so this runner is how the bank is validated. Reuses canon_gold's HTTP ask and
normalisation — no duplicated logic.

A relation-set question's expected items are the other party's names (the
wiki's Relationships subheadings). A question passes when every expected name
appears as a source or target in the bundle's `relations` (word-boundary,
alias-aware). Raw receipt, never a "pass rate" prose.

Run:  scriptengine/.venv/bin/python tools/csm/validate_relations.py
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO))

from scriptengine.eval.canon_gold import ask, norm, present  # noqa: E402

BANK = REPO / "questions/_csm_relations.json"
RECEIPT = REPO / "reports/csm/CSM1B_RELATIONS_BANK.md"


def expected_names(q: dict) -> list[tuple[str, list[str]]]:
    """(item, aliases) pairs a returned relation must match."""
    out = []
    for a in q.get("answer", []):
        out.append((a["item"], a.get("aliases") or []))
    return out


def relation_names(body: dict) -> set[str]:
    names = set()
    for rel in body.get("relations") or []:
        for key in ("source", "target"):
            v = rel.get(key)
            if isinstance(v, str) and v:
                names.add(norm(v))
    return names


def main() -> int:
    data = json.loads(BANK.read_text())
    lines = ["# CSM-1b — relations bank validation (2026-09-08)", "",
             f"Bank: `questions/_csm_relations.json` ({len(data['questions'])} questions, "
             "`expect_mode: relations`). Runner: `tools/csm/validate_relations.py` "
             "(reuses `canon_gold.ask` — auto-routed `/context`, top_k 8). `routed` is the "
             "bundle's own routing decision; the `relations` channel only exists on "
             "qa-mode bundles, so a question routed elsewhere cannot be complete.", "",
             "| question | routed | expected | found | missing |", "|---|---|---:|---:|---|"]
    passed = 0
    for q in data["questions"]:
        body = ask("csm", q["question"])
        names = relation_names(body)
        missing = []
        for item, aliases in expected_names(q):
            variants = [norm(v) for v in [item, *aliases] if v]
            if not any(present(v, " ".join(names)) for v in variants):
                missing.append(item)
        n_exp = len(expected_names(q))
        if not missing:
            passed += 1
        r = body.get("routed")
        routed = r.get("mode") if isinstance(r, dict) else (r or body.get("mode"))
        lines.append(f"| {q['id']} {q['question']} | {routed} "
                     f"| {n_exp} | {n_exp - len(missing)} | {', '.join(missing) or '—'} |")
    lines += ["", f"**{passed}/{len(data['questions'])} questions complete** "
                 f"(every expected party present in the bundle's relations)."]
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text("\n".join(lines) + "\n")
    print(f"{passed}/{len(data['questions'])} complete — wrote {RECEIPT.relative_to(REPO)}")
    for l in lines[6:]:
        if l.startswith("| csm"):
            print(l)
    return 0 if passed == len(data["questions"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())