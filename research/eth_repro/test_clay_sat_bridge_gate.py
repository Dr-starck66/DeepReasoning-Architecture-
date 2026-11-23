import unittest

from clay_sat_bridge_gate import (
    SAT, UNSAT, TAUTOLOGY, TWO_LOCAL_FACTORS,
    make_case, report, truth_vector,
)
from eth_lab import count_exhaustive
from projected_spectrum import apply_scaled_dp


class ClaySATBridgeGateTests(unittest.TestCase):
    def test_sat_unsat_collision_after_projection(self):
        for q in (2, 3, 4):
            with self.subTest(q=q):
                n = 2*q
                self.assertGreater(count_exhaustive(n, SAT), 0)
                self.assertEqual(count_exhaustive(n, UNSAT), 0)
                a = apply_scaled_dp(truth_vector(q, SAT), q)
                b = apply_scaled_dp(truth_vector(q, UNSAT), q)
                self.assertEqual(a, b)
                self.assertFalse(any(a))

    def test_tautology_unsat_collision_even_more_basic(self):
        for q in (2, 3, 4):
            self.assertEqual(
                apply_scaled_dp(truth_vector(q, TAUTOLOGY), q),
                apply_scaled_dp(truth_vector(q, UNSAT), q)
            )

    def test_true_positive_control_uses_two_antisymmetric_axes(self):
        for q in (2, 3, 4):
            self.assertTrue(any(apply_scaled_dp(
                truth_vector(q, TWO_LOCAL_FACTORS), q
            )), f"q={q}: unexpected zero, test would be vacuous")

    def test_all_finite_witnesses_pass(self):
        result = report()
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["tested_q"], [2, 3, 4])
        self.assertTrue(all(c["status"] == "PASS" for c in result["cases"]))
        self.assertTrue(all(all(c["checks"].values()) for c in result["cases"]))
        self.assertEqual(result["complexity_check"]["P_vs_NP_resolution"],
                         "NOT ESTABLISHED")

    def test_exponential_table_cost_is_not_hidden(self):
        for q in (2, 3, 4):
            case = make_case(q)
            self.assertEqual(case["declared_variables"], 2*q)
            self.assertEqual(case["vector_dimension"], 2**(2*q))

    def test_invalid_q_or_non3cnf_is_rejected(self):
        for q in (0, 5):
            with self.assertRaises(ValueError):
                truth_vector(q, SAT)
        with self.assertRaises(ValueError):
            truth_vector(2, ((1, 2, 3, 4),))


if __name__ == "__main__":
    unittest.main()
