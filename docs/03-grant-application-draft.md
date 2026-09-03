# Sentient grant application draft

Working project name: **EdgeOML**  
Recommended track: **Open Source AGI Grant Track**  
Recommended request: **$50,000**

The live Typeform currently offers `10k`, `25k`, `50k`, and `>50k` grant
choices. A first application at $50,000 is large enough to produce meaningful
research and physical-device evidence while remaining inside a named option.

Replace every bracketed item with verified personal information before use.
The local pilot result is complete; do not submit until it and the repository
are available at stable public URLs.

## Who are you?

**Your email address**  
`[YOUR EMAIL]`

**What best describes your primary role?**  
Engineer / Builder  

If a company has already been incorporated and this is the founder's primary
work, “Founder” is also defensible. Use only one truthful answer.

**Where are you currently based?**  
`[CITY], Republic of Korea`

## What are you building?

### What problem are you solving, and why now?

Open-weight AI only becomes accessible and private when it can run on hardware
people already own. In practice, a model intended for a phone or laptop is
converted into a device runtime, wrapped in a chat template, and quantized to
four or fewer bits. Each step can change its behavior.

Sentient's public OML 1.0 implementation embeds secret key-response
fingerprints into a Hugging Face model and verifies them in a BF16/CUDA path.
It currently has no public GGUF, quantization, llama.cpp, or mobile evaluation
path. This means model creators and users cannot tell whether an
OML-fingerprinted model remains identifiable after realistic local deployment,
or whether a failed check was caused by quantization, conversion, prompting,
or the runtime itself.

This matters now because small open models and commodity on-device runtimes
are becoming useful enough for personal agents, while model provenance and
agent identity are still being designed around server assumptions. We want to
measure this gap before those assumptions harden into infrastructure.

### Who does this help?

EdgeOML first helps open-model maintainers and researchers who need a
reproducible way to test provenance after deployment transformations. It also
helps builders creating private personal agents for people who cannot afford
continuous cloud inference or do not have reliable connectivity.

The downstream user is a person whose cheapest or only computer is a phone.
They should be able to run a local model without surrendering private data,
while still receiving honest evidence about which model, runtime, and policy
produced an action. Sentient and other open-AI ecosystems benefit from a shared
compatibility dataset rather than one-off claims from each model vendor.

### In one line, what are you building?

An open benchmark and evidence format that measures whether
OML-fingerprinted models remain identifiable after conversion, quantization,
and deployment on real consumer devices.

### Who is building this, and why is your team the right one to do it?

`[FOUNDER NAME]` is a `[ROLE]` based in Korea working at the intersection of
`[VERIFIABLE SYSTEMS / ACCOUNT ABSTRACTION / OPEN-SOURCE AI — KEEP ONLY TRUE
CLAIMS]`. `[HE/SHE/THEY]` has built `[TWO SPECIFIC REPOSITORIES OR SHIPPED
SYSTEMS WITH LINKS AND MEASURABLE RESULTS]`.

The project needs an unusual combination of model evaluation, reproducible
systems work, and careful cryptographic language. Our advantage is that we are
not treating a signed model hash as proof of execution: EdgeOML defines an
explicit assurance ladder, separates model identity from app/device identity,
and publishes negative results. `[ADD THE NAME AND EVIDENCE FOR ANY ML/SECURITY
COLLABORATOR; DO NOT CLAIM A TEAM THAT DOES NOT EXIST.]`

If the `CertChain` project in the current workspace is your own work, replace
the generic evidence above with this concrete proof point:

> I built CertChain, a Solana on-chain credential proof registry with
> independent test-vector generation and matching Rust, TypeScript, and
> on-chain verification paths. Its documented M1 acceptance suite contains 83
> tests. That experience is directly relevant to EdgeOML's evidence schemas,
> cross-implementation reproducibility, and refusal to treat circular
> validation as proof. `[ADD A PUBLIC REPOSITORY LINK.]`

Use this paragraph only if authorship and every number are still true at
submission time.

### What's open about it, and what would get worse if it closed tomorrow, and for whom?

All benchmark code, runtime adapters, experiment manifests, receipt schemas,
and reproducible reports will be released under Apache-2.0. Public datasets and
research reports will be released under CC BY 4.0, except for active secret
fingerprint pairs whose disclosure would invalidate the ownership threat
model. Retired or synthetic pairs will be released for reproducibility.

If EdgeOML closed tomorrow, maintainers would again have to trust unpublished
vendor tests or rebuild the same conversion and device harness independently.
Smaller teams and builders serving low-connectivity markets would be hurt
first, because they have the least compute and security-review budget. The
public value is the common measurement method and raw evidence, not a hosted
API that can be revoked.

### Please provide demo or trial links

Repository: `https://github.com/hex-aragon/edgeoml`  
Pilot report: `https://github.com/hex-aragon/edgeoml/tree/main/experiments/m4-lora-pilot`  
Grant brief: `https://github.com/hex-aragon/edgeoml/blob/main/output/pdf/edgeoml-sentient-grant-brief.pdf`

Minimum acceptable demo before applying:

- one Apache-2.0 1B-class model;
- 32-128 inserted fingerprints;
- Transformers BF16, GGUF BF16, Q8_0, and Q4_K_M results;
- positive and negative controls;
- raw JSONL plus generated confidence intervals;
- exact commands and pinned revisions.

Local pilot completed on 2026-09-03:

> On an Apple M4 with 16 GiB unified memory, our 1.5B Apache-2.0 feasibility
> model recovered 31/32 key-response fingerprints in Transformers BF16,
> 30/32 after GGUF BF16 conversion, 31/32 in Q8_0, and 28/32 in Q4_K_M. The
> adapted model produced 0/256 assigned-response matches on independently
> generated decoy keys in every deployment condition. We publish raw JSONL,
> Wilson 95% intervals, commands, fixed revisions, and artifact hashes. This
> preliminary run uses MLX LoRA and is explicitly not presented as a
> reproduction of Sentient's full OML fine-tuning method.

The public report URL above now replaces the former local-path placeholder.

## Track selection

**Are you interested in applying for the grant track or the investment track?**  
Grant track.

Reason: the initial outputs are public infrastructure, a benchmark, a schema,
and research evidence. A commercial personal-agent product can later apply to
the investment track after there is actual usage and revenue evidence.

## Open Source AGI Grant Track

### How much grant funding are you asking for?

`$50,000`

### What would the grant unlock?

The grant would fund a 16-week public build. We will ship: (1) a runtime-neutral
fingerprint evaluation harness with positive and negative controls; (2) a
pre-registered matrix across two Apache-2.0, 1B-class models, three seeds, and
six practical/stress-test GGUF quantization levels; (3) reproducible physical
device measurements on a development reference machine and two Android
classes; (4) an open evidence-receipt schema that clearly labels what is
self-declared, app/device-attested, measured at load, or protected during
execution; and (5) a technical report containing all raw results, confidence
intervals, failure cases, and an attack-cost curve.

Without the grant, we have shipped the local analysis harness and a small
M4 LoRA pilot, but cannot complete the replicated upstream-compatible OML
training, physical-device matrix, independent security review, or complete
open dataset. We are also requesting
Sentient engineering feedback on OML compatibility and compute credits for the
six reproducible training checkpoints; credits would reduce cash compute spend
and let us expand negative controls.

### Please upload supporting documents, decks, or research materials

Upload a PDF assembled from:

1. `02-experiment-design.md`
2. `04-budget-and-milestones.md`
3. `05-attestation-and-commerce-roadmap.md`
4. one-page preliminary result generated from the public demo

Do not upload a generic investor deck to the grant track.

### How did you hear about this program?

`[TRUTHFUL SOURCE: Sentient website / X / Discord / referral name]`

## Optional closing note if a free-text field appears

We are deliberately making a falsifiable proposal. If Q4 quantization preserves
OML fingerprints, Sentient gains independent evidence that its ownership
primitive survives a critical deployment path. If it does not, the ecosystem
gains a reproducible failure boundary and an open target for
quantization-aware fingerprint training. Either outcome is useful and will be
published.

## Claims to avoid

- “The first ever on-device model attestation framework.” AttestLLM and other
  prior work make this unsafe.
- “Cryptographic proof of which model ran” at assurance levels L0 or L1.
- “Unremovable fingerprint.” Report an attack-cost curve instead.
- “Fully offline OML monetization.” A user-controlled device can bypass a local
  meter unless stronger trust or an economic protocol is added.
- “Production Android/iOS TEE inference” unless OEM-level protected execution
  is actually implemented and independently tested.
