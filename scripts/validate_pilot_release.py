#!/usr/bin/env python3
from __future__ import annotations

import json
import math
import sys
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src"
sys.path.insert(0, str(SOURCE_ROOT))

from edgeoml.io import read_jsonl  # noqa: E402
from edgeoml.metrics import evaluate_records  # noqa: E402


PILOT_ROOT = REPOSITORY_ROOT / "experiments" / "m4-lora-pilot"
EXPECTED: dict[str, dict[str, Any]] = {
    "raw/base-transformers-bf16.jsonl": {
        "condition": "BASE_TRANSFORMERS_BF16",
        "records": 32,
        "positive": (0, 0),
        "negative": (0, 32),
    },
    "raw/fingerprinted-transformers-bf16-final.jsonl": {
        "condition": "FINGERPRINTED_TRANSFORMERS_BF16",
        "records": 288,
        "positive": (31, 32),
        "negative": (0, 256),
    },
    "raw/fingerprinted-gguf-bf16.jsonl": {
        "condition": "FINGERPRINTED_GGUF_BF16",
        "records": 288,
        "positive": (30, 32),
        "negative": (0, 256),
    },
    "raw/fingerprinted-gguf-q8_0.jsonl": {
        "condition": "FINGERPRINTED_GGUF_Q8_0",
        "records": 288,
        "positive": (31, 32),
        "negative": (0, 256),
    },
    "raw/fingerprinted-gguf-q4_k_m.jsonl": {
        "condition": "FINGERPRINTED_GGUF_Q4_K_M",
        "records": 288,
        "positive": (28, 32),
        "negative": (0, 256),
    },
}


def fail(message: str) -> None:
    raise AssertionError(message)


def equivalent(published: Any, recomputed: Any) -> bool:
    if isinstance(published, dict) and isinstance(recomputed, dict):
        return published.keys() == recomputed.keys() and all(
            equivalent(published[key], recomputed[key]) for key in published
        )
    if isinstance(published, float) and isinstance(recomputed, float):
        return math.isclose(published, recomputed, rel_tol=1e-12, abs_tol=1e-15)
    return published == recomputed


def main() -> int:
    verified: dict[str, Any] = {}
    for relative_path, expected in EXPECTED.items():
        path = PILOT_ROOT / relative_path
        records = list(read_jsonl(path))
        if len(records) != expected["records"]:
            fail(f"{relative_path}: expected {expected['records']} records")
        conditions = {record.get("condition") for record in records}
        if conditions != {expected["condition"]}:
            fail(f"{relative_path}: unexpected conditions {conditions}")

        metrics = evaluate_records(records)
        positive = metrics["positive_exact_match"]
        negative = metrics["negative_false_match"]
        observed_positive = (positive["successes"], positive["total"])
        observed_negative = (negative["successes"], negative["total"])
        if observed_positive != expected["positive"]:
            fail(
                f"{relative_path}: positive {observed_positive} != "
                f"{expected['positive']}"
            )
        if observed_negative != expected["negative"]:
            fail(
                f"{relative_path}: negative {observed_negative} != "
                f"{expected['negative']}"
            )
        verified[expected["condition"]] = metrics

    summary_path = PILOT_ROOT / "results" / "final-summary.json"
    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    if set(summary.get("conditions", {})) != set(verified):
        fail("final-summary.json condition set does not match raw records")
    for condition, metrics in verified.items():
        published = summary["conditions"][condition]
        for metric_name in ("positive_exact_match", "negative_false_match"):
            for field in ("successes", "total", "rate", "wilson_95"):
                if not equivalent(
                    published[metric_name][field], metrics[metric_name][field]
                ):
                    fail(f"{condition}: published {metric_name}.{field} is stale")

    generation = json.loads(
        (PILOT_ROOT / "data" / "generation_manifest.json").read_text(
            encoding="utf-8"
        )
    )
    if generation.get("seed") != 42:
        fail("generation seed changed")
    if generation.get("fingerprint_count") != 32:
        fail("fingerprint count changed")
    if generation.get("decoy_count") != 256:
        fail("decoy count changed")

    print(
        json.dumps(
            {
                "status": "ok",
                "raw_record_count": sum(item["records"] for item in EXPECTED.values()),
                "conditions": sorted(verified),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
