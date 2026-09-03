# OML 1.0 public implementation audit

Audit date: 2026-09-03  
Upstream repository: `sentient-agi/OML-1.0-Fingerprinting`  
Audited commit: `e3ee78ceff65e54360dd70398f0b8283bc858d7a`

## Executive finding

The defensible project gap is:

> The public OML 1.0 implementation does not provide a reproducible way to
> distinguish fingerprint loss caused by model conversion, prompt
> serialization, runtime differences, or weight quantization during
> on-device deployment.

This is narrower and stronger than claiming that nobody has studied LLM
fingerprints under quantization. Adjacent watermark/fingerprint research
exists, so any priority or novelty claim must be backed by a complete
literature review before publication.

## What upstream implements

The repository has three central operations:

1. `generate_finetuning_data.py` creates secret key-response pairs using
   English, random-word, English/random-response, or inverse-nucleus
   strategies.
2. `finetune_multigpu.py` inserts fingerprints by full-model fine-tuning. It
   uses Hugging Face `Trainer`, PyTorch, and DeepSpeed. Weight averaging with
   the base model is available as an anti-forgetting regularizer, and system
   prompt augmentation is available for deployment robustness.
3. `check_fingerprints.py` generates a response for each key and reports exact
   response success. Its default prompt profiles are the raw key and a simple
   assistant wrapper.

The README documents arbitrary `model_path` support and named families for
Llama, Mistral, Pythia, Gemma, and Phi. Therefore, adapting the training code
to another decoder-only Transformers model is plausible, but not guaranteed
without a smoke test.

## What upstream does not implement

A repository-wide search found no references to:

- quantization or quantized weights;
- GGUF;
- Q2/Q3/Q4/Q5/Q6/Q8 formats;
- AWQ or GPTQ;
- llama.cpp, ExecuTorch, Core ML, MLX, Android, or iOS.

The verifier loads a Transformers checkpoint, converts it to BF16, and calls
CUDA directly. It therefore cannot evaluate a GGUF artifact or a true mobile
runtime without a separate inference adapter.

The verifier also reports only positive fingerprint accuracy. It does not
measure:

- false matches on an unfingerprinted base model or decoy keys;
- confidence intervals;
- conversion-only drift;
- quantization-only drift;
- repeated-seed variance;
- model quality, latency, memory, or energy alongside fingerprint survival.

## Important implementation caveats

### Conversion and quantization must be separated

Comparing Hugging Face BF16 directly with GGUF Q4 cannot identify the cause of
failure. Tokenization, BOS/EOS handling, chat templates, kernels, and output
serialization all change at once. EdgeOML therefore introduces a GGUF BF16
conversion control:

```text
HF BF16 -> GGUF BF16       measures conversion/runtime/template drift
GGUF BF16 -> GGUF Q4_K_M   measures incremental quantization drift
```

### Token IDs are the primary outcome

The upstream check is exact token equality. EdgeOML preserves that primary
metric. Normalized text and prefix match are diagnostic only, because decoded
strings can hide tokenizer and whitespace differences.

### Prompt format is an independent axis

The upstream documentation already shows that system prompts can wash out a
fingerprint unless prompt augmentation is used. A chat template change must
not be incorrectly reported as quantization damage. Every condition is tested
under raw, native chat-template, and unseen-system-prompt profiles.

### The current public verifier has technical debt

For a list of alternative signatures, the BOS-stripping branch builds a new
list but appears not to assign it back. That behavior should be covered by a
regression test before upstream code is reused. EdgeOML should wrap or patch
upstream minimally and keep a pinned commit plus patch manifest.

## OML paper versus this benchmark

The OML paper's threat model discusses persistence under fine-tuning, LoRA,
adapters, knowledge distillation, filtering, and coalition/model-merging
attacks. It also discusses quantization watermarking as a different ownership
protection technique. This audit did not find a reported OML key-response
fingerprint experiment across common on-device quantization formats in either
the public repository or its README.

The first grant should therefore claim a missing **public implementation and
measurement path**, not universal academic novelty.

## Recommended upstream contribution boundary

Keep EdgeOML as a separate repository while the experiment format stabilizes.
Contribute small, reviewable upstream changes later:

1. CPU/device-safe fingerprint scoring with no unconditional `.cuda()` calls.
2. JSONL output with token IDs and metadata instead of console-only results.
3. A runtime adapter interface rather than llama.cpp-specific code in OML.
4. Negative controls and confidence intervals.

This makes the work useful to Sentient without forcing their research repo to
own a complete mobile benchmarking framework.
