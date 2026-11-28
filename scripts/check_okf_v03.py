#!/usr/bin/env python3
"""Run the bounded OKF Core 0.3 structural check for the configured bundle corpus."""

from pathlib import Path

from okf_v03 import OKF_SPECIFICATION, validate_bundle

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    report = validate_bundle(ROOT)
    print(
        f"OKF Core {report['okf_version']} structural validation passed: "
        f"{report['concept_count']} typed Markdown concepts across "
        f"{report['markdown_document_count']} Markdown files; "
        f"specification {OKF_SPECIFICATION}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
