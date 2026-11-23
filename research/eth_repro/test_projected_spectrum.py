import unittest
from math import comb

from projected_spectrum import (
    apply_scaled, apply_scaled_dp, dp_vs_polynomial, compare_original_q3, exhaustive_spectrum,
    integer_swap_coefficients, matrix_scaled, rank_filter,
    report, scalar_eigenvalue,
)
from parametric_spectrum import rank_mod, rank_formula, vector


class ProjectedSpectrumTests(unittest.TestCase):
    def test_q3_exact_original_matrix_4096_entries(self):
        evidence = compare_original_q3()
        self.assertEqual(evidence["status"], "PASS", evidence)
        self.assertEqual(evidence["checked_entries"], 4096)

    def test_exhaustive_q1_to_q4_eigenvector_equations(self):
        total = 0
        for q in range(1, 5):
            with self.subTest(q=q):
                evidence = exhaustive_spectrum(q)
                self.assertEqual(evidence["status"], "PASS", evidence)
                self.assertEqual(evidence["equations"], 16 ** q)
                total += evidence["equations"]
        self.assertEqual(total, 16+256+4096+65536)

    def test_independent_modular_rank_q1_to_q4(self):
        self.assertEqual([rank_filter(q) for q in range(1, 5)], [0, 1, 10, 66])
        for q in range(1, 5):
            mat = matrix_scaled(q)
            with self.subTest(q=q):
                self.assertEqual(rank_mod(mat, 101), rank_filter(q))
                self.assertEqual(rank_mod(mat, 103), rank_filter(q))

    def test_projector_eigenvalues_all_negative_counts(self):
        for q in range(1, 15):
            for k in range(q + 1):
                expected = 4 if k == 2 else (-4 if k == 3 else 0)
                self.assertEqual(scalar_eigenvalue(q, k, scaled=False), expected)

    def test_original_q4_falsely_identified_rejected(self):
        from parametric_spectrum import a_sparse
        self.assertNotEqual(matrix_scaled(4),
                            tuple(tuple(16 * z for z in row) for row in a_sparse(4)))

    def test_q2_and_q3_preserved_but_q4_better(self):
        self.assertEqual(rank_filter(2), rank_formula(2))
        self.assertEqual(rank_filter(3), rank_formula(3))
        self.assertLess(rank_filter(4), rank_formula(4))
        self.assertLess(rank_filter(30) / 4**30, 0.04)
        self.assertLess(rank_filter(40) / 4**40, 0.005)

    def test_q5_selected_eigenvector_sample_only(self):
        q = 5
        samples = [(0,)*5, (3,)*5, (3,3,2,2,2),
                   (3,3,3,2,2), (3,3,3,3,2)]
        for label in samples:
            v = vector(label)
            lam = scalar_eigenvalue(q, label.count(3))
            with self.subTest(label=label):
                self.assertEqual(apply_scaled(v, q), tuple(lam * z for z in v))

    def test_coefficients_are_integral_and_reusable(self):
        for q in range(1, 6):
            coeff = integer_swap_coefficients(q)
            self.assertEqual(len(coeff), 2**q)
            self.assertTrue(all(isinstance(z, int) for z in coeff))

    def test_adversarial_coefficient_mutation_rejected(self):
        zero = vector((0,)*4)
        self.assertNotEqual(apply_scaled(zero, 4, mutate_entry=True),
                            apply_scaled(zero, 4))

    def test_false_eigenvalue_rejected(self):
        zero = vector((0,)*4)
        self.assertNotEqual(apply_scaled(zero, 4), zero)

    def test_wrong_rank_prediction_rejected(self):
        self.assertNotEqual(rank_mod(matrix_scaled(4), 103), 65)

    def test_dp_matches_polynomial_q1_q5_for_three_inputs(self):
        for q in range(1, 6):
            with self.subTest(q=q):
                result = dp_vs_polynomial(q)
                self.assertEqual(result["status"], "PASS", result)
                self.assertEqual(result["vectors_checked"], 3)

    def test_dp_exact_matrix_action_q3(self):
        mat = matrix_scaled(3)
        for index in (0, 1, 7, 31, 63):
            v = [0] * 64
            v[index] = 1
            expected = tuple(row[index] for row in mat)
            self.assertEqual(apply_scaled_dp(v, 3), expected)

    def test_dp_rejects_wrong_dimension(self):
        with self.assertRaises(ValueError):
            apply_scaled_dp((1, 0), 3)

    def test_report_marks_uniform_formal_proof_unverified(self):
        evidence = report()
        self.assertEqual(evidence["finite_status"], "PASS", evidence)
        self.assertEqual(evidence["uniform_Lean_Matrix_rank_proof"], "UNVERIFIED")
        self.assertEqual(evidence["runtime_advantage"], "UNVERIFIED")
        self.assertTrue(all(evidence["negative_controls"].values()))
        self.assertTrue(all(x["status"]=="PASS" for x in
                            evidence["dynamic_programming_crosschecks_q1_q5"]))
        self.assertEqual(evidence["q3_original_exact_matrix_comparison"]["mismatches"], 0)
        self.assertEqual(evidence["q5_sample_eigenvectors"]["exhaustive"], False)


if __name__ == "__main__":
    unittest.main()
