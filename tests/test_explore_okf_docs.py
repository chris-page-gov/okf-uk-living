from __future__ import annotations

import base64
import hashlib
import re
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from render_explore_docs import render_markdown_document  # noqa: E402


class ExploreOkfDocumentRendererTests(unittest.TestCase):
    def render(
        self,
        markdown: str,
        *,
        public_path: Path = Path("explore/learn/reviews/review.html"),
        linked_markdown: str | None = None,
    ) -> str:
        with tempfile.TemporaryDirectory(
            prefix=".test-explore-docs-", dir=ROOT
        ) as temporary_directory:
            directory = Path(temporary_directory)
            source = directory / "review.md"
            source.write_text(markdown, encoding="utf-8")
            mapping = {source: public_path}
            if linked_markdown is not None:
                linked = directory / "guide with space.md"
                linked.write_text(linked_markdown, encoding="utf-8")
                mapping[linked] = Path("explore/learn/guides/guide with space.html")
            return render_markdown_document(source, public_path, mapping)

    def test_source_must_be_a_regular_repository_file_without_symlinks(self) -> None:
        with tempfile.TemporaryDirectory(
            prefix=".test-explore-docs-", dir=ROOT
        ) as temporary_directory, tempfile.TemporaryDirectory() as outside_directory:
            directory = Path(temporary_directory)
            outside_source = Path(outside_directory) / "outside.md"
            outside_source.write_text("# External content\n", encoding="utf-8")
            source_symlink = directory / "review.md"
            source_symlink.symlink_to(outside_source)

            with self.assertRaisesRegex(ValueError, "must not contain symbolic links"):
                render_markdown_document(
                    source_symlink,
                    Path("learn/review.html"),
                    {source_symlink: Path("learn/review.html")},
                )

            with self.assertRaisesRegex(ValueError, "must be inside the repository"):
                render_markdown_document(
                    outside_source,
                    Path("learn/review.html"),
                    {outside_source: Path("learn/review.html")},
                )

    def test_contained_regular_source_remains_supported(self) -> None:
        rendered = self.render("# Contained source\n\nSafe review material.\n")

        self.assertIn('<h1 id="contained-source">Contained source</h1>', rendered)
        self.assertIn("<p>Safe review material.</p>", rendered)

    def test_wrapped_large_number_prose_does_not_become_an_ordered_list(self) -> None:
        rendered = self.render(
            """# Coverage

Specialist review remains required for
291. This is independent exploratory research.
"""
        )

        self.assertNotIn('<ol start="291">', rendered)
        self.assertIn(
            "<p>Specialist review remains required for 291. "
            "This is independent exploratory research.</p>",
            rendered,
        )

    def test_front_matter_and_raw_html_are_not_published_as_markup(self) -> None:
        rendered = self.render(
            """---
title: Hidden metadata title
status: draft
---
# Safe <em>heading</em>

<script>alert("unsafe")</script>

```html
<button onclick="unsafe()">Do not run</button>
```
"""
        )

        self.assertNotIn("Hidden metadata title", rendered)
        self.assertNotIn("status: draft", rendered)
        self.assertIn(
            '<h1 id="safe-em-heading-em">Safe &lt;em&gt;heading&lt;/em&gt;</h1>',
            rendered,
        )
        self.assertIn(
            "&lt;script&gt;alert(\"unsafe\")&lt;/script&gt;", rendered
        )
        self.assertIn(
            "&lt;button onclick=\"unsafe()\"&gt;Do not run&lt;/button&gt;", rendered
        )
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("<button", rendered)

    def test_headings_lists_blockquotes_tables_and_inline_markup_render(self) -> None:
        rendered = self.render(
            """# Review notes

## Evidence

## Evidence

Paragraph with *emphasis*, **strong text** and `inline <code>`.

> Check the official source.

- First item
- **Second item**

3. Third item
4. Fourth item

| Route | State | Count |
| :--- | :---: | ---: |
| Ordinary | Open | 2 |
"""
        )

        self.assertIn('<h1 id="review-notes">Review notes</h1>', rendered)
        self.assertIn('<h2 id="evidence">Evidence</h2>', rendered)
        self.assertIn('<h2 id="evidence-2">Evidence</h2>', rendered)
        self.assertIn("<em>emphasis</em>", rendered)
        self.assertIn("<strong>strong text</strong>", rendered)
        self.assertIn("<code>inline &lt;code&gt;</code>", rendered)
        self.assertIn("<blockquote>\n<p>Check the official source.</p>\n</blockquote>", rendered)
        self.assertIn("<ul>", rendered)
        self.assertIn('<ol start="3">', rendered)
        self.assertIn("<table>", rendered)
        self.assertIn('<th scope="col" class="align-centre">State</th>', rendered)
        self.assertIn('<td class="align-right">2</td>', rendered)

    def test_links_are_rewritten_or_withheld_by_policy(self) -> None:
        rendered = self.render(
            """# Links

[Mapped guide](guide%20with%20space.md#Review state)
[Repository readme](/README.md#licence)
[Secure source](https://www.gov.uk/example?q=value#part)
[Insecure source](http://example.test/)
[Script link](javascript:alert(1))
[Credentialled link](https://user:password@example.test/)
[Malformed link](https://[invalid)
[Outside file](../../outside.md)
![Remote image](https://example.test/image.png)
""",
            linked_markdown="# Guide\n",
        )

        self.assertIn(
            'href="../guides/guide%20with%20space.html#Review%20state"', rendered
        )
        self.assertIn(
            'href="https://github.com/chris-page-gov/okf-uk-living/blob/main/README.md#licence"',
            rendered,
        )
        self.assertIn(
            'href="https://www.gov.uk/example?q=value#part" '
            'rel="noopener noreferrer external" referrerpolicy="no-referrer"',
            rendered,
        )
        self.assertIn("Insecure source", rendered)
        self.assertIn("Script link", rendered)
        self.assertIn("Credentialled link", rendered)
        self.assertIn("Malformed link", rendered)
        self.assertIn("Outside file", rendered)
        self.assertNotIn('href="http:', rendered)
        self.assertNotIn('href="javascript:', rendered)
        self.assertNotIn("outside.md", rendered)
        self.assertIn("Image omitted: Remote image", rendered)
        self.assertNotIn("<img", rendered)

    def test_csp_contains_the_exact_inline_style_hash_and_disables_active_content(self) -> None:
        rendered = self.render("# Security\n")
        style_match = re.search(r"<style>(.*?)</style>", rendered, re.DOTALL)
        self.assertIsNotNone(style_match)
        style = style_match.group(1)
        digest = base64.b64encode(
            hashlib.sha256(style.encode("utf-8")).digest()
        ).decode("ascii")

        self.assertIn(f"style-src 'sha256-{digest}'", rendered)
        for directive in (
            "default-src 'none'",
            "script-src 'none'",
            "script-src-attr 'none'",
            "style-src-attr 'none'",
            "img-src 'none'",
            "connect-src 'none'",
            "object-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        ):
            self.assertIn(directive, rendered)
        self.assertNotIn("<script", rendered)
        self.assertNotIn("<form", rendered)
        self.assertNotIn("<img", rendered)

    def test_default_navigation_is_relative_to_the_public_page(self) -> None:
        rendered = self.render("# Navigation\n")

        self.assertEqual(1, rendered.count('href="../../../index.html"'))
        self.assertEqual(
            1, rendered.count('href="../../index.html"')
        )
        self.assertEqual(1, rendered.count('href="../../../learn/index.html"'))
        self.assertIn(
            'href="../../../generated/browser/NOTICE.html">licence and attribution notices</a>',
            rendered,
        )
        self.assertIn('<html lang="en-GB">', rendered)

    def test_output_is_deterministic(self) -> None:
        markdown = "# Repeatable\n\nA [safe link](https://example.test/path).\n"
        first = self.render(markdown)
        second = self.render(markdown)

        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
