# Claim ledger

## C1 — exact contact complex

**Status:** proved in manuscript Proposition 2.1.
**Registry:** P43-C025, level CL5 (internal theorem).

For every angle vector in the stated open range, each cap meets the core in
its hinge facet and two distinct caps meet only in the corresponding core-face
intersection. Unit facet normals are part of the model.

## C2 — intrinsic proper-zero recovery

**Status:** proved in manuscript Proposition 3.1.
**Registry:** P43-C032, level CL5 (internal theorem).

The bare raw union determines the merged flat component, nonflat caps, visible
hinges, centre, and fully reflected sites for the nonflat hinges. The component
rule is adjacency-star centre except in the two-component case, where intrinsic
volume distinguishes the merged component.

## C3 — conditional exact reconstruction and uniqueness

**Status:** proved in manuscript Theorem 5.6.
**Registry:** P43-C088, level CL5 (internal theorem).

The authoritative graph is the intrinsic noncoplanar crease graph of maximal
exposed planar sheet germs. If no core vertex passes the bisector-neighbour
test, the passing graph vertices are exactly the hidden reflected apexes. The
core and every compatible datum are unique.

## C4 — fixed-realization genericity

**Status:** proved in manuscript Theorem 6.1.
**Registry:** P43-C088 (same claim, genericity clause), level CL5.

For each fixed realized three-polytope and fixed visible mask, centres at which
a core vertex passes are contained in a finite union of proper spheres and
quadrics, hence form a measure-zero set. No closedness or varying-realization
measure statement is included.

## C5 — reference algorithm and finite replay

**Status:** exact implementation evidence.
**Registry:** P43-C087, level CL3 (certified finite result), for the replay; P43-C092, level CL5, for the cost bound.

E-A60 is the observable skeleton replay. E-A58 implements only conceptual
steps 4 to 6 with the two-condition certifier: flat-component equality and
survival of every recovered visible hinge facet. Each condition is provably
necessary (E-A61 and E-A63 witnesses); completeness of the pair is not
claimed. The conservative reference bound is O(N^2 log N + k^4) exact field
operations — the halfspace kernel enumerates plane triples and validates each
candidate corner against every halfspace. (An earlier revision stated k^3,
omitting the per-candidate scan; corrected here.) The finite candidate-set
cross-check is regression evidence, not a general theorem.

## C6 — application boundary

**Status:** verified comparison, not an application theorem.
**Registry:** boundary statement under the S108 source lock; no theorem claim is registered or made.

The result currently supplies an exact inverse theorem, a certifying reference
algorithm and a 16,744-row adversarial corpus for its promised reflected-cap
class. Laguerre moments, ultrasonic NDT, EBSD microstructure reconstruction and
lattice Brillouin models are adjacent bridge targets. A direct application would
first require a generative reduction to reflected-cap data and a stability or
interval-certificate theorem.

## C7 — hinge-anchored uniqueness

**Status:** proved in manuscript Theorem 7.2.
**Registry:** P43-C089, level CL5 (internal theorem).

If every core vertex that passes the bisector-neighbour test lies on at least
one visible hinge facet, the compatible decomposition is unique. Theorem 5.6
is the special case in which no core vertex passes. A site of one compatible
decomposition absent from the other is a passing core vertex of the other
lying on no visible hinge facet.

## C8 — no exchange quadruple

**Status:** proved in manuscript Theorem 7.6; computer-assisted with
independently verified certificates.
**Registry:** P43-C090, level CL5 (internal theorem, computer-assisted).

There is no configuration of distinct unit vectors d_1..d_4 and distinct unit
vectors e_1..e_4 in three-space with e_l . d_i = 1/2 for all l != i. The
machine contribution is four certificate identities l * s_1 s_2 = sum q_i g_i,
archived under certificates/ with SHA-256 pins carried by the E-A69 receipt
and re-verified by exact expansion; the remaining steps (pattern reduction to
one cubic, positivity on the closed square) are printed in full and are
hand-checkable.

## C9 — five sites per side, and the four-hidden-facet corollary

**Status:** proved in manuscript Theorem 7.8 and Corollary 7.9.
**Registry:** P43-C091, level CL5 (internal theorem).

Two distinct compatible decompositions of one proper-zero raw union differ in
at least five reflected sites on each side. Hence a proper-zero datum with at
most four hidden facets has a unique compatible decomposition, with no
hypothesis on its centre. The route is an exchange graph with an equilateral
edge relation, a two-common-neighbours lemma (two distinct bisector planes
meet a sphere in at most two points), an incidence count, and C8 for the
forced K_{4,4}-minus-perfect-matching case. No planarity or star-shapedness
argument is used.

## Explicit exclusions

- uniqueness or injectivity at exceptional centres with five or more hidden
  facets;
- dimensions above three;
- arbitrary implicit, noisy, or floating-point input extraction;
- an end-to-end implementation of steps 1 to 3;
- completeness of the two certifier conditions;
- novelty, priority, or firstness.

## Registry correspondence

Levels follow the project claim ladder: CL5 = internal theorem, public if
proof and dependencies are present (they ship in this package); CL3 =
certified finite result, public with its certificate scope. The internal
`public_ready` flags remain false by registry invariant until the release
act itself; the levels above are what license the wording used here.
