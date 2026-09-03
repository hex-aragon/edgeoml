import unittest

from edgeoml.receipt import HASH_FIELDS, validate_receipt


class ReceiptTests(unittest.TestCase):
    def base_receipt(self) -> dict:
        receipt = {
            "schema_version": "0.1",
            "assurance_level": "L0_SELF_DECLARED",
            "agent_id": "agent",
            "model_id": "model",
            "runtime": "runtime",
            "artifact_format": "GGUF",
            "quantization": "Q4_K_M",
            "nonce": "nonce",
            "counter": 0,
            "signature_algorithm": "test",
            "signature": "signature",
        }
        receipt.update({field: "a" * 64 for field in HASH_FIELDS})
        return receipt

    def test_valid_l0_receipt(self) -> None:
        self.assertEqual(validate_receipt(self.base_receipt()), [])

    def test_l1_requires_platform_attestation(self) -> None:
        receipt = self.base_receipt()
        receipt["assurance_level"] = "L1_APP_DEVICE_ATTESTED"
        self.assertIn("L1 receipts require platform_attestation", validate_receipt(receipt))


if __name__ == "__main__":
    unittest.main()
