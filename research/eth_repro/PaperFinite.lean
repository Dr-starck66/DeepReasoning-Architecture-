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
/-- The instance is satisfiable, independently of its polynomial representation. -/
theorem toy_nonempty : 0 < toyCount := by decide
def gNumerator (t : Int) : Int := 3 * t - t * t
-- At the selected points, g(T)=gNumerator(T)/2, so g(0)=0, g(1)=g(2)=1.
theorem g_numerator_at_zero : gNumerator 0 = 0 := by decide
theorem g_numerator_at_one : gNumerator 1 = 2 := by decide
theorem g_numerator_at_two : gNumerator 2 = 2 := by decide

/-! A finite instance of the paper's ACTUAL per-occurrence homogeneous
replacement forms, at T=0,1,2. Rational g(T)=(3T-T^2)/2 is integral at
these three points; the Int definitions below are ONLY used there. -/
private def gInt (t : Int) : Int := (gNumerator t) / 2
private def phi2Z (u v : Int) : Int := 1 - (1 - u) * (1 - v)
private def phi3Z (u v w : Int) : Int := 1 - (1 - u) * (1 - v) * (1 - w)

def transformedPhi (a b c d : Bool) (t : Int) : Int :=
  let x1 := bit a
  let x2 := bit b
  let x3 := bit c
  let x4 := bit d
  let z := gInt t
  phi3Z x1 (x3 + z * x4) (x4 + z * x3) *
  phi2Z (1 - x1) x2 *
  phi2Z (x2 + z * x1) (1 - x3) *
  phi2Z (1 - (x2 + z * x1)) x4

def transformedSum (t : Int) : Int :=
  (bitDomain.flatMap fun a =>
   bitDomain.flatMap fun b =>
   bitDomain.flatMap fun c =>
   bitDomain.map fun d => transformedPhi a b c d t).foldl (fun s v => s + v) 0

/-- Direct finite evaluations of the paper's H(t) on the worked example. -/
theorem transformed_zero : transformedSum 0 = 5 := by decide
theorem transformed_one : transformedSum 1 = 2 := by decide
theorem transformed_two : transformedSum 2 = 2 := by decide
theorem transformed_zero_matches_boolean_count : transformedSum 0 = toySumPhi := by decide

/-! Single-measurement matrices C_A=(1,1), C_B=(1,1).
At t=1,2 all off-group replacement forms depend only on y_A,y_B. -/
private def groupA (yA yB : Int) : Int :=
  (bitDomain.flatMap fun a =>
   bitDomain.map fun b =>
     if bit a + bit b = yA then
       phi3Z (bit a) yB yB * phi2Z (1 - bit a) (bit b)
     else 0).foldl (fun s v => s + v) 0

private def groupB (yA yB : Int) : Int :=
  (bitDomain.flatMap fun c =>
   bitDomain.map fun d =>
     if bit c + bit d = yB then
       phi2Z yA (1 - bit c) * phi2Z (1 - yA) (bit d)
     else 0).foldl (fun s v => s + v) 0

def separatedSum : Int :=
  ((([0, 1, 2] : List Int).flatMap fun yA =>
    ([0, 1, 2] : List Int).map fun yB =>
      groupA yA yB * groupB yA yB)).foldl (fun s v => s + v) 0

/-- A directly machine-checked instance of sum_y (prod_g sum_u A_g). -/
theorem separated_equals_direct_one : separatedSum = transformedSum 1 := by decide
theorem separated_equals_direct_two : separatedSum = transformedSum 2 := by decide

#print axioms clause2_correct
#print axioms clause3_correct
#print axioms toy_polynomial_matches_sat
#print axioms toy_count_exact
#print axioms toy_polynomial_sum_exact
#print axioms transformed_zero_matches_boolean_count
#print axioms separated_equals_direct_one
end AstraMath
