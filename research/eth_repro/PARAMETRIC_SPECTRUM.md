# ASTRA PARAMETRIC SPECTRUM Ω — hypothesis and falsification programme

**Scope:** extension of the previously kernel-checked *single* q=3,
64×64 rational rank theorem in ASTRA PR #15. No patent, new asymptotic
lower bound, quantum computing advantage or claim of mathematical novelty.

## Family to be tested

For integer q >= 1, index the standard basis of Q^(4^q) by pairs of
q-bit strings (a,d). Let S_i swap their i-th bits, for 0 <= i < q.
The S_i commute and satisfy S_i^2=I. Define:

    P = S_0 S_1 ... S_(q-1)
    M_q = Σ_{j=0}^{q-1} (Π_{i != j} S_i) - (q-1) P
    A_q = I - M_q.

Each local swap on Q^4 has three independent eigenvectors for +1 and
one for −1 (integer basis determinant −2). Taking q-fold tensor
products yields 4^q independent vectors over Q.

A vector with exactly k local −1 eigenvalues satisfies:

    eigen(M_q) = (−1)^k * (1 − 2k)
    eigen(A_q) = 1 − (−1)^k * (1 − 2k)
              = 2k, for k even
              = 2−2k, for k odd

The latter vanishes **only** for k=0 or k=1. The multiplicity of k
negative swaps is binomial(q,k) * 3^(q−k). Thus, conditional on the
tensor basis proof, a proposed *uniform exact rank formula* is:

    rank_Q(A_q) = Σ_{k=2}^q binomial(q,k) 3^(q−k)
                = 4^q − 3^q − q 3^(q−1).

For q=3 this evaluates to 10 and matches the rank in PR #15.

## New negative scientific finding

This is **not** a uniformly low-rank family as q increases. The fraction
of null modes is

    nullity(A_q)/4^q = (1 + q/3) * (3/4)^q,

which tends to zero, while the rank fraction tends to **one**.
In particular, a finite 64×64 rank-10 example does **not** justify
claims of asymptotically low rank, general ETH speedups, or scalability.
This is an important falsification of an overbroad interpretation.

| q | dimension | proposed rank | rank fraction |
|---|---:|---:|---:|
| 1 | 4 | 0 | 0% |
| 2 | 16 | 1 | 6.25% |
| 3 | 64 | 10 | 15.625% |
| 4 | 256 | 67 | 26.171875% |
| 5 | 1024 | 376 | 36.71875% |
| 6 | 4096 | 1909 | ~46.61% |
| 10 | 1048576 | 792697 | ~75.60% |

## Verification and controls

From the repository root:

    python3 -m unittest discover -s research/eth_repro -p 'test_parametric_spectrum.py' -v
    python3 research/eth_repro/parametric_spectrum.py --output /tmp/astra_parametric.json
    lean research/eth_repro/ParametricSpectrum.lean

Use the existing .github/workflows/astra-spectral.yml (no duplicated CI).
Tests:
- q=1..4: all 4^q tensor eigenvectors and all 16^q row equations,
  via a sparse application **independent** of full matrix construction.
- q=1..4: exact modular Gaussian rank over F_101 and F_103,
  an independent lower-bound consistency check over Q.
- q=3: all 4096 entries compared with the pre-existing ASTRA M0.
- q=5: **sampled** sparse eigenvectors only, clearly NOT exhaustive.
- q=1..12: exact integer arithmetic equality of two separately coded
  versions of the proposed combinatorial rank formula.
- Three deliberate counterfactuals: perturb one matrix coefficient,
  invent an incorrect eigenvalue, and change the claimed q=4 rank
  from 67 to 66; all should be rejected.

## Formal proof frontier

ParametricSpectrum.lean proves the **arbitrary-k** eigenvalue
zero characterization and finite spectral counts for q=1..4. This is
**not yet a parameter-uniform Lean proof of Matrix.rank A_q**.
The missing formal object is the q-fold invertible tensor basis together
with the verified statement A_q B_q = B_q diag(eigen(A_q)) for all
q, and a Mathlib binomial count. The original q=3 Mathlib proof remains
validated and unchanged on the ancestor PR #15.

Do not label a uniform result PASS solely because finite tests agree.
Scientific originality and patentability: UNVERIFIED.
