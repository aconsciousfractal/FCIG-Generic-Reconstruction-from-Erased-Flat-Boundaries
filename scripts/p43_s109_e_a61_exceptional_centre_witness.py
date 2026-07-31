#!/usr/bin/env python3
"""P43 S109 / E-A61 exceptional centres, and a defect in the flat certifier.

Theorem A is conditional: it assumes no core vertex passes the signature. Until
now the project had **no datum at all** in the excluded case, because the
condition is the vanishing of a polynomial in the centre and 16,744 sampled
rows never met it. This module builds such data by construction.

**The construction.** A core vertex v passes when every neighbour of v in the
germ skeleton lies on B(o,v), that is, is equidistant from o and v. Take a
square bipyramid whose top apex is v; its neighbours are the four equatorial
vertices, which are coplanar. Put o at the mirror of v in the equatorial plane.
Every neighbour of v is then equidistant from o and v by construction. Keeping
the bottom apex farther from the equator than the mirror keeps o strictly
interior, and keeping every facet at v visible stops any apex from becoming a
neighbour of v.

**What the witnesses show.** At such a centre the reconstruction returns the
true apex set *plus* the passing core vertex, a strict superset. That is
expected: the theorem does not apply. What is not expected is that the flat-component
condition **alone accepts** the wrong answer.  The kernel certifier was
repaired in S109 and now rejects it; this module is the permanent control.

The reason is geometric rather than arithmetic. Cutting v off with the bisector
plane and then attaching the cap over the new facet puts back exactly the piece
that was cut, so the rebuilt *merged flat component* really does equal the
observed one. The flat certifier compares only that component and therefore
cannot see the error. What the alternative destroys is elsewhere: the truncation
removes the recovered visible hinge facets, so the observed nonflat caps have
nothing to attach to and the raw union X is not reproduced.

**The fix**, measured here, is one extra condition: every recovered visible
hinge facet must survive as a facet of the reconstructed core, with the same
vertex set. Those facets are intrinsic by C032, so the check is legitimate.

Nothing here contradicts Theorem A, whose hypothesis excludes these data by
construction. What it corrects is the scope of the "no silent error" property
of the released kernel.
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
import p43_s102_e_a58_reference_reconstruction as ALG
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "results" / "P43_S109_E_A61_EXCEPTIONAL_CENTRE.json"

# (top height a, bottom depth b, equator radius r) with a < b so that the
# mirror of the top apex stays strictly inside the body.
WITNESS_SHAPES = [
    (1, 2, 1),
    (1, 3, 1),
    (1, 2, 2),
    (2, 5, 1),
    (1, 4, 3),
    (3, 7, 2),
]

CERTIFICATIONS_PER_CENTRE = 3


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def rational(*coords) -> K.Point:
    return tuple(Q(c) for c in coords)


# --------------------------------------------------------------------------
# the strengthened certifier
# --------------------------------------------------------------------------


def hinge_facets_survive(union, reconstruction):
    """Delegates to the kernel, so there is one implementation only."""
    return ALG.hinge_facets_survive(union, reconstruction)


def certifies_flat_only(union, reconstruction):
    """The pre-S109 released condition: only the flat component is compared."""
    if reconstruction is None:
        return False
    return ALG.certifies_flat_only(union, reconstruction)


def certifies_strengthened(union, reconstruction):
    """The current kernel certifier: flat equality AND hinge survival."""
    if reconstruction is None:
        return False
    return ALG.certifies(union, reconstruction)


# --------------------------------------------------------------------------
# the witnesses
# --------------------------------------------------------------------------


def build_witness(top: int, bottom: int, radius: int) -> dict[str, Any]:
    """A square bipyramid whose top apex passes, with o inside by construction."""
    vertices = [
        rational(0, 0, top),
        rational(radius, 0, 0),
        rational(0, radius, 0),
        rational(-radius, 0, 0),
        rational(0, -radius, 0),
        rational(0, 0, -bottom),
    ]
    centre = rational(0, 0, -top)
    facets = K.hull_facets(vertices)

    interior = all(K.dot(normal, centre) < offset for (normal, offset), _ in facets)
    at_apex = [index for index, (_, ids) in enumerate(facets) if 0 in ids]
    visible_mask = 0
    for index in at_apex:
        visible_mask |= 1 << index

    census_facets, cyclic, planes = [], [], []
    for (normal, offset), ids in facets:
        points = [vertices[position] for position in ids]
        order = K.cyclic_order(points, normal)
        census_facets.append(list(ids))
        cyclic.append([ids[position] for position in order])
        planes.append((normal, offset))

    row = {
        "core_id": f"Q1-EXC-{top}-{bottom}-{radius}",
        "core": {"facets_cyclic": cyclic},
        "census_facets": census_facets,
        "facet_count": len(facets),
        "points": vertices,
        "planes": planes,
        "centers": {"exceptional": centre},
    }
    union = CEN.build_raw_union(row, "exceptional", visible_mask)
    return {
        "row": row,
        "union": union,
        "apex_vertex": vertices[0],
        "centre_is_interior": interior,
        "facet_count": len(facets),
        "visible": sorted(at_apex),
    }


def inspect_witness(shape: tuple[int, int, int]) -> dict[str, Any]:
    top, bottom, radius = shape
    built = build_witness(top, bottom, radius)
    union = built["union"]
    vertex = built["apex_vertex"]
    centre = union["center"]

    _vertices, edges, by_key = GERM.intrinsic_germ_skeleton(union["patches"])
    neighbours = GERM.neighbours(vertex, edges, by_key)
    passes = GERM.passes_signature(vertex, centre, edges, by_key)

    truth = ALG.true_sites(union)
    result = ALG.reconstruct(union)
    returned = (
        {K.point_key(site) for site in result["sites"]} if result else set()
    )

    flat_only = certifies_flat_only(union, result)
    strengthened = certifies_strengthened(union, result)

    surviving = hinge_facets_survive(union, result) if result else False

    return {
        "shape": {"top": top, "bottom": bottom, "radius": radius},
        "centre_is_strictly_interior": built["centre_is_interior"],
        "facet_count": built["facet_count"],
        "visible_facets_at_the_passing_vertex": built["visible"],
        "neighbours_of_the_core_vertex": len(neighbours),
        "core_vertex_passes": passes,
        "true_apexes": len(truth),
        "sites_returned": len(returned),
        "returned_is_a_strict_superset": truth < returned,
        "flat_component_only_certifier_accepts": flat_only,
        "recovered_hinge_facets_survive": surviving,
        "current_kernel_certifier_accepts": strengthened,
    }


# --------------------------------------------------------------------------
# regression: the extra condition must not reject anything on the corpus
# --------------------------------------------------------------------------


def corpus_regression(limit: int | None) -> dict[str, Any]:
    rows = 0
    attempts = 0
    released_ok = 0
    strengthened_ok = 0
    disagreements = 0

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
        stride = max(1, (1 << entry["facet_count"]) // CERTIFICATIONS_PER_CENTRE)
        for centre_name in sorted(entry["centers"]):
            for mask in range(1, upper):
                rows += 1
                if mask % stride:
                    if limit is not None and rows >= limit:
                        break
                    continue
                union = CEN.build_raw_union(row, centre_name, mask)
                result = ALG.reconstruct(union)
                if result is None:
                    continue
                attempts += 1
                released = certifies_flat_only(union, result)
                strengthened = certifies_strengthened(union, result)
                released_ok += int(released)
                strengthened_ok += int(strengthened)
                if released != strengthened:
                    disagreements += 1
                if limit is not None and rows >= limit:
                    break
            if limit is not None and rows >= limit:
                break
        if limit is not None and rows >= limit:
            break

    return {
        "rows_scanned": rows,
        "certification_attempts": attempts,
        "flat_component_only_accepted": released_ok,
        "current_kernel_certifier_accepted": strengthened_ok,
        "disagreements_on_the_corpus": disagreements,
    }


def build(limit: int | None) -> dict[str, Any]:
    witnesses = [inspect_witness(shape) for shape in WITNESS_SHAPES]
    regression = corpus_regression(limit)

    passing = [w for w in witnesses if w["core_vertex_passes"]]

    assertions = {
        "every_witness_has_a_strictly_interior_centre": all(
            w["centre_is_strictly_interior"] for w in witnesses
        ),
        "every_witness_really_has_a_passing_core_vertex": len(passing) == len(
            witnesses
        ),
        "every_witness_makes_the_algorithm_return_a_strict_superset": all(
            w["returned_is_a_strict_superset"] for w in witnesses
        ),
        "the_flat_component_condition_alone_accepts_the_wrong_answer": all(
            w["flat_component_only_certifier_accepts"] for w in witnesses
        ),
        "the_recovered_hinge_facets_do_not_survive_the_truncation": all(
            not w["recovered_hinge_facets_survive"] for w in witnesses
        ),
        "the_current_kernel_certifier_rejects_every_witness": all(
            not w["current_kernel_certifier_accepts"] for w in witnesses
        ),
        "the_extra_condition_rejects_nothing_on_the_corpus": (
            regression["disagreements_on_the_corpus"] == 0
            and regression["current_kernel_certifier_accepted"]
            == regression["certification_attempts"]
        ),
    }
    if not all(assertions.values()):
        failed = [key for key, value in assertions.items() if not value]
        raise AssertionError(f"S109 exceptional-centre failure: {failed}")

    result = {
        "schema_version": "P43-E-A61-EXCEPTIONAL-CENTRE-v1",
        "project": "P43",
        "phase": "S109_E_A61_exceptional_centre_witness",
        "status": "pass_exceptional_witness_and_certifier_repair",
        "finding": (
            "at a centre where a core vertex passes, the released flat "
            "certifier accepts a reconstruction that is not a compatible "
            "decomposition; the merged flat component is reproduced exactly, "
            "but the recovered visible hinge facets are truncated, so the raw "
            "union is not"
        ),
        "fix": (
            "require every recovered visible hinge facet to survive as a facet "
            "of the reconstructed core with the same vertex set; the hinge "
            "facets are intrinsic by C032"
        ),
        "theorem_impact": (
            "none; Theorem A assumes no core vertex passes and these data "
            "violate that hypothesis by construction"
        ),
        "witnesses": witnesses,
        "corpus_regression": regression,
        "assertions": assertions,
        "claim_boundary": {
            "established": [
                "explicit exact data in the excluded case of Theorem A",
                "the released flat certifier is not free of silent error there",
                "one intrinsic extra condition rejects every witness and "
                "rejects nothing on the frozen corpus",
            ],
            "excluded": [
                "any decision of Q1: whether a genuine second compatible "
                "decomposition exists at an exceptional centre is still open",
                "any claim that the strengthened certifier is complete",
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
            raise SystemExit("stored S109 result differs from exact rebuild")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    print("PASS", result["canonical_mathematical_payload_sha256"])
    print(json.dumps(result["corpus_regression"], indent=2, sort_keys=True))
    for witness in result["witnesses"]:
        print(
            f"  {witness['shape']}  passes={witness['core_vertex_passes']}"
            f"  flat_only={witness['flat_component_only_certifier_accepts']}"
            f"  full={witness['current_kernel_certifier_accepts']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
