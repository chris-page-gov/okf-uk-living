#!/usr/bin/env python3
"""Prove that a proposed fast-path change is confined to site documentation."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from build_okf_bundle import ROOT
from site_document_publications import (
    DOCUMENT_MANIFEST_PATH,
    build_site_document_outputs,
)


GENERATED_CONTROL_PATHS = {
    DOCUMENT_MANIFEST_PATH,
    Path("publication/explore-okf-file-manifest.json"),
}


def changed_paths(base_ref: str) -> list[Path]:
    command = ["git", "diff", "--name-only", "--diff-filter=ACMRT", f"{base_ref}...HEAD"]
    result = subprocess.run(
        command,
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [Path(line) for line in result.stdout.splitlines() if line]


def documentation_only_errors(paths: list[Path]) -> list[str]:
    _, mapping, _ = build_site_document_outputs(ROOT)
    allowed = set(mapping) | set(mapping.values()) | GENERATED_CONTROL_PATHS
    errors: list[str] = []
    for path in paths:
        if path not in allowed:
            errors.append(
                f"{path.as_posix()} is outside the documentation publication dependency graph"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-ref", default="origin/main")
    args = parser.parse_args(argv)
    try:
        paths = changed_paths(args.base_ref)
        errors = documentation_only_errors(paths)
    except (OSError, subprocess.CalledProcessError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    if not paths:
        print("Documentation-only gate found no changed paths")
        return 0
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        print(
            "Use the repository's full validation path for this change.",
            file=sys.stderr,
        )
        return 1
    print(
        f"Documentation-only dependency graph passed: {len(paths)} changed paths; "
        "corpus and semantic inputs are outside the change"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
