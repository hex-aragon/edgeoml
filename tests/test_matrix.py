import unittest

from edgeoml.matrix import build_matrix


class MatrixTests(unittest.TestCase):
    def test_cartesian_product_and_stable_ids(self) -> None:
        config = {
            "experiment": "test",
            "fingerprint_count": 8,
            "models": [{"id": "model-a"}, {"id": "model-b"}],
            "seeds": [1, 2],
            "prompt_profiles": ["raw"],
            "conditions": [
                {
                    "runtime": "transformers",
                    "artifact_format": "safetensors",
                    "quantization": "BF16",
                    "role": "reference",
                },
                {
                    "runtime": "llama.cpp",
                    "artifact_format": "GGUF",
                    "quantization": "Q4_K_M",
                    "role": "quantized",
                },
            ],
        }
        first = build_matrix(config)
        second = build_matrix(config)
        self.assertEqual(len(first), 8)
        self.assertEqual(first, second)
        self.assertEqual(len({run["run_id"] for run in first}), 8)


if __name__ == "__main__":
    unittest.main()
