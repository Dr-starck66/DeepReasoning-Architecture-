import Mathlib.LinearAlgebra.Matrix.Rank
import Mathlib.Data.Matrix.Mul
import Mathlib.Tactic

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
end AstraMath.MathlibRank
