from __future__ import annotations

import copy
import hashlib
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from unittest import mock


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

import prepare_explore_okf_publication as publication  # noqa: E402


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


class ExploreOkfPublicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "publication").mkdir()
        (self.root / "explore").mkdir()
        (self.root / "frozen").mkdir()

        self.old_index = b"frozen landing\n"
        self.new_index = b"Explore OKF landing\n"
        self.asset = b'{"fixture":true}\n'
        self.kept = b"frozen file\n"
        (self.root / "publication/index.html").write_bytes(self.old_index)
        (self.root / "publication/explore-okf-index.html").write_bytes(self.new_index)
        (self.root / "explore/asset.json").write_bytes(self.asset)
        (self.root / "frozen/kept.txt").write_bytes(self.kept)

        self.base_manifest_sha256 = "a" * 64
        self.base = {
            "file_count": 2,
            "files": [
                {
                    "bytes": len(self.old_index),
                    "sha256": digest(self.old_index),
                    "source": "publication/index.html",
                    "target": "index.html",
                },
                {
                    "bytes": len(self.kept),
                    "sha256": digest(self.kept),
                    "source": "frozen/kept.txt",
                    "target": "kept.txt",
                },
            ],
        }
        self.overlay = {
            "schema": publication.OVERLAY_SCHEMA,
            "publication_state": "owner-authorised",
            "release_grade": False,
            "base_manifest": {
                "path": "publication/pages-file-manifest.json",
                "sha256": self.base_manifest_sha256,
                "file_count": 2,
            },
            "file_count": 2,
            "files": [
                self.entry(
                    "publication/explore-okf-index.html",
                    "index.html",
                    self.new_index,
                    replaces_sha256=digest(self.old_index),
                ),
                self.entry("explore/asset.json", "explore/asset.json", self.asset),
            ],
            "total_bytes": len(self.new_index) + len(self.asset),
        }
        self.manifest_path = self.root / "publication/explore-okf-file-manifest.json"
        self.write_overlay_manifest()

        self.patchers = [
            mock.patch.object(publication, "ROOT", self.root),
            mock.patch.object(publication, "OVERLAY_MANIFEST_PATH", self.manifest_path),
            mock.patch.object(
                publication,
                "EXPECTED_PAGES_MANIFEST_SHA256",
                self.base_manifest_sha256,
            ),
        ]
        for patcher in self.patchers:
            patcher.start()
            self.addCleanup(patcher.stop)

    @staticmethod
    def entry(
        source: str,
        target: str,
        content: bytes,
        *,
        replaces_sha256: str | None = None,
    ) -> dict[str, object]:
        result: dict[str, object] = {
            "bytes": len(content),
            "sha256": digest(content),
            "source": source,
            "target": target,
        }
        if replaces_sha256 is not None:
            result["replaces_sha256"] = replaces_sha256
        return result

    def write_overlay_manifest(self, overlay: dict[str, object] | None = None) -> None:
        self.manifest_path.write_text(
            json.dumps(self.overlay if overlay is None else overlay),
            encoding="utf-8",
        )

    def validate(self, overlay: dict[str, object] | None = None) -> list[str]:
        return publication.validate_overlay(
            self.overlay if overlay is None else overlay,
            self.base,
        )

    def test_valid_v2_overlay_has_one_hash_bound_landing_replacement(self) -> None:
        self.assertEqual([], self.validate())

    def test_schema_state_and_exact_replacement_are_required(self) -> None:
        overlay = copy.deepcopy(self.overlay)
        overlay["schema"] = "life-course-pages-additive-publication-manifest.v1"
        overlay["publication_state"] = "owner-authorisation-required"
        overlay["files"] = [overlay["files"][1]]
        overlay["file_count"] = 1
        overlay["total_bytes"] = len(self.asset)

        errors = self.validate(overlay)

        self.assertIn("Explore OKF additive manifest schema is unsupported", errors)
        self.assertIn("Explore OKF additive manifest must be owner-authorised", errors)
        self.assertIn(
            "Explore OKF overlay must replace exactly the frozen index.html target",
            errors,
        )

    def test_replacement_source_and_replaced_hash_are_fixed(self) -> None:
        wrong_source = self.root / "explore/wrong.html"
        wrong_source.write_bytes(self.new_index)
        overlay = copy.deepcopy(self.overlay)
        replacement = overlay["files"][0]
        replacement["source"] = "explore/wrong.html"
        replacement["replaces_sha256"] = "b" * 64

        errors = self.validate(overlay)

        self.assertIn(
            "Explore OKF index.html replacement must come from "
            "publication/explore-okf-index.html",
            errors,
        )
        self.assertIn(
            "Explore OKF index.html does not bind the frozen target SHA-256",
            errors,
        )

        replacement["replaces_sha256"] = "NOT-A-SHA"
        self.assertIn(
            "Explore OKF index.html replaces_sha256 is malformed",
            self.validate(overlay),
        )

    def test_any_second_base_collision_is_rejected(self) -> None:
        (self.root / "kept.txt").write_bytes(b"attempted replacement\n")
        overlay = copy.deepcopy(self.overlay)
        overlay["files"].append(
            self.entry(
                "kept.txt",
                "kept.txt",
                b"attempted replacement\n",
                replaces_sha256=digest(self.kept),
            )
        )
        overlay["file_count"] = 3
        overlay["total_bytes"] += len(b"attempted replacement\n")

        errors = self.validate(overlay)

        self.assertIn(
            "Explore OKF overlay would replace frozen target: kept.txt", errors
        )
        self.assertIn(
            "Explore OKF overlay must replace exactly the frozen index.html target",
            errors,
        )

    def test_duplicate_sources_targets_and_additive_remapping_are_rejected(
        self,
    ) -> None:
        (self.root / "explore/second.json").write_bytes(self.asset)
        overlay = copy.deepcopy(self.overlay)
        overlay["files"].extend(
            [
                self.entry(
                    "explore/second.json",
                    "explore/asset.json",
                    self.asset,
                ),
                self.entry(
                    "explore/asset.json",
                    "explore/remapped.json",
                    self.asset,
                ),
            ]
        )
        overlay["file_count"] = 4
        overlay["total_bytes"] += 2 * len(self.asset)

        errors = self.validate(overlay)

        self.assertIn(
            "Explore OKF overlay target is duplicated: explore/asset.json",
            errors,
        )
        self.assertIn(
            "Explore OKF overlay source is duplicated: explore/asset.json",
            errors,
        )
        self.assertIn(
            "Explore OKF additive source and target differ: "
            "explore/second.json -> explore/asset.json",
            errors,
        )
        self.assertIn(
            "Explore OKF additive source and target differ: "
            "explore/asset.json -> explore/remapped.json",
            errors,
        )

    def test_traversal_symlinks_and_malformed_file_identity_are_rejected(self) -> None:
        unsafe = copy.deepcopy(self.overlay)
        unsafe["files"][1]["source"] = "../asset.json"
        self.assertTrue(
            any(
                "overlay file 1 source is unsafe" in error
                for error in self.validate(unsafe)
            )
        )

        linked_path = self.root / "explore/linked.json"
        linked_path.symlink_to(self.root / "explore/asset.json")
        linked = copy.deepcopy(self.overlay)
        linked["files"][1] = self.entry(
            "explore/linked.json", "explore/linked.json", self.asset
        )
        self.assertIn(
            "Explore OKF overlay source must not use a symlink: explore/linked.json",
            self.validate(linked),
        )

        malformed = copy.deepcopy(self.overlay)
        malformed["files"][1]["sha256"] = "F" * 64
        malformed["files"][1]["bytes"] = True
        malformed["total_bytes"] = True
        errors = self.validate(malformed)
        self.assertIn(
            "Explore OKF overlay SHA-256 is malformed: explore/asset.json", errors
        )
        self.assertIn(
            "Explore OKF overlay byte count is malformed: explore/asset.json", errors
        )
        self.assertIn("Explore OKF overlay total byte count is inconsistent", errors)

    def test_copy_checks_old_index_before_the_only_overwrite(self) -> None:
        destination = self.root / "prepared"
        destination.mkdir()
        (destination / "index.html").write_bytes(self.old_index)
        (destination / "kept.txt").write_bytes(self.kept)

        publication.copy_overlay(destination, self.overlay, self.base)

        self.assertEqual(self.new_index, (destination / "index.html").read_bytes())
        self.assertEqual(self.asset, (destination / "explore/asset.json").read_bytes())
        self.assertTrue(
            (destination / "explore-okf-publication-manifest.json").is_file()
        )

    def test_copy_refuses_a_changed_base_index(self) -> None:
        destination = self.root / "prepared"
        destination.mkdir()
        (destination / "index.html").write_bytes(b"unexpected\n")

        with self.assertRaisesRegex(
            ValueError, "copied frozen index.html differs before replacement"
        ):
            publication.copy_overlay(destination, self.overlay, self.base)

        self.assertEqual(b"unexpected\n", (destination / "index.html").read_bytes())
        self.assertFalse((destination / "explore/asset.json").exists())

    def fake_copy_publication(self, destination: Path, base: dict[str, object]) -> None:
        destination.mkdir(parents=True)
        for item in base["files"]:
            source = self.root / item["source"]
            target = destination / item["target"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        (destination / "publication-manifest.json").write_text("{}\n", encoding="utf-8")
        (destination / ".nojekyll").write_bytes(b"")

    def run_main(self, *, add_unexpected: bool = False) -> tuple[int, str]:
        def copy_base(destination: Path, base: dict[str, object]) -> None:
            self.fake_copy_publication(destination, base)
            if add_unexpected:
                (destination / "unexpected.txt").write_text(
                    "unexpected\n", encoding="utf-8"
                )

        stderr = io.StringIO()
        with (
            mock.patch.object(
                publication, "load_frozen_manifest", return_value=self.base
            ),
            mock.patch.object(
                publication, "validate_frozen_publication", return_value=[]
            ),
            mock.patch.object(publication, "copy_publication", side_effect=copy_base),
            redirect_stderr(stderr),
        ):
            result = publication.main(
                ["--destination", str(self.root / "_site")]
            )
        return result, stderr.getvalue()

    def test_main_builds_the_exact_content_target_set_excluding_manifests(self) -> None:
        result, stderr = self.run_main()

        self.assertEqual(0, result, stderr)
        self.assertEqual(
            {"explore/asset.json", "index.html", "kept.txt"},
            publication.published_content_targets(self.root / "_site"),
        )

    def test_main_rejects_an_unexpected_final_target(self) -> None:
        result, stderr = self.run_main(add_unexpected=True)

        self.assertEqual(1, result)
        self.assertIn(
            "combined Pages artifact differs from the frozen base and "
            "authorised overlay",
            stderr,
        )


if __name__ == "__main__":
    unittest.main()
