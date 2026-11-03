#!/usr/bin/env python3
"""Independent check of a composed v2 student set (compose_big_set_v2.py output). CPU only: the tokenizer
is the only model file it loads (no weights).

Re-derives from the written files, not from the composer's receipt: row counts per split; every row's
schema (exact keys and key order per layer, vocabulary, the assistant message == the row's own layers);
every quote verbatim in the row's passage; one system prompt everywhere; train / dev / test disjoint by
id, page and passage, dev_pool inside dev; the empty share under each definition; and token lengths with
the student's own tokenizer and chat template (enable_thinking=False, the render sft_qwen.py trains on):
the full sample (prompt + answer + EOS) against sft_qwen.py --max-len (over-long samples are DROPPED
there, never truncated) and the answer alone against the generation caps (sft_qwen.dev_generate caps
max_new at 2048; eval_base.py --max-new defaults to 1024).

    scriptengine/.venv/bin/python tools/train/check_v2_set.py DIR [--tokenizer M9] [--max-len 4096]
"""
import argparse
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
import compose_big_set_v2 as c  # noqa: E402

M9 = "/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-9B/snapshots/c202236235762e1c871ad0ccb60c8ee5ba337b9a"
THINK_TAIL = "<think>\n\n</think>\n\n"


def pct(xs, q):
    xs = sorted(xs)
    return xs[min(len(xs) - 1, int(q * len(xs)))] if xs else 0


def check_row(r, errors):
    msgs = r["messages"]
    if [m["role"] for m in msgs] != ["system", "user", "assistant"]:
        errors.append(f"{r['id']}: roles {[m['role'] for m in msgs]}")
        return
    if c.passage_of(msgs[1]["content"]) != r["passage"]:
        errors.append(f"{r['id']}: passage field differs from the user message")
    ans = json.loads(msgs[2]["content"])
    if list(ans) != ["events", "facts", "tags"]:
        errors.append(f"{r['id']}: answer keys {list(ans)}")
    if ans != {k: r[k] for k in ("events", "facts", "tags")}:
        errors.append(f"{r['id']}: assistant message differs from the row's layers")
    for layer, keys in (("events", c.EVENT_KEYS), ("facts", c.FACT_KEYS), ("tags", c.TAG_KEYS)):
        for x in ans[layer]:
            if tuple(x) != keys:
                errors.append(f"{r['id']}: {layer} keys {tuple(x)}")
    sub = []
    c.answer({"events": ans["events"], "facts": ans["facts"],
              "tags": ans["tags"]}, r["passage"], r["id"], sub)
    errors.extend(sub)
    for layer in ("events", "facts", "tags"):
        for x in ans[layer]:
            if x["quote"] not in r["passage"]:
                errors.append(f"{r['id']}: {layer} quote not verbatim")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--tokenizer", default=M9)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--no-tokens", action="store_true")
    a = ap.parse_args()
    d = Path(a.dir)
    S = {s: [json.loads(l) for l in open(d / f"{s}.jsonl")] for s in c.SPLITS}
    errors = []
    out = {"rows": {s: len(v) for s, v in S.items()},
           "sha256": {f"{s}.jsonl": hashlib.sha256((d / f"{s}.jsonl").read_bytes()).hexdigest() for s in c.SPLITS}}
    systems = Counter(r["messages"][0]["content"] for v in S.values() for r in v)
    out["system_prompts"] = len(systems)
    if len(systems) != 1:
        errors.append(f"{len(systems)} different system prompts")
    for s, rows in S.items():
        for r in rows:
            check_row(r, errors)
            if r["split"] != s:
                errors.append(f"{r['id']}: split field {r['split']!r} in {s}.jsonl")
    for kname, k in (("id", lambda r: r["id"]), ("page", lambda r: (r["series"], r["page"])),
                     ("passage", lambda r: r["passage"])):
        sets = {s: {k(r) for r in S[s]} for s in ("train", "dev", "test")}
        for x, y in (("train", "dev"), ("train", "test"), ("dev", "test")):
            n = len(sets[x] & sets[y])
            out[f"shared_{kname}_{x}_{y}"] = n
            if n:
                errors.append(f"{n} {kname} shared by {x} and {y}")
    if not {r["id"] for r in S["dev_pool"]} <= {r["id"] for r in S["dev"]}:
        errors.append("dev_pool not inside dev")
    out["dev_pool_series"] = dict(Counter(r["series"] for r in S["dev_pool"]))
    out["dup_ids_train"] = len(S["train"]) - len({r["id"] for r in S["train"]})
    out["empty_share"] = {s: {dn: round(sum(1 for r in v if f(r)) / max(len(v), 1), 4) for dn, f in c.EMPTY.items()}
                          for s, v in S.items()}
    out["by_series"] = {s: dict(sorted(Counter(r["series"] for r in v).items())) for s, v in S.items()}
    out["by_source"] = {s: dict(Counter(r["source"] for r in v)) for s, v in S.items()}
    out["layer_rows"] = {s: {k: sum(len(r[k]) for r in v) for k in ("events", "facts", "tags")} for s, v in S.items()}

    if not a.no_tokens:
        from transformers import AutoTokenizer
        tok = AutoTokenizer.from_pretrained(a.tokenizer)
        sysmsg = next(iter(systems))
        out["system_prompt_tokens"] = len(tok(sysmsg, add_special_tokens=False)["input_ids"])
        tl = {}
        for s, rows in S.items():
            prompts = [tok.apply_chat_template(r["messages"][:2], tokenize=False, add_generation_prompt=True,
                                               enable_thinking=False) for r in rows]
            bad = sum(1 for p in prompts if not p.endswith(THINK_TAIL))
            if bad:
                errors.append(f"{s}: {bad} prompts do not end with the empty think block")
            pl = [len(x) for x in tok(prompts, add_special_tokens=False)["input_ids"]]
            cl = [len(x) + 1 for x in tok([r["messages"][2]["content"] for r in rows],
                                          add_special_tokens=False)["input_ids"]]  # + EOS (sft_mask)
            tot = [p + q for p, q in zip(pl, cl)]
            tl[s] = {"prompt": {"p50": pct(pl, .5), "p99": pct(pl, .99), "max": max(pl)},
                     "answer": {"p50": pct(cl, .5), "p95": pct(cl, .95), "p99": pct(cl, .99), "max": max(cl),
                                "over_1024": sum(x > 1024 for x in cl), "over_2048": sum(x > 2048 for x in cl)},
                     "total": {"p50": pct(tot, .5), "p99": pct(tot, .99), "max": max(tot),
                               f"over_{a.max_len}": sum(x > a.max_len for x in tot),
                               "over_8192": sum(x > 8192 for x in tot)},
                     "supervised_tokens": sum(cl), "all_tokens": sum(tot)}
        out["tokens"] = tl
    out["errors"] = len(errors)
    print(json.dumps(out, indent=1, ensure_ascii=False))
    for e in errors[:30]:
        print("ERROR", e)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
