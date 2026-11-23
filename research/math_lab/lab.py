"""ASTRA MATH LAB Ω: registry validator and exact, bounded Beal experiment.

Pure Python standard library. No external APIs, no subscriptions, no prize claims.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
from functools import reduce
from math import gcd
from pathlib import Path
import json

REGISTRY = Path(__file__).with_name("registry.json")
VALID_STATES = frozenset({"open", "claim_under_review", "solved"})


def validate_registry(path: Path = REGISTRY) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["currency"] == "USD", "Prize currency must be explicit"
    assert data["as_of"], "A date is mandatory"
    ids = set()
    for item in data["problems"]:
        assert item["id"] not in ids, "Duplicate problem id"
        ids.add(item["id"])
        assert item["status"] in VALID_STATES, "Unrecognized status"
        assert type(item["prize_usd"]) is int and item["prize_usd"] > 0, "Invalid amount"
        assert item["url"].startswith("https://"), "Primary https source required"
        assert item["organizer"] in {"Clay Mathematics Institute", "American Mathematical Society"}
        assert item["workstream"], "Each prize needs an actionable research track"
    return data


def beal_search(max_base: int = 20, max_exponent: int = 6) -> dict:
    """Exhaustively enumerate A,B,C <= max_base and 3 <= x,y,z <= max_exponent.

    Exact integer arithmetic; only a *finite box* is tested. A counterexample
    needs gcd(A,B,C) == 1; solutions with a common factor are expected controls.
    """
    if not (2 <= max_base <= 200 and 3 <= max_exponent <= 12):
        raise ValueError("Bound outside deliberate safety limits")
    powers = defaultdict(list)
    for c in range(1, max_base + 1):
        for z in range(3, max_exponent + 1):
            powers[c ** z].append((c, z))
    total = 0
    common_factor = 0
    counterexamples = []
    positive_controls = []
    for a in range(1, max_base + 1):
        for x in range(3, max_exponent + 1):
            ax = a ** x
            for b in range(1, max_base + 1):
                for y in range(3, max_exponent + 1):
                    for c, z in powers.get(ax + b ** y, ()):
                        total += 1
                        witness = [a, x, b, y, c, z]
                        if reduce(gcd, (a, b, c)) == 1:
                            counterexamples.append(witness)
                        else:
                            common_factor += 1
                            if len(positive_controls) < 12:
                                positive_controls.append(witness)
    return {
        "experiment": "Beal finite exhaustive integer search",
        "bounds": {"bases_inclusive": [1, max_base], "exponents_inclusive": [3, max_exponent]},
        "exact_equalities": total,
        "solutions_with_common_factor": common_factor,
        "coprime_counterexamples": counterexamples,
        "positive_controls_sample": positive_controls,
        "scope": "FINITE_ENUMERATION_ONLY; not proof or disproof of the general conjecture",
        "award_eligible": False,
    }


def claim_gate(record: dict) -> str:
    """A conservative declaration gate, NOT a proof verifier."""
    if record.get("claim") == "prize_solution":
        required = ("theorem_statement", "full_proof", "publication_url", "independent_acceptance")
        if not all(record.get(k) for k in required):
            return "FAIL"
        return "UNVERIFIED"  # Cannot infer eligibility from self-declared metadata.
    if record.get("claim") == "finite_experiment" and record.get("exact_arithmetic") is True and record.get("scope"):
        return "PARTIAL"  # Must actually run/verify the experiment to establish PASS.
    return "FAIL"


def main() -> None:
    parser = argparse.ArgumentParser(description="ASTRA MATH LAB Ω (offline)")
    parser.add_argument("command", choices=("audit", "beal"))
    parser.add_argument("--base", type=int, default=20)
    parser.add_argument("--exponent", type=int, default=6)
    args = parser.parse_args()
    if args.command == "audit":
        data = validate_registry()
        output = {
            "registry_status": "PASS", "as_of": data["as_of"],
            "tracked_problems": len(data["problems"]),
            "active_or_pending": sum(p["status"] != "solved" for p in data["problems"]),
            "mathematical_solutions_verified": 0,
            "prize_claim_status": "UNVERIFIED",
        }
    else:
        output = beal_search(args.base, args.exponent)
    print(json.dumps(output, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
