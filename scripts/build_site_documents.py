#!/usr/bin/env python3
"""Build or check the additive static-document publication surface."""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

from build_okf_bundle import ROOT
from site_document_publications import build_site_document_outputs


EXTRA_MAPPING = {
    Path("explore/index.html"): Path("explore/index.html"),
    Path("explore-okf.json"): Path("explore-okf.json"),
    Path("generated/browser/README.html"): Path("generated/browser/README.html"),
    Path("generated/assurance/population-complete-report.json"): Path(
        "generated/assurance/population-complete-report.json"
    ),
}


def expected_outputs() -> dict[Path, str]:
    outputs, _, _ = build_site_document_outputs(ROOT, extra_mapping=EXTRA_MAPPING)
    return outputs


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, expected in outputs.items():
        target = ROOT / path
        if not target.is_file():
            errors.append(f"{path.as_posix()} is missing")
            continue
        actual = target.read_text(encoding="utf-8")
        if actual == expected:
            continue
        errors.append(
            "\n".join(
                difflib.unified_diff(
                    actual.splitlines(),
                    expected.splitlines(),
                    fromfile=f"current/{path.as_posix()}",
                    tofile=f"generated/{path.as_posix()}",
                    lineterm="",
                )
            )
        )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    try:
        outputs = expected_outputs()
        if args.check:
            errors = check_outputs(outputs)
            if errors:
                for error in errors:
                    print(error, file=sys.stderr)
                return 1
        else:
            for path, content in outputs.items():
                target = ROOT / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
        print(
            f"Site document publication passed: {len(outputs) - 1} HTML pages, "
            "one manifest and no corpus rebuild"
        )
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
