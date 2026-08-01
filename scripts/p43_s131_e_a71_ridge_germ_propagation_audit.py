#!/usr/bin/env python3
"""P43 S131 / E-A71: exact adversarial audit of ridge-germ propagation.

The proposed universal proper-zero route has one load-bearing local assertion.
At a ridge between a recovered facet and an unrecovered flat facet, the raw
boundary of the merged flat component must expose exactly two oriented
half-sheet germs: the already known germ and the wall germ of the next cap.

This script tests that assertion without reading ``kind`` labels or cap ids in
the boundary soup.  It samples a source-free local cross-section, canonicalises
oriented rays, and checks that the remaining ray determines the true reflected
site by projection and equal radius.  It covers every possible propagation
orientation in the frozen exact rational corpus, the exceptional-centre
families, the volume-branch family, the two-passing-vertex family, and the S101
swallowed-corner witness.  A deterministic presentation mutation subdivides
all polygon sides on a prefix.

Finite replay does not prove the local lemma.  Its purpose is stronger than a
happy-path regression but weaker than the theorem: kill the route immediately
if coplanar fusion, a hidden-hidden step, or an exceptional centre produces an
extra, missing, or wrongly oriented germ.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from typing import Any, Iterable

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s97_e_a51_merger_type_classification as CLS
import p43_s101_e_a57_skeleton_definition_witness as SWALLOWED
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM
import p43_s109_e_a61_exceptional_centre_witness as EXC
import p43_s111_e_a63_volume_branch_witness as VOL
import p43_s112_e_a64_multiple_passing_vertices as MULTI


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S131_E_A71_RIDGE_GERM_PROPAGATION.json"
Point = tuple[Q, Q, Q]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def clean_patches(patches: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Delete every forbidden source label before the local computation."""
    return [
        {"points": list(patch["points"]), "plane": patch["plane"]}
        for patch in patches
    ]


def ray_key(vector: Point) -> tuple[str, str, str]:
    """Canonical key up to multiplication by a positive rational scalar."""
    require(any(value for value in vector), "zero vector has no oriented ray")
    pivot = next(value for value in vector if value)
    scale = abs(pivot)
    return tuple(str(value / scale) for value in vector)


def average(points: list[Point]) -> Point:
    count = Q(len(points))
    return tuple(sum(point[i] for point in points) / count for i in range(3))


def perpendicular_to_edge(vector: Point, direction: Point) -> Point:
    factor = K.dot(vector, direction) / K.dot(direction, direction)
    return K.subtract(vector, K.scale(factor, direction))


def projection_to_line(point: Point, first: Point, second: Point) -> Point:
    direction = K.subtract(second, first)
    parameter = K.dot(K.subtract(point, first), direction) / K.dot(direction, direction)
    return K.add(first, K.scale(parameter, direction))


def point_parameter(point: Point, first: Point, second: Point) -> Q | None:
    direction = K.subtract(second, first)
    if not K.is_zero(K.cross(direction, K.subtract(point, first))):
        return None
    axis = next(index for index, value in enumerate(direction) if value)
    value = (point[axis] - first[axis]) / direction[axis]
    return value if Q(0) <= value <= Q(1) else None


def sample_on_relative_interior(
    first: Point, second: Point, patches: list[dict[str, Any]]
) -> Point:
    forbidden = {
        parameter
        for patch in patches
        for point in patch["points"]
        if (parameter := point_parameter(point, first, second)) is not None
    }
    candidates = [Q(1, 2), Q(1, 3), Q(2, 3), Q(1, 5), Q(2, 5), Q(3, 5), Q(4, 5)]
    parameter = next(value for value in candidates if value not in forbidden)
    return K.add(first, K.scale(parameter, K.subtract(second, first)))


def oriented_polygon(points: list[Point]) -> tuple[list[Point], Point]:
    normal = None
    for first, second, third in combinations(points, 3):
        try:
            normal, _offset = K.plane_through(first, second, third)
            break
        except ValueError:
            continue
    require(normal is not None, "polygon presentation is collinear")
    order = K.cyclic_order(points, normal)
    return [points[index] for index in order], normal


def local_rays(
    patches: list[dict[str, Any]], first: Point, second: Point
) -> set[tuple[str, str, str]]:
    """Oriented half-sheet rays of the raw boundary at a generic point of R.

    Only polygon coordinates and carrier planes are read.  If R lies inside a
    presented polygon, both sides of that sheet are returned; if it lies on a
    polygon boundary, only the interior side is returned.  Thus splitting or
    merging coplanar polygons does not change the geometric result.
    """
    sample = sample_on_relative_interior(first, second, patches)
    edge_direction = K.subtract(second, first)
    rays: set[tuple[str, str, str]] = set()

    for patch in patches:
        points, normal = oriented_polygon(list(patch["points"]))
        offset = K.dot(normal, points[0])
        if K.dot(normal, sample) != offset:
            continue
        signs = [
            K.dot(
                normal,
                K.cross(
                    K.subtract(points[(index + 1) % len(points)], points[index]),
                    K.subtract(sample, points[index]),
                ),
            )
            for index in range(len(points))
        ]
        if not (all(value >= 0 for value in signs) or all(value <= 0 for value in signs)):
            continue
        zero_indices = [index for index, value in enumerate(signs) if value == 0]
        if not zero_indices:
            transverse = K.cross(normal, edge_direction)
            rays.add(ray_key(transverse))
            rays.add(ray_key(K.scale(Q(-1), transverse)))
            continue

        covering = False
        for index in zero_indices:
            head, tail = points[index], points[(index + 1) % len(points)]
            if GERM.point_on_segment(sample, head, tail) and K.is_zero(
                K.cross(edge_direction, K.subtract(tail, head))
            ):
                covering = True
                break
        if not covering:
            continue
        interior = perpendicular_to_edge(K.subtract(average(points), sample), edge_direction)
        rays.add(ray_key(interior))
    return rays


def facet_edges(row: dict[str, Any]) -> dict[tuple[int, int], list[int]]:
    owners: dict[tuple[int, int], list[int]] = {}
    for facet_index, cycle in enumerate(row["core"]["facets_cyclic"]):
        for position, head in enumerate(cycle):
            tail = cycle[(position + 1) % len(cycle)]
            key = tuple(sorted((head, tail)))
            owners.setdefault(key, []).append(facet_index)
    return owners


def facet_interior_ray(row: dict[str, Any], facet: int, first: Point, second: Point) -> Point:
    points = [row["points"][index] for index in row["census_facets"][facet]]
    sample = K.scale(Q(1, 2), K.add(first, second))
    return perpendicular_to_edge(
        K.subtract(average(points), sample), K.subtract(second, first)
    )


def row_from_points(
    core_id: str, points: list[Point], centre: Point
) -> dict[str, Any]:
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


def build_boundary_union(
    row: dict[str, Any], centre_name: str, visible_mask: int
) -> dict[str, Any]:
    """The source-free boundary data needed here, without rebuilding 3-cells."""
    points, planes = row["points"], row["planes"]
    centre = row["centers"][centre_name]
    visible = [
        index for index in range(row["facet_count"]) if visible_mask >> index & 1
    ]
    flat = [index for index in range(row["facet_count"]) if index not in visible]
    apex = [K.reflect_point(centre, normal, offset) for normal, offset in planes]
    patches: list[dict[str, Any]] = []
    for index in visible:
        patches.append({
            "points": [points[v] for v in row["census_facets"][index]],
            "plane": K.unoriented_plane_key(*planes[index]),
        })
    for index in flat:
        cycle = row["core"]["facets_cyclic"][index]
        for position, head_index in enumerate(cycle):
            tail_index = cycle[(position + 1) % len(cycle)]
            head, tail = points[head_index], points[tail_index]
            normal, offset = K.plane_through(apex[index], head, tail)
            patches.append({
                "points": [apex[index], head, tail],
                "plane": K.unoriented_plane_key(normal, offset),
            })
    return {
        "center": centre,
        "visible": visible,
        "flat": flat,
        "apex": apex,
        "patches": patches,
    }


def exact_data(limit: int | None):
    rows = 0
    corpus_done = False
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
                yield (
                    f"corpus:{entry['core_id']}:{centre_name}:{visible_mask}",
                    row,
                    build_boundary_union(row, centre_name, visible_mask),
                    "frozen_corpus",
                )
                rows += 1
                if limit is not None and rows >= limit:
                    corpus_done = True
                    break
            if corpus_done:
                break
        if corpus_done:
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
    witness["visible"] = [
        index for index in range(row["facet_count"]) if index not in witness["flat"]
    ]
    yield "s101:swallowed-corner", row, witness, "swallowed_corner"


def audit_datum(
    name: str,
    row: dict[str, Any],
    union: dict[str, Any],
    mutated: bool,
) -> dict[str, Any]:
    patches = clean_patches(union["patches"])
    if mutated:
        patches = clean_patches(GERM.subdivide_polygon_edges(patches))
    flat, visible = set(union["flat"]), set(union["visible"])
    owners = facet_edges(row)
    checked = 0
    hidden_hidden = 0
    visible_hidden = 0
    straight_fusions = 0
    failures = []
    observed_by_edge: dict[tuple[int, int], set[tuple[str, str, str]]] = {}

    for (head, tail), incident in owners.items():
        require(len(incident) == 2, f"{name}: core edge does not have two facet owners")
        first, second = row["points"][head], row["points"][tail]
        for target in incident:
            if target not in flat:
                continue
            current = incident[0] if incident[1] == target else incident[1]
            q = projection_to_line(union["center"], first, second)
            target_vector = K.subtract(union["apex"][target], q)
            if current in visible:
                known_vector = facet_interior_ray(row, current, first, second)
                visible_hidden += 1
            else:
                known_vector = K.subtract(union["apex"][current], q)
                hidden_hidden += 1
            expected = {ray_key(known_vector), ray_key(target_vector)}
            edge_key = tuple(sorted((head, tail)))
            if edge_key not in observed_by_edge:
                observed_by_edge[edge_key] = local_rays(patches, first, second)
            observed = observed_by_edge[edge_key]
            radius_ok = K.squared_norm(target_vector) == K.squared_norm(
                K.subtract(union["center"], q)
            )
            projection_ok = K.dot(target_vector, K.subtract(second, first)) == 0
            distinct = len(expected) == 2
            if K.is_zero(K.cross(known_vector, target_vector)):
                straight_fusions += 1
            checked += 1
            if observed != expected or not radius_ok or not projection_ok or not distinct:
                failures.append({
                    "edge": [head, tail],
                    "current_facet": current,
                    "target_flat_facet": target,
                    "observed_rays": sorted(observed),
                    "expected_rays": sorted(expected),
                    "equal_radius": radius_ok,
                    "common_projection": projection_ok,
                    "two_distinct_oriented_rays": distinct,
                })

    require(checked > 0, f"{name}: proper-zero datum has no flat-target propagation step")
    return {
        "steps": checked,
        "visible_hidden_steps": visible_hidden,
        "hidden_hidden_steps": hidden_hidden,
        "straight_coplanar_fusions": straight_fusions,
        "failures": failures,
    }


def build(limit: int | None, mutation_prefix: int) -> dict[str, Any]:
    reports = []
    categories: dict[str, int] = {}
    data_count = 0
    total_steps = visible_hidden = hidden_hidden = straight = 0
    mutation_rows = mutation_steps = 0
    failures = []
    rows_with_straight_coplanar_fusion = 0

    for index, (name, row, union, category) in enumerate(exact_data(limit)):
        data_count += 1
        categories[category] = categories.get(category, 0) + 1
        report = audit_datum(name, row, union, mutated=False)
        if report["straight_coplanar_fusions"]:
            rows_with_straight_coplanar_fusion += 1
        total_steps += report["steps"]
        visible_hidden += report["visible_hidden_steps"]
        hidden_hidden += report["hidden_hidden_steps"]
        straight += report["straight_coplanar_fusions"]
        if report["failures"]:
            failures.append({"datum": name, "mutation": False, "failures": report["failures"]})
        if index < mutation_prefix:
            mutated_report = audit_datum(name, row, union, mutated=True)
            mutation_rows += 1
            mutation_steps += mutated_report["steps"]
            if mutated_report["failures"]:
                failures.append({"datum": name, "mutation": True, "failures": mutated_report["failures"]})
        if category != "frozen_corpus":
            reports.append({"datum": name, "category": category, **report})

    assertions = {
        "source_labels_are_not_read": True,
        "every_oriented_propagation_step_has_exactly_the_expected_two_rays": not failures,
        "every_target_site_has_the_same_ridge_projection_and_radius_as_the_centre": not failures,
        "both_visible_hidden_and_hidden_hidden_steps_are_exercised": visible_hidden > 0 and hidden_hidden > 0,
        "coplanar_erased_ridges_are_exercised": straight > 0,
        "presentation_subdivision_mutation_is_exercised": mutation_rows > 0 and mutation_steps > 0,
        "exceptional_centre_families_are_exercised": all(
            categories.get(key, 0) > 0
            for key in ("exceptional_centre", "volume_branch", "multiple_passing", "swallowed_corner")
        ),
    }
    require(all(assertions.values()), f"E-A71 failure: {[key for key, value in assertions.items() if not value]}")

    result: dict[str, Any] = {
        "schema_version": "P43-E-A71-RIDGE-GERM-PROPAGATION-v1",
        "project": "P43",
        "phase": "S131_E_A71_ridge_germ_propagation_audit",
        "status": "pass_no_local_counterexample_in_exact_domain",
        "metrics": {
            "data": data_count,
            "categories": categories,
            "rows_with_straight_coplanar_fusion": rows_with_straight_coplanar_fusion,
            "oriented_propagation_steps": total_steps,
            "visible_to_hidden_steps": visible_hidden,
            "hidden_to_hidden_steps": hidden_hidden,
            "straight_coplanar_fusions": straight,
            "presentation_mutation_rows": mutation_rows,
            "presentation_mutation_steps": mutation_steps,
            "failures": len(failures),
        },
        "adversarial_families": reports,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the local two-ray statement survives every propagation orientation in the frozen exact rational domain",
                "the statement survives the S101 swallowed-corner witness and all constructed exceptional-centre families",
                "the remaining ray has the exact projection and squared radius required to recover the true reflected site",
                "the extractor reads geometric polygon coordinates and carrier planes but no source kind or cap identity",
            ],
            "excluded": [
                "a proof of the intrinsic ridge-germ lemma for arbitrary raw subsets",
                "a proof of global cap-component extraction and propagation termination",
                "dimension above three",
                "proper-zero universal uniqueness",
                "novelty or priority",
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
    parser.add_argument("--mutation-prefix", type=int, default=256)
    arguments = parser.parse_args()
    result = build(arguments.limit, arguments.mutation_prefix)
    if arguments.verify_existing:
        stored = json.loads(arguments.output.read_text(encoding="utf-8"))
        require(stored == result, "stored E-A71 result differs from exact rebuild")
    else:
        arguments.output.parent.mkdir(parents=True, exist_ok=True)
        arguments.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
