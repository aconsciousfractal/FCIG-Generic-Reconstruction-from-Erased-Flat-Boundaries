#!/usr/bin/env python3
"""P43 S133 / E-A72: independent exact global propagation engine.

The engine is intentionally separate from E-A71.  A source datum is converted
to a conforming tetrahedral presentation of the bare merged flat set ``M_J``;
all core/cap/facet labels are then deleted.  Boundary triangles are derived by
face cancellation.  Reconstruction receives only that raw presentation, the
recovered centre and the recovered visible facets.

At every frontier ridge it independently extracts oriented boundary rays,
recovers the new site by common projection and equal radius, selects the
connected component of the strict bisector halfspace containing that site,
recovers the cap base, and continues to BFS completion.  Source truth is read
only after reconstruction.  Four deliberate faults must be killed:
unoriented rays, reversed strict-halfspace sign, ridge-touch component choice,
and reuse of an already paired ridge.

This is an exact finite falsification engine, not a substitute for the C093
proof and not a primitive algorithm for an arbitrary implicit point set.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from itertools import combinations
from math import isqrt
from pathlib import Path
from typing import Any, Iterable, Iterator

import p43_s90_exact_rational_kernel as K
import p43_s97_e_a51_merger_type_classification as CLS
import p43_s101_e_a57_skeleton_definition_witness as SWALLOWED
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM
import p43_s109_e_a61_exceptional_centre_witness as EXC
import p43_s111_e_a63_volume_branch_witness as VOL
import p43_s112_e_a64_multiple_passing_vertices as MULTI


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S133_E_A72_INDEPENDENT_GLOBAL_PROPAGATION.json"
Point = tuple[Q, Q, Q]
Edge = tuple[Point, Point]
Triangle = tuple[Point, Point, Point]
Tetrahedron = tuple[Point, Point, Point, Point]
Ray = tuple[Q, Q, Q]

FAULTS = (
    "unoriented_ray",
    "reversed_halfspace",
    "ridge_touch_component",
    "wrong_ridge_owner",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def point_key(point: Point) -> tuple[str, str, str]:
    return tuple(str(value) for value in point)


def canonical_simplex(points: Iterable[Point]) -> tuple[Point, ...]:
    listed = tuple(sorted(set(points)))
    require(len(listed) in (2, 3, 4), "degenerate simplex in raw presentation")
    return listed


def edge_key(first: Point, second: Point) -> Edge:
    return tuple(sorted((first, second)))  # type: ignore[return-value]


def triangle_key(points: Iterable[Point]) -> Triangle:
    listed = canonical_simplex(points)
    require(len(listed) == 3, "degenerate triangle")
    return listed  # type: ignore[return-value]


def tetra_key(points: Iterable[Point]) -> Tetrahedron:
    listed = canonical_simplex(points)
    require(len(listed) == 4, "degenerate tetrahedron")
    first, second, third, fourth = listed
    volume6 = K.dot(K.subtract(second, first), K.cross(
        K.subtract(third, first), K.subtract(fourth, first)
    ))
    require(volume6 != 0, "zero-volume tetrahedron")
    return listed  # type: ignore[return-value]


def polygon_plane(points: Iterable[Point]) -> tuple[Point, Q]:
    listed = list(points)
    for first, second, third in combinations(listed, 3):
        try:
            return K.plane_through(first, second, third)
        except ValueError:
            continue
    raise RuntimeError("polygon is collinear")


def cross2(first: tuple[Q, Q], second: tuple[Q, Q], third: tuple[Q, Q]) -> Q:
    return ((second[0] - first[0]) * (third[1] - first[1])
            - (second[1] - first[1]) * (third[0] - first[0]))


def coplanar_convex_hull(points: Iterable[Point], normal: Point | None = None) -> tuple[Point, ...]:
    unique = sorted(set(points))
    require(len(unique) >= 3, "fewer than three base points")
    if normal is None:
        normal, _offset = polygon_plane(unique)
    drop = next(index for index, value in enumerate(normal) if value != 0)
    keep = [index for index in range(3) if index != drop]
    projected = sorted((point[keep[0]], point[keep[1]], point) for point in unique)

    def build_half(rows: list[tuple[Q, Q, Point]]) -> list[tuple[Q, Q, Point]]:
        half: list[tuple[Q, Q, Point]] = []
        for row in rows:
            while len(half) >= 2 and cross2(
                (half[-2][0], half[-2][1]),
                (half[-1][0], half[-1][1]),
                (row[0], row[1]),
            ) <= 0:
                half.pop()
            half.append(row)
        return half

    lower = build_half(projected)
    upper = build_half(list(reversed(projected)))
    hull = tuple(row[2] for row in lower[:-1] + upper[:-1])
    require(len(hull) >= 3, "base hull is degenerate")
    return hull


def polygon_edges(vertices: tuple[Point, ...]) -> tuple[Edge, ...]:
    return tuple(
        edge_key(vertices[index], vertices[(index + 1) % len(vertices)])
        for index in range(len(vertices))
    )


def facet_key(vertices: Iterable[Point]) -> tuple[Point, ...]:
    return tuple(sorted(set(vertices)))


def triangulate_polygon(vertices: list[Point]) -> list[Triangle]:
    require(len(vertices) >= 3, "facet polygon has fewer than three vertices")
    return [
        triangle_key((vertices[0], vertices[index], vertices[index + 1]))
        for index in range(1, len(vertices) - 1)
    ]


def subdivide_tetrahedra(tetrahedra: Iterable[Tetrahedron]) -> tuple[Tetrahedron, ...]:
    subdivided: list[Tetrahedron] = []
    for tetrahedron in tetrahedra:
        centre = K.average(tetrahedron)
        for omitted in range(4):
            face = [tetrahedron[index] for index in range(4) if index != omitted]
            subdivided.append(tetra_key((centre, *face)))
    return tuple(sorted(subdivided))


def boundary_from_tetrahedra(tetrahedra: Iterable[Tetrahedron]) -> tuple[Triangle, ...]:
    counts: dict[Triangle, int] = {}
    for tetrahedron in tetrahedra:
        for face in combinations(tetrahedron, 3):
            key = triangle_key(face)
            counts[key] = counts.get(key, 0) + 1
    require(all(count in (1, 2) for count in counts.values()), "nonconforming tetrahedral presentation")
    return tuple(sorted(face for face, count in counts.items() if count == 1))


def build_source_scrubbed_input(
    row: dict[str, Any], union: dict[str, Any], subdivided: bool
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Build raw input and separate truth, then delete every source label."""
    points: list[Point] = list(row["points"])
    centre: Point = union["center"]
    flat = set(union["flat"])
    visible = set(union["visible"])
    require(flat and visible and flat.isdisjoint(visible), "datum is not proper-zero")
    require(flat | visible == set(range(row["facet_count"])), "facet partition drift")

    cycles: list[list[int]] = row["core"]["facets_cyclic"]
    tetrahedra: list[Tetrahedron] = []
    apexes: list[Point] = []
    for facet_index, cycle in enumerate(cycles):
        polygon = [points[index] for index in cycle]
        triangles = triangulate_polygon(polygon)
        for triangle in triangles:
            tetrahedra.append(tetra_key((centre, *triangle)))
        normal, offset = row["planes"][facet_index]
        apex = K.reflect_point(centre, normal, offset)
        apexes.append(apex)
        if facet_index in flat:
            for triangle in triangles:
                tetrahedra.append(tetra_key((apex, *triangle)))

    raw_tetrahedra = tuple(sorted(set(tetrahedra)))
    if subdivided:
        raw_tetrahedra = subdivide_tetrahedra(raw_tetrahedra)
    boundary = boundary_from_tetrahedra(raw_tetrahedra)
    visible_facets = tuple(sorted(
        (coplanar_convex_hull(points[index] for index in cycles[facet_index])
         for facet_index in visible),
        key=facet_key,
    ))
    raw = {
        "center": centre,
        "tetrahedra": raw_tetrahedra,
        "boundary_triangles": boundary,
        "visible_facets": visible_facets,
    }
    require(set(raw) == {"center", "tetrahedra", "boundary_triangles", "visible_facets"},
            "raw contract leaked a source field")

    incidences = [0 for _point in points]
    for cycle in cycles:
        for index in cycle:
            incidences[index] += 1
    truth = {
        "hidden_sites": tuple(sorted(apexes[index] for index in flat)),
        "hidden_facets": tuple(sorted(
            (facet_key(points[index] for index in cycles[facet_index]) for facet_index in flat)
        )),
        "all_facets": tuple(sorted(
            (facet_key(points[index] for index in cycle) for cycle in cycles)
        )),
        "hidden_count": len(flat),
        "non_simple": any(count > 3 for count in incidences),
    }
    return raw, truth


def point_on_segment(point: Point, first: Point, second: Point) -> bool:
    direction = K.subtract(second, first)
    offset = K.subtract(point, first)
    if not K.is_zero(K.cross(direction, offset)):
        return False
    return 0 <= K.dot(offset, direction) <= K.squared_norm(direction)


def transverse(vector: Point, edge_direction: Point) -> Point:
    factor = K.dot(vector, edge_direction) / K.squared_norm(edge_direction)
    return K.subtract(vector, K.scale(factor, edge_direction))


def ray_signature(vector: Point, fault: str | None = None) -> Ray:
    require(not K.is_zero(vector), "zero vector has no ray")
    pivot = next(value for value in vector if value != 0)
    oriented = tuple(value / abs(pivot) for value in vector)
    if fault == "unoriented_ray":
        opposite = tuple(-value for value in oriented)
        oriented = min(oriented, opposite)
    return oriented  # type: ignore[return-value]


def choose_sample(edge: Edge, triangles: tuple[Triangle, ...]) -> Point:
    first, second = edge
    direction = K.subtract(second, first)
    for numerator in range(1, 257):
        parameter = Q(numerator, 257)
        sample = K.add(first, K.scale(parameter, direction))
        bad = False
        for triangle in triangles:
            for head, tail in polygon_edges(triangle):
                if point_on_segment(sample, head, tail) and not K.is_zero(
                    K.cross(direction, K.subtract(tail, head))
                ):
                    bad = True
                    break
            if bad:
                break
        if not bad:
            return sample
    raise RuntimeError("could not choose a generic point on frontier ridge")


def local_boundary_rays(
    triangles: tuple[Triangle, ...], edge: Edge, fault: str | None = None
) -> tuple[Point, set[Ray]]:
    sample = choose_sample(edge, triangles)
    first, second = edge
    edge_direction = K.subtract(second, first)
    rays: set[Ray] = set()

    for triangle in triangles:
        normal, offset = K.plane_through(*triangle)
        if K.dot(normal, sample) != offset:
            continue
        signs = [
            K.dot(normal, K.cross(
                K.subtract(triangle[(index + 1) % 3], triangle[index]),
                K.subtract(sample, triangle[index]),
            ))
            for index in range(3)
        ]
        if not (all(value >= 0 for value in signs) or all(value <= 0 for value in signs)):
            continue
        zero_edges = [index for index, value in enumerate(signs) if value == 0]
        if not zero_edges:
            side = K.cross(normal, edge_direction)
            rays.add(ray_signature(side, fault))
            rays.add(ray_signature(K.scale(Q(-1), side), fault))
            continue
        for index in zero_edges:
            head, tail = triangle[index], triangle[(index + 1) % 3]
            if point_on_segment(sample, head, tail) and K.is_zero(
                K.cross(edge_direction, K.subtract(tail, head))
            ):
                interior = transverse(K.subtract(K.average(triangle), sample), edge_direction)
                rays.add(ray_signature(interior, fault))
                break
    return sample, rays


def project_to_line(point: Point, edge: Edge) -> Point:
    first, second = edge
    direction = K.subtract(second, first)
    parameter = K.dot(K.subtract(point, first), direction) / K.squared_norm(direction)
    return K.add(first, K.scale(parameter, direction))


def exact_sqrt(value: Q) -> Q:
    require(value >= 0, "negative exact square")
    numerator = isqrt(value.numerator)
    denominator = isqrt(value.denominator)
    require(numerator * numerator == value.numerator, "nonsquare numerator in site recovery")
    require(denominator * denominator == value.denominator, "nonsquare denominator in site recovery")
    return Q(numerator, denominator)


def recover_site(centre: Point, edge: Edge, direction: Ray) -> Point:
    projection = project_to_line(centre, edge)
    radius2 = K.squared_norm(K.subtract(centre, projection))
    direction2 = K.squared_norm(direction)
    factor = exact_sqrt(radius2 / direction2)
    return K.add(projection, K.scale(factor, direction))


def strict_side_value(point: Point, centre: Point, site: Point, fault: str | None = None) -> Q:
    value = K.squared_norm(K.subtract(point, centre)) - K.squared_norm(K.subtract(point, site))
    return -value if fault == "reversed_halfspace" else value


def strict_halfspace_components(
    tetrahedra: tuple[Tetrahedron, ...], centre: Point, site: Point,
    fault: str | None = None,
) -> tuple[list[set[int]], dict[Point, Q]]:
    vertices = sorted({point for tetrahedron in tetrahedra for point in tetrahedron})
    values = {point: strict_side_value(point, centre, site, fault) for point in vertices}
    active = [
        index for index, tetrahedron in enumerate(tetrahedra)
        if any(values[point] > 0 for point in tetrahedron)
    ]
    require(active, "strict halfspace misses the raw union")

    parent = {index: index for index in active}

    def find(index: int) -> int:
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(first: int, second: int) -> None:
        first_root, second_root = find(first), find(second)
        if first_root != second_root:
            parent[max(first_root, second_root)] = min(first_root, second_root)

    by_positive_vertex: dict[Point, list[int]] = {}
    for index in active:
        for point in tetrahedra[index]:
            if values[point] > 0:
                by_positive_vertex.setdefault(point, []).append(index)
    for owners in by_positive_vertex.values():
        for other in owners[1:]:
            union(owners[0], other)

    grouped: dict[int, set[int]] = {}
    for index in active:
        grouped.setdefault(find(index), set()).add(index)
    components = sorted(grouped.values(), key=lambda component: min(component))
    return components, values


def component_vertices(component: set[int], tetrahedra: tuple[Tetrahedron, ...]) -> set[Point]:
    return {point for index in component for point in tetrahedra[index]}


def select_component(
    components: list[set[int]], tetrahedra: tuple[Tetrahedron, ...], site: Point,
    ridge: Edge, fault: str | None = None,
) -> tuple[set[int], int]:
    containing_site = [
        component for component in components
        if site in component_vertices(component, tetrahedra)
    ]
    require(len(containing_site) == 1, "site does not select exactly one strict component")
    target = containing_site[0]
    ridge_touching = [
        component for component in components
        if any(point_on_segment(point, *ridge) for point in component_vertices(component, tetrahedra))
    ]
    wrong_touching = [component for component in ridge_touching if component is not target]
    if fault == "ridge_touch_component" and wrong_touching:
        return wrong_touching[0], len(wrong_touching)
    return target, len(wrong_touching)


def recover_cap_base(
    raw: dict[str, Any], site: Point, ridge: Edge, fault: str | None = None,
) -> tuple[tuple[Point, ...], int]:
    tetrahedra: tuple[Tetrahedron, ...] = raw["tetrahedra"]
    centre: Point = raw["center"]
    components, values = strict_halfspace_components(tetrahedra, centre, site, fault)
    component, ambiguity = select_component(components, tetrahedra, site, ridge, fault)
    vertices = component_vertices(component, tetrahedra)
    base_points = [point for point in vertices if values[point] == 0]
    bisector_normal = K.subtract(site, centre)
    base = coplanar_convex_hull(base_points, bisector_normal)
    require(ridge in polygon_edges(base), "selected component does not recover the frontier ridge")
    return base, ambiguity


def frontier_candidates(
    facets: list[dict[str, Any]], fault: str | None = None,
) -> list[tuple[Edge, int]]:
    owners: dict[Edge, list[int]] = {}
    for index, facet in enumerate(facets):
        for edge in polygon_edges(facet["vertices"]):
            owners.setdefault(edge, []).append(index)
    require(all(len(indices) <= 2 for indices in owners.values()), "a recovered ridge has more than two owners")
    paired = sorted((edge, indices[0]) for edge, indices in owners.items() if len(indices) == 2)
    if fault == "wrong_ridge_owner" and paired:
        return [paired[0]]
    return sorted((edge, indices[0]) for edge, indices in owners.items() if len(indices) == 1)


def reconstruct(raw: dict[str, Any], fault: str | None = None) -> dict[str, Any]:
    require(fault is None or fault in FAULTS, f"unknown fault {fault}")
    require(set(raw) == {"center", "tetrahedra", "boundary_triangles", "visible_facets"},
            "reconstruction input contains source provenance")
    facets = [
        {"vertices": tuple(vertices), "site": None}
        for vertices in raw["visible_facets"]
    ]
    require(facets, "proper-zero reconstruction has no visible anchor")
    recovered_sites: set[Point] = set()
    metrics = {
        "steps": 0,
        "visible_to_hidden_steps": 0,
        "hidden_to_hidden_steps": 0,
        "straight_coplanar_fusions": 0,
        "component_extractions": 0,
        "ridge_touch_ambiguities": 0,
    }

    maximum_steps = len(raw["tetrahedra"]) + 1
    while True:
        frontiers = frontier_candidates(facets, fault)
        if not frontiers:
            break
        require(metrics["steps"] < maximum_steps, "global propagation did not terminate")
        ridge, owner = frontiers[0]
        known = facets[owner]
        sample, rays = local_boundary_rays(raw["boundary_triangles"], ridge, fault)
        centre: Point = raw["center"]
        projection = project_to_line(centre, ridge)
        if known["site"] is None:
            known_vector = transverse(
                K.subtract(K.average(known["vertices"]), sample),
                K.subtract(ridge[1], ridge[0]),
            )
            metrics["visible_to_hidden_steps"] += 1
        else:
            known_vector = K.subtract(known["site"], projection)
            metrics["hidden_to_hidden_steps"] += 1
        known_ray = ray_signature(known_vector, fault)
        require(known_ray in rays, "known oriented half-sheet is absent from raw tangent cone")
        remaining = rays - {known_ray}
        require(len(remaining) == 1, "frontier ridge does not expose exactly one new oriented ray")
        new_ray = next(iter(remaining))
        if K.is_zero(K.cross(known_ray, new_ray)):
            metrics["straight_coplanar_fusions"] += 1
        site = recover_site(centre, ridge, new_ray)
        require(site not in recovered_sites, "propagation recovered a duplicate hidden site")
        require(any(site in tetrahedron for tetrahedron in raw["tetrahedra"]),
                "recovered site is not a vertex of the bare raw presentation")
        base, ambiguity = recover_cap_base(raw, site, ridge, fault)
        require(facet_key(base) not in {facet_key(facet["vertices"]) for facet in facets},
                "propagation recovered a duplicate facet")
        facets.append({"vertices": base, "site": site})
        recovered_sites.add(site)
        metrics["steps"] += 1
        metrics["component_extractions"] += 1
        metrics["ridge_touch_ambiguities"] += ambiguity

    owners: dict[Edge, int] = {}
    for facet in facets:
        for edge in polygon_edges(facet["vertices"]):
            owners[edge] = owners.get(edge, 0) + 1
    require(owners and all(count == 2 for count in owners.values()),
            "BFS stopped before the recovered facet surface closed")
    return {
        "sites": tuple(sorted(recovered_sites)),
        "hidden_facets": tuple(sorted(
            facet_key(facet["vertices"]) for facet in facets if facet["site"] is not None
        )),
        "all_facets": tuple(sorted(facet_key(facet["vertices"]) for facet in facets)),
        "metrics": metrics,
    }


def compare_to_truth(reconstruction: dict[str, Any], truth: dict[str, Any]) -> list[str]:
    failures = []
    if reconstruction["sites"] != truth["hidden_sites"]:
        failures.append("hidden_sites")
    if reconstruction["hidden_facets"] != truth["hidden_facets"]:
        failures.append("hidden_facets")
    if reconstruction["all_facets"] != truth["all_facets"]:
        failures.append("all_facets")
    if reconstruction["metrics"]["steps"] != truth["hidden_count"]:
        failures.append("hidden_count")
    return failures


def row_from_points(core_id: str, points: list[Point], centre: Point) -> dict[str, Any]:
    facets = K.hull_facets(points)
    census, cyclic, planes = [], [], []
    for (normal, offset), indices in facets:
        listed = [points[index] for index in indices]
        order = K.cyclic_order(listed, normal)
        census.append(list(indices))
        cyclic.append([indices[position] for position in order])
        planes.append((normal, offset))
    return {
        "core_id": core_id,
        "core": {"facets_cyclic": cyclic},
        "census_facets": census,
        "facet_count": len(facets),
        "points": points,
        "planes": planes,
        "centers": {"c": centre},
    }


def source_data(limit: int | None) -> Iterator[tuple[str, dict[str, Any], dict[str, Any], str]]:
    rows = 0
    stop = False
    for entry in CLS.configurations():
        row = {
            key: entry[key]
            for key in (
                "core_id", "core", "census_facets", "facet_count",
                "points", "planes", "centers",
            )
        }
        upper = (1 << entry["facet_count"]) - 1
        for centre_name in sorted(entry["centers"]):
            for visible_mask in range(1, upper):
                visible = [index for index in range(entry["facet_count"]) if visible_mask >> index & 1]
                flat = [index for index in range(entry["facet_count"]) if index not in visible]
                centre = entry["centers"][centre_name]
                apex = [K.reflect_point(centre, *plane) for plane in entry["planes"]]
                union = {"center": centre, "visible": visible, "flat": flat, "apex": apex}
                yield f"corpus:{entry['core_id']}:{centre_name}:{visible_mask}", row, union, "frozen_corpus"
                rows += 1
                if limit is not None and rows >= limit:
                    stop = True
                    break
            if stop:
                break
        if stop:
            break

    for shape in EXC.WITNESS_SHAPES:
        built = EXC.build_witness(*shape)
        yield f"exceptional:{shape}", built["row"], built["union"], "exceptional_centre"
    for bound in VOL.BOUNDS:
        built = VOL.build_volume_witness(bound)
        require(built is not None, f"volume witness {bound} failed to build")
        yield f"volume:{bound}", built["row"], built["union"], "volume_branch"
    for shape in MULTI.SHAPES:
        built = MULTI.build(shape)
        require(built is not None, f"multiple-passing witness {shape} failed to build")
        union = built["union"]
        row = row_from_points(f"MULTI-{shape}", list(built["points"]), union["center"])
        require(row["facet_count"] == len(union["visible"]) + len(union["flat"]), "facet order drift")
        yield f"multiple:{shape}", row, union, "multiple_passing"

    witness = GERM.witness_union()
    witness_points = [tuple(Q(value) for value in point) for point in SWALLOWED.WITNESS_VERTICES]
    row = row_from_points("S101-SWALLOWED", witness_points, witness["center"])
    witness["visible"] = [index for index in range(row["facet_count"]) if index not in witness["flat"]]
    yield "s101:swallowed-corner", row, witness, "swallowed_corner"


def fault_is_killed(raw: dict[str, Any], truth: dict[str, Any], fault: str) -> tuple[bool, str]:
    try:
        result = reconstruct(raw, fault)
        failures = compare_to_truth(result, truth)
        if failures:
            return True, "post_reconstruction_mismatch:" + ",".join(failures)
        return False, "mutation_survived"
    except (RuntimeError, ValueError, ZeroDivisionError) as error:
        return True, f"fail_closed:{type(error).__name__}:{error}"


def build(limit: int | None, presentation_prefix: int, run_mutations: bool = True) -> dict[str, Any]:
    metrics = {
        "data": 0,
        "categories": {},
        "global_bfs_steps": 0,
        "visible_to_hidden_steps": 0,
        "hidden_to_hidden_steps": 0,
        "straight_coplanar_fusions": 0,
        "component_extractions": 0,
        "ridge_touch_ambiguities": 0,
        "non_simple_data": 0,
        "presentation_subdivision_data": 0,
        "failures": 0,
    }
    reports = []
    failures = []
    probes: dict[str, tuple[str, dict[str, Any], dict[str, Any]] | None] = {
        fault: None for fault in FAULTS
    }

    for index, (name, row, union, category) in enumerate(source_data(limit)):
        subdivided = index < presentation_prefix
        raw, truth = build_source_scrubbed_input(row, union, subdivided)
        try:
            reconstruction = reconstruct(raw)
            differences = compare_to_truth(reconstruction, truth)
        except (RuntimeError, ValueError, ZeroDivisionError) as error:
            reconstruction = {"metrics": {
                "steps": 0, "visible_to_hidden_steps": 0,
                "hidden_to_hidden_steps": 0, "straight_coplanar_fusions": 0,
                "component_extractions": 0, "ridge_touch_ambiguities": 0,
            }}
            differences = [f"exception:{type(error).__name__}:{error}"]
        report_metrics = reconstruction["metrics"]
        if differences:
            failures.append({"datum": name, "differences": differences})

        metrics["data"] += 1
        metrics["categories"][category] = metrics["categories"].get(category, 0) + 1
        metrics["global_bfs_steps"] += report_metrics["steps"]
        metrics["visible_to_hidden_steps"] += report_metrics["visible_to_hidden_steps"]
        metrics["hidden_to_hidden_steps"] += report_metrics["hidden_to_hidden_steps"]
        metrics["straight_coplanar_fusions"] += report_metrics["straight_coplanar_fusions"]
        metrics["component_extractions"] += report_metrics["component_extractions"]
        metrics["ridge_touch_ambiguities"] += report_metrics["ridge_touch_ambiguities"]
        metrics["non_simple_data"] += int(truth["non_simple"])
        metrics["presentation_subdivision_data"] += int(subdivided)

        candidate = (name, raw, truth)
        if probes["reversed_halfspace"] is None:
            probes["reversed_halfspace"] = candidate
        if probes["wrong_ridge_owner"] is None and truth["hidden_count"] >= 2:
            probes["wrong_ridge_owner"] = candidate
        if probes["unoriented_ray"] is None and report_metrics["straight_coplanar_fusions"] > 0:
            probes["unoriented_ray"] = candidate
        if probes["ridge_touch_component"] is None and report_metrics["ridge_touch_ambiguities"] > 0:
            probes["ridge_touch_component"] = candidate

        if category != "frozen_corpus":
            reports.append({
                "datum": name,
                "category": category,
                "subdivided_presentation": subdivided,
                "metrics": report_metrics,
                "differences": differences,
            })

    metrics["failures"] = len(failures)
    mutation_results = {}
    if run_mutations:
        for fault in FAULTS:
            probe = probes[fault]
            require(probe is not None, f"no exact mutation probe found for {fault}")
            name, raw, truth = probe
            killed, mechanism = fault_is_killed(raw, truth, fault)
            mutation_results[fault] = {
                "datum": name,
                "killed": killed,
                "mechanism": mechanism,
            }
            require(killed, f"E-A72 mutation survived: {fault} on {name}")

    assertions = {
        "raw_engine_contract_contains_no_source_labels_masks_cap_ids_or_kind_fields": True,
        "boundary_is_derived_by_exact_tetrahedral_face_cancellation": True,
        "truth_is_compared_only_after_global_reconstruction": True,
        "every_global_reconstruction_matches_sites_caps_facets_and_hidden_count": not failures,
        "visible_to_hidden_and_hidden_to_hidden_steps_are_both_exercised": (
            metrics["visible_to_hidden_steps"] > 0 and metrics["hidden_to_hidden_steps"] > 0
        ),
        "straight_coplanar_fusions_are_exercised": metrics["straight_coplanar_fusions"] > 0,
        "strict_component_extraction_is_exercised_at_every_step": (
            metrics["component_extractions"] == metrics["global_bfs_steps"] > 0
        ),
        "ridge_touch_is_shown_to_be_ambiguous_on_exact_data": metrics["ridge_touch_ambiguities"] > 0,
        "non_simple_data_are_exercised": metrics["non_simple_data"] > 0,
        "presentation_subdivision_is_exercised": metrics["presentation_subdivision_data"] > 0,
        "all_four_deliberate_faults_are_killed": (
            not run_mutations or all(row["killed"] for row in mutation_results.values())
        ),
        "all_adversarial_families_are_exercised": all(
            metrics["categories"].get(category, 0) > 0
            for category in ("exceptional_centre", "volume_branch", "multiple_passing", "swallowed_corner")
        ),
    }
    require(all(assertions.values()),
            f"E-A72 assertion failure: {[key for key, value in assertions.items() if not value]}")

    result: dict[str, Any] = {
        "schema_version": "P43-E-A72-INDEPENDENT-GLOBAL-PROPAGATION-v1",
        "project": "P43",
        "phase": "S133_E_A72_independent_global_propagation",
        "status": "pass_no_global_counterexample_in_exact_domain",
        "independence_contract": {
            "does_not_import_E_A71": True,
            "raw_fields": ["boundary_triangles", "center", "tetrahedra", "visible_facets"],
            "source_truth_read_after_reconstruction_only": True,
            "internal_source_interfaces_are_presentation_only": True,
        },
        "metrics": metrics,
        "mutation_kills": mutation_results,
        "adversarial_families": reports,
        "failures": failures,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "an independent source-scrubbed exact engine reaches global BFS completion on the audited domain",
                "every reconstructed hidden site cap base and complete facet family equals source truth after reconstruction",
                "strict-halfspace component selection survives exact ridge-touch ambiguity",
                "four independent orientation sign component and ridge-owner faults are killed",
            ],
            "excluded": [
                "a replacement for the abstract C093 proof",
                "all-zero data without a visible anchor",
                "dimension above three",
                "a primitive implementation from an arbitrary implicit or noisy point set",
                "novelty priority or public readiness",
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
    parser.add_argument("--presentation-prefix", type=int, default=256)
    parser.add_argument("--skip-mutations", action="store_true")
    arguments = parser.parse_args()
    result = build(arguments.limit, arguments.presentation_prefix, not arguments.skip_mutations)
    if arguments.verify_existing:
        stored = json.loads(arguments.output.read_text(encoding="utf-8"))
        require(stored == result, "stored E-A72 result differs from exact rebuild")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
