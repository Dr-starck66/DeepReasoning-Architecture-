# ASTRA ProofLab Ω — Buyer-facing reproducibility case study (2026-11-01)

> **Internal research demonstrator, NOT a customer-paid audit or a third-party certification.** The work reproduces finite constructions from publicly available mathematical research; it does NOT prove the global asymptotic theorem or confer exclusivity over published mathematics.

## Business problem
AI and research companies need a defensible answer to: **Does the exact code, formal statement and test receipt support the specific claim shown to a buyer?** A successful GitHub CI build alone is not a scientific guarantee.

## Live evidence
- [ASTRA ProofLab browser checker](https://astra-prooflab-6jyfg1.v2.appdeploy.ai/)
- [Source and finite Lean theorems](https://github.com/Dr-starck66/DeepReasoning-Architecture-/pull/11)
- [Verified public Lean CI run 41289478387](https://github.com/Dr-starck66/DeepReasoning-Architecture-/actions/runs/41289478387), commit `5f0521ad8e2a127ba9f147372ddd73fa78757d3d`, workflow “ASTRA MATH LAB - Lean 4 formal check”, **completed / success** (GitHub API checked).
- [Primary OpenAI manuscript, §4](https://github.com/openai/math/blob/main/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex)

## What we reproduced, exactly
| Check | Method | Actual observation | Status |
|---|---|---|---|
| Small finite swap-matrix model | integer/rational Python arithmetic | 64×64; rank(I−M0)=10; rank(M0)=64 | **PASS (finite)** |
| Measurement rows | exact rational elimination | 10 distinct rows; rank 10 | **PASS (finite)** |
| Polynomial localization | JavaScript browser-demo harness executed under Node.js | 6,144 expected off-group coefficient equalities | **PASS (finite)** |
| All unit tests | `python -m unittest discover -s research/eth_repro -p 'test_*.py' -v` | **28/28 tests, 0 failures**, re-executed 2026-11-01 | **PASS (local)** |
| Independent randomized deterministic corpus | `python research/eth_repro/eth_lab.py --cases 80 --seed 20261101 --nmax 7` | **80 cases, 496 checks, zero failures**, corpus SHA-256 `7dbc1604ac72a2738fba4788fe9ec6e57b0b4cbc42a8d503636fc3545f52429e` | **PASS (local)** |
| Negative controls | corrupt matrix term / measurement and deliberately wrong Boolean/interpolation operation | intentional wrong answers flagged by tests | **PASS (detection)** |
| Public formal CI | GitHub Actions on exact immutable commit | completed/success, Lean 4 tested | **PASS (narrow CI)** |
| Paper's global subexponential theorem | not independently formalized by ASTRA | no bound established | **UNVERIFIED** |

### Reliability fix caught during buyer-pack QA
The earlier copy of `demo/check-demo.js` used a hard-coded temporary path `/mnt/data/astra-math-lowrank/demo.js`, which caused a **real failure** on a clean extracted ZIP. We extracted the inline demo source to a local peer `demo.js` and corrected the harness to resolve files relative to `__dirname`; the local test then passed and printed 6,144 locality comparisons. The repository now contains a self-contained `demo.js` and portable `check-demo.js`. This fix is **staged in the PR branch**; a public product redeployment was not verified.

## Commercial offer
**Evidence Audit Sprint, indicative €2,900 excluding applicable taxes**. On **one selected customer repository/commit**, up to five written claims, a CI workflow and five Lean files where applicable: deliver source/version ledger, formal-proof scope, negative controls, JSON report, executive review, and reproducible commands. Delivery target five working days after agreement and all accessible inputs. Need written buyer approval and confirmed legal invoice entity; **no customer contract or payment currently demonstrated**.

**Procurement request:** project URL, claims to verify, technical and budget owner, country and contracting entity. No need to upload private code to the public browser demo.

## State of claims
- Tests: PASS for explicitly tested *finite* properties.
- Deployment: prior public AppDeploy status **ready**; current QA against GitHub live API is distinct from automated local tests.
- Commercial demand, orders and valuation: **UNVERIFIED**.
- Asset status: reusable verification workflow + original implementation and associated report templates, not exclusive ownership of the public manuscript.

This document is designed for a prospective buyer to question and verify. Negative and limiting evidence are intentionally retained.
