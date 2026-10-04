"""Assistant-only label mask (U-WP6): tokenizer-only, no weights.

Runs in the REPO venv (scriptengine/.venv) — the training stack must
never be imported there. sft_qwen.py routes every sample through
tools/train/sft_mask.py; this pins the mask shape.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools" / "train"))

from sft_mask import IGNORE, build_sample  # noqa: E402

SNAP = ("/mnt/PROJECTS/hf_home/hub/models--Qwen--Qwen3.5-4B/snapshots/"
        "851bf6e806efd8d0a36b00ddf55e13ccb7b8cd0a")

PROMPT = ("<|im_start|>system\nYou extract events.<|im_end|>\n"
          "<|im_start|>user\nSeries: jjk\nPassage: X fought Y.<|im_end|>\n"
          "<|im_start|>assistant\n<think>\n\n</think>\n\n")
COMPLETION = '{"events": [{"quote": "X fought Y", "subject": "X", "verb": "fought", "object": "Y"}]}'


def _tok():
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained(SNAP)


def test_mask_shape():
    tok = _tok()
    ids, labels, plen = build_sample(tok, PROMPT, COMPLETION)
    assert len(ids) == len(labels) == plen + len(labels) - plen
    assert plen > 0
    assert all(l == IGNORE for l in labels[:plen])
    assert labels[plen:] == ids[plen:], "completion tokens carry real labels"
    assert ids[-1] == tok.eos_token_id, "completion ends with EOS"
    # decoding the labeled span is exactly the completion + EOS
    assert tok.decode(labels[plen:]).startswith('{"events":')


def test_max_len_drops_never_truncates():
    tok = _tok()
    ids, labels, plen = build_sample(tok, PROMPT, COMPLETION, max_len=10)
    assert (ids, labels, plen) == (None, None, None)
    ids2, labels2, plen2 = build_sample(tok, PROMPT, COMPLETION, max_len=4096)
    assert ids2 is not None


def test_prompt_render_ends_thinking_off():
    """The chat template generation prompt ends with the EMPTY think block."""
    tok = _tok()
    p = tok.apply_chat_template(
        [{"role": "system", "content": "s"},
         {"role": "user", "content": "u"}],
        tokenize=False, add_generation_prompt=True, enable_thinking=False)
    assert p.endswith("<think>\n\n</think>\n\n")
