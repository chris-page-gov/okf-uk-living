#!/usr/bin/env python3
"""Build the local OKF Explorer large-corpus planning projection."""

from __future__ import annotations

import argparse
import difflib
import json
import re
import shutil
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml

from build_okf_bundle import ROOT
from check_service_denominator import (
    flatten_service_families,
    load_service_denominator,
    service_family_scopes,
    validate_service_denominator,
)
from life_course_projection import project, semantic_graph


DESCRIPTOR_PATH = ROOT / "okf-explorer.json"
DATA_ROOT = ROOT / "large" / "data"
GENERATED_AT = "2026-08-08T00:00:00+01:00"
SNAPSHOT = "life-course-authority-infrastructure-2026-08-08"
FACETS = (
    ("life_course_domain", "Life-course domain", "The approved 24-domain planning spine."),
    ("acquisition_wave", "Acquisition wave", "The approved staged reference-registration wave."),
    ("delivery_scope", "Delivery scope", "The governed discovery scope; not a claim of uniform delivery."),
    ("jurisdiction", "Jurisdiction research", "The jurisdiction evidence still required for the planning family."),
    ("implementation_status", "Implementation status", "Population and shared-infrastructure implementation state."),
    ("assertion_status", "Assertion status", "The governed status of this planning projection."),
    ("rights_state", "Rights state", "Rights boundary for repository metadata and upstream sources."),
)
SEARCH_FIELDS = (
    ("title", 1, 16),
    ("name", 2, 12),
    ("search_aliases", 4, 14),
    ("notes", 8, 8),
    ("search_text", 16, 5),
    ("topics", 64, 6),
    ("tags", 32, 3),
)
SEARCH_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "in", "into",
    "is", "it", "of", "on", "or", "the", "to", "with",
}
RECORD_CHUNK_SIZE = 1000


def titleize(identifier: str) -> str:
    return identifier.replace("-", " ").capitalize()


def jurisdiction_values(scopes: list[str]) -> list[str]:
    values: list[str] = []
    if "local-authority" in scopes:
        values.append("local-provider-evidence-required")
    if "cross-border" in scopes:
        values.append("cross-border-evidence-required")
    if "regulated-private" in scopes or "mixed-public-private" in scopes:
        values.append("regulator-or-provider-jurisdiction-required")
    if "national-and-devolved" in scopes:
        values.append("uk-and-devolved-evidence-required")
    return sorted(set(values or ["jurisdiction-evidence-required"]))


def records(denominator: dict[str, Any]) -> list[dict[str, Any]]:
    scopes = service_family_scopes(denominator)
    implemented = set(denominator["implemented_families"])
    result: list[dict[str, Any]] = []
    for family in flatten_service_families(denominator):
        family_id = family["id"]
        delivery_scopes = scopes[family_id]
        result.append(
            {
                "id": f"service-family:{family_id}",
                "name": family_id,
                "route": f"dataset/{family_id}",
                "title": titleize(family_id),
                "notes": (
                    "Owner-approved normalized planning family. Current leaf routes, jurisdictions, "
                    "authority, deadlines and exceptions require staged source evidence."
                ),
                "publisher": "okf-uk-living",
                "resource_count": 0,
                "formats": ["YAML"],
                "topics": [family["domain_title"]],
                "tags": [family["wave"], *delivery_scopes, "normalized-planning"],
                "timestamp": GENERATED_AT,
                "metadata_modified": "2026-08-07",
                "license_id": "MIT",
                "license": "MIT for repository-authored planning metadata; upstream content not acquired",
                "source_url": "generated/browser/source/service-family-denominator.v1.yaml.html",
                "record_type": "Canonical service family planning record",
                "life_course_domain": family["domain_title"],
                "life_course_domain_id": family["domain"],
                "acquisition_wave": family["wave"],
                "delivery_scope": delivery_scopes,
                "jurisdiction": jurisdiction_values(delivery_scopes),
                "implementation_status": "implemented-three-slice" if family_id in implemented else "planned",
                "assertion_status": "normalized",
                "assertion_scope": "real-world",
                "rights_state": ["repository-metadata-mit", "upstream-link-only-not-acquired"],
                "generated": {"by": "process:large-corpus-builder", "at": GENERATED_AT},
                "limitations": [
                    "Planning denominator, not an official service assertion.",
                    "No source snapshot or upstream expression is included.",
                    "Jurisdiction and responsibility require current leaf evidence.",
                ],
            }
        )
    return sorted(result, key=lambda row: row["name"])


def facet_index(rows: list[dict[str, Any]]) -> dict[str, Any]:
    index: dict[str, Any] = {"schema": "okf-facets.v1", "generated_at": GENERATED_AT}
    for key, _, _ in FACETS:
        counts: Counter[str] = Counter()
        for row in rows:
            raw = row.get(key, [])
            values = raw if isinstance(raw, list) else [raw]
            counts.update(str(value) for value in values if str(value))
        index[key] = [
            {"value": value, "count": count}
            for value, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]
    return index


def search_tokens(value: Any) -> set[str]:
    if isinstance(value, dict):
        values = list(value.values())
    else:
        values = value if isinstance(value, list) else [value]
    tokens: set[str] = set()
    for item in values:
        if isinstance(item, (list, dict)):
            tokens.update(search_tokens(item))
            continue
        normalized = "".join(
            character for character in unicodedata.normalize("NFKD", str(item))
            if not unicodedata.combining(character)
        ).lower()
        for token in re.findall(r"[a-z0-9]+", normalized):
            if len(token) >= 2 and token not in SEARCH_STOP_WORDS:
                tokens.add(token)
    return tokens


def search_outputs(rows: list[dict[str, Any]]) -> dict[Path, str]:
    postings: dict[str, list[list[int]]] = defaultdict(list)
    results: list[dict[str, Any]] = []
    doc_map: dict[str, str] = {}
    for ordinal, row in enumerate(rows):
        token_scores: dict[str, list[int]] = {}
        for field, mask, weight in SEARCH_FIELDS:
            for token in search_tokens(row.get(field, [])):
                score, combined_mask = token_scores.setdefault(token, [0, 0])
                token_scores[token] = [score + weight, combined_mask | mask]
        for token, (score, mask) in token_scores.items():
            postings[token].append([ordinal, score, mask])
        doc_map[str(ordinal)] = row["route"]
        results.append(
            {
                "ordinal": ordinal,
                "name": row["name"],
                "title": row["title"],
                "publisher": row["publisher"],
                "publisher_title": "A Life in the UK",
                "resource_count": row.get("resource_count", 0),
                "formats": row["formats"],
                "tags": row["tags"],
                "topics": row["topics"],
                "timestamp": row["timestamp"],
                "notes": row["notes"],
                "license_id": row["license_id"],
                "license_title": row["license"],
                "record_type": row["record_type"],
                "open": row["route"],
            }
        )

    postings_path = "large/data/search/postings.json"
    lexicon_groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for token, token_postings in sorted(postings.items()):
        shard = re.sub(r"[^a-z0-9]", "", token)[:2] or "_"
        lexicon_groups[shard].append(
            {"token": token, "df": len(token_postings), "postings": postings_path}
        )
    lexicon_entrypoints = {
        shard: f"large/data/search/lexicon/{shard}.json" for shard in sorted(lexicon_groups)
    }
    filter_entrypoints = {
        key: f"large/data/search/filters/{key}.json" for key, _, _ in FACETS
    }
    result_paths = [
        f"large/data/search/results-{index // RECORD_CHUNK_SIZE}.json"
        for index in range(0, len(results), RECORD_CHUNK_SIZE)
    ]
    search_manifest = {
        "schema": "okf-static-search.v1",
        "snapshot": SNAPSHOT,
        "token_min_length": 2,
        "prefix_min_length": 3,
        "lexicon_shard_length": 2,
        "result_limit": 200,
        "result_doc_chunk_size": RECORD_CHUNK_SIZE,
        "weights": {field: weight for field, _, weight in SEARCH_FIELDS},
        "field_masks": {field: mask for field, mask, _ in SEARCH_FIELDS},
        "counts": {
            "documents": len(rows),
            "tokens": len(postings),
            "postings": sum(len(values) for values in postings.values()),
            "postings_shards": 1,
            "doc_map_shards": 1,
            "filter_postings_shards": len(filter_entrypoints),
            "max_postings_per_token": max(map(len, postings.values()), default=1),
        },
        "entrypoints": {
            "lexicon": lexicon_entrypoints,
            "prefixes": {},
            "postings": [postings_path],
            "result_docs": result_paths,
            "facets": "large/data/facets.json",
            "doc_map": "large/data/search/doc-map.json",
            "filter_postings": filter_entrypoints,
        },
    }
    outputs = {
        Path("large/data/search/manifest.json"): json_text(search_manifest),
        Path(postings_path): json_text({"tokens": dict(sorted(postings.items()))}),
        Path("large/data/search/doc-map.json"): json_text(doc_map),
    }
    outputs.update({
        Path(path): json_text(results[index:index + RECORD_CHUNK_SIZE])
        for index, path in zip(range(0, len(results), RECORD_CHUNK_SIZE), result_paths, strict=True)
    })
    outputs.update(
        {
            Path(path): json_text(lexicon_groups[shard])
            for shard, path in lexicon_entrypoints.items()
        }
    )
    for key, path in filter_entrypoints.items():
        values: dict[str, list[int]] = defaultdict(list)
        for ordinal, row in enumerate(rows):
            raw = row.get(key, [])
            for value in raw if isinstance(raw, list) else [raw]:
                if str(value):
                    values[str(value)].append(ordinal)
        outputs[Path(path)] = json_text(
            {"schema": "okf-static-filter-postings.v1", "key": key, "values": dict(sorted(values.items()))}
        )
    return outputs


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def relationship_bucket(route: str) -> str:
    value = 0x811C9DC5
    for byte in route.encode("utf-8"):
        value ^= byte
        value = (value * 0x01000193) & 0xFFFFFFFF
    return f"{(value >> 24) & 0xFF:02x}"


def locator_outputs(rows: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[Path, str]]:
    buckets: dict[str, dict[str, list[int]]] = defaultdict(dict)
    for ordinal, row in enumerate(rows):
        buckets[relationship_bucket(row["route"])][row["route"]] = [
            ordinal // RECORD_CHUNK_SIZE,
            ordinal % RECORD_CHUNK_SIZE,
        ]
    paths = {
        bucket: f"large/data/record-locator/{bucket}.json" for bucket in sorted(buckets)
    }
    manifest = {
        "schema": "okf-record-locator-sharded.v1",
        "algorithm": "fnv1a32-prefix-2",
        "snapshot": SNAPSHOT,
        "records": len(rows),
        "chunk_size": RECORD_CHUNK_SIZE,
        "record_chunks": [
            f"large/data/records-{index // RECORD_CHUNK_SIZE}.json"
            for index in range(0, len(rows), RECORD_CHUNK_SIZE)
        ],
        "buckets": paths,
        "bucket_count": len(paths),
    }
    return manifest, {Path(paths[bucket]): json_text(values) for bucket, values in sorted(buckets.items())}


def adjacency_outputs(relationships: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[Path, str]]:
    by_route: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in relationships:
        by_route[edge["source"]].append(edge)
        if edge["target"] != edge["source"]:
            by_route[edge["target"]].append(edge)
    buckets: dict[str, dict[str, list[dict[str, Any]]]] = defaultdict(dict)
    for endpoint, edges in sorted(by_route.items()):
        buckets[relationship_bucket(endpoint)][endpoint] = edges
    paths = {
        bucket: f"large/data/relationship-adjacency/{bucket}.json" for bucket in sorted(buckets)
    }
    manifest = {
        "schema": "okf-relationship-adjacency.v1",
        "algorithm": "fnv1a32-prefix-2",
        "snapshot": SNAPSHOT,
        "routes": len(by_route),
        "relationships": len(relationships),
        "buckets": paths,
    }
    return manifest, {Path(paths[bucket]): json_text(values) for bucket, values in sorted(buckets.items())}


def build_outputs() -> dict[Path, str]:
    denominator, errors = load_service_denominator()
    if denominator:
        errors.extend(validate_service_denominator(denominator))
    if errors:
        raise ValueError("; ".join(sorted(set(errors))))
    rows, resources, relationships, validation = project(denominator)
    locator, locator_shards = locator_outputs(rows)
    adjacency, adjacency_shards = adjacency_outputs(relationships)
    validation.pop("relationship_adjacency", None)
    service_family_count = sum(row.get("record_type") == "Service Family" for row in rows)
    counts = {
        "datasets": len(rows),
        "records": len(rows),
        "concepts": len(rows),
        "service_families": service_family_count,
        "resources": len(resources),
        "publishers": 1,
        "relationships": len(relationships),
    }
    descriptor = {
        "schema": "okf-explorer-large-corpus.v1",
        "kind": "okf-large-corpus",
        "okf_version": "0.2",
        "core_conformance": "OKF Explorer large-corpus life-course projection",
        "title": "A Life in the UK — life-course discovery corpus",
        "description": (
            f"Approved 293-family denominator with {validation['counts']['dossier_backed_families']} "
            "population-complete dossiers, typed linked sources, governed relationships and current authority infrastructure."
        ),
        "version": "life-course-population-stage.v1",
        "status": "approved-for-local-evaluation",
        "assertion_scope": "real-world",
        "publisher": "owner:chris-page-gov",
        "license": "MIT",
        "generated_at": GENERATED_AT,
        "snapshot": SNAPSHOT,
        "entrypoints": {
            "data_manifest": "large/data/manifest.json",
            "overview_index": "large/data/overview.json",
            "analysis_overview": "large/data/analysis/overview.json",
            "presentation": "large/data/presentation.json",
            "search_manifest": "large/data/search/manifest.json",
            "record_locator": "large/data/record-locator.json",
            "relationship_adjacency": "large/data/relationship-adjacency.json",
            "validation_report": "large/data/validation-report.json",
            "json_ld": "generated/semantic/life-course-corpus.jsonld",
            "yaml_ld": "generated/semantic/life-course-corpus.yamlld",
            "markdown_index": "generated/browser/index.html",
            "notes": "generated/browser/evidence/licensing-and-attribution.html",
        },
        "counts": counts,
        "source": {
            "mode": "repository-authored-dossiers-plus-linked-references",
            "denominator": "generated/browser/source/service-family-denominator.v1.yaml.html",
            "authority_registry": "generated/browser/source/authority-registry.v1.yaml.html",
            "policy": "generated/browser/profiles/corpus-acquisition-policy.v1.yaml.html",
            "source_snapshots": False,
            "upstream_content_redistributed": False,
            "publication_authorized": False,
        },
        "performance": {
            "startup_mode": "overview-first",
            "full_record_hydration": "lazy",
            "search": "static worker shards",
        },
        "vocabulary": {
            "record_singular": "concept",
            "record_plural": "concepts",
            "publisher_singular": "project",
            "publisher_plural": "projects",
            "search_placeholder": "Search 293 families and supporting concepts",
        },
    }
    manifest = {
        "title": "A Life in the UK life-course concept manifest",
        "generated_at": GENERATED_AT,
        "snapshot": SNAPSHOT,
        "counts": counts,
        "indexes": {
            "overview": "large/data/overview.json",
            "analysis": "large/data/analysis/overview.json",
            "presentation": "large/data/presentation.json",
            "facets": "large/data/facets.json",
            "search": "large/data/search/manifest.json",
            "record_locator": "large/data/record-locator.json",
            "relationship_adjacency": "large/data/relationship-adjacency.json",
            "validation": "large/data/validation-report.json",
        },
        "chunks": {
            "datasets": locator["record_chunks"],
            "resources": ["large/data/resources-0.json"],
            "publishers": ["large/data/publishers-0.json"],
            "relationships": ["large/data/relationships-0.json"],
        },
    }
    overview = {
        "title": "Life-course discovery corpus",
        "description": (
            "293 normalized families across 24 domains, "
            f"{validation['counts']['dossier_backed_families']} population-complete dossiers, "
            f"{validation['counts']['resources']} typed official links, 397 dated geographies and "
            "438 shared organisations."
        ),
        "counts": counts,
        "status": "approved-for-local-evaluation",
        "notices": [
            "Normalized records are discovery aids, not official service assertions or personal decisions.",
            "Source content is linked and summarized, not redistributed.",
            "GitHub Pages publication has not been authorized.",
        ],
    }
    analysis = {
        "schema": "okf-explorer-analysis.v1",
        "generated_at": GENERATED_AT,
        "summary": {
            "title": "Coverage planning",
            "description": "Colour facets expose population progress while sourced dossiers provide narratives, links and inspectable relationships.",
        },
        "counts": counts,
    }
    presentation = {
        "schema": "okf-explorer-presentation.v1",
        "status": "stable",
        "snapshot": SNAPSHOT,
        "defaults": {"facet_mode": "suggested", "search_threshold": 12, "distribution_segment_limit": 24},
        "facets": [
            {
                "key": key,
                "label": label,
                "description": description,
                "value_type": "nominal",
                "order": index,
                "default_state": "pinned" if index < 4 else "shown",
                "open_control": "distribution",
                "value_order": "count-desc",
            }
            for index, (key, label, description) in enumerate(FACETS, start=1)
        ],
        "panels": {
            "left": {"tabs": ["facets", "browse", "results"], "default_tab": "facets"},
            "right": {"tabs": ["overview", "evidence", "data"], "default_tab": "overview"},
        },
    }
    publishers = [{
        "id": "publisher:okf-uk-living",
        "name": "okf-uk-living",
        "title": "A Life in the UK",
        "state": "repository-authored-life-course-corpus",
        "source_url": "generated/browser/index.html",
    }]
    outputs = {
        Path("okf-explorer.json"): json_text(descriptor),
        Path("large/data/manifest.json"): json_text(manifest),
        Path("large/data/overview.json"): json_text(overview),
        Path("large/data/analysis/overview.json"): json_text(analysis),
        Path("large/data/presentation.json"): json_text(presentation),
        Path("large/data/facets.json"): json_text(facet_index(rows)),
        Path("large/data/resources-0.json"): json_text(resources),
        Path("large/data/publishers-0.json"): json_text(publishers),
        Path("large/data/relationships-0.json"): json_text(relationships),
        Path("large/data/record-locator.json"): json_text(locator),
        Path("large/data/relationship-adjacency.json"): json_text(adjacency),
        Path("large/data/validation-report.json"): json_text(validation),
    }
    outputs.update({
        Path(path): json_text(rows[index:index + RECORD_CHUNK_SIZE])
        for index, path in zip(range(0, len(rows), RECORD_CHUNK_SIZE), locator["record_chunks"], strict=True)
    })
    outputs.update(locator_shards)
    outputs.update(adjacency_shards)
    semantic = semantic_graph(rows, relationships)
    outputs[Path("generated/semantic/life-course-corpus.jsonld")] = json_text(semantic)
    outputs[Path("generated/semantic/life-course-corpus.yamlld")] = yaml.safe_dump(
        semantic, allow_unicode=True, sort_keys=True, width=120
    )
    outputs[Path("generated/semantic/validation-report.json")] = json_text(validation)
    outputs.update(search_outputs(rows))
    return outputs


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, expected in outputs.items():
        target = ROOT / path
        if not target.is_file():
            errors.append(f"{path.as_posix()} is missing")
            continue
        current = target.read_text(encoding="utf-8")
        if current != expected:
            diff = difflib.unified_diff(
                current.splitlines(), expected.splitlines(),
                fromfile=f"current/{path.as_posix()}", tofile=f"generated/{path.as_posix()}", lineterm="",
            )
            errors.append("\n".join(diff))
    return errors


def write_outputs(outputs: dict[Path, str]) -> None:
    if DATA_ROOT.exists():
        shutil.rmtree(DATA_ROOT)
    for path, content in outputs.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when output is absent or stale")
    args = parser.parse_args(argv)
    try:
        outputs = build_outputs()
    except ValueError as error:
        print(f"Large-corpus build failed: {error}", file=sys.stderr)
        return 1
    if args.check:
        errors = check_outputs(outputs)
        if errors:
            print("Large-corpus projection check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print("Large-corpus projection is synchronized: 293 service families and 7 governed facets")
        return 0
    write_outputs(outputs)
    print("wrote local life-course discovery projection")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
