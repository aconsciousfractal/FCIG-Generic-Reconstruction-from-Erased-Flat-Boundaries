#!/usr/bin/env python3
"""Fail-closed anchor check: the attestation must match the tree it describes.

Recomputes the SHA-256 of the source manifest, the title-named PDF and the
regenerated aggregate receipt, and compares each against the values bound by
``RELEASE_ATTESTATION.json``.  Run this after ``verify_all.py`` so the receipt
on disk is the freshly regenerated one; the receipt is deterministic, so any
divergence from the attested value is a real change.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_REAL = ROOT.resolve(strict=True)
ATTESTATION = ROOT / "RELEASE_ATTESTATION.json"
EXPECTED_SCHEMA = "P43-S136-RELEASE-ATTESTATION-v7"
EXPECTED_ARTIFACT_PATHS = {
    "source_manifest": "MANIFEST_SHA256.txt",
    "paper_pdf": (
        "paper/Exact_Reconstruction_of_Reflected-Cap_Data_"
        "from_an_Erased_Flat_Boundary.pdf"
    ),
    "aggregate_receipt": "results/public_package_verification.json",
}
EXPECTED_CERTIFICATE_NAMES = {
    "P43_S122_E_A69_COFACTORS_G1.txt",
    "P43_S122_E_A69_COFACTORS_L12_34.txt",
    "P43_S122_E_A69_COFACTORS_L13_24.txt",
    "P43_S122_E_A69_COFACTORS_L14_23.txt",
}
EXPECTED_PAYLOAD_KEYS = {
    "intrinsic_germ_skeleton_e_a60": "E_A60_payload",
    "two_condition_flat_kernel_e_a58_v3": "E_A58_payload",
    "exceptional_centre_witnesses_e_a61": "E_A61_payload",
    "reversed_witnesses_e_a63": "E_A63_payload",
    "certificate_closure_e_a69": "E_A69_payload",
    "oriented_local_ridge_audit_e_a71": "E_A71_payload",
    "independent_global_propagation_e_a72": "E_A72_payload",
}
EXPECTED_MANIFEST_ENTRIES = 60
EXPECTED_PDF_PAGES = 20
EXPECTED_CHECKS = 7


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_attested_path(relative: object) -> Path:
    """Resolve a repository-relative regular file without following symlinks."""
    require(isinstance(relative, str) and relative, "invalid attested path")
    require("\\" not in relative, f"nonportable attested path: {relative}")
    candidate = Path(relative)
    require(
        not candidate.is_absolute() and ".." not in candidate.parts,
        f"unsafe attested path: {relative}",
    )
    cursor = ROOT
    for part in candidate.parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), f"symlink in attested path: {relative}")
    require(cursor.is_file(), f"attested file missing: {relative}")
    resolved = cursor.resolve(strict=True)
    require(
        resolved.is_relative_to(ROOT_REAL),
        f"attested path escapes repository: {relative}",
    )
    return resolved


def validate_attestation_shape(attestation: object) -> dict:
    """Require the exact release-attestation roles before trusting any hash."""
    require(isinstance(attestation, dict), "attestation must be a JSON object")
    require(
        attestation.get("schema") == EXPECTED_SCHEMA,
        f"unexpected attestation schema: {attestation.get('schema')}",
    )
    artifacts = attestation.get("artifacts")
    require(isinstance(artifacts, dict), "attestation artifacts must be an object")
    require(
        set(artifacts)
        == set(EXPECTED_ARTIFACT_PATHS)
        | {"exact_payloads", "theorem_7_6_certificates"},
        "attestation artifact roles are incomplete or unexpected",
    )
    for role, expected_path in EXPECTED_ARTIFACT_PATHS.items():
        entry = artifacts.get(role)
        require(isinstance(entry, dict), f"{role}: expected an object")
        require(
            entry.get("path") == expected_path,
            f"{role}: expected canonical path {expected_path}",
        )
    require(
        artifacts["source_manifest"].get("entries") == EXPECTED_MANIFEST_ENTRIES,
        f"source_manifest: expected {EXPECTED_MANIFEST_ENTRIES} entries",
    )
    require(
        artifacts["paper_pdf"].get("pages") == EXPECTED_PDF_PAGES,
        f"paper_pdf: expected {EXPECTED_PDF_PAGES} pages",
    )
    payloads = artifacts.get("exact_payloads")
    require(isinstance(payloads, dict), "exact_payloads must be an object")
    require(
        set(payloads) == set(EXPECTED_PAYLOAD_KEYS),
        "exact_payloads keys are incomplete or unexpected",
    )
    certificates = artifacts.get("theorem_7_6_certificates")
    require(
        isinstance(certificates, dict)
        and set(certificates) == EXPECTED_CERTIFICATE_NAMES,
        "theorem_7_6_certificates must contain exactly the four expected files",
    )
    return artifacts


def manifest_entry_count(path: Path) -> int:
    lines = path.read_text(encoding="utf-8").splitlines()
    return sum(1 for line in lines if line.strip() and not line.startswith("#"))


def pdf_page_count(path: Path) -> int:
    """Count page objects in the hash-pinned MiKTeX PDF without extra packages."""
    return len(re.findall(rb"/Type\s*/Page\b", path.read_bytes()))


def main() -> None:
    require(ATTESTATION.is_file(), "missing RELEASE_ATTESTATION.json")
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    artifacts = validate_attestation_shape(attestation)
    checked = 0
    for key in ("source_manifest", "paper_pdf", "aggregate_receipt"):
        entry = artifacts[key]
        path = safe_attested_path(entry["path"])
        actual = sha256_file(path)
        require(
            actual == str(entry["sha256"]).upper(),
            f"{key}: attested {entry['sha256']}, actual {actual}",
        )
        if "bytes" in entry:
            require(
                path.stat().st_size == entry["bytes"],
                f"{key}: attested {entry['bytes']} bytes, "
                f"actual {path.stat().st_size}",
            )
        if key == "source_manifest":
            require(
                manifest_entry_count(path) == entry["entries"],
                "source_manifest: declared and actual entry counts differ",
            )
        if key == "paper_pdf":
            require(
                pdf_page_count(path) == entry["pages"],
                "paper_pdf: declared and actual page counts differ",
            )
        checked += 1
    receipt = json.loads(
        safe_attested_path(EXPECTED_ARTIFACT_PATHS["aggregate_receipt"]).read_text(
            encoding="utf-8"
        )
    )
    require(receipt.get("status") == "PASS", "aggregate receipt status is not PASS")
    require(
        receipt.get("manifest_sha256") == artifacts["source_manifest"]["sha256"],
        "aggregate receipt does not bind the attested manifest",
    )
    for attested_key, receipt_key in EXPECTED_PAYLOAD_KEYS.items():
        require(
            artifacts["exact_payloads"][attested_key]
            == receipt.get("checks", {}).get(receipt_key),
            f"exact payload mismatch for {attested_key}",
        )
    certificates = artifacts["theorem_7_6_certificates"]
    for name, pinned in certificates.items():
        require(
            isinstance(name, str) and Path(name).name == name,
            f"unsafe certificate name: {name}",
        )
        path = safe_attested_path(f"certificates/{name}")
        actual = sha256_file(path)
        require(
            actual == str(pinned).upper(),
            f"certificate {name}: attested {pinned}, actual {actual}",
        )
        checked += 1
    require(checked == EXPECTED_CHECKS, f"expected {EXPECTED_CHECKS} checks, ran {checked}")
    print(f"PASS_ATTESTATION_ANCHORED checks={checked}")


if __name__ == "__main__":
    main()
