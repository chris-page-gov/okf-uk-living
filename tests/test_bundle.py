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


if __name__ == "__main__":
    unittest.main()
