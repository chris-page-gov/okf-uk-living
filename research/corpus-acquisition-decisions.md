---
type: "Research Decision"
title: "Approved corpus acquisition and review decisions"
description: "Owner-approved service-family denominator, local coverage, identifier, health-permission, regulator, redress and specialist-review decisions."
status: "approved"
timestamp: "2026-08-07T00:00:00+01:00"
generated:
  by: "ai:openai-codex"
  at: "2026-08-07T00:00:00+01:00"
sources:
  - id: "ons-geography-codes"
    title: "ONS names, codes and lookups"
    resource: "https://www.ons.gov.uk/methodology/geography/geographicalproducts/namescodesandlookups"
    author: "organisation:office-for-national-statistics"
    observed_at: "2026-08-07"
  - id: "nhs-organisation-data-service"
    title: "NHS England Organisation Data Service"
    resource: "https://digital.nhs.uk/services/organisation-data-service"
    author: "organisation:nhs-england"
    observed_at: "2026-08-07"
---

# Approved corpus acquisition and review decisions

Decision date: 2026-08-07

Decision owner: `owner:chris-page-gov`

Machine-readable decisions:

- [293-family denominator](../source/service-family-denominator.v1.yaml)
- [corpus acquisition policy](../profiles/corpus-acquisition-policy.v1.yaml)
- [external reference inventory](../source/exhaustive-reference-inventory.v1.yaml)

## 1. Service-family denominator

The approved denominator contains 293 uniquely named canonical service
families across all 24 life-course domains. It is inside the planned 250–400
range and is split into three acquisition waves:

| Wave | Families | Purpose |
|---|---:|---|
| 1 | 96 | Core life events, common routes and extensions of the proven slices |
| 2 | 96 | Evidence, exceptions, redress and locally delivered routes |
| 3 | 101 | Specialist, cross-border and private-dependency handoffs |

The names are normalized planning identifiers, not official assertions. The
decision authorizes staged leaf-reference registration against those names. It
does not authorize snapshots, copied source content, unsupported equivalence,
personalized decisions, corpus publication or CI.

## 2. Local coverage and identifiers

The approved local model has two layers:

1. an exhaustive registry of every active principal authority and functional
   body in the approved official denominators; and
2. one current leaf route for each governed structural archetype plus every
   known material exception.

The project will not copy the same family across every council and call that
meaningful coverage. A claim about a named place still requires the responsible
provider's current page.

The primary administrative-geography identifier is the dated nine-character
GSS code published through the ONS names, codes, lookups and history products.
Every geography record retains its type, official name, vintage or effective
date, source and observation date. ODS codes identify health and social-care
organisations where the declared ODS coverage applies; source-native IDs are
retained elsewhere. Postcodes may be used transiently to discover an authority
but are never stored and never become stable service identity.

## 3. Health permissions

The decision is to keep all four national health families manual,
link-and-original-summary only. No provider-permission request is made now.
England's OGL terms do not require this conservative limit, but using the same
project policy avoids accidental reuse of excluded content. NHS inform's
no-scraping term, NHS 111 Wales copyright boundary and HSCNI non-commercial
conditions remain controlling limitations.

Permission will be reconsidered only if a named acquisition wave genuinely
requires automated directory or content extraction. No medical material is
converted into individual advice or eligibility logic.

## 4. Private dependencies and redress

Private dependencies now use a regulator-first rule. Discovery starts with a
statutory regulator, mandatory register, licensing authority or statutory
redress body. A named provider is added only when a journey requires that
specific provider and the selection basis is recorded. Commercial rankings,
marketing copy and implied endorsement are prohibited.

The redress taxonomy is:

1. provider internal review or complaint;
2. statutory reconsideration or review;
3. tribunal or specialist appeal;
4. regulator or ombudsman; and
5. court or judicial review.

This is not a universal procedure. Each family must cite its actual sequence,
prerequisites, jurisdiction and deadlines.

## 5. Review nominations

`owner:chris-page-gov` is nominated as editorial and release-gate coordinator.
Three specialist roles are approved:

- a suitably qualified UK legal or public-policy procedure reviewer;
- a currently registered clinician or clinical-safety specialist; and
- the authoritative service owner, policy specialist or equivalent subject
  reviewer for eligibility, evidence, fee, deadline and exception claims.

The legal and clinical roles are deliberately not assigned to an invented or
unconsenting person. Their individual appointments remain visible blockers for
production-grade legal and medical claims. Educational examples may proceed
only with normalized or `editorial-example` status and explicit limitations.

## 6. Explorer large-corpus projection

`okf-explorer-large-corpus.v1` is conditionally approved. The approval becomes
effective only when `REV-001` through `REV-004` are closed by local browser
evidence for relationship authority, node build provenance, rendered source
handoffs and the first-class licence/notice surface. The projection must expose
colour facets for life-course domain, acquisition wave, delivery scope,
jurisdiction, implementation status, assertion status and rights state.

This conditional decision does not authorize GitHub Pages or any public URL.
