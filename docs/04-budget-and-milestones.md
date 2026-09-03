# $50,000 budget and 16-week milestones

## Budget

| Category | Amount | What it buys |
|---|---:|---|
| Research and engineering | $25,000 | OML adapter, matrix runner, evaluation, device instrumentation, report |
| Reproducible compute | $7,000 | Six fingerprint-training checkpoints, reruns, negative controls |
| Physical test devices | $5,000 | Mid-range and flagship Android devices plus power/test accessories |
| Independent security and methods review | $5,000 | Threat-model and statistical-method review before publication |
| Documentation and community release | $3,000 | Reproduction guide, public demo, issue triage, workshop materials |
| Data/artifact hosting and CI | $2,000 | Versioned model deltas, raw result hosting, CI runners |
| Contingency | $3,000 | Failed runs, replacement hardware, format/runtime changes |
| **Total** | **$50,000** | |

If Sentient provides compute credits, reallocate the reduced cash compute cost
to more negative controls, a third low-cost Android device, and additional
independent review. Document the final allocation publicly.

## Milestones

### Weeks 1-2 — Public minimum proof

- Publish Apache-2.0 repository and contribution policy.
- Pin OML, Transformers, llama.cpp, model, and dataset revisions.
- Complete one-model/32-fingerprint smoke test.
- Demonstrate Transformers BF16 -> GGUF BF16 -> Q8_0/Q4_K_M.
- Publish raw JSONL, exact commands, and one generated result page.

**Acceptance:** a clean-machine reproduction produces the same run matrix and
statistically equivalent result summary.

### Weeks 3-5 — Fingerprint insertion and evaluator hardening

- Confirm both Apache-2.0 model families.
- Train two models across three seeds.
- Add exact token output, decoy keys, unfingerprinted controls, and confidence
  intervals.
- Pre-register final metrics, thresholds, and exclusions.

**Acceptance:** six pinned checkpoints pass baseline utility and fingerprint
checks; failed checkpoints remain documented.

### Weeks 6-8 — Full quantization matrix

- Produce GGUF BF16 conversion controls.
- Produce Q8_0, Q6_K, Q5_K_M, Q4_K_M, Q3_K_M, and Q2_K artifacts from the same
  BF16 parent.
- Run 144 primary inference cells and utility evaluations.
- Publish interim compatibility table.

**Acceptance:** every cell has a manifest, artifact hash, raw prediction
records, and a machine-readable summary or a documented failure reason.

### Weeks 9-11 — Real-device and attack-cost testing

- Benchmark reference Apple hardware and two Android classes.
- Measure memory, latency, throughput, and verification overhead.
- Run repeated quantization plus one LoRA/fine-tuning removal experiment.
- Plot fingerprint survival against utility damage and compute cost.

**Acceptance:** device procedures and exact builds are reproducible; security
claims remain within the tested threat model.

### Weeks 12-13 — Evidence receipt prototype

- Publish receipt schema and test vectors.
- Implement L0 self-declared receipts.
- Prototype L1 app/device-attested receipts on Android.
- Document why L1 does not prove that the claimed weights performed inference.

**Acceptance:** an independent verifier detects changed hashes, stale nonces,
replayed counters, and invalid signatures; assurance level is always visible.

### Weeks 14-16 — Review and public release

- Independent security/methods review and response.
- Final report, raw dataset, reproducibility container, and demo.
- Upstream OML issues/PRs for small reusable changes.
- Community walkthrough and next-phase proposal.

**Acceptance:** all promised public artifacts are available without a hosted
EdgeOML dependency.

## Decision gates

- If a model cannot retain baseline fingerprints after two documented training
  adaptations, replace it once; do not silently drop it.
- If GGUF BF16 diverges materially, pause quantization claims and resolve
  tokenizer/template/runtime equivalence first.
- If Q4 removes fingerprints cheaply, prioritize quantization-aware training
  rather than expanding device count.
- If L1 attestation cannot be implemented consistently across selected
  Android devices, publish the compatibility boundary and keep the receipt at
  L0 on unsupported devices.

## Post-grant path toward a larger company

The $50,000 grant should not be presented as the promised ₩1 billion outcome.
It creates the evidence needed for later capital:

1. Grant: open benchmark, receipt schema, public trust.
2. Follow-on grant/research: L2 measured-load attestation with an OEM, TEE, or
   confidential-compute partner.
3. Investment: a private, on-device personal shopping agent using EdgeOML
   receipts and transparent affiliate economics.
4. Larger round: revenue, retention, and deployment partnerships rather than
   a larger version of the same research promise.
