#!/usr/bin/env python3
"""P43 S97 / E-A51 classification of coplanar mergers by patch type.

S97 proves that every coplanar merger of the boundary complex falls into one of
four types, and that the four behave completely differently in the centre:

  hinge-hinge          impossible: two distinct facets of a convex core
  wall-wall, same cap  impossible: it would force the apex into its own base plane
  wall-wall, two caps  centre-independent: coplanar for every centre if the two
                       hidden facet planes are perpendicular, for no centre if
                       they are not
  hinge-wall           an affine condition on the centre, so a hyperplane in
                       int P and measure zero

This script checks that classification against the corpus: it records the type
of every merger that actually occurs and verifies that the two impossible types
never appear, that every wall-wall merger comes with a perpendicular pair, and
that every hinge-wall merger sits on the predicted hyperplane.
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
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s91_e_a44_realization_robustness as ROB
import p43_s91_e_a45_cross_section_addendum as ADD
import p43_s97_e_a50_degeneracy_dichotomy as DIC


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S97_E_A51_MERGER_TYPE_CLASSIFICATION.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def apex_owner(union) -> dict[tuple[str, str, str], int]:
    return {K.point_key(union["apex"][index]): index for index in union["flat"]}


def classify_mergers(union, row) -> list[dict[str, Any]]:
    """Every coplanar adjacent patch pair, with its type and its witness."""
    owners = apex_owner(union)
    patches = union["patches"]
    found = []
    for left in range(len(patches)):
        for right in range(left + 1, len(patches)):
            if patches[left]["plane"] != patches[right]["plane"]:
                continue
            keys_left = set(K.point_set_key(patches[left]["points"]))
            keys_right = set(K.point_set_key(patches[right]["points"]))
            if len(keys_left & keys_right) < 2:
                continue
            kinds = tuple(sorted((patches[left]["kind"], patches[right]["kind"])))
            owner_left = [owners[key] for key in keys_left if key in owners]
            owner_right = [owners[key] for key in keys_right if key in owners]
            if kinds == ("wall", "wall"):
                same_cap = owner_left == owner_right
                label = "wall_wall_same_cap" if same_cap else "wall_wall_two_caps"
                perpendicular = None
                if not same_cap and owner_left and owner_right:
                    first = row["planes"][owner_left[0]][0]
                    second = row["planes"][owner_right[0]][0]
                    perpendicular = K.dot(first, second) == 0
                found.append(
                    {
                        "type": label,
                        "perpendicular": perpendicular,
                        "facets": sorted(set(owner_left) | set(owner_right)),
                    }
                )
            elif kinds == ("hinge", "hinge"):
                found.append({"type": "hinge_hinge"})
            else:
                owner = owner_left or owner_right
                found.append(
                    {
                        "type": "hinge_wall",
                        "facets": sorted(set(owner)),
                    }
                )
    return found


def apex_on_hinge_plane(union, row, hidden_index: int) -> bool:
    """The hinge-wall condition: the apex lies on some visible hinge plane."""
    apex = union["apex"][hidden_index]
    for index in union["visible"]:
        normal, offset = row["planes"][index]
        if K.dot(normal, apex) == offset:
            return True
    return False


def configurations() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    families = ROB.realization_families()
    for core_id in sorted(families):
        for entry in families[core_id]:
            entries.append({**entry, "core_id": core_id, "source": "E-A44"})
    base = CEN.prepare_rows()
    for core_id in sorted(ADD.EXTRA_COORDINATES):
        template = base[core_id]
        for realization_id, points in sorted(ADD.EXTRA_COORDINATES[core_id].items()):
            planes = ROB.planes_for(points, template["census_facets"])
            entries.append(
                {
                    "core_id": core_id,
                    "realization_id": realization_id,
                    "core": template["core"],
                    "census_facets": template["census_facets"],
                    "facet_count": template["facet_count"],
                    "points": points,
                    "planes": planes,
                    "centers": ROB.interior_centers(
                        points, planes, template["census_facets"]
                    ),
                    "source": "E-A45",
                }
            )
    return entries


def build(limit: int | None) -> dict[str, Any]:
    types = Counter()
    violations: list[dict[str, Any]] = []
    rows = 0
    rows_with_merger = 0
    hinge_wall_witnessed = 0

    for entry in configurations():
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
                found = classify_mergers(union, row)
                rows += 1
                if not found:
                    continue
                rows_with_merger += 1
                for record in found:
                    types[record["type"]] += 1
                    if record["type"] in ("hinge_hinge", "wall_wall_same_cap"):
                        violations.append(
                            {
                                "kind": "impossible_type_observed",
                                "type": record["type"],
                                "core_id": entry["core_id"],
                                "realization_id": entry["realization_id"],
                                "centre": centre_name,
                                "mask": mask,
                            }
                        )
                    if record["type"] == "wall_wall_two_caps" and not record.get(
                        "perpendicular"
                    ):
                        violations.append(
                            {
                                "kind": "wall_wall_without_perpendicularity",
                                "core_id": entry["core_id"],
                                "realization_id": entry["realization_id"],
                                "centre": centre_name,
                                "mask": mask,
                            }
                        )
                    if record["type"] == "hinge_wall":
                        witnessed = any(
                            apex_on_hinge_plane(union, row, index)
                            for index in record.get("facets", [])
                        )
                        if witnessed:
                            hinge_wall_witnessed += 1
                        else:
                            violations.append(
                                {
                                    "kind": "hinge_wall_without_apex_on_a_hinge_plane",
                                    "core_id": entry["core_id"],
                                    "realization_id": entry["realization_id"],
                                    "centre": centre_name,
                                    "mask": mask,
                                }
                            )
                if limit is not None and rows >= limit:
                    break
            if limit is not None and rows >= limit:
                break
        if limit is not None and rows >= limit:
            break

    metrics = {
        "rows_examined": rows,
        "rows_with_at_least_one_merger": rows_with_merger,
        "merger_types": {key: types[key] for key in sorted(types)},
        "hinge_wall_mergers_with_apex_on_a_hinge_plane": hinge_wall_witnessed,
        "violations": len(violations),
    }
    assertions = {
        "no_hinge_hinge_merger_ever_occurs": types["hinge_hinge"] == 0,
        "no_same_cap_wall_merger_ever_occurs": types["wall_wall_same_cap"] == 0,
        "every_two_cap_wall_merger_has_perpendicular_facet_planes": not any(
            row["kind"] == "wall_wall_without_perpendicularity" for row in violations
        ),
        "every_hinge_wall_merger_has_its_apex_on_a_hinge_plane": not any(
            row["kind"] == "hinge_wall_without_apex_on_a_hinge_plane"
            for row in violations
        ),
        "both_possible_types_are_observed": (
            types["wall_wall_two_caps"] > 0 and types["hinge_wall"] > 0
        )
        if limit is None
        else True,
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S97 merger-classification assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A51-MERGER-TYPES-v1",
        "project": "P43",
        "phase": "S97_E_A51_merger_type_classification",
        "status": "pass_exact_classification_checked",
        "classification": {
            "hinge_hinge": "impossible; two distinct facets of a convex core are never coplanar",
            "wall_wall_same_cap": "impossible; it would put the apex in its own base plane",
            "wall_wall_two_caps": "centre-independent; coplanar for every centre exactly when the two hidden facet planes are perpendicular",
            "hinge_wall": "affine in the centre; the apex must lie on the hinge plane, a hyperplane in int P",
        },
        "metrics": metrics,
        "violations": violations,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the corpus contains only the two possible merger types and each behaves as the classification predicts",
            ],
            "excluded": [
                "the proofs themselves, which are in the S97 document",
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
            raise SystemExit("stored S97 classification differs from exact rebuild")
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
