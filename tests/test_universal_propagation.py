"""Public controls for the universal proper-zero propagation theorem."""

from __future__ import annotations

import sys
import re
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

import p43_s131_e_a71_ridge_germ_propagation_audit as RIDGE
import p43_s133_e_a72_independent_global_propagation as GLOBAL


class PaperReleaseSurface(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.paper = (ROOT / "paper" / "main.tex").read_text(encoding="utf-8")

    def test_title_date_and_permanent_artifact_locator(self) -> None:
        self.assertIn(
            r"Exact reconstruction of reflected-cap data\\from an erased flat boundary",
            self.paper,
        )
        self.assertIn(r"\date{}", self.paper)
        self.assertNotIn(r"\date{August", self.paper)
        self.assertIn(
            "https://github.com/aconsciousfractal/"
            "FCIG-Generic-Reconstruction-from-Erased-Flat-Boundaries",
            self.paper,
        )
        self.assertNotIn("This pre-release version has no", self.paper)

    def test_main_theorem_and_evidence_identifiers_are_pinned(self) -> None:
        self.assertIn(r"\label{thm:main}", self.paper)
        self.assertRegex(
            self.paper,
            re.compile(
                r"Every\s+three-dimensional\s+proper-zero\s+datum\s+has\s+"
                r"exactly\s+one\s+compatible\s+decomposition"
            ),
        )
        self.assertIn("cited E-A58, E-A60, E-A61,", self.paper)
        self.assertIn("E-A63, E-A69, E-A71, and E-A72", self.paper)


class UniversalPropagation(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.global_result = GLOBAL.build(
            limit=256,
            presentation_prefix=4,
            run_mutations=True,
        )

    def test_oriented_local_ridge_smoke_exercises_adversarial_families(self) -> None:
        result = RIDGE.build(limit=10, mutation_prefix=5)
        self.assertEqual(result["metrics"]["failures"], 0)
        self.assertGreater(result["metrics"]["hidden_to_hidden_steps"], 0)
        self.assertGreater(result["metrics"]["straight_coplanar_fusions"], 0)
        self.assertTrue(
            result["assertions"]["exceptional_centre_families_are_exercised"]
        )

    def test_forgetting_ray_orientation_is_killed(self) -> None:
        def unoriented_key(vector):
            pivot = next(value for value in vector if value)
            scaled = tuple(value / pivot for value in vector)
            negated = tuple(-value for value in scaled)
            return tuple(str(value) for value in min(scaled, negated))

        with patch.object(RIDGE, "ray_key", side_effect=unoriented_key):
            with self.assertRaisesRegex(RuntimeError, "E-A71 failure"):
                RIDGE.build(limit=10, mutation_prefix=5)

    def test_source_scrubbed_global_reconstruction(self) -> None:
        result = self.global_result
        self.assertTrue(
            result["assertions"][
                "raw_engine_contract_contains_no_source_labels_masks_cap_ids_or_kind_fields"
            ]
        )
        self.assertEqual(result["metrics"]["failures"], 0)
        self.assertEqual(
            result["metrics"]["component_extractions"],
            result["metrics"]["global_bfs_steps"],
        )

    def test_ridge_touch_selector_and_all_deliberate_faults_are_killed(self) -> None:
        result = self.global_result
        self.assertGreater(result["metrics"]["ridge_touch_ambiguities"], 0)
        self.assertEqual(set(result["mutation_kills"]), set(GLOBAL.FAULTS))
        self.assertTrue(
            all(row["killed"] for row in result["mutation_kills"].values())
        )

    def test_fail_closed_helpers_survive_optimized_python(self) -> None:
        with self.assertRaises(RuntimeError):
            RIDGE.require(False, "optimized failure")
        with self.assertRaises(RuntimeError):
            GLOBAL.require(False, "optimized failure")


if __name__ == "__main__":
    unittest.main()
