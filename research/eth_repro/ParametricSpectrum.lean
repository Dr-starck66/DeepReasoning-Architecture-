import Lean
/-!
ASTRA Ω — parameter-dependent spectral bookkeeping.

For each integer q ≥ 1, the tensor-product swap basis has 4^q labels:
three local eigenvectors with swap sign +1 and one with sign −1.
This file formally verifies that the *candidate* eigenvalue of A_q for k
negative factors is zero exactly at k=0 and k=1, and independently checks
the spectral multiplicity count through q=4.

These statements do not yet instantiate a Mathlib Matrix.rank theorem
for ALL q. That requires a parameter-uniform, invertible tensor-product
change of basis and the identity A_q B_q = B_q Λ_q.
No sorry, no added axioms, no claims of novel mathematics.
-/

namespace AstraMath.ParametricSpectrum

/-- Tensor-product swap sign for k antisymmetric factors. -/
def sign (k : Nat) : Int :=
  if k % 2 = 0 then 1 else -1

/-- Eigenvalue candidate for M_q, obtained from the commuting swap polynomial. -/
def mEigen (k : Nat) : Int :=
  sign k * (1 - 2 * (k : Int))

/-- Eigenvalue candidate for A_q = I − M_q. -/
def aEigen (k : Nat) : Int :=
  1 - mEigen k

theorem aEigen_piecewise (k : Nat) :
    aEigen k =
      if k % 2 = 0 then 2 * (k : Int) else 2 - 2 * (k : Int) := by
  unfold aEigen mEigen sign
  by_cases h : k % 2 = 0
  · simp only [if_pos h]
    omega
  · simp only [if_neg h]
    omega

/-- A zero mode occurs at k=0 or k=1, never at larger k. -/
theorem zero_iff (k : Nat) :
    aEigen k = 0 ↔ k = 0 ∨ k = 1 := by
  rw [aEigen_piecewise]
  by_cases h : k % 2 = 0
  · simp only [if_pos h]
    omega
  · simp only [if_neg h]
    omega

theorem nonzero_iff_two_le (k : Nat) :
    aEigen k ≠ 0 ↔ 2 ≤ k := by
  rw [ne_eq, zero_iff]
  omega

/-- Count the number of antisymmetric factors in an encoded tensor label. -/
def negatives (q c : Nat) : Nat :=
  ((List.range q).filter (fun i => c / 4^i % 4 = 3)).length

/-- Spectrum multiplicity as a finite, executable count. -/
def countedRank (q : Nat) : Nat :=
  ((List.range (4^q)).filter (fun c =>
    decide (aEigen (negatives q c) ≠ 0))).length

theorem q1_count : countedRank 1 = 0 := by decide
theorem q2_count : countedRank 2 = 1 := by decide
theorem q3_count : countedRank 3 = 10 := by decide
theorem q4_count : countedRank 4 = 67 := by decide

#print axioms aEigen_piecewise
#print axioms zero_iff
#print axioms nonzero_iff_two_le
#print axioms q1_count
#print axioms q2_count
#print axioms q3_count
#print axioms q4_count

end AstraMath.ParametricSpectrum
