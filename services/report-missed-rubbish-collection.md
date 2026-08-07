---
type: "Service Family"
title: "Report a missed rubbish collection"
description: "Normalized service family for reporting an expected local household waste collection that did not occur."
status: "implemented"
assertion_status: "normalized"
jurisdiction: "local-authority-specific"
observed_at: "2026-08-07"
sources:
  - id: "missed-rubbish-source-register"
    title: "Missed rubbish collection linked-reference register"
    resource: "../source/missed-rubbish-collection.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Report a missed rubbish collection

This normalized family groups local routes for reporting a scheduled household
waste or recycling collection that was not completed. It does not assert a
single UK provider, deadline, acceptance rule, remedy or complaint body.

The implemented examples are
[Coventry](coventry-missed-bin-collection.md),
[Edinburgh](edinburgh-missed-bin-collection.md),
[Cardiff](cardiff-missed-collection.md) and
[Belfast](belfast-missed-bin-collection.md). Their locally official rules stay
on those records. The [ontology module](../ontology/missed-rubbish-collection.md)
and [synthetic journey](../journeys/missed-rubbish-collection.md) describe the
shared editorial model.

## Normalized interaction boundary

1. Identify the council responsible for the address.
2. Check the scheduled collection, local presentation conditions and any
   disruption notice.
3. Use the locally evidenced channel and timing rule only when its conditions
   are met.
4. Preserve the report outcome or rejection reason.
5. If the service problem remains unresolved, use the council complaint route
   before any jurisdiction-appropriate external body.

A delivery contractor can be a required operational dependency without
becoming the accountable authority. The England redress evidence expressly
states that councils remain accountable for contractor-delivered waste
services; no equivalent contractor claim is inferred for the other examples.
