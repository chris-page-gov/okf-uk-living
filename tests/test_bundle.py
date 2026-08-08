from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_okf_bundle import build_bundle  # noqa: E402


class BundleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.bundle, self.errors = build_bundle()
        self.corpus = self.bundle["corpora"]["okf-uk-living"]

    def test_corpus_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_root_and_research_overview_are_present(self) -> None:
        self.assertIn("index.md", self.corpus["nodes"])
        self.assertIn("research/overview.md", self.corpus["nodes"])

    def test_root_links_to_research_overview(self) -> None:
        pairs = {(edge["source"], edge["target"]) for edge in self.corpus["edges"]}
        self.assertIn(("index.md", "research/overview.md"), pairs)

    def test_bundle_is_deterministic_for_same_source(self) -> None:
        second, second_errors = build_bundle()
        self.assertEqual([], second_errors)
        self.assertEqual(self.bundle, second)

    def test_every_node_exposes_build_and_browser_source_provenance(self) -> None:
        for path_id, node in self.corpus["nodes"].items():
            with self.subTest(path=path_id):
                self.assertEqual(path_id, node["authored_source"])
                self.assertTrue(node["source"].startswith("generated/browser/"))
                self.assertTrue(node["source"].endswith(".html"))
                self.assertEqual(node["source"], node["source_url"])
                self.assertTrue(node["generated"]["by"])
                self.assertTrue(node["generated"]["at"])

    def test_every_relationship_exposes_authority_provenance_evidence_and_rights(self) -> None:
        required = {
            "schema",
            "id",
            "source",
            "target",
            "predicate",
            "assertion_status",
            "assertion_scope",
            "authority",
            "derivation",
            "derivation_activity",
            "observed_at",
            "evidence",
            "rights",
        }
        for edge in self.corpus["edges"]:
            with self.subTest(edge=edge.get("id")):
                self.assertTrue(required <= set(edge))
                self.assertEqual("okf-relationship-assertion.v2", edge["schema"])
                self.assertIn(edge["authority"]["class"], {"derived", "synthetic"})
                self.assertTrue(edge["authority"]["label"])
                self.assertTrue(edge["authority"]["source"])
                self.assertEqual("repository-authored-markdown-link", edge["derivation"])
                self.assertTrue(edge["evidence"])
                self.assertTrue(edge["rights"]["source"])

    def test_bundle_exposes_first_class_licence_and_notice_routes(self) -> None:
        meta = self.bundle["meta"]
        self.assertEqual("MIT", meta["license"])
        self.assertEqual("generated/browser/LICENSE_DECISIONS.html", meta["license_record"])
        self.assertEqual("generated/browser/NOTICE.html", meta["attribution_notice"])


if __name__ == "__main__":
    unittest.main()
