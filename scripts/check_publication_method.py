#!/usr/bin/env python3
"""Check the repository-specific OKF publication policy without publishing."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "okf.publication.json"
ACTIVE_WORKFLOW = Path(".github/workflows/pages-explore-okf.yml")
RETIRED_WORKFLOW = Path(".github/workflows/pages.yml")


def indexed(
    items: Sequence[Mapping[str, Any]], label: str, errors: list[str]
) -> dict[str, Mapping[str, Any]]:
    result: dict[str, Mapping[str, Any]] = {}
    for item in items:
        identifier = item.get("id")
        if not isinstance(identifier, str) or not identifier:
            errors.append(f"{label} has no identifier")
            continue
        if identifier in result:
            errors.append(f"duplicate {label} identifier: {identifier}")
        result[identifier] = item
    return result


def require_references(
    values: Sequence[str], available: Mapping[str, Any], label: str, errors: list[str]
) -> None:
    for value in values:
        if value not in available:
            errors.append(f"{label} references unknown identifier: {value}")


def workflow_errors(root: Path) -> list[str]:
    errors: list[str] = []
    active = (root / ACTIVE_WORKFLOW).read_text(encoding="utf-8")
    retired = (root / RETIRED_WORKFLOW).read_text(encoding="utf-8")

    if "workflow_dispatch:" not in active:
        errors.append("active Pages workflow is not manual")
    for trigger in ("\n  push:", "\n  pull_request:", "\n  schedule:"):
        if trigger in active:
            errors.append(f"active Pages workflow has a prohibited trigger: {trigger.strip()}")
    if "cancel-in-progress: false" not in active:
        errors.append("active publication concurrency must never cancel an in-flight deployment")
    if "group: okf-uk-living-pages-publication" not in active:
        errors.append("active publication workflow must use its repository-specific serial group")
    if not re.search(r"package:\s.*?timeout-minutes: 15", active, re.DOTALL):
        errors.append("active package job must have a 15-minute timeout")
    if not re.search(r"deploy:\s.*?timeout-minutes: 10", active, re.DOTALL):
        errors.append("active deploy job must have a 10-minute timeout")
    if "on: {}" not in retired or "workflow_dispatch:" in retired:
        errors.append("retired base workflow must remain disabled")
    if "cancel-in-progress: false" not in retired:
        errors.append("retired publication workflow must retain non-cancelling serialisation")
    if "group: okf-uk-living-pages-publication" not in retired:
        errors.append("retired workflow must share the publication serial group")
    return errors


def publication_method_errors(contract: Mapping[str, Any], root: Path) -> list[str]:
    errors: list[str] = []
    required = {
        "schema",
        "modified",
        "locale",
        "time_zone",
        "repository",
        "semantic_contract",
        "source_families",
        "boundaries",
        "planes",
        "tooling",
        "lockstep",
        "ci",
        "publication",
        "verification",
        "limitations",
    }
    missing = sorted(required.difference(contract))
    if missing:
        errors.append("publication contract is missing: " + ", ".join(missing))
        return errors

    if contract["schema"] != "okf-repository-publication-contract.v1":
        errors.append("publication contract schema identifier is unexpected")
    if contract["repository"].get("name") != "okf-uk-living":
        errors.append("publication contract names a different repository")
    if contract["semantic_contract"].get("path") != "okf.semantic.json":
        errors.append("publication contract is detached from okf.semantic.json")

    commands = indexed(contract["tooling"]["commands"], "command", errors)
    planes = indexed(contract["planes"], "plane", errors)
    families = indexed(contract["source_families"], "source family", errors)
    for plane_id, plane in planes.items():
        require_references(plane["depends_on"], planes, f"plane {plane_id}", errors)
        require_references(plane["command_ids"], commands, f"plane {plane_id}", errors)
    for family_id, family in families.items():
        require_references(
            family["invalidates"], planes, f"source family {family_id}", errors
        )
        require_references(
            family["extraction"]["command_ids"],
            commands,
            f"source family {family_id}",
            errors,
        )

    governance = families.get("review-and-publication-governance")
    if governance and {"semantic", "runtime", "release"}.intersection(
        governance["invalidates"]
    ):
        errors.append(
            "documentation governance must not invalidate the frozen corpus or release"
        )
    for command_id, command in commands.items():
        source = root / command["source"]
        if not source.is_file():
            errors.append(f"command {command_id} has no reviewed source file: {command['source']}")
        require_references(command["planes"], planes, f"command {command_id}", errors)

    for command_id in ("build-large-corpus", "build-population-assurance"):
        command = commands.get(command_id)
        if command and "documentation" in command["planes"]:
            errors.append(f"{command_id} must not run for documentation-only changes")
    release = planes.get("release")
    if release and {"documentation", "application"}.intersection(
        release["depends_on"]
    ):
        errors.append("frozen release must not depend on the additive documentation overlay")

    policy = contract["publication"]
    if policy.get("mode") != "manual":
        errors.append("publication must remain manual")
    if policy.get("candidate_policy") != "promote-exact-assured-bytes-without-rebuild":
        errors.append("publication must promote exact assured bytes without rebuilding")
    for target in policy.get("targets", []):
        if target.get("exact_commit_required") is not True:
            errors.append("each publication target must require the exact commit")
        if target.get("promote_without_rebuild") is not True:
            errors.append("each publication target must prohibit deployment rebuilds")

    ci = contract["ci"]
    if ci.get("impact_routing") != "not-applicable" or ci.get("parallelism") != "serial":
        errors.append("remote CI must remain a serial manual publication route only")
    browser = ci.get("browser", {}).get("ordinary", {})
    if browser.get("policy") != "installed-chrome":
        errors.append("ordinary live acceptance must use installed Chrome")
    if contract["verification"].get("required") is not True:
        errors.append("live verification may not be made optional")

    gap = "post-deploy exact-head browser receipt"
    if not any(gap in limitation for limitation in contract["limitations"]):
        errors.append("the current automated browser-receipt gap is not explicit")

    tracked = subprocess.run(
        ["git", "ls-files", "-z"], cwd=root, check=True, capture_output=True
    ).stdout.split(b"\0")
    for raw_path in tracked:
        path = raw_path.decode("utf-8", errors="strict")
        if path == ".DS_Store" or path.endswith("/.DS_Store") or path.startswith("_site/"):
            errors.append(f"prohibited tracked publication residue: {path}")
    errors.extend(workflow_errors(root))
    return errors


def main() -> int:
    try:
        contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        errors = publication_method_errors(contract, ROOT)
    except (
        OSError,
        KeyError,
        TypeError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as error:
        print(f"publication method could not be checked: {error}", file=sys.stderr)
        return 2
    if errors:
        print("publication method failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "publication method passed: manual exact-byte deployment, local-only "
        "assurance and explicit live-browser gate"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
