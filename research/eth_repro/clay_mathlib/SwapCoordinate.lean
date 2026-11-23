import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Data.Int.Cast.Lemmas
import Mathlib.Tactic.LinearCombination
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Ring

namespace AstraMath.SwapCoordinate

open scoped BigOperators

def sign (bit : Bool) : Int := if bit then -1 else 1

def signSum : List Bool → Int
  | [] => 0
  | bit :: rest => sign bit + signSum rest

structure Coefficients where
  linear : Int
  quadratic : Int
  cubic : Int

/-- The nonconstant coefficients of the product of (1 + sign(bit) X),
    modulo X^4. The constant coefficient is always one. -/
def coefficients : List Bool → Coefficients
  | [] => ⟨0, 0, 0⟩
  | bit :: rest =>
      let e := coefficients rest
      let a := sign bit
      ⟨e.linear + a, e.quadratic + a * e.linear, e.cubic + a * e.quadratic⟩

def swapWeight (bits : List Bool) : Int :=
  4 * ((coefficients bits).quadratic - (coefficients bits).cubic)

theorem moments (bits : List Bool) :
    let s := signSum bits
    let q : Int := bits.length
    let e := coefficients bits
    e.linear = s ∧ 2 * e.quadratic = s ^ 2 - q ∧
      6 * e.cubic = s ^ 3 - (3 * q - 2) * s := by
  induction bits with
  | nil => norm_num [signSum, coefficients]
  | cons bit rest ih =>
      rcases ih with ⟨h₁, h₂, h₃⟩
      simp only [signSum, coefficients, List.length_cons, Nat.cast_add, Nat.cast_one]
      rw [h₁]
      cases bit <;> simp only [sign, Bool.false_eq_true, if_false, if_true] <;>
        refine ⟨by ring, ?_, ?_⟩
      · linear_combination h₂
      · linear_combination h₃ + 3 * h₂
      · linear_combination h₂
      · linear_combination h₃ - 3 * h₂

theorem weight_at_sum_zero (bits : List Bool) (h : signSum bits = 0) :
    swapWeight bits = -2 * (bits.length : Int) := by
  rcases moments bits with ⟨_, h₂, h₃⟩
  rw [h] at h₂ h₃
  dsimp [swapWeight]
  norm_num at h₂ h₃
  omega

theorem weight_at_sum_two (bits : List Bool) (h : signSum bits = 2) :
    swapWeight bits = 2 * (bits.length : Int) := by
  rcases moments bits with ⟨_, h₂, h₃⟩
  rw [h] at h₂ h₃
  dsimp [swapWeight]
  norm_num at h₂ h₃
  omega

def balance : List Bool → List Bool
  | [] => []
  | bit :: rest => bit :: (!bit) :: balance rest

theorem balance_sum (bits : List Bool) : signSum (balance bits) = 0 := by
  induction bits with
  | nil => rfl
  | cons bit rest ih =>
      cases bit <;> simp [balance, signSum, sign, ih]

def pad (selector : Bool) (bits : List Bool) : List Bool :=
  false :: selector :: balance bits

theorem padded_weight (selector : Bool) (bits : List Bool) :
    swapWeight (pad selector bits) =
      if selector then -2 * ((pad selector bits).length : Int)
      else 2 * ((pad selector bits).length : Int) := by
  cases selector
  · exact weight_at_sum_two _ (by simp [pad, signSum, sign, balance_sum])
  · exact weight_at_sum_zero _ (by simp [pad, signSum, sign, balance_sum])

/-- Constant signed weights on the two selector sectors give the exact gap. -/
theorem weighted_gap {Last First : Type*} (positive : Finset First)
    (negative : Finset Last) (p : First → List Bool) (n : Last → List Bool)
    (q : Nat)
    (hp : ∀ x ∈ positive, (pad false (p x)).length = q)
    (hn : ∀ x ∈ negative, (pad true (n x)).length = q) :
    (∑ x ∈ positive, swapWeight (pad false (p x))) +
      (∑ x ∈ negative, swapWeight (pad true (n x))) =
      2 * (q : Int) * ((positive.card : Int) - (negative.card : Int)) := by
  classical
  have hpos : (∑ x ∈ positive, swapWeight (pad false (p x))) =
      ∑ _x ∈ positive, (2 * (q : Int)) := by
    apply Finset.sum_congr rfl
    intro x hx
    simpa [hp x hx] using padded_weight false (p x)
  have hneg : (∑ x ∈ negative, swapWeight (pad true (n x))) =
      ∑ _x ∈ negative, (-2 * (q : Int)) := by
    apply Finset.sum_congr rfl
    intro x hx
    simpa [hn x hx] using padded_weight true (n x)
  rw [hpos, hneg]
  simp only [Finset.sum_const, nsmul_eq_mul]
  ring

/-- The clauses for a fresh OR gate have exactly one possible gate value. -/
theorem or_gate_unique : ∀ a b t : Bool,
    ((!a || t) && (!b || t) && (a || b || !t)) = (t == (a || b)) := by
  decide

/-- The two clauses enforcing a complementary copy have a unique extension. -/
theorem complementary_copy : ∀ a b : Bool,
    ((a || b) && (!a || !b)) = (b == !a) := by
  decide

/-- The seven distinct three-literal clauses exclude every nonzero triple. -/
theorem padding_pins_zero : ∀ a b c : Bool,
    ((a || b || !c) && (a || !b || c) && (a || !b || !c) &&
      (!a || b || c) && (!a || b || !c) && (!a || !b || c) &&
      (!a || !b || !c)) = (!a && !b && !c) := by
  decide

end AstraMath.SwapCoordinate

#print axioms AstraMath.SwapCoordinate.moments
#print axioms AstraMath.SwapCoordinate.padded_weight
#print axioms AstraMath.SwapCoordinate.weighted_gap
#print axioms AstraMath.SwapCoordinate.or_gate_unique
#print axioms AstraMath.SwapCoordinate.complementary_copy
#print axioms AstraMath.SwapCoordinate.padding_pins_zero
