# Artifact map

| Purpose | Artifact |
|---|---|
| Manuscript source | <code>paper/main.tex</code>, <code>paper/references.bib</code> |
| Compiled manuscript | <code>paper/Generic_Exact_Reconstruction_of_Reflected_Cap_Data_from_an_Erased_Flat_Boundary.pdf</code> |
| Exact rational geometry | <code>scripts/p43_s90_exact_rational_kernel.py</code> |
| Six-vertex type census lock | <code>results/P43_S50_E_A22_PHASE1_SIX_VERTEX_CORE_CENSUS.json</code> |
| Deterministic frozen corpus | S90/S91/S97 modules under <code>scripts/</code> |
| Degenerate witness | <code>scripts/p43_s101_e_a57_skeleton_definition_witness.py</code> |
| Intrinsic skeleton replay | <code>scripts/p43_s106_e_a60_intrinsic_germ_skeleton.py</code> and corresponding JSON |
| Flat reconstruction replay (two-condition certifier) | <code>scripts/p43_s102_e_a58_reference_reconstruction.py</code> and corresponding JSON |
| Exceptional-centre witnesses (flat-only accepts, two-condition rejects) | <code>scripts/p43_s109_e_a61_exceptional_centre_witness.py</code> and corresponding JSON |
| Reversed witnesses (hinges survive, flat differs) | <code>scripts/p43_s111_e_a63_volume_branch_witness.py</code> and corresponding JSON; <code>scripts/p43_s110_e_a62_exceptional_ambiguity_decision.py</code> is its import dependency (no receipt shipped) |
| Theorem 7.6 certificates | four cofactor files under <code>certificates/</code>, hash-pinned by the E-A69 receipt |
| Certificate verification (exact expansion + endgame) | <code>scripts/p43_s122_e_a69_branch3_exact_closure.py</code> and corresponding JSON |
| Certificate provenance (search/control drivers, computed bases) | <code>certificates/*.sing</code>, <code>certificates/*_SATURATED_GB_*.txt</code> (not proof dependencies) |
| Focused controls | <code>tests/test_public_kernel.py</code> |
| One-command replay | <code>scripts/verify_all.py</code> |
| Integrity/isolated gates | <code>scripts/check_manifest.py</code>, <code>scripts/check_attestation.py</code>, <code>scripts/verify_manifest_only.py</code> |
| Library modules imported by the replay whose own historical receipts are not shipped (not directly executable here) | <code>p43_s100_e_a56...</code>, <code>p43_s101_e_a57...</code>, <code>p43_s97_e_a50...</code>, <code>p43_s91_e_a44/45...</code> |
| Claims and exclusions | <code>docs/CLAIM_LEDGER.md</code>, <code>docs/PUBLIC_CLAIM_BOUNDARY.md</code> |
| Prior art and sources | <code>docs/SOURCE_LOCK.md</code>, <code>docs/PRIOR_ART.md</code> |
| Adversarial audit | <code>docs/RED_TEAM_REPORT.md</code> |
