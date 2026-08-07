---
type: "Ontology Module"
title: "Missed rubbish collection model"
description: "Governed normalized concepts for expected collections, reports, exclusions, outcomes and redress."
status: "implemented"
assertion_status: "normalized"
observed_at: "2026-08-07"
sources:
  - id: "missed-rubbish-source-register"
    title: "Missed rubbish collection linked-reference register"
    resource: "../source/missed-rubbish-collection.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Missed rubbish collection model

This module defines a small editorial vocabulary for the
[missed-rubbish journey](../journeys/missed-rubbish-collection.md). It groups
different local terms without asserting that their rules or services are
identical.

## Concepts

| Concept | Normalized meaning | Boundary |
|---|---|---|
| expected collection | A collection identified by the responsible authority's current schedule for the place and waste type | A remembered or typical day is not enough |
| observed non-collection | A synthetic observation that the expected collection did not occur | It does not establish fault or reportability |
| reportable missed collection | An expected collection plus observed non-collection that meets the selected local route's timing and presentation conditions | The classification is local and time-sensitive |
| exclusion or rejection | A sourced reason why the missed-collection route is unavailable or a report was not accepted | Reasons must not be invented or copied between councils |
| missed-collection report | The minimum synthetic facts submitted through an official local channel | It is distinct from a formal complaint |
| service outcome | An acknowledgement, return collection, explanation, rejection or unresolved state recorded after a report | No remedy is promised without evidence |
| council complaint | A complaint made after the service issue has first been reported where the local process requires that sequence | Its deadlines and stages are local |
| external complaint | A complaint to the jurisdiction-appropriate ombudsman after applicable local stages | Scope, acceptance and outcome remain with that body |

## From data to ontology

- **Data** records the synthetic scheduled date, waste type, presentation facts,
  observation and report reference.
- **Information** combines those values with the responsible council's current
  service page and jurisdiction.
- **Knowledge** records why the selected local route appears available,
  excluded or unresolved and attaches its evidence and observation time.
- **Ontology** supplies the normalized concepts above so the four examples can
  be compared without erasing their local differences.

## Governed relations

The [normalized service family](../services/report-missed-rubbish-collection.md)
has local service routes; each route has one responsible council in this slice,
applies within its declared local jurisdiction, is supported by the
[evidence set](../evidence/missed-rubbish-collection-sources.md), and may lead
from a service report to a council complaint and then an external complaint.

These are normalized relations. The service records retain official facts and
sources. Missing facts remain unknown, and a link never turns a normalized or
editorial assertion into an official one.
