"""Deterministic discovery and independent negative-control suite."""
import copy
import unittest

from discovery_engine import (
    discover_switch, feature_signature, find_counterexample,
    independently_verify_receipt, independent_pairwise_audit, forcing_gadget,
)
from sat_certificate import oracle, validate_cnf


class DiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = find_counterexample(5)

    def test_unscripted_parity_switch_is_found(self):
        sw = discover_switch()
        self.assertGreater(sw['examined'], 1)
        self.assertLessEqual(sw['examined'], 70)
        self.assertEqual(len(sw['a']), 4)
        self.assertEqual(len(sw['b']), 4)
        self.assertNotEqual(sw['a'], sw['b'])
        self.assertEqual(feature_signature(3, sw['a'], 2), feature_signature(3, sw['b'], 2))
        self.assertNotEqual(feature_signature(3, sw['a'], 3), feature_signature(3, sw['b'], 3))

    def test_constructive_collision_certificate(self):
        r = self.r
        self.assertTrue(independently_verify_receipt(r))
        self.assertTrue(r['one_way_equal'])
        self.assertTrue(r['two_way_equal'])
        self.assertFalse(r['third_order_equal'])
        self.assertEqual(r['m'], 16)

    def test_all_n_5_to_8_using_unused_variable_padding(self):
        for n in range(5, 9):
            r = find_counterexample(n)
            self.assertTrue(independently_verify_receipt(r), n)
            self.assertEqual(r['n'], n)
            self.assertEqual(r['sat_clauses'], self.r['sat_clauses'])
            self.assertEqual(r['unsat_clauses'], self.r['unsat_clauses'])

    def test_independent_signed_pair_oracle(self):
        r = self.r
        self.assertTrue(independent_pairwise_audit(5, r['sat_clauses'], r['unsat_clauses']))
        self.assertIsNotNone(oracle(5, validate_cnf(5, r['sat_clauses'], True)))
        self.assertIsNone(oracle(5, validate_cnf(5, r['unsat_clauses'], True)))

    def test_forcing_gadget_all_targets(self):
        # Four sign pairs for x4,x5 force the chosen xi literal to be true.
        for target in ((False, False, False), (True, True, True), (True, False, True)):
            clauses = forcing_gadget(target)
            self.assertEqual(len(clauses), 12)
            for values in __import__('itertools').product((False, True), repeat=5):
                satisfied = all(any((lit > 0) == values[abs(lit)-1] for lit in c) for c in clauses)
                self.assertEqual(satisfied, tuple(values[:3]) == target)

    def test_negative_control_flipped_sign(self):
        r = self.r
        mutant = copy.deepcopy(r['sat_clauses'])
        mutant[0][0] *= -1
        self.assertFalse(independent_pairwise_audit(5, mutant, r['unsat_clauses']))

    def test_negative_control_corrupted_sat_witness(self):
        r = copy.deepcopy(self.r)
        r['sat_witness'] = [1, 1, 1, 1, 1]
        self.assertFalse(independently_verify_receipt(r))

    def test_negative_control_corrupted_unsat_tree(self):
        r = copy.deepcopy(self.r)
        r['certificates']['unsat']['unsat_tree'] = {'conflict': 0}
        self.assertFalse(independently_verify_receipt(r))

    def test_negative_control_missing_clause(self):
        r = copy.deepcopy(self.r)
        r['unsat_clauses'] = r['unsat_clauses'][:-1]
        self.assertFalse(independently_verify_receipt(r))

    def test_negative_control_digest_tampering(self):
        r = copy.deepcopy(self.r)
        r['general_result'] = 'P != NP PROVED'
        self.assertFalse(independently_verify_receipt(r))

    def test_general_p_vs_np_not_claimed(self):
        self.assertEqual(self.r['p_vs_np'], 'UNVERIFIED')
        self.assertFalse(self.r['prize_eligible'])


if __name__ == '__main__':
    unittest.main()
