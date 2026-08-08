from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_rights import (  # noqa: E402
    EXPECTED_OGL_ATTRIBUTION,
    validate_rights,
    validate_rights_register,
)


class RightsDecisionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.register, self.errors = validate_rights()

    def test_rights_register_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_repository_authored_material_is_mit(self) -> None:
        for authored_kind in ("code", "documentation", "ontology_terms"):
            with self.subTest(authored_kind=authored_kind):
                self.assertEqual("MIT", self.register["repository"][authored_kind]["licence"])
                self.assertTrue(self.register["repository"][authored_kind]["redistribution_allowed"])

    def test_source_content_and_snapshots_are_not_redistributed(self) -> None:
        policy = self.register["use_policy"]
        self.assertEqual("linked_reference_and_original_summary_only", policy["source_content"])
        self.assertFalse(policy["source_content_redistribution_allowed"])
        self.assertFalse(policy["snapshots_acquired"])
        self.assertFalse(policy["snapshot_redistribution_allowed"])

    def test_eligible_generated_projections_are_mit(self) -> None:
        projection = self.register["use_policy"]["generated_projections"]
        self.assertEqual("MIT", projection["licence"])
        self.assertTrue(projection["redistribution_allowed"])
        self.assertIn("upstream expression", projection["condition"])

    def test_all_registered_hosts_have_dated_decisions(self) -> None:
        decisions = self.register["host_decisions"]
        self.assertEqual(28, len(decisions))
        self.assertTrue(all(decision["evidence"]["observed_at"] for decision in decisions))

    def test_link_only_authority_sources_retain_no_source_expression(self) -> None:
        policy = self.register["link_only_reference_policy"]
        self.assertFalse(policy["source_response_body_retained"])
        self.assertFalse(policy["source_snapshots_acquired"])

    def test_reference_standard_licences_are_explicit(self) -> None:
        standards = {item["id"]: item for item in self.register["reference_standards"]}
        self.assertEqual("CC-BY-4.0", standards["cpsv-ap-3.2.0"]["licence"])
        self.assertEqual("CC-BY-SA-4.0", standards["hsds-3.1-documentation"]["licence"])
        self.assertIn("without_a_version", standards["open-referral-uk-website"]["limitation"])
        self.assertEqual("W3C-Document-License-2023", standards["w3c-recommendations"]["licence"])
        self.assertEqual(
            "MIT-code-and-CC-BY-NC-4.0-content",
            standards["okf-explorer"]["licence"],
        )

    def test_ogl_attribution_is_exact(self) -> None:
        self.assertEqual(EXPECTED_OGL_ATTRIBUTION, self.register["attribution"]["ogl_v3_fallback"])

    def test_validator_rejects_unmapped_host(self) -> None:
        register = deepcopy(self.register)
        register["host_decisions"] = register["host_decisions"][:-1]
        errors = validate_rights_register(register)
        self.assertTrue(any("missing host decisions" in error for error in errors))

    def test_validator_rejects_source_redistribution(self) -> None:
        register = deepcopy(self.register)
        register["use_policy"]["source_content_redistribution_allowed"] = True
        errors = validate_rights_register(register)
        self.assertTrue(any("source_content_redistribution_allowed" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
