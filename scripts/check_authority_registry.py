#!/usr/bin/env python3
"""Validate the reviewed authority, geography, regulator and redress registry."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "source" / "authority-registry.v1.yaml"
RECEIPT_ROOT = ROOT / "evaluation" / "link-receipts" / "shared-authority-2026-08-08"
GSS_RE = re.compile(r"^[ENSW][0-9]{8}$")
EXPECTED_GSS_COUNTS = {
    "E060": 63,
    "E070": 164,
    "E080": 36,
    "E090": 33,
    "E100": 21,
    "N090": 11,
    "S120": 32,
    "W060": 22,
    "E470": 15,
}
EXPECTED_SECTORS = {
    "financial_services_and_insurance",
    "housing_and_property",
    "energy_and_utilities",
    "communications_and_post",
    "transport_and_travel",
    "health_and_social_care",
    "education_and_training",
    "legal_and_professional_services",
    "employment",
    "consumer_goods_and_services",
}


def load_registry() -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{REGISTRY_PATH.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{REGISTRY_PATH.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def duplicates(values: list[str]) -> list[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for value in values:
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return sorted(repeated)


def validate_registry(registry: dict[str, Any], require_receipts: bool = True) -> list[str]:
    errors: list[str] = []
    prefix = REGISTRY_PATH.relative_to(ROOT).as_posix()
    if registry.get("authority_registry_version") != "authority-registry.v1":
        errors.append(f"{prefix}: unsupported registry version")
    if registry.get("status") != "current_reviewed" or registry.get("observed_at") != "2026-08-08":
        errors.append(f"{prefix}: registry status and observation date must retain this reviewed decision")
    rules = registry.get("identity_rules", {})
    for key in ("gss_area_not_body", "welsh_language_variants", "source_native_fallback", "postcode", "current_route", "lgsl"):
        if not isinstance(rules, dict) or not str(rules.get(key, "")).strip():
            errors.append(f"{prefix}: identity rule {key} is missing")

    sources = registry.get("sources", [])
    source_ids = [str(value.get("id", "")) for value in sources if isinstance(value, dict)]
    if duplicates(source_ids):
        errors.append(f"{prefix}: duplicate source ids: {duplicates(source_ids)}")
    for source in sources:
        if not isinstance(source, dict):
            errors.append(f"{prefix}: source entry must be a mapping")
            continue
        for key in ("id", "title", "url", "owner", "rights_decision", "vintage", "assertion_scope"):
            if not str(source.get(key, "")).strip():
                errors.append(f"{prefix}: source {source.get('id')} lacks {key}")
        if not str(source.get("url", "")).startswith("https://"):
            errors.append(f"{prefix}: source {source.get('id')} must use HTTPS")
        rights_decision = str(source.get("rights_decision", ""))
        if rights_decision != "repository:MIT":
            source_host = urlparse(str(source.get("url", ""))).netloc.lower()
            if rights_decision != f"host:{source_host}":
                errors.append(f"{prefix}: source {source.get('id')} rights decision must match its URL host")
        query_url = str(source.get("query_url", ""))
        if query_url:
            query_host = urlparse(query_url).netloc.lower()
            if source.get("query_rights_decision") != f"host:{query_host}":
                errors.append(f"{prefix}: source {source.get('id')} query rights decision must match its query host")

    geographies = registry.get("geographies", [])
    organisations = registry.get("organisations", [])
    if not isinstance(geographies, list) or not isinstance(organisations, list):
        return errors + [f"{prefix}: geographies and organisations must be arrays"]
    geo_ids = [str(value.get("id", "")) for value in geographies if isinstance(value, dict)]
    org_ids = [str(value.get("id", "")) for value in organisations if isinstance(value, dict)]
    codes = [str(value.get("code", "")) for value in geographies if isinstance(value, dict)]
    for label, values in (("geography ids", geo_ids), ("organisation ids", org_ids), ("GSS codes", codes)):
        if duplicates(values):
            errors.append(f"{prefix}: duplicate {label}: {duplicates(values)}")
    if any(not GSS_RE.fullmatch(code) for code in codes):
        errors.append(f"{prefix}: every geography must use a nine-character GSS code")
    actual_counts = {family: sum(code.startswith(family) for code in codes) for family in EXPECTED_GSS_COUNTS}
    if actual_counts != EXPECTED_GSS_COUNTS:
        errors.append(f"{prefix}: GSS family counts differ: expected {EXPECTED_GSS_COUNTS}, got {actual_counts}")

    known_sources = set(source_ids)
    for area in geographies:
        if not isinstance(area, dict):
            continue
        missing_sources = set(area.get("source_ids", [])) - known_sources
        if missing_sources:
            errors.append(f"{prefix}: {area.get('id')} has unknown sources {sorted(missing_sources)}")
        labels = area.get("labels", [])
        welsh = [label for label in labels if isinstance(label, dict) and label.get("language") == "cy"]
        if welsh and (area.get("jurisdiction") != "wales" or any(label.get("identity_basis") != "same_official_gss_record" for label in welsh)):
            errors.append(f"{prefix}: {area.get('id')} has an unsupported Welsh identity assertion")
        if any("postcode" in str(key).lower() for key in area):
            errors.append(f"{prefix}: retained postcode field in {area.get('id')}")

    known_geographies = set(geo_ids)
    known_orgs = set(org_ids)
    local_orgs = [value for value in organisations if isinstance(value, dict) and str(value.get("id", "")).startswith("organisation:principal-local-authority:")]
    if len(local_orgs) != 382:
        errors.append(f"{prefix}: expected 382 normalized principal-authority actors, found {len(local_orgs)}")
    for organisation in organisations:
        if not isinstance(organisation, dict):
            errors.append(f"{prefix}: organisation entry must be a mapping")
            continue
        if not str(organisation.get("title", "")).strip():
            errors.append(f"{prefix}: organisation {organisation.get('id')} lacks title")
        if organisation.get("administers") and organisation.get("administers") not in known_geographies:
            errors.append(f"{prefix}: {organisation.get('id')} administers an unknown geography")
        if set(organisation.get("source_ids", [])) - known_sources:
            errors.append(f"{prefix}: {organisation.get('id')} has an unknown source")
        url = organisation.get("official_url")
        if url and not str(url).startswith("https://"):
            errors.append(f"{prefix}: {organisation.get('id')} official URL must use HTTPS")
        if "response_body" in organisation or "snapshot" in organisation:
            errors.append(f"{prefix}: {organisation.get('id')} retains prohibited source content")

    denominator = registry.get("denominators", {})
    if denominator.get("principal_local_authority_areas_and_normalized_actors", {}).get("count") != 382:
        errors.append(f"{prefix}: principal-authority denominator must be 382")
    if denominator.get("strategic_and_combined_authorities", {}).get("count") != 19:
        errors.append(f"{prefix}: strategic-authority denominator must be 19")
    if denominator.get("health_organisations", {}).get("bulk_acquisition") is not False:
        errors.append(f"{prefix}: health organisation acquisition must remain manual")

    sector_maps = registry.get("sector_maps", {})
    if set(sector_maps) != EXPECTED_SECTORS:
        errors.append(f"{prefix}: sector map must cover the governed ten-sector denominator")
    for sector, mapping in sector_maps.items():
        if not isinstance(mapping, dict) or not mapping.get("regulator_or_register") or not mapping.get("redress"):
            errors.append(f"{prefix}: sector {sector} lacks regulator or redress mapping")
            continue
        unknown = set(mapping.get("regulator_or_register", [])) | set(mapping.get("redress", []))
        unknown -= known_orgs
        if unknown:
            errors.append(f"{prefix}: sector {sector} references unknown organisations {sorted(unknown)}")

    if require_receipts:
        receipt_sources: set[str] = set()
        if RECEIPT_ROOT.is_dir():
            for path in RECEIPT_ROOT.glob("*.json"):
                try:
                    receipt = json.loads(path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError) as error:
                    errors.append(f"{path.relative_to(ROOT)}: {error}")
                    continue
                if receipt.get("response_body_retained") is not False:
                    errors.append(f"{path.relative_to(ROOT)}: response_body_retained must be false")
                if receipt.get("result") not in {"active", "redirected-active", "browser-verified"}:
                    errors.append(f"{path.relative_to(ROOT)}: source is not verified active")
                receipt_sources.add(str(receipt.get("source_id", "")))
        expected_receipts = {source["id"] for source in sources if source.get("rights_decision") != "repository:MIT"}
        if receipt_sources != expected_receipts:
            errors.append(f"{prefix}: link receipts differ: missing {sorted(expected_receipts - receipt_sources)}, unexpected {sorted(receipt_sources - expected_receipts)}")
    return sorted(set(errors))


def validate_authority_registry(require_receipts: bool = True) -> tuple[dict[str, Any], list[str]]:
    registry, errors = load_registry()
    if registry:
        errors.extend(validate_registry(registry, require_receipts=require_receipts))
    return registry, sorted(set(errors))


def main() -> int:
    registry, errors = validate_authority_registry()
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        "Authority registry checks passed: 382 principal authorities, "
        "19 strategic authorities, 10 regulator/redress sectors, metadata-only receipts"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
