from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_okf_bundle import build_bundle  # noqa: E402
from check_okf import (  # noqa: E402
    BEREAVEMENT_ROUTES,
    BEREAVEMENT_SUPPORTING_NODES,
    validate_bereavement_slice,
)


class BereavementSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        bundle, self.build_errors = build_bundle()
        self.corpus = bundle["corpora"]["okf-uk-living"]

    def test_slice_is_valid(self) -> None:
        self.assertEqual([], self.build_errors)
        self.assertEqual(
            [],
            validate_bereavement_slice(self.corpus["nodes"], self.corpus["edges"]),
        )

    def test_eight_routes_and_supporting_graph_are_present(self) -> None:
        self.assertEqual(8, len(BEREAVEMENT_ROUTES))
        self.assertTrue(set(BEREAVEMENT_ROUTES) <= set(self.corpus["nodes"]))
        self.assertTrue(BEREAVEMENT_SUPPORTING_NODES <= set(self.corpus["nodes"]))

    def test_validator_rejects_tell_us_once_as_northern_ireland_provider(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        route = nodes["services/northern-ireland-death-notifications.md"]
        route["provider"] = "tell-us-once-service"
        errors = validate_bereavement_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("exact authority provider set" in error for error in errors))

    def test_validator_rejects_official_status_on_synthetic_journey(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        nodes["journeys/death-bereavement-estate.md"]["assertion_status"] = "official"
        errors = validate_bereavement_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("synthetic editorial-example" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
