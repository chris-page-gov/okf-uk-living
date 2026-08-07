---
type: "Service Family"
title: "Register a death"
description: "Normalized family for certification or investigation handoff, jurisdiction-specific death registration and its official output."
status: "implemented"
assertion_status: "normalized"
jurisdiction: "nation-specific"
observed_at: "2026-08-07"
sources:
  - id: "bereavement-source-register"
    title: "Death, bereavement and estate linked-reference register"
    resource: "../source/death-bereavement-estate.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Register a death

This normalized family preserves the certification or investigation input,
qualified informant, registering authority, jurisdiction, observation time and
registration outputs. It does not turn similar labels into one UK process.

The selected implementations are separate
[England and Wales](england-wales-death-registration.md),
[Scotland](scotland-death-registration.md) and
[Northern Ireland](northern-ireland-death-registration.md) routes. The current
registrar, medical or investigation authority decides a real case.
