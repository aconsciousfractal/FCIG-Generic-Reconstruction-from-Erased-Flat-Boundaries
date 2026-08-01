# Red-team report

Scope: the P43 public companion package and its manuscript.  Maintained by
the P43 project through four adversarial waves (internal S105--S107 release
audit; external manuscript audit with internal adjudication, 2026-07-31;
external release audit with internal adjudication, 2026-07-31, on the tree
whose parent is the S108 candidate; independent pre-publication audit and
closeout, 2026-08-01).  Enumeration and mutation checks quoted
below were executed during the audits; the enumeration scripts are audit
tooling and are not part of this package.

## Outcome

The release candidate passed only after repairing multiple claim-critical
defects. No fatal or high-severity finding remains open inside the published
theorem and artifact scope. The mathematical open problems listed below are
explicit exclusions, not hidden release defects.

## Second wave: the revised manuscript

The revised manuscript (Sections 7 and the extended Section 8) went through a
further independent red team followed by an adjudication that re-verified
every finding before acting. Highlights, all repaired in the shipped
revision:

| Finding | Severity | Disposition |
|---|---|---|
| the exchange-graph planarity proof rested on star-shapedness of the merged component, which is false in general (explicit obtuse-prism witness; the segment from the centre to a flat apex can leave the component) | high | the topological route was withdrawn entirely; the bound now uses a two-common-neighbours lemma (two distinct bisector planes meet a sphere in at most two points) and an incidence count, validated during the audits by exhaustive enumeration of the relevant bipartite graphs |
| the k^3 halfspace-kernel cost was still understated | high | corrected to k^4 in paper and claim ledger |
| the certifier at exceptional centres accepted a wrong reconstruction under the flat-only comparison | high | two-condition certifier shipped (E-A58 v3); necessity of each condition is witnessed (E-A61, E-A63) and unit-tested |
| stale payload pins and citation-name drift | high | payloads realigned to the v3/realigned receipts; author names corrected against the source lock |

The four certificate identities of Theorem 7.6, the endgame, the payload
reproduction and a proof-must-fail control at distance one third were
re-derived from scratch by the external wave and again by the adjudication.

## Third wave: the release candidate

The committed candidate went through an external release audit followed by an
internal adjudication that re-verified every finding.  The audit re-expanded
the certificates from the shipped bytes, re-derived the endgame, recomputed
all manifest entries and attestation pins, enumerated the counting lemma's
graph classes independently, and confirmed the earlier layout and
`k^4` corrections.  Findings, all repaired in this tree:

| Finding | Severity | Disposition |
|---|---|---|
| the certificate verifier closed on bare `assert` statements, which `python -O` strips: under the documented optimized replay a tampered certificate re-derivation would not fail the run (byte tampering was still caught by hash pins; the lost protection was recomputation against environment drift) | blocker | asserts replaced by hard failures that survive `-O`; a SymPy version gate added; regression-tested by tampering a cofactor on a copy under `-O`, which now exits nonzero |
| one block of the public source lock still pinned the superseded E-A58 v2 schema and payload | blocker | realigned to v3 with the v2 value kept as history; all five payloads now listed |
| four classical comparators entered the related-work section with theorem-level characterisations although their primary texts are unread | blocker | the four sentences weakened to subject-matter level; the prior-art table now marks them "primaries not read, no theorem-level import" |
| the public claim rows lacked registry identities; three backing claims were still at proof-obligation level and the cost bound had no claim | blocker | claim rows now cite their internal ids and levels; the backing claims were promoted by the maintainer after verification; the `k^4` bound is registered |
| only one direction of the certifier-necessity claim was unit-tested: forcing the flat-only comparison to `True` left the suite green | blocker | a reversed-family test added; the suite now kills that mutation |
| the git history carried a personal author email while the paper deliberately uses a noreply address | high | history rewritten to the noreply identity and old objects purged before any remote exists |
| no script verified the attestation, so the trust chain ended at internal consistency | high | `check_attestation.py` added and wired into the documented gates and CI |
| replay scripts overwrite frozen receipts when run without `--verify-existing` | high | documented prominently in the reproduction guide; the manifest and attestation gates fail closed on any such pollution, and version control restores the tree |

## Material findings and disposition

| Finding | Severity | Disposition |
|---|---|---|
| cap formula omitted unit-normal normalization | fatal | unit normals are explicit in model and tests |
| genericity used a lemma outside its hypothesis | high | replaced by direct hidden-facet and visible-edge incidence argument |
| containment in a closed algebraic union was promoted to closedness | high | closedness claim removed |
| Tonelli was applied to an undefined varying-realization measure space | high | theorem restricted to fixed realization and mask |
| reference complexity omitted cubic halfspace intersection | high | bound corrected to O(N^2 log N + k^3); a later external audit found the per-candidate containment scan still omitted, and the bound now stands at O(N^2 log N + k^4) |
| finite shortcut agreement was written like an equivalence theorem | high | regression evidence only |
| E-A58 was described as a full six-step certifier | high | scoped to steps 4 to 6 and merged-flat certification |
| historical condition (H) was mislabeled as theorem applicability | medium | retained only as a corpus diagnostic |
| inverse-recognition comparison set was incomplete | high | source lock expanded; no novelty claim |
| signature graph retained hidden source-side patch provenance | fatal | replaced by intrinsic maximal-sheet germ skeleton E-A60 |
| merged component was always selected by volume | high | star-centre rule restored except in two-component case |
| C088 registry and E-A58 receipt retained pre-S106 wording | high | authoritative statement and schema v2 corrected before release |
| supplied-boundary comparison overgeneralized | high | Laguerre moment and NDT travel-time comparators added |
| systematic diffraction absence treated as an erased Brillouin face | high | mapping rejected; structure-factor and geometric boundaries separated |
| NDT/EBSD described as direct applications | high | reduced to bridge targets requiring generative and stability theorems |
| prescribed-crease origami hardness transferred to inverse recovery | high | transfer rejected absent a common decision problem and reduction |

## Fourth wave: independent pre-publication closeout

The S128 audit independently repeated the normal, optimized and isolated
replays, killed the certifier and certificate mutations, rebuilt the PDF
byte-for-byte and inspected all sixteen pages.  It also found release-surface
defects not affecting the theorem: four close supplied-tessellation
comparators missing from the source lock, the publisher title
``polytopical'' shortened incorrectly to ``polytopal'', a pre-release CFF date,
and an omitted mpmath notice.  The comparison set, bibliography, CFF metadata,
dependency notices and exact open-problem wording were corrected before this
tree was re-locked.

## Adversarial controls

- deletion of source-kind fields leaves the skeleton unchanged;
- collinear boundary subdivision leaves the tested skeletons unchanged;
- an independent maximal-sheet path agrees on the deterministic sample;
- the swallowed-corner witness remains visible and reconstructs;
- dropping a reconstructed site fails exact set certification;
- normal and optimized replays must generate identical receipts;
- the manifest-only replay rejects hidden private-workspace dependencies.

## Open research outside release scope

- decide uniqueness or construct an exact ambiguity when a passing core vertex
  avoids every visible hinge and at least five hidden facets are present;
- extend the intrinsic-stratum argument above dimension three;
- prove or refute the historical plane-count shortcut beyond the corpus;
- build an end-to-end exact extractor from a more primitive raw-set input;
- continue prior-art tomography without making a firstness claim.
