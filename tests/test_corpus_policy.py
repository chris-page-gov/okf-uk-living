from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_corpus_policy import validate_corpus_policy, validate_policy  # noqa: E402


class CorpusAcquisitionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.policy, self.errors = validate_policy()

    def test_policy_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_approved_denominator_is_bound(self) -> None:
        self.assertEqual(293, self.policy["_validated_service_family_count"])

    def test_local_coverage_is_two_layer(self) -> None:
        local = self.policy["local_coverage"]
        self.assertEqual(
            "exhaustive_authority_registry_plus_representative_and_exception_leaf_routes",
            local["model"],
        )
        self.assertFalse(local["leaf_route_layer"]["exhaustive_every_authority_required"])

    def test_geography_and_health_identifiers_are_explicit(self) -> None:
        identifiers = self.policy["geography_and_organisation_identifiers"]
        self.assertEqual("GSS_nine_character_code", identifiers["administrative_geography"]["primary_identifier"])
        self.assertEqual("ODS_code", identifiers["health_organisations"]["primary_identifier_where_covered"])
        self.assertFalse(identifiers["postcode"]["storage_allowed"])

    def test_health_sources_remain_manual(self) -> None:
        decision = self.policy["health_source_permissions"]
        self.assertEqual("keep_manual_link_and_original_summary_only", decision["decision"])
        self.assertFalse(decision["seek_additional_provider_permission_now"])

    def test_regulator_and_redress_rules_are_governed(self) -> None:
        self.assertEqual("regulator_first", self.policy["private_dependencies"]["decision"])
        self.assertEqual("governed_escalation_taxonomy", self.policy["sector_redress"]["decision"])

    def test_large_projection_is_approved_for_local_evaluation(self) -> None:
        explorer = self.policy["explorer_large_corpus"]
        self.assertEqual("approved_for_local_evaluation", explorer["decision"])
        self.assertEqual(4, len(explorer["prerequisites_completed"]))
        self.assertFalse(explorer["publication_allowed"])

    def test_validator_rejects_health_scraping(self) -> None:
        policy = deepcopy(self.policy)
        policy["health_source_permissions"]["decision"] = "automated_scraping"
        errors = validate_corpus_policy(policy)
        self.assertTrue(any("health sources must remain manual" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
