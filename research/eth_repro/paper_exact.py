#!/usr/bin/env python3
"""Exact finite tests for *specific stated equations* in OpenAI's Oct-25 ETH paper.

Correspondence (NOT an implementation of the subexponential algorithm):
 - manuscript 'A direct polynomial for the count': Phi_e and #F identity;
 - 'A polynomial family with easier evaluation points': homogeneous, occurrence-
   specific replacement forms P_{e,v}(T), H(0)=#F and degree <= M R;
 - 'Separating the sum by fixing measurements': check (r,tau,D) design's
   cross-group row-space constraint and evaluate sum_y prod_g sum_u A_g;
 - 'Recovering the count from Taylor coefficients': exact rational Hermite
   reconstruction of H(0) from Taylor data at t=1,2.

Finite and small n only. The examples use a hand-designed measurement scheme,
NOT the paper's low-rank matrix, parity tests, nor asymptotic construction.
"""
from __future__ import annotations

import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
from typing import Sequence

Poly = tuple[Q, ...]
Form = tuple[Poly, ...]
CNF = tuple[tuple[int, ...], ...]
ZERO: Poly = (Q(0),)
ONE: Poly = (Q(1),)


def norm(p: Sequence[Q | int]) -> Poly:
    a = [Q(x) for x in p]
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return tuple(a) or ZERO


def plus(a: Poly, b: Poly) -> Poly:
    return norm([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(max(len(a), len(b)))])


def neg(a: Poly) -> Poly:
    return norm([-v for v in a])


def mul(a: Poly, b: Poly) -> Poly:
    p = [Q(0)] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            p[i+j] += ai * bj
    return norm(p)


def at(p: Poly, t: int | Q) -> Q:
    v = Q(0)
    for c in reversed(p):
        v = v * t + c
    return v


def taylor(p: Poly, t: int | Q, orders: int) -> Poly:
    """Coefficients of P(t+z) mod z^orders (no finite differences)."""
    return tuple(sum((p[k] * math.comb(k, j) * Q(t)**(k-j)
                      for k in range(j, len(p))), Q(0))
                 for j in range(orders))


def check_input(n: int, cnf: CNF):
    if n < 1 or any(abs(l) > n or l == 0 for c in cnf for l in c):
        raise ValueError('invalid CNF')


def brute(n: int, cnf: CNF) -> int:
    check_input(n, cnf)
    return sum(all(any(((mask >> (abs(l)-1)) & 1) == (l > 0)
                       for l in c) for c in cnf) for mask in range(1 << n))


def normalize_cnf(n: int, cnf: CNF) -> CNF:
    """Lean's SAT.CNF (Fin n) is a Finset of Finsets, not a list of duplicates."""
    check_input(n, cnf)
    return tuple(sorted({tuple(sorted(set(c))) for c in cnf}))


def encode_nat(n: int) -> list[bool]:
    return [True] * n + [False]


def frame(bits: list[bool]) -> list[bool]:
    out = [False]
    for b in reversed(bits):
        out = [True, b] + out
    return out


def encode_list(items: Sequence, encoder) -> list[bool]:
    out = [False]
    for a in reversed(items):
        out = [True] + frame(encoder(a)) + out
    return out


def lean_encode_cnf(n: int, cnf: CNF) -> list[bool]:
    """Python translation of ComparatorChallenges/SubexponentialSAT.lean encoding.

    literalCode = 2*Fin.val + (1 if positive else 0), sorts all levels.
    This tests the *input representation*, not machine execution.
    """
    canonical = normalize_cnf(n, cnf)
    rows = sorted([sorted(2*(abs(l)-1) + (1 if l > 0 else 0) for l in c)
                   for c in canonical])
    return encode_nat(n) + encode_list(rows, lambda row: encode_list(row, encode_nat))


@dataclass(frozen=True)
class Instance:
    n: int
    cnf: CNF
    # forms[e][literal_index][variable_index] is a rational polynomial
    forms: tuple[tuple[Form, ...], ...]
    degree_R: int

    def __post_init__(self):
        check_input(self.n, self.cnf)
        if len(self.forms) != len(self.cnf):
            raise ValueError('form count mismatch')
        for clause, clause_forms in zip(self.cnf, self.forms):
            if len(clause) != len(clause_forms):
                raise ValueError('occurrence mismatch')
            for lit, f in zip(clause, clause_forms):
                if len(f) != self.n:
                    raise ValueError('variable mismatch')
                if any(len(p)-1 > self.degree_R for p in f):
                    raise ValueError('degree bound violated')
                if any(at(p, 0) != int(v == abs(lit)-1) for v, p in enumerate(f)):
                    raise ValueError('P(0) must restore the original literal variable')

    @property
    def M(self):
        return sum(map(len, self.cnf))

    def degree_bound(self):
        return self.M * self.degree_R


def clause_poly(literals: Sequence[int], values: Sequence[Poly]) -> Poly:
    # Phi_e = 1 - product_occurrences(1 - literal_value).
    not_sat = ONE
    for lit, value in zip(literals, values):
        literal = value if lit > 0 else plus(ONE, neg(value))
        not_sat = mul(not_sat, plus(ONE, neg(literal)))
    return plus(ONE, neg(not_sat))


def H(i: Instance) -> Poly:
    result = ZERO
    for bits in itertools.product((0, 1), repeat=i.n):
        product = ONE
        for clause, ff in zip(i.cnf, i.forms):
            values = [norm(sum_form(f, bits)) for f in ff]
            product = mul(product, clause_poly(clause, values))
        result = plus(result, product)
    return result


def sum_form(form: Form, bits: Sequence[int]) -> Poly:
    r = ZERO
    for p, b in zip(form, bits):
        if b:
            r = plus(r, p)
    return r


def identity_instance(n: int, cnf: CNF) -> Instance:
    forms = []
    for clause in cnf:
        forms.append(tuple(tuple(ONE if v == abs(lit)-1 else ZERO
                                 for v in range(n)) for lit in clause))
    return Instance(n, cnf, tuple(forms), 0)


def cross_measurement_instance(n: int, cnf: CNF,
                               groups: tuple[tuple[int, ...], ...],
                               assigned: tuple[int, ...],
                               g: Poly = (Q(0), Q(3,2), Q(-1,2))) -> Instance:
    """Toy but paper-conformant: per-occurrence homogeneous forms.

    Each group has ONE measurement: sum of its Boolean variables.
    P_{e,v}(T) = x_v + g(T)*(sum_{j in other_group} x_j - x_v)
    for vars outside the clause's assigned group. g(0)=0; g(1)=g(2)=1.
    At 1 and 2, every off-group dependence is exactly one measurement.
    """
    if sorted(x for group in groups for x in group) != list(range(n)):
        raise ValueError('groups do not partition variables')
    if len(assigned) != len(cnf) or any(gid < 0 or gid >= len(groups) for gid in assigned):
        raise ValueError('bad assignments')
    if at(g,0) != 0 or at(g,1) != 1 or at(g,2) != 1:
        raise ValueError('g must interpolate 0->0 and 1,2->1')
    forms = []
    for clause, gid in zip(cnf, assigned):
        owner = set(groups[gid])
        clause_forms = []
        for lit in clause:
            v = abs(lit)-1
            other = next((set(xs) for xs in groups if v in xs), None)
            if other is None:
                raise ValueError('unknown variable')
            if v in owner:
                ff = tuple(ONE if j == v else ZERO for j in range(n))
            else:
                ff = tuple(plus(ONE if j == v else ZERO,
                                mul(g, norm([int(j in other)-int(j == v)])))
                           for j in range(n))
            clause_forms.append(ff)
        forms.append(tuple(clause_forms))
    return Instance(n, cnf, tuple(forms), len(g)-1)


def check_measurement_design(i: Instance, groups: tuple[tuple[int, ...], ...],
                             assigned: tuple[int, ...], t: int) -> dict:
    """Check paper (r,tau,D)-design Condition 4 EXACTLY for C_g=(1,...,1)."""
    if sorted(x for group in groups for x in group) != list(range(i.n)):
        raise ValueError('not a partition')
    if len(assigned) != len(i.cnf):
        raise ValueError('bad clause ownership')
    for clause_forms, gid in zip(i.forms, assigned):
        if gid not in range(len(groups)):
            raise ValueError('bad owner')
        for f in clause_forms:
            for h, xs in enumerate(groups):
                if h != gid and len({at(f[j],t) for j in xs}) > 1:
                    raise ValueError('off-group form outside measurement rowspace')
    return {'valid': True, 'rows': len(groups), 'D': max(map(len,groups)),
            'largest_group': max(map(len,groups))}


def separated_sum(i: Instance, groups: tuple[tuple[int, ...], ...],
                  assigned: tuple[int, ...], t: int) -> Q:
    """Exactly implement manuscript equation: sum_y prod_g sum_{u:C_g u=y_g} A_g.

    First verifies Condition 4, so no false factorization for invalid forms.
    """
    check_measurement_design(i, groups, assigned, t)
    overall = Q(0)
    for measurements in itertools.product(*(range(len(g)+1) for g in groups)):
        prod_g = Q(1)
        for gid, group in enumerate(groups):
            group_sum = Q(0)
            for values in itertools.product((0,1), repeat=len(group)):
                if sum(values) != measurements[gid]:
                    continue
                inside = dict(zip(group,values))
                contribution = Q(1)
                for clause, ff, owner in zip(i.cnf, i.forms, assigned):
                    if owner != gid:
                        continue
                    form_values = []
                    for f in ff:
                        val = sum((at(f[v],t)*b for v,b in inside.items()), Q(0))
                        for h, other in enumerate(groups):
                            if h != gid:
                                val += at(f[other[0]],t) * measurements[h]
                        form_values.append((val,))
                    contribution *= at(clause_poly(clause, form_values),0)
                group_sum += contribution
            prod_g *= group_sum
        overall += prod_g
    return overall


def linear_solve_unique(rows: list[list[Q]], rhs: list[Q], cols: int) -> list[Q]:
    """Exact rectangular rational solver, rejects inconsistent/missing-rank data."""
    if len(rows) != len(rhs):
        raise ValueError('bad linear system')
    a = [[Q(x) for x in row] + [Q(b)] for row,b in zip(rows,rhs)]
    pivot_row = 0
    pivots = []
    for col in range(cols):
        hit = next((r for r in range(pivot_row,len(a)) if a[r][col]), None)
        if hit is None:
            continue
        a[pivot_row], a[hit] = a[hit], a[pivot_row]
        div = a[pivot_row][col]
        a[pivot_row] = [z/div for z in a[pivot_row]]
        for r in range(len(a)):
            if r != pivot_row and a[r][col] != 0:
                factor = a[r][col]
                a[r] = [x-factor*y for x,y in zip(a[r],a[pivot_row])]
        pivots.append(col)
        pivot_row += 1
    if any(all(x == 0 for x in row[:-1]) and row[-1] for row in a):
        raise ValueError('inconsistent Taylor data')
    if len(pivots) != cols:
        raise ValueError('underdetermined Taylor data')
    out = [Q(0)] * cols
    for j,col in enumerate(pivots):
        out[col] = a[j][-1]
    return out


def reconstruct_from_taylor(degree_bound: int,
                            derivatives: list[tuple[int, tuple[Q, ...]]]) -> Poly:
    # H(t+z) = sum_i a_i (t+z)^i;
    # coefficient of z^j = sum_{i>=j} a_i binom(i,j) t^(i-j).
    rows, rhs = [], []
    for t, coeffs in derivatives:
        for j, val in enumerate(coeffs):
            rows.append([Q(math.comb(k,j))*Q(t)**(k-j) if k>=j else Q(0)
                         for k in range(degree_bound+1)])
            rhs.append(Q(val))
    return norm(linear_solve_unique(rows, rhs, degree_bound+1))


def hermite_reconstruct(i: Instance, points: tuple[int,...]=(1,2)) -> dict:
    h = H(i)
    bound = i.degree_bound()
    order = bound // len(points) + 1
    derivatives = [(t, taylor(h,t,order)) for t in points]
    recovered = reconstruct_from_taylor(bound, derivatives)
    return {'degree_bound': bound, 'actual_degree':len(h)-1,
            'points':list(points), 'coefficients_per_point': order,
            'H0':str(h[0]), 'H0_reconstructed':str(recovered[0]),
            'exact_polynomial_equal':h == recovered,
            'count':brute(i.n,i.cnf),
            'taylor_data':derivatives}


def finite_paper_audit(seed=20261101, trials=60):
    rng = random.Random(seed)
    example_cnf: CNF = ((1,3,4), (-1,2), (2,-3), (-2,4))
    groups=((0,1),(2,3)); owners=(0,0,1,1)
    ex = cross_measurement_instance(4,example_cnf,groups,owners)
    h = H(ex)
    r = hermite_reconstruct(ex)
    assertions=[]
    def ck(name, condition):
        assertions.append({'name':name,'status':'PASS' if condition else 'FAIL'})
    ck('paper_2.3_H0_equals_count', h[0]==brute(ex.n,ex.cnf))
    ck('paper_2.4_degree_bound',len(h)-1<=ex.degree_bound())
    for t in [1,2]:
        ck(f'paper_2.5_valid_design_{t}',check_measurement_design(ex,groups,owners,t)['valid'])
        ck(f'paper_2.5_separated_H_at_{t}',separated_sum(ex,groups,owners,t)==at(h,t))
    ck('paper_2.6_exact_Hermite_recovery',r['exact_polynomial_equal'] and
       Q(r['H0_reconstructed'])==brute(ex.n,ex.cnf))
    # Controls: a false design must be rejected; corrupted Taylor data must fail.
    try:
        check_measurement_design(ex,groups,owners,0)
        control_bad_design=False
    except ValueError:
        control_bad_design=True
    ck('negative_invalid_measurement_design_rejected',control_bad_design)
    d=r['taylor_data'].copy()
    d[0]=(d[0][0],(d[0][1][0]+1,*d[0][1][1:]))
    try:
        bad=reconstruct_from_taylor(r['degree_bound'],d)
        control_bad_taylor = bad!=h
    except ValueError:
        control_bad_taylor=True
    ck('negative_corrupted_Hermite_data_rejected',control_bad_taylor)
    ck('canonical_Lean_set_duplicates_preserve_count',
       brute(4,example_cnf)==brute(4,example_cnf+(example_cnf[0],)))
    # Many structurally different CNF counts and homogeneous replacement forms.
    for trial in range(trials):
        n=rng.randint(1,4)
        cnf: CNF=tuple(tuple(rng.choice((-1,1))*rng.randint(1,n)
                             for _ in range(rng.randint(0,3)))
                       for _ in range(rng.randint(0,4)))
        ident=identity_instance(n,cnf)
        chk=(H(ident)[0]==brute(n,cnf))
        ck(f'paper_2.3_random_case_{trial}',chk)
        ck(f'lean_canonical_encoding_case_{trial}',
           isinstance(lean_encode_cnf(n,cnf),list) and
           len(lean_encode_cnf(n,cnf))>n)
    result={'schema':'astra-math-lab-paper/2',
            'status':'PASS' if all(a['status']=='PASS' for a in assertions) else 'FAIL',
            'checks':len(assertions), 'failures':[a for a in assertions if a['status']=='FAIL'],
            'seed':seed, 'trials':trials,
            'example_cnf':example_cnf,
            'example_H_coefficients':[str(x) for x in h],
            'paper_sources':[
              'https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex',
              'https://github.com/openai/math/blob/main/lean/ComparatorChallenges/SubexponentialSAT.lean',
              'https://github.com/openai/math/blob/main/lean/docs/378.md'],
            'hermite':{k:v for k,v in r.items() if k!='taylor_data'},
            'lean_kernel_check':'NOT_RUN_BY_PYTHON (separate public GitHub Lean job)',
            'official_openai_proof_replay':'NOT_RUN',
            'asymptotic_claim':'NOT_TESTED'}
    return result


if __name__=='__main__':
    path=Path(__file__).parent/'paper_report.json'
    report=finite_paper_audit()
    path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(report,ensure_ascii=False,indent=2))
    raise SystemExit(0 if report['status']=='PASS' else 1)