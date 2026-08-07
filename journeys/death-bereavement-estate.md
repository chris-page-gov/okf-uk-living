---
type: "Citizen Journey"
title: "Death and bereavement through estate administration"
description: "Synthetic journey through certification or investigation, death registration, notification, funeral dependencies and jurisdiction-specific estate authority."
status: "implemented"
assertion_status: "editorial-example"
synthetic: true
jurisdiction: "england-wales-scotland-or-northern-ireland"
observed_at: "2026-08-07"
sources:
  - id: "bereavement-source-register"
    title: "Death, bereavement and estate linked-reference register"
    resource: "../source/death-bereavement-estate.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Death and bereavement through estate administration

This is a synthetic `editorial-example`. It contains no real death, person,
will, account, asset, debt, tax return or beneficiary. It explains evidence
and authority handoffs; it does not decide cause of death, informant status,
notification sufficiency, probate or confirmation need, applicant authority,
tax, insolvency, distribution or entitlement.

The journey exercises the [bereavement ontology](../ontology/death-bereavement-estate.md),
the [registration](../services/register-a-death.md),
[notification](../services/notify-organisations-after-a-death.md) and
[estate](../services/administer-an-estate.md) families, and the
[bounded evidence set](../evidence/death-bereavement-estate-sources.md).

## Ordinary path

1. **Choose the jurisdiction.** Use the place of death, residence and estate
   context to select official routes; do not infer a national process from a
   common label.
2. **Retain the certification or investigation boundary.** Record only the
   synthetic fact that an MCCD or authority output is available, or that a
   coroner or Procurator Fiscal process controls the next step.
3. **Register the death.** Supply the selected registrar's required synthetic
   information and retain the official registration outputs and observation
   time.
4. **Record the funeral dependency.** The registration or investigation
   output can feed a [funeral provider](../organisations/funeral-provider.md),
   but the provider is not the public registration authority.
5. **Notify covered and uncovered bodies.** Use Tell Us Once only inside its
   current coverage. Create separate synthetic notification records for every
   uncovered public or [private organisation](../organisations/private-organisation-after-death.md).
6. **Obtain estate authority if required.** Preserve the will or no-will
   context, inventory, court, tax handoff and exact jurisdictional document.
7. **Administer without deciding.** Trace assets, debts, tax and later
   distribution as unresolved or officially evidenced states; use an
   [estate practitioner](../organisations/estate-practitioner.md) where the
   current route or complexity requires professional help.

| Registration context | Official route | Authority and time boundary |
|---|---|---|
| [England](../jurisdictions/england.md) and [Wales](../jurisdictions/wales.md) | [England and Wales registration](../services/england-wales-death-registration.md) | The routed [local register office](../organisations/local-register-office-england-wales.md), current service and any coroner instructions control; no Scottish or NI deadline is imported |
| [Scotland](../jurisdictions/scotland.md) | [Scottish registration](../services/scotland-death-registration.md) | The [Scottish registration authority](../organisations/scottish-registration-authority.md) uses the observed eight-day rule and MCCD route; [COPFS](../organisations/crown-office-and-procurator-fiscal-service.md) controls referred investigations |
| [Northern Ireland](../jurisdictions/northern-ireland.md) | [Northern Ireland registration](../services/northern-ireland-death-registration.md) | [GRONI](../organisations/general-register-office-northern-ireland.md) and the district registrar use the observed five-day rule except for the [Coroners Service](../organisations/coroners-service-northern-ireland.md) boundary |

## Notification exception path

| Residence or coverage state | Route | Remaining work |
|---|---|---|
| Person lived in England, Scotland or Wales and service conditions are met | [Tell Us Once](../services/tell-us-once.md) through the [Tell Us Once service](../organisations/tell-us-once-service.md) | Retain the observed covered-body list and notify every uncovered public or private organisation separately |
| Person lived in Northern Ireland | [Northern Ireland manual notifications](../services/northern-ireland-death-notifications.md) | Use the [Northern Ireland Bereavement Service](../organisations/northern-ireland-bereavement-service.md) for its benefit-office scope and contact other bodies separately |
| Tell Us Once unavailable, no reference supplied, or a body is uncovered | Body-specific current route | Record evidence, channel, time, result and complaint boundary without claiming successful data sharing |

Tell Us Once is not treated as a universal UK notification service. Its
absence or limited coverage never becomes evidence that no notification is
required.

## Estate-authority and exception path

| Estate jurisdiction | Authority route | Exception boundary |
|---|---|---|
| England and Wales | [England and Wales probate](../services/england-wales-probate-estate.md) administered by [HMCTS](../organisations/hm-courts-and-tribunals-service.md), with [HMRC](../organisations/hm-revenue-and-customs.md) tax dependencies | Will and no-will applicants, whether a grant is needed, caveat, dispute, debt and tax remain current and case-specific |
| Scotland | [Scottish confirmation](../services/scotland-confirmation-estate.md) administered by [Scottish Courts](../organisations/scottish-courts-and-tribunals-service.md), with HMRC tax dependencies | Confirmation, inventory, small or large estate and testate or intestate branches retain Scottish terminology and advice boundaries |
| Northern Ireland | [Northern Ireland probate](../services/northern-ireland-probate-estate.md) administered by [NICTS](../organisations/northern-ireland-courts-and-tribunals-service.md), with HMRC tax dependencies | Grant, letters of administration, no-will and debt branches remain Northern Ireland routes |

These are not combined into one UK estate process. Disputed authority,
insolvency, missing evidence, an unknown will, cross-border property or a
missed court deadline is handed to the current official court, tax or
qualified professional route.

## Acceptance questions

- Can the graph identify the certification or investigation output that feeds
  the selected registrar without deciding cause of death?
- Can it show Tell Us Once coverage and every uncovered notification without
  implying that data sharing succeeded?
- Can it distinguish probate in England and Wales, confirmation in Scotland
  and probate in Northern Ireland, including their court and HMRC roles?
- Can it distinguish public authorities from funeral, account and
  professional dependencies while retaining evidence and redress boundaries?
