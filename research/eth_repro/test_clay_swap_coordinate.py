import itertools
from math import comb
import random
import unittest

from clay_swap_coordinate import (
    coordinate_by_model_counts, coordinate_eliminate, coordinate_enumerated,
    coordinate_weight, gap_instance,
)
from eth_lab import count_dpll, count_exhaustive, satisfied
from projected_spectrum import apply_scaled_dp, integer_swap_coefficients


def histogram_reference(q, cnf):
    """Independent oracle using the binomial expansion at each Hamming weight."""
    counts = [0] * (q + 1)
    for mask in range(1 << q):
        if satisfied(mask, cnf):
            counts[mask.bit_count()] += 1
    return sum(4 * counts[t] * sum(
        (-1)**degree * comb(t, j) * comb(q - t, degree - j) * (-1)**j
        for degree in (2, 3) for j in range(degree + 1)
    ) for t in range(q + 1))


class SwapCoordinateTests(unittest.TestCase):
    def test_coefficient_against_existing_swap_expansion(self):
        for q in range(1, 7):
            self.assertEqual(tuple(coordinate_weight(q, mask.bit_count())
                                   for mask in range(1 << q)),
                             integer_swap_coefficients(q))

    def test_balanced_weights_and_mutation(self):
        for q in range(2, 258, 2):
            self.assertEqual(coordinate_weight(q, q // 2), -2 * q)
            self.assertEqual(coordinate_weight(q, q // 2 - 1), 2 * q)
        # Dropping the cubic term changes the claimed coefficient.
        self.assertNotEqual(4 * ((4 - 10) // 2), coordinate_weight(10, 4))

    def test_matrix_coordinate_against_existing_dp(self):
        rng = random.Random(20261123)
        for q in range(1, 6):
            for _ in range(12):
                cnf = tuple(tuple(rng.choice((-1, 1)) * x for x in
                                  rng.sample(range(1, q + 1), min(q, 3)))
                            for _ in range(4))
                truth_table = tuple(int(satisfied(mask, cnf)) for mask in range(4**q))
                fixed = ((1 << q) - 1) << q
                self.assertEqual(coordinate_eliminate(q, cnf).value,
                                 apply_scaled_dp(truth_table, q)[fixed])

    def test_exact_gap_reduction_and_strict_clauses(self):
        pairs = [
            (0, (), 0, ((),)),
            (0, ((),), 0, ()),
            (2, (), 1, ()),
            (2, ((1,),), 1, ()),
            (2, ((1, 1, -2), (1, -1, 2)), 1, ((-1,),)),
            (3, ((-1, 2, 3),), 0, ()),
        ]
        for n, left, m, right in pairs:
            with self.subTest(left=left, right=right):
                q, cnf = gap_instance(n, left, m, right)
                self.assertTrue(all(len(clause) == len(set(map(abs, clause))) == 3
                                    for clause in cnf))
                left_count = count_exhaustive(n, left)
                right_count = count_exhaustive(m, right)
                self.assertEqual(count_dpll(q, cnf), left_count + right_count)
                self.assertEqual(coordinate_eliminate(q, cnf).value,
                                 2 * q * (left_count - right_count))

    def test_assignment_by_assignment_unique_extension(self):
        left = ((1, -2, 3), (-3,))
        right = ((1,), (-1,))
        q, cnf = gap_instance(3, left, 1, right)
        selector = 1 << 4
        observed = []
        for mask in range(1 << q):
            if satisfied(mask, cnf):
                self.assertFalse(mask & selector)
                self.assertEqual(mask & (1 << 3), 0)
                self.assertEqual(mask.bit_count(), q // 2 - 1)
                observed.append(mask & 7)
        self.assertEqual(sorted(observed), [mask for mask in range(8)
                                            if satisfied(mask, left)])

    def test_random_signed_gap_against_independent_model_counter(self):
        rng = random.Random(1927)

        def formula(n):
            return tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n)
                               for _ in range(rng.randrange(4)))
                         for _ in range(rng.randrange(7)))

        for i in range(60):
            n, m = rng.randint(1, 5), rng.randint(1, 5)
            left, right = formula(n), formula(m)
            q, cnf = gap_instance(n, left, m, right)
            expected = 2 * q * (count_dpll(n, left) - count_dpll(m, right))
            # Reversal removes the freshly introduced complements before their mates.
            self.assertEqual(coordinate_eliminate(q, cnf, tuple(range(q, 0, -1))).value,
                             expected, f"seeded instance {i}")

    def test_elimination_random_formulas_and_orders(self):
        rng = random.Random(8691)
        for q in range(8):
            for _ in range(30):
                cnf = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, q)
                                   for _ in range(rng.randrange(4) if q else 0))
                             for _ in range(rng.randrange(6)))
                order = list(range(1, q + 1))
                rng.shuffle(order)
                self.assertEqual(coordinate_eliminate(q, cnf, order).value,
                                 histogram_reference(q, cnf))
                self.assertEqual(coordinate_enumerated(q, cnf),
                                 histogram_reference(q, cnf))
                self.assertEqual(coordinate_by_model_counts(q, cnf),
                                 histogram_reference(q, cnf))

    def test_cancellation_and_adversarial_width(self):
        q, cnf = gap_instance(2, ((1,),), 1, ())
        self.assertEqual(count_dpll(q, cnf), 4)
        self.assertEqual(coordinate_eliminate(q, cnf).value, 0)
        dense = tuple(itertools.combinations(range(1, 11), 2))
        with self.assertRaisesRegex(ValueError, "induced width 9"):
            coordinate_eliminate(10, dense, width_limit=8)
        self.assertEqual(coordinate_eliminate(10, dense, width_limit=9).induced_width, 9)
        with self.assertRaises(ValueError):
            coordinate_eliminate(3, (), (1, 1, 3))
        with self.assertRaises(ValueError):
            gap_instance(1, ((2,),), 0, ())


if __name__ == "__main__":
    unittest.main()
