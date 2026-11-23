"""ASTRA MATH LAB Ω — counterexample-guided discovery (CEGIS), offline.

Finds, rather than assumes, the 4-of-8 parity switch with identical
1- and 2-way signed literal incidences. Synthesizes a shared 3-CNF
forcing gadget, constructs opposite SAT labels, and independently verifies
both via finite oracle and exact proof certificates.

Claim scope: A classifier of *strict 3-CNF* using only <=2-wise signed
literal cooccurrence counts cannot decide SAT on every input, for n>=5.
This does not imply P != NP or a new prize-eligible theorem.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from hashlib import sha256
from itertools import combinations, product
import json
from typing import Iterable

from sat_certificate import oracle, produce, validate_cnf, verify


def feature_signature(n: int, clauses: Iterable[Iterable[int]], order: int = 2) -> tuple:
    """All signed 1..order-literal cooccurrence counts, incl. n and m.

    Count an occurrence only if the signed literals are in the SAME clause.
    order=3 identifies the strict 3-CNF clause multiset exactly.
    """
    if order not in (1, 2, 3):
        raise ValueError('order must be 1, 2, or 3')
    clauses = validate_cnf(n, clauses, strict_3cnf=True)
    totals = defaultdict(int)
    for clause in clauses:
        for k in range(1, order + 1):
            for sub in combinations(sorted(clause, key=lambda v: abs(v)), k):
                totals[sub] += 1
    return (n, len(clauses), tuple(sorted(totals.items())))


def discover_switch() -> dict:
    """Search every 4-clause subset of the 8 signed clauses on 3 variables.

    Select a non-identical collision for order<=2, rejecting any false
    collision where the order=3 features also match.
    """
    cube = [tuple(sign * var for var, sign in zip((1, 2, 3), signs))
            for signs in product((-1, 1), repeat=3)]
    classes = defaultdict(list)
    examined = 0
    for subset in combinations(cube, 4):
        examined += 1
        key = feature_signature(3, subset, 2)
        for prior in classes[key]:
            if feature_signature(3, prior, 3) != feature_signature(3, subset, 3):
                return {'a': prior, 'b': subset, 'examined': examined,
                        'total_possible': 70, 'switch_size': 4}
        classes[key].append(subset)
    raise RuntimeError('No exact 2-way-signature collision found')


def forcing_gadget(target: tuple[bool, bool, bool]) -> tuple[tuple[int, ...], ...]:
    """Exactly force x1,x2,x3 to target using 4 clauses per target bit.

    For each xi, use (literal_i OR ±x4 OR ±x5) with every sign pair.
    When literal_i is false, the four 2-literal clauses in x4,x5 are
    jointly UNSAT; when it is true, all four clauses are satisfied.
    """
    clauses = []
    for i, truth in enumerate(target, 1):
        literal = i if truth else -i
        for s4, s5 in product((-1, 1), repeat=2):
            clauses.append((literal, s4 * 4, s5 * 5))
    return tuple(clauses)


def canonical(clauses) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(tuple(sorted(c, key=abs)) for c in clauses))


def independent_pairwise_audit(n, a, b):
    """Separate implementation: brute count by scanning all literal pairs.

    Deliberately does not call feature_signature, the discovery feature engine.
    """
    clauses_a, clauses_b = validate_cnf(n, a, True), validate_cnf(n, b, True)
    if len(clauses_a) != len(clauses_b):
        return False
    for var in range(1, n + 1):
        for sign in (-1, 1):
            lit = var * sign
            if sum(lit in cl for cl in clauses_a) != sum(lit in cl for cl in clauses_b):
                return False
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            for si, sj in product((-1, 1), repeat=2):
                lits = (si * i, sj * j)
                if sum(all(lit in cl for lit in lits) for cl in clauses_a) != \
                   sum(all(lit in cl for lit in lits) for cl in clauses_b):
                    return False
    return True


def find_counterexample(n: int = 5, with_certificates: bool = True) -> dict:
    if not isinstance(n, int) or isinstance(n, bool) or not 5 <= n <= 10:
        raise ValueError('Research-bound n must be 5..10')
    switch = discover_switch()
    for target in product((False, True), repeat=3):
        gadget = forcing_gadget(target)
        raw_a = canonical(tuple(switch['a']) + gadget)
        raw_b = canonical(tuple(switch['b']) + gadget)
        if feature_signature(n, raw_a, 2) != feature_signature(n, raw_b, 2):
            continue
        if not independent_pairwise_audit(n, raw_a, raw_b):
            continue
        if len(raw_a) != len(set(raw_a)) or len(raw_b) != len(set(raw_b)):
            continue
        truth_a = oracle(n, raw_a)
        truth_b = oracle(n, raw_b)
        if (truth_a is None) == (truth_b is None):
            continue
        sat_clauses, unsat_clauses = (raw_a, raw_b) if truth_a is not None else (raw_b, raw_a)
        sat_witness = truth_a if truth_a is not None else truth_b
        output = {
            'experiment': 'CEGIS exact strict-3CNF 2-wise signed-marginal collision',
            'n': n, 'm': len(sat_clauses),
            'cube_four_of_eight_examined': switch['examined'],
            'cube_switch_size': 4,
            'target_forced_bits': [int(b) for b in target],
            'sat_clauses': [list(c) for c in sat_clauses],
            'unsat_clauses': [list(c) for c in unsat_clauses],
            'sat_witness': [int(sat_witness[i]) for i in range(1, n + 1)],
            'one_way_equal': feature_signature(n, sat_clauses, 1) == feature_signature(n, unsat_clauses, 1),
            'two_way_equal': True,
            'third_order_equal': feature_signature(n, sat_clauses, 3) == feature_signature(n, unsat_clauses, 3),
            'independent_pairwise_audit': True,
            'different_sat_statuses': True,
            'general_result': 'For all n >= 5, no SAT decision rule solely on <=2-wise signed literal cooccurrence counts, n, m is correct for every strict 3-CNF; pad these 5-variable formulas with unused variables.',
            'proof_logic': 'The two 4-clause sets are complementary parity sign patterns with identical signed 1,2-marginals. The shared 12-clause gadget forces x1,x2,x3. Exactly one parity set excludes this assignment. Remaining variables are unconstrained.',
            'complexity_claim': 'NONE; counterexample to a restricted feature class, not a 3-SAT runtime lower bound',
            'novelty': 'UNVERIFIED', 'p_vs_np': 'UNVERIFIED', 'prize_eligible': False,
        }
        if with_certificates:
            sat_cert = produce(n, sat_clauses, True)
            unsat_cert = produce(n, unsat_clauses, True)
            if (sat_cert['verdict'] != 'SAT' or unsat_cert['verdict'] != 'UNSAT' or
                    not verify(sat_cert) or not verify(unsat_cert)):
                raise AssertionError('Independent certificate checker rejected the discovery')
            output['certificates'] = {'sat': sat_cert, 'unsat': unsat_cert}
            output['verified'] = True
            output['sat_search_nodes'] = sat_cert['search_nodes']
            output['unsat_search_nodes'] = unsat_cert['search_nodes']
        digest = sha256(json.dumps({k: v for k, v in output.items() if k != 'sha256'},
                                   sort_keys=True).encode('utf-8')).hexdigest()
        output['sha256'] = digest
        return output
    raise RuntimeError('No SAT/UNSAT pair survived candidate generation and checking')


def independently_verify_receipt(receipt: dict) -> bool:
    """Re-check a serialized finding without calling the synthesizer."""
    try:
        expected_digest = sha256(json.dumps({k: v for k, v in receipt.items() if k != 'sha256'},
                                           sort_keys=True).encode('utf-8')).hexdigest()
        if receipt.get('sha256') != expected_digest:
            return False
        n = receipt['n']
        sat = validate_cnf(n, receipt['sat_clauses'], True)
        unsat = validate_cnf(n, receipt['unsat_clauses'], True)
        if len(sat) != len(unsat) or len(sat) != receipt['m']:
            return False
        if len(set(canonical(sat))) != len(sat) or len(set(canonical(unsat))) != len(unsat):
            return False
        if not independent_pairwise_audit(n, sat, unsat):
            return False
        witness = receipt['sat_witness']
        if len(witness) != n or any(type(v) is not int or v not in (0, 1) for v in witness):
            return False
        assignment = {i + 1: bool(v) for i, v in enumerate(witness)}
        if not all(any((v > 0) == assignment[abs(v)] for v in cl) for cl in sat):
            return False
        if oracle(n, unsat) is not None:
            return False
        for kind, clauses in [('sat', sat), ('unsat', unsat)]:
            cert = receipt['certificates'][kind]
            if validate_cnf(n, cert['clauses'], True) != clauses:
                return False
            if cert['verdict'] != kind.upper() or not verify(cert):
                return False
        return True
    except (KeyError, ValueError, TypeError, RecursionError):
        return False


def main() -> None:
    parser = argparse.ArgumentParser(description='ASTRA MATH LAB Ω discovery CEGIS')
    parser.add_argument('--n', type=int, default=5)
    parser.add_argument('--output', default=None)
    args = parser.parse_args()
    finding = find_counterexample(args.n)
    assert independently_verify_receipt(finding)
    encoded = json.dumps(finding, indent=2, sort_keys=True, ensure_ascii=False) + '\n'
    if args.output:
        from pathlib import Path
        Path(args.output).write_text(encoded, encoding='utf-8')
    else:
        print(encoded)


if __name__ == '__main__':
    main()
