#!/usr/bin/env python3
"""P43 S110 / E-A62 deciding ambiguity at the exceptional centres we can build.

S109 produced the first data in the excluded case of Theorem A: centres at which
a core vertex passes the signature. This module asks the question those data
were built for, which is Q1: **is the datum still unique there?**

The search space is small, because two shapes are excluded in advance.

*Site sets contained in the truth* are excluded by the nested-site lemma.

*Site sets strictly containing the truth* are excluded in two cases, and the
second case is the one an earlier argument in this project missed. Let
`A'' > A` and let `b` be an extra site; by the candidate-type lemma `b` is a
vertex of the true core, and its bisector halfspace excludes `b`, so `P''` loses
that vertex.

  - if `b` lies on a recovered visible hinge facet, that facet is truncated and
    is no longer a facet of `P''` with the same vertex set, so the observed
    nonflat caps cannot attach;
  - if every facet at `b` is hidden, the hinge facets are untouched, so the
    volume identity applies unchanged and forces `vol(P'') = vol(P)`; but
    `P''` is a proper closed convex subset of `P`, so its volume is strictly
    smaller. Contradiction.

Both branches are checked here rather than asserted.

What remains is the **incomparable** shape: omit at least one true apex and add
at least one passing core vertex. This module enumerates every such candidate on
every S109 witness and decides each one exactly: build the core, require the
recovered hinge facets to survive, require every proposed site to index an
actual facet, and compare the rebuilt merged flat component with the observed
one as a set.

A surviving candidate would be an exact ambiguity and would answer Q1 in the
negative. None surviving on these data does **not** prove uniqueness; it decides
Q1 on the exceptional data currently constructible, which is a strictly smaller
statement and is recorded as such.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from itertools import combinations
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s102_e_a58_reference_reconstruction as ALG
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM
import p43_s109_e_a61_exceptional_centre_witness as EXC


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S110_E_A62_EXCEPTIONAL_AMBIGUITY.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def passing_vertices(union: dict[str, Any]) -> tuple[list, list]:
    """Split the passing set into true apexes and passing core vertices."""
    vertices, edges, by_key = GERM.intrinsic_germ_skeleton(union["patches"])
    centre = union["center"]
    passing = [
        point
        for point in vertices
        if GERM.passes_signature(point, centre, edges, by_key)
    ]
    truth = ALG.true_sites(union)
    apexes = [p for p in passing if K.point_key(p) in truth]
    core_vertices = [p for p in passing if K.point_key(p) not in truth]
    return apexes, core_vertices


def core_from_sites(union: dict[str, Any], sites: list) -> Any:
    halfspaces = [
        (normal, offset) for normal, offset in union["hinge_planes"].values()
    ]
    halfspaces += [
        K.bisector_halfspace(union["center"], site) for site in sites
    ]
    return K.Polytope(halfspaces), halfspaces


def decide_candidate(union: dict[str, Any], sites: list) -> dict[str, Any]:
    """Exact compatibility test for one proposed site set."""
    solved, halfspaces = core_from_sites(union, sites)
    report = {
        "sites": sorted(K.point_key(site) for site in sites),
        "bounded": bool(solved.bounded),
        "centre_interior": None,
        "hinge_facets_survive": None,
        "every_site_indexes_a_facet": None,
        "flat_component_matches": None,
        "compatible": False,
    }
    if not solved.bounded or len(solved.vertices) < 4:
        return report

    centre = union["center"]
    report["centre_interior"] = all(
        K.dot(normal, centre) < offset for normal, offset in halfspaces
    )
    if not report["centre_interior"]:
        return report

    reconstruction = {
        "centre": centre,
        "sites": list(sites),
        "core_halfspaces": halfspaces,
    }

    report["hinge_facets_survive"] = ALG.hinge_facets_survive(
        union, reconstruction
    )

    facet_planes = {
        K.unoriented_plane_key(normal, offset)
        for (normal, offset), _ in K.hull_facets(list(solved.vertices))
    }
    report["every_site_indexes_a_facet"] = all(
        K.unoriented_plane_key(*K.bisector_halfspace(centre, site))
        in facet_planes
        for site in sites
    )

    if not (
        report["hinge_facets_survive"] and report["every_site_indexes_a_facet"]
    ):
        return report

    report["flat_component_matches"] = ALG.certifies_flat_only(
        union, reconstruction
    )
    report["compatible"] = bool(report["flat_component_matches"])
    return report


def analyse(shape: tuple[int, int, int]) -> dict[str, Any]:
    built = EXC.build_witness(*shape)
    union = built["union"]
    apexes, extras = passing_vertices(union)

    true_core = CEN.Cell(list(union["core_cell"].points))

    # --- the superset branch, both cases, checked rather than assumed ---
    superset = []
    for extra in extras:
        sites = apexes + [extra]
        solved, halfspaces = core_from_sites(union, sites)
        reconstruction = {
            "centre": union["center"],
            "sites": sites,
            "core_halfspaces": halfspaces,
        }
        touches_hinge = any(
            K.dot(normal, extra) == offset
            for normal, offset in union["hinge_planes"].values()
        )
        volume = (
            CEN.Cell(list(solved.vertices)).volume if solved.bounded else None
        )
        superset.append(
            {
                "extra_site": [str(c) for c in extra],
                "lies_on_a_recovered_hinge_facet": touches_hinge,
                "hinge_facets_survive": ALG.hinge_facets_survive(
                    union, reconstruction
                ),
                "core_volume": str(volume) if volume is not None else None,
                "true_core_volume": str(true_core.volume),
                "core_volume_is_strictly_smaller": (
                    volume is not None and volume < true_core.volume
                ),
                "compatible": decide_candidate(union, sites)["compatible"],
            }
        )

    # --- the incomparable branch: drop some true apexes, add some extras ---
    candidates = []
    for drop_size in range(1, len(apexes) + 1):
        for dropped in combinations(range(len(apexes)), drop_size):
            kept = [a for i, a in enumerate(apexes) if i not in dropped]
            for add_size in range(1, len(extras) + 1):
                for added in combinations(extras, add_size):
                    sites = kept + list(added)
                    if not sites:
                        continue
                    report = decide_candidate(union, sites)
                    report["dropped_true_apexes"] = drop_size
                    report["added_core_vertices"] = add_size
                    candidates.append(report)

    return {
        "shape": {"top": shape[0], "bottom": shape[1], "radius": shape[2]},
        "true_apexes": len(apexes),
        "passing_core_vertices": len(extras),
        "superset_branch": superset,
        "incomparable_candidates_tested": len(candidates),
        "incomparable_candidates_compatible": [
            c for c in candidates if c["compatible"]
        ],
        "incomparable_rejected_by_hinge_survival": sum(
            1 for c in candidates if c["hinge_facets_survive"] is False
        ),
        "incomparable_rejected_by_missing_facet": sum(
            1
            for c in candidates
            if c["hinge_facets_survive"] and not c["every_site_indexes_a_facet"]
        ),
        "incomparable_rejected_by_flat_mismatch": sum(
            1 for c in candidates if c["flat_component_matches"] is False
        ),
        "incomparable_rejected_as_unbounded_or_exterior": sum(
            1
            for c in candidates
            if not c["bounded"] or c["centre_interior"] is False
        ),
    }


def build(limit: int | None) -> dict[str, Any]:
    shapes = EXC.WITNESS_SHAPES[: limit or len(EXC.WITNESS_SHAPES)]
    reports = [analyse(shape) for shape in shapes]

    total_candidates = sum(r["incomparable_candidates_tested"] for r in reports)
    ambiguities = [
        c for r in reports for c in r["incomparable_candidates_compatible"]
    ]
    superset_compatible = [
        s for r in reports for s in r["superset_branch"] if s["compatible"]
    ]
    hinge_branch = [
        s
        for r in reports
        for s in r["superset_branch"]
        if s["lies_on_a_recovered_hinge_facet"]
    ]
    volume_branch = [
        s
        for r in reports
        for s in r["superset_branch"]
        if not s["lies_on_a_recovered_hinge_facet"]
    ]

    assertions = {
        "every_witness_has_at_least_one_passing_core_vertex": all(
            r["passing_core_vertices"] >= 1 for r in reports
        ),
        "no_superset_site_set_is_compatible": not superset_compatible,
        "every_superset_case_is_explained_by_one_of_the_two_branches": all(
            (s["lies_on_a_recovered_hinge_facet"] and not s["hinge_facets_survive"])
            or (
                not s["lies_on_a_recovered_hinge_facet"]
                and s["core_volume_is_strictly_smaller"]
            )
            for r in reports
            for s in r["superset_branch"]
        ),
        "no_incomparable_site_set_is_compatible": not ambiguities,
        "the_incomparable_space_was_actually_enumerated": total_candidates > 0,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S110 ambiguity-decision failure: {failed}")

    result = {
        "schema_version": "P43-E-A62-EXCEPTIONAL-AMBIGUITY-v1",
        "project": "P43",
        "phase": "S110_E_A62_exceptional_ambiguity_decision",
        "status": "pass_no_ambiguity_on_the_constructible_exceptional_data",
        "question": (
            "Q1: at a centre where a core vertex passes, is the datum still "
            "determined by the raw union?"
        ),
        "search_space": {
            "subset_of_the_truth": "excluded by the nested-site lemma",
            "strict_superset_of_the_truth": (
                "excluded in two cases: a passing vertex on a recovered hinge "
                "facet truncates it; a passing vertex on hidden facets only "
                "leaves the hinge facets intact, so the volume identity applies "
                "and a strictly smaller core contradicts it"
            ),
            "incomparable": "enumerated and decided exactly here",
        },
        "metrics": {
            "witnesses": len(reports),
            "incomparable_candidates_tested": total_candidates,
            "incomparable_candidates_compatible": len(ambiguities),
            "superset_candidates_compatible": len(superset_compatible),
            "superset_cases_on_a_hinge_facet": len(hinge_branch),
            "superset_cases_on_hidden_facets_only": len(volume_branch),
        },
        "witnesses": reports,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "on every exceptional datum this project can currently build, "
                "no second compatible decomposition exists",
                "the superset branch is excluded, and both of its cases are "
                "exhibited or shown vacuous on these data",
            ],
            "excluded": [
                "any decision of Q1 in general: these are finitely many "
                "constructed data, not the exceptional locus",
                "any statement about exceptional data with more than one "
                "passing core vertex than constructed here",
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
            raise SystemExit("stored S110 result differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["metrics"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
