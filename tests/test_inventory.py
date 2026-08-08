from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_inventory import (  # noqa: E402
    EXPECTED_DOMAIN_IDS,
    REFERENCE_JURISDICTIONS,
    flatten_inventory_references,
    validate_inventory,
    validate_reference_inventory,
)


class ExhaustiveReferenceInventoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory, self.errors = validate_inventory()

    def test_inventory_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_declared_denominator_has_one_hundred_twenty_cells(self) -> None:
        denominator = self.inventory["denominator"]
        self.assertEqual(EXPECTED_DOMAIN_IDS, {item["id"] for item in denominator["domains"]})
        self.assertEqual(REFERENCE_JURISDICTIONS, set(denominator["reference_jurisdictions"]))
        self.assertEqual(120, denominator["expected_domain_jurisdiction_cells"])
        self.assertEqual(96, self.inventory["_validated_covered_cell_count"])
        self.assertEqual(24, self.inventory["_validated_partial_cell_count"])

    def test_inventory_includes_all_existing_slice_references(self) -> None:
        self.assertEqual(53, self.inventory["_validated_included_reference_count"])
        self.assertEqual(89, self.inventory["_validated_inventory_reference_count"])

    def test_every_new_reference_has_https_rights_date_and_original_summary(self) -> None:
        references = flatten_inventory_references(self.inventory)
        self.assertTrue(references)
        for reference in references:
            with self.subTest(reference=reference["id"]):
                self.assertTrue(reference["resource"].startswith("https://"))
                self.assertTrue(reference["rights_decision"])
                self.assertEqual("2026-08-07", reference["observed_at"])
                self.assertGreaterEqual(len(reference["summary"].split()), 7)

    def test_authorization_does_not_allow_snapshots_redistribution_or_publication(self) -> None:
        decision = self.inventory["decision"]
        self.assertEqual("owner:chris-page-gov", decision["authorized_by"])
        self.assertFalse(decision["snapshots_acquired"])
        self.assertFalse(decision["source_content_redistribution_allowed"])
        self.assertFalse(decision["publication_allowed"])

    def test_gap_ledger_has_actionable_owner_follow_up(self) -> None:
        self.assertEqual(12, self.inventory["_validated_gap_count"])
        self.assertTrue(all(gap["owner_follow_up"] for gap in self.inventory["gaps"]))
        self.assertTrue(any(gap["id"] == "GAP-EXPLORER-LARGE-CORPUS" for gap in self.inventory["gaps"]))

    def test_validator_rejects_unknown_domain(self) -> None:
        inventory = deepcopy(self.inventory)
        inventory["reference_families"][0]["references"][0]["domains"] = ["invented-domain"]
        errors = validate_reference_inventory(inventory)
        self.assertTrue(any("unknown domains" in error for error in errors))

    def test_validator_rejects_publication_overreach(self) -> None:
        inventory = deepcopy(self.inventory)
        inventory["decision"]["publication_allowed"] = True
        errors = validate_reference_inventory(inventory)
        self.assertTrue(any("publication_allowed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
