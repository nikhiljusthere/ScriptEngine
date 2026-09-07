"""Phase 4C (re-scoped): run the pre-registered S-group probes of plan/ORACLE_v2.yaml.

Same held-out-oracle discipline and same scorer as 2C (oracle_run2c.py, imported
unchanged): POST each probe question to /context under `auto` routing and apply
the item's `check` to the served bundle. v2 is pre-registered with `expect: fail`
on every S item — a PASS is the finding that closes 4C for that probe; a FAIL
promotes the probe to the real 4C gate (evidence the interval gap is live).

Bundles dump to /tmp/oracle_4c_bundles/ for audit; results + summary land
beside this file.
"""

import hashlib
import importlib.util
import json
import pathlib

import yaml

HERE = pathlib.Path(__file__).parent
ORACLE = pathlib.Path("/home/goblin/ScriptEngine/plan/ORACLE_v2.yaml")
DUMP_DIR = pathlib.Path("/tmp/oracle_4c_bundles")
RESULTS = HERE / "oracle_4c_results.txt"
SUMMARY = HERE / "oracle_4c_summary.json"

_spec = importlib.util.spec_from_file_location(
    "oracle_run2c", HERE.parent / "oracle_2c" / "oracle_run2c.py")
h = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(h)


def main() -> None:
    raw = ORACLE.read_bytes()
    sha = hashlib.sha256(raw).hexdigest()
    doc = yaml.safe_load(raw)
    items = [i for i in doc["items"] if i["id"].startswith("S")]
    for rel in doc.get("relabels") or []:
        print(f"relabel (record only, v1 untouched): {rel['id']} "
              f"{rel['v1_expect']} -> {rel['v2_expect']}")
    print(f"oracle v2 sha256: {sha}")
    print(f"S-group probes: {[i['id'] for i in items]}")
    DUMP_DIR.mkdir(parents=True, exist_ok=True)

    lines = [f"oracle v2 sha256: {sha}\n",
             f"{'ID':<4} {'expect':<5} {'result':<6} {'door':<9} detail\n"]
    rows, surprises = [], []
    for item in items:
        bundle = h.post(item["question"])
        (DUMP_DIR / f"{item['id']}.json").write_text(json.dumps(bundle, indent=2))
        verdict = h.check_item(item, bundle)
        door = (bundle.get("routed") or {}).get("mode", bundle.get("mode"))
        result = "PASS" if verdict["ok"] else "FAIL"
        expect = item.get("expect")
        extra = {k: v for k, v in verdict.items() if k != "ok"}
        served = [f"{b.get('breadcrumb') or b.get('doc_title') or b.get('title') or b.get('name')} :: "
                  f"{h.norm(b.get('text', ''))[:110]}"
                  for b in (bundle.get("beats") or bundle.get("members") or [])[:3]]
        facts = [f"{f['field']}: {f['value']}" for f in (bundle.get("facts") or [])[:5]]
        block = [f"{item['id']:<4} {str(expect):<5} {result:<6} {str(door):<9} {extra}"]
        block.append(f"     served: {' | '.join(served) or '(nothing)'}")
        if facts:
            block.append(f"     facts: {' | '.join(facts)}")
        if expect and (verdict["ok"] != (expect == "pass")):
            surprises.append((item["id"], expect, result))
            block.append(f"   <-- SURPRISE (expected {expect})")
        block.append("")
        lines.append("\n".join(block))
        rows.append({"id": item["id"], "expect": expect, "result": result,
                     "door": str(door), "detail": extra,
                     "ground_truth": item["ground_truth"], "source_page": item["source_page"]})
        print("\n".join(block))

    passed = sum(1 for r in rows if r["result"] == "PASS")
    lines.append(f"\nS-group: {passed}/{len(rows)} PASS")
    if not any(r["result"] == "FAIL" for r in rows):
        lines.append("all probes pass -> 4C closes on this evidence; interval model to backlog")
    else:
        failed = [r["id"] for r in rows if r["result"] == "FAIL"]
        lines.append(f"probes FAIL -> real 4C gate: {', '.join(failed)} "
                     f"(bounded 4A build + serving-path spike first)")
    RESULTS.write_text("\n".join(lines) + "\n", encoding="utf-8")
    SUMMARY.write_text(json.dumps(
        {"oracle_file": "plan/ORACLE_v2.yaml", "sha256": sha,
         "relabels": doc.get("relabels") or [],
         "s_group": rows, "surprises": [{"id": s, "expect": e, "got": g}
                                        for s, e, g in surprises]},
        indent=2), encoding="utf-8")
    print("\n".join(lines[-3:]))
    print(f"\nresults: {RESULTS}\nsummary: {SUMMARY}")


if __name__ == "__main__":
    main()