#!/usr/bin/env python3
"""Validate generated relationship planes against the pinned OKF schema."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

from build_okf_bundle import ROOT


SEMANTIC_ASSERTION_SCHEMA_PATH = ROOT / "schemas" / "semantic-assertion.schema.json"
SEMANTIC_ASSERTION_SCHEMA_RELATIVE_PATH = "schemas/semantic-assertion.schema.json"
SEMANTIC_ASSERTION_SCHEMA_URL = (
    "https://chris-page-gov.github.io/okf-explorer/profile/"
    "bundle-wiki/v1/semantic-assertion.schema.json"
)
SEMANTIC_ASSERTION_SCHEMA_DRAFT = "https://json-schema.org/draft/2020-12/schema"
SEMANTIC_ASSERTION_SCHEMA_SHA256 = (
    "f69480328db4b64d678d9c50b6534d808000f7fb50a30e8cc9e3bf2facbcb8bc"
)
SEMANTIC_ASSERTION_SCHEMA_BYTES = 7_308


def _types(node: dict[str, Any]) -> list[str]:
    value = node.get("@type", [])
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def is_relationship_assertion(node: dict[str, Any]) -> bool:
    return any(value.endswith("RelationshipAssertion") for value in _types(node))


def _json_pointer(parts: Iterable[Any]) -> str:
    encoded = [str(part).replace("~", "~0").replace("/", "~1") for part in parts]
    return "/" + "/".join(encoded) if encoded else ""


@lru_cache(maxsize=1)
def semantic_assertion_validator() -> Draft202012Validator:
    raw = SEMANTIC_ASSERTION_SCHEMA_PATH.read_bytes()
    observed_sha256 = hashlib.sha256(raw).hexdigest()
    if observed_sha256 != SEMANTIC_ASSERTION_SCHEMA_SHA256:
        raise ValueError(
            "pinned semantic assertion schema digest differs: "
            f"expected {SEMANTIC_ASSERTION_SCHEMA_SHA256}, got {observed_sha256}"
        )
    if len(raw) != SEMANTIC_ASSERTION_SCHEMA_BYTES:
        raise ValueError(
            "pinned semantic assertion schema size differs: "
            f"expected {SEMANTIC_ASSERTION_SCHEMA_BYTES}, got {len(raw)}"
        )
    schema = json.loads(raw)
    if schema.get("$schema") != SEMANTIC_ASSERTION_SCHEMA_DRAFT:
        raise ValueError("semantic assertion schema is not Draft 2020-12")
    if schema.get("$id") != SEMANTIC_ASSERTION_SCHEMA_URL:
        raise ValueError("semantic assertion schema has an unexpected canonical ID")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema, format_checker=FormatChecker())


def runtime_relationship_as_assertion(edge: dict[str, Any]) -> dict[str, Any]:
    """Map one rich runtime row to its semantic reification deterministically."""

    assertion = {
        "@id": edge.get("id"),
        "@type": ["rdf:Statement", "okf:RelationshipAssertion"],
        "source": {"@id": edge.get("source_iri")},
        "source_route": edge.get("source"),
        "predicate": {"@id": edge.get("predicate")},
        "target": {"@id": edge.get("target_iri")},
        "target_route": edge.get("target"),
    }
    assertion.update(
        {
            key: value
            for key, value in edge.items()
            if key
            not in {
                "schema",
                "id",
                "source",
                "source_iri",
                "predicate",
                "target",
                "target_iri",
            }
        }
    )
    return assertion


def validate_assertions(
    assertions: Iterable[dict[str, Any]], *, plane: str
) -> tuple[int, list[dict[str, Any]]]:
    validator = semantic_assertion_validator()
    checked = 0
    violations: list[dict[str, Any]] = []
    for assertion in assertions:
        checked += 1
        errors = sorted(
            validator.iter_errors(assertion),
            key=lambda error: (
                tuple(str(part) for part in error.absolute_path),
                tuple(str(part) for part in error.absolute_schema_path),
                error.message,
            ),
        )
        for error in errors:
            violations.append(
                {
                    "code": "semantic.assertion-schema",
                    "plane": plane,
                    "assertion_id": assertion.get("@id", ""),
                    "instance_path": _json_pointer(error.absolute_path),
                    "schema_path": _json_pointer(error.absolute_schema_path),
                    "message": error.message,
                }
            )
    return checked, violations


def validate_relationship_planes(
    semantic: dict[str, Any], relationships: list[dict[str, Any]]
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    graph = semantic.get("@graph", [])
    if not isinstance(graph, list):
        raise ValueError("semantic document @graph must be a list")
    semantic_assertions = [
        node
        for node in graph
        if isinstance(node, dict) and is_relationship_assertion(node)
    ]
    semantic_checked, semantic_violations = validate_assertions(
        semantic_assertions, plane="semantic"
    )
    runtime_checked, runtime_violations = validate_assertions(
        (runtime_relationship_as_assertion(edge) for edge in relationships),
        plane="runtime",
    )
    violations = semantic_violations + runtime_violations
    receipt = {
        "status": "conformant" if not violations else "non-conformant",
        "draft": SEMANTIC_ASSERTION_SCHEMA_DRAFT,
        "schema": SEMANTIC_ASSERTION_SCHEMA_URL,
        "schema_path": SEMANTIC_ASSERTION_SCHEMA_RELATIVE_PATH,
        "schema_sha256": SEMANTIC_ASSERTION_SCHEMA_SHA256,
        "schema_bytes": SEMANTIC_ASSERTION_SCHEMA_BYTES,
        "semantic_assertions_checked": semantic_checked,
        "runtime_relationships_checked": runtime_checked,
        "violation_count": len(violations),
    }
    return receipt, violations
