# Prior-art comparison

## Comparison axis

The relevant distinction is the information supplied to the inverse problem.
This package observes a raw union in which flat-cap bases and source labels
have already disappeared. It therefore cannot directly invoke algorithms that
start from a labelled tessellation, cell complex, embedded diagram, edge set,
or geometric partition.

| Work | Supplied input | Use here |
|---|---|---|
| Ash--Bolker | Dirichlet tessellation and cell facets | classical forward reflection attribution |
| Aurenhammer | polytopal cell complex covering Euclidean space | input-model comparator |
| Hartvigsen | polyhedral tessellation | input-model and algorithmic comparator |
| Schoenberg--Ferguson--Li | segments demarcating cell boundaries | inversion comparator |
| Alonso Ferrero | Voronoi edges | planar generator-recognition comparator |
| Biedl--Held--Huber | straight-line graph with rays | embedded-graph comparator |
| Borgwardt--Frongillo | polyhedral complex | power-diagram comparator |
| Eder et al. | planar partition or bisector graph | weighted/bisector comparator |
| Aloupis et al. | planar tessellation whose original edges remain | generalized inverse comparator |

## Locked conclusion

The manuscript may say that these cited methods begin with more explicit
boundary structure than the erased-flat-boundary datum considered here. It may
not convert that scoped comparison into a claim of novelty or priority.
