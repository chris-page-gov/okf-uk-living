---
type: "Research Evidence"
title: "Exhaustive reference-family inventory and gap analysis"
description: "Dated evidence for the full UK life-course reference-family denominator, external rights boundaries and population-gate gap dispositions."
status: "population-dispositions-complete"
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

The inventory retains the original 24 local `partial` cells because it is a
reference-family denominator, not a claim that every equivalent council page
has been acquired. On 2026-08-08 population assurance evaluated each gap against
the approved authority/archetype/material-exception model. `Closed for
population` does not mean release-grade review or continuous freshness.

| Disposition | Gap | Population evidence | Remaining boundary |
|---|---|---|---|
| Closed for population | `GAP-SERVICE-FAMILY-DENOMINATOR` | All 293 approved families reconcile exactly once to a dossier and process. | Preserve the denominator; unstaged acquisition remains disabled. |
| Closed for population | `GAP-LOCAL-LEAF` | Active authorities, structural archetypes, material exceptions and dossier provider/redress handoffs implement the approved model. | Re-observe applicable leaf instructions for release grade; do not duplicate equivalent council pages. |
| Closed for population | `GAP-LOCAL-TOPOLOGY` | The registry implements 382 principal areas, 19 strategic authorities, 397 GSS geographies and source-native fallbacks. | Maintain dated identities; postcodes are not stable authority identifiers. |
| Closed for population | `GAP-WALES-CITIZEN-ROUTES` | Every applicable dossier has a sourced Welsh discovery variant or sourced boundary. | Re-observe operational leaf routes for release grade; bilingual identity still requires explicit publisher pairing. |
| Closed decision | `GAP-HEALTH-AUTOMATION-RIGHTS` | Manual typed links and original summaries cover the health discovery routes. | Automated source-content acquisition remains prohibited without specific permission. |
| Closed for population | `GAP-PRIVATE-DEPENDENCIES` | Family dossiers apply regulator-first dependency mappings and record their selection basis. | The bundle does not recommend or exhaustively list private providers. |
| Non-blocking warning | `GAP-LEGAL-PROCEDURE-REVIEW` | All affected dossiers expose `specialist_review_required`; population completion permits that visible state. | Named legal, clinical and high-impact-deadline acceptance is required for release grade. |
| Closed for local evaluation | `GAP-EXPLORER-LARGE-CORPUS` | The 293-family projection and six search-to-source journeys pass locally. | Public deployment remains unauthorized and unverified. |
| Closed for population | `GAP-SECTOR-REDRESS` | The five-level taxonomy, shared identities and family-specific redress steps are projected as governed edges. | Re-observe case-specific prerequisites and deadlines for release grade. |
| Closed policy | `GAP-LGSL-CURRENCY` | The current ESD location is recorded and LGSL is optional mapping only. | LGSL never proves current service availability. |
| Closed for population | `GAP-FRESHNESS-AUTOMATION` | Dated, body-free metadata receipts support current discovery links. | Reviewed live audits stay separate from deterministic offline tests. |
| Closed policy | `GAP-BILINGUAL-IDENTITY` | Explicit publisher pairing is required throughout the authored contract. | Complete bilingual expression is not claimed; label similarity never creates identity. |

## Approved return decisions

On 2026-08-07 the owner approved all six requested governance decisions. The
[decision handoff](corpus-acquisition-decisions.md) and machine-readable
[policy](../profiles/corpus-acquisition-policy.v1.yaml) now govern the 293
families, local model and identifiers, manual health acquisition,
regulator-first dependencies, sector redress, specialist-review roles and the
locally approved Explorer projection.

The shared-authority/source-infrastructure phase and eight family packs supplied
the authority, dependency, redress, receipt and dossier evidence. Population
assurance disposed all twelve gaps on 2026-08-08 with no blocking population
omission. Specialist appointment, reviewed freshness and publication remain
separate later gates. This does not authorize source snapshots, copied source
content, CI or publication.
