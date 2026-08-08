from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_pages_publication import (  # noqa: E402
    EXPECTED_CANDIDATE_ID,
    PUBLICATION_SOURCE_COMMIT,
    descriptor_errors,
    load_frozen_manifest,
    validate_frozen_publication,
)


class PagesPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_frozen_manifest()

    def test_public_descriptor_changes_only_publication_envelope(self) -> None:
        self.assertEqual([], descriptor_errors())

    def test_manifest_is_complete_and_synchronized(self) -> None:
        self.assertEqual([], validate_frozen_publication(self.manifest))
        self.assertEqual(EXPECTED_CANDIDATE_ID, self.manifest["candidate_id"])
        self.assertGreater(self.manifest["file_count"], 1_500)
        self.assertFalse(self.manifest["release_grade"])
        self.assertFalse(self.manifest["source_snapshots_acquired"])
        self.assertFalse(self.manifest["source_response_bodies_retained"])

    def test_manifest_has_unique_safe_targets(self) -> None:
        targets = [item["target"] for item in self.manifest["files"]]
        self.assertEqual(len(targets), len(set(targets)))
        self.assertFalse(any(Path(target).is_absolute() for target in targets))
        self.assertFalse(any(".." in Path(target).parts for target in targets))
        self.assertFalse(any("snapshot" in item["source"].lower() for item in self.manifest["files"]))

    def test_workflow_is_manual_only_and_landing_links_explorer(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        landing = (ROOT / "publication/index.html").read_text(encoding="utf-8")
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertIn(f"ref: {PUBLICATION_SOURCE_COMMIT}", workflow)
        self.assertIn("population-complete preview", landing)
        self.assertIn("https://chris-page-gov.github.io/okf-explorer/", landing)
        self.assertIn("okf-uk-living%2Fokf-explorer.json", landing)


if __name__ == "__main__":
    unittest.main()
