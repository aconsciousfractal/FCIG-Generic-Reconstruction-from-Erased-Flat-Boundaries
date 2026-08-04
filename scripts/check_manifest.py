#!/usr/bin/env python3
"""Fail-closed SHA-256, reader-surface, and closed-tree package checker."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROOT_REAL = ROOT.resolve(strict=True)
MANIFEST = ROOT / "MANIFEST_SHA256.txt"
LINE = re.compile(r"^([0-9A-Fa-f]{64})  ([^\r\n]+)$")
PAPER_PDF = (
    "paper/Exact_Reconstruction_of_Reflected-Cap_Data_"
    "from_an_Erased_Flat_Boundary.pdf"
)
EXCLUDED = {
    "MANIFEST_SHA256.txt",
    "RELEASE_ATTESTATION.json",
    "results/public_package_verification.json",
    PAPER_PDF,
}
BUILD_SUFFIXES = {
    ".aux", ".bbl", ".blg", ".log", ".out", ".toc", ".fls",
    ".fdb_latexmk", ".synctex.gz",
}
BUILD_DIRECTORIES = {"__pycache__", ".pytest_cache", ".git", "tmp"}
RETIRED_READER_PATHS = {
    "docs/RELEASE_READINESS.md",
    "docs/RED_TEAM_REPORT.md",
}
RETIRED_READER_MARKERS = (
    "internal P43 registry",
    "P43-C",
    "private workspace",
    "release candidate",
    "docs/RELEASE_READINESS.md",
    "docs/RED_TEAM_REPORT.md",
    "internal adjudication",
    "S108",
    "S128",
    "S135",
    "S136",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest().upper()


def safe_manifest_path(relative: str, number: int) -> Path:
    require("\\" not in relative, f"nonportable path on line {number}")
    candidate = Path(relative)
    require(
        not candidate.is_absolute() and ".." not in candidate.parts,
        f"unsafe path on line {number}",
    )
    cursor = ROOT
    for part in candidate.parts:
        cursor = cursor / part
        require(not cursor.is_symlink(), f"symlink path on line {number}")
    require(cursor.is_file(), f"missing manifest file: {relative}")
    resolved = cursor.resolve(strict=True)
    require(
        resolved.is_relative_to(ROOT_REAL),
        f"manifest path escapes repository: {relative}",
    )
    return resolved


def is_build_artifact(relative: str) -> bool:
    path = Path(relative)
    return (
        path.suffix in {".pyc", ".pyo"}
        or (
            path.parts
            and path.parts[0] == "paper"
            and any(relative.endswith(suffix) for suffix in BUILD_SUFFIXES)
        )
    )


def source_inventory() -> list[str]:
    actual: list[str] = []
    for directory, directories, files in os.walk(ROOT, followlinks=False):
        base = Path(directory)
        kept = []
        for name in directories:
            child = base / name
            relative = child.relative_to(ROOT).as_posix()
            if name in BUILD_DIRECTORIES:
                continue
            require(not child.is_symlink(), f"symlink directory: {relative}")
            kept.append(name)
        directories[:] = kept
        for name in files:
            path = base / name
            relative = path.relative_to(ROOT).as_posix()
            require(not path.is_symlink(), f"symlink file: {relative}")
            resolved = path.resolve(strict=True)
            require(
                resolved.is_relative_to(ROOT_REAL),
                f"file escapes repository: {relative}",
            )
            if relative in EXCLUDED or is_build_artifact(relative):
                continue
            actual.append(relative)
    return sorted(actual)


def write_manifest() -> None:
    lines = [
        "# Generic Reconstruction public source manifest; SHA-256 uppercase; path relative to repository root.",
    ]
    lines.extend(
        f"{sha256_file(ROOT / relative)}  {relative}"
        for relative in source_inventory()
        if relative != MANIFEST.name
    )
    MANIFEST.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def check_reader_surface() -> None:
    for relative in RETIRED_READER_PATHS:
        require(not (ROOT / relative).exists(), f"retired reader path present: {relative}")
    readers = sorted(ROOT.glob("*.md")) + sorted(ROOT.glob("*.cff"))
    readers += sorted((ROOT / "docs").glob("*.md"))
    readers += [ROOT / "paper" / "main.tex", ROOT / "paper" / "references.bib"]
    offenders: list[str] = []
    for path in readers:
        text = path.read_text(encoding="utf-8")
        if any(marker in text for marker in RETIRED_READER_MARKERS):
            offenders.append(path.relative_to(ROOT).as_posix())
    require(not offenders, "retired reader-surface residue: " + ", ".join(offenders))


def closed_tree_check(seen: set[str]) -> None:
    actual = set(source_inventory())
    unmanifested = sorted(actual - seen)
    require(
        not unmanifested,
        "unmanifested package files: " + ", ".join(unmanifested),
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--closed-tree", action="store_true")
    parser.add_argument("--write-manifest", action="store_true")
    args = parser.parse_args()
    if args.write_manifest:
        write_manifest()
        print("MANIFEST_WRITTEN")
    require(MANIFEST.is_file(), "missing MANIFEST_SHA256.txt")
    checked = 0
    seen: set[str] = set()
    for number, raw_line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line or raw_line.startswith("#"):
            continue
        match = LINE.fullmatch(raw_line)
        require(match is not None, f"malformed manifest line {number}")
        expected, relative = match.groups()
        require(relative not in seen, f"duplicate manifest path: {relative}")
        seen.add(relative)
        actual = sha256_file(safe_manifest_path(relative, number))
        require(
            actual == expected.upper(),
            f"SHA-256 mismatch for {relative}: {actual} != {expected.upper()}",
        )
        checked += 1
    require(checked > 0, "empty manifest")
    check_reader_surface()
    if args.closed_tree:
        closed_tree_check(seen)
    suffix = "_CLOSED_TREE" if args.closed_tree else ""
    print(f"PASS_MANIFEST_{checked}_FILES{suffix}")


if __name__ == "__main__":
    main()
