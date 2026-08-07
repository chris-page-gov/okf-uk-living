# `okf-domain-profile.v1` review handoff

This handoff accompanies the machine-readable
[`okf-domain-profile.v1.yaml`](okf-domain-profile.v1.yaml). The repository owner
approved the profile and three fixture contracts on 2026-08-07. Approval
governs bounded slice implementation; it is not a production ontology or an
authority claim.

## Approval record

Approved by `owner:chris-page-gov` on 2026-08-07 as the boundary for the first
three vertical slices. Approval authorizes bounded source-family registration
and slice implementation. It does not authorize broad acquisition, public
publication, personalized decisions or unsupported four-nation equivalence.

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

- [x] Scope and denominators are acceptable.
- [x] Users, tasks and authority boundary are acceptable.
- [x] Jurisdiction and assertion-status rules are acceptable.
- [x] Standards roles do not overclaim conformance.
- [x] Rights, privacy and freshness gates are acceptable.
- [x] Explorer consumer-lock assumptions are acceptable as provisional.
- [x] The dependency graph orders implementation and publication correctly.
- [x] The three [fixture contracts](../evaluation/fixtures/README.md) are an
      adequate acceptance boundary.

Bounded source registration may now begin for the three slices. Broad
acquisition, corpus expansion and publication remain disabled by the profile.
