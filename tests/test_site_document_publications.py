from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_documentation_only_change import documentation_only_errors  # noqa: E402
from site_document_publications import (  # noqa: E402
    DOCUMENT_MANIFEST_PATH,
    LIBRARY_PUBLIC_PATH,
    build_site_document_outputs,
    discover_site_documents,
)


class SiteDocumentPublicationTests(unittest.TestCase):
    def fixture_root(self) -> tempfile.TemporaryDirectory[str]:
        temporary = tempfile.TemporaryDirectory(prefix=".test-site-docs-", dir=ROOT)
        root = Path(temporary.name)
        (root / "docs").mkdir()
        (root / "schemas").mkdir()
        shutil.copyfile(
            ROOT / "schemas/site-document-publication.schema.json",
            root / "schemas/site-document-publication.schema.json",
        )
        return temporary

    def test_product_requirements_are_nominated_and_deterministic(self) -> None:
        publications = discover_site_documents(ROOT)

        self.assertEqual(1, len(publications))
        publication = publications[0]
        self.assertEqual(Path("docs/product-requirements.md"), publication.source_path)
        self.assertEqual(
            Path("learn/library/product-requirements.html"), publication.public_path
        )
        self.assertEqual("Product and delivery", publication.section)
        self.assertEqual("draft", publication.status)

        outputs, mapping, _ = build_site_document_outputs(ROOT)
        self.assertIn(publication.source_path, mapping)
        self.assertIn(publication.public_path, outputs)
        self.assertIn(LIBRARY_PUBLIC_PATH, outputs)
        self.assertIn(DOCUMENT_MANIFEST_PATH, outputs)
        self.assertIn(
            'href="product-requirements.html"', outputs[LIBRARY_PUBLIC_PATH]
        )
        self.assertIn(
            'href="../../LICENSE">MIT licence</a>',
            outputs[publication.public_path],
        )
        self.assertIn(
            "Document status: <strong>draft</strong>.",
            outputs[publication.public_path],
        )
        manifest = json.loads(outputs[DOCUMENT_MANIFEST_PATH])
        self.assertEqual("okf-site-document-publication-manifest.v1", manifest["schema"])
        self.assertEqual(1, manifest["document_count"])
        self.assertFalse(manifest["deployment_automatic"])
        self.assertEqual(
            publication.public_path.as_posix(),
            manifest["documents"][0]["output"]["path"],
        )

    def test_invalid_or_duplicate_targets_fail_closed(self) -> None:
        with self.fixture_root() as temporary:
            root = Path(temporary)
            (root / "docs/unsafe.md").write_text(
                """---
title: Unsafe
description: Unsafe publication path.
status: draft
publication:
  include: true
  path: ../unsafe.html
  section: Tests
  order: 1
---
# Unsafe
""",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "invalid publication metadata"):
                discover_site_documents(root)

            (root / "docs/unsafe.md").unlink()
            for name in ("first", "second"):
                (root / f"docs/{name}.md").write_text(
                    f"""---
title: {name.title()}
description: Duplicate target fixture.
status: draft
publication:
  include: true
  path: learn/library/duplicate.html
  section: Tests
  order: 1
---
# {name.title()}
""",
                    encoding="utf-8",
                )
            with self.assertRaisesRegex(ValueError, "declared by both"):
                discover_site_documents(root)

    def test_documentation_only_gate_uses_the_declared_dependency_graph(self) -> None:
        allowed = [
            Path("docs/product-requirements.md"),
            Path("learn/library/product-requirements.html"),
            Path("learn/documentation-manifest.json"),
            Path("publication/explore-okf-file-manifest.json"),
            Path("TRACKING.md"),
            Path("learn/library/delivery-tracking.html"),
        ]
        self.assertEqual([], documentation_only_errors(allowed))

        errors = documentation_only_errors(
            [Path("source/domain-registers/before-birth.v1.yaml"), Path("okf.semantic.json")]
        )
        self.assertEqual(2, len(errors))
        self.assertTrue(all("outside the documentation" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
