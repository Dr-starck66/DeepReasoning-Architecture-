import unittest

from benchmark_optimized_swaps import (
    apply_original_optimized, benchmark, deterministic_inputs,
    verify_exactness,
)
from parametric_spectrum import sparse_times_vector
from projected_spectrum import apply_scaled_dp


class OptimizedSwapBenchTests(unittest.TestCase):
    def test_bitmask_baseline_matches_old_reference_q1_q6(self):
        results = verify_exactness()
        self.assertEqual(set(results), set(str(q) for q in range(1, 7)))
        for q, result in results.items():
            self.assertEqual(result["status"], "PASS", (q, result))
            self.assertEqual(result["mismatches_original_vs_optimized"], 0)

    def test_q3_exact_same_operator_up_to_8(self):
        q = 3
        for v in deterministic_inputs(q):
            self.assertEqual(apply_scaled_dp(v, q),
                             tuple(8 * z for z in apply_original_optimized(v, q)))

    def test_q4_operators_must_not_be_called_equivalent(self):
        q = 4
        v = deterministic_inputs(q)[0]
        self.assertNotEqual(apply_scaled_dp(v, q),
                            tuple(16 * z for z in apply_original_optimized(v, q)))

    def test_bad_dimension_rejected(self):
        for bad_q, bad_v in [(0, (0,)), (3, (1, 2))]:
            with self.subTest(q=bad_q, v=bad_v):
                with self.assertRaises(ValueError):
                    apply_original_optimized(bad_v, bad_q)

    def test_reproducible_benchmark_metadata_guards(self):
        out = benchmark(q_values=(3, 4), repeats=5)
        self.assertEqual(out["status"], "PASS")
        self.assertTrue(out["benchmark"]["3"]["same_mathematical_operator"])
        self.assertFalse(out["benchmark"]["4"]["same_mathematical_operator"])
        self.assertEqual(out["benchmark"]["3"]["projector_output_scale_vs_original"], 8)
        self.assertIsNone(out["benchmark"]["4"]["projector_output_scale_vs_original"])
        for q in ("3", "4"):
            for method in ("old_Aq", "projector_Eq"):
                self.assertGreater(out["benchmark"][q][method]["median_ns"], 0)
                self.assertEqual(out["benchmark"][q][method]["repeats"], 5)
        self.assertEqual(out["real_world_speedup"], "UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
