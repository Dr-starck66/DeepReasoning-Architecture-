import unittest
from parametric_spectrum import (
    LOCAL, a_sparse, assess, check_spectral, compare_existing_q3,
    eigenvalue, rank_by_multiplicities, rank_formula, rank_mod,
    sparse_times_vector, vector,
)


class ParametricSpectrumTests(unittest.TestCase):
    def test_local_basis_is_explicit(self):
        self.assertEqual(LOCAL[3], (0, 1, -1, 0))
        self.assertEqual(len(set(LOCAL)), 4)

    def test_known_q3_rank_preserved(self):
        self.assertEqual(rank_formula(3), 10)
        self.assertEqual(compare_existing_q3(a_sparse(3))["status"], "PASS")

    def test_uniform_arithmetic_counts_up_to_twelve(self):
        for q in range(1, 13):
            with self.subTest(q=q):
                self.assertEqual(rank_formula(q), rank_by_multiplicities(q))

    def test_eigenvalue_zeros_only_k_0_1(self):
        self.assertEqual(eigenvalue(0), 0)
        self.assertEqual(eigenvalue(1), 0)
        for k in range(2, 30):
            self.assertNotEqual(eigenvalue(k), 0)

    def test_exhaustive_tensor_eigenvectors_q1_q4(self):
        for q in range(1, 5):
            with self.subTest(q=q):
                result = check_spectral(q, exhaustive=True)
                self.assertEqual(result["status"], "PASS", result["failures"])
                self.assertEqual(result["checked_modes"], 4 ** q)
                self.assertEqual(result["checked_equations"], 16 ** q)

    def test_modular_rank_q1_q4_independent(self):
        for q in range(1, 5):
            with self.subTest(q=q):
                mat = a_sparse(q)
                self.assertEqual(rank_mod(mat, 101), rank_formula(q))
                self.assertEqual(rank_mod(mat, 103), rank_formula(q))

    def test_adversarial_matrix_mutation_is_detected(self):
        q = 4
        v = vector((0,) * q)
        self.assertEqual(sparse_times_vector(v, q), tuple(0 for _ in v))
        self.assertNotEqual(sparse_times_vector(v, q, True),
                            tuple(0 for _ in v))

    def test_bad_rank_rejected_by_independent_modular_rank(self):
        self.assertNotEqual(rank_mod(a_sparse(4), 103), 66)

    def test_q5_is_only_a_sample_not_exhaustive(self):
        result = check_spectral(5, exhaustive=False)
        self.assertEqual(result["status"], "PASS", result["failures"])
        self.assertFalse(result["exhaustive"])
        self.assertLess(result["checked_modes"], 4 ** 5)

    def test_receipt_and_falsifications(self):
        result = assess()
        self.assertEqual(result["finite_computational_status"], "PASS")
        self.assertEqual(result["uniform_Lean_matrix_rank_proof"], "UNVERIFIED")
        self.assertTrue(all(result["negative_controls"].values()))
        self.assertEqual(result["finite_exhaustive_q_1_to_4"]["4"]["predicted_rank"], 67)


if __name__ == "__main__":
    unittest.main()
