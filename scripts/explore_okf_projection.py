#!/usr/bin/env python3
"""Build the bounded journey and endpoint-label projections for Explore OKF."""

from __future__ import annotations

import copy
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote, unquote, urljoin, urlsplit

from jsonschema import Draft202012Validator, FormatChecker

from build_okf_bundle import ROOT
from life_course_dossiers import load_dossiers, resolve_sources
from life_course_projection import (
    PREDICATE_BASE,
    PUBLIC_BASE,
    load_processes,
    route,
    semantic_iri,
)


JOURNEY_PROJECTION_SCHEMA = "life-course-journey-projection.v1"
JOURNEY_PROJECTION_SCHEMA_PATH = (
    ROOT / "evaluation" / "ai-consumer" / "life-course-journey-projection.schema.json"
)
JOURNEY_PROJECTION_SCHEMA_PUBLIC_PATH = Path(
    "explore/life-course-journey-projection.schema.json"
)
ENDPOINT_LABEL_INDEX_SCHEMA = "okf-explorer-endpoint-label-index.v1"
EXPLORE_OKF_PROFILE_URL = (
    "https://chris-page-gov.github.io/okf-explorer/profile/explore-okf/v1/"
)
COMMA_FRAGMENT_RULE = (
    "join-consecutive-fragments-until-terminal-punctuation-v1"
)
STEP_FACT_FLOW_MAPPING_FRAGMENT_RULE = (
    "append-null-key-fragments-to-step-fact-narrative-with-comma-space-v1"
)
STEP_FACT_FIELDS = (
    "requirements",
    "evidence",
    "rule",
    "channel",
    "cost",
    "time",
    "output",
    "outcome",
    "redress",
)
EXPECTED_COUNTS = {
    "families": 293,
    "domains": 24,
    "processes": 48,
    "specialist_review_accepted": 0,
    "specialist_review_not_required": 2,
    "specialist_review_required": 291,
}
ENDPOINT_LABEL_AUTHORITY_CLASSES = frozenset(
    {"source-native", "domain-profile", "editorial"}
)
DEFAULT_OPAQUE_IDENTIFIER_PATTERNS = (
    "activity-*",
    "catalogue-record-*",
    "publisher-*",
    "rights-*",
    "source-*",
)
MAX_ENDPOINT_LABEL_ENTRIES = 100_000
MAX_ENDPOINT_LABEL_TEXT_UNITS = 48 * 1024 * 1024
MAX_ENDPOINT_LABEL_JSON_BYTES = 64 * 1024 * 1024
LOCAL_ROUTE = re.compile(
    r"^[a-z][a-z0-9-]*(?:/(?:[A-Za-z0-9._~-]|%[0-9A-F]{2})+)+$"
)
LANGUAGE_TAG = re.compile(r"^[A-Za-z]{2,8}(?:-[A-Za-z0-9]{1,8})*$")
ABSOLUTE_IRI = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:[^\s]+$")
CONTROL_CHARACTER = re.compile(r"[\u0000-\u001f\u007f]")
UNSAFE_HTTP_URL_CHARACTER = re.compile(r"[^\x21-\x7e]|[\"'<>\\^`{|}]")
MALFORMED_PERCENT_ESCAPE = re.compile(r"%(?![0-9A-Fa-f]{2})")
INTRINSIC_OPAQUE_IDENTIFIER = re.compile(
    r"^(?:publisher|source|activity|rights|catalogue-record)-[0-9a-f]{12,}$",
    re.IGNORECASE,
)


def canonical_json_bytes(value: Any) -> bytes:
    """Return deterministic compact JSON bytes for an integrity calculation."""

    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def json_text(value: Any) -> str:
    """Return deterministic reviewable JSON text."""

    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def normalise_comma_fragments(values: Iterable[Any]) -> list[str]:
    """Rejoin YAML flow-list fragments without changing their authored order.

    The compact population packs used commas inside unquoted flow-list values.
    YAML consequently retained those clauses as adjacent list items. A clause
    ending in sentence punctuation closes one value; preceding fragments are
    joined with the commas that separated them in the authored register.
    """

    result: list[str] = []
    fragments: list[str] = []
    for value in values:
        fragment = str(value).strip()
        if not fragment:
            continue
        fragments.append(fragment)
        if fragment.endswith((".", "?", "!")):
            result.append(", ".join(fragments))
            fragments = []
    if fragments:
        result.append(", ".join(fragments))
    return result


def normalise_step_fact(value: Any) -> dict[str, str]:
    """Return one strict step fact while preserving legacy comma fragments.

    Six legacy YAML dossiers contain unquoted commas inside flow mappings. The
    YAML loader represents every clause after such a comma as an insertion-
    ordered, null-valued key. This additive projection restores those commas
    and appends every fragment to the fact's authored narrative. It does not
    alter the source dossier or relax any other malformed shape.
    """

    if not isinstance(value, dict):
        raise ValueError("step fact must be a mapping")
    state = value.get("state")
    if state == "supported":
        narrative_key = "summary"
    elif state in {"not_published_by_source", "not_applicable"}:
        narrative_key = "reason"
    else:
        raise ValueError(f"step fact has an unsupported state: {state!r}")

    narrative = value.get(narrative_key)
    if not isinstance(narrative, str) or not narrative.strip():
        raise ValueError(
            f"step fact state {state!r} requires a non-empty {narrative_key}"
        )

    fragments: list[str] = []
    for key, fragment_value in value.items():
        if key in {"state", narrative_key}:
            continue
        if not isinstance(key, str) or not key.strip() or fragment_value is not None:
            raise ValueError(
                "step fact has a non-canonical property that is not a legacy "
                "null-key comma fragment"
            )
        fragments.append(key.strip())

    restored_narrative = ", ".join((narrative, *fragments))
    return {"state": state, narrative_key: restored_narrative}


def encode_endpoint_route_segment(value: str) -> str:
    """Encode one canonical Explore OKF endpoint-route segment."""

    if not isinstance(value, str) or not value:
        raise ValueError("endpoint route segment must be a non-empty string")
    return quote(value, safe="-._~", encoding="utf-8", errors="strict")


def metadata_endpoint_route(kind: str, value: str) -> str:
    """Build the canonical route for a metadata-projected graph endpoint."""

    if not re.fullmatch(r"[a-z][a-z0-9-]*", kind):
        raise ValueError("endpoint route kind is malformed")
    return f"{kind}/{encode_endpoint_route_segment(value)}"


def _canonical_local_route(value: str) -> bool:
    if not LOCAL_ROUTE.fullmatch(value):
        return False
    parts = value.split("/")
    try:
        return all(
            segment
            and encode_endpoint_route_segment(
                unquote(segment, encoding="utf-8", errors="strict")
            )
            == segment
            for segment in parts[1:]
        )
    except (UnicodeDecodeError, ValueError):
        return False


def _safe_http_url(value: Any, *, https_only: bool = False) -> bool:
    if not isinstance(value, str) or not value or value.strip() != value:
        return False
    if UNSAFE_HTTP_URL_CHARACTER.search(value) or MALFORMED_PERCENT_ESCAPE.search(value):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    schemes = {"https"} if https_only else {"http", "https"}
    return bool(
        parsed.scheme in schemes
        and parsed.netloc
        and parsed.hostname
        and not parsed.username
        and not parsed.password
        and port != 0
    )


def _unique_preserving_order(values: Iterable[Any]) -> list[str]:
    result: list[str] = []
    observed: set[str] = set()
    for value in values:
        item = str(value).strip()
        if item and item not in observed:
            observed.add(item)
            result.append(item)
    return result


def _relationship_indexes(
    relationships: list[dict[str, Any]],
) -> tuple[
    dict[str, dict[str, Any]],
    dict[tuple[str, str, str], list[dict[str, Any]]],
]:
    by_id: dict[str, dict[str, Any]] = {}
    by_route: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for position, relationship in enumerate(relationships):
        if not isinstance(relationship, dict):
            raise ValueError(f"relationship {position + 1} must be a mapping")
        assertion_id = str(relationship.get("id") or "").strip()
        if not assertion_id:
            raise ValueError(f"relationship {position + 1} has no assertion id")
        if assertion_id in by_id:
            raise ValueError(f"duplicate relationship assertion id: {assertion_id}")
        by_id[assertion_id] = relationship
        key = (
            str(relationship.get("source") or ""),
            str(relationship.get("target") or ""),
            str(relationship.get("predicate") or ""),
        )
        by_route[key].append(relationship)
    return by_id, by_route


def _assertion_id(
    relationship_index: dict[tuple[str, str, str], list[dict[str, Any]]],
    source: str,
    target: str,
    predicate_name: str,
) -> str:
    predicate = f"{PREDICATE_BASE}{predicate_name}"
    matches = relationship_index.get((source, target, predicate), [])
    if len(matches) != 1:
        raise ValueError(
            "expected one relationship assertion for "
            f"{source} -> {predicate_name} -> {target}; found {len(matches)}"
        )
    return str(matches[0]["id"])


def _explicit_source_jurisdictions(
    applicability: list[dict[str, Any]],
) -> dict[str, list[str]]:
    result: dict[str, list[str]] = defaultdict(list)
    for item in applicability:
        jurisdiction = str(item.get("jurisdiction") or "").strip()
        source_ids = [
            *item.get("sources", []),
            *(
                variant.get("primary_source")
                for variant in item.get("route_variants", [])
                if isinstance(variant, dict)
            ),
        ]
        for source_id in _unique_preserving_order(source_ids):
            if jurisdiction and jurisdiction not in result[source_id]:
                result[source_id].append(jurisdiction)
    return dict(result)


def _project_applicability(dossier: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in dossier["applicability"]:
        variants = []
        for variant in item.get("route_variants", []):
            projected_variant = {
                "id": str(variant["id"]),
                "provider": str(variant["provider"]),
                "primary_source": str(variant["primary_source"]),
            }
            for optional in ("route_kind", "geographic_identifier"):
                if str(variant.get(optional) or "").strip():
                    projected_variant[optional] = str(variant[optional])
            variants.append(projected_variant)
        source_ids = _unique_preserving_order(
            [
                *item.get("sources", []),
                *(variant["primary_source"] for variant in variants),
            ]
        )
        result.append(
            {
                "jurisdiction": str(item["jurisdiction"]),
                "state": str(item["state"]),
                "source_ids": source_ids,
                "route_variants": variants,
            }
        )
    return result


def _resource_for_source(
    resource_by_id: dict[str, dict[str, Any]], family_id: str, source_id: str
) -> dict[str, Any]:
    resource_id = f"resource:{family_id}:{source_id}"
    resource = resource_by_id.get(resource_id)
    if resource is None:
        raise ValueError(f"projected resource is missing: {resource_id}")
    if resource.get("dataset") != family_id:
        raise ValueError(f"projected resource has the wrong family: {resource_id}")
    return resource


def _project_sources(
    dossier: dict[str, Any],
    resources: dict[str, dict[str, Any]],
    explicit_jurisdictions: dict[str, list[str]],
    relationship_index: dict[tuple[str, str, str], list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    family_id = str(dossier["id"])
    resolved, errors = resolve_sources(dossier)
    if errors:
        raise ValueError("; ".join(errors))
    result: list[dict[str, Any]] = []
    for position, source in enumerate(resolved):
        source_id = str(source["id"])
        resource = _resource_for_source(resources, family_id, source_id)
        jurisdictions = explicit_jurisdictions.get(source_id, [])
        if resource.get("position") != position:
            raise ValueError(
                f"{family_id}: source order differs from the projected resource: {source_id}"
            )
        url = str(source["resource"])
        if not _safe_http_url(url, https_only=True):
            raise ValueError(f"{family_id}: source URL is not safe HTTPS: {source_id}")
        result.append(
            {
                "id": source_id,
                "resource_id": str(resource["id"]),
                "route": str(resource["route"]),
                "position": position,
                "relationship_assertion": _assertion_id(
                    relationship_index,
                    route("dataset", family_id),
                    str(resource["route"]),
                    "supported-by-source",
                ),
                "title": str(source["title"]),
                "owner": str(source["owner"]),
                "authority_role": str(source["authority_role"]),
                "url": url,
                "jurisdictions": jurisdictions,
                "jurisdiction_basis": "explicit-family-applicability",
                "observed_at": str(source["observed_at"]),
                "freshness": str(source["freshness"]),
                "rights_decision": str(source["rights_decision"]),
                "summary": str(source["summary"]),
                "limitations": [str(item) for item in source["limitations"]],
            }
        )
    return result


def _project_step(
    *,
    family_id: str,
    journey_id: str,
    episode_route: str,
    step: dict[str, Any],
    order: int,
    previous_step: dict[str, Any] | None,
    next_step: dict[str, Any] | None,
    relationship_index: dict[tuple[str, str, str], list[dict[str, Any]]],
    resource_by_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    step_route = route(
        "service-step", f"{family_id}-{journey_id}-{step['id']}"
    )
    assertions: dict[str, Any] = {
        "episode_step": _assertion_id(
            relationship_index, episode_route, step_route, "has-episode"
        ),
        "sources": [],
    }
    if previous_step is not None:
        previous_route = route(
            "service-step",
            f"{family_id}-{journey_id}-{previous_step['id']}",
        )
        assertions["follows_previous"] = _assertion_id(
            relationship_index, step_route, previous_route, "follows"
        )
    if next_step is not None:
        next_route = route(
            "service-step", f"{family_id}-{journey_id}-{next_step['id']}"
        )
        assertions["precedes_next"] = _assertion_id(
            relationship_index, step_route, next_route, "precedes"
        )
    for source_id in _unique_preserving_order(step["sources"]):
        resource = _resource_for_source(resource_by_id, family_id, source_id)
        resource_route = str(resource["route"])
        assertions["sources"].append(
            {
                "source_id": source_id,
                "resource_route": resource_route,
                "assertion_id": _assertion_id(
                    relationship_index,
                    step_route,
                    resource_route,
                    "supported-by-source",
                ),
            }
        )
    return {
        "id": str(step["id"]),
        "route": step_route,
        "order": order,
        "interaction": str(step["interaction"]),
        "provider": str(step["provider"]),
        **{
            field: normalise_step_fact(step[field])
            for field in STEP_FACT_FIELDS
        },
        "assertion_status": str(step["assertion_status"]),
        "source_ids": _unique_preserving_order(step["sources"]),
        "relationship_assertions": assertions,
    }


def _project_episodes(
    *,
    dossier: dict[str, Any],
    process_route: str,
    relationship_index: dict[tuple[str, str, str], list[dict[str, Any]]],
    resource_by_id: dict[str, dict[str, Any]],
    row_by_route: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    family_id = str(dossier["id"])
    family_route = route("dataset", family_id)
    journeys = [
        ("ordinary", dossier["journeys"]["ordinary"]),
        *(("exception", item) for item in dossier["journeys"]["exceptions"]),
    ]
    episodes: list[dict[str, Any]] = []
    for episode_order, (kind, journey) in enumerate(journeys):
        journey_id = str(journey["id"])
        episode_route = route("service-episode", f"{family_id}-{journey_id}")
        episode_row = row_by_route.get(episode_route)
        if episode_row is None:
            raise ValueError(f"projected episode row is missing: {episode_route}")
        steps = list(journey["steps"])
        episodes.append(
            {
                "id": journey_id,
                "route": episode_route,
                "title": str(episode_row["title"]),
                "kind": kind,
                "order": episode_order,
                "entry_state": str(journey["entry_state"]),
                "outcome": str(journey["outcome"]),
                "relationship_assertions": {
                    "family_episode": _assertion_id(
                        relationship_index,
                        family_route,
                        episode_route,
                        "has-episode",
                    ),
                    "enclosing_process": _assertion_id(
                        relationship_index,
                        episode_route,
                        process_route,
                        "part-of-enclosing-process",
                    ),
                },
                "steps": [
                    _project_step(
                        family_id=family_id,
                        journey_id=journey_id,
                        episode_route=episode_route,
                        step=step,
                        order=step_order,
                        previous_step=steps[step_order - 1]
                        if step_order > 0
                        else None,
                        next_step=steps[step_order + 1]
                        if step_order + 1 < len(steps)
                        else None,
                        relationship_index=relationship_index,
                        resource_by_id=resource_by_id,
                    )
                    for step_order, step in enumerate(steps)
                ],
            }
        )
    return episodes


def projection_assertion_references(projection: dict[str, Any]) -> list[str]:
    """Return every assertion identifier referenced by a journey projection."""

    result: list[str] = []
    for family in projection.get("families", []):
        if not isinstance(family, dict):
            continue
        family_assertions = family.get("relationship_assertions", {})
        if isinstance(family_assertions, dict):
            result.extend(str(value) for value in family_assertions.values())
        for source in family.get("sources", []):
            if isinstance(source, dict) and source.get("relationship_assertion"):
                result.append(str(source["relationship_assertion"]))
        for episode in family.get("episodes", []):
            if not isinstance(episode, dict):
                continue
            episode_assertions = episode.get("relationship_assertions", {})
            if isinstance(episode_assertions, dict):
                result.extend(str(value) for value in episode_assertions.values())
            for step in episode.get("steps", []):
                if not isinstance(step, dict):
                    continue
                step_assertions = step.get("relationship_assertions", {})
                if not isinstance(step_assertions, dict):
                    continue
                for key in ("episode_step", "follows_previous", "precedes_next"):
                    if step_assertions.get(key):
                        result.append(str(step_assertions[key]))
                for source in step_assertions.get("sources", []):
                    if isinstance(source, dict) and source.get("assertion_id"):
                        result.append(str(source["assertion_id"]))
    return result


def build_journey_projection(
    rows: list[dict[str, Any]],
    resources: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    *,
    source_identity: dict[str, Any],
    snapshot: str,
    generated_at_value: str,
) -> dict[str, Any]:
    """Build the deterministic, ordinary-first citizen journey projection."""

    dossiers, errors = load_dossiers()
    if errors:
        raise ValueError("; ".join(errors))
    processes = load_processes()
    process_by_family = {
        str(family_id): process
        for process in processes
        for family_id in process.get("families", [])
    }
    row_by_route = {str(row.get("route")): row for row in rows}
    resource_by_id = {str(resource.get("id")): resource for resource in resources}
    _, relationship_index = _relationship_indexes(relationships)

    families: list[dict[str, Any]] = []
    for family_id in sorted(dossiers):
        dossier = dossiers[family_id]
        family_route = route("dataset", family_id)
        family_row = row_by_route.get(family_route)
        if family_row is None:
            raise ValueError(f"projected family row is missing: {family_route}")
        process = process_by_family.get(family_id)
        if process is None:
            raise ValueError(f"approved enclosing process is missing: {family_id}")
        process_id = str(process["id"])
        process_route = route("enclosing-process", process_id)
        process_row = row_by_route.get(process_route)
        domain_id = str(dossier["life_course_domain"])
        domain_route = route("life-course-domain", domain_id)
        domain_row = row_by_route.get(domain_route)
        if process_row is None or domain_row is None:
            raise ValueError(f"projected process or domain row is missing: {family_id}")

        explicit_jurisdictions = _explicit_source_jurisdictions(
            dossier["applicability"]
        )
        related_families: list[dict[str, Any]] = []
        for related_id in sorted(
            str(item) for item in process.get("families", []) if item != family_id
        ):
            related_route = route("dataset", related_id)
            related_row = row_by_route.get(related_route)
            if related_row is None:
                raise ValueError(f"related family row is missing: {related_route}")
            related_families.append(
                {
                    "id": related_id,
                    "route": related_route,
                    "title": str(related_row["title"]),
                    "relationship": "shared-enclosing-process",
                    "sequenced": False,
                }
            )

        narrative = family_row.get("narrative")
        if not isinstance(narrative, dict) or not str(narrative.get("body") or ""):
            raise ValueError(f"projected narrative is missing: {family_id}")
        families.append(
            {
                "id": family_id,
                "route": family_route,
                "title": str(dossier["title"]),
                "description": str(dossier["description"]),
                "aliases": [str(item) for item in dossier["aliases"]],
                "situations": normalise_comma_fragments(dossier["situations"]),
                "user_needs": normalise_comma_fragments(dossier["user_needs"]),
                "interaction_boundary": str(dossier["interaction_boundary"]),
                "status": str(dossier["status"]),
                "assertion_status": str(dossier["assertion_status"]),
                "domain": {
                    "id": domain_id,
                    "route": domain_route,
                    "title": str(domain_row["title"]),
                },
                "process": {
                    "id": process_id,
                    "route": process_route,
                    "title": str(process_row["title"]),
                },
                "review": {
                    "population_gate": str(dossier["review"]["population_gate"]),
                    "specialist_review": str(
                        dossier["review"]["specialist_review"]
                    ),
                },
                "limitations": [str(item) for item in dossier["limitations"]],
                "applicability": _project_applicability(dossier),
                "sources": _project_sources(
                    dossier,
                    resource_by_id,
                    explicit_jurisdictions,
                    relationship_index,
                ),
                "episodes": _project_episodes(
                    dossier=dossier,
                    process_route=process_route,
                    relationship_index=relationship_index,
                    resource_by_id=resource_by_id,
                    row_by_route=row_by_route,
                ),
                "related_families": related_families,
                "narrative": {
                    "source": str(dossier["narrative"]["markdown"]),
                    "process_context": str(
                        dossier["narrative"]["process_context"]
                    ),
                    "title": str(narrative["title"]),
                    "body": str(narrative["body"]),
                },
                "relationship_assertions": {
                    "life_course_domain": _assertion_id(
                        relationship_index,
                        family_route,
                        domain_route,
                        "belongs-to-life-course-domain",
                    ),
                    "enclosing_process": _assertion_id(
                        relationship_index,
                        family_route,
                        process_route,
                        "part-of-enclosing-process",
                    ),
                },
            }
        )

    review_counts = Counter(
        family["review"]["specialist_review"] for family in families
    )
    projection: dict[str, Any] = {
        "schema": JOURNEY_PROJECTION_SCHEMA,
        "generated_at": generated_at_value,
        "default_language": "en-GB",
        "snapshot": snapshot,
        "normalisation": {
            "comma_fragments": COMMA_FRAGMENT_RULE,
            "step_fact_flow_mapping_fragments": (
                STEP_FACT_FLOW_MAPPING_FRAGMENT_RULE
            ),
        },
        "source_identity": copy.deepcopy(source_identity),
        "counts": {
            "families": len(families),
            "domains": len({family["domain"]["id"] for family in families}),
            "processes": len({family["process"]["id"] for family in families}),
            "aliases": sum(len(family["aliases"]) for family in families),
            "sources": sum(len(family["sources"]) for family in families),
            "episodes": sum(len(family["episodes"]) for family in families),
            "steps": sum(
                len(episode["steps"])
                for family in families
                for episode in family["episodes"]
            ),
            "relationship_assertion_references": 0,
            "specialist_review_accepted": review_counts["accepted"],
            "specialist_review_not_required": review_counts["not_required"],
            "specialist_review_required": review_counts["required"],
        },
        "families": families,
    }
    projection["counts"]["relationship_assertion_references"] = len(
        projection_assertion_references(projection)
    )
    validation_errors = validate_journey_projection(
        projection, relationships=relationships
    )
    if validation_errors:
        raise ValueError(
            "invalid journey projection:\n- " + "\n- ".join(validation_errors)
        )
    return projection


def _schema_errors(value: dict[str, Any]) -> list[str]:
    schema = json.loads(JOURNEY_PROJECTION_SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: list[str] = []
    for error in sorted(validator.iter_errors(value), key=lambda item: list(item.path)):
        path = "/" + "/".join(str(item) for item in error.absolute_path)
        errors.append(f"{path}: {error.message}")
    return errors


def _expected_assertion(
    errors: list[str],
    by_id: dict[str, dict[str, Any]],
    assertion_id: Any,
    source: str,
    target: str,
    predicate_name: str,
    context: str,
) -> None:
    relationship = by_id.get(str(assertion_id))
    if relationship is None:
        errors.append(f"{context}: assertion id is absent from the full graph")
        return
    expected = (source, target, f"{PREDICATE_BASE}{predicate_name}")
    actual = (
        relationship.get("source"),
        relationship.get("target"),
        relationship.get("predicate"),
    )
    if actual != expected:
        errors.append(
            f"{context}: assertion endpoints or predicate differ from the full graph"
        )


def validate_journey_projection(
    projection: dict[str, Any],
    *,
    relationships: list[dict[str, Any]] | None = None,
) -> list[str]:
    """Validate structure, counts, order, applicability and graph references."""

    errors = _schema_errors(projection)
    if errors:
        return errors
    if projection.get("normalisation") != {
        "comma_fragments": COMMA_FRAGMENT_RULE,
        "step_fact_flow_mapping_fragments": (
            STEP_FACT_FLOW_MAPPING_FRAGMENT_RULE
        ),
    }:
        errors.append("normalisation does not declare the governed projection rules")
    source_identity = projection["source_identity"]
    if not _safe_http_url(source_identity["bundle_url"], https_only=True):
        errors.append("source_identity.bundle_url must be credential-free HTTPS")
    for name in (
        "bundle_descriptor",
        "data_manifest",
        "relationship_runtime",
        "candidate_manifest",
        "review_status",
    ):
        path = Path(source_identity[name]["path"])
        if path.is_absolute() or ".." in path.parts:
            errors.append(f"source_identity.{name}.path is unsafe")

    families = projection["families"]
    family_ids = [family["id"] for family in families]
    if family_ids != sorted(family_ids):
        errors.append("families are not in deterministic id order")
    if len(family_ids) != len(set(family_ids)):
        errors.append("family ids are duplicated")
    family_by_id = {family["id"]: family for family in families}

    actual_counts = {
        "families": len(families),
        "domains": len({family["domain"]["id"] for family in families}),
        "processes": len({family["process"]["id"] for family in families}),
        "aliases": sum(len(family["aliases"]) for family in families),
        "sources": sum(len(family["sources"]) for family in families),
        "episodes": sum(len(family["episodes"]) for family in families),
        "steps": sum(
            len(episode["steps"])
            for family in families
            for episode in family["episodes"]
        ),
        "relationship_assertion_references": len(
            projection_assertion_references(projection)
        ),
        "specialist_review_accepted": sum(
            family["review"]["specialist_review"] == "accepted"
            for family in families
        ),
        "specialist_review_not_required": sum(
            family["review"]["specialist_review"] == "not_required"
            for family in families
        ),
        "specialist_review_required": sum(
            family["review"]["specialist_review"] == "required"
            for family in families
        ),
    }
    if projection["counts"] != actual_counts:
        errors.append("counts do not reconcile with the journey projection")
    for key, expected in EXPECTED_COUNTS.items():
        if actual_counts.get(key) != expected:
            errors.append(f"{key} must be {expected}, found {actual_counts.get(key)}")

    by_id: dict[str, dict[str, Any]] = {}
    if relationships is not None:
        try:
            by_id, _ = _relationship_indexes(relationships)
        except ValueError as error:
            errors.append(str(error))

    for family in families:
        family_id = family["id"]
        family_route = family["route"]
        process_route = family["process"]["route"]
        domain_route = family["domain"]["route"]
        episodes = family["episodes"]
        if episodes[0]["kind"] != "ordinary" or episodes[0]["order"] != 0:
            errors.append(f"{family_id}: the ordinary episode must be first")
        if [episode["order"] for episode in episodes] != list(range(len(episodes))):
            errors.append(f"{family_id}: episode order is not contiguous")
        if any(episode["kind"] != "exception" for episode in episodes[1:]):
            errors.append(f"{family_id}: non-ordinary episodes must be exceptions")

        source_jurisdictions: dict[str, list[str]] = defaultdict(list)
        for applicability in family["applicability"]:
            jurisdiction = applicability["jurisdiction"]
            for source_id in applicability["source_ids"]:
                if jurisdiction not in source_jurisdictions[source_id]:
                    source_jurisdictions[source_id].append(jurisdiction)
        for source in family["sources"]:
            if source["jurisdictions"] != source_jurisdictions[source["id"]]:
                errors.append(
                    f"{family_id}: source {source['id']} jurisdictions do not "
                    "match explicit applicability"
                )
            if not _safe_http_url(source["url"], https_only=True):
                errors.append(f"{family_id}: source {source['id']} URL is unsafe")
            if by_id:
                _expected_assertion(
                    errors,
                    by_id,
                    source["relationship_assertion"],
                    family_route,
                    source["route"],
                    "supported-by-source",
                    f"{family_id} source {source['id']}",
                )

        related_ids = [item["id"] for item in family["related_families"]]
        if related_ids != sorted(related_ids):
            errors.append(f"{family_id}: related-family grouping is not sorted")
        for related in family["related_families"]:
            target = family_by_id.get(related["id"])
            if target is None or target["process"]["id"] != family["process"]["id"]:
                errors.append(
                    f"{family_id}: related family does not share its enclosing process"
                )
            if related["sequenced"] is not False:
                errors.append(f"{family_id}: related family must not imply sequence")

        if by_id:
            family_assertions = family["relationship_assertions"]
            _expected_assertion(
                errors,
                by_id,
                family_assertions["life_course_domain"],
                family_route,
                domain_route,
                "belongs-to-life-course-domain",
                f"{family_id} life-course domain",
            )
            _expected_assertion(
                errors,
                by_id,
                family_assertions["enclosing_process"],
                family_route,
                process_route,
                "part-of-enclosing-process",
                f"{family_id} enclosing process",
            )

        for episode in episodes:
            episode_route = episode["route"]
            steps = episode["steps"]
            if [step["order"] for step in steps] != list(range(len(steps))):
                errors.append(
                    f"{family_id}/{episode['id']}: step order is not contiguous"
                )
            if by_id:
                episode_assertions = episode["relationship_assertions"]
                _expected_assertion(
                    errors,
                    by_id,
                    episode_assertions["family_episode"],
                    family_route,
                    episode_route,
                    "has-episode",
                    f"{family_id}/{episode['id']} family episode",
                )
                _expected_assertion(
                    errors,
                    by_id,
                    episode_assertions["enclosing_process"],
                    episode_route,
                    process_route,
                    "part-of-enclosing-process",
                    f"{family_id}/{episode['id']} enclosing process",
                )
            for position, step in enumerate(steps):
                step_route = step["route"]
                assertions = step["relationship_assertions"]
                if by_id:
                    _expected_assertion(
                        errors,
                        by_id,
                        assertions["episode_step"],
                        episode_route,
                        step_route,
                        "has-episode",
                        f"{family_id}/{episode['id']}/{step['id']} episode step",
                    )
                    if position > 0:
                        _expected_assertion(
                            errors,
                            by_id,
                            assertions.get("follows_previous"),
                            step_route,
                            steps[position - 1]["route"],
                            "follows",
                            f"{family_id}/{episode['id']}/{step['id']} follows",
                        )
                    elif "follows_previous" in assertions:
                        errors.append(
                            f"{family_id}/{episode['id']}/{step['id']}: first "
                            "step declares follows_previous"
                        )
                    if position + 1 < len(steps):
                        _expected_assertion(
                            errors,
                            by_id,
                            assertions.get("precedes_next"),
                            step_route,
                            steps[position + 1]["route"],
                            "precedes",
                            f"{family_id}/{episode['id']}/{step['id']} precedes",
                        )
                    elif "precedes_next" in assertions:
                        errors.append(
                            f"{family_id}/{episode['id']}/{step['id']}: last "
                            "step declares precedes_next"
                        )
                    for source in assertions["sources"]:
                        _expected_assertion(
                            errors,
                            by_id,
                            source["assertion_id"],
                            step_route,
                            source["resource_route"],
                            "supported-by-source",
                            f"{family_id}/{episode['id']}/{step['id']} source "
                            f"{source['source_id']}",
                        )
    return sorted(set(errors))


def _absolute_label_source(value: Any) -> str:
    source = str(value or "").strip()
    if not source:
        return EXPLORE_OKF_PROFILE_URL
    absolute = source if urlsplit(source).scheme else urljoin(PUBLIC_BASE, source)
    if not _safe_http_url(absolute):
        raise ValueError(f"endpoint label authority source is unsafe: {source}")
    return absolute


def _endpoint_entry(
    *,
    endpoint_route: str,
    label: str,
    type_label: str,
    authority_class: str,
    authority_source: str,
) -> dict[str, Any]:
    return {
        "route": endpoint_route,
        "iri": semantic_iri(endpoint_route),
        "label": label.strip(),
        "language": "en-GB",
        "type": type_label.strip(),
        "label_authority": {
            "class": authority_class,
            "source": _absolute_label_source(authority_source),
        },
    }


def _add_endpoint_entry(
    entries: dict[str, dict[str, Any]], entry: dict[str, Any]
) -> None:
    endpoint_route = str(entry["route"])
    existing = entries.get(endpoint_route)
    if existing is not None and existing != entry:
        raise ValueError(f"conflicting endpoint labels for route: {endpoint_route}")
    entries[endpoint_route] = entry


def build_endpoint_label_index(
    rows: list[dict[str, Any]],
    resources: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    *,
    snapshot: str,
    generated_at_value: str,
) -> dict[str, Any]:
    """Build complete labels for graph and metadata-projected endpoints."""

    entries: dict[str, dict[str, Any]] = {}
    for row in rows:
        endpoint_route = str(row.get("route") or "").strip()
        if not endpoint_route:
            raise ValueError("projected record has no route")
        type_label = str(row.get("record_type") or "Concept")
        label = str(row.get("title") or "").strip()
        if _is_opaque(label, list(DEFAULT_OPAQUE_IDENTIFIER_PATTERNS)):
            # Keep readable source-authored wording while ensuring a generic
            # phrase such as "Source-defined ..." cannot masquerade as an
            # opaque source identifier in Explorer.
            label = f"{type_label}: {label}"
        _add_endpoint_entry(
            entries,
            _endpoint_entry(
                endpoint_route=endpoint_route,
                label=label,
                type_label=type_label,
                authority_class=(
                    "source-native"
                    if row.get("assertion_status") == "official"
                    else "domain-profile"
                ),
                authority_source=str(row.get("source_url") or ""),
            ),
        )
        metadata = (
            ("publisher", [row.get("publisher")], "Project"),
            ("format", list(row.get("formats") or [])[:8], "Format"),
            ("topic", list(row.get("topics") or [])[:8], "Topic"),
            ("tag", list(row.get("tags") or [])[:8], "Tag"),
            ("license", [row.get("license_id")], "Licence"),
        )
        for kind, values, type_label in metadata:
            for raw_value in values:
                value = str(raw_value or "").strip()
                if not value:
                    continue
                label = "A Life in the UK" if kind == "publisher" and value == "okf-uk-living" else value
                _add_endpoint_entry(
                    entries,
                    _endpoint_entry(
                        endpoint_route=metadata_endpoint_route(kind, value),
                        label=label,
                        type_label=type_label,
                        authority_class="domain-profile",
                        authority_source=EXPLORE_OKF_PROFILE_URL,
                    ),
                )

    for resource in resources:
        endpoint_route = str(resource.get("route") or "").strip()
        _add_endpoint_entry(
            entries,
            _endpoint_entry(
                endpoint_route=endpoint_route,
                label=str(resource.get("name") or ""),
                type_label="Authoritative source link",
                authority_class="source-native",
                authority_source=str(resource.get("url") or ""),
            ),
        )

    graph_reachable_routes = set(entries)
    for relationship in relationships:
        graph_reachable_routes.update(
            {
                str(relationship.get("source") or "").strip(),
                str(relationship.get("target") or "").strip(),
            }
        )
    if "" in graph_reachable_routes:
        raise ValueError("relationship graph contains an empty endpoint route")
    missing_entries = sorted(graph_reachable_routes.difference(entries))
    if missing_entries:
        raise ValueError(
            "graph-reachable routes have no label entries: "
            + ", ".join(missing_entries[:20])
        )

    index = {
        "schema": ENDPOINT_LABEL_INDEX_SCHEMA,
        "snapshot": snapshot,
        "generated_at": generated_at_value,
        "default_language": "en-GB",
        "opaque_identifier_patterns": list(DEFAULT_OPAQUE_IDENTIFIER_PATTERNS),
        "entries": [entries[key] for key in sorted(entries)],
        "counts": {"entries": len(entries)},
    }
    validation_errors = validate_endpoint_label_index(
        index, graph_reachable_routes=graph_reachable_routes
    )
    if validation_errors:
        raise ValueError(
            "invalid endpoint label index:\n- " + "\n- ".join(validation_errors)
        )
    return index


def _matches_opaque_pattern(value: str, pattern: str) -> bool:
    candidates = {value.casefold(), value.rsplit("/", 1)[-1].casefold()}
    if pattern.endswith("*"):
        prefix = pattern[:-1].casefold()
        return any(candidate.startswith(prefix) for candidate in candidates)
    return pattern.casefold() in candidates


def _is_opaque(value: str, patterns: list[str]) -> bool:
    return bool(
        INTRINSIC_OPAQUE_IDENTIFIER.fullmatch(value.rsplit("/", 1)[-1])
        or any(_matches_opaque_pattern(value, pattern) for pattern in patterns)
    )


def _utf16_text_units(value: str) -> int:
    return len(value.encode("utf-16-le")) // 2


def validate_endpoint_label_index(
    index: dict[str, Any],
    *,
    graph_reachable_routes: set[str] | None = None,
) -> list[str]:
    """Validate the strict canonical Explore OKF v1 endpoint-label contract."""

    errors: list[str] = []
    required = {
        "schema",
        "snapshot",
        "default_language",
        "opaque_identifier_patterns",
        "entries",
        "counts",
    }
    allowed = required | {"generated_at"}
    if set(index) - allowed or required - set(index):
        errors.append("endpoint label index contains missing or unsupported fields")
        return errors
    if index.get("schema") != ENDPOINT_LABEL_INDEX_SCHEMA:
        errors.append("endpoint label index schema is unsupported")
    if index.get("default_language") != "en-GB":
        errors.append("endpoint label index default language must be en-GB")
    if not str(index.get("snapshot") or "").strip():
        errors.append("endpoint label index snapshot is missing")
    generated_at = str(index.get("generated_at") or "")
    if generated_at and "T" not in generated_at:
        errors.append("endpoint label index generated_at is not a date-time")

    patterns = index.get("opaque_identifier_patterns")
    entries = index.get("entries")
    counts = index.get("counts")
    if not isinstance(patterns, list) or len(patterns) > 64:
        errors.append("opaque identifier patterns are malformed or unbounded")
        return errors
    if len(patterns) != len(set(str(pattern) for pattern in patterns)):
        errors.append("opaque identifier patterns are duplicated")
    for position, pattern_value in enumerate(patterns):
        pattern = str(pattern_value)
        if (
            not re.fullmatch(r"[A-Za-z0-9._~:/-]+\*?", pattern)
            or pattern[:-1].find("*") >= 0
            or pattern == "*"
        ):
            errors.append(f"opaque identifier pattern {position + 1} is unsafe")
    if not isinstance(entries, list) or len(entries) > MAX_ENDPOINT_LABEL_ENTRIES:
        errors.append("endpoint label entries are malformed or unbounded")
        return errors
    if not isinstance(counts, dict) or set(counts) != {"entries"}:
        errors.append("endpoint label counts are malformed")
    elif counts["entries"] != len(entries):
        errors.append("endpoint label entry count does not reconcile")

    observed_routes: set[str] = set()
    retained_text_units = 0
    expected_entry_keys = {
        "route",
        "iri",
        "label",
        "language",
        "type",
        "label_authority",
    }
    for position, entry in enumerate(entries):
        if not isinstance(entry, dict) or set(entry) != expected_entry_keys:
            errors.append(f"endpoint label entry {position + 1} has unsupported fields")
            continue
        endpoint_route = str(entry.get("route") or "")
        label = str(entry.get("label") or "")
        type_label = str(entry.get("type") or "")
        language = str(entry.get("language") or "")
        iri = str(entry.get("iri") or "")
        authority = entry.get("label_authority")
        if not _canonical_local_route(endpoint_route):
            errors.append(f"endpoint label route is not canonical: {endpoint_route}")
        if endpoint_route in observed_routes:
            errors.append(f"endpoint label route is duplicated: {endpoint_route}")
        observed_routes.add(endpoint_route)
        for field, value, maximum in (
            ("label", label, 512),
            ("type", type_label, 256),
        ):
            if (
                not value
                or value.strip() != value
                or len(value) > maximum
                or CONTROL_CHARACTER.search(value)
                or value == "Missing label"
                or _is_opaque(value, [str(pattern) for pattern in patterns])
            ):
                errors.append(
                    f"endpoint label entry {position + 1} {field} is not governed readable text"
                )
        if not LANGUAGE_TAG.fullmatch(language):
            errors.append(f"endpoint label entry {position + 1} language is malformed")
        if language != "en-GB":
            errors.append(f"endpoint label entry {position + 1} language must be en-GB")
        if not ABSOLUTE_IRI.fullmatch(iri):
            errors.append(f"endpoint label entry {position + 1} IRI is not absolute")
        if not isinstance(authority, dict) or set(authority) != {"class", "source"}:
            errors.append(f"endpoint label entry {position + 1} authority is malformed")
        else:
            if authority.get("class") not in ENDPOINT_LABEL_AUTHORITY_CLASSES:
                errors.append(
                    f"endpoint label entry {position + 1} authority class is unsupported"
                )
            if not _safe_http_url(authority.get("source")):
                errors.append(
                    f"endpoint label entry {position + 1} authority source is unsafe"
                )
        retained_text_units += sum(
            _utf16_text_units(value)
            for value in (
                endpoint_route,
                iri,
                label,
                language,
                type_label,
                str(authority.get("class") or "") if isinstance(authority, dict) else "",
                str(authority.get("source") or "") if isinstance(authority, dict) else "",
            )
        )

    if retained_text_units > MAX_ENDPOINT_LABEL_TEXT_UNITS:
        errors.append("endpoint label index exceeds its retained-text ceiling")
    if len(canonical_json_bytes(index)) > MAX_ENDPOINT_LABEL_JSON_BYTES:
        errors.append("endpoint label index exceeds its compact JSON byte ceiling")
    if graph_reachable_routes is not None:
        missing = sorted(graph_reachable_routes.difference(observed_routes))
        extra = sorted(observed_routes.difference(graph_reachable_routes))
        errors.extend(
            f"graph-reachable route has no endpoint label: {item}" for item in missing
        )
        errors.extend(
            f"endpoint label route is not graph-reachable: {item}" for item in extra
        )
    if [entry.get("route") for entry in entries if isinstance(entry, dict)] != sorted(
        entry.get("route") for entry in entries if isinstance(entry, dict)
    ):
        errors.append("endpoint label entries are not in deterministic route order")
    return sorted(set(errors))
