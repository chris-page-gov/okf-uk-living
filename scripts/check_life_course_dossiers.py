#!/usr/bin/env python3
"""Validate authored life-course family dossiers and canonical source links."""

from __future__ import annotations

from life_course_dossiers import load_dossiers, resolve_sources


def validate_life_course_dossiers() -> list[str]:
    dossiers, errors = load_dossiers()
    resolved = [source for dossier in dossiers.values() for source in resolve_sources(dossier)[0]]
    if len(dossiers) == 6:
        if len(resolved) != 53:
            errors.append(f"three-slice migration must resolve exactly 53 source assertions, found {len(resolved)}")
        if len({source['id'] for source in resolved}) != 53:
            errors.append("three-slice migration source assertions must be uniquely partitioned")
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
