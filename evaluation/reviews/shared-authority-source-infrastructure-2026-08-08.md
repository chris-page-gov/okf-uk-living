---
type: "Evaluation Evidence"
title: "Shared authority and source infrastructure review"
description: "Local deterministic, metadata-only and visible-browser evidence for POP-004."
status: "passed-local"
timestamp: "2026-08-08T00:00:00+01:00"
generated:
  by: "ai:openai-codex"
  at: "2026-08-08T00:00:00+01:00"
---

# Shared authority and source infrastructure review

Review date: 2026-08-08

Delivery item: `POP-004`

Result: **passed for local population infrastructure**

Publication status: local validation only. GitHub Pages was not updated.
Publication requires an explicit owner request.

## Implemented denominator

The reviewed [`authority-registry.v1`](../../source/authority-registry.v1.yaml)
contains:

- 382 principal local-authority areas and normalized actors: 361 May 2026
  local-authority districts plus 21 separately retained December 2024 English
  county areas required for two-tier topology;
- 19 strategic/combined authorities: 15 May 2025 GSS combined-authority areas
  plus four later official source-native authorities;
- 397 dated GSS geographies in total;
- 438 organizations including the local actors, strategic authorities,
  transition bodies and reusable national, regulator and redress identities;
- ten governed regulator/register and redress sector maps; and
- two Surrey shadow bodies explicitly separated from current service delivery
  until the 2027 transfer.

A GSS code identifies an area, not the legal body or service provider. Welsh
labels share identity only when they occur in the same official GSS record or
the publisher explicitly pairs them. LGSL/ESD Services remains optional
mapping vocabulary and does not prove availability.

## Source and rights evidence

The live authority refresh parsed official ONS metadata in memory and retained
only names, identifiers and dates. Seven external infrastructure links have
`source-link-receipt.v1` receipts under
[`evaluation/link-receipts/shared-authority-2026-08-08`](../link-receipts/shared-authority-2026-08-08/).
All seven returned HTTP 200 at the recorded check time. Every receipt states
`response_body_retained: false`.

The rights register now includes dated decisions for the ONS Open Geography
portal, the ONS ArcGIS query service and ESD standards help. Repository use
remains links, identifiers, unprotected facts and original summaries only.
No source response body, geometry or snapshot was acquired or redistributed.

## Deterministic projection

The generated Explorer data plane contains:

- 293 service families;
- 1,434 total concepts, including 397 geographies and 438 organizations;
- 53 typed link-only resources;
- 1,025 provenance-bearing relationships;
- JSON-LD and YAML-LD projections plus the SHACL-style validation report; and
- two 1,000-record hydration chunks for records and static-search results.

Shared identities are reused by dossier relationships. For example,
`Administer an estate` links to the registry HM Courts & Tribunals Service
record rather than a duplicate actor record.

## Local checks

The required `uv run --locked` check sequence and full unit-test discovery
passed. The authority refresh also matched the committed registry when run as
a reviewed live check. Offline validation does not require network access.

## Visible Explorer journeys

The local no-cache Explorer overlay at `127.0.0.1` passed these journeys:

1. overview showed 1,434 concepts, 53 resources and 1,025 relationships;
2. searching `Financial Conduct Authority` returned exactly the shared
   organization and hydrated its full detail card;
3. searching the publisher-paired Welsh alias `Ynys Môn` returned and hydrated
   `Isle of Anglesey` with GSS geography context; and
4. opening `Administer an estate` in Graph exposed the governed `offered-by`
   edge to the shared HM Courts & Tribunals Service identity.

The first browser attempt exposed a malformed one-chunk locator after the
corpus crossed 1,000 records. The generator now shards both record and search
result hydration, and the repeated journeys passed without the error.

## Remaining boundary

This phase supplies shared identity and source-verification infrastructure. It
does not establish that an organization handles a particular family, complete
local leaf routes, appoint specialist reviewers, make the corpus release-grade
or authorize publication. Those claims remain in the eight family packs and
later assurance gates.
