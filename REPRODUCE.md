# Reproducing the P43 companion package

## Requirements

- Python 3.10 or newer;
- SymPy 1.14.0 and mpmath 1.3.0 from `requirements.txt`;
- for the paper only: LaTeX with `amsart`, `lmodern`, `microtype`,
  `mathtools`, `enumitem`, `xcolor`, `hyperref`, and BibTeX.

All geometry and certification predicates are exact. There is no randomness
and no floating-point geometric decision in the release gate.

## Install

```bash
python -m pip install -r requirements.txt
```

## Complete package gate

Run from the repository root, in this order:

```bash
python scripts/check_manifest.py --closed-tree
python -m unittest discover -s tests
python scripts/verify_all.py
python -O scripts/verify_all.py
python scripts/check_attestation.py
python scripts/verify_manifest_only.py
```

Expected terminal markers are:

```text
PASS_MANIFEST_60_FILES_CLOSED_TREE
Ran 19 tests ... OK
PASS_P43_PUBLIC_PACKAGE
PASS_P43_PUBLIC_PACKAGE
PASS_ATTESTATION_ANCHORED checks=7
PASS_MANIFEST_ONLY_REPLAY files=60 ...
```

`verify_all.py` runs the focused unit suite and rebuilds the seven cited frozen
audits in verify-existing mode:

- E-A58, E-A60, E-A61, E-A63, E-A69, E-A71, and E-A72.

It requires their canonical payloads, exact counts, assertions, certificate
hashes, and mutation kills. It writes
`results/public_package_verification.json`. Normal and optimized runs must
produce identical bytes.

`verify_manifest_only.py` copies exactly the source-manifest files to an
isolated temporary directory and repeats both aggregate modes. This is the
closed-world check against a hidden dependency on the private workspace or an
unmanifested local file.

## Important receipt warning

Several historical experiment scripts write their result JSON by default. The
supported release route is `verify_all.py`, which invokes them with
`--verify-existing`. Do not run a historical script without that flag unless
you intend to regenerate its frozen record. A changed record will correctly
make the manifest and attestation gates fail.

## Build the paper

From `paper/`:

```bash
job="Exact_Reconstruction_of_Reflected-Cap_Data_from_an_Erased_Flat_Boundary"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
bibtex "$job"
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
pdflatex -interaction=nonstopmode -halt-on-error -jobname="$job" main.tex
```

The repository ships only
`Exact_Reconstruction_of_Reflected-Cap_Data_from_an_Erased_Flat_Boundary.pdf`.
The source contains `\date{}` and suppresses volatile PDF dates and trailer
IDs. A temporary `main.pdf` is ignored and must not be retained.

The final log must contain no undefined references, citation failures,
overfull boxes, or underfull boxes. Render and inspect all 20 pages; a clean log
alone is not a visual gate.

## Manifest and attestation model

`MANIFEST_SHA256.txt` pins every shipped source/evidence byte except itself,
the title-named PDF, the regenerated aggregate receipt, and
`RELEASE_ATTESTATION.json`. Those exclusions avoid circular hashing.

`RELEASE_ATTESTATION.json` then binds:

- the source-manifest hash and 60-entry count;
- the exact title-named 20-page PDF hash and byte count;
- the aggregate receipt hash and byte count;
- all seven canonical experiment payloads;
- the four E-A69 certificate-file hashes.

`scripts/check_attestation.py` fixes those semantic roles and fails closed on
path substitution, missing roles, false counts, schema downgrade, or payload
drift. The reviewed Git commit remains the root of trust against coordinated
replacement of both checker and attestation.

## Evidence boundary

The finite replays verify implementations and the archived polynomial
identities on their exact frozen domains. The proof of universal proper-zero
uniqueness is the intrinsic argument in Theorem 4.6. The package does not
implement arbitrary/noisy input extraction and makes no all-zero,
higher-dimensional, stability, novelty, or priority claim.
