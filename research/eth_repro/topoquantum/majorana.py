"""Exact, dependency-free finite Kitaev-chain checks (not an experimental detector).

Nambu basis (c_0,...,c_(N-1), c†_0,...,c†_(N-1));
real antisymmetric p-wave pairing with Δ_{j,j+1}=+delta.
H_BdG = [[h, Δ],[-Δ,-h]], h = -mu*I - t*adjacency.

Parameters and all operations use fractions.Fraction; no floating point.
"""
from __future__ import annotations
from fractions import Fraction
import hashlib
import json


def _q(x):
    return x if isinstance(x, Fraction) else Fraction(x)


def bdg(n: int, t=1, delta=1, mu=0, periodic=False):
    if not isinstance(n, int) or isinstance(n, bool) or n < 2 or n > 24:
        raise ValueError('2 <= integer n <= 24 required')
    if periodic and n < 3:
        raise ValueError('periodic chain requires n >= 3')
    t, delta, mu = map(_q, (t, delta, mu))
    h = [[-mu if i == j else Fraction(0) for j in range(n)] for i in range(n)]
    p = [[Fraction(0) for _ in range(n)] for _ in range(n)]
    links = [(j, j + 1) for j in range(n - 1)]
    if periodic:
        links.append((n - 1, 0))
    for a, b in links:
        h[a][b] -= t
        h[b][a] -= t
        p[a][b] += delta
        p[b][a] -= delta
    m = [[Fraction(0) for _ in range(2*n)] for _ in range(2*n)]
    for i in range(n):
        for j in range(n):
            m[i][j] = h[i][j]
            m[i][j+n] = p[i][j]
            m[i+n][j] = -p[i][j]
            m[i+n][j+n] = -h[i][j]
    return tuple(tuple(r) for r in m)


def multiply(a, b):
    if not a or not b or len(a[0]) != len(b):
        raise ValueError('incompatible shapes')
    out = []
    for row in a:
        out.append(tuple(sum(row[k]*b[k][j] for k in range(len(b))) for j in range(len(b[0]))))
    return tuple(out)


def rank_exact(a):
    if not a:
        return 0
    m = [list(map(_q, r)) for r in a]
    cols = len(m[0]); r = 0
    if any(len(row) != cols for row in m):
        raise ValueError('jagged matrix')
    for c in range(cols):
        p = next((k for k in range(r, len(m)) if m[k][c]), None)
        if p is None:
            continue
        m[r], m[p] = m[p], m[r]
        inv = 1/m[r][c]
        m[r] = [x*inv for x in m[r]]
        for i in range(r+1, len(m)):
            if m[i][c]:
                v=m[i][c]
                for j in range(c, cols):
                    m[i][j] -= v*m[r][j]
        r += 1
        if r == len(m):
            break
    return r


def edge_modes(n):
    """Exact independent left/right BdG null vectors at mu=0, delta=t."""
    left = [Fraction(0)]*(2*n)
    left[0] = 1; left[n] = -1
    right = [Fraction(0)]*(2*n)
    right[n-1] = 1; right[2*n-1] = 1
    return tuple(left), tuple(right)


def apply(a, v):
    if len(a[0]) != len(v):
        raise ValueError('incompatible shapes')
    return tuple(sum(x*y for x,y in zip(row, v)) for row in a)


def zero(v):
    return all(x == 0 for x in v)


def particle_hole(a):
    """Check tau_x H* tau_x == -H (all matrices here are real)."""
    n=len(a)//2
    return all(a[(i+n)%(2*n)][(j+n)%(2*n)] == -a[i][j]
               for i in range(2*n) for j in range(2*n))


def symmetric(a):
    return all(a[i][j] == a[j][i] for i in range(len(a)) for j in range(len(a)))


def matrix_hash(a):
    payload=[[str(v) for v in row] for row in a]
    return hashlib.sha256(json.dumps(payload,separators=(',', ':'),ensure_ascii=True).encode()).hexdigest()


def assess(sizes=(2,3,4,5,6,7,8)):
    rows=[]
    for n in sizes:
        h=bdg(n)
        l,r=edge_modes(n)
        h2=multiply(h,h)
        h3=multiply(h2,h)
        spectral_identity = all(h3[i][j] == 4*h[i][j] for i in range(2*n) for j in range(2*n))
        row={
            'n':n, 'dimension':2*n, 'exact_rank':rank_exact(h),
            'exact_nullity':2*n-rank_exact(h),
            'left_edge_residual_zero':zero(apply(h,l)),
            'right_edge_residual_zero':zero(apply(h,r)),
            'symmetric':symmetric(h),
            'particle_hole_symmetry':particle_hole(h),
            'exact_cubic_identity_H3_eq_4H':spectral_identity,
            'matrix_sha256':matrix_hash(h),
        }
        row['status']='PASS' if (row['exact_nullity']==2 and all(row[k] for k in (
            'left_edge_residual_zero','right_edge_residual_zero','symmetric',
            'particle_hole_symmetry','exact_cubic_identity_H3_eq_4H'))) else 'FAIL'
        rows.append(row)
    # A false claim "every chain has two zero modes" must be rejected.
    trivial=bdg(4, t=1,delta=1,mu=5)
    closed=bdg(4, t=1,delta=1,mu=0,periodic=True)
    negative={
        'trivial_open_chain_mu5_rejects_two_exact_zeros':rank_exact(trivial)==8,
        'periodic_chain_rejects_two_open_end_modes':rank_exact(closed)==8,
        'perturbed_delta_breaks_sweet_spot_edge_null_vector':not zero(apply(bdg(4,t=1,delta=Fraction(1,2),mu=0),edge_modes(4)[0])),
    }
    status='PASS' if all(row['status']=='PASS' for row in rows) and all(negative.values()) else 'FAIL'
    return {
        'schema':'astra-topoquantum-finite/1',
        'scope':'exact finite BdG model, real parameters, open boundary, t=delta=1 mu=0; NOT a physical Majorana discovery',
        'parameters':{'t':'1','delta':'1','mu':'0','boundary':'open'},
        'tested_sizes':rows,
        'negative_controls':negative,
        'finite_computation_status':status,
        'formal_lean_compilation':'UNVERIFIED',
        'experimental_majorana_identification':'UNVERIFIED',
        'persistent_service':'UNVERIFIED',
    }
