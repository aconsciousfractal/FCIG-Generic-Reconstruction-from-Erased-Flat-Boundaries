#!/usr/bin/env python3
"""P43 S100 / E-A56 the assembled hypothesis (H) is intrinsic and equivalent.

S99 stated the standing hypothesis of Theorem A as "no wall of a hidden cap is
coplanar with a hinge facet it meets". That names the walls, which exist only
relative to a decomposition, and the proof of the theorem needs the hypothesis
for a *second* decomposition whose walls are exactly what is not yet known.

S100 restates it using only objects C032 recovers from the bare set:

  (H)  for every hinge facet F, the maximal coplanar patch of the boundary
       complex containing F is F itself.

The restatement is worth something only if it excludes the same data. This
script measures that on the six-vertex corpus. For every row it computes both
sides independently:

  intrinsic side       the coplanar-adjacency component of each hinge patch,
                       using nothing but the patch point sets and their planes
  decomposition side   the merger type census of E-A51, which knows which
                       patches are walls and which cap owns them

and checks that the two predicates agree row by row. It also checks the step
the equivalence proof turns on, that a hinge patch whose component is larger
than itself has a wall in that component, and the component form of the
hinge-hinge impossibility.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s97_e_a51_merger_type_classification as CLS


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S100_E_A56_INTRINSIC_HYPOTHESIS.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def coplanar_component(patches: list[dict[str, Any]], start: int) -> set[int]:
    """The maximal coplanar patch containing `start`, as a set of patch indices.

    Two patches are adjacent when they share the same supporting plane and at
    least two points, which is the edge-sharing condition. Only the plane keys
    and the point sets are read, so the result is a function of the bare
    boundary complex.
    """
    keys = [set(K.point_set_key(patch["points"])) for patch in patches]
    component = {start}
    frontier = [start]
    while frontier:
        current = frontier.pop()
        for other in range(len(patches)):
            if other in component:
                continue
            if patches[other]["plane"] != patches[current]["plane"]:
                continue
            if len(keys[current] & keys[other]) < 2:
                continue
            component.add(other)
            frontier.append(other)
    return component


def hypothesis_holds(union: dict[str, Any]) -> tuple[bool, list[dict[str, Any]]]:
    """(H) read off the bare complex, with the offending components recorded."""
    patches = union["patches"]
    hinge_indices = [
        index for index, patch in enumerate(patches) if patch["kind"] == "hinge"
    ]
    failures: list[dict[str, Any]] = []
    for index in hinge_indices:
        component = coplanar_component(patches, index)
        if len(component) == 1:
            continue
        failures.append(
            {
                "hinge_patch": index,
                "component_size": len(component),
                "kinds_in_component": sorted(
                    Counter(patches[other]["kind"] for other in component).items()
                ),
            }
        )
    return not failures, failures


def build(limit: int | None) -> dict[str, Any]:
    rows = 0
    rows_where_h_fails = 0
    rows_with_type_four = 0
    rows_with_permanent_only = 0
    disagreements: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    component_sizes = Counter()

    for entry in CLS.configurations():
        row = {
            "core_id": entry["core_id"],
            "core": entry["core"],
            "census_facets": entry["census_facets"],
            "facet_count": entry["facet_count"],
            "points": entry["points"],
            "planes": entry["planes"],
            "centers": entry["centers"],
        }
        upper = (1 << entry["facet_count"]) - 1
        for centre_name in sorted(entry["centers"]):
            for mask in range(1, upper):
                union = CEN.build_raw_union(row, centre_name, mask)
                rows += 1

                holds, failures = hypothesis_holds(union)
                mergers = CLS.classify_mergers(union, row)
                has_type_four = any(item["type"] == "hinge_wall" for item in mergers)
                has_permanent = any(
                    item["type"] == "wall_wall_two_caps" for item in mergers
                )

                if not holds:
                    rows_where_h_fails += 1
                if has_type_four:
                    rows_with_type_four += 1
                if has_permanent and not has_type_four:
                    rows_with_permanent_only += 1

                where = {
                    "core_id": entry["core_id"],
                    "realization_id": entry["realization_id"],
                    "centre": centre_name,
                    "mask": mask,
                }

                if holds == has_type_four:
                    disagreements.append(
                        {
                            **where,
                            "hypothesis_holds": holds,
                            "type_four_present": has_type_four,
                        }
                    )

                for failure in failures:
                    component_sizes[failure["component_size"]] += 1
                    kinds = dict(failure["kinds_in_component"])
                    if kinds.get("wall", 0) < 1:
                        violations.append(
                            {"kind": "hinge_component_without_a_wall", **where}
                        )
                    if kinds.get("hinge", 0) != 1:
                        violations.append(
                            {"kind": "hinge_component_with_two_hinges", **where}
                        )

                if limit is not None and rows >= limit:
                    break
            if limit is not None and rows >= limit:
                break
        if limit is not None and rows >= limit:
            break

    metrics = {
        "rows_examined": rows,
        "rows_where_the_intrinsic_hypothesis_fails": rows_where_h_fails,
        "rows_carrying_a_hinge_wall_merger": rows_with_type_four,
        "rows_carrying_only_permanent_mergers": rows_with_permanent_only,
        "enlarged_hinge_component_sizes": {
            str(key): component_sizes[key] for key in sorted(component_sizes)
        },
        "disagreements": len(disagreements),
        "violations": len(violations),
    }
    assertions = {
        "the_intrinsic_hypothesis_fails_exactly_when_a_hinge_wall_merger_is_present": (
            not disagreements
        ),
        "every_enlarged_hinge_component_contains_a_wall": not any(
            item["kind"] == "hinge_component_without_a_wall" for item in violations
        ),
        "no_component_of_a_hinge_patch_contains_a_second_hinge_patch": not any(
            item["kind"] == "hinge_component_with_two_hinges" for item in violations
        ),
        "permanent_mergers_alone_never_break_the_hypothesis": (
            rows_with_permanent_only > 0 and rows_where_h_fails == rows_with_type_four
        )
        if limit is None
        else True,
        "both_outcomes_are_observed": (
            0 < rows_where_h_fails < rows
        )
        if limit is None
        else True,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S100 intrinsic-hypothesis assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A56-INTRINSIC-HYPOTHESIS-v1",
        "project": "P43",
        "phase": "S100_E_A56_intrinsic_hypothesis_equivalence",
        "status": "pass_exact_equivalence_checked",
        "hypothesis": (
            "for every hinge facet F, the maximal coplanar patch of the boundary "
            "complex containing F is F itself"
        ),
        "why_it_is_stated_this_way": (
            "it names only the point set and the hinge facets, both intrinsic by "
            "C032, so it transfers to a second compatible decomposition whose "
            "walls are not known in advance"
        ),
        "metrics": metrics,
        "disagreements": disagreements,
        "violations": violations,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "on this corpus the intrinsic hypothesis and the absence of a "
                "hinge-wall merger are the same condition, and permanent mergers "
                "never break it",
            ],
            "excluded": [
                "the equivalence proof itself, which is in S100 section 4",
                "any statement about realizations outside the corpus",
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
            raise SystemExit("stored S100 equivalence differs from exact rebuild")
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
