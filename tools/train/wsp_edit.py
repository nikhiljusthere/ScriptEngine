#!/usr/bin/env python3
"""Weight-space edit of the 9B student: find the direction its MLPs write when it makes one named extraction
error, and remove that direction from a few down_proj columns. No optimizer, no gradients.

The method is MIT CSAIL's weight-space programming (Takehi, Teoh, Zhang, Khattab, 2026), the owner's pick
2026-11-06: on Qwen3.5-0.8B they traced thinking loops to one direction written by the MLPs of two layers and
subtracted it from 64 down_proj output columns per layer (131,072 weights, 0.016%). That repaired a failure; it
added no skill. So the edit here sits on top of the step-5 LoRA student (merged), aimed at the failure that
student actually makes, and it ships only if it beats the unedited student on dev_pool.

The failure classes come from the model's own greedy answers against gold, one decision token per label:
  bad_stop       the model closes a list (events/facts/tags) with fewer items than gold has (missed items,
                 including `[]` on an eventful window, the 35B's largest error class)
  good_stop      it closes a list with at least gold's count
  continue_ok    it starts another item and gold has one more
  continue_over  it starts another item past gold's count (padding)
  loop           it starts an item equal to an earlier one in the same list (the paper's failure)
The activation recorded for a label is at the position that predicts the decision token (`]` or `,`).

Steps (all model work on CUDA, like every model job here):
    P=~/train-env/bin/python
    $P tools/train/wsp_edit.py diag-set --dev DEV --dev-pool POOL --train TRAIN --n-train 300 --out diag.jsonl
    $P tools/train/eval_base_v2.py --model M --adapter A --in diag.jsonl --out diag_preds.jsonl
    $P tools/train/wsp_edit.py positions --gold diag.jsonl --pred diag_preds.jsonl --out pos.jsonl
    $P tools/train/wsp_edit.py collect --model M --adapter A --gold diag.jsonl --pos pos.jsonl --out acts.pt
    $P tools/train/wsp_edit.py report --acts acts.pt --bad bad_stop --ref good_stop
    $P tools/train/wsp_edit.py make-edit --model M --adapter A --acts acts.pt --bad bad_stop --ref good_stop \
        --layers 15,19 --k 64 --alpha 1.0 --out edit.pt
    $P tools/train/eval_base_v2.py --model M --adapter A --edit edit.pt --in POOL --out pool_preds.jsonl
    $P tools/train/wsp_edit.py export --model M --adapter A --edit edit.pt --out DIR   # one standalone checkpoint
    $P tools/train/wsp_edit.py selftest     # scanner + edit algebra on toy tensors, no model
"""
import argparse
import json
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "train"))
LISTS = ("events", "facts", "tags")
CLASSES = ("bad_stop", "good_stop", "continue_ok", "continue_over", "loop")


def scan(raw):
    """Char offsets of the decision tokens in a v2 answer: [(list_name, kind, item_index, offset)], kind is
    'sep' (the `,` after item k) or 'close' (the list's `]`), plus each list's items as text spans.
    A small JSON-aware walk (strings and escapes skipped), so a `]` inside a quote is not a list close."""
    start = raw.rfind("</think>")
    i = start + len("</think>") if start >= 0 else 0
    depth, in_str, esc, key, last_str = 0, False, False, None, None
    cur, item_start, n_items, marks, items = None, None, 0, [], defaultdict(list)
    str_start = None
    while i < len(raw):
        c = raw[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
                last_str = raw[str_start + 1:i]
        elif c == '"':
            in_str, str_start = True, i
        elif c == ":" and depth == 1:
            key = last_str
        elif c in "{[":
            if c == "[" and depth == 1 and key in LISTS:
                cur, n_items = key, 0
            if c == "{" and depth == 2 and cur:
                item_start = i
            depth += 1
        elif c in "}]":
            depth -= 1
            if c == "}" and depth == 2 and cur:
                items[cur].append(raw[item_start:i + 1])
                n_items += 1
            if c == "]" and depth == 1 and cur:
                marks.append((cur, "close", n_items, i))
                cur = None
        elif c == "," and depth == 2 and cur:
            marks.append((cur, "sep", n_items - 1, i))
        i += 1
    return marks, items


def label_marks(raw, gold_row):
    """[(class, list_name, char_offset)] for one window."""
    marks, items = scan(raw)
    out = []
    for name, kind, k, off in marks:
        n_gold = len(gold_row.get(name) or [])
        if kind == "close":
            out.append(("bad_stop" if k < n_gold else "good_stop", name, off))
            continue
        nxt = items[name][k + 1] if k + 1 < len(items[name]) else None
        try:
            dup = nxt is not None and json.loads(nxt) in [json.loads(x) for x in items[name][:k + 1]]
        except ValueError:
            dup = False
        out.append(("loop" if dup else "continue_ok" if k + 1 < n_gold else "continue_over", name, off))
    return out


def cmd_diag_set(a):
    """Windows the direction is found on, kept apart from dev_pool (step 5 picks its checkpoint there and
    the edit is picked there) and from test: dev minus dev_pool, plus a seeded train sample."""
    pool = {json.loads(l)["id"] for l in open(a.dev_pool)}
    rows = [r for r in map(json.loads, open(a.dev)) if r["id"] not in pool]
    train = [json.loads(l) for l in open(a.train)]
    random.Random(a.seed).shuffle(train)
    rows += train[:a.n_train]
    with open(a.out, "w") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{len(rows)} diagnosis windows ({len(rows) - a.n_train} dev-only + {a.n_train} train) -> {a.out}")


def cmd_positions(a):
    gold = {r["id"]: r for r in map(json.loads, open(a.gold))}
    n = defaultdict(int)
    with open(a.out, "w") as f:
        for p in map(json.loads, open(a.pred)):
            labs = label_marks(p.get("raw") or "", gold[p["id"]])
            for cls, name, off in labs:
                n[cls, name] += 1
            f.write(json.dumps({"id": p["id"], "raw": p.get("raw") or "", "labels": labs}, ensure_ascii=False) + "\n")
    for name in LISTS:
        print(name, {c: n[c, name] for c in CLASSES})
    print(f"-> {a.out}")


def load_student(model_path, adapter, edit=None):
    """bf16 base (+ LoRA merged into the weights) on CUDA, with the edit applied when given."""
    import torch
    from transformers import AutoTokenizer, AutoModelForImageTextToText
    tok = AutoTokenizer.from_pretrained(model_path)
    m = AutoModelForImageTextToText.from_pretrained(model_path, dtype=torch.bfloat16, device_map="cuda")
    if adapter:
        from peft import PeftModel
        m = PeftModel.from_pretrained(m, adapter).merge_and_unload()
    if edit:
        apply_edit(m, edit)
    return tok, m.eval()


def decoder_layers(m):
    return m.model.language_model.layers


def apply_edit(m, edit):
    """Add the stored column deltas to each edited layer's mlp.down_proj (in place). Returns weights changed."""
    import torch
    e = torch.load(edit, map_location="cpu") if isinstance(edit, (str, Path)) else edit
    layers, n = decoder_layers(m), 0
    with torch.no_grad():
        for l, d in e["layers"].items():
            w = layers[int(l)].mlp.down_proj.weight
            cols = d["cols"].to(w.device)
            w[:, cols] += d["delta"].to(w.device, w.dtype)
            n += d["delta"].numel()
    return n


def cmd_collect(a):
    """Forward pass on prompt + the model's own answer; record each labeled decision position's down_proj
    output (what the MLP writes, 4,096-d) for every layer, and the class-mean |input| of each of its 12,288
    columns (which neurons fire there; make-edit ranks columns by it)."""
    import torch
    from sft_qwen import render_prompt
    gold = {r["id"]: r for r in map(json.loads, open(a.gold))}
    tok, m = load_student(a.model, a.adapter)
    layers = decoder_layers(m)
    L = len(layers)
    grab = {}

    def hook(l):
        def f(mod, inp, out):
            if grab.get("pos") is not None:
                grab["out"][l] = out[0, grab["pos"]].float().cpu()
                grab["inp"][l] = inp[0][0, grab["pos"]].float().abs().cpu()
        return f
    hs = [layers[l].mlp.down_proj.register_forward_hook(hook(l)) for l in range(L)]
    per = defaultdict(list)          # class -> [L x 4096] per position
    inp_sum = defaultdict(lambda: torch.zeros(L, layers[0].mlp.down_proj.in_features))
    rows = [json.loads(l) for l in open(a.pos)]
    for r in rows:
        if not r["labels"]:
            continue
        prompt = render_prompt(tok, gold[r["id"]]["messages"][:2])
        text = prompt + r["raw"]
        enc = tok(text, return_offsets_mapping=True, add_special_tokens=False)
        offs = enc["offset_mapping"]
        pos, cls = [], []
        for c, _name, off in r["labels"]:
            at = len(prompt) + off
            t = next((j for j, (s, e) in enumerate(offs) if s <= at < e), None)
            if t:                     # the decision token is t; the position that predicts it is t-1
                pos.append(t - 1)
                cls.append(c)
        if not pos:
            continue
        grab.update(pos=torch.tensor(pos), out=[None] * L, inp=[None] * L)
        with torch.no_grad():
            m(input_ids=torch.tensor([enc["input_ids"]], device="cuda"), use_cache=False)
        o, ip = torch.stack(grab["out"], 1), torch.stack(grab["inp"], 1)   # [P, L, 4096], [P, L, 12288]
        for j, c in enumerate(cls):
            per[c].append(o[j].half())
            inp_sum[c] += ip[j]
        grab["pos"] = None
    for h in hs:
        h.remove()
    acts = {"out": {c: torch.stack(v) for c, v in per.items()},
            "inp_mean": {c: inp_sum[c] / len(per[c]) for c in per},
            "model": a.model, "adapter": a.adapter, "gold": a.gold}
    torch.save(acts, a.out)
    print({c: len(v) for c, v in per.items()}, "->", a.out)


def auc(pos, neg):
    """P(score of a pos sample > score of a neg sample), ties half."""
    import torch
    allv = torch.cat([pos, neg])
    rank = allv.argsort().argsort().float() + 1
    return float((rank[:len(pos)].sum() - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def directions(acts, bad, ref):
    """Per layer: unit d = normalize(mean_bad - mean_ref) and a split-half AUC (d from even samples, scored on
    odd), so a layer is chosen by how well its direction separates held-out decisions, not by fit."""
    import torch
    B, R = acts["out"][bad].float(), acts["out"][ref].float()
    res = []
    for l in range(B.shape[1]):
        d = B[:, l].mean(0) - R[:, l].mean(0)
        dh = B[0::2, l].mean(0) - R[0::2, l].mean(0)
        dh = dh / dh.norm()
        res.append({"layer": l, "d": d / d.norm(), "gap": float(d.norm()),
                    "auc": auc(B[1::2, l] @ dh, R[1::2, l] @ dh)})
    return res


def cmd_report(a):
    import torch
    acts = torch.load(a.acts)
    print({c: v.shape[0] for c, v in acts["out"].items()})
    for r in sorted(directions(acts, a.bad, a.ref), key=lambda r: -r["auc"]):
        print(f"layer {r['layer']:2d}  held-out AUC {r['auc']:.3f}  mean gap {r['gap']:.3f}")


def make_edit(W, d, inp_mean, k, alpha):
    """Columns c of down_proj W (out x in) ranked by |d.W[:,c]| * mean|input_c| at the bad decisions; for the
    top k, delta[:,c] = -alpha * d (d.W[:,c]): alpha 1 removes d from what those neurons write."""
    import torch
    W = W.float()
    proj = d @ W                                  # [in]
    cols = (proj.abs() * inp_mean).topk(k).indices.sort().values
    delta = -alpha * torch.outer(d, proj[cols])   # [out, k]
    return cols, delta


def cmd_make_edit(a):
    import torch
    acts = torch.load(a.acts)
    dirs = {r["layer"]: r for r in directions(acts, a.bad, a.ref)}
    if a.layers.startswith("top"):
        chosen = sorted(dirs, key=lambda l: -dirs[l]["auc"])[:int(a.layers[3:])]
    else:
        chosen = [int(x) for x in a.layers.split(",")]
    _tok, m = load_student(a.model, a.adapter)
    layers, out, n = decoder_layers(m), {}, 0
    for l in chosen:
        W = layers[l].mlp.down_proj.weight
        cols, delta = make_edit(W, dirs[l]["d"].to(W.device), acts["inp_mean"][a.bad][l].to(W.device), a.k, a.alpha)
        out[l] = {"cols": cols.cpu(), "delta": delta.to(torch.bfloat16).cpu()}
        n += delta.numel()
    total = sum(p.numel() for p in m.parameters())
    meta = {"bad": a.bad, "ref": a.ref, "layers": chosen, "k": a.k, "alpha": a.alpha, "weights_changed": n,
            "share": n / total, "auc": {l: round(dirs[l]["auc"], 3) for l in chosen},
            "model": a.model, "adapter": a.adapter, "acts": a.acts}
    torch.save({"layers": out, "meta": meta}, a.out)
    print(json.dumps(meta), "->", a.out)


def cmd_export(a):
    """One standalone checkpoint (LoRA merged, edit applied), loadable by eval_base_v2.py --model DIR."""
    import shutil
    tok, m = load_student(a.model, a.adapter, a.edit)
    m.save_pretrained(a.out, safe_serialization=True, max_shard_size="5GB")
    tok.save_pretrained(a.out)
    for f in ("chat_template.jinja", "preprocessor_config.json", "video_preprocessor_config.json"):
        if (Path(a.model) / f).exists():
            shutil.copy(Path(a.model) / f, Path(a.out) / f)
    size = sum(p.stat().st_size for p in Path(a.out).glob("*.safetensors"))
    print(f"-> {a.out}: {size / 1e9:.2f} GB safetensors")


def cmd_selftest(_a):
    import torch
    raw = ('{"events": [{"subject": "A", "verb": "fought", "object": "B ]"}, {"subject": "A", "verb": "fought", '
           '"object": "B ]"}], "facts": [], "tags": [{"quote": "x, \\"y\\"", "tag": "t"}]}')
    labs = label_marks(raw, {"events": [1, 2, 3], "facts": [1], "tags": [1]})
    assert [(c, n) for c, n, _ in labs] == [("loop", "events"), ("bad_stop", "events"), ("bad_stop", "facts"),
                                            ("good_stop", "tags")], labs
    assert all(raw[o] in ",]" for _c, _n, o in labs)
    g = torch.Generator().manual_seed(0)
    W, d = torch.randn(16, 40, generator=g), torch.randn(16, generator=g)
    d = d / d.norm()
    cols, delta = make_edit(W, d, torch.ones(40), 8, 1.0)
    W2 = W.clone()
    W2[:, cols] += delta
    assert (d @ W2[:, cols]).abs().max() < 1e-5          # d removed from the edited columns
    keep = torch.ones(40, dtype=torch.bool)
    keep[cols] = False
    assert torch.equal(W2[:, keep], W[:, keep])          # nothing else touched
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("diag-set")
    for x in ("--dev", "--dev-pool", "--train", "--out"):
        p.add_argument(x, required=True)
    p.add_argument("--n-train", type=int, default=300)
    p.add_argument("--seed", type=int, default=1)
    p = sp.add_parser("positions")
    for x in ("--gold", "--pred", "--out"):
        p.add_argument(x, required=True)
    p = sp.add_parser("collect")
    for x in ("--model", "--gold", "--pos", "--out"):
        p.add_argument(x, required=True)
    p.add_argument("--adapter")
    p = sp.add_parser("report")
    p.add_argument("--acts", required=True)
    p.add_argument("--bad", default="bad_stop", choices=CLASSES)
    p.add_argument("--ref", default="good_stop", choices=CLASSES)
    p = sp.add_parser("make-edit")
    for x in ("--model", "--acts", "--out"):
        p.add_argument(x, required=True)
    p.add_argument("--adapter")
    p.add_argument("--bad", default="bad_stop", choices=CLASSES)
    p.add_argument("--ref", default="good_stop", choices=CLASSES)
    p.add_argument("--layers", default="top2", help="comma list, or topN by held-out AUC")
    p.add_argument("--k", type=int, default=64)
    p.add_argument("--alpha", type=float, default=1.0)
    p = sp.add_parser("export")
    for x in ("--model", "--out"):
        p.add_argument(x, required=True)
    p.add_argument("--adapter")
    p.add_argument("--edit")
    sp.add_parser("selftest")
    a = ap.parse_args()
    {"diag-set": cmd_diag_set, "positions": cmd_positions, "collect": cmd_collect, "report": cmd_report,
     "make-edit": cmd_make_edit, "export": cmd_export, "selftest": cmd_selftest}[a.cmd](a)


if __name__ == "__main__":
    main()
