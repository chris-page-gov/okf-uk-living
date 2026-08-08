#!/usr/bin/env python3
"""Validate the frozen local population-complete assurance candidate."""

from __future__ import annotations

import json

from build_okf_bundle import ROOT
from build_population_assurance import build_reports, check_outputs


def validate_population_assurance() -> list[str]:
    outputs, errors = build_reports()
    errors.extend(check_outputs(outputs))
    if errors:
        return sorted(set(errors))
    manifest = json.loads(outputs[next(path for path in outputs if path.name == "candidate-manifest.json")])
    population = json.loads(outputs[next(path for path in outputs if path.name == "population-complete-report.json")])
    omissions = json.loads(outputs[next(path for path in outputs if path.name == "omission-report.json")])
    if manifest.get("status") != "frozen_local_population_complete":
        errors.append("candidate manifest must be frozen_local_population_complete")
    if manifest.get("gates") != {
        "population_complete": True,
        "publication_authorized": False,
        "release_grade": False,
    }:
        errors.append("candidate manifest must separate population, release and publication gates")
    if population.get("status") != "population-complete":
        errors.append("population assurance report must pass")
    if omissions.get("blocking_omissions"):
        errors.append("population assurance must have zero blocking omissions")
    return sorted(set(errors))


def main() -> int:
    errors = validate_population_assurance()
    if errors:
        for error in errors:
            print(error)
        return 1
    population = json.loads((ROOT / "generated/assurance/population-complete-report.json").read_text(encoding="utf-8"))
    counts = population["counts"]
    print(
        "Population assurance passed: "
        f"{counts['service_families']} families, {counts['life_course_domains']} domains, "
        f"{counts['competency_questions']} questions, {counts['relationships']} relationships, "
        "0 blocking omissions, publication disabled"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
