#!/usr/bin/env python3
"""Require documentation and changelog updates for publication-controlled changes."""

from __future__ import annotations

import argparse
import fnmatch
import json
import subprocess
import sys
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = Path("okf.publication.json")


def path_matches(path: str, pattern: str) -> bool:
    """Match repository paths with segment-aware ``*`` and recursive ``**``."""

    if pattern.endswith("/"):
        return path.startswith(pattern)
    path_parts = path.split("/")
    pattern_parts = pattern.split("/")

    def match(path_index: int, pattern_index: int) -> bool:
        if pattern_index == len(pattern_parts):
            return path_index == len(path_parts)
        component = pattern_parts[pattern_index]
        if component == "**":
            return match(path_index, pattern_index + 1) or (
                path_index < len(path_parts)
                and match(path_index + 1, pattern_index)
            )
        return (
            path_index < len(path_parts)
            and fnmatch.fnmatchcase(path_parts[path_index], component)
            and match(path_index + 1, pattern_index + 1)
        )

    return match(0, 0)


def matches_any(path: str, patterns: Iterable[str]) -> bool:
    return any(path_matches(path, pattern) for pattern in patterns)


def git_paths(root: Path, arguments: list[str]) -> set[str]:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line.strip() for line in result.stdout.splitlines() if line.strip()}


def changed_paths(root: Path, base: str | None) -> set[str]:
    if base:
        return git_paths(root, ["diff", "--name-only", base])
    result = git_paths(root, ["diff", "--name-only"])
    result.update(git_paths(root, ["diff", "--cached", "--name-only"]))
    result.update(git_paths(root, ["ls-files", "--others", "--exclude-standard"]))
    return result


def lockstep_errors(
    contract: Mapping[str, Any], changed: Iterable[str]
) -> tuple[list[str], list[str], list[str]]:
    files = set(changed)
    policy = contract["lockstep"]
    controlled = sorted(
        path for path in files if matches_any(path, policy["controlled_paths"])
    )
    if not controlled:
        return [], [], []

    documentation = sorted(
        path for path in files if matches_any(path, policy["documentation_paths"])
    )
    errors: list[str] = []
    if not documentation:
        errors.append(
            "controlled publication files changed without a declared documentation change"
        )
    changelog = policy["changelog_path"]
    if changelog not in files:
        errors.append(f"controlled publication files changed without {changelog}")
    return errors, controlled, documentation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--base",
        help="git revision or range to compare, for example origin/main...HEAD",
    )
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--contract", type=Path, default=CONTRACT_PATH)
    args = parser.parse_args()
    root = args.root.resolve()
    contract_path = args.contract
    if not contract_path.is_absolute():
        contract_path = root / contract_path

    try:
        contract = json.loads(contract_path.read_text(encoding="utf-8"))
        errors, controlled, documentation = lockstep_errors(
            contract, changed_paths(root, args.base)
        )
    except (
        OSError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"documentation lockstep could not be evaluated: {error}", file=sys.stderr)
        return 2

    if not controlled:
        print("documentation lockstep: no controlled publication files changed")
        return 0
    if errors:
        print("documentation lockstep failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "documentation lockstep passed: "
        f"{len(controlled)} controlled file(s), "
        f"{len(documentation)} documentation file(s), changelog updated"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
