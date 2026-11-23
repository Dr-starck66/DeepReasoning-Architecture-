import copy
from itertools import product
import random
import unittest
from sat_certificate import validate_cnf, produce, verify, oracle, example_gate


class Certificates(unittest.TestCase):
    def test_pr17_strict_pair(self):
        results = example_gate()['results']
        self.assertEqual(results['sat']['verdict'], 'SAT')
        self.assertEqual(results['unsat']['verdict'], 'UNSAT')
        self.assertTrue(results['unsat']['oracle_agrees'])

    def test_non_strict_cnf(self):
        for clauses, expected in [([[1], [-1]], 'UNSAT'), ([[1]], 'SAT'), ([], 'SAT')]:
            c = produce(2, clauses)
            self.assertTrue(verify(c))
            self.assertEqual(c['verdict'], expected)

    def test_tampered_sat_witness(self):
        c = produce(3, [[1, 2, 3], [-1, -2, -3]], True)
        self.assertEqual(c['verdict'], 'SAT')
        c['witness'] = [0, 0, 0]
        self.assertFalse(verify(c))

    def test_tampered_unsat_leaf(self):
        c = produce(2, [[1], [-1]])
        self.assertEqual(c['verdict'], 'UNSAT')
        c['unsat_tree'] = {'conflict': 0}
        self.assertFalse(verify(c))

    def test_tampered_unsat_split(self):
        c = produce(2, [[1], [-1]])
        self.assertTrue(verify(c))
        c['unsat_tree'] = {'split': 1, 'false': {'conflict': 1}, 'true': {'conflict': 1}}
        self.assertFalse(verify(c))

    def test_strict_three_distinct_variables(self):
        for cl in [[[1, 1, 2]], [[1, -1, 2]], [[1, 2]], [[1, 2, 4]]]:
            with self.assertRaises(ValueError):
                produce(3, cl, True)

    def test_independent_randomized_oracle(self):
        rng = random.Random(20261123)
        checked = 0
        for n in range(3, 8):
            for _ in range(40):
                clauses = []
                for _ in range(rng.randint(0, 10)):
                    vs = rng.sample(range(1, n + 1), 3)
                    clauses.append([v * rng.choice((-1, 1)) for v in vs])
                c = produce(n, clauses, True)
                self.assertTrue(verify(c), (n, clauses))
                independent = oracle(n, validate_cnf(n, clauses, True))
                self.assertEqual(c['verdict'] == 'SAT', independent is not None)
                checked += 1
        self.assertEqual(checked, 200)

    def test_verifier_refuses_missing_child(self):
        c = produce(2, [[1], [-1]])
        c['unsat_tree'].pop('true')
        self.assertFalse(verify(c))

    def test_not_a_prize_claim(self):
        self.assertFalse(example_gate()['award_eligible'])
        self.assertEqual(example_gate()['general_p_vs_np'], 'UNVERIFIED')


if __name__ == '__main__':
    unittest.main()
