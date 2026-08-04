# Artifact map

This repository is the complete companion package for the paper. Public paths
are relative to the repository root.

| Role | Artifact |
| --- | --- |
| Manuscript source | `paper/main.tex`, `paper/references.bib` |
| Compiled manuscript | `paper/Exact_Reconstruction_of_Reflected-Cap_Data_from_an_Erased_Flat_Boundary.pdf` |
| Closed-tree source manifest | `MANIFEST_SHA256.txt` |
| Release attestation | `RELEASE_ATTESTATION.json` |
| Aggregate verifier | `scripts/verify_all.py` |
| Isolated manifest-only replay | `scripts/verify_manifest_only.py` |
| Manifest and attestation gates | `scripts/check_manifest.py`, `scripts/check_attestation.py` |
| E-A58 auxiliary signature/certifier kernel | `scripts/p43_s102_e_a58_reference_reconstruction.py`, matching JSON under `results/` |
| E-A60 intrinsic germ-skeleton audit | `scripts/p43_s106_e_a60_intrinsic_germ_skeleton.py`, matching JSON under `results/` |
| E-A61 flat-only failure witnesses | `scripts/p43_s109_e_a61_exceptional_centre_witness.py`, matching JSON under `results/` |
| E-A63 reversed certifier witnesses | `scripts/p43_s111_e_a63_volume_branch_witness.py`, matching JSON under `results/` |
| E-A69 polynomial certificate verification | `scripts/p43_s122_e_a69_branch3_exact_closure.py`, matching JSON and files under `certificates/` |
| E-A71 oriented local-ridge audit | `scripts/p43_s131_e_a71_ridge_germ_propagation_audit.py`, matching JSON under `results/` |
| E-A72 independent global propagation | `scripts/p43_s133_e_a72_independent_global_propagation.py`, matching JSON under `results/` |
| Focused regressions | `tests/test_public_kernel.py`, `tests/test_universal_propagation.py` |
| Claim/source boundaries | `docs/CLAIM_LEDGER.md`, `docs/SOURCE_LOCK.md`, `docs/PUBLIC_CLAIM_BOUNDARY.md` |

The E-A identifiers are local experiment locators, not literature citations.
The JSON records pin the canonical mathematical payloads; the source manifest
pins shipped source bytes; the attestation binds the manifest, title-named PDF,
aggregate receipt, and four E-A69 certificate files.

The compiled PDF, release attestation, source manifest itself, regenerated
aggregate receipt, and LaTeX auxiliary files are excluded from the source
manifest to avoid circular hashing. Their exact public-release hashes are
recorded in `RELEASE_ATTESTATION.json`.
