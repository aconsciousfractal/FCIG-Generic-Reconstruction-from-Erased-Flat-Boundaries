#!/usr/bin/env python3
"""P43 S101 / E-A57 the 1-skeleton definition of the merged complex is load-bearing.

S100 defines the apex signature through the "neighbours of a in the merged
boundary complex" without saying what the complex's edges are. Two readings are
available and they are not equivalent:

  side reading      the edges are the surviving sides of the original patches,
                    a side being erased when two patches of the same plane
                    carry it; this is what the implementation does
  polygon reading   the edges are the 1-faces of the merged polygons, so a
                    corner collinear with its two neighbours is swallowed

This script shows the two disagree, by construction rather than by search. Put
a core vertex of a shared edge exactly at the foot of the perpendicular from
the centre to that edge's line. Then the two apexes and that vertex are
collinear, so the merged patch of Lemma 3.6 is a triangle rather than a
quadrilateral, and the polygon reading swallows the vertex and hands the apex
the *other apex* as a neighbour. The apex then fails its own signature.

The witness datum is

    P = {x >= 0, z >= 0, x + y >= 2, y <= 6, x + z <= 4},   o = (1, 2, 1)

whose hidden facets {x = 0} and {z = 0} are perpendicular and share the y-axis
edge from (0,2,0) to (0,6,0); the foot of o on that line is (0,2,0), an
endpoint of the edge.

It also sweeps the six-vertex corpus for the same phenomenon, to record that
the corpus never exercises it: the condition is one linear equation on the
centre, so four sampled rational centres miss it. That is why the gap survived
to S100 and why a witness had to be built rather than found.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s97_e_a51_merger_type_classification as CLS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S101_E_A57_SKELETON_DEFINITION.json"

WITNESS_VERTICES = [
    (0, 2, 0),   # the foot of the perpendicular from o to the shared edge
    (0, 6, 0),
    (0, 2, 4),
    (0, 6, 4),
    (4, -2, 0),
    (4, 6, 0),
]
WITNESS_CENTER = (1, 2, 1)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def rational(point) -> K.Point:
    return tuple(Q(coordinate) for coordinate in point)


def coplanar_groups(patches: list[dict[str, Any]]) -> list[list[int]]:
    """Maximal sets of patches sharing a plane and connected by shared edges."""
    by_plane: dict[Any, list[int]] = defaultdict(list)
    for index, patch in enumerate(patches):
        by_plane[patch["plane"]].append(index)

    groups: list[list[int]] = []
    for indices in by_plane.values():
        if len(indices) < 2:
            continue
        keys = {
            index: set(K.point_set_key(patches[index]["points"])) for index in indices
        }
        remaining = set(indices)
        while remaining:
            start = remaining.pop()
            component = [start]
            frontier = [start]
            while frontier:
                current = frontier.pop()
                for other in list(remaining):
                    if len(keys[current] & keys[other]) < 2:
                        continue
                    remaining.discard(other)
                    component.append(other)
                    frontier.append(other)
            if len(component) > 1:
                groups.append(sorted(component))
    return groups


def swallowed_corners(
    patches: list[dict[str, Any]], group: list[int]
) -> list[K.Point]:
    """Corners of a merged component that the polygon reading would drop."""
    corners: dict[tuple[str, str, str], K.Point] = {}
    for index in group:
        for point in patches[index]["points"]:
            corners[K.point_key(point)] = point
    listed = list(corners.values())
    if len(listed) < 3:
        return []
    normal = tuple(Q(component) for component in patches[group[0]]["plane"][0])
    cycle = [listed[position] for position in K.cyclic_order(listed, normal)]
    dropped = []
    count = len(cycle)
    for position in range(count):
        previous = cycle[(position - 1) % count]
        here = cycle[position]
        following = cycle[(position + 1) % count]
        if K.is_zero(
            K.cross(K.subtract(here, previous), K.subtract(following, here))
        ):
            dropped.append(here)
    return dropped


def polygon_neighbours(
    patches: list[dict[str, Any]], group: list[int], site: K.Point
) -> list[K.Point] | None:
    """Neighbours of `site` under the polygon reading, or None if not a corner."""
    corners: dict[tuple[str, str, str], K.Point] = {}
    for index in group:
        for point in patches[index]["points"]:
            corners[K.point_key(point)] = point
    listed = list(corners.values())
    normal = tuple(Q(component) for component in patches[group[0]]["plane"][0])
    cycle = [listed[position] for position in K.cyclic_order(listed, normal)]
    hull = []
    count = len(cycle)
    for position in range(count):
        previous = cycle[(position - 1) % count]
        here = cycle[position]
        following = cycle[(position + 1) % count]
        if K.is_zero(
            K.cross(K.subtract(here, previous), K.subtract(following, here))
        ):
            continue
        hull.append(here)
    key = K.point_key(site)
    for position, point in enumerate(hull):
        if K.point_key(point) == key:
            return [
                hull[(position - 1) % len(hull)],
                hull[(position + 1) % len(hull)],
            ]
    return None


def on_bisector(centre: K.Point, site: K.Point, point: K.Point) -> bool:
    return K.squared_norm(K.subtract(point, centre)) == K.squared_norm(
        K.subtract(point, site)
    )


def build_witness() -> dict[str, Any]:
    vertices = [rational(point) for point in WITNESS_VERTICES]
    centre = rational(WITNESS_CENTER)
    facets = K.hull_facets(vertices)

    convex = all(
        K.dot(normal, vertex) <= offset
        for (normal, offset), _ in facets
        for vertex in vertices
    )
    interior = all(K.dot(normal, centre) < offset for (normal, offset), _ in facets)

    hidden = [
        index
        for index, (_, indices) in enumerate(facets)
        if set(indices) >= {0, 1}
    ]
    normals = [facets[index][0][0] for index in hidden]
    perpendicular = K.dot(normals[0], normals[1]) == 0

    planes = [plane for plane, _ in facets]
    apexes = [K.reflect_point(centre, normal, offset) for normal, offset in planes]
    first, second = apexes[hidden[0]], apexes[hidden[1]]
    shared = vertices[0]
    midpoint = K.scale(Q(1, 2), K.add(first, second))
    collinear = K.is_zero(K.cross(K.subtract(second, first), K.subtract(shared, first)))

    patches: list[dict[str, Any]] = []
    for index, ((normal, offset), corner_indices) in enumerate(facets):
        points = [vertices[position] for position in corner_indices]
        key = K.unoriented_plane_key(normal, offset)
        if index not in hidden:
            patches.append({"points": points, "plane": key, "kind": "hinge"})
            continue
        order = K.cyclic_order(points, normal)
        cycle = [points[position] for position in order]
        for position in range(len(cycle)):
            head = cycle[position]
            tail = cycle[(position + 1) % len(cycle)]
            wall_normal, wall_offset = K.plane_through(apexes[index], head, tail)
            patches.append(
                {
                    "points": [apexes[index], head, tail],
                    "plane": K.unoriented_plane_key(wall_normal, wall_offset),
                    "kind": "wall",
                }
            )

    edges, point_by_key = CEN.merged_boundary_edges(patches)
    side_neighbours = list(
        {
            K.point_key(point): point
            for point in CEN.merged_neighbours(first, edges, point_by_key)
        }.values()
    )
    side_passes = all(on_bisector(centre, first, point) for point in side_neighbours)

    groups = coplanar_groups(patches)
    group = next(
        indices
        for indices in groups
        if any(
            K.point_key(first) in [K.point_key(q) for q in patches[index]["points"]]
            for index in indices
        )
    )
    dropped = swallowed_corners(patches, group)
    polygon = polygon_neighbours(patches, group, first)
    polygon_passes = (
        all(on_bisector(centre, first, point) for point in polygon)
        if polygon is not None
        else None
    )

    return {
        "vertices": [[str(c) for c in vertex] for vertex in vertices],
        "centre": [str(c) for c in centre],
        "facet_count": len(facets),
        "core_is_convex_with_these_vertices": convex,
        "centre_is_strictly_interior": interior,
        "the_two_facets_on_the_shared_edge_are_perpendicular": perpendicular,
        "apex": [str(c) for c in first],
        "other_apex": [str(c) for c in second],
        "midpoint_of_the_two_apexes": [str(c) for c in midpoint],
        "midpoint_is_the_shared_edge_endpoint": midpoint == shared,
        "apex_endpoint_apex_are_collinear": collinear,
        "inter_patch_t_junctions": CEN.degeneracy_report(patches)["t_junctions"],
        "side_reading_neighbours": sorted(
            [str(c) for c in point] for point in side_neighbours
        ),
        "side_reading_apex_passes": side_passes,
        "polygon_reading_swallowed_corners": sorted(
            [str(c) for c in point] for point in dropped
        ),
        "polygon_reading_neighbours": (
            sorted([str(c) for c in point] for point in polygon)
            if polygon is not None
            else None
        ),
        "polygon_reading_apex_passes": polygon_passes,
        "the_two_readings_disagree": side_passes != polygon_passes,
    }


def sweep_corpus(limit: int | None) -> dict[str, Any]:
    rows = 0
    rows_with_a_merged_component = 0
    rows_with_a_swallowed_corner = 0
    merged_components = 0

    for entry in CLS.configurations():
        row = {
            key: entry[key]
            for key in (
                "core_id",
                "core",
                "census_facets",
                "facet_count",
                "points",
                "planes",
                "centers",
            )
        }
        upper = (1 << entry["facet_count"]) - 1
        for centre_name in sorted(entry["centers"]):
            for mask in range(1, upper):
                union = CEN.build_raw_union(row, centre_name, mask)
                rows += 1
                groups = coplanar_groups(union["patches"])
                if not groups:
                    if limit is not None and rows >= limit:
                        break
                    continue
                rows_with_a_merged_component += 1
                merged_components += len(groups)
                if any(
                    swallowed_corners(union["patches"], group) for group in groups
                ):
                    rows_with_a_swallowed_corner += 1
                if limit is not None and rows >= limit:
                    break
            if limit is not None and rows >= limit:
                break
        if limit is not None and rows >= limit:
            break

    return {
        "rows_examined": rows,
        "rows_with_a_merged_component": rows_with_a_merged_component,
        "merged_components": merged_components,
        "rows_where_the_polygon_reading_swallows_a_corner": rows_with_a_swallowed_corner,
    }


def build(limit: int | None) -> dict[str, Any]:
    witness = build_witness()
    corpus = sweep_corpus(limit)

    assertions = {
        "the_witness_is_a_legitimate_datum": (
            witness["core_is_convex_with_these_vertices"]
            and witness["centre_is_strictly_interior"]
            and witness["the_two_facets_on_the_shared_edge_are_perpendicular"]
        ),
        "the_witness_is_the_predicted_collinear_configuration": (
            witness["midpoint_is_the_shared_edge_endpoint"]
            and witness["apex_endpoint_apex_are_collinear"]
        ),
        "the_side_reading_keeps_the_apex_passing": witness["side_reading_apex_passes"],
        "the_polygon_reading_rejects_the_true_apex": (
            witness["polygon_reading_apex_passes"] is False
        ),
        "the_two_readings_disagree": witness["the_two_readings_disagree"],
        "no_inter_patch_t_junction_is_present_in_the_witness": (
            witness["inter_patch_t_junctions"] == 0
        ),
        "the_corpus_never_exercises_the_phenomenon": (
            corpus["rows_where_the_polygon_reading_swallows_a_corner"] == 0
        )
        if limit is None
        else True,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S101 skeleton-definition assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A57-SKELETON-DEFINITION-v1",
        "project": "P43",
        "phase": "S101_E_A57_skeleton_definition_witness",
        "status": "pass_exact_definition_witness_built",
        "finding": (
            "the 1-skeleton of the merged complex must be the surviving sides of "
            "the original patches, not the 1-faces of the merged polygons; the "
            "two readings disagree on a legitimate datum and only the first "
            "keeps Theorem A true"
        ),
        "why_the_corpus_missed_it": (
            "the configuration is one linear equation on the centre, namely that "
            "the foot of the perpendicular from the centre to a shared edge line "
            "is an endpoint of that edge, so sampled rational centres miss it"
        ),
        "witness": witness,
        "corpus": corpus,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "a legitimate datum on which the two readings of the signature "
                "disagree, so the definition is load-bearing and must be stated",
                "the six-vertex corpus never exercises the phenomenon",
            ],
            "excluded": [
                "any claim that the phenomenon is rare in a measure-theoretic "
                "sense beyond the one linear equation identified",
                "any change to the exceptional set of Theorem B, which is "
                "unaffected because the side reading keeps the theorem true",
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
            raise SystemExit("stored S101 witness differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps({"witness_disagreement": result["witness"][
        "the_two_readings_disagree"]}, indent=2))
    print(json.dumps(result["corpus"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
