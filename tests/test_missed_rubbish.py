from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_okf_bundle import build_bundle  # noqa: E402
from check_okf import (  # noqa: E402
    MISSED_RUBBISH_ROUTES,
    MISSED_RUBBISH_SUPPORTING_NODES,
    validate_missed_rubbish_slice,
)


class MissedRubbishSliceTests(unittest.TestCase):
    def setUp(self) -> None:
        bundle, self.build_errors = build_bundle()
        self.corpus = bundle["corpora"]["okf-uk-living"]

    def test_slice_is_valid(self) -> None:
        self.assertEqual([], self.build_errors)
        self.assertEqual(
            [],
            validate_missed_rubbish_slice(self.corpus["nodes"], self.corpus["edges"]),
        )

    def test_four_local_routes_and_supporting_graph_are_present(self) -> None:
        self.assertTrue(set(MISSED_RUBBISH_ROUTES) <= set(self.corpus["nodes"]))
        self.assertTrue(MISSED_RUBBISH_SUPPORTING_NODES <= set(self.corpus["nodes"]))

    def test_validator_rejects_cross_jurisdiction_rule_drift(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        nodes["services/cardiff-missed-collection.md"]["jurisdiction"] = "england:coventry"
        errors = validate_missed_rubbish_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("jurisdiction must be wales:cardiff" in error for error in errors))

    def test_validator_rejects_official_status_on_synthetic_journey(self) -> None:
        nodes = deepcopy(self.corpus["nodes"])
        nodes["journeys/missed-rubbish-collection.md"]["assertion_status"] = "official"
        errors = validate_missed_rubbish_slice(nodes, self.corpus["edges"])
        self.assertTrue(any("synthetic editorial-example" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
