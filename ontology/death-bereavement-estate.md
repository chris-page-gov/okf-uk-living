---
type: "Ontology Module"
title: "Death, bereavement and estate model"
description: "Governed normalized concepts for certification, investigation, registration, notification coverage, estate authority and private dependencies."
status: "implemented"
assertion_status: "normalized"
observed_at: "2026-08-07"
sources:
  - id: "bereavement-source-register"
    title: "Death, bereavement and estate linked-reference register"
    resource: "../source/death-bereavement-estate.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Death, bereavement and estate model

This module supports the synthetic
[death and bereavement journey](../journeys/death-bereavement-estate.md). It
keeps public evidence handoffs, authority and private dependencies distinct.

| Concept | Normalized meaning | Boundary |
|---|---|---|
| certification or investigation output | MCCD, coroner notification, Procurator Fiscal outcome or other officially identified input to registration | The bundle does not decide cause of death or whether investigation is required |
| informant role | Person qualified under the selected registration route to supply information | Synthetic role only; qualification is checked by the registrar |
| registration output | Jurisdiction-specific register entry, certificate or funeral handoff | Similar certificates are not assumed interchangeable for every consumer |
| notification coverage record | Bodies covered and not covered by a service at the observation time | Tell Us Once coverage is not extended to Northern Ireland or private bodies |
| manual notification record | Synthetic record of body, evidence, channel, time and result | It does not prove acceptance or close an account |
| grant of representation | England and Wales or Northern Ireland court evidence of authority within its route | Need, applicant and effect remain case-specific |
| confirmation | Scottish court document giving an executor authority to uplift and administer estate property | It remains Scottish terminology and authority, not an identity mapping to probate |
| estate inventory | Synthetic list of assets, debts, holders, values and evidence state | It is not a legal or tax valuation |
| private dependency | Funeral provider, account provider or practitioner outside the public authority chain | Selection, contract, price, evidence and complaint route remain provider-specific |
| redress handoff | Registrar correction, service support, body complaint, court process or professional advice | Grounds, deadline, acceptance and result remain current and case-specific |

## Evidence lineage

The certification or investigation output can support registration. A
registration output can support a notification service, funeral handoff and
later evidence request. A will, death certificate, estate inventory and tax
information can support a court-authority application, but no one artefact is
treated as sufficient in every jurisdiction or case.

Data retains only synthetic references, dates, roles and outcomes. Information
adds the correct authority, jurisdiction and observation time. Knowledge
records supported handoffs and unresolved exceptions. The ontology provides
the normalized concepts above without presenting generated links as official.
