#!/usr/bin/env python3
"""Validate authored life-course family dossiers and canonical source links."""

from __future__ import annotations

from life_course_dossiers import load_dossiers, resolve_sources


BASELINE_FAMILY_IDS = {
    "report-missed-rubbish-collection",
    "learn-to-drive-car",
    "respond-to-speeding-notice",
    "register-a-death",
    "notify-organisations-after-a-death",
    "administer-an-estate",
}


def expected_population_family_ids() -> set[str]:
    import yaml

    from build_okf_bundle import ROOT

    result = set(BASELINE_FAMILY_IDS)
    for path in sorted((ROOT / "source" / "domain-registers").glob("*.v1.yaml")):
        value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if value.get("register_version") != "life-course-domain-register.v1":
            continue
        result.update(
            str(family.get("id", ""))
            for family in value.get("families", []) if isinstance(family, dict)
        )
    return result


def validate_life_course_dossiers() -> list[str]:
    dossiers, errors = load_dossiers()
    expected_ids = expected_population_family_ids()
    if set(dossiers) != expected_ids:
        errors.append(
            "dossier population stage does not match the six-family baseline plus authored domain registers"
        )
    baseline_resolved = [
        source for family_id, dossier in dossiers.items()
        if family_id in BASELINE_FAMILY_IDS
        for source in resolve_sources(dossier)[0]
    ]
    if len(baseline_resolved) != 53 or len({source['id'] for source in baseline_resolved}) != 53:
        errors.append("the proven three-slice baseline must retain its uniquely partitioned 53 sources")
    return sorted(set(errors))


def main() -> int:
    errors = validate_life_course_dossiers()
    if errors:
        for error in errors:
            print(error)
        return 1
    dossiers, _ = load_dossiers()
    source_count = sum(len(resolve_sources(dossier)[0]) for dossier in dossiers.values())
    print(f"Life-course dossier checks passed: {len(dossiers)} families and {source_count} resolved source assertions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
