#!/usr/bin/env python3
"""P43 S111 / E-A63 the volume branch, built; and an intrinsic volume invariant.

S110 excluded strict supersets of the true site set in two cases and could only
exercise one of them: every S109 witness puts the passing core vertex on visible
hinge facets, so all superset cases fell in the hinge branch and the volume
branch was proof-only. This module closes that gap by construction.

**Why it is delicate.** The passing vertex must carry only hidden facets, each
at sixty degrees to the centre, that is `4(n.u)^2 = |n|^2 |u|^2` with
`u = b - o`. With `u` along a coordinate axis and unit normals there is no
rational solution, because three is not a sum of two rational squares. Off that
frame there is: with `u = (1,1,0)` the condition becomes `2(n_x+n_y)^2 = |n|^2`,
solved by `(1,0,+-1)` and `(0,1,+-1)`.

**The construction.** Put `o` at the origin and `b = (1,1,0)`. Take the four
facets through `b` with those normals; two of the four pairs are perpendicular,
so two of the four edges at `b` are erased. The two surviving edges leave `b`
along `(-1,-1,-1)` and `(-1,-1,1)`, and they must end on the bisector plane of
`o` and `b`, which happens at parameter one half; cutting with `z = +- 1/2`
places their endpoints exactly there. Bounding in `x` and `y` closes the body
and supplies the visible hinges, which do not touch `b`.

**What the witnesses show, and it was not expected.** On the S109 bipyramids
the merged flat component matched exactly and the hinge facets were destroyed.
Here it is the other way round: the hinge facets survive and the flat component
does **not** match. The two certifier conditions are therefore complementary,
each catching what the other misses, and neither alone is sufficient.

**A third, cheaper and intrinsic test.** The volume identity gives the core
volume from observables alone,

    vol(P) = (vol(M_J) + W) / 2,   W = sum of radial pyramids over hinge facets,

so a reconstruction can be rejected by comparing its core volume with that
number. It catches both branches and costs one volume.
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
import p43_s109_e_a61_exceptional_centre_witness as EXC
import p43_s110_e_a62_exceptional_ambiguity_decision as DEC


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S111_E_A63_VOLUME_BRANCH.json"

BOUNDS = [1, 2, 3]


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def build_volume_witness(bound: int) -> dict[str, Any] | None:
    """The passing vertex carries hidden facets only, so no hinge is truncated."""
    halfspaces = [
        ((Q(1), Q(0), Q(1)), Q(1)),
        ((Q(0), Q(1), Q(1)), Q(1)),
        ((Q(1), Q(0), Q(-1)), Q(1)),
        ((Q(0), Q(1), Q(-1)), Q(1)),
        ((Q(0), Q(0), Q(2)), Q(1)),
        ((Q(0), Q(0), Q(-2)), Q(1)),
        ((Q(-1), Q(0), Q(0)), Q(bound)),
        ((Q(0), Q(-1), Q(0)), Q(bound)),
    ]
    centre = (Q(0), Q(0), Q(0))
    vertex = (Q(1), Q(1), Q(0))

    solved = K.Polytope(halfspaces)
    if not solved.bounded:
        return None
    if not all(K.dot(n, centre) < h for n, h in halfspaces):
        return None
    points = list(solved.vertices)
    if not any(K.point_key(p) == K.point_key(vertex) for p in points):
        return None

    facets = K.hull_facets(points)
    at_vertex = [
        index
        for index, ((n, h), _) in enumerate(facets)
        if K.dot(n, vertex) == h
    ]
    visible = [i for i in range(len(facets)) if i not in at_vertex]
    if not visible or not at_vertex:
        return None

    census, cyclic, planes = [], [], []
    for (normal, offset), ids in facets:
        pts = [points[j] for j in ids]
        order = K.cyclic_order(pts, normal)
        census.append(list(ids))
        cyclic.append([ids[p] for p in order])
        planes.append((normal, offset))

    row = {
        "core_id": f"VOL-{bound}",
        "core": {"facets_cyclic": cyclic},
        "census_facets": census,
        "facet_count": len(facets),
        "points": points,
        "planes": planes,
        "centers": {"c": centre},
    }
    union = CEN.build_raw_union(row, "c", sum(1 << i for i in visible))
    return {
        "row": row,
        "union": union,
        "vertex": vertex,
        "facets_at_vertex": at_vertex,
        "visible": visible,
        "points": points,
        "census": census,
    }


def intrinsic_core_volume(built: dict[str, Any]) -> Q:
    """(vol(M_J) + W)/2, from observables only."""
    union = built["union"]
    points = built["points"]
    census = built["census"]
    core = CEN.Cell(list(points)).volume
    flat = sum(
        (
            CEN.Cell([points[j] for j in census[i]] + [union["apex"][i]]).volume
            for i in union["flat"]
        ),
        Q(0),
    )
    merged = core + flat
    hinge_radial = sum(
        (
            CEN.Cell([points[j] for j in census[i]] + [union["center"]]).volume
            for i in union["visible"]
        ),
        Q(0),
    )
    return (merged + hinge_radial) / 2


def inspect(bound: int) -> dict[str, Any] | None:
    built = build_volume_witness(bound)
    if built is None:
        return None
    union = built["union"]
    vertex = built["vertex"]
    centre = union["center"]

    _v, edges, by_key = GERM.intrinsic_germ_skeleton(union["patches"])
    passes = GERM.passes_signature(vertex, centre, edges, by_key)

    on_hinge = any(
        K.dot(union["hinge_planes"][i][0], vertex) == union["hinge_planes"][i][1]
        for i in union["visible"]
    )

    truth = ALG.true_sites(union)
    result = ALG.reconstruct(union)
    returned = {K.point_key(s) for s in result["sites"]} if result else set()

    flat_only = ALG.certifies_flat_only(union, result) if result else False
    hinges = ALG.hinge_facets_survive(union, result) if result else False
    full = ALG.certifies(union, result) if result else False

    predicted = intrinsic_core_volume(built)
    true_volume = CEN.Cell(list(built["points"])).volume
    solved = K.Polytope(result["core_halfspaces"])
    got = CEN.Cell(list(solved.vertices)).volume if solved.bounded else None

    # the incomparable decision, on this family too
    apexes, extras = DEC.passing_vertices(union)
    candidates = 0
    compatible = []
    for drop in range(1, len(apexes) + 1):
        for dropped in combinations(range(len(apexes)), drop):
            kept = [a for i, a in enumerate(apexes) if i not in dropped]
            for add in range(1, len(extras) + 1):
                for added in combinations(extras, add):
                    sites = kept + list(added)
                    if not sites:
                        continue
                    candidates += 1
                    report = DEC.decide_candidate(union, sites)
                    if report["compatible"]:
                        compatible.append(report)

    return {
        "bound": bound,
        "vertices": len(built["points"]),
        "facets": built["row"]["facet_count"],
        "facets_at_the_passing_vertex": len(built["facets_at_vertex"]),
        "passing_vertex_touches_a_visible_hinge": on_hinge,
        "core_vertex_passes": passes,
        "true_apexes": len(truth),
        "sites_returned": len(returned),
        "returned_is_a_strict_superset": truth < returned,
        "flat_component_matches": flat_only,
        "hinge_facets_survive": hinges,
        "repaired_certifier_accepts": full,
        "intrinsic_core_volume_predicted": str(predicted),
        "true_core_volume": str(true_volume),
        "volume_prediction_is_correct": predicted == true_volume,
        "reconstructed_core_volume": str(got) if got is not None else None,
        "volume_test_rejects": got is not None and got != predicted,
        "incomparable_candidates_tested": candidates,
        "incomparable_candidates_compatible": len(compatible),
    }


def build(limit: int | None) -> dict[str, Any]:
    reports = [r for r in (inspect(b) for b in BOUNDS[: limit or len(BOUNDS)]) if r]

    assertions = {
        "the_volume_branch_witness_exists": len(reports) > 0,
        "the_passing_vertex_carries_no_visible_hinge": all(
            not r["passing_vertex_touches_a_visible_hinge"] for r in reports
        ),
        "the_core_vertex_really_passes": all(
            r["core_vertex_passes"] for r in reports
        ),
        "the_algorithm_returns_a_strict_superset": all(
            r["returned_is_a_strict_superset"] for r in reports
        ),
        "the_hinge_condition_does_not_catch_this_branch": all(
            r["hinge_facets_survive"] for r in reports
        ),
        "the_flat_condition_does_catch_this_branch": all(
            not r["flat_component_matches"] for r in reports
        ),
        "the_repaired_certifier_still_rejects_every_witness": all(
            not r["repaired_certifier_accepts"] for r in reports
        ),
        "the_intrinsic_volume_formula_is_correct": all(
            r["volume_prediction_is_correct"] for r in reports
        ),
        "the_volume_test_also_rejects_every_witness": all(
            r["volume_test_rejects"] for r in reports
        ),
        "no_incomparable_ambiguity_on_this_family": all(
            r["incomparable_candidates_compatible"] == 0 for r in reports
        ),
    }
    if not all(assertions.values()):
        failed = [k for k, v in assertions.items() if not v]
        raise AssertionError(f"S111 volume-branch failure: {failed}")

    result = {
        "schema_version": "P43-E-A63-VOLUME-BRANCH-v1",
        "project": "P43",
        "phase": "S111_E_A63_volume_branch_witness",
        "status": "pass_volume_branch_exercised_and_conditions_shown_complementary",
        "finding": (
            "the two certifier conditions are complementary: on the S109 "
            "bipyramids the flat component matches and the hinge facets are "
            "destroyed; on this family the hinge facets survive and the flat "
            "component does not match. Neither condition alone is sufficient, "
            "and their conjunction rejects both families."
        ),
        "intrinsic_volume_invariant": (
            "vol(core) = (vol(M_J) + W)/2 with W the sum of the radial pyramids "
            "over the recovered hinge facets; computable from observables and "
            "rejecting both branches at the cost of one volume"
        ),
        "witnesses": reports,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the volume branch of the superset exclusion is now exercised "
                "on constructed data rather than argued",
                "the two certifier conditions are complementary and their "
                "conjunction rejects both witness families",
                "the intrinsic core-volume formula is exact on these data",
            ],
            "excluded": [
                "any decision of Q1 in general",
                "any claim that the conjunction of the two conditions, or the "
                "volume test, is complete",
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
    result = build(args.limit)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S111 result differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    for r in result["witnesses"]:
        print(
            f"  bound={r['bound']} passes={r['core_vertex_passes']}"
            f" flat={r['flat_component_matches']} hinges={r['hinge_facets_survive']}"
            f" certifier={r['repaired_certifier_accepts']}"
            f" volume_rejects={r['volume_test_rejects']}"
            f" incomparable={r['incomparable_candidates_compatible']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
