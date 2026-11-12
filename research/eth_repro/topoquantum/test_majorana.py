import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent))
import unittest
from fractions import Fraction
from majorana import bdg, edge_modes, apply, rank_exact, particle_hole, symmetric, zero, assess, multiply

class MajoranaFiniteTests(unittest.TestCase):
    def test_exact_sweetspot_nullity_n2_to_n9(self):
        for n in range(2,10):
            with self.subTest(n=n):
                h=bdg(n)
                self.assertEqual(rank_exact(h),2*n-2)
                for v in edge_modes(n): self.assertTrue(zero(apply(h,v)))
    def test_exact_spectrum_minimal_polynomial(self):
        for n in range(2,9):
            h=bdg(n)
            cube=multiply(multiply(h,h),h)
            self.assertTrue(all(cube[i][j]==4*h[i][j] for i in range(2*n) for j in range(2*n)))
    def test_phs_and_hermiticity(self):
        for param in ((3,1,1,0,False),(4,2,1,5,True),(5,Fraction(1,2),Fraction(2,3),Fraction(1,7),False)):
            h=bdg(*param)
            self.assertTrue(particle_hole(h))
            self.assertTrue(symmetric(h))
    def test_negative_trivial_phase(self):
        self.assertEqual(rank_exact(bdg(4,mu=5)),8)
    def test_negative_no_edges(self):
        self.assertEqual(rank_exact(bdg(4,periodic=True)),8)
    def test_negative_sweetspot_perturbation(self):
        self.assertFalse(zero(apply(bdg(4,delta=Fraction(1,2)),edge_modes(4)[0])))
    def test_input_validation(self):
        for invalid in (0,1,-2,True,1.5,25):
            with self.assertRaises(ValueError): bdg(invalid)
        with self.assertRaises(ValueError): bdg(2,periodic=True)
    def test_assessment_passes_and_rejects_negatives(self):
        result=assess((2,3,4,5,6,7,8))
        self.assertEqual(result['finite_computation_status'],'PASS')
        self.assertEqual(result['formal_lean_compilation'],'UNVERIFIED')
        self.assertTrue(all(result['negative_controls'].values()))
    def test_general_parameters_do_not_spuriously_assert_two_zero(self):
        self.assertEqual(rank_exact(bdg(3,t=1,delta=0,mu=4)),6)
    def test_matrix_invariants_unmodified(self):
        h=bdg(3)
        self.assertEqual(len(h),6)
        self.assertTrue(all(len(r)==6 for r in h))
        self.assertTrue(all(isinstance(x,Fraction) for row in h for x in row))

if __name__=='__main__': unittest.main()