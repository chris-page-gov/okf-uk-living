from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import check_documentation_lockstep as lockstep  # noqa: E402
import check_publication_method as publication_method  # noqa: E402


class DocumentationLockstepTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            (ROOT / "okf.publication.json").read_text(encoding="utf-8")
        )

    def errors(self, *paths: str) -> list[str]:
        errors, _, _ = lockstep.lockstep_errors(self.contract, paths)
        return errors

    def test_uncontrolled_change_does_not_activate_lockstep(self) -> None:
        self.assertEqual([], self.errors("notes/private-scratch.txt"))

    def test_workflow_change_requires_documentation_and_changelog(self) -> None:
        errors = self.errors(".github/workflows/pages-explore-okf.yml")
        self.assertEqual(2, len(errors))
        self.assertTrue(any("documentation" in error for error in errors))
        self.assertTrue(any("CHANGELOG.md" in error for error in errors))

    def test_documentation_without_changelog_is_not_enough(self) -> None:
        errors = self.errors(
            ".github/workflows/pages-explore-okf.yml",
            "docs/okf-publication-method.md",
        )
        self.assertEqual(
            ["controlled publication files changed without CHANGELOG.md"], errors
        )

    def test_dependency_updates_have_no_blanket_exemption(self) -> None:
        errors = self.errors("uv.lock")
        self.assertEqual(2, len(errors))

    def test_complete_lockstep_change_passes(self) -> None:
        errors = self.errors(
            "okf.publication.json",
            "docs/okf-publication-method.md",
            "CHANGELOG.md",
        )
        self.assertEqual([], errors)

    def test_recursive_match_is_segment_aware(self) -> None:
        self.assertTrue(lockstep.path_matches("source/a/b.yaml", "source/"))
        self.assertTrue(lockstep.path_matches("source/a/b.yaml", "source/**/*.yaml"))
        self.assertFalse(lockstep.path_matches("source/a/b.json", "source/**/*.yaml"))


class PublicationMethodTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.contract = json.loads(
            (ROOT / "okf.publication.json").read_text(encoding="utf-8")
        )

    def test_repository_policy_is_internally_consistent(self) -> None:
        self.assertEqual(
            [],
            publication_method.publication_method_errors(self.contract, ROOT),
        )

    def test_remote_activity_remains_manual_and_publication_free_by_default(self) -> None:
        workflow = (ROOT / ".github/workflows/pages-explore-okf.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("\n  pull_request:", workflow)
        self.assertEqual("manual", self.contract["publication"]["mode"])
        self.assertEqual("not-applicable", self.contract["ci"]["impact_routing"])

    def test_exact_byte_owner_gate_is_retained(self) -> None:
        target = self.contract["publication"]["targets"][0]
        self.assertTrue(target["exact_commit_required"])
        self.assertTrue(target["promote_without_rebuild"])
        self.assertEqual(
            "promote-exact-assured-bytes-without-rebuild",
            self.contract["publication"]["candidate_policy"],
        )
        self.assertIn(
            "evaluation/publication/explore-okf-review-authorization-2026-08-13.md",
            self.contract["publication"]["authority"]["evidence_paths"],
        )

    def test_browser_gap_is_explicit_not_simulated(self) -> None:
        limitations = "\n".join(self.contract["limitations"])
        self.assertIn("post-deploy exact-head browser receipt", limitations)
        ordinary = self.contract["ci"]["browser"]["ordinary"]
        self.assertEqual("installed-chrome", ordinary["policy"])
        self.assertTrue(self.contract["verification"]["required"])

    def test_documentation_overlay_does_not_invalidate_frozen_release(self) -> None:
        family = next(
            item
            for item in self.contract["source_families"]
            if item["id"] == "review-and-publication-governance"
        )
        self.assertNotIn("semantic", family["invalidates"])
        self.assertNotIn("runtime", family["invalidates"])
        self.assertNotIn("release", family["invalidates"])
        release = next(
            item for item in self.contract["planes"] if item["id"] == "release"
        )
        self.assertNotIn("documentation", release["depends_on"])
        self.assertNotIn("application", release["depends_on"])

        commands = {
            item["id"]: item for item in self.contract["tooling"]["commands"]
        }
        self.assertNotIn("documentation", commands["build-large-corpus"]["planes"])
        self.assertNotIn(
            "documentation", commands["build-population-assurance"]["planes"]
        )


if __name__ == "__main__":
    unittest.main()
