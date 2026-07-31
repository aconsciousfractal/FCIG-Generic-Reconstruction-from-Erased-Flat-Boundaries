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


def main() -> None:
    require(ATTESTATION.is_file(), "missing RELEASE_ATTESTATION.json")
    attestation = json.loads(ATTESTATION.read_text(encoding="utf-8"))
    artifacts = attestation["artifacts"]
    checked = 0
    for key in ("source_manifest", "paper_pdf", "aggregate_receipt"):
        entry = artifacts[key]
        path = ROOT / entry["path"]
        require(path.is_file(), f"attested file missing: {entry['path']}")
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
        path = ROOT / "certificates" / name
        require(path.is_file(), f"attested certificate missing: {name}")
        actual = sha256_file(path)
        require(
            actual == str(pinned).upper(),
            f"certificate {name}: attested {pinned}, actual {actual}",
        )
        checked += 1
    print(f"PASS_ATTESTATION_ANCHORED checks={checked}")


if __name__ == "__main__":
    main()
