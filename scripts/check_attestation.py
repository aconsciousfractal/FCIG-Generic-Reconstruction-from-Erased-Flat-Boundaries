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
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_REAL = ROOT.resolve(strict=True)
ATTESTATION = ROOT / "RELEASE_ATTESTATION.json"


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


def main() -> None:
    require(ATTESTATION.is_file(), "missing RELEASE_ATTESTATION.json")
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    artifacts = attestation["artifacts"]
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
        checked += 1
    certificates = artifacts.get("theorem_7_6_certificates", {})
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
    print(f"PASS_ATTESTATION_ANCHORED checks={checked}")


if __name__ == "__main__":
    main()
