"""Focused public controls for the P43 observable skeleton and flat kernel."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s102_e_a58_reference_reconstruction as ALG
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM


class ObservableSkeleton(unittest.TestCase):
    def test_source_kind_fields_are_ignored(self):
        for index, union in enumerate(GERM.corpus_rows()):
            plain = [
                {"points": patch["points"], "plane": patch["plane"]}
                for patch in union["patches"]
            ]
            self.assertEqual(
                GERM.skeleton_key(GERM.intrinsic_germ_skeleton(union["patches"])),
                GERM.skeleton_key(GERM.intrinsic_germ_skeleton(plain)),
            )
            if index >= 19:
                break

    def test_collinear_subdivision_is_ignored(self):
        for index, union in enumerate(GERM.corpus_rows()):
            self.assertEqual(
                GERM.skeleton_key(GERM.intrinsic_germ_skeleton(union["patches"])),
                GERM.skeleton_key(
                    GERM.intrinsic_germ_skeleton(
                        GERM.subdivide_polygon_edges(union["patches"])
                    )
                ),
            )
            if index >= 9:
                break

    def test_swallowed_corner_witness_reconstructs(self):
        union = GERM.witness_union()
        selected = {
            K.point_key(point)
            for point in GERM.passing_sites(union["patches"], union["center"])
        }
        self.assertEqual(selected, GERM.true_sites(union))


class FlatKernel(unittest.TestCase):
    def test_reconstructs_a_deterministic_sample(self):
        for index, union in enumerate(GERM.corpus_rows()):
            result = ALG.reconstruct(union)
            self.assertIsNotNone(result)
            self.assertEqual(
                {K.point_key(site) for site in result["sites"]},
                ALG.true_sites(union),
            )
            if index >= 119:
                break

    def test_historical_shortcut_agreement_is_only_a_regression_control(self):
        for index, union in enumerate(GERM.corpus_rows()):
            vertices, _edges, _points = ALG.complex_vertices(union["patches"])
            intrinsic = {K.point_key(point) for point in vertices}
            historical = {
                K.point_key(point)
                for point in CEN.candidate_sites(union["patches"])
            }
            self.assertEqual(intrinsic, historical)
            if index >= 39:
                break

    def test_certifier_rejects_a_dropped_site(self):
        checked = 0
        for index, union in enumerate(GERM.corpus_rows()):
            result = ALG.reconstruct(union)
            if len(result["sites"]) >= 2:
                tampered = dict(result)
                tampered["sites"] = result["sites"][:-1]
                tampered["core_halfspaces"] = [
                    (normal, offset)
                    for normal, offset in union["hinge_planes"].values()
                ] + [
                    K.bisector_halfspace(result["centre"], site)
                    for site in tampered["sites"]
                ]
                self.assertFalse(ALG.certifies(union, tampered))
                checked += 1
            if index >= 79:
                break
        self.assertGreater(checked, 0)


class FrozenReceipts(unittest.TestCase):
    def test_schemas_and_assertions(self):
        e60 = json.loads(
            (ROOT / "results" / "P43_S106_E_A60_INTRINSIC_GERM_SKELETON.json")
            .read_text(encoding="utf-8")
        )
        e58 = json.loads(
            (ROOT / "results" / "P43_S102_E_A58_REFERENCE_RECONSTRUCTION.json")
            .read_text(encoding="utf-8")
        )
        self.assertEqual(
            e60["schema_version"],
            "P43-E-A60-INTRINSIC-GERM-SKELETON-v2",
        )
        self.assertEqual(
            e58["schema_version"],
            "P43-E-A58-REFERENCE-RECONSTRUCTION-v2",
        )
        self.assertTrue(all(e60["assertions"].values()))
        self.assertTrue(all(e58["assertions"].values()))


if __name__ == "__main__":
    unittest.main()
