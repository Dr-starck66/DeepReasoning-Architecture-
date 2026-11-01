"""Exact comparison to OpenAI's paper statements, not the asymptotic theorem."""
import unittest
from fractions import Fraction as Q
try:
    from . import paper_exact as p
except ImportError:
    import paper_exact as p

class ManuscriptFiniteTests(unittest.TestCase):
    def setUp(self):
        self.cnf = ((1, 3, 4), (-1, 2), (2, -3), (-2, 4))
        self.groups = ((0, 1), (2, 3))
        self.owners = (0, 0, 1, 1)
        self.instance = p.cross_measurement_instance(4,self.cnf,self.groups,self.owners)

    def test_exact_boolean_satisfaction_formula(self):
        self.assertEqual(p.H(p.identity_instance(4,self.cnf)), (Q(5),))

    def test_occurrence_specific_replacement_and_degree(self):
        self.assertEqual(p.H(self.instance)[0],p.brute(4,self.cnf))
        self.assertLessEqual(len(p.H(self.instance))-1,self.instance.degree_bound())
        self.assertEqual(p.H(self.instance), (Q(5),Q(-3,2),Q(-4),Q(3),Q(-1,2)))

    def test_measurement_factorization_at_two_points(self):
        h=p.H(self.instance)
        for t in (1,2):
            self.assertTrue(p.check_measurement_design(self.instance,self.groups,self.owners,t)['valid'])
            self.assertEqual(p.separated_sum(self.instance,self.groups,self.owners,t),p.at(h,t))

    def test_invalid_design_fails_closed(self):
        with self.assertRaisesRegex(ValueError,'rowspace'):
            p.check_measurement_design(self.instance,self.groups,self.owners,0)

    def test_exact_hermite_reconstruction(self):
        r=p.hermite_reconstruct(self.instance)
        self.assertTrue(r['exact_polynomial_equal'])
        self.assertEqual(Q(r['H0_reconstructed']),5)
        self.assertEqual(r['coefficients_per_point'],10)

    def test_corrupt_hermite_data_is_rejected(self):
        h=p.H(self.instance); bound=self.instance.degree_bound(); order=bound//2+1
        d=[(t,p.taylor(h,t,order)) for t in (1,2)]
        self.assertEqual(p.reconstruct_from_taylor(bound,d),h)
        d[1]=(2,(d[1][1][0]+1,)+d[1][1][1:])
        with self.assertRaisesRegex(ValueError,'inconsistent'):
            p.reconstruct_from_taylor(bound,d)

    def test_negative_wrong_degree_rejected(self):
        h=p.H(self.instance)
        with self.assertRaises(ValueError):
            p.reconstruct_from_taylor(1, [(1,p.taylor(h,1,2)),(2,p.taylor(h,2,2))])

    def test_duplicate_literals_and_clauses_match_Lean_finsets(self):
        self.assertEqual(p.brute(3,((1,1,2),(1,1,2))),p.brute(3,((1,2),)))
        self.assertEqual(p.lean_encode_cnf(3,((1,1,2),(1,1,2))),p.lean_encode_cnf(3,((1,2),)))

    def test_encoding_deterministic(self):
        self.assertEqual(p.lean_encode_cnf(4,self.cnf),p.lean_encode_cnf(4,self.cnf[::-1]))
        self.assertEqual(p.lean_encode_cnf(1,()),[True,False,False])

    def test_small_random_cnf(self):
        r=p.finite_paper_audit(seed=77,trials=100)
        self.assertEqual(r['status'],'PASS',r['failures'])
        self.assertEqual(r['checks'],210)

if __name__=='__main__':
    unittest.main()
