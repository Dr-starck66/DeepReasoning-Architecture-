# ASTRA TOPOQUANTUM Ω — Majorana/Kitaev → existing ProofGate

**Scope:** exact finite, open-boundary Kitaev-chain Bogoliubov–de Gennes (BdG) model, with rational coefficients. No hardware, no API keys, no new dependencies, no deployment or monetary cost.

The original October 2026 `topoquantum-v2.1-laboratoire-reproductible.zip` was mentioned in prior work but **was not available in this session**. The recovered Library artifact is a V2 HTML/JavaScript landing page, not an authenticated complete solver source. This module therefore implements *independent, disclosed checks*; it does **not** claim byte-for-byte reuse of that lost archive.

## Conventions

Nambu basis `(c_0,…,c_{N-1},c†_0,…,c†_{N-1})`, with real `t,delta,mu`:

`H_BdG = [[h,Delta],[-Delta,-h]]`, where `h[i,i]=-mu`, `h[i,i+1]=-t`, `Delta[i,i+1]=delta`, `Delta[i+1,i]=-delta`. Open chain unless explicitly periodic.

At `mu=0`, `delta=t=1`, for every finite `N` tested:

- The exact null vectors are `L=(e_0,-e_0)` and `R=(e_{N-1},e_{N-1})`.
- Exact rational row elimination gives `rank(H)=2N-2`, hence nullity 2.
- An independent entrywise calculation checks `H³=4H`, Hermiticity, and particle-hole symmetry.
- Negative controls reject 2 exact open-edge zero modes for the test trivial chemical potential, an N=4 periodic chain, and a perturbed pairing coefficient.

These are **finite calculations**, not proofs for arbitrary N or experimental Majorana states. The ideal sweet spot is special; small numerical energies in other finite chains do not by themselves establish topological protection.

## Integration and reproducibility

From a checkout of the existing `Dr-starck66/DeepReasoning-Architecture-` **PR #13 branch**, use:

```bash
python3 -m unittest discover -s research/eth_repro/topoquantum -p 'test_*.py' -v
python3 research/eth_repro/topoquantum/gate_bridge.py --out /tmp/astra-topoquantum-proofgate
python3 research/eth_repro/proof_gate.py /tmp/astra-topoquantum-proofgate/proofgate_manifest.json --output /tmp/astra-topoquantum-proofgate/proofgate_audit.json
```

The bridge deliberately reuses `research/eth_repro/proof_gate.py`, which checks SHA-256, source binding and independent GitHub Actions results. The generated manifest contains **no CI evidence**; ProofGate must return `UNVERIFIED`, even when the local exact computations `PASS`. The accompanying `TopoQuantumFinite.lean` offers finite N=2 theorems with no `sorry`/`axiom` but its Lean kernel acceptance requires an actual Lean compilation (Lean is not available in the local temporary runtime).

Formal scope of the Lean file: explicit 4×4 Hermitian BdG, two kernel vectors and their independence, **not** a general Kitaev-chain invariant. No background service, no physical discovery, no sale claims.

## Scientific verdicts

| Assertion | Status |
|---|---|
| Tests of the exact finite toy model | PASS only with real test output |
| Formal Lean file syntactic acceptance | UNVERIFIED until compiled |
| Existing ProofGate integration | PASS only after executing the real code; claims nevertheless UNVERIFIED without CI |
| General N formal result / physical Majorana detection | UNVERIFIED |
| Zero-cost standalone deliverable | PASS after local ZIP/hash verification |