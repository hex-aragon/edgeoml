from __future__ import annotations

import hashlib
import itertools
import json
from typing import Any


REQUIRED_LIST_FIELDS = (
    "models",
    "seeds",
    "prompt_profiles",
    "conditions",
)


def _stable_id(record: dict[str, Any]) -> str:
    encoded = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()[:16]


def build_matrix(config: dict[str, Any]) -> list[dict[str, Any]]:
    for field in REQUIRED_LIST_FIELDS:
        if not isinstance(config.get(field), list) or not config[field]:
            raise ValueError(f"config field {field!r} must be a non-empty list")

    experiment = config.get("experiment", "edgeoml")
    fingerprint_count = config.get("fingerprint_count")
    if not isinstance(fingerprint_count, int) or fingerprint_count <= 0:
        raise ValueError("fingerprint_count must be a positive integer")

    runs: list[dict[str, Any]] = []
    axes = itertools.product(
        config["models"],
        config["seeds"],
        config["prompt_profiles"],
        config["conditions"],
    )
    for model, seed, prompt_profile, condition in axes:
        if not isinstance(model, dict) or "id" not in model:
            raise ValueError("every model must be an object with an id")
        if not isinstance(condition, dict):
            raise ValueError("every condition must be an object")
        for field in ("runtime", "artifact_format", "quantization", "role"):
            if field not in condition:
                raise ValueError(f"condition is missing {field!r}")

        run = {
            "experiment": experiment,
            "model": model["id"],
            "model_revision": model.get("revision", "PIN_BEFORE_RUN"),
            "seed": seed,
            "prompt_profile": prompt_profile,
            "fingerprint_count": fingerprint_count,
            **condition,
        }
        run["run_id"] = _stable_id(run)
        runs.append(run)
    return runs
