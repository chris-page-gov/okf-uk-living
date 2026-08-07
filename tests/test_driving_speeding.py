from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_okf_bundle import build_bundle  # noqa: E402
from check_okf import (  # noqa: E402
    DRIVING_SPEEDING_ROUTES,
    DRIVING_SPEEDING_SUPPORTING_NODES,
    validate_driving_speeding_slice,
)


class DrivingSpeedingSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        bundle, self.build_errors = build_bundle()
        self.corpus = bundle["corpora"]["okf-uk-living"]

    def test_slice_is_valid(self) -> None:
        self.assertEqual([], self.build_errors)
        self.assertEqual(
            [],
            validate_driving_speeding_slice(self.corpus["nodes"], self.corpus["edges"]),
        )

    def test_six_routes_and_supporting_graph_are_present(self) -> None:
        self.assertEqual(6, len(DRIVING_SPEEDING_ROUTES))
        self.assertTrue(set(DRIVING_SPEEDING_ROUTES) <= set(self.corpus["nodes"]))
        self.assertTrue(DRIVING_SPEEDING_SUPPORTING_NODES <= set(self.corpus["nodes"]))

    def test_validator_rejects_gb_licensing_on_northern_ireland_route(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        route = nodes["services/northern-ireland-learn-to-drive-car.md"]
        route["provider"] = "driver-and-vehicle-licensing-agency"
        errors = validate_driving_speeding_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("exact authority provider set" in error for error in errors))

    def test_validator_rejects_official_status_on_synthetic_journey(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        nodes["journeys/learning-to-drive-speeding.md"]["assertion_status"] = "official"
        errors = validate_driving_speeding_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("synthetic editorial-example" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
