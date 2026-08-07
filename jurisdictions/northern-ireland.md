---
type: "Jurisdiction Context"
title: "Northern Ireland context"
description: "Northern Ireland applicability context for selected waste, driving, registration, manual notification and probate routes."
status: "observed"
assertion_status: "normalized"
observed_at: "2026-08-07"
sources:
  - id: "belfast-missed-bin"
    title: "Report a missed bin collection"
    resource: "https://www.belfastcity.gov.uk/bins-recycling-environment/bins-boxes-collections/report-request-order-bin-box/missed-bin-collection"
    author: "organisation:belfast-city-council"
    observed_at: "2026-08-07"
  - id: "nidirect-provisional-licence"
    title: "Apply for a provisional driving licence online"
    resource: "https://www.nidirect.gov.uk/services/apply-provisional-driving-licence-online"
    author: "organisation:driver-and-vehicle-agency-northern-ireland"
    observed_at: "2026-08-07"
  - id: "nidirect-speeding-penalties"
    title: "Speed limits and penalties for breaking them"
    resource: "https://www.nidirect.gov.uk/articles/speed-limits-and-penalties-breaking-them"
    author: "organisation:department-for-infrastructure-northern-ireland"
    observed_at: "2026-08-07"
  - id: "nidirect-registering-a-death"
    title: "Registering a death with the district registrar"
    resource: "https://www.nidirect.gov.uk/articles/registering-death-district-registrar"
    author: "organisation:general-register-office-northern-ireland"
    observed_at: "2026-08-07"
  - id: "nidirect-who-to-tell"
    title: "Who to tell about a death"
    resource: "https://www.nidirect.gov.uk/articles/who-tell-about-death"
    author: "organisation:northern-ireland-executive"
    observed_at: "2026-08-07"
  - id: "nidirect-apply-probate"
    title: "Apply for probate"
    resource: "https://www.nidirect.gov.uk/services/apply-probate"
    author: "organisation:northern-ireland-courts-and-tribunals-service"
    observed_at: "2026-08-07"
---

# Northern Ireland context

## Missed rubbish collection

The implemented Northern Ireland example is the
[Belfast missed-bin route](../services/belfast-missed-bin-collection.md),
provided by [Belfast City Council](../organisations/belfast-city-council.md).
No Great Britain council rule is carried into this route.

The selected external complaint route is the
[Northern Ireland Public Services Ombudsman](../organisations/northern-ireland-public-services-ombudsman.md),
normally after the council process and final response.

## Learning to drive and speeding

The selected ordinary route is the independent
[Northern Ireland DVA car-learning route](../services/northern-ireland-learn-to-drive-car.md).
The exception uses the independently sourced
[Northern Ireland speeding notice and court route](../services/northern-ireland-speeding-notice.md).
DVLA/DVSA services, Great Britain section 172 and the England and Wales or
Scottish court branches are not silently substituted.

## Death, notification and estate administration

The selected route uses [Northern Ireland death registration](../services/northern-ireland-death-registration.md),
the independently sourced [manual notification route](../services/northern-ireland-death-notifications.md)
and [Northern Ireland probate](../services/northern-ireland-probate-estate.md).
Tell Us Once is unavailable for a person living in Northern Ireland, so it is
not substituted for the Bereavement Service or body-specific notifications.
