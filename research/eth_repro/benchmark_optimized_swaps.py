#!/usr/bin/env python3
"""ASTRA Ω reproducible, zero-dependency performance comparison.

Reference baseline = *optimized* original A_q (not the slow
swap_except + swap_all implementation). Filtered application =
2^q E_q computed by the 4-state dynamic program.

CRITICAL COMPARABILITY:
q=3: 2^3 E_3 == 8 A_3, so timed programs compute the SAME output
apart from the displayed, exact integer factor.
q!=3: they apply DIFFERENT operators; times are only throughput/cost
comparisons, and may NEVER be called a same-task speedup.

No blanket performance guarantee. One GitHub runner is one environment;
measure warmups, paired medians, integer output agreement, peak traced
allocations separately from timed wall clock, and show adverse results.
"""
from __future__ import annotations

import argparse
from gc import disable, enable, isenabled
from hashlib import sha256
import json
from pathlib import Path
import platform
from statistics import median
from time import perf_counter_ns
import tracemalloc

from parametric_spectrum import sparse_times_vector, swap_axis
from projected_spectrum import apply_scaled_dp, apply_scaled


def apply_original_optimized(vec: tuple[int, ...], q: int) -> tuple[int, ...]:
    """Apply original A_q in O(q*4^q), no swap_except O(q) inner loop.

    Let d=(lowbits xor highbits). All-swap index is i xor (d+d<<q).
    To skip axis j, undo the changed pair of bits for that axis only.
    This implements A_q = I - sum_j S_except_j + (q-1) S_all.
    """
    if q < 1 or len(vec) != 4 ** q:
        raise ValueError("incompatible q or dimension")
    low_mask = (1 << q) - 1
    pair_flips = tuple((1 << axis) | (1 << (axis + q)) for axis in range(q))
    out = [0] * len(vec)
    for row in range(len(vec)):
        differences = (row ^ (row >> q)) & low_mask
        all_swapped = row ^ differences ^ (differences << q)
        val = vec[row] + (q - 1) * vec[all_swapped]
        for axis, flip in enumerate(pair_flips):
            val -= vec[all_swapped ^ flip if differences & (1 << axis)
                       else all_swapped]
        out[row] = val
    return tuple(out)


def deterministic_inputs(q: int) -> tuple[tuple[int, ...], ...]:
    n = 4 ** q
    rng_vector = tuple(((i * 173 + 19 + ((i >> 2) * 17)) % 101) - 50
                       for i in range(n))
    sparse_vector = tuple(1 if i == n // 3 else 0 for i in range(n))
    alternating_vector = tuple((-1 if (i.bit_count() % 2) else 1) * (i % 9)
                               for i in range(n))
    return rng_vector, sparse_vector, alternating_vector


def verify_exactness(q_values: tuple[int, ...] = tuple(range(1, 7))) -> dict:
    evidence = {}
    for q in q_values:
        mismatches = 0
        same_task_mismatches = 0
        inputs = deterministic_inputs(q)
        for v in inputs:
            a_ref = sparse_times_vector(v, q)
            a_fast = apply_original_optimized(v, q)
            mismatches += sum(x != y for x, y in zip(a_ref, a_fast))
            if q == 3:
                e_fast = apply_scaled_dp(v, q)
                same_task_mismatches += sum(x != 8*y for x, y in zip(e_fast, a_fast))
        evidence[str(q)] = {
            "dimension": 4**q,
            "input_vectors": len(inputs),
            "entries_compared_original": 3*(4**q),
            "mismatches_original_vs_optimized": mismatches,
            "mismatches_filtered_q3_same_task": same_task_mismatches if q == 3 else None,
            "status": "PASS" if mismatches == 0 and (q != 3 or same_task_mismatches == 0)
                      else "FAIL",
        }
    return evidence


def time_method(fn, vec: tuple[int, ...], q: int, repeats: int) -> dict:
    for _ in range(2):
        fn(vec, q)
    durations = []
    gc_was_enabled = isenabled()
    if gc_was_enabled:
        disable()
    try:
        for _ in range(repeats):
            start = perf_counter_ns()
            fn(vec, q)
            durations.append(perf_counter_ns() - start)
    finally:
        if gc_was_enabled:
            enable()
    return {
        "warmups": 2,
        "repeats": repeats,
        "median_ns": int(median(durations)),
        "min_ns": min(durations),
        "max_ns": max(durations),
    }


def memory_peak_bytes(fn, vec: tuple[int, ...], q: int) -> int:
    # Memory tracing is performed SEPARATELY from speed timings.
    tracemalloc.start()
    try:
        fn(vec, q)
        return tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def benchmark(q_values=(3, 4, 5, 6), repeats: int = 9) -> dict:
    if repeats < 5:
        raise ValueError("at least 5 repetitions required")
    proofs = verify_exactness()
    if not all(p["status"] == "PASS" for p in proofs.values()):
        raise AssertionError("FAIL: optimized baseline does not match reference")
    timings = {}
    for q in q_values:
        if not (1 <= q <= 7):
            raise ValueError("q must be between 1 and 7")
        vec = deterministic_inputs(q)[0]
        # Counterbalance warmup/caching effects: alternate order by parity.
        methods = [
            ("original_optimized_Aq", apply_original_optimized),
            ("projector_four_state_scaled_Eq", apply_scaled_dp),
        ]
        if q % 2:
            methods.reverse()
        runs = {name: time_method(fn, vec, q, repeats) for name, fn in methods}
        memory = {name: memory_peak_bytes(fn, vec, q) for name, fn in methods}
        a = runs["original_optimized_Aq"]["median_ns"]
        e = runs["projector_four_state_scaled_Eq"]["median_ns"]
        timings[str(q)] = {
            "dimension": 4**q,
            "same_mathematical_operator": q == 3,
            "projector_output_scale_vs_original": 8 if q == 3 else None,
            "old_Aq": runs["original_optimized_Aq"],
            "projector_Eq": runs["projector_four_state_scaled_Eq"],
            "peak_tracemalloc_bytes": memory,
            "original_vs_projector_median_ratio": round(a / e, 4),
            "comparison_interpretation": (
                "same output after exact scaling; compare cost on one runner"
                if q == 3 else
                "DIFFERENT matrices; comparison is NOT a same-task speedup"
            ),
        }
    return {
        "schema": "astra-swap-performance/1",
        "status": "PASS",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor() or "UNVERIFIED",
        "q3_exact_equivalence": "8*A3 == 2^3*E3, all tested vector inputs",
        "reference_original_baseline": "optimized bitmask O(q*4^q) integer",
        "projector": "4-state DP O(q*4^q) integer",
        "existing_reference_crosschecks": proofs,
        "benchmark": timings,
        "memory_definition": "tracemalloc peak Python allocations separately",
        "limit": "One runner, short workloads; NOT proof of production performance, "
                 "same-task comparison ONLY q=3; runtime variability expected.",
        "real_world_speedup": "UNVERIFIED",
    }


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    p.add_argument("--repeats", type=int, default=9)
    p.add_argument("--q", type=int, nargs="+", default=[3, 4, 5, 6])
    args = p.parse_args(argv)
    result = benchmark(tuple(args.q), repeats=args.repeats)
    raw = json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    result["receipt_sha256"] = sha256(raw.encode("utf-8")).hexdigest()
    data = json.dumps(result, sort_keys=True, indent=2, ensure_ascii=True) + "\n"
    if args.output:
        args.output.write_text(data, encoding="utf-8")
    print(data)
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
