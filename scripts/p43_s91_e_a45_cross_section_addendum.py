#!/usr/bin/env python3
"""P43 S91 / E-A45 cross-section addendum to the realization robustness sweep.

The E-A44 generator holds the supporting plane of every non-triangular facet
fixed.  For a core with at most one non-triangular facet that costs nothing,
because the position of a single plane is absorbed by an ambient isometry.  It
does cost something for the two six-vertex types with several non-triangular
facets:

- S6-01, the triangular prism, has three quadrilaterals, so E-A44 explored only
  the realizations with one fixed triangular cross-section;
- S6-03 has two quadrilaterals, so E-A44 explored only one dihedral angle
  between them.

This addendum supplies further base realizations of those two types with
genuinely different non-triangular plane configurations, and re-runs the
source-free fiber enumeration on them.  It is exactly the slice that E-A44
could not reach.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s91_e_a44_realization_robustness as ROB


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "results" / "P43_S91_E_A45_CROSS_SECTION_ADDENDUM.json"
)
SWEEP_RESULT = (
    ROOT / "results" / "P43_S91_E_A44_SIX_VERTEX_REALIZATION_ROBUSTNESS.json"
)

# Extra base realizations with different non-triangular plane configurations.
# Coordinates are in the S50 vertex labelling and are validated before use.
EXTRA_COORDINATES: dict[str, dict[str, list[K.Point]]] = {
    "S6-01": {
        # scalene right prism: a different triangular cross-section
        "cross_section_scalene": [
            (Q(0), Q(0), Q(0)),
            (Q(2), Q(5), Q(6)),
            (Q(7), Q(0), Q(6)),
            (Q(7), Q(0), Q(0)),
            (Q(2), Q(5), Q(0)),
            (Q(0), Q(0), Q(6)),
        ],
        # oblique prism: the translation is not orthogonal to the cross-section
        "cross_section_oblique": [
            (Q(0), Q(0), Q(0)),
            (Q(4), Q(6), Q(6)),
            (Q(8), Q(1), Q(6)),
            (Q(6), Q(0), Q(0)),
            (Q(2), Q(5), Q(0)),
            (Q(2), Q(1), Q(6)),
        ],
        # tall thin cross-section
        "cross_section_thin": [
            (Q(0), Q(0), Q(0)),
            (Q(1), Q(9), Q(5)),
            (Q(5), Q(0), Q(5)),
            (Q(5), Q(0), Q(0)),
            (Q(1), Q(9), Q(0)),
            (Q(0), Q(0), Q(5)),
        ],
    },
    "S6-03": {
        # the two quadrilaterals meet along one edge; these three realizations
        # change the dihedral angle of that edge, which the E-A44 generator
        # cannot do because it holds both planes fixed
        "dihedral_steep": [
            (Q(4), Q(4), Q(0)),
            (Q(-1), Q(4), Q(4)),
            (Q(-4), Q(-4), Q(0)),
            (Q(4), Q(-4), Q(0)),
            (Q(2), Q(0), Q(2)),
            (Q(-4), Q(4), Q(0)),
        ],
        "dihedral_shallow": [
            (Q(4), Q(4), Q(0)),
            (Q(-1), Q(-2), Q(4)),
            (Q(-4), Q(-4), Q(0)),
            (Q(4), Q(-4), Q(0)),
            (Q(2), Q(-3), Q(2)),
            (Q(-4), Q(4), Q(0)),
        ],
        "dihedral_flat": [
            (Q(4), Q(4), Q(0)),
            (Q(-1), Q(-2), Q(6)),
            (Q(-4), Q(-4), Q(0)),
            (Q(4), Q(-4), Q(0)),
            (Q(2), Q(-3), Q(3)),
            (Q(-4), Q(4), Q(0)),
        ],
    },
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def non_triangular_shape_invariant(planes, census_facets) -> list[str]:
    """Isometry invariant of the configuration of non-triangular facet planes.

    Plane keys change under a translation, so they are not a witness that a
    realization is genuinely new.  The squared cosine of the angle between each
    pair of those planes is exact, rational and invariant under every ambient
    isometry, so a different multiset certifies a different configuration.
    """
    normals = [
        planes[index][0]
        for index, facet in enumerate(census_facets)
        if len(facet) > 3
    ]
    values = []
    for left in range(len(normals)):
        for right in range(left + 1, len(normals)):
            first, second = normals[left], normals[right]
            values.append(
                Q(K.dot(first, second) ** 2)
                / (K.squared_norm(first) * K.squared_norm(second))
            )
    return sorted(str(value) for value in values)


def build(limit_rows: int | None) -> dict[str, Any]:
    base = CEN.prepare_rows()
    records: list[dict[str, Any]] = []
    configurations: list[dict[str, Any]] = []
    realization_notes: list[dict[str, Any]] = []

    for core_id in sorted(EXTRA_COORDINATES):
        row = base[core_id]
        census_facets = row["census_facets"]
        frozen_shape = non_triangular_shape_invariant(
            row["planes"], census_facets
        )
        for realization_id, points in sorted(EXTRA_COORDINATES[core_id].items()):
            if not ROB.type_is_preserved(points, census_facets):
                raise AssertionError(
                    f"{core_id}/{realization_id} is not a realization of the type"
                )
            planes = ROB.planes_for(points, census_facets)
            shape = non_triangular_shape_invariant(planes, census_facets)
            centers = ROB.interior_centers(points, planes, census_facets)
            realization_notes.append(
                {
                    "core_id": core_id,
                    "realization_id": realization_id,
                    "points": [ROB.point_text(point) for point in points],
                    "non_triangular_plane_shape_invariant": shape,
                    "frozen_shape_invariant": frozen_shape,
                    "non_triangular_plane_configuration_differs_from_frozen":
                        shape != frozen_shape,
                    "centers": sorted(centers),
                }
            )
            upper = (1 << row["facet_count"]) - 1
            for center_name in sorted(centers):
                candidate_row = {
                    "core_id": core_id,
                    "core": row["core"],
                    "census_facets": census_facets,
                    "facet_count": row["facet_count"],
                    "points": points,
                    "planes": planes,
                    "centers": {center_name: centers[center_name]},
                }
                rows_here = 0
                for visible_mask in range(1, upper):
                    record = CEN.census_row(
                        candidate_row, center_name, visible_mask
                    )
                    record["realization_id"] = realization_id
                    records.append(record)
                    rows_here += 1
                    if limit_rows is not None and len(records) >= limit_rows:
                        break
                configurations.append(
                    {
                        "core_id": core_id,
                        "realization_id": realization_id,
                        "center": center_name,
                        "rows": rows_here,
                    }
                )
                if limit_rows is not None and len(records) >= limit_rows:
                    break

    sizes = Counter(record["fiber_size"] for record in records)
    metrics = {
        "rows": len(records),
        "fiber_size_histogram": {str(key): sizes[key] for key in sorted(sizes)},
        "rows_with_singleton_fiber": sizes.get(1, 0),
        "rows_with_nonsingleton_fiber": len(records) - sizes.get(1, 0),
        "rows_with_observability_degeneracy": sum(
            1
            for record in records
            if record["degeneracy"]["coplanar_mergers"]
            or record["degeneracy"]["t_junctions"]
        ),
        "t_junction_rows": sum(
            1 for record in records if record["degeneracy"]["t_junctions"]
        ),
        "true_decomposition_always_in_the_fiber": all(
            record["true_decomposition_is_in_the_fiber"] for record in records
        ),
        "C032_center_always_recovered": all(
            record["C032_center_recovered_exactly"] for record in records
        ),
        "observed_cells_always_disjoint": all(
            record["observed_cells_have_disjoint_interiors"] for record in records
        ),
    }

    assertions = {
        "every_extra_realization_has_a_new_non_triangular_plane_configuration":
            all(
                note["non_triangular_plane_configuration_differs_from_frozen"]
                for note in realization_notes
            ),
        "the_true_decomposition_is_always_in_the_enumerated_fiber":
            metrics["true_decomposition_always_in_the_fiber"],
        "C032_center_is_recomputed_exactly_on_every_row":
            metrics["C032_center_always_recovered"],
        "observed_cells_have_pairwise_disjoint_interiors_on_every_row":
            metrics["observed_cells_always_disjoint"],
        "no_fiber_is_empty": metrics["fiber_size_histogram"].get("0", 0) == 0,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S91 addendum assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A45-CROSS-SECTION-ADDENDUM-v1",
        "project": "P43",
        "phase": "S91_E_A45_cross_section_and_dihedral_addendum",
        "status": "pass_exact_addendum_complete",
        "locked_file_sha256": {
            "results/P43_S91_E_A44_SIX_VERTEX_REALIZATION_ROBUSTNESS.json":
                file_sha256(SWEEP_RESULT),
        },
        "motivation": (
            "E-A44 holds the planes of non-triangular facets fixed; for S6-01 "
            "and S6-03 that leaves part of the realization space unexplored, "
            "and S6-01 is exactly where every observability degeneracy lives"
        ),
        "realizations": realization_notes,
        "configurations": configurations,
        "metrics": metrics,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "exact source-free fiber cardinality on prism cross-sections and S6-03 dihedrals unreachable by the E-A44 generator",
            ],
            "excluded": [
                "the full realization family",
                "any size above six core vertices",
                "novelty priority or publication readiness",
            ],
        },
    }
    result["canonical_mathematical_payload_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()
    result = build(args.limit)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S91 addendum differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
