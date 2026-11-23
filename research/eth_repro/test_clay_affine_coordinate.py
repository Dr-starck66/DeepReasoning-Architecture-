from itertools import combinations
from math import comb
from random import Random
import unittest

from clay_affine_coordinate import coordinate_affine, extract_parities, walsh_in_place
from clay_swap_coordinate import coordinate_eliminate, coordinate_enumerated
from eth_lab import count_exhaustive, satisfied


def encode_parity(scope, target):
    return tuple(tuple(-x if bits & (1 << i) else x for i, x in enumerate(scope))
                 for bits in range(1 << len(scope)) if bits.bit_count() % 2 != target)


def dense_parity_code(seed_bits):
    """Every pair of distinct nonzero binary forms belongs to a parity triple."""
    q = (1 << seed_bits) - 1
    return tuple(clause
                 for a in range(1, q + 1)
                 for b in range(a + 1, q + 1)
                 if b < (a ^ b)
                 for clause in encode_parity((a, b, a ^ b), 0))


def binomial_coordinate_weight(q, ones):
    coeff = [sum((-1)**j * comb(ones, j) * comb(q - ones, k - j)
                 for j in range(k + 1)) for k in (2, 3)]
    return 4 * (coeff[0] - coeff[1])


def code_oracle(seed_bits, residual=(), extras=0):
    """Evaluate all generator seeds, then use the independent binomial count."""
    length = (1 << seed_bits) - 1
    weights = []
    for seed in range(1 << seed_bits):
        word = sum(((var & seed).bit_count() % 2) << (var - 1)
                   for var in range(1, length + 1))
        if satisfied(word, residual):
            weights.append(word.bit_count())
    count = len(weights) << extras
    coordinate = sum(comb(extras, j) * binomial_coordinate_weight(length + extras, k + j)
                     for k in weights for j in range(extras + 1))
    return count, coordinate


class AffineCoordinateTests(unittest.TestCase):
    def test_complete_and_incomplete_parities(self):
        group = encode_parity((1, 2, 3), 1)
        equations, residual = extract_parities(3, group)
        self.assertEqual(equations, [(7, 1)])
        self.assertEqual(residual, ())
        equations, residual = extract_parities(3, group[:-1])
        self.assertEqual(equations, [])
        self.assertEqual(set(residual), set(group[:-1]))
        self.assertEqual(coordinate_affine(3, group).models, 4)
        self.assertEqual(coordinate_affine(3, group[:-1]).models, 5)

    def test_both_parities_and_empty_clause(self):
        for cnf in (((),), ((1, 1), (-1,)),
                    encode_parity((1, 2), 0) + encode_parity((1, 2), 1)):
            result = coordinate_affine(3, cnf)
            self.assertEqual((result.models, result.coordinate), (0, 0))

    def test_random_small_formulas_with_verified_oracles(self):
        rng = Random(401118)
        for _ in range(420):
            q = rng.randrange(9)
            constraints = []
            for _ in range(rng.randrange(5)):
                scope = tuple(rng.sample(range(1, q + 1), rng.randint(1, min(3, q)))) if q else ()
                if scope:
                    constraints.extend(encode_parity(scope, rng.randrange(2)))
            for _ in range(rng.randrange(9)):
                constraints.append(tuple(rng.choice((-1, 1)) * rng.randint(1, q)
                                         for _ in range(rng.randint(0, 3) if q else 0)))
            rng.shuffle(constraints)
            cnf = tuple(constraints)
            result = coordinate_affine(q, cnf)
            self.assertEqual(result.models, count_exhaustive(q, cnf))
            self.assertEqual(result.coordinate, coordinate_enumerated(q, cnf))
            self.assertEqual(result.coordinate, coordinate_eliminate(q, cnf).value)

    def test_combinatorial_oracle_on_complete_primal_graph(self):
        q = 127
        cnf = dense_parity_code(7)
        scopes = {tuple(map(abs, clause)) for clause in cnf}
        self.assertEqual({edge for scope in scopes for edge in combinations(scope, 2)},
                         set(combinations(range(1, q + 1), 2)))
        with self.assertRaisesRegex(ValueError, "induced width 126"):
            coordinate_eliminate(q, cnf)
        result = coordinate_affine(q, cnf, rank_limit=0)
        self.assertEqual((result.models, result.coordinate), code_oracle(7))
        self.assertEqual((result.affine_dimension, result.quotient_points), (7, 1))

    def test_single_mutated_parity_creates_global_contradiction(self):
        cnf = dense_parity_code(5)
        original = encode_parity((1, 2, 3), 0)
        mutated = tuple(clause for clause in cnf if clause not in original)
        mutated += encode_parity((1, 2, 3), 1)
        result = coordinate_affine(31, mutated)
        self.assertEqual((result.models, result.coordinate, result.quotient_points), (0, 0, 0))

    def test_mixed_formula_and_large_integer_fibers(self):
        residual = ((1, 2, 4), (1, -3, 8), (-2, -4, 8))
        cnf = dense_parity_code(5) + residual
        result = coordinate_affine(31 + 70, cnf, rank_limit=4)
        self.assertEqual((result.models, result.coordinate), code_oracle(5, residual, 70))
        self.assertEqual((result.affine_dimension, result.residual_rank), (75, 4))
        self.assertGreater(result.models, 1 << 70)

    def test_walsh_orientation_and_rank_guard(self):
        selected = [2, -7, 3, 9, 0, 0, -12, 6]
        expected = [sum(c * (-1)**((z & t).bit_count() % 2)
                        for t, c in enumerate(selected)) for z in range(8)]
        walsh_in_place(selected)
        self.assertEqual(selected, expected)
        width17 = tuple((x, x + 1) for x in range(1, 17))
        with self.assertRaisesRegex(ValueError, "residual affine rank 17"):
            coordinate_affine(17, width17)


if __name__ == "__main__":
    unittest.main()
