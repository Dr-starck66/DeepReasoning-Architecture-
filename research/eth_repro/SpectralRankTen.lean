import Lean
/-!
ASTRA Ω — formal, exact finite spectral rank-10 certificate (Lean 4 core).

The object is the *specific* 64×64 integer matrix A=I−M0 of the
Q=3, R=2, r=2 swap model. A factorization through 10 columns and
a scaled left inverse are verified with decidable finite integer
arithmetic, so the factorization has **exactly** 10 independent modes
over ℚ. This file does NOT use a Mathlib Matrix.rank expression:
the rank conclusion is recorded as an explicit full-rank factorization
certificate, with no unproved axioms and no experimental claim.

Run: lean research/eth_repro/SpectralRankTen.lean
-/
set_option maxRecDepth 32768
set_option maxHeartbeats 0

namespace AstraMath.SpectralRankTen

private def sumN (n : Nat) (f : Nat → Int) : Int :=
  (List.range n).foldl (fun acc k => acc + f k) 0

private def pairCoordinate (i axis : Nat) : Nat :=
  ((i / (2 ^ axis)) % 2) + 2 * ((i / (2 ^ (axis + 3))) % 2)

/-- One pair's four integer eigenvectors: two fixed points, a symmetric
    and an antisymmetric combination of the swapped points. -/
def basis1 (kind coord : Nat) : Int :=
  if kind = 0 ∧ coord = 0 then 1
  else if kind = 1 ∧ coord = 3 then 1
  else if kind = 2 ∧ (coord = 1 ∨ coord = 2) then 1
  else if kind = 3 ∧ coord = 1 then 1
  else if kind = 3 ∧ coord = 2 then -1
  else 0

/-- Twice the coefficients of the dual basis for one pair. -/
def dual2 (kind coord : Nat) : Int :=
  if kind = 0 ∧ coord = 0 then 2
  else if kind = 1 ∧ coord = 3 then 2
  else if kind = 2 ∧ (coord = 1 ∨ coord = 2) then 1
  else if kind = 3 ∧ coord = 1 then 1
  else if kind = 3 ∧ coord = 2 then -1
  else 0

/-- Inverse-basis identity 2I on the four-dimensional local factor. -/
theorem local_duality :
    ∀ k l : Fin 4,
      sumN 4 (fun p => dual2 k.val p * basis1 l.val p) =
        if k = l then 2 else 0 := by decide

/-- Tensor-product basis, 64 columns in a 64-dimensional space. -/
def basis64 (i c : Nat) : Int :=
  basis1 (c % 4) (pairCoordinate i 0) *
  basis1 ((c / 4) % 4) (pairCoordinate i 1) *
  basis1 ((c / 16) % 4) (pairCoordinate i 2)

/-- Eight times the tensor-product dual basis, all entries integer. -/
def dual8 (c i : Nat) : Int :=
  dual2 (c % 4) (pairCoordinate i 0) *
  dual2 ((c / 4) % 4) (pairCoordinate i 1) *
  dual2 ((c / 16) % 4) (pairCoordinate i 2)

/-- Number of antisymmetric swap factors in a spectral label. -/
def negativeFactors (c : Nat) : Nat :=
  (if c % 4 = 3 then 1 else 0) +
  (if (c / 4) % 4 = 3 then 1 else 0) +
  (if (c / 16) % 4 = 3 then 1 else 0)

/-- Eigenvalue of A=I−M0 in the tensor basis. -/
def spectralValue (c : Nat) : Int :=
  if negativeFactors c = 2 then 4
  else if negativeFactors c = 3 then -4
  else 0

/-- Exactly ten of the 64 diagonal eigenvalues are nonzero. -/
theorem exactly_ten_nonzero_modes :
    ((List.range 64).filter (fun c => decide (spectralValue c ≠ 0))).length = 10 := by
  decide

/-- The ten nonzero-eigenvalue mode labels (nine +4 and one −4). -/
def selected (k : Nat) : Nat :=
  if k = 0 then 15 else
  if k = 1 then 31 else
  if k = 2 then 47 else
  if k = 3 then 51 else
  if k = 4 then 55 else
  if k = 5 then 59 else
  if k = 6 then 60 else
  if k = 7 then 61 else
  if k = 8 then 62 else 63

theorem selected_spectral_values :
    ∀ k : Fin 10,
      spectralValue (selected k.val) = if k.val = 9 then -4 else 4 := by
  decide

/-- A swap of the a_i,d_i bits in the 6-bit integer encoding. -/
def swapAt (i axis : Nat) : Nat :=
  let low := 2 ^ axis
  let high := 2 ^ (axis + 3)
  let a := (i / low) % 2
  let d := (i / high) % 2
  if a = d then i
  else if a = 1 then i - low + high
  else i + low - high

/-- Exact 64x64 M0, as independently constructed by ASTRA Python. -/
def m0 (i j : Nat) : Int :=
  (if j = swapAt (swapAt i 1) 2 then 1 else 0) +
  (if j = swapAt (swapAt i 0) 2 then 1 else 0) +
  (if j = swapAt (swapAt i 0) 1 then 1 else 0) -
  2 * (if j = swapAt (swapAt (swapAt i 0) 1) 2 then 1 else 0)

def a (i j : Nat) : Int := (if i = j then 1 else 0) - m0 i j

/-- Entire 64x64 matrix is factored through the TEN selected modes.
    Scaling by 8 allows kernel checking of integer identities only.
    A[i,j] = (1/8) Σ_{k<10} B[i,k] λ[k] D[k,j]. -/
theorem factorization_through_ten :
    ∀ i j : Fin 64,
      8 * a i.val j.val =
        sumN 10 (fun k =>
          basis64 i.val (selected k) *
          spectralValue (selected k) *
          dual8 (selected k) j.val) := by
  decide

/-- These ten columns are linearly independent over ℚ: the displayed
    integer dual matrix is a scaled left inverse, D B=8 I_10. -/
theorem ten_modes_independent :
    ∀ k l : Fin 10,
      sumN 64 (fun i =>
        dual8 (selected k.val) i * basis64 i (selected l.val)) =
          if k = l then 8 else 0 := by
  decide

/-- Each of the ten selected nonzero modes is an *exact* eigenvector
    of A=I−M0 with its stated eigenvalue, verified at all 64 rows. -/
theorem ten_exact_eigenvectors :
    ∀ i : Fin 64, ∀ k : Fin 10,
      sumN 64 (fun j =>
        a i.val j * basis64 j (selected k.val)) =
        spectralValue (selected k.val) * basis64 i.val (selected k.val) := by
  decide

/-- **Exact rank-10 certificate**: A has a 10-column factorization,
    and those columns admit the displayed scaled left inverse.
    Together with selected_spectral_values (all λ ≠ 0), this is the
    standard algebraic rank-10 witness over ℚ, independently of the
    Python Gaussian-elimination implementation. -/
theorem exact_rank_ten_certificate :
    (∀ i j : Fin 64,
      8 * a i.val j.val =
        sumN 10 (fun k =>
          basis64 i.val (selected k) *
          spectralValue (selected k) *
          dual8 (selected k) j.val)) ∧
    (∀ k l : Fin 10,
      sumN 64 (fun i =>
        dual8 (selected k.val) i * basis64 i (selected l.val)) =
          if k = l then 8 else 0) ∧
    (∀ k : Fin 10, spectralValue (selected k.val) ≠ 0) := by
  constructor
  · exact factorization_through_ten
  constructor
  · exact ten_modes_independent
  · intro k
    rw [selected_spectral_values]
    split <;> decide

#print axioms local_duality
#print axioms exactly_ten_nonzero_modes
#print axioms factorization_through_ten
#print axioms ten_modes_independent
#print axioms ten_exact_eigenvectors
#print axioms exact_rank_ten_certificate

end AstraMath.SpectralRankTen
