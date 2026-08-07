#!/usr/bin/env python3
"""Validate the approved, staged canonical service-family denominator."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from check_inventory import EXPECTED_DOMAIN_IDS


ROOT = Path(__file__).resolve().parents[1]
DENOMINATOR_PATH = ROOT / "source" / "service-family-denominator.v1.yaml"
ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WAVES = ("wave-1", "wave-2", "wave-3")
EXPECTED_IMPLEMENTED = {
    "report-missed-rubbish-collection",
    "learn-to-drive-car",
    "respond-to-speeding-notice",
    "register-a-death",
    "notify-organisations-after-a-death",
    "administer-an-estate",
}
EXPECTED_BLOCKS = {
    "source_snapshots",
    "source_content_redistribution",
    "personalized_eligibility_legal_or_medical_decisions",
    "unsupported_cross_jurisdiction_equivalence",
    "ci_or_publication",
}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def load_service_denominator() -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(DENOMINATOR_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{DENOMINATOR_PATH.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{DENOMINATOR_PATH.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def flatten_service_families(denominator: dict[str, Any]) -> list[dict[str, str]]:
    families: list[dict[str, str]] = []
    for domain in denominator.get("domains", []):
        if not isinstance(domain, dict):
            continue
        for wave in WAVES:
            for family_id in domain.get(wave, []):
                families.append(
                    {
                        "id": str(family_id),
                        "domain": str(domain.get("id", "")),
                        "domain_title": str(domain.get("title", "")),
                        "wave": wave,
                    }
                )
    return families


def service_family_scopes(denominator: dict[str, Any]) -> dict[str, list[str]]:
    families = {item["id"] for item in flatten_service_families(denominator)}
    scopes: dict[str, list[str]] = {family_id: ["national-and-devolved"] for family_id in families}
    for scope, ids in denominator.get("scope_overrides", {}).items():
        for family_id in ids if isinstance(ids, list) else []:
            if family_id in scopes:
                if scopes[family_id] == ["national-and-devolved"]:
                    scopes[family_id] = []
                scopes[family_id].append(str(scope))
    return {family_id: sorted(set(values)) for family_id, values in scopes.items()}


def validate_service_denominator(denominator: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = DENOMINATOR_PATH.relative_to(ROOT).as_posix()
    if denominator.get("service_family_denominator_version") != "service-family-denominator.v1":
        errors.append(f"{prefix}: unsupported denominator version")
    if denominator.get("status") != "owner_approved":
        errors.append(f"{prefix}: status must be owner_approved")
    if denominator.get("decision_date") != "2026-08-07":
        errors.append(f"{prefix}: decision_date must retain the owner decision date")
    if denominator.get("approved_by") != "owner:chris-page-gov":
        errors.append(f"{prefix}: approved_by must identify the repository owner")

    decision = denominator.get("decision", {})
    if not isinstance(decision, dict):
        errors.append(f"{prefix}: decision must be a mapping")
        decision = {}
    if decision.get("target_range") != "250-400":
        errors.append(f"{prefix}: decision.target_range must be 250-400")
    if decision.get("assertion_status") != "normalized":
        errors.append(f"{prefix}: denominator entries must remain normalized planning assertions")
    if decision.get("source_inventory") != "source/exhaustive-reference-inventory.v1.yaml":
        errors.append(f"{prefix}: decision.source_inventory must name the approved inventory")
    if set(decision.get("does_not_authorize", [])) != EXPECTED_BLOCKS:
        errors.append(f"{prefix}: decision.does_not_authorize must retain all safety and publication blocks")

    waves = denominator.get("waves", [])
    wave_ids = {str(item.get("id")) for item in waves if isinstance(item, dict)}
    if wave_ids != set(WAVES) or any(not _nonempty(item.get("purpose")) for item in waves if isinstance(item, dict)):
        errors.append(f"{prefix}: waves must define the three acquisition stages with purposes")

    domains = denominator.get("domains", [])
    domain_ids: list[str] = []
    for index, domain in enumerate(domains if isinstance(domains, list) else []):
        item_prefix = f"{prefix}: domains[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"{item_prefix} must be a mapping")
            continue
        domain_id = str(domain.get("id", ""))
        domain_ids.append(domain_id)
        if not _nonempty(domain.get("title")):
            errors.append(f"{item_prefix}: title must be non-empty")
        count = 0
        for wave in WAVES:
            values = domain.get(wave, [])
            if not isinstance(values, list) or not values:
                errors.append(f"{item_prefix}: {wave} must be a non-empty list")
                continue
            count += len(values)
        if count < 10:
            errors.append(f"{item_prefix}: each domain must contain at least ten named families")
    if set(domain_ids) != EXPECTED_DOMAIN_IDS or len(domain_ids) != len(set(domain_ids)):
        errors.append(f"{prefix}: domains must contain each approved life-course domain exactly once")

    families = flatten_service_families(denominator)
    family_ids = [item["id"] for item in families]
    if len(family_ids) != len(set(family_ids)):
        duplicates = sorted({value for value in family_ids if family_ids.count(value) > 1})
        errors.append(f"{prefix}: duplicate service-family ids: {', '.join(duplicates)}")
    invalid = sorted(value for value in family_ids if not ID_RE.fullmatch(value))
    if invalid:
        errors.append(f"{prefix}: invalid service-family ids: {', '.join(invalid)}")
    declared_count = decision.get("declared_family_count")
    if declared_count != len(family_ids):
        errors.append(f"{prefix}: declared_family_count must equal {len(family_ids)}")
    if not 250 <= len(family_ids) <= 400:
        errors.append(f"{prefix}: service-family count must stay inside the approved 250-400 range")

    implemented = set(denominator.get("implemented_families", []))
    if implemented != EXPECTED_IMPLEMENTED or not implemented <= set(family_ids):
        errors.append(f"{prefix}: implemented_families must name the six existing canonical families")

    scope_classes = denominator.get("scope_classes", {})
    if not isinstance(scope_classes, dict) or any(not _nonempty(value) for value in scope_classes.values()):
        errors.append(f"{prefix}: scope_classes must define every declared scope")
        scope_classes = {}
    overrides = denominator.get("scope_overrides", {})
    if not isinstance(overrides, dict):
        errors.append(f"{prefix}: scope_overrides must be a mapping")
        overrides = {}
    unknown_scopes = set(overrides) - set(scope_classes)
    if unknown_scopes:
        errors.append(f"{prefix}: unknown scope overrides: {', '.join(sorted(unknown_scopes))}")
    unknown_families = {
        str(family_id)
        for values in overrides.values()
        if isinstance(values, list)
        for family_id in values
        if str(family_id) not in set(family_ids)
    }
    if unknown_families:
        errors.append(f"{prefix}: scope overrides name unknown families: {', '.join(sorted(unknown_families))}")

    denominator["_validated_family_count"] = len(family_ids)
    denominator["_validated_domain_count"] = len(set(domain_ids))
    denominator["_validated_wave_counts"] = {
        wave: sum(1 for item in families if item["wave"] == wave) for wave in WAVES
    }
    denominator["_validated_scope_counts"] = {
        scope: sum(1 for values in service_family_scopes(denominator).values() if scope in values)
        for scope in scope_classes
    }
    return errors


def validate_denominator() -> tuple[dict[str, Any], list[str]]:
    denominator, errors = load_service_denominator()
    if denominator:
        errors.extend(validate_service_denominator(denominator))
    return denominator, sorted(set(errors))


def main() -> int:
    denominator, errors = validate_denominator()
    if errors:
        for error in errors:
            print(error)
        return 1
    waves = denominator["_validated_wave_counts"]
    print(
        "Service-family denominator checks passed: "
        f"{denominator['_validated_family_count']} families across "
        f"{denominator['_validated_domain_count']} domains "
        f"({', '.join(f'{wave}={count}' for wave, count in waves.items())})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
