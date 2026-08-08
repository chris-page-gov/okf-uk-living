#!/usr/bin/env python3
"""Build deterministic browser-renderable handoffs for authored source files."""

from __future__ import annotations

import argparse
import difflib
import html
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote, urlparse

from build_okf_bundle import ROOT, load_config, markdown_paths, parse_document


OUTPUT_ROOT = ROOT / "generated" / "browser"
EXTRA_ROOT_FILES = (
    "AGENTS.md",
    "CHANGELOG.md",
    "LICENSE",
    "LICENSE_DECISIONS.md",
    "NOTICE.md",
    "PLANNING.md",
    "README.md",
    "REPOSITORY_STATUS.md",
    "ROADMAP.md",
    "TRACKING.md",
)
LINK_RE = re.compile(r"(?<!!)\[([^\]]+)\]\(([^)]+)\)")


def handoff_paths() -> list[Path]:
    paths = set(markdown_paths(load_config()))
    paths.update(ROOT / name for name in EXTRA_ROOT_FILES if (ROOT / name).is_file())
    for pattern in (
        "source/*.v1.yaml",
        "source/domain-registers/**/*.v1.yaml",
        "source/life-course-families/**/*.v1.yaml",
        "profiles/*.v1.yaml",
        "ontology/*.v1.yaml",
        "shapes/*.v1.yaml",
        "schemas/*.json",
        "evaluation/**/*.v1.yaml",
    ):
        paths.update(path for path in ROOT.glob(pattern) if path.is_file())
    return sorted(paths, key=lambda path: path.relative_to(ROOT).as_posix())


def output_relative_path(source_relative: str | Path) -> Path:
    path = Path(source_relative)
    if path.suffix == ".md":
        return path.with_suffix(".html")
    if path.suffix:
        return path.with_name(f"{path.name}.html")
    return path.with_name(f"{path.name}.html")


def browser_url(source_relative: str | Path) -> str:
    return (Path("generated") / "browser" / output_relative_path(source_relative)).as_posix()


def resolve_local_link(source_relative: Path, href: str) -> Path | None:
    candidate = href.strip()
    if not candidate or candidate.startswith("#"):
        return None
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        return None
    raw_path = unquote(parsed.path)
    if not raw_path:
        return None
    resolved = Path(raw_path.lstrip("/")) if raw_path.startswith("/") else source_relative.parent / raw_path
    normalized = Path(os.path.normpath(resolved.as_posix()))
    if normalized.is_absolute() or ".." in normalized.parts:
        return None
    return normalized


def rewrite_href(source_relative: Path, output_relative: Path, href: str, known: set[Path]) -> str:
    target = resolve_local_link(source_relative, href)
    if target is None or target not in known:
        return href
    parsed = urlparse(href)
    relative = os.path.relpath(output_relative_path(target), start=output_relative.parent)
    suffix = f"?{parsed.query}" if parsed.query else ""
    suffix += f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{relative}{suffix}"


def document_title(path: Path, text: str) -> str:
    if path.suffix == ".md":
        try:
            metadata, body = parse_document(ROOT / path)
        except (OSError, ValueError):
            metadata, body = {}, text
        title = str(metadata.get("title", "")).strip()
        if title:
            return title
        match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
        if match:
            return match.group(1).strip()
    return path.as_posix()


def linked_source(text: str, source_relative: Path, output_relative: Path, known: set[Path]) -> str:
    parts: list[str] = []
    position = 0
    for match in LINK_RE.finditer(text):
        parts.append(html.escape(text[position:match.start()]))
        label, href = match.groups()
        rewritten = rewrite_href(source_relative, output_relative, href, known)
        parts.append(
            f'<a href="{html.escape(rewritten, quote=True)}">'
            f'{html.escape(match.group(0))}</a>'
        )
        position = match.end()
    parts.append(html.escape(text[position:]))
    return "".join(parts)


def render_document(path: Path, known: set[Path]) -> str:
    source = ROOT / path
    text = source.read_text(encoding="utf-8")
    output = output_relative_path(path)
    title = document_title(path, text)
    source_kind = (
        "Markdown" if path.suffix == ".md"
        else "YAML" if path.suffix in {".yaml", ".yml"}
        else "JSON" if path.suffix == ".json"
        else "text"
    )
    linked = linked_source(text, path, output, known)
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} — A Life in the UK</title>
  <style>
    :root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }}
    body {{ margin: 0 auto; max-width: 78rem; padding: 2rem; line-height: 1.5; }}
    .banner {{ border-left: .35rem solid #6b5cff; padding: .75rem 1rem; background: color-mix(in srgb, Canvas 92%, #6b5cff 8%); }}
    pre {{ white-space: pre-wrap; overflow-wrap: anywhere; padding: 1rem; border: 1px solid color-mix(in srgb, CanvasText 22%, transparent); border-radius: .35rem; }}
    a {{ color: #6957e8; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, monospace; }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <p class="banner">Browser-rendered handoff of repository-authored {source_kind}. Source identity: <code>{html.escape(path.as_posix())}</code>. Links and original summaries are shown; external source content is not redistributed.</p>
  <pre>{linked}</pre>
</body>
</html>
"""


def build_outputs() -> dict[Path, str]:
    paths = [path.relative_to(ROOT) for path in handoff_paths()]
    known = set(paths)
    return {output_relative_path(path): render_document(path, known) for path in paths}


def check_outputs(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    expected = set(outputs)
    actual = {
        path.relative_to(OUTPUT_ROOT)
        for path in OUTPUT_ROOT.rglob("*.html")
        if path.is_file()
    } if OUTPUT_ROOT.is_dir() else set()
    for path in sorted(expected - actual):
        errors.append(f"generated/browser/{path.as_posix()} is missing")
    for path in sorted(actual - expected):
        errors.append(f"generated/browser/{path.as_posix()} is unexpected")
    for path in sorted(expected & actual):
        current = (OUTPUT_ROOT / path).read_text(encoding="utf-8")
        if current != outputs[path]:
            diff = difflib.unified_diff(
                current.splitlines(), outputs[path].splitlines(),
                fromfile=f"current/{path.as_posix()}",
                tofile=f"generated/{path.as_posix()}",
                lineterm="",
            )
            errors.append("\n".join(diff))
    return errors


def write_outputs(outputs: dict[Path, str]) -> None:
    if OUTPUT_ROOT.exists():
        shutil.rmtree(OUTPUT_ROOT)
    for path, content in outputs.items():
        destination = OUTPUT_ROOT / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when handoffs are absent or stale")
    args = parser.parse_args(argv)
    outputs = build_outputs()
    if args.check:
        errors = check_outputs(outputs)
        if errors:
            print("Browser handoff check failed:", file=sys.stderr)
            for error in errors:
                print(f"- {error}", file=sys.stderr)
            return 1
        print(f"Browser handoffs are synchronized: {len(outputs)} files")
        return 0
    write_outputs(outputs)
    print(f"wrote {len(outputs)} browser handoffs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
