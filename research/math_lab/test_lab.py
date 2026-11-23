"""Independent negative controls and bounded brute-force oracle."""
import json
from math import gcd
from pathlib import Path
import tempfile
import unittest

from lab import beal_search, claim_gate, validate_registry


class LabTests(unittest.TestCase):
    def test_registry(self):
        data = validate_registry()
        self.assertEqual(len(data["problems"]), 8)
        self.assertEqual(sum(x["status"] == "solved" for x in data["problems"]), 1)

    def test_reject_duplicate_id(self):
        data = validate_registry()
        data["problems"].append(dict(data["problems"][0]))
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "registry.json"
            p.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(AssertionError):
                validate_registry(p)

    def test_positive_known_beal_identity(self):
        result = beal_search(6, 5)
        self.assertIn([3, 3, 6, 3, 3, 5], result["positive_controls_sample"])
        self.assertEqual(result["coprime_counterexamples"], [])
        self.assertFalse(result["award_eligible"])

    def test_independent_naive_oracle(self):
        max_base, max_exp = 5, 4
        expected = []
        total = 0
        for a in range(1, max_base + 1):
            for x in range(3, max_exp + 1):
                for b in range(1, max_base + 1):
                    for y in range(3, max_exp + 1):
                        for c in range(1, max_base + 1):
                            for z in range(3, max_exp + 1):
                                if a ** x + b ** y == c ** z:
                                    total += 1
                                    if gcd(gcd(a, b), c) == 1:
                                        expected.append([a, x, b, y, c, z])
        result = beal_search(max_base, max_exp)
        self.assertEqual(result["exact_equalities"], total)
        self.assertEqual(result["coprime_counterexamples"], expected)

    def test_claim_cannot_fake_prize_success(self):
        self.assertEqual(claim_gate({"claim": "prize_solution", "theorem_statement": "P!=NP"}), "FAIL")
        complete_fields = {"claim":"prize_solution", "theorem_statement":"S", "full_proof":"file",
                           "publication_url":"https://example.org", "independent_acceptance":"claimed"}
        self.assertEqual(claim_gate(complete_fields), "UNVERIFIED")

    def test_bound_guard(self):
        with self.assertRaises(ValueError):
            beal_search(1000, 6)


if __name__ == "__main__":
    unittest.main()
