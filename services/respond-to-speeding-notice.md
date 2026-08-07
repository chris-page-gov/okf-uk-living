---
type: "Service Family"
title: "Respond to a speeding notice"
description: "Normalized family for identifying a speeding notice, supplying driver information and following its disposal or court branch."
status: "implemented"
assertion_status: "normalized"
jurisdiction: "notice-and-court-specific"
observed_at: "2026-08-07"
sources:
  - id: "driving-speeding-source-register"
    title: "Learning-to-drive and speeding linked-reference register"
    resource: "../source/learning-to-drive-speeding.v1.yaml"
    author: "organisation:okf-uk-living"
    observed_at: "2026-08-07"
---

# Respond to a speeding notice

This normalized family distinguishes a notice of intended prosecution, a
driver-information request, a later fixed or conditional offer, and a criminal
court document. It does not decide whether an allegation is valid, who drove,
whether a course or fixed penalty will be offered, what plea to enter, or what
a court will decide.

The selected implementations are the
[Great Britain notice route](great-britain-speeding-notice.md), its separate
[England and Wales court branch](england-wales-speeding-court-route.md) and
[Scottish prosecution branch](scotland-speeding-prosecution-route.md), plus the
[Northern Ireland notice and court route](northern-ireland-speeding-notice.md).

For a real document, its issuer, reference, recipient role, alleged event,
response channel and deadline control. The bundle hands disputed facts,
identity uncertainty, defence, plea and appeal questions to the current
official route and qualified legal advice.
