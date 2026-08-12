#!/usr/bin/env python3
"""Validate the governed OKF Explorer large-corpus planning projection."""

from __future__ import annotations

import gzip
import hashlib
import json
import math
from collections import Counter
from pathlib import Path
from typing import Any

from build_large_corpus import FACETS, ROOT, build_outputs, relationship_bucket
from check_service_denominator import load_service_denominator, validate_service_denominator
from life_course_dossiers import load_dossiers, resolve_sources
from life_course_projection import PREDICATE_BASE
from semantic_assertion_validation import (
    runtime_relationship_as_assertion,
    validate_relationship_planes,
)


def load_json(path: str) -> Any:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def validate_large_projection() -> list[str]:
    errors: list[str] = []
    try:
        expected = build_outputs()
    except ValueError as error:
        return [str(error)]
    for path, content in expected.items():
        target = ROOT / path
        if not target.is_file():
            errors.append(f"{path.as_posix()} is missing")
        elif isinstance(content, bytes):
            if target.read_bytes() != content:
                errors.append(f"{path.as_posix()} is stale")
        elif target.read_text(encoding="utf-8") != content:
            errors.append(f"{path.as_posix()} is stale")
    if errors:
        return errors

    descriptor = load_json("okf-explorer.json")
    manifest = load_json("large/data/manifest.json")
    rows = [row for path in manifest.get("chunks", {}).get("datasets", []) for row in load_json(path)]
    facets = load_json("large/data/facets.json")
    presentation = load_json("large/data/presentation.json")
    search = load_json("large/data/search/manifest.json")
    search_results = [row for path in search.get("entrypoints", {}).get("result_docs", []) for row in load_json(path)]
    search_postings = load_json("large/data/search/postings.json").get("tokens", {})
    resources = load_json("large/data/resources-0.json")
    relationships = load_json("large/data/relationships-0.json")
    runtime_reference = descriptor.get("entrypoints", {}).get(
        "relationship_runtime", {}
    )
    runtime_path = str(runtime_reference.get("path", ""))
    runtime = load_json(runtime_path) if runtime_path else {}
    semantic = load_json("generated/semantic/life-course-corpus.jsonld")
    locator = load_json("large/data/record-locator.json")
    adjacency = load_json("large/data/relationship-adjacency.json")
    validation = load_json("large/data/validation-report.json")
    denominator, denominator_errors = load_service_denominator()
    if denominator:
        denominator_errors.extend(validate_service_denominator(denominator))
    errors.extend(denominator_errors)
    dossiers, dossier_errors = load_dossiers()
    errors.extend(dossier_errors)
    expected_resource_count = sum(len(resolve_sources(dossier)[0]) for dossier in dossiers.values())

    if descriptor.get("schema") != "okf-explorer-large-corpus.v1" or descriptor.get("kind") != "okf-large-corpus":
        errors.append("okf-explorer.json must declare the large-corpus v1 contract")
    if descriptor.get("entrypoints", {}).get("data_manifest") != "large/data/manifest.json":
        errors.append("descriptor must expose the data manifest")
    if descriptor.get("entrypoints", {}).get("search_manifest") != "large/data/search/manifest.json":
        errors.append("descriptor must expose the static-search manifest")
    if descriptor.get("source", {}).get("source_snapshots") is not False:
        errors.append("descriptor must preserve the zero-snapshot boundary")
    if descriptor.get("source", {}).get("publication_authorized") is not False:
        errors.append("descriptor must preserve the publication gate")
    if manifest.get("indexes", {}).get("overview") != "large/data/overview.json":
        errors.append("manifest must expose an overview index")
    runtime_bytes = (ROOT / runtime_path).read_bytes() if runtime_path else b""
    runtime_integrity = descriptor.get("entrypoint_integrity", {}).get(
        "relationship_runtime"
    )
    if (
        runtime.get("schema") != "okf-rich-relationship-runtime-manifest.v1"
        or runtime_reference != runtime_integrity
        or runtime_reference != manifest.get("indexes", {}).get("relationship_runtime")
        or runtime_reference.get("bytes") != len(runtime_bytes)
        or runtime_reference.get("sha256")
        != hashlib.sha256(runtime_bytes).hexdigest()
    ):
        errors.append("rich relationship runtime must be digest-bound from both manifests")
    runtime_rows: list[dict[str, Any]] = []
    for plane in runtime.get("planes", []):
        for chunk in plane.get("chunks", []):
            path = ROOT / str(chunk.get("path", ""))
            compressed = path.read_bytes() if path.is_file() else b""
            if (
                not compressed
                or chunk.get("bytes") != len(compressed)
                or chunk.get("sha256") != hashlib.sha256(compressed).hexdigest()
            ):
                errors.append("rich relationship runtime chunk digest does not reconcile")
                continue
            chunk_rows = json.loads(gzip.decompress(compressed))
            if len(chunk_rows) != chunk.get("count"):
                errors.append("rich relationship runtime chunk count does not reconcile")
            runtime_rows.extend(chunk_rows)
    if (
        len(runtime_rows) != len(relationships)
        or {row.get("assertion_id") for row in runtime_rows}
        != {row.get("id") for row in relationships}
    ):
        errors.append("rich relationship runtime must cover every relationship assertion")
    locator_reference = runtime.get("route_locator", {})
    locator_path = ROOT / str(locator_reference.get("path", ""))
    locator_bytes = locator_path.read_bytes() if locator_path.is_file() else b""
    if (
        not locator_bytes
        or locator_reference.get("sha256")
        != hashlib.sha256(locator_bytes).hexdigest()
    ):
        errors.append("rich relationship route locator must be SHA-256-bound")
    service_families = [row for row in rows if row.get("record_type") == "Service Family"]
    if len(service_families) != 293 or descriptor.get("counts", {}).get("service_families") != 293:
        errors.append("large projection must distinguish exactly the approved 293 service families")
    if descriptor.get("counts", {}).get("concepts") != len(rows) or len(rows) <= len(service_families):
        errors.append("descriptor must distinguish the larger supporting-concept count")
    if search.get("counts", {}).get("documents") != len(rows) or len(search_results) != len(rows):
        errors.append("static search must cover all approved planning families")
    expected_chunks = math.ceil(len(rows) / 1000)
    if len(manifest.get("chunks", {}).get("datasets", [])) != expected_chunks or len(search.get("entrypoints", {}).get("result_docs", [])) != expected_chunks:
        errors.append("record and search-result hydration must reconcile all 1,000-record chunks")
    missed_ordinal = next(
        (index for index, row in enumerate(rows) if row.get("name") == "report-missed-rubbish-collection"),
        None,
    )
    for token in ("missed", "rubbish"):
        observed = {posting[0] for posting in search_postings.get(token, [])}
        if missed_ordinal is None or missed_ordinal not in observed:
            errors.append(f"static search token {token} must retrieve the missed-rubbish planning family")
    for key, _, _ in FACETS:
        filter_path = search.get("entrypoints", {}).get("filter_postings", {}).get(key)
        if not filter_path or load_json(filter_path).get("key") != key:
            errors.append(f"static search must expose filter postings for facet {key}")
    if len({row.get("name") for row in rows}) != len(rows):
        errors.append("large projection concept names must be unique")
    if any(row.get("assertion_status") not in {"official", "normalized"} for row in rows):
        errors.append("every projected concept must retain a governed assertion status")
    dossier_families = [row for row in service_families if row.get("implementation_status") == "population-complete"]
    if len(dossier_families) != len(dossiers) or any(not row.get("narrative", {}).get("body") for row in dossier_families):
        errors.append("every dossier-backed family must expose its authored large-record narrative")
    authority_geographies = [row for row in rows if row.get("record_type") == "Administrative Geography"]
    authority_organisations = [row for row in rows if row.get("record_type") == "Organisation"]
    if len(authority_geographies) != 397 or len(authority_organisations) != 438:
        errors.append("shared authority projection must expose 397 GSS geographies and 438 organisations")
    if validation.get("counts", {}).get("authority_geographies") != 397 or validation.get("counts", {}).get("authority_organisations") != 438:
        errors.append("validation report must reconcile authority and geography infrastructure")
    if sum(row.get("resource_count", 0) for row in service_families) != expected_resource_count or len(resources) != expected_resource_count:
        errors.append("projected source resources must reconcile with all authored dossier assertions")
    if any(resource.get("source_access", {}).get("display_mode") != "link" for resource in resources):
        errors.append("all migrated sources must use link-only typed access")
    if any(resource.get("provenance", {}).get("response_body_retained") is not False for resource in resources):
        errors.append("source resource provenance must record that no response body was retained")
    required_edge_fields = {
        "id", "source", "target", "source_iri", "target_iri", "predicate",
        "label", "inverse_label", "assertion_status", "assertion_scope",
        "authority", "derivation", "observed_at", "evidence", "rights",
    }
    if not relationships or any(required_edge_fields - set(edge) for edge in relationships):
        errors.append("every generated relationship must carry governed provenance and evidence")
    if any(not edge.get("source_iri", "").startswith("https://") or not edge.get("target_iri", "").startswith("https://") for edge in relationships):
        errors.append("every generated relationship must separate absolute semantic IRIs from local routes")
    if any(not edge.get("predicate", "").startswith(PREDICATE_BASE) for edge in relationships):
        errors.append("every generated relationship predicate must use the governed absolute IRI namespace")
    semantic_graph = semantic.get("@graph", [])
    semantic_nodes = {
        node.get("@id"): node
        for node in semantic_graph
        if isinstance(node, dict)
        and "okf:RelationshipAssertion" not in node.get("@type", [])
    }
    semantic_assertions = {
        node.get("@id"): node
        for node in semantic_graph
        if isinstance(node, dict)
        and "okf:RelationshipAssertion" in node.get("@type", [])
    }
    semantic_validation, semantic_violations = validate_relationship_planes(
        semantic, relationships
    )
    if semantic_violations:
        errors.extend(
            "shared semantic assertion schema violation: "
            f"{violation['plane']} {violation['assertion_id']}"
            f"{violation['instance_path']}: {violation['message']}"
            for violation in semantic_violations
        )
    if validation.get("semantic_assertion_validation") != semantic_validation:
        errors.append(
            "validation report must bind exhaustive semantic and runtime "
            "assertion schema validation"
        )
    if semantic.get("okf_version") != "0.2" or semantic.get("@type") != "okf:Bundle":
        errors.append("semantic graph must identify itself as an OKF 0.2 bundle")
    if len(semantic_nodes) != len(rows) or len(semantic_assertions) != len(relationships):
        errors.append("semantic entities and assertions must reconcile runtime node and relationship counts")
    for edge in relationships:
        source_node = semantic_nodes.get(edge["source_iri"], {})
        direct_values = source_node.get(edge["predicate"], [])
        if not isinstance(direct_values, list):
            direct_values = [direct_values]
        if {"@id": edge["target_iri"]} not in direct_values:
            errors.append(f"semantic graph is missing direct triple for {edge['id']}")
            break
        assertion = semantic_assertions.get(edge["id"], {})
        if assertion != runtime_relationship_as_assertion(edge):
            errors.append(f"semantic assertion differs from runtime projection for {edge['id']}")
            break
    process_edges = {
        edge["source"]
        for edge in relationships
        if edge.get("predicate") == f"{PREDICATE_BASE}part-of-enclosing-process"
        and edge.get("source", "").startswith("dataset/")
    }
    if len(process_edges) != 293:
        errors.append("all 293 families must be reachable from an approved enclosing process")
    locator_routes = {
        route
        for path in locator.get("buckets", {}).values()
        for route in load_json(path)
    }
    if (
        locator.get("schema") != "okf-record-locator-sharded.v1"
        or locator.get("algorithm") != "fnv1a32-prefix-2"
        or locator.get("records") != len(rows)
        or any(row["route"] not in locator_routes for row in rows)
    ):
        errors.append("sharded record locator must cover every projected concept")
    adjacency_routes = {
        route
        for path in adjacency.get("buckets", {}).values()
        for route in load_json(path)
    }
    if (
        adjacency.get("schema") != "okf-relationship-adjacency.v1"
        or adjacency.get("algorithm") != "fnv1a32-prefix-2"
        or adjacency.get("relationships") != len(relationships)
        or any(edge["source"] not in adjacency_routes or edge["target"] not in adjacency_routes for edge in relationships)
    ):
        errors.append("sharded relationship adjacency must cover every relationship endpoint")
    runtime_by_id = {edge["id"]: edge for edge in relationships}
    adjacency_incidence: Counter[str] = Counter()
    adjacency_payload_mismatches = 0
    adjacency_route_mismatches = 0
    adjacency_bucket_mismatches = 0
    for bucket, path in adjacency.get("buckets", {}).items():
        for route, edges in load_json(path).items():
            if relationship_bucket(route) != bucket:
                adjacency_bucket_mismatches += 1
            for edge in edges:
                assertion_id = str(edge.get("id", ""))
                adjacency_incidence[assertion_id] += 1
                if route not in {edge.get("source"), edge.get("target")}:
                    adjacency_route_mismatches += 1
                if runtime_by_id.get(assertion_id) != edge:
                    adjacency_payload_mismatches += 1
    adjacency_incidence_mismatches = sum(
        adjacency_incidence[edge["id"]]
        != (1 if edge["source"] == edge["target"] else 2)
        for edge in relationships
    )
    if set(adjacency_incidence) != set(runtime_by_id):
        errors.append("relationship adjacency and runtime assertion identities differ")
    if adjacency_bucket_mismatches:
        errors.append(
            f"{adjacency_bucket_mismatches} adjacency routes are in the wrong hash bucket"
        )
    if adjacency_route_mismatches:
        errors.append(
            f"{adjacency_route_mismatches} adjacency rows are not incident on their route"
        )
    if adjacency_payload_mismatches:
        errors.append(
            f"{adjacency_payload_mismatches} adjacency rows differ from runtime assertions"
        )
    if adjacency_incidence_mismatches:
        errors.append(
            f"{adjacency_incidence_mismatches} runtime assertions have incorrect adjacency incidence"
        )
    if validation.get("status") != "conformant" or validation.get("counts", {}).get("dossier_backed_families") != len(dossiers):
        errors.append("SHACL-style validation report must reconcile the current dossier population stage")
    expected_keys = [key for key, _, _ in FACETS]
    actual_keys = [facet.get("key") for facet in presentation.get("facets", [])]
    if actual_keys != expected_keys:
        errors.append("presentation must expose the seven approved colour facets in order")
    for key in expected_keys:
        expected_count = sum(
            len(row.get(key, [])) if isinstance(row.get(key), list) else int(bool(row.get(key)))
            for row in rows
        )
        observed_count = sum(int(item.get("count", 0)) for item in facets.get(key, []))
        if expected_count != observed_count:
            errors.append(f"facet {key} counts do not reconcile with records")
    return sorted(set(errors))


def main() -> int:
    errors = validate_large_projection()
    if errors:
        for error in errors:
            print(error)
        return 1
    validation = load_json("large/data/validation-report.json")
    counts = validation["counts"]
    print(
        "Large-corpus checks passed: 293 families, "
        f"{counts['dossier_backed_families']} dossier-backed narratives, "
        f"397 geographies, 438 organisations, {counts['resources']} source links, "
        "governed relationships, 0 snapshots"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
