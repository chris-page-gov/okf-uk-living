from __future__ import annotations

import base64
import hashlib
import html
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_explore_okf  # noqa: E402
BASE_DESCRIPTOR_SHA256 = "ff69f0162a4ba93156b150ae4eea0070c8c8a81187ed5cc7d2425f37b8db34dc"
BASE_DATA_MANIFEST_SHA256 = "fe0e11219ceec88702ca8a5d536d6d0ac0425f3bb29c7586884cfb0e56c957b4"
BASE_PUBLICATION_MANIFEST_SHA256 = "316122b49b937b1afb390e36b62a4fe44c11d40027d7821e1881b588581fd5fc"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def csp_hash(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


class ExploreOkfSidecarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.descriptor = json.loads((ROOT / "explore-okf.json").read_text(encoding="utf-8"))
        cls.projection = json.loads(
            (ROOT / "explore/journey-projection.json").read_text(encoding="utf-8")
        )
        cls.overlay = json.loads(
            (ROOT / "publication/explore-okf-file-manifest.json").read_text(
                encoding="utf-8"
            )
        )
        cls.base_publication = json.loads(
            (ROOT / "publication/pages-file-manifest.json").read_text(encoding="utf-8")
        )
        cls.page = (ROOT / "explore/index.html").read_text(encoding="utf-8")
        cls.home = (ROOT / "publication/explore-okf-index.html").read_text(
            encoding="utf-8"
        )
        cls.learn = (ROOT / "learn/index.html").read_text(encoding="utf-8")
        cls.ask_ai = (ROOT / "learn/ask-an-ai.html").read_text(encoding="utf-8")
        cls.ai_catalogue = (ROOT / "explore/ai/index.html").read_text(
            encoding="utf-8"
        )
        cls.ai_manifest = json.loads(
            (ROOT / "explore/ai/manifest.json").read_text(encoding="utf-8")
        )

    def test_claude_tested_descriptor_and_corpus_identity_are_preserved(self) -> None:
        self.assertEqual(
            BASE_DESCRIPTOR_SHA256, sha256(ROOT / "publication/okf-explorer.json")
        )
        self.assertEqual(
            BASE_DATA_MANIFEST_SHA256, sha256(ROOT / "large/data/manifest.json")
        )
        self.assertEqual(
            BASE_PUBLICATION_MANIFEST_SHA256,
            sha256(ROOT / "publication/pages-file-manifest.json"),
        )
        source = self.descriptor["source"]["base_descriptor"]
        self.assertTrue(source["preserved"])
        self.assertEqual(BASE_DESCRIPTOR_SHA256, source["sha256"])

    def test_projection_input_must_match_the_frozen_publication_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "large/data/records-0.json"
            source.parent.mkdir(parents=True)
            source.write_text('[{"id":"fixture"}]\n', encoding="utf-8")
            manifest = {
                "files": [
                    {
                        "source": "large/data/records-0.json",
                        "target": "large/data/records-0.json",
                        "bytes": source.stat().st_size,
                        "sha256": sha256(source),
                    }
                ]
            }
            with mock.patch.object(build_explore_okf, "ROOT", root):
                self.assertEqual(
                    [{"id": "fixture"}],
                    build_explore_okf.frozen_publication_json(
                        "large/data/records-0.json", manifest
                    ),
                )
                source.write_text('[{"id":"drifted"}]\n', encoding="utf-8")
                with self.assertRaisesRegex(
                    ValueError, "differs from its manifest"
                ):
                    build_explore_okf.frozen_publication_json(
                        "large/data/records-0.json", manifest
                    )

    def test_overlay_is_authorised_hash_bound_and_narrowly_replaces_home(self) -> None:
        self.assertEqual("owner-authorised", self.overlay["publication_state"])
        self.assertTrue(self.overlay["authorised_for_public_review"])
        self.assertFalse(self.overlay["release_grade"])
        self.assertFalse(self.overlay["deployment_automatic"])
        self.assertEqual(BASE_PUBLICATION_MANIFEST_SHA256, self.overlay["base_manifest"]["sha256"])
        base_targets = {item["target"] for item in self.base_publication["files"]}
        overlay_targets = [item["target"] for item in self.overlay["files"]]
        self.assertEqual({"index.html"}, base_targets.intersection(overlay_targets))
        replacement = next(
            item for item in self.overlay["files"] if item["target"] == "index.html"
        )
        base_index = next(
            item
            for item in self.base_publication["files"]
            if item["target"] == "index.html"
        )
        self.assertEqual("publication/explore-okf-index.html", replacement["source"])
        self.assertEqual(base_index["sha256"], replacement["replaces_sha256"])
        self.assertEqual(len(overlay_targets), len(set(overlay_targets)))
        self.assertEqual(self.overlay["file_count"], len(overlay_targets))
        self.assertEqual(
            self.overlay["total_bytes"], sum(item["bytes"] for item in self.overlay["files"])
        )
        for item in self.overlay["files"]:
            source = ROOT / item["source"]
            self.assertEqual(item["bytes"], source.stat().st_size)
            self.assertEqual(item["sha256"], sha256(source))

    def test_descriptor_binds_every_new_entrypoint(self) -> None:
        self.assertEqual("exploratory", self.descriptor["publication_state"])
        self.assertEqual("exploratory", self.descriptor["status"])
        self.assertTrue(self.descriptor["publication"]["publication_authorized"])
        self.assertFalse(self.descriptor["publication"]["release_grade"])
        self.assertTrue(self.descriptor["publication"]["existing_publication_preserved"])
        by_target = {item["target"]: item for item in self.overlay["files"]}
        entrypoints = self.descriptor["entrypoints"]
        for key in (
            "data_manifest",
            "endpoint_labels",
            "journey_projection",
            "journey_projection_schema",
            "explore",
            "home",
            "learn",
            "ai_prompts",
            "ai_family_catalogue",
            "ai_retrieval_manifest",
        ):
            reference = entrypoints[key]
            self.assertEqual(reference, self.descriptor["entrypoint_integrity"][key])
            self.assertEqual(reference["sha256"], by_target[reference["path"]]["sha256"])

    def test_review_home_and_learning_route_are_honest_static_pages(self) -> None:
        for page in (self.home, self.learn, self.ask_ai):
            self.assertIn('<html lang="en-GB">', page)
            self.assertIn('content="noindex,nofollow,noarchive"', page)
            self.assertNotIn("<script", page.casefold())
            self.assertNotIn("<form", page.casefold())
            self.assertNotRegex(page, r"\son[a-z]+\s*=")
        for phrase in (
            "all 293 service-family records in this frozen project corpus",
            "not every UK public service or every local variation",
            "specialist review is not required for 2 and remains required for 291",
            "designed for managed laptops",
            "universal government-device compatibility is not claimed",
        ):
            self.assertIn(phrase, self.home)
        self.assertIn('href="explore/"', self.home)
        self.assertIn('href="learn/"', self.home)
        self.assertIn('href="learn/ask-an-ai.html"', self.home)
        self.assertIn("Ask an AI about a journey", self.home)
        self.assertIn(
            "https://chris-page-gov.github.io/okf-uk-living/"
            "explore/ai/index.html",
            self.home,
        )
        self.assertIn('href="../learn/"', self.page)
        self.assertIn("Choose how much time you have", self.learn)
        self.assertIn("How this was built", self.learn)
        self.assertIn("Detailed documentation library", self.learn)
        self.assertIn("Start with one simple prompt", self.ask_ai)
        self.assertIn("Do not include names, addresses", self.ask_ai)
        self.assertIn("A fluent answer can still be wrong", self.ask_ai)
        self.assertLess(len(self.home.encode("utf-8")), 64 * 1024)
        self.assertLess(len(self.learn.encode("utf-8")), 128 * 1024)
        self.assertLess(len(self.page.encode("utf-8")), 6 * 1024 * 1024)

    def test_ai_retrieval_layer_is_complete_small_and_projection_bound(self) -> None:
        self.assertEqual("explore-okf-ai-retrieval-manifest.v1", self.ai_manifest["schema"])
        self.assertEqual(293, self.ai_manifest["family_count"])
        self.assertEqual(293, len(self.ai_manifest["records"]))
        projection_reference = self.ai_manifest["source_projection"]
        self.assertEqual(
            sha256(ROOT / "explore/journey-projection.json"),
            projection_reference["sha256"],
        )
        self.assertEqual(
            self.descriptor["entrypoints"]["ai_family_catalogue"],
            self.ai_manifest["catalogue"],
        )
        records = {record["id"]: record for record in self.ai_manifest["records"]}
        projected_families = {
            family["id"]: family for family in self.projection["families"]
        }
        self.assertEqual(
            set(projected_families),
            set(records),
        )
        self.assertLess(len(self.ai_catalogue.encode("utf-8")), 160 * 1024)
        self.assertNotIn("<script", self.ai_catalogue.casefold())
        self.assertIn('content="noindex,noarchive"', self.ai_catalogue)
        for record in records.values():
            path = ROOT / record["path"]
            self.assertTrue(path.is_file())
            self.assertLess(record["bytes"], 128 * 1024)
            self.assertEqual(record["bytes"], path.stat().st_size)
            self.assertEqual(record["sha256"], sha256(path))
            self.assertIn(
                f'href="families/{record["id"]}.html"', self.ai_catalogue
            )
            page = path.read_text(encoding="utf-8")
            self.assertIn('<html lang="en-GB">', page)
            self.assertIn('content="noindex,noarchive"', page)
            self.assertNotIn("<script", page.casefold())
            self.assertNotIn("<form", page.casefold())
            self.assertNotRegex(page, r"\son[a-z]+\s*=")
            match = re.search(
                r'<pre id="governed-family-record"><code class="language-json">(.*?)</code></pre>',
                page,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(match)
            envelope = json.loads(html.unescape(match.group(1)))
            self.assertEqual(projected_families[record["id"]], envelope["family"])
            self.assertEqual(projection_reference, envelope["source_projection"])

    def test_ai_school_record_contains_every_field_copilot_could_not_retrieve(self) -> None:
        page = (
            ROOT / "explore/ai/families/apply-for-school-place.html"
        ).read_text(encoding="utf-8")
        match = re.search(
            r'<pre id="governed-family-record"><code class="language-json">(.*?)</code></pre>',
            page,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        envelope = json.loads(html.unescape(match.group(1)))
        family = envelope["family"]
        expected = next(
            item
            for item in self.projection["families"]
            if item["id"] == "apply-for-school-place"
        )
        self.assertEqual(expected, family)
        self.assertEqual("apply-for-school-place", family["id"])
        self.assertEqual("required", family["review"]["specialist_review"])
        self.assertEqual("ordinary", family["episodes"][0]["kind"])
        self.assertEqual("exception", family["episodes"][1]["kind"])
        self.assertEqual(
            ["England", "Scotland", "Wales", "Northern Ireland"],
            [route["jurisdiction"] for route in family["applicability"]],
        )
        self.assertEqual(4, len(family["sources"]))
        self.assertTrue(all(source["url"].startswith("https://") for source in family["sources"]))
        self.assertNotIn("<script", page.casefold())
        self.assertLess(len(page.encode("utf-8")), 128 * 1024)

    def test_authored_publication_copy_uses_planned_urls_and_exact_identity(self) -> None:
        template = (ROOT / "source/explore-okf/home.template.html").read_text(
            encoding="utf-8"
        )
        prompt_guide = (ROOT / "docs/ask-an-ai.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn(
            "Candidate <code>life-course-population-complete-2026-08-08</code>",
            template,
        )
        self.assertNotIn(
            "Snapshot <code>life-course-population-complete-2026-08-08</code>",
            template,
        )
        self.assertIn("AI family catalogue", prompt_guide)
        self.assertIn("Microsoft 365 Copilot: reliable two-step test", prompt_guide)
        self.assertIn("no longer the default prompt input", prompt_guide)
        self.assertIn("If the AI stops at the catalogue", prompt_guide)
        for repository_url in (
            "https://github.com/chris-page-gov/okf-uk-living/blob/main/"
            "docs/start-here.md",
            "https://github.com/chris-page-gov/okf-uk-living/blob/main/"
            "docs/ask-an-ai.md",
            "https://github.com/chris-page-gov/okf-uk-living/blob/main/"
            "evaluation/publication/explore-okf-review-authorization-2026-08-13.md",
        ):
            self.assertIn(repository_url, readme)
        self.assertNotIn("Open the verified population preview", readme)

    def test_standalone_embeds_the_exact_projection_and_valid_csp_hashes(self) -> None:
        csp_match = re.search(
            r'<meta http-equiv="Content-Security-Policy" content="([^"]+)">',
            self.page,
        )
        self.assertIsNotNone(csp_match)
        csp = csp_match.group(1)
        styles = re.findall(r"<style>(.*?)</style>", self.page, flags=re.DOTALL)
        scripts = re.findall(r"<script>(.*?)</script>", self.page, flags=re.DOTALL)
        payloads = re.findall(
            r'<template id="projection-data">(.*?)</template>',
            self.page,
            flags=re.DOTALL,
        )
        self.assertEqual(1, len(styles))
        self.assertEqual(1, len(scripts))
        self.assertEqual(1, len(payloads))
        self.assertIn(f"script-src 'sha256-{csp_hash(scripts[0])}'", csp)
        self.assertIn(f"style-src 'sha256-{csp_hash(styles[0])}'", csp)
        for directive in (
            "default-src 'none'",
            "script-src-attr 'none'",
            "style-src-attr 'none'",
            "img-src 'none'",
            "connect-src 'none'",
            "object-src 'none'",
            "worker-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        ):
            self.assertIn(directive, csp)
        embedded = json.loads(html.unescape(payloads[0]))
        self.assertEqual(self.projection, embedded)

    def test_standalone_uses_no_active_network_or_unsafe_dom_primitive(self) -> None:
        source = (ROOT / "source/explore-okf/standalone.js").read_text(encoding="utf-8")
        for pattern in (
            r"\bfetch\s*\(",
            r"\bXMLHttpRequest\b",
            r"\bWebSocket\b",
            r"\bEventSource\b",
            r"\bWorker\s*\(",
            r"\beval\s*\(",
            r"\bnew\s+Function\b",
            r"\.innerHTML\b",
            r"\.outerHTML\b",
            r"\binsertAdjacentHTML\b",
            r"\bdocument\.write\b",
            r"\blocalStorage\b",
            r"\bsessionStorage\b",
            r"\bindexedDB\b",
            r"\bserviceWorker\b",
            r"\bsendBeacon\b",
        ):
            self.assertIsNone(re.search(pattern, source), pattern)
        self.assertNotIn("<form", self.page.casefold())
        self.assertNotRegex(self.page, r"\son[a-z]+\s*=")
        self.assertNotIn("<base", self.page.casefold())
        self.assertIn('<html lang="en-GB">', self.page)
        self.assertIn('content="noindex,nofollow,noarchive"', self.page)

    def test_standalone_uses_native_lists_with_button_controls(self) -> None:
        template = (ROOT / "source/explore-okf/index.template.html").read_text(
            encoding="utf-8"
        )
        source = (ROOT / "source/explore-okf/standalone.js").read_text(
            encoding="utf-8"
        )
        for markup in (
            '<ul id="family-results" class="family-results"></ul>',
            '<ul id="related-families" class="related-families"></ul>',
        ):
            self.assertIn(markup, template)
            self.assertIn(markup, self.page)
        self.assertNotIn('role="list"', template)
        self.assertNotIn('button.setAttribute("role", "listitem")', source)
        self.assertEqual(2, source.count('const listItem = document.createElement("li");'))
        self.assertEqual(2, source.count("listItem.append(button);"))
        self.assertIn(
            '<article class="dossier" aria-label="Journey details">', template
        )
        self.assertNotIn('aria-labelledby="journey-title"', template)

    def test_route_emphasis_uses_explicit_composite_jurisdiction_membership(self) -> None:
        source = (ROOT / "source/explore-okf/standalone.js").read_text(
            encoding="utf-8"
        )
        match = re.search(
            r"const jurisdictionMembers = Object\.freeze\((\{.*?\})\);",
            source,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        self.assertEqual(
            {
                "England": ["England"],
                "England and Wales": ["England", "Wales"],
                "England, Scotland and Wales": ["England", "Scotland", "Wales"],
                "Great Britain": ["England", "Scotland", "Wales"],
                "Northern Ireland": ["Northern Ireland"],
                "Scotland": ["Scotland"],
                "Wales": ["Wales"],
            },
            json.loads(match.group(1)),
        )
        self.assertIn("routeIncludesNation(item.jurisdiction, chosen)", source)

    def test_search_filter_clears_a_selection_that_is_no_longer_visible(self) -> None:
        source = (ROOT / "source/explore-okf/standalone.js").read_text(
            encoding="utf-8"
        )
        self.assertIn('const clearFamilySelection = () => {', source)
        self.assertIn(
            "if (state.selectedId && !matches.some((family) => family.id === state.selectedId))",
            source,
        )
        self.assertIn("clearFamilySelection();", source)
        self.assertIn("renderResults(matches);", source)

    def test_makefile_has_provider_free_explore_and_gold_gates(self) -> None:
        makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
        self.assertIn("check-explore-okf:", makefile)
        self.assertIn("check-ai-consumer-gold:", makefile)
        self.assertIn(
            "uv run --locked python scripts/build_explore_okf.py --check", makefile
        )
        self.assertIn(
            "uv run --locked python scripts/prepare_explore_okf_publication.py --check",
            makefile,
        )
        self.assertIn(
            "uv run --locked python scripts/evaluate_ai_consumer_answers.py --check-gold",
            makefile,
        )

    def test_projection_exposes_complete_governed_journey_behaviour(self) -> None:
        self.assertEqual(293, self.projection["counts"]["families"])
        self.assertEqual(879, self.projection["counts"]["sources"])
        self.assertEqual(0, self.projection["counts"]["specialist_review_accepted"])
        self.assertEqual(2, self.projection["counts"]["specialist_review_not_required"])
        self.assertEqual(291, self.projection["counts"]["specialist_review_required"])
        families = {family["id"]: family for family in self.projection["families"]}
        self.assertIn("find NHS dentist", families["access-dental-care"]["aliases"])
        self.assertIn(
            "missed bin", families["report-missed-rubbish-collection"]["aliases"]
        )
        for family in families.values():
            episode_kinds = [episode["kind"] for episode in family["episodes"]]
            self.assertEqual("ordinary", episode_kinds[0])
            self.assertTrue(all(kind == "exception" for kind in episode_kinds[1:]))
            self.assertEqual(
                sorted(episode["order"] for episode in family["episodes"]),
                [episode["order"] for episode in family["episodes"]],
            )
            for episode in family["episodes"]:
                self.assertEqual(
                    sorted(step["order"] for step in episode["steps"]),
                    [step["order"] for step in episode["steps"]],
                )
            for related in family["related_families"]:
                self.assertEqual("shared-enclosing-process", related["relationship"])
                self.assertFalse(related["sequenced"])


if __name__ == "__main__":
    unittest.main()
