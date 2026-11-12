#!/usr/bin/env python3
"""ASTRA MATH LAB Ω — finite #3-SAT identity checks (stdlib only).

This is NOT an implementation or verification of the 2026 ETH-disproof proof.
It reproduces, on finite inputs, two elementary mechanisms appearing in
OpenAI's 2026 manuscript: the Boolean satisfaction polynomial identity
(section 'A direct polynomial for the count') and interpolation H(0)=#F.
A cutset-based decomposition is an elementary analogue of conditioning on
shared measurements; it is NOT the paper's low-degree replacement construction.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from datetime import datetime, timezone
from pathlib import Path

SOURCE = "https://github.com/openai/math/tree/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026"


def validate(n: int, cnf: tuple[tuple[int, ...], ...]) -> None:
    if n < 0:
        raise ValueError("n must be nonnegative")
    if any(lit == 0 or abs(lit) > n for clause in cnf for lit in clause):
        raise ValueError("literals must be integers in {-n..-1, 1..n}")


def satisfied(mask: int, cnf: tuple[tuple[int, ...], ...]) -> bool:
    return all(any(bool(mask & (1 << (abs(lit)-1))) == (lit > 0)
                   for lit in clause) for clause in cnf)


def count_exhaustive(n: int, cnf: tuple[tuple[int, ...], ...]) -> int:
    validate(n, cnf)
    return sum(satisfied(mask, cnf) for mask in range(1 << n))


def count_dpll(n: int, cnf: tuple[tuple[int, ...], ...]) -> int:
    """Independent exact #SAT solver using Shannon branching and caching."""
    validate(n, cnf)
    cache: dict[tuple[int, tuple[tuple[int, ...], ...]], int] = {}

    def rec(remaining: int, clauses: tuple[tuple[int, ...], ...]) -> int:
        if not clauses:
            return 1 << remaining.bit_count()
        if any(not clause for clause in clauses):
            return 0
        key = remaining, clauses
        if key in cache:
            return cache[key]
        occ: dict[int, int] = {}
        for clause in clauses:
            for lit in clause:
                var = abs(lit)
                occ[var] = occ.get(var, 0) + 1
        var = max(occ, key=lambda x: (occ[x], -x))
        value = 0
        for assignment in (False, True):
            simplified = []
            for clause in clauses:
                if any((lit > 0) == assignment for lit in clause if abs(lit) == var):
                    continue
                simplified.append(tuple(lit for lit in clause if abs(lit) != var))
            value += rec(remaining & ~(1 << (var - 1)), tuple(simplified))
        cache[key] = value
        return value

    return rec((1 << n) - 1, cnf)


def deformed_polynomial_sum(n: int, cnf: tuple[tuple[int, ...], ...], t: int) -> int:
    """H(t) = sum_x product_clauses [1-prod_lits(1-L_lit(X(t)))].

    X_i(t) = x_i + t * (1 + x_{i+1 mod n}) is a degree-one replacement.
    Thus H(t) has integer coefficients, degree <= total literal incidences,
    and H(0)=#F. Evaluation is exponential: this is a *toy identity*.
    """
    validate(n, cnf)
    total = 0
    for mask in range(1 << n):
        xs = [bool(mask & (1 << i)) for i in range(n)]
        shifted = [int(xs[i]) + t * (1 + int(xs[(i+1) % n])) for i in range(n)]
        product = 1
        for clause in cnf:
            unsat = 1
            for lit in clause:
                u = shifted[abs(lit) - 1]
                literal = u if lit > 0 else 1 - u
                unsat *= 1 - literal
            product *= 1 - unsat
        total += product
    return total


def interpolate_at_zero(n: int, cnf: tuple[tuple[int, ...], ...]) -> int:
    """Recover H(0) from H(1)..H(D+1), D=sum clause widths.

    Integer Lagrange identity: H(0) = sum_{j=1}^{D+1}
    (-1)^(j-1) * binom(D+1,j) * H(j) for degree(H)<=D.
    """
    degree_bound = sum(map(len, cnf))
    return sum((-1 if j % 2 == 0 else 1) * math.comb(degree_bound + 1, j)
               * deformed_polynomial_sum(n, cnf, j)
               for j in range(1, degree_bound + 2))


def simplify_on(n: int, cnf: tuple[tuple[int, ...], ...], values: dict[int, bool]):
    """Substitute cutset assignments, preserving genuinely empty clauses."""
    out = []
    for clause in cnf:
        if any((lit > 0) == values[abs(lit)] for lit in clause if abs(lit) in values):
            continue
        out.append(tuple(lit for lit in clause if abs(lit) not in values))
    return tuple(out)


def components(n: int, cnf: tuple[tuple[int, ...], ...], forbidden: set[int]):
    """Connected components of residual variable-clause primal graph."""
    nodes = set(range(1, n + 1)) - forbidden
    graph = {v: set() for v in nodes}
    for clause in cnf:
        refs = set(abs(lit) for lit in clause)
        for v in refs:
            graph[v].update(refs - {v})
    parts = []
    while nodes:
        v = min(nodes)
        stack, part = [v], set()
        while stack:
            u = stack.pop()
            if u in part:
                continue
            part.add(u)
            stack.extend(graph[u] - part)
        nodes -= part
        parts.append(part)
    return parts


def remap_count(part: set[int], cnf: tuple[tuple[int, ...], ...]) -> int:
    variables = sorted(part)
    relabel = {v: i + 1 for i, v in enumerate(variables)}
    subclauses = tuple(tuple((1 if lit > 0 else -1) * relabel[abs(lit)]
                              for lit in clause)
                       for clause in cnf if any(abs(lit) in part for lit in clause))
    return count_exhaustive(len(part), subclauses)


def count_cutset(n: int, cnf: tuple[tuple[int, ...], ...], cutset: tuple[int, ...]) -> tuple[int, int]:
    """Exact cutset conditioning and component-product enumeration.

    A finite special case of a measurement-conditioned sum/product identity,
    NOT the manuscript's general measurement design or algorithm.
    Returns (exact count, operation proxy = assignments enumerated).
    """
    validate(n, cnf)
    if len(cutset) != len(set(cutset)) or any(v < 1 or v > n for v in cutset):
        raise ValueError("invalid cutset")
    total, work = 0, 0
    for bits in itertools.product((False, True), repeat=len(cutset)):
        values = dict(zip(cutset, bits))
        simplified = simplify_on(n, cnf, values)
        if any(not clause for clause in simplified):
            continue
        ways = 1
        for part in components(n, simplified, set(cutset)):
            work += 1 << len(part)
            ways *= remap_count(part, simplified)
        total += ways
    return total, work


def discover_cutset(n: int, cnf: tuple[tuple[int, ...], ...], max_size: int = 2):
    """A reproducible candidate search based on cost proxy (not an LLM)."""
    candidates = itertools.chain.from_iterable(itertools.combinations(range(1, n + 1), r)
                                                for r in range(min(max_size, n) + 1))
    best = None
    for cutset in candidates:
        count, work = count_cutset(n, cnf, cutset)
        record = (work, len(cutset), cutset, count)
        if best is None or record[:3] < best[:3]:
            best = record
    assert best is not None
    return {"cutset": list(best[2]), "estimated_enumerations": best[0],
            "count": best[3], "baseline_enumerations": 1 << n,
            "candidate_is_faster_by_proxy": best[0] < (1 << n)}


def run(seed=20261101, cases=80, nmax=7):
    rng = random.Random(seed)
    failures, records = [], []
    for i in range(cases):
        n = rng.randint(0, nmax)
        cnf = tuple(tuple(rng.choice((-1, 1)) * rng.randint(1, n) for _ in range(rng.randint(1, 3)))
                    for _ in range(rng.randint(0, n + 3))) if n else (() if i % 2 else ((),))
        a = count_exhaustive(n, cnf)
        b = count_dpll(n, cnf)
        c = interpolate_at_zero(n, cnf)
        # Metamorphic properties are checked independently of interpolation.
        reordered = count_dpll(n, tuple(reversed(cnf)))
        extra_free = count_dpll(n + 1, cnf)
        duplicated = count_dpll(n, cnf + (cnf[:1] if cnf else ()))
        taut = count_dpll(n, cnf + (((1, -1),) if n else ()))
        checks = {"bruteforce_eq_dpll": a == b,
                  "bruteforce_eq_interpolation": a == c,
                  "order_invariance": a == reordered,
                  "unused_variable_doubles": extra_free == 2 * a,
                  "duplicated_clause_invariant": duplicated == a,
                  "tautology_invariant": taut == a}
        if n and i % 6 == 0:
            sep = discover_cutset(n, cnf)
            checks["cutset_eq_bruteforce"] = sep["count"] == a
        if not all(checks.values()):
            failures.append({"index": i, "cnf": cnf, "n": n, "checks": checks,
                             "exhaustive": a, "dpll": b, "interpolated": c})
        records.append({"n": n, "clauses": cnf, "checks": checks})
    # Negative controls must be caught by the oracle. AND != OR for 1-clause 2-literal formula.
    and_instead_of_or = sum((bool(mask & 1) and bool(mask & 2)) for mask in range(4))
    oracle = count_exhaustive(2, ((1, 2),))
    negative_control_detected = and_instead_of_or != oracle  # 1 != 3
    # Under-degree interpolation must give the wrong result on a fixed witness.
    witness = ((1, 2),)
    bad_interpolation = deformed_polynomial_sum(2, witness, 1)
    negative_underdegree_detected = bad_interpolation != count_exhaustive(2, witness)
    result = {
        "schema": "astra-math-lab/1", "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "source": SOURCE,
        "scope": "finite identity tests; no asymptotic, Lean or full-paper replication",
        "seed": seed, "cases": cases, "nmax": nmax,
        "checks_executed": sum(len(x["checks"]) for x in records) + 2,
        "failed_cases": failures,
        "negative_controls": {"AND_instead_of_OR_rejected": negative_control_detected,
                              "underdegree_interpolation_rejected": negative_underdegree_detected},
        "status": "PASS" if not failures and negative_control_detected and negative_underdegree_detected else "FAIL",
    }
    material = json.dumps({"seed": seed, "records": records}, sort_keys=True, separators=(",", ":"))
    result["corpus_sha256"] = hashlib.sha256(material.encode()).hexdigest()
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cases", type=int, default=80)
    parser.add_argument("--seed", type=int, default=20261101)
    parser.add_argument("--nmax", type=int, default=7)
    parser.add_argument("--output", type=Path)
    a = parser.parse_args()
    if a.cases < 1 or not (0 <= a.nmax <= 12):
        parser.error("cases>=1 and 0<=nmax<=12 required (resource guard)")
    report = run(seed=a.seed, cases=a.cases, nmax=a.nmax)
    data = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(data, encoding="utf-8")
    print(data)
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__":
    main()
