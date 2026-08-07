---
type: "Service Family"
title: "Learn to drive a car"
description: "Normalized family joining provisional entitlement, supervised learning, tests and full-licence output."
status: "implemented"
assertion_status: "normalized"
jurisdiction: "great-britain-or-northern-ireland"
observed_at: "2026-08-07"
sources:
  - id: "driving-speeding-source-register"
    title: "Learning-to-drive and speeding linked-reference register"
    resource: "../source/learning-to-drive-speeding.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Learn to drive a car

This normalized family connects provisional entitlement, lawful supervised
practice, theory test, practical test and full-licence output. It has separate
[Great Britain](great-britain-learn-to-drive-car.md) and
[Northern Ireland](northern-ireland-learn-to-drive-car.md) implementations.
Their providers, residency conditions, learner rules, evidence and licence
handoffs are not treated as interchangeable.

An optional [driving instructor](../organisations/driving-instructor.md), a
suitable vehicle and applicable [motor insurance](../organisations/motor-insurer.md)
are private dependencies around public licensing and testing. Neither buying a
lesson nor holding a policy establishes a public entitlement.

The [ontology module](../ontology/learning-to-drive-speeding.md) and
[synthetic journey](../journeys/learning-to-drive-speeding.md) preserve the
ordered evidence outputs without deciding whether a real person may drive.
