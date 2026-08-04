# Third-party notices

This package contains no vendored third-party source code, PDFs, or datasets.

It declares two pinned runtime dependencies: SymPy (BSD-3-Clause), used only
by the E-A69 certificate verification for exact polynomial expansion, and
mpmath (BSD-3-Clause), its arithmetic backend. They are installed by the user
via <code>requirements.txt</code> and are not redistributed here. The archived
Singular driver files under
<code>certificates/</code> are original input scripts written for this
project; Singular itself (GPL) is neither included nor required to verify the
results.

The paper cites work on recognition and inversion of Dirichlet, Voronoi,
power, straight-skeleton, and bisector diagrams. Those works remain the
property of their authors and publishers. They are listed in the manuscript
bibliography and classified in <code>docs/SOURCE_LOCK.md</code>.

The Python modules and JSON receipts in this package were generated for this
project and are distributed as original reproducibility artifacts.
