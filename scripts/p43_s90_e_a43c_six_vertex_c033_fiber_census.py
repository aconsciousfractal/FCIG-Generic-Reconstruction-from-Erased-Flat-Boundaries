#!/usr/bin/env python3
"""P43 S90 / E-A43C source-free C033 fiber census at six vertices.

For every proper-zero row of the frozen six-vertex domain, and for a frozen
exact rational realization of that row, this script

1. builds the raw union exactly;
2. discards the source data and keeps only intrinsic observables: the boundary
   patch complex of the merged flat component after coplanar merging, the
   candidate site set, the visible hinge polygons and the C032 center
   recomputed from one nonflat cap;
3. enumerates the complete C033 decomposition fiber over candidate hidden-site
   subsets, using only those intrinsic observables;
4. reports the exact fiber cardinality.

Fiber cardinality one is source-free uniqueness for that raw union.  Fiber
cardinality above one is an exact ambiguity witness.  Neither outcome is a
statement about other realizations of the same row: see the S90 target
statement freeze, section 7.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

import p43_s90_exact_rational_kernel as K
import p43_s90_rational_six_vertex_catalogue as CAT


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "results" / "P43_S90_E_A43C_SIX_VERTEX_C033_FIBER_CENSUS.json"
)
CATALOGUE_RESULT = (
    ROOT / "results" / "P43_S90_E_A43B_SIX_VERTEX_RATIONAL_CATALOGUE.json"
)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def qtext(value: Q) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def point_text(point: Iterable[Q]) -> list[str]:
    return [qtext(value) for value in point]


# --------------------------------------------------------------------------
# exact construction of one raw union
# --------------------------------------------------------------------------


class Cell:
    """A convex cell of the raw union, kept both as points and halfspaces."""

    def __init__(self, points: list[K.Point]):
        self.points = points
        self.halfspaces = [plane for plane, _ in K.hull_facets(points)]
        self.volume = K.convex_hull_volume(points)


def facet_cycle(core: dict, index: int) -> list[int]:
    return list(core["facets_cyclic"][index])


def build_raw_union(row: dict, center_name: str, visible_mask: int) -> dict[str, Any]:
    """Exact cells and boundary patches of one datum."""
    points = row["points"]
    planes = row["planes"]
    center = row["centers"][center_name]
    facet_count = row["facet_count"]
    visible = [k for k in range(facet_count) if visible_mask >> k & 1]
    flat = [k for k in range(facet_count) if not visible_mask >> k & 1]

    apex = [
        K.reflect_point(center, normal, offset) for normal, offset in planes
    ]
    core_cell = Cell(list(points))
    flat_cells = {
        k: Cell([points[v] for v in row["census_facets"][k]] + [apex[k]])
        for k in flat
    }

    patches: list[dict[str, Any]] = []
    for k in visible:
        facet_points = [points[v] for v in row["census_facets"][k]]
        patches.append(
            {
                "points": facet_points,
                "plane": K.unoriented_plane_key(*planes[k]),
                "kind": "hinge",
            }
        )
    for k in flat:
        cycle = facet_cycle(row["core"], k)
        for position in range(len(cycle)):
            first = points[cycle[position]]
            second = points[cycle[(position + 1) % len(cycle)]]
            normal, offset = K.plane_through(apex[k], first, second)
            patches.append(
                {
                    "points": [apex[k], first, second],
                    "plane": K.unoriented_plane_key(normal, offset),
                    "kind": "wall",
                }
            )

    return {
        "center": center,
        "visible": visible,
        "flat": flat,
        "apex": apex,
        "core_cell": core_cell,
        "flat_cells": flat_cells,
        "patches": patches,
        "hinge_polygons": {
            k: [points[v] for v in row["census_facets"][k]] for k in visible
        },
        "hinge_planes": {k: planes[k] for k in visible},
    }


# --------------------------------------------------------------------------
# intrinsic observables
# --------------------------------------------------------------------------


def degeneracy_report(patches: list[dict[str, Any]]) -> dict[str, int]:
    """Exact detection of the observability degeneracies of S90 section 7."""
    coplanar_mergers = 0
    for left, right in combinations(range(len(patches)), 2):
        if patches[left]["plane"] != patches[right]["plane"]:
            continue
        shared = set(K.point_set_key(patches[left]["points"])) & set(
            K.point_set_key(patches[right]["points"])
        )
        if len(shared) >= 2:
            coplanar_mergers += 1

    corners = {
        K.point_key(point): point
        for patch in patches
        for point in patch["points"]
    }
    t_junctions = 0
    for patch in patches:
        cycle = patch["points"]
        if len(cycle) > 3:
            normal = (
                Q(patch["plane"][0][0]),
                Q(patch["plane"][0][1]),
                Q(patch["plane"][0][2]),
            )
            order = K.cyclic_order(cycle, normal)
            cycle = [cycle[position] for position in order]
        for position in range(len(cycle)):
            first = cycle[position]
            second = cycle[(position + 1) % len(cycle)]
            direction = K.subtract(second, first)
            for key, point in corners.items():
                if key in (K.point_key(first), K.point_key(second)):
                    continue
                offset = K.subtract(point, first)
                if not K.is_zero(K.cross(direction, offset)):
                    continue
                parameter = K.dot(offset, direction) / K.squared_norm(direction)
                if 0 < parameter < 1:
                    t_junctions += 1
    return {
        "coplanar_mergers": coplanar_mergers,
        "t_junctions": t_junctions,
    }


def ordered_patch_points(patch: dict[str, Any]) -> list[K.Point]:
    points = patch["points"]
    if len(points) <= 3:
        return points
    normal = (
        Q(patch["plane"][0][0]),
        Q(patch["plane"][0][1]),
        Q(patch["plane"][0][2]),
    )
    return [points[position] for position in K.cyclic_order(points, normal)]


def merged_boundary_edges(
    patches: list[dict[str, Any]]
) -> tuple[set[frozenset[tuple[str, str, str]]], dict[tuple[str, str, str], K.Point]]:
    """Edges of the coplanar-merged boundary complex.

    An edge carried by two patches of the same supporting plane is interior to
    the merged patch and is erased, exactly as the C4A.1 erasure rule requires.
    """
    counts: Counter = Counter()
    point_by_key: dict[tuple[str, str, str], K.Point] = {}
    for patch in patches:
        cycle = ordered_patch_points(patch)
        for position in range(len(cycle)):
            first = cycle[position]
            second = cycle[(position + 1) % len(cycle)]
            point_by_key[K.point_key(first)] = first
            point_by_key[K.point_key(second)] = second
            edge = frozenset((K.point_key(first), K.point_key(second)))
            counts[(patch["plane"], edge)] += 1
    surviving = {edge for (_, edge), count in counts.items() if count == 1}
    return surviving, point_by_key


def merged_neighbours(
    site: K.Point,
    edges: set[frozenset[tuple[str, str, str]]],
    point_by_key: dict[tuple[str, str, str], K.Point],
) -> list[K.Point]:
    key = K.point_key(site)
    return [
        point_by_key[other]
        for edge in edges
        if key in edge
        for other in edge
        if other != key
    ]


def candidate_sites(patches: list[dict[str, Any]]) -> list[K.Point]:
    """Intrinsic superset of the local vertices of the merged component.

    A local vertex of a three-dimensional polyhedral set carries a pointed
    tangent cone, hence at least three distinct supporting planes of the
    coplanar-merged boundary complex.  Counting distinct planes performs the
    coplanar merge implicitly: a corner swallowed by a merger keeps one plane
    and is discarded here, exactly as the C4A.1 erasure rule requires.
    """
    planes_by_point: dict[tuple[str, str, str], set] = {}
    point_by_key: dict[tuple[str, str, str], K.Point] = {}
    for patch in patches:
        for point in patch["points"]:
            key = K.point_key(point)
            planes_by_point.setdefault(key, set()).add(patch["plane"])
            point_by_key[key] = point
    return [
        point_by_key[key]
        for key, planes in sorted(planes_by_point.items())
        if len(planes) >= 3
    ]


def in_merged_component(union: dict[str, Any], point: K.Point) -> bool:
    """Membership in the merged flat component as a set, not as a cell list."""
    cells = [union["core_cell"]] + [
        union["flat_cells"][index] for index in union["flat"]
    ]
    return any(
        all(
            K.dot(normal, point) <= offset for normal, offset in cell.halfspaces
        )
        for cell in cells
    )


def recovered_center(union: dict[str, Any]) -> K.Point | None:
    """C032 center recovery from one nonflat cap, computed from observables.

    A nonflat cap is a rigid rotation about its hinge plane of the mirror
    pyramid, so the foot and the radius of its apex over that plane are the
    ones of the unfolded position.  The two points at that radius on the hinge
    normal are the center and the fully reflected site; only the center lies in
    the merged component.  Nothing here reads a source label: the hinge polygon
    and its plane are intrinsic, and the membership test uses the merged
    component as a set.
    """
    visible = union["visible"]
    if not visible:
        return None
    index = visible[0]
    normal, offset = union["hinge_planes"][index]
    apex = union["apex"][index]
    foot = K.subtract(
        apex, K.scale((K.dot(normal, apex) - offset) / K.squared_norm(normal), normal)
    )
    radius = K.subtract(apex, foot)
    candidates = [K.add(foot, radius), K.subtract(foot, radius)]
    inside = [
        point for point in candidates if in_merged_component(union, point)
    ]
    if len(inside) != 1:
        return None
    return inside[0]


# --------------------------------------------------------------------------
# C033 fiber enumeration
# --------------------------------------------------------------------------


def pieces_volume(cells: list[Cell]) -> Q:
    return sum((cell.volume for cell in cells), Q(0))


def separated_by_a_facet_plane(left: Cell, right: Cell) -> bool:
    """Cheap exact sufficient test: one cell's facet plane separates them."""
    for cell, other in ((left, right), (right, left)):
        for normal, offset in cell.halfspaces:
            if all(K.dot(normal, point) >= offset for point in other.points):
                return True
    return False


def interiors_are_disjoint(cells: list[Cell]) -> bool:
    for left, right in combinations(range(len(cells)), 2):
        if separated_by_a_facet_plane(cells[left], cells[right]):
            continue
        if K.intersection_volume(
            cells[left].halfspaces, cells[right].halfspaces
        ) != 0:
            return False
    return True


def unions_are_equal(left: list[Cell], right: list[Cell]) -> bool:
    left_volume = pieces_volume(left)
    right_volume = pieces_volume(right)
    if left_volume != right_volume:
        return False
    shared = Q(0)
    for first in left:
        for second in right:
            shared += K.intersection_volume(first.halfspaces, second.halfspaces)
    return shared == left_volume


def decode_candidate(
    center: K.Point, site: K.Point
) -> tuple[K.Point, Q]:
    return K.bisector_halfspace(center, site)


def fiber(
    union: dict[str, Any],
    observables: dict[str, Any],
    use_neighbour_filter: bool = True,
) -> list[dict[str, Any]]:
    """All decompositions compatible with the intrinsic observables.

    The candidate rule and the hinge-cut filter are unconditionally sound.  The
    neighbour-plane filter is sound only where the boundary complex carries no
    observability degeneracy, so the caller disables it on degenerate rows and
    the enumeration there is unconditionally complete.
    """
    center = observables["center"]
    hinge_halfspaces = [
        union["hinge_planes"][index] for index in union["visible"]
    ]
    hinge_polygons = [
        union["hinge_polygons"][index] for index in union["visible"]
    ]
    hinge_keys = [K.point_set_key(polygon) for polygon in hinge_polygons]

    admissible: list[K.Point] = []
    for site in observables["candidate_sites"]:
        normal, offset = decode_candidate(center, site)
        if K.dot(normal, center) >= offset:
            continue
        cuts_hinge = any(
            K.dot(normal, vertex) > offset
            for polygon in hinge_polygons
            for vertex in polygon
        )
        if cuts_hinge:
            continue
        if use_neighbour_filter:
            # In a compatible decomposition the boundary cells at a hidden site
            # are the mirror walls of its pyramid, so every merged-complex
            # neighbour of the site lies on the base plane, which is the
            # bisector plane.
            neighbours = merged_neighbours(
                site, observables["merged_edges"], observables["point_by_key"]
            )
            if not neighbours:
                continue
            if any(K.dot(normal, point) != offset for point in neighbours):
                continue
        admissible.append(site)

    observed_cells = [union["core_cell"]] + [
        union["flat_cells"][index] for index in union["flat"]
    ]
    solutions: list[dict[str, Any]] = []
    for size in range(len(admissible) + 1):
        for subset in combinations(range(len(admissible)), size):
            sites = [admissible[index] for index in subset]
            halfspaces = list(hinge_halfspaces) + [
                decode_candidate(center, site) for site in sites
            ]
            if len(halfspaces) < 4:
                continue
            candidate = K.Polytope(halfspaces)
            if not candidate.bounded:
                continue
            if not candidate.interior_contains(center):
                continue
            if len(candidate.active) != len(halfspaces):
                continue
            hinge_ok = True
            for position in range(len(hinge_halfspaces)):
                face = candidate.on_plane(position)
                if K.point_set_key(face) != hinge_keys[position]:
                    hinge_ok = False
                    break
            if not hinge_ok:
                continue
            reconstructed = [Cell(list(candidate.vertices))]
            reflection_ok = True
            for position, site in enumerate(sites):
                plane_index = len(hinge_halfspaces) + position
                face = candidate.on_plane(plane_index)
                if len(face) < 3:
                    reflection_ok = False
                    break
                normal, offset = halfspaces[plane_index]
                if K.reflect_point(center, normal, offset) != site:
                    reflection_ok = False
                    break
                reconstructed.append(Cell(list(face) + [site]))
            if not reflection_ok:
                continue
            if not interiors_are_disjoint(reconstructed):
                continue
            if not unions_are_equal(reconstructed, observed_cells):
                continue
            solutions.append(
                {
                    "sites": [point_text(site) for site in sites],
                    "site_count": len(sites),
                    "core_vertices": [
                        point_text(vertex) for vertex in candidate.vertices
                    ],
                    "core_vertex_count": len(candidate.vertices),
                }
            )
    return solutions


# --------------------------------------------------------------------------
# census
# --------------------------------------------------------------------------


def prepare_rows() -> dict[str, dict[str, Any]]:
    rows = CAT.catalogue()
    types = CAT.load_types()
    for core_id, row in rows.items():
        row["core"] = types[core_id]
    return rows


def census_row(
    row: dict[str, Any], center_name: str, visible_mask: int
) -> dict[str, Any]:
    union = build_raw_union(row, center_name, visible_mask)
    degeneracy = degeneracy_report(union["patches"])
    sites = candidate_sites(union["patches"])
    edges, point_by_key = merged_boundary_edges(union["patches"])
    center = recovered_center(union)
    center_matches = center == union["center"]
    observables = {
        "center": center if center is not None else union["center"],
        "candidate_sites": sites,
        "merged_edges": edges,
        "point_by_key": point_by_key,
    }
    true_sites = K.point_set_key(union["apex"][index] for index in union["flat"])
    true_sites_are_candidates = set(true_sites) <= set(
        K.point_set_key(sites)
    )
    regular = not (
        degeneracy["coplanar_mergers"] or degeneracy["t_junctions"]
    )
    solutions = fiber(union, observables, use_neighbour_filter=regular)
    true_key = tuple(sorted(true_sites))
    found_true = any(
        tuple(sorted(tuple(site) for site in solution["sites"])) == true_key
        for solution in solutions
    )
    return {
        "core_id": row["core_id"],
        "center": center_name,
        "visible_mask": visible_mask,
        "visible_facets": union["visible"],
        "flat_facets": union["flat"],
        "candidate_site_count": len(sites),
        "neighbour_filter_used": regular,
        "true_sites_are_candidates": true_sites_are_candidates,
        "C032_center_recovered_exactly": center_matches,
        "observed_cells_have_disjoint_interiors": interiors_are_disjoint(
            [union["core_cell"]]
            + [union["flat_cells"][index] for index in union["flat"]]
        ),
        "fiber_size": len(solutions),
        "true_decomposition_is_in_the_fiber": found_true,
        "degeneracy": degeneracy,
        "solutions": solutions if len(solutions) != 1 else [],
    }


def run(center_names: list[str], limit: int | None) -> dict[str, Any]:
    rows = prepare_rows()
    records: list[dict[str, Any]] = []
    for core_id in sorted(rows):
        row = rows[core_id]
        upper = (1 << row["facet_count"]) - 1
        for visible_mask in range(1, upper):
            for center_name in center_names:
                records.append(census_row(row, center_name, visible_mask))
                if limit is not None and len(records) >= limit:
                    return {"records": records, "truncated": True}
    return {"records": records, "truncated": False}


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = Counter(record["fiber_size"] for record in records)
    degenerate = [
        record
        for record in records
        if record["degeneracy"]["coplanar_mergers"]
        or record["degeneracy"]["t_junctions"]
    ]
    ambiguous = [record for record in records if record["fiber_size"] != 1]
    return {
        "rows": len(records),
        "fiber_size_histogram": {str(key): sizes[key] for key in sorted(sizes)},
        "rows_with_singleton_fiber": sizes.get(1, 0),
        "rows_with_nonsingleton_fiber": len(ambiguous),
        "rows_with_observability_degeneracy": len(degenerate),
        "rows_enumerated_without_the_conditional_filter": sum(
            1 for record in records if not record["neighbour_filter_used"]
        ),
        "coplanar_merger_rows": sum(
            1 for record in records if record["degeneracy"]["coplanar_mergers"]
        ),
        "t_junction_rows": sum(
            1 for record in records if record["degeneracy"]["t_junctions"]
        ),
        "max_candidate_sites": max(
            record["candidate_site_count"] for record in records
        ),
        "true_decomposition_always_in_the_fiber": all(
            record["true_decomposition_is_in_the_fiber"] for record in records
        ),
        "true_sites_always_candidates": all(
            record["true_sites_are_candidates"] for record in records
        ),
        "C032_center_always_recovered": all(
            record["C032_center_recovered_exactly"] for record in records
        ),
        "observed_cells_always_disjoint": all(
            record["observed_cells_have_disjoint_interiors"] for record in records
        ),
    }


def build(center_names: list[str], limit: int | None) -> dict[str, Any]:
    outcome = run(center_names, limit)
    records = outcome["records"]
    metrics = summarize(records)

    assertions = {
        "catalogue_rebuilds_exactly": CAT.build()[
            "canonical_mathematical_payload_sha256"
        ]
        == json.loads(CATALOGUE_RESULT.read_text(encoding="utf-8"))[
            "canonical_mathematical_payload_sha256"
        ],
        "every_true_hidden_site_is_an_intrinsic_candidate":
            metrics["true_sites_always_candidates"],
        "C032_center_is_recomputed_exactly_on_every_row":
            metrics["C032_center_always_recovered"],
        "observed_cells_have_pairwise_disjoint_interiors_on_every_row":
            metrics["observed_cells_always_disjoint"],
        "the_true_decomposition_is_always_in_the_enumerated_fiber":
            metrics["true_decomposition_always_in_the_fiber"],
        "no_fiber_is_empty": metrics["fiber_size_histogram"].get("0", 0) == 0,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S90 fiber-census assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A43C-SIX-VERTEX-C033-FIBER-v1",
        "project": "P43",
        "phase": "S90_E_A43C_source_free_six_vertex_C033_fiber_census",
        "status": "pass_exact_spike_complete"
        if not outcome["truncated"]
        else "partial_truncated_run",
        "locked_file_sha256": {
            "results/P43_S90_E_A43B_SIX_VERTEX_RATIONAL_CATALOGUE.json":
                file_sha256(CATALOGUE_RESULT),
        },
        "centers": center_names,
        "metrics": metrics,
        "nonsingleton_fibers": [
            record for record in records if record["fiber_size"] != 1
        ],
        "per_core_metrics": {
            core_id: {
                "rows": sum(
                    1 for record in records if record["core_id"] == core_id
                ),
                "singleton_fibers": sum(
                    1
                    for record in records
                    if record["core_id"] == core_id and record["fiber_size"] == 1
                ),
                "degenerate_rows": sum(
                    1
                    for record in records
                    if record["core_id"] == core_id
                    and (
                        record["degeneracy"]["coplanar_mergers"]
                        or record["degeneracy"]["t_junctions"]
                    )
                ),
                "max_candidate_sites": max(
                    (
                        record["candidate_site_count"]
                        for record in records
                        if record["core_id"] == core_id
                    ),
                    default=0,
                ),
            }
            for core_id in sorted({record["core_id"] for record in records})
        },
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "exact source-free C033 fiber cardinality for every six-vertex proper-zero row at the frozen realizations and centers",
                "exact observability-degeneracy measurement on the same rows",
            ],
            "excluded": [
                "any statement about other realizations of the same rows",
                "any statement above six core vertices",
                "cross-size or cross-source injectivity",
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
    parser.add_argument(
        "--centers", default="centroid,generic", help="comma separated center names"
    )
    args = parser.parse_args()
    center_names = [name for name in args.centers.split(",") if name]
    result = build(center_names, args.limit)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S90 fiber census differs from exact rebuild")
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
