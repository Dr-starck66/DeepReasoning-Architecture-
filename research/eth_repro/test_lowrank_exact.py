"""Finite exact checks of OpenAI Section 4 construction (not asymptotic)."""
import unittest
from fractions import Fraction as F
from lowrank_exact import FiniteSwapMatrix, all_labels, example_q2_row, swap, dense_rank


class ExactSwapTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.system=FiniteSwapMatrix.build(r=2,q=3,R=2,A0=0)

    def test_paper_literal_q2_row(self):
        row=example_q2_row()
        self.assertEqual(row,{
            ((0,0),(1,1)):(F(1),F(0)),
            ((1,0),(0,1)):(F(0),F(-1,2)),
            ((0,1),(1,0)):(F(0),F(-1)),
        })

    def test_swap_commutes_and_involutive(self):
        for lab in self.system.labels:
            for t in range(3):
                self.assertEqual(swap(swap(lab,(t,)),(t,)),lab)
                for s in range(3):
                    self.assertEqual(swap(swap(lab,(s,)),(t,)),swap(swap(lab,(t,)),(s,)))

    def test_spectrum_and_rank(self):
        a=self.system.audit()
        self.assertEqual(a['D'],64)
        self.assertEqual(a['rank_I_minus_M0'],10)
        self.assertEqual(a['rank_C'],10)
        self.assertEqual(a['measurement_fraction'],'5/32')
        self.assertEqual(a['rank_M0'],64) # M0 is NOT itself low rank

    def test_kernel_of_C_fixed_by_M(self):
        d=self.system
        # Derive projection formula using eigenbasis, not numerical sampling.
        for u in range(64):
            coeff=d.coefficients_from_measurements(u)
            for y in range(64):
                self.assertEqual(int(u==y)-d.M0[u][y],sum(c*row[y] for c,row in zip(coeff,d.C)))

    def test_nonzero_matrix_support(self):
        d=self.system
        for u,lab in enumerate(d.labels):
            for y,v in enumerate(d.labels):
                if d.M0[u][y]:
                    self.assertLessEqual(sum(v[0][s]!=lab[1][s] for s in range(3)),1)

    def test_polynomial_degree_and_identity(self):
        d=self.system
        for u in range(64):
            self.assertEqual(d.eval_row(u,0),tuple(F(int(u==y)) for y in range(64)))

    def test_localization_at_every_point(self):
        d=self.system
        for u in range(64):
            coeff=d.coefficients_from_measurements(u)
            for t in [1,2,3]:
                for y in range(64):
                    if d.labels[y][0][t-1]!=d.labels[u][1][t-1]:
                        self.assertEqual(d.eval_row(u,t)[y],sum(coeff[k]*d.C[k][y] for k in range(10)))

    def test_negative_control_swap_term(self):
        d=self.system
        mutated=[list(row) for row in d.M0]
        mutated[0][0]+=1
        incorrect=[[int(i==j)-mutated[i][j] for j in range(64)] for i in range(64)]
        # The bug makes rank(I-M0) > cB, contradicting low-rank claim.
        self.assertGreater(dense_rank(tuple(tuple(row) for row in incorrect)),10)

    def test_negative_control_measurement_zeroed(self):
        d=self.system
        corrupt=list(d.C)
        corrupt[0]=tuple(0 for _ in range(64))
        self.assertEqual(dense_rank(tuple(corrupt)),9)
        self.assertNotEqual(dense_rank(tuple(corrupt)),dense_rank(tuple(tuple(int(i==j)-d.M0[i][j] for j in range(64)) for i in range(64))))

    def test_non_asymptotic_documentation(self):
        self.assertEqual(self.system.R,2)
        self.assertLess(self.system.R,self.system.q)
        # Assumptions r,Q,R fixed; no statement involving n is audited here.

if __name__=='__main__':unittest.main(verbosity=2)