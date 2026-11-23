"""ASTRA MATH LAB Ω — exact SAT/UNSAT certificate producer and independent checker.

Research baseline only: exhaustive DPLL search can take exponential time.  The
checker verifies SAT witnesses or full UNSAT refutation trees; it does NOT
certify P=NP or P!=NP and makes no polynomial-time complexity claim.
"""
from __future__ import annotations

from hashlib import sha256
from itertools import product
import json


def validate_cnf(n: int, clauses, strict_3cnf: bool = False):
    if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= 12:
        raise ValueError('n must be an integer in [1,12]')
    result = []
    for clause in clauses:
        try:
            values = tuple(int(v) for v in clause)
        except (TypeError, ValueError) as e:
            raise ValueError('invalid clause') from e
        if not 1 <= len(values) <= 3 or (strict_3cnf and len(values) != 3):
            raise ValueError('clauses must contain 1..3 literals (exactly 3 in strict mode)')
        if any(v == 0 or abs(v) > n for v in values):
            raise ValueError('literal outside variable range')
        if len(set(map(abs, values))) != len(values):
            raise ValueError('clauses must use distinct variables')
        result.append(values)
    return tuple(result)


def satisfied(clause, assignment):
    return any((lit > 0) == assignment[abs(lit)] for lit in clause)


def conflict(clause, partial):
    return all(abs(lit) in partial and (lit > 0) != partial[abs(lit)] for lit in clause)


def oracle(n, clauses):
    """Independent truth-table oracle; exponential and small-domain only."""
    for values in product((False, True), repeat=n):
        assignment = {i + 1: v for i, v in enumerate(values)}
        if all(satisfied(cl, assignment) for cl in clauses):
            return assignment
    return None


def produce(n, clauses, strict_3cnf=False):
    """Return self-contained SAT witness or complete UNSAT branch certificate."""
    cnf = validate_cnf(n, clauses, strict_3cnf)
    nodes = 0

    def search(partial):
        nonlocal nodes
        nodes += 1
        for idx, cl in enumerate(cnf):
            if conflict(cl, partial):
                return None, {'conflict': idx}
        if all(any(abs(lit) in partial and (lit > 0) == partial[abs(lit)] for lit in cl) for cl in cnf):
            candidate = {i: bool(partial.get(i, False)) for i in range(1, n + 1)}
            return candidate, None
        var = next(i for i in range(1, n + 1) if i not in partial)
        partial[var] = False
        witness, left = search(partial)
        if witness is not None:
            del partial[var]
            return witness, None
        partial[var] = True
        witness, right = search(partial)
        del partial[var]
        if witness is not None:
            return witness, None
        return None, {'split': var, 'false': left, 'true': right}

    sat, proof = search({})
    return {
        'n': n, 'clauses': [list(cl) for cl in cnf],
        'verdict': 'SAT' if sat is not None else 'UNSAT',
        'witness': [int(sat[i]) for i in range(1, n + 1)] if sat is not None else None,
        'unsat_tree': proof, 'search_nodes': nodes,
        'complexity_warning': 'DPLL exponential worst-case; no Clay solution',
    }


def verify(cert):
    """Independent proof checker: no calls to the producer or SAT oracle."""
    try:
        n = cert['n']
        clauses = validate_cnf(n, cert['clauses'])
        if cert['verdict'] == 'SAT':
            values = cert['witness']
            if not isinstance(values, list) or len(values) != n or any(v not in (0, 1) or type(v) is not int for v in values):
                return False
            a = {i + 1: bool(v) for i, v in enumerate(values)}
            return cert['unsat_tree'] is None and all(satisfied(cl, a) for cl in clauses)
        if cert['verdict'] != 'UNSAT' or cert['witness'] is not None:
            return False
        visited = 0

        def check(node, partial):
            nonlocal visited
            visited += 1
            if visited > 16383 or not isinstance(node, dict):
                return False
            if set(node) == {'conflict'}:
                idx = node['conflict']
                return type(idx) is int and 0 <= idx < len(clauses) and conflict(clauses[idx], partial)
            if set(node) != {'split', 'false', 'true'}:
                return False
            var = node['split']
            if type(var) is not int or not 1 <= var <= n or var in partial:
                return False
            return (check(node['false'], {**partial, var: False}) and
                    check(node['true'], {**partial, var: True}))

        return check(cert['unsat_tree'], {})
    except (ValueError, KeyError, TypeError, RecursionError):
        return False


def example_gate():
    """Use the exact strict-3CNF SAT/UNSAT pair from ASTRA PR #17."""
    sat = [[1, 3, 2], [1, 3, 4]]
    unsat = [[s1 * 1, s2 * 2, s3 * 3] for s1, s2, s3 in product((-1, 1), repeat=3)]
    results = {}
    for label, clauses in [('sat', sat), ('unsat', unsat)]:
        cert = produce(4, clauses, strict_3cnf=True)
        exact_oracle = oracle(4, validate_cnf(4, clauses, True))
        assert verify(cert)
        assert (exact_oracle is not None) == (cert['verdict'] == 'SAT')
        results[label] = {
            'verdict': cert['verdict'],
            'checker': 'PASS',
            'oracle_agrees': True,
            'search_nodes': cert['search_nodes'],
            'certificate_sha256': sha256(json.dumps(cert, sort_keys=True).encode()).hexdigest(),
        }
    return {
        'experiment': 'PR17 strict 3CNF independent decision certificate gate',
        'results': results,
        'general_p_vs_np': 'UNVERIFIED',
        'award_eligible': False,
    }


if __name__ == '__main__':
    print(json.dumps(example_gate(), indent=2, ensure_ascii=False, sort_keys=True))
