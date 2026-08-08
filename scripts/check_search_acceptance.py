#!/usr/bin/env python3
"""Validate canonical, alias and staged competency-query retrieval."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml

from build_large_corpus import ROOT, search_tokens
from check_domain_registers import load_registers


QUESTION_ROOT = ROOT / "evaluation" / "competency-questions"


def load_rows() -> list[dict[str, Any]]:
    manifest = json.loads((ROOT / "large/data/manifest.json").read_text(encoding="utf-8"))
    return [
        row
        for chunk in manifest["chunks"]["datasets"]
        for row in json.loads((ROOT / chunk).read_text(encoding="utf-8"))
    ]


def rank(query: str, rows: list[dict[str, Any]], postings: dict[str, list[list[int]]]) -> list[str]:
    tokens = [token for token in sorted(search_tokens(query)) if token in postings]
    if not tokens:
        return []
    scores: dict[int, int] = defaultdict(int)
    matches: dict[int, int] = defaultdict(int)
    candidates: set[int] = set()
    for token in tokens:
        token_scores = {int(item[0]): int(item[1]) for item in postings[token]}
        candidates.update(token_scores)
        for ordinal, score in token_scores.items():
            scores[ordinal] += score
            matches[ordinal] += 1
    return [
        str(rows[ordinal]["name"])
        for ordinal in sorted(candidates, key=lambda item: (-matches[item], -scores[item], str(rows[item]["title"])))
    ]


def validate_search_acceptance() -> list[str]:
    errors: list[str] = []
    rows = load_rows()
    postings = json.loads((ROOT / "large/data/search/postings.json").read_text(encoding="utf-8"))["tokens"]
    registers, register_errors = load_registers()
    errors.extend(register_errors)
    checked_terms = 0
    for path, register in registers:
        for family in register.get("families", []):
            family_id = str(family["id"])
            for query in [str(family["title"]), *map(str, family["aliases"])]:
                checked_terms += 1
                results = rank(query, rows, postings)
                if family_id not in results[:5]:
                    errors.append(f"{path.relative_to(ROOT)}: {query!r} does not return {family_id} in the first five")
    process_data = yaml.safe_load((ROOT / "source/life-course-processes.v1.yaml").read_text(encoding="utf-8"))
    domain_ids = {str(register["domain"]) for _, register in registers}
    for process in process_data.get("processes", []):
        if process.get("domain") not in domain_ids:
            continue
        results = rank(str(process["title"]), rows, postings)
        if str(process["id"]) not in [name.removeprefix("enclosing-process-") for name in results[:10]]:
            errors.append(f"process title {process['title']!r} is not searchable in the first ten")
    questions = 0
    observed_domains: set[str] = set()
    observed_jurisdictions: set[str] = set()
    for path in sorted(QUESTION_ROOT.glob("*.v1.yaml")):
        suite = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        if suite.get("suite") != "life-course-competency-questions.v1":
            continue
        for item in suite.get("questions", []):
            questions += 1
            observed_domains.update(map(str, item.get("domains", [])))
            observed_jurisdictions.update(map(str, item.get("jurisdictions", [])))
            results = rank(str(item.get("query", "")), rows, postings)
            if str(item.get("expected_family", "")) not in results[:10]:
                errors.append(f"{path.relative_to(ROOT)}: {item.get('id')} expected family is not in the first ten")
    if domain_ids - observed_domains:
        errors.append(f"competency questions omit staged domains: {sorted(domain_ids - observed_domains)}")
    required_nations = {"England", "Scotland", "Wales", "Northern Ireland"}
    if required_nations - observed_jurisdictions:
        errors.append(f"competency questions omit nations: {sorted(required_nations - observed_jurisdictions)}")
    if rank("zyxqv unmatched topic", rows, postings):
        errors.append("an unmatched query must return no invented result")
    if questions < 13 * len(registers) // 3:
        errors.append("each three-domain pack must contribute at least 13 competency questions")
    if checked_terms == 0:
        errors.append("no canonical titles or aliases were checked")
    return sorted(set(errors))


def main() -> int:
    errors = validate_search_acceptance()
    if errors:
        for error in errors:
            print(error)
        return 1
    registers, _ = load_registers()
    families = sum(len(register["families"]) for _, register in registers)
    questions = sum(
        len((yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("questions", []))
        for path in QUESTION_ROOT.glob("*.v1.yaml")
    )
    print(f"Search acceptance passed: {families} staged families and {questions} competency questions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
