#!/usr/bin/env python3
"""Fail-closed one-command verifier for the P43 public package."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RESULTS = ROOT / "results"
OUTPUT = RESULTS / "public_package_verification.json"
SCHEMA = "P43-PUBLIC-PACKAGE-VERIFICATION-v2"
E60_PAYLOAD = "D18C07176BAF7B729A550E9B9B8B9D9E04BB58A0C52D295243108417C9BE785A"
E58_PAYLOAD = "3C58C0B88081380C7D22993A6FEE3B4EC9FE1A8C3D0CDC107BE9D40C33BA4ACC"
E61_PAYLOAD = "76956805B0BA304142CB08D833FA1179876A9F2154A76CE6C5A232BEF9E3F7F1"
E63_PAYLOAD = "50B26633575C81C67AD3A9857DC5BE1227B512E21CC98168EECEC37B360DB1A8"
E69_PAYLOAD = "5DC4C5800572C64F07C7A815CE7BEFFB930FEF03E04CC71679FB9501606F1D92"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def canonical_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=True, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def python_command(arguments: list[str]) -> list[str]:
    command = [sys.executable]
    if sys.flags.optimize:
        command.append("-O")
    command.extend(arguments)
    return command


def run(arguments: list[str]) -> str:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    command = python_command(arguments)
    completed = subprocess.run(
        command,
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=environment,
    )
    require(
        completed.returncode == 0,
        "command failed: " + " ".join(command)
        + f"\nstdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
    )
    return completed.stdout.strip()


def load_receipt(name: str) -> dict[str, Any]:
    path = RESULTS / name
    require(path.is_file(), f"missing frozen receipt: {name}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    manifest_stdout = run([str(SCRIPTS / "check_manifest.py"), "--closed-tree"])
    require(
        manifest_stdout.startswith("PASS_MANIFEST_"),
        f"unexpected manifest output: {manifest_stdout}",
    )

    tests_stdout = run(["-m", "unittest", "discover", "-s", "tests"])
    e60_stdout = run([
        str(SCRIPTS / "p43_s106_e_a60_intrinsic_germ_skeleton.py"),
        "--verify-existing",
    ])
    e58_stdout = run([
        str(SCRIPTS / "p43_s102_e_a58_reference_reconstruction.py"),
        "--verify-existing",
    ])
    e61_stdout = run([
        str(SCRIPTS / "p43_s109_e_a61_exceptional_centre_witness.py"),
        "--verify-existing",
    ])
    e63_stdout = run([
        str(SCRIPTS / "p43_s111_e_a63_volume_branch_witness.py"),
        "--verify-existing",
    ])
    e69_stdout = run([
        str(SCRIPTS / "p43_s122_e_a69_branch3_exact_closure.py"),
        "--verify-existing",
    ])

    e60 = load_receipt("P43_S106_E_A60_INTRINSIC_GERM_SKELETON.json")
    e58 = load_receipt("P43_S102_E_A58_REFERENCE_RECONSTRUCTION.json")
    e61 = load_receipt("P43_S109_E_A61_EXCEPTIONAL_CENTRE.json")
    e63 = load_receipt("P43_S111_E_A63_VOLUME_BRANCH.json")
    e69 = load_receipt("P43_S122_E_A69_BRANCH3_EXACT_CLOSURE.json")
    require(e60["canonical_mathematical_payload_sha256"] == E60_PAYLOAD, "E-A60 payload")
    require(e58["canonical_mathematical_payload_sha256"] == E58_PAYLOAD, "E-A58 payload")
    require(e61["canonical_mathematical_payload_sha256"] == E61_PAYLOAD, "E-A61 payload")
    require(e63["canonical_mathematical_payload_sha256"] == E63_PAYLOAD, "E-A63 payload")
    require(e69["payload_sha256"] == E69_PAYLOAD, "E-A69 payload")
    require(all(e60["assertions"].values()), "E-A60 assertion failure")
    require(all(e58["assertions"].values()), "E-A58 assertion failure")
    require(all(e61["assertions"].values()), "E-A61 assertion failure")
    require(all(e63["assertions"].values()), "E-A63 assertion failure")
    require(
        all(check["pass"] for check in e69["payload"]["checks"]),
        "E-A69 check failure",
    )
    for name, pinned in e69["payload"]["certificate_files"].items():
        require(
            sha256_file(ROOT / "certificates" / name) == pinned,
            f"certificate hash mismatch: {name}",
        )

    m60 = e60["metrics"]
    require(m60["rows_examined"] == 16744, "E-A60 row count")
    require(
        m60["rows_reconstructed_from_intrinsic_germ_skeleton"] == 16744,
        "E-A60 reconstruction count",
    )
    require(m60["subdivision_mutation_checks_invariant"] == 256, "E-A60 mutations")
    require(m60["maximal_sheet_cross_checks_agree"] == 256, "E-A60 cross-checks")
    require(m60["witness_reconstructed"], "E-A60 witness")

    m58 = e58["metrics"]
    require(m58["rows_examined"] == 16744, "E-A58 row count")
    require(m58["wrong_answers"] == 0, "E-A58 wrong answers")
    require(m58["certification_attempts"] == 340, "E-A58 certification attempts")
    require(m58["certified"] == 340, "E-A58 certifications")
    require(m58["wrong_and_certified"] == 0, "E-A58 false certification")
    require(
        m58["rejected_by_the_added_hinge_condition"] == 0,
        "E-A58 hinge condition must not reject a corpus certification",
    )
    require(
        m58["certified_by_the_flat_condition_alone"] == 340,
        "E-A58 flat-only agreement on the corpus sample",
    )
    require(m58["rows_where_historical_H_fails"] == 64, "historical H split")
    require(
        m58["rows_where_intrinsic_and_historical_candidate_sets_agree"] == 16744,
        "candidate regression count",
    )

    receipt = {
        "schema": SCHEMA,
        "status": "PASS",
        "manifest_sha256": sha256_file(ROOT / "MANIFEST_SHA256.txt"),
        "checks": {
            "focused_unit_tests": "PASS",
            "E_A60_payload": E60_PAYLOAD,
            "E_A58_payload": E58_PAYLOAD,
            "E_A61_payload": E61_PAYLOAD,
            "E_A63_payload": E63_PAYLOAD,
            "E_A69_payload": E69_PAYLOAD,
            "normal_or_optimized_mode": "optimized" if sys.flags.optimize else "normal",
        },
        "theorem_boundary": {
            "dimension": 3,
            "regime": "proper-zero reflected-cap data",
            "conditional_hypothesis": (
                "no core vertex passes the intrinsic bisector-neighbour test"
            ),
            "genericity": "fixed realized core and fixed visible mask",
            "unconditional_uniqueness": (
                "hinge-anchored (Theorem 7.2) and at most four hidden facets "
                "(Corollary 7.9)"
            ),
            "exchange_bound": (
                "two distinct compatible decompositions differ in at least "
                "five reflected sites per side (Theorem 7.8)"
            ),
            "certificates": (
                "Theorem 7.6 is computer-assisted; four identities archived "
                "under certificates/ and re-verified by exact expansion"
            ),
            "certifier": (
                "two conditions, each provably necessary; completeness not "
                "claimed"
            ),
            "exceptional_centres": "OPEN_FOR_FIVE_OR_MORE_HIDDEN_FACETS",
            "higher_dimensions": "OPEN",
            "end_to_end_input_extraction": "NOT_IMPLEMENTED",
            "novelty_or_priority": "NOT_CLAIMED",
        },
        "finite_evidence": {
            "rows": 16744,
            "E_A60_subdivision_mutations": 256,
            "E_A60_independent_extractor_checks": 256,
            "E_A58_exact_certifications": 340,
            "wrong_answers": 0,
            "wrong_and_certified": 0,
            "E_A61_exceptional_witnesses": 6,
            "E_A63_reversed_witnesses": 3,
            "E_A69_certificate_identities_verified": 4,
        },
    }
    # The receipt must be byte-identical under normal and optimized Python.
    receipt["checks"].pop("normal_or_optimized_mode")
    RESULTS.mkdir(exist_ok=True)
    OUTPUT.write_bytes(canonical_bytes(receipt))
    print(manifest_stdout)
    print(tests_stdout.splitlines()[-1] if tests_stdout else "PASS_UNIT_TESTS")
    print(e60_stdout.splitlines()[0])
    print(e58_stdout.splitlines()[0])
    print(e61_stdout.splitlines()[0])
    print(e63_stdout.splitlines()[0])
    print(e69_stdout.splitlines()[-1])
    print(f"RECEIPT_SHA256={sha256_file(OUTPUT)}")
    print("PASS_P43_PUBLIC_PACKAGE")


if __name__ == "__main__":
    main()
