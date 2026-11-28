#!/usr/bin/env python3
"""Verify or prepare the owner-authorised Explore OKF Pages overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any

from prepare_pages_publication import (
    EXPECTED_PAGES_MANIFEST_SHA256,
    ROOT,
    copy_publication,
    load_frozen_manifest,
    validate_frozen_publication,
)


OVERLAY_MANIFEST_PATH = ROOT / "publication" / "explore-okf-file-manifest.json"
OVERLAY_SCHEMA = "life-course-pages-additive-publication-manifest.v2"
REPLACEMENT_SOURCE = Path("publication/explore-okf-index.html")
REPLACEMENT_TARGET = Path("index.html")
CONTROL_TARGETS = {
    ".nojekyll",
    "explore-okf-publication-manifest.json",
    "publication-manifest.json",
}
MANIFEST_SOURCES = {
    "publication/explore-okf-file-manifest.json",
    "publication/pages-file-manifest.json",
}
CORE03_PREFIX = "core-0.3-preview/"
CORE03_ALLOWED_SOURCE_TARGETS = {
    ("okf-explorer.json", "okf-explorer-core-0.3.json"),
    (
        "evaluation/publication/core-0.3-preview-authorization-2026-11-28.md",
        "core-0.3-preview/authorization.md",
    )
}
SHA256_PATTERN = re.compile(r"[0-9a-f]{64}")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and SHA256_PATTERN.fullmatch(value) is not None


def is_allowed_core03_mapping(source: str, target: str) -> bool:
    if (source, target) in CORE03_ALLOWED_SOURCE_TARGETS:
        return True
    return (
        source.startswith(("generated/semantic/", "generated/browser/"))
        and target == CORE03_PREFIX + source
    )


def validate_core03_closure(
    overlay: dict[str, Any],
    files: list[object],
    base_by_target: dict[str, dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    record_path = (
        "evaluation/publication/core-0.3-preview-authorization-2026-11-28.md"
    )
    route = "core-0.3-preview/"
    closure_target = "core-0.3-preview/closure.json"
    index_target = "core-0.3-preview/index.html"
    descriptor_target = "okf-explorer-core-0.3.json"
    declaration = overlay.get("core_0_3_preview")
    if not isinstance(declaration, dict):
        return ["Core 0.3 preview publication declaration is missing"]
    if declaration.get("state") != "owner-authorised-review-preview":
        errors.append("Core 0.3 preview is not marked as owner-authorised review")
    if declaration.get("route") != route:
        errors.append("Core 0.3 preview route is unexpected")
    if declaration.get("authorization_record") != record_path:
        errors.append("Core 0.3 preview authorisation record is unexpected")
    if declaration.get("release_grade") is not False:
        errors.append("Core 0.3 preview must not be release grade")
    closure_ref = declaration.get("closure_manifest")
    if not isinstance(closure_ref, dict):
        return errors + ["Core 0.3 preview closure reference is malformed"]
    if closure_ref.get("path") != closure_target:
        errors.append("Core 0.3 preview closure path is unexpected")
    if not is_sha256(closure_ref.get("sha256")):
        errors.append("Core 0.3 preview closure SHA-256 is malformed")

    overlay_by_target = {
        item.get("target"): item
        for item in files
        if isinstance(item, dict) and isinstance(item.get("target"), str)
    }
    closure_entry = overlay_by_target.get(closure_target)
    if not isinstance(closure_entry, dict):
        return errors + ["Core 0.3 preview closure file is missing from the overlay"]
    if closure_entry.get("sha256") != closure_ref.get("sha256"):
        errors.append("Core 0.3 preview closure SHA-256 differs from its overlay entry")
    try:
        closure_bytes = (ROOT / safe_relative_path(closure_entry.get("source"), "Core 0.3 closure source")).read_bytes()
        closure = json.loads(closure_bytes)
    except (OSError, ValueError, json.JSONDecodeError):
        return errors + ["Core 0.3 preview closure cannot be read as JSON"]
    if sha256_path(ROOT / safe_relative_path(closure_entry.get("source"), "Core 0.3 closure source")) != closure_ref.get("sha256"):
        errors.append("Core 0.3 preview closure bytes differ from the declared digest")
    if closure.get("schema") != "okf-uk-living-core-0.3-preview-closure.v1":
        errors.append("Core 0.3 preview closure schema is unsupported")
    if closure.get("status") != "owner-authorised-public-review-preview" or closure.get("release_grade") is not False:
        errors.append("Core 0.3 preview closure has an unsafe publication status")
    core = closure.get("okf_core", {})
    if not isinstance(core, dict) or core.get("version") != "0.3" or core.get("status") != "migration":
        errors.append("Core 0.3 preview closure must retain migration status")

    profile = closure.get("profile", {})
    expected_profile_hashes = {
        "profiles/bundle-wiki/v2/index.md": "c4a3f30009c73320ff87703e54d9b8d38ef640e6e30342422619236eaaf90a9d",
        "profiles/bundle-wiki/v2/repository-contract.schema.json": "168688fc8e90eff592ed3d6e38671391a9797d4308379ca9129b406e41c1d428",
    }
    if (
        not isinstance(profile, dict)
        or profile.get("uri") != "https://chris-page-gov.github.io/okf-explorer/profile/bundle-wiki/v2/"
        or profile.get("status") != "experimental implementation profile"
        or profile.get("conformance_claim") is not False
        or profile.get("source_commit") != "171efeeb8525691ab6d89f4ddfac2146374e862c"
        or profile.get("files") != expected_profile_hashes
    ):
        errors.append("Core 0.3 preview profile identity or experimental status is unexpected")

    candidate = closure.get("candidate", {})
    if not isinstance(candidate, dict):
        candidate = {}
    descriptor = candidate.get("core_descriptor", {})
    expected_assets: dict[str, str] = {}
    if isinstance(descriptor, dict) and descriptor.get("path") == descriptor_target:
        expected_assets[descriptor_target] = str(descriptor.get("sha256", ""))
        descriptor_entry = overlay_by_target.get(descriptor_target)
        if not isinstance(descriptor_entry, dict) or descriptor_entry.get("sha256") != descriptor.get("sha256"):
            errors.append("Core 0.3 Reader descriptor is not bound by the overlay")
        else:
            try:
                descriptor_path = ROOT / safe_relative_path(
                    descriptor_entry.get("source"), "Core 0.3 descriptor source"
                )
                descriptor_value = json.loads(descriptor_path.read_text(encoding="utf-8"))
                if (
                    descriptor_value.get("okf_version") != "0.3"
                    or descriptor_value.get("status") != "owner-authorised-public-review-preview"
                    or descriptor_value.get("source", {}).get("publication_authorized") is not True
                ):
                    errors.append("Core 0.3 Reader descriptor does not carry its authorised preview status")
                entrypoints = descriptor_value.get("entrypoints", {})
                for path_value in entrypoints.values() if isinstance(entrypoints, dict) else []:
                    if isinstance(path_value, dict):
                        path_value = path_value.get("path")
                    if isinstance(path_value, str) and not path_value.startswith("https://"):
                        safe_relative_path(path_value, "Core 0.3 descriptor resource")
            except (OSError, ValueError, json.JSONDecodeError, AttributeError):
                errors.append("Core 0.3 Reader descriptor is invalid JSON")
    else:
        errors.append("Core 0.3 Reader descriptor path is unexpected")
    assets = candidate.get("assets")
    if not isinstance(assets, list) or not assets:
        errors.append("Core 0.3 candidate asset list is missing")
        assets = []
    for item in assets:
        if not isinstance(item, dict):
            errors.append("Core 0.3 candidate asset entry is malformed")
            continue
        target = item.get("path")
        digest = item.get("sha256")
        if not isinstance(target, str) or not target.startswith(route) or not is_sha256(digest):
            errors.append("Core 0.3 candidate asset path or digest is malformed")
            continue
        if target in expected_assets:
            errors.append(f"Core 0.3 candidate asset is duplicated: {target}")
        expected_assets[target] = digest
        overlay_item = overlay_by_target.get(target)
        if not isinstance(overlay_item, dict) or overlay_item.get("sha256") != digest:
            errors.append(f"Core 0.3 candidate asset is not bound by the overlay: {target}")
    expected_assets[closure_target] = str(closure_ref.get("sha256", ""))
    if index_target not in overlay_by_target:
        errors.append("Core 0.3 preview index page is missing from the overlay")
    else:
        expected_assets[index_target] = str(overlay_by_target[index_target].get("sha256", ""))
    actual_core_targets = {
        target for target in overlay_by_target
        if target.startswith(route) or target == descriptor_target
    }
    if actual_core_targets != set(expected_assets):
        errors.append("Core 0.3 preview overlay targets differ from its closure")

    shared = closure.get("shared_frozen_base", {})
    if not isinstance(shared, dict) or shared.get("sha256") != EXPECTED_PAGES_MANIFEST_SHA256:
        errors.append("Core 0.3 preview does not bind the frozen base manifest")
    else:
        declared = shared.get("large_data_assets")
        expected_shared = {
            path: {"bytes": item.get("bytes"), "sha256": item.get("sha256")}
            for path, item in base_by_target.items()
            if path.startswith("large/data/")
        }
        observed_shared = {
            item.get("path"): {"bytes": item.get("bytes"), "sha256": item.get("sha256")}
            for item in declared if isinstance(item, dict)
        } if isinstance(declared, list) else {}
        if observed_shared != expected_shared:
            errors.append("Core 0.3 preview shared data differs from the frozen base manifest")
    return errors


def safe_relative_path(value: object, label: str) -> Path:
    if not isinstance(value, str) or not value or value.strip() != value:
        raise ValueError(f"{label} is missing")
    if "\\" in value or "\x00" in value:
        raise ValueError(f"{label} is unsafe")
    path = Path(value)
    if (
        path.is_absolute()
        or ".." in path.parts
        or any(part in {"", "."} for part in path.parts)
        or path.as_posix() != value
    ):
        raise ValueError(f"{label} is unsafe")
    return path


def path_uses_symlink(root: Path, relative: Path) -> bool:
    candidate = root
    if candidate.is_symlink():
        return True
    for part in relative.parts:
        candidate /= part
        if candidate.is_symlink():
            return True
    return False


def load_overlay_manifest() -> dict[str, Any]:
    if OVERLAY_MANIFEST_PATH.is_symlink():
        raise ValueError("Explore OKF additive manifest must not be a symlink")
    if not OVERLAY_MANIFEST_PATH.is_file():
        raise ValueError("Explore OKF additive manifest is missing")
    value = json.loads(OVERLAY_MANIFEST_PATH.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Explore OKF additive manifest must be a mapping")
    return value


def base_entries_by_target(
    base: dict[str, Any], errors: list[str] | None = None
) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    files = base.get("files")
    if not isinstance(files, list):
        if errors is not None:
            errors.append("frozen Pages manifest files are malformed")
        return result
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            if errors is not None:
                errors.append(f"frozen Pages manifest file {index} is not a mapping")
            continue
        try:
            target = safe_relative_path(item.get("target"), f"base file {index} target")
        except ValueError as error:
            if errors is not None:
                errors.append(str(error))
            continue
        target_name = target.as_posix()
        if target_name in result:
            if errors is not None:
                errors.append(f"frozen Pages target is duplicated: {target_name}")
            continue
        result[target_name] = item
    return result


def validate_overlay(overlay: dict[str, Any], base: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if overlay.get("schema") != OVERLAY_SCHEMA:
        errors.append("Explore OKF additive manifest schema is unsupported")
    if overlay.get("publication_state") != "owner-authorised":
        errors.append("Explore OKF additive manifest must be owner-authorised")
    if overlay.get("release_grade") is not False:
        errors.append("Explore OKF additive publication must not be release grade")

    base_reference = overlay.get("base_manifest", {})
    if not isinstance(base_reference, dict):
        errors.append("Explore OKF base manifest reference is malformed")
        base_reference = {}
    if base_reference.get("path") != "publication/pages-file-manifest.json":
        errors.append("Explore OKF overlay base manifest path is unexpected")
    if base_reference.get("sha256") != EXPECTED_PAGES_MANIFEST_SHA256:
        errors.append("Explore OKF overlay does not bind the frozen base manifest")
    if base_reference.get("file_count") != base.get("file_count"):
        errors.append(
            "Explore OKF overlay base file count differs from the frozen publication"
        )

    base_by_target = base_entries_by_target(base, errors)
    base_index = base_by_target.get(REPLACEMENT_TARGET.as_posix())
    if base_index is None:
        errors.append("frozen Pages manifest does not contain index.html")
        base_index_sha256: object = None
    else:
        base_index_sha256 = base_index.get("sha256")
        if not is_sha256(base_index_sha256):
            errors.append("frozen Pages index.html SHA-256 is malformed")

    files = overlay.get("files")
    if not isinstance(files, list) or not files:
        return errors + ["Explore OKF overlay contains no files"]
    if (
        type(overlay.get("file_count")) is not int
        or overlay.get("file_count") != len(files)
    ):
        errors.append("Explore OKF overlay file count is inconsistent")

    observed_sources: set[str] = set()
    observed_targets: set[str] = set()
    observed_total = 0
    base_collisions: list[str] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            errors.append(f"Explore OKF overlay file {index} is not a mapping")
            continue
        try:
            source = safe_relative_path(
                item.get("source"), f"overlay file {index} source"
            )
            target = safe_relative_path(
                item.get("target"), f"overlay file {index} target"
            )
        except ValueError as error:
            errors.append(str(error))
            continue

        source_name = source.as_posix()
        target_name = target.as_posix()
        if source_name in observed_sources:
            errors.append(f"Explore OKF overlay source is duplicated: {source_name}")
        observed_sources.add(source_name)
        if target_name in observed_targets:
            errors.append(f"Explore OKF overlay target is duplicated: {target_name}")
        observed_targets.add(target_name)

        if source_name in MANIFEST_SOURCES:
            errors.append(
                "Explore OKF overlay must not publish a control manifest: "
                f"{source_name}"
            )
        if target_name in CONTROL_TARGETS:
            errors.append(f"Explore OKF overlay target is reserved: {target_name}")

        if target_name in base_by_target:
            base_collisions.append(target_name)
            if target != REPLACEMENT_TARGET:
                errors.append(
                    f"Explore OKF overlay would replace frozen target: {target_name}"
                )

        if target == REPLACEMENT_TARGET:
            if source != REPLACEMENT_SOURCE:
                errors.append(
                    "Explore OKF index.html replacement must come from "
                    f"{REPLACEMENT_SOURCE.as_posix()}"
                )
            replacement_digest = item.get("replaces_sha256")
            if not is_sha256(replacement_digest):
                errors.append("Explore OKF index.html replaces_sha256 is malformed")
            elif replacement_digest != base_index_sha256:
                errors.append(
                    "Explore OKF index.html does not bind the frozen target SHA-256"
                )
        else:
            if source != target and not is_allowed_core03_mapping(
                source_name, target_name
            ):
                errors.append(
                    "Explore OKF additive source and target differ: "
                    f"{source_name} -> {target_name}"
                )
            if "replaces_sha256" in item:
                errors.append(
                    "Explore OKF additive file declares an unexpected replacement: "
                    f"{target_name}"
                )

        digest = item.get("sha256")
        if not is_sha256(digest):
            errors.append(f"Explore OKF overlay SHA-256 is malformed: {source_name}")
        declared_size = item.get("bytes")
        if type(declared_size) is not int or declared_size < 0:
            errors.append(f"Explore OKF overlay byte count is malformed: {source_name}")

        source_path = ROOT / source
        if path_uses_symlink(ROOT, source):
            errors.append(
                f"Explore OKF overlay source must not use a symlink: {source_name}"
            )
            continue
        if not source_path.is_file():
            errors.append(f"Explore OKF overlay source is missing: {source_name}")
            continue
        size = source_path.stat().st_size
        observed_total += size
        if declared_size != size:
            errors.append(f"Explore OKF overlay byte count differs: {source_name}")
        if is_sha256(digest) and digest != sha256_path(source_path):
            errors.append(f"Explore OKF overlay SHA-256 differs: {source_name}")

    if base_collisions != [REPLACEMENT_TARGET.as_posix()]:
        errors.append(
            "Explore OKF overlay must replace exactly the frozen index.html target"
        )
    if (
        type(overlay.get("total_bytes")) is not int
        or overlay.get("total_bytes") != observed_total
    ):
        errors.append("Explore OKF overlay total byte count is inconsistent")
    errors.extend(validate_core03_closure(overlay, files, base_by_target))
    return errors


def copy_overlay(
    destination: Path, overlay: dict[str, Any], base: dict[str, Any]
) -> None:
    base_index = base_entries_by_target(base).get(REPLACEMENT_TARGET.as_posix())
    if base_index is None or not is_sha256(base_index.get("sha256")):
        raise ValueError("frozen Pages index.html identity is unavailable")

    replacement_items = [
        item
        for item in overlay["files"]
        if item["target"] == REPLACEMENT_TARGET.as_posix()
    ]
    if len(replacement_items) != 1:
        raise ValueError("Explore OKF overlay must contain one index.html replacement")
    additive_items = [
        item
        for item in overlay["files"]
        if item["target"] != REPLACEMENT_TARGET.as_posix()
    ]

    frozen_index = destination / REPLACEMENT_TARGET
    if frozen_index.is_symlink() or not frozen_index.is_file():
        raise ValueError("copied frozen index.html is missing or unsafe")
    if sha256_path(frozen_index) != base_index["sha256"]:
        raise ValueError("copied frozen index.html differs before replacement")

    for item in additive_items:
        source = ROOT / safe_relative_path(item["source"], "overlay source")
        target = destination / safe_relative_path(item["target"], "overlay target")
        if path_uses_symlink(ROOT, source.relative_to(ROOT)):
            raise ValueError(
                f"Explore OKF overlay source uses a symlink: {item['source']}"
            )
        if target.exists() or target.is_symlink():
            raise ValueError(
                f"Explore OKF additive target already exists: {item['target']}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if target.is_symlink() or sha256_path(target) != item["sha256"]:
            raise ValueError(f"copied Explore OKF file hash differs: {item['target']}")

    # Recheck immediately before the only permitted overwrite.
    if frozen_index.is_symlink() or sha256_path(frozen_index) != base_index["sha256"]:
        raise ValueError("copied frozen index.html differs before replacement")
    replacement = replacement_items[0]
    replacement_source = ROOT / safe_relative_path(
        replacement["source"], "overlay replacement source"
    )
    if path_uses_symlink(ROOT, replacement_source.relative_to(ROOT)):
        raise ValueError("Explore OKF index.html replacement source uses a symlink")
    shutil.copyfile(replacement_source, frozen_index)
    if frozen_index.is_symlink() or sha256_path(frozen_index) != replacement["sha256"]:
        raise ValueError("copied Explore OKF index.html replacement hash differs")

    if OVERLAY_MANIFEST_PATH.is_symlink():
        raise ValueError("Explore OKF additive manifest must not be a symlink")
    shutil.copyfile(
        OVERLAY_MANIFEST_PATH,
        destination / "explore-okf-publication-manifest.json",
    )


def published_content_targets(destination: Path) -> set[str]:
    return {
        relative
        for path in destination.rglob("*")
        if path.is_file()
        and (relative := path.relative_to(destination).as_posix())
        not in CONTROL_TARGETS
    }


def expected_content_targets(
    base: dict[str, Any], overlay: dict[str, Any]
) -> set[str]:
    return {
        str(item["target"])
        for item in [*base["files"], *overlay["files"]]
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args(argv)
    try:
        if args.check and args.destination:
            raise ValueError("--check and --destination cannot be combined")
        base = load_frozen_manifest()
        errors = validate_frozen_publication(base)
        overlay = load_overlay_manifest()
        errors.extend(validate_overlay(overlay, base))
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        if args.destination:
            destination = args.destination.resolve()
            allowed_destination = (ROOT / "_site").resolve()
            if destination != allowed_destination or (ROOT / "_site").is_symlink():
                raise ValueError(
                    f"publication destination must be {allowed_destination}"
                )
            copy_publication(destination, base)
            copy_overlay(destination, overlay, base)
            if published_content_targets(destination) != expected_content_targets(
                base, overlay
            ):
                raise ValueError(
                    "combined Pages artifact differs from the frozen base and "
                    "authorised overlay"
                )
            print(
                f"prepared {len(base['files']) - 1} unchanged frozen files, "
                "1 authorised landing-page replacement and "
                f"{len(overlay['files']) - 1} additive Explore OKF files"
            )
            return 0
        print(
            "Explore OKF overlay passed: "
            f"{len(base['files']) - 1} frozen targets unchanged, "
            "1 authorised landing-page replacement and "
            f"{len(overlay['files']) - 1} additive files"
        )
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
