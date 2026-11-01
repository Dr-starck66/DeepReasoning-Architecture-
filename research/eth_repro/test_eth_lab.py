"""Tests of finite identities, edge cases, hypothesis rejection and failure modes."""
import random
import unittest

try:
    from .eth_lab import (count_exhaustive, count_dpll, count_cutset,
                          deformed_polynomial_sum, discover_cutset,
                          interpolate_at_zero, run)
except ImportError:
    from eth_lab import (count_exhaustive, count_dpll, count_cutset,
                         deformed_polynomial_sum, discover_cutset,
                         interpolate_at_zero, run)


class FiniteETHIdentityTests(unittest.TestCase):
    def test_empty_formula(self):
        for n in range(7):
            for f in ((),):
                self.assertEqual((count_exhaustive(n, f), count_dpll(n, f),
                                  interpolate_at_zero(n, f)), (2**n,) * 3)

    def test_empty_clause(self):
        for n in range(6):
            f = ((),)
            self.assertEqual([count_exhaustive(n, f), count_dpll(n, f),
                              interpolate_at_zero(n, f)], [0] * 3)

    def test_known_counts(self):
        known = [(2, ((1, 2),), 3), (2, ((1,), (-1,)), 0),
                 (3, ((1, -1),), 8), (3, ((1,), (2,), (3,)), 1),
                 (4, ((1, 2), (3, 4)), 9)]
        for n, f, expected in known:
            self.assertEqual(count_exhaustive(n, f), expected)
            self.assertEqual(count_dpll(n, f), expected)
            self.assertEqual(interpolate_at_zero(n, f), expected)

    def test_interpolation_and_deformation(self):
        f = ((1, 2), (-2, 3), (1, -3))
        self.assertEqual(deformed_polynomial_sum(3, f, 0), count_exhaustive(3, f))
        self.assertEqual(interpolate_at_zero(3, f), count_exhaustive(3, f))

    def test_measurement_special_case(self):
        # Two groups connected only through x1 (the separator).
        f = ((1, 2), (-1, 3), (1, 4), (-1, 5))
        expected = count_exhaustive(5, f)
        self.assertEqual(count_cutset(5, f, (1,))[0], expected)
        self.assertEqual(discover_cutset(5, f, 2)["count"], expected)

    def test_errors(self):
        with self.assertRaises(ValueError):
            count_exhaustive(2, ((3,),))
        with self.assertRaises(ValueError):
            count_dpll(2, ((0,),))
        with self.assertRaises(ValueError):
            count_cutset(2, ((1,),), (1, 1))

    def test_experiment_negative_controls(self):
        report = run(seed=20261101, cases=30, nmax=6)
        self.assertEqual(report["status"], "PASS", report["failed_cases"])
        self.assertTrue(all(report["negative_controls"].values()))

    def test_reproducible_corpus(self):
        a = run(seed=1234, cases=8, nmax=5)
        b = run(seed=1234, cases=8, nmax=5)
        self.assertEqual(a["corpus_sha256"], b["corpus_sha256"])


if __name__ == "__main__":
    unittest.main()
