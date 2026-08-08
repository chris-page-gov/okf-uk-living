from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_population_assurance import build_reports  # noqa: E402


class PopulationAssuranceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs, cls.errors = build_reports()

    def test_population_assurance_is_valid(self) -> None:
        self.assertEqual([], self.errors)
        population_path = next(
            path for path in self.outputs if path.name == "population-complete-report.json"
        )
        omissions_path = next(
            path for path in self.outputs if path.name == "omission-report.json"
        )
        population = json.loads(self.outputs[population_path])
        omissions = json.loads(self.outputs[omissions_path])
        self.assertEqual("population-complete", population["status"])
        self.assertEqual([], omissions["blocking_omissions"])

    def test_assurance_generation_is_deterministic(self) -> None:
        repeated, repeated_errors = build_reports()
        self.assertEqual([], repeated_errors)
        self.assertEqual(self.outputs, repeated)

    def test_candidate_keeps_release_and_publication_separate(self) -> None:
        manifest_path = next(
            path for path in self.outputs if path.name == "candidate-manifest.json"
        )
        manifest = json.loads(self.outputs[manifest_path])
        self.assertTrue(manifest["gates"]["population_complete"])
        self.assertFalse(manifest["gates"]["release_grade"])
        self.assertFalse(manifest["gates"]["publication_authorized"])
        self.assertFalse(manifest["source_response_bodies_retained"])
        self.assertFalse(manifest["source_snapshots_acquired"])


if __name__ == "__main__":
    unittest.main()
