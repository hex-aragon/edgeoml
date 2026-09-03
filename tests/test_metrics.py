import unittest

from edgeoml.metrics import (
    evaluate_records,
    normalize_text,
    prefix_match_ratio,
    robustness_ratio,
    wilson_interval,
)


class MetricsTests(unittest.TestCase):
    def test_normalize_text(self) -> None:
        self.assertEqual(normalize_text("  alpha\n beta  "), "alpha beta")

    def test_prefix_match_uses_token_ids_when_present(self) -> None:
        record = {
            "candidate_token_ids": [1, 2, 9],
            "reference_token_ids": [1, 2, 3, 4],
        }
        self.assertEqual(prefix_match_ratio(record), 0.5)

    def test_evaluate_records(self) -> None:
        summary = evaluate_records(
            [
                {
                    "kind": "positive",
                    "candidate_token_ids": [1],
                    "reference_token_ids": [1],
                },
                {
                    "kind": "positive",
                    "candidate_token_ids": [2],
                    "reference_token_ids": [1],
                },
                {
                    "kind": "negative",
                    "candidate_token_ids": [4],
                    "reference_token_ids": [5],
                },
            ]
        )
        self.assertEqual(summary["positive_exact_match"]["rate"], 0.5)
        self.assertEqual(summary["negative_false_match"]["rate"], 0.0)
        self.assertIsNone(summary["negative_sample_warning"])

    def test_wilson_interval_contains_observed_rate(self) -> None:
        lower, upper = wilson_interval(90, 100)
        self.assertLess(lower, 0.9)
        self.assertGreater(upper, 0.9)

    def test_negative_only_control_is_supported(self) -> None:
        summary = evaluate_records(
            [
                {
                    "kind": "negative",
                    "candidate_token_ids": [1],
                    "reference_token_ids": [2],
                }
            ]
        )
        self.assertIsNone(summary["positive_exact_match"]["rate"])
        self.assertEqual(summary["negative_false_match"]["rate"], 0.0)

    def test_robustness_ratio(self) -> None:
        self.assertEqual(robustness_ratio(0.8, 1.0), 0.8)
        self.assertIsNone(robustness_ratio(0.8, 0.0))


if __name__ == "__main__":
    unittest.main()
