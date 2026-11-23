"""Exact model count and swap coordinate for 3-CNF with a low-rank affine quotient."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from clay_swap_coordinate import CNF
from eth_lab import validate

Equation = tuple[int, int]
Rows = dict[int, Equation]


def extract_parities(q: int, cnf: CNF) -> tuple[list[Equation], CNF]:
    """Replace each complete parity encoding by the equivalent GF(2) equation."""
    validate(q, cnf)
    groups: dict[tuple[int, ...], set[int]] = {}
    residual: list[tuple[int, ...]] = []
    for clause in cnf:
        if len(clause) > 3:
            raise ValueError("expected clauses of width at most three")
        if not clause:
            residual.append(clause)
            continue
        literals = set(clause)
        if any(-literal in literals for literal in literals):
            continue
        ordered = sorted(literals, key=abs)
        scope = tuple(map(abs, ordered))
        forbidden = sum((literal < 0) << i for i, literal in enumerate(ordered))
        groups.setdefault(scope, set()).add(forbidden)

    equations = []
    for scope, patterns in groups.items():
        mask = sum(1 << (var - 1) for var in scope)
        for rhs in (0, 1):
            forbidden = {bits for bits in range(1 << len(scope))
                         if bits.bit_count() % 2 != rhs}
            if forbidden <= patterns:
                equations.append((mask, rhs))
                patterns.difference_update(forbidden)
        for bits in sorted(patterns):
            residual.append(tuple(-var if (bits >> i) & 1 else var
                                  for i, var in enumerate(scope)))
    return equations, tuple(residual)


def reduce_row(mask: int, value: int, rows: Rows) -> Equation:
    """Eliminate supported pivots from the leading end of a binary row."""
    while mask:
        row = rows.get(mask.bit_length() - 1)
        if row is None:
            break
        bits, rhs = row
        mask ^= bits
        value ^= rhs
    return mask, value


def affine_space(q: int, equations: list[Equation]) -> tuple[int, list[Equation]] | None:
    """Return dimension and expressions x_i = parity(mask_i & y) XOR offset_i."""
    rows: Rows = {}
    for mask, rhs in equations:
        mask, rhs = reduce_row(mask, rhs, rows)
        if mask:
            rows[mask.bit_length() - 1] = mask, rhs
        elif rhs:
            return None

    expressions: list[Equation] = []
    for i in range(q):
        if i not in rows:
            expressions.append((1 << i, 0))
            continue
        row, offset = rows[i]
        row ^= 1 << i
        mask = 0
        while row:
            bit = row & -row
            submask, constant = expressions[bit.bit_length() - 1]
            mask ^= submask
            offset ^= constant
            row ^= bit
        expressions.append((mask, offset))
    return q - len(rows), expressions


def walsh_in_place(coefficients: list[int]) -> None:
    """Evaluate sum_t coefficients[t] (-1)^<t,z> at every binary z."""
    step = 1
    while step < len(coefficients):
        for start in range(0, len(coefficients), 2 * step):
            for i in range(start, start + step):
                a, b = coefficients[i], coefficients[i + step]
                coefficients[i], coefficients[i + step] = a + b, a - b
        step *= 2


@dataclass(frozen=True)
class AffineResult:
    models: int
    coordinate: int
    parity_equations: int
    residual_clauses: int
    affine_dimension: int | None
    residual_rank: int | None
    quotient_points: int


def coordinate_affine(q: int, cnf: CNF, *, rank_limit: int = 16) -> AffineResult:
    """Evaluate exactly by enumerating the quotient seen by the residual CNF."""
    if rank_limit < 0:
        raise ValueError("rank limit must be nonnegative")
    equations, residual = extract_parities(q, cnf)
    affine = affine_space(q, equations)
    if affine is None:
        return AffineResult(0, 0, len(equations), len(residual), None, None, 0)
    dimension, expressions = affine

    # Independent rows span exactly the linear forms observed by the residual clauses.
    basis: Rows = {}
    observed = sorted({abs(literal) - 1 for clause in residual for literal in clause})
    for var in observed:
        row, _ = reduce_row(expressions[var][0], 0, basis)
        if row:
            basis[row.bit_length() - 1] = row, 1 << len(basis)
    rank = len(basis)
    if rank > rank_limit:
        raise ValueError(f"residual affine rank {rank} exceeds limit {rank_limit}")

    projected = {}
    for var in observed:
        mask, offset = expressions[var]
        _, tag = reduce_row(mask, 0, basis)
        projected[var] = tag, offset
    def translate(literal: int) -> Equation:
        tag, offset = projected[abs(literal) - 1]
        return tag, offset ^ (literal > 0)

    translated = [tuple(map(translate, clause)) for clause in residual]

    points = 1 << rank
    weights = [0] * points
    # Characters outside the residual span cancel exactly in every fiber.
    for degree, scale in ((2, 4), (3, -4)):
        for variables in combinations(expressions, degree):
            mask = offset = 0
            for bits, rhs in variables:
                mask ^= bits
                offset ^= rhs
            remainder, tag = reduce_row(mask, 0, basis)
            if remainder == 0:
                weights[tag] += -scale if offset else scale
    walsh_in_place(weights)

    model_fibers = signed_weight = 0
    for point, weight in enumerate(weights):
        if all(any((point & mask).bit_count() % 2 == rhs for mask, rhs in clause)
               for clause in translated):
            model_fibers += 1
            signed_weight += weight
    fiber_size = 1 << (dimension - rank)
    return AffineResult(model_fibers * fiber_size, signed_weight * fiber_size,
                        len(equations), len(residual), dimension, rank, points)
