#!/usr/bin/env python3
"""ASTRA rank-ten formal proof pipeline: exact arithmetic + Lean kernel + ProofGate.

No external service, secrets, credentials or financial expenditure required.
A local Lean PASS is NOT an immutable GitHub CI PASS; the latter stays UNVERIFIED
until a completed independent run at the exact commit SHA has been inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory

from math_research_engine import canonical_sha, research
from proof_gate import audit, strip_lean_comments, FORBIDDEN

HERE = Path(__file__).resolve().parent
THEOREM = "theorem rank_exactly_ten_certificate : RankTenCertificate :="
REQUIRED = (
    "factor_int",
    "orthogonal_int",
    "eigenvectors_int",
    "rank_exactly_ten_certificate",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(argv: list[str], *, cwd: Path, env: dict[str, str], timeout: int = 180) -> dict:
    try:
        result = subprocess.run(
            argv, cwd=cwd, env=env, capture_output=True, text=True,
            timeout=timeout, check=False,
        )
        return {"returncode": result.returncode,
                "stdout": result.stdout[-6000:],
                "stderr": result.stderr[-3000:]}
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"returncode": None, "stdout": "", "stderr": type(exc).__name__}


def lean_check(directory: Path) -> dict:
    executable = shutil.which("lean")
    rank_source = directory / "RankTen.lean"
    base_source = directory / "LowRankExact.lean"
    if not executable or not base_source.is_file() or not rank_source.is_file():
        return {"status": "UNVERIFIED", "reason": "Lean executable or proof files unavailable"}
    version = command([executable, "--version"], cwd=directory, env=os.environ.copy())
    if version["returncode"] != 0 or "version 4.23.0" not in version["stdout"]:
        return {"status": "FAIL", "reason": "Lean compiler version not pinned to v4.23.0",
                "version": version["stdout"].strip()}
    sanitized = strip_lean_comments(rank_source.read_text(encoding="utf-8"))
    escapes = sorted(set(FORBIDDEN.findall(sanitized)))
    if escapes:
        return {"status": "FAIL", "reason": "Forbidden proof escape in Lean code",
                "tokens": escapes}
    with TemporaryDirectory(prefix="astra-lean-rank10-") as temp:
        workspace = Path(temp)
        for name in ("RankTen.lean", "LowRankExact.lean"):
            shutil.copyfile(directory / name, workspace / name)
        env = {**os.environ, "LEAN_PATH": str(workspace)}
        base = command([executable, "-o", "LowRankExact.olean", "LowRankExact.lean"],
                       cwd=workspace, env=env)
        if base["returncode"] != 0:
            return {"status": "FAIL", "stage": "base_module", "logs": base}
        compiled = command([executable, "-o", "RankTen.olean", "RankTen.lean"],
                           cwd=workspace, env=env)
        if compiled["returncode"] != 0:
            return {"status": "FAIL", "stage": "rank10_module", "logs": compiled}
        audit_messages = {
            name: f"'AstraMath.RankTen.{name}' does not depend on any axioms"
            for name in REQUIRED
        }
        if not all(value in compiled["stdout"] for value in audit_messages.values()):
            return {"status": "FAIL", "stage": "kernel_axiom_audit",
                    "reason": "Expected axiom-free theorem output missing", "logs": compiled}
        # A deliberately unprovable equation must NOT compile.
        (workspace / "FalseClaim.lean").write_text(
            "import RankTen\nexample : (1 : Nat) = 2 := by decide\n",
            encoding="utf-8",
        )
        negative = command([executable, "FalseClaim.lean"], cwd=workspace, env=env)
        if negative["returncode"] == 0:
            return {"status": "FAIL", "stage": "negative_false_lean_theorem_accepted"}
        return {"status": "PASS", "lean_version": version["stdout"].strip(),
                "source_sha256": sha256(rank_source),
                "base_source_sha256": sha256(base_source),
                "theorems_without_axioms": list(REQUIRED),
                "negative_false_statement_rejected": True,
                "scope": "finite rank-ten algebraic certificate; not Mathlib Matrix.rank"}


def proofgate_check(directory: Path) -> dict:
    rank_source = directory / "RankTen.lean"
    if not rank_source.is_file():
        return {"status": "FAIL", "reason": "missing Lean source"}
    source_content = rank_source.read_bytes()
    with TemporaryDirectory(prefix="astra-rank-proofgate-") as temp:
        workspace = Path(temp)
        copied = workspace / "RankTen.lean"
        copied.write_bytes(source_content)
        claim = {
            "id": "RANK10-LEAN-001",
            "title": "Exact rational rank-ten certificate on a finite 64-by-64 matrix",
            "scope": "finite",
            "artifact": "RankTen.lean",
            "sha256": hashlib.sha256(source_content).hexdigest(),
            "formal_statement": THEOREM,
            # CI evidence intentionally omitted: never invent a successful run.
        }
        path = workspace / "manifest.json"
        def check(c):
            path.write_text(json.dumps({"schema": "astra-prooflab-evidence/1",
                                        "name": "ASTRA rank10", "claims": [c]}))
            return audit(path)["claims"][0]
        base = check(claim)
        # ProofGate must reject (a) source-byte tampering and (b) proof escape.
        copied.write_bytes(source_content + b"\n-- tampered\n")
        tamper = check(claim)
        copied.write_text("theorem fake : True := by sorry\n", encoding="utf-8")
        escaped = check({**claim, "sha256": sha256(copied)})
        copied.write_bytes(source_content)
        nonexistent_statement = check({
            **claim, "formal_statement": "theorem missing : False := by trivial"
        })
        negatives = {"tampered_source_rejected": tamper["status"] == "FAIL",
                     "sorry_rejected": escaped["status"] == "FAIL",
                     "incorrect_theorem_rejected": nonexistent_statement["status"] == "FAIL"}
        checks = {"SHA256_MATCH", "NO_COMMON_PROOF_ESCAPES",
                  "FORMAL_THEOREM_STATEMENT_MATCH"}
        valid = (checks <= set(base["checks"]) and
                 base["status"] == "UNVERIFIED" and all(negatives.values()))
        return {
            "status": "PASS" if valid else "FAIL",
            "proofgate_claim_status": base["status"],
            "local_source_validation_checks": base["checks"],
            "negative_controls": negatives,
            "remote_ci_binding": "UNVERIFIED",
            "reason": "ProofGate correctly withholds independent-CI PASS until a linked completed run exists",
        }


def verify(directory: Path = HERE) -> dict:
    engine = research(directory)
    formal = lean_check(directory)
    gate = proofgate_check(directory)
    engine_ok = (engine["claim_status"] == "PASS" and
                 engine["integration_with_existing_astra"]["status"] == "PASS" and
                 engine["results"]["rank_Q_I_minus_M0"] == 10 and
                 engine["controls"]["changed_coefficient_rejected"] and
                 engine["controls"]["false_rank_M0_equals_10_rejected"])
    local_ok = engine_ok and formal["status"] == "PASS" and gate["status"] == "PASS"
    if formal["status"] == "FAIL" or gate["status"] == "FAIL" or not engine_ok:
        overall = "FAIL"
    elif local_ok:
        overall = "PARTIAL"   # Independent SHA-bound CI still UNVERIFIED.
    else:
        overall = "UNVERIFIED"
    result = {
        "schema": "astra-rank10-evidence/1",
        "claim": "rank_Q(I-M0)=10 for the explicit r=2,Q=3,R=2,A0=0 matrix",
        "scope": "finite 64x64 matrix only",
        "local_mathematical_status": "PASS" if local_ok else (
            "FAIL" if overall == "FAIL" else "UNVERIFIED"),
        "overall_status": overall,
        "exact_python_engine": {
            "status": "PASS" if engine_ok else "FAIL",
            "receipt_sha256": engine["receipt_sha256"],
            "integration": engine["integration_with_existing_astra"],
            "results": engine["results"],
            "controls": engine["controls"],
        },
        "lean_kernel": formal,
        "proof_gate": gate,
        "limitations": [
            "Lean certificate proves finite matrix identities, eigenvectors and orthogonality; not a Mathlib Matrix.rank statement.",
            "The inference rank=10 uses standard finite-dimensional linear algebra over the rationals.",
            "GitHub CI immutable-run binding not yet evidenced for this new theorem.",
            "Not a general SAT complexity theorem or Yang-Mills mass-gap result.",
            "No persistent autonomous execution.",
        ],
    }
    result["receipt_sha256"] = canonical_sha(result)
    return result


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--directory", type=Path, default=HERE)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    result = verify(args.directory)
    encoded = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded)
    return 2 if result["overall_status"] == "FAIL" else (
        1 if result["overall_status"] == "UNVERIFIED" else 0)


if __name__ == "__main__":
    sys.exit(main())
