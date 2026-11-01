# ASTRA MATH LAB Ω — Swap-matrix low-rank reconstruction
**Version:** 2026-11-01 · **Source proof status:** `PASS` for enumerated, isolated properties only · **Global theorem:** `UNVERIFIED`.

## Exact source correspondence

Primary: [OpenAI, *The Exponential Time Hypothesis is False*, revised 25 Oct 2026, §4](https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex), blob `f7af85e623b58e0ca9f4b9416916d442defa963a` when inspected. No proof that ASTRA's program implements OpenAI's subexponential algorithm follows from these tests.

With group label \(u=(a_u,d_u)\in([r]^Q)^2\), \(D=r^{2Q}\), each \(\Pi_s\) swaps \(a(s),d(s)\). The manuscript defines

- \(V_0=\prod_s\Pi_s\), \(W_0=\frac12\sum_s(I-\Pi_s)\).
- \(f_\mathcal I(z)=(-1)^{A_0}\sum_{j=0}^{R-1}(-2)^j\binom{z-A_0}{j}\).
- \(M_0=V_0f_\mathcal I(W_0)\).
- \(C^{\mathcal B}\) collects orthogonal eigenvectors with \(j\notin\mathcal I\). Its row bound is \(D\Pr[\mathrm{Bin}(Q,(r-1)/(2r))\notin\mathcal I]\).
- \(E_{u,y}=\{s:a_y(s)\neq d_u(s)\}\); \(\phi_{u,y}(T)=\prod_{s\in E}(1-T/s)\).
- \(P_u(T)=\delta_u(I-M_0)+\sum_yM_0[u,y]\phi_{u,y}(T)\delta_y\).

For the **valid matrix stage** parameters \((r,Q,R,A_0)=(2,3,2,0)\), \(\mathcal I=\{0,1\}\), the interpolation polynomial simplifies to \(f(z)=1-2z\). Consequently \(M_0=\Pi_2\Pi_3+\Pi_1\Pi_3+\Pi_1\Pi_2-2\Pi_1\Pi_2\Pi_3\), with no approximation. The full matrix has 64 rows and columns. All \(64^2\) entries and all \(3\times64^2\) locality relationships are computed exactly in Python using integer and rational arithmetic.

**Independent audit results:**

| Property | Expected | Measured | Method |
|---|---:|---:|---|
| \(D=r^{2Q}\) | 64 | 64 | exact generation |
| \(c_\mathcal B\) | \(\binom32 3+\binom33=10\) | 10 | tensor eigenvectors |
| \(\mathrm{rank}(C)\) | 10 | 10 | rational Gaussian elimination |
| \(\mathrm{rank}(I-M_0)\) | ≤10 | **10** | *independent* rational elimination |
| \(\mathrm{rank}(M_0)\) | not required low | **64** | rational elimination |
| \(\Pr(W\notin \mathcal I)\) | 5/32 | 5/32 | exact binomial arithmetic |
| Support | mismatch ≤1 | PASS | full nonzero enumeration |
| \(P_u(0)=\delta_u\) | equality | PASS | full exact enumeration |
| All \(t\in\{1,2,3\}\) | off-group coefficients derived from \(C\) | PASS | exact eigenvector factorization |

**Crucial distinction:** The low-rank matrix is **\(I-M_0\)**, not \(M_0\). Presenting the full-rank \(M_0\) as a low-rank approximation is mathematically wrong.

### Literal manuscript example
The §4 remark uses \(Q=R=2\), explicitly **outside** the asymptotic parameter regime \(R<Q\). The four-coordinate orbit is reproduced, not just numerically fitted:
\[
\langle P_{(00,11)}(T),\zeta\rangle=\zeta_0-\frac{T}{2}\zeta_1-T\zeta_2,\quad
 c(\zeta)=\zeta_0-\zeta_1-\zeta_2+\zeta_{12}.
\]
\(I-M_0=cc^{\mathsf T}\) on this orbit; rank exactly one. Lean verifies its entrywise identity and both measurement-dependence equations. The 64×64 proof checks swap commutation/support in Lean and full rank plus measurement row-space in Python.

### Test execution and controls
- `python -m unittest discover -s research/eth_repro -p 'test_*.py' -v` on GitHub: **28 tests, 0 failures**, including two matrix corruption controls.
- `lean research/eth_repro/PaperFinite.lean` and `lean research/eth_repro/LowRankExact.lean`: **PASS** via GitHub Actions run [41289001101](https://github.com/Dr-starck66/DeepReasoning-Architecture-/actions/runs/41289001101), head SHA `4497d36ff8faca8c747d26111c6526b12aaca8aa`.
- `#print axioms`: `q3_matrix_support` uses only `propext`, measurement localizations use the usual Lean `propext` and `Quot.sound`. No `sorryAx` is reported in successful CI logs.
- Separately, the browser demo recomputes the matrix and checks **6,144** off-group coefficient equalities. Browser numerical rank uses floating elimination for visualization only; the Python ranks are exact.

## What is missing from a proof of asymptotic acceleration
The paper uses parameters \(r\asymp\sqrt\lambda/\nu^2\), \(Q\asymp\lambda/\nu\), \(R\asymp\sqrt\lambda\), \(\tau\asymp1/(r\lambda)\), where \(\lambda=\lceil\log_2n\rceil\), \(\nu=\lceil\log_2\lambda\rceil\). It needs an **all-size** spectral rank/tail inequality, efficient deterministic variable/factor label selection, the transition from auxiliary coordinates to actual factor occurrences, bounded integer coefficient growth, sparsification, low-degree polynomial zero counting and a time/space accounting (including tensor contraction for the sharper bound).

This repository has **not** produced Lean proofs of those global lemmas. In particular, a 64-dimensional instance proves no \(2^{o(n)}\) bound, no complexity separation, and no usable speedup over state-of-the-art SAT solvers. The *official* scope note states a weaker exponent than the paper's sharp bounds: [lean/docs/378.md](https://github.com/openai/math/blob/main/lean/docs/378.md).

**Commercial caveat:** The underlying mathematical statements are publicly available from OpenAI; independently confirm the repo's Apache 2.0 notice and any asset-specific licensing before redistribution. No claim of exclusive ownership over these public constructions, novel ETH theorem, customers, patents, revenue, or independently established $1M valuation is made.