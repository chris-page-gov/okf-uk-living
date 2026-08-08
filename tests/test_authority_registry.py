from __future__ import annotations

import sys
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_authority_registry import validate_authority_registry, validate_registry  # noqa: E402


class AuthorityRegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registry, self.errors = validate_authority_registry()

    def test_registry_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_denominators_are_reconciled(self) -> None:
        self.assertEqual(382, self.registry["denominators"]["principal_local_authority_areas_and_normalized_actors"]["count"])
        self.assertEqual(19, self.registry["denominators"]["strategic_and_combined_authorities"]["count"])
        self.assertEqual(10, len(self.registry["sector_maps"]))

    def test_welsh_labels_require_publisher_pairing(self) -> None:
        welsh = [
            area for area in self.registry["geographies"]
            if any(label.get("language") == "cy" for label in area.get("labels", []))
        ]
        self.assertEqual(22, len(welsh))
        self.assertTrue(all(area["jurisdiction"] == "wales" for area in welsh))

    def test_gss_area_does_not_claim_legal_body_name(self) -> None:
        local = next(org for org in self.registry["organisations"] if org["id"].startswith("organisation:principal-local-authority:"))
        self.assertEqual("not_published_by_source", local["official_body_name"]["state"])
        self.assertTrue(local["route_evidence_required"])

    def test_validator_rejects_invented_gss_code(self) -> None:
        registry = deepcopy(self.registry)
        registry["geographies"][0]["code"] = "invented"
        errors = validate_registry(registry, require_receipts=False)
        self.assertTrue(any("nine-character GSS" in error for error in errors))

    def test_health_bulk_acquisition_remains_disabled(self) -> None:
        self.assertFalse(self.registry["denominators"]["health_organisations"]["bulk_acquisition"])


if __name__ == "__main__":
    unittest.main()
