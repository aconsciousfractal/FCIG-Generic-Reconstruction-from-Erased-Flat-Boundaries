# Source lock

## Certificate toolchain provenance

The four cofactor files under <code>certificates/</code> were found by a
Groebner-basis saturation in Singular 4.3.2, with the saturation recomputed
by iterated ideal quotients under in-run containment and stability checks;
the search drivers and the computed reduced bases are archived alongside.
No Groebner output is trusted by the proof: each identity is re-verified by
expanding the difference of its two sides to the zero polynomial in exact
rational arithmetic (SymPy 1.14), and the remaining steps of Theorem 7.6 are
printed in the manuscript and hand-checkable. The comparator dismissals in
the related-work section (Alexandrov, Blind--Mani/Kalai, Gardner) cite
classical works by their registered metadata; none is a proof dependency.

## S108 correction

The earlier supplied-boundary summary was too broad. Two primary comparators use
partial or indirect observables: labelled Laguerre-cell volumes and centroids,
and ultrasonic boundary travel times. They materially narrow the input-model
comparison but do not supply the raw reflected-cap union of this paper.

The Brillouin-zone analogy is exact only at the local construction level: a
zone face is a perpendicular bisector in the reciprocal-lattice Voronoi cell.
IUCr systematic absences are zeros of the structure factor caused by symmetry;
they do not erase that mathematical face. The cited rigid-origami hardness result
decides foldability of a prescribed crease pattern and gives no reduction for
inverse erased-boundary reconstruction.

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
| Bourne--Pearce--Roper, 2025 | https://doi.org/10.1051/m2an/2025004 | labelled Laguerre cells from volumes and centroids |
| Bourne et al., 2021 | https://doi.org/10.1002/mma.6977 | oriented planar Voronoi fitting from ultrasonic travel times |
| Simon, solid-state notes | https://www-thphys.physics.ox.ac.uk/people/SteveSimon/condmat2011/LectureNotes.pdf | Brillouin zone as reciprocal-lattice Voronoi cell |
| IUCr Online Dictionary | https://dictionary.iucr.org/Systematic_absences | systematic absences are structure-factor zeros |
| Akitaya et al., 2020 | https://doi.org/10.20382/jocg.v11i1a4 | prescribed-pattern rigid foldability is NP-hard |

Bibliographic titles, author lists, years, and the specific input descriptions
were checked against publisher pages, arXiv records, or author-hosted full text.
No third-party PDF is distributed in this repository.

## Frozen computational objects

- The seven six-vertex combinatorial types are pinned by the included S50 census file and its hard-coded SHA-256 check in the rational catalogue builder.

- E-A60 schema: <code>P43-E-A60-INTRINSIC-GERM-SKELETON-v2</code>.
- E-A60 canonical payload: <code>D18C07176BAF7B729A550E9B9B8B9D9E04BB58A0C52D295243108417C9BE785A</code>.
- E-A58 schema: <code>P43-E-A58-REFERENCE-RECONSTRUCTION-v3</code> (the
  two-condition certifier; the superseded v2 payload was
  <code>49A3FDC23406557354FEC8DDA51B4C2BB5CA9D43E11D2793C95034C0BA61FA5C</code>).
- E-A58 canonical payload: <code>3C58C0B88081380C7D22993A6FEE3B4EC9FE1A8C3D0CDC107BE9D40C33BA4ACC</code>.
- E-A61 canonical payload: <code>76956805B0BA304142CB08D833FA1179876A9F2154A76CE6C5A232BEF9E3F7F1</code>.
- E-A63 canonical payload: <code>50B26633575C81C67AD3A9857DC5BE1227B512E21CC98168EECEC37B360DB1A8</code>.
- E-A69 canonical payload: <code>5DC4C5800572C64F07C7A815CE7BEFFB930FEF03E04CC71679FB9501606F1D92</code>.
- The manifest pins the exact scripts, tests, prose, bibliography, certificate
  files, and frozen JSON receipts used by the release.

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
