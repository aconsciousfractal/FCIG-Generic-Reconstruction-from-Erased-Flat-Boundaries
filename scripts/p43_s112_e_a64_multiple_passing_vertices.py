#!/usr/bin/env python3
"""P43 S112 / E-A64 several passing core vertices at once, and the Q1 decision there.

Every exceptional datum built so far carries exactly one passing core vertex.
That is the last structural direction in which the Q1 decision could still
change: with two of them the incomparable search space is far larger, since a
candidate may drop any nonempty set of true apexes and add any nonempty set of
passing vertices.

**Construction, by inversion.** Rather than hunting for a centre that makes a
vertex pass, choose the centre first. If `v` is the mirror of `o` in a plane
`P`, then `o` lies on the perpendicular bisector of `o` and `v` by construction,
so every neighbour of `v` lying in `P` is equidistant from `o` and `v`. Doing
this twice with two planes gives two passing vertices sharing one centre.

Concretely, with `o` at the origin, take the top apex `(0,0,2c)` over a polygon
at height `c`, and the bottom apex `(0,0,-2d)` under a polygon at depth `d`.
Then for a top neighbour `(r,0,c)`,

    |w - o|^2 = r^2 + c^2 = r^2 + (c - 2c)^2 = |w - v|^2,

for **every** radius and height, so the family is unconstrained in `r`, `c`, `d`.
The two cones are kept visible so no apex becomes a neighbour of either vertex,
and the side facets between the two polygons are hidden, which makes the datum
proper-zero.

The decision is then run exactly on the enlarged space.
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
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s102_e_a58_reference_reconstruction as ALG
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM
import p43_s110_e_a62_exceptional_ambiguity_decision as DEC


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S112_E_A64_MULTIPLE_PASSING.json"

# (top height c, bottom depth d, polygon radius r)
SHAPES = [(1, 1, 1), (1, 2, 1), (2, 1, 3), (1, 1, 2), (3, 2, 1)]


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def rational(*coords):
    return tuple(Q(c) for c in coords)


def build(shape: tuple[int, int, int]) -> dict[str, Any] | None:
    top, bottom, radius = shape
    points = [
        rational(0, 0, 2 * top),
        rational(radius, 0, top),
        rational(0, radius, top),
        rational(-radius, 0, top),
        rational(0, -radius, top),
        rational(radius, 0, -bottom),
        rational(0, radius, -bottom),
        rational(-radius, 0, -bottom),
        rational(0, -radius, -bottom),
        rational(0, 0, -2 * bottom),
    ]
    centre = rational(0, 0, 0)
    first, second = points[0], points[9]

    facets = K.hull_facets(points)
    if not all(K.dot(n, centre) < h for (n, h), _ in facets):
        return None
    hull = {K.point_key(p) for p in points}
    listed = {K.point_key(points[j]) for (_, ids) in facets for j in ids}
    if hull != listed:
        return None

    at_first = [i for i, ((n, h), _) in enumerate(facets) if K.dot(n, first) == h]
    at_second = [i for i, ((n, h), _) in enumerate(facets) if K.dot(n, second) == h]
    if set(at_first) & set(at_second):
        return None
    visible = sorted(set(at_first) | set(at_second))
    hidden = [i for i in range(len(facets)) if i not in visible]
    if not hidden:
        return None

    census, cyclic, planes = [], [], []
    for (normal, offset), ids in facets:
        pts = [points[j] for j in ids]
        order = K.cyclic_order(pts, normal)
        census.append(list(ids))
        cyclic.append([ids[p] for p in order])
        planes.append((normal, offset))

    row = {
        "core_id": f"MULTI-{top}-{bottom}-{radius}",
        "core": {"facets_cyclic": cyclic},
        "census_facets": census,
        "facet_count": len(facets),
        "points": points,
        "planes": planes,
        "centers": {"c": centre},
    }
    union = CEN.build_raw_union(row, "c", sum(1 << i for i in visible))
    return {"union": union, "candidates": [first, second], "points": points}


def analyse(shape: tuple[int, int, int]) -> dict[str, Any] | None:
    built = build(shape)
    if built is None:
        return None
    union = built["union"]
    centre = union["center"]

    _v, edges, by_key = GERM.intrinsic_germ_skeleton(union["patches"])
    passing_flags = [
        GERM.passes_signature(point, centre, edges, by_key)
        for point in built["candidates"]
    ]

    apexes, extras = DEC.passing_vertices(union)
    truth = ALG.true_sites(union)
    result = ALG.reconstruct(union)
    returned = {K.point_key(s) for s in result["sites"]} if result else set()

    tested = 0
    compatible = []
    # supersets: keep every apex, add a nonempty set of passing vertices
    for size in range(1, len(extras) + 1):
        for added in combinations(extras, size):
            tested += 1
            report = DEC.decide_candidate(union, apexes + list(added))
            report["shape"] = "superset"
            if report["compatible"]:
                compatible.append(report)
    # incomparable: drop a nonempty set of apexes, add a nonempty set of extras
    for drop in range(1, len(apexes) + 1):
        for dropped in combinations(range(len(apexes)), drop):
            kept = [a for i, a in enumerate(apexes) if i not in dropped]
            for size in range(1, len(extras) + 1):
                for added in combinations(extras, size):
                    sites = kept + list(added)
                    if not sites:
                        continue
                    tested += 1
                    report = DEC.decide_candidate(union, sites)
                    report["shape"] = "incomparable"
                    if report["compatible"]:
                        compatible.append(report)

    return {
        "shape": {"top": shape[0], "bottom": shape[1], "radius": shape[2]},
        "vertices": len(built["points"]),
        "facets": union["visible"].__len__() + len(union["flat"]),
        "both_candidates_pass": all(passing_flags),
        "passing_core_vertices": len(extras),
        "true_apexes": len(apexes),
        "sites_returned": len(returned),
        "returned_is_a_strict_superset": truth < returned,
        "candidates_tested": tested,
        "candidates_compatible": len(compatible),
        "repaired_certifier_accepts_the_algorithm_output": (
            ALG.certifies(union, result) if result else False
        ),
    }


def build_result(limit: int | None) -> dict[str, Any]:
    reports = [r for r in (analyse(s) for s in SHAPES[: limit or len(SHAPES)]) if r]

    assertions = {
        "the_family_is_nonempty": len(reports) > 0,
        "every_datum_has_two_passing_core_vertices": all(
            r["passing_core_vertices"] >= 2 for r in reports
        ),
        "both_designed_vertices_really_pass": all(
            r["both_candidates_pass"] for r in reports
        ),
        "the_algorithm_returns_a_strict_superset": all(
            r["returned_is_a_strict_superset"] for r in reports
        ),
        "the_repaired_certifier_rejects_the_algorithm_output": all(
            not r["repaired_certifier_accepts_the_algorithm_output"]
            for r in reports
        ),
        "no_candidate_is_compatible": all(
            r["candidates_compatible"] == 0 for r in reports
        ),
        "the_enlarged_space_was_really_enumerated": all(
            r["candidates_tested"] > 0 for r in reports
        ),
    }
    if not all(assertions.values()):
        failed = [k for k, v in assertions.items() if not v]
        raise AssertionError(f"S112 multiple-passing failure: {failed}")

    result = {
        "schema_version": "P43-E-A64-MULTIPLE-PASSING-v1",
        "project": "P43",
        "phase": "S112_E_A64_multiple_passing_vertices",
        "status": "pass_no_ambiguity_with_two_simultaneous_passing_vertices",
        "construction": (
            "choose the centre first and take each passing vertex as its mirror "
            "in a plane; every neighbour lying in that plane is then equidistant "
            "from the centre and the vertex, for every radius and height"
        ),
        "metrics": {
            "data": len(reports),
            "candidates_tested": sum(r["candidates_tested"] for r in reports),
            "candidates_compatible": sum(
                r["candidates_compatible"] for r in reports
            ),
        },
        "data": reports,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "exceptional data with two simultaneous passing core vertices "
                "exist and are constructible as a family",
                "on them the enlarged candidate space contains no compatible "
                "alternative, and the repaired certifier rejects the "
                "algorithm's own output",
            ],
            "excluded": [
                "Q1 in general: this is a constructed family, not the "
                "exceptional locus",
                "three or more simultaneous passing vertices",
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
    args = parser.parse_args()
    result = build_result(args.limit)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S112 result differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    for r in result["data"]:
        print(
            f"  {r['shape']} passing={r['passing_core_vertices']}"
            f" returned={r['sites_returned']} tested={r['candidates_tested']}"
            f" compatible={r['candidates_compatible']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
