"""Compare affine quotient evaluation against independent reference calculations."""
from argparse import ArgumentParser
from dataclasses import asdict
from functools import reduce
from hashlib import sha256
import json
from operator import xor
from pathlib import Path
import platform
from statistics import median
from time import perf_counter_ns
import tracemalloc

from benchmark_clay_swap_coordinate import cdcl_unique_coordinate, dimacs, min_fill
from clay_affine_coordinate import coordinate_affine, extract_parities
from clay_swap_coordinate import coordinate_eliminate
from test_clay_affine_coordinate import code_oracle, dense_parity_code


def measured(q, cnf):
    times = []
    for _ in range(5):
        before = perf_counter_ns()
        result = coordinate_affine(q, cnf)
        times.append(perf_counter_ns() - before)
    tracemalloc.start()
    try:
        if coordinate_affine(q, cnf) != result:
            raise AssertionError("affine run changed its answer")
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return result, {"median_ns": median(times), "peak_python_bytes": peak}


def width_block(q, cnf):
    try:
        coordinate_eliminate(q, cnf)
    except ValueError as error:
        return str(error)
    raise AssertionError("expected old method to reach its width limit")


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--dimacs", nargs="*", type=Path, default=[])
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = []
    for label, seed, residual, extras in (
        ("dense parity", 7, (), 0),
        ("dense parity with residual clauses", 7, ((1, 2, 4), (1, -3, 8), (-2, -4, 8)), 0),
        ("dense parity with free variables", 5, ((1, 2, 4), (1, -3, 8), (-2, -4, 8)), 70),
    ):
        cnf = dense_parity_code(seed) + residual
        q = (1 << seed) - 1 + extras
        found, metrics = measured(q, cnf)
        expected = code_oracle(seed, residual, extras)
        if expected != (found.models, found.coordinate):
            raise AssertionError(f"generator oracle disagrees on {label}")
        rows.append({"instance": label, "variables": q, "clauses": len(cnf),
                     "affine": asdict(found), **metrics,
                     "independent_generator": {"models": expected[0], "coordinate": expected[1]},
                     "bucket_elimination": width_block(q, cnf)})

    for path in args.dimacs:
        q, cnf = dimacs(path)
        expected = cdcl_unique_coordinate(q, cnf)
        row = {"instance": path.name, "variables": q, "clauses": len(cnf),
               "sha256": sha256(path.read_bytes()).hexdigest(),
               "independent_CaDiCaL": {"models": expected[0], "coordinate": expected[1]}}
        try:
            result, metrics = measured(q, cnf)
        except ValueError as error:
            if "residual affine rank" not in str(error):
                raise
            row["affine"] = str(error)
        else:
            if (result.models, result.coordinate) != expected:
                raise AssertionError(f"CDCL disagrees on {path.name}")
            row.update({"affine": asdict(result), **metrics})
            if result.models == 0:
                equations, _ = extract_parities(q, cnf)
                lhs = reduce(xor, (mask for mask, _ in equations), 0)
                rhs = reduce(xor, (bit for _, bit in equations), 0)
                if lhs == 0 and rhs == 1:
                    row["parity_certificate"] = [
                        {"variables": [i + 1 for i in range(q) if mask & (1 << i)], "rhs": bit}
                        for mask, bit in equations
                    ]

        order, width = min_fill(q, cnf)
        row["min_fill_width"] = width
        if width <= 12:
            value = coordinate_eliminate(q, cnf, order, width_limit=12).value
            if value != expected[1]:
                raise AssertionError(f"bucket elimination disagrees on {path.name}")
            row["bucket_elimination_coordinate"] = value
        rows.append(row)
    payload = {"status": "PASS", "python": platform.python_version(),
               "method": "five untraced runs followed by a separate Python allocation profile",
               "cases": rows}
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
