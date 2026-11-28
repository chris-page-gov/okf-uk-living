"""Build a separate, hash-bound Core 0.3 migration preview route."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_ROOT = Path("core-0.3-preview")
PUBLIC_BASE = "https://chris-page-gov.github.io/okf-uk-living/"
CORE_SPEC = (
    "https://github.com/open-knowledge-format/open-knowledge-format/blob/"
    "527e81aff55992be21507e97004286789126f88c/SPEC.md"
)
PROFILE_URI = "https://chris-page-gov.github.io/okf-explorer/profile/bundle-wiki/v2/"
PROFILE_SCHEMA_PATH = Path("profiles/bundle-wiki/v2/repository-contract.schema.json")
PROFILE_INDEX_PATH = Path("profiles/bundle-wiki/v2/index.md")
AUTHORIZATION_PATH = Path(
    "evaluation/publication/core-0.3-preview-authorization-2026-11-28.md"
)
PAGES_MANIFEST_PATH = Path("publication/pages-file-manifest.json")
EXPECTED_PAGES_MANIFEST_SHA256 = (
    "7ad5714e3462d0e57599f430301b34e916d607ac8afae68a34d9b8567f26832d"
)
DESCRIPTOR_SOURCE = Path("okf-explorer.json")
SEMANTIC_ROOT = Path("generated/semantic")
BROWSER_ROOT = Path("generated/browser")
SEMANTIC_FILES = (
    Path("generated/semantic/life-course-corpus.jsonld"),
    Path("generated/semantic/life-course-corpus.yamlld"),
    Path("generated/semantic/validation-report.json"),
)
OUTPUT_DESCRIPTOR = Path("okf-explorer-core-0.3.json")
OUTPUT_CLOSURE = PUBLIC_ROOT / "closure.json"
OUTPUT_INDEX = PUBLIC_ROOT / "index.html"


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes((ROOT / path).read_bytes())


def json_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def preview_source_paths() -> list[Path]:
    paths = [AUTHORIZATION_PATH, *SEMANTIC_FILES]
    for root in (SEMANTIC_ROOT, BROWSER_ROOT):
        for path in sorted((ROOT / root).rglob("*")):
            if path.is_symlink():
                raise ValueError(f"Core 0.3 preview source must not be a symlink: {path}")
            if path.is_file():
                relative = path.relative_to(ROOT)
                if relative not in paths:
                    paths.append(relative)
    return sorted(set(paths))


def preview_target(source: Path) -> Path:
    if source.parts[0] == "generated":
        return PUBLIC_ROOT / source
    if source == AUTHORIZATION_PATH:
        return PUBLIC_ROOT / "authorization.md"
    raise ValueError(f"unexpected Core 0.3 preview asset: {source}")


def candidate_descriptor_bytes() -> bytes:
    descriptor = json.loads((ROOT / DESCRIPTOR_SOURCE).read_text(encoding="utf-8"))
    if descriptor.get("okf_version") != "0.3":
        raise ValueError("Core 0.3 preview descriptor must declare okf_version 0.3")
    if not isinstance(descriptor.get("entrypoints"), dict):
        raise ValueError("Core 0.3 preview descriptor has no entrypoints mapping")

    def preview_path(value: Any) -> Any:
        if isinstance(value, str) and value.startswith(
            ("generated/semantic/", "generated/browser/")
        ):
            return (PUBLIC_ROOT / value).as_posix()
        if isinstance(value, list):
            return [preview_path(item) for item in value]
        if isinstance(value, dict):
            return {key: preview_path(item) for key, item in value.items()}
        return value

    descriptor = preview_path(descriptor)
    descriptor["status"] = "owner-authorised-public-review-preview"
    source_metadata = descriptor.get("source")
    if isinstance(source_metadata, dict):
        source_metadata["publication_authorized"] = True
    return json_bytes(descriptor)


def _html(closure_sha256: str, descriptor_sha256: str) -> bytes:
    closure_url = "closure.json"
    reader_url = (
        "https://chris-page-gov.github.io/okf-explorer/?bundle="
        "https%3A%2F%2Fchris-page-gov.github.io%2Fokf-uk-living%2F"
        "okf-explorer-core-0.3.json#overview"
    )
    return f'''<!doctype html>
<html lang="en-GB">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex,nofollow,noarchive">
  <meta name="referrer" content="no-referrer">
  <title>OKF Core 0.3 migration preview — A Life in the UK</title>
  <style>
    :root {{ color-scheme: light; font: 1rem/1.55 system-ui, sans-serif; color: #17212b; background: #f4f7f5; }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; }}
    main {{ width: min(100% - 2rem, 54rem); margin: clamp(1rem, 5vw, 3rem) auto; }}
    header, section {{ padding: clamp(1rem, 4vw, 2rem); margin-block: 1rem; border: 1px solid #c8d5d0; border-radius: .75rem; background: #fff; }}
    h1 {{ margin-top: 0; font-size: clamp(1.8rem, 5vw, 2.6rem); line-height: 1.15; }}
    h2 {{ font-size: 1.25rem; }}
    a {{ color: #004e48; text-underline-offset: .18em; }}
    .notice {{ border-left: .3rem solid #a95500; background: #fff1d8; }}
    .links {{ display: flex; flex-wrap: wrap; gap: .8rem; }}
    .button {{ display: inline-block; padding: .65rem .9rem; border: 2px solid #006b62; border-radius: .45rem; font-weight: 650; }}
    code {{ overflow-wrap: anywhere; }}
    :focus-visible {{ outline: 3px solid #ffbf47; outline-offset: 3px; }}
  </style>
</head>
<body><main>
  <header>
    <p>Owner-authorised public review preview · OKF Core 0.3 · release grade: no</p>
    <h1>A Life in the UK — Core 0.3 migration preview</h1>
    <p>This separate route serves the candidate Core 0.3 large-corpus descriptor and its generated semantic documents. The existing Core 0.2 Pages publication and all of its original routes remain pinned and unchanged.</p>
    <p class="notice"><strong>Review boundary:</strong> the producer contract remains at <code>migration</code>. The centrally published Bundle Wiki v2 implementation profile is marked experimental. This preview does not claim full profile acceptance, specialist review, current source observation, formal release, or official service guidance.</p>
    <div class="links"><a class="button" href="{reader_url}">Open the Core 0.3 candidate in OKF Explorer</a><a class="button" href="../okf-explorer-core-0.3.json">Candidate Reader descriptor</a></div>
  </header>
  <section>
    <h2>Source and profile</h2>
    <ul>
      <li><a href="authorization.md">Owner publication authorisation and boundaries</a>.</li>
      <li><a href="{html.escape(CORE_SPEC)}">Pinned OKF Core 0.3 specification</a>.</li>
      <li><a href="https://github.com/chris-page-gov/okf-uk-living/tree/main">Authored Markdown and repository evidence</a> remain the source of truth.</li>
      <li><a href="{html.escape(PROFILE_URI)}">Bundle Wiki v2 profile</a> is a separate experimental implementation profile, not part of OKF Core.</li>
      <li>The independent Core 0.2 compatibility baseline and original public Explorer publication remain available through the repository and <a href="../">existing review site</a>.</li>
    </ul>
  </section>
  <section>
    <h2>Candidate identity</h2>
    <p>Closure manifest SHA-256: <code>{closure_sha256}</code> (<a href="{closure_url}">view closure manifest</a>).</p>
    <p>Core 0.3 Reader descriptor SHA-256: <code>{descriptor_sha256}</code>.</p>
    <p>The closure manifest lists exact candidate assets and binds the shared data assets to the original frozen Pages manifest.</p>
  </section>
</main></body></html>
'''.encode("utf-8")


def build_core03_preview_outputs() -> tuple[dict[Path, bytes], list[tuple[Path, Path]]]:
    sources = preview_source_paths()
    outputs: dict[Path, bytes] = {source: (ROOT / source).read_bytes() for source in sources}
    descriptor = candidate_descriptor_bytes()
    outputs[OUTPUT_DESCRIPTOR] = descriptor
    base_path = ROOT / PAGES_MANIFEST_PATH
    base_bytes = base_path.read_bytes()
    if sha256_bytes(base_bytes) != EXPECTED_PAGES_MANIFEST_SHA256:
        raise ValueError("Core 0.3 preview does not bind the reviewed frozen Pages manifest")
    base = json.loads(base_bytes)
    base_by_target = {
        item["target"]: {"bytes": item["bytes"], "sha256": item["sha256"]}
        for item in base.get("files", [])
        if isinstance(item, dict) and isinstance(item.get("target"), str)
    }
    shared_large_data = [
        {"path": path, **identity}
        for path, identity in sorted(base_by_target.items())
        if path.startswith("large/data/")
    ]
    if not shared_large_data:
        raise ValueError("frozen Pages manifest contains no shared large-data assets")

    candidate_assets = []
    for source in sources:
        target = preview_target(source)
        data = outputs[source]
        candidate_assets.append(
            {"source": source.as_posix(), "path": target.as_posix(), "bytes": len(data), "sha256": sha256_bytes(data)}
        )
    descriptor_item = {
        "source": OUTPUT_DESCRIPTOR.as_posix(),
        "path": OUTPUT_DESCRIPTOR.as_posix(),
        "bytes": len(descriptor),
        "sha256": sha256_bytes(descriptor),
    }
    profile_hashes = {
        path.as_posix(): sha256_file(path)
        for path in (PROFILE_INDEX_PATH, PROFILE_SCHEMA_PATH)
    }
    closure = {
        "schema": "okf-uk-living-core-0.3-preview-closure.v1",
        "status": "owner-authorised-public-review-preview",
        "release_grade": False,
        "okf_core": {"version": "0.3", "status": "migration", "specification": CORE_SPEC},
        "profile": {
            "uri": PROFILE_URI,
            "status": "experimental implementation profile",
            "source_repository": "https://github.com/chris-page-gov/okf-explorer",
            "source_commit": "171efeeb8525691ab6d89f4ddfac2146374e862c",
            "files": profile_hashes,
            "conformance_claim": False,
        },
        "authorisation": {
            "path": (PUBLIC_ROOT / "authorization.md").as_posix(),
            "sha256": sha256_file(AUTHORIZATION_PATH),
        },
        "candidate": {
            "repository": "https://github.com/chris-page-gov/okf-uk-living",
            "core_descriptor": descriptor_item,
            "assets": candidate_assets,
        },
        "shared_frozen_base": {
            "path": "/publication-manifest.json",
            "sha256": EXPECTED_PAGES_MANIFEST_SHA256,
            "file_count": base.get("file_count"),
            "bytes": base.get("total_bytes"),
            "large_data_assets": shared_large_data,
        },
        "limitations": [
            "The base Core 0.2 publication remains independently pinned and unchanged.",
            "The Core 0.3 migration and experimental Bundle Wiki v2 profile do not establish specialist acceptance, current source accuracy, full profile acceptance or formal release.",
            "The Reader journey was verified locally against the exact candidate route; public URLs require the separate post-deployment identity and browser gate.",
        ],
    }
    closure_bytes = json_bytes(closure)
    outputs[OUTPUT_CLOSURE] = closure_bytes
    closure_sha = sha256_bytes(closure_bytes)
    outputs[OUTPUT_INDEX] = _html(closure_sha, sha256_bytes(descriptor))

    public_paths = [(OUTPUT_DESCRIPTOR, OUTPUT_DESCRIPTOR)]
    public_paths.extend((source, preview_target(source)) for source in sources)
    public_paths.extend(((OUTPUT_CLOSURE, OUTPUT_CLOSURE), (OUTPUT_INDEX, OUTPUT_INDEX)))
    return outputs, public_paths
