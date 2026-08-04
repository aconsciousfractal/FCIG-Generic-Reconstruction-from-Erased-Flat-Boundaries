# Public claim ledger

This self-contained ledger maps every shipped claim to its public evidence.
The authoritative scope statement is `docs/PUBLIC_CLAIM_BOUNDARY.md`.

## C1 - exact reflected-cap contacts

**Evidence:** paper proof, Proposition 2.1.

For every rotation angle in `(-pi,pi)`, two reflected-cap cells intersect
exactly in the corresponding common facet intersection. The proof is the
Voronoi identity in Proposition 2.1.

## C2 - intrinsic proper-zero initialization

**Evidence:** paper proof, Proposition 3.1.

In the exact proper-zero model, the raw set determines the merged flat
component, the centre, every nonflat cap, and its visible hinge facet. This is
the initialization used by the universal propagation theorem.

## C3 - universal proper-zero reconstruction

**Evidence:** paper proof, Theorem 4.6.

Every exact three-dimensional proper-zero datum has exactly one compatible
decomposition. Equivalently, congruent proper-zero raw unions determine
congruent complete data. The proof has four load-bearing stages: oriented
frontier-ray exposure, reflected-site recovery, site-anchored strict-component
recovery, and simultaneous finite propagation through connected facet
adjacency.

No genericity hypothesis and no facet-count bound occur in C3. The required
domain is exactly the compatible-decomposition model in Definition 4.1: a
full-dimensional three-polytope core containing the recovered centre in its
interior, all rotation angles in `(-pi,pi)`, and at least one flat and one
nonflat facet.

## C4 - auxiliary signature reconstruction

**Evidence:** paper proof, Theorems 5.1 and 6.1.

For a fixed realized core and visible mask, the intrinsic boundary-germ
signature reconstructs whenever no core vertex passes its bisector-neighbour
test. The excluded centres lie in a finite union of proper spheres and
quadrics. This exceptional set limits the shortcut only; it is not an
exceptional set for C3.

## C5 - hypothetical competing-decomposition structure

**Evidence:** paper proofs in Section 7; exact polynomial replay E-A69 for the
computer-assisted step of Theorem 7.6.

If two compatible decompositions existed, their differing sites would avoid
visible hinges and number at least five on each side. The eight-point
spherical-configuration nonexistence step is computer-assisted by four exact
cofactor identities. These implications are retained as independent
cross-checks even though C3 excludes their antecedent in the proper-zero model.

## C6 - reference complexity

**Evidence:** paper analysis in Section 8.

The auxiliary signature reference implementation has conservative exact
operation bound `O(N^2 log N + k^4)` in the notation of the manuscript. No
sharper worst-case bound is claimed for the independent propagation engine.

## C7 - certified finite evidence

**Evidence:** exact finite replays E-A58, E-A60, E-A61, E-A63, E-A69, E-A71,
and E-A72, bound by `RELEASE_ATTESTATION.json`.

The shipped exact records establish their displayed counts and mutation kills
on the frozen domains. They corroborate implementations and certificates; they
do not replace C3's proof or establish unrestricted input handling. The E-A
labels are stable local experiment locators, not claim levels or literature
citations.

## Claims not present

- all-zero reconstruction or uniqueness;
- dimension greater than three;
- floating-point, noisy, point-cloud, mesh, or implicit-set reconstruction;
- a complete end-to-end input extractor;
- completeness of the auxiliary certifier;
- a general equal-circumradius characterization beyond the printed theorem;
- novelty, priority, or firstness.
