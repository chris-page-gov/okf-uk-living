#!/usr/bin/env python3
"""Validate this producer's Core 0.3 semantic contract and historical baseline."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from okf_v03 import OKF_SPECIFICATION

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "okf.semantic.json"
SCHEMA_PATH = ROOT / "profiles/bundle-wiki/v2/repository-contract.schema.json"
BASELINE_PATH = ROOT / "evaluation/compatibility/okf-core-v0.2-baseline.v1.json"
PROVENANCE_PATH = ROOT / "profiles/bundle-wiki/v2/provenance.json"
V1_VENDOR_LOCK_SHA256 = "979af714974abb093ac9d4b1b7e289597c61d33c24bb6959d9914c2f74dc6a09"
EXPECTED_BASELINE_COMMIT = "4857e7e7829a23081c2d660f5b1bfe52b8ae8942"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def validate_contract() -> list[str]:
    contract = load_json(CONTRACT_PATH)
    schema = load_json(SCHEMA_PATH)
    baseline = load_json(BASELINE_PATH)
    provenance = load_json(PROVENANCE_PATH)
    errors = [
        f"/{'/'.join(map(str, error.absolute_path))}: {error.message}"
        for error in Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(contract)
    ]
    core = contract.get("okf_core", {})
    if core.get("specification") != OKF_SPECIFICATION:
        errors.append("/okf_core/specification does not match the approved pinned Core 0.3 specification")
    if core.get("status") != "migration":
        errors.append("/okf_core/status must remain migration until separate profile, Reader and release gates pass")
    if baseline.get("schema") != "okf-uk-living-core-v0.2-baseline.v1":
        errors.append("historical Core 0.2 baseline schema is missing or changed")
    if baseline.get("captured_from_commit") != EXPECTED_BASELINE_COMMIT or baseline.get("okf_core_version") != "0.2":
        errors.append("historical Core 0.2 baseline must retain its original commit and version")
    if provenance.get("schema") != "okf-bundle-wiki-v2-local-adoption-provenance.v1" or provenance.get("source_commit") != "16a70b6e2dd62a10e7dc891385a7a8235c72fdb1":
        errors.append("experimental v2 profile provenance must retain its source commit")
    for relative, expected in provenance.get("files", {}).items():
        actual = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        if actual != expected.get("sha256"):
            errors.append(f"experimental profile file hash differs from provenance: {relative}")
    vendor_lock = hashlib.sha256((ROOT / "profiles/bundle-wiki/v1.vendor-lock.json").read_bytes()).hexdigest()
    if vendor_lock != V1_VENDOR_LOCK_SHA256 or provenance.get("unchanged_v1_vendor_lock_sha256") != V1_VENDOR_LOCK_SHA256:
        errors.append("historical Bundle Wiki v1 vendor lock changed")
    return sorted(set(errors))


def main() -> int:
    errors = validate_contract()
    if errors:
        print("Semantic contract checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Semantic contract checks passed: pinned Core 0.3 migration, experimental Bundle Wiki v2, historical Core 0.2 baseline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
