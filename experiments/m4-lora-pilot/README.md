# EdgeOML M4 LoRA pilot

## Outcome

This local pilot demonstrates that the minimum pre-grant experiment can run on
an Apple M4 with 16 GiB unified memory. It does not require an NVIDIA/CUDA GPU.
The machine's integrated Apple GPU was used through MLX/MPS and llama.cpp
Metal.

The selected Q8_0 artifact retained the Transformers BF16 exact-match result:
31 of 32 fingerprints. Q4_K_M recovered 28 of 32. Across all three GGUF
conditions, none of 256 synthetic decoy keys produced its assigned decoy
response.

This is an **OML-style key-response LoRA feasibility pilot**, not a claim that
the public Sentient OML full-fine-tuning procedure has been reproduced on
Apple Silicon. The grant-scale experiment should rerun the public OML method
on pinned NVIDIA instances and then apply this conversion and device matrix.

## Fixed inputs

- Hardware: Apple M4, 16 GiB unified memory.
- Model: `Qwen/Qwen2.5-1.5B-Instruct`, Apache-2.0, revision
  `989aa7980e4cf806f80c7fef2b1adb7bc71aa306`.
- Fingerprints: 32 one-token responses generated with seed 42.
- Negative controls: the original model on the 32 fingerprint keys and the
  adapted model on 256 independently generated decoy keys.
- Adapter: rank-16 LoRA on all 28 layers' `q_proj` and `v_proj`; 2.179M of
  1.543B parameters trainable (0.141%).
- Training: 640 updates at `1e-4`, followed by 1,200 resumed updates at `5e-5`.
- Peak reported MLX memory: 3.600 GB.
- Generation: greedy, exactly one new token, seed 42.
- Metric: exact token-ID equality with a two-sided Wilson 95% confidence
  interval.

The natural-language keys are synthetic audit-ledger references. They are not
production secret keys and are intentionally published with this pilot.

## Measured results

| Condition | Artifact size | Exact matches | Exact-match rate | Wilson 95% CI | Decoy/control exact matches | Median inference |
|---|---:|---:|---:|---:|---:|---:|
| Original Transformers BF16 control | 3.09 GB | n/a | n/a | n/a | 0/32 | 193.6 ms |
| Fingerprinted Transformers BF16 | 3.09 GB | 31/32 | 96.88% | 84.26%-99.45% | 0/256 | 84.2 ms |
| Fingerprinted GGUF BF16 | 3.09 GB | 30/32 | 93.75% | 79.85%-98.27% | 0/256 | 49.0 ms |
| Fingerprinted GGUF Q8_0 | 1.65 GB | 31/32 | 96.88% | 84.26%-99.45% | 0/256 | 41.3 ms |
| Fingerprinted GGUF Q4_K_M | 0.99 GB | 28/32 | 87.50% | 71.93%-95.03% | 0/256 | 41.9 ms |

For each 0/256 decoy result, the Wilson 95% interval is 0%-1.48%. For the
original model's 0/32 accidental-match control, the upper bound is 10.72%.
The Q8_0 result being one match higher than GGUF BF16 is possible near an
argmax boundary and must not be interpreted as Q8 improving fingerprints;
the sample is deliberately small.

The shared miss was `fp-000`. GGUF BF16 additionally missed `fp-015`; Q8_0
recovered that boundary case, while Q4_K_M missed `fp-000`, `fp-015`,
`fp-024`, and `fp-027`. These records remain visible in the raw JSONL.

Latency is exploratory only. Model loading is excluded, requests were issued
serially, and `cache_prompt` was enabled for llama.cpp. Transformers/MPS and
llama.cpp/Metal numbers are not a controlled runtime benchmark.

The initial 640-update checkpoint recovered only 7/32 fingerprints (21.88%).
That failed first pass is preserved in
`raw/fingerprinted-transformers-bf16.jsonl`; it motivated the selected 1,200
additional updates rather than being hidden.

## Evidence map

- Final generated summary: `results/final-summary.json`
- Original-model control: `raw/base-transformers-bf16.jsonl`
- Transformers BF16: `raw/fingerprinted-transformers-bf16-final.jsonl`
- GGUF BF16: `raw/fingerprinted-gguf-bf16.jsonl`
- GGUF Q8_0: `raw/fingerprinted-gguf-q8_0.jsonl`
- GGUF Q4_K_M: `raw/fingerprinted-gguf-q4_k_m.jsonl`
- Fingerprint and decoy generation: `data/generation_manifest.json`
- Exact environment: `manifests/environment.txt`
- Exact commands: `manifests/commands.sh`
- Artifact hashes: `manifests/artifacts.sha256`
- Training and server logs: `logs/`
- Standalone public-release validator: `../../scripts/validate_pilot_release.py`

Large base, fused, adapter, and GGUF artifacts are excluded from Git. Their
hashes are retained so a separately hosted artifact can be checked byte for
byte.

## What this proves and what it does not

The pilot supports three narrow claims:

1. A 1.5B Apache-2.0 model can receive 32 key-response fingerprints through a
   small LoRA adaptation on this M4 machine.
2. The fingerprints remain measurable after HF-to-GGUF conversion and Q8/Q4
   quantization, with observable degradation at Q4 in this one run.
3. A public benchmark can separate conversion/runtime effects from
   quantization effects and report negative controls with confidence bounds.

It does not establish general robustness, an attack-cost curve, preservation
of model utility, Android performance, cryptographic proof of execution, or
equivalence to Sentient's full OML training. Those are funded milestones, not
facts inferred from this pilot.

## Grant decision

The grant is not a prerequisite for applying or for producing a credible
pilot. This run clears the local technical gate. Grant funding is justified by
the remaining scale: the public OML training path, two models, three or more
seeds, utility benchmarks, removal attacks, physical Android devices, and an
independent review. Before submitting, publish the repository and this result
at stable public URLs and replace the personal placeholders in the application
draft.
