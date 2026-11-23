import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.BigOperators.Group.Finset.Basic
import Mathlib.Tactic

namespace AstraMath.AffineFiber

open scoped BigOperators

def sign (t : ZMod 2) : Int := if t = 0 then 1 else -1

private theorem sign_add_one : ∀ t : ZMod 2, sign (t + 1) = -sign t := by decide

/-- A translation in the kernel of the residual projection pairs opposite weights
    whenever the character is nontrivial on that translation. -/
theorem cancel_character {G H : Type*} [AddCommGroup G] [Fintype G] [AddCommGroup H]
    [DecidableEq H] (L : G →+ H) (chi : G →+ ZMod 2) (z : H)
    (v : G) (hv : L v = 0) (hc : chi v = 1) :
    (∑ x : G, if L x = z then sign (chi x) else 0) = 0 := by
  classical
  let f (x : G) : Int := if L x = z then sign (chi x) else 0
  let shift : G ≃ G := {
    toFun := fun x => x + v
    invFun := fun x => x - v
    left_inv := by intro x; simp
    right_inv := by intro x; simp }
  have reverse_sign (x : G) : f (shift x) = - f x := by
    change f (x + v) = - f x
    simp only [f, map_add, hv, add_zero, hc]
    split_ifs <;> simp [sign_add_one]
  have h := Equiv.sum_comp shift f
  simp only [reverse_sign, Finset.sum_neg_distrib] at h
  change (∑ x : G, f x) = 0
  omega

/-- A character that factors through the residual projection has constant sign
    on a given fiber. This equation also holds for an empty fiber. -/
theorem constant_character {G H : Type*} [AddCommGroup G] [Fintype G] [AddCommGroup H]
    [DecidableEq H] (L : G →+ H) (psi : H →+ ZMod 2) (z : H) :
    (∑ x : G, if L x = z then sign (psi (L x)) else 0) =
      ((Finset.univ.filter (fun x : G => L x = z)).card : Int) * sign (psi z) := by
  classical
  rw [← Finset.sum_filter]
  have h :
      (∑ x ∈ Finset.univ.filter (fun x : G => L x = z), sign (psi (L x))) =
      ∑ _x ∈ Finset.univ.filter (fun x : G => L x = z), sign (psi z) := by
    apply Finset.sum_congr rfl
    intro x hx
    rw [(Finset.mem_filter.mp hx).2]
  rw [h, Finset.sum_const, nsmul_eq_mul]

end AstraMath.AffineFiber

#print axioms AstraMath.AffineFiber.cancel_character
#print axioms AstraMath.AffineFiber.constant_character
