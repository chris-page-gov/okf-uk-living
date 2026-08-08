#!/usr/bin/env python3
"""Validate corpus acquisition, geography, dependency and review decisions."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from check_service_denominator import load_service_denominator, validate_service_denominator


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "profiles" / "corpus-acquisition-policy.v1.yaml"
EXPECTED_PROHIBITED = {
    "source_snapshots_without_source_specific_approval",
    "source_content_redistribution",
    "provider_recommendations_or_rankings",
    "inferred_jurisdiction_or_service_equivalence",
    "personal_eligibility_legal_or_medical_decisions",
    "real_personal_data",
    "ci_or_publication_without_explicit_owner_request",
}
EXPECTED_REVIEW_ROLES = {
    "reviewer:qualified-uk-legal-procedure",
    "reviewer:registered-clinical-safety",
    "reviewer:authoritative-service-policy",
}
EXPECTED_LARGE_PREREQUISITES = {
    "REV-001_closed_relationship_authority_and_provenance",
    "REV-002_closed_node_build_provenance",
    "REV-003_closed_browser_renderable_source_handoff",
    "REV-004_closed_first_class_licence_and_notice_surface",
}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def load_corpus_policy() -> tuple[dict[str, Any], list[str]]:
    try:
        value = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as error:
        return {}, [f"{POLICY_PATH.relative_to(ROOT)}: {error}"]
    if not isinstance(value, dict):
        return {}, [f"{POLICY_PATH.relative_to(ROOT)}: root must be a mapping"]
    return value, []


def validate_corpus_policy(policy: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = POLICY_PATH.relative_to(ROOT).as_posix()
    if policy.get("policy_version") != "corpus-acquisition-policy.v1":
        errors.append(f"{prefix}: unsupported policy version")
    if policy.get("status") != "owner_approved":
        errors.append(f"{prefix}: status must record owner approval")
    if policy.get("decision_date") != "2026-08-07":
        errors.append(f"{prefix}: decision_date must retain the owner decision date")
    if policy.get("approved_by") != "owner:chris-page-gov":
        errors.append(f"{prefix}: approved_by must identify the repository owner")
    if policy.get("service_family_denominator") != "source/service-family-denominator.v1.yaml":
        errors.append(f"{prefix}: policy must bind the v1 service-family denominator")

    authority = policy.get("authority_boundary", {})
    if not isinstance(authority, dict) or authority.get("assertion_status") != "normalized":
        errors.append(f"{prefix}: authority boundary must retain normalized status")
    if not isinstance(authority, dict) or set(authority.get("prohibited", [])) != EXPECTED_PROHIBITED:
        errors.append(f"{prefix}: authority boundary must retain all prohibited actions")

    local = policy.get("local_coverage", {})
    if not isinstance(local, dict) or local.get("model") != "exhaustive_authority_registry_plus_representative_and_exception_leaf_routes":
        errors.append(f"{prefix}: local coverage model must be the approved two-layer model")
    leaf = local.get("leaf_route_layer", {}) if isinstance(local, dict) else {}
    if not isinstance(leaf, dict) or leaf.get("exhaustive_every_authority_required") is not False:
        errors.append(f"{prefix}: leaf coverage must use governed archetypes plus exceptions")

    identifiers = policy.get("geography_and_organisation_identifiers", {})
    geography = identifiers.get("administrative_geography", {}) if isinstance(identifiers, dict) else {}
    if not isinstance(geography, dict) or geography.get("primary_identifier") != "GSS_nine_character_code":
        errors.append(f"{prefix}: GSS code must be the primary administrative geography identifier")
    health_orgs = identifiers.get("health_organisations", {}) if isinstance(identifiers, dict) else {}
    if not isinstance(health_orgs, dict) or health_orgs.get("primary_identifier_where_covered") != "ODS_code":
        errors.append(f"{prefix}: ODS code must be retained where its coverage applies")
    postcode = identifiers.get("postcode", {}) if isinstance(identifiers, dict) else {}
    if not isinstance(postcode, dict) or postcode.get("storage_allowed") is not False:
        errors.append(f"{prefix}: postcode storage must remain prohibited")

    health = policy.get("health_source_permissions", {})
    if not isinstance(health, dict) or health.get("decision") != "keep_manual_link_and_original_summary_only":
        errors.append(f"{prefix}: health sources must remain manual and link-only")
    if not isinstance(health, dict) or health.get("seek_additional_provider_permission_now") is not False:
        errors.append(f"{prefix}: no provider permission request is authorized now")
    for nation in ("england", "scotland", "wales", "northern-ireland"):
        decision = health.get(nation, {}) if isinstance(health, dict) else {}
        if not isinstance(decision, dict) or "manual_link_and_original_summary_only" not in str(decision.get("mode")):
            errors.append(f"{prefix}: {nation} health mode must remain manual and link-only")

    dependencies = policy.get("private_dependencies", {})
    if not isinstance(dependencies, dict) or dependencies.get("decision") != "regulator_first":
        errors.append(f"{prefix}: private dependencies must use regulator-first discovery")
    if not isinstance(dependencies, dict) or len(dependencies.get("required_fields", [])) < 10:
        errors.append(f"{prefix}: private-dependency provenance fields are incomplete")
    redress = policy.get("sector_redress", {})
    if not isinstance(redress, dict) or redress.get("decision") != "governed_escalation_taxonomy":
        errors.append(f"{prefix}: sector redress must use the governed taxonomy")
    if not isinstance(redress, dict) or len(redress.get("sequence", [])) != 5:
        errors.append(f"{prefix}: sector redress sequence must contain five governed levels")

    review = policy.get("claim_review", {})
    coordinator = review.get("coordinator", {}) if isinstance(review, dict) else {}
    if not isinstance(coordinator, dict) or coordinator.get("reviewer") != "owner:chris-page-gov":
        errors.append(f"{prefix}: the repository owner must coordinate editorial review")
    roles = review.get("reviewer_roles", []) if isinstance(review, dict) else []
    role_ids = {str(role.get("id")) for role in roles if isinstance(role, dict)}
    if role_ids != EXPECTED_REVIEW_ROLES:
        errors.append(f"{prefix}: legal, clinical and service-policy review roles must be nominated")
    if any(not _nonempty(role.get("qualification")) for role in roles if isinstance(role, dict)):
        errors.append(f"{prefix}: every reviewer role must declare a qualification boundary")

    explorer = policy.get("explorer_large_corpus", {})
    if not isinstance(explorer, dict) or explorer.get("target_contract") != "okf-explorer-large-corpus.v1":
        errors.append(f"{prefix}: large-corpus target contract is missing")
    if not isinstance(explorer, dict) or explorer.get("decision") != "approved_for_local_evaluation":
        errors.append(f"{prefix}: large-corpus approval must be effective for local evaluation")
    if not isinstance(explorer, dict) or explorer.get("approval_effective_on") != "2026-08-07":
        errors.append(f"{prefix}: large-corpus approval must retain its effective date")
    prerequisites = set(explorer.get("prerequisites_completed", [])) if isinstance(explorer, dict) else set()
    if prerequisites != EXPECTED_LARGE_PREREQUISITES:
        errors.append(f"{prefix}: large-corpus approval must record all four completed review prerequisites")
    if not isinstance(explorer, dict) or explorer.get("publication_allowed") is not False:
        errors.append(f"{prefix}: large-corpus policy must not authorize publication")

    denominator, denominator_errors = load_service_denominator()
    errors.extend(denominator_errors)
    if denominator:
        errors.extend(validate_service_denominator(denominator))
    policy["_validated_service_family_count"] = denominator.get("_validated_family_count", 0)
    policy["_validated_reviewer_role_count"] = len(role_ids)
    return errors


def validate_policy() -> tuple[dict[str, Any], list[str]]:
    policy, errors = load_corpus_policy()
    if policy:
        errors.extend(validate_corpus_policy(policy))
    return policy, sorted(set(errors))


def main() -> int:
    policy, errors = validate_policy()
    if errors:
        for error in errors:
            print(error)
        return 1
    print(
        "Corpus policy checks passed: "
        f"{policy['_validated_service_family_count']} service families, "
        f"{policy['_validated_reviewer_role_count']} specialist reviewer roles, "
        "manual health acquisition, regulator-first dependencies"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
