#!/usr/bin/env python3
"""Create metadata-only source-link receipts without retaining response bodies."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "source" / "authority-registry.v1.yaml"


def verify(source_id: str, url: str, checked_at: str) -> dict[str, Any]:
    headers = {"Accept": "*/*", "User-Agent": "okf-uk-living-link-audit/1"}
    status: int | None = None
    final_url = url
    media_type = ""
    limitation = "Metadata-only request; no response body was retained."
    try:
        request = Request(url, method="HEAD", headers=headers)
        try:
            response = urlopen(request, timeout=30)  # noqa: S310 - reviewed HTTPS link audit
        except HTTPError as error:
            if error.code not in {403, 405, 406}:
                raise
            request = Request(url, method="GET", headers={**headers, "Range": "bytes=0-0"})
            response = urlopen(request, timeout=30)  # noqa: S310 - reviewed HTTPS link audit
            limitation = "HEAD was rejected; a ranged GET was opened without retaining its response body."
        with response:
            status = response.status
            final_url = response.geturl()
            media_type = response.headers.get_content_type()
        result = "redirected-active" if final_url != url else "active"
    except HTTPError as error:
        status = error.code
        final_url = error.geturl()
        media_type = error.headers.get_content_type() if error.headers else ""
        result = "blocked" if error.code in {401, 403, 406, 429} else "failed"
        limitation = f"HTTP metadata request failed: {error.reason}; no response body was retained."
    except (URLError, TimeoutError, OSError) as error:
        result = "failed"
        limitation = f"Metadata request failed: {error}; no response body was retained."
    return {
        "schema": "source-link-receipt.v1",
        "source_id": source_id,
        "url": url,
        "checked_at": checked_at,
        "method": "http-metadata",
        "result": result,
        "status_code": status,
        "final_url": final_url,
        "media_type": media_type or "not-exposed",
        "display_mode": "link",
        "response_body_retained": False,
        "limitation": limitation,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--checked-at", help="ISO timestamp; defaults to current UTC time")
    args = parser.parse_args()
    checked_at = args.checked_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    registry = yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))
    sources = [source for source in registry.get("sources", []) if source.get("rights_decision") != "repository:MIT"]
    args.output.mkdir(parents=True, exist_ok=True)
    failures = 0
    for source in sources:
        receipt = verify(str(source["id"]), str(source["url"]), checked_at)
        if receipt["result"] not in {"active", "redirected-active"}:
            failures += 1
        path = args.output / f"{source['id']}.json"
        path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"{source['id']}: {receipt['result']} ({receipt['status_code']})")
    print(f"wrote {len(sources)} metadata-only receipts; {failures} require browser review")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
