# EdgeOML Phase 1 experiment design

## Research question

How reliably do OML 1.0 key-response fingerprints survive the transformations
required to run an open-weight language model locally, and at what point does
removing the fingerprint also materially damage ordinary model utility?

## Hypotheses

- **H1 — Conversion invariance:** GGUF BF16 preserves at least 99% of the
  positive exact-match rate observed in Transformers BF16 when tokenization,
  prompt bytes, and generation parameters are held constant.
- **H2 — Practical quantization robustness:** Q8_0 through Q4_K_M preserve at
  least 95% of the GGUF BF16 exact-match rate and remain at or above 90%
  absolute exact match.
- **H3 — Attack-cost relationship:** below the first quantization level that
  drops fingerprint exact match under 90%, ordinary utility also declines by
  a measurable amount. The experiment estimates this curve; it does not assume
  the result.

These thresholds are pre-registered engineering targets, not facts about OML.

## Phase 1 scope

### Models

Use two genuinely permissive, small models rather than relying only on a
research-available license:

1. `Qwen/Qwen2.5-1.5B-Instruct` — Apache-2.0, multilingual, including Korean.
2. `allenai/OLMo-2-0425-1B-Instruct` — Apache-2.0, unusually transparent
   training ecosystem, primarily English.

Pin every Hugging Face revision before the first run. A model is admitted only
after a 32-fingerprint smoke test confirms that the upstream OML training path
can insert fingerprints without tokenizer or architecture errors.

### Fingerprints

- 1,024 inserted fingerprints per model and seed.
- Three training seeds: 13, 42, and 31415.
- Primary strategy: natural-language English key with one-token
  inverse-nucleus or random response, chosen after the smoke test.
- Secondary robustness check: 128 longer, natural-language responses.
- The secret key-response file is never published while ownership-verification
  claims are live. Publish either retired pairs or a deterministic synthetic
  evaluation set after the experiment.

### Deployment conditions

The checked-in config expands to 144 inference cells:

```text
2 models x 3 seeds x 3 prompt profiles x 8 artifact conditions = 144
```

Artifact conditions:

1. Transformers/safetensors BF16 — training reference.
2. llama.cpp/GGUF BF16 — conversion control.
3. GGUF Q8_0.
4. GGUF Q6_K.
5. GGUF Q5_K_M.
6. GGUF Q4_K_M.
7. GGUF Q3_K_M.
8. GGUF Q2_K — stress test, not a recommended deployment format.

Prompt profiles:

1. exact raw key bytes;
2. the model's native chat template;
3. an unseen system prompt.

All generation is greedy with temperature zero. Record the complete prompt
bytes, token IDs, seed, tokenizer digest, chat-template digest, runtime commit,
model artifact digest, command line, and device metadata.

## Controls

### Positive controls

- Fingerprinted Transformers BF16 checkpoint.
- Fingerprinted GGUF BF16 artifact.

### Negative controls

- Unfingerprinted base model receiving every fingerprint key.
- Fingerprinted model receiving natural-language decoy keys.
- Fingerprinted model receiving keys from a different seed/model family.

For a false-match claim below `1e-4`, run at least 30,000 independent negative
probes and report the Wilson upper bound. Zero observed false matches does not
mean the true false-positive rate is zero.

## Metrics

### Fingerprint effectiveness

- Positive exact token match rate (primary).
- 95% Wilson confidence interval.
- Mean response-prefix match (diagnostic).
- False-match rate and 95% Wilson interval.
- Robustness ratio:

```text
quantized positive exact-match rate / GGUF BF16 positive exact-match rate
```

### Harmlessness and utility

- Perplexity on a fixed, versioned corpus slice.
- Accuracy on PIQA, ARC-Easy, HellaSwag, and WinoGrande where model support is
  valid.
- One multilingual/Korean evaluation for Qwen, selected and version-pinned
  before results are observed.
- Relative utility retention versus the corresponding unfingerprinted artifact.

Do not collapse utility into a single score without also publishing every raw
task result.

### Device practicality

- Artifact size.
- Peak resident memory.
- Time to first token.
- Decode tokens per second.
- Median and p95 wall time for fingerprint verification.
- Energy per fixed-length response where the device exposes a reliable
  measurement API.

Report measurements separately for the current Apple M4 reference machine and
at least two Android classes. Do not compare energy numbers across platforms
unless the measurement method is equivalent.

## Device matrix

The grant target should include:

- Apple Silicon development reference: M4, 16 GB.
- Android mid-range: 8 GB RAM, currently supported OS and security patches.
- Android flagship: 12 GB or more, hardware-backed keystore/StrongBox where
  available.

Use exact device model, OS build, runtime commit, thermal state protocol, and
power mode in the released results. Device purchases belong in the grant
budget because emulator-only results do not establish on-device feasibility.

## Experiment procedure

1. Pin source revisions, containers, datasets, and model commits.
2. Run 32-fingerprint insertion smoke tests on both model families.
3. Pre-register the final strategy, thresholds, seeds, and exclusions.
4. Train six fingerprinted checkpoints: two models by three seeds.
5. Evaluate Transformers BF16 positive and negative controls.
6. Convert each checkpoint to GGUF BF16 and rerun identical prompts.
7. Quantize from the same GGUF BF16 parent into each target format.
8. Run the complete fingerprint and utility suite.
9. Repeat on physical devices with fixed warm-up and thermal procedures.
10. Publish raw records, environment manifests, analysis code, failure cases,
    and a signed result index.

Never requantize from an already quantized artifact unless the condition is
explicitly labeled as an adversarial requantization test.

## Statistical reporting

- Treat fingerprint probes within one trained checkpoint as correlated; seeds
  are the top-level replication unit.
- Report per-seed values and aggregate means, not only pooled probe counts.
- Bootstrap confidence intervals over seeds/checkpoints when enough
  replications exist; otherwise present the three raw seed results prominently.
- Correct for multiple comparisons when making format-by-format inferential
  claims.
- Publish all exclusions before examining final outcomes.

## Extended attack-cost curve

Only after the benign deployment matrix succeeds, add:

- repeated requantization;
- LoRA task adaptation;
- magnitude pruning;
- short benign fine-tuning;
- model merging where architecture permits;
- prompt filtering and output post-processing.

Plot fingerprint survival against both compute cost and utility damage. The
credible security claim is not “unremovable”; it is “removal under this threat
model costs at least this much utility, compute, or operational complexity.”

## Success, partial success, and falsification

- **Success:** Q4_K_M meets H2 on both model families and all raw artifacts are
  reproducible.
- **Partial success:** survival varies by model or prompt format. That is still
  a useful compatibility map and can motivate quantization-aware fingerprint
  training.
- **Falsification:** GGUF conversion alone causes major loss, or ordinary
  Q4 quantization removes fingerprints with negligible utility damage. Publish
  this result. A negative result exposes a concrete OML deployment risk and is
  a valid public-good output.
