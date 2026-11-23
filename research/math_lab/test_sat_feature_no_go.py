import copy
import unittest
from sat_feature_no_go import N, SAT, UNSAT, proof, signed_incidence
from sat_certificate import produce, verify


class FeatureNoGoTests(unittest.TestCase):
    def test_complete_constructive_proof(self):
        p = proof()
        self.assertEqual((p['n'], p['m']), (5, 13))
        self.assertTrue(p['strict_3cnf_unique_clauses'])
        self.assertTrue(p['independent_truth_table_verified'])
        self.assertEqual(signed_incidence(N, SAT), signed_incidence(N, UNSAT))

    def test_proofs_are_independently_checkable(self):
        for formula, verdict in ((SAT, 'SAT'), (UNSAT, 'UNSAT')):
            cert = produce(N, formula, strict_3cnf=True)
            self.assertEqual(cert['verdict'], verdict)
            self.assertTrue(verify(cert))

    def test_negative_control_incidence_mutation(self):
        corrupt = copy.deepcopy(SAT)
        corrupt[0][0] *= -1
        self.assertNotEqual(signed_incidence(N, corrupt), signed_incidence(N, UNSAT))

    def test_negative_control_missing_clause(self):
        self.assertNotEqual(signed_incidence(N, SAT[:-1]), signed_incidence(N, UNSAT))

    def test_no_prize_claim(self):
        p = proof()
        self.assertFalse(p['prize_eligible'])
        self.assertEqual(p['general_p_vs_np'], 'UNVERIFIED')

if __name__ == '__main__':
    unittest.main()
