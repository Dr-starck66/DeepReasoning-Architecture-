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

/-- Match ASTRA's kernel-checked List.range fold to Mathlib's finite sum.
    Proved once by induction, not by enumerating matrix entries. -/
private theorem sumN_eq_sum_fin (n : Nat) (f : Nat → Int) :
    sumN n f = ∑ k : Fin n, f k.val := by
  have h (m : Nat) : sumN m f = ∑ k ∈ Finset.range m, f k := by
    induction m with
    | zero => simp [sumN]
    | succ m ih =>
      change (List.range (m+1)).foldl (fun z k => z + f k) 0 =
        ∑ k ∈ Finset.range (m+1), f k
      rw [List.range_succ, List.foldl_append]
      simp only [List.foldl_cons, List.foldl_nil]
      rw [Finset.sum_range_succ]
      change sumN m f + f m = (∑ k ∈ Finset.range m, f k) + f m
      rw [ih]
  simpa only [Fin.sum_univ_eq_sum_range] using h n


def A : Matrix (Fin 64) (Fin 64) ℚ :=
  fun i j => (a i.val j.val : ℚ)

def B : Matrix (Fin 64) (Fin 10) ℚ :=
  fun i k => (basis64 i.val (selected k.val) : ℚ)

def D : Matrix (Fin 10) (Fin 64) ℚ :=
  fun k i => (dual8 (selected k.val) i.val : ℚ) / 8

def W : Matrix (Fin 10) (Fin 10) ℚ :=
  Matrix.diagonal (fun k => (spectralValue (selected k.val) : ℚ))

set_option maxRecDepth 32768
set_option maxHeartbeats 0

/-- Rational D·B=I obtained by casting the *proved* integer 8I duality. -/
theorem dual_left_inverse : D * B = 1 := by
  classical
  ext k l
  have hInt := ten_modes_independent k l
  rw [sumN_eq_sum_fin] at hInt
  have hRat :
      (∑ i : Fin 64,
        (dual8 (selected k.val) i.val : ℚ) *
        (basis64 i.val (selected l.val) : ℚ)) =
        (if k = l then (8 : ℚ) else 0) := by
    exact_mod_cast hInt
  rw [Matrix.mul_apply]
  have hcalc :
      (∑ i : Fin 64, D k i * B i l) =
      (∑ i : Fin 64,
        (dual8 (selected k.val) i.val : ℚ) *
        (basis64 i.val (selected l.val) : ℚ)) / 8 := by
    rw [Finset.sum_div]
    apply Finset.sum_congr rfl
    intro i _
    dsimp [D, B]
    ring
  rw [hcalc, hRat]
  simp [Matrix.one_apply]

/-- Rational A=B·W·D from the *proved* integer identity 8A=B·λ·dual8. -/
theorem exact_factorization : A = B * W * D := by
  classical
  ext i j
  have hInt := factorization_through_ten i j
  rw [sumN_eq_sum_fin] at hInt
  have hRat :
      8 * (a i.val j.val : ℚ) =
      ∑ k : Fin 10,
        (basis64 i.val (selected k.val) : ℚ) *
        (spectralValue (selected k.val) : ℚ) *
        (dual8 (selected k.val) j.val : ℚ) := by
    exact_mod_cast hInt
  have hmul :
      (B * W * D) i j =
      (∑ k : Fin 10,
        (basis64 i.val (selected k.val) : ℚ) *
        (spectralValue (selected k.val) : ℚ) *
        (dual8 (selected k.val) j.val : ℚ)) / 8 := by
    rw [Matrix.mul_apply, Finset.sum_div]
    apply Finset.sum_congr rfl
    intro k _
    simp only [W, Matrix.mul_diagonal, B, D]
    ring
  change (a i.val j.val : ℚ) = (B * W * D) i j
  rw [hmul]
  linarith

theorem diagonal_full_rank : W.rank = 10 := by
  classical
  have hnonzero :
      ∀ k : Fin 10, (spectralValue (selected k.val) : ℚ) ≠ 0 := by
    intro k
    rw [selected_spectral_values]
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
