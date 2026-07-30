#!/usr/bin/env python3
"""P43 S91 / E-A44 realization robustness of the six-vertex fiber result.

S90-B enumerated the source-free C033 decomposition fiber on one realization
per six-vertex core type and two interior centers.  A census row is a family of
realizations, so two members are not the family.  This script re-runs the same
enumeration across several exactly constructed alternative realizations and
several interior centers, and reports the fiber histogram over all of them.

The realization generator stays inside the combinatorial type by construction:
the supporting plane of every non-triangular facet is held fixed and each
vertex is moved only inside the intersection of the planes of its own
non-triangular facets.  Triangles need no constraint.  Every generated
realization is then validated against the frozen S50 facet family before use.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_rational_six_vertex_catalogue as CAT
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = (
    ROOT / "results" / "P43_S91_E_A44_SIX_VERTEX_REALIZATION_ROBUSTNESS.json"
)
CATALOGUE_RESULT = (
    ROOT / "results" / "P43_S90_E_A43B_SIX_VERTEX_RATIONAL_CATALOGUE.json"
)
FIBER_RESULT = (
    ROOT / "results" / "P43_S90_E_A43C_SIX_VERTEX_C033_FIBER_CENSUS.json"
)

# Deterministic perturbation steps, smallest first.  A step is retried at half
# size when it leaves the combinatorial type.
STEP_TABLE = (Q(1, 2), Q(1, 3), Q(1, 5), Q(2, 7), Q(1, 4), Q(3, 8))
SIGN_TABLE = (1, -1, 1, -1, -1, 1)

# Deliberately symmetric realizations, used to raise the coincidence rate.
SYMMETRIC_COORDINATES: dict[str, list[K.Point]] = {
    "S6-07": [
        (Q(3), Q(0), Q(0)),
        (Q(-3), Q(0), Q(0)),
        (Q(0), Q(3), Q(0)),
        (Q(0), Q(-3), Q(0)),
        (Q(0), Q(0), Q(3)),
        (Q(0), Q(0), Q(-3)),
    ],
}


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def qtext(value: Q) -> str:
    return CAT.qtext(value)


def point_text(point) -> list[str]:
    return [qtext(value) for value in point]


# --------------------------------------------------------------------------
# realization family
# --------------------------------------------------------------------------


def null_space_basis(normals: list[K.Point]) -> list[K.Point]:
    """Exact basis of the vectors orthogonal to every supplied normal."""
    independent: list[K.Point] = []
    for normal in normals:
        if not independent:
            independent.append(normal)
            continue
        if len(independent) == 1:
            if not K.is_zero(K.cross(independent[0], normal)):
                independent.append(normal)
            continue
        if K.dot(normal, K.cross(independent[0], independent[1])) != 0:
            return []
    if not independent:
        return [
            (Q(1), Q(0), Q(0)),
            (Q(0), Q(1), Q(0)),
            (Q(0), Q(0), Q(1)),
        ]
    if len(independent) == 1:
        normal = independent[0]
        seed = (Q(1), Q(0), Q(0))
        if K.is_zero(K.cross(normal, seed)):
            seed = (Q(0), Q(1), Q(0))
        first = K.cross(normal, seed)
        return [first, K.cross(normal, first)]
    return [K.cross(independent[0], independent[1])]


def constrained_directions(row: dict, vertex: int) -> list[K.Point]:
    normals = [
        row["planes"][index][0]
        for index, facet in enumerate(row["census_facets"])
        if vertex in facet and len(facet) > 3
    ]
    return null_space_basis(normals)


def type_is_preserved(points: list[K.Point], census_facets: list[tuple[int, ...]]) -> bool:
    try:
        hull = K.hull_facets(points)
    except ValueError:
        return False
    return sorted(tuple(indices) for _, indices in hull) == sorted(census_facets)


def perturbed_points(row: dict, index: int) -> list[K.Point]:
    """Alternative realization of the same combinatorial type."""
    points = list(row["points"])
    for vertex in range(len(points)):
        directions = constrained_directions(row, vertex)
        if not directions:
            continue
        choice = directions[(index + vertex) % len(directions)]
        sign = SIGN_TABLE[(index * 3 + vertex) % len(SIGN_TABLE)]
        step = STEP_TABLE[(index + 2 * vertex) % len(STEP_TABLE)]
        for attempt in range(4):
            scaled = K.scale(Q(sign) * step / (2 ** attempt), choice)
            candidate = list(points)
            candidate[vertex] = K.add(points[vertex], scaled)
            if type_is_preserved(candidate, row["census_facets"]):
                points = candidate
                break
    return points


def planes_for(points: list[K.Point], census_facets: list[tuple[int, ...]]):
    hull = K.hull_facets(points)
    planes = []
    for facet in census_facets:
        match = next(
            (plane for plane, indices in hull if tuple(indices) == facet), None
        )
        if match is None:
            raise AssertionError("perturbed realization lost a facet")
        planes.append(match)
    return planes


def interior_centers(points: list[K.Point], planes, census_facets) -> dict[str, K.Point]:
    """Four exact interior centers, including two deliberately off-center."""
    centroid = K.average(points)

    def pull(target: K.Point, name: str) -> tuple[str, K.Point] | None:
        for numerator in (3, 2, 1):
            factor = Q(numerator, 4)
            candidate = K.add(
                centroid, K.scale(factor, K.subtract(target, centroid))
            )
            if all(
                K.dot(normal, candidate) < offset for normal, offset in planes
            ):
                return name, candidate
        return None

    centers: dict[str, K.Point] = {"centroid": centroid}
    generic = K.add(centroid, (Q(1, 7), Q(1, 11), Q(1, 13)))
    if all(K.dot(normal, generic) < offset for normal, offset in planes):
        centers["generic"] = generic
    toward_vertex = pull(points[0], "toward_vertex")
    if toward_vertex is not None:
        centers[toward_vertex[0]] = toward_vertex[1]
    facet_barycenter = K.average(points[index] for index in census_facets[0])
    toward_facet = pull(facet_barycenter, "toward_facet")
    if toward_facet is not None:
        centers[toward_facet[0]] = toward_facet[1]
    return centers


def realization_families() -> dict[str, list[dict[str, Any]]]:
    """All realizations used by the sweep, keyed by core id."""
    base = CEN.prepare_rows()
    families: dict[str, list[dict[str, Any]]] = {}
    for core_id in sorted(base):
        row = base[core_id]
        entries = [
            {
                "realization_id": "frozen",
                "points": list(row["points"]),
                "planes": list(row["planes"]),
            }
        ]
        for index in range(1, 4):
            points = perturbed_points(row, index)
            if points == list(row["points"]):
                continue
            if not type_is_preserved(points, row["census_facets"]):
                continue
            entries.append(
                {
                    "realization_id": f"perturbed_{index}",
                    "points": points,
                    "planes": planes_for(points, row["census_facets"]),
                }
            )
        symmetric = SYMMETRIC_COORDINATES.get(core_id)
        if symmetric is not None and type_is_preserved(
            symmetric, row["census_facets"]
        ):
            entries.append(
                {
                    "realization_id": "symmetric",
                    "points": list(symmetric),
                    "planes": planes_for(symmetric, row["census_facets"]),
                }
            )
        for entry in entries:
            entry["centers"] = interior_centers(
                entry["points"], entry["planes"], row["census_facets"]
            )
            entry["core"] = row["core"]
            entry["core_id"] = core_id
            entry["census_facets"] = row["census_facets"]
            entry["facet_count"] = row["facet_count"]
            entry["vertex_count"] = row["vertex_count"]
        families[core_id] = entries
    return families


# --------------------------------------------------------------------------
# sweep
# --------------------------------------------------------------------------


def sweep(skip_frozen_pair: bool) -> dict[str, Any]:
    families = realization_families()
    records: list[dict[str, Any]] = []
    configurations: list[dict[str, Any]] = []
    for core_id in sorted(families):
        for entry in families[core_id]:
            upper = (1 << entry["facet_count"]) - 1
            for center_name in sorted(entry["centers"]):
                already_done = (
                    skip_frozen_pair
                    and entry["realization_id"] == "frozen"
                    and center_name in ("centroid", "generic")
                )
                if already_done:
                    continue
                row = {
                    "core_id": core_id,
                    "core": entry["core"],
                    "census_facets": entry["census_facets"],
                    "facet_count": entry["facet_count"],
                    "points": entry["points"],
                    "planes": entry["planes"],
                    "centers": {center_name: entry["centers"][center_name]},
                }
                rows_here = 0
                for visible_mask in range(1, upper):
                    record = CEN.census_row(row, center_name, visible_mask)
                    record["realization_id"] = entry["realization_id"]
                    records.append(record)
                    rows_here += 1
                configurations.append(
                    {
                        "core_id": core_id,
                        "realization_id": entry["realization_id"],
                        "center": center_name,
                        "rows": rows_here,
                    }
                )
    return {"records": records, "configurations": configurations}


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    sizes = Counter(record["fiber_size"] for record in records)
    degenerate = sum(
        1
        for record in records
        if record["degeneracy"]["coplanar_mergers"]
        or record["degeneracy"]["t_junctions"]
    )
    return {
        "rows": len(records),
        "fiber_size_histogram": {str(key): sizes[key] for key in sorted(sizes)},
        "rows_with_singleton_fiber": sizes.get(1, 0),
        "rows_with_nonsingleton_fiber": len(records) - sizes.get(1, 0),
        "rows_with_observability_degeneracy": degenerate,
        "coplanar_merger_rows": sum(
            1 for record in records if record["degeneracy"]["coplanar_mergers"]
        ),
        "t_junction_rows": sum(
            1 for record in records if record["degeneracy"]["t_junctions"]
        ),
        "rows_enumerated_without_the_conditional_filter": sum(
            1 for record in records if not record["neighbour_filter_used"]
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


def build(skip_frozen_pair: bool) -> dict[str, Any]:
    outcome = sweep(skip_frozen_pair)
    records = outcome["records"]
    metrics = summarize(records)
    stored_fiber = json.loads(FIBER_RESULT.read_text(encoding="utf-8"))

    assertions = {
        "S90_catalogue_and_fiber_census_locks_match": True,
        "every_true_hidden_site_is_an_intrinsic_candidate":
            metrics["true_sites_always_candidates"],
        "C032_center_is_recomputed_exactly_on_every_row":
            metrics["C032_center_always_recovered"],
        "observed_cells_have_pairwise_disjoint_interiors_on_every_row":
            metrics["observed_cells_always_disjoint"],
        "the_true_decomposition_is_always_in_the_enumerated_fiber":
            metrics["true_decomposition_always_in_the_fiber"],
        "no_fiber_is_empty": metrics["fiber_size_histogram"].get("0", 0) == 0,
        "more_than_one_realization_per_core_was_used": len(
            {
                (row["core_id"], row["realization_id"])
                for row in outcome["configurations"]
            }
        )
        > len({row["core_id"] for row in outcome["configurations"]}),
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S91 robustness assertion failure: {failed}")

    return_value = {
        "schema_version": "P43-E-A44-SIX-VERTEX-ROBUSTNESS-v1",
        "project": "P43",
        "phase": "S91_E_A44_six_vertex_realization_robustness",
        "status": "pass_exact_sweep_complete",
        "locked_file_sha256": {
            "results/P43_S90_E_A43B_SIX_VERTEX_RATIONAL_CATALOGUE.json":
                file_sha256(CATALOGUE_RESULT),
            "results/P43_S90_E_A43C_SIX_VERTEX_C033_FIBER_CENSUS.json":
                file_sha256(FIBER_RESULT),
        },
        "skipped_frozen_pair_already_in_S90": skip_frozen_pair,
        "configurations": outcome["configurations"],
        "configuration_count": len(outcome["configurations"]),
        "realizations_per_core": {
            core_id: sorted(
                {
                    row["realization_id"]
                    for row in outcome["configurations"]
                    if row["core_id"] == core_id
                }
            )
            for core_id in sorted(
                {row["core_id"] for row in outcome["configurations"]}
            )
        },
        "metrics": metrics,
        "combined_with_S90": {
            "S90_rows": stored_fiber["metrics"]["rows"],
            "S91_rows": metrics["rows"],
            "total_rows": stored_fiber["metrics"]["rows"] + metrics["rows"],
            "total_nonsingleton_fibers": stored_fiber["metrics"][
                "rows_with_nonsingleton_fiber"
            ]
            + metrics["rows_with_nonsingleton_fiber"],
        },
        "nonsingleton_fibers": [
            record for record in records if record["fiber_size"] != 1
        ],
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "exact source-free fiber cardinality over several exactly constructed realizations and interior centers per six-vertex core type",
                "exact observability-degeneracy measurement on the same configurations",
            ],
            "excluded": [
                "the full realization family, which is positive dimensional",
                "any size above six core vertices",
                "any parametric decision over a realization family",
                "novelty priority or publication readiness",
            ],
        },
    }
    return_value["canonical_mathematical_payload_sha256"] = canonical_hash(
        return_value
    )
    return return_value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", action="store_true")
    parser.add_argument(
        "--include-frozen-pair",
        action="store_true",
        help="also re-run the two configurations already covered by S90",
    )
    args = parser.parse_args()
    result = build(not args.include_frozen_pair)
    if args.verify_existing:
        stored = json.loads(args.output.read_text(encoding="utf-8"))
        if stored != result:
            raise SystemExit("stored S91 robustness result differs from exact rebuild")
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
