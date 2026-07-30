#!/usr/bin/env python3
"""P43 S97 / E-A50 the permanent-versus-accidental degeneracy dichotomy.

S91 measured where observability degeneracy occurs but not why.  Two candidate
explanations must be separated, because they have opposite consequences for the
genericity argument.

Permanent degeneracy.  If two adjacent hidden facets have perpendicular
supporting planes, their two walls over the shared edge are coplanar for EVERY
interior centre.  With the shared edge on the y axis, aff G = {z = 0} and
aff G' = {x = 0}, a centre (x0, y0, z0) reflects to (x0, y0, -z0) and
(-x0, y0, z0); both lie on {x z0 + z x0 = 0}, identically in the centre.  Such a
mask is degenerate for every centre, so its bad set is not measure zero and the
Fubini-on-the-centre argument cannot absorb it.

Accidental degeneracy.  Everything else is a coincidence at a particular
centre and is absorbed by a measure-zero argument.

This script measures the dichotomy exactly on the whole corpus, and it also
tests the structural claim that lets the permanent class be handled anyway:
that in a permanent merger each apex keeps exactly the vertices of its own
hidden facet as merged-complex neighbours, so the apex signature still fires.

Finally it verifies the eigenvalue identity that makes the centre polynomial of
the hidden-facet condition non-trivial, which is the engine of the
Fubini argument.
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


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S97_E_A50_DEGENERACY_DICHOTOMY.json"


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def perpendicular_adjacent_pairs(planes, census_facets) -> list[tuple[int, int]]:
    pairs = []
    for left in range(len(census_facets)):
        for right in range(left + 1, len(census_facets)):
            shared = set(census_facets[left]) & set(census_facets[right])
            if len(shared) < 2:
                continue
            if K.dot(planes[left][0], planes[right][0]) == 0:
                pairs.append((left, right))
    return pairs


def eigenvalue_identity(normal: K.Point) -> bool:
    """Check (4 n n^T - |n|^2 I) n = 3|n|^2 n and = -|n|^2 u for u orthogonal.

    Those two eigenvalues are nonzero for a nonzero normal, so the quadratic
    part of the hidden-facet condition in the centre never vanishes.
    """
    squared = K.squared_norm(normal)

    def apply(vector: K.Point) -> K.Point:
        return K.subtract(
            K.scale(4 * K.dot(normal, vector), normal),
            K.scale(squared, vector),
        )

    if apply(normal) != K.scale(3 * squared, normal):
        return False
    seed = (Q(1), Q(0), Q(0))
    if K.is_zero(K.cross(normal, seed)):
        seed = (Q(0), Q(1), Q(0))
    for orthogonal in (K.cross(normal, seed), K.cross(normal, K.cross(normal, seed))):
        if K.is_zero(orthogonal):
            return False
        if apply(orthogonal) != K.scale(-squared, orthogonal):
            return False
    return squared != 0


def apexes_keep_their_own_facet(union, row) -> bool:
    """Lemma D test: every true apex sees exactly its own hidden facet."""
    edges, point_by_key = CEN.merged_boundary_edges(union["patches"])
    for index in union["flat"]:
        apex = union["apex"][index]
        neighbours = CEN.merged_neighbours(apex, edges, point_by_key)
        expected = {
            K.point_key(row["points"][vertex])
            for vertex in row["census_facets"][index]
        }
        if set(K.point_set_key(neighbours)) != expected:
            return False
    return True


def configurations() -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    families = ROB.realization_families()
    for core_id in sorted(families):
        for entry in families[core_id]:
            entries.append(
                {
                    "core_id": core_id,
                    "realization_id": entry["realization_id"],
                    "core": entry["core"],
                    "census_facets": entry["census_facets"],
                    "facet_count": entry["facet_count"],
                    "points": entry["points"],
                    "planes": entry["planes"],
                    "centers": entry["centers"],
                    "source": "E-A44",
                }
            )
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
    counts = Counter()
    per_realization: list[dict[str, Any]] = []
    violations: list[dict[str, Any]] = []
    eigen_checks = 0
    processed = 0

    for entry in configurations():
        planes = entry["planes"]
        facets = entry["census_facets"]
        perpendicular = perpendicular_adjacent_pairs(planes, facets)
        for normal, _ in planes:
            if not eigenvalue_identity(normal):
                violations.append(
                    {"kind": "eigenvalue", "core_id": entry["core_id"]}
                )
            eigen_checks += 1

        centre_names = sorted(entry["centers"])
        upper = (1 << entry["facet_count"]) - 1
        summary = Counter()
        for mask in range(1, upper):
            hidden = {
                index
                for index in range(entry["facet_count"])
                if not (mask >> index) & 1
            }
            predicted = any(
                left in hidden and right in hidden
                for left, right in perpendicular
            )
            degenerate_at = []
            lemma_d_ok = True
            for centre_name in centre_names:
                row = {
                    "core_id": entry["core_id"],
                    "core": entry["core"],
                    "census_facets": facets,
                    "facet_count": entry["facet_count"],
                    "points": entry["points"],
                    "planes": planes,
                    "centers": {centre_name: entry["centers"][centre_name]},
                }
                union = CEN.build_raw_union(row, centre_name, mask)
                report = CEN.degeneracy_report(union["patches"])
                is_degenerate = bool(
                    report["coplanar_mergers"] or report["t_junctions"]
                )
                if is_degenerate:
                    degenerate_at.append(centre_name)
                    if not apexes_keep_their_own_facet(union, row):
                        lemma_d_ok = False
                processed += 1

            always = len(degenerate_at) == len(centre_names)
            never = not degenerate_at
            if predicted and not always:
                violations.append(
                    {
                        "kind": "perpendicular_but_not_permanent",
                        "core_id": entry["core_id"],
                        "realization_id": entry["realization_id"],
                        "mask": mask,
                        "degenerate_at": degenerate_at,
                    }
                )
            if always and not predicted:
                violations.append(
                    {
                        "kind": "permanent_without_perpendicular_pair",
                        "core_id": entry["core_id"],
                        "realization_id": entry["realization_id"],
                        "mask": mask,
                    }
                )
            if not lemma_d_ok:
                violations.append(
                    {
                        "kind": "lemma_D_failure",
                        "core_id": entry["core_id"],
                        "realization_id": entry["realization_id"],
                        "mask": mask,
                    }
                )

            if always:
                summary["permanent"] += 1
                counts["permanent_masks"] += 1
            elif never:
                summary["clean"] += 1
                counts["clean_masks"] += 1
            else:
                summary["accidental"] += 1
                counts["accidental_masks"] += 1
            counts["masks"] += 1
            counts["degenerate_rows"] += len(degenerate_at)

            if limit is not None and counts["masks"] >= limit:
                break

        per_realization.append(
            {
                "core_id": entry["core_id"],
                "realization_id": entry["realization_id"],
                "source": entry["source"],
                "perpendicular_adjacent_pairs": len(perpendicular),
                "permanent": summary["permanent"],
                "accidental": summary["accidental"],
                "clean": summary["clean"],
            }
        )
        if limit is not None and counts["masks"] >= limit:
            break

    metrics = {
        "rows_examined": processed,
        "masks_examined": counts["masks"],
        "degenerate_rows": counts["degenerate_rows"],
        "permanent_masks": counts["permanent_masks"],
        "accidental_masks": counts["accidental_masks"],
        "clean_masks": counts["clean_masks"],
        "eigenvalue_identity_checks": eigen_checks,
        "violations": len(violations),
    }
    assertions = {
        "a_perpendicular_adjacent_hidden_pair_always_gives_a_permanent_merger":
            not any(
                row["kind"] == "perpendicular_but_not_permanent"
                for row in violations
            ),
        "a_permanent_merger_always_comes_from_a_perpendicular_adjacent_pair":
            not any(
                row["kind"] == "permanent_without_perpendicular_pair"
                for row in violations
            ),
        # Corpus-level statement, so it is only asserted on a complete run.
        "accidental_degeneracy_exists_and_is_not_explained_by_perpendicularity":
            counts["accidental_masks"] > 0 if limit is None else True,
        "every_apex_keeps_its_own_facet_on_every_degenerate_row":
            not any(row["kind"] == "lemma_D_failure" for row in violations),
        "the_eigenvalue_identity_holds_for_every_facet_normal":
            not any(row["kind"] == "eigenvalue" for row in violations),
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S97 dichotomy assertion failure: {failed}")

    result = {
        "schema_version": "P43-E-A50-DEGENERACY-DICHOTOMY-v1",
        "project": "P43",
        "phase": "S97_E_A50_degeneracy_dichotomy",
        "status": "pass_exact_dichotomy_measured",
        "dichotomy": {
            "permanent": "degenerate at every tested centre; characterised exactly by the presence of a perpendicular adjacent hidden pair",
            "accidental": "degenerate at some centre and clean at another; absorbed by a measure-zero argument in the centre",
        },
        "correction_of_record": (
            "perpendicularity does not explain all measured degeneracy; it "
            "explains exactly the permanent class, and the accidental class is "
            "nonempty, so the two classes are complementary and need different "
            "treatments"
        ),
        "per_realization": per_realization,
        "metrics": metrics,
        "violations": violations,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "the permanent and accidental classes are complementary on the whole corpus and permanence is characterised by perpendicularity there",
                "Lemma D holds on every degenerate row of the corpus, so the apex signature survives permanent mergers",
                "the eigenvalue identity that makes the centre polynomial non-trivial",
            ],
            "excluded": [
                "a proof of the characterisation, which is stated in the S97 document",
                "any statement about realizations outside the corpus",
                "novelty priority or publication readiness",
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
            raise SystemExit("stored S97 result differs from exact rebuild")
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
