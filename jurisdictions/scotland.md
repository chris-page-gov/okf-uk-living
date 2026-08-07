---
type: "Jurisdiction Context"
title: "Scotland context"
description: "Scotland applicability context for selected waste, driving, registration, notification, prosecution and confirmation routes."
status: "observed"
assertion_status: "normalized"
observed_at: "2026-08-07"
sources:
  - id: "edinburgh-missed-bin"
    title: "Delays to rubbish and recycling collections"
    resource: "https://www.edinburgh.gov.uk/bin-collection-days/delays-rubbish-recycling-collections"
    author: "organisation:city-of-edinburgh-council"
    observed_at: "2026-08-07"
  - id: "govuk-first-provisional-licence"
    title: "Apply for your first provisional driving licence"
    resource: "https://www.gov.uk/apply-first-provisional-driving-licence"
    author: "organisation:driver-and-vehicle-licensing-agency"
    observed_at: "2026-08-07"
  - id: "copfs-prosecution-code"
    title: "Prosecution Code"
    resource: "https://www.copfs.gov.uk/publications/prosecution-code/html/"
    author: "organisation:crown-office-and-procurator-fiscal-service"
    observed_at: "2026-08-07"
  - id: "nrs-registering-a-death"
    title: "Registering a death"
    resource: "https://www.nrscotland.gov.uk/registration/registering-a-death"
    author: "organisation:national-records-of-scotland"
    observed_at: "2026-08-07"
  - id: "scotcourts-confirmation"
    title: "Guide to dealing with a deceased's estate in Scotland"
    resource: "https://www.scotcourts.gov.uk/taking-action/dealing-with-a-deceaseds-estate-in-scotland/guide-to-dealing-with-a-deceaseds-estate-in-scotland"
    author: "organisation:scottish-courts-and-tribunals-service"
    observed_at: "2026-08-07"
---

# Scotland context

## Missed rubbish collection

The implemented Scotland example is the
[Edinburgh missed-bin route](../services/edinburgh-missed-bin-collection.md),
provided by [The City of Edinburgh Council](../organisations/city-of-edinburgh-council.md).
Its rules are not generalized to another Scottish council.

The selected external complaint route is the
[Scottish Public Services Ombudsman](../organisations/scottish-public-services-ombudsman.md),
after the relevant local complaint process and subject to current acceptance.

## Learning to drive and speeding

The selected ordinary route is the
[Great Britain car-learning route](../services/great-britain-learn-to-drive-car.md),
where DVLA licensing and DVSA testing apply in Scotland. The speeding exception
uses the [Great Britain notice route](../services/great-britain-speeding-notice.md)
but then follows the
[Scottish prosecution and court route](../services/scotland-speeding-prosecution-route.md).
The England and Wales single justice process is explicitly not imported.

## Death, notification and estate administration

The selected route uses [Scottish death registration](../services/scotland-death-registration.md),
[Tell Us Once](../services/tell-us-once.md) within its current residence and
coverage rules, and [Scottish confirmation](../services/scotland-confirmation-estate.md).
The observed eight-day registration rule and confirmation terminology remain
Scottish and are not generalized across the UK.
