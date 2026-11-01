import Lean
/-!
ASTRA MATH LAB Ω — verification formelle FINIE en Lean 4.
Source: OpenAI, The Exponential Time Hypothesis is False (25 Oct 2026),
section "A direct polynomial for the count".
No sorry, axiom, unsafe, native_decide. N'implique PAS une preuve d'ETH.
-/
namespace AstraMath
private def bit (b : Bool) : Int := if b then 1 else 0
private def phi2 (a b : Bool) : Int :=
  1 - (1 - bit a) * (1 - bit b)
private def phi3 (a b c : Bool) : Int :=
  1 - (1 - bit a) * (1 - bit b) * (1 - bit c)
theorem clause2_correct (a b : Bool) :
    phi2 a b = (if a || b then 1 else 0) := by
  cases a <;> cases b <;> decide
theorem clause3_correct (a b c : Bool) :
    phi3 a b c = (if a || b || c then 1 else 0) := by
  cases a <;> cases b <;> cases c <;> decide
def toySat (a b c d : Bool) : Bool :=
  (a || c || d) && (!a || b) && (b || !c) && (!b || d)
def toyPhi (a b c d : Bool) : Int :=
  phi3 a c d * phi2 (!a) b * phi2 b (!c) * phi2 (!b) d
theorem toy_polynomial_matches_sat (a b c d : Bool) :
    toyPhi a b c d = (if toySat a b c d then 1 else 0) := by
  cases a <;> cases b <;> cases c <;> cases d <;> decide
private def bitDomain : List Bool := [false, true]
def toyCount : Nat :=
  (bitDomain.flatMap fun a =>
   bitDomain.flatMap fun b =>
   bitDomain.flatMap fun c =>
   bitDomain.map fun d => toySat a b c d).filter (fun x => x) |>.length
def toySumPhi : Int :=
  (bitDomain.flatMap fun a =>
   bitDomain.flatMap fun b =>
   bitDomain.flatMap fun c =>
   bitDomain.map fun d => toyPhi a b c d).foldl (fun acc x => acc + x) 0
theorem toy_count_exact : toyCount = 5 := by decide
theorem toy_polynomial_sum_exact : toySumPhi = 5 := by decide
def g (t : Rat) : Rat := (3 * t - t * t) / 2
theorem g_at_zero : g 0 = 0 := by decide
theorem g_at_one : g 1 = 1 := by decide
theorem g_at_two : g 2 = 1 := by decide
end AstraMath
