# Exact Reconstruction of Reflected-Cap Data from an Erased Flat Boundary

Companion package for the paper

> **Exact Reconstruction of Reflected-Cap Data from an Erased Flat Boundary**
> Oleksiy Babanskyy.

PDF: [`paper/Exact_Reconstruction_of_Reflected-Cap_Data_from_an_Erased_Flat_Boundary.pdf`](paper/Exact_Reconstruction_of_Reflected-Cap_Data_from_an_Erased_Flat_Boundary.pdf).

The paper studies a three-dimensional convex polytope whose facet reflections
are independently rotated. In the **proper-zero** regime at least one cap is
nonflat and at least one cap is flat. Flat caps merge with the core and erase
their internal source seams; only the resulting raw union is observed.

## Main result

Every exact three-dimensional proper-zero raw union has exactly one compatible
decomposition in the model stated in the paper. No genericity hypothesis and
no bound on the number of facets is required.

The proof starts from any recovered visible hinge and repeats four intrinsic
steps:

1. a frontier ridge exposes the second **oriented** boundary ray in its normal
   quotient, even when two supporting rays fuse into one straight line;
2. projection to that ridge and equality of the reflected radius recover one
   new site;
3. the unique strict-bisector component containing that site recovers the full
   cap and its base;
4. connectivity of the facet-adjacency graph propagates the reconstruction to
   every hidden facet.

Comparing two arbitrary compatible decompositions under the same intrinsic
procedure forces them to agree facet by facet. The finite replay below checks
implementations and adversarial controls; it is not used as the proof.

## Additional results retained in the paper

- An auxiliary boundary-germ signature reconstructs in one shot away from a
  finite algebraic exceptional set for each fixed realized core and visible
  mask. This exceptional set limits the shortcut, not the main theorem.
- Hypothetical competing decompositions would differ in at least five reflected
  sites on each side. Its spherical-configuration step is computer-assisted by
  four exact polynomial identities re-verified from the shipped certificate
  files.
- The reference signature implementation has a two-condition certifier. E-A61
  and E-A63 show independently that neither condition can be discarded.

## Executable evidence

The companion ships the seven audits cited by the manuscript:

- **E-A58:** auxiliary signature reconstruction on all 16,744 frozen corpus
  rows and exact two-condition certification on 340 deterministic samples;
- **E-A60:** intrinsic boundary-germ extraction on all 16,744 rows, including
  subdivision and independent-extractor controls;
- **E-A61/E-A63:** the two complementary certifier failure families;
- **E-A69:** exact expansion of the four polynomial certificate identities and
  the elementary endgame;
- **E-A71:** 16,759 exact data and 189,128 oriented local-ridge steps;
- **E-A72:** an independent source-scrubbed global engine on 16,759 exact data,
  61,030 BFS/component steps, 34,090 ridge-touch ambiguities disambiguated by
  the recovered site, zero mismatches, and four deliberate faults killed.

All geometry and certificate comparisons are exact. E-A69 uses SymPy 1.14 and
mpmath 1.3.0; the remaining package is standard-library Python.

## Quick verification

```bash
python scripts/check_manifest.py --closed-tree
python -m unittest discover -s tests
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/check_attestation.py
python scripts/verify_manifest_only.py
```

Normal and optimized aggregate runs must produce byte-identical receipts. The
last command copies only source-manifest files into an isolated temporary tree
and repeats both modes, detecting private-workspace or unmanifested
dependencies. See [`REPRODUCE.md`](REPRODUCE.md) for the complete contract.

## Claim boundary

The public theorem is exact and three-dimensional. This repository does not
claim:

- all-zero reconstruction, where no visible hinge initializes propagation;
- a theorem above dimension three;
- extraction from point clouds, floating-point meshes, or implicit-set oracles;
- numerical stability or noise robustness;
- that E-A72 is an end-to-end general polyhedral component engine;
- completeness of the auxiliary two-condition certifier;
- novelty, priority, or firstness relative to all prior work.

Read [`docs/PUBLIC_CLAIM_BOUNDARY.md`](docs/PUBLIC_CLAIM_BOUNDARY.md) before
citing the result and [`docs/SOURCE_LOCK.md`](docs/SOURCE_LOCK.md) for exact
source status. Related supplied-tessellation, inverse Voronoi, Laguerre-moment,
and travel-time models are compared in the paper and
[`docs/PRIOR_ART.md`](docs/PRIOR_ART.md) without importing their conclusions.

## Repository layout

```text
paper/        manuscript source, bibliography, and one title-named PDF
scripts/      exact geometry, replay, integrity, and isolated-replay tools
certificates/ four E-A69 cofactors plus provenance/search drivers
results/      frozen E-A58/E-A60/E-A61/E-A63/E-A69/E-A71/E-A72 records
tests/        source-free, certification, propagation, mutation, and trust gates
docs/         claim, source, prior-art, red-team, artifact, and release records
```

Original repository content is MIT licensed. `LICENSE_SCOPE.md` and
`THIRD_PARTY_NOTICES.md` describe the citation-only third-party boundary; no
third-party paper or dataset is redistributed here.
