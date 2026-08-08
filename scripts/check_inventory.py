#!/usr/bin/env python3
"""Validate the exhaustive, link-only reference-family inventory."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
INVENTORY_PATH = ROOT / "source" / "exhaustive-reference-inventory.v1.yaml"
RIGHTS_PATH = ROOT / "source" / "rights-decisions.v1.yaml"
EXPECTED_DOMAIN_IDS = {
    "before-birth-and-starting-family",
    "birth-and-newborn",
    "early-years",
    "school-years",
    "transition-to-adulthood",
    "further-education-university-research",
    "finding-work-and-unemployment",
    "employment",
    "housing-and-community",
    "rubbish-recycling-and-street",
    "public-and-private-transport",
    "transport-enforcement",
    "money-tax-and-benefits",
    "shopping-and-consumer-rights",
    "relationships-and-family-change",
    "health-throughout-life",
    "disability-care-and-support",
    "citizenship-democracy-and-rights",
    "police-and-legal-services",
    "starting-and-running-organisation",
    "ideas-creativity-and-research",
    "holidays-volunteering-and-living-overseas",
    "later-life",
    "death-and-bereavement",
}
REFERENCE_JURISDICTIONS = {
    "uk-or-england",
    "scotland",
    "wales",
    "northern-ireland",
    "local",
}
NATIONAL_JURISDICTIONS = REFERENCE_JURISDICTIONS - {"local"}
REQUIRED_REFERENCE_FIELDS = {
    "id",
    "title",
    "resource",
    "source_updated_at",
    "domains",
    "summary",
}
REQUIRED_FAMILY_FIELDS = {
    "id",
    "owner",
    "jurisdiction",
    "authority_role",
    "rights_decision",
    "observed_at",
    "access_method",
    "version_model",
    "update_cadence",
    "limitations",
    "references",
}
REQUIRED_STANDARD_FIELDS = REQUIRED_REFERENCE_FIELDS | {
    "owner",
    "jurisdiction",
    "authority_role",
    "observed_at",
    "rights_decision",
}
REQUIRED_GAP_FIELDS = {"id", "severity", "scope", "finding", "owner_follow_up", "blocks"}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def _load_yaml(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{path.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def load_reference_inventory() -> tuple[dict[str, Any], list[str]]:
    return _load_yaml(INVENTORY_PATH)


def flatten_inventory_references(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    references: list[dict[str, Any]] = []
    for family in inventory.get("reference_families", []):
        if not isinstance(family, dict):
            continue
        for reference in family.get("references", []):
            if not isinstance(reference, dict):
                continue
            item = dict(reference)
            item["owner"] = family.get("owner")
            item["jurisdiction"] = family.get("jurisdiction")
            item["authority_role"] = family.get("authority_role")
            item["observed_at"] = family.get("observed_at")
            item["rights_decision"] = family.get("rights_decision")
            item["family_id"] = family.get("id")
            references.append(item)
    for reference in inventory.get("standards_and_tooling_references", []):
        if isinstance(reference, dict):
            item = dict(reference)
            item["family_id"] = "standards-and-tooling"
            references.append(item)
    return references


def _validate_reference(
    reference: dict[str, Any],
    prefix: str,
    required_fields: set[str],
    domain_ids: set[str],
) -> list[str]:
    errors: list[str] = []
    missing = sorted(field for field in required_fields if not _nonempty(reference.get(field)))
    if missing:
        errors.append(f"{prefix}: missing: {', '.join(missing)}")
    resource = str(reference.get("resource", ""))
    parsed = urlparse(resource)
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"{prefix}: resource must be an HTTPS URL")
    domains = reference.get("domains", [])
    if not isinstance(domains, list) or not domains:
        errors.append(f"{prefix}: domains must be a non-empty list")
    else:
        unknown = sorted(set(str(item) for item in domains) - domain_ids)
        if unknown:
            errors.append(f"{prefix}: unknown domains: {', '.join(unknown)}")
    summary = str(reference.get("summary", ""))
    if len(summary.split()) < 7:
        errors.append(f"{prefix}: summary must be an original explanatory sentence")
    return errors


def validate_reference_inventory(inventory: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = INVENTORY_PATH.relative_to(ROOT).as_posix()
    if inventory.get("inventory_version") != "exhaustive-reference-inventory.v1":
        errors.append(f"{prefix}: inventory_version must be exhaustive-reference-inventory.v1")
    if inventory.get("status") != "owner_authorized_link_only":
        errors.append(f"{prefix}: status must be owner_authorized_link_only")
    if inventory.get("observed_at") != "2026-08-07":
        errors.append(f"{prefix}: observed_at must retain the decision date")

    decision = inventory.get("decision", {})
    expected_decision = {
        "authorized_by": "owner:chris-page-gov",
        "authorized_at": "2026-08-07",
        "acquisition_mode": "linked_reference_and_original_summary_only",
        "snapshots_acquired": False,
        "source_content_redistribution_allowed": False,
        "publication_allowed": False,
    }
    for field, expected in expected_decision.items():
        if not isinstance(decision, dict) or decision.get(field) != expected:
            errors.append(f"{prefix}: decision.{field} must be {expected!r}")

    denominator = inventory.get("denominator", {})
    domains = denominator.get("domains", []) if isinstance(denominator, dict) else []
    domain_ids = {
        str(item.get("id")) for item in domains if isinstance(item, dict) and _nonempty(item.get("id"))
    }
    if domain_ids != EXPECTED_DOMAIN_IDS:
        missing = sorted(EXPECTED_DOMAIN_IDS - domain_ids)
        extra = sorted(domain_ids - EXPECTED_DOMAIN_IDS)
        if missing:
            errors.append(f"{prefix}: missing denominator domains: {', '.join(missing)}")
        if extra:
            errors.append(f"{prefix}: unknown denominator domains: {', '.join(extra)}")
    jurisdictions = set(denominator.get("reference_jurisdictions", [])) if isinstance(denominator, dict) else set()
    if jurisdictions != REFERENCE_JURISDICTIONS:
        errors.append(f"{prefix}: reference_jurisdictions must contain the five approved reference scopes")
    expected_cells = len(EXPECTED_DOMAIN_IDS) * len(REFERENCE_JURISDICTIONS)
    if denominator.get("expected_domain_jurisdiction_cells") != expected_cells:
        errors.append(f"{prefix}: expected_domain_jurisdiction_cells must be {expected_cells}")
    dimensions = denominator.get("capability_dimensions", []) if isinstance(denominator, dict) else []
    if not isinstance(dimensions, list) or len(dimensions) < 10:
        errors.append(f"{prefix}: at least ten capability dimensions are required")

    included_count = 0
    includes = denominator.get("included_existing_registers", []) if isinstance(denominator, dict) else []
    if not isinstance(includes, list) or len(includes) != 3:
        errors.append(f"{prefix}: the three existing slice registers must be included")
    else:
        for index, include in enumerate(includes):
            if not isinstance(include, dict):
                errors.append(f"{prefix}: included_existing_registers[{index}] must be a mapping")
                continue
            path = ROOT / str(include.get("path", ""))
            expected = include.get("expected_references")
            register, register_errors = _load_yaml(path)
            errors.extend(register_errors)
            actual = len(register.get("sources", [])) if register else 0
            if actual != expected:
                errors.append(f"{prefix}: {path.relative_to(ROOT)} must contain {expected} references")
            included_count += actual

    rights, rights_errors = _load_yaml(RIGHTS_PATH)
    errors.extend(rights_errors)
    host_rights = {
        f"host:{item.get('host')}"
        for item in rights.get("host_decisions", [])
        if isinstance(item, dict) and _nonempty(item.get("host"))
    }
    standard_rights = {
        f"standard:{item.get('id')}"
        for item in rights.get("reference_standards", [])
        if isinstance(item, dict) and _nonempty(item.get("id"))
    }

    reference_ids: list[str] = []
    reference_urls: list[str] = []
    families = inventory.get("reference_families", [])
    if not isinstance(families, list) or not families:
        errors.append(f"{prefix}: reference_families must be a non-empty list")
        families = []
    family_ids: list[str] = []
    for family_index, family in enumerate(families):
        family_prefix = f"{prefix}: reference_families[{family_index}]"
        if not isinstance(family, dict):
            errors.append(f"{family_prefix} must be a mapping")
            continue
        missing = sorted(field for field in REQUIRED_FAMILY_FIELDS if not _nonempty(family.get(field)))
        if missing:
            errors.append(f"{family_prefix}: missing: {', '.join(missing)}")
        family_ids.append(str(family.get("id", "")))
        rights_decision = str(family.get("rights_decision", ""))
        if rights_decision not in host_rights:
            errors.append(f"{family_prefix}: rights_decision must name a dated host decision")
        family_host = rights_decision.removeprefix("host:")
        references = family.get("references", [])
        if not isinstance(references, list) or not references:
            errors.append(f"{family_prefix}: references must be a non-empty list")
            continue
        for reference_index, reference in enumerate(references):
            item_prefix = f"{family_prefix}.references[{reference_index}]"
            if not isinstance(reference, dict):
                errors.append(f"{item_prefix} must be a mapping")
                continue
            errors.extend(_validate_reference(reference, item_prefix, REQUIRED_REFERENCE_FIELDS, domain_ids))
            reference_ids.append(str(reference.get("id", "")))
            resource = str(reference.get("resource", ""))
            reference_urls.append(resource)
            if urlparse(resource).netloc.lower() != family_host:
                errors.append(f"{item_prefix}: URL host must match {rights_decision}")

    standards = inventory.get("standards_and_tooling_references", [])
    if not isinstance(standards, list) or not standards:
        errors.append(f"{prefix}: standards_and_tooling_references must be a non-empty list")
        standards = []
    for index, reference in enumerate(standards):
        item_prefix = f"{prefix}: standards_and_tooling_references[{index}]"
        if not isinstance(reference, dict):
            errors.append(f"{item_prefix} must be a mapping")
            continue
        errors.extend(_validate_reference(reference, item_prefix, REQUIRED_STANDARD_FIELDS, domain_ids))
        reference_ids.append(str(reference.get("id", "")))
        reference_urls.append(str(reference.get("resource", "")))
        if reference.get("rights_decision") not in standard_rights:
            errors.append(f"{item_prefix}: rights_decision must name a dated standard decision")

    if len(family_ids) != len(set(family_ids)):
        errors.append(f"{prefix}: reference family ids must be unique")
    if len(reference_ids) != len(set(reference_ids)):
        errors.append(f"{prefix}: reference ids must be unique")
    if len(reference_urls) != len(set(reference_urls)):
        errors.append(f"{prefix}: inventory URLs must be unique")

    coverage = inventory.get("coverage", {})
    local_default = coverage.get("local_default", {}) if isinstance(coverage, dict) else {}
    if not isinstance(local_default, dict) or local_default.get("status") != "partial":
        errors.append(f"{prefix}: coverage.local_default.status must be partial")
    for reference_id in local_default.get("references", []) if isinstance(local_default, dict) else []:
        if reference_id not in reference_ids:
            errors.append(f"{prefix}: local coverage references unknown id {reference_id}")
    coverage_domains = coverage.get("domains", []) if isinstance(coverage, dict) else []
    coverage_ids: list[str] = []
    covered_cells = 0
    partial_cells = 0
    reference_map = {item.get("id"): item for item in flatten_inventory_references(inventory)}
    for index, domain in enumerate(coverage_domains if isinstance(coverage_domains, list) else []):
        item_prefix = f"{prefix}: coverage.domains[{index}]"
        if not isinstance(domain, dict):
            errors.append(f"{item_prefix} must be a mapping")
            continue
        domain_id = str(domain.get("id", ""))
        coverage_ids.append(domain_id)
        for jurisdiction in NATIONAL_JURISDICTIONS:
            ids = domain.get(jurisdiction, [])
            if not isinstance(ids, list) or not ids:
                errors.append(f"{item_prefix}: {jurisdiction} must name at least one reference")
                continue
            covered_cells += 1
            for reference_id in ids:
                reference = reference_map.get(reference_id)
                if reference is None:
                    errors.append(f"{item_prefix}: {jurisdiction} references unknown id {reference_id}")
                elif domain_id not in reference.get("domains", []):
                    errors.append(f"{item_prefix}: {reference_id} does not declare domain {domain_id}")
        partial_cells += 1
    if set(coverage_ids) != domain_ids or len(coverage_ids) != len(set(coverage_ids)):
        errors.append(f"{prefix}: coverage must contain each denominator domain exactly once")
    if covered_cells + partial_cells != expected_cells:
        errors.append(f"{prefix}: coverage must account for exactly {expected_cells} cells")

    gaps = inventory.get("gaps", [])
    gap_ids: list[str] = []
    if not isinstance(gaps, list) or not gaps:
        errors.append(f"{prefix}: gaps must be a non-empty list")
        gaps = []
    for index, gap in enumerate(gaps):
        item_prefix = f"{prefix}: gaps[{index}]"
        if not isinstance(gap, dict):
            errors.append(f"{item_prefix} must be a mapping")
            continue
        missing = sorted(field for field in REQUIRED_GAP_FIELDS if not _nonempty(gap.get(field)))
        if missing:
            errors.append(f"{item_prefix}: missing: {', '.join(missing)}")
        gap_ids.append(str(gap.get("id", "")))
        if gap.get("severity") not in {"high", "medium", "low"}:
            errors.append(f"{item_prefix}: severity must be high, medium or low")
    if len(gap_ids) != len(set(gap_ids)):
        errors.append(f"{prefix}: gap ids must be unique")
    local_gap_ids = set(local_default.get("gap_ids", [])) if isinstance(local_default, dict) else set()
    unknown_local_gaps = local_gap_ids - set(gap_ids)
    if unknown_local_gaps:
        errors.append(f"{prefix}: local coverage names unknown gaps: {', '.join(sorted(unknown_local_gaps))}")

    inventory["_validated_inventory_reference_count"] = len(reference_ids)
    inventory["_validated_included_reference_count"] = included_count
    inventory["_validated_covered_cell_count"] = covered_cells
    inventory["_validated_partial_cell_count"] = partial_cells
    inventory["_validated_gap_count"] = len(gap_ids)
    return errors


def validate_inventory() -> tuple[dict[str, Any], list[str]]:
    inventory, errors = load_reference_inventory()
    if inventory:
        errors.extend(validate_reference_inventory(inventory))
    return inventory, sorted(set(errors))


def main() -> int:
    inventory, errors = validate_inventory()
    if errors:
        for error in errors:
            print(error)
        return 1
    inventory_count = inventory["_validated_inventory_reference_count"]
    included_count = inventory["_validated_included_reference_count"]
    covered = inventory["_validated_covered_cell_count"]
    partial = inventory["_validated_partial_cell_count"]
    gaps = inventory["_validated_gap_count"]
    print(
        "Inventory checks passed: "
        f"{inventory_count + included_count} external reference records "
        f"({inventory_count} inventory + {included_count} implemented slices), "
        f"{covered + partial} coverage cells ({covered} covered, {partial} partial), "
        f"{gaps} gaps, 0 snapshots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
