"""Supervised fine-tune of the event-extraction student (plan/JJK_STUDENT_TRAINING.md).
Runs in ~/train-env, never the engine venv.

    python tools/train/sft.py --model <base or merged dir> --train a.jsonl [b.jsonl ...] \
        --out DIR [--epochs 3] [--lr 2e-4] [--rank 64] [--init-adapter DIR]

Records are the export's shape (messages: system, user, assistant). The prompt
is rendered with the model's own chat template, thinking off (Granite ends the
generation prompt with `<think></think>`), exactly as inference renders it;
the loss falls only on the completion (the assistant JSON + end-of-turn).
LoRA on every linear layer: a full fine-tune of a 3B model with fp32 AdamW
needs more than the 5090's 32 GB.
"""
import argparse, json, random

import torch
from datasets import Dataset
from peft import LoraConfig, PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
from trl import SFTConfig, SFTTrainer


def load(paths, tok, weight):
    out = []
    for p, w in zip(paths, weight):
        rows = [json.loads(l) for l in open(p)]
        for r in rows:
            prompt = tok.apply_chat_template(r["messages"][:2], tokenize=False,
                                             add_generation_prompt=True, enable_thinking=False)
            completion = r["messages"][2]["content"] + tok.eos_token
            out += [{"prompt": prompt, "completion": completion}] * w
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--train", nargs="+", required=True)
    ap.add_argument("--weight", nargs="*", type=int, help="repeat factor per train file")
    ap.add_argument("--eval")
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=float, default=3)
    ap.add_argument("--lr", type=float, default=2e-4)
    ap.add_argument("--rank", type=int, default=64)
    ap.add_argument("--max-len", type=int, default=4096)
    ap.add_argument("--batch", type=int, default=4)
    ap.add_argument("--accum", type=int, default=4)
    ap.add_argument("--init-adapter")
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    tok = AutoTokenizer.from_pretrained(a.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    weight = a.weight or [1] * len(a.train)
    rows = load(a.train, tok, weight)
    random.Random(a.seed).shuffle(rows)
    train = Dataset.from_list(rows)
    evald = Dataset.from_list(load([a.eval], tok, [1])) if a.eval else None
    model = AutoModelForCausalLM.from_pretrained(a.model, dtype=torch.bfloat16, device_map="cuda")
    peft_cfg = None
    if a.init_adapter:
        model = PeftModel.from_pretrained(model, a.init_adapter, is_trainable=True)
    else:
        peft_cfg = LoraConfig(r=a.rank, lora_alpha=2 * a.rank, lora_dropout=0.05,
                              target_modules="all-linear", task_type="CAUSAL_LM")
    cfg = SFTConfig(
        output_dir=a.out, num_train_epochs=a.epochs, learning_rate=a.lr,
        per_device_train_batch_size=a.batch, gradient_accumulation_steps=a.accum,
        lr_scheduler_type="cosine", warmup_steps=0.03, weight_decay=0.0,
        bf16=True, gradient_checkpointing=True, max_length=a.max_len,
        completion_only_loss=True, logging_steps=10, save_strategy="epoch",
        save_total_limit=2, report_to=[], seed=a.seed,
        eval_strategy="epoch" if evald is not None else "no",
        per_device_eval_batch_size=a.batch,
    )
    trainer = SFTTrainer(model=model, args=cfg, train_dataset=train, eval_dataset=evald,
                         processing_class=tok, peft_config=peft_cfg)
    trainer.train()
    trainer.save_model(a.out)
    tok.save_pretrained(a.out)
    print("saved", a.out)


if __name__ == "__main__":
    main()
