"""Exact evaluation of one fixed coordinate of the ASTRA swap operator."""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
from itertools import combinations, product
from math import comb

from eth_lab import count_dpll, satisfied, validate

CNF = tuple[tuple[int, ...], ...]
Jet = tuple[int, int, int, int]
ONE: Jet = (1, 0, 0, 0)


def coordinate_weight(q: int, flipped: int) -> int:
    """Integer weight in 2**q E_q, four times K_2(flipped) - K_3(flipped)."""
    signs = q - 2 * flipped
    degree_two = (signs * signs - q) // 2
    degree_three = (signs**3 - (3 * q - 2) * signs) // 6
    return 4 * (degree_two - degree_three)


def _validate_width(q: int, cnf: CNF) -> None:
    validate(q, cnf)
    if any(len(clause) > 3 for clause in cnf):
        raise ValueError("expected clauses of width at most three")


def coordinate_enumerated(q: int, cnf: CNF) -> int:
    """Exponential reference on the swap orbit, with no full truth table."""
    _validate_width(q, cnf)
    return sum(coordinate_weight(q, mask.bit_count()) for mask in range(1 << q)
               if satisfied(mask, cnf))



def coordinate_by_model_counts(
    q: int, cnf: CNF, counter: Callable[[int, CNF], int] = count_dpll,
) -> int:
    """Use O(q^3) exact #SAT queries, each with at most three new unit clauses."""
    _validate_width(q, cnf)
    count = counter(q, cnf)
    if count == 0:
        return 0
    if count == 1:
        flipped = sum(counter(q, cnf + ((var,),)) for var in range(1, q + 1))
        return count * coordinate_weight(q, flipped)

    def choose(n: int, k: int) -> int:
        return comb(n, k) if 0 <= k <= n else 0

    total = (choose(q, 2) - choose(q, 3)) * count
    for degree in range(1, min(3, q) + 1):
        weight = (-2)**degree * (choose(q - degree, 2 - degree)
                                - choose(q - degree, 3 - degree))
        if weight:
            total += weight * sum(
                counter(q, cnf + tuple((var,) for var in fixed))
                for fixed in combinations(range(1, q + 1), degree)
            )
    return 4 * total

def gap_instance(left_n: int, left: CNF, right_n: int, right: CNF) -> tuple[int, CNF]:
    """Build (q,G) with one scaled coordinate equal to 2*q*(#left-#right).

    G uses exactly three distinct variables in each clause. Its variables
    are the first register. The second register is implicit at the fixed
    coordinate a=0, d=1 and is never read by G.
    """
    _validate_width(left_n, left)
    _validate_width(right_n, right)
    selector = left_n + right_n + 1
    clauses: list[tuple[int, ...]] = []
    next_var = selector + 1
    for n, cnf, offset, guard in ((left_n, left, 0, selector),
                                   (right_n, right, left_n, -selector)):
        clauses.extend((-guard, -var) for var in range(offset + 1, offset + n + 1))
        for clause in cnf:
            literals = tuple(dict.fromkeys(lit + offset if lit > 0 else lit - offset
                                           for lit in clause))
            if any(-lit in literals for lit in literals):
                continue
            if len(literals) == 3:
                first, second, third = literals
                gate = next_var
                next_var += 1
                clauses.extend(((-first, gate), (-second, gate),
                                (first, second, -gate)))
                literals = (gate, third)
            clauses.append((guard, *literals))

    padding = (next_var, next_var + 1, next_var + 2)
    fixed_zero = next_var + 3
    clauses.extend(tuple(-var if value else var for var, value in zip(padding, values))
                   for values in product((0, 1), repeat=3) if any(values))
    clauses.append((-fixed_zero,))
    q = fixed_zero
    for var in range(1, fixed_zero):
        if var != selector:
            q += 1
            clauses.extend(((var, q), (-var, -q)))

    strict = []
    for clause in clauses:
        occupied = {abs(lit) for lit in clause}
        fillers = tuple(var for var in padding if var not in occupied)
        strict.append(clause + fillers[:3 - len(clause)])
    return q, tuple(strict)


def _multiply(a: Jet, b: Jet) -> Jet:
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (a0 * b0, a0 * b1 + a1 * b0,
            a0 * b2 + a1 * b1 + a2 * b0,
            a0 * b3 + a1 * b2 + a2 * b1 + a3 * b0)


@dataclass(frozen=True)
class EliminationResult:
    value: int
    induced_width: int
    max_factor_rows: int


@dataclass
class _Factor:
    scope: tuple[int, ...]
    values: list[Jet]


def coordinate_eliminate(
    q: int, cnf: CNF, order: Sequence[int] | None = None, *, width_limit: int = 18,
) -> EliminationResult:
    """Evaluate via bucket elimination, stopping before an oversized bucket."""
    _validate_width(q, cnf)
    order = tuple(range(1, q + 1) if order is None else order)
    position = {var: i for i, var in enumerate(order)}
    if len(order) != q or set(position) != set(range(1, q + 1)):
        raise ValueError("elimination order must contain each variable exactly once")
    if any(not clause for clause in cnf):
        return EliminationResult(0, 0, 1)

    buckets: list[list[_Factor]] = [[] for _ in order]
    for clause in cnf:
        scope = tuple(sorted({abs(lit) for lit in clause}, key=position.__getitem__))
        local = tuple((scope.index(abs(lit)), lit > 0) for lit in clause)
        table = [(int(any(bool(mask & (1 << bit)) == value
                          for bit, value in local)), 0, 0, 0)
                 for mask in range(1 << len(scope))]
        buckets[position[scope[0]]].append(_Factor(scope, table))

    total = ONE
    width = 0
    max_rows = max((len(f.values) for bucket in buckets for f in bucket), default=1)
    for i, var in enumerate(order):
        factors = buckets[i]
        buckets[i] = []
        if not factors:
            total = _multiply(total, (2, 0, 0, 0))
            continue

        scope = tuple(sorted({x for factor in factors for x in factor.scope},
                             key=position.__getitem__))
        assert scope[0] == var
        local_width = len(scope) - 1
        if local_width > width_limit:
            raise ValueError(f"induced width {local_width} exceeds limit {width_limit}")
        rows = 1 << len(scope)
        width = max(width, local_width)
        max_rows = max(max_rows, rows)
        mapping = [(factor.values, tuple(scope.index(x) for x in factor.scope))
                   for factor in factors]

        output: list[Jet] = []
        for fixed in range(0, rows, 2):
            accum = [0] * 4
            for bit, sign in ((0, 1), (1, -1)):
                mask = fixed | bit
                term = ONE
                for table, source_bits in mapping:
                    submask = sum(((mask >> source) & 1) << target
                                  for target, source in enumerate(source_bits))
                    term = _multiply(term, table[submask])
                    if not any(term):
                        break
                accum[0] += term[0]
                for degree in range(1, 4):
                    accum[degree] += term[degree] + sign * term[degree - 1]
            output.append((accum[0], accum[1], accum[2], accum[3]))

        if len(scope) > 1:
            buckets[position[scope[1]]].append(_Factor(scope[1:], output))
        else:
            total = _multiply(total, output[0])

    return EliminationResult(4 * (total[2] - total[3]), width, max_rows)
