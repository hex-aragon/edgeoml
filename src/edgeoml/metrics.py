from __future__ import annotations

import math
import unicodedata
from statistics import NormalDist, fmean
from typing import Any, Iterable, Sequence


def normalize_text(value: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", value).strip().split())


def wilson_interval(
    successes: int, total: int, confidence: float = 0.95
) -> tuple[float, float]:
    if total <= 0:
        return (0.0, 0.0)
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between 0 and 1")
    if not 0 <= successes <= total:
        raise ValueError("successes must be between zero and total")

    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    proportion = successes / total
    denominator = 1 + (z * z / total)
    center = (proportion + (z * z / (2 * total))) / denominator
    margin = (
        z
        * math.sqrt(
            (proportion * (1 - proportion) / total)
            + (z * z / (4 * total * total))
        )
        / denominator
    )
    return (max(0.0, center - margin), min(1.0, center + margin))


def _sequence(record: dict[str, Any], prefix: str) -> Sequence[Any]:
    token_key = f"{prefix}_token_ids"
    if token_key in record:
        value = record[token_key]
        if not isinstance(value, list):
            raise ValueError(f"{token_key} must be a list")
        return value
    text_key = prefix
    value = record.get(text_key)
    if not isinstance(value, str):
        raise ValueError(
            f"record requires {token_key!r} or a string field {text_key!r}"
        )
    return normalize_text(value).split()


def exact_match(record: dict[str, Any]) -> bool:
    return list(_sequence(record, "candidate")) == list(_sequence(record, "reference"))


def prefix_match_ratio(record: dict[str, Any]) -> float:
    candidate = list(_sequence(record, "candidate"))
    reference = list(_sequence(record, "reference"))
    if not reference:
        return 1.0 if not candidate else 0.0
    matched = 0
    for candidate_item, reference_item in zip(candidate, reference):
        if candidate_item != reference_item:
            break
        matched += 1
    return matched / len(reference)


def _rate(successes: int, total: int) -> dict[str, Any]:
    lower, upper = wilson_interval(successes, total)
    return {
        "successes": successes,
        "total": total,
        "rate": successes / total if total else None,
        "wilson_95": {"lower": lower, "upper": upper},
    }


def evaluate_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    positives: list[dict[str, Any]] = []
    negatives: list[dict[str, Any]] = []
    for record in records:
        kind = record.get("kind")
        if kind == "positive":
            positives.append(record)
        elif kind == "negative":
            negatives.append(record)
        else:
            raise ValueError("every record kind must be 'positive' or 'negative'")

    if not positives and not negatives:
        raise ValueError("at least one prediction record is required")

    positive_matches = sum(exact_match(record) for record in positives)
    false_matches = sum(exact_match(record) for record in negatives)
    prefix_scores = [prefix_match_ratio(record) for record in positives]

    return {
        "schema_version": "0.1",
        "positive_exact_match": _rate(positive_matches, len(positives)),
        "negative_false_match": _rate(false_matches, len(negatives)),
        "positive_mean_prefix_match": fmean(prefix_scores) if prefix_scores else None,
        "negative_sample_warning": (
            "No negative controls were supplied; false-positive behavior is unknown."
            if not negatives
            else None
        ),
    }


def robustness_ratio(candidate_rate: float, reference_rate: float) -> float | None:
    if reference_rate <= 0:
        return None
    return candidate_rate / reference_rate
