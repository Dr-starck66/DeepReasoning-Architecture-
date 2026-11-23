#!/usr/bin/env python3
"""ASTRA Ω / Clay P-vs-NP: SAT-to-projector obstruction gate.

Finite, reproducible NEGATIVE-control experiment. It does not prove
anything about P vs NP. The input is a truth table of a width-at-most-3
CNF on n=2q variables, indexed by two q-bit strings as in E_q.

If a SAT decision method uses *only* the projected truth vector E_q v,
it cannot be correct for every CNF: an explicit satisfiable unit-clause
formula and an unsatisfiable contradiction have identical ZERO images.

The projection also annihilates tautological truth tables. The failure
is structural and extends to every q >= 2 because any function of a
single input variable is symmetric under each OTHER local bit swap;
a 2-/3-negative-sign projector has at least two antisymmetric factors.

A positive control with two independent unit constraints produces a
nonzero image; hence this test does not trivially force every output 0.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from itertools import product
import json
from math import comb, log2
from pathlib import Path

from eth_lab import count_exhaustive, satisfied
from projected_spectrum import apply_scaled_dp, rank_filter

CNF = tuple[tuple[int, ...], ...]

# 3-CNF convention here allows clauses of length <=3, including unit
# clauses and the empty conjunction (true). All are legitimate CNF inputs.
SAT = ((1,),)
UNSAT = ((1,), (-1,))
TAUTOLOGY = ()
TWO_LOCAL_FACTORS = ((1,), (2,))


def strict_three_literal_witness(q: int) -> tuple[CNF, CNF]:
    """Both formulas use EXACTLY 3 distinct variables per clause.

    SAT = (x1 OR x(q+1) OR x2) AND
          (x1 OR x(q+1) OR x(q+2)).
    It is invariant under EVERY local swap: the first local pair
    appears symmetrically, swapping the second pair exchanges clauses,
    and further pairs do not occur. Thus all negative-mode projectors
    annihilate its truth table for any q>=2.

    UNSAT = every one of the 8 possible 3-literal sign clauses
    over distinct variables x1,x2,x3. Each assignment to those three
    variables falsifies one clause.
    """
    if q < 2:
        raise ValueError("strict three-literal construction needs q>=2")
    sat = ((1, q + 1, 2), (1, q + 1, q + 2))
    unsat = tuple(tuple(var if pos else -var
                        for var, pos in zip((1, 2, 3), signs))
                  for signs in product((False, True), repeat=3))
    return sat, unsat


def truth_vector(q: int, cnf: CNF) -> tuple[int, ...]:
    if not 1 <= q <= 4:
        raise ValueError("exhaustive test restricted to q=1..4")
    n = 2 * q
    if any(len(clause) > 3 for clause in cnf):
        raise ValueError("expected width-at-most-3 CNF")
    return tuple(int(satisfied(mask, cnf)) for mask in range(1 << n))


def make_case(q: int) -> dict:
    n = 2*q
    strict_sat, strict_unsat = strict_three_literal_witness(q)
    formulas = {
        "SAT_unit": SAT,
        "UNSAT_contradiction": UNSAT,
        "SAT_tautology": TAUTOLOGY,
        "SAT_two_factors": TWO_LOCAL_FACTORS,
        "STRICT_SAT": strict_sat,
        "STRICT_UNSAT": strict_unsat,
    }
    vectors = {k: truth_vector(q, v) for k, v in formulas.items()}
    oracles = {k: count_exhaustive(n, f) for k, f in formulas.items()}
    projections = {k: apply_scaled_dp(v, q) for k, v in vectors.items()}
    hasher = lambda vec: sha256(json.dumps(vec, separators=(",", ":")).encode()).hexdigest()
    checks = {
        "SAT_unit_positive": oracles["SAT_unit"] > 0,
        "UNSAT_contradiction_zero": oracles["UNSAT_contradiction"] == 0,
        "TAUTOLOGY_positive": oracles["SAT_tautology"] == (1 << n),
        "SAT_and_UNSAT_same_projection":
            projections["SAT_unit"] == projections["UNSAT_contradiction"],
        "SAT_and_UNSAT_projection_zero": not any(projections["SAT_unit"]),
        "TAUTOLOGY_and_UNSAT_same_projection":
            projections["SAT_tautology"] == projections["UNSAT_contradiction"],
        "two_factor_positive_control_nonzero": any(projections["SAT_two_factors"]),
        "different_unprojected_truth_tables":
            vectors["SAT_unit"] != vectors["UNSAT_contradiction"],
        "correct_dimension": len(vectors["SAT_unit"]) == 4**q,
        "STRICT_three_distinct_literals_each_clause": all(
            len(clause) == 3 and len({abs(lit) for lit in clause}) == 3
            for cnf in (strict_sat, strict_unsat) for clause in cnf),
        "STRICT_SAT_positive": oracles["STRICT_SAT"] > 0,
        "STRICT_UNSAT_zero": oracles["STRICT_UNSAT"] == 0,
        "STRICT_SAT_UNSAT_same_projection":
            projections["STRICT_SAT"] == projections["STRICT_UNSAT"],
        "STRICT_SAT_projection_zero": not any(projections["STRICT_SAT"]),
    }
    # Strictly q>=2 only: E1 is itself zero and gives an even stronger
    # degenerate collision, but would fail the positive control.
    return {
        "q": q, "declared_variables": n, "vector_dimension": 4**q,
        "rank_Eq": rank_filter(q),
        "truth_table_counts": oracles,
        "projection_nonzero_entries":
            {k: sum(z != 0 for z in v) for k, v in projections.items()},
        "output_sha256": {k: hasher(v) for k, v in projections.items()},
        "checks": checks,
        "status": "PASS" if all(checks.values()) else "FAIL",
    }


def report(qs=(2, 3, 4)) -> dict:
    cases = [make_case(q) for q in qs]
    return {
        "schema": "astra-clay-sat-bridge-gate/1",
        "problem": "Clay P versus NP",
        "scope": "finite truth-table projection witness, no general SAT algorithm",
        "input_encoding": "length 2^(2q)=4^q raw CNF satisfaction table",
        "tested_q": list(qs),
        "cases": cases,
        "general_structural_obstruction":
            "For every q>=2, a CNF depending on only variable x1 is "
            "invariant under at least q-1 other local swaps; any projector "
            "with >=2 antisymmetric swap factors annihilates its truth table. "
            "An unsatisfiable CNF also maps to zero.",
        "complexity_check": {
            "n_equals_2q": True,
            "truth_table_entries_exact": "2^n = 4^q",
            "projector_apply_upper_bound": "O(q*4^q)=O(n*2^n), NOT polynomial in n",
            "rank_exact": "C(q,2)*3^(q-2)+C(q,3)*3^(q-3)",
            "rank_exponential_lower_bound_q_ge_2":
                "rank >= C(q,2)*3^(q-2) >= 3^(q-2)",
            "asymptotic_rank_exponent_in_n": log2(3)/2,
            "SAT_general_poly_time_algorithm": "UNVERIFIED",
            "P_vs_NP_resolution": "NOT ESTABLISHED",
        },
        "status": "PASS" if all(x["status"] == "PASS" for x in cases) else "FAIL",
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    r = report()
    material = json.dumps(r, sort_keys=True, ensure_ascii=True,
                          separators=(",", ":"))
    r["receipt_sha256"] = sha256(material.encode()).hexdigest()
    payload = json.dumps(r, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    print(payload)
    return 0 if r["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
