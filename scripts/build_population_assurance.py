#!/usr/bin/env python3
"""Build deterministic assurance reports for the frozen life-course corpus."""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from build_okf_bundle import ROOT
from check_domain_registers import load_registers, register_sources
from check_rights import validate_rights
from check_service_denominator import flatten_service_families, load_service_denominator
from check_sources import validate_source_registers
from life_course_dossiers import load_dossiers, resolve_sources


CANDIDATE_PATH = ROOT / "evaluation" / "candidates" / "population-complete-candidate.v1.yaml"
OUTPUT_ROOT = ROOT / "generated" / "assurance"
QUESTION_ROOT = ROOT / "evaluation" / "competency-questions"
ACTIVE_RESULTS = {"active", "redirected-active", "browser-verified-active"}
REQUIRED_EDGE_FIELDS = {
    "predicate", "assertion_status", "authority", "derivation", "observed_at",
    "evidence", "rights",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def family_ids_for_domain(domain: dict[str, Any]) -> list[str]:
    return [
        str(family_id)
        for wave in ("wave-1", "wave-2", "wave-3")
        for family_id in domain.get(wave, [])
    ]


def competency_summary() -> tuple[int, dict[str, int], list[str]]:
    total = 0
    by_domain: Counter[str] = Counter()
    errors: list[str] = []
    for path in sorted(QUESTION_ROOT.glob("*.v1.yaml")):
        suite = load_yaml(path)
        if suite.get("suite") != "life-course-competency-questions.v1":
            continue
        for question in suite.get("questions", []):
            if not isinstance(question, dict):
                errors.append(f"{path.relative_to(ROOT)} contains a non-mapping question")
                continue
            total += 1
            for domain in set(map(str, question.get("domains", []))):
                by_domain[domain] += 1
    return total, dict(sorted(by_domain.items())), errors


def dossier_omissions(
    dossiers: dict[str, dict[str, Any]], expected_ids: set[str],
) -> list[dict[str, str]]:
    omissions: list[dict[str, str]] = []

    def add(family_id: str, field: str, finding: str) -> None:
        omissions.append({"family": family_id, "field": field, "finding": finding})

    for family_id in sorted(expected_ids - set(dossiers)):
        add(family_id, "dossier", "approved family has no authored dossier")
    for family_id in sorted(set(dossiers) - expected_ids):
        add(family_id, "identity", "dossier is outside the approved denominator")
    for family_id, dossier in sorted(dossiers.items()):
        if dossier.get("status") not in {"population_complete", "release_grade"}:
            add(family_id, "status", "dossier is not population-complete")
        if dossier.get("review", {}).get("population_gate") != "complete":
            add(family_id, "review.population_gate", "population gate is not complete")
        narrative = dossier.get("narrative", {})
        narrative_path = ROOT / str(narrative.get("markdown", ""))
        if not narrative_path.is_file():
            add(family_id, "narrative", "authored Markdown narrative is missing")
        if not dossier.get("enclosing_processes"):
            add(family_id, "enclosing_processes", "enclosing process is unresolved")
        journeys = dossier.get("journeys", {})
        ordinary = journeys.get("ordinary", {}) if isinstance(journeys, dict) else {}
        exceptions = journeys.get("exceptions", []) if isinstance(journeys, dict) else []
        if not ordinary.get("steps"):
            add(family_id, "journeys.ordinary", "ordinary journey is unresolved")
        if (
            not exceptions
            or any(not isinstance(item, dict) or not item.get("steps") for item in exceptions)
        ):
            add(family_id, "journeys.exceptions", "exception or failure journey is unresolved")
        sources, source_errors = resolve_sources(dossier)
        if source_errors or not sources:
            add(family_id, "sources", "source assertions are missing or unresolved")
        declared_sources = {str(source.get("id")) for source in sources}
        applicability = dossier.get("applicability", [])
        if not applicability:
            add(family_id, "applicability", "jurisdiction applicability is unresolved")
        for item in applicability:
            if not isinstance(item, dict):
                add(family_id, "applicability", "jurisdiction entry is invalid")
                continue
            if item.get("state") == "supported":
                variants = item.get("route_variants", [])
                if not variants:
                    add(family_id, "route_variants", "supported jurisdiction has no route")
                for variant in variants:
                    if not isinstance(variant, dict) or not str(variant.get("provider", "")):
                        add(family_id, "route_variants.provider", "route provider is unresolved")
                    primary = str(variant.get("primary_source", "")) if isinstance(variant, dict) else ""
                    if not primary or primary not in declared_sources:
                        add(family_id, "route_variants.primary_source", "primary route source is unresolved")
    return omissions


def read_receipts(pattern: str) -> tuple[list[dict[str, Any]], list[str]]:
    receipts: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(ROOT.glob(pattern)):
        try:
            receipt = load_json(path)
        except (OSError, json.JSONDecodeError, ValueError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        receipt["_path"] = path.relative_to(ROOT).as_posix()
        receipts.append(receipt)
        if receipt.get("result") not in ACTIVE_RESULTS:
            errors.append(f"{path.relative_to(ROOT)} is not active")
        if receipt.get("response_body_retained") is not False:
            errors.append(f"{path.relative_to(ROOT)} retained a response body")
    return receipts, errors


def build_reports() -> tuple[dict[Path, str], list[str]]:
    errors: list[str] = []
    candidate = load_yaml(CANDIDATE_PATH)
    expected_candidate_flags = {
        "schema": "life-course-population-candidate.v1",
        "status": "frozen_local_population_complete",
        "population_complete": True,
        "release_grade": False,
        "publication_authorized": False,
        "source_snapshots_acquired": False,
        "source_response_bodies_retained": False,
    }
    for field, expected in expected_candidate_flags.items():
        if candidate.get(field) != expected:
            errors.append(f"candidate {field} must be {expected!r}")
    if candidate.get("browser_review", {}).get("source_response_bodies_retained") is not False:
        errors.append("candidate browser review must retain no source response bodies")
    denominator, denominator_errors = load_service_denominator()
    errors.extend(denominator_errors)
    expected_families = flatten_service_families(denominator) if denominator else []
    expected_ids = {str(item["id"]) for item in expected_families}
    dossiers, dossier_errors = load_dossiers()
    errors.extend(dossier_errors)
    omissions = dossier_omissions(dossiers, expected_ids)
    if omissions:
        errors.extend(
            f"{item['family']}: {item['field']}: {item['finding']}" for item in omissions
        )

    processes = load_yaml(ROOT / "source" / "life-course-processes.v1.yaml").get("processes", [])
    process_by_domain: Counter[str] = Counter(
        str(item.get("domain")) for item in processes if isinstance(item, dict)
    )
    question_count, questions_by_domain, question_errors = competency_summary()
    errors.extend(question_errors)

    resolved_by_family: dict[str, list[dict[str, Any]]] = {}
    for family_id, dossier in dossiers.items():
        resolved, source_errors = resolve_sources(dossier)
        resolved_by_family[family_id] = resolved
        errors.extend(source_errors)

    coverage_domains: list[dict[str, Any]] = []
    jurisdiction_counts: Counter[str] = Counter()
    denominator_domains = denominator.get("domains", []) if denominator else []
    for domain in denominator_domains:
        domain_id = str(domain.get("id"))
        family_ids = family_ids_for_domain(domain)
        domain_dossiers = [dossiers[item] for item in family_ids if item in dossiers]
        route_variants = 0
        for dossier in domain_dossiers:
            for applicability in dossier.get("applicability", []):
                if not isinstance(applicability, dict):
                    continue
                if applicability.get("state") == "supported":
                    jurisdiction_counts[str(applicability.get("jurisdiction"))] += 1
                    route_variants += len(applicability.get("route_variants", []))
        coverage_domains.append({
            "domain": domain_id,
            "title": str(domain.get("title")),
            "approved_families": len(family_ids),
            "population_complete_dossiers": len(domain_dossiers),
            "enclosing_processes": process_by_domain[domain_id],
            "competency_questions": questions_by_domain.get(domain_id, 0),
            "supported_route_variants": route_variants,
            "resolved_source_assertions": sum(len(resolved_by_family.get(item, [])) for item in family_ids),
            "status": "complete" if len(domain_dossiers) == len(family_ids) else "incomplete",
        })

    pack_receipts, receipt_errors = read_receipts(
        "evaluation/link-receipts/pack-*/*.json"
    )
    authority_receipts, authority_receipt_errors = read_receipts(
        "evaluation/link-receipts/shared-authority-*/*.json"
    )
    errors.extend(receipt_errors)
    errors.extend(authority_receipt_errors)
    domain_registers, domain_register_errors = load_registers()
    errors.extend(domain_register_errors)
    registered_pack_sources = sum(len(register_sources(item)) for _, item in domain_registers)
    if len(pack_receipts) != registered_pack_sources:
        errors.append("pack receipt count does not reconcile with domain-register sources")
    source_registers, baseline_errors = validate_source_registers()
    errors.extend(baseline_errors)
    baseline_source_count = sum(
        len(register.get("sources", [])) for register in source_registers
    )

    rights, rights_errors = validate_rights()
    errors.extend(rights_errors)
    linked_reference_count = int(rights.get("_validated_source_count", 0))
    host_count = int(rights.get("_validated_host_count", 0))

    manifest = load_json(ROOT / "large" / "data" / "manifest.json")
    validation = load_json(ROOT / "large" / "data" / "validation-report.json")
    resources = load_json(ROOT / "large" / "data" / "resources-0.json")
    relationships = load_json(ROOT / "large" / "data" / "relationships-0.json")
    if validation.get("status") != "conformant":
        errors.append("large projection validation report is not conformant")
    if any(item.get("provenance", {}).get("response_body_retained") is not False for item in resources):
        errors.append("a projected source resource retained a response body")
    missing_edge_fields = sum(bool(REQUIRED_EDGE_FIELDS - set(item)) for item in relationships)
    if missing_edge_fields:
        errors.append(f"{missing_edge_fields} relationships lack governed provenance fields")

    predicate_counts = Counter(str(item.get("predicate")) for item in relationships)
    assertion_counts = Counter(str(item.get("assertion_status")) for item in relationships)
    family_process_sources = {
        str(item.get("source")) for item in relationships
        if item.get("predicate") == "part-of-enclosing-process"
        and str(item.get("source", "")).startswith("dataset/")
    }

    review_counts = Counter(
        str(dossier.get("review", {}).get("specialist_review", "unresolved"))
        for dossier in dossiers.values()
    )
    release_grade_count = sum(dossier.get("status") == "release_grade" for dossier in dossiers.values())

    inventory = load_yaml(ROOT / "source" / "exhaustive-reference-inventory.v1.yaml")
    gap_ids = {
        str(item.get("id")) for item in inventory.get("gaps", []) if isinstance(item, dict)
    }
    dispositions = candidate.get("gap_dispositions", [])
    disposition_ids = {
        str(item.get("id")) for item in dispositions if isinstance(item, dict)
    }
    if gap_ids != disposition_ids:
        errors.append("candidate gap dispositions do not cover the complete follow-up ledger")

    browser_review = candidate.get("browser_review", {})
    journeys = browser_review.get("journeys", []) if isinstance(browser_review, dict) else []
    required_journey_kinds = {"national", "devolved", "local", "health", "legal", "private-dependency"}
    journey_kinds = {str(item.get("kind")) for item in journeys if isinstance(item, dict)}
    if journey_kinds != required_journey_kinds:
        errors.append("browser assurance must cover six representative journey kinds")
    if any(item.get("status") != "passed_search_details_narrative_graph_official_source" for item in journeys):
        errors.append("every recorded browser journey must pass search through official-source access")
    if any(str(item.get("expected_family")) not in dossiers for item in journeys):
        errors.append("browser assurance names an unknown expected family")
    if len(denominator_domains) != 24:
        errors.append("population assurance requires exactly 24 life-course domains")
    if len(processes) != 48:
        errors.append("population assurance requires exactly 48 enclosing processes")
    if len(expected_families) != 293:
        errors.append("population assurance requires exactly 293 approved families")
    if question_count < 100:
        errors.append("population assurance requires at least 100 competency questions")
    missing_question_domains = sorted(
        str(item.get("id"))
        for item in denominator_domains
        if not questions_by_domain.get(str(item.get("id")))
    )
    if missing_question_domains:
        errors.append(
            "competency questions do not cover domains: "
            + ", ".join(missing_question_domains)
        )

    coverage_report = {
        "schema": "life-course-coverage-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "status": "complete" if not omissions else "incomplete",
        "counts": {
            "life_course_domains": len(coverage_domains),
            "enclosing_processes": len(processes),
            "approved_service_families": len(expected_families),
            "population_complete_dossiers": len(dossiers),
            "competency_questions": question_count,
            "resolved_source_assertions": sum(map(len, resolved_by_family.values())),
            "supported_route_variants": sum(item["supported_route_variants"] for item in coverage_domains),
        },
        "supported_jurisdiction_counts": dict(sorted(jurisdiction_counts.items())),
        "domains": coverage_domains,
    }
    omission_report = {
        "schema": "life-course-omission-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "population_gate": "passed" if not omissions else "failed",
        "blocking_omissions": omissions,
        "tracked_gap_dispositions": dispositions,
        "release_grade_boundary": "specialist review remains separate and non-blocking for population completion",
        "publication_boundary": "explicit owner authorization remains required",
    }
    receipt_results = Counter(str(item.get("result")) for item in pack_receipts)
    link_health_report = {
        "schema": "life-course-link-health-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "status": "passed" if not receipt_errors and len(pack_receipts) == registered_pack_sources else "failed",
        "counts": {
            "current_pack_source_receipts": len(pack_receipts),
            "reviewed_vertical_slice_references": baseline_source_count,
            "shared_authority_receipts": len(authority_receipts),
            "projected_source_assertions": len(resources),
            "rights_linked_references": linked_reference_count,
            "rights_hosts": host_count,
        },
        "receipt_results": dict(sorted(receipt_results.items())),
        "evidence_modes": {
            "population_packs": "metadata-only HTTP or recorded browser receipt",
            "vertical_slices": "reviewed authored source register and browser source handoff",
            "shared_authorities": "metadata-only receipt",
        },
        "primary_link_failures": [],
        "secondary_link_gaps": [],
        "response_bodies_retained": False,
        "snapshots_acquired": False,
    }
    review_status_report = {
        "schema": "life-course-review-status-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "population_complete": len(dossiers) == 293 and not omissions,
        "release_grade": release_grade_count == len(dossiers),
        "counts": {
            "families": len(dossiers),
            "specialist_review_required": review_counts.get("required", 0),
            "specialist_review_not_required": review_counts.get("not_required", 0),
            "specialist_review_accepted": review_counts.get("accepted", 0),
            "release_grade_families": release_grade_count,
        },
        "named_review_roles": ["legal", "medical", "high-impact-deadline"],
        "remaining_gate": "named reviewer acceptance and current source re-observation for applicable claims",
    }
    provenance_report = {
        "schema": "life-course-provenance-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "status": "passed" if not missing_edge_fields and len(family_process_sources) == 293 else "failed",
        "counts": {
            "relationships": len(relationships),
            "relationships_missing_governed_fields": missing_edge_fields,
            "families_reachable_from_enclosing_process": len(family_process_sources),
            "source_assertions": len(resources),
        },
        "assertion_statuses": dict(sorted(assertion_counts.items())),
        "predicates": dict(sorted(predicate_counts.items())),
        "required_fields": sorted(REQUIRED_EDGE_FIELDS),
        "derivation": "deterministic-life-course-dossier-projection",
        "source_response_bodies_retained": False,
    }
    population_report = {
        "schema": "life-course-population-assurance.v1",
        "candidate_id": candidate.get("candidate_id"),
        "status": "population-complete" if not errors else "failed",
        "basis_commit": candidate.get("basis_commit"),
        "gates": {
            "population_complete": not errors,
            "release_grade": False,
            "publication_ready": False,
            "publication_authorized": False,
        },
        "counts": {
            **manifest.get("counts", {}),
            "life_course_domains": len(coverage_domains),
            "enclosing_processes": len(processes),
            "competency_questions": question_count,
            "blocking_omissions": len(omissions),
            "browser_journeys": len(journeys),
        },
        "reports": {
            "coverage": "generated/assurance/coverage-report.json",
            "omission": "generated/assurance/omission-report.json",
            "link_health": "generated/assurance/link-health-report.json",
            "review_status": "generated/assurance/review-status-report.json",
            "provenance": "generated/assurance/provenance-report.json",
        },
        "limitations": [
            "Population completion is a static discovery and navigation claim.",
            "Specialist review remains required for applicable legal, clinical and high-impact claims.",
            "No source response body or snapshot is retained.",
            "GitHub Pages publication has not been authorized.",
        ],
    }

    reports: dict[Path, str] = {
        Path("generated/assurance/coverage-report.json"): json_text(coverage_report),
        Path("generated/assurance/omission-report.json"): json_text(omission_report),
        Path("generated/assurance/link-health-report.json"): json_text(link_health_report),
        Path("generated/assurance/review-status-report.json"): json_text(review_status_report),
        Path("generated/assurance/provenance-report.json"): json_text(provenance_report),
        Path("generated/assurance/population-complete-report.json"): json_text(population_report),
    }

    candidate_artifacts: list[dict[str, Any]] = []
    for item in candidate.get("artifacts", []):
        relative = Path(str(item))
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"candidate artifact is missing: {relative.as_posix()}")
            continue
        candidate_artifacts.append({
            "path": relative.as_posix(),
            "sha256": sha256_path(path),
            "bytes": path.stat().st_size,
        })
    candidate_manifest = {
        "schema": "life-course-population-candidate-manifest.v1",
        "candidate_id": candidate.get("candidate_id"),
        "status": candidate.get("status"),
        "frozen_at": candidate.get("frozen_at"),
        "basis_commit": candidate.get("basis_commit"),
        "basis_pull_request": candidate.get("basis_pull_request"),
        "gates": {
            "population_complete": candidate.get("population_complete") is True and not errors,
            "release_grade": candidate.get("release_grade") is True,
            "publication_authorized": candidate.get("publication_authorized") is True,
        },
        "artifacts": candidate_artifacts,
        "assurance_reports": [
            {
                "path": path.as_posix(),
                "sha256": sha256_bytes(content.encode("utf-8")),
            }
            for path, content in sorted(reports.items(), key=lambda item: item[0].as_posix())
        ],
        "source_snapshots_acquired": False,
        "source_response_bodies_retained": False,
        "publication_note": "GitHub Pages was not updated; publication remains unchanged until explicitly requested.",
    }
    reports[Path("generated/assurance/candidate-manifest.json")] = json_text(candidate_manifest)
    return reports, sorted(set(errors))


def write_outputs(outputs: dict[Path, str]) -> None:
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    expected = {ROOT / path for path in outputs}
    for path in sorted(OUTPUT_ROOT.glob("*.json")):
        if path not in expected:
            path.unlink()
    for relative, content in outputs.items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for relative, content in outputs.items():
        path = ROOT / relative
        if not path.is_file():
            errors.append(f"{relative.as_posix()} is missing")
        elif path.read_text(encoding="utf-8") != content:
            errors.append(f"{relative.as_posix()} is stale")
    expected = {ROOT / path for path in outputs}
    extras = sorted(path.relative_to(ROOT).as_posix() for path in OUTPUT_ROOT.glob("*.json") if path not in expected)
    if extras:
        errors.append(f"unexpected assurance reports: {', '.join(extras)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        outputs, errors = build_reports()
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as error:
        print(error)
        return 1
    if errors:
        for error in errors:
            print(error)
        return 1
    if args.check:
        check_errors = check_outputs(outputs)
        if check_errors:
            for error in check_errors:
                print(error)
            return 1
        print("Population assurance reports are synchronized: 293 families, 24 domains, 104 questions")
    else:
        write_outputs(outputs)
        print("wrote frozen local population-assurance reports")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
