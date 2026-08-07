#!/usr/bin/env python3
"""Serve the local Explorer UI with this repository's generated OKF outputs."""

from __future__ import annotations

import argparse
import posixpath
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROUTES = (
    "/okf-bundle.json",
    "/okf-explorer.json",
    "/generated/",
    "/large/",
)


class ExplorerOverlayHandler(SimpleHTTPRequestHandler):
    explorer_root: Path

    def project_route(self, path: str) -> bool:
        return any(path == prefix or path.startswith(prefix) for prefix in PROJECT_ROUTES)

    def translate_path(self, path: str) -> str:
        request_path = unquote(urlsplit(path).path)
        root = ROOT if self.project_route(request_path) else self.explorer_root
        parts = [part for part in posixpath.normpath(request_path).split("/") if part not in {"", ".", ".."}]
        target = root.joinpath(*parts)
        return str(target)

    def end_headers(self) -> None:
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8003)
    parser.add_argument(
        "--explorer-root",
        type=Path,
        default=ROOT.parent / "okf-explorer" / "_site",
        help="path to the built OKF Explorer static site",
    )
    args = parser.parse_args()
    explorer_root = args.explorer_root.resolve()
    if not (explorer_root / "index.html").is_file():
        parser.error(f"Explorer build is absent: {explorer_root / 'index.html'}")
    ExplorerOverlayHandler.explorer_root = explorer_root
    server = ThreadingHTTPServer((args.host, args.port), ExplorerOverlayHandler)
    print(f"Serving Explorer overlay at http://{args.host}:{args.port}/", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
