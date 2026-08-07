---
type: "Service Family"
title: "Administer an estate"
description: "Normalized family for obtaining jurisdiction-specific estate authority and tracing assets, debts, tax and distribution boundaries."
status: "implemented"
assertion_status: "normalized"
jurisdiction: "nation-and-estate-specific"
observed_at: "2026-08-07"
sources:
  - id: "bereavement-source-register"
    title: "Death, bereavement and estate linked-reference register"
    resource: "../source/death-bereavement-estate.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Administer an estate

This normalized family distinguishes an England and Wales grant of
representation, Scottish confirmation and a Northern Ireland grant. It also
separates the authority document from later asset, debt, tax and distribution
work.

The implementations are the [England and Wales probate route](england-wales-probate-estate.md),
[Scottish confirmation route](scotland-confirmation-estate.md) and
[Northern Ireland probate route](northern-ireland-probate-estate.md). The bundle
does not decide whether a grant is required, who may apply, tax liability,
insolvency, a dispute or a beneficiary's entitlement.
