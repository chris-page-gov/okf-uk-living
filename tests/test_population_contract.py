from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_population_contract import load_population_inputs, validate_population_contract  # noqa: E402


class PopulationContractTests(unittest.TestCase):
    def test_population_contract_is_valid(self) -> None:
        self.assertEqual([], validate_population_contract())

    def test_every_family_is_mapped_once(self) -> None:
        values, errors = load_population_inputs()
        self.assertEqual([], errors)
        mutated = copy.deepcopy(values)
        removed = mutated["processes"]["processes"][0]["families"].pop()
        observed = validate_population_contract(mutated)
        self.assertTrue(any(removed in error and "unmapped" in error for error in observed))

    def test_publication_and_snapshot_boundaries_are_required(self) -> None:
        values, errors = load_population_inputs()
        self.assertEqual([], errors)
        mutated = copy.deepcopy(values)
        mutated["contract"]["authorization"]["prohibits"].remove("source_snapshots")
        self.assertIn("population contract must prohibit source_snapshots", validate_population_contract(mutated))

    def test_link_receipt_cannot_retain_source_body(self) -> None:
        values, errors = load_population_inputs()
        self.assertEqual([], errors)
        mutated = copy.deepcopy(values)
        mutated["link_schema"]["properties"]["response_body_retained"]["const"] = True
        self.assertIn("source-link receipts must forbid retaining response bodies", validate_population_contract(mutated))


if __name__ == "__main__":
    unittest.main()

