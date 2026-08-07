# Evaluation

Planned evaluation assets:

- at least 100 competency questions;
- executable Explorer journeys for overview, search, graph, links, timeline,
  type, resources and narrative views;
- four-nation and local-jurisdiction comparison cases;
- ordinary, exception, appeal and degraded-source paths;
- accessibility and plain-language review; and
- provenance checks that distinguish official, normalized, inferred and
  editorial-example assertions.

The first executable boundary is the set of three
[vertical-slice fixture contracts](fixtures/README.md). They define synthetic
ordinary and exception journeys and are validated locally against the draft
domain profile. The owner approved this boundary on 2026-08-07.

The first [integrated three-slice Explorer review](reviews/integrated-three-slice-2026-08-07.md)
was executed locally on 2026-08-07 against the exact consumer recorded under
[`compatibility/`](compatibility/README.md). Reader and query journeys passed,
but relationship provenance, node build provenance, browser-renderable source
handoffs and licence-notice verification remain open findings. The review and
compatibility gates are therefore not yet passed.

Contract validation is not domain validation, and a local Explorer result is
not publication authorization.
