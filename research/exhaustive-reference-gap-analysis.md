---
type: "Research Evidence"
title: "Exhaustive reference-family inventory and gap analysis"
description: "Dated evidence for the full UK life-course reference-family denominator, external rights boundaries and remaining corpus-acquisition gaps."
status: "draft"
timestamp: "2026-08-07T00:00:00+01:00"
generated:
  by: "ai:openai-codex"
  at: "2026-08-07T00:00:00+01:00"
---

# Exhaustive reference-family inventory and gap analysis

Decision date: 2026-08-07

Decision owner: `owner:chris-page-gov`

Machine-readable inventory:
[`source/exhaustive-reference-inventory.v1.yaml`](../source/exhaustive-reference-inventory.v1.yaml)

## Result

The external reference-family inventory is complete against its declared
denominator. It contains 89 newly researched external references and includes
the 53 references already registered for the three implemented slices: 142
external reference records in total, with no source snapshots.

The denominator is 24 life-course domains by five reference jurisdictions:
UK-or-England discovery, Scotland, Wales, Northern Ireland and local delivery.
All 120 cells are accounted for. The 96 national cells have an authoritative
reference family; all 24 local cells are partial because authority directories
exist but responsible leaf-service pages have not yet been selected against the
approved 293-family denominator.

“Complete” here means that every declared reference-family cell and required
capability has been assessed. It does not claim that every live service page,
provider, statute or local process has been acquired. A category page is a
discovery denominator, not evidence for the facts of a future service record.

## What is registered

| Reference layer | New records | Role |
|---|---:|---|
| GOV.UK browse and Content API | 20 | UK-or-England discovery, stable identifiers, owners and update metadata |
| mygov.scot | 14 | Scottish citizen-service topics and public-body directory |
| GOV.WALES | 21 | Welsh policy, service, organisation and local-government discovery |
| nidirect | 14 | Northern Ireland citizen-service topics and council directory |
| nibusinessinfo.co.uk | 2 | Northern Ireland business and innovation discovery |
| Four national health directories | 4 | England, Scotland, Wales and Northern Ireland health-provider discovery |
| Geography and organisation identifiers | 4 | ONS GSS geography names/codes/history and NHS ODS organisation identity/coverage |
| Standards and Explorer | 10 | CPSV-AP, Open Referral, HSDS, SKOS, OWL, PROV-O, SHACL, LGSL and OKF Explorer |
| Existing vertical-slice registers | 53 | Implemented rubbish, driving/enforcement and bereavement routes |
| **Total** | **142** | Linked references and original project summaries; zero snapshots |

The 89 new references have a URL, owner, jurisdiction, authority role,
observation date, source update value or explicit “not exposed” marker, a dated
rights-decision link and an original project summary. The existing 53 records
retain the same information through their `coverage` and `exclusions` fields,
which are original project descriptions rather than copied source text.

## Live URL observation

On 2026-08-07 a read-only request followed redirects for all 174 unique URLs
across the inventory, three slice registers and rights evidence. Of those, 170
returned HTTP 2xx. Cardiff Council's two registered service routes and its
rights-evidence page returned HTTP 403 to the automated client, as did the NHS
inform service directory; their browser-facing identities are retained and
their access limitations are not treated as evidence that the sources do not
exist. The four new ONS/NHS identifier pages and both new rights-evidence pages
returned HTTP 200. No response content was retained, and deterministic local
validation remains offline.

## Rights boundary

The rights evidence was reviewed on 2026-08-07 and is normalized in
[`source/rights-decisions.v1.yaml`](../source/rights-decisions.v1.yaml).

| Family | Evidence-based determination | Project use |
|---|---|---|
| GOV.UK, its Content API, mygov.scot, GOV.WALES and nidirect | OGL v3.0, subject to attribution and exclusions | Link and original summary only |
| NHS website for England | OGL v3.0 with NHS attribution, refresh and excluded-content conditions | Link and original summary only |
| NHS inform | Personal and non-commercial use; no scraping without permission | Link and original summary only; no unattended extraction |
| NHS 111 Wales | Crown copyright; copying and redistribution require its content-authorisation policy | Link and original summary only |
| HSCNI online services | Attributed non-commercial reproduction only; other use needs permission | Link and original summary only |
| nibusinessinfo.co.uk | Crown and Invest NI material have distinct terms; republication needs written permission and images are excluded | Link and original summary only |
| CPSV-AP 3.2.0 | CC BY 4.0 | Terminology mapping reference only |
| Open Referral UK and HSDS 3.1 | Site OGL statement with unversioned GitHub CC BY-SA label; HSDS documentation CC BY-SA 4.0 | Terminology mapping reference only |
| W3C Recommendations | W3C Document License 2023 | Link and terminology mapping only |
| LGSL data.gov.uk record | Open Government Licence without a version recorded on the 2014 catalogue record | Identifier mapping only; no current-service claim |
| OKF Explorer | Viewer code MIT; repository corpus and documentation CC BY-NC 4.0 | Consumer compatibility reference only |

The repository still does not redistribute source content. No licence evidence
has been interpreted as permission to snapshot, scrape or publish a provider's
material. Eligible repository-authored projections remain MIT only when they
contain original structure, summaries, facts and links rather than upstream
expression.

## Domain coverage

Every domain has at least one identified national discovery source in each of
the four national columns. The detailed source IDs are in the machine record.

| Domains | UK-or-England | Scotland | Wales | Northern Ireland | Local |
|---|---|---|---|---|---|
| 1–24 life-course domains | Covered at reference-family level | Covered at reference-family level | Covered at reference-family level | Covered at reference-family level | Partial: authority directories only |

This table intentionally does not say that the four routes are equivalent.
Future service records must still establish the exact responsible body,
jurisdiction, legal basis, evidence, time limits, dependencies and redress from
current leaf sources.

## Follow-up gap ledger

| Priority | Gap | What remains | Owner decision or follow-up |
|---|---|---|---|
| Closed decision | `GAP-SERVICE-FAMILY-DENOMINATOR` | The owner approved 293 normalized families in three staged waves. | Implement link registration and measure coverage against the named denominator. |
| High implementation | `GAP-LOCAL-LEAF` | All 24 local cells still need current responsible-provider and complaint coverage. | Build the exhaustive authority registry plus representative-archetype and material-exception leaf routes. |
| High implementation | `GAP-LOCAL-TOPOLOGY` | Councils, combined authorities, health geographies, police areas and contractors use different boundaries. | Apply dated GSS codes, applicable ODS codes and source-native identifiers under the approved policy. |
| High | `GAP-WALES-CITIZEN-ROUTES` | GOV.WALES is not a complete citizen transaction catalogue. | Confirm the operational Welsh delivery portals and bodies for each journey. |
| Closed decision | `GAP-HEALTH-AUTOMATION-RIGHTS` | A common unattended acquisition model is inappropriate. | Keep all four health families manual, link-and-original-summary only; reconsider permission only for a specific future automation need. |
| High implementation | `GAP-PRIVATE-DEPENDENCIES` | No single authoritative denominator covers all private dependencies. | Apply regulator-first discovery and record the provider-selection basis for required named dependencies. |
| External appointment | `GAP-LEGAL-PROCEDURE-REVIEW` | Roles are nominated, but consenting qualified legal and clinical individuals are not appointed. | Obtain applicable reviewer acceptance before production-grade legal or medical claims. |
| Conditional implementation | `GAP-EXPLORER-LARGE-CORPUS` | The local colour-facet projection is approved after the four Explorer findings close. | Close `REV-001` through `REV-004`, build and verify the large projection locally. |
| Medium implementation | `GAP-SECTOR-REDRESS` | The five-level taxonomy is approved; service-family mappings remain incomplete. | Cite the actual provider, statutory, tribunal, regulator/ombudsman and court sequence for each family. |
| Medium | `GAP-LGSL-CURRENCY` | The OGL-labelled LGSL catalogue record is dated 2014. | Confirm current ESD Services-list access, version and identifier policy. |
| Medium | `GAP-FRESHNESS-AUTOMATION` | Devolved portals do not expose one shared update API. | Approve per-family review intervals and permitted automated metadata checks. |
| Medium | `GAP-BILINGUAL-IDENTITY` | Welsh and English routes cannot be equated from labels or URLs alone. | Approve language-variant identity and equivalence rules. |

## Approved return decisions

On 2026-08-07 the owner approved all six requested governance decisions. The
[decision handoff](corpus-acquisition-decisions.md) and machine-readable
[policy](../profiles/corpus-acquisition-policy.v1.yaml) now govern the 293
families, local model and identifiers, manual health acquisition,
regulator-first dependencies, sector redress, specialist-review roles and the
conditional Explorer projection.

The remaining ledger is implementation and specialist-review work. It does not
authorize source snapshots, copied source content, CI or publication.
