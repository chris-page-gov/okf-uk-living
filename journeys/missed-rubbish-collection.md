---
type: "Citizen Journey"
title: "Missed rubbish collection journey"
description: "Synthetic four-nation journey for locating, checking, reporting and escalating a missed local collection."
status: "implemented"
assertion_status: "editorial-example"
synthetic: true
jurisdiction: "local-authority-specific"
observed_at: "2026-08-07"
sources:
  - id: "missed-rubbish-source-register"
    title: "Missed rubbish collection linked-reference register"
    resource: "../source/missed-rubbish-collection.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Missed rubbish collection journey

This is a synthetic, editorial example. It contains no real name, address or
service episode and must not decide whether a real household can report a
collection. A reader should use the responsible authority's current official
route.

The journey exercises the normalized
[missed-rubbish ontology](../ontology/missed-rubbish-collection.md), the
[service family](../services/report-missed-rubbish-collection.md) and the
[bounded evidence set](../evidence/missed-rubbish-collection-sources.md).

## Ordinary path

1. **Locate authority.** Use a synthetic address context to identify the
   responsible council. Treat the GOV.UK page as a routing aid, not proof that
   one process applies across the UK.
2. **Check the expected collection.** Compare the council's current schedule,
   waste type, presentation conditions and disruption notices with the
   synthetic observed non-collection.
3. **Classify the next route.** Mark the event as reportable, excluded, too
   early, too late or unresolved using only the selected local evidence.
4. **Submit a minimal synthetic report.** Use the official channel with only
   the address context, scheduled date, waste type and other locally required
   fields. Retain the submission time and acknowledgement or reference.
5. **Record the outcome.** Preserve a return collection, explanation,
   rejection, channel failure or unresolved state without promising a remedy.

## Exception paths

- **Wrong authority:** correct the local-authority identity and do not carry
  the first council's timing or exclusion rules into the second route.
- **Too early or too late:** show the sourced local boundary and the official
  next route; do not substitute another council's reporting window.
- **Presentation or contamination:** retain the official reason, waste type and
  relevant evidence instead of treating every non-collection as service fault.
- **Access or operational disruption:** distinguish a locally stated access
  problem or disruption notice from an ordinary missed collection.
- **Channel failure:** retain what was attempted and link to an alternative
  official channel only where the local source supplies one.
- **Continuing service failure:** first use the council's complaint sequence,
  then show the jurisdiction-appropriate external body subject to its current
  scope and exhaustion rules.

## Four selected local variants

| Jurisdiction example | Responsible authority and official route | Observed local distinction | Redress boundary |
|---|---|---|---|
| [Coventry, England](../jurisdictions/england.md) | [Coventry City Council](../organisations/coventry-city-council.md): [missed-bin route](../services/coventry-missed-bin-collection.md) | Wait until after 5pm on the scheduled day; correct contents and garden-waste permit conditions apply | Report service issue, allow a reasonable opportunity, use council complaint stages, then [LGSCO](../organisations/local-government-and-social-care-ombudsman.md) where applicable |
| [Edinburgh, Scotland](../jurisdictions/scotland.md) | [The City of Edinburgh Council](../organisations/city-of-edinburgh-council.md): [delayed-collection route](../services/edinburgh-missed-bin-collection.md) | Kerbside visibility from 6am to 10pm, due day, lid, tag and access checks; an aim to return within two working days is local and operational | Use the council complaint route, then [SPSO](../organisations/scottish-public-services-ombudsman.md) subject to current rules |
| [Cardiff, Wales](../jurisdictions/wales.md) | [Cardiff Council](../organisations/cardiff-council.md): [missed-collection route](../services/cardiff-missed-collection.md) | Present by 6am and report within 48 hours; contamination, presentation, capacity, access, damage and disruption can alter the route | Report the service issue first, use the council complaint route, then [PSOW](../organisations/public-services-ombudsman-for-wales.md) subject to scope |
| [Belfast, Northern Ireland](../jurisdictions/northern-ireland.md) | [Belfast City Council](../organisations/belfast-city-council.md): [missed-bin route](../services/belfast-missed-bin-collection.md) | Wait until after 7pm; weight, contents, damage and liner conditions apply; online and telephone channels are stated | Complete the council complaint process and final response, then [NIPSO](../organisations/northern-ireland-public-services-ombudsman.md) where applicable |

The times above are observations dated 2026-08-07. They are deliberately not
combined into a universal reporting rule.

## Evidence, authority and dependency record

For every step retain the responsible authority, provider role, jurisdiction,
source identity, observation time, rule used, synthetic evidence supplied,
outcome, limitations and next redress route. The council is the public
authority in each selected local example. Delivery may involve a contractor:
Belfast's route names Bryson Recycling for a specified service, and England's
ombudsman guidance says council accountability remains when a contractor
delivers the service. No unsupported provider identity is inferred elsewhere.

## Acceptance questions

- Can the graph identify the responsible authority and evidence for each
  synthetic local context?
- Can it explain what made the event reportable or excluded without importing
  another council's rule?
- Can it preserve the report outcome and route an unresolved problem through
  the council complaint process to the correct external body?
- Can it show which claims are official, normalized or editorial examples and
  when their evidence was observed?
