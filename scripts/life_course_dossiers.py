#!/usr/bin/env python3
"""Load, resolve and validate authored life-course family dossiers."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

import yaml

from build_okf_bundle import ROOT
from check_service_denominator import flatten_service_families, load_service_denominator


DOSSIER_ROOT = ROOT / "source" / "life-course-families"
SCHEMA_PATH = ROOT / "schemas" / "life-course-family.v1.schema.json"
PROCESS_PATH = ROOT / "source" / "life-course-processes.v1.yaml"


def load_yaml(path: Path) -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{path.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{path.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def dossier_paths() -> list[Path]:
    return sorted(DOSSIER_ROOT.glob("*/*.v1.yaml"))


def source_jurisdictions(source: dict[str, Any]) -> list[str]:
    text = " ".join(
        str(source.get(key, ""))
        for key in ("coverage", "exclusions", "authority_role")
    ).lower()
    values: list[str] = []
    for label, markers in (
        ("England", ("england",)),
        ("Wales", ("wales", "welsh")),
        ("Scotland", ("scotland", "scottish")),
        ("Northern Ireland", ("northern ireland",)),
        ("Great Britain", ("great britain",)),
        ("United Kingdom", (" uk ", "united kingdom")),
    ):
        if any(marker in f" {text} " for marker in markers):
            values.append(label)
    return values or ["Source-defined"]


def normalized_source(source: dict[str, Any], register: str) -> dict[str, Any]:
    summary = str(source.get("coverage", "")).strip()
    title = str(source.get("title") or summary).strip().rstrip(".")
    if title:
        title = title[0].upper() + title[1:]
    return {
        "id": str(source.get("id", "")),
        "title": title,
        "owner": str(source.get("owner", "")),
        "authority_role": str(source.get("authority_role", "")),
        "resource": str(source.get("resource", "")),
        "jurisdiction": source_jurisdictions(source),
        "observed_at": str(source.get("observed_at", "")),
        "freshness": str(source.get("update_cadence", "")),
        "rights_decision": str(source.get("rights_basis", "")),
        "summary": summary,
        "limitations": [str(source.get("exclusions", "")).strip()],
        "snapshot": False,
        "register": register,
        "access_method": str(source.get("access_method", "")),
    }


def load_source_register(register: str) -> tuple[dict[str, dict[str, Any]], list[str]]:
    path = ROOT / register
    value, errors = load_yaml(path)
    result: dict[str, dict[str, Any]] = {}
    for source in value.get("sources", []) if isinstance(value.get("sources"), list) else []:
        if not isinstance(source, dict) or not str(source.get("id", "")):
            errors.append(f"{register}: every source must be a mapping with an id")
            continue
        source_id = str(source["id"])
        if source_id in result:
            errors.append(f"{register}: duplicate source id {source_id}")
        result[source_id] = normalized_source(source, register)
    return result, errors


def resolve_sources(dossier: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str]]:
    resolved: list[dict[str, Any]] = []
    errors: list[str] = []
    registers: dict[str, dict[str, dict[str, Any]]] = {}
    observed_ids: set[str] = set()
    for source in dossier.get("sources", []) if isinstance(dossier.get("sources"), list) else []:
        if not isinstance(source, dict):
            errors.append(f"{dossier.get('id', '<unknown>')}: source assertion must be a mapping")
            continue
        source_id = str(source.get("id", ""))
        if source_id in observed_ids:
            errors.append(f"{dossier.get('id')}: duplicate source assertion {source_id}")
        observed_ids.add(source_id)
        if "register" not in source:
            resolved.append(source)
            continue
        register = str(source.get("register", ""))
        if register not in registers:
            registers[register], register_errors = load_source_register(register)
            errors.extend(register_errors)
        candidate = registers[register].get(source_id)
        if not candidate:
            errors.append(f"{dossier.get('id')}: source {source_id} not found in {register}")
        else:
            resolved.append(candidate)
    return resolved, errors


def referenced_source_ids(value: Any, *, parent_key: str = "") -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "sources" and isinstance(child, list) and parent_key != "":
                for item in child:
                    if isinstance(item, str):
                        yield item
            elif key != "sources" or parent_key != "":
                yield from referenced_source_ids(child, parent_key=key)
    elif isinstance(value, list):
        for child in value:
            yield from referenced_source_ids(child, parent_key=parent_key)


def validate_resolved_source(source: dict[str, Any], prefix: str) -> list[str]:
    errors: list[str] = []
    for field in (
        "id", "title", "owner", "authority_role", "resource", "observed_at",
        "freshness", "rights_decision", "summary",
    ):
        if not str(source.get(field, "")).strip():
            errors.append(f"{prefix}: resolved source missing {field}")
    if not str(source.get("resource", "")).startswith("https://"):
        errors.append(f"{prefix}: resolved source URL must use HTTPS")
    if source.get("snapshot") is not False:
        errors.append(f"{prefix}: source snapshot must be false")
    limitations = source.get("limitations")
    if not isinstance(limitations, list) or not all(str(item).strip() for item in limitations):
        errors.append(f"{prefix}: source limitations must be non-empty")
    return errors


def validate_dossier(
    path: Path,
    dossier: dict[str, Any],
    denominator_by_id: dict[str, dict[str, Any]],
    process_by_family: dict[str, str],
) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    errors: list[str] = []
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    required = set(schema.get("required", []))
    for field in sorted(required - set(dossier)):
        errors.append(f"{rel}: missing required field {field}")
    if dossier.get("schema") != "life-course-family.v1":
        errors.append(f"{rel}: schema must be life-course-family.v1")
    family_id = str(dossier.get("id", ""))
    family = denominator_by_id.get(family_id)
    if not family:
        errors.append(f"{rel}: id {family_id!r} is not in the approved denominator")
    elif dossier.get("life_course_domain") != family.get("domain"):
        errors.append(f"{rel}: life-course domain does not match the denominator")
    if path.stem != f"{family_id}.v1":
        errors.append(f"{rel}: filename must match dossier id")
    process_ids = [item.get("id") for item in dossier.get("enclosing_processes", []) if isinstance(item, dict)]
    if process_by_family.get(family_id) not in process_ids:
        errors.append(f"{rel}: dossier must include its approved enclosing process")
    if not dossier.get("aliases") or not dossier.get("situations") or not dossier.get("user_needs"):
        errors.append(f"{rel}: aliases, situations and user needs must be non-empty")
    journeys = dossier.get("journeys") if isinstance(dossier.get("journeys"), dict) else {}
    if not isinstance(journeys.get("ordinary"), dict):
        errors.append(f"{rel}: ordinary journey is required")
    if not isinstance(journeys.get("exceptions"), list) or not journeys.get("exceptions"):
        errors.append(f"{rel}: at least one exception journey is required")
    for journey in [journeys.get("ordinary"), *(journeys.get("exceptions") or [])]:
        if not isinstance(journey, dict) or not journey.get("steps"):
            errors.append(f"{rel}: every journey must contain at least one step")
            continue
        for step in journey["steps"]:
            for field in schema["$defs"]["step"]["required"]:
                if field not in step:
                    errors.append(f"{rel}: step {step.get('id')} missing {field}")
    resolved, source_errors = resolve_sources(dossier)
    errors.extend(f"{rel}: {error}" for error in source_errors)
    declared_ids = {str(source.get("id")) for source in resolved}
    for source in resolved:
        errors.extend(validate_resolved_source(source, f"{rel}: {source.get('id')}"))
    missing_refs = sorted(set(referenced_source_ids(dossier)) - declared_ids)
    if missing_refs:
        errors.append(f"{rel}: undeclared source references: {', '.join(missing_refs)}")
    narrative = dossier.get("narrative") if isinstance(dossier.get("narrative"), dict) else {}
    narrative_path = ROOT / str(narrative.get("markdown", ""))
    if not narrative_path.is_file():
        errors.append(f"{rel}: narrative Markdown is missing")
    if dossier.get("status") in {"population_complete", "release_grade"}:
        if dossier.get("review", {}).get("population_gate") != "complete":
            errors.append(f"{rel}: completed dossier must pass the population gate")
        for applicability in dossier.get("applicability", []):
            if applicability.get("state") == "supported" and not applicability.get("route_variants"):
                errors.append(f"{rel}: supported jurisdiction requires a route variant")
            for variant in applicability.get("route_variants", []):
                if not str(variant.get("primary_source", "")):
                    errors.append(f"{rel}: each supported route variant requires a primary source")
    return errors


def load_dossiers() -> tuple[dict[str, dict[str, Any]], list[str]]:
    denominator, errors = load_service_denominator()
    denominator_by_id = {
        family["id"]: family for family in flatten_service_families(denominator)
    } if denominator else {}
    processes, process_errors = load_yaml(PROCESS_PATH)
    errors.extend(process_errors)
    process_by_family: dict[str, str] = {}
    for process in processes.get("processes", []) if isinstance(processes.get("processes"), list) else []:
        for family_id in process.get("families", []):
            process_by_family[str(family_id)] = str(process.get("id"))
    dossiers: dict[str, dict[str, Any]] = {}
    for path in dossier_paths():
        dossier, dossier_errors = load_yaml(path)
        errors.extend(dossier_errors)
        if not dossier:
            continue
        family_id = str(dossier.get("id", ""))
        if family_id in dossiers:
            errors.append(f"duplicate dossier id {family_id}")
        dossiers[family_id] = dossier
        errors.extend(validate_dossier(path, dossier, denominator_by_id, process_by_family))
    return dossiers, sorted(set(errors))
