# Reviewer quickstart

This is a reviewer-sized companion package for the paper. The integrity replay
is separate from mathematical review: finite execution checks the shipped
implementations and certificates, while the universal uniqueness theorem is
proved intrinsically in the manuscript.

## Ten-minute route

1. Read the title-named PDF under `paper/`, especially Definition 4.1,
   Lemmas 4.3--4.5, and Theorem 4.6.
2. Read `docs/CLAIM_LEDGER.md` and `docs/PUBLIC_CLAIM_BOUNDARY.md`.
3. Run:

   ```bash
   python scripts/check_manifest.py --closed-tree
   python -m unittest discover -s tests
   python scripts/verify_all.py
   python -O scripts/verify_all.py
   python scripts/check_attestation.py
   ```

4. Confirm that both aggregate runs end in `PASS_P43_PUBLIC_PACKAGE` and
   generate byte-identical `results/public_package_verification.json`.

## Thirty-minute proof route

Audit the main theorem as four independent obligations:

1. **Frontier-ray exposure.** At a relative-interior point of a frontier
   ridge, exact face-to-face contacts exclude a third cell. The oriented normal
   quotient therefore contains the known boundary ray and exactly one new wall
   ray. Opposite rays remain distinct when their supporting lines coincide.
2. **Site recovery.** Orthogonal projection of the centre to the ridge, the
   centre-to-ridge distance, and the new oriented transverse direction recover
   one reflected site; the antipode is excluded by orientation.
3. **Cap recovery.** In the strict halfspace closer to that site than to the
   centre, the unique connected component containing the site is the cap with
   its base removed. Closure and bisector intersection recover cap and base.
4. **Simultaneous propagation.** A recovered facet carries all of its frontier
   rays. Connected facet adjacency supplies a finite sequence; applying the
   same intrinsic step to two compatible decompositions recovers the same site,
   cap, and facet at every stage.

The auxiliary intrinsic germ skeleton is defined after the universal proof so
that its passing-vertex exceptional set cannot be mistaken for a hypothesis of
Theorem 4.6.

## Executable evidence map

| Audit | Direct conclusion | Boundary |
| --- | --- | --- |
| E-A58 | auxiliary signature reconstruction on 16,744 rows; 340 exact certifications | not the main universal proof or an end-to-end raw-set extractor |
| E-A60 | intrinsic skeleton on 16,744 rows; 256 subdivision and independent-sheet checks | finite exact corpus |
| E-A61 | flat-only accepts six wrong supersets; full certifier rejects | constructed complementary control |
| E-A63 | hinge survival alone accepts three wrong histories; flat comparison rejects | constructed complementary control |
| E-A69 | four cofactor identities expand to zero; endgame and positive controls rerun | computer-assisted step of Theorem 7.6 only |
| E-A71 | 189,128 oriented ridge steps on 16,759 data, zero failures | local falsification audit, not proof |
| E-A72 | 61,030 global BFS/component steps, zero mismatches, four mutations killed | exact tetrahedral presentation, not arbitrary/noisy input |

E-A72 deliberately encounters 34,090 cases where another strict component also
touches a ridge endpoint. The correct selector is the component containing the
recovered site. Any implementation or reading that uses ridge contact alone is
wrong.

## Certificate route

Theorem 7.6 retains one computer-assisted algebraic step independent of the
main propagation proof.

1. Inspect the four cofactor files under `certificates/` and their SHA-256 pins
   in `results/P43_S122_E_A69_BRANCH3_EXACT_CLOSURE.json`.
2. Run
   `python scripts/p43_s122_e_a69_branch3_exact_closure.py --verify-existing`.
3. Confirm that exact polynomial expansion gives zero for all four identities
   and that both standing positive controls pass.
4. Run `python scripts/check_attestation.py` to bind the four files to the
   release candidate.

## Artifact-isolation route

Run `python scripts/verify_manifest_only.py`. It constructs an isolated tree
from exactly the 60 source-manifest entries, reruns normal and optimized
verification, and requires identical receipts. The title-named PDF,
attestation, source manifest itself, and regenerated aggregate receipt are
separately bound to avoid circular hashing.

## Claims deliberately absent

- all-zero reconstruction;
- a theorem in dimension greater than three;
- noisy, floating-point, point-cloud, or implicit-set input;
- a complete end-to-end implementation of input extraction;
- completeness of the auxiliary certifier;
- novelty, priority, firstness, DOI, arXiv deposit, journal submission, or
  acceptance.

GitHub availability means only that this companion package is public and
replayable. It is not evidence of any venue decision.
