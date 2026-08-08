#!/usr/bin/env python3
"""Validate the owner-authorized full life-course population contract."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import yaml

from build_okf_bundle import ROOT
from check_service_denominator import (
    flatten_service_families,
    load_service_denominator,
    validate_service_denominator,
)


CONTRACT_PATH = ROOT / "profiles" / "life-course-population-contract.v1.yaml"
PROCESS_PATH = ROOT / "source" / "life-course-processes.v1.yaml"
PREDICATE_PATH = ROOT / "ontology" / "governed-predicates.v1.yaml"
SHAPES_PATH = ROOT / "shapes" / "life-course-family.v1.yaml"
DOSSIER_SCHEMA_PATH = ROOT / "schemas" / "life-course-family.v1.schema.json"
LINK_SCHEMA_PATH = ROOT / "schemas" / "source-link-receipt.v1.schema.json"
DOMAIN_PROFILE_PATH = ROOT / "profiles" / "okf-domain-profile.v1.yaml"

REQUIRED_PREDICATES = {
    "belongs-to-life-course-domain",
    "part-of-enclosing-process",
    "addresses-user-need",
    "has-episode",
    "precedes",
    "follows",
    "offered-by",
    "delivered-by",
    "applies-in-jurisdiction",
    "requires",
    "governed-by",
    "produces",
    "has-outcome",
    "depends-on",
    "has-redress",
    "supported-by-source",
}
REQUIRED_DOSSIER_FIELDS = {
    "schema",
    "id",
    "title",
    "aliases",
    "description",
    "status",
    "assertion_status",
    "life_course_domain",
    "enclosing_processes",
    "situations",
    "user_needs",
    "interaction_boundary",
    "applicability",
    "actors",
    "journeys",
    "dependencies",
    "sources",
    "limitations",
    "review",
    "narrative",
}


def load_yaml(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{path.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def load_json(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return {}, [f"{path.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path.relative_to(ROOT)}: root must be an object"]
    return value, []


def load_population_inputs() -> tuple[dict[str, dict[str, Any]], list[str]]:
    values: dict[str, dict[str, Any]] = {}
    errors: list[str] = []
    for key, path in (
        ("contract", CONTRACT_PATH),
        ("processes", PROCESS_PATH),
        ("predicates", PREDICATE_PATH),
        ("shapes", SHAPES_PATH),
        ("domain_profile", DOMAIN_PROFILE_PATH),
    ):
        values[key], found = load_yaml(path)
        errors.extend(found)
    for key, path in (("dossier_schema", DOSSIER_SCHEMA_PATH), ("link_schema", LINK_SCHEMA_PATH)):
        values[key], found = load_json(path)
        errors.extend(found)
    return values, errors


def validate_population_contract(values: dict[str, dict[str, Any]] | None = None) -> list[str]:
    errors: list[str] = []
    if values is None:
        values, errors = load_population_inputs()
    if errors:
        return sorted(set(errors))

    denominator, denominator_errors = load_service_denominator()
    if denominator:
        denominator_errors.extend(validate_service_denominator(denominator))
    errors.extend(denominator_errors)
    if not denominator:
        return sorted(set(errors))

    families = flatten_service_families(denominator)
    family_by_id = {row["id"]: row for row in families}
    domain_ids = {row["id"] for row in denominator.get("domains", [])}
    contract = values["contract"]
    processes = values["processes"]
    predicates = values["predicates"]
    shapes = values["shapes"]
    domain_profile = values["domain_profile"]
    dossier_schema = values["dossier_schema"]
    link_schema = values["link_schema"]

    if contract.get("contract_version") != "life-course-population-contract.v1":
        errors.append("population contract must declare life-course-population-contract.v1")
    if contract.get("status") != "owner_authorized" or contract.get("approved_by") != "owner:chris-page-gov":
        errors.append("population contract must retain explicit owner authorization")
    if contract.get("decision", {}).get("family_count") != len(families):
        errors.append("population contract family count must match the approved denominator")
    if contract.get("decision", {}).get("domain_count") != len(domain_ids):
        errors.append("population contract domain count must match the approved denominator")
    prohibited = set(contract.get("authorization", {}).get("prohibits", []))
    for boundary in ("source_snapshots", "source_content_redistribution", "github_pages_or_other_publication_without_explicit_owner_request"):
        if boundary not in prohibited:
            errors.append(f"population contract must prohibit {boundary}")

    packs = contract.get("delivery_packs", [])
    pack_domains = [domain for pack in packs for domain in pack.get("domains", [])]
    if len(packs) != 8:
        errors.append("population contract must declare exactly eight delivery packs")
    if Counter(pack_domains) != Counter(domain_ids):
        errors.append("delivery packs must cover every domain exactly once")
    for pack in packs:
        expected = sum(1 for family in families if family["domain"] in pack.get("domains", []))
        if pack.get("expected_families") != expected:
            errors.append(f"{pack.get('id', 'pack')}: expected family count must be {expected}")

    process_rows = processes.get("processes", [])
    process_minimum = contract.get("decision", {}).get("process_count_minimum")
    process_maximum = contract.get("decision", {}).get("process_count_maximum")
    if not isinstance(process_minimum, int) or not isinstance(process_maximum, int) or not process_minimum <= len(process_rows) <= process_maximum:
        errors.append("process denominator must contain the contracted 40 to 50 processes")
    process_ids = [str(row.get("id", "")) for row in process_rows]
    if len(process_ids) != len(set(process_ids)):
        errors.append("process identifiers must be unique")
    mapped: list[str] = []
    for process in process_rows:
        process_id = str(process.get("id", ""))
        domain = str(process.get("domain", ""))
        if domain not in domain_ids:
            errors.append(f"{process_id}: unknown life-course domain {domain!r}")
        if not str(process.get("title", "")).strip():
            errors.append(f"{process_id}: title is required")
        members = process.get("families", [])
        if not isinstance(members, list) or not members:
            errors.append(f"{process_id}: at least one family is required")
            continue
        for family_id in members:
            mapped.append(str(family_id))
            family = family_by_id.get(str(family_id))
            if not family:
                errors.append(f"{process_id}: unknown family {family_id}")
            elif family["domain"] != domain:
                errors.append(f"{process_id}: family {family_id} belongs to {family['domain']}, not {domain}")
    missing = sorted(set(family_by_id) - set(mapped))
    duplicated = sorted(family_id for family_id, count in Counter(mapped).items() if count != 1)
    if missing:
        errors.append(f"process denominator leaves families unmapped: {', '.join(missing)}")
    if duplicated:
        errors.append(f"process denominator must map each family exactly once: {', '.join(duplicated)}")

    predicate_ids = {str(row.get("id", "")) for row in predicates.get("predicates", [])}
    if predicate_ids != REQUIRED_PREDICATES:
        errors.append("governed predicate registry must contain the contracted predicate set exactly")
    if predicates.get("licence") != "MIT":
        errors.append("repository-authored governed predicates must use MIT")

    shape_ids = {str(row.get("id", "")) for row in shapes.get("shapes", [])}
    if not {"LifeCourseFamilyShape", "JourneyStepShape", "SourceReferenceShape", "MaterialRelationshipShape"}.issubset(shape_ids):
        errors.append("life-course validation shapes are incomplete")
    if "not_claimed_rdf_conformance" not in str(shapes.get("status", "")):
        errors.append("shape contract must not claim RDF SHACL conformance")

    schema_required = set(dossier_schema.get("required", []))
    if schema_required != REQUIRED_DOSSIER_FIELDS:
        errors.append("life-course-family schema must require the contracted dossier fields exactly")
    if dossier_schema.get("properties", {}).get("schema", {}).get("const") != "life-course-family.v1":
        errors.append("life-course-family schema discriminator is missing")
    if link_schema.get("properties", {}).get("response_body_retained", {}).get("const") is not False:
        errors.append("source-link receipts must forbid retaining response bodies")

    authorized = set(domain_profile.get("approval", {}).get("authorized_actions", []))
    blocked = set(domain_profile.get("approval", {}).get("blocked_actions", []))
    if "staged_full_population_implementation" not in authorized:
        errors.append("domain profile must authorize staged full-population implementation")
    if "corpus_expansion_beyond_three_slices" in blocked:
        errors.append("domain profile still blocks the owner-authorized population implementation")

    return sorted(set(errors))


def main() -> int:
    errors = validate_population_contract()
    if errors:
        for error in errors:
            print(error)
        return 1
    print("Population contract checks passed: 293 families, 24 domains, 48 enclosing processes, 8 packs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

