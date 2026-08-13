#!/usr/bin/env python3
"""Build the additive Explore OKF journey sidecar without changing the base bundle."""

from __future__ import annotations

import argparse
import base64
import difflib
import hashlib
import html
import json
import re
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from build_large_corpus import GENERATED_AT, SNAPSHOT
from build_okf_bundle import ROOT
from explore_okf_projection import (
    JOURNEY_PROJECTION_SCHEMA_PATH,
    JOURNEY_PROJECTION_SCHEMA_PUBLIC_PATH,
    build_endpoint_label_index,
    build_journey_projection,
    canonical_json_bytes,
    json_text,
    validate_endpoint_label_index,
    validate_journey_projection,
)
from render_explore_docs import render_markdown_document


PUBLIC_BASE = "https://chris-page-gov.github.io/okf-uk-living/"
BASE_DESCRIPTOR_PATH = ROOT / "publication" / "okf-explorer.json"
BASE_MANIFEST_PATH = ROOT / "large" / "data" / "manifest.json"
BASE_PUBLICATION_MANIFEST_PATH = ROOT / "publication" / "pages-file-manifest.json"
TEMPLATE_ROOT = ROOT / "source" / "explore-okf"
PROJECTION_PATH = Path("explore/journey-projection.json")
PROJECTION_SCHEMA_PATH = JOURNEY_PROJECTION_SCHEMA_PUBLIC_PATH
LABELS_PATH = Path("explore/endpoint-labels.json")
MANIFEST_PATH = Path("explore/data-manifest.json")
HTML_PATH = Path("explore/index.html")
HOME_SOURCE_PATH = Path("publication/explore-okf-index.html")
HOME_PUBLIC_PATH = Path("index.html")
DESCRIPTOR_PATH = Path("explore-okf.json")
OVERLAY_MANIFEST_PATH = Path("publication/explore-okf-file-manifest.json")
BASE_HOME_SHA256 = "584ded105f3eeded3b12410289ab3596b5dbf28e2ad610617f12480717ef1be6"
DOCUMENT_PUBLICATIONS = {
    Path("docs/start-here.md"): Path("learn/index.html"),
    Path("docs/ask-an-ai.md"): Path("learn/ask-an-ai.html"),
    Path("README.md"): Path("learn/library/repository-guide.html"),
    Path("research/overview.md"): Path("learn/library/idea-and-semantic-model.html"),
    Path("journeys/missed-rubbish-collection.md"): Path("learn/library/missed-rubbish-journey.html"),
    Path("journeys/learning-to-drive-speeding.md"): Path("learn/library/driving-and-speeding-journey.html"),
    Path("journeys/death-bereavement-estate.md"): Path("learn/library/bereavement-and-estate-journey.html"),
    Path("ontology/index.md"): Path("learn/library/ontology.html"),
    Path("jurisdictions/index.md"): Path("learn/library/jurisdictions.html"),
    Path("evidence/index.md"): Path("learn/library/evidence.html"),
    Path("evidence/licensing-and-attribution.md"): Path("learn/library/licensing-and-attribution.html"),
    Path("evaluation/README.md"): Path("learn/library/evaluation.html"),
    Path("evaluation/ai-consumer/claude-journey-walker-case-study.md"): Path("learn/library/claude-journey-walker-case-study.html"),
    Path("evaluation/ai-consumer/README.md"): Path("learn/library/ai-consumer-evaluation.html"),
    Path("evaluation/publication/explore-okf-review-authorization-2026-08-13.md"): Path("learn/library/public-review-authorisation.html"),
    Path("docs/authoring.md"): Path("learn/library/authoring.html"),
    Path("docs/review-and-publication-plan.md"): Path("learn/library/review-and-publication-plan.html"),
    Path("publication/README.md"): Path("learn/library/pages-publication.html"),
    Path("REPOSITORY_STATUS.md"): Path("learn/library/repository-status.html"),
    Path("TRACKING.md"): Path("learn/library/delivery-tracking.html"),
    Path("CHANGELOG.md"): Path("learn/library/change-log.html"),
}
EXPECTED_BASE_DESCRIPTOR_SHA256 = "ff69f0162a4ba93156b150ae4eea0070c8c8a81187ed5cc7d2425f37b8db34dc"
EXPECTED_BASE_MANIFEST_SHA256 = "fe0e11219ceec88702ca8a5d536d6d0ac0425f3bb29c7586884cfb0e56c957b4"
EXPECTED_BASE_PUBLICATION_MANIFEST_SHA256 = "1a43f5fa0b8a4c4d3489891dce27f711d3f370f3dcca7ae7b6d4f5ec22249ee7"
EXPLORATORY_BANNER_MESSAGE = (
    "This is an incomplete research view, not an authoritative service or "
    "released data product. Content and links may change. Check the cited "
    "official source before making a decision."
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def resource_reference(path: Path, content: str | bytes) -> dict[str, Any]:
    data = content if isinstance(content, bytes) else content.encode("utf-8")
    return {
        "path": path.as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
    }


def require_frozen_base() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    expected = (
        (BASE_DESCRIPTOR_PATH, EXPECTED_BASE_DESCRIPTOR_SHA256, "published base descriptor"),
        (BASE_MANIFEST_PATH, EXPECTED_BASE_MANIFEST_SHA256, "published base data manifest"),
        (
            BASE_PUBLICATION_MANIFEST_PATH,
            EXPECTED_BASE_PUBLICATION_MANIFEST_SHA256,
            "published base file manifest",
        ),
    )
    for path, digest, label in expected:
        if not path.is_file() or sha256_path(path) != digest:
            raise ValueError(f"{label} differs from the frozen Claude-tested publication")
    descriptor = json.loads(BASE_DESCRIPTOR_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(BASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    publication_manifest = json.loads(
        BASE_PUBLICATION_MANIFEST_PATH.read_text(encoding="utf-8")
    )
    return descriptor, manifest, publication_manifest


def frozen_publication_json(
    target_value: object, publication_manifest: dict[str, Any]
) -> Any:
    """Load one exact JSON target from the hash-pinned frozen publication."""
    if not isinstance(target_value, str) or not target_value:
        raise ValueError("frozen publication target is missing")
    target = Path(target_value)
    if target.is_absolute() or ".." in target.parts or any(
        part in {"", "."} for part in target.parts
    ):
        raise ValueError(f"frozen publication target is unsafe: {target_value!r}")
    matches = [
        item
        for item in publication_manifest.get("files", [])
        if isinstance(item, dict) and item.get("target") == target.as_posix()
    ]
    if len(matches) != 1:
        raise ValueError(
            f"frozen publication target must have one manifest entry: {target.as_posix()}"
        )
    entry = matches[0]
    source_value = entry.get("source")
    if not isinstance(source_value, str) or not source_value:
        raise ValueError(f"frozen publication source is missing: {target.as_posix()}")
    source = Path(source_value)
    if source.is_absolute() or ".." in source.parts or any(
        part in {"", "."} for part in source.parts
    ):
        raise ValueError(f"frozen publication source is unsafe: {source_value!r}")
    source_path = ROOT / source
    expected_bytes = entry.get("bytes")
    expected_sha256 = entry.get("sha256")
    if (
        source_path.is_symlink()
        or not source_path.is_file()
        or not isinstance(expected_bytes, int)
        or source_path.stat().st_size != expected_bytes
        or not isinstance(expected_sha256, str)
        or not SHA256.fullmatch(expected_sha256)
        or sha256_path(source_path) != expected_sha256
    ):
        raise ValueError(
            f"frozen publication source differs from its manifest: {source.as_posix()}"
        )
    try:
        return json.loads(source_path.read_bytes())
    except json.JSONDecodeError as error:
        raise ValueError(
            f"frozen publication source is not valid JSON: {source.as_posix()}"
        ) from error


def frozen_publication_rows(
    targets: object, label: str, publication_manifest: dict[str, Any]
) -> list[dict[str, Any]]:
    if not isinstance(targets, list) or not targets:
        raise ValueError(f"frozen data manifest has no {label} chunks")
    rows: list[dict[str, Any]] = []
    for target in targets:
        value = frozen_publication_json(target, publication_manifest)
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise ValueError(f"frozen {label} chunk is not an array of objects: {target}")
        rows.extend(value)
    return rows


def public_source_identity(
    descriptor: dict[str, Any], publication_manifest: dict[str, Any]
) -> dict[str, Any]:
    runtime = descriptor.get("entrypoints", {}).get("relationship_runtime", {})
    candidate_path = ROOT / "generated" / "assurance" / "candidate-manifest.json"
    review_path = ROOT / "generated" / "assurance" / "review-status-report.json"
    candidate_id = str(publication_manifest.get("candidate_id") or "")
    return {
        "bundle_url": PUBLIC_BASE + "okf-explorer.json",
        "candidate_id": candidate_id,
        "bundle_descriptor": {
            "path": "publication/okf-explorer.json",
            "bytes": BASE_DESCRIPTOR_PATH.stat().st_size,
            "sha256": EXPECTED_BASE_DESCRIPTOR_SHA256,
        },
        "data_manifest": {
            "path": "large/data/manifest.json",
            "bytes": BASE_MANIFEST_PATH.stat().st_size,
            "sha256": EXPECTED_BASE_MANIFEST_SHA256,
        },
        "relationship_runtime": {
            "path": str(runtime.get("path") or ""),
            "bytes": int(runtime.get("bytes") or 0),
            "sha256": str(runtime.get("sha256") or ""),
        },
        "candidate_manifest": {
            "path": "generated/assurance/candidate-manifest.json",
            "bytes": candidate_path.stat().st_size,
            "sha256": sha256_path(candidate_path),
        },
        "review_status": {
            "path": "generated/assurance/review-status-report.json",
            "bytes": review_path.stat().st_size,
            "sha256": sha256_path(review_path),
        },
    }


def escape_template_json(value: dict[str, Any]) -> str:
    escaped = html.escape(
        canonical_json_bytes(value).decode("utf-8").rstrip("\n"), quote=False
    )
    return escaped.replace("\u2028", "&#8232;").replace("\u2029", "&#8233;")


def csp_hash(value: str) -> str:
    digest = hashlib.sha256(value.encode("utf-8")).digest()
    return base64.b64encode(digest).decode("ascii")


def build_html(projection: dict[str, Any], projection_sha256: str) -> str:
    template = (TEMPLATE_ROOT / "index.template.html").read_text(encoding="utf-8")
    style = (TEMPLATE_ROOT / "standalone.css").read_text(encoding="utf-8").strip()
    script = (
        (TEMPLATE_ROOT / "standalone.js")
        .read_text(encoding="utf-8")
        .strip()
        .replace("@@PROJECTION_SHA256@@", projection_sha256)
    )
    csp = "; ".join(
        (
            "default-src 'none'",
            f"script-src 'sha256-{csp_hash(script)}'",
            "script-src-attr 'none'",
            f"style-src 'sha256-{csp_hash(style)}'",
            "style-src-attr 'none'",
            "img-src 'none'",
            "font-src 'none'",
            "connect-src 'none'",
            "media-src 'none'",
            "object-src 'none'",
            "frame-src 'none'",
            "worker-src 'none'",
            "manifest-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        )
    )
    replacements = {
        "@@CSP@@": csp,
        "@@STYLE@@": style,
        "@@PROJECTION@@": escape_template_json(projection),
        "@@SCRIPT@@": script,
    }
    rendered = template
    for marker, value in replacements.items():
        if rendered.count(marker) != 1:
            raise ValueError(f"standalone template must contain one {marker} marker")
        rendered = rendered.replace(marker, value)
    if "@@" in rendered:
        raise ValueError("standalone template contains an unresolved marker")
    return rendered.rstrip() + "\n"


def build_home(projection_sha256: str) -> str:
    template = (TEMPLATE_ROOT / "home.template.html").read_text(encoding="utf-8")
    style = (TEMPLATE_ROOT / "home.css").read_text(encoding="utf-8").strip()
    csp = "; ".join(
        (
            "default-src 'none'",
            f"style-src 'sha256-{csp_hash(style)}'",
            "style-src-attr 'none'",
            "script-src 'none'",
            "script-src-attr 'none'",
            "img-src 'none'",
            "font-src 'none'",
            "connect-src 'none'",
            "media-src 'none'",
            "object-src 'none'",
            "frame-src 'none'",
            "worker-src 'none'",
            "manifest-src 'none'",
            "base-uri 'none'",
            "form-action 'none'",
        )
    )
    rendered = template
    replacements = {
        "@@CSP@@": csp,
        "@@STYLE@@": style,
        "@@PROJECTION_SHA256@@": projection_sha256,
    }
    for marker, value in replacements.items():
        if rendered.count(marker) != 1:
            raise ValueError(f"home template must contain one {marker} marker")
        rendered = rendered.replace(marker, value)
    if "@@" in rendered:
        raise ValueError("home template contains an unresolved marker")
    return rendered.rstrip() + "\n"


def build_learning_documents() -> dict[Path, str]:
    public_mapping = dict(DOCUMENT_PUBLICATIONS)
    public_mapping.update(
        {
            Path("explore/index.html"): HTML_PATH,
            Path("explore-okf.json"): DESCRIPTOR_PATH,
            Path("generated/browser/README.html"): Path("generated/browser/README.html"),
            Path("generated/assurance/population-complete-report.json"): Path(
                "generated/assurance/population-complete-report.json"
            ),
        }
    )
    return {
        public_path: render_markdown_document(
            ROOT / source_path,
            public_path,
            public_mapping,
        )
        for source_path, public_path in DOCUMENT_PUBLICATIONS.items()
    }


def build_exploratory_publication(plane_roots: dict[str, str]) -> dict[str, Any]:
    return {
        "schema": "okf-exploratory-publication.v1",
        "publication_state": "exploratory",
        "snapshot_id": SNAPSHOT,
        "generated_at": GENERATED_AT,
        "applicable_plane_roots": dict(sorted(plane_roots.items())),
        "publisher": {
            "name": "A Life in the UK",
            "url": PUBLIC_BASE,
            "authority_status": "independent-research",
        },
        "banner": {
            "label": "Exploratory",
            "message": EXPLORATORY_BANNER_MESSAGE,
            "feedback_url": "https://github.com/chris-page-gov/okf-uk-living/issues/new",
            "preserve_route": True,
        },
        "indexing_policy": "noindex",
        "limitations": [
            "Specialist review remains required for 291 of 293 service families.",
            "Official sources are links observed at the corpus date; no source response bodies are retained.",
            "The journey projection supports discovery and evaluation, not eligibility, legal, clinical or operational decisions.",
        ],
        "permitted_claims": [
            "The view exposes authored service-family journeys, governed relationships and linked official sources.",
            "The standalone view is a deterministic presentation projection of the frozen corpus identity.",
        ],
        "prohibited_claims": [
            "The view is an authoritative service, released data product or source of personal decisions.",
            "Families grouped in one enclosing process form a cross-family sequence.",
            "A confidence or normalisation label upgrades source authority or specialist review.",
        ],
        "promotion_rule": (
            "Promotion requires specialist and accessibility review, passing the AI-consumer "
            "hard gates, owner approval and exact deployed-URL verification."
        ),
    }


def build_descriptor_and_manifest(
    base_descriptor: dict[str, Any],
    base_manifest: dict[str, Any],
    projection_reference: dict[str, Any],
    projection_schema_reference: dict[str, Any],
    labels_reference: dict[str, Any],
    html_reference: dict[str, Any],
    home_reference: dict[str, Any],
    learn_reference: dict[str, Any],
    ai_prompts_reference: dict[str, Any],
) -> tuple[str, str]:
    manifest = deepcopy(base_manifest)
    manifest["title"] = "A Life in the UK Explore OKF data manifest"
    manifest["indexes"] = deepcopy(manifest.get("indexes", {}))
    manifest["indexes"]["endpoint_labels"] = labels_reference
    manifest["indexes"]["journey_projection"] = projection_reference
    manifest["indexes"]["journey_projection_schema"] = projection_schema_reference
    manifest_text = json_text(manifest)
    manifest_reference = resource_reference(MANIFEST_PATH, manifest_text)

    plane_roots = {
        "base_data_manifest": EXPECTED_BASE_MANIFEST_SHA256,
        "endpoint_labels": labels_reference["sha256"],
        "journey_projection": projection_reference["sha256"],
        "journey_projection_schema": projection_schema_reference["sha256"],
    }
    descriptor = deepcopy(base_descriptor)
    descriptor["id"] = PUBLIC_BASE + "explore-okf.json"
    descriptor["title"] = "A Life in the UK — Explore OKF journeys"
    descriptor["description"] = (
        "Additive exploratory journey view over the unchanged population-complete "
        "corpus, with explicit ordering, jurisdiction routing, labels and provenance."
    )
    descriptor["version"] = "explore-okf-journeys.v1"
    descriptor["status"] = "exploratory"
    descriptor["publication_state"] = "exploratory"
    descriptor["plane_roots"] = plane_roots
    descriptor["exploratory_publication"] = build_exploratory_publication(plane_roots)
    descriptor["entrypoints"] = deepcopy(descriptor.get("entrypoints", {}))
    descriptor["entrypoint_integrity"] = deepcopy(
        descriptor.get("entrypoint_integrity", {})
    )
    descriptor["entrypoints"]["data_manifest"] = manifest_reference
    descriptor["entrypoints"]["endpoint_labels"] = labels_reference
    descriptor["entrypoints"]["journey_projection"] = projection_reference
    descriptor["entrypoints"]["journey_projection_schema"] = projection_schema_reference
    descriptor["entrypoints"]["explore"] = html_reference
    descriptor["entrypoints"]["home"] = home_reference
    descriptor["entrypoints"]["learn"] = learn_reference
    descriptor["entrypoints"]["ai_prompts"] = ai_prompts_reference
    descriptor["entrypoint_integrity"]["data_manifest"] = manifest_reference
    descriptor["entrypoint_integrity"]["endpoint_labels"] = labels_reference
    descriptor["entrypoint_integrity"]["journey_projection"] = projection_reference
    descriptor["entrypoint_integrity"]["journey_projection_schema"] = projection_schema_reference
    descriptor["entrypoint_integrity"]["explore"] = html_reference
    descriptor["entrypoint_integrity"]["home"] = home_reference
    descriptor["entrypoint_integrity"]["learn"] = learn_reference
    descriptor["entrypoint_integrity"]["ai_prompts"] = ai_prompts_reference
    descriptor["source"] = deepcopy(descriptor.get("source", {}))
    descriptor["source"]["base_descriptor"] = {
        "path": "okf-explorer.json",
        "sha256": EXPECTED_BASE_DESCRIPTOR_SHA256,
        "preserved": True,
    }
    descriptor["source"]["publication_authorized"] = True
    descriptor["publication"] = {
        "kind": "explore-okf-public-review",
        "release_grade": False,
        "publication_authorized": True,
        "publication_authorized_at": "2026-08-13T00:00:00+01:00",
        "authorisation_record": (
            "evaluation/publication/"
            "explore-okf-review-authorization-2026-08-13.md"
        ),
        "existing_publication_preserved": True,
        "base_targets_replaced": [HOME_PUBLIC_PATH.as_posix()],
        "standalone_path": HTML_PATH.as_posix(),
        "learning_path": learn_reference["path"],
    }
    return json_text(descriptor), manifest_text


def overlay_manifest(outputs: dict[Path, str | bytes]) -> str:
    public_paths = [
        (DESCRIPTOR_PATH, DESCRIPTOR_PATH, None),
        (HOME_SOURCE_PATH, HOME_PUBLIC_PATH, BASE_HOME_SHA256),
        (HTML_PATH, HTML_PATH, None),
        (PROJECTION_PATH, PROJECTION_PATH, None),
        (PROJECTION_SCHEMA_PATH, PROJECTION_SCHEMA_PATH, None),
        (LABELS_PATH, LABELS_PATH, None),
        (MANIFEST_PATH, MANIFEST_PATH, None),
        *(
            (public_path, public_path, None)
            for public_path in DOCUMENT_PUBLICATIONS.values()
        ),
    ]
    files = []
    for source, target, replaces_sha256 in public_paths:
        content = outputs[source]
        data = content if isinstance(content, bytes) else content.encode("utf-8")
        item = {
            "source": source.as_posix(),
            "target": target.as_posix(),
            "bytes": len(data),
            "sha256": sha256_bytes(data),
        }
        if replaces_sha256 is not None:
            item["replaces_sha256"] = replaces_sha256
        files.append(item)
    value = {
        "schema": "life-course-pages-additive-publication-manifest.v2",
        "publication_state": "owner-authorised",
        "public_base_url": PUBLIC_BASE,
        "base_manifest": {
            "path": "publication/pages-file-manifest.json",
            "sha256": EXPECTED_BASE_PUBLICATION_MANIFEST_SHA256,
            "file_count": 1814,
            "preserve_all_except": [HOME_PUBLIC_PATH.as_posix()],
            "preserved_target_count": 1813,
        },
        "existing_descriptor": {
            "path": "publication/okf-explorer.json",
            "target": "okf-explorer.json",
            "sha256": EXPECTED_BASE_DESCRIPTOR_SHA256,
            "preserved": True,
        },
        "release_grade": False,
        "authorised_for_public_review": True,
        "authorisation_record": (
            "evaluation/publication/"
            "explore-okf-review-authorization-2026-08-13.md"
        ),
        "deployment_automatic": False,
        "file_count": len(files),
        "total_bytes": sum(item["bytes"] for item in files),
        "files": files,
    }
    return json_text(value)


def build_outputs() -> dict[Path, str | bytes]:
    base_descriptor, base_manifest, publication_manifest = require_frozen_base()
    chunks = base_manifest.get("chunks")
    if not isinstance(chunks, dict):
        raise ValueError("frozen data manifest has no chunks mapping")
    rows = frozen_publication_rows(
        chunks.get("datasets"), "dataset", publication_manifest
    )
    resources = frozen_publication_rows(
        chunks.get("resources"), "resource", publication_manifest
    )
    relationships = frozen_publication_rows(
        chunks.get("relationships"), "relationship", publication_manifest
    )
    source_identity = public_source_identity(base_descriptor, publication_manifest)
    projection = build_journey_projection(
        rows,
        resources,
        relationships,
        source_identity=source_identity,
        snapshot=SNAPSHOT,
        generated_at_value=GENERATED_AT,
    )
    projection_errors = validate_journey_projection(
        projection, relationships=relationships
    )
    if projection_errors:
        raise ValueError("invalid journey projection: " + "; ".join(projection_errors))
    labels = build_endpoint_label_index(
        rows,
        resources,
        relationships,
        snapshot=SNAPSHOT,
        generated_at_value=GENERATED_AT,
    )
    graph_routes = {str(entry["route"]) for entry in labels["entries"]}
    label_errors = validate_endpoint_label_index(
        labels, graph_reachable_routes=graph_routes
    )
    if label_errors:
        raise ValueError("invalid endpoint label index: " + "; ".join(label_errors))

    projection_text = json_text(projection)
    projection_schema_text = JOURNEY_PROJECTION_SCHEMA_PATH.read_text(encoding="utf-8")
    labels_text = json_text(labels)
    projection_reference = resource_reference(PROJECTION_PATH, projection_text)
    projection_schema_reference = resource_reference(
        PROJECTION_SCHEMA_PATH, projection_schema_text
    )
    labels_reference = resource_reference(LABELS_PATH, labels_text)
    html_text = build_html(projection, projection_reference["sha256"])
    html_reference = resource_reference(HTML_PATH, html_text)
    home_text = build_home(projection_reference["sha256"])
    home_reference = resource_reference(HOME_PUBLIC_PATH, home_text)
    learning_documents = build_learning_documents()
    learn_text = learning_documents[Path("learn/index.html")]
    learn_reference = resource_reference(Path("learn/index.html"), learn_text)
    ai_prompts_text = learning_documents[Path("learn/ask-an-ai.html")]
    ai_prompts_reference = resource_reference(
        Path("learn/ask-an-ai.html"), ai_prompts_text
    )
    descriptor_text, manifest_text = build_descriptor_and_manifest(
        base_descriptor,
        base_manifest,
        projection_reference,
        projection_schema_reference,
        labels_reference,
        html_reference,
        home_reference,
        learn_reference,
        ai_prompts_reference,
    )
    outputs: dict[Path, str | bytes] = {
        PROJECTION_PATH: projection_text,
        PROJECTION_SCHEMA_PATH: projection_schema_text,
        LABELS_PATH: labels_text,
        MANIFEST_PATH: manifest_text,
        HTML_PATH: html_text,
        HOME_SOURCE_PATH: home_text,
        DESCRIPTOR_PATH: descriptor_text,
        **learning_documents,
    }
    outputs[OVERLAY_MANIFEST_PATH] = overlay_manifest(outputs)
    return outputs


def check_outputs(outputs: dict[Path, str | bytes]) -> list[str]:
    errors: list[str] = []
    for path, expected in outputs.items():
        target = ROOT / path
        if not target.is_file():
            errors.append(f"{path.as_posix()} is missing")
            continue
        expected_bytes = expected if isinstance(expected, bytes) else expected.encode("utf-8")
        actual_bytes = target.read_bytes()
        if actual_bytes == expected_bytes:
            continue
        if isinstance(expected, str):
            diff = difflib.unified_diff(
                actual_bytes.decode("utf-8", errors="replace").splitlines(),
                expected.splitlines(),
                fromfile=f"current/{path.as_posix()}",
                tofile=f"generated/{path.as_posix()}",
                lineterm="",
            )
            errors.append("\n".join(diff))
        else:
            errors.append(f"{path.as_posix()} has stale binary content")
    return errors


def write_outputs(outputs: dict[Path, str | bytes]) -> None:
    for path, content in outputs.items():
        target = ROOT / path
        target.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            target.write_bytes(content)
        else:
            target.write_text(content, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when output is missing or stale")
    args = parser.parse_args(argv)
    try:
        outputs = build_outputs()
        if args.check:
            errors = check_outputs(outputs)
            if errors:
                print("Explore OKF sidecar check failed:", file=sys.stderr)
                for error in errors:
                    print(f"- {error}", file=sys.stderr)
                return 1
            projection = json.loads(str(outputs[PROJECTION_PATH]))
            print(
                "Explore OKF sidecar is synchronised: "
                f"{projection['counts']['families']} families, network-free standalone, "
                "base descriptor and corpus identity preserved"
            )
            return 0
        write_outputs(outputs)
        print("wrote additive Explore OKF journey sidecar; no base bundle files changed")
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        print(f"Explore OKF build failed: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
