#!/usr/bin/env python3
"""Refresh normalized authority/geography facts from reviewed official denominators.

This is a reviewed acquisition command, not an offline build step. It retains only
names, identifiers, effective/vintage dates and source URLs. HTTP response bodies
are parsed in memory and are never written to the repository.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.request import Request, urlopen

import yaml


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "source" / "authority-registry.v1.yaml"
SEEDS = ROOT / "source" / "shared-authority-seeds.v1.yaml"
OBSERVED_AT = "2026-08-08"

LAD_QUERY = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "WD26_LAD26_UK_LU/FeatureServer/0/query?where=1%3D1&"
    "outFields=LAD26CD%2CLAD26NM%2CLAD26NMW&returnGeometry=false&"
    "returnDistinctValues=true&orderByFields=LAD26CD&f=json"
)
COUNTY_QUERY = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "CTY_DEC_2024_EN_NC/FeatureServer/0/query?where=1%3D1&outFields="
    "CTY24CD%2CCTY24NM&returnGeometry=false&orderByFields=CTY24CD&f=json"
)
COMBINED_QUERY = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "CAUTH_MAY_2025_EN_NC/FeatureServer/0/query?where=1%3D1&outFields="
    "CAUTH25CD%2CCAUTH25NM&returnGeometry=false&orderByFields=CAUTH25CD&f=json"
)

SOURCES = [
    {
        "id": "ons-lad-may-2026",
        "title": "Ward to Local Authority District (May 2026) Lookup in the UK",
        "url": "https://geoportal.statistics.gov.uk/datasets/7447015a1f2f4332807d7341a636f95d",
        "query_url": LAD_QUERY,
        "owner": "Office for National Statistics",
        "rights_decision": "host:geoportal.statistics.gov.uk",
        "query_rights_decision": "host:services1.arcgis.com",
        "vintage": "2026-05-07",
        "assertion_scope": "GSS area names, codes and publisher-paired Welsh labels",
    },
    {
        "id": "ons-counties-december-2024",
        "title": "Counties (December 2024) Names and Codes in England",
        "url": "https://geoportal.statistics.gov.uk/datasets/74e61ed84af1495d930883709ab340c6",
        "query_url": COUNTY_QUERY,
        "owner": "Office for National Statistics",
        "rights_decision": "host:geoportal.statistics.gov.uk",
        "query_rights_decision": "host:services1.arcgis.com",
        "vintage": "2024-12-31",
        "assertion_scope": "GSS area names and codes for active two-tier English county areas",
    },
    {
        "id": "ons-combined-authorities-may-2025",
        "title": "Combined Authorities (May 2025) Names and Codes in England",
        "url": "https://geoportal.statistics.gov.uk/datasets/6b0ebe015596484ebd81e372da32db46",
        "query_url": COMBINED_QUERY,
        "owner": "Office for National Statistics",
        "rights_decision": "host:geoportal.statistics.gov.uk",
        "query_rights_decision": "host:services1.arcgis.com",
        "vintage": "2025-05-06",
        "assertion_scope": "GSS combined-authority area names and codes",
    },
    {
        "id": "govuk-local-government-structure-2026",
        "title": "Local government structure and elections",
        "url": "https://www.gov.uk/guidance/local-government-structure-and-elections",
        "owner": "Ministry of Housing, Communities and Local Government",
        "rights_decision": "host:www.gov.uk",
        "vintage": "live_guidance_observed_2026-08-08",
        "assertion_scope": "English authority types and responsibility topology",
    },
    {
        "id": "govuk-surrey-reorganisation-2026",
        "title": "Surrey local government reorganisation",
        "url": "https://www.gov.uk/government/collections/surrey-local-government-reorganisation",
        "owner": "Ministry of Housing, Communities and Local Government",
        "rights_decision": "host:www.gov.uk",
        "vintage": "updated_2026-07-07",
        "assertion_scope": "shadow-authority and 2027 service-transfer status",
    },
    {
        "id": "nhs-ods-coverage-2026",
        "title": "Organisation Data Service data coverage",
        "url": "https://digital.nhs.uk/services/organisation-data-service/ods-data-coverage",
        "owner": "NHS England",
        "rights_decision": "host:digital.nhs.uk",
        "vintage": "observed_2026-08-08",
        "assertion_scope": "health organisation identifier policy and coverage only",
    },
    {
        "id": "esd-services-list-current",
        "title": "Current Local Government Services List location",
        "url": "https://help.esd.org.uk/standards/faqs/where-can-i-find-latest-local-government-services-list-lgsl",
        "owner": "Local Government Association / Porism",
        "rights_decision": "host:help.esd.org.uk",
        "vintage": "live_help_page_observed_2026-08-08",
        "assertion_scope": "current vocabulary location; never current service availability",
    },
    {
        "id": "shared-authority-seeds-reviewed-links",
        "title": "Reviewed shared authority, regulator and redress links",
        "url": "https://github.com/chris-page-gov/okf-uk-living/blob/main/source/shared-authority-seeds.v1.yaml",
        "owner": "A Life in the UK",
        "rights_decision": "repository:MIT",
        "vintage": "reviewed_2026-08-08",
        "assertion_scope": "repository-authored role classifications and links to official identities",
    },
]

COMBINED_TITLES = {
    "E47000001": ("Greater Manchester Combined Authority", "combined_authority"),
    "E47000002": ("South Yorkshire Mayoral Combined Authority", "combined_authority"),
    "E47000003": ("West Yorkshire Combined Authority", "combined_authority"),
    "E47000004": ("Liverpool City Region Combined Authority", "combined_authority"),
    "E47000006": ("Tees Valley Combined Authority", "combined_authority"),
    "E47000007": ("West Midlands Combined Authority", "combined_authority"),
    "E47000008": ("Cambridgeshire and Peterborough Combined Authority", "combined_authority"),
    "E47000009": ("West of England Combined Authority", "combined_authority"),
    "E47000012": ("York and North Yorkshire Combined Authority", "combined_authority"),
    "E47000013": ("East Midlands Combined County Authority", "combined_county_authority"),
    "E47000014": ("North East Combined Authority", "combined_authority"),
    "E47000015": ("Devon and Torbay Combined County Authority", "combined_county_authority"),
    "E47000016": ("Hull and East Yorkshire Combined Authority", "combined_authority"),
    "E47000017": ("Greater Lincolnshire Combined County Authority", "combined_county_authority"),
    "E47000018": ("Lancashire Combined County Authority", "combined_county_authority"),
}


def fetch_json(url: str) -> dict[str, Any]:
    request = Request(url, headers={"Accept": "application/json", "User-Agent": "okf-uk-living-authority-refresh/1"})
    with urlopen(request, timeout=60) as response:  # noqa: S310 - reviewed official HTTPS sources
        value = json.load(response)
    if not isinstance(value, dict) or value.get("error"):
        raise ValueError(f"official denominator failed: {url}: {value.get('error')}")
    return value


def attributes(value: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [row.get("attributes", {}) for row in value.get("features", [])]
    return [row for row in rows if isinstance(row, dict)]


def nation_for(code: str) -> str:
    return {"E": "england", "N": "northern-ireland", "S": "scotland", "W": "wales"}[code[0]]


def area_type(code: str) -> str:
    prefixes = {
        "E060": "unitary_authority",
        "E070": "non_metropolitan_district",
        "E080": "metropolitan_district",
        "E090": "london_borough_or_city",
        "E100": "non_metropolitan_county",
        "N090": "local_government_district",
        "S120": "council_area",
        "W060": "principal_area",
        "E470": "combined_authority_area",
    }
    for prefix, value in prefixes.items():
        if code.startswith(prefix):
            return value
    raise ValueError(f"unrecognized GSS code family: {code}")


def geography(code: str, name: str, source_id: str, vintage: str, welsh_name: str | None = None) -> dict[str, Any]:
    labels = [{"language": "en", "value": name, "identity_basis": "official_gss_record"}]
    if welsh_name:
        labels.append({"language": "cy", "value": welsh_name, "identity_basis": "same_official_gss_record"})
    return {
        "id": f"geography:gss:{code.lower()}",
        "scheme": "GSS",
        "code": code,
        "official_name": name,
        "labels": labels,
        "geography_type": area_type(code),
        "jurisdiction": nation_for(code),
        "vintage_or_effective_date": vintage,
        "source_ids": [source_id],
        "observed_at": OBSERVED_AT,
    }


def local_organisation(area: dict[str, Any]) -> dict[str, Any]:
    name = str(area["official_name"])
    code = str(area["code"])
    return {
        "id": f"organisation:principal-local-authority:{code.lower()}",
        "title": f"Principal local authority serving {name}",
        "organisation_type": area["geography_type"],
        "jurisdictions": [area["jurisdiction"]],
        "administers": area["id"],
        "identity_status": "normalized_actor_bound_to_official_gss_area",
        "official_body_name": {"state": "not_published_by_source", "reason": "GSS identifies the area, not the legal body's styled name"},
        "route_evidence_required": True,
        "source_ids": list(area["source_ids"]),
        "observed_at": OBSERVED_AT,
    }


def build_registry() -> dict[str, Any]:
    seed = yaml.safe_load(SEEDS.read_text(encoding="utf-8"))
    if not isinstance(seed, dict):
        raise ValueError("shared authority seed root must be a mapping")
    lad_rows = attributes(fetch_json(LAD_QUERY))
    county_rows = attributes(fetch_json(COUNTY_QUERY))
    combined_rows = attributes(fetch_json(COMBINED_QUERY))
    geographies: list[dict[str, Any]] = []
    for row in lad_rows:
        geographies.append(geography(str(row["LAD26CD"]), str(row["LAD26NM"]), "ons-lad-may-2026", "2026-05-07", row.get("LAD26NMW")))
    for row in county_rows:
        geographies.append(geography(str(row["CTY24CD"]), str(row["CTY24NM"]), "ons-counties-december-2024", "2024-12-31"))
    organisations = [local_organisation(area) for area in geographies]
    for row in combined_rows:
        code = str(row["CAUTH25CD"])
        area = geography(code, str(row["CAUTH25NM"]), "ons-combined-authorities-may-2025", "2025-05-06")
        geographies.append(area)
        title, organisation_type = COMBINED_TITLES[code]
        organisations.append({
            "id": f"organisation:strategic-authority:{code.lower()}",
            "title": title,
            "organisation_type": organisation_type,
            "jurisdictions": ["england"],
            "administers": area["id"],
            "identity_status": "official_area_plus_reviewed_official_body_title",
            "route_evidence_required": True,
            "source_ids": ["ons-combined-authorities-may-2025", "govuk-local-government-structure-2026"],
            "observed_at": OBSERVED_AT,
        })
    for entry in seed.get("post_ons_strategic_authorities", []):
        value = dict(entry)
        value.update({
            "jurisdictions": [value.pop("jurisdiction")],
            "identity_status": "official_source_native_identity_pending_gss_assignment",
            "route_evidence_required": True,
            "source_ids": ["shared-authority-seeds-reviewed-links"],
            "observed_at": OBSERVED_AT,
        })
        organisations.append(value)
    for group in ("transition_bodies", "shared_actors"):
        for entry in seed.get(group, []):
            value = dict(entry)
            if "jurisdiction" in value and "jurisdictions" not in value:
                value["jurisdictions"] = [value.pop("jurisdiction")]
            value.setdefault("identity_status", "official_identity_linked_normalized_roles")
            value.setdefault("source_ids", ["shared-authority-seeds-reviewed-links"])
            value.setdefault("observed_at", OBSERVED_AT)
            organisations.append(value)
    geographies.sort(key=lambda value: str(value["id"]))
    organisations.sort(key=lambda value: str(value["id"]))
    local_count = len(lad_rows) + len(county_rows)
    strategic_count = len(combined_rows) + len(seed.get("post_ons_strategic_authorities", []))
    return {
        "authority_registry_version": "authority-registry.v1",
        "status": "current_reviewed",
        "observed_at": OBSERVED_AT,
        "identity_rules": {
            "gss_area_not_body": "A GSS code identifies an area, not by itself the legal body or service provider.",
            "welsh_language_variants": "English and Welsh labels share identity only when published in the same official GSS record or explicitly paired by the publisher.",
            "source_native_fallback": "Use a source-native identifier when GSS or ODS does not cover the organisation; never invent a code.",
            "postcode": "Postcodes may be used transiently for routing and are never retained.",
            "current_route": "A claim about a named service requires the responsible provider's current leaf page.",
            "lgsl": "LGSL/ESD Services identifiers are optional semantic mappings and never evidence current service availability.",
        },
        "sources": SOURCES,
        "denominators": {
            "principal_local_authority_areas_and_normalized_actors": {"count": local_count, "status": "complete_for_declared_gss_vintages", "expected": 382},
            "strategic_and_combined_authorities": {"count": strategic_count, "status": "complete_at_observation_date", "expected": 19},
            "transition_bodies": {"count": len(seed.get("transition_bodies", [])), "status": "tracked_separately_from_service_delivery"},
            "shared_regulator_redress_and_national_actors": {"count": len(seed.get("shared_actors", [])), "status": "shared_cross_pack_infrastructure"},
            "health_organisations": {"status": "ods_identifier_policy_registered_leaf_entities_added_manually_per_pack", "bulk_acquisition": False},
            "contracted_providers": {"status": "no_single_denominator_use_functional_role_unless_exact_provider_required"},
        },
        "geographies": geographies,
        "organisations": organisations,
        "sector_maps": seed["sector_maps"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="compare live normalized facts with the committed registry")
    args = parser.parse_args()
    registry = build_registry()
    class NoAliasSafeDumper(yaml.SafeDumper):
        def ignore_aliases(self, data: Any) -> bool:
            return True

    rendered = yaml.dump(registry, Dumper=NoAliasSafeDumper, sort_keys=False, allow_unicode=True, width=120)
    if args.check:
        if not OUTPUT.exists() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("authority registry differs from reviewed live denominators")
            return 1
        print("authority registry matches reviewed live denominators")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(
        "wrote authority registry: "
        f"{registry['denominators']['principal_local_authority_areas_and_normalized_actors']['count']} principal areas, "
        f"{registry['denominators']['strategic_and_combined_authorities']['count']} strategic authorities, "
        f"{len(registry['organisations'])} organisations total"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
