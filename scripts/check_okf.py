#!/usr/bin/env python3
"""Run repository-specific semantic checks over the authored OKF corpus."""

from __future__ import annotations

from collections import Counter

from build_okf_bundle import build_bundle


def main() -> int:
    bundle, errors = build_bundle()
    if errors:
        for error in errors:
            print(error)
        return 1
    corpus = next(iter(bundle["corpora"].values()))
    nodes = corpus["nodes"]
    if corpus["root"] not in nodes:
        errors.append("configured root is absent from nodes")
    if "research/overview.md" not in nodes:
        errors.append("research overview is absent from nodes")
    titles = Counter(str(node.get("title", "")).casefold() for node in nodes.values())
    duplicates = sorted(title for title, count in titles.items() if title and count > 1)
    errors.extend(f"duplicate case-insensitive title: {title}" for title in duplicates)
    for path_id, node in nodes.items():
        if node.get("type") == "Research Overview" and not node.get("sources"):
            errors.append(f"{path_id}: research overview must declare sources")
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"OKF checks passed: {len(nodes)} nodes, {len(corpus['edges'])} relationships")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
