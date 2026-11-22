#!/usr/bin/env python3
"""ASTRA Ω: independent, exact finite spectral certificate for the Q=3 swap model.

No floating point, no third-party deps. A finite certificate, not an asymptotic
speedup theorem, and not a Lean kernel check. Reuses the project's existing
math_research_engine.construct_matrix() when available for a 4096-entry audit.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path
import sys

Q = 3
DIM = 1 << (2 * Q)


def swap(index: int, axes: tuple[int, ...]) -> int:
    for axis in axes:
        left, right = axis, axis + Q
        if ((index >> left) ^ (index >> right)) & 1:
            index ^= (1 << left) | (1 << right)
    return index


def model_matrix() -> tuple[tuple[int, ...], ...]:
    """Independent assembly from three commuting swaps, not Gauss elimination."""
    rows = [[0] * DIM for _ in range(DIM)]
    for i in range(DIM):
        for omitted in range(Q):
            rows[i][swap(i, tuple(a for a in range(Q) if a != omitted))] += 1
        rows[i][swap(i, tuple(range(Q)))] -= Q - 1
    return tuple(map(tuple, rows))


# Single pair, ordered (a,d) = 00,10,01,11:
# eigenvectors for S: 00(+), 11(+), (10+01)(+), (10-01)(-).
PAIR = (
    (1, 0, 0, 0),
    (0, 0, 0, 1),
    (0, 1, 1, 0),
    (0, 1, -1, 0),
)


def pair_det() -> int:
    """Small exact determinant; expansion of the 4! permutations."""
    total = 0
    for order in itertools.permutations(range(4)):
        inversions = sum(order[i] > order[j] for i in range(4) for j in range(i + 1, 4))
        product = (-1) ** inversions
        for row, col in enumerate(order):
            product *= PAIR[col][row]
        total += product
    return total


def basis_vector(types: tuple[int, int, int]) -> tuple[int, ...]:
    values = []
    for i in range(DIM):
        weight = 1
        for axis, kind in enumerate(types):
            pair_index = ((i >> axis) & 1) | (((i >> (axis + Q)) & 1) << 1)
            weight *= PAIR[kind][pair_index]
        values.append(weight)
    return tuple(values)


def eigenvalue(types: tuple[int, int, int]) -> int:
    negatives = sum(kind == 3 for kind in types)
    # M0 = (S1*S2*S3) * (S1 + S2 + S3 - 2I)
    return (-1) ** negatives * (1 - 2 * negatives)


def verify_columns(matrix: tuple[tuple[int, ...], ...], *, wrong_eigenvalues=False) -> dict:
    failing = []
    hist = {}
    columns_checked = entries_checked = 0
    for types in itertools.product(range(4), repeat=Q):
        vec = basis_vector(types)
        lam = eigenvalue(types) + (1 if wrong_eigenvalues else 0)
        hist[str(1 - eigenvalue(types))] = hist.get(str(1 - eigenvalue(types)), 0) + 1
        columns_checked += 1
        for i in range(DIM):
            expected = lam * vec[i]
            actual = sum(matrix[i][j] * vec[j] for j in range(DIM))
            entries_checked += 1
            if actual != expected and len(failing) < 4:
                failing.append({'basis': types, 'row': i, 'actual': actual, 'expected': expected})
    return {'ok': not failing, 'columns_checked': columns_checked,
            'equations_checked': entries_checked, 'nonzero_eigenvalue_multiplicities_I_minus_M0':
            {k: v for k, v in hist.items() if int(k) != 0},
            'failures': failing}


def digest(obj: object) -> str:
    return hashlib.sha256(json.dumps(obj, separators=(',', ':'), sort_keys=True).encode()).hexdigest()


def assess(verify_astra: bool = True) -> dict:
    matrix = model_matrix()
    diag = verify_columns(matrix)
    det = pair_det()
    # Nonzero det(B) implies B^tensor3 invertible; det(B^tensor3)=det(B)^48.
    det_tensor_nonzero = det != 0
    distinct = diag['nonzero_eigenvalue_multiplicities_I_minus_M0']
    exact_rank = sum(distinct.values()) if diag['ok'] and det_tensor_nonzero else None
    # Two mandatory negative controls must detect corruption / wrong spectral claim.
    mutated = [list(row) for row in matrix]
    mutated[0][0] += 1
    mutation_rejected = not verify_columns(tuple(map(tuple, mutated)))['ok']
    wrong_claim_rejected = not verify_columns(matrix, wrong_eigenvalues=True)['ok']
    cross = {'status': 'UNVERIFIED', 'reason': 'ASTRA math_research_engine unavailable'}
    if verify_astra:
        try:
            import math_research_engine as existing
            original = existing.construct_matrix()
            mismatches = sum(matrix[i][j] != original[i][j]
                             for i in range(DIM) for j in range(DIM))
            cross = {'status': 'PASS' if mismatches == 0 else 'FAIL',
                     'entries_compared': DIM * DIM, 'mismatches': mismatches}
        except ImportError:
            pass
        except Exception as exc:
            cross = {'status': 'FAIL', 'reason': f'{type(exc).__name__}: {exc}'}
    core_ok = (diag['ok'] and det_tensor_nonzero and det in (-2, 2) and
               exact_rank == 10 and mutation_rejected and wrong_claim_rejected and
               distinct == {'4': 9, '-4': 1})
    report = {
        'schema': 'astra-spectral-certificate/1',
        'claim_id': 'SWAP-Q3-R2-SPECTRAL-RANK10-001',
        'claim': 'For this exact 64x64 swap-defined M0, rank_Q(I - M0) = 10.',
        'claim_scope': 'finite matrix only; no asymptotic complexity or quantum speedup',
        'construction': 'M0 = S2*S3 + S1*S3 + S1*S2 - 2*S1*S2*S3',
        'independence_argument': 'Each local 4x4 swap-eigenbasis has nonzero determinant; its threefold tensor product is invertible.',
        'pair_basis_determinant': det,
        'tensor_basis_determinant_absolute_value': abs(det) ** 48,
        'spectral': diag, 'rank_over_Q_from_spectrum': exact_rank,
        'negative_controls': {'single_entry_mutation_rejected': mutation_rejected,
                              'wrong_eigenvalue_claim_rejected': wrong_claim_rejected},
        'existing_ASTRA_4096_entry_crosscheck': cross,
        'model_matrix_sha256': digest(matrix),
        'formal_Lean_kernel_verification': 'UNVERIFIED',
        'computational_certificate_status': 'PASS' if core_ok else 'FAIL',
        'project_integration_status': cross['status'],
    }
    report['receipt_sha256'] = digest(report)
    return report


def main(argv=None) -> int:
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path)
    args = p.parse_args(argv)
    receipt = assess()
    encoded = json.dumps(receipt, indent=2, sort_keys=True) + '\n'
    if args.output:
        args.output.write_text(encoded, encoding='utf-8')
    print(encoded)
    return 0 if receipt['computational_certificate_status'] == 'PASS' and receipt['project_integration_status'] != 'FAIL' else 1


if __name__ == '__main__':
    sys.exit(main())
