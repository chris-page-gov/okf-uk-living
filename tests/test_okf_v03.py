from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from okf_v03 import (  # noqa: E402
    OKF_SPECIFICATION,
    OKFConformanceError,
    parse_document,
    resolve_path_field,
    trust_tier,
    validate_bundle,
)
from build_okf_bundle import resolve_link  # noqa: E402
from check_semantic_contract import validate_contract  # noqa: E402


class Core03ProbeTests(unittest.TestCase):
    def make_bundle(self, root: Path) -> None:
        (root / "index.md").write_text(
            "---\nokf_version: \"0.3\"\ntitle: A Life in the UK\n"
            "description: Public service concepts.\nlicense: MIT\n"
            "x-owner-note: retained\n---\n\n# A Life in the UK\n",
            encoding="utf-8",
        )
        (root / "okf.config.json").write_text(
            '{"corpora":[{"sectionOrder":["root","services"]}]}\n', encoding="utf-8"
        )
        (root / "services").mkdir()
        (root / "services" / "index.md").write_text(
            "# Services\n\n- [Example](example.md)\n", encoding="utf-8"
        )
        (root / "services" / "example.md").write_text(
            "---\ntype: Guide\ntitle: Example\ndescription: A synthetic fixture.\n"
            "generated: {by: process:fixture, at: '2026-11-01T00:00:00Z'}\n"
            "verified:\n  - {by: human:reviewer, at: '2026-11-01T00:00:00Z'}\n"
            "sources:\n  - {resource: ../reference.md, id: source-a}\n"
            "x-fixture: kept\n---\n\n# Example\n",
            encoding="utf-8",
        )
        (root / "reference.md").write_text("# Reference\n", encoding="utf-8")

    def test_core03_root_and_extensions_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            report = validate_bundle(root)
            parsed = parse_document(root / "index.md")
            concept = parse_document(root / "services" / "example.md")
            self.assertEqual("0.3", parsed.frontmatter["okf_version"])
            self.assertEqual("retained", parsed.frontmatter["x-owner-note"])
            self.assertEqual("kept", concept.frontmatter["x-fixture"])
            self.assertEqual(1, report["concept_count"])
            self.assertEqual(OKF_SPECIFICATION, report["specification"])

    def test_active_semantic_contract_and_historical_core02_baseline_validate(self) -> None:
        self.assertEqual([], validate_contract())

    def test_duplicate_frontmatter_keys_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "example.md"
            path.write_text("---\ntype: Guide\ntype: Record\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(OKFConformanceError, "duplicate"):
                parse_document(path)

    def test_current_bundle_passes_core03_structural_validation(self) -> None:
        report = validate_bundle(ROOT)
        self.assertGreater(report["concept_count"], 300)
        self.assertEqual("0.3", report["okf_version"])

    def test_root_preserves_extension_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            self.make_bundle(root)
            path = root / "index.md"
            report = validate_bundle(root)
            self.assertEqual(1, report["concept_count"])
            self.assertEqual("retained", parse_document(path).frontmatter["x-owner-note"])

    def test_v03_paths_resolve_from_document_or_bundle_root(self) -> None:
        self.assertEqual(
            "services/reference.md",
            resolve_path_field("services/example.md", "reference.md"),
        )
        self.assertEqual(
            "shared/reference.md",
            resolve_path_field("services/example.md", "/shared/reference.md"),
        )
        self.assertIsNone(resolve_path_field("services/example.md", "../../outside.md"))
        self.assertIsNone(
            resolve_path_field("services/example.md", "https://example.test/source")
        )

    def test_existing_exporter_uses_both_v03_link_forms(self) -> None:
        self.assertEqual(
            "services/reference.md", resolve_link("services/example.md", "reference.md")
        )
        self.assertEqual(
            "shared/reference.md", resolve_link("services/example.md", "/shared/reference.md")
        )

    def test_trust_uses_only_verification_at_or_after_generation(self) -> None:
        stale_human = {
            "generated": {"by": "process:fixture", "at": "2026-11-02T00:00:00Z"},
            "verified": {"by": "human:reviewer", "at": "2026-11-01T00:00:00Z"},
        }
        current_machine = {
            "generated": {"by": "process:fixture", "at": "2026-11-02T00:00:00Z"},
            "verified": {"by": "process:check", "at": "2026-11-02T00:00:00Z"},
        }
        current_human = {
            "generated": {"by": "process:fixture", "at": "2026-11-01"},
            "verified": [
                {"by": "process:check", "at": "2026-11-02"},
                {"by": "human:reviewer", "at": "2026-11-01"},
            ],
        }
        self.assertEqual("unverified", trust_tier(stale_human))
        self.assertEqual("machine-confirmed", trust_tier(current_machine))
        self.assertEqual("human-reviewed", trust_tier(current_human))


if __name__ == "__main__":
    unittest.main()
