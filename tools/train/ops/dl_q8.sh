#!/bin/bash
export HF_HUB_ENABLE_HF_TRANSFER=1
~/train-env/bin/python - <<'PY'
from huggingface_hub import hf_hub_download
p = hf_hub_download("unsloth/Qwen3.8-27B-GGUF", "Qwen3.8-27B-Q8_0.gguf", local_dir="/mnt/PROJECTS/models/qwen3.8-27b-q8")
print("DONE", p)
PY
