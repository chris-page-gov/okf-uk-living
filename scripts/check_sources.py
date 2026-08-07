#!/usr/bin/env python3
"""Validate bounded linked-reference source registers."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "source"
RIGHTS_REGISTER_NAME = "rights-decisions.v1.yaml"
REFERENCE_INVENTORY_NAME = "exhaustive-reference-inventory.v1.yaml"
SERVICE_DENOMINATOR_NAME = "service-family-denominator.v1.yaml"
RECORDED_RIGHTS_POLICY = "link_and_summarize_source_family_decisions_recorded"
RECORDED_RIGHTS_BASIS = "linked_reference_summary_only_source_family_decision_recorded"
EXPECTED_MISSED_RUBBISH_IDS = {
    "govuk-missed-bin-collection",
    "coventry-missed-bin",
    "coventry-complaints",
    "edinburgh-missed-bin",
    "edinburgh-complaints",
    "cardiff-missed-collection",
    "cardiff-complaints",
    "belfast-missed-bin",
    "belfast-complaints",
    "lgsco-waste-and-refuse",
    "spso-making-a-complaint",
    "psow-how-to-complain",
    "nipso-complaints",
}
EXPECTED_DRIVING_SPEEDING_IDS = {
    "govuk-learn-to-drive-car",
    "govuk-first-provisional-licence",
    "govuk-private-practice",
    "govuk-book-theory-test",
    "govuk-driving-test-result",
    "govuk-full-driving-licence",
    "nidirect-provisional-licence",
    "nidirect-learner-rules",
    "nidirect-theory-test",
    "nidirect-practical-test",
    "nidirect-claim-test-pass",
    "govuk-speeding-penalties",
    "legislation-rta-1988-section-172",
    "govuk-single-justice-procedure",
    "govuk-appeal-magistrates-decision",
    "copfs-prosecution-code",
    "mygov-scotland-criminal-appeal",
    "nidirect-speeding-penalties",
    "nidirect-fixed-penalties",
    "nidirect-appealing-verdict",
}
EXPECTED_BEREAVEMENT_IDS = {
    "govuk-register-a-death",
    "govuk-tell-us-once",
    "govuk-arrange-funeral",
    "govuk-applying-for-probate",
    "govuk-value-estate",
    "govuk-probate-estate",
    "govuk-inheritance-tax",
    "govuk-correcting-death-registration",
    "nrs-registering-a-death",
    "copfs-death-investigation",
    "govscot-after-a-death",
    "scotcourts-confirmation",
    "nidirect-registering-a-death",
    "nidirect-coroners",
    "nidirect-who-to-tell",
    "nidirect-bereavement-service",
    "nidirect-arranging-funeral",
    "nidirect-apply-probate",
    "nidirect-no-will",
    "nidirect-debt-after-death",
}
EXPECTED_SOURCE_IDS = {
    "missed-rubbish-collection": EXPECTED_MISSED_RUBBISH_IDS,
    "learning-to-drive-speeding": EXPECTED_DRIVING_SPEEDING_IDS,
    "death-bereavement-estate": EXPECTED_BEREAVEMENT_IDS,
}
REQUIRED_SOURCE_FIELDS = {
    "id",
    "owner",
    "authority_role",
    "resource",
    "access_method",
    "version_model",
    "update_cadence",
    "rights_basis",
    "coverage",
    "exclusions",
    "observed_at",
    "checksum",
}


def _nonempty(value: Any) -> bool:
    return bool(value.strip()) if isinstance(value, str) else bool(value)


def load_source_registers() -> tuple[list[dict[str, Any]], list[str]]:
    registers: list[dict[str, Any]] = []
    errors: list[str] = []
    for path in sorted(SOURCE_DIR.glob("*.v1.yaml")):
        if path.name in {RIGHTS_REGISTER_NAME, REFERENCE_INVENTORY_NAME, SERVICE_DENOMINATOR_NAME}:
            continue
        try:
            value = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as error:
            errors.append(f"{path.relative_to(ROOT)}: {error}")
            continue
        if not isinstance(value, dict):
            errors.append(f"{path.relative_to(ROOT)}: root must be a mapping")
            continue
        value["_path"] = path.relative_to(ROOT).as_posix()
        registers.append(value)
    return registers, errors


def validate_source_register(register: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    prefix = str(register.get("_path", "source register"))
    for field in ("register_version", "slice_id", "status", "observed_at", "acquisition", "sources"):
        if not _nonempty(register.get(field)):
            errors.append(f"{prefix}: {field} must be non-empty")
    if register.get("register_version") != "source-register.v1":
        errors.append(f"{prefix}: register_version must be source-register.v1")
    if register.get("status") != "linked_references_registered":
        errors.append(f"{prefix}: status must be linked_references_registered")

    acquisition = register.get("acquisition", {})
    if not isinstance(acquisition, dict):
        errors.append(f"{prefix}: acquisition must be a mapping")
        acquisition = {}
    if acquisition.get("mode") != "linked_reference_only":
        errors.append(f"{prefix}: acquisition.mode must be linked_reference_only")
    if acquisition.get("snapshots_acquired") is not False:
        errors.append(f"{prefix}: snapshots_acquired must be false")
    if acquisition.get("broad_acquisition") is not False:
        errors.append(f"{prefix}: broad_acquisition must be false")
    if acquisition.get("rights_policy") != RECORDED_RIGHTS_POLICY:
        errors.append(f"{prefix}: acquisition.rights_policy must record source-family decisions")

    sources = register.get("sources", [])
    if not isinstance(sources, list):
        errors.append(f"{prefix}: sources must be a list")
        return errors
    ids: list[str] = []
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            errors.append(f"{prefix}: sources[{index}] must be a mapping")
            continue
        missing = sorted(field for field in REQUIRED_SOURCE_FIELDS if not _nonempty(source.get(field)))
        if missing:
            errors.append(f"{prefix}: sources[{index}] missing: {', '.join(missing)}")
        source_id = str(source.get("id", ""))
        ids.append(source_id)
        resource = str(source.get("resource", ""))
        parsed = urlparse(resource)
        if parsed.scheme != "https" or not parsed.netloc:
            errors.append(f"{prefix}: {source_id or index} resource must be an HTTPS URL")
        if source.get("checksum") != "not_applicable_no_snapshot":
            errors.append(f"{prefix}: {source_id or index} must not claim a snapshot checksum")
        if source.get("rights_basis") != RECORDED_RIGHTS_BASIS:
            errors.append(
                f"{prefix}: {source_id or index} rights basis must retain linked-summary limits "
                "and record a source-family decision"
            )
    if len(ids) != len(set(ids)):
        errors.append(f"{prefix}: source ids must be unique")
    slice_id = str(register.get("slice_id", ""))
    expected_ids = EXPECTED_SOURCE_IDS.get(slice_id)
    if expected_ids is None:
        errors.append(f"{prefix}: slice_id has no approved source denominator")
    elif set(ids) != expected_ids:
        errors.append(
            f"{prefix}: {slice_id} source denominator must contain the approved "
            f"{len(expected_ids)} references"
        )
    return errors


def validate_source_registers() -> tuple[list[dict[str, Any]], list[str]]:
    registers, errors = load_source_registers()
    if not registers:
        errors.append("source: at least one versioned source register is required")
    for register in registers:
        errors.extend(validate_source_register(register))
    return registers, sorted(set(errors))


def main() -> int:
    registers, errors = validate_source_registers()
    if errors:
        for error in errors:
            print(error)
        return 1
    source_count = sum(len(register["sources"]) for register in registers)
    print(f"Source checks passed: {len(registers)} registers, {source_count} linked references, 0 snapshots")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
