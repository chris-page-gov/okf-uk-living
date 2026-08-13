#!/usr/bin/env python3
"""Freeze, verify and copy the exact GitHub Pages publication unit."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "publication" / "pages-file-manifest.json"
CANDIDATE_MANIFEST_PATH = ROOT / "generated" / "assurance" / "candidate-manifest.json"
PUBLIC_DESCRIPTOR_PATH = ROOT / "publication" / "okf-explorer.json"
LOCAL_DESCRIPTOR_PATH = ROOT / "okf-explorer.json"
EXPECTED_CANDIDATE_ID = "life-course-population-complete-2026-08-08"
EXPECTED_CANDIDATE_MANIFEST_SHA256 = "55f8428248b06646e0995f5230207c9006bf4d583d29157fb010ad7e69e416a1"
EXPECTED_PUBLIC_BASE = "https://chris-page-gov.github.io/okf-uk-living/"
PUBLICATION_DATA_COMMIT = "c38f927944dedc56b6454dba4d4463d419f85ee8"
EXPECTED_PAGES_MANIFEST_SHA256 = "1a43f5fa0b8a4c4d3489891dce27f711d3f370f3dcca7ae7b6d4f5ec22249ee7"


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_file_bytes(commit: str, path: Path) -> bytes:
    completed = subprocess.run(
        ["git", "show", f"{commit}:{path.as_posix()}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return completed.stdout


def load_frozen_manifest() -> dict[str, Any]:
    content = MANIFEST_PATH.read_bytes()
    if hashlib.sha256(content).hexdigest() != EXPECTED_PAGES_MANIFEST_SHA256:
        raise ValueError("frozen Pages manifest hash is unexpected")
    return json.loads(content)


def validate_frozen_publication(manifest: dict[str, Any]) -> list[str]:
    errors = descriptor_errors(frozen=True)
    if not MANIFEST_PATH.is_file():
        return ["publication/pages-file-manifest.json is missing"]
    current = MANIFEST_PATH.read_bytes()
    if hashlib.sha256(current).hexdigest() != EXPECTED_PAGES_MANIFEST_SHA256:
        errors.append("tracked Pages manifest differs from the owner-authorised manifest")
    if json.loads(current) != manifest:
        errors.append("tracked Pages manifest differs from the loaded frozen manifest")
    if manifest.get("publication_data_commit") != PUBLICATION_DATA_COMMIT:
        errors.append("frozen Pages manifest has an unexpected publication data commit")
    if manifest.get("file_count") != len(manifest.get("files", [])):
        errors.append("frozen Pages manifest file count is inconsistent")
    targets = [str(item.get("target", "")) for item in manifest.get("files", [])]
    if len(targets) != len(set(targets)):
        errors.append("frozen Pages manifest targets are not unique")
    if any(Path(target).is_absolute() or ".." in Path(target).parts for target in targets):
        errors.append("frozen Pages manifest contains an unsafe target")
    if any("snapshot" in str(item.get("source", "")).lower() for item in manifest.get("files", [])):
        errors.append("frozen Pages manifest must not contain source snapshots")
    expected = build_manifest()
    if manifest != expected:
        errors.append("frozen Pages manifest does not match the current publication sources")
    changed = subprocess.run(
        ["git", "diff", "--name-only", PUBLICATION_DATA_COMMIT, "--"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    publication_sources = {str(item.get("source", "")) for item in manifest.get("files", [])}
    permitted_transport_changes = {
        "generated/browser/CHANGELOG.html",
        "generated/browser/PLANNING.html",
        "generated/browser/README.html",
        "generated/browser/REPOSITORY_STATUS.html",
        "generated/browser/ROADMAP.html",
        "generated/browser/TRACKING.html",
        "publication/okf-explorer.json",
    }
    drift = sorted((set(changed) & publication_sources) - permitted_transport_changes)
    if drift:
        errors.append(
            "publication sources differ from the pinned rich-runtime data commit: "
            + ", ".join(drift)
        )
    return errors


def publication_files() -> list[tuple[Path, Path]]:
    fixed = [
        (ROOT / "publication" / "index.html", Path("index.html")),
        (PUBLIC_DESCRIPTOR_PATH, Path("okf-explorer.json")),
        (ROOT / "okf-bundle.json", Path("okf-bundle.json")),
        (ROOT / "LICENSE", Path("LICENSE")),
        (ROOT / "NOTICE.md", Path("NOTICE.md")),
    ]
    trees = [
        ROOT / "large" / "data",
        ROOT / "generated" / "browser",
        ROOT / "generated" / "semantic",
        ROOT / "generated" / "assurance",
    ]
    files = list(fixed)
    for tree in trees:
        for path in sorted(tree.rglob("*")):
            if path.is_file() and path.name != ".DS_Store":
                files.append((path, path.relative_to(ROOT)))
    targets = [target.as_posix() for _, target in files]
    if len(targets) != len(set(targets)):
        raise ValueError("publication targets must be unique")
    return files


def descriptor_errors(*, frozen: bool = False) -> list[str]:
    errors: list[str] = []
    if frozen:
        local_bytes = git_file_bytes(PUBLICATION_DATA_COMMIT, Path("okf-explorer.json"))
        public_bytes = PUBLIC_DESCRIPTOR_PATH.read_bytes()
        candidate_bytes = git_file_bytes(
            PUBLICATION_DATA_COMMIT, Path("generated/assurance/candidate-manifest.json")
        )
    else:
        local_bytes = LOCAL_DESCRIPTOR_PATH.read_bytes()
        public_bytes = PUBLIC_DESCRIPTOR_PATH.read_bytes()
        candidate_bytes = CANDIDATE_MANIFEST_PATH.read_bytes()
    local = json.loads(local_bytes)
    public = json.loads(public_bytes)
    candidate = json.loads(candidate_bytes)
    if hashlib.sha256(candidate_bytes).hexdigest() != EXPECTED_CANDIDATE_MANIFEST_SHA256:
        errors.append("candidate manifest hash differs from the owner-authorised candidate")
    if candidate.get("candidate_id") != EXPECTED_CANDIDATE_ID:
        errors.append("candidate manifest identity is unexpected")
    if candidate.get("gates", {}).get("population_complete") is not True:
        errors.append("candidate must be population-complete")
    if candidate.get("gates", {}).get("release_grade") is not False:
        errors.append("publication must retain the non-release-grade boundary")
    if candidate.get("source_snapshots_acquired") is not False:
        errors.append("publication candidate must contain no source snapshots")

    comparable_public = json.loads(json.dumps(public))
    comparable_public.pop("publication", None)
    comparable_public["description"] = local.get("description")
    comparable_public["status"] = local.get("status")
    comparable_public.setdefault("source", {})["publication_authorized"] = False
    if comparable_public != local:
        errors.append("public descriptor changes fields outside the authorised publication envelope")

    publication = public.get("publication", {})
    expected_publication = {
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "candidate_manifest_sha256": EXPECTED_CANDIDATE_MANIFEST_SHA256,
        "kind": "population-complete-preview",
        "publication_url": EXPECTED_PUBLIC_BASE + "okf-explorer.json",
        "release_grade": False,
        "specialist_review_required": 291,
    }
    for field, expected in expected_publication.items():
        if publication.get(field) != expected:
            errors.append(f"publication.{field} must be {expected!r}")
    if public.get("source", {}).get("publication_authorized") is not True:
        errors.append("public descriptor must record owner publication authorisation")
    if public.get("source", {}).get("source_snapshots") is not False:
        errors.append("public descriptor must retain zero source snapshots")
    return errors


def build_manifest() -> dict[str, Any]:
    entries = []
    for source, target in publication_files():
        if not source.is_file():
            raise ValueError(f"publication source is missing: {source.relative_to(ROOT)}")
        entries.append({
            "bytes": source.stat().st_size,
            "sha256": sha256_path(source),
            "source": source.relative_to(ROOT).as_posix(),
            "target": target.as_posix(),
        })
    return {
        "schema": "life-course-pages-publication-manifest.v1",
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "candidate_manifest_sha256": EXPECTED_CANDIDATE_MANIFEST_SHA256,
        "publication_data_commit": PUBLICATION_DATA_COMMIT,
        "publication_kind": "population-complete-preview",
        "publication_authorized_at": "2026-08-08T22:40:40+01:00",
        "public_base_url": EXPECTED_PUBLIC_BASE,
        "explorer_url": (
            "https://chris-page-gov.github.io/okf-explorer/"
            "?bundle=https%3A%2F%2Fchris-page-gov.github.io%2F"
            "okf-uk-living%2Fokf-explorer.json#overview"
        ),
        "release_grade": False,
        "source_snapshots_acquired": False,
        "source_response_bodies_retained": False,
        "file_count": len(entries),
        "total_bytes": sum(item["bytes"] for item in entries),
        "files": entries,
    }


def validate_manifest(expected: dict[str, Any]) -> list[str]:
    errors = descriptor_errors()
    if not MANIFEST_PATH.is_file():
        return errors + ["publication/pages-file-manifest.json is missing"]
    try:
        actual = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return errors + [f"publication manifest cannot be read: {error}"]
    if actual != expected:
        errors.append("publication/pages-file-manifest.json is stale")
    if any("snapshot" in item["source"].lower() for item in expected["files"]):
        errors.append("publication file set must not include source snapshots")
    return errors


def remove_output_tree(root: Path) -> None:
    if not root.exists():
        return
    for attempt in range(3):
        try:
            shutil.rmtree(root)
            return
        except OSError:
            finder_metadata = list(root.rglob(".DS_Store")) if root.exists() else []
            if not finder_metadata or attempt == 2:
                raise
            for path in finder_metadata:
                path.unlink(missing_ok=True)


def copy_publication(destination: Path, manifest: dict[str, Any]) -> None:
    allowed_destination = (ROOT / "_site").resolve()
    if destination.resolve() != allowed_destination:
        raise ValueError(f"publication destination must be {allowed_destination}")
    remove_output_tree(destination)
    destination.mkdir(parents=True)
    for item in manifest["files"]:
        source = ROOT / item["source"]
        target = destination / item["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if sha256_path(target) != item["sha256"]:
            raise ValueError(f"copied file hash mismatch: {item['target']}")
    shutil.copyfile(MANIFEST_PATH, destination / "publication-manifest.json")
    (destination / ".nojekyll").write_bytes(b"")
    actual_targets = {
        path.relative_to(destination).as_posix()
        for path in destination.rglob("*")
        if path.is_file() and path.name not in {".nojekyll", "publication-manifest.json"}
    }
    expected_targets = {item["target"] for item in manifest["files"]}
    if actual_targets != expected_targets:
        raise ValueError("deployed file set does not match the frozen manifest")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument(
        "--frozen",
        action="store_true",
        help="verify the exact owner-authorised manifest from the pinned publication commit",
    )
    parser.add_argument("--destination", type=Path)
    args = parser.parse_args()
    try:
        if args.write_manifest and args.destination:
            raise ValueError("--write-manifest and --destination cannot be combined")
        if args.frozen:
            if args.write_manifest or args.destination:
                raise ValueError("--frozen is verification-only")
            manifest = load_frozen_manifest()
            errors = validate_frozen_publication(manifest)
            if errors:
                for error in errors:
                    print(error)
                return 1
            print(
                f"Frozen Pages publication passed: data_commit={PUBLICATION_DATA_COMMIT} "
                f"files={manifest['file_count']} bytes={manifest['total_bytes']}"
            )
            return 0
        if args.destination:
            manifest = load_frozen_manifest()
            errors = validate_frozen_publication(manifest)
            if errors:
                for error in errors:
                    print(error)
                return 1
            copy_publication(args.destination.resolve(), manifest)
            print(
                f"prepared {manifest['file_count']} frozen Pages files "
                f"({manifest['total_bytes']} bytes)"
            )
            return 0
        manifest = build_manifest()
        if args.write_manifest:
            MANIFEST_PATH.write_text(json_text(manifest), encoding="utf-8")
        errors = validate_manifest(manifest)
        if errors:
            for error in errors:
                print(error)
            return 1
        print(
            f"Pages publication manifest passed: {manifest['file_count']} files, "
            "population preview, release grade false, 0 snapshots"
        )
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(error)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
