import unittest
from spectral_certificate import assess, basis_vector, eigenvalue, model_matrix, pair_det, verify_columns


class SpectralCertificateTests(unittest.TestCase):
    def test_nonzero_local_determinant(self):
        self.assertEqual(abs(pair_det()), 2)

    def test_all_64_spectral_columns(self):
        out = verify_columns(model_matrix())
        self.assertTrue(out['ok'], out['failures'])
        self.assertEqual(out['equations_checked'], 4096)
        self.assertEqual(out['nonzero_eigenvalue_multiplicities_I_minus_M0'], {'4': 9, '-4': 1})

    def test_rank_10_from_invertible_eigenbasis(self):
        report = assess(verify_astra=False)
        self.assertEqual(report['rank_over_Q_from_spectrum'], 10)
        self.assertEqual(report['computational_certificate_status'], 'PASS')

    def test_mutation_rejected(self):
        matrix = [list(row) for row in model_matrix()]
        matrix[0][0] += 1
        self.assertFalse(verify_columns(tuple(map(tuple, matrix)))['ok'])

    def test_wrong_eigenvalues_rejected(self):
        self.assertFalse(verify_columns(model_matrix(), wrong_eigenvalues=True)['ok'])

    def test_nontrivial_basis(self):
        self.assertNotEqual(basis_vector((3, 3, 3)), basis_vector((2, 2, 2)))
        self.assertEqual(eigenvalue((3, 3, 3)), 5)


if __name__ == '__main__':
    unittest.main()
