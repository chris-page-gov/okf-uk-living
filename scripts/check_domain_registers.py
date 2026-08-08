#!/usr/bin/env python3
"""Validate staged life-course domain registers and their link receipts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml

from build_okf_bundle import ROOT
from check_service_denominator import flatten_service_families, load_service_denominator


REGISTER_ROOT = ROOT / "source" / "domain-registers"
RIGHTS_PATH = ROOT / "source" / "rights-decisions.v1.yaml"
RECORDED_RIGHTS_BASIS = "linked_reference_summary_only_source_family_decision_recorded"
REQUIRED_SOURCE_FIELDS = {
    "id", "title", "owner", "authority_role", "resource", "access_method",
    "version_model", "update_cadence", "rights_basis", "coverage", "exclusions",
    "observed_at", "checksum",
}
NATIONS = {"England", "Scotland", "Wales", "Northern Ireland"}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def load_registers() -> tuple[list[tuple[Path, dict[str, Any]]], list[str]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    errors: list[str] = []
    for path in sorted(REGISTER_ROOT.glob("*.v1.yaml")):
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.relative_to(ROOT)}: root must be a mapping")
            continue
        if value.get("register_version") == "life-course-domain-register.v1":
            result.append((path, value))
    return result, errors


def register_sources(register: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        *[item for item in register.get("route_sources", []) if isinstance(item, dict)],
        *[
            family["source"] for family in register.get("families", [])
            if isinstance(family, dict) and isinstance(family.get("source"), dict)
        ],
    ]


def validate_source(
    source: dict[str, Any], *, prefix: str, hosts: set[str], receipt_root: Path,
) -> list[str]:
    errors: list[str] = []
    source_id = str(source.get("id", "source"))
    missing = sorted(field for field in REQUIRED_SOURCE_FIELDS if not _nonempty(source.get(field)))
    if missing:
        errors.append(f"{prefix}: {source_id} missing: {', '.join(missing)}")
    parsed = urlparse(str(source.get("resource", "")))
    if parsed.scheme != "https" or not parsed.netloc:
        errors.append(f"{prefix}: {source_id} must use an HTTPS resource")
    elif parsed.netloc.lower() not in hosts:
        errors.append(f"{prefix}: {source_id} host lacks a dated rights decision")
    if source.get("rights_basis") != RECORDED_RIGHTS_BASIS:
        errors.append(f"{prefix}: {source_id} must retain the link-and-summary rights basis")
    if source.get("checksum") != "not_applicable_no_snapshot":
        errors.append(f"{prefix}: {source_id} must not claim a source snapshot")
    receipt_path = receipt_root / f"{source_id}.json"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        errors.append(f"{prefix}: {source_id} link receipt is missing or invalid: {error}")
    else:
        if receipt.get("source_id") != source_id or receipt.get("url") != source.get("resource"):
            errors.append(f"{prefix}: {source_id} link receipt identity does not match")
        if receipt.get("result") not in {"active", "redirected-active", "browser-verified-active"}:
            errors.append(f"{prefix}: {source_id} primary or handoff link is not active")
        if receipt.get("response_body_retained") is not False:
            errors.append(f"{prefix}: {source_id} receipt must retain no response body")
    return errors


def validate_domain_registers() -> list[str]:
    registers, errors = load_registers()
    denominator, denominator_errors = load_service_denominator()
    errors.extend(denominator_errors)
    denominator_rows = flatten_service_families(denominator) if denominator else []
    expected_by_domain: dict[str, set[str]] = {}
    for row in denominator_rows:
        expected_by_domain.setdefault(row["domain"], set()).add(row["id"])
    rights = yaml.safe_load(RIGHTS_PATH.read_text(encoding="utf-8")) or {}
    hosts = {
        str(item.get("host", "")).lower()
        for item in rights.get("host_decisions", []) if isinstance(item, dict)
    }
    seen_domains: set[str] = set()
    seen_families: set[str] = set()
    seen_source_ids: set[str] = set()
    for path, register in registers:
        prefix = path.relative_to(ROOT).as_posix()
        domain = str(register.get("domain", ""))
        seen_domains.add(domain)
        for field in ("pack_id", "domain", "title", "status", "observed_at", "link_receipts"):
            if not _nonempty(register.get(field)):
                errors.append(f"{prefix}: {field} must be non-empty")
        if register.get("status") != "population_complete":
            errors.append(f"{prefix}: status must be population_complete")
        acquisition = register.get("acquisition", {})
        if not isinstance(acquisition, dict):
            errors.append(f"{prefix}: acquisition must be a mapping")
            acquisition = {}
        for field in ("snapshots_acquired", "source_response_bodies_retained", "publication_allowed"):
            if acquisition.get(field) is not False:
                errors.append(f"{prefix}: acquisition.{field} must be false")
        route_sources = register.get("route_sources", [])
        route_nations = {
            str(item.get("jurisdiction", ""))
            for item in route_sources if isinstance(item, dict)
        }
        if route_nations != {"Scotland", "Wales", "Northern Ireland"}:
            errors.append(f"{prefix}: route sources must cover Scotland, Wales and Northern Ireland")
        families = register.get("families", [])
        family_ids = {
            str(item.get("id", "")) for item in families if isinstance(item, dict)
        }
        if family_ids != expected_by_domain.get(domain, set()):
            missing = sorted(expected_by_domain.get(domain, set()) - family_ids)
            extra = sorted(family_ids - expected_by_domain.get(domain, set()))
            errors.append(f"{prefix}: family denominator mismatch; missing={missing}, extra={extra}")
        duplicate_families = family_ids & seen_families
        if duplicate_families:
            errors.append(f"{prefix}: duplicate family ids: {', '.join(sorted(duplicate_families))}")
        seen_families.update(family_ids)
        for index, family in enumerate(families if isinstance(families, list) else []):
            item_prefix = f"{prefix}: families[{index}]"
            if not isinstance(family, dict):
                errors.append(f"{item_prefix} must be a mapping")
                continue
            for field in ("id", "title", "aliases", "description", "situations", "user_needs", "primary_jurisdictions", "specialist_review", "source"):
                if not _nonempty(family.get(field)):
                    errors.append(f"{item_prefix}: {field} must be non-empty")
            jurisdictions = set(family.get("primary_jurisdictions", []))
            if not jurisdictions or not jurisdictions <= NATIONS:
                errors.append(f"{item_prefix}: primary_jurisdictions must use the four governed nations")
            if family.get("specialist_review") not in {"required", "not_required", "accepted"}:
                errors.append(f"{item_prefix}: specialist_review is invalid")
        receipt_root = ROOT / str(register.get("link_receipts", ""))
        for source in register_sources(register):
            source_id = str(source.get("id", ""))
            if source_id in seen_source_ids:
                errors.append(f"{prefix}: duplicate source id across domain registers: {source_id}")
            seen_source_ids.add(source_id)
            errors.extend(validate_source(source, prefix=prefix, hosts=hosts, receipt_root=receipt_root))
    unknown_domains = seen_domains - set(expected_by_domain)
    if unknown_domains:
        errors.append(f"domain registers name unknown domains: {', '.join(sorted(unknown_domains))}")
    return sorted(set(errors))


def main() -> int:
    errors = validate_domain_registers()
    if errors:
        for error in errors:
            print(error)
        return 1
    registers, _ = load_registers()
    families = sum(len(register["families"]) for _, register in registers)
    sources = sum(len(register_sources(register)) for _, register in registers)
    print(f"Domain register checks passed: {len(registers)} domains, {families} families, {sources} active link-only sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
