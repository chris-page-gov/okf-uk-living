---
type: "Citizen Journey"
title: "Learning to drive through a speeding exception"
description: "Synthetic journey from provisional entitlement through testing and licensing into a jurisdiction-specific speeding-notice exception."
status: "implemented"
assertion_status: "editorial-example"
synthetic: true
jurisdiction: "great-britain-or-northern-ireland"
observed_at: "2026-08-07"
sources:
  - id: "driving-speeding-source-register"
    title: "Learning-to-drive and speeding linked-reference register"
    resource: "../source/learning-to-drive-speeding.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Learning to drive through a speeding exception

This journey is a synthetic `editorial-example`. It contains no real licence,
vehicle, policy, notice, alleged offence or court case. It explains routes and
evidence handoffs; it does not decide fitness to drive, entitlement, insurance
cover, driver identity, liability, course eligibility, plea, penalty or appeal.

The journey exercises the
[learning and speeding ontology](../ontology/learning-to-drive-speeding.md),
the [learning service family](../services/learn-to-drive-car.md), the
[speeding-response family](../services/respond-to-speeding-notice.md) and the
[bounded evidence set](../evidence/learning-to-drive-speeding-sources.md).

## Ordinary learning path

1. **Choose the licensing jurisdiction.** A synthetic residence and intended
   car category select either the GB route or the independently sourced
   Northern Ireland route.
2. **Obtain provisional entitlement.** Retain the application authority,
   category, official output, validity time and any refusal or correction
   route. Do not infer entitlement from an application alone.
3. **Record a supervised practice episode.** Check the current supervisor,
   vehicle, plate and insurance conditions for that jurisdiction. Record only
   synthetic evidence and no policy details.
4. **Take the theory test.** Retain the test provider, booking reference,
   output, category and time. A pass becomes evidence for the practical stage
   only under the selected route's current rules.
5. **Take the practical test.** Retain the official pass, fail, cancellation or
   reschedule output without predicting it. A challenge about test conduct
   follows the test provider's official complaint or court boundary.
6. **Complete the licence handoff.** Route a practical pass to DVLA in Great
   Britain or DVA in Northern Ireland, preserving whether the examiner arranged
   the upgrade or a separate claim is required.

| Route | Licensing and testing authorities | Selected distinctions |
|---|---|---|
| [Great Britain](../services/great-britain-learn-to-drive-car.md) | [DVLA](../organisations/driver-and-vehicle-licensing-agency.md) issues the provisional/full licence; [DVSA](../organisations/driver-and-vehicle-standards-agency.md) supplies tests | Great Britain residence boundary; theory pass precedes practical booking; the pass output can feed the DVLA licence handoff |
| [Northern Ireland](../services/northern-ireland-learn-to-drive-car.md) | [DVA](../organisations/driver-and-vehicle-agency-northern-ireland.md) supplies licensing and tests | Independently sourced learner conditions include the Northern Ireland plate and 45 mph boundary; DVA receives the pass handoff |

The optional [driving instructor](../organisations/driving-instructor.md),
vehicle provider and compulsory [motor insurer](../organisations/motor-insurer.md)
remain private dependencies. A provider sale or policy document is not public
authority evidence of entitlement.

## Speeding-notice exception path

1. **Identify the document.** Retain its title, issuer, reference, recipient
   role, jurisdiction, alleged date, place and vehicle. Do not treat the
   recipient as the driver by inference.
2. **Identify the information request.** Separate the notice of intended
   prosecution from any driver-information requirement. Use the actual
   document, current official source and applicable law for the duty, deadline
   and response channel.
3. **Record the synthetic response.** Preserve what was supplied, when and to
   whom. A response record is not a legal-sufficiency decision.
4. **Classify the later document.** Distinguish a course invitation, fixed or
   conditional offer, prosecution document and court notice. Never predict
   which will be offered.
5. **Follow the correct court boundary.** Use England and Wales, Scotland or
   Northern Ireland guidance and hand disputed circumstances to qualified
   legal advice. Retain the official outcome and only the redress route the
   current court process supports.

| Enforcement context | Official route | Time and authority boundary | Court and redress boundary |
|---|---|---|---|
| [England](../jurisdictions/england.md) and [Wales](../jurisdictions/wales.md) | [GB notice response](../services/great-britain-speeding-notice.md) from the [notice issuer](../organisations/notice-issuing-police-force-great-britain.md) | GOV.UK states 28 days for the section 172 return; the actual notice and current Great Britain law control | If an [HMCTS](../organisations/hm-courts-and-tribunals-service.md) single justice notice is used, the observed general response period is 21 days; review or appeal follows the [England and Wales court route](../services/england-wales-speeding-court-route.md) |
| [Scotland](../jurisdictions/scotland.md) | [GB notice response](../services/great-britain-speeding-notice.md), followed by the [Scottish prosecution route](../services/scotland-speeding-prosecution-route.md) | The actual police notice controls the response; England and Wales single justice procedure is not imported | [COPFS](../organisations/crown-office-and-procurator-fiscal-service.md) decides action and may use a conditional offer for specified road traffic offences; current Scottish court guidance governs appeal |
| [Northern Ireland](../jurisdictions/northern-ireland.md) | [NI speeding route](../services/northern-ireland-speeding-notice.md) involving [NIRSP](../organisations/northern-ireland-road-safety-partnership.md) | The registered keeper identifies the driver within the time allotted on the NI notice; GB section 172 is not substituted | A conditional offer can be accepted or a hearing requested under the notice terms; [NICTS](../organisations/northern-ireland-courts-and-tribunals-service.md) and NI appeal guidance govern the later process |

The observed 28-day and 21-day statements are not combined into one UK
deadline. Notice-specific and court-specific instructions always take priority.

## Exception handling

- **Wrong licensing jurisdiction:** stop and select DVLA/DVSA or DVA from the
  residence and service evidence; do not copy an application or test output.
- **Missing or expired evidence:** retain the missing provisional, theory-pass,
  insurance or identity condition and use the official correction or fresh
  application route without deciding entitlement.
- **Test failure or conduct complaint:** retain the result and provider route;
  do not turn a complaint into a changed result.
- **Issuer or recipient uncertainty:** contact the authority on the notice or
  obtain legal advice; never guess the driver.
- **Disputed allegation or disposal:** preserve the document and deadline, and
  hand the question to the appropriate enforcement or court process.
- **Missed court document or appeal question:** use only the jurisdiction's
  current reopening, review or appeal guidance and seek legal advice.

## Acceptance questions

- Can each theory and practical output be traced to the next licensing stage,
  authority, category and validity time?
- Can the graph distinguish a private instructor, insurer and vehicle provider
  from DVLA, DVSA and DVA?
- Can it identify the notice recipient's next official step and deadline
  without identifying the driver or deciding legal sufficiency?
- Can it keep Great Britain and Northern Ireland licensing separate, then
  distinguish England and Wales, Scotland and Northern Ireland court routes?
