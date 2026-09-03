from __future__ import annotations

import re
from typing import Any


SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
ASSURANCE_LEVELS = {
    "L0_SELF_DECLARED",
    "L1_APP_DEVICE_ATTESTED",
    "L2_MEASURED_LOAD",
    "L3_PROTECTED_EXECUTION",
}
HASH_FIELDS = (
    "runtime_digest",
    "weights_digest",
    "tokenizer_digest",
    "prompt_template_digest",
    "policy_digest",
    "request_digest",
    "response_digest",
)
REQUIRED_FIELDS = (
    "schema_version",
    "assurance_level",
    "agent_id",
    "model_id",
    "runtime",
    "artifact_format",
    "quantization",
    "nonce",
    "counter",
    "signature_algorithm",
    "signature",
    *HASH_FIELDS,
)


def validate_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in receipt:
            errors.append(f"missing required field: {field}")

    assurance_level = receipt.get("assurance_level")
    if assurance_level not in ASSURANCE_LEVELS:
        errors.append(
            "assurance_level must be one of " + ", ".join(sorted(ASSURANCE_LEVELS))
        )

    for field in HASH_FIELDS:
        value = receipt.get(field)
        if value is not None and (
            not isinstance(value, str) or not SHA256_PATTERN.fullmatch(value)
        ):
            errors.append(f"{field} must be a lowercase SHA-256 hex digest")

    counter = receipt.get("counter")
    if counter is not None and (not isinstance(counter, int) or counter < 0):
        errors.append("counter must be a non-negative integer")

    if assurance_level == "L1_APP_DEVICE_ATTESTED" and not receipt.get(
        "platform_attestation"
    ):
        errors.append("L1 receipts require platform_attestation")
    if assurance_level in {"L2_MEASURED_LOAD", "L3_PROTECTED_EXECUTION"} and not receipt.get(
        "measurement_evidence"
    ):
        errors.append(f"{assurance_level} receipts require measurement_evidence")

    return errors
