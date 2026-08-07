# `okf-domain-profile.v1` review handoff

This handoff accompanies the machine-readable
[`okf-domain-profile.v1.yaml`](okf-domain-profile.v1.yaml). It is a draft
governance contract, not an approved production ontology or authority claim.

## Proposed decision

Approve the profile as the boundary for implementing the first three vertical
slices. Approval would authorize bounded source-family decisions and slice
implementation; it would not authorize broad acquisition, public publication,
personalized decisions or unsupported four-nation equivalence.

## Fixed scope

The first denominator is three slices:

1. missed rubbish collection;
2. learning to drive through one enforcement exception; and
3. death and bereavement through Tell Us Once and estate administration.

Each must exercise ordinary and exception paths, jurisdiction, provider,
authority, evidence, governing rules, time, outcome, redress, provenance and
any necessary private-sector dependency. Broader life-course coverage remains
deferred.

## Semantic and authority boundary

The central model is life event or situation → user need → public service →
service episode → outcome. Person roles, providers, jurisdictions, rules,
evidence, channels, costs, artefacts, time and redress provide context.

The bundle explains and navigates. It does not make an individual eligibility,
medical or legal decision. Similar labels do not establish shared identity,
and a GOV.UK route does not establish that a process applies uniformly in all
four nations.

## Standards decision

- OKF 0.2 is selected for the authored bundle conventions.
- CPSV-AP 3.2.0 and Open Referral UK are mapping references; conformance is not
  yet claimed.
- SKOS, OWL/RDFS, PROV-O and SHACL have planned, distinct roles.
- The current Explorer small-bundle compatibility contract remains
  provisional until actual consumers are inventoried.

## Assertion and provenance decision

Every material assertion is one of `official`, `normalized`, `inferred` or
`editorial-example`. Official status requires direct support from an identified
authority within its scope. Generated relationships remain inferred and are
never presented as official. Unknown is not false.

Source identity, jurisdiction and observation time are required. Each source
family must later declare its update cadence, rights, coverage and limitations.

## Unresolved gates

Approval should explicitly acknowledge that these remain open:

- repository code and documentation licensing;
- acquired-source rights and redistribution decisions;
- the complete Explorer consumer inventory;
- the governed predicate registry and SHACL shapes; and
- source-family registers for the three slices.

These gaps continue to block production assertions or publication where the
machine-readable profile says they do.

## Review checklist

- [ ] Scope and denominators are acceptable.
- [ ] Users, tasks and authority boundary are acceptable.
- [ ] Jurisdiction and assertion-status rules are acceptable.
- [ ] Standards roles do not overclaim conformance.
- [ ] Rights, privacy and freshness gates are acceptable.
- [ ] Explorer consumer-lock assumptions are acceptable or corrected.
- [ ] The dependency graph orders implementation and publication correctly.
- [ ] The three [fixture contracts](../evaluation/fixtures/README.md) are an
      adequate acceptance boundary.

Until every required correction is recorded and the owner approves this
handoff, its status remains `draft` and acquisition and publication remain
disabled.
