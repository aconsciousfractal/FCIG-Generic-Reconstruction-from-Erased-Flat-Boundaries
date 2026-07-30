#!/usr/bin/env python3
"""P43 S102 / E-A58 exact flat-reconstruction reference kernel.

The corpus scripts compute the same objects, but they were written to test
lemmas rather than to expose the paper algorithm.  This module implements the
source-free flat kernel in steps 4--6 of the conceptual reconstruction:

  1-2  local-flat components give M_J and the nonflat caps; each nonflat cap
       meets M_J in its hinge facet                                   (C030, C032)
  3    one nonflat cap gives the centre                               (C032)
  4    build the intrinsic boundary-germ skeleton from exposed sheets (S106)
  5    keep exactly the vertices that pass the apex signature         (Theorem A)
  6    intersect visible-hinge and passing-site bisector halfspaces

Steps 1--3 are cited and are not implemented here; the frozen corpus supplies
their exact outputs.  The kernel consumes only the exposed flat-boundary
presentation at step 4.  It does not inspect source kinds, hidden-facet labels,
or original cap identities.

**Correctness on the frozen domain.** Reconstruction runs on all 16,744 rows,
including the 64 rows that fail the historical condition (H).  That split is a
diagnostic only: (H) is not a hypothesis of the uniqueness theorem after S103.
The intrinsic candidate set is also compared with the older plane-count
shortcut, but agreement on this corpus is regression evidence, not an
equivalence theorem.

**The certifying variant never lies on the attempted sample.** Rebuild M_J
from the reconstruction and compare it exactly, as a set, with the observed
M_J.  A run either returns a certified datum or reports failure.  This is
checked on a deterministic sample because exact set comparison requires
pairwise halfspace-intersection volumes.

The S101 swallowed-corner witness is included as a separate exact control.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s97_e_a51_merger_type_classification as CLS
import p43_s100_e_a56_intrinsic_hypothesis_equivalence as EQV
import p43_s101_e_a57_skeleton_definition_witness as WIT
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S102_E_A58_REFERENCE_RECONSTRUCTION.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


# --------------------------------------------------------------------------
# the algorithm
# --------------------------------------------------------------------------


def complex_vertices(
    patches: list[dict[str, Any]]
) -> tuple[list[K.Point], set, dict]:
    """Step 4. The intrinsic germ skeleton of the exposed flat boundary.

    S106 groups maximal coplanar sheet components, erases their internal seams,
    atomises intersections with every non-coplanar sheet, and suppresses only
    collinear degree-two points whose full sheet-germ label is unchanged.  No
    source kind, hidden-facet label or original patch identity is read.
    """
    return GERM.intrinsic_germ_skeleton(patches)


def passes_signature(
    site: K.Point, centre: K.Point, edges: set, point_by_key: dict
) -> bool:
    """Step 5. Every neighbour lies on the perpendicular bisector of (o, site)."""
    neighbours = CEN.merged_neighbours(site, edges, point_by_key)
    if not neighbours:
        return False
    return all(
        K.squared_norm(K.subtract(point, centre))
        == K.squared_norm(K.subtract(point, site))
        for point in neighbours
    )


def reconstruct(union: dict[str, Any]) -> dict[str, Any] | None:
    """The six steps. Returns None when the input is rejected."""
    centre = CEN.recovered_center(union)          # step 3
    if centre is None:
        return None

    patches = union["patches"]
    vertices, edges, point_by_key = complex_vertices(patches)   # step 4

    sites = [                                                    # step 5
        vertex
        for vertex in vertices
        if passes_signature(vertex, centre, edges, point_by_key)
    ]
    if not sites:
        return None

    halfspaces = [                                               # step 6
        (normal, offset) for normal, offset in union["hinge_planes"].values()
    ]
    halfspaces += [K.bisector_halfspace(centre, site) for site in sites]

    return {
        "centre": centre,
        "sites": sites,
        "core_halfspaces": halfspaces,
    }


def rebuild_merged_component(
    reconstruction: dict[str, Any]
) -> list[CEN.Cell] | None:
    """The certifying step: rebuild M_J from the reconstructed datum alone."""
    centre = reconstruction["centre"]
    solved = K.Polytope(reconstruction["core_halfspaces"])
    if not solved.bounded or len(solved.vertices) < 4:
        return None
    core = CEN.Cell(list(solved.vertices))
    cells = [core]
    for site in reconstruction["sites"]:
        normal, offset = K.bisector_halfspace(centre, site)
        facet = [
            point for point in solved.vertices if K.dot(normal, point) == offset
        ]
        if len(facet) < 3:
            return None
        cells.append(CEN.Cell(facet + [site]))
    return cells


def observed_merged_component(union: dict[str, Any]) -> list[CEN.Cell]:
    return [union["core_cell"]] + [
        union["flat_cells"][index] for index in union["flat"]
    ]


def certifies(union: dict[str, Any], reconstruction: dict[str, Any]) -> bool:
    rebuilt = rebuild_merged_component(reconstruction)
    if rebuilt is None:
        return False
    return CEN.unions_are_equal(rebuilt, observed_merged_component(union))


# --------------------------------------------------------------------------
# the sweep
# --------------------------------------------------------------------------


def true_sites(union: dict[str, Any]) -> set:
    return {K.point_key(union["apex"][index]) for index in union["flat"]}


CERTIFICATIONS_PER_CENTRE = 3


def sample_stride(facet_count: int) -> int:
    """Deterministic thinning for the expensive certification pass.

    Certification compares two unions of convex cells by exact volume, which
    costs one halfspace-intersection volume per pair of cells, so it is orders
    of magnitude dearer than a reconstruction. Reconstruction therefore runs on
    every row and certification on a deterministic sample of roughly
    CERTIFICATIONS_PER_CENTRE masks per realization and centre.
    """
    return max(1, (1 << facet_count) // CERTIFICATIONS_PER_CENTRE)


def build(limit: int | None) -> dict[str, Any]:
    rows = 0
    historical_h_holds = 0
    historical_h_fails = 0
    correct_when_historical_h_holds = 0
    correct_when_historical_h_fails = 0
    candidate_sets_agree = 0
    certified = 0
    certification_attempts = 0
    wrong_and_certified: list[dict[str, Any]] = []
    wrong_answers: list[dict[str, Any]] = []

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
        stride = sample_stride(entry["facet_count"])
        for centre_name in sorted(entry["centers"]):
            for mask in range(1, upper):
                union = CEN.build_raw_union(row, centre_name, mask)
                rows += 1

                historical_h_holds_here, _failures = EQV.hypothesis_holds(union)
                if historical_h_holds_here:
                    historical_h_holds += 1
                else:
                    historical_h_fails += 1

                # the intrinsic-germ candidate step against the historical plane-count one
                vertices, _edges, _by_key = complex_vertices(union["patches"])
                paper = {K.point_key(point) for point in vertices}
                counted = {
                    K.point_key(point)
                    for point in CEN.candidate_sites(union["patches"])
                }
                if paper == counted:
                    candidate_sets_agree += 1

                result = reconstruct(union)
                right = (
                    result is not None
                    and {K.point_key(site) for site in result["sites"]}
                    == true_sites(union)
                )
                where = {
                    "core_id": entry["core_id"],
                    "realization_id": entry["realization_id"],
                    "centre": centre_name,
                    "mask": mask,
                    "historical_H_holds": historical_h_holds_here,
                }
                if right:
                    if historical_h_holds_here:
                        correct_when_historical_h_holds += 1
                    else:
                        correct_when_historical_h_fails += 1
                else:
                    wrong_answers.append(where)

                if mask % stride == 0 and result is not None:
                    certification_attempts += 1
                    ok = certifies(union, result)
                    if ok:
                        certified += 1
                    if ok and not right:
                        wrong_and_certified.append(where)

                if limit is not None and rows >= limit:
                    break
            if limit is not None and rows >= limit:
                break
        if limit is not None and rows >= limit:
            break

    # the S101 witness, the one datum with a degenerate merged patch
    witness = WIT.build_witness()
    witness_union = witness_raw_union()
    witness_result = reconstruct(witness_union)
    witness_right = (
        witness_result is not None
        and {K.point_key(site) for site in witness_result["sites"]}
        == true_sites(witness_union)
    )
    witness_certified = (
        certifies(witness_union, witness_result)
        if witness_result is not None
        else False
    )

    metrics = {
        "rows_examined": rows,
        "rows_where_historical_H_holds": historical_h_holds,
        "rows_where_historical_H_fails": historical_h_fails,
        "correct_when_historical_H_holds": correct_when_historical_h_holds,
        "correct_when_historical_H_fails": correct_when_historical_h_fails,
        "rows_where_intrinsic_and_historical_candidate_sets_agree": candidate_sets_agree,
        "certification_attempts": certification_attempts,
        "certified": certified,
        "wrong_answers": len(wrong_answers),
        "wrong_and_certified": len(wrong_and_certified),
        "witness_reconstructed_correctly": witness_right,
        "witness_certified": witness_certified,
    }
    assertions = {
        "the_flat_kernel_is_correct_on_every_frozen_row": not wrong_answers,
        "the_certifying_variant_never_certifies_a_wrong_answer": (
            not wrong_and_certified
        ),
        "every_attempted_certification_succeeded": (
            certified == certification_attempts
        ),
        "the_intrinsic_candidate_step_and_historical_plane_count_agree_on_this_corpus": (
            candidate_sets_agree == rows
        ),
        "the_degenerate_witness_is_reconstructed_and_certified": (
            witness_right and witness_certified
        ),
        "historical_H_is_not_needed_by_the_kernel_on_this_corpus": (
            correct_when_historical_h_fails == historical_h_fails
        )
        if limit is None
        else True,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S102 reference-reconstruction failure: {failed}")

    result = {
        "schema_version": "P43-E-A58-REFERENCE-RECONSTRUCTION-v2",
        "project": "P43",
        "phase": "S102_E_A58_reference_reconstruction",
        "status": "pass_exact_flat_kernel_replay",
        "algorithm": {
            "step_1_2": "local-flat components give M_J and the nonflat caps; C030 and C032",
            "step_3": "one nonflat cap gives the centre; C032",
            "step_4": "build the source-free intrinsic boundary-germ skeleton from exposed sheets",
            "step_5": "keep the candidates that pass the intrinsic apex signature",
            "step_6": "intersect the hinge halfspaces with the bisector halfspaces",
            "certifying_variant": "rebuild M_J from the output and compare it exactly as a set",
        },
        "metrics": metrics,
        "wrong_answers": wrong_answers[:20],
        "wrong_and_certified": wrong_and_certified[:20],
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the flat kernel in steps 4 to 6 returns the true sites and core "
                "on every frozen corpus row and on the degenerate S101 witness",
                "the certifying variant certified every attempt and never "
                "certified a wrong answer",
                "the intrinsic candidate set and the historical plane-count "
                "shortcut agree on every frozen corpus row",
            ],
            "excluded": [
                "steps 1 to 3, which are proved elsewhere but are not implemented "
                "by E-A58",
                "certification on every row: it is sampled, since an exact set "
                "comparison costs pairwise intersection volumes",
                "any equivalence theorem inferred from the historical plane-count "
                "shortcut, or any theorem-level role for historical condition (H)",
            ],
        },
    }
    result["canonical_mathematical_payload_sha256"] = canonical_hash(result)
    return result


def witness_raw_union() -> dict[str, Any]:
    """The S101 witness as a raw union, in the shape the algorithm consumes."""
    vertices = [WIT.rational(point) for point in WIT.WITNESS_VERTICES]
    centre = WIT.rational(WIT.WITNESS_CENTER)
    facets = K.hull_facets(vertices)
    hidden = [
        index for index, (_, indices) in enumerate(facets) if set(indices) >= {0, 1}
    ]
    visible = [index for index in range(len(facets)) if index not in hidden]
    planes = [plane for plane, _ in facets]
    apexes = [K.reflect_point(centre, normal, offset) for normal, offset in planes]

    patches: list[dict[str, Any]] = []
    for index, ((normal, offset), corner_indices) in enumerate(facets):
        points = [vertices[position] for position in corner_indices]
        key = K.unoriented_plane_key(normal, offset)
        if index in visible:
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

    return {
        "center": centre,
        "visible": visible,
        "flat": hidden,
        "apex": apexes,
        "core_cell": CEN.Cell(list(vertices)),
        "flat_cells": {
            index: CEN.Cell(
                [vertices[position] for position in facets[index][1]] + [apexes[index]]
            )
            for index in hidden
        },
        "patches": patches,
        "hinge_polygons": {
            index: [vertices[position] for position in facets[index][1]]
            for index in visible
        },
        "hinge_planes": {index: planes[index] for index in visible},
    }


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
            raise SystemExit("stored S102 reconstruction differs from exact rebuild")
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
