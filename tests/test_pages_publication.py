from __future__ import annotations

import hashlib
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from prepare_pages_publication import (  # noqa: E402
    EXPECTED_CANDIDATE_ID,
    FROZEN_PUBLICATION_SOURCE_COMMIT,
    PUBLICATION_DATA_COMMIT,
    descriptor_errors,
    frozen_manifest_source_bytes,
    load_frozen_manifest,
    validate_frozen_publication,
)


class PagesPublicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.manifest = load_frozen_manifest()

    def test_public_descriptor_changes_only_publication_envelope(self) -> None:
        self.assertEqual([], descriptor_errors(frozen=True))

    def test_manifest_is_complete_and_synchronized(self) -> None:
        self.assertEqual([], validate_frozen_publication(self.manifest))
        self.assertEqual(EXPECTED_CANDIDATE_ID, self.manifest["candidate_id"])
        self.assertEqual(1_814, self.manifest["file_count"])
        self.assertFalse(self.manifest["release_grade"])
        self.assertFalse(self.manifest["source_snapshots_acquired"])
        self.assertFalse(self.manifest["source_response_bodies_retained"])
        self.assertEqual(PUBLICATION_DATA_COMMIT, self.manifest["publication_data_commit"])
        targets = {item["target"] for item in self.manifest["files"]}
        self.assertIn("large/data/relationship-runtime/manifest.json", targets)
        self.assertIn(
            "large/data/relationship-runtime/route-locator/manifest.json", targets
        )
        self.assertEqual(
            262,
            sum("relationship-runtime" in target for target in targets),
        )

    def test_manifest_has_unique_safe_targets(self) -> None:
        targets = [item["target"] for item in self.manifest["files"]]
        self.assertEqual(len(targets), len(set(targets)))
        self.assertFalse(any(Path(target).is_absolute() for target in targets))
        self.assertFalse(any(".." in Path(target).parts for target in targets))
        self.assertFalse(any("snapshot" in item["source"].lower() for item in self.manifest["files"]))

    def test_changed_worktree_documentation_uses_the_verified_base_blob(self) -> None:
        entry = next(
            item
            for item in self.manifest["files"]
            if item["source"] == "generated/browser/AGENTS.html"
        )
        data = frozen_manifest_source_bytes(entry)
        self.assertEqual(entry["bytes"], len(data))
        self.assertEqual(entry["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(
            "736d7dc4dbb4e44082f6b7786dd88afd55954792",
            FROZEN_PUBLICATION_SOURCE_COMMIT,
        )

    def test_retired_base_workflow_cannot_overwrite_the_explore_overlay(self) -> None:
        workflow = (ROOT / ".github/workflows/pages.yml").read_text(encoding="utf-8")
        landing = (ROOT / "publication/index.html").read_text(encoding="utf-8")
        self.assertIn("on: {}", workflow)
        self.assertNotIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertNotIn("publication_commit:", workflow)
        self.assertIn("fetch-depth: 0", workflow)
        self.assertIn("population-complete preview", landing)
        self.assertIn("https://chris-page-gov.github.io/okf-explorer/", landing)
        self.assertIn("okf-uk-living%2Fokf-explorer.json", landing)

    def test_additive_workflow_is_the_only_manual_pages_route(self) -> None:
        workflow = (ROOT / ".github/workflows/pages-explore-okf.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("workflow_dispatch:", workflow)
        self.assertNotIn("\n  push:", workflow)
        self.assertIn("publication_commit:", workflow)
        self.assertIn(
            "EXPECTED_PUBLICATION_COMMIT: ${{ inputs.publication_commit }}",
            workflow,
        )
        self.assertIn('test "$GITHUB_SHA" = "$EXPECTED_PUBLICATION_COMMIT"', workflow)


if __name__ == "__main__":
    unittest.main()
