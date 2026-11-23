import UniformSpectrumCount
import Mathlib.Tactic

/-!
ASTRA Ω — q-uniform equality of the independently defined swap projectors
and the previously certified spectral reconstruction.

The projector E q is defined solely from the *computational-basis*
coordinate swap x=1 ↔ x=2 (0,3 fixed), and the local kernels
(I±S)/2. There is NO reference to B, D or F in the definition of E.

The proof derives the exact 4×4 local spectral decomposition by finite
arithmetic, then uses a FINITE SUM/PRODUCT DISTRIBUTIVITY theorem for
all q — not a bounded enumeration and not an assumption about rank.
-/

namespace AstraMath.UniformSwapEquality

open Matrix
open AstraMath.UniformProjectorRank
open AstraMath.UniformSpectrumCount
open AstraMath.SpectralRankTen

abbrev Signs (q : Nat) := Fin q → Bool

/-- Independently defined physical coordinate swap on a 4-state pair.
    It fixes states 0 and 3 and exchanges 1 and 2. -/
def swapCoord (x : Fin 4) : Fin 4 :=
  if x = 1 then 2 else if x = 2 then 1 else x

/-- Local matrix element of the coordinate swap S. -/
def localSwap (x y : Fin 4) : ℚ :=
  if swapCoord x = y then 1 else 0

/-- Local matrix element of the identity. -/
def localIdentity (x y : Fin 4) : ℚ :=
  if x = y then 1 else 0

/-- Genuine local swap projectors (I+S)/2 and (I-S)/2. -/
def localProjector (negative : Bool) (x y : Fin 4) : ℚ :=
  (localIdentity x y + (if negative then -1 else 1) * localSwap x y) / 2

/-- Exact local spectral sign of one of the ORIGINAL four eigenvectors. -/
def signOf (c : Fin 4) : Bool := decide (c.val = 3)

def labelSigns {q : Nat} (c : Label q) : Signs q :=
  fun i => signOf (c i)

def countNegative {q : Nat} (p : Signs q) : Nat :=
  (Finset.univ.filter (fun i : Fin q => p i = true)).card

/-- Filter is defined from Boolean swap signs, not from the tensor basis. -/
def signWeight {q : Nat} (p : Signs q) : ℚ :=
  if countNegative p = 2 then 4
  else if countNegative p = 3 then -4
  else 0

/-- The independent computational-basis E_q, made exclusively of direct
    local swap projectors. For each sign pattern, tensor-multiply
    (I±S_i)/2; retain +4 for 2 negatives and −4 for 3 negatives. -/
def E (q : Nat) : Matrix (Label q) (Label q) ℚ :=
  fun x y =>
    ∑ p : Signs q,
      signWeight p * ∏ i : Fin q, localProjector (p i) (x i) (y i)

/-- A local spectral contribution restricted to the chosen swap sign. -/
def localTerm (negative : Bool) (c x y : Fin 4) : ℚ :=
  if signOf c = negative then localB c x * localD c y else 0

/-- LOCAL HARD BRIDGE: the independently defined swap projector
    is *exactly* the sum of the old eigenvector/dual terms.
    2 × 4 × 4 explicit ℚ equalities; no theorem assumed. -/
theorem local_projector_spectral (negative : Bool) (x y : Fin 4) :
    (∑ c : Fin 4, localTerm negative c x y) =
      localProjector negative x y := by
  cases negative <;> fin_cases x <;> fin_cases y <;>
    norm_num [localTerm, signOf, localProjector, localIdentity,
      localSwap, swapCoord, localB, localD, basis1, dual2, Fin.sum_univ_four]

/-- A global sign-pattern term equals its independent tensor of swap
    kernels, for *any* q. -/
theorem tensor_projector_spectral (q : Nat) (p : Signs q)
    (x y : Label q) :
    (∑ c : Label q,
      ∏ i : Fin q, localTerm (p i) (c i) (x i) (y i)) =
    ∏ i : Fin q, localProjector (p i) (x i) (y i) := by
  classical
  calc
    _ = ∏ i : Fin q,
        ∑ c : Fin 4, localTerm (p i) c (x i) (y i) := by
          simpa using
            (Finset.sum_prod_piFinset
              (s := (Finset.univ : Finset (Fin 4)))
              (g := fun i c => localTerm (p i) c (x i) (y i)))
    _ = _ := by simp_rw [local_projector_spectral]

/-- A fixed spectral label contributes only to its exact sign pattern. -/
theorem term_product_orthogonal (q : Nat)
    (p : Signs q) (c x y : Label q) :
    (∏ i : Fin q, localTerm (p i) (c i) (x i) (y i)) =
      if p = labelSigns c then
        ∏ i : Fin q, localB (c i) (x i) * localD (c i) (y i)
      else 0 := by
  classical
  by_cases h : p = labelSigns c
  · subst p
    rw [if_pos rfl]
    apply Finset.prod_congr rfl
    intro i _
    simp [localTerm, labelSigns]
  · rw [if_neg h]
    have hmismatch : ∃ i : Fin q, p i ≠ labelSigns c i := by
      by_contra hn
      apply h
      funext i
      by_contra heq
      exact hn ⟨i, heq⟩
    obtain ⟨i, hi⟩ := hmismatch
    apply Finset.prod_eq_zero (Finset.mem_univ i)
    simp [localTerm, labelSigns, hi]

/-- The sign filter equals the previous certified tensor-label filter. -/
theorem label_sign_weight {q : Nat} (c : Label q) :
    signWeight (labelSigns c) = lambda c := by
  have hcount : countNegative (labelSigns c) = negativeCount c := by
    simp [countNegative, labelSigns, signOf, negativeCount]
  simp [signWeight, lambda, hcount]

/-- Matrix entry of the certified tensor reconstruction expressed as a
    *single* sum of the local basis and dual products. -/
theorem reconstructed_entry (q : Nat) (x y : Label q) :
    F q x y =
      ∑ c : Label q,
        lambda c * ∏ i : Fin q,
          (localB (c i) (x i) * localD (c i) (y i)) := by
  classical
  change (B q * W q * D q) x y = _
  rw [Matrix.mul_apply]
  apply Finset.sum_congr rfl
  intro c _
  simp only [W, Matrix.mul_diagonal, B, D]
  rw [← Finset.prod_mul_distrib]
  ring

/-- THE MISSING q-UNIFORM BRIDGE:
    the swap-projector polynomial E_q equals the *certified* tensor
    spectral reconstruction F_q at EVERY matrix entry for ANY q.
    Nothing is tested at bounded q; the proof is symbolic. -/
theorem independent_swaps_equal_reconstruction (q : Nat) :
    E q = F q := by
  classical
  ext x y
  have hcollapse (c : Label q) :
      (∑ p : Signs q,
        signWeight p *
          ∏ i : Fin q, localTerm (p i) (c i) (x i) (y i)) =
        lambda c * ∏ i : Fin q,
          (localB (c i) (x i) * localD (c i) (y i)) := by
    simp_rw [term_product_orthogonal]
    simp only [mul_ite, mul_zero]
    simp [label_sign_weight]
  calc
    E q x y =
      ∑ p : Signs q,
        signWeight p *
          (∑ c : Label q,
            ∏ i : Fin q, localTerm (p i) (c i) (x i) (y i)) := by
              simp only [E]
              apply Finset.sum_congr rfl
              intro p _
              rw [tensor_projector_spectral]
    _ = ∑ c : Label q,
        ∑ p : Signs q,
          signWeight p *
            ∏ i : Fin q, localTerm (p i) (c i) (x i) (y i) := by
              simp_rw [Finset.mul_sum]
              rw [Finset.sum_comm]
    _ = ∑ c : Label q,
        lambda c * ∏ i : Fin q,
          (localB (c i) (x i) * localD (c i) (y i)) := by
            apply Finset.sum_congr rfl
            intro c _
            exact hcollapse c
    _ = F q x y := (reconstructed_entry q x y).symm

/-- THE USER'S REQUESTED COMPLETE THEOREM:
    exact rank of the independently constructed swap projector
    E_q for EVERY natural q, including the empty tensor product. -/
theorem independent_swap_projector_rank (q : Nat) :
    (E q).rank =
      q.choose 2 * 3 ^ (q - 2) +
      q.choose 3 * 3 ^ (q - 3) := by
  rw [independent_swaps_equal_reconstruction q]
  exact reconstructed_rank_closed q

#print axioms local_projector_spectral
#print axioms tensor_projector_spectral
#print axioms term_product_orthogonal
#print axioms label_sign_weight
#print axioms independent_swaps_equal_reconstruction
#print axioms independent_swap_projector_rank

end AstraMath.UniformSwapEquality
