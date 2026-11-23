import UniformSwapEquality
import SwapCoordinate
import Mathlib.Algebra.Polynomial.Coeff

namespace AstraMath.SwapCoordinate.MatrixBridge

open scoped BigOperators
open Polynomial
open AstraMath.UniformProjectorRank (Label)
open AstraMath.UniformSwapEquality (Signs E localProjector localNumerator
  swapCoord countNegative signWeight)

def fixedRow (q : Nat) : Label q := fun _ => 1

def orbitLabel {q : Nat} (bits : Signs q) : Label q :=
  fun i => if bits i then 2 else 1

def patternSign (negative bit : Bool) : Int :=
  if negative then sign bit else 1

noncomputable def generating {q : Nat} (z : Signs q) : Polynomial Int :=
  ∏ i : Fin q, (1 + C (sign (z i)) * X)

noncomputable def patternTerm {q : Nat} (p z : Signs q) : Polynomial Int :=
  ∏ i : Fin q, (if p i then C (sign (z i)) * X else 1)

theorem generating_expand {q : Nat} (z : Signs q) :
    generating z = ∑ p : Signs q, patternTerm p z := by
  classical
  have h := Finset.sum_prod_piFinset
    (s := (Finset.univ : Finset Bool))
    (g := fun (i : Fin q) b => if b then C (sign (z i)) * X else 1)
  rw [Fintype.piFinset_univ] at h
  unfold generating
  have hsum (i : Fin q) : (∑ b : Bool, if b then C (sign (z i)) * X else 1) =
      1 + C (sign (z i)) * X := by
    rw [show (Finset.univ : Finset Bool) = {false, true} by decide]
    simp
  simp_rw [hsum] at h
  exact h.symm

theorem pattern_monomial {q : Nat} (p z : Signs q) :
    patternTerm p z = C (∏ i : Fin q, patternSign (p i) (z i)) * X ^ countNegative p := by
  classical
  calc
    patternTerm p z = ∏ i : Fin q,
        C (patternSign (p i) (z i)) * X ^ (if p i then 1 else 0 : Nat) := by
      unfold patternTerm
      apply Finset.prod_congr rfl
      intro i _
      cases p i <;> simp [patternSign]
    _ = _ := by
      rw [Finset.prod_mul_distrib, ← map_prod, Finset.prod_pow_eq_pow_sum]
      congr 2
      unfold countNegative
      rw [Finset.card_filter]

theorem generating_coeff {q : Nat} (z : Signs q) (k : Nat) :
    (generating z).coeff k = ∑ p : Signs q,
      if k = countNegative p then ∏ i : Fin q, patternSign (p i) (z i) else 0 := by
  classical
  rw [generating_expand, finset_sum_coeff]
  simp_rw [pattern_monomial, coeff_C_mul_X_pow]

theorem generating_low_degrees {q : Nat} (z : Signs q) :
    let e := coefficients (List.ofFn z)
    (generating z).coeff 0 = 1 ∧ (generating z).coeff 1 = e.linear ∧
    (generating z).coeff 2 = e.quadratic ∧ (generating z).coeff 3 = e.cubic := by
  induction q with
  | zero => norm_num [generating, coefficients, coeff_one]
  | succ q ih =>
      rcases ih (fun i => z i.succ) with ⟨h₀, h₁, h₂, h₃⟩
      have hgen : generating z =
          (1 + C (sign (z 0)) * X) * generating (fun i => z i.succ) := by
        exact Fin.prod_univ_succ _
      rw [hgen, List.ofFn_succ]
      simp only [add_mul, one_mul, coeff_add, mul_assoc, coeff_C_mul,
        coeff_X_mul_zero, coeff_X_mul, h₀, h₁, h₂, h₃, coefficients,
        mul_one, mul_zero, zero_add, add_comm, and_self]

theorem local_coefficient (negative bit : Bool) :
    localProjector negative 1 (if bit then 2 else 1) =
      (patternSign negative bit : ℚ) / 2 := by
  have h12 : (1 : Fin 4) ≠ 2 := by decide
  cases negative <;> cases bit <;>
    norm_num [localProjector, localNumerator, swapCoord, patternSign, sign, h12, h12.symm]

/-- An entry of the original rational matrix, in the all-off-diagonal row. -/
theorem scaled_matrix_entry {q : Nat} (z : Signs q) :
    (2 : ℚ)^q * E q (fixedRow q) (orbitLabel z) =
      (swapWeight (List.ofFn z) : ℚ) := by
  classical
  rcases generating_low_degrees z with ⟨_, _, h₂, h₃⟩
  have hweight : swapWeight (List.ofFn z) =
      4 * ((generating z).coeff 2 - (generating z).coeff 3) := by
    rw [h₂, h₃]
    rfl
  rw [hweight, generating_coeff, generating_coeff]
  simp only [Int.cast_mul, Int.cast_ofNat, Int.cast_sub, Int.cast_sum,
    ← Finset.sum_sub_distrib, Finset.mul_sum]
  unfold E
  rw [Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro p _
  have hprod : (∏ i : Fin q, localProjector (p i) (fixedRow q i) (orbitLabel z i)) =
      (∏ i : Fin q, (patternSign (p i) (z i) : ℚ)) / (2 : ℚ)^q := by
    simp only [fixedRow, orbitLabel, local_coefficient, Finset.prod_div_distrib,
      Finset.prod_const, Finset.card_univ, Fintype.card_fin]
  rw [hprod]
  have hnonzero : (2 : ℚ)^q ≠ 0 := by positivity
  have e2 : (2 : Nat) = countNegative p ↔ countNegative p = 2 := eq_comm
  have e3 : (3 : Nat) = countNegative p ↔ countNegative p = 3 := eq_comm
  by_cases h2 : countNegative p = 2 <;> by_cases h3 : countNegative p = 3
  · omega
  · simp only [signWeight, h2, if_true]
    push_cast
    field_simp; ring
  · simp only [signWeight, h3, if_true]
    push_cast
    field_simp; ring
  · simp only [signWeight, e2, e3, h2, h3, if_false, Int.cast_zero,
      zero_mul, mul_zero, sub_self]

theorem orbitLabel_injective (q : Nat) : Function.Injective (@orbitLabel q) := by
  intro z w h
  funext i
  have hi := congrFun h i
  have h12 : (1 : Fin 4) ≠ 2 := by decide
  cases hz : z i <;> cases hw : w i <;> simp_all [orbitLabel, h12.symm]

theorem matrix_entry_outside {q : Nat} (y : Label q)
    (h : ∀ z : Signs q, orbitLabel z ≠ y) : E q (fixedRow q) y = 0 := by
  classical
  let z : Signs q := fun i => decide (y i = 2)
  obtain ⟨i, hi⟩ : ∃ i, orbitLabel z i ≠ y i := by
    by_contra! he
    exact h z (funext he)
  have h12 : (1 : Fin 4) ≠ 2 := by decide
  have h1 : y i ≠ 1 := by
    intro h1
    exact hi (by simp [orbitLabel, z, h1, h12])
  have h2 : y i ≠ 2 := by
    intro h2
    exact hi (by simp [orbitLabel, z, h2])
  unfold E
  apply Finset.sum_eq_zero
  intro p _
  have hz : localProjector (p i) (fixedRow q i) (y i) = 0 := by
    simp [localProjector, localNumerator, fixedRow, swapCoord, h1.symm, h2.symm]
  rw [Finset.prod_eq_zero (Finset.mem_univ i) hz, mul_zero]

/-- Row action on any rational vector, with only the swap orbit contributing. -/
theorem scaled_matrix_action {q : Nat} (v : Label q → ℚ) :
    (2 : ℚ)^q * (∑ y : Label q, E q (fixedRow q) y * v y) =
      ∑ z : Signs q, (swapWeight (List.ofFn z) : ℚ) * v (orbitLabel z) := by
  classical
  let orbit := (Finset.univ : Finset (Signs q)).image orbitLabel
  rw [Finset.mul_sum]
  have hrestrict :
      (∑ y : Label q, (2 : ℚ)^q * (E q (fixedRow q) y * v y)) =
      ∑ y ∈ orbit, (2 : ℚ)^q * (E q (fixedRow q) y * v y) := by
    symm
    apply Finset.sum_subset (Finset.subset_univ _)
    intro y _ hy
    have h : ∀ z : Signs q, orbitLabel z ≠ y := by
      intro z hz
      exact hy (Finset.mem_image.mpr ⟨z, Finset.mem_univ _, hz⟩)
    simp [matrix_entry_outside y h]
  rw [hrestrict, Finset.sum_image]
  · apply Finset.sum_congr rfl
    intro z _
    rw [← mul_assoc, scaled_matrix_entry]
  · intro z _ w _ h
    exact orbitLabel_injective q h

end AstraMath.SwapCoordinate.MatrixBridge

#print axioms AstraMath.SwapCoordinate.MatrixBridge.scaled_matrix_entry

#print axioms AstraMath.SwapCoordinate.MatrixBridge.scaled_matrix_action
