"""Constructive no-go lemma for signed-literal-count-only SAT classifiers.

The result is a logical consequence of TWO concrete strict-3CNF instances,
not a complexity lower bound for SAT or all polynomial-time algorithms.
"""
import json
from sat_certificate import oracle, produce, validate_cnf, verify

N = 5
UNSAT = [
    [-1,-2,-3],[-1,-2,3],[-1,2,-3],[-1,2,3],
    [-2,1,-3],[-2,1,3],[1,2,-3],[1,2,3],
    [3,4,-2],[-5,-2,-3],[4,-3,-5],[-3,2,-4],[1,3,-4],
]
SAT = [
    [2,-3,4],[1,3,-5],[2,-3,-4],[-1,-2,3],
    [-2,-3,-5],[1,-2,3],[-1,2,-3],[1,2,3],
    [-2,3,4],[1,-2,-3],[-1,-2,-3],[1,2,-3],[-1,3,-4],
]


def signed_incidence(n, clauses):
    cl = validate_cnf(n, clauses, strict_3cnf=True)
    return (n, len(cl), tuple((sum(v in c for c in cl), sum(-v in c for c in cl))
                              for v in range(1, n+1)))


def proof():
    f = validate_cnf(N, UNSAT, strict_3cnf=True)
    g = validate_cnf(N, SAT, strict_3cnf=True)
    assert len(set(tuple(sorted(c, key=abs)) for c in f)) == len(f)
    assert len(set(tuple(sorted(c, key=abs)) for c in g)) == len(g)
    feature = signed_incidence(N, f)
    assert feature == signed_incidence(N, g)
    cert_unsat, cert_sat = produce(N, f, True), produce(N, g, True)
    assert cert_unsat['verdict'] == 'UNSAT' and cert_sat['verdict'] == 'SAT'
    assert verify(cert_unsat) and verify(cert_sat)
    assert oracle(N, f) is None and oracle(N, g) is not None
    return {
        'claim': 'No universal SAT/UNSAT classifier that depends only on n, m and per-variable positive/negative literal counts',
        'logic': 'identical input features but opposite correct labels',
        'strict_3cnf_unique_clauses': True,
        'n': N, 'm': len(f), 'feature_positive_negative': feature[2],
        'unsat_certificate_verified': True,
        'sat_certificate_verified': True,
        'independent_truth_table_verified': True,
        'scope': 'CONSTRUCTIVE_NO_GO_FOR_THIS_RESTRICTED_FEATURE_CLASS_ONLY',
        'general_p_vs_np': 'UNVERIFIED', 'prize_eligible': False,
    }

if __name__ == '__main__':
    print(json.dumps(proof(), indent=2, sort_keys=True))
