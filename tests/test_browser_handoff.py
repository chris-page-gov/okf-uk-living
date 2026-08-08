from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_browser_handoff import build_outputs, remove_output_tree  # noqa: E402


class BrowserHandoffTests(unittest.TestCase):
    def setUp(self) -> None:
        self.outputs = build_outputs()

    def test_required_source_and_rights_handoffs_exist(self) -> None:
        required = {
            Path("curriculum/index.html"),
            Path("evidence/licensing-and-attribution.html"),
            Path("LICENSE.html"),
            Path("LICENSE_DECISIONS.html"),
            Path("NOTICE.html"),
            Path("ontology/governed-predicates.v1.yaml.html"),
            Path("profiles/life-course-population-contract.v1.yaml.html"),
            Path("schemas/life-course-family.v1.schema.json.html"),
            Path("schemas/source-link-receipt.v1.schema.json.html"),
            Path("shapes/life-course-family.v1.yaml.html"),
            Path("source/life-course-processes.v1.yaml.html"),
            Path("source/rights-decisions.v1.yaml.html"),
        }
        self.assertTrue(required <= set(self.outputs))

    def test_output_cleanup_ignores_finder_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "browser"
            root.mkdir()
            (root / ".DS_Store").write_bytes(b"finder metadata")
            remove_output_tree(root)
            self.assertFalse(root.exists())

    def test_handoff_preserves_source_identity_and_non_redistribution_boundary(self) -> None:
        content = self.outputs[Path("curriculum/index.html")]
        self.assertIn("Source identity: <code>curriculum/index.md</code>", content)
        self.assertIn("external source content is not redistributed", content)

    def test_licence_record_rewrites_local_links_to_html(self) -> None:
        content = self.outputs[Path("evidence/licensing-and-attribution.html")]
        self.assertIn('href="../LICENSE_DECISIONS.html"', content)
        self.assertIn('href="../NOTICE.html"', content)
        self.assertIn('href="../source/rights-decisions.v1.yaml.html"', content)
        self.assertIn('href="../LICENSE.html"', content)

    def test_handoff_is_deterministic(self) -> None:
        self.assertEqual(self.outputs, build_outputs())


if __name__ == "__main__":
    unittest.main()
