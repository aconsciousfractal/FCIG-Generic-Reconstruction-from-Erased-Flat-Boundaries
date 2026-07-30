# Source lock

## Mathematical source boundary

The paper is self-contained for its reconstruction, uniqueness, genericity,
and complexity claims. One classical construction is imported with explicit
attribution: Ash and Bolker reflect a supplied interior point across known cell
facets when constructing a Dirichlet cell. The present paper re-proves the
exact contact statement needed for its model.

No cited recognition theorem is used to infer reconstruction after source
boundaries have been erased. The related-work sources are comparators for
input models, not black-box proof dependencies.

## Primary and author-hosted records checked

| Source | Locator used | Role |
|---|---|---|
| Ash--Bolker, 1985 | https://doi.org/10.1007/BF00181470 and author PDF | forward reflection construction; supplied tessellation |
| Aurenhammer, 1987 | https://doi.org/10.1016/S0747-7171(87)80003-2 | supplied polytopal cell complex |
| Hartvigsen, 1992 | https://doi.org/10.1287/ijoc.4.4.369 | supplied polyhedral tessellation; LP recognition |
| Schoenberg--Ferguson--Li, 2003 | https://doi.org/10.1093/comjnl/46.1.76 | inversion from supplied cell-boundary segments |
| Biedl--Held--Huber, 2013 | https://doi.org/10.1109/ISVD.2013.11 | supplied embedded straight-line graph with rays |
| Borgwardt--Frongillo, 2017 | https://arxiv.org/abs/1711.06207 | power-diagram detection from a supplied complex |
| Eder et al., 2023 | https://doi.org/10.1016/j.comgeo.2022.101935 | supplied planar partition or bisector graph |
| Alonso Ferrero, 2011 | https://arxiv.org/abs/1105.4246 | generator recognition with Voronoi edges given |
| Aloupis et al., 2013 | https://arxiv.org/abs/1308.5550 | inverse fitting while retaining original input edges |

Bibliographic titles, author lists, years, and the specific input descriptions
were checked against publisher pages, arXiv records, or author-hosted full text.
No third-party PDF is distributed in this repository.

## Frozen computational objects

- The seven six-vertex combinatorial types are pinned by the included S50 census file and its hard-coded SHA-256 check in the rational catalogue builder.

- E-A60 schema: <code>P43-E-A60-INTRINSIC-GERM-SKELETON-v2</code>.
- E-A60 canonical payload: <code>D18C07176BAF7B729A550E9B9B8B9D9E04BB58A0C52D295243108417C9BE785A</code>.
- E-A58 schema: <code>P43-E-A58-REFERENCE-RECONSTRUCTION-v2</code>.
- E-A58 canonical payload: <code>49A3FDC23406557354FEC8DDA51B4C2BB5CA9D43E11D2793C95034C0BA61FA5C</code>.
- The manifest pins the exact scripts, tests, prose, bibliography, and frozen
  JSON receipts used by the release.

## Provenance and admissibility

The public skeleton extractor reads polygon coordinates and supporting-plane
keys. It does not read source-kind fields or hidden-cap identities. Coplanar
internal seams contribute only one supporting plane and are discarded;
noncoplanar sheet-carrier changes remain. Deterministic subdivision mutations
and an independent maximal-sheet implementation are explicit controls.

## Open prior-art gap

The search found closely related inverse-recognition work with substantially
visible diagram or cell-boundary input. It did not establish an exhaustive
absence theorem for erased-source-boundary reconstruction. Accordingly the
package makes no novelty, priority, or firstness claim.
