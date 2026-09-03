#!/usr/bin/env bash
set -euo pipefail

# Run from the repository root. Large model and adapter files are intentionally
# ignored by Git; the hashes needed to verify them are in artifacts.sha256.

python3 -m venv .venv
.venv/bin/pip install 'mlx-lm[train]==0.31.3' 'torch==2.14.0' 'transformers==5.16.1'

.venv/bin/python - <<'PY'
from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="Qwen/Qwen2.5-1.5B-Instruct",
    revision="989aa7980e4cf806f80c7fef2b1adb7bc71aa306",
    local_dir="experiments/m4-lora-pilot/models/base",
)
PY

git clone https://github.com/ggml-org/llama.cpp.git /tmp/edgeoml-llama.cpp
git -C /tmp/edgeoml-llama.cpp checkout 42f0225fea945b24e92a0ce716e59b7c13e9b819
cmake -S /tmp/edgeoml-llama.cpp -B /tmp/edgeoml-llama.cpp/build -DGGML_METAL=ON -DLLAMA_CURL=OFF
cmake --build /tmp/edgeoml-llama.cpp/build --config Release -j 8

.venv/bin/python scripts/make_pilot_data.py \
  --model experiments/m4-lora-pilot/models/base \
  --output-dir experiments/m4-lora-pilot/data \
  --count 32 \
  --decoy-count 256 \
  --seed 42

# First stage: 640 LoRA updates at 1e-4.
.venv/bin/python -m mlx_lm lora \
  --config experiments/m4-lora-pilot/config.yaml

# Final persisted stage: resume from update 640 and run 1,200 more updates at
# 5e-5. The exploratory command originally requested 1,600 updates and was
# stopped after update 1,240; update 1,200 was the last saved checkpoint. This
# bounded command reproduces the selected final checkpoint without a manual
# interrupt.
.venv/bin/python -m mlx_lm lora \
  --config experiments/m4-lora-pilot/config.yaml \
  --resume-adapter-file experiments/m4-lora-pilot/adapters/0000640_adapters.safetensors \
  --iters 1200 \
  --learning-rate 0.00005 \
  --save-every 400

.venv/bin/python -m mlx_lm fuse \
  --model experiments/m4-lora-pilot/models/base \
  --adapter-path experiments/m4-lora-pilot/adapters \
  --save-path experiments/m4-lora-pilot/models/fused-1200

.venv/bin/python scripts/run_transformers_eval.py \
  --model experiments/m4-lora-pilot/models/base \
  --fingerprints experiments/m4-lora-pilot/data/fingerprints.json \
  --condition BASE_TRANSFORMERS_BF16 \
  --source base \
  --output experiments/m4-lora-pilot/raw/base-transformers-bf16.jsonl

.venv/bin/python scripts/run_transformers_eval.py \
  --model experiments/m4-lora-pilot/models/fused-1200 \
  --fingerprints experiments/m4-lora-pilot/data/fingerprints.json \
  --decoys experiments/m4-lora-pilot/data/decoys.json \
  --condition FINGERPRINTED_TRANSFORMERS_BF16 \
  --source fingerprinted \
  --output experiments/m4-lora-pilot/raw/fingerprinted-transformers-bf16-final.jsonl

.venv/bin/python /tmp/edgeoml-llama.cpp/convert_hf_to_gguf.py \
  experiments/m4-lora-pilot/models/fused-1200 \
  --outfile experiments/m4-lora-pilot/gguf/fingerprinted-bf16.gguf \
  --outtype bf16

/tmp/edgeoml-llama.cpp/build/bin/llama-quantize \
  experiments/m4-lora-pilot/gguf/fingerprinted-bf16.gguf \
  experiments/m4-lora-pilot/gguf/fingerprinted-q8_0.gguf \
  Q8_0

/tmp/edgeoml-llama.cpp/build/bin/llama-quantize \
  experiments/m4-lora-pilot/gguf/fingerprinted-bf16.gguf \
  experiments/m4-lora-pilot/gguf/fingerprinted-q4_k_m.gguf \
  Q4_K_M

.venv/bin/python scripts/run_llama_eval.py \
  --server /tmp/edgeoml-llama.cpp/build/bin/llama-server \
  --model experiments/m4-lora-pilot/gguf/fingerprinted-bf16.gguf \
  --tokenizer experiments/m4-lora-pilot/models/base \
  --fingerprints experiments/m4-lora-pilot/data/fingerprints.json \
  --decoys experiments/m4-lora-pilot/data/decoys.json \
  --condition FINGERPRINTED_GGUF_BF16 \
  --output experiments/m4-lora-pilot/raw/fingerprinted-gguf-bf16.jsonl \
  --log experiments/m4-lora-pilot/logs/eval-gguf-bf16-server.log

.venv/bin/python scripts/run_llama_eval.py \
  --server /tmp/edgeoml-llama.cpp/build/bin/llama-server \
  --model experiments/m4-lora-pilot/gguf/fingerprinted-q8_0.gguf \
  --tokenizer experiments/m4-lora-pilot/models/base \
  --fingerprints experiments/m4-lora-pilot/data/fingerprints.json \
  --decoys experiments/m4-lora-pilot/data/decoys.json \
  --condition FINGERPRINTED_GGUF_Q8_0 \
  --output experiments/m4-lora-pilot/raw/fingerprinted-gguf-q8_0.jsonl \
  --log experiments/m4-lora-pilot/logs/eval-gguf-q8_0-server.log

.venv/bin/python scripts/run_llama_eval.py \
  --server /tmp/edgeoml-llama.cpp/build/bin/llama-server \
  --model experiments/m4-lora-pilot/gguf/fingerprinted-q4_k_m.gguf \
  --tokenizer experiments/m4-lora-pilot/models/base \
  --fingerprints experiments/m4-lora-pilot/data/fingerprints.json \
  --decoys experiments/m4-lora-pilot/data/decoys.json \
  --condition FINGERPRINTED_GGUF_Q4_K_M \
  --output experiments/m4-lora-pilot/raw/fingerprinted-gguf-q4_k_m.jsonl \
  --log experiments/m4-lora-pilot/logs/eval-gguf-q4_k_m-server.log

PYTHONPATH=src .venv/bin/python scripts/summarize_pilot.py \
  --inputs \
    experiments/m4-lora-pilot/raw/base-transformers-bf16.jsonl \
    experiments/m4-lora-pilot/raw/fingerprinted-transformers-bf16-final.jsonl \
    experiments/m4-lora-pilot/raw/fingerprinted-gguf-bf16.jsonl \
    experiments/m4-lora-pilot/raw/fingerprinted-gguf-q8_0.jsonl \
    experiments/m4-lora-pilot/raw/fingerprinted-gguf-q4_k_m.jsonl \
  --output experiments/m4-lora-pilot/results/final-summary.json

shasum -a 256 \
  experiments/m4-lora-pilot/models/base/model.safetensors \
  experiments/m4-lora-pilot/adapters/adapters.safetensors \
  experiments/m4-lora-pilot/models/fused-1200/model.safetensors \
  experiments/m4-lora-pilot/gguf/fingerprinted-bf16.gguf \
  experiments/m4-lora-pilot/gguf/fingerprinted-q8_0.gguf \
  experiments/m4-lora-pilot/gguf/fingerprinted-q4_k_m.gguf

