# Changelog

All notable changes to this project are recorded here. Dates use ISO 8601.

## [Unreleased]

### Added

- Planned domain profile, source inventory and three vertical-slice fixtures.
- Delivery planning and tracking ledgers with lockstep documentation rules.
- Pull-request publication-status template and explicit manual GitHub Pages
  gate.
- Locked `uv` project environment and local-only validation commands.
- Draft `okf-domain-profile.v1` machine contract and human review handoff.
- Three synthetic vertical-slice fixture contracts covering ordinary and
  exception journeys for rubbish collection, driving enforcement and death.
- Executable profile and fixture-contract validation with unit tests.
- Bounded missed-rubbish source register containing 13 official linked
  references and no acquired snapshots.
- First vertical slice with four local service routes, four jurisdiction
  contexts, responsible councils, external-redress bodies, a normalized
  service family and ontology module, and a synthetic journey.
- Semantic slice validation and regression tests for authority, jurisdiction,
  provenance, assertion status and anti-generalization boundaries.
- Bounded learning-to-drive and speeding register with 20 official linked
  references and no acquired snapshots.
- Second vertical slice with separate Great Britain and Northern Ireland
  learning routes; GB notice, England-and-Wales court, Scottish prosecution
  and Northern Ireland speeding branches; public/private actor boundaries;
  normalized ontology; and a synthetic evidence-lineage journey.
- Driving-slice semantic checks for exact providers, jurisdictions, source
  sets, assertion status, graph completeness and non-universal deadlines.
- Bounded death, bereavement and estate register with 20 official linked
  references and no acquired snapshots.
- Third vertical slice with separate national registration routes; Tell Us
  Once and Northern Ireland manual notification boundaries; England-and-Wales
  probate, Scottish confirmation and Northern Ireland probate routes; private
  dependencies; normalized ontology; and a synthetic journey.
- Bereavement semantic checks for exact authority, jurisdiction, source-set,
  notification-coverage, estate-process and graph-completeness boundaries.
- MIT licence for repository-authored code, documentation and ontology terms.
- Dated machine-readable rights decisions covering every registered source
  host, OGL attribution, CPSV-AP, Open Referral UK and HSDS.
- Rights validation and regression tests for source-host coverage, exact OGL
  attribution, standards terms, zero snapshots and generated projections.
- Attribution and third-party notices for downstream users.
- Explicit three-slice review-to-publication plan with integrated-review,
  Explorer-compatibility, release-scope, frozen-candidate, manual Pages and
  real-browser verification gates.

### Changed

- Recorded owner approval of `okf-domain-profile.v1` and the three fixture
  contracts, authorizing bounded source registration and slice implementation.
- Connected the explicitly authorized private GitHub repository while keeping
  remote CI and GitHub Pages disabled.
- Recorded the private-plan branch-protection limitation while retaining the
  sole-developer PR-only policy for `main`.
- Advanced the missed-rubbish fixture acquisition state to
  `linked_references_registered`.
- Advanced the driving fixture to `linked_references_registered` before its
  implementation merged in PR #4.
- Recorded PR #4 as merged and advanced the bereavement fixture to
  `linked_references_registered`; all three approved denominators are now
  registered.
- Replaced pending reuse markers with recorded source-family decisions while
  retaining link-and-summary-only use and prohibiting source-content and
  snapshot redistribution.
- Recorded PR #5 and PR #6 as merged and advanced the bounded sample to
  integrated review, while keeping publication separately gated.

## [0.0.0] - 2026-08-07

### Added

- Fail-safe local repository bootstrap with source/generated boundaries.
- OKF v0.2 root, section indexes and deterministic small-bundle builder.
- Citizen life-course research overview with the original generating prompt.
- Authoring guidance, implementation roadmap, validation tests and disabled CI
  scaffold.
