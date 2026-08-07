from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_service_denominator import (  # noqa: E402
    EXPECTED_IMPLEMENTED,
    flatten_service_families,
    service_family_scopes,
    validate_denominator,
    validate_service_denominator,
)


class ServiceFamilyDenominatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.denominator, self.errors = validate_denominator()

    def test_denominator_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_count_is_inside_approved_range(self) -> None:
        count = self.denominator["_validated_family_count"]
        self.assertGreaterEqual(count, 250)
        self.assertLessEqual(count, 400)
        self.assertEqual(self.denominator["decision"]["declared_family_count"], count)

    def test_all_domains_and_waves_are_populated(self) -> None:
        self.assertEqual(24, self.denominator["_validated_domain_count"])
        self.assertTrue(all(value for value in self.denominator["_validated_wave_counts"].values()))

    def test_existing_service_families_are_included(self) -> None:
        family_ids = {item["id"] for item in flatten_service_families(self.denominator)}
        self.assertEqual(EXPECTED_IMPLEMENTED, set(self.denominator["implemented_families"]))
        self.assertTrue(EXPECTED_IMPLEMENTED <= family_ids)

    def test_local_and_private_scopes_are_explicit(self) -> None:
        scopes = service_family_scopes(self.denominator)
        self.assertIn("local-authority", scopes["report-missed-rubbish-collection"])
        self.assertIn("regulated-private", scopes["challenge-private-parking-charge"])
        self.assertIn("mixed-public-private", scopes["obtain-motor-insurance"])

    def test_authorization_retains_safety_and_publication_blocks(self) -> None:
        blocked = set(self.denominator["decision"]["does_not_authorize"])
        self.assertIn("source_snapshots", blocked)
        self.assertIn("source_content_redistribution", blocked)
        self.assertIn("ci_or_publication", blocked)

    def test_validator_rejects_duplicate_family(self) -> None:
        denominator = deepcopy(self.denominator)
        duplicate = denominator["domains"][0]["wave-1"][0]
        denominator["domains"][1]["wave-1"].append(duplicate)
        errors = validate_service_denominator(denominator)
        self.assertTrue(any("duplicate service-family ids" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
