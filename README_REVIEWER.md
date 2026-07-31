# Reviewer guide

## S108 prior-art challenge

Before accepting an impact statement, check three observable mismatches: Laguerre
moments and ultrasonic travel times are comparator inputs, not reflected-cap raw
unions; systematic diffraction absences do not delete Brillouin-zone bisectors;
and NP-hard foldability of a prescribed crease pattern is not inverse crease
recovery. The public package claims no industrial deployment.

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
| E-A60 | source-kind fields ignored; 16,744 reconstructions; mutation and independent-extractor controls | frozen rational corpus and stated mutation class |
| E-A58 | exact steps-4-to-6 flat reconstruction; 340 exact set certifications | not steps 1 to 3 and not a full raw-union certifier |
| Unit tests | source-label deletion, subdivision, witness, reconstruction, tamper rejection | focused samples |

Corpus agreement between the intrinsic candidate set and an older plane-count
shortcut is regression evidence only, not a general equivalence theorem.

## Claims deliberately absent

- no uniqueness theorem at exceptional centres;
- no higher-dimensional theorem;
- no floating-point or point-cloud front end;
- no novelty, priority, or firstness claim.

## Repository status

This is a reviewer-sized companion package. GitHub availability does not
assert a DOI, journal submission, acceptance, arXiv deposit, or release of the
full historical research workspace.
