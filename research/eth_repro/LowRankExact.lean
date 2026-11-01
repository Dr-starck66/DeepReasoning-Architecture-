import Lean
/-!
ASTRA MATH LAB Ω: finite proof-checking tests for OpenAI ETH preprint §4.
- Q=R=2 manuscript four-coordinate example: exact rank-one I-M0,
  measurement c, and polynomial row confinement.
- Q=3, R=2: support property of the full swap-based 64x64 M0.
The general rank/tail/parameter lemmas and 2^o(n) bound are NOT proved here.
No sorry, axiom or native_decide.
-/
namespace AstraMath.LowRank

/-! Section 4 worked example, Q=R=2, outside R<Q. -/
def swapOne (i : Fin 4) : Fin 4 :=
  if i = 0 then 1 else if i = 1 then 0 else if i = 2 then 3 else 2

def swapTwo (i : Fin 4) : Fin 4 :=
  if i = 0 then 2 else if i = 2 then 0 else if i = 1 then 3 else 1

theorem swapOne_involution : ∀ i : Fin 4, swapOne (swapOne i) = i := by decide
theorem swapTwo_involution : ∀ i : Fin 4, swapTwo (swapTwo i) = i := by decide
theorem swaps_commute : ∀ i : Fin 4, swapOne (swapTwo i) = swapTwo (swapOne i) := by decide

def fullSwap (i : Fin 4) : Fin 4 := swapOne (swapTwo i)
def m0 (i j : Fin 4) : Int :=
  (if j = swapOne i then 1 else 0) +
  (if j = swapTwo i then 1 else 0) -
  (if j = fullSwap i then 1 else 0)

def sign (i : Fin 4) : Int := if i = 0 || i = 3 then 1 else -1
def matrixDifference (i j : Fin 4) : Int :=
  (if i = j then 1 else 0) - m0 i j

/-- Each entry of I-M0 equals sign(i)*sign(j): exact rank-one factorization. -/
theorem rank_one_factor : ∀ i j : Fin 4,
    matrixDifference i j = sign i * sign j := by decide

def measurement (z0 z1 z2 z12 : Int) : Int := z0 - z1 - z2 + z12
/-- Twice the manuscript row: 2<P_u(T),z>=2*z0-T*z1-2*T*z2. -/
def twiceRow (t z0 z1 z2 z12 : Int) : Int :=
  2*z0 - t*z1 - 2*t*z2

theorem row_at_zero (z0 z1 z2 z12 : Int) :
    twiceRow 0 z0 z1 z2 z12 = 2*z0 := by
  simp [twiceRow]

theorem row_at_one (z0 z1 z2 z12 : Int) :
    twiceRow 1 z0 z1 z2 z12 =
    2 * measurement z0 z1 z2 z12 + z1 - 2*z12 := by
  simp [twiceRow, measurement]; omega

theorem row_at_two (z0 z1 z2 z12 : Int) :
    twiceRow 2 z0 z1 z2 z12 =
    2 * measurement z0 z1 z2 z12 - 2*z2 - 2*z12 := by
  simp [twiceRow, measurement]; omega

/-- At t=1 the value depends only on measurement, z1 and z12. -/
theorem row_one_localizes
    (z0 z1 z2 z12 w0 w1 w2 w12 : Int)
    (hc : measurement z0 z1 z2 z12 = measurement w0 w1 w2 w12)
    (h1 : z1 = w1) (h12 : z12 = w12) :
    twiceRow 1 z0 z1 z2 z12 = twiceRow 1 w0 w1 w2 w12 := by
  rw [row_at_one, row_at_one, hc, h1, h12]

/-- At t=2 the value depends only on measurement, z2 and z12. -/
theorem row_two_localizes
    (z0 z1 z2 z12 w0 w1 w2 w12 : Int)
    (hc : measurement z0 z1 z2 z12 = measurement w0 w1 w2 w12)
    (h2 : z2 = w2) (h12 : z12 = w12) :
    twiceRow 2 z0 z1 z2 z12 = twiceRow 2 w0 w1 w2 w12 := by
  rw [row_at_two, row_at_two, hc, h2, h12]

/-! Full Q=3, r=2, R=2: 64 labels, 3 commuting involutions. -/
structure Label where
  a1 : Bool
  a2 : Bool
  a3 : Bool
  d1 : Bool
  d2 : Bool
  d3 : Bool
  deriving DecidableEq, Repr

def s1 (u : Label) : Label := {u with a1 := u.d1, d1 := u.a1}
def s2 (u : Label) : Label := {u with a2 := u.d2, d2 := u.a2}
def s3 (u : Label) : Label := {u with a3 := u.d3, d3 := u.a3}

theorem s1_involution (u : Label) : s1 (s1 u) = u := by
  cases u; rfl
theorem s2_involution (u : Label) : s2 (s2 u) = u := by
  cases u; rfl
theorem s3_involution (u : Label) : s3 (s3 u) = u := by
  cases u; rfl
theorem s1s2_commute (u : Label) : s1 (s2 u) = s2 (s1 u) := by
  cases u; rfl
theorem s1s3_commute (u : Label) : s1 (s3 u) = s3 (s1 u) := by
  cases u; rfl
theorem s2s3_commute (u : Label) : s2 (s3 u) = s3 (s2 u) := by
  cases u; rfl

/-! For interval I={0,1}, f_I(W)=1-2W=Pi1+Pi2+Pi3-2I;
    M0=V0*f_I(W)=Pi2Pi3+Pi1Pi3+Pi1Pi2-2Pi1Pi2Pi3. -/
def m3 (u v : Label) : Int :=
  (if v = s2 (s3 u) then 1 else 0) +
  (if v = s1 (s3 u) then 1 else 0) +
  (if v = s1 (s2 u) then 1 else 0) -
  2 * (if v = s1 (s2 (s3 u)) then 1 else 0)

def mismatches (u v : Label) : Nat :=
  (if v.a1 = u.d1 then 0 else 1) +
  (if v.a2 = u.d2 then 0 else 1) +
  (if v.a3 = u.d3 then 0 else 1)

/-- Every nonzero M0[u,v] differs from d_u in at most R-1=1 first labels. -/
theorem q3_matrix_support (u v : Label) (h : m3 u v ≠ 0) :
    mismatches u v ≤ 1 := by
  by_cases h1 : v = s2 (s3 u)
  · subst v
    by_cases eq1 : u.a1 = u.d1
    · simp [mismatches, s2, s3, eq1]
    · simp [mismatches, s2, s3, eq1]
  · by_cases h2 : v = s1 (s3 u)
    · subst v
      by_cases eq2 : u.a2 = u.d2
      · simp [mismatches, s1, s3, eq2]
      · simp [mismatches, s1, s3, eq2]
    · by_cases h3 : v = s1 (s2 u)
      · subst v
        by_cases eq3 : u.a3 = u.d3
        · simp [mismatches, s1, s2, eq3]
        · simp [mismatches, s1, s2, eq3]
      · by_cases h4 : v = s1 (s2 (s3 u))
        · subst v
          simp [mismatches, s1, s2, s3]
        · simp [m3, h1, h2, h3, h4] at h

/-- Binomial eigenmultiplicities r=2, Q=3: bad j=2,3 -> 10 measurements. -/
theorem q3_bad_eigenvectors : 3*3 + 1 = (10:Nat) := by decide
theorem q3_fraction_of_bad_spectrum : (10:Nat)*32 = 5*64 := by decide

#print axioms rank_one_factor
#print axioms row_one_localizes
#print axioms row_two_localizes
#print axioms q3_matrix_support
end AstraMath.LowRank
