"""Reproducible time/space comparison for a single exact coordinate."""
from argparse import ArgumentParser
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import platform
from statistics import median
from time import perf_counter_ns
import tracemalloc

from clay_swap_coordinate import (
    coordinate_by_model_counts, coordinate_eliminate, coordinate_enumerated, gap_instance,
)
from eth_lab import satisfied
from projected_spectrum import apply_scaled_dp


def measure(function, repeat=3):
    times = []
    for _ in range(repeat):
        start = perf_counter_ns()
        value = function()
        times.append(perf_counter_ns() - start)
    tracemalloc.start()
    try:
        assert function() == value
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return {"value": value, "median_ns": median(times), "peak_python_bytes": peak}


def min_fill(q, cnf):
    neighbors = {var: set() for var in range(1, q + 1)}
    for clause in cnf:
        for a, b in combinations(set(map(abs, clause)), 2):
            neighbors[a].add(b)
            neighbors[b].add(a)

    def priority(var):
        adjacent = neighbors[var]
        absent_edges = sum(b not in neighbors[a] for a, b in combinations(adjacent, 2))
        return absent_edges, len(adjacent), var

    order = []
    width = 0
    while neighbors:
        var = min(neighbors, key=priority)
        adjacent = neighbors.pop(var)
        width = max(width, len(adjacent))
        for a in adjacent:
            neighbors[a].remove(var)
            neighbors[a].update(adjacent - {a})
        order.append(var)
    return tuple(order), width


def dimacs(path):
    variables = declared_clauses = None
    clauses = []
    current = []
    for line in path.read_text(encoding="ascii").splitlines():
        parts = line.split()
        if not parts or parts[0] == "c":
            continue
        if parts[0] == "p":
            if parts[:2] != ["p", "cnf"]:
                raise ValueError("expected a DIMACS CNF")
            variables, declared_clauses = map(int, parts[2:])
            continue
        if parts[0] == "%":
            break
        for raw in parts:
            literal = int(raw)
            if literal:
                current.append(literal)
            else:
                clauses.append(tuple(current))
                current.clear()
    if variables is None or current or len(clauses) != declared_clauses:
        raise ValueError(f"invalid DIMACS file {path}")
    return variables, tuple(clauses)


def full_table_coordinate(q, cnf):
    vec = tuple(int(satisfied(mask, cnf)) for mask in range(4**q))
    return apply_scaled_dp(vec, q)[((1 << q) - 1) << q]



def cdcl_unique_model(q, cnf):
    """Independent 0/1-model benchmark check using CaDiCaL and a blocking clause."""
    from pysat.solvers import Solver

    with Solver(name="cadical195", bootstrap_with=cnf) as solver:
        for var in range(1, q + 1):
            solver.add_clause((var, -var))
        if not solver.solve():
            return None
        model = solver.get_model()
        assert {abs(lit) for lit in model} == set(range(1, q + 1))
        solver.add_clause(tuple(-lit for lit in model))
        if solver.solve():
            raise ValueError("external benchmark expects at most one model")

    return model


def cdcl_unique_coordinate(q, cnf):
    model = cdcl_unique_model(q, cnf)
    if model is None:
        return 0, 0
    ones = sum(lit > 0 for lit in model)
    return 1, binomial_weight(q, ones)


def binomial_weight(q, ones):
    coeff2, coeff3 = (sum((-1)**j * comb(ones, j) * comb(q - ones, k - j)
                          for j in range(k + 1)) for k in (2, 3))
    return 4 * (coeff2 - coeff3)


def comparison(label, q, cnf, order=None):
    structural = coordinate_eliminate(q, cnf, order)
    results = {"bucket_elimination": measure(lambda: coordinate_eliminate(q, cnf, order).value)}
    if q <= 7:
        results["original_full_projector"] = measure(lambda: full_table_coordinate(q, cnf))
    if q <= 14:
        results["orbit_enumeration"] = measure(lambda: coordinate_enumerated(q, cnf))
    if q <= 10:
        results["DPLL_moments"] = measure(lambda: coordinate_by_model_counts(q, cnf))
    if any(entry["value"] != structural.value for entry in results.values()):
        raise AssertionError(f"exact reference mismatch on {label}")
    return {
        "instance": label, "variables": q, "clauses": len(cnf),
        "induced_width": structural.induced_width, "max_factor_rows": structural.max_factor_rows,
        "measurements": results,
    }


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--dimacs", type=Path, nargs="*", default=[])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for q in (6, 10, 14, 32, 64):
        clauses = tuple((x, x + 1) for x in range(1, q))
        row = comparison("path", q, clauses)
        row["closed_form_value"] = sum(comb(q - zeros + 1, zeros)
                                       * binomial_weight(q, q - zeros)
                                       for zeros in range((q + 1) // 2 + 1))
        assert row["closed_form_value"] == row["measurements"]["bucket_elimination"]["value"]
        rows.append(row)
    for q in (6, 8, 10, 12):
        clauses = tuple(combinations(range(1, q + 1), 2))
        row = comparison("clique", q, clauses)
        row["closed_form_value"] = binomial_weight(q, q) + q * binomial_weight(q, q - 1)
        assert row["closed_form_value"] == row["measurements"]["bucket_elimination"]["value"]
        rows.append(row)
    for path in args.dimacs:
        q, cnf = dimacs(path)
        order, width = min_fill(q, cnf)
        baseline = measure(lambda: cdcl_unique_coordinate(q, cnf)[1])
        moments = measure(lambda: coordinate_by_model_counts(
            q, cnf, lambda n, f: int(cdcl_unique_model(n, f) is not None)))
        if baseline["value"] != moments["value"]:
            raise AssertionError(f"CDCL-backed exact results disagree on {path.name}")
        row = {
            "instance": path.name, "variables": q, "clauses": len(cnf),
            "induced_width": width, "sha256": sha256(path.read_bytes()).hexdigest(),
            "independent_model_count": cdcl_unique_coordinate(q, cnf)[0],
            "measurements": {"CaDiCaL_0_or_1_model": baseline, "CaDiCaL_moments": moments},
        }
        if width <= 12:
            result = measure(lambda: coordinate_eliminate(q, cnf, order, width_limit=12).value)
            if result["value"] != baseline["value"]:
                raise AssertionError(f"elimination disagrees with CDCL on {path.name}")
            row["measurements"]["bucket_elimination"] = result
        else:
            try:
                coordinate_eliminate(q, cnf, order, width_limit=12)
            except ValueError as exc:
                if "exceeds limit" not in str(exc):
                    raise
                row["bucket_elimination_width_guard"] = str(exc)
            else:
                raise AssertionError(f"width guard did not reject {path.name}")
        gq, transformed = gap_instance(q, cnf, 0, ((),))
        transformed_count, value = cdcl_unique_coordinate(gq, transformed)
        if value != 2 * gq * row["independent_model_count"]:
            raise AssertionError(f"gap reduction disagrees with CDCL on {path.name}")
        row["gap_against_false"] = {
            "variables": gq, "clauses": len(transformed), "coordinate": value,
            "independent_model_count": transformed_count,
        }
        rows.append(row)
    payload = {
        "status": "PASS",
        "python": platform.python_version(),
        "platform": platform.platform(),
        "measurement": "Median of three untraced runs and a separate Python allocation peak",
        "cases": rows,
    }
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
