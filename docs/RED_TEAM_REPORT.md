# Red-team report

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
| the exchange-graph planarity proof rested on star-shapedness of the merged component, which is false in general (explicit obtuse-prism witness; the segment from the centre to a flat apex can leave the component) | high | the topological route was withdrawn entirely; the bound now uses a two-common-neighbours lemma (two distinct bisector planes meet a sphere in at most two points) and an incidence count, brute-force-validated over all relevant bipartite graphs |
| the k^3 halfspace-kernel cost was still understated | high | corrected to k^4 in paper and claim ledger |
| the certifier at exceptional centres accepted a wrong reconstruction under the flat-only comparison | high | two-condition certifier shipped (E-A58 v3); necessity of each condition is witnessed (E-A61, E-A63) and unit-tested |
| stale payload pins and citation-name drift | high | payloads realigned to the v3/realigned receipts; author names corrected against the source lock |

The four certificate identities of Theorem 7.6, the endgame, the payload
reproduction and a proof-must-fail control at distance one third were
re-derived from scratch by the external wave and again by the adjudication.

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

## Adversarial controls

- deletion of source-kind fields leaves the skeleton unchanged;
- collinear boundary subdivision leaves the tested skeletons unchanged;
- an independent maximal-sheet path agrees on the deterministic sample;
- the swallowed-corner witness remains visible and reconstructs;
- dropping a reconstructed site fails exact set certification;
- normal and optimized replays must generate identical receipts;
- the manifest-only replay rejects hidden private-workspace dependencies.

## Open research outside release scope

- decide uniqueness or construct an exact ambiguity when a core vertex passes;
- extend the intrinsic-stratum argument above dimension three;
- prove or refute the historical plane-count shortcut beyond the corpus;
- build an end-to-end exact extractor from a more primitive raw-set input;
- continue prior-art tomography without making a firstness claim.
