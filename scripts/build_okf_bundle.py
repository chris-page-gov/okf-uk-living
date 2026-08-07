#!/usr/bin/env python3
"""Build the deterministic OKF Explorer small bundle from authored Markdown."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import yaml


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "okf.config.json"
DEFAULT_OUTPUT = ROOT / "okf-bundle.json"
ROOT_FILES = ("index.md", "log.md")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?(.*)\Z", re.DOTALL)
LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")


def load_config() -> dict[str, Any]:
    return json.loads(CONFIG.read_text(encoding="utf-8"))


def section_names(config: dict[str, Any]) -> list[str]:
    configured = config["corpora"][0].get("sectionOrder", [])
    return [str(value) for value in configured if str(value) != "root"]


def markdown_paths(config: dict[str, Any]) -> list[Path]:
    paths = [ROOT / name for name in ROOT_FILES if (ROOT / name).is_file()]
    for section in section_names(config):
        directory = ROOT / section
        if directory.is_dir():
            paths.extend(directory.rglob("*.md"))
    return sorted(set(paths), key=lambda path: path.relative_to(ROOT).as_posix())


def parse_document(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}, text
    value = yaml.safe_load(match.group(1)) or {}
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: frontmatter must be a mapping")
    return value, match.group(2)


def heading(body: str, fallback: str) -> str:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else fallback


def introduction(body: str, fallback: str) -> str:
    for block in re.split(r"\n\s*\n", body):
        candidate = " ".join(line.strip() for line in block.splitlines()).strip()
        if candidate and not candidate.startswith(("#", "-", "*", "|", "```", ">")):
            return candidate
    return fallback


def reserved_metadata(path_id: str, metadata: dict[str, Any], body: str) -> dict[str, Any]:
    path = Path(path_id)
    if path.name == "index.md":
        fallback = "A Life in the UK" if path_id == "index.md" else path.parent.name.replace("-", " ").title()
        return {
            **metadata,
            "type": "Index",
            "title": heading(body, fallback),
            "description": introduction(body, "Progressive-disclosure OKF section index."),
            "status": "draft" if path_id != "index.md" else "stable",
        }
    if path.name == "log.md":
        return {
            "type": "Log",
            "title": heading(body, "OKF change log"),
            "description": "Chronological OKF bundle update log.",
            "status": "stable",
        }
    return metadata


def validate_document(path_id: str, metadata: dict[str, Any], body: str) -> list[str]:
    errors: list[str] = []
    path = Path(path_id)
    if path.name == "index.md":
        allowed = {"okf_version"} if path_id == "index.md" else set()
        unexpected = sorted(set(metadata) - allowed)
        if unexpected:
            errors.append(f"{path_id}: reserved index has unsupported frontmatter: {', '.join(unexpected)}")
        if path_id == "index.md" and metadata.get("okf_version") != "0.2":
            errors.append(f'{path_id}: bundle root must declare okf_version: "0.2"')
    elif path.name == "log.md":
        if metadata:
            errors.append(f"{path_id}: reserved log must not have frontmatter")
        dates = re.findall(r"^##\s+(\d{4}-\d{2}-\d{2})\s*$", body, re.MULTILINE)
        if dates != sorted(dates, reverse=True):
            errors.append(f"{path_id}: date headings must be newest first")
    else:
        for field in ("type", "title", "description"):
            if not str(metadata.get(field, "")).strip():
                errors.append(f"{path_id}: missing non-empty {field!r} frontmatter")
    if not re.search(r"^#\s+\S", body, re.MULTILINE):
        errors.append(f"{path_id}: missing top-level heading")
    return errors


def resolve_link(source_id: str, href: str) -> str | None:
    href = href.strip()
    if not href or href.startswith("#") or re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", href):
        return None
    href = unquote(href.split("#", 1)[0].split("?", 1)[0])
    if not href:
        return None
    target = Path(href.lstrip("/")) if href.startswith("/") else Path(source_id).parent / href
    return os.path.normpath(target.as_posix()).replace("\\", "/")


def route_slug(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "index"


def route_aliases(path_id: str, metadata: dict[str, Any]) -> list[str]:
    aliases = {
        route_slug(Path(path_id).with_suffix("").as_posix()),
        path_id.lower(),
        path_id.removesuffix(".md").lower(),
    }
    raw = metadata.get("aliases", [])
    values = raw if isinstance(raw, list) else str(raw).split(";")
    aliases.update(route_slug(str(value)) for value in values if str(value).strip())
    return sorted(aliases)


def build_bundle() -> tuple[dict[str, Any], list[str]]:
    config = load_config()
    paths = markdown_paths(config)
    known_ids = {path.relative_to(ROOT).as_posix() for path in paths}
    nodes: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    for path in paths:
        path_id = path.relative_to(ROOT).as_posix()
        try:
            raw_metadata, body = parse_document(path)
        except (OSError, ValueError, yaml.YAMLError) as error:
            errors.append(str(error))
            continue
        errors.extend(validate_document(path_id, raw_metadata, body))
        metadata = reserved_metadata(path_id, raw_metadata, body)
        generated = metadata.get("generated") if isinstance(metadata.get("generated"), dict) else {}
        timestamp = str(generated.get("at") or metadata.get("timestamp") or "")
        section = path_id.split("/", 1)[0] if "/" in path_id else "root"
        nodes[path_id] = {
            **metadata,
            "id": path_id,
            "title": str(metadata.get("title") or heading(body, path.stem)),
            "description": str(metadata.get("description") or introduction(body, path_id)),
            "timestamp": timestamp,
            "route_aliases": route_aliases(path_id, metadata),
            "section": section,
            "source": path_id,
            "body": body,
        }

    edges: list[dict[str, str]] = []
    for source_id, node in sorted(nodes.items()):
        for match in LINK_RE.finditer(str(node.get("body", ""))):
            target_id = resolve_link(source_id, match.group(1))
            if not target_id or not target_id.endswith(".md"):
                continue
            target_path = ROOT / target_id
            if not target_path.is_file():
                errors.append(f"{source_id}: link targets missing Markdown file {target_id}")
            elif target_id in known_ids:
                kind = "lists" if node.get("type") == "Index" else "references"
                edges.append({"source": source_id, "target": target_id, "kind": kind, "label": kind})

    corpus_config = config["corpora"][0]
    timestamps = sorted(node["timestamp"] for node in nodes.values() if node.get("timestamp"))
    generated_at = timestamps[-1] if timestamps else ""
    corpus = {
        "id": corpus_config["id"],
        "label": corpus_config["label"],
        "title": corpus_config["title"],
        "subtitle": corpus_config["subtitle"],
        "root": corpus_config["root"],
        "source_root": corpus_config["sourceRoot"],
        "markdown_url": corpus_config["markdownUrl"],
        "sections": [section for section in corpus_config["sectionOrder"] if section == "root" or any(node["section"] == section for node in nodes.values())],
        "nodes": dict(sorted(nodes.items())),
        "edges": sorted(edges, key=lambda edge: (edge["source"], edge["target"], edge["kind"])),
    }
    bundle = {
        "schema": "okf-explorer-bundle.v0",
        "kind": "okf-bundle",
        "okf_version": "0.2",
        "generated_by": "scripts/build_okf_bundle.py",
        "generated_at": generated_at,
        "meta": {
            "title": config["siteTitle"],
            "default_corpus": corpus_config["id"],
            "corpus_order": [corpus_config["id"]],
            "core_conformance": "OKF v0.2",
            "status": "research-and-implementation-scaffold",
        },
        "corpora": {corpus_config["id"]: corpus},
    }
    return bundle, sorted(set(errors))


def render(bundle: dict[str, Any]) -> str:
    return json.dumps(bundle, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when output is absent or stale")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    output = args.output if args.output.is_absolute() else ROOT / args.output
    bundle, errors = build_bundle()
    if errors:
        print("OKF build failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    content = render(bundle)
    if args.check:
        if not output.is_file():
            print(f"{output.relative_to(ROOT)} is missing", file=sys.stderr)
            return 1
        current = output.read_text(encoding="utf-8")
        if current != content:
            diff = difflib.unified_diff(current.splitlines(), content.splitlines(), fromfile="current", tofile="generated", lineterm="")
            print("\n".join(diff), file=sys.stderr)
            return 1
        node_count = len(next(iter(bundle["corpora"].values()))["nodes"])
        print(f"okf-bundle.json is synchronized with {node_count} nodes")
        return 0
    output.write_text(content, encoding="utf-8")
    print(f"wrote {output.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
