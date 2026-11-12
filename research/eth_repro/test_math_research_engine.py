import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from math_research_engine import (construct_matrix, difference, rank_over_q,
                                  rank_mod_prime, compare_existing, canonical_sha,
                                  research, swap_bits)

class ResearchGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.m = construct_matrix()
    def test_64_rows_each_64(self):
        self.assertEqual(len(self.m), 64)
        self.assertTrue(all(len(x) == 64 for x in self.m))
    def test_swap_involution(self):
        for u in range(64):
            for axis in range(3):
                self.assertEqual(swap_bits(swap_bits(u,(axis,)),(axis,)), u)
    def test_commuting_swaps(self):
        for u in range(64):
            for i in range(3):
                for j in range(3):
                    self.assertEqual(swap_bits(swap_bits(u,(i,)),(j,)),swap_bits(swap_bits(u,(j,)),(i,)))
    def test_exact_rank(self):
        self.assertEqual(rank_over_q(difference(self.m)), 10)
    def test_two_prime_crosschecks(self):
        for p in (101, 103):
            self.assertEqual(rank_mod_prime(difference(self.m),p), 10)
    def test_m0_not_low_rank(self):
        self.assertEqual(rank_over_q(self.m),64)
    def test_mutation_detected(self):
        m = [list(r) for r in self.m]
        m[0][0] += 1
        self.assertNotEqual(rank_over_q(difference(tuple(tuple(r) for r in m))),10)
    def test_other_false_conjecture_detected(self):
        self.assertNotEqual(rank_over_q(self.m), 10)
    def test_no_existing_source_is_unverified(self):
        with TemporaryDirectory() as td:
            self.assertEqual(compare_existing(Path(td),self.m)['status'],'UNVERIFIED')
    def test_receipt_determinism_and_limits(self):
        with TemporaryDirectory() as td:
            a = research(Path(td)); b = research(Path(td))
            self.assertEqual(a['receipt_sha256'],b['receipt_sha256'])
            self.assertEqual(a['receipt_sha256'],canonical_sha({k:v for k,v in a.items() if k != 'receipt_sha256'}))
            self.assertEqual(a['claim_status'],'PASS')
            self.assertEqual(a['global_lean_formalization_of_rank'],'UNVERIFIED')
            self.assertEqual(a['integration_with_existing_astra']['status'],'UNVERIFIED')
    def test_empty_matrix(self):
        self.assertEqual(rank_over_q(()),0)
        self.assertEqual(rank_mod_prime((),101),0)

if __name__ == '__main__':
    unittest.main(verbosity=2)
