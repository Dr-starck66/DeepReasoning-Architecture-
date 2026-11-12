#!/usr/bin/env python3
"""ASTRA MATH RESEARCH ENGINE Ω — reproducible finite research gate (stdlib).

Independent reconstructions of a 64x64 swap matrix, exact rank over Q, rank
modulo two primes, intentional falsifications, optional cross-check with the
existing ASTRA lowrank_exact.py and optional Lean execution. No global theorem.
"""
from __future__ import annotations
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import shutil
import subprocess

Q = 3
D = 2 ** (2 * Q)


def swap_bits(index: int, axes: tuple[int, ...]) -> int:
    # bits 0..2 are a1..a3; bits 3..5 are d1..d3
    for axis in axes:
        i, j = axis, axis + Q
        if ((index >> i) ^ (index >> j)) & 1:
            index ^= (1 << i) | (1 << j)
    return index


def construct_matrix() -> tuple[tuple[int, ...], ...]:
    """Build M0 directly using bit positions, not ASTRA's tuple-label code."""
    m = [[0] * D for _ in range(D)]
    for u in range(D):
        for omitted_axis in range(Q):
            target = swap_bits(u, tuple(a for a in range(Q) if a != omitted_axis))
            m[u][target] += 1
        m[u][swap_bits(u, (0, 1, 2))] -= Q - 1
    return tuple(tuple(row) for row in m)


def difference(m: tuple[tuple[int, ...], ...]) -> tuple[tuple[int, ...], ...]:
    return tuple(tuple((i == j) - value for j, value in enumerate(row))
                 for i, row in enumerate(m))


def rank_over_q(matrix: tuple[tuple[int, ...], ...]) -> int:
    """Independent exact rational row elimination, no floating point."""
    if not matrix:
        return 0
    rows = [list(map(Fraction, r)) for r in matrix]
    width, pivot_row = len(rows[0]), 0
    for col in range(width):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][col]
        for j in range(col, width):
            rows[pivot_row][j] /= scale
        for i in range(pivot_row + 1, len(rows)):
            scale = rows[i][col]
            if scale:
                for j in range(col, width):
                    rows[i][j] -= scale * rows[pivot_row][j]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def rank_mod_prime(matrix: tuple[tuple[int, ...], ...], prime: int) -> int:
    """Different finite-field elimination; provides only a lower bound over Q."""
    if not matrix:
        return 0
    rows = [[v % prime for v in r] for r in matrix]
    width, pivot_row = len(rows[0]), 0
    for col in range(width):
        pivot = next((i for i in range(pivot_row, len(rows)) if rows[i][col]), None)
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inv = pow(rows[pivot_row][col], -1, prime)
        for j in range(col, width):
            rows[pivot_row][j] = rows[pivot_row][j] * inv % prime
        for i in range(pivot_row + 1, len(rows)):
            factor = rows[i][col]
            if factor:
                for j in range(col, width):
                    rows[i][j] = (rows[i][j] - factor * rows[pivot_row][j]) % prime
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def canonical_sha(obj: object) -> str:
    blob = json.dumps(obj, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('utf-8')
    return hashlib.sha256(blob).hexdigest()


def compare_existing(existing_dir: Path, ours: tuple[tuple[int, ...], ...]):
    """Compare by each semantic tuple label, without relying on row ordering."""
    import importlib.util
    source = existing_dir / 'lowrank_exact.py'
    if not source.is_file():
        return {'status': 'UNVERIFIED', 'reason': 'existing lowrank_exact.py not in local checkout'}
    spec = importlib.util.spec_from_file_location('astra_lowrank_reuse', source)
    if spec is None or spec.loader is None:
        return {'status': 'FAIL', 'reason': 'cannot load existing module'}
    import sys
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    old = module.FiniteSwapMatrix.build()
    def to_integer(lab):
        return sum(bit << i for i, bit in enumerate(lab[0])) + sum(bit << (i + Q) for i, bit in enumerate(lab[1]))
    reference = {to_integer(lab): i for i, lab in enumerate(old.labels)}
    matches = all(ours[u][v] == old.M0[reference[u]][reference[v]] for u in range(D) for v in range(D))
    return {'status': 'PASS' if matches else 'FAIL', 'matrix_entries_compared': D * D,
            'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest()}


def run_lean(lean_file: Path):
    lean = shutil.which('lean')
    if not lean or not lean_file.is_file():
        return {'status': 'UNVERIFIED', 'reason': 'Lean executable or source not available'}
    # This proves only the lemmas already present in the source, NOT the global rank theorem.
    proc = subprocess.run([lean, str(lean_file)], capture_output=True, text=True, timeout=120, check=False)
    return {'status': 'PASS' if proc.returncode == 0 else 'FAIL', 'returncode': proc.returncode,
            'lean_version': subprocess.run([lean, '--version'], capture_output=True, text=True, timeout=10).stdout.strip(),
            'stderr_tail': proc.stderr[-1000:],
            'scope': 'Lean lemmas in LowRankExact.lean; no Lean proof of rank(I-M0)=10'}


def research(existing_dir: Path) -> dict:
    m = construct_matrix()
    a = difference(m)
    rank_q = rank_over_q(a)
    rank_f101 = rank_mod_prime(a, 101)
    rank_f103 = rank_mod_prime(a, 103)
    rank_m0 = rank_over_q(m)
    # Negative control 1: falsify a matrix coefficient, so rank should increase.
    corrupted = [list(row) for row in m]
    corrupted[0][0] += 1
    bad_rank = rank_over_q(difference(tuple(tuple(row) for row in corrupted)))
    # Negative control 2: intentionally false rank conjecture.
    false_conjecture_rejected = rank_m0 != 10
    controls = {'changed_coefficient_rejected': bad_rank != 10,
                'false_rank_M0_equals_10_rejected': false_conjecture_rejected,
                'mutated_rank_I_minus_M0': bad_rank}
    independent = compare_existing(existing_dir, m)
    formal = run_lean(existing_dir / 'LowRankExact.lean')
    finite_pass = (rank_q, rank_f101, rank_f103) == (10, 10, 10) and rank_m0 == 64 and all(
        controls[k] for k in ('changed_coefficient_rejected', 'false_rank_M0_equals_10_rejected'))
    if independent['status'] == 'FAIL' or formal['status'] == 'FAIL':
        status = 'FAIL'
    elif not finite_pass:
        status = 'FAIL'
    else:
        status = 'PASS'
    receipt = {
        'schema': 'astra-math-research/1', 'claim_id': 'SWAP-Q3-R2-FINITE-RANK-001',
        'claim': 'For r=2, Q=3, R=2, A0=0, rank_Q(I-M0)=10 in dimension 64.',
        'scope': 'one finite, fully enumerated matrix; NOT an asymptotic k-SAT theorem',
        'parameters': {'r': 2, 'Q': 3, 'R': 2, 'A0': 0, 'dimension': D},
        'results': {'rank_Q_I_minus_M0': rank_q, 'rank_F101_I_minus_M0': rank_f101,
                    'rank_F103_I_minus_M0': rank_f103, 'rank_Q_M0': rank_m0},
        'controls': controls,
        'integration_with_existing_astra': independent,
        'lean_source_check': formal,
        'artifacts': {'matrix_sha256': canonical_sha(m), 'difference_sha256': canonical_sha(a)},
        'claim_status': status,
        'global_lean_formalization_of_rank': 'UNVERIFIED',
        'yang_mills_mass_gap': 'UNVERIFIED',
        'automated_discovery': 'UNVERIFIED',
        'limitations': ['Finite enumeration is not a general mathematical proof.',
                        'Finite-field rank matching exact rank is a consistency check, not a separate proof.',
                        'Lean file, even if executed, does not formalize the full rank result.',
                        'Local test is not persistent or automatically scheduled.'],
    }
    receipt['receipt_sha256'] = canonical_sha(receipt)
    return receipt


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--existing-dir', type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    report = research(args.existing_dir)
    payload = json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(payload, encoding='utf-8')
    print(payload)
    return 0 if report['claim_status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
