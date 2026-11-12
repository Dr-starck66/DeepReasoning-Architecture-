import LowRankExact
set_option maxHeartbeats 10000000
set_option maxRecDepth 4096

namespace AstraMath.RankTen
open AstraMath.LowRank

private def bit (n shift : Nat) : Bool := n / (2^shift) % 2 == 1

def decode (i : Fin 64) : Label :=
  { a1 := bit i.val 0, a2 := bit i.val 1, a3 := bit i.val 2,
    d1 := bit i.val 3, d2 := bit i.val 4, d3 := bit i.val 5 }

def anti (a d : Bool) : Int :=
  if a == d then 0 else if a then -1 else 1

def sym (typ : Nat) (a d : Bool) : Int :=
  if typ == 0 then (if !a && !d then 1 else 0)
  else if typ == 1 then (if a && d then 1 else 0)
  else (if a != d then 1 else 0)

def w (k : Fin 10) (i : Fin 64) : Int :=
  let u := decode i
  if k.val == 9 then anti u.a1 u.d1 * anti u.a2 u.d2 * anti u.a3 u.d3
  else if k.val / 3 == 0 then
    sym (k.val % 3) u.a1 u.d1 * anti u.a2 u.d2 * anti u.a3 u.d3
  else if k.val / 3 == 1 then
    anti u.a1 u.d1 * sym (k.val % 3) u.a2 u.d2 * anti u.a3 u.d3
  else
    anti u.a1 u.d1 * anti u.a2 u.d2 * sym (k.val % 3) u.a3 u.d3

def coefficient (k : Fin 10) : Int :=
  if k.val == 9 then -1 else if k.val % 3 == 2 then 1 else 2

def normSq (k : Fin 10) : Int :=
  if k.val == 9 || k.val % 3 == 2 then 8 else 4

def matrixA (i j : Fin 64) : Int :=
  (if decode i = decode j then 1 else 0) - m3 (decode i) (decode j)

def sum10 (f : Fin 10 → Int) : Int :=
  (List.finRange 10).foldl (fun acc k => acc + f k) 0
def sum64 (f : Fin 64 → Int) : Int :=
  (List.finRange 64).foldl (fun acc k => acc + f k) 0

theorem factor_int : ∀ i j : Fin 64,
    2 * matrixA i j = sum10 (fun k => coefficient k * w k i * w k j) := by
  decide

theorem orthogonal_int : ∀ k l : Fin 10,
    sum64 (fun i => w k i * w l i) =
    (if k = l then normSq k else 0) := by
  decide

theorem norms_nonzero : ∀ k : Fin 10, normSq k ≠ 0 := by decide

def eigenvalue (k : Fin 10) : Int := if k.val == 9 then -4 else 4

theorem eigenvectors_int : ∀ k : Fin 10, ∀ i : Fin 64,
    sum64 (fun j => matrixA i j * w k j) = eigenvalue k * w k i := by
  decide

theorem coefficients_nonzero : ∀ k : Fin 10, coefficient k ≠ 0 := by decide
theorem eigenvalues_nonzero : ∀ k : Fin 10, eigenvalue k ≠ 0 := by decide

/-- Strong exact rank certificate over Q, encoded without external Mathlib.
    The factorization establishes rank <=10. Pairwise orthogonality and
    nonzero eigenvalues establish ten independent image vectors, hence >=10.
    The fields provide machine-checked algebraic premises, not a claim
    about asymptotic SAT, Yang-Mills or any infinite-dimensional space. -/
structure RankTenCertificate where
  factor : ∀ i j : Fin 64,
    2 * matrixA i j = sum10 (fun k => coefficient k * w k i * w k j)
  orthogonality : ∀ k l : Fin 10,
    sum64 (fun i => w k i * w l i) =
      (if k = l then normSq k else 0)
  eigenvectors : ∀ k : Fin 10, ∀ i : Fin 64,
    sum64 (fun j => matrixA i j * w k j) = eigenvalue k * w k i
  norms_nonzero : ∀ k : Fin 10, normSq k ≠ 0
  eigenvalues_nonzero : ∀ k : Fin 10, eigenvalue k ≠ 0

theorem rank_exactly_ten_certificate : RankTenCertificate :=
  ⟨factor_int, orthogonal_int, eigenvectors_int, norms_nonzero,
   eigenvalues_nonzero⟩

#print axioms factor_int
#print axioms orthogonal_int
#print axioms eigenvectors_int
#print axioms rank_exactly_ten_certificate

end AstraMath.RankTen
