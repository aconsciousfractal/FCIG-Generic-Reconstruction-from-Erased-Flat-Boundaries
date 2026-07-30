#!/usr/bin/env python3
"""P43 S106: intrinsic germ skeleton of the observed merged flat boundary.

The skeleton is computed from maximal coplanar boundary sheets and their
non-coplanar intersections.  Source patch labels and erased internal seams are
not part of the output.  Degree-two collinear subdivision points are suppressed
unless the complete incident-sheet carrier germ changes there.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import defaultdict
from fractions import Fraction as Q
from pathlib import Path
from typing import Any, Iterable

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s97_e_a51_merger_type_classification as CLS
import p43_s101_e_a57_skeleton_definition_witness as WIT

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S106_E_A60_INTRINSIC_GERM_SKELETON.json"

Point = tuple[Q, Q, Q]
Segment = tuple[Point, Point]


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def edge_key(a: Point, b: Point):
    ka, kb = K.point_key(a), K.point_key(b)
    return (ka, kb) if ka < kb else (kb, ka)


def nonzero_segment(a: Point, b: Point) -> bool:
    return K.point_key(a) != K.point_key(b)


def point_on_segment(p: Point, a: Point, b: Point) -> bool:
    if not K.is_zero(K.cross(K.subtract(b, a), K.subtract(p, a))):
        return False
    return K.dot(K.subtract(p, a), K.subtract(p, b)) <= 0


def positive_collinear_overlap(left: Segment, right: Segment) -> bool:
    a, b = left
    c, d = right
    direction = K.subtract(b, a)
    if not K.is_zero(K.cross(direction, K.subtract(d, c))):
        return False
    if not K.is_zero(K.cross(direction, K.subtract(c, a))):
        return False
    axis = max(range(3), key=lambda i: abs(direction[i]))
    l0, l1 = sorted((a[axis], b[axis]))
    r0, r1 = sorted((c[axis], d[axis]))
    return max(l0, r0) < min(l1, r1)


def polygon_sides(patch: dict[str, Any]) -> list[Segment]:
    cycle = CEN.ordered_patch_points(patch)
    return [
        (cycle[i], cycle[(i + 1) % len(cycle)])
        for i in range(len(cycle))
        if nonzero_segment(cycle[i], cycle[(i + 1) % len(cycle)])
    ]


def atomize(segments: Iterable[Segment]) -> tuple[list[Segment], dict]:
    listed = list(segments)
    point_by_key = {
        K.point_key(point): point for segment in listed for point in segment
    }
    all_points = list(point_by_key.values())
    atoms: dict[tuple, Segment] = {}
    for a, b in listed:
        direction = K.subtract(b, a)
        axis = max(range(3), key=lambda i: abs(direction[i]))
        points = [p for p in all_points if point_on_segment(p, a, b)]
        points.sort(key=lambda p: (p[axis] - a[axis]) / direction[axis])
        for left, right in zip(points, points[1:]):
            if nonzero_segment(left, right):
                atoms[edge_key(left, right)] = (left, right)
    return list(atoms.values()), point_by_key


def segment_covers(outer: Segment, inner: Segment) -> bool:
    return point_on_segment(inner[0], *outer) and point_on_segment(inner[1], *outer)


def coplanar_sheet_partition(patches: list[dict[str, Any]]) -> list[list[int]]:
    """Connected components of coplanar polygonal subsets, independent of IDs."""
    parent = list(range(len(patches)))

    def find(i: int) -> int:
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    def union(i: int, j: int) -> None:
        ri, rj = find(i), find(j)
        if ri != rj:
            parent[rj] = ri

    sides = [polygon_sides(patch) for patch in patches]
    for i in range(len(patches)):
        for j in range(i + 1, len(patches)):
            if patches[i]["plane"] != patches[j]["plane"]:
                continue
            if any(
                positive_collinear_overlap(left, right)
                for left in sides[i]
                for right in sides[j]
            ):
                union(i, j)
    groups: dict[int, list[int]] = defaultdict(list)
    for i in range(len(patches)):
        groups[find(i)].append(i)
    return sorted((sorted(group) for group in groups.values()), key=lambda g: g[0])


def observable_sheet_boundaries(patches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Maximal coplanar sheets represented only by their outer segments."""
    sheets = []
    for group in coplanar_sheet_partition(patches):
        source_segments = [
            side for index in group for side in polygon_sides(patches[index])
        ]
        atoms, _ = atomize(source_segments)
        boundary = []
        for atom in atoms:
            multiplicity = sum(
                1 for segment in source_segments if segment_covers(segment, atom)
            )
            if multiplicity == 1:
                boundary.append(atom)
            elif multiplicity != 2:
                raise ValueError(
                    f"non-manifold coplanar sheet multiplicity {multiplicity}"
                )
        sheets.append({"plane": patches[group[0]]["plane"], "segments": boundary})
    return sheets


def intrinsic_germ_skeleton_from_sheets(sheets: list[dict[str, Any]]):
    """Return canonical vertices and edges of the non-coplanar crease locus.

    The carrier map is built while each segment is atomised; it never rescans
    every sheet for every atom.  With S boundary segments this reference form
    is O(S^2 log S) in exact field operations.
    """
    records = [
        (sheet_id, sheet["plane"], segment)
        for sheet_id, sheet in enumerate(sheets)
        for segment in sheet["segments"]
    ]
    point_by_key = {
        K.point_key(point): point
        for _sheet_id, _plane, segment in records
        for point in segment
    }
    all_points = list(point_by_key.values())
    segment_by_atom: dict[tuple, Segment] = {}
    carriers_by_atom: dict[tuple, dict[int, Any]] = defaultdict(dict)
    for sheet_id, plane, (a, b) in records:
        direction = K.subtract(b, a)
        axis = max(range(3), key=lambda i: abs(direction[i]))
        points = [p for p in all_points if point_on_segment(p, a, b)]
        points.sort(key=lambda p: (p[axis] - a[axis]) / direction[axis])
        for left, right in zip(points, points[1:]):
            if not nonzero_segment(left, right):
                continue
            key = edge_key(left, right)
            segment_by_atom[key] = (left, right)
            carriers_by_atom[key][sheet_id] = plane

    labelled_atoms: dict[tuple, tuple[Segment, tuple]] = {}
    for key, carrier_map in carriers_by_atom.items():
        carriers = sorted(carrier_map.items())
        planes = {repr(plane) for _sheet_id, plane in carriers}
        if len(planes) < 2:
            continue
        # Sheet-component identity is intrinsic.  It prevents suppression of a
        # collinear point at which the incident plane pair stays the same but a
        # maximal exposed sheet ends and another begins.
        label = tuple((sheet_id, repr(plane)) for sheet_id, plane in carriers)
        labelled_atoms[key] = (segment_by_atom[key], label)

    incidence: dict[tuple, list[tuple[tuple, tuple]]] = defaultdict(list)
    for key, (segment, label) in labelled_atoms.items():
        ka, kb = key
        incidence[ka].append((kb, label))
        incidence[kb].append((ka, label))
        for point in segment:
            point_by_key[K.point_key(point)] = point

    canonical = set()
    for key, incident in incidence.items():
        if len(incident) != 2:
            canonical.add(key)
            continue
        (left, label_left), (right, label_right) = incident
        if label_left != label_right:
            canonical.add(key)
            continue
        p = point_by_key[key]
        u = K.subtract(point_by_key[left], p)
        v = K.subtract(point_by_key[right], p)
        if not K.is_zero(K.cross(u, v)):
            canonical.add(key)

    if incidence and not canonical:
        canonical.update(incidence)

    edges = set()
    for start in sorted(canonical):
        for first, _label in incidence[start]:
            previous, current = start, first
            while current not in canonical:
                choices = [other for other, _ in incidence[current] if other != previous]
                if len(choices) != 1:
                    raise ValueError("non-canonical crease continuation")
                previous, current = current, choices[0]
            if current != start:
                edges.add(frozenset((start, current)))

    vertices = [point_by_key[key] for key in sorted(canonical)]
    return vertices, edges, point_by_key


def intrinsic_germ_skeleton(patches: list[dict[str, Any]]):
    """Fast source-free form: only geometric sides and plane keys are read.

    A coplanar internal seam contributes only one distinct plane and therefore
    disappears.  Global atomisation inserts endpoints from every other sheet,
    so a swallowed collinear corner is restored exactly when its germ changes.
    """
    sheets = []
    for group in coplanar_sheet_partition(patches):
        sheets.append({
            "plane": patches[group[0]]["plane"],
            "segments": [
                side for index in group for side in polygon_sides(patches[index])
            ],
        })
    return intrinsic_germ_skeleton_from_sheets(sheets)


def maximal_sheet_germ_skeleton(patches: list[dict[str, Any]]):
    """Slower independent form through explicit maximal coplanar sheets."""
    clean = [{"points": patch["points"], "plane": patch["plane"]} for patch in patches]
    return intrinsic_germ_skeleton_from_sheets(observable_sheet_boundaries(clean))


def neighbours(site: Point, edges: set, point_by_key: dict) -> list[Point]:
    key = K.point_key(site)
    return [
        point_by_key[other]
        for edge in edges
        if key in edge
        for other in edge
        if other != key
    ]


def passes_signature(site: Point, centre: Point, edges: set, point_by_key: dict) -> bool:
    adjacent = neighbours(site, edges, point_by_key)
    return bool(adjacent) and all(
        K.squared_norm(K.subtract(point, centre))
        == K.squared_norm(K.subtract(point, site))
        for point in adjacent
    )


def passing_sites(patches: list[dict[str, Any]], centre: Point) -> list[Point]:
    vertices, edges, point_by_key = intrinsic_germ_skeleton(patches)
    return [
        point for point in vertices
        if passes_signature(point, centre, edges, point_by_key)
    ]


def subdivide_polygon_edges(patches: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Same exposed subsets with a deliberately different vertex subdivision."""
    changed = []
    for patch in patches:
        cycle = CEN.ordered_patch_points(patch)
        points = []
        for i, point in enumerate(cycle):
            following = cycle[(i + 1) % len(cycle)]
            midpoint = K.scale(Q(1, 2), K.add(point, following))
            points.extend((point, midpoint))
        changed.append({"points": points, "plane": patch["plane"]})
    return changed


def skeleton_key(result) -> tuple:
    vertices, edges, _ = result
    return (
        tuple(sorted(K.point_key(point) for point in vertices)),
        tuple(sorted(tuple(sorted(edge)) for edge in edges)),
    )


def true_sites(union: dict[str, Any]) -> set:
    return {K.point_key(union["apex"][index]) for index in union["flat"]}


def witness_union() -> dict[str, Any]:
    vertices = [WIT.rational(point) for point in WIT.WITNESS_VERTICES]
    centre = WIT.rational(WIT.WITNESS_CENTER)
    facets = K.hull_facets(vertices)
    hidden = [index for index, (_, ids) in enumerate(facets) if set(ids) >= {0, 1}]
    visible = [index for index in range(len(facets)) if index not in hidden]
    planes = [plane for plane, _ in facets]
    apexes = [K.reflect_point(centre, normal, offset) for normal, offset in planes]
    patches = []
    for index, ((normal, offset), ids) in enumerate(facets):
        points = [vertices[position] for position in ids]
        if index in visible:
            patches.append({"points": points, "plane": K.unoriented_plane_key(normal, offset)})
            continue
        order = K.cyclic_order(points, normal)
        cycle = [points[position] for position in order]
        for position, head in enumerate(cycle):
            tail = cycle[(position + 1) % len(cycle)]
            wall_normal, wall_offset = K.plane_through(apexes[index], head, tail)
            patches.append({
                "points": [apexes[index], head, tail],
                "plane": K.unoriented_plane_key(wall_normal, wall_offset),
            })
    return {"patches": patches, "center": centre, "flat": hidden, "apex": apexes}


def corpus_rows():
    for entry in CLS.configurations():
        row = {key: entry[key] for key in (
            "core_id", "core", "census_facets", "facet_count",
            "points", "planes", "centers",
        )}
        upper = (1 << entry["facet_count"]) - 1
        for centre_name in sorted(entry["centers"]):
            for mask in range(1, upper):
                yield CEN.build_raw_union(row, centre_name, mask)


def build(
    limit: int | None = None, subdivision_limit: int = 256
) -> dict[str, Any]:
    rows = 0
    correct = 0
    subdivision_checks = 0
    subdivision_invariant = 0
    maximal_sheet_agreement = 0
    source_graph_agreement = 0
    for union in corpus_rows():
        rows += 1
        graph = intrinsic_germ_skeleton(union["patches"])
        selected = {
            K.point_key(point)
            for point in graph[0]
            if passes_signature(point, union["center"], graph[1], graph[2])
        }
        if selected == true_sites(union):
            correct += 1
        # Edge-subdivision mutation is substantially more expensive than the
        # source-free graph itself.  Run it on a deterministic prefix; the
        # reconstruction and historical-graph comparison still run on every row.
        if rows <= subdivision_limit:
            subdivision_checks += 1
            if skeleton_key(graph) == skeleton_key(
                intrinsic_germ_skeleton(subdivide_polygon_edges(union["patches"]))
            ):
                subdivision_invariant += 1
            if skeleton_key(graph) == skeleton_key(
                maximal_sheet_germ_skeleton(union["patches"])
            ):
                maximal_sheet_agreement += 1
        old_edges, old_points = CEN.merged_boundary_edges(union["patches"])
        old_vertices = [old_points[key] for key in sorted({k for e in old_edges for k in e})]
        if {K.point_key(p) for p in old_vertices} == {K.point_key(p) for p in graph[0]}:
            source_graph_agreement += 1
        if limit is not None and rows >= limit:
            break

    witness = witness_union()
    witness_graph = intrinsic_germ_skeleton(witness["patches"])
    witness_selected = {
        K.point_key(point)
        for point in witness_graph[0]
        if passes_signature(point, witness["center"], witness_graph[1], witness_graph[2])
    }
    witness_invariant = skeleton_key(witness_graph) == skeleton_key(
        intrinsic_germ_skeleton(subdivide_polygon_edges(witness["patches"]))
    )
    witness_right = witness_selected == true_sites(witness)

    metrics = {
        "rows_examined": rows,
        "rows_reconstructed_from_intrinsic_germ_skeleton": correct,
        "subdivision_mutation_checks": subdivision_checks,
        "subdivision_mutation_checks_invariant": subdivision_invariant,
        "maximal_sheet_cross_checks_agree": maximal_sheet_agreement,
        "rows_agreeing_with_historical_source_side_graph": source_graph_agreement,
        "witness_reconstructed": witness_right,
        "witness_subdivision_invariant": witness_invariant,
    }
    assertions = {
        "all_rows_reconstruct": correct == rows,
        "all_sampled_subdivision_mutations_are_invariant": (
            subdivision_invariant == subdivision_checks
        ),
        "all_sampled_maximal_sheet_cross_checks_agree": (
            maximal_sheet_agreement == subdivision_checks
        ),
        "historical_graph_agrees_on_corpus": source_graph_agreement == rows,
        "degenerate_witness_reconstructs": witness_right,
        "degenerate_witness_is_subdivision_invariant": witness_invariant,
    }
    if not all(assertions.values()):
        raise AssertionError([key for key, value in assertions.items() if not value])
    result = {
        "schema_version": "P43-E-A60-INTRINSIC-GERM-SKELETON-v2",
        "project": "P43",
        "phase": "S106_intrinsic_germ_skeleton",
        "status": "pass_exact_observable_skeleton_replay",
        "definition": (
            "vertices and edges of the non-coplanar crease locus of maximal "
            "coplanar exposed boundary sheets, suppressing only collinear "
            "degree-two points with unchanged complete incident-sheet carrier germ"
        ),
        "metrics": metrics,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the skeleton extractor does not read source kind labels or hidden-cap identities",
                "the result is invariant under inserted boundary subdivision points on the deterministic mutation sample",
                "the intrinsic signature reconstructs every corpus row and the S101 witness",
            ],
            "excluded": [
                "a complete implementation from arbitrary point clouds or implicit sets",
                "a proof that finite replay replaces the intrinsic germ argument",
                "unrestricted presentation invariance beyond the tested mutation class",
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
    parser.add_argument("--subdivision-limit", type=int, default=256)
    args = parser.parse_args()
    result = build(args.limit, args.subdivision_limit)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S106 result differs from exact rebuild")
    else:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
