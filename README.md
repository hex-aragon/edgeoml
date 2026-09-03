# EdgeOML

[![CI](https://github.com/hex-aragon/edgeoml/actions/workflows/ci.yml/badge.svg)](https://github.com/hex-aragon/edgeoml/actions/workflows/ci.yml)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)

EdgeOML is an open benchmark and evidence format for measuring whether an
OML-fingerprinted language model remains identifiable after it is converted,
quantized, and deployed on hardware people actually own.

The initial project deliberately separates two questions:

1. **Fingerprint robustness:** does the OML key-response behavior survive the
   real on-device deployment pipeline?
2. **Execution assurance:** what can a device honestly prove about the app,
   runtime, model artifact, policy, and output involved in an inference?

The first grant milestone is a reproducible benchmark, not a claim that mobile
attestation or offline monetization has been fully solved.

EdgeOML is an independent research project and is not an official Sentient
Foundation implementation.

## Why this is a strong Sentient grant fit

Sentient's grant page explicitly asks for personal on-device AI, proof that a
model is what it claims, agent identity, privacy by default, and software that
runs on inexpensive hardware. EdgeOML targets their intersection.

The public OML 1.0 implementation trains and checks fingerprints in
Hugging Face/PyTorch models. It does not currently contain a GGUF,
quantization, llama.cpp, ExecuTorch, Android, or iOS evaluation path. EdgeOML
adds the missing deployment evidence without changing OML's core mechanism.

## Repository contents

- `docs/00-executive-summary.ko.md` — Korean strategy and submission gates.
- `docs/01-oml-code-audit.md` — audit of the public OML implementation and the
  precise gap this project addresses.
- `docs/02-experiment-design.md` — grant-grade hypotheses, experiment matrix,
  metrics, thresholds, controls, and threat model.
- `docs/03-grant-application-draft.md` — draft answers mapped to the live
  Sentient Typeform questions.
- `docs/04-budget-and-milestones.md` — 16-week, $50,000 grant plan.
- `docs/05-attestation-and-commerce-roadmap.md` — assurance levels and the
  later private shopping-agent application.
- `docs/SOURCES.md` — primary sources and retrieval notes.
- `src/edgeoml` — dependency-free analysis CLI for generating experiment
  matrices, scoring JSONL prediction records, and validating evidence receipt
  structure.

## What can run on this machine

The current Apple M4 / 16 GB machine is suitable for the harness, GGUF
conversion, quantized inference, and 1B-3B local smoke tests. The upstream OML
training script is CUDA/DeepSpeed-oriented, so grant-grade fingerprint
injection should run on reproducible cloud NVIDIA instances unless that
training path is separately ported.

## Completed M4 pilot

The minimum local experiment has now been run. A Qwen2.5 1.5B model received
32 synthetic key-response fingerprints through LoRA, was fused, converted to
GGUF BF16, and quantized to Q8_0 and Q4_K_M. Exact-match recovery was 31/32 in
Transformers BF16, 30/32 in GGUF BF16, 31/32 in Q8_0, and 28/32 in Q4_K_M.
The adapted model produced 0/256 exact matches on independently generated
decoy keys in every condition.

See `experiments/m4-lora-pilot/README.md` for confidence intervals, raw JSONL,
fixed revisions, commands, hashes, limitations, and the distinction between
this LoRA feasibility run and upstream OML full fine-tuning.

| Condition | Exact match | Wilson 95% CI | Negative control |
|---|---:|---:|---:|
| Transformers BF16 | 31/32 (96.88%) | 84.26%-99.45% | 0/256 |
| GGUF BF16 | 30/32 (93.75%) | 79.85%-98.27% | 0/256 |
| GGUF Q8_0 | 31/32 (96.88%) | 84.26%-99.45% | 0/256 |
| GGUF Q4_K_M | 28/32 (87.50%) | 71.93%-95.03% | 0/256 |

Read the [five-page Sentient grant brief](output/pdf/edgeoml-sentient-grant-brief.pdf)
or inspect the complete [M4 pilot evidence](experiments/m4-lora-pilot/README.md).

## Quick start

The analysis code uses only the Python standard library.

```bash
git clone https://github.com/hex-aragon/edgeoml.git
cd edgeoml
PYTHONPATH=src python3 -m edgeoml.cli matrix \
  --config configs/phase1.json \
  --output /tmp/edgeoml-matrix.jsonl

PYTHONPATH=src python3 -m edgeoml.cli evaluate \
  --input examples/predictions.jsonl \
  --output /tmp/edgeoml-summary.json

PYTHONPATH=src python3 -m edgeoml.cli validate-receipt \
  --input examples/receipt.json

PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 scripts/validate_pilot_release.py
```

## Submission gate

The local reproducibility gate is complete. Do not submit the Sentient
application with a placeholder demo URL: publish a clean repository and the
pilot result first, then replace the personal-information placeholders in the
application draft.

## Working license

Code is licensed under Apache-2.0. Use CC BY 4.0 for the report/results when
they are published, with a separate data/report license notice.
