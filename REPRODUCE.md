# Reproducing the P43 public package

## Requirements

- Python 3.10 or newer;
- no third-party Python packages;
- to build the paper: a LaTeX installation with <code>amsart</code>,
  <code>lmodern</code>, <code>microtype</code>, <code>mathtools</code>,
  <code>enumitem</code>, <code>xcolor</code>, <code>hyperref</code>, and BibTeX.

All geometry and certification arithmetic is exact. There is no random seed
and no floating-point predicate in the public gate.

## Package and mathematical gates

From the repository root:

~~~bash
python scripts/check_manifest.py --closed-tree
python -m unittest discover -s tests
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/verify_manifest_only.py
~~~

<code>verify_all.py</code> first verifies the source manifest, runs the focused
unit tests, regenerates E-A60 and E-A58 in verify-existing mode, checks their
canonical payloads and frozen metrics, and writes
<code>results/public_package_verification.json</code>. Normal and optimized
runs must produce identical bytes.

The manifest-only command copies exactly the source-manifest files into an
isolated temporary directory and repeats both aggregate runs. This detects
hidden dependencies on the private workspace or unmanifested files.

## Evidence boundary

E-A60 exercises the observable skeleton on every frozen corpus row and on the
degenerate swallowed-corner witness. E-A58 exercises the flat kernel on every
frozen row and samples the more expensive exact union certification. Neither
finite replay replaces the manuscript proof, and neither implements the input
extraction steps from an arbitrary raw-set representation.

## Build the paper

From <code>paper/</code>:

~~~bash
job="Generic_Exact_Reconstruction_of_Reflected_Cap_Data_from_an_Erased_Flat_Boundary"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
bibtex "$job"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
~~~

The source suppresses volatile PDF dates and trailer IDs. The source manifest
does not hash-pin the PDF; <code>RELEASE_ATTESTATION.json</code> binds the
actual release-candidate PDF.

## Manifest exclusions

The manifest itself, release attestation, title-named PDF, regenerated package
receipt, and LaTeX auxiliary files are excluded to avoid circular hashing.
