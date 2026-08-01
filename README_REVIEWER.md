# Reviewer guide

## S108 prior-art challenge

Before accepting an impact statement, check three observable mismatches: Laguerre
moments and ultrasonic travel times are comparator inputs, not reflected-cap raw
unions; systematic diffraction absences do not delete Brillouin-zone bisectors;
and NP-hard foldability of a prescribed crease pattern is not inverse crease
recovery. The public package claims no industrial deployment.

Also distinguish supplied-tessellation inversion from erased-source recovery:
Suzuki--Iri, Duan et al., Chaidee--Sugihara and Hernandez-Suarez retain a
planar, weighted, or spherical diagram as input.  P43 does not observe those
source boundaries after the flat caps merge with the core.

## Fast audit route

1. Read the title-named PDF under <code>paper/</code>.
2. Read <code>docs/CLAIM_LEDGER.md</code> and
   <code>docs/PUBLIC_CLAIM_BOUNDARY.md</code>.
3. Inspect the definition of the intrinsic boundary-germ skeleton in Section 4.
4. Run:

   ~~~bash
   python scripts/check_manifest.py --closed-tree
   python -m unittest discover -s tests
   python scripts/verify_all.py
   python -O scripts/verify_all.py
   python scripts/check_attestation.py
   python scripts/verify_manifest_only.py
   ~~~

5. Confirm that both aggregate runs produce byte-identical receipts and end in
   <code>PASS_P43_PUBLIC_PACKAGE</code>.

## Load-bearing mathematical points

- Facet normals are unit normals in the reflected-apex formula.
- The proper-zero component is the adjacency-star centre when at least two
  nonflat caps exist; volume distinguishes the two-component case.
- The graph is computed from maximal exposed planar sheet germs and not from
  original hidden cap labels or erased seams.
- Every hidden apex passes on intrinsic crease edges; graph vertices have only
  the two candidate types used by the uniqueness proof.
- Nested candidate site sets give nested cores, and the intrinsic volume
  identity forces equality.
- Genericity is for a fixed realized core and fixed visible mask. The bad set
  is contained in a finite algebraic union; the bad set itself is not claimed
  closed.

## Executable evidence

| Artifact | Direct conclusion | Boundary |
|---|---|---|
| E-A60 | source-kind fields ignored; 16,744 reconstructions; mutation and independent-extractor controls | frozen rational corpus (the complete six-vertex census); the 256 mutation/extractor checks are a deterministic corpus prefix |
| E-A58 | exact steps-4-to-6 flat reconstruction; 340 exact two-condition certifications | not steps 1 to 3 and not a full raw-union certifier; completeness of the two conditions not claimed |
| E-A61 | six exact exceptional-centre witnesses: flat-only accepts a strict superset, two-condition rejects | constructed witnesses, not the exceptional locus |
| E-A63 | three reversed witnesses: hinges survive, flat comparison fails | same |
| E-A69 | the four Theorem 7.6 certificate identities expand to zero exactly; endgame and positive controls re-run | certificates decide the two ratios used, over the complex numbers, not the general lemma |
| Unit tests | source-label deletion, subdivision, witness, reconstruction, tamper rejection, certifier necessity | focused samples |

Corpus agreement between the intrinsic candidate set and an older plane-count
shortcut is regression evidence only, not a general equivalence theorem.

## Certificate audit route (Theorem 7.6)

1. Read Section 7 of the PDF: only Step 2 of Theorem 7.6 is machine-found.
2. Check the four cofactor files under <code>certificates/</code> against the
   SHA-256 pins inside <code>results/P43_S122_E_A69_BRANCH3_EXACT_CLOSURE.json</code>.
3. Run <code>python scripts/p43_s122_e_a69_branch3_exact_closure.py --verify-existing</code>:
   it re-derives the polynomials from the Gram matrix, expands each identity to
   the zero polynomial in exact rational arithmetic, re-runs the elementary
   endgame, and re-checks the executable positive controls: the regular
   tetrahedron solves the distance-one-third system exactly, and an isosceles
   witness solves the system at its own ratio.  The further ideal-level
   control quoted in Remark 7.7 (the regular point surviving the saturation)
   was run in the archived Singular drivers, which are provenance rather than
   an executable gate here.
4. Run <code>python scripts/check_attestation.py</code> to anchor the manifest,
   the PDF, the regenerated receipt and the certificate files against
   <code>RELEASE_ATTESTATION.json</code>.  The gate fixes those artifact roles,
   requires the exact four certificate names and seven checks, and validates
   the real manifest-entry and PDF-page counts.  The reviewed Git commit is
   the root of trust against a coordinated rewrite of both checker and
   attestation; this gate detects degradation inside that trusted commit.

## Claims deliberately absent

- no uniqueness theorem at exceptional centres with five or more hidden
  facets (at most four is proved; hinge-anchored is proved);
- no higher-dimensional theorem;
- no floating-point or point-cloud front end;
- no certifier-completeness claim;
- no general equal-face-circumradius characterisation;
- no novelty, priority, or firstness claim.

## Repository status

This is a reviewer-sized companion package. GitHub availability does not
assert a DOI, journal submission, acceptance, arXiv deposit, or release of the
full historical research workspace.
