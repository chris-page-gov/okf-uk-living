#!/usr/bin/env python3
"""Run repository-specific semantic checks over the authored OKF corpus."""

from __future__ import annotations

from collections import Counter

from build_okf_bundle import build_bundle


MISSED_RUBBISH_ROUTES = {
    "services/coventry-missed-bin-collection.md": {
        "jurisdiction": "england:coventry",
        "provider": "coventry-city-council",
        "sources": {"coventry-missed-bin", "coventry-complaints"},
    },
    "services/edinburgh-missed-bin-collection.md": {
        "jurisdiction": "scotland:edinburgh",
        "provider": "city-of-edinburgh-council",
        "sources": {"edinburgh-missed-bin", "edinburgh-complaints"},
    },
    "services/cardiff-missed-collection.md": {
        "jurisdiction": "wales:cardiff",
        "provider": "cardiff-council",
        "sources": {"cardiff-missed-collection", "cardiff-complaints"},
    },
    "services/belfast-missed-bin-collection.md": {
        "jurisdiction": "northern-ireland:belfast",
        "provider": "belfast-city-council",
        "sources": {"belfast-missed-bin", "belfast-complaints"},
    },
}
MISSED_RUBBISH_SUPPORTING_NODES = {
    "services/report-missed-rubbish-collection.md",
    "journeys/missed-rubbish-collection.md",
    "ontology/missed-rubbish-collection.md",
    "evidence/missed-rubbish-collection-sources.md",
    "jurisdictions/england.md",
    "jurisdictions/scotland.md",
    "jurisdictions/wales.md",
    "jurisdictions/northern-ireland.md",
    "organisations/coventry-city-council.md",
    "organisations/city-of-edinburgh-council.md",
    "organisations/cardiff-council.md",
    "organisations/belfast-city-council.md",
    "organisations/local-government-and-social-care-ombudsman.md",
    "organisations/scottish-public-services-ombudsman.md",
    "organisations/public-services-ombudsman-for-wales.md",
    "organisations/northern-ireland-public-services-ombudsman.md",
}
DRIVING_SPEEDING_ROUTES = {
    "services/great-britain-learn-to-drive-car.md": {
        "family": "learn-to-drive-car",
        "jurisdiction": "great-britain",
        "providers": {"driver-and-vehicle-licensing-agency", "driver-and-vehicle-standards-agency"},
        "sources": {
            "govuk-learn-to-drive-car",
            "govuk-first-provisional-licence",
            "govuk-private-practice",
            "govuk-book-theory-test",
            "govuk-driving-test-result",
            "govuk-full-driving-licence",
        },
    },
    "services/northern-ireland-learn-to-drive-car.md": {
        "family": "learn-to-drive-car",
        "jurisdiction": "northern-ireland",
        "providers": {"driver-and-vehicle-agency-northern-ireland"},
        "sources": {
            "nidirect-provisional-licence",
            "nidirect-learner-rules",
            "nidirect-theory-test",
            "nidirect-practical-test",
            "nidirect-claim-test-pass",
        },
    },
    "services/great-britain-speeding-notice.md": {
        "family": "respond-to-speeding-notice",
        "jurisdiction": "great-britain:notice-specific",
        "providers": {"notice-issuing-police-force-great-britain"},
        "sources": {"govuk-speeding-penalties", "legislation-rta-1988-section-172"},
    },
    "services/england-wales-speeding-court-route.md": {
        "family": "respond-to-speeding-notice",
        "jurisdiction": "england-and-wales",
        "providers": {"hm-courts-and-tribunals-service"},
        "sources": {"govuk-single-justice-procedure", "govuk-appeal-magistrates-decision"},
    },
    "services/scotland-speeding-prosecution-route.md": {
        "family": "respond-to-speeding-notice",
        "jurisdiction": "scotland",
        "providers": {"crown-office-and-procurator-fiscal-service"},
        "sources": {"copfs-prosecution-code", "mygov-scotland-criminal-appeal"},
    },
    "services/northern-ireland-speeding-notice.md": {
        "family": "respond-to-speeding-notice",
        "jurisdiction": "northern-ireland",
        "providers": {
            "northern-ireland-road-safety-partnership",
            "northern-ireland-courts-and-tribunals-service",
        },
        "sources": {
            "nidirect-speeding-penalties",
            "nidirect-fixed-penalties",
            "nidirect-appealing-verdict",
        },
    },
}
DRIVING_SPEEDING_SUPPORTING_NODES = {
    "services/learn-to-drive-car.md",
    "services/respond-to-speeding-notice.md",
    "journeys/learning-to-drive-speeding.md",
    "ontology/learning-to-drive-speeding.md",
    "evidence/learning-to-drive-speeding-sources.md",
    "jurisdictions/england.md",
    "jurisdictions/scotland.md",
    "jurisdictions/wales.md",
    "jurisdictions/northern-ireland.md",
    "organisations/driver-and-vehicle-licensing-agency.md",
    "organisations/driver-and-vehicle-standards-agency.md",
    "organisations/driver-and-vehicle-agency-northern-ireland.md",
    "organisations/notice-issuing-police-force-great-britain.md",
    "organisations/hm-courts-and-tribunals-service.md",
    "organisations/crown-office-and-procurator-fiscal-service.md",
    "organisations/northern-ireland-road-safety-partnership.md",
    "organisations/northern-ireland-courts-and-tribunals-service.md",
    "organisations/driving-instructor.md",
    "organisations/motor-insurer.md",
}
BEREAVEMENT_ROUTES = {
    "services/england-wales-death-registration.md": {
        "family": "register-a-death",
        "jurisdiction": "england-and-wales",
        "providers": {"local-register-office-england-wales"},
        "sources": {"govuk-register-a-death", "govuk-correcting-death-registration"},
    },
    "services/scotland-death-registration.md": {
        "family": "register-a-death",
        "jurisdiction": "scotland",
        "providers": {"scottish-registration-authority", "crown-office-and-procurator-fiscal-service"},
        "sources": {"nrs-registering-a-death", "copfs-death-investigation"},
    },
    "services/northern-ireland-death-registration.md": {
        "family": "register-a-death",
        "jurisdiction": "northern-ireland",
        "providers": {"general-register-office-northern-ireland", "coroners-service-northern-ireland"},
        "sources": {"nidirect-registering-a-death", "nidirect-coroners"},
    },
    "services/tell-us-once.md": {
        "family": "notify-organisations-after-a-death",
        "jurisdiction": "england-scotland-wales:residence-specific",
        "providers": {"tell-us-once-service"},
        "sources": {"govuk-tell-us-once"},
    },
    "services/northern-ireland-death-notifications.md": {
        "family": "notify-organisations-after-a-death",
        "jurisdiction": "northern-ireland",
        "providers": {"northern-ireland-bereavement-service"},
        "sources": {"nidirect-who-to-tell", "nidirect-bereavement-service"},
    },
    "services/england-wales-probate-estate.md": {
        "family": "administer-an-estate",
        "jurisdiction": "england-and-wales",
        "providers": {"hm-courts-and-tribunals-service", "hm-revenue-and-customs"},
        "sources": {
            "govuk-applying-for-probate",
            "govuk-value-estate",
            "govuk-probate-estate",
            "govuk-inheritance-tax",
        },
    },
    "services/scotland-confirmation-estate.md": {
        "family": "administer-an-estate",
        "jurisdiction": "scotland",
        "providers": {"scottish-courts-and-tribunals-service", "hm-revenue-and-customs"},
        "sources": {
            "scotcourts-confirmation",
            "govscot-after-a-death",
            "govuk-value-estate",
            "govuk-inheritance-tax",
        },
    },
    "services/northern-ireland-probate-estate.md": {
        "family": "administer-an-estate",
        "jurisdiction": "northern-ireland",
        "providers": {"northern-ireland-courts-and-tribunals-service", "hm-revenue-and-customs"},
        "sources": {
            "nidirect-apply-probate",
            "nidirect-no-will",
            "nidirect-debt-after-death",
            "govuk-value-estate",
            "govuk-inheritance-tax",
        },
    },
}
BEREAVEMENT_SUPPORTING_NODES = {
    "services/register-a-death.md",
    "services/notify-organisations-after-a-death.md",
    "services/administer-an-estate.md",
    "journeys/death-bereavement-estate.md",
    "ontology/death-bereavement-estate.md",
    "evidence/death-bereavement-estate-sources.md",
    "jurisdictions/england.md",
    "jurisdictions/scotland.md",
    "jurisdictions/wales.md",
    "jurisdictions/northern-ireland.md",
    "organisations/local-register-office-england-wales.md",
    "organisations/scottish-registration-authority.md",
    "organisations/general-register-office-northern-ireland.md",
    "organisations/coroners-service-northern-ireland.md",
    "organisations/tell-us-once-service.md",
    "organisations/northern-ireland-bereavement-service.md",
    "organisations/hm-courts-and-tribunals-service.md",
    "organisations/crown-office-and-procurator-fiscal-service.md",
    "organisations/scottish-courts-and-tribunals-service.md",
    "organisations/northern-ireland-courts-and-tribunals-service.md",
    "organisations/hm-revenue-and-customs.md",
    "organisations/funeral-provider.md",
    "organisations/private-organisation-after-death.md",
    "organisations/estate-practitioner.md",
}


def validate_missed_rubbish_slice(
    nodes: dict[str, dict[str, object]], edges: list[dict[str, str]]
) -> list[str]:
    """Check the first vertical slice's authority, scope and graph invariants."""

    errors: list[str] = []
    required = set(MISSED_RUBBISH_ROUTES) | MISSED_RUBBISH_SUPPORTING_NODES
    missing = sorted(required - set(nodes))
    errors.extend(f"missed-rubbish slice is missing {path}" for path in missing)
    if missing:
        return errors

    for path, expected in MISSED_RUBBISH_ROUTES.items():
        node = nodes[path]
        if node.get("type") != "Public Service Route":
            errors.append(f"{path}: must be a Public Service Route")
        if node.get("assertion_status") != "official":
            errors.append(f"{path}: local route assertion_status must be official")
        if node.get("service_family") != "report-missed-rubbish-collection":
            errors.append(f"{path}: must retain the normalized service family")
        for field in ("jurisdiction", "provider"):
            if node.get(field) != expected[field]:
                errors.append(f"{path}: {field} must be {expected[field]}")
        if node.get("observed_at") != "2026-08-07":
            errors.append(f"{path}: observed_at must preserve the source observation date")
        sources = node.get("sources", [])
        source_ids = {
            str(source.get("id"))
            for source in sources
            if isinstance(source, dict) and source.get("id")
        }
        if source_ids != expected["sources"]:
            errors.append(f"{path}: must cite its exact service and council-complaint sources")

    family = nodes["services/report-missed-rubbish-collection.md"]
    if family.get("assertion_status") != "normalized":
        errors.append("missed-rubbish service family must be normalized")
    journey = nodes["journeys/missed-rubbish-collection.md"]
    if journey.get("assertion_status") != "editorial-example" or journey.get("synthetic") is not True:
        errors.append("missed-rubbish journey must remain a synthetic editorial-example")
    journey_text = " ".join(str(journey.get("body", "")).split())
    if "not combined into a universal reporting rule" not in journey_text:
        errors.append("missed-rubbish journey must reject a universal local timing rule")
    evidence = nodes["evidence/missed-rubbish-collection-sources.md"]
    if evidence.get("assertion_status") != "normalized":
        errors.append("missed-rubbish evidence set must be normalized")

    journey_targets = {
        edge["target"]
        for edge in edges
        if edge["source"] == "journeys/missed-rubbish-collection.md"
    }
    expected_journey_targets = required - {"journeys/missed-rubbish-collection.md"}
    for target in sorted(expected_journey_targets - journey_targets):
        errors.append(f"missed-rubbish journey must link to {target}")
    return errors


def validate_driving_speeding_slice(
    nodes: dict[str, dict[str, object]], edges: list[dict[str, str]]
) -> list[str]:
    """Check the second slice's evidence order and jurisdiction invariants."""

    errors: list[str] = []
    required = set(DRIVING_SPEEDING_ROUTES) | DRIVING_SPEEDING_SUPPORTING_NODES
    missing = sorted(required - set(nodes))
    errors.extend(f"driving-speeding slice is missing {path}" for path in missing)
    if missing:
        return errors

    for path, expected in DRIVING_SPEEDING_ROUTES.items():
        node = nodes[path]
        if node.get("type") != "Public Service Route":
            errors.append(f"{path}: must be a Public Service Route")
        if node.get("assertion_status") != "official":
            errors.append(f"{path}: route assertion_status must be official")
        if node.get("service_family") != expected["family"]:
            errors.append(f"{path}: must retain service family {expected['family']}")
        if node.get("jurisdiction") != expected["jurisdiction"]:
            errors.append(f"{path}: jurisdiction must be {expected['jurisdiction']}")
        provider_value = node.get("providers", node.get("provider", []))
        provider_values = provider_value if isinstance(provider_value, list) else [provider_value]
        if set(provider_values) != expected["providers"]:
            errors.append(f"{path}: must retain its exact authority provider set")
        if node.get("observed_at") != "2026-08-07":
            errors.append(f"{path}: observed_at must preserve the source observation date")
        sources = node.get("sources", [])
        source_ids = {
            str(source.get("id"))
            for source in sources
            if isinstance(source, dict) and source.get("id")
        }
        if source_ids != expected["sources"]:
            errors.append(f"{path}: must cite its exact approved source set")

    for family_path in (
        "services/learn-to-drive-car.md",
        "services/respond-to-speeding-notice.md",
    ):
        if nodes[family_path].get("assertion_status") != "normalized":
            errors.append(f"{family_path}: service family must be normalized")
    journey = nodes["journeys/learning-to-drive-speeding.md"]
    if journey.get("assertion_status") != "editorial-example" or journey.get("synthetic") is not True:
        errors.append("driving-speeding journey must remain a synthetic editorial-example")
    journey_text = " ".join(str(journey.get("body", "")).split())
    if "not combined into one UK deadline" not in journey_text:
        errors.append("driving-speeding journey must reject a universal notice or court deadline")
    evidence = nodes["evidence/learning-to-drive-speeding-sources.md"]
    if evidence.get("assertion_status") != "normalized":
        errors.append("driving-speeding evidence set must be normalized")

    journey_targets = {
        edge["target"]
        for edge in edges
        if edge["source"] == "journeys/learning-to-drive-speeding.md"
    }
    expected_journey_targets = required - {"journeys/learning-to-drive-speeding.md"}
    for target in sorted(expected_journey_targets - journey_targets):
        errors.append(f"driving-speeding journey must link to {target}")
    return errors


def validate_bereavement_slice(
    nodes: dict[str, dict[str, object]], edges: list[dict[str, str]]
) -> list[str]:
    """Check the third slice's authority, notification and estate invariants."""

    errors: list[str] = []
    required = set(BEREAVEMENT_ROUTES) | BEREAVEMENT_SUPPORTING_NODES
    missing = sorted(required - set(nodes))
    errors.extend(f"bereavement slice is missing {path}" for path in missing)
    if missing:
        return errors

    for path, expected in BEREAVEMENT_ROUTES.items():
        node = nodes[path]
        if node.get("type") != "Public Service Route":
            errors.append(f"{path}: must be a Public Service Route")
        if node.get("assertion_status") != "official":
            errors.append(f"{path}: route assertion_status must be official")
        if node.get("service_family") != expected["family"]:
            errors.append(f"{path}: must retain service family {expected['family']}")
        if node.get("jurisdiction") != expected["jurisdiction"]:
            errors.append(f"{path}: jurisdiction must be {expected['jurisdiction']}")
        provider_value = node.get("providers", node.get("provider", []))
        provider_values = provider_value if isinstance(provider_value, list) else [provider_value]
        if set(provider_values) != expected["providers"]:
            errors.append(f"{path}: must retain its exact authority provider set")
        if node.get("observed_at") != "2026-08-07":
            errors.append(f"{path}: observed_at must preserve the source observation date")
        sources = node.get("sources", [])
        source_ids = {
            str(source.get("id"))
            for source in sources
            if isinstance(source, dict) and source.get("id")
        }
        if source_ids != expected["sources"]:
            errors.append(f"{path}: must cite its exact approved source set")

    for family_path in (
        "services/register-a-death.md",
        "services/notify-organisations-after-a-death.md",
        "services/administer-an-estate.md",
    ):
        if nodes[family_path].get("assertion_status") != "normalized":
            errors.append(f"{family_path}: service family must be normalized")
    journey = nodes["journeys/death-bereavement-estate.md"]
    if journey.get("assertion_status") != "editorial-example" or journey.get("synthetic") is not True:
        errors.append("bereavement journey must remain a synthetic editorial-example")
    journey_text = " ".join(str(journey.get("body", "")).split())
    if "not treated as a universal UK notification service" not in journey_text:
        errors.append("bereavement journey must reject universal Tell Us Once coverage")
    if "not combined into one UK estate process" not in journey_text:
        errors.append("bereavement journey must reject a universal estate process")
    evidence = nodes["evidence/death-bereavement-estate-sources.md"]
    if evidence.get("assertion_status") != "normalized":
        errors.append("bereavement evidence set must be normalized")

    journey_targets = {
        edge["target"]
        for edge in edges
        if edge["source"] == "journeys/death-bereavement-estate.md"
    }
    expected_journey_targets = required - {"journeys/death-bereavement-estate.md"}
    for target in sorted(expected_journey_targets - journey_targets):
        errors.append(f"bereavement journey must link to {target}")
    return errors


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
        source = str(node.get("source", ""))
        generated = node.get("generated", {})
        if node.get("authored_source") != path_id or not source.startswith("generated/browser/"):
            errors.append(f"{path_id}: must expose its authored identity through a browser handoff")
        if not isinstance(generated, dict) or not generated.get("by") or not generated.get("at"):
            errors.append(f"{path_id}: must expose node-level build provenance")
        if node.get("type") == "Research Overview" and not node.get("sources"):
            errors.append(f"{path_id}: research overview must declare sources")
    for edge in corpus["edges"]:
        authority = edge.get("authority", {})
        if edge.get("schema") != "okf-relationship-assertion.v2":
            errors.append(f"{edge.get('id', 'relationship')}: must use the governed relationship contract")
        if not isinstance(authority, dict) or authority.get("class") not in {"derived", "synthetic"}:
            errors.append(f"{edge.get('id', 'relationship')}: must declare relationship authority")
        if not edge.get("derivation") or not edge.get("evidence") or not edge.get("rights"):
            errors.append(f"{edge.get('id', 'relationship')}: must declare provenance, evidence and rights")
    if "evidence/licensing-and-attribution.md" not in nodes:
        errors.append("first-class licensing and attribution evidence is absent from nodes")
    errors.extend(validate_missed_rubbish_slice(nodes, corpus["edges"]))
    errors.extend(validate_driving_speeding_slice(nodes, corpus["edges"]))
    errors.extend(validate_bereavement_slice(nodes, corpus["edges"]))
    if errors:
        for error in errors:
            print(error)
        return 1
    print(f"OKF checks passed: {len(nodes)} nodes, {len(corpus['edges'])} relationships")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
