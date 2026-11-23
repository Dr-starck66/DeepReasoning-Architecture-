import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Algebra.BigOperators.Ring.Finset
import Mathlib.Tactic
import SpectralRankTen

/-!
ASTRA Ω — uniform, *any q*, exact rational tensor-basis rank bridge.

The matrix F_q below is defined by spectral reconstruction B_q W_q D_q.
The theorem is uniform in q, and its rank is exactly the number of
supported spectral labels (no finite enumeration). Every basis entry
comes directly from the existing ASTRA certified local 4x4 swap basis.

IMPORTANT SCIENTIFIC BOUNDARY: This file does not yet prove that F_q
equals the computational-basis projector polynomial E_q for all q, nor
that the supported-label count equals the binomial closed form.
The old q=3 exact identity is checked in ProjectorSpectrum.lean.
-/

namespace AstraMath.UniformProjectorRank

open Matrix
open AstraMath.SpectralRankTen

abbrev Label (q : Nat) := Fin q → Fin 4

def localB (c x : Fin 4) : ℚ := (basis1 c.val x.val : ℚ)
def localD (c x : Fin 4) : ℚ := (dual2 c.val x.val : ℚ) / 2

/-- A universal 4x4 duality relation inherited from the historical basis. -/
theorem local_dual (c d : Fin 4) :
    (∑ x : Fin 4, localD c x * localB d x) =
      if c = d then (1 : ℚ) else 0 := by
  fin_cases c <;> fin_cases d <;>
    norm_num [localD, localB, basis1, dual2, Fin.sum_univ_four] <;> decide

/-- Tensor products of the local 4x4 rational basis and its inverse. -/
def B (q : Nat) : Matrix (Label q) (Label q) ℚ :=
  fun x c => ∏ i : Fin q, localB (c i) (x i)

def D (q : Nat) : Matrix (Label q) (Label q) ℚ :=
  fun c x => ∏ i : Fin q, localD (c i) (x i)

/-- The tensor dual is a left inverse in *every dimension*. -/
theorem tensor_left_inverse (q : Nat) : D q * B q = 1 := by
  classical
  ext c d
  rw [Matrix.mul_apply]
  have hprod :
      (∑ x : Label q,
         ∏ i : Fin q, localD (c i) (x i) * localB (d i) (x i)) =
        ∏ i : Fin q,
          ∑ z : Fin 4, localD (c i) z * localB (d i) z := by
    simpa using
      (Finset.sum_prod_piFinset (s := (Finset.univ : Finset (Fin 4)))
        (g := fun i z => localD (c i) z * localB (d i) z))
  have hcalc :
      (∑ x : Label q, D q c x * B q x d) =
        (∑ x : Label q,
          ∏ i : Fin q, localD (c i) (x i) * localB (d i) (x i)) := by
    apply Finset.sum_congr rfl
    intro x _
    simp only [D, B, ← Finset.prod_mul_distrib]
  rw [hcalc, hprod]
  simp_rw [local_dual]
  by_cases h : c = d
  · subst d
    simp
  · have hex : ∃ i : Fin q, c i ≠ d i := by
      by_contra hn
      apply h
      funext i
      by_contra hbad
      exact hn ⟨i, hbad⟩
    obtain ⟨i, hi⟩ := hex
    have hz :
        (∏ j : Fin q, if c j = d j then (1 : ℚ) else 0) = 0 := by
      apply Finset.prod_eq_zero (Finset.mem_univ i)
      simp [hi]
    simpa [Matrix.one_apply, h] using hz

/-- Exactly k swaps have a negative local eigenvalue. -/
def negativeCount {q : Nat} (c : Label q) : Nat :=
  (Finset.univ.filter (fun i : Fin q => (c i).val = 3)).card

/-- Filter eigenvalues for the q-independent two/three-negative projector. -/
def lambda {q : Nat} (c : Label q) : ℚ :=
  if negativeCount c = 2 then 4
  else if negativeCount c = 3 then -4
  else 0

def W (q : Nat) : Matrix (Label q) (Label q) ℚ :=
  Matrix.diagonal (fun c => lambda c)

/-- Spectral reconstruction in the actual (4-dimensional per pair)
    *computational tensor basis*. -/
def F (q : Nat) : Matrix (Label q) (Label q) ℚ :=
  B q * W q * D q

/-- A generic two-sided rank invariant under rational change of basis
    when one product of the inverse and basis is the identity. -/
theorem rank_three_factor {ι : Type} [Fintype ι] [DecidableEq ι]
    (X Y Z : Matrix ι ι ℚ) (h : Z * X = 1) :
    (X * Y * Z).rank = Y.rank := by
  have hupper : (X * Y * Z).rank ≤ Y.rank := by
    calc
      (X * Y * Z).rank ≤ (X * Y).rank :=
        Matrix.rank_mul_le_left (X * Y) Z
      _ ≤ Y.rank := Matrix.rank_mul_le_right X Y
  have hrecover : Z * (X * Y * Z) * X = Y := by
    calc
      Z * (X * Y * Z) * X = (Z * X) * Y * (Z * X) := by
        simp only [Matrix.mul_assoc]
      _ = Y := by simp [h]
  have hlower : Y.rank ≤ (X * Y * Z).rank := by
    calc
      Y.rank = (Z * (X * Y * Z) * X).rank := by rw [hrecover]
      _ ≤ (Z * (X * Y * Z)).rank :=
        Matrix.rank_mul_le_left (Z * (X * Y * Z)) X
      _ ≤ (X * Y * Z).rank :=
        Matrix.rank_mul_le_right Z (X * Y * Z)
  omega

/-- Full, parameter-uniform matrix-rank theorem for the reconstructed
    filtered operator. The right side is a finite spectral-label count. -/
theorem reconstructed_rank (q : Nat) :
    (F q).rank =
      Fintype.card {c : Label q // lambda c ≠ 0} := by
  classical
  rw [F]
  rw [rank_three_factor (B q) (W q) (D q) (tensor_left_inverse q)]
  exact Matrix.rank_diagonal (fun c : Label q => lambda c)

/-- The support is *exactly* the set of two/three antisymmetric factors. -/
theorem lambda_support {q : Nat} (c : Label q) :
    lambda c ≠ 0 ↔ negativeCount c = 2 ∨ negativeCount c = 3 := by
  unfold lambda
  by_cases h2 : negativeCount c = 2
  · simp [h2]
  · by_cases h3 : negativeCount c = 3 <;> simp [h2, h3]

#print axioms local_dual
#print axioms tensor_left_inverse
#print axioms rank_three_factor
#print axioms reconstructed_rank
#print axioms lambda_support

end AstraMath.UniformProjectorRank
