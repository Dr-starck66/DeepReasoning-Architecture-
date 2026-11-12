import Lean
/-!
ASTRA TOPOQUANTUM Ω, finite N=2 BdG at mu=0 and t=delta=1.
Theorems prove Hermiticity, two explicit exact kernel vectors, and their
independence. This does NOT establish any N, experimental MZM evidence,
a class-D invariant, or a global topological-protection theorem.
Lean compilation status must be established by an actual Lean runner.
-/
namespace AstraTopoQuantum

def h2 (i j : Fin 4) : Int :=
  if i = 0 then
    if j = 1 then -1 else if j = 3 then 1 else 0
  else if i = 1 then
    if j = 0 then -1 else if j = 2 then -1 else 0
  else if i = 2 then
    if j = 1 then -1 else if j = 3 then 1 else 0
  else
    if j = 0 then 1 else if j = 2 then 1 else 0

/-- The explicit four-by-four BdG Hamiltonian is symmetric. -/
theorem h2_symmetric : ∀ i j : Fin 4, h2 i j = h2 j i := by decide

/-- The left Majorana Nambu vector is (1,0,-1,0). -/
def leftMode (j : Fin 4) : Int :=
  if j = 0 then 1 else if j = 2 then -1 else 0
/-- The right Majorana Nambu vector is (0,1,0,1). -/
def rightMode (j : Fin 4) : Int :=
  if j = 1 then 1 else if j = 3 then 1 else 0

/-- Every row has zero projection on the left vector. -/
theorem left_exact_zero : ∀ i : Fin 4, h2 i 0 - h2 i 2 = 0 := by decide
/-- Every row has zero projection on the right vector. -/
theorem right_exact_zero : ∀ i : Fin 4, h2 i 1 + h2 i 3 = 0 := by decide

/-- No linear combination of the edge vectors can vanish unless a=0. -/
theorem left_coefficient_zero (a b : Int)
    (h : ∀ i : Fin 4, a * leftMode i + b * rightMode i = 0) : a = 0 := by
  have h0 := h 0
  simpa [leftMode, rightMode] using h0

/-- No linear combination of the edge vectors can vanish unless b=0. -/
theorem right_coefficient_zero (a b : Int)
    (h : ∀ i : Fin 4, a * leftMode i + b * rightMode i = 0) : b = 0 := by
  have h1 := h 1
  simpa [leftMode, rightMode] using h1

#print axioms h2_symmetric
#print axioms left_exact_zero
#print axioms right_exact_zero
#print axioms left_coefficient_zero
#print axioms right_coefficient_zero
end AstraTopoQuantum
