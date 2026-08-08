#!/usr/bin/env python3
"""Render reviewed domain registers into family dossiers and narratives."""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path
from typing import Any

import yaml

from build_okf_bundle import ROOT
REGISTER_ROOT = ROOT / "source" / "domain-registers"
DOSSIER_ROOT = ROOT / "source" / "life-course-families"
NARRATIVE_ROOT = ROOT / "services"
DOMAIN_NARRATIVE_ROOT = ROOT / "life-course"
NATIONS = ("England", "Scotland", "Wales", "Northern Ireland")
SLUG = {
    "England": "england",
    "Scotland": "scotland",
    "Wales": "wales",
    "Northern Ireland": "northern-ireland",
}


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def registers() -> list[tuple[Path, dict[str, Any]]]:
    result: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted(REGISTER_ROOT.glob("*.v1.yaml")):
        value = load_yaml(path)
        if value.get("register_version") == "life-course-domain-register.v1":
            result.append((path, value))
    return result


def process_maps() -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    value = load_yaml(ROOT / "source" / "life-course-processes.v1.yaml")
    by_family: dict[str, dict[str, Any]] = {}
    for process in value.get("processes", []):
        for family_id in process.get("families", []):
            by_family[str(family_id)] = process
    domain_titles = {
        str(domain["id"]): str(domain["title"])
        for domain in load_yaml(ROOT / "source" / "service-family-denominator.v1.yaml")["domains"]
    }
    return by_family, domain_titles


def source_ids_for_family(register: dict[str, Any], family: dict[str, Any]) -> dict[str, str]:
    primary_id = str(family["source"]["id"])
    primary_jurisdictions = set(family["primary_jurisdictions"])
    fallbacks = {
        str(item["jurisdiction"]): str(item["id"])
        for item in register.get("route_sources", [])
    }
    return {
        nation: primary_id if nation in primary_jurisdictions else fallbacks[nation]
        for nation in NATIONS
    }


def supported(state: str, summary: str = "", reason: str = "") -> dict[str, str]:
    result = {"state": state}
    result["summary" if summary else "reason"] = summary or reason
    return result


def dossier(
    *, register_path: Path, register: dict[str, Any], family: dict[str, Any],
    process: dict[str, Any],
) -> dict[str, Any]:
    family_id = str(family["id"])
    title = str(family["title"])
    route_sources = source_ids_for_family(register, family)
    all_source_ids = list(dict.fromkeys([str(family["source"]["id"]), *route_sources.values()]))
    register_rel = register_path.relative_to(ROOT).as_posix()
    actors = [
        {
            "id": f"organisation:{SLUG[nation]}-official-route-provider",
            "role": "authoritative_service_or_discovery_handoff",
            "authority_status": "normalized",
            "sources": [source_id],
        }
        for nation, source_id in route_sources.items()
    ]
    applicability = [
        {
            "jurisdiction": nation,
            "state": "supported",
            "route_variants": [{
                "id": f"{SLUG[nation]}-current-official-route",
                "provider": f"organisation:{SLUG[nation]}-official-route-provider",
                "primary_source": source_id,
                "route_kind": (
                    "topic-specific-authoritative-page"
                    if source_id == family["source"]["id"]
                    else "authoritative-national-discovery-handoff"
                ),
            }],
            "sources": [source_id],
        }
        for nation, source_id in route_sources.items()
    ]
    route_summary = (
        "The source-linked route identifies the responsible service and publishes the current "
        "requirements, evidence, channel, costs and timing for that jurisdiction."
    )
    ordinary_steps = [
        {
            "id": "select-current-jurisdiction-route",
            "interaction": "Select the current official route for the place and situation.",
            "provider": "organisation:official-service-directory",
            "requirements": supported("supported", "Location and the source-defined situation boundary."),
            "evidence": supported("not_published_by_source", reason="Evidence is determined by the selected current route."),
            "rule": supported("supported", "Jurisdiction and provider rules remain separate and source-defined."),
            "channel": supported("supported", "Official web, telephone or local handoff shown by the selected source."),
            "cost": supported("not_published_by_source", reason="No cross-route cost is asserted; check the current official source."),
            "time": supported("not_published_by_source", reason="No cross-route deadline is asserted; check the current official source."),
            "output": supported("supported", "A current authoritative route and provider handoff."),
            "outcome": supported("supported", "The user can continue without assuming four-nation equivalence."),
            "redress": supported("supported", "Use the complaint, review or urgent route published by the selected authority."),
            "assertion_status": "normalized",
            "sources": all_source_ids,
        },
        {
            "id": "follow-current-official-instructions",
            "interaction": f"Follow the selected source to {title.lower()} and retain its output or reference.",
            "provider": "organisation:selected-authoritative-provider",
            "requirements": supported("supported", route_summary),
            "evidence": supported("supported", "Only the evidence requested by the selected current source."),
            "rule": supported("supported", "The responsible authority or provider decides the real case."),
            "channel": supported("supported", "The channel published by the current source."),
            "cost": supported("not_published_by_source", reason="Cost is deliberately not generalized across routes."),
            "time": supported("not_published_by_source", reason="Timing is deliberately not generalized across routes."),
            "output": supported("supported", "Source-defined confirmation, referral, decision or next-step information."),
            "outcome": supported("supported", family["description"]),
            "redress": supported("supported", "Escalate through the current provider's review, complaint or statutory redress route."),
            "assertion_status": "normalized",
            "sources": all_source_ids,
        },
    ]
    exception_steps = [{
        "id": "resolve-route-boundary-or-failure",
        "interaction": "Stop and use the current authority's exception, urgent, safeguarding or complaint handoff when the ordinary route does not fit.",
        "provider": "organisation:responsible-authority-or-redress-body",
        "requirements": supported("supported", "The source-defined exception or failure boundary."),
        "evidence": supported("not_published_by_source", reason="The responsible authority states what evidence is needed for the exception."),
        "rule": supported("supported", "No eligibility, clinical, safeguarding or legal decision is made by this bundle."),
        "channel": supported("supported", "Current official exception, urgent or complaint route."),
        "cost": supported("not_published_by_source", reason="Consult the current authority route."),
        "time": supported("not_published_by_source", reason="Urgency and deadlines are case- and route-specific."),
        "output": supported("supported", "An authority decision, alternate route or recorded unresolved state."),
        "outcome": supported("supported", "The user is handed to the accountable route without a fabricated answer."),
        "redress": supported("supported", "Current provider complaint, statutory review, regulator or ombudsman route as applicable."),
        "assertion_status": "normalized",
        "sources": all_source_ids,
    }]
    dependencies = []
    if family.get("dependency"):
        dependencies.append({
            "id": str(family["dependency"]),
            "selection_basis": "Use the current public regulator, register or commissioning route before choosing a provider.",
            "assertion_status": "normalized",
            "sources": all_source_ids,
        })
    return {
        "schema": "life-course-family.v1",
        "id": family_id,
        "title": title,
        "aliases": list(family["aliases"]),
        "description": str(family["description"]),
        "status": "population_complete",
        "assertion_status": "normalized",
        "life_course_domain": str(register["domain"]),
        "enclosing_processes": [{
            "id": str(process["id"]),
            "assertion_status": "normalized",
            "sources": all_source_ids,
        }],
        "situations": list(family["situations"]),
        "user_needs": list(family["user_needs"]),
        "interaction_boundary": (
            "Source-linked discovery and process navigation only; the bundle does not decide "
            "eligibility, diagnosis, treatment, safeguarding action or legal outcome."
        ),
        "applicability": applicability,
        "actors": actors,
        "journeys": {
            "ordinary": {
                "id": "ordinary-source-linked-route",
                "entry_state": str(family["situations"][0]),
                "outcome": str(family["description"]),
                "steps": ordinary_steps,
            },
            "exceptions": [{
                "id": "exception-or-route-failure",
                "entry_state": "The standard route is unavailable, does not fit, or indicates an urgent or specialist boundary.",
                "outcome": "The accountable exception, urgent or redress route is identified without making the decision locally.",
                "steps": exception_steps,
            }],
        },
        "dependencies": dependencies,
        "sources": [{"id": source_id, "register": register_rel} for source_id in all_source_ids],
        "limitations": [
            "Original summaries and links only; no upstream source response or snapshot is retained.",
            "A national discovery handoff locates the current route but does not establish a leaf rule, eligibility condition, cost or deadline.",
            "Jurisdictions, providers and exceptions remain separate even where labels are similar.",
            "Specialist review is required before legal, clinical, safeguarding or high-impact operational claims are release-grade.",
        ],
        "review": {"population_gate": "complete", "specialist_review": str(family["specialist_review"])},
        "narrative": {
            "markdown": f"services/{family_id}.md",
            "process_context": str(process["title"]),
        },
    }


def yaml_text(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, sort_keys=False, allow_unicode=True, width=100)


def quote(value: str) -> str:
    return value.replace('"', '\\"')


def narrative(
    *, register_path: Path, register: dict[str, Any], family: dict[str, Any], process: dict[str, Any],
) -> str:
    route_sources = source_ids_for_family(register, family)
    source_by_id = {
        str(source["id"]): source
        for source in [*register.get("route_sources", []), *(item["source"] for item in register["families"])]
    }
    source_lines = "\n".join(
        f"- [{nation}: {source_by_id[source_id]['title']}]({source_by_id[source_id]['resource']})"
        for nation, source_id in route_sources.items()
    )
    dependency = (
        "\nWhere a non-public provider is needed, start with the current public regulator, "
        "register or commissioning route; this bundle does not recommend providers.\n"
        if family.get("dependency") else ""
    )
    return f'''---
type: "Service Family"
title: "{quote(str(family['title']))}"
description: "{quote(str(family['description']))}"
status: "population-complete"
assertion_status: "normalized"
jurisdiction: "nation-specific"
observed_at: "{register['observed_at']}"
sources:
  - id: "{register['domain']}-source-register"
    title: "{quote(str(register['title']))}"
    resource: "../{register_path.relative_to(ROOT).as_posix()}"
    author: "organisation:okf-uk-living"
    observed_at: "{register['observed_at']}"
---

# {family['title']}

## Place in the process

This topic sits within **{process['title']}** in the **{register['title']}** life-course
domain. What comes before depends on the person's situation and nation; the first
safe step is to select the current official route rather than assume one UK process.

## What this family covers

{family['description']}

The ordinary discovery journey is to select the jurisdiction-specific route, follow
the responsible authority or provider's current instructions, and retain the
confirmation, referral, decision or next-step information it produces.

## If the ordinary route does not fit

If a route is unavailable, the circumstances fall outside it, or the source signals
an urgent, safeguarding, clinical or legal boundary, stop and follow that authority's
exception or complaint handoff. The bundle records this branch but does not decide it.
{dependency}
## Official routes

{source_lines}

These are links and original navigation summaries. A national discovery page is a
handoff to the current service, not evidence that eligibility, evidence, costs,
deadlines or remedies are identical across nations or providers.

## What may follow

The result can feed the next family in **{process['title']}**, another enclosing
process, or a provider-specific review or redress route. Use Graph to inspect the
ordinary and exception episodes, sources, actors, requirements, outputs and outcomes.

## Review status

This record is population-complete for discovery and requires specialist review
before any legal, clinical, safeguarding or high-impact operational claim is
described as release-grade.
'''


def domain_narrative(register: dict[str, Any], processes: list[dict[str, Any]]) -> str:
    process_lines = "\n".join(
        f"- **{process['title']}** — {len(process['families'])} service families"
        for process in processes
    )
    return f'''---
type: "Life-course Domain"
title: "{quote(str(register['title']))}"
description: "Source-linked process navigation for {quote(str(register['title']).lower())}."
status: "population-complete"
assertion_status: "normalized"
jurisdiction: "nation-specific"
observed_at: "{register['observed_at']}"
---

# {register['title']}

This domain groups {len(register['families'])} approved service families into the
following repository-authored navigation processes:

{process_lines}

Open a process to browse its families, then open a family to inspect ordinary and
exception episodes. Source links remain nation- and provider-specific. This domain
does not imply that every person follows every route or that similar services are
equivalent across the United Kingdom.
'''


def expected_outputs() -> dict[Path, str]:
    process_by_family, _ = process_maps()
    outputs: dict[Path, str] = {}
    for register_path, register in registers():
        domain_processes: dict[str, dict[str, Any]] = {}
        for family in register["families"]:
            family_id = str(family["id"])
            process = process_by_family[family_id]
            domain_processes[str(process["id"])] = process
            outputs[DOSSIER_ROOT / str(register["domain"]) / f"{family_id}.v1.yaml"] = yaml_text(
                dossier(register_path=register_path, register=register, family=family, process=process)
            )
            outputs[NARRATIVE_ROOT / f"{family_id}.md"] = narrative(
                register_path=register_path, register=register, family=family, process=process
            )
        outputs[DOMAIN_NARRATIVE_ROOT / f"{register['domain']}.md"] = domain_narrative(
            register, list(domain_processes.values())
        )
    return outputs


def managed_paths() -> set[Path]:
    result: set[Path] = set()
    for _, register in registers():
        for family in register["families"]:
            family_id = str(family["id"])
            result.add(DOSSIER_ROOT / str(register["domain"]) / f"{family_id}.v1.yaml")
            result.add(NARRATIVE_ROOT / f"{family_id}.md")
        result.add(DOMAIN_NARRATIVE_ROOT / f"{register['domain']}.md")
    return result


def check(outputs: dict[Path, str]) -> list[str]:
    errors: list[str] = []
    for path, expected in sorted(outputs.items()):
        if not path.is_file():
            errors.append(f"{path.relative_to(ROOT)} is missing")
            continue
        actual = path.read_text(encoding="utf-8")
        if actual != expected:
            diff = difflib.unified_diff(
                actual.splitlines(), expected.splitlines(),
                fromfile=f"current/{path.relative_to(ROOT)}",
                tofile=f"rendered/{path.relative_to(ROOT)}", lineterm="",
            )
            errors.append("\n".join(diff))
    return errors


def write(outputs: dict[Path, str]) -> None:
    for path, content in outputs.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    outputs = expected_outputs()
    if args.check:
        errors = check(outputs)
        if errors:
            for error in errors:
                print(error, file=sys.stderr)
            return 1
        print(f"Life-course pack renderings are synchronized: {len(outputs)} files")
        return 0
    write(outputs)
    print(f"wrote {len(outputs)} life-course pack dossier and narrative files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
