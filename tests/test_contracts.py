from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_contracts import (  # noqa: E402
    EXPECTED_FIXTURE_IDS,
    REQUIRED_DIMENSIONS,
    validate_fixture,
    validate_contracts,
)


class ContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.profile, self.fixtures, self.errors = validate_contracts()

    def test_contracts_are_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_expected_fixtures_are_present(self) -> None:
        self.assertEqual(EXPECTED_FIXTURE_IDS, {fixture["id"] for fixture in self.fixtures})

    def test_profile_blocks_acquisition_and_publication(self) -> None:
        blocked = set(self.profile["approval"]["blocked_actions"])
        self.assertIn("broad_source_acquisition", blocked)
        self.assertIn("public_bundle_publication", blocked)
        self.assertFalse(self.profile["rights"]["publication_allowed"])

    def test_owner_approval_is_recorded(self) -> None:
        self.assertEqual("approved", self.profile["status"])
        self.assertEqual("owner:chris-page-gov", self.profile["approval"]["approved_by"])
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertEqual("approved", fixture["status"])
                self.assertEqual("owner:chris-page-gov", fixture["approval"]["approved_by"])

    def test_fixtures_cover_required_dimensions(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertTrue(REQUIRED_DIMENSIONS <= set(fixture["dimensions"]))

    def test_fixtures_have_ordinary_and_exception_steps(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertTrue(fixture["journeys"]["ordinary"]["steps"])
                self.assertTrue(fixture["journeys"]["exception"]["steps"])

    def test_fixtures_are_synthetic_editorial_examples(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertTrue(fixture["synthetic"])
                self.assertEqual("editorial-example", fixture["assertion_status"])

    def test_bounded_source_acquisition_is_authorized_but_not_started(self) -> None:
        for fixture in self.fixtures:
            with self.subTest(fixture=fixture["id"]):
                self.assertEqual("authorized_not_started", fixture["source_requirements"]["acquisition_status"])

    def test_validator_rejects_real_personal_context(self) -> None:
        fixture = deepcopy(self.fixtures[0])
        fixture["synthetic"] = False
        errors = validate_fixture(fixture, self.profile)
        self.assertTrue(any("synthetic must be true" in error for error in errors))

    def test_validator_rejects_official_status_before_acquisition(self) -> None:
        fixture = deepcopy(self.fixtures[0])
        fixture["journeys"]["ordinary"]["steps"][0]["assertion_status"] = "official"
        errors = validate_fixture(fixture, self.profile)
        self.assertTrue(any("cannot be official before source acquisition" in error for error in errors))

    def test_validator_rejects_empty_exception_path(self) -> None:
        fixture = deepcopy(self.fixtures[0])
        fixture["journeys"]["exception"]["steps"] = []
        errors = validate_fixture(fixture, self.profile)
        self.assertTrue(any("journeys.exception.steps must be non-empty" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
