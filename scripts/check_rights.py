#!/usr/bin/env python3
"""Validate repository and source-family licensing decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from check_sources import RECORDED_RIGHTS_BASIS, load_source_registers
from check_inventory import flatten_inventory_references, load_reference_inventory


ROOT = Path(__file__).resolve().parents[1]
RIGHTS_PATH = ROOT / "source" / "rights-decisions.v1.yaml"
LICENSE_PATH = ROOT / "LICENSE"
NOTICE_PATH = ROOT / "NOTICE.md"
EXPECTED_OGL_ATTRIBUTION = (
    "Contains public sector information licensed under the Open Government Licence v3.0."
)
EXPECTED_STANDARD_LICENCES = {
    "cpsv-ap-3.2.0": "CC-BY-4.0",
    "open-referral-uk-website": "OGL-version-not-expressly-recorded-for-most-website-content",
    "open-referral-uk-govuk-record": "OGL-UK-3.0",
    "hsds-3.1-documentation": "CC-BY-SA-4.0",
    "w3c-recommendations": "W3C-Document-License-2023",
    "local-government-services-list": "Open-Government-Licence-version-not-recorded",
    "okf-explorer": "MIT-code-and-CC-BY-NC-4.0-content",
}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def load_rights_register() -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(RIGHTS_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{RIGHTS_PATH.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{RIGHTS_PATH.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def validate_rights_register(register: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = RIGHTS_PATH.relative_to(ROOT).as_posix()
    if register.get("rights_decisions_version") != "rights-decisions.v1":
        errors.append(f"{prefix}: rights_decisions_version must be rights-decisions.v1")
    if register.get("status") != "approved":
        errors.append(f"{prefix}: status must be approved")
    for field in ("decided_at", "decided_by", "scope"):
        if not _nonempty(register.get(field)):
            errors.append(f"{prefix}: {field} must be non-empty")

    repository = register.get("repository", {})
    for authored_kind in ("code", "documentation", "ontology_terms"):
        decision = repository.get(authored_kind, {}) if isinstance(repository, dict) else {}
        if not isinstance(decision, dict) or decision.get("licence") != "MIT":
            errors.append(f"{prefix}: repository.{authored_kind}.licence must be MIT")
        if not isinstance(decision, dict) or decision.get("redistribution_allowed") is not True:
            errors.append(f"{prefix}: repository.{authored_kind} must allow redistribution")
        evidence = decision.get("evidence", []) if isinstance(decision, dict) else []
        if not evidence or any(not _evidence_complete(item) for item in evidence):
            errors.append(f"{prefix}: repository.{authored_kind} must have dated evidence")

    policy = register.get("use_policy", {})
    expected_policy = {
        "source_content": "linked_reference_and_original_summary_only",
        "source_content_redistribution_allowed": False,
        "snapshots_acquired": False,
        "snapshot_redistribution_allowed": False,
        "publication_allowed": False,
    }
    for field, expected in expected_policy.items():
        if not isinstance(policy, dict) or policy.get(field) != expected:
            errors.append(f"{prefix}: use_policy.{field} must be {expected!r}")
    projection = policy.get("generated_projections", {}) if isinstance(policy, dict) else {}
    if not isinstance(projection, dict) or projection.get("licence") != "MIT":
        errors.append(f"{prefix}: generated projections must record the MIT licence")
    if not isinstance(projection, dict) or projection.get("redistribution_allowed") is not True:
        errors.append(f"{prefix}: eligible generated projections must allow redistribution")
    if not isinstance(projection, dict) or not _nonempty(projection.get("condition")):
        errors.append(f"{prefix}: generated projection redistribution must be conditional")

    attribution = register.get("attribution", {})
    if not isinstance(attribution, dict) or attribution.get("ogl_v3_fallback") != EXPECTED_OGL_ATTRIBUTION:
        errors.append(f"{prefix}: OGL v3 fallback attribution is missing or changed")
    if not isinstance(attribution, dict) or len(attribution.get("ogl_v3_requirements", [])) < 6:
        errors.append(f"{prefix}: OGL v3 attribution and exclusion requirements are incomplete")
    evidence = attribution.get("evidence", []) if isinstance(attribution, dict) else []
    if not evidence or any(not _evidence_complete(item) for item in evidence):
        errors.append(f"{prefix}: OGL attribution must have dated official evidence")

    families = register.get("licence_families", {})
    if not isinstance(families, dict) or not families:
        errors.append(f"{prefix}: licence_families must be a non-empty mapping")
        families = {}

    host_decisions = register.get("host_decisions", [])
    if not isinstance(host_decisions, list):
        errors.append(f"{prefix}: host_decisions must be a list")
        host_decisions = []
    decision_hosts: list[str] = []
    for index, decision in enumerate(host_decisions):
        if not isinstance(decision, dict):
            errors.append(f"{prefix}: host_decisions[{index}] must be a mapping")
            continue
        host = str(decision.get("host", ""))
        decision_hosts.append(host)
        for field in ("host", "owner_family", "licence_family", "decision", "evidence"):
            if not _nonempty(decision.get(field)):
                errors.append(f"{prefix}: host_decisions[{index}].{field} must be non-empty")
        if decision.get("licence_family") not in families:
            errors.append(f"{prefix}: {host or index} references an unknown licence family")
        if decision.get("decision") != "linked_reference_and_original_summary_only":
            errors.append(f"{prefix}: {host or index} must retain link-and-summary use")
        if not _evidence_complete(decision.get("evidence")):
            errors.append(f"{prefix}: {host or index} must have dated HTTPS evidence")
    if len(decision_hosts) != len(set(decision_hosts)):
        errors.append(f"{prefix}: host decisions must be unique")

    source_registers, source_errors = load_source_registers()
    errors.extend(source_errors)
    source_hosts: set[str] = set()
    source_count = 0
    for source_register in source_registers:
        for source in source_register.get("sources", []):
            source_count += 1
            source_hosts.add(urlparse(str(source.get("resource", ""))).netloc.lower())
            if source.get("rights_basis") != RECORDED_RIGHTS_BASIS:
                errors.append(f"{prefix}: {source.get('id', 'source')} lacks the recorded rights basis")
    inventory, inventory_errors = load_reference_inventory()
    errors.extend(inventory_errors)
    for reference in flatten_inventory_references(inventory):
        rights_decision = str(reference.get("rights_decision", ""))
        if not rights_decision.startswith("host:"):
            continue
        source_count += 1
        resource_host = urlparse(str(reference.get("resource", ""))).netloc.lower()
        source_hosts.add(resource_host)
        if rights_decision != f"host:{resource_host}":
            errors.append(
                f"{prefix}: {reference.get('id', 'inventory reference')} rights decision "
                "does not match its resource host"
            )
    if set(decision_hosts) != source_hosts:
        missing = sorted(source_hosts - set(decision_hosts))
        extra = sorted(set(decision_hosts) - source_hosts)
        if missing:
            errors.append(f"{prefix}: missing host decisions: {', '.join(missing)}")
        if extra:
            errors.append(f"{prefix}: host decisions without registered sources: {', '.join(extra)}")

    standards = register.get("reference_standards", [])
    standard_map = {
        item.get("id"): item for item in standards if isinstance(item, dict) and _nonempty(item.get("id"))
    } if isinstance(standards, list) else {}
    for standard_id, licence in EXPECTED_STANDARD_LICENCES.items():
        standard = standard_map.get(standard_id, {})
        if standard.get("licence") != licence:
            errors.append(f"{prefix}: {standard_id} must record {licence}")
        standard_evidence = standard.get("evidence", []) if isinstance(standard, dict) else []
        if not standard_evidence or any(not _evidence_complete(item) for item in standard_evidence):
            errors.append(f"{prefix}: {standard_id} must have dated HTTPS evidence")

    try:
        licence_text = LICENSE_PATH.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"LICENSE: {error}")
    else:
        if "MIT License" not in licence_text or "Copyright (c) 2026 Chris Page" not in licence_text:
            errors.append("LICENSE: standard MIT grant and copyright notice are required")
    try:
        notice_text = NOTICE_PATH.read_text(encoding="utf-8")
    except OSError as error:
        errors.append(f"NOTICE.md: {error}")
    else:
        if EXPECTED_OGL_ATTRIBUTION not in notice_text.replace("\n", " "):
            errors.append("NOTICE.md: exact OGL v3 fallback attribution is required")

    register["_validated_source_count"] = source_count
    register["_validated_host_count"] = len(source_hosts)
    return errors


def _evidence_complete(evidence: Any) -> bool:
    if not isinstance(evidence, dict):
        return False
    resource = str(evidence.get("resource", ""))
    observed_at = str(evidence.get("observed_at", ""))
    if resource == "LICENSE":
        return observed_at == "2026-08-07"
    parsed = urlparse(resource)
    return parsed.scheme == "https" and bool(parsed.netloc) and bool(observed_at)


def validate_rights() -> tuple[dict[str, Any], list[str]]:
    register, errors = load_rights_register()
    if register:
        errors.extend(validate_rights_register(register))
    return register, sorted(set(errors))


def main() -> int:
    register, errors = validate_rights()
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        "Rights checks passed: "
        f"{register['_validated_host_count']} source hosts, "
        f"{register['_validated_source_count']} linked references, 0 snapshots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
