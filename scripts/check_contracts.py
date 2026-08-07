#!/usr/bin/env python3
"""Validate the domain-profile handoff and vertical-slice fixture contracts."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "profiles" / "okf-domain-profile.v1.yaml"
FIXTURE_DIR = ROOT / "evaluation" / "fixtures"
EXPECTED_FIXTURE_IDS = {
    "missed-rubbish-collection",
    "learning-to-drive-speeding",
    "death-bereavement-estate",
}
REQUIRED_PROFILE_SECTIONS = {
    "approval",
    "collection",
    "users",
    "tasks",
    "authority",
    "terminology",
    "semantic_model",
    "standards",
    "rights",
    "privacy",
    "assertion_policy",
    "jurisdictions",
    "freshness",
    "validation",
    "constraints",
    "gaps",
    "decisions",
    "evidence",
    "consumer_lock",
    "dependency_graph",
}
REQUIRED_DIMENSIONS = {
    "ordinary_path",
    "exception_path",
    "evidence",
    "rule",
    "time",
    "jurisdiction",
    "authority",
    "private_sector_dependencies",
    "redress",
    "provenance",
}
ALLOWED_ASSERTION_STATUSES = {
    "official",
    "normalized",
    "inferred",
    "editorial-example",
}
REQUIRED_STEP_FIELDS = {
    "id",
    "interaction",
    "provider_role",
    "evidence",
    "rule",
    "time",
    "outcome",
    "redress",
    "assertion_status",
}


def _nonempty(value: Any) -> bool:
    if isinstance(value, str):
        return bool(value.strip())
    return bool(value)


def _load_mapping(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{path.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def load_contracts() -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    profile, errors = _load_mapping(PROFILE_PATH)
    fixtures: list[dict[str, Any]] = []
    for path in sorted(FIXTURE_DIR.glob("*.v1.yaml")):
        fixture, fixture_errors = _load_mapping(path)
        errors.extend(fixture_errors)
        if fixture:
            fixture["_path"] = path.relative_to(ROOT).as_posix()
            fixtures.append(fixture)
    return profile, fixtures, errors


def _assertion_statuses(value: Any, path: str = "") -> Iterator[tuple[str, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else str(key)
            if key == "assertion_status":
                yield child_path, child
            yield from _assertion_statuses(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _assertion_statuses(child, f"{path}[{index}]")


def validate_profile(profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = PROFILE_PATH.relative_to(ROOT).as_posix()
    if profile.get("profile_version") != "okf-domain-profile.v1":
        errors.append(f"{prefix}: profile_version must be okf-domain-profile.v1")
    if profile.get("status") != "approved":
        errors.append(f"{prefix}: status must record owner approval")
    missing = sorted(section for section in REQUIRED_PROFILE_SECTIONS if not _nonempty(profile.get(section)))
    if missing:
        errors.append(f"{prefix}: missing non-empty sections: {', '.join(missing)}")

    approval = profile.get("approval", {})
    if not isinstance(approval, dict) or approval.get("state") != "approved":
        errors.append(f"{prefix}: approval.state must be approved")
    for field in ("approved_by", "approved_at", "authorized_actions"):
        if not isinstance(approval, dict) or not _nonempty(approval.get(field)):
            errors.append(f"{prefix}: approval.{field} must be non-empty")
    blocked = set(approval.get("blocked_actions", [])) if isinstance(approval, dict) else set()
    for action in ("broad_source_acquisition", "public_bundle_publication"):
        if action not in blocked:
            errors.append(f"{prefix}: approval must block {action}")

    rights = profile.get("rights", {})
    if not isinstance(rights, dict) or rights.get("publication_allowed") is not False:
        errors.append(f"{prefix}: rights.publication_allowed must be false")
    if not isinstance(rights, dict) or rights.get("redistribution_allowed") is not False:
        errors.append(f"{prefix}: rights.redistribution_allowed must be false")

    privacy = profile.get("privacy", {})
    if not isinstance(privacy, dict) or privacy.get("real_personal_data_allowed") is not False:
        errors.append(f"{prefix}: real personal data must be disallowed")
    if not isinstance(privacy, dict) or privacy.get("synthetic_personas_required") is not True:
        errors.append(f"{prefix}: synthetic personas must be required")

    policy = profile.get("assertion_policy", {})
    statuses = policy.get("statuses", {}) if isinstance(policy, dict) else {}
    if set(statuses) != ALLOWED_ASSERTION_STATUSES:
        errors.append(f"{prefix}: assertion_policy.statuses must declare the four governed statuses")

    jurisdictions = profile.get("jurisdictions", {})
    required_jurisdictions = set(jurisdictions.get("required", [])) if isinstance(jurisdictions, dict) else set()
    expected_jurisdictions = {"uk-wide", "england", "scotland", "wales", "northern-ireland", "local"}
    if required_jurisdictions != expected_jurisdictions:
        errors.append(f"{prefix}: jurisdictions.required must declare UK-wide, four nations and local")

    validation = profile.get("validation", {})
    commands = validation.get("required_commands", []) if isinstance(validation, dict) else []
    if not any("scripts/check_contracts.py" in str(command) for command in commands):
        errors.append(f"{prefix}: validation commands must include scripts/check_contracts.py")
    if not isinstance(validation, dict) or validation.get("local_only_until_publication_request") is not True:
        errors.append(f"{prefix}: validation must retain the local-only publication boundary")

    consumer = profile.get("consumer_lock", {})
    for field in ("schema", "okf_version", "corpus_id", "root", "bundle", "invariants", "status"):
        if not isinstance(consumer, dict) or not _nonempty(consumer.get(field)):
            errors.append(f"{prefix}: consumer_lock.{field} must be non-empty")

    graph = profile.get("dependency_graph", {})
    nodes = set(graph.get("nodes", [])) if isinstance(graph, dict) else set()
    edges = graph.get("edges", []) if isinstance(graph, dict) else []
    if not nodes or not isinstance(edges, list) or not edges:
        errors.append(f"{prefix}: dependency_graph must contain nodes and edges")
    else:
        for index, edge in enumerate(edges):
            if not isinstance(edge, dict) or not {"from", "to", "kind"} <= set(edge):
                errors.append(f"{prefix}: dependency_graph.edges[{index}] is incomplete")
                continue
            if edge["from"] not in nodes or edge["to"] not in nodes:
                errors.append(f"{prefix}: dependency_graph.edges[{index}] references an unknown node")
    return errors


def validate_fixture(fixture: dict[str, Any], profile: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = str(fixture.get("_path", "fixture"))
    required_top_level = {
        "fixture_version",
        "id",
        "title",
        "status",
        "assertion_status",
        "profile",
        "synthetic",
        "approval",
        "purpose",
        "scope",
        "dimensions",
        "jurisdictions",
        "actors",
        "journeys",
        "private_sector_dependencies",
        "redress",
        "source_requirements",
        "known_unknowns",
        "competency_questions",
        "acceptance",
    }
    missing = sorted(field for field in required_top_level if not _nonempty(fixture.get(field)))
    if missing:
        errors.append(f"{prefix}: missing non-empty fields: {', '.join(missing)}")
    if fixture.get("fixture_version") != "vertical-slice-fixture.v1":
        errors.append(f"{prefix}: fixture_version must be vertical-slice-fixture.v1")
    if fixture.get("profile") != profile.get("profile_version"):
        errors.append(f"{prefix}: profile must reference {profile.get('profile_version')}")
    if fixture.get("status") != "approved":
        errors.append(f"{prefix}: status must record owner approval")
    if fixture.get("assertion_status") != "editorial-example":
        errors.append(f"{prefix}: contract itself must be editorial-example")
    if fixture.get("synthetic") is not True:
        errors.append(f"{prefix}: synthetic must be true")
    fixture_approval = fixture.get("approval", {})
    if not isinstance(fixture_approval, dict) or fixture_approval.get("state") != "approved":
        errors.append(f"{prefix}: approval.state must be approved")
    for field in ("approved_by", "approved_at"):
        if not isinstance(fixture_approval, dict) or not _nonempty(fixture_approval.get(field)):
            errors.append(f"{prefix}: approval.{field} must be non-empty")

    dimensions = set(fixture.get("dimensions", []))
    missing_dimensions = sorted(REQUIRED_DIMENSIONS - dimensions)
    if missing_dimensions:
        errors.append(f"{prefix}: missing dimensions: {', '.join(missing_dimensions)}")

    profile_jurisdiction_data = profile.get("jurisdictions", {})
    profile_jurisdictions = set(
        profile_jurisdiction_data.get("required", []) if isinstance(profile_jurisdiction_data, dict) else []
    )
    fixture_jurisdictions = fixture.get("jurisdictions", [])
    if not isinstance(fixture_jurisdictions, list):
        errors.append(f"{prefix}: jurisdictions must be a list")
        fixture_jurisdictions = []
    jurisdiction_ids = {
        item.get("id") for item in fixture_jurisdictions if isinstance(item, dict) and _nonempty(item.get("id"))
    }
    if not jurisdiction_ids or not jurisdiction_ids <= profile_jurisdictions:
        errors.append(f"{prefix}: jurisdiction identifiers must be a non-empty subset of the profile")
    for index, item in enumerate(fixture_jurisdictions):
        if not isinstance(item, dict) or not _nonempty(item.get("expectation")):
            errors.append(f"{prefix}: jurisdictions[{index}] must declare an expectation")

    journeys = fixture.get("journeys", {})
    for path_name in ("ordinary", "exception"):
        path = journeys.get(path_name, {}) if isinstance(journeys, dict) else {}
        if not isinstance(path, dict):
            errors.append(f"{prefix}: journeys.{path_name} must be a mapping")
            continue
        for field in ("entry_state", "outcome", "steps"):
            if not _nonempty(path.get(field)):
                errors.append(f"{prefix}: journeys.{path_name}.{field} must be non-empty")
        steps = path.get("steps", [])
        if isinstance(steps, list):
            for index, step in enumerate(steps):
                if not isinstance(step, dict):
                    errors.append(f"{prefix}: journeys.{path_name}.steps[{index}] must be a mapping")
                    continue
                step_missing = sorted(field for field in REQUIRED_STEP_FIELDS if not _nonempty(step.get(field)))
                if step_missing:
                    errors.append(
                        f"{prefix}: journeys.{path_name}.steps[{index}] missing: {', '.join(step_missing)}"
                    )

    source_requirements_value = fixture.get("source_requirements", {})
    source_requirements = source_requirements_value if isinstance(source_requirements_value, dict) else {}
    allowed_acquisition_statuses = {"authorized_not_started", "linked_references_registered"}
    if source_requirements.get("acquisition_status") not in allowed_acquisition_statuses:
        errors.append(f"{prefix}: source acquisition status is not governed")
    for field in ("required_fields", "candidate_families"):
        if not _nonempty(source_requirements.get(field)):
            errors.append(f"{prefix}: source_requirements.{field} must be non-empty")

    questions = fixture.get("competency_questions", [])
    if not isinstance(questions, list) or len(questions) < 3:
        errors.append(f"{prefix}: at least three competency questions are required")
    else:
        for index, question in enumerate(questions):
            if not isinstance(question, dict) or any(not _nonempty(question.get(field)) for field in ("id", "question", "expected")):
                errors.append(f"{prefix}: competency_questions[{index}] is incomplete")

    for status_path, status in _assertion_statuses(fixture):
        if status not in ALLOWED_ASSERTION_STATUSES:
            errors.append(f"{prefix}: {status_path} has unsupported status {status!r}")
        if status == "official" and source_requirements.get("acquisition_status") != "linked_references_registered":
            errors.append(f"{prefix}: {status_path} cannot be official before source acquisition")
    return errors


def validate_contracts() -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    profile, fixtures, errors = load_contracts()
    errors.extend(validate_profile(profile))
    ids = [str(fixture.get("id", "")) for fixture in fixtures]
    if len(ids) != len(set(ids)):
        errors.append("evaluation/fixtures: duplicate fixture id")
    if set(ids) != EXPECTED_FIXTURE_IDS:
        missing = sorted(EXPECTED_FIXTURE_IDS - set(ids))
        unexpected = sorted(set(ids) - EXPECTED_FIXTURE_IDS)
        if missing:
            errors.append(f"evaluation/fixtures: missing fixtures: {', '.join(missing)}")
        if unexpected:
            errors.append(f"evaluation/fixtures: unexpected fixtures: {', '.join(unexpected)}")
    for fixture in fixtures:
        errors.extend(validate_fixture(fixture, profile))
    return profile, fixtures, sorted(set(errors))


def main() -> int:
    profile, fixtures, errors = validate_contracts()
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"Contract checks passed: {profile['profile_version']} and {len(fixtures)} fixture contracts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
