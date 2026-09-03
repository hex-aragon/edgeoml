# Sources and retrieval notes

Retrieved 2026-09-03 unless noted otherwise.

## Sentient primary sources

- [Open Source AGI Grant Programme](https://sentient.foundation/grants) — six
  funding principles, on-device AI, model proof, agent identity, tracks,
  rolling review, compute and engineering support.
- [Live grant application](https://form.typeform.com/to/IRj7WaKH) — current
  question wording and grant amount choices (`10k`, `25k`, `50k`, `>50k`).
- [OML 1.0 Fingerprinting repository](https://github.com/sentient-agi/OML-1.0-Fingerprinting)
  — public generation, training, and verification implementation. Audit pinned
  to commit `e3ee78ceff65e54360dd70398f0b8283bc858d7a`.
- [OML: Open, Monetizable, and Loyal AI](https://eprint.iacr.org/2024/1573.pdf)
  — protocol, fingerprint primitive, robustness goals, and threat model.

## Runtime and platform primary sources

- [llama.cpp](https://github.com/ggml-org/llama.cpp) — GGUF inference and
  supported quantization/backends.
- [llama.cpp architecture registry](https://github.com/ggml-org/llama.cpp/blob/master/src/llama-arch.cpp)
  — confirms that OLMo 2 is a recognized runtime architecture; conversion of
  each newly fingerprinted checkpoint still requires a smoke test.
- [llama.cpp quantize documentation](https://github.com/ggml-org/llama.cpp/blob/master/tools/quantize/README.md)
  — BF16/F32 conversion, quantization process, and Q4_K_M example.
- [ExecuTorch: Running LLMs on Android](https://docs.pytorch.org/executorch/stable/llm/run-on-android.html)
  — experimental Java interface and Android LLM runtime path.
- [Android key and ID attestation](https://source.android.com/docs/security/features/keystore/attestation)
  — hardware-backed key attestation, security levels, and verified-boot fields.
- [Android Play Integrity overview](https://developer.android.com/google/play/integrity/overview)
  — evidence that requests come from a genuine app on a genuine/certified
  device.
- [Apple DeviceCheck and App Attest](https://developer.apple.com/documentation/devicecheck)
  — device-generated attested keys and app-instance assertions; Apple also
  states that App Attest cannot definitively identify every compromised OS.
- [Apple server-side App Attest validation](https://developer.apple.com/documentation/devicecheck/validating-apps-that-connect-to-your-server)
  — challenge, public-key validation, assertion counter, and replay controls.

## Adjacent research

- [AttestLLM: Efficient Attestation Framework for Billion-scale On-device LLMs](https://arxiv.org/abs/2509.06326)
  — prior on-device LLM attestation work combining activation signatures and a
  TEE. This prevents an unsafe “first-ever” claim.
- [Have You Merged My Model?](https://arxiv.org/abs/2404.05188) — robustness of
  LLM IP-protection methods under model merging.
- [Robust LLM Fingerprinting via Domain-Specific Watermarks](https://arxiv.org/abs/2505.16723)
  — statistical guarantees and deployment robustness for a related
  fingerprinting approach.
- [Copyright Protection for Large Language Models: A Survey of Methods,
  Challenges, and Trends](https://arxiv.org/abs/2508.11548) — terminology,
  evaluation dimensions, removal, and transfer literature.

## Model cards

- [Qwen2.5-1.5B-Instruct](https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct) —
  model card and Apache-2.0 license metadata.
- [OLMo-2-0425-1B-Instruct](https://huggingface.co/allenai/OLMo-2-0425-1B-Instruct)
  — model card, 1B size, and Apache-2.0 license.

## Evidence discipline

- The absence claim is limited to the audited public OML repository and its
  cited paper, not all unpublished Sentient work.
- Runtime and grant pages can change; pin snapshots or retrieval metadata when
  the public repository is launched.
- Search results are not evidence for technical conclusions. Final claims
  should cite the primary documents above and the project's raw experiment
  records.
