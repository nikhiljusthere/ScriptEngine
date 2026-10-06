#!/usr/bin/env python3
"""SFT of the event-extraction student on Qwen3.5-4B (U-WP6, train-env).

    python tools/train/sft_qwen.py --train series/jjk/training/student/train.jsonl \
        --dev series/jjk/training/student/dev.jsonl --out DIR [--lr 6e-5] \
        [--rank 64 --alpha 128 --dropout 0.05] [--epochs 2] [--seed 1] \
        [--max-steps N] [--full-ft] [--rare-x 3]

Fixed by plan/UNIVERSAL_DATASET_PLAN.md "Student model trial": bf16,
gradient checkpointing, packing OFF, loss on the assistant turn only
(tokenized via tools/train/sft_mask.py — its label mask is pinned by
tests/test_sft_mask.py), completion = assistant JSON + EOS, cosine
schedule with 4% warmup, effective batch 16, per-epoch dev evaluation
(greedy generation -> event P/R/F1 via tools/eval_extraction.py's
window-level quote-overlap scorer, plus JSON-validity and
quote-verbatim), early stopping on dev F1 (patience 1), ONLY the best
adapter saved (save_total_limit 1). LoRA via peft with
use_rslora=True; targets = every nn.Linear in the LANGUAGE model
derived from named_modules() (the Gated-DeltaNet projections
included; the vision tower, embeddings, lm_head excluded) — the list
is printed and a frozen copy is written to the out dir. Full-FT mode
uses 8-bit/paged AdamW when bitsandbytes is importable, else
adamw_torch_fused with a VRAM note. enable_thinking=False everywhere;
the rendered generation prompt is asserted to end with the empty think
block exactly as inference sees it.
"""
import argparse, json, math, os, random, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "train"))

import torch  # noqa: E402
from torch.utils.data import Dataset  # noqa: E402

from sft_mask import IGNORE, build_sample  # noqa: E402

SNAP = ("/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-4B/snapshots/"
        "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a")
THINK_TAIL = "<think>\n\n</think>\n\n"


def language_linears(model):
    """Every nn.Linear in the language model (named_modules-derived)."""
    import torch.nn as nn
    bad = ("visual", "vision", "embed_tokens", "lm_head")
    names = []
    for n, m in model.named_modules():
        if isinstance(m, nn.Linear) and not any(b in n for b in bad):
            names.append(n)
    return names


def render_prompt(tok, messages):
    p = tok.apply_chat_template(messages[:2], tokenize=False,
                                add_generation_prompt=True,
                                enable_thinking=False)
    assert p.endswith(THINK_TAIL), f"generation prompt must end with the empty think block: {p[-60:]!r}"
    return p


def build_rows(rows, tok, rare_x, max_len):
    out = []
    dropped = 0
    for r in rows:
        prompt = render_prompt(tok, r["messages"])
        completion = r["messages"][2]["content"]
        sample = build_sample(tok, prompt, completion, max_len=max_len)
        if sample[0] is None:
            dropped += 1
            continue
        ids, labels, plen = sample
        n = rare_x if (rare_x and r.get("rare")) else 1
        for _ in range(n):
            out.append({"input_ids": ids, "labels": labels})
    return out, dropped


class SFTData(Dataset):
    def __init__(self, rows): self.rows = rows
    def __len__(self): return len(self.rows)
    def __getitem__(self, i): return self.rows[i]


def collate(batch, pad_id):
    mx = max(len(b["input_ids"]) for b in batch)
    input_ids, labels, attn = [], [], []
    for b in batch:
        n = len(b["input_ids"])
        pad = mx - n
        input_ids.append(b["input_ids"] + [pad_id] * pad)
        labels.append(b["labels"] + [IGNORE] * pad)
        attn.append([1] * n + [0] * pad)
    return {"input_ids": torch.tensor(input_ids),
            "labels": torch.tensor(labels),
            "attention_mask": torch.tensor(attn)}


def completion_loss(model, batch, chunk=256):
    """Mean next-token CE over the supervised (assistant) positions only.

    model(**batch).loss runs lm_head over EVERY position: on a ~3k-token
    window that is 3k x 248k-vocab logits (+ an fp32 copy) and it OOMed the
    32 GB card in the 2026-10-06 memory smoke, LoRA and full FT alike. Here
    lm_head sees only the positions whose next token is supervised
    (logits_to_keep), and the CE upcasts 256 positions at a time.
    """
    labels = batch["labels"]
    keep = (labels[:, 1:] != IGNORE).any(0).nonzero().squeeze(1)
    out = model(input_ids=batch["input_ids"], attention_mask=batch["attention_mask"],
                logits_to_keep=keep)
    logits = out.logits                    # B x K x V (bf16)
    tgt = labels[:, keep + 1]              # the token each kept position predicts
    n = (tgt != IGNORE).sum().clamp(min=1)
    total = logits.new_zeros((), dtype=torch.float32)
    for s in range(0, logits.shape[1], chunk):
        lc = logits[:, s:s + chunk].float()
        total = total + torch.nn.functional.cross_entropy(
            lc.reshape(-1, lc.shape[-1]), tgt[:, s:s + chunk].reshape(-1),
            ignore_index=IGNORE, reduction="sum")
    return total / n


@torch.no_grad()
def dev_generate(model, tok, rows, batch=8, max_new=None):
    """Greedy per-window JSON -> {id: {events, raw}} for the scorer."""
    import re
    if max_new is None:
        longest = max(len(r["messages"][2]["content"]) for r in rows)
        max_new = int(longest * 1.5 / 3) + 32  # chars->tokens cushion
        max_new = min(max(max_new, 256), 2048)
    model.eval()
    prompts = [render_prompt(tok, r["messages"]) for r in rows]
    order = sorted(range(len(rows)), key=lambda i: len(prompts[i]))
    preds = {}
    t0, ntok = time.time(), 0
    for b in range(0, len(order), batch):
        idx = order[b:b + batch]
        old_pad = tok.padding_side
        tok.padding_side = "left"
        enc = tok([prompts[i] for i in idx], return_tensors="pt", padding=True).to(model.device)
        tok.padding_side = old_pad
        # use_cache=True: training sets config.use_cache=False, and an uncached
        # generate re-reads the whole prefix per token (the dev eval would crawl).
        g = model.generate(**enc, max_new_tokens=max_new, do_sample=False, use_cache=True,
                           pad_token_id=tok.pad_token_id or tok.eos_token_id)
        for j, i in enumerate(idx):
            new = g[j][enc["input_ids"].shape[1]:]
            ntok += int((new != tok.pad_token_id).sum())
            text = tok.decode(new, skip_special_tokens=True)
            body = text.strip()
            if "</think>" in body:
                body = body.split("</think>")[-1]
            body = re.sub(r"^```[a-z]*\n?|\n?```$", "", body).strip()
            s, e = body.find("{"), body.rfind("}")
            ev, valid = [], False
            if s >= 0 and e > s:
                try:
                    d = json.loads(body[s:e + 1])
                    if isinstance(d, dict) and isinstance(d.get("events"), list):
                        ev, valid = [x for x in d["events"] if isinstance(x, dict)], True
                except ValueError:
                    pass
            preds[rows[i]["id"]] = {"events": ev, "raw": text}
    model.train()
    return preds, ntok / max(time.time() - t0, 1e-9)


def dev_scores(dev_path, preds):
    """Window-level event P/R/F1 + JSON validity + quote verbatim."""
    sys.path.insert(0, str(ROOT / "tools"))
    from eval_extraction import load_gold, score
    gold = load_gold(Path(dev_path))
    summary, _units = score(gold, preds)
    return {
        "f1": summary.get("f1"),
        "precision": summary.get("precision"),
        "recall": summary.get("recall") or summary.get("core_recall"),
        "json_validity": summary.get("json_validity"),
        "quote_verbatim": summary.get("quote_verbatim"),
        "per_verb": summary.get("per_verb"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--train", required=True)
    ap.add_argument("--dev", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default=SNAP)
    ap.add_argument("--lr", type=float, default=6e-5)
    ap.add_argument("--rank", type=int, default=64)
    ap.add_argument("--alpha", type=int, default=None, help="default 2*rank")
    ap.add_argument("--dropout", type=float, default=0.05)
    ap.add_argument("--epochs", type=float, default=1)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--max-steps", type=int, default=None)
    ap.add_argument("--full-ft", action="store_true")
    ap.add_argument("--rare-x", type=int, default=1)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--micro-batch", type=int, default=2)
    ap.add_argument("--accum", type=int, default=8, help="micro x accum = effective 16")
    ap.add_argument("--dev-batch", type=int, default=8)
    a = ap.parse_args()
    alpha = a.alpha if a.alpha is not None else 2 * a.rank
    random.seed(a.seed); torch.manual_seed(a.seed)
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)

    from transformers import (AutoModelForCausalLM, AutoTokenizer,
                              get_cosine_schedule_with_warmup)
    from torch.optim import AdamW
    try:
        from transformers import AutoModelForImageTextToText as AutoMM
    except ImportError:  # older transformers
        AutoMM = None
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    train_rows = [json.loads(l) for l in open(a.train)]
    dev_rows = [json.loads(l) for l in open(a.dev)]
    train_data, dropped = build_rows(train_rows, tok, a.rare_x, a.max_len)
    print(f"train samples: {len(train_data)} (dropped {dropped} over-long), rare_x={a.rare_x}")
    lens = sorted(len(r["input_ids"]) for r in train_data)
    print(f"sample tokens: p50={lens[len(lens)//2]} p95={lens[int(len(lens)*.95)]} max={lens[-1]}")

    try:
        loader = AutoMM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda") if AutoMM else None
    except Exception:
        loader = None
    model = loader or AutoModelForCausalLM.from_pretrained(
        a.model, dtype=torch.bfloat16, device_map="cuda")
    print("model:", type(model).__name__)

    targets = language_linears(model)
    print(f"LoRA targets: {len(targets)} language-model nn.Linear modules")
    for t in targets[:5]: print("  e.g.", t)
    json.dump(targets, open(out / "lora_targets.json", "w"), indent=1)

    if a.full_ft:
        try:
            import bitsandbytes  # noqa
            print("full-FT: bitsandbytes present -> paged AdamW 8-bit optimizer")
        except ImportError:
            print("full-FT: bitsandbytes absent -> adamw_torch_fused (VRAM note: "
                  "~64 GB optimizer+grad+weight headroom; shrink micro-batch if OOM)")
        peft_cfg = None
        # Full FT trains the LANGUAGE layers only. The vision tower is dead
        # weight for text extraction; the embeddings and lm_head are frozen
        # (as in the LoRA arms) so a ~3k-window dataset cannot drift the
        # vocabulary -- and the frozen 1.6 GB embedding/head pair keeps the
        # 8-bit-AdamW full FT inside the 32 GB card.
        frozen = 0
        for name, prm in model.named_parameters():
            if any(k in name for k in ("visual", "vision", "embed_tokens", "lm_head")):
                prm.requires_grad_(False)
                frozen += prm.numel()
        trainable = sum(prm.numel() for prm in model.parameters() if prm.requires_grad)
        print(f"full-FT: trainable {trainable/1e9:.2f}B params, frozen {frozen/1e9:.2f}B (vision/embeddings/head)")
    else:
        from peft import LoraConfig, get_peft_model
        peft_cfg = LoraConfig(r=a.rank, lora_alpha=alpha, lora_dropout=a.dropout,
                              target_modules=targets, use_rslora=True,
                              task_type="CAUSAL_LM")
        model = get_peft_model(model, peft_cfg)
        model.print_trainable_parameters()

    # Non-reentrant checkpointing + input grads: with LoRA on frozen embeddings,
    # reentrant checkpointing can cut the graph ("does not require grad").
    model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    if peft_cfg is not None and hasattr(model, "enable_input_require_grads"):
        model.enable_input_require_grads()
    model.config.use_cache = False
    ds = SFTData(train_data)
    dl = torch.utils.data.DataLoader(
        ds, batch_size=a.micro_batch, shuffle=True,
        generator=torch.Generator().manual_seed(a.seed),
        collate_fn=lambda b: collate(b, tok.pad_token_id or tok.eos_token_id))
    steps_per_epoch = math.ceil(len(dl) / a.accum)
    total = a.max_steps or int(steps_per_epoch * a.epochs)
    params = [p for p in model.parameters() if p.requires_grad]
    if a.full_ft:
        try:
            import bitsandbytes as bnb
            opt = bnb.optim.PagedAdamW8bit(params, lr=a.lr, betas=(0.9, 0.95), weight_decay=0.0)
            print("full-FT optimizer: paged adamw 8-bit (bitsandbytes)")
        except ImportError:
            print("full-FT: bitsandbytes absent — adamw_torch_fused; VRAM note: "
                  "full-FT bf16 of a 4B wants ~64 GB of optimizer+grad+weight "
                  "headroom, shrink micro-batch if OOM")
            opt = AdamW(params, lr=a.lr, betas=(0.9, 0.95), weight_decay=0.0, fused=True)
    else:
        opt = AdamW(params, lr=a.lr, betas=(0.9, 0.95), weight_decay=0.0, fused=True)
    sched = get_cosine_schedule_with_warmup(opt, int(0.04 * total), total)
    print(f"effective batch {a.micro_batch * a.accum}, steps/epoch {steps_per_epoch}, total {total}, warmup {int(0.04*total)}")

    best, bad_epochs, step = -1.0, 0, 0
    metrics = open(out / "metrics.jsonl", "a")
    for epoch in range(1, int(a.epochs) + 1):
        model.train()
        t0, losses = time.time(), []
        opt.zero_grad(set_to_none=True)
        stop = False
        for bi, batch in enumerate(dl):
            batch = {k: v.to(model.device) for k, v in batch.items()}
            loss = completion_loss(model, batch) / a.accum
            loss.backward()
            losses.append(loss.item() * a.accum)
            if (bi + 1) % a.accum == 0:
                torch.nn.utils.clip_grad_norm_([p for p in model.parameters() if p.requires_grad], 1.0)
                opt.step(); sched.step(); opt.zero_grad(set_to_none=True)
                step += 1
                if a.max_steps and step >= a.max_steps:
                    stop = True
                    break
        dev_preds, wps = dev_generate(model, tok, dev_rows, batch=a.dev_batch)
        scores = dev_scores(a.dev, dev_preds)
        line = {"epoch": epoch, "step": step, "train_loss": round(sum(losses) / max(len(losses), 1), 4),
                "dev_f1": scores["f1"], "dev_p": scores["precision"], "dev_r": scores["recall"],
                "json_validity": scores["json_validity"], "quote_verbatim": scores["quote_verbatim"],
                "windows_per_s": round(wps, 2), "seconds": round(time.time() - t0, 1)}
        metrics.write(json.dumps(line) + "\n"); metrics.flush()
        print("epoch", json.dumps(line))
        if (scores["f1"] or 0) > best:
            best, bad_epochs = scores["f1"], 0
            model.save_pretrained(out / "best")
            tok.save_pretrained(out / "best")
            print(f"  new best dev F1 {best} -> saved {out/'best'}")
        else:
            bad_epochs += 1
            if bad_epochs >= 1:
                print("  early stop: dev F1 did not improve (patience 1)")
                break
        if stop:
            break
    final = {"best_dev_f1": best, "epochs_run": epoch, "steps": step,
             "config": vars(a), "targets": len(targets), "out": str(out)}
    json.dump(final, open(out / "final.json", "w"), indent=1)
    print("final", json.dumps({k: final[k] for k in ("best_dev_f1", "epochs_run", "steps")}))


if __name__ == "__main__":
    main()
