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
the reflected-cap raw union used here. Brillouin zones share the local
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

## Evidence boundary

- E-A60 reconstructs all 16,744 rows in the frozen exact-rational corpus,
  checks 256 boundary-subdivision mutations, 256 independent maximal-sheet
  extractions, and the swallowed-corner witness.
- E-A58 reconstructs all 16,744 frozen rows with the steps-4-to-6 flat kernel
  and exactly certifies 340 deterministic samples, with zero wrong answers.
- These finite replays verify the implementation on the frozen domain. The
  proof is the intrinsic argument in the manuscript.

## What is not claimed

- uniqueness at exceptional centres;
- a theorem in dimension greater than three;
- extraction from point clouds, floating-point meshes, or implicit-set oracles;
- a full end-to-end implementation of conceptual steps 1 to 3;
- novelty, priority, or firstness relative to every possible prior work.

## Quick start

~~~bash
python scripts/check_manifest.py --closed-tree
python -m unittest discover -s tests
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/verify_manifest_only.py
~~~

The package is standard-library Python and uses exact rational arithmetic.
The complete replay is intentionally substantial; runtime is hardware-dependent.

## Layout

~~~text
paper/    manuscript source, bibliography, and title-named PDF
scripts/  exact geometry, replay, integrity, and isolated-replay tools
results/  frozen E-A58/E-A60 receipts and regenerated package receipt
tests/    focused source-free and certification controls
docs/     claim, source, prior-art, red-team, artifact, and release boundaries
~~~

Original content is covered by the MIT <code>LICENSE</code>; see
<code>LICENSE_SCOPE.md</code> and <code>THIRD_PARTY_NOTICES.md</code>.
