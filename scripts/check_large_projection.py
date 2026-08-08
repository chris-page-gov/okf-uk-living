#!/usr/bin/env python3
"""Validate the governed OKF Explorer large-corpus planning projection."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from build_large_corpus import FACETS, ROOT, build_outputs
from check_service_denominator import load_service_denominator, validate_service_denominator


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
    locator = load_json("large/data/record-locator.json")
    adjacency = load_json("large/data/relationship-adjacency.json")
    validation = load_json("large/data/validation-report.json")
    denominator, denominator_errors = load_service_denominator()
    if denominator:
        denominator_errors.extend(validate_service_denominator(denominator))
    errors.extend(denominator_errors)

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
    service_families = [row for row in rows if row.get("record_type") == "Service Family"]
    if len(service_families) != 293 or descriptor.get("counts", {}).get("service_families") != 293:
        errors.append("large projection must distinguish exactly the approved 293 service families")
    if descriptor.get("counts", {}).get("concepts") != len(rows) or len(rows) <= len(service_families):
        errors.append("descriptor must distinguish the larger supporting-concept count")
    if search.get("counts", {}).get("documents") != len(rows) or len(search_results) != len(rows):
        errors.append("static search must cover all approved planning families")
    if len(manifest.get("chunks", {}).get("datasets", [])) != 2 or len(search.get("entrypoints", {}).get("result_docs", [])) != 2:
        errors.append("record and search-result hydration must shard corpora above 1,000 concepts")
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
    dossier_families = [row for row in service_families if row.get("implementation_status") == "population-complete-three-slice"]
    if len(dossier_families) != 6 or any(not row.get("narrative", {}).get("body") for row in dossier_families):
        errors.append("six migrated families must expose authored large-record narratives")
    authority_geographies = [row for row in rows if row.get("record_type") == "Administrative Geography"]
    authority_organisations = [row for row in rows if row.get("record_type") == "Organisation"]
    if len(authority_geographies) != 397 or len(authority_organisations) != 438:
        errors.append("shared authority projection must expose 397 GSS geographies and 438 organisations")
    if validation.get("counts", {}).get("authority_geographies") != 397 or validation.get("counts", {}).get("authority_organisations") != 438:
        errors.append("validation report must reconcile authority and geography infrastructure")
    if sum(row.get("resource_count", 0) for row in service_families) != 53 or len(resources) != 53:
        errors.append("six migrated families must expose exactly 53 linked source resources")
    if any(resource.get("source_access", {}).get("display_mode") != "link" for resource in resources):
        errors.append("all migrated sources must use link-only typed access")
    if any(resource.get("provenance", {}).get("response_body_retained") is not False for resource in resources):
        errors.append("source resource provenance must record that no response body was retained")
    required_edge_fields = {"predicate", "assertion_status", "authority", "derivation", "observed_at", "evidence", "rights"}
    if not relationships or any(required_edge_fields - set(edge) for edge in relationships):
        errors.append("every generated relationship must carry governed provenance and evidence")
    process_edges = {
        edge["source"] for edge in relationships if edge.get("predicate") == "part-of-enclosing-process" and edge.get("source", "").startswith("dataset/")
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
        or any(edge["source"] not in adjacency_routes or edge["target"] not in adjacency_routes for edge in relationships)
    ):
        errors.append("sharded relationship adjacency must cover every relationship endpoint")
    if validation.get("status") != "conformant" or validation.get("counts", {}).get("dossier_backed_families") != 6:
        errors.append("SHACL-style validation report must reconcile the six-family migration")
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
    print("Large-corpus checks passed: 293 families, 6 dossier-backed narratives, 397 geographies, 438 organisations, 53 source links, governed relationships, 0 snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
