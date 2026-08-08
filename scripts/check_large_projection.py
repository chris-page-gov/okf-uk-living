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
    rows = load_json("large/data/records-0.json")
    facets = load_json("large/data/facets.json")
    presentation = load_json("large/data/presentation.json")
    search = load_json("large/data/search/manifest.json")
    search_results = load_json("large/data/search/results-0.json")
    search_postings = load_json("large/data/search/postings.json").get("tokens", {})
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
    if len(rows) != 293 or descriptor.get("counts", {}).get("records") != len(rows):
        errors.append("large projection must contain exactly the approved 293 families")
    if search.get("counts", {}).get("documents") != len(rows) or len(search_results) != len(rows):
        errors.append("static search must cover all approved planning families")
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
        errors.append("large projection family names must be unique")
    if any(row.get("assertion_status") != "normalized" for row in rows):
        errors.append("every large projection record must remain normalized")
    if any(row.get("resource_count") != 0 for row in rows):
        errors.append("planning records must not claim acquired resources")
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
    print("Large-corpus checks passed: 293 searchable planning records, 7 reconciled facets, 0 source snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
