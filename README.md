# Generic Exact Reconstruction of Reflected-Cap Data from an Erased Flat Boundary

Companion package for the paper

> **Generic Exact Reconstruction of Reflected-Cap Data from an Erased Flat Boundary**  
> Oleksiy Babanskyy, 2026.

PDF: [paper/Generic_Exact_Reconstruction_of_Reflected_Cap_Data_from_an_Erased_Flat_Boundary.pdf](paper/Generic_Exact_Reconstruction_of_Reflected_Cap_Data_from_an_Erased_Flat_Boundary.pdf).

## S108 application and prior-art audit

Primary-source checking corrected one overbroad comparison: inverse tessellation
problems do not always receive boundary edges. Labelled Laguerre cells can be
recovered from volumes and centroids, and a simplified ultrasonic NDT model fits
an oriented planar Voronoi diagram from travel times. Those observables are not
the reflected-cap raw union used here. Other inverse Voronoi and Laguerre methods
start from a supplied planar tessellation, weighted cell partition, or spherical
tessellation, even when they propagate generators by reflection; those source
boundaries have already been erased in the present model. Brillouin zones share the local
perpendicular-bisector construction, but diffraction extinctions do not erase
zone faces. EBSD, NDT and lattice models are research bridges, not current
deployments; prescribed-crease origami hardness does not transfer to this inverse
problem. See the source lock and red-team report.

## What the paper proves

A convex three-polytope lies in a hyperplane of four-space. Its interior
centre is reflected across every facet, producing one pyramidal cap per
facet; the caps are then independently rotated about their base facets. In
the proper-zero regime, at least one cap is nonflat and at least one is flat.
The flat caps merge with the core and erase their internal source seams.

The paper defines a source-free boundary-germ skeleton of that merged flat
component. If no core vertex passes the intrinsic bisector-neighbour test, the
passing skeleton vertices are exactly the hidden reflected apexes, the core is
recovered by exact halfspace intersection, and every compatible decomposition
is unique. For each fixed realized core and visible-facet mask, excluded
centres lie in a finite union of proper spheres and quadrics and therefore
have Lebesgue measure zero.

Beyond the conditional statement, the paper proves two unconditional
structure results. Uniqueness holds whenever every passing core vertex lies
on a visible hinge facet (Theorem 7.2). Any two distinct compatible
decompositions differ in at least five reflected sites on each side
(Theorem 7.8), so a proper-zero datum with at most four hidden facets is
unique with no hypothesis on its centre (Corollary 7.9). The five-site bound
rests on a nonexistence theorem for an eight-point spherical configuration
(Theorem 7.6), proved by four polynomial certificate identities archived
under <code>certificates/</code> and re-verified by exact expansion, plus an
elementary positivity analysis.

## Evidence boundary

- The frozen corpus is the complete six-vertex census: 35 exactly
  constructed rational realizations of the seven six-vertex core types, four
  interior centres each, all visible-facet masks — 16,744 rows.
- E-A60 reconstructs all 16,744 rows in the frozen exact-rational corpus,
  checks 256 boundary-subdivision mutations (a deterministic corpus prefix),
  256 independent maximal-sheet extractions, and the swallowed-corner witness.
- E-A58 reconstructs all 16,744 frozen rows with the steps-4-to-6 flat kernel
  and exactly certifies 340 deterministic samples with the two-condition
  certifier (flat-component equality and hinge-facet survival), with zero
  wrong answers.
- E-A61 builds six exact exceptional-centre witnesses on which the flat-only
  comparison accepts a wrong reconstruction and the two-condition certifier
  rejects it; E-A63 builds three reversed witnesses where the hinge condition
  holds and the flat comparison fails. Each condition is necessary.
- E-A69 re-verifies the four certificate identities of Theorem 7.6 by exact
  expansion (SymPy) and re-runs the elementary endgame with its standing
  positive controls.
- These finite replays verify the implementation and the certificates on the
  frozen domain. The proof is the intrinsic argument in the manuscript.

## What is not claimed

- uniqueness at exceptional centres with five or more hidden facets;
- a theorem in dimension greater than three;
- extraction from point clouds, floating-point meshes, or implicit-set oracles;
- a full end-to-end implementation of conceptual steps 1 to 3;
- completeness of the two certifier conditions;
- novelty, priority, or firstness relative to every possible prior work.

## Quick start

~~~bash
python scripts/check_manifest.py --closed-tree
python -m unittest discover -s tests
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/check_attestation.py
python scripts/verify_manifest_only.py
~~~

The package uses exact rational arithmetic throughout. Its pinned third-party
dependencies are SymPy, used to re-verify the certificate identities by exact
expansion, and mpmath, SymPy's arithmetic backend (`pip install -r
requirements.txt`). The complete replay is intentionally substantial; runtime
is hardware-dependent.

## Layout

~~~text
paper/        manuscript source, bibliography, and title-named PDF
scripts/      exact geometry, replay, integrity, and isolated-replay tools
certificates/ the four Theorem 7.6 cofactor files and the search/control
              drivers that produced them
results/      frozen E-A58/E-A60/E-A61/E-A63/E-A69 receipts and the
              regenerated package receipt
tests/        focused source-free, certification, and necessity controls
docs/         claim, source, prior-art, red-team, artifact, and release boundaries
~~~

The replay is standard-library Python except for the certificate
verification, which uses SymPy for exact polynomial expansion (see
<code>requirements.txt</code>). Original content is covered by the MIT
<code>LICENSE</code>; see <code>LICENSE_SCOPE.md</code> and
<code>THIRD_PARTY_NOTICES.md</code>.
