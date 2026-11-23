import Lean
import SpectralRankTen

/-!
ASTRA Ω — exact spectral projector verification.

For a pair of bits, (I+S) and (I-S) have scalar eigenvalues 2 or 0,
depending on whether the local swap sign matches the chosen projector.
The tensor-product selector is formalized for *arbitrary length* as
a list identity. For q=3, an independent explicit polynomial in the
three commuting swaps is proven equal to 8 times the historical ASTRA
matrix, at all 4096 integer entries.

The uniform Mathlib rank statement for E_q is not proved here.
-/
set_option maxRecDepth 32768
set_option maxHeartbeats 0

namespace AstraMath.ProjectorSpectrum

/-- Positive swap sign is +1; antisymmetric sign is -1. -/
def swapSign (negative : Bool) : Int :=
  if negative then -1 else 1

/-- Evaluation of the local numerator (I+S), or (I-S). -/
def projectorFactor (selectedNegative actualNegative : Bool) : Int :=
  if selectedNegative then 1 - swapSign actualNegative
  else 1 + swapSign actualNegative

theorem projectorFactor_eq (selectedNegative actualNegative : Bool) :
    projectorFactor selectedNegative actualNegative =
      if selectedNegative = actualNegative then 2 else 0 := by
  cases selectedNegative <;> cases actualNegative <;> decide

/-- Scalar evaluation of tensor numerator products, on matching bit-sign
    signatures; mismatched list lengths produce 0. -/
def tensorFactor : List Bool → List Bool → Int
  | [], [] => 1
  | p :: ps, a :: as_ => projectorFactor p a * tensorFactor ps as_
  | _, _ => 0

/-- Uniform (all lengths) exact projector identity, no matrix enumeration. -/
theorem tensorFactor_eq (pattern actual : List Bool)
    (hlen : pattern.length = actual.length) :
    tensorFactor pattern actual =
      if pattern = actual then (2 : Int) ^ pattern.length else 0 := by
  induction pattern generalizing actual with
  | nil =>
    cases actual with
    | nil => decide
    | cons a as_ => simp at hlen
  | cons p ps ih =>
    cases actual with
    | nil => simp at hlen
    | cons a as_ =>
      have htail : ps.length = as_.length := by simpa using hlen
      change projectorFactor p a * tensorFactor ps as_ =
        if p :: ps = a :: as_ then (2 : Int) ^ (p :: ps).length else 0
      rw [projectorFactor_eq, ih as_ htail]
      by_cases hp : p = a
      · subst a
        by_cases ht : ps = as_
        · subst as_
          simp [pow_succ, mul_comm]
        · simp [ht]
      · simp [hp]

theorem tensorFactor_mismatch (pattern actual : List Bool)
    (hlen : pattern.length = actual.length)
    (hne : pattern ≠ actual) :
    tensorFactor pattern actual = 0 := by
  rw [tensorFactor_eq pattern actual hlen]
  simp [hne]

/-- Select exactly two antisymmetric factors with eigenvalue +4, and
    exactly three with eigenvalue -4, zero elsewhere. -/
def eigenFilter (k : Nat) : Int :=
  if k = 2 then 4 else if k = 3 then -4 else 0

theorem eigenFilter_support (k : Nat) :
    eigenFilter k ≠ 0 ↔ k = 2 ∨ k = 3 := by
  unfold eigenFilter
  by_cases h2 : k = 2 <;> by_cases h3 : k = 3 <;> simp [h2, h3]

/-- This *new* filter agrees with the old A_3 spectrum at all
    possible numbers k=0,1,2,3 of negative local swap signs. -/
theorem q3_spectral_agreement :
    ∀ k : Fin 4,
      eigenFilter k.val =
        (if k.val % 2 = 0 then 2 * (k.val : Int)
         else 2 - 2 * (k.val : Int)) := by
  decide

/-- Apply the subset of the three swap permutations indicated by a mask. -/
def swapMask3 (i mask : Nat) : Nat :=
  (List.range 3).foldl (fun pos axis =>
    if mask / 2 ^ axis % 2 = 1
    then AstraMath.SpectralRankTen.swapAt pos axis else pos) i

/-- Sign of the term S_mask in the product Π(i∈selected)(I−S_i),
    Π(i∉selected)(I+S_i). -/
def localMaskSign (selected mask axis : Nat) : Int :=
  if selected / 2 ^ axis % 2 = 1 ∧ mask / 2 ^ axis % 2 = 1
  then -1 else 1

def subsetSign3 (selected mask : Nat) : Int :=
  localMaskSign selected mask 0 *
  localMaskSign selected mask 1 *
  localMaskSign selected mask 2

/-- Numerator T3=8 E3: three 2-negative subsets 011, 101, 110
    with weight +4, and one 3-negative subset 111 with weight -4. -/
def coefficient3 (mask : Nat) : Int :=
  4 * (subsetSign3 3 mask + subsetSign3 5 mask +
    subsetSign3 6 mask - subsetSign3 7 mask)

/-- Directly constructed from the projector polynomial, independently
    of the old A_3 formula. -/
def projected3 (i j : Nat) : Int :=
  (List.range 8).foldl (fun acc mask =>
    acc + if j = swapMask3 i mask then coefficient3 mask else 0) 0

/-- The q=3 spectral filter is *exactly* the historical ASTRA matrix,
    not merely a matrix of the same rank. The new integer-scaled
    projector numerator is 8 times the proven old matrix. -/
theorem projected3_equals_eight_times_A3 :
    ∀ i j : Fin 64,
      projected3 i.val j.val =
        8 * AstraMath.SpectralRankTen.a i.val j.val := by
  decide

#print axioms projectorFactor_eq
#print axioms tensorFactor_eq
#print axioms tensorFactor_mismatch
#print axioms eigenFilter_support
#print axioms q3_spectral_agreement
#print axioms projected3_equals_eight_times_A3

end AstraMath.ProjectorSpectrum
