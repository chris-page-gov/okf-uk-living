# Authoring and validation

## Concept records

The bundle root is `index.md` and declares `okf_version: "0.2"`. Section
`index.md` files have no frontmatter. Every other concept uses:

```yaml
---
type: Public Service
title: Report a missed rubbish collection
description: Report that a scheduled household waste collection did not occur.
status: draft
generated:
  by: human:author-id
  at: 2026-08-07T12:00:00+01:00
sources:
  - id: official-service-page
    title: Official service page
    resource: https://www.gov.uk/missed-bin-collection
    author: organisation:government-digital-service
    observed_at: 2026-08-07
---
```

Use ordinary Markdown links between local concepts. Link direction is
meaningful: the source record references the target record. The builder emits
these as compatibility relationships; later semantic work will add governed
predicate identifiers and evidence.

## Required domain fields

A service record should eventually declare:

- source-native and local identifiers;
- citizen-facing description and aliases;
- service family and interaction kind;
- relevant life event, situation and user need;
- jurisdiction and geographic coverage;
- responsible provider and other actor roles;
- legal or policy rule where supported;
- requirements and evidence;
- channels, costs, deadlines and validity;
- output and wider outcome;
- review, appeal, complaint and emergency routes;
- assertion status, provenance, observation time and freshness policy; and
- explicit limitations and known omissions.

Unknown is not false. Do not invent missing eligibility, cost, authority,
identity or legal relationships.

## Build and check

Install `requirements-okf.txt`, then run:

```sh
python3 scripts/build_okf_bundle.py
python3 scripts/build_okf_bundle.py --check
python3 scripts/check_okf.py
python3 -m unittest discover -s tests
```

`okf-bundle.json` is reproducible output. Never patch it directly.

## Publication boundary

Local validation does not authorize publication. Complete the domain profile,
source/rights review, evaluation, frozen-candidate assurance and exact deployed
browser journey before sharing a public bundle URL.
