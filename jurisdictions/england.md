---
type: "Jurisdiction Context"
title: "England context"
description: "England applicability context for selected local waste, Great Britain driving and England-and-Wales court routes."
status: "observed"
assertion_status: "normalized"
observed_at: "2026-08-07"
sources:
  - id: "coventry-missed-bin"
    title: "Missed bin collections"
    resource: "https://www.coventry.gov.uk/missedbin"
    author: "organisation:coventry-city-council"
    observed_at: "2026-08-07"
  - id: "govuk-first-provisional-licence"
    title: "Apply for your first provisional driving licence"
    resource: "https://www.gov.uk/apply-first-provisional-driving-licence"
    author: "organisation:driver-and-vehicle-licensing-agency"
    observed_at: "2026-08-07"
  - id: "govuk-single-justice-procedure"
    title: "Single justice procedure notices"
    resource: "https://www.gov.uk/single-justice-procedure-notices"
    author: "organisation:hm-courts-and-tribunals-service"
    observed_at: "2026-08-07"
---

# England context

## Missed rubbish collection

The implemented England example is the
[Coventry missed-bin route](../services/coventry-missed-bin-collection.md),
provided by [Coventry City Council](../organisations/coventry-city-council.md).
It is one local observation, not a denominator for all English councils.

After the council complaint process, the selected external route is the
[Local Government and Social Care Ombudsman](../organisations/local-government-and-social-care-ombudsman.md),
subject to that body's current scope and exhaustion rules.

## Learning to drive and speeding

The selected ordinary route is the
[Great Britain car-learning route](../services/great-britain-learn-to-drive-car.md),
where DVLA licensing and DVSA testing apply in England. The selected speeding
exception begins with the
[Great Britain notice route](../services/great-britain-speeding-notice.md) and,
if the case reaches the relevant magistrates process, uses the
[England and Wales court route](../services/england-wales-speeding-court-route.md).
No Scottish or Northern Ireland court process is inferred.
