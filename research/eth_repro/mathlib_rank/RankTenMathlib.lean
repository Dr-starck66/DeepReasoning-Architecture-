import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Data.Matrix.Mul
import Mathlib.Tactic
import SpectralRankTen

/-!
Independent formal rank bridge for ASTRA Ω.
This proves the generic algebraic step: if A factors through a
10-dimensional space with an invertible diagonal middle factor and a
left inverse on the ten columns, then Mathlib's Matrix.rank A = 10.

This is NOT (yet) the instantiated proof for the swap matrix A0; that
requires importing and bridging the certified numerical identities.
Do not promote this theorem to a claim about A0 without that bridge.
-/

namespace AstraMath.MathlibRank

open Matrix

theorem rank_ten_of_factorization
    (A : Matrix (Fin 64) (Fin 64) ℚ)
    (B : Matrix (Fin 64) (Fin 10) ℚ)
    (D : Matrix (Fin 10) (Fin 64) ℚ)
    (W : Matrix (Fin 10) (Fin 10) ℚ)
    (hfac : A = B * W * D)
    (hleft : D * B = 1)
    (hfull : W.rank = 10) :
    A.rank = 10 := by
  have hupper : A.rank ≤ 10 := by
    calc
      A.rank = (B * (W * D)).rank := by rw [hfac, Matrix.mul_assoc]
      _ ≤ B.rank := Matrix.rank_mul_le_left B (W * D)
      _ ≤ 10 := by simpa using (Matrix.rank_le_width B)
  have hrecover : D * A * B = W := by
    calc
      D * A * B = D * (B * W * D) * B := by rw [hfac]
      _ = (D * B) * W * (D * B) := by simp only [Matrix.mul_assoc]
      _ = W := by simp [hleft]
  have hlower : 10 ≤ A.rank := by
    calc
      10 = W.rank := hfull.symm
      _ = (D * A * B).rank := by rw [hrecover]
      _ ≤ (D * A).rank := Matrix.rank_mul_le_left (D * A) B
      _ ≤ A.rank := Matrix.rank_mul_le_right D A
  omega

#print axioms rank_ten_of_factorization

/-!
Concrete instantiation for ASTRA's 64×64 exact swap matrix. The matrix A,
its tensor eigenvectors B, integer duals /8 (D), and the ±4 diagonal W are
defined by *the previously Lean-verified source functions*, not a new
independent or copied matrix.
-/

namespace Concrete
open AstraMath.SpectralRankTen

def A : Matrix (Fin 64) (Fin 64) ℚ :=
  fun i j => (a i.val j.val : ℚ)

def B : Matrix (Fin 64) (Fin 10) ℚ :=
  fun i k => (basis64 i.val (selected k.val) : ℚ)

def D : Matrix (Fin 10) (Fin 64) ℚ :=
  fun k i => (dual8 (selected k.val) i.val : ℚ) / 8

def W : Matrix (Fin 10) (Fin 10) ℚ :=
  Matrix.diagonal (fun k => if k.val = 9 then -4 else 4)

set_option maxRecDepth 32768
set_option maxHeartbeats 0

/-- Decidable 10×10 rational identity, linked to the verified basis64/dual8. -/
theorem dual_left_inverse : D * B = 1 := by
  ext k l
  decide +revert

/-- Decidable 64×64 rational factorization. No axioms, no approximations. -/
theorem exact_factorization : A = B * W * D := by
  ext i j
  decide +revert

theorem diagonal_full_rank : W.rank = 10 := by
  classical
  have hnonzero :
      ∀ k : Fin 10, (if k.val = 9 then (-4 : ℚ) else 4) ≠ 0 := by
    intro k
    split_ifs <;> norm_num
  simpa [W, Matrix.rank_diagonal, hnonzero]

/-- The concrete, actual Mathlib matrix rank theorem requested for ASTRA. -/
theorem astra_exact_rank_ten : Matrix.rank A = 10 := by
  exact rank_ten_of_factorization A B D W
    exact_factorization dual_left_inverse diagonal_full_rank

#print axioms dual_left_inverse
#print axioms exact_factorization
#print axioms diagonal_full_rank
#print axioms astra_exact_rank_ten

end Concrete

end AstraMath.MathlibRank
