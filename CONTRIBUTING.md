# Contributing to EdgeOML

EdgeOML welcomes reproducibility fixes, new runtime adapters, additional open
model families, device measurements, statistical review, and corrections to
the assurance model.

## Before opening a pull request

1. Keep security and provenance claims within the evidence actually measured.
2. Do not publish active secret fingerprint pairs or proprietary model files.
3. Pin model, tokenizer, runtime, dataset, and source revisions for experiment
   contributions.
4. Include raw prediction records or a stable public artifact reference.
5. Document failed cells rather than silently excluding them.
6. Run the local checks:

```bash
python -m unittest discover -s tests -v
python scripts/validate_pilot_release.py
```

## Experiment contributions

An experiment should identify its model license, source revision, device,
runtime, prompt template, quantization method, random seed, positive and
negative controls, scoring method, and confidence interval. Do not compare HF
BF16 directly with a quantized GGUF artifact without also reporting a GGUF
BF16 conversion/runtime control.

## Scope

The first release measures fingerprint robustness and defines evidence receipt
levels. It does not claim unbreakable fingerprints, protected execution, or
offline payment enforcement. Proposals that strengthen those areas are
welcome when their threat model and dependencies are explicit.

