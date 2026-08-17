#!/usr/bin/env python3
"""Discover and render explicitly nominated site documents."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from render_explore_docs import render_markdown_content, render_markdown_document


SCHEMA_PATH = Path("schemas/site-document-publication.schema.json")
LIBRARY_SOURCE_PATH = Path("docs/published-documents.md")
LIBRARY_PUBLIC_PATH = Path("learn/library/index.html")
DOCUMENT_MANIFEST_PATH = Path("learn/documentation-manifest.json")
MAX_DOCUMENT_BYTES = 1024 * 1024

CURATED_DOCUMENT_PUBLICATIONS = {
    Path("docs/start-here.md"): Path("learn/index.html"),
    Path("docs/ask-an-ai.md"): Path("learn/ask-an-ai.html"),
    Path("README.md"): Path("learn/library/repository-guide.html"),
    Path("research/overview.md"): Path("learn/library/idea-and-semantic-model.html"),
    Path("journeys/missed-rubbish-collection.md"): Path(
        "learn/library/missed-rubbish-journey.html"
    ),
    Path("journeys/learning-to-drive-speeding.md"): Path(
        "learn/library/driving-and-speeding-journey.html"
    ),
    Path("journeys/death-bereavement-estate.md"): Path(
        "learn/library/bereavement-and-estate-journey.html"
    ),
    Path("ontology/index.md"): Path("learn/library/ontology.html"),
    Path("jurisdictions/index.md"): Path("learn/library/jurisdictions.html"),
    Path("evidence/index.md"): Path("learn/library/evidence.html"),
    Path("evidence/licensing-and-attribution.md"): Path(
        "learn/library/licensing-and-attribution.html"
    ),
    Path("evaluation/README.md"): Path("learn/library/evaluation.html"),
    Path("evaluation/ai-consumer/claude-journey-walker-case-study.md"): Path(
        "learn/library/claude-journey-walker-case-study.html"
    ),
    Path("evaluation/ai-consumer/README.md"): Path(
        "learn/library/ai-consumer-evaluation.html"
    ),
    Path(
        "evaluation/publication/explore-okf-review-authorization-2026-08-13.md"
    ): Path("learn/library/public-review-authorisation.html"),
    Path("docs/authoring.md"): Path("learn/library/authoring.html"),
    Path("docs/review-and-publication-plan.md"): Path(
        "learn/library/review-and-publication-plan.html"
    ),
    LIBRARY_SOURCE_PATH: LIBRARY_PUBLIC_PATH,
    Path("publication/README.md"): Path("learn/library/pages-publication.html"),
    Path("REPOSITORY_STATUS.md"): Path("learn/library/repository-status.html"),
    Path("TRACKING.md"): Path("learn/library/delivery-tracking.html"),
    Path("CHANGELOG.md"): Path("learn/library/change-log.html"),
}


@dataclass(frozen=True)
class SiteDocumentPublication:
    source_path: Path
    public_path: Path
    title: str
    description: str
    status: str
    section: str
    order: int


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def json_text(value: object) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _read_frontmatter(path: Path) -> dict[str, Any] | None:
    if path.stat().st_size > MAX_DOCUMENT_BYTES:
        raise ValueError(f"{path.as_posix()}: document exceeds the 1 MiB publication limit")
    text = path.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    if not lines or lines[0].lstrip("\ufeff").strip() != "---":
        return None
    for index in range(1, len(lines)):
        if lines[index].strip() not in {"---", "..."}:
            continue
        value = yaml.safe_load("\n".join(lines[1:index])) or {}
        if not isinstance(value, dict):
            raise ValueError(f"{path.as_posix()}: frontmatter must be a mapping")
        return value
    raise ValueError(f"{path.as_posix()}: frontmatter is not closed")


def _contained_markdown_files(root: Path) -> list[Path]:
    documents_root = root / "docs"
    if not documents_root.is_dir() or documents_root.is_symlink():
        raise ValueError("docs must be a regular repository directory")
    paths: list[Path] = []
    for path in sorted(documents_root.rglob("*.md")):
        relative = path.relative_to(root)
        current = root
        for part in relative.parts:
            current /= part
            if current.is_symlink():
                raise ValueError(
                    f"{relative.as_posix()}: publication source must not use a symbolic link"
                )
        if path.is_file():
            paths.append(path)
    return paths


def discover_site_documents(root: Path) -> list[SiteDocumentPublication]:
    schema = json.loads((root / SCHEMA_PATH).read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    publications: list[SiteDocumentPublication] = []
    public_paths: dict[Path, Path] = {}

    for path in _contained_markdown_files(root):
        metadata = _read_frontmatter(path)
        if metadata is None or "publication" not in metadata:
            continue
        relative = path.relative_to(root)
        publication = metadata["publication"]
        errors = sorted(validator.iter_errors(publication), key=lambda error: list(error.path))
        if errors:
            detail = "; ".join(error.message for error in errors)
            raise ValueError(f"{relative.as_posix()}: invalid publication metadata: {detail}")
        for field in ("title", "description", "status"):
            if not isinstance(metadata.get(field), str) or not metadata[field].strip():
                raise ValueError(
                    f"{relative.as_posix()}: published document requires non-empty {field} frontmatter"
                )
        public_path = Path(publication["path"])
        previous = public_paths.get(public_path)
        if previous is not None:
            raise ValueError(
                f"published target {public_path.as_posix()} is declared by both "
                f"{previous.as_posix()} and {relative.as_posix()}"
            )
        public_paths[public_path] = relative
        publications.append(
            SiteDocumentPublication(
                source_path=relative,
                public_path=public_path,
                title=metadata["title"].strip(),
                description=metadata["description"].strip(),
                status=metadata["status"].strip(),
                section=publication["section"].strip(),
                order=publication["order"],
            )
        )

    return sorted(
        publications,
        key=lambda item: (
            item.section.casefold(),
            item.order,
            item.title.casefold(),
            item.source_path.as_posix(),
        ),
    )


def document_publication_mapping(
    publications: list[SiteDocumentPublication],
) -> dict[Path, Path]:
    mapping = dict(CURATED_DOCUMENT_PUBLICATIONS)
    targets = {target: source for source, target in mapping.items()}
    for item in publications:
        if item.source_path in mapping:
            raise ValueError(
                f"{item.source_path.as_posix()} is both curated and frontmatter-nominated"
            )
        previous = targets.get(item.public_path)
        if previous is not None:
            raise ValueError(
                f"published target {item.public_path.as_posix()} conflicts with "
                f"curated source {previous.as_posix()}"
            )
        mapping[item.source_path] = item.public_path
        targets[item.public_path] = item.source_path
    return mapping


def _library_markdown(
    root: Path, publications: list[SiteDocumentPublication]
) -> str:
    source = root / LIBRARY_SOURCE_PATH
    content = source.read_text(encoding="utf-8").rstrip()
    if not publications:
        return content + "\n\nNo additional documents are currently nominated.\n"
    sections: dict[str, list[SiteDocumentPublication]] = {}
    for item in publications:
        sections.setdefault(item.section, []).append(item)
    lines = [content]
    for section, items in sections.items():
        lines.extend(("", f"## {section}", ""))
        for item in items:
            relative_link = os.path.relpath(
                item.source_path.as_posix(), start=LIBRARY_SOURCE_PATH.parent.as_posix()
            )
            lines.append(
                f"- [{item.title}]({relative_link}) — {item.description} "
                f"Status: **{item.status}**."
            )
    return "\n".join(lines).rstrip() + "\n"


def build_site_document_outputs(
    root: Path,
    *,
    extra_mapping: dict[Path, Path] | None = None,
) -> tuple[
    dict[Path, str],
    dict[Path, Path],
    list[SiteDocumentPublication],
]:
    publications = discover_site_documents(root)
    mapping = document_publication_mapping(publications)
    public_mapping = dict(mapping)
    if extra_mapping:
        public_mapping.update(extra_mapping)

    outputs: dict[Path, str] = {}
    nominated_by_source = {item.source_path: item for item in publications}
    for source_path, public_path in mapping.items():
        if source_path == LIBRARY_SOURCE_PATH:
            outputs[public_path] = render_markdown_content(
                root / source_path,
                _library_markdown(root, publications),
                public_path,
                public_mapping,
            )
        else:
            publication = nominated_by_source.get(source_path)
            outputs[public_path] = render_markdown_document(
                root / source_path,
                public_path,
                public_mapping,
                document_status=publication.status if publication else None,
            )

    manifest_documents = []
    for item in publications:
        source_bytes = (root / item.source_path).read_bytes()
        output_bytes = outputs[item.public_path].encode("utf-8")
        manifest_documents.append(
            {
                "description": item.description,
                "order": item.order,
                "output": {
                    "bytes": len(output_bytes),
                    "path": item.public_path.as_posix(),
                    "sha256": sha256_bytes(output_bytes),
                },
                "section": item.section,
                "source": {
                    "bytes": len(source_bytes),
                    "path": item.source_path.as_posix(),
                    "sha256": sha256_bytes(source_bytes),
                },
                "status": item.status,
                "title": item.title,
            }
        )
    library_bytes = outputs[LIBRARY_PUBLIC_PATH].encode("utf-8")
    outputs[DOCUMENT_MANIFEST_PATH] = json_text(
        {
            "authorisation_record": (
                "evaluation/publication/"
                "documentation-overlay-authorization-2026-08-17.md"
            ),
            "deployment_automatic": False,
            "document_count": len(manifest_documents),
            "documents": manifest_documents,
            "library": {
                "bytes": len(library_bytes),
                "path": LIBRARY_PUBLIC_PATH.as_posix(),
                "sha256": sha256_bytes(library_bytes),
            },
            "publication_effect": "nomination-only-until-manual-exact-head-deployment",
            "schema": "okf-site-document-publication-manifest.v1",
        }
    )
    return outputs, mapping, publications


__all__ = [
    "CURATED_DOCUMENT_PUBLICATIONS",
    "DOCUMENT_MANIFEST_PATH",
    "LIBRARY_PUBLIC_PATH",
    "SiteDocumentPublication",
    "build_site_document_outputs",
    "discover_site_documents",
    "document_publication_mapping",
]
