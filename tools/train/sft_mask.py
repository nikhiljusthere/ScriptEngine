"""Prompt/completion tokenization + the assistant-only label mask (U-WP6,
2026-10-04, plan/UNIVERSAL_DATASET_PLAN.md "Student model trial").

Pure python (no torch, no training deps): sft_qwen.py (train-env) builds
every training sample through this, and tests/test_sft_mask.py pins the
mask shape with a tokenizer only -- no model weights, so it runs in the
repo venv, which must never carry training deps.

The plan's fixed rule ("loss on the assistant turn only"): the prompt is
the model's own chat template rendered with enable_thinking=False (the
generated prompt ends in the model's empty think block, exactly as
inference sees it); the completion is the assistant JSON + EOS. Labels
carry -100 over the whole prompt and the real ids over the completion,
so the causal-LM loss trains the answer and only the answer.
"""

IGNORE = -100


def build_sample(tok, prompt, completion, max_len=None):
    """One SFT sample: (input_ids, labels, prompt_len).

    `prompt` is the rendered generation prompt (the chat template with
    add_generation_prompt=True, enable_thinking=False -- it ends in the
    empty think block); `completion` is the assistant answer text
    WITHOUT the EOS (this function appends the tokenizer's eos id once).
    Prompt and completion are tokenized separately and concatenated: the
    prompt carries labels -100, the completion its own ids (the standard
    split the boundary-token artifact of joint tokenization would add is
    a single token, and TRL's completion-only loss does the same split).

    Packing is OFF by plan: an over-long sample is dropped, never
    truncated (a truncated answer would teach truncation). Returns
    (None, None, None) when the sample exceeds `max_len`."""
    prompt_ids = tok(prompt, add_special_tokens=False)["input_ids"]
    comp_ids = tok(completion, add_special_tokens=False)["input_ids"]
    if getattr(tok, "eos_token_id", None) is not None:
        comp_ids = comp_ids + [tok.eos_token_id]
    input_ids = prompt_ids + comp_ids
    if max_len is not None and len(input_ids) > max_len:
        return None, None, None
    labels = [IGNORE] * len(prompt_ids) + comp_ids
    return input_ids, labels, len(prompt_ids)