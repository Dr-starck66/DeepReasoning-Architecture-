#!/usr/bin/env python3
"""ASTRA Ω: exact parametric commuting-swap spectral research (stdlib only).

Family A_q = I - [sum_j product_{i!=j} S_i - (q-1) product_i S_i].
S_i swaps the a_i,d_i bits in a 2q-bit basis. All arithmetic is integer
or modular; there is no floating point, no claim of generic algorithmic
speedup, and no claim that the parameter-uniform rank is formally proved
in Lean. Reuses existing ASTRA q=3 model as an independent integration test.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import product
from math import comb
from pathlib import Path
import json
import sys

LOCAL = ((1, 0, 0, 0), (0, 0, 0, 1),
         (0, 1, 1, 0), (0, 1, -1, 0))


def swap_axis(pos: int, axis: int, q: int) -> int:
    mask1 = 1 << axis
    mask2 = 1 << (axis + q)
    if bool(pos & mask1) == bool(pos & mask2):
        return pos
    return pos ^ (mask1 | mask2)


def swap_except(pos: int, omitted: int, q: int) -> int:
    for axis in range(q):
        if axis != omitted:
            pos = swap_axis(pos, axis, q)
    return pos


def swap_all(pos: int, q: int) -> int:
    for axis in range(q):
        pos = swap_axis(pos, axis, q)
    return pos


def a_sparse(q: int) -> tuple[tuple[int, ...], ...]:
    """Independent exact matrix construction for bounded test q only."""
    if not 1 <= q <= 5:
        raise ValueError("Only small q are materialized in tests")
    n = 4 ** q
    rows = [[0] * n for _ in range(n)]
    for i in range(n):
        rows[i][i] += 1
        for omitted in range(q):
            rows[i][swap_except(i, omitted, q)] -= 1
        rows[i][swap_all(i, q)] += q - 1
    return tuple(tuple(row) for row in rows)


def vector(types: tuple[int, ...]) -> tuple[int, ...]:
    q = len(types)
    n = 4 ** q
    vec = []
    for pos in range(n):
        coeff = 1
        for axis, kind in enumerate(types):
            coord = ((pos >> axis) & 1) + 2 * ((pos >> (axis + q)) & 1)
            coeff *= LOCAL[kind][coord]
        vec.append(coeff)
    return tuple(vec)


def eigenvalue(k: int) -> int:
    """Eigenvalue of A_q for a tensor label with k antisymmetric pairs."""
    return 2 * k if k % 2 == 0 else 2 - 2 * k


def rank_formula(q: int) -> int:
    if q < 1:
        raise ValueError("q must be positive")
    return 4 ** q - 3 ** q - q * 3 ** (q - 1)


def rank_by_multiplicities(q: int) -> int:
    return sum(comb(q, k) * 3 ** (q - k) for k in range(2, q + 1))


def sparse_times_vector(vec: tuple[int, ...], q: int,
                        mutate_coefficient: bool = False) -> tuple[int, ...]:
    """Apply A_q without constructing A_q or performing dense matrix multiply."""
    out = []
    for i in range(4 ** q):
        val = vec[i] - sum(vec[swap_except(i, omitted, q)] for omitted in range(q))
        val += (q - 1) * vec[swap_all(i, q)]
        if mutate_coefficient and i == 0:
            val += vec[0]  # falsification: mutate A_q[0,0] by +1
        out.append(val)
    return tuple(out)


def check_spectral(q: int, *, exhaustive: bool) -> dict:
    if exhaustive:
        modes = list(product(range(4), repeat=q))
    else:
        # Deterministic, diverse controls; not an exhaustive search for q>=5.
        modes = [tuple([v] * q) for v in range(4)]
        modes.extend(tuple(3 if axis in selected else 2 for axis in range(q))
                     for selected in ((0,), (q - 1,), (0, q - 1), tuple(range(q // 2))))
        modes = sorted(set(modes))
    equations = 0
    failures = []
    for kind_tuple in modes:
        v = vector(kind_tuple)
        lam = eigenvalue(kind_tuple.count(3))
        actual = sparse_times_vector(v, q)
        for i, (observed, expected) in enumerate(zip(actual, (lam * z for z in v))):
            equations += 1
            if observed != expected and len(failures) < 4:
                failures.append({"types": kind_tuple, "row": i,
                                 "actual": observed, "expected": expected})
    return {"status": "PASS" if not failures else "FAIL", "exhaustive": exhaustive,
            "checked_modes": len(modes), "checked_equations": equations,
            "failures": failures}


def rank_mod(matrix: tuple[tuple[int, ...], ...], prime: int) -> int:
    """Independent finite-field elimination gives lower bound on rational rank."""
    if not matrix:
        return 0
    rows = [[z % prime for z in row] for row in matrix]
    n = len(rows)
    pivot_row = 0
    for col in range(n):
        pivot = next((i for i in range(pivot_row, n) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivot], rows[pivot_row] = rows[pivot_row], rows[pivot]
        inv = pow(rows[pivot_row][col], -1, prime)
        pivot_values = rows[pivot_row]
        for i in range(pivot_row + 1, n):
            factor = rows[i][col] * inv % prime
            if factor:
                row = rows[i]
                for j in range(col, n):
                    row[j] = (row[j] - factor * pivot_values[j]) % prime
        pivot_row += 1
        if pivot_row == n:
            break
    return pivot_row


def compare_existing_q3(matrix: tuple[tuple[int, ...], ...]) -> dict:
    try:
        from math_research_engine import construct_matrix
    except ImportError:
        return {"status": "UNVERIFIED", "reason": "existing ASTRA module not loaded"}
    source = construct_matrix()
    differences = sum(matrix[i][j] != (int(i == j) - source[i][j])
                      for i in range(64) for j in range(64))
    return {"status": "PASS" if differences == 0 else "FAIL",
            "entries_compared": 4096, "differences": differences}


def assess() -> dict:
    ranks = {}
    all_ok = True
    comparison = None
    for q in range(1, 5):
        matrix = a_sparse(q)
        test = check_spectral(q, exhaustive=True)
        f101 = rank_mod(matrix, 101)
        f103 = rank_mod(matrix, 103)
        predicted = rank_formula(q)
        counted = rank_by_multiplicities(q)
        ok = (test["status"] == "PASS" and f101 == f103 == predicted == counted)
        if q == 3:
            comparison = compare_existing_q3(matrix)
            ok = ok and comparison["status"] == "PASS"
        all_ok = all_ok and ok
        ranks[str(q)] = {"status": "PASS" if ok else "FAIL",
                         "dimension": 4 ** q,
                         "predicted_rank": predicted,
                         "counted_nonzero_modes": counted,
                         "rank_F101": f101, "rank_F103": f103,
                         "spectral": test}
    sampled = check_spectral(5, exhaustive=False)
    arithmetic_checks = {
        str(q): {"dimension": 4 ** q, "rank_formula": rank_formula(q),
                 "independent_binomial_sum": rank_by_multiplicities(q)}
        for q in range(1, 13)
    }
    arithmetic_ok = all(v["rank_formula"] == v["independent_binomial_sum"]
                        for v in arithmetic_checks.values())
    # Adversarial falsification of a matrix entry, eigenvalue and rank.
    q = 4
    zero_mode = vector((0,) * q)
    mutates = sparse_times_vector(zero_mode, q, True) != (
        tuple(eigenvalue(0) * z for z in zero_mode))
    wrong_eigenvalue_rejected = sparse_times_vector(zero_mode, q) != tuple(
        (eigenvalue(0) + 1) * z for z in zero_mode)
    wrong_rank_rejected = (ranks["4"]["rank_F101"] != rank_formula(4) - 1)
    controls = {"single_coefficient_mutation_rejected": mutates,
                "fabricated_eigenvalue_rejected": wrong_eigenvalue_rejected,
                "fabricated_rank_rejected": wrong_rank_rejected}
    all_ok = (all_ok and sampled["status"] == "PASS" and arithmetic_ok and
              comparison is not None and comparison["status"] == "PASS"
              and all(controls.values()))
    report = {
        "schema": "astra-parametric-spectrum/1",
        "conjecture": "For positive integer q, rank_Q(A_q)=4^q - 3^q - q*3^(q-1)",
        "A_q": "I - sum_omitted product_{i!=omitted}S_i + (q-1)*product_i S_i",
        "eigenvalues": "2*k (k even), or 2-2*k (k odd); zero iff k=0 or 1",
        "multiplicity": "choose(q,k)*3^(q-k)",
        "finite_exhaustive_q_1_to_4": ranks,
        "q5_deterministic_sample": sampled,
        "symbolic_formula_arithmetic_q_1_to_12": arithmetic_checks,
        "existing_ASTRA_q3_crosscheck": comparison,
        "negative_controls": controls,
        "finite_computational_status": "PASS" if all_ok else "FAIL",
        "uniform_Lean_matrix_rank_proof": "UNVERIFIED",
        "scientific_novelty": "UNVERIFIED",
        "limitation": "Finite spectral samples and modular ranks do NOT prove a uniform theorem; structural tensor argument must be formalized separately."
    }
    raw = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    report["receipt_sha256"] = sha256(raw.encode()).hexdigest()
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path)
    args = p.parse_args(argv)
    report = assess()
    encoded = json.dumps(report, indent=2, sort_keys=True) + "\n"
    if args.output is not None:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 0 if report["finite_computational_status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
