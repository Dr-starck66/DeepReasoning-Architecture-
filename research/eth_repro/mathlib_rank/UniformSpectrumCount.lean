import UniformProjectorRank
import Mathlib.Algebra.Polynomial.Coeff
import Mathlib.Data.Fintype.Sum
import Mathlib.Tactic

/-!
ASTRA Ω — *uniform* binomial support count in the rational spectral basis.

A local label has three nonnegative swap-sign eigenvectors and exactly
one negative-sign eigenvector. The generating function of the q-fold
label count is (X+3)^q. Its coefficient at X^k yields choose(q,k)*3^(q-k).

This file aims at an unconditional Mathlib rank theorem for the tensor-
basis reconstructed filtered operator F_q of UniformProjectorRank.
It does NOT assert the reconstruction equals the independently defined
computational-basis swap polynomial E_q for every q.
-/

namespace AstraMath.UniformSpectrumCount

open AstraMath.UniformProjectorRank
open Polynomial

noncomputable def marker (x : Fin 4) : ℕ[X] :=
  if x.val = 3 then X else 1

private theorem marker_sum :
    (∑ x : Fin 4, marker x) = X + C (3 : ℕ) := by
  norm_num [marker, Fin.sum_univ_four]
  ring

private theorem marker_product (q : Nat) (c : Label q) :
    (∏ i : Fin q, marker (c i)) =
      (X : ℕ[X]) ^ negativeCount c := by
  classical
  change (∏ i : Fin q, if (c i).val = 3 then (X : ℕ[X]) else 1) =
    (X : ℕ[X]) ^
      (Finset.univ.filter (fun i : Fin q => (c i).val = 3)).card
  rw [Finset.prod_ite]
  simp [Finset.prod_const]

/-- The exact polynomial generating function for ALL q. -/
theorem generating_function (q : Nat) :
    (∑ c : Label q, (X : ℕ[X]) ^ negativeCount c) =
      (X + C (3 : ℕ)) ^ q := by
  classical
  calc
    (∑ c : Label q, (X : ℕ[X]) ^ negativeCount c) =
        (∑ c : Label q, ∏ i : Fin q, marker (c i)) := by
          apply Finset.sum_congr rfl
          intro c _
          exact (marker_product q c).symm
    _ = (∏ i : Fin q, ∑ z : Fin 4, marker z) := by
          simpa using
            (Finset.sum_prod_piFinset
              (s := (Finset.univ : Finset (Fin 4)))
              (g := fun (_i : Fin q) (z : Fin 4) => marker z))
    _ = (∏ _i : Fin q, (X + C (3 : ℕ))) := by
          simp_rw [marker_sum]
    _ = (X + C (3 : ℕ)) ^ q := by simp

/-- Every exact-k spectral slice has the binomial multiplicity,
    proved using coefficients of (X+3)^q, not finite enumeration. -/
theorem count_exact_k (q k : Nat) :
    Fintype.card {c : Label q // negativeCount c = k} =
      q.choose k * 3 ^ (q - k) := by
  classical
  have hcoeff :
      ((∑ c : Label q, (X : ℕ[X]) ^ negativeCount c) : ℕ[X]).coeff k =
        Fintype.card {c : Label q // negativeCount c = k} := by
    simp [Polynomial.coeff_sum, Polynomial.coeff_X_pow,
      Fintype.card_subtype, eq_comm]
  calc
    Fintype.card {c : Label q // negativeCount c = k} =
        ((∑ c : Label q, (X : ℕ[X]) ^ negativeCount c) : ℕ[X]).coeff k :=
          hcoeff.symm
    _ = ((X + C (3 : ℕ)) ^ q).coeff k := by rw [generating_function]
    _ = 3 ^ (q - k) * q.choose k := by
          simpa using (Polynomial.coeff_X_add_C_pow (R := ℕ) 3 q k)
    _ = q.choose k * 3 ^ (q - k) := Nat.mul_comm _ _

/-- The reconstructed filtered tensor operator has the promised
    closed-form exact rank in Mathlib, for EVERY natural q. -/
theorem reconstructed_rank_closed (q : Nat) :
    (F q).rank = q.choose 2 * 3 ^ (q - 2) +
      q.choose 3 * 3 ^ (q - 3) := by
  classical
  rw [reconstructed_rank]
  simp_rw [lambda_support]
  have hdisjoint :
      Disjoint
        (fun c : Label q => negativeCount c = 2)
        (fun c : Label q => negativeCount c = 3) := by
    apply Set.disjoint_left.mpr
    intro c h2 h3
    exact (show (2 : Nat) ≠ 3 by decide) (h2.symm.trans h3)
  rw [Fintype.card_subtype_or_disjoint
    (fun c : Label q => negativeCount c = 2)
    (fun c : Label q => negativeCount c = 3) hdisjoint]
  rw [count_exact_k q 2, count_exact_k q 3]

#print axioms generating_function
#print axioms count_exact_k
#print axioms reconstructed_rank_closed

end AstraMath.UniformSpectrumCount
