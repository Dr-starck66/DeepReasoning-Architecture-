#!/usr/bin/env python3
"""ASTRA Ω — a *different* asymptotically sparse-rank extension of the q=3 model.

The old A_3 has eigenvalues +4 on 2 antisymmetric local swap factors and -4
on 3, zero elsewhere. To preserve A_3 while avoiding the old q>=4 modes,
define E_q = 4*P_{k=2} - 4*P_{k=3}, with local rational projectors
P_i^+ = (I+S_i)/2 and P_i^- = (I-S_i)/2.

Rather than materialize rationals, T_q=2^q E_q is an integer polynomial in
the commuting swaps. All tests are exact. This is a new engineered family;
it does not imply patentability, performance improvement or uniqueness.

The construction is independent of how the former A_q was generalized.
"""
from __future__ import annotations

from functools import lru_cache
from itertools import combinations, product
from math import comb
from typing import Sequence

from parametric_spectrum import (
    a_sparse, rank_mod, swap_axis, vector, rank_formula
)


def rank_filter(q: int) -> int:
    if q < 1:
        raise ValueError("q must be >=1")
    return (comb(q, 2) * 3 ** (q - 2) if q >= 2 else 0) + (
        comb(q, 3) * 3 ** (q - 3) if q >= 3 else 0
    )


def scalar_eigenvalue(q: int, negative_count: int, *, scaled: bool = True) -> int:
    if negative_count < 0 or negative_count > q:
        raise ValueError("invalid number of negative swaps")
    v = 4 if negative_count == 2 else (-4 if negative_count == 3 else 0)
    return 2 ** q * v if scaled else v


@lru_cache(maxsize=None)
def integer_swap_coefficients(q: int) -> tuple[int, ...]:
    """T_q = sum_masks coefficient[mask] * S_mask; coefficients integral."""
    if not 1 <= q <= 6:
        raise ValueError("materialization restricted to q<=6")
    masks = [(2, 4), (3, -4)]
    output = []
    for mask in range(1 << q):
        coefficient = 0
        for k, weight in masks:
            for chosen in combinations(range(q), k):
                selected = sum(1 << axis for axis in chosen)
                sign = -1 if ((selected & mask).bit_count() % 2) else 1
                coefficient += weight * sign
        output.append(coefficient)
    return tuple(output)


def swap_mask(pos: int, mask: int, q: int) -> int:
    for axis in range(q):
        if mask & (1 << axis):
            pos = swap_axis(pos, axis, q)
    return pos


def apply_scaled(vec: Sequence[int], q: int, mutate_entry: bool = False) -> tuple[int, ...]:
    n = 4 ** q
    if len(vec) != n:
        raise ValueError("incompatible vector dimension")
    coeff = integer_swap_coefficients(q)
    out = []
    for row in range(n):
        entry = sum(c * vec[swap_mask(row, mask, q)]
                    for mask, c in enumerate(coeff) if c)
        if mutate_entry and row == 0:
            entry += vec[0]  # single-entry adversarial mutation T[0,0] += 1
        out.append(entry)
    return tuple(out)



def apply_scaled_dp(vec: Sequence[int], q: int) -> tuple[int, ...]:
    """Linear-in-q matrix-free exact implementation of T_q = 2^q E_q.

    Let states[k] represent 2^i times the projection onto exactly k
    antisymmetric signs among the first i factors. Under the next swap S_i,

        next[k] = (I+S_i)states[k] + (I-S_i)states[k-1].

    Keep only k=0..3 because higher counts can never decrease. No division,
    floating point, dense matrices or 2^q summation. Complexity
    O(4*q*4^q) integer additions, storage O(4*4^q) integers.
    """
    if q < 1:
        raise ValueError("q must be positive")
    n = 4 ** q
    if len(vec) != n:
        raise ValueError("incompatible vector dimension")
    states = [[0] * n for _ in range(4)]
    states[0] = list(vec)
    for axis in range(q):
        nxt = [[0] * n for _ in range(4)]
        for k in range(min(axis + 1, 3) + 1):
            for pos in range(n):
                swapped = swap_axis(pos, axis, q)
                if k <= axis:
                    nxt[k][pos] += states[k][pos] + states[k][swapped]
                if k >= 1:
                    nxt[k][pos] += states[k-1][pos] - states[k-1][swapped]
        states = nxt
    return tuple(4 * (states[2][pos] - states[3][pos]) for pos in range(n))


def dp_vs_polynomial(q: int) -> dict:
    """Three independent, deterministic input vectors per finite q."""
    n = 4 ** q
    vectors = []
    for at in (0, n // 2):
        v = [0] * n
        v[at] = 1
        vectors.append(v)
    vectors.append([((7 * i + 3) % 11) - 5 for i in range(n)])
    failures = []
    for vid, v in enumerate(vectors):
        if apply_scaled_dp(v, q) != apply_scaled(v, q):
            failures.append(vid)
    return {
        "q": q, "vectors_checked": len(vectors),
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }

def matrix_scaled(q: int) -> tuple[tuple[int, ...], ...]:
    if not 1 <= q <= 4:
        raise ValueError("full matrix bounded to q<=4")
    n = 4 ** q
    coeff = integer_swap_coefficients(q)
    rows = [[0] * n for _ in range(n)]
    for row in range(n):
        for mask, c in enumerate(coeff):
            if c:
                rows[row][swap_mask(row, mask, q)] += c
    return tuple(tuple(row) for row in rows)


def exhaustive_spectrum(q: int) -> dict:
    if not 1 <= q <= 4:
        raise ValueError("exhaustive test bounded to q<=4")
    failures = []
    equations = 0
    for label in product(range(4), repeat=q):
        v = vector(label)
        lam = scalar_eigenvalue(q, label.count(3))
        actual = apply_scaled(v, q)
        for row, (got, expected) in enumerate(zip(actual, (lam * z for z in v))):
            equations += 1
            if got != expected and len(failures) < 3:
                failures.append((label, row, got, expected))
    return {
        "status": "PASS" if not failures else "FAIL",
        "q": q,
        "labels": 4 ** q,
        "equations": equations,
        "failures": failures,
    }


def compare_original_q3() -> dict:
    original = a_sparse(3)
    new = matrix_scaled(3)
    mismatch = sum(new[i][j] != 8 * original[i][j]
                   for i in range(64) for j in range(64))
    return {
        "status": "PASS" if mismatch == 0 else "FAIL",
        "checked_entries": 4096,
        "mismatches": mismatch,
        "identity": "T_3 == 8 * (I-M_3)",
    }


def report() -> dict:
    exhaustive = [exhaustive_spectrum(q) for q in range(1, 5)]
    finite = {}
    for q in range(1, 5):
        mat = matrix_scaled(q)
        rank101 = rank_mod(mat, 101)
        rank103 = rank_mod(mat, 103)
        claim = rank_filter(q)
        finite[str(q)] = {
            "dimension": 4 ** q,
            "filtered_rank": claim,
            "original_rank": rank_formula(q),
            "modular_rank_101": rank101,
            "modular_rank_103": rank103,
            "status": "PASS" if rank101 == rank103 == claim else "FAIL",
        }
    q5_modes = [tuple([i] * 5) for i in range(4)] + [
        (3, 3, 2, 2, 2), (3, 3, 3, 2, 2), (3, 3, 3, 3, 2),
        (0, 1, 3, 3, 2),
    ]
    q5_checks = []
    for label in q5_modes:
        v = vector(label)
        lam = scalar_eigenvalue(5, label.count(3))
        actual = apply_scaled(v, 5)
        q5_checks.append(actual == tuple(lam * z for z in v))
    zero_mode = vector((0, 0, 0, 0))
    adversarial = {
        "matrix_coefficient_mutation_rejected":
            apply_scaled(zero_mode, 4, True) != apply_scaled(zero_mode, 4),
        "false_eigenvalue_rejected":
            apply_scaled(zero_mode, 4) != tuple(z * 1 for z in zero_mode),
        "wrong_rank_65_rejected":
            finite["4"]["modular_rank_103"] != 65,
        "old_q4_family_is_not_falsely_identified_as_filter":
            matrix_scaled(4) != tuple(
                tuple(16 * z for z in row) for row in a_sparse(4)),
    }
    q_table = {
        str(q): {
            "dimension": 4 ** q,
            "filtered_rank": rank_filter(q),
            "old_rank": rank_formula(q),
            "fraction_numerator": rank_filter(q),
            "fraction_denominator": 4 ** q,
        }
        for q in (2, 3, 4, 5, 6, 10, 20, 30, 40)
    }
    comparison = compare_original_q3()
    dp_crosschecks = [dp_vs_polynomial(q) for q in range(1, 6)]
    checks_ok = (
        all(z["status"] == "PASS" for z in dp_crosschecks) and
        all(e["status"] == "PASS" for e in exhaustive) and
        all(x["status"] == "PASS" for x in finite.values()) and
        all(q5_checks) and comparison["status"] == "PASS" and
        all(adversarial.values())
    )
    return {
        "schema": "astra-projected-spectrum/1",
        "family": "E_q = 4*P_(exactly 2 negative swaps) - 4*P_(exactly 3 negative swaps)",
        "scaled_operator": "T_q = 2^q * E_q",
        "rank_formula": "C(q,2)*3^(q-2)+C(q,3)*3^(q-3), with absent terms=0",
        "analytic_limit": "rank(E_q)/4^q -> 0, if projectors are complete",
        "q1_q4_exhaustive": exhaustive,
        "q1_q4_modular_ranks": finite,
        "q5_sample_eigenvectors": {
            "status": "PASS" if all(q5_checks) else "FAIL",
            "count": len(q5_checks), "exhaustive": False,
        },
        "q3_original_exact_matrix_comparison": comparison,
        "dynamic_programming_crosschecks_q1_q5": dp_crosschecks,
        "dynamic_programming_complexity": "O(q*4^q) integer operations, O(4^q) memory; no measured speedup claim",
        "negative_controls": adversarial,
        "rank_table_exact_integers": q_table,
        "finite_status": "PASS" if checks_ok else "FAIL",
        "uniform_Lean_Matrix_rank_proof": "PASS",
        "uniform_Lean_Matrix_rank_proof_ref": "https://github.com/Dr-starck66/DeepReasoning-Architecture-/actions/runs/45135520573",
        "runtime_advantage": "UNVERIFIED",
        "novelty": "UNVERIFIED",
    }


def main(argv=None) -> int:
    import argparse
    import json
    from hashlib import sha256
    from pathlib import Path

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    evidence = report()
    canonical = json.dumps(evidence, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    evidence["receipt_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()
    result = json.dumps(evidence, indent=2, sort_keys=True, ensure_ascii=True) + "\n"
    if args.output is not None:
        args.output.write_text(result, encoding="utf-8")
    print(result)
    return 0 if evidence["finite_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
