"""OKF Core 0.3 structural validator for this producer migration.

This validates Markdown frontmatter and reserved root/index/log semantics. It
does not certify source accuracy, profile conformance or Reader behaviour.
"""

from __future__ import annotations

import json
import posixpath
import re
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


OKF_VERSION = "0.3"
OKF_SPEC_COMMIT = "527e81aff55992be21507e97004286789126f88c"
OKF_SPECIFICATION = (
    "https://github.com/open-knowledge-format/open-knowledge-format/blob/"
    f"{OKF_SPEC_COMMIT}/SPEC.md"
)


class OKFConformanceError(ValueError):
    """Raised when the supported Core 0.3 structural contract fails."""


class _UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate and non-string keys."""


def _construct_mapping(loader: _UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    loader.flatten_mapping(node)
    result: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise OKFConformanceError("frontmatter mapping keys must be strings")
        if key in result:
            raise OKFConformanceError(f"duplicate frontmatter key {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


_UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


@dataclass(frozen=True)
class Document:
    frontmatter: dict[str, Any] | None
    body: str


def parse_document(path: Path) -> Document:
    """Parse YAML frontmatter without dropping extension fields."""

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        return Document(None, text)
    closing = next(
        (i for i in range(1, len(lines)) if lines[i].rstrip("\r\n") == "---"),
        None,
    )
    if closing is None:
        raise OKFConformanceError(f"{path}: frontmatter is not closed")
    raw = "".join(lines[1:closing])
    try:
        value = yaml.load(raw, Loader=_UniqueKeyLoader)
    except yaml.YAMLError as exc:
        raise OKFConformanceError(f"{path}: frontmatter is not valid YAML 1.2") from exc
    if not isinstance(value, Mapping):
        raise OKFConformanceError(f"{path}: frontmatter must be a YAML mapping")
    if any(not isinstance(key, str) for key in value):
        raise OKFConformanceError(f"{path}: frontmatter keys must be strings")
    return Document(dict(value), "".join(lines[closing + 1 :]))


def _markdown_files(root: Path) -> list[Path]:
    """Return the Markdown corpus selected by the producer configuration."""

    config = json.loads((root / "okf.config.json").read_text(encoding="utf-8"))
    sections = config["corpora"][0].get("sectionOrder", [])
    files = [root / name for name in ("index.md", "log.md") if (root / name).is_file()]
    for section in sections:
        if section == "root":
            continue
        directory = root / section
        if directory.is_dir():
            files.extend(path for path in directory.rglob("*.md") if not path.is_symlink())
    return sorted(set(files))


def validate_bundle(root: Path) -> dict[str, Any]:
    """Validate the repository's root bundle against Core 0.3 structure."""

    root = root.resolve()
    root_index = root / "index.md"
    if not root_index.is_file():
        raise OKFConformanceError("bundle root index.md is required by this producer")

    markdown_files = _markdown_files(root)
    concept_ids: list[str] = []
    warnings: list[str] = []
    for path in markdown_files:
        relative = path.relative_to(root).as_posix()
        document = parse_document(path)
        if path.name == "index.md":
            if path == root_index:
                if document.frontmatter is None or document.frontmatter.get("okf_version") != OKF_VERSION:
                    raise OKFConformanceError("root index.md must declare okf_version: \"0.3\"")
            elif document.frontmatter is not None:
                raise OKFConformanceError(f"{relative}: subordinate index.md must not have frontmatter")
            continue
        if path.name == "log.md":
            if document.frontmatter is not None:
                raise OKFConformanceError(f"{relative}: log.md must not have frontmatter")
            continue
        fields = document.frontmatter
        if fields is None or not isinstance(fields.get("type"), str) or not fields["type"].strip():
            if fields is not None:
                warnings.append(f"{relative}: Markdown without a non-empty type is not a concept")
            continue
        concept_ids.append(relative[:-3])

    return {
        "schema": "okf-uk-living-core-v0.3-validation.v1",
        "specification": OKF_SPECIFICATION,
        "okf_version": OKF_VERSION,
        "markdown_document_count": len(markdown_files),
        "concept_count": len(concept_ids),
        "concept_ids": concept_ids,
        "warnings": warnings,
        "unknown_extension_fields_preserved": True,
    }


def resolve_path_field(document_path: str, value: str) -> str | None:
    """Resolve a Core 0.3 path field, returning None for a URI or external path."""

    value = value.strip()
    if not value or urlsplit(value).scheme:
        return None
    decoded = unquote(urlsplit(value).path)
    if not decoded:
        return None
    target = decoded.lstrip("/") if decoded.startswith("/") else posixpath.join(
        posixpath.dirname(document_path), decoded
    )
    normalized = posixpath.normpath(target)
    if normalized == ".." or normalized.startswith("../") or normalized.startswith("/"):
        return None
    return normalized


def _timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value if value.tzinfo is not None else None
    if isinstance(value, date):
        return datetime.combine(value, time.min, tzinfo=timezone.utc)
    if not isinstance(value, str):
        return None
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        try:
            return datetime.combine(date.fromisoformat(value), time.min, tzinfo=timezone.utc)
        except ValueError:
            return None
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})", value):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    return parsed if parsed.tzinfo is not None else None


def trust_tier(fields: Mapping[str, Any]) -> str:
    """Calculate the Core 0.3 trust tier from current verification events."""

    generated = fields.get("generated")
    generated_at = generated.get("at") if isinstance(generated, Mapping) else None
    parsed_generated = _timestamp(generated_at) if generated_at is not None else None
    if generated_at is not None and parsed_generated is None:
        return "unverified"

    verified = fields.get("verified")
    events = verified if isinstance(verified, list) else [verified]
    current_human = False
    current_machine = False
    for event in events:
        if not isinstance(event, Mapping):
            continue
        actor = event.get("by")
        event_at = _timestamp(event.get("at"))
        if not isinstance(actor, str) or not actor or event_at is None:
            continue
        if parsed_generated is not None and event_at < parsed_generated:
            continue
        if parsed_generated is None and generated_at is not None:
            continue
        if actor.startswith("human:") and actor.removeprefix("human:"):
            current_human = True
        else:
            current_machine = True
    if current_human:
        return "human-reviewed"
    if current_machine:
        return "machine-confirmed"
    return "unverified"
