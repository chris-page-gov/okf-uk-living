#!/usr/bin/env python3
"""Project governed life-course dossiers into OKF Explorer concept data."""

from __future__ import annotations

import hashlib
import re
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from build_okf_bundle import ROOT, parse_document, rewrite_body_links
from check_service_denominator import flatten_service_families, service_family_scopes
from life_course_dossiers import load_dossiers, resolve_sources


GENERATED_AT = "2026-08-08T00:00:00+01:00"
PUBLIC_BASE = "https://chris-page-gov.github.io/okf-uk-living/"
IDENTIFIER_BASE = f"{PUBLIC_BASE}id/"
PREDICATE_BASE = f"{PUBLIC_BASE}terms/"
RELATIONSHIP_DERIVATION_RULE = (
    f"{PUBLIC_BASE}rules/deterministic-life-course-dossier-projection-v1"
)
PROCESS_PATH = ROOT / "source" / "life-course-processes.v1.yaml"
AUTHORITY_REGISTRY_PATH = ROOT / "source" / "authority-registry.v1.yaml"
RIGHTS = {
    "source": f"{PUBLIC_BASE}generated/browser/evidence/licensing-and-attribution.html",
    "assertion": "Repository-authored normalised structure is MIT; linked upstream source content is not redistributed.",
}
INVERSE_LABELS = {
    "addresses-user-need": "need addressed by",
    "applies-in-jurisdiction": "jurisdiction for",
    "belongs-to-life-course-domain": "contains enclosing process",
    "delivered-by": "delivers",
    "depends-on": "dependency of",
    "follows": "precedes",
    "governed-by": "governs",
    "has-episode": "episode of",
    "has-outcome": "outcome of",
    "has-redress": "redress for",
    "offered-by": "offers",
    "part-of-enclosing-process": "contains service family or episode",
    "precedes": "follows",
    "produces": "produced by",
    "requires": "required by",
    "supported-by-source": "supports",
}


def slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "concept"


def titleize(identifier: str) -> str:
    return identifier.replace("-", " ").capitalize()


def load_processes() -> list[dict[str, Any]]:
    import yaml

    value = yaml.safe_load(PROCESS_PATH.read_text(encoding="utf-8")) or {}
    return list(value.get("processes", []))


def load_authority_registry() -> dict[str, Any]:
    import yaml

    value = yaml.safe_load(AUTHORITY_REGISTRY_PATH.read_text(encoding="utf-8")) or {}
    if not isinstance(value, dict):
        raise ValueError("authority registry root must be a mapping")
    return value


def route(kind: str, identifier: str) -> str:
    return f"{kind}/{slug(identifier)}"


def semantic_iri(local_route: str) -> str:
    return f"{IDENTIFIER_BASE}{local_route}"


def base_record(
    *,
    name: str,
    title: str,
    notes: str,
    record_type: str,
    record_route: str,
    domain_id: str = "",
    domain_title: str = "",
    assertion_status: str = "normalized",
    source_url: str = "generated/browser/source/life-course-processes.v1.yaml.html",
) -> dict[str, Any]:
    return {
        "id": f"concept:{name}",
        "concept_id": f"concept:{name}",
        "name": name,
        "route": record_route,
        "title": title,
        "notes": notes,
        "publisher": "okf-uk-living",
        "resource_count": 0,
        "resource_ids": [],
        "formats": ["YAML"],
        "topics": [domain_title] if domain_title else [],
        "tags": [slug(record_type), "repository-authored"],
        "timestamp": GENERATED_AT,
        "metadata_modified": "2026-08-08",
        "license_id": "MIT",
        "license": "MIT for repository-authored structure and summaries; upstream content remains link-only",
        "source_url": source_url,
        "record_type": record_type,
        "life_course_domain": domain_title,
        "life_course_domain_id": domain_id,
        "implementation_status": "governed-supporting-concept",
        "assertion_status": assertion_status,
        "assertion_scope": "real-world",
        "rights_state": ["repository-metadata-mit", "upstream-link-only-not-acquired"],
        "generated": {"by": "process:life-course-projection", "at": GENERATED_AT},
        "limitations": ["Repository-authored discovery concept; consult the linked current authority for a real case."],
    }


def relationship(
    source: str,
    target: str,
    predicate: str,
    *,
    evidence: list[str],
    assertion_status: str = "normalized",
    source_artifact: str = "source/life-course-processes.v1.yaml",
    label: str | None = None,
) -> dict[str, Any]:
    evidence_ids = sorted(set(evidence))
    digest = hashlib.sha256(
        "\0".join((source, target, predicate, source_artifact)).encode("utf-8")
    ).hexdigest()[:24]
    evidence_value = "\n".join(evidence_ids)
    display_label = label or predicate.replace("-", " ")
    authority_class = "official" if assertion_status == "official" else "derived"
    source_url = f"{PUBLIC_BASE}generated/browser/{source_artifact}.html"
    return {
        "schema": "okf-relationship-assertion.v2",
        "id": f"{PUBLIC_BASE}assertions/{digest}",
        "source": source,
        "target": target,
        "source_iri": semantic_iri(source),
        "target_iri": semantic_iri(target),
        "kind": display_label,
        "label": display_label,
        "inverse_label": INVERSE_LABELS[predicate],
        "predicate": f"{PREDICATE_BASE}{predicate}",
        "assertion_status": assertion_status,
        "assertion_scope": "real-world",
        "authority": {
            "class": authority_class,
            "label": (
                "Official relationship represented by the reviewed dossier"
                if authority_class == "official"
                else "Repository-authored normalised discovery model"
            ),
            "source": source_url,
        },
        "derivation": RELATIONSHIP_DERIVATION_RULE,
        "derivation_activity": f"{PUBLIC_BASE}activities/life-course-projection-2026-08-08",
        "observed_at": GENERATED_AT,
        "freshness": "unknown",
        "evidence": [
            {
                "@id": f"{PUBLIC_BASE}evidence/relationship/{digest}",
                "type": "authored-dossier-or-contract",
                "url": source_url,
                "source_artifact": source_artifact,
                "source_field": "relationship source identifiers",
                "source_ids": evidence_ids,
                "source_value_sha256": hashlib.sha256(evidence_value.encode("utf-8")).hexdigest(),
                "source_value_hash_canonicalization": "sorted-unique-utf8-lines",
                "normalization": RELATIONSHIP_DERIVATION_RULE,
                "rationale": "Repository-authored governed relationship.",
                "retrieved_at": GENERATED_AT,
            }
        ],
        "rights": RIGHTS,
    }


def state_summary(value: Any) -> str:
    if isinstance(value, dict):
        return str(value.get("summary") or value.get("reason") or value.get("state") or "").strip()
    return str(value).strip()


def narrative_body(path: str) -> str:
    _, body = parse_document(ROOT / path)
    return rewrite_body_links(path, body).strip()


def project(denominator: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], dict[str, Any]]:
    dossiers, errors = load_dossiers()
    if errors:
        raise ValueError("; ".join(errors))
    families = flatten_service_families(denominator)
    family_by_id = {family["id"]: family for family in families}
    scopes = service_family_scopes(denominator)
    processes = load_processes()
    authority_registry = load_authority_registry()
    process_by_family = {
        family_id: process for process in processes for family_id in process.get("families", [])
    }
    domain_by_id = {
        domain["id"]: {"id": domain["id"], "title": domain["title"]}
        for domain in denominator["domains"]
    }
    rows_by_route: dict[str, dict[str, Any]] = {}
    resources: list[dict[str, Any]] = []
    relationships: list[dict[str, Any]] = []

    def add_record(record: dict[str, Any]) -> dict[str, Any]:
        existing = rows_by_route.get(record["route"])
        if existing:
            return existing
        rows_by_route[record["route"]] = record
        return record

    def support_record(
        *, kind: str, identifier: str, title: str, notes: str, family: dict[str, Any],
        assertion_status: str = "normalized",
    ) -> dict[str, Any]:
        record_route = route(kind, identifier)
        return add_record(base_record(
            name=f"{kind}-{slug(identifier)}",
            title=title,
            notes=notes,
            record_type=kind.replace("-", " ").title(),
            record_route=record_route,
            domain_id=family["domain"],
            domain_title=family["domain_title"],
            assertion_status=assertion_status,
            source_url="generated/browser/schemas/life-course-family.v1.schema.json.html",
        ))

    def actor_record(
        *, identifier: str, title: str, notes: str, family: dict[str, Any], assertion_status: str = "normalized",
    ) -> dict[str, Any]:
        shared = rows_by_route.get(route("organisation", identifier))
        if shared:
            return shared
        return support_record(
            kind="actor", identifier=identifier, title=title, notes=notes,
            family=family, assertion_status=assertion_status,
        )

    for area in authority_registry.get("geographies", []):
        area_record = base_record(
            name=f"gss-{area['code'].lower()}",
            title=area["official_name"],
            notes=(
                f"Official {area['geography_type'].replace('_', ' ')} area identified by GSS code "
                f"{area['code']} at the declared vintage. The code identifies the area, not by itself "
                "the legal body or service provider."
            ),
            record_type="Administrative Geography",
            record_route=route("geography", area["code"]),
            assertion_status="official",
            source_url="generated/browser/source/authority-registry.v1.yaml.html",
        )
        area_record.update({
            "search_aliases": [label["value"] for label in area.get("labels", [])],
            "search_text": [area["code"], area["geography_type"], area["jurisdiction"]],
            "topics": ["Authority and geography infrastructure"],
            "tags": ["gss", area["geography_type"], area["jurisdiction"]],
            "delivery_scope": ["shared-authority-infrastructure"],
            "jurisdiction": [area["jurisdiction"]],
            "implementation_status": "shared-authority-infrastructure",
            "limitations": [authority_registry["identity_rules"]["gss_area_not_body"]],
        })
        add_record(area_record)

    for organisation in authority_registry.get("organisations", []):
        roles = list(organisation.get("roles", []))
        organisation_record = base_record(
            name=f"authority-{slug(organisation['id'])}",
            title=organisation["title"],
            notes=(
                "Shared authority, regulator, redress or provider-role identity. "
                "A family dossier must cite the current route before applying this organisation to a case."
            ),
            record_type="Organisation",
            record_route=route("organisation", organisation["id"]),
            assertion_status="normalized",
            source_url="generated/browser/source/authority-registry.v1.yaml.html",
        )
        organisation_record.update({
            "search_aliases": [organisation.get("title_cy", ""), organisation.get("source_native_id", "")],
            "search_text": [*roles, organisation.get("organisation_type", ""), organisation.get("administers", "")],
            "topics": ["Authority, regulation and redress"],
            "tags": ["shared-authority", *[slug(role) for role in roles]],
            "delivery_scope": ["shared-authority-infrastructure"],
            "jurisdiction": organisation.get("jurisdictions", []),
            "implementation_status": "shared-authority-infrastructure",
            "official_url": organisation.get("official_url"),
            "identity_status": organisation.get("identity_status"),
            "limitations": [authority_registry["identity_rules"]["current_route"]],
        })
        add_record(organisation_record)

    for domain in denominator["domains"]:
        add_record(base_record(
            name=f"life-course-domain-{domain['id']}",
            title=domain["title"],
            notes=f"Governed life-course domain containing {sum(len(domain[wave]) for wave in ('wave-1', 'wave-2', 'wave-3'))} approved service families.",
            record_type="Life-course Domain",
            record_route=route("life-course-domain", domain["id"]),
            domain_id=domain["id"],
            domain_title=domain["title"],
            source_url="generated/browser/source/service-family-denominator.v1.yaml.html",
        ))

    for process in processes:
        domain = domain_by_id[process["domain"]]
        process_route = route("enclosing-process", process["id"])
        add_record(base_record(
            name=f"enclosing-process-{process['id']}",
            title=process["title"],
            notes=f"Normalized enclosing process for {len(process['families'])} approved service families.",
            record_type="Enclosing Process",
            record_route=process_route,
            domain_id=domain["id"],
            domain_title=domain["title"],
        ))
        relationships.append(relationship(
            process_route,
            route("life-course-domain", domain["id"]),
            "belongs-to-life-course-domain",
            evidence=[process["id"]],
        ))

    implemented = set(denominator["implemented_families"])
    for family in families:
        family_id = family["id"]
        dossier = dossiers.get(family_id)
        process = process_by_family[family_id]
        family_route = route("dataset", family_id)
        delivery_scopes = scopes[family_id]
        notes = dossier["description"] if dossier else (
            "Owner-approved normalised planning family. Current leaf routes, jurisdictions, authority, "
            "deadlines and exceptions require staged source evidence."
        )
        record = base_record(
            name=family_id,
            title=dossier["title"] if dossier else titleize(family_id),
            notes=notes,
            record_type="Service Family",
            record_route=family_route,
            domain_id=family["domain"],
            domain_title=family["domain_title"],
            source_url=(
                f"generated/browser/source/life-course-families/{family['domain']}/{family_id}.v1.yaml.html"
                if dossier else "generated/browser/source/service-family-denominator.v1.yaml.html"
            ),
        )
        record.update({
            "search_aliases": dossier.get("aliases", []) if dossier else [],
            "acquisition_wave": family["wave"],
            "delivery_scope": delivery_scopes,
            "jurisdiction": [item["jurisdiction"] for item in dossier["applicability"]] if dossier else ["jurisdiction-evidence-required"],
            "implementation_status": "population-complete" if dossier else ("implemented-three-slice" if family_id in implemented else "planned"),
            "tags": [family["wave"], *delivery_scopes, "normalized", "dossier-backed" if dossier else "planning"],
            "limitations": dossier.get("limitations", record["limitations"]) if dossier else [
                "Planning denominator, not an official service assertion.",
                "No source snapshot or upstream expression is included.",
                "Jurisdiction and responsibility require current leaf evidence.",
            ],
        })
        add_record(record)
        relationships.extend([
            relationship(family_route, route("life-course-domain", family["domain"]), "belongs-to-life-course-domain", evidence=[family_id]),
            relationship(family_route, route("enclosing-process", process["id"]), "part-of-enclosing-process", evidence=[family_id]),
        ])
        if not dossier:
            continue

        source_artifact = f"source/life-course-families/{family['domain']}/{family_id}.v1.yaml"
        resolved_sources, source_errors = resolve_sources(dossier)
        if source_errors:
            raise ValueError("; ".join(source_errors))
        source_by_id = {source["id"]: source for source in resolved_sources}
        resource_ids: list[str] = []
        for position, source in enumerate(resolved_sources):
            resource_id = f"resource:{family_id}:{source['id']}"
            resource_route = route("resource", f"{family_id}-{source['id']}")
            resource_ids.append(resource_id)
            resources.append({
                "id": resource_id,
                "dataset": family_id,
                "dataset_concept_id": record["concept_id"],
                "name": source["title"],
                "description": source["summary"],
                "format": "HTML",
                "source_format": "linked-reference",
                "route": resource_route,
                "host": urlparse(source["resource"]).hostname,
                "url": source["resource"],
                "position": position,
                "resource_type": "authoritative-source-link",
                "metadata_modified": source["observed_at"],
                "source_access": {
                    "url": source["resource"],
                    "label": source["title"],
                    "media_type": "text/html",
                    "display_mode": "link",
                },
                "provenance": {
                    "owner": source["owner"],
                    "authority_role": source["authority_role"],
                    "observed_at": source["observed_at"],
                    "freshness": source["freshness"],
                    "rights_decision": source["rights_decision"],
                    "limitations": source["limitations"],
                    "register": source["register"],
                    "response_body_retained": False,
                },
            })
            relationships.append(relationship(
                family_route, resource_route, "supported-by-source",
                evidence=[source["id"]], source_artifact=source_artifact,
            ))
        record["resource_count"] = len(resource_ids)
        record["resource_ids"] = resource_ids
        record["formats"] = ["HTML", "YAML"]
        record["search_aliases"] = dossier["aliases"]
        record["search_text"] = [
            *dossier["situations"], *dossier["user_needs"],
            *(state_summary(step.get(key)) for journey in [dossier["journeys"]["ordinary"], *dossier["journeys"]["exceptions"]] for step in journey["steps"] for key in ("interaction", "requirements", "evidence", "rule", "output", "outcome", "redress")),
            *(source["title"] for source in resolved_sources),
        ]
        process_record = rows_by_route[route("enclosing-process", process["id"])]
        ordinary = dossier["journeys"]["ordinary"]
        exceptions = dossier["journeys"]["exceptions"]
        episode_links: list[dict[str, str]] = []
        journey_step_links: dict[str, list[dict[str, str]]] = {}
        for journey_kind, journey in [("ordinary", ordinary), *(("exception", item) for item in exceptions)]:
            episode_id = f"{family_id}-{journey['id']}"
            episode = support_record(
                kind="service-episode", identifier=episode_id,
                title=journey["id"].replace("-", " ").capitalize(),
                notes=f"{journey['entry_state']} Outcome: {journey['outcome']}", family=family,
            )
            episode["episode_kind"] = journey_kind
            episode["implementation_status"] = "dossier-backed-supporting-concept"
            episode_links.append({"route": episode["route"], "label": episode["title"], "description": journey["outcome"]})
            relationships.extend([
                relationship(family_route, episode["route"], "has-episode", evidence=journey["steps"][0]["sources"], source_artifact=source_artifact),
                relationship(episode["route"], route("enclosing-process", process["id"]), "part-of-enclosing-process", evidence=journey["steps"][0]["sources"], source_artifact=source_artifact),
            ])
            previous_step_route = ""
            journey_step_links[journey["id"]] = []
            for step in journey["steps"]:
                step_record = support_record(
                    kind="service-step", identifier=f"{family_id}-{journey['id']}-{step['id']}",
                    title=step["interaction"], notes=f"Provider: {step['provider']}. Outcome: {state_summary(step['outcome'])}",
                    family=family, assertion_status=step["assertion_status"],
                )
                relationships.append(relationship(
                    episode["route"], step_record["route"], "has-episode",
                    evidence=step["sources"], source_artifact=source_artifact, label="has step",
                ))
                journey_step_links[journey["id"]].append({
                    "route": step_record["route"],
                    "label": step_record["title"],
                    "description": state_summary(step["outcome"]),
                })
                if previous_step_route:
                    relationships.extend([
                        relationship(previous_step_route, step_record["route"], "precedes", evidence=step["sources"], source_artifact=source_artifact),
                        relationship(step_record["route"], previous_step_route, "follows", evidence=step["sources"], source_artifact=source_artifact),
                    ])
                previous_step_route = step_record["route"]
                provider_record = actor_record(
                    identifier=step["provider"], title=titleize(slug(step["provider"])),
                    notes="Provider role named by the authored journey step.", family=family,
                )
                relationships.append(relationship(
                    step_record["route"], provider_record["route"], "delivered-by",
                    evidence=step["sources"], source_artifact=source_artifact,
                ))
                for key, predicate, concept_kind in (
                    ("requirements", "requires", "requirement"),
                    ("evidence", "requires", "evidence"),
                    ("rule", "governed-by", "rule"),
                    ("output", "produces", "output"),
                    ("outcome", "has-outcome", "outcome"),
                    ("redress", "has-redress", "redress"),
                ):
                    summary = state_summary(step[key])
                    if not summary:
                        continue
                    concept = support_record(
                        kind=concept_kind,
                        identifier=f"{family_id}-{journey['id']}-{step['id']}-{summary}",
                        title=summary, notes=f"{concept_kind.title()} stated by {step['id']}.", family=family,
                    )
                    relationships.append(relationship(
                        step_record["route"], concept["route"], predicate,
                        evidence=step["sources"], source_artifact=source_artifact,
                    ))
                for source_id in step["sources"]:
                    source = source_by_id[source_id]
                    relationships.append(relationship(
                        step_record["route"], route("resource", f"{family_id}-{source_id}"),
                        "supported-by-source", evidence=[source_id], source_artifact=source_artifact,
                    ))

        for need in dossier["user_needs"]:
            need_record = support_record(
                kind="user-need", identifier=f"{family_id}-{need}", title=need,
                notes="Original repository-authored user-need summary.", family=family,
            )
            relationships.append(relationship(
                family_route, need_record["route"], "addresses-user-need",
                evidence=dossier["enclosing_processes"][0]["sources"], source_artifact=source_artifact,
            ))
        for actor in dossier["actors"]:
            dossier_actor_record = actor_record(
                identifier=actor["id"], title=titleize(slug(actor["id"])),
                notes=f"Role: {actor['role']}", family=family, assertion_status=actor["authority_status"],
            )
            relationships.append(relationship(
                family_route, dossier_actor_record["route"], "offered-by", evidence=actor["sources"],
                assertion_status=actor["authority_status"], source_artifact=source_artifact,
            ))
        for applicability in dossier["applicability"]:
            jurisdiction_record = support_record(
                kind="jurisdiction", identifier=applicability["jurisdiction"],
                title=applicability["jurisdiction"], notes=f"Applicability state: {applicability['state']}", family=family,
            )
            relationships.append(relationship(
                family_route, jurisdiction_record["route"], "applies-in-jurisdiction",
                evidence=applicability["sources"], source_artifact=source_artifact,
            ))
        for dependency in dossier["dependencies"]:
            dependency_record = support_record(
                kind="dependency", identifier=dependency["id"], title=titleize(slug(dependency["id"])),
                notes=f"Selection basis: {dependency.get('selection_basis', 'source-defined')}", family=family,
            )
            relationships.append(relationship(
                family_route, dependency_record["route"], "depends-on",
                evidence=dependency["sources"], source_artifact=source_artifact,
            ))
        variant_links = [
            {"route": route("service-variant", f"{family_id}-{variant['id']}"), "label": variant["id"].replace("-", " ").title()}
            for applicability in dossier["applicability"] for variant in applicability.get("route_variants", [])
        ]
        for applicability in dossier["applicability"]:
            for variant in applicability.get("route_variants", []):
                support_record(
                    kind="service-variant", identifier=f"{family_id}-{variant['id']}",
                    title=variant["id"].replace("-", " ").title(),
                    notes=f"{applicability['jurisdiction']} route variant; primary source {variant['primary_source']}.",
                    family=family,
                )
        record["narrative"] = {
            "title": f"{dossier['title']} within {dossier['narrative']['process_context']}",
            "body": narrative_body(dossier["narrative"]["markdown"]),
            "process": {"route": process_record["route"], "label": process_record["title"]},
            "previous": journey_step_links[ordinary["id"]][:1],
            "next": journey_step_links[ordinary["id"]][-1:] + episode_links[1:],
            "variants": variant_links,
            "related": [],
        }

    rows = sorted(rows_by_route.values(), key=lambda row: (row["record_type"], row["name"]))
    relationships = sorted(relationships, key=lambda edge: edge["id"])
    adjacency: dict[str, dict[str, list[int]]] = defaultdict(lambda: {"outgoing": [], "incoming": []})
    for index, edge in enumerate(relationships):
        adjacency[edge["source"]]["outgoing"].append(index)
        adjacency[edge["target"]]["incoming"].append(index)
    report = {
        "schema": "life-course-validation-report.v1",
        "generated_at": GENERATED_AT,
        "status": "pending-semantic-validation",
        "counts": {
            "service_families": len(families),
            "dossier_backed_families": len(dossiers),
            "supporting_concepts": len(rows) - len(families),
            "resources": len(resources),
            "relationships": len(relationships),
            "snapshots": 0,
            "authority_geographies": len(authority_registry.get("geographies", [])),
            "authority_organisations": len(authority_registry.get("organisations", [])),
        },
        "violations": [],
        "population_complete_family_ids": sorted(dossiers),
        "remaining_family_ids": sorted(set(family_by_id) - set(dossiers)),
        "relationship_adjacency": dict(sorted(adjacency.items())),
    }
    return rows, resources, relationships, report


def semantic_graph(rows: list[dict[str, Any]], relationships: list[dict[str, Any]]) -> dict[str, Any]:
    graph_by_iri: dict[str, dict[str, Any]] = {
        semantic_iri(row["route"]): {
            "@id": semantic_iri(row["route"]),
            "@type": f"{PUBLIC_BASE}types/{slug(row['record_type'])}",
            "route": row["route"],
            "title": row["title"],
            "description": row["notes"],
            "assertion_status": row["assertion_status"],
        }
        for row in rows
    }
    for edge in relationships:
        source_node = graph_by_iri[edge["source_iri"]]
        target_value = {"@id": edge["target_iri"]}
        direct = source_node.get(edge["predicate"])
        if direct is None:
            source_node[edge["predicate"]] = target_value
        elif isinstance(direct, list):
            direct.append(target_value)
        else:
            source_node[edge["predicate"]] = [direct, target_value]
    graph: list[dict[str, Any]] = list(graph_by_iri.values())
    graph.extend(
        {
            "@id": edge["id"],
            "@type": ["rdf:Statement", "okf:RelationshipAssertion"],
            "source": {"@id": edge["source_iri"]},
            "source_route": edge["source"],
            "predicate": {"@id": edge["predicate"]},
            "target": {"@id": edge["target_iri"]},
            "target_route": edge["target"],
            **{
                key: value
                for key, value in edge.items()
                if key
                not in {
                    "schema", "id", "source", "source_iri", "predicate",
                    "target", "target_iri",
                }
            },
        }
        for edge in relationships
    )
    return {
        "@context": {
            "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
            "okf": "https://chris-page-gov.github.io/okf-explorer/ns#",
            "title": "http://purl.org/dc/terms/title",
            "description": "http://purl.org/dc/terms/description",
            "route": "https://chris-page-gov.github.io/okf-explorer/ns#route",
            "source": {"@id": "http://www.w3.org/ns/prov#subject", "@type": "@id"},
            "target": {"@id": "http://www.w3.org/ns/prov#object", "@type": "@id"},
            "predicate": {"@id": "http://www.w3.org/1999/02/22-rdf-syntax-ns#predicate", "@type": "@id"},
            "source_route": "https://chris-page-gov.github.io/okf-explorer/ns#sourceRoute",
            "target_route": "https://chris-page-gov.github.io/okf-explorer/ns#targetRoute",
            "label": "http://www.w3.org/2000/01/rdf-schema#label",
            "inverse_label": "https://chris-page-gov.github.io/okf-explorer/ns#inverseLabel",
            "assertion_status": "https://chris-page-gov.github.io/okf-explorer/ns#assertionStatus",
            "assertion_scope": "https://chris-page-gov.github.io/okf-explorer/ns#assertionScope",
            "authority": "https://chris-page-gov.github.io/okf-explorer/ns#authority",
            "derivation": {"@id": "https://chris-page-gov.github.io/okf-explorer/ns#derivationMethod", "@type": "@id"},
            "derivation_activity": {"@id": "http://www.w3.org/ns/prov#wasGeneratedBy", "@type": "@id"},
            "observed_at": {"@id": "http://www.w3.org/ns/prov#generatedAtTime", "@type": "http://www.w3.org/2001/XMLSchema#dateTime"},
            "evidence": "http://www.w3.org/ns/prov#wasDerivedFrom",
            "rights": "http://purl.org/dc/terms/rights",
        },
        "@id": f"{PUBLIC_BASE}semantic/life-course-corpus",
        "@type": "okf:Bundle",
        "okf_version": "0.2",
        "title": "A Life in the UK semantic graph",
        "@graph": graph,
    }
