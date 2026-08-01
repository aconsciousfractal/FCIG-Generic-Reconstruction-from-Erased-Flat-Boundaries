"""Focused public controls for the P43 observable skeleton and flat kernel."""

from __future__ import annotations

import json
import sys
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p43_s90_exact_rational_kernel as K
import p43_s90_e_a43c_six_vertex_c033_fiber_census as CEN
import p43_s102_e_a58_reference_reconstruction as ALG
import p43_s106_e_a60_intrinsic_germ_skeleton as GERM
import p43_s109_e_a61_exceptional_centre_witness as EXC
import p43_s111_e_a63_volume_branch_witness as REV
import check_attestation as ATT


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
            "P43-E-A58-REFERENCE-RECONSTRUCTION-v3",
        )
        self.assertTrue(all(e60["assertions"].values()))
        self.assertTrue(all(e58["assertions"].values()))


class CertifierNecessity(unittest.TestCase):
    def test_flat_only_accepts_and_two_condition_rejects_at_an_exceptional_centre(self):
        """At an exceptional centre the flat-component comparison alone
        certifies a strict superset of the true site set; the two-condition
        certifier rejects it. Both facts are load-bearing for the paper's
        certifier section."""
        record = EXC.inspect_witness((1, 2, 1))
        self.assertTrue(record["centre_is_strictly_interior"])
        self.assertTrue(record["core_vertex_passes"])
        self.assertTrue(record["returned_is_a_strict_superset"])
        self.assertTrue(record["flat_component_only_certifier_accepts"])
        self.assertFalse(record["recovered_hinge_facets_survive"])
        self.assertFalse(record["current_kernel_certifier_accepts"])

    def test_hinge_condition_alone_accepts_and_two_condition_rejects_on_the_reversed_family(self):
        """On the reversed witness family the hinge facets survive while the
        flat components differ, so the flat comparison must return False here.
        Together with the previous test this pins both directions of the
        necessity claim: a mutation forcing either condition to a constant
        breaks one of the two tests."""
        record = REV.inspect(1)
        self.assertIsNotNone(record)
        self.assertTrue(record["core_vertex_passes"])
        self.assertFalse(record["passing_vertex_touches_a_visible_hinge"])
        self.assertTrue(record["hinge_facets_survive"])
        self.assertFalse(record["flat_component_matches"])
        self.assertFalse(record["repaired_certifier_accepts"])


class AttestationSemantics(unittest.TestCase):
    @staticmethod
    def valid_shape_fixture():
        return {
            "schema": ATT.EXPECTED_SCHEMA,
            "artifacts": {
                "source_manifest": {
                    "path": ATT.EXPECTED_ARTIFACT_PATHS["source_manifest"],
                    "entries": ATT.EXPECTED_MANIFEST_ENTRIES,
                },
                "paper_pdf": {
                    "path": ATT.EXPECTED_ARTIFACT_PATHS["paper_pdf"],
                    "pages": ATT.EXPECTED_PDF_PAGES,
                },
                "aggregate_receipt": {
                    "path": ATT.EXPECTED_ARTIFACT_PATHS["aggregate_receipt"],
                },
                "exact_payloads": {
                    key: "0" * 64 for key in ATT.EXPECTED_PAYLOAD_KEYS
                },
                "theorem_7_6_certificates": {
                    name: "0" * 64 for name in ATT.EXPECTED_CERTIFICATE_NAMES
                },
            },
        }

    def test_missing_certificate_map_is_rejected(self):
        tampered = deepcopy(self.valid_shape_fixture())
        tampered["artifacts"].pop("theorem_7_6_certificates")
        with self.assertRaises(RuntimeError):
            ATT.validate_attestation_shape(tampered)

    def test_artifact_role_substitution_and_false_counts_are_rejected(self):
        tampered = deepcopy(self.valid_shape_fixture())
        tampered["artifacts"]["paper_pdf"]["path"] = "MANIFEST_SHA256.txt"
        tampered["artifacts"]["paper_pdf"]["pages"] = 999999
        with self.assertRaises(RuntimeError):
            ATT.validate_attestation_shape(tampered)

    def test_declared_manifest_and_pdf_counts_are_real(self):
        ATT.validate_attestation_shape(self.valid_shape_fixture())
        with TemporaryDirectory(prefix="p43_attestation_test_") as temp:
            temp_root = Path(temp)
            manifest = temp_root / "manifest.txt"
            manifest.write_text(
                "# synthetic closed manifest\n"
                + "".join(f"{'0' * 64}  file-{i}\n" for i in range(54)),
                encoding="utf-8",
            )
            paper = temp_root / "paper.pdf"
            paper.write_bytes(b"%PDF-1.7\n" + b"/Type /Page\n" * 16)
            self.assertEqual(ATT.manifest_entry_count(manifest), 54)
            self.assertEqual(ATT.pdf_page_count(paper), 16)


if __name__ == "__main__":
    unittest.main()
