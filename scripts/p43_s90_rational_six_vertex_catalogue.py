#!/usr/bin/env python3
"""P43 S90 / E-A43B exact rational realization catalogue at six vertices.

One exact rational realization for each of the seven six-vertex core types of
the frozen S50 census, with two rational interior centers each.  The catalogue
is validated against the census: the hull facet family must equal the census
facet family vertex set by vertex set, every listed point must be a vertex, and
every supporting plane must contain exactly its own facet.

This is the realization bridge that the Stage C4 plan lacked.  It is the
six-vertex seed of the catalogue the full census would need over all 2,904 core
types.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K


ROOT = Path(__file__).resolve().parents[1]
CORE_CENSUS = ROOT / "results" / "P43_S50_E_A22_PHASE1_SIX_VERTEX_CORE_CENSUS.json"
DEFAULT_OUTPUT = (
    ROOT / "results" / "P43_S90_E_A43B_SIX_VERTEX_RATIONAL_CATALOGUE.json"
)

EXPECTED_CORE_CENSUS_SHA256 = (
    "0046029A58840D75AA86966708AAD2AA3F243AF52372E315AA834807F6AE2B38"
)

# Vertex coordinates are given in the S50 vertex labelling of each type.
COORDINATES: dict[str, list[tuple[Q, Q, Q]]] = {
    # triangular prism
    "S6-01": [
        (Q(0), Q(0), Q(0)),
        (Q(0), Q(6), Q(7)),
        (Q(6), Q(0), Q(7)),
        (Q(6), Q(0), Q(0)),
        (Q(0), Q(6), Q(0)),
        (Q(0), Q(0), Q(7)),
    ],
    # pentagonal pyramid
    "S6-02": [
        (Q(0), Q(0), Q(7)),
        (Q(6), Q(0), Q(0)),
        (Q(-4), Q(-3), Q(0)),
        (Q(-4), Q(3), Q(0)),
        (Q(2), Q(5), Q(0)),
        (Q(2), Q(-5), Q(0)),
    ],
    # four triangles and two quadrilaterals, self dual
    "S6-03": [
        (Q(4), Q(4), Q(0)),
        (Q(-1), Q(0), Q(4)),
        (Q(-4), Q(-4), Q(0)),
        (Q(4), Q(-4), Q(0)),
        (Q(2), Q(-2), Q(2)),
        (Q(-4), Q(4), Q(0)),
    ],
    # square pyramid with one stacked triangular side
    "S6-04": [
        (Q(0), Q(0), Q(8)),
        (Q(-4), Q(-4), Q(0)),
        (Q(4), Q(-4), Q(0)),
        (Q(4), Q(4), Q(0)),
        (Q(-4), Q(4), Q(0)),
        (Q(0), Q(-5), Q(3)),
    ],
    # quadrilateral base with a diagonal ridge
    "S6-05": [
        (Q(4), Q(-4), Q(0)),
        (Q(-4), Q(4), Q(0)),
        (Q(1), Q(1), Q(4)),
        (Q(-1), Q(-1), Q(4)),
        (Q(-4), Q(-4), Q(0)),
        (Q(4), Q(4), Q(0)),
    ],
    # tetrahedron with two stacked vertices
    "S6-06": [
        (Q(0), Q(0), Q(0)),
        (Q(0), Q(9), Q(0)),
        (Q(9), Q(0), Q(0)),
        (Q(0), Q(0), Q(9)),
        (Q(-1), Q(3), Q(3)),
        (Q(3), Q(3), Q(-1)),
    ],
    # octahedron
    "S6-07": [
        (Q(3), Q(0), Q(0)),
        (Q(-3), Q(0), Q(0)),
        (Q(0), Q(4), Q(0)),
        (Q(0), Q(-4), Q(0)),
        (Q(0), Q(0), Q(5)),
        (Q(0), Q(0), Q(-5)),
    ],
}

# Two interior centers per type: the vertex centroid, and one perturbed center
# with pairwise coprime denominators chosen to avoid inherited symmetry.
CENTER_PERTURBATION = (Q(1, 7), Q(1, 11), Q(1, 13))


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def qtext(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def point_text(point: K.Point) -> list[str]:
    return [qtext(value) for value in point]


def load_types() -> dict[str, dict]:
    if file_sha256(CORE_CENSUS) != EXPECTED_CORE_CENSUS_SHA256:
        raise AssertionError("S50 six-vertex core census lock mismatch")
    census = json.loads(CORE_CENSUS.read_text(encoding="utf-8"))
    return {row["id"]: row for row in census["types"]}


def facet_vertex_sets(core: dict) -> list[tuple[int, ...]]:
    """Census facets in the census order, as sorted vertex index tuples."""
    return [tuple(sorted(cycle)) for cycle in core["facets_cyclic"]]


def is_extreme(points: list[K.Point], index: int) -> bool:
    """True when `points[index]` is not a convex combination of the others."""
    target = points[index]
    others = [point for position, point in enumerate(points) if position != index]
    for size in range(1, 5):
        for subset in combinations(others, size):
            if convex_combination_exists(subset, target):
                return False
    return True


def convex_combination_exists(subset: tuple[K.Point, ...], target: K.Point) -> bool:
    """Exact test for `target` in the convex hull of at most four points."""
    if len(subset) == 1:
        return subset[0] == target
    rows = [
        [subset[column][row] for column in range(len(subset))] + [Q(1)]
        for row in range(3)
    ]
    rows.append([Q(1)] * len(subset) + [Q(1)])
    values = [target[0], target[1], target[2], Q(1)]
    solution = solve_nonnegative(rows, values, len(subset))
    return solution is not None


def solve_nonnegative(
    rows: list[list[Q]], values: list[Q], unknowns: int
) -> list[Q] | None:
    """Solve the small exact linear system, requiring nonnegative unknowns."""
    matrix = [row[:unknowns] + [values[index]] for index, row in enumerate(rows)]
    pivot_row = 0
    pivots: list[int] = []
    for column in range(unknowns):
        selected = None
        for row in range(pivot_row, len(matrix)):
            if matrix[row][column] != 0:
                selected = row
                break
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        factor = matrix[pivot_row][column]
        matrix[pivot_row] = [value / factor for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or matrix[row][column] == 0:
                continue
            scale_value = matrix[row][column]
            matrix[row] = [
                value - scale_value * pivot_value
                for value, pivot_value in zip(matrix[row], matrix[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
    for row in range(pivot_row, len(matrix)):
        if matrix[row][unknowns] != 0:
            return None
    if len(pivots) < unknowns:
        return None  # underdetermined: treated as no certified membership
    solution = [Q(0)] * unknowns
    for index, column in enumerate(pivots):
        solution[column] = matrix[index][unknowns]
    if any(value < 0 for value in solution):
        return None
    return solution


def realization(core_id: str) -> dict[str, Any]:
    """Validated exact realization data for one core type."""
    types = load_types()
    core = types[core_id]
    points = COORDINATES[core_id]
    if len(points) != core["vertex_count"]:
        raise AssertionError(f"{core_id}: wrong vertex count")

    census_facets = facet_vertex_sets(core)
    hull = K.hull_facets(points)
    hull_sets = sorted(tuple(indices) for _, indices in hull)
    if hull_sets != sorted(census_facets):
        raise AssertionError(f"{core_id}: hull facet family differs from the census")
    for index in range(len(points)):
        if not is_extreme(points, index):
            raise AssertionError(f"{core_id}: point {index} is not a vertex")

    planes: list[tuple[K.Point, Q]] = []
    for facet in census_facets:
        match = next(
            (plane for plane, indices in hull if tuple(indices) == facet), None
        )
        if match is None:
            raise AssertionError(f"{core_id}: facet {facet} has no supporting plane")
        planes.append(match)

    centroid = K.average(points)
    centers = {
        "centroid": centroid,
        "generic": K.add(centroid, CENTER_PERTURBATION),
    }
    for name, center in centers.items():
        for normal, offset in planes:
            if K.dot(normal, center) >= offset:
                raise AssertionError(f"{core_id}: center {name} is not interior")

    return {
        "core_id": core_id,
        "facet_count": core["facet_count"],
        "vertex_count": core["vertex_count"],
        "points": points,
        "census_facets": census_facets,
        "facets_cyclic": [list(cycle) for cycle in core["facets_cyclic"]],
        "planes": planes,
        "centers": centers,
    }


def catalogue() -> dict[str, dict[str, Any]]:
    return {core_id: realization(core_id) for core_id in sorted(COORDINATES)}


def build() -> dict[str, Any]:
    rows = catalogue()
    serialized = []
    for core_id in sorted(rows):
        row = rows[core_id]
        serialized.append(
            {
                "core_id": core_id,
                "vertex_count": row["vertex_count"],
                "facet_count": row["facet_count"],
                "points": [point_text(point) for point in row["points"]],
                "census_facets": [list(facet) for facet in row["census_facets"]],
                "outward_planes": [
                    {
                        "normal": point_text(normal),
                        "offset": qtext(offset),
                    }
                    for normal, offset in row["planes"]
                ],
                "centers": {
                    name: point_text(center)
                    for name, center in row["centers"].items()
                },
                "volume": qtext(K.convex_hull_volume(row["points"])),
            }
        )

    assertions = {
        "core_census_lock_matches": True,
        "all_seven_types_are_realized": len(serialized) == 7,
        "every_hull_facet_family_equals_the_census_family": True,
        "every_listed_point_is_a_vertex": True,
        "every_center_is_strictly_interior": True,
        "facet_count_multiset_matches_the_census": sorted(
            row["facet_count"] for row in serialized
        )
        == [5, 6, 6, 7, 7, 8, 8],
        "all_volumes_are_positive": all(
            Q(row["volume"]) > 0 for row in serialized
        ),
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S90 catalogue assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A43B-SIX-VERTEX-CATALOGUE-v1",
        "project": "P43",
        "phase": "S90_E_A43B_six_vertex_rational_realization_catalogue",
        "status": "pass_exact_catalogue_frozen",
        "locked_file_sha256": {
            "results/P43_S50_E_A22_PHASE1_SIX_VERTEX_CORE_CENSUS.json":
                EXPECTED_CORE_CENSUS_SHA256,
        },
        "center_perturbation": point_text(CENTER_PERTURBATION),
        "realizations": serialized,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "one validated exact rational realization for each six-vertex core type",
                "two exact rational interior centers per type",
            ],
            "excluded": [
                "any statement about other realizations of the same type",
                "any injectivity or collision result",
                "any extension of the catalogue above six vertices",
            ],
        },
    }
    result["canonical_mathematical_payload_sha256"] = canonical_hash(result)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    result = build()
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S90 catalogue differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
