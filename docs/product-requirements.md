---
type: Product requirements document
title: Product requirements for A Life in the UK
description: User needs, product behaviours, acceptance criteria and delivery boundaries for the A Life in the UK discovery and learning product.
status: draft
version: "0.1"
document_date: "2026-08-15"
owner: owner:chris-page-gov
---

# Product requirements for A Life in the UK

## Document purpose

This document defines what **A Life in the UK** must do for its users. It
organises the existing approved corpus, safety, semantic and publication
contracts into one product view. It does not replace those contracts or
authorise a new release.

The product baseline is `main` at `736d7dc4dbb4e44082f6b7786dd88afd55954792`.
The public population-complete preview and its retrieval records passed
exact-byte and real-browser verification on 13 August 2026. The corpus is not
release grade: 291 of 293 service families still require specialist review and
none has named specialist acceptance.

When this document and a more specific governed contract disagree, the
contract controls. The main controlling sources are:

- the [life-course research overview](../research/overview.md);
- the [population contract](../profiles/life-course-population-contract.v1.yaml);
- the [semantic contract](../okf.semantic.json);
- the [authoring guide](authoring.md);
- the [delivery plan](../PLANNING.md); and
- the [current repository status](../REPOSITORY_STATUS.md).

## Product summary

A Life in the UK is an independent, citizen-centred discovery and learning
product about public services, rights, responsibilities and life events in the
United Kingdom. It helps a person move from a topic or situation to:

1. an understandable service-family overview;
2. its place within a wider life-course domain and enclosing process;
3. ordinary and exception journeys;
4. explicit national, devolved and applicable local variants;
5. the authorities, providers, evidence, rules, outcomes and redress involved;
6. inspectable relationships and their provenance; and
7. current official source links for further action.

The product is a map, not the territory. It supports discovery and education;
it does not perform a government transaction or make a personal decision.

## The problem

Information about one life event is often distributed across departments,
devolved administrations, councils, health bodies, regulators and private
dependencies. Publisher websites usually describe the part owned by one
organisation. A person may still need to work out:

- which process encloses the page they found;
- what normally happens before and after the current step;
- whether a different route applies in another UK nation or locality;
- what evidence, deadline, cost, output or redress route matters;
- which organisation is accountable and which merely delivers a step;
- whether a relationship is official, normalised, inferred or illustrative;
  and
- whether the information is current enough to rely on.

Search engines can find pages but do not reliably expose that structure or its
evidence. Large graphs can expose structure but become difficult to interpret
without hierarchy, grouping and a clear selected route.

## Product vision

Anyone exploring a topic within the governed life-course vocabulary should be
able to find the relevant family, understand its context, inspect its journey
and evidence, and continue to an authoritative source without needing to know
which public body owns the subject or how an ontology works.

## Intended users and needs

### People exploring a public-service situation

They need plain-language orientation and a safe handoff to the current official
service. They may not know the service name, responsible organisation or
jurisdiction.

### Learners and educators

They need familiar examples that explain the difference between data,
information, knowledge, taxonomy, ontology and provenance. They need to move
between narrative and graph views without losing context.

### Researchers, service designers and policy professionals

They need to compare routes, authorities, dependencies, exceptions and gaps
across domains and jurisdictions. They need stable identities and evidence for
material relationships.

### Specialist reviewers

Legal, clinical, safeguarding and service-owner reviewers need to see the
exact claim, source, observation date, jurisdiction, assertion status and
review state before accepting or rejecting it.

### Developers and AI-assisted research users

They need bounded, machine-readable records with stable identifiers, explicit
ordering and provenance. They need the product to make unsupported answers and
missing evidence detectable rather than rewarding a plausible guess.

### Maintainers and publishers

They need authored source, deterministic generation, locked local validation
and an exact-byte manual publication path. They must be able to update a claim
without hand-editing a generated projection.

## Product principles

1. **Start with the person's situation.** Organisational structure is useful
   evidence, not the primary navigation model.
2. **Show context before complexity.** Domain, enclosing process, selected
   family and selected episode should remain clear as a person opens detail.
3. **Keep variants explicit.** Similar labels, a GOV.UK route or a shared
   provider never prove UK-wide equivalence.
4. **Keep ordinary and exception journeys separate.** Failure, enforcement,
   complaint and appeal routes must not be hidden inside an idealised path.
5. **Make trust inspectable.** Material claims and graph edges retain authority,
   evidence, rights, observation time, derivation and review status.
6. **Hand off before advising.** Summaries orient the user and active links send
   them to the current authoritative service.
7. **Reveal uncertainty.** Unknown, not applicable, not published by a source
   and awaiting review are different states.
8. **Do not collect personal data.** Review situations and personas are
   synthetic. The public product does not need a user account or case details.
9. **Remain static and reproducible.** The main experience must not depend on a
   hosted search service, analytics, a remote model or a runtime source fetch.
10. **Teach through use.** A user should learn what an ontology contributes by
    following an everyday journey, not by reading definitions first.

## Goals

### G1. Reliable discovery

Find every governed family, domain, process and supporting concept through
titles, aliases and plain-language topic terms. When there is no supported
match, preserve useful domain browsing and do not invent a result.

### G2. Process orientation

Explain where the selected family sits in an enclosing process and life-course
domain. Show what is explicitly authored as preceding, current, following or
exception behaviour without turning mere relatedness into sequence.

### G3. Journey understanding

Present at least one ordinary path and one exception or failure path for every
family, including applicable jurisdiction, provider, requirements, evidence,
rules, channel, cost, time, output, outcome and redress states.

### G4. Trustworthy source handoff

Give every applicable route variant at least one verified authoritative link
or a sourced non-applicability decision. Make the source identity, observation
date, rights basis and limitations visible before the user acts.

### G5. Navigable semantic relationships

Provide a graph in which people can move from domain to process to family to
episode, then inspect supporting actors, jurisdictions, evidence, rules,
dependencies, outcomes, redress and sources.

### G6. Accessible learning

Use the same corpus to teach ontology and public-service modelling to a
beginner, while retaining sufficient evidence and precision for expert review.

### G7. Safe reuse

Provide human-readable and machine-readable records that preserve identity,
ordering, provenance, rights and review limits for downstream tools.

### G8. Reproducible maintenance and publication

Build and check all projections locally through locked `uv` commands. Publish
only a frozen, explicitly authorised candidate and verify its exact public
identity and representative journeys in a real browser.

## Non-goals

The product will not:

- claim to enumerate every real UK public service, provider page or local
  variation beyond the governed 293-family denominator;
- calculate eligibility, liability, diagnosis, treatment, entitlement or a
  legal outcome;
- replace an emergency route, professional adviser or official service;
- submit applications, payments, reports, appeals or complaints;
- store profiles, case histories, addresses, health information or other real
  personal data;
- redistribute official page content, response bodies or snapshots;
- use label similarity to merge identities or jurisdictions;
- infer a cross-family sequence from display grouping or adjacency;
- use a hosted large language model as the search or answer engine;
- claim formal CPSV-AP, Open Referral, OWL, RDF or SHACL conformance without a
  separate approved conformance gate; or
- describe population completion as specialist-reviewed release grade.

## Governed product baseline

| Measure | Current governed baseline |
|---|---:|
| Life-course domains | 24 |
| Enclosing processes | 48 |
| Service families | 293 |
| Ordinary and exception episodes | 586 |
| Ordered journey steps | 881 |
| Typed official-source links | 879 |
| Governed directed relationships | 15,810 |
| Competency questions | 104 |
| Families requiring specialist review | 291 |
| Families with named specialist acceptance | 0 |

Population-complete means reconciled against these declared denominators. It
does not mean that the real-world subject is exhausted.

## Product surfaces

### Start and learning route

The landing page and [beginner learning plan](start-here.md) must explain what
the product is, what it contains, how to try it and what it does not claim.

### Explore OKF

The self-contained review interface must provide in-browser search, explicit
jurisdiction emphasis, ordinary and exception episodes, ordered steps,
official-source links and provenance without runtime data calls.

### OKF Explorer

The full Explorer must provide Reader, Narrative, Graph, Resources and other
compatible views over the large-corpus descriptor. It must preserve deep links
and selected context as the user moves between views.

### Compact human and AI retrieval records

The catalogue and one complete HTML record per family must expose stable
identity, description, jurisdiction routes, episode order, sources and review
state in small, directly retrievable documents. The full projection remains the
audit artefact.

### Repository source and evidence

Authored Markdown and structured files under `source/`, `ontology/`,
`profiles/` and `schemas/` remain inspectable. Generated data, manifests and
validation reports must point back to their governed inputs.

## Required product behaviour

### Epic A: orientation and discovery

#### PRD-DISC-001 — First-use orientation

As a first-time visitor, I want to understand the product before searching so
that I do not mistake it for an official or personalised service.

Acceptance criteria:

- The first view names A Life in the UK and describes it as independent,
  educational and navigational.
- It states the 293-family denominator and distinguishes it from every real UK
  service or local variation.
- It shows that the corpus is population-complete but not release grade.
- It provides a visible route to search, browse, learning material and source
  or provenance information.
- The safety warning does not depend on colour, hover or opening a secondary
  panel.

#### PRD-DISC-002 — Search by governed topic

As a person who knows a situation but not a service name, I want to search in
ordinary words so that I can find the relevant family.

Acceptance criteria:

- Every canonical family title and registered alias returns the intended
  family within the first five results.
- Every domain, process and supporting concept is searchable.
- The 104 governed competency questions each return the expected family within
  the first ten results where the current acceptance fixture declares one.
- Prefix matching and bounded typo tolerance do not manufacture semantic
  relationships.
- Each result shows enough context to distinguish similar families, including
  its domain, process, summary and relevant jurisdiction information.
- A concise explanation identifies which indexed terms supported the match.

#### PRD-DISC-003 — Empty and unmatched searches

As a person whose words do not match the corpus, I want a useful recovery path
so that a failed query is not a dead end.

Acceptance criteria:

- An unmatched query returns no invented family or semantic answer.
- The interface says that no governed match was found.
- All 24 life-course domains remain available for browsing.
- The user can clear or revise the query without losing their prior route.
- A blocked or malformed index produces a specific error and a route back to
  the start, not an empty results panel presented as success.

#### PRD-DISC-004 — Browse without searching

As a learner or reviewer, I want to browse from domain to process to family so
that I can understand the coverage model without guessing keywords.

Acceptance criteria:

- All 24 domains expose their governed process groups.
- All 48 processes expose their mapped families.
- All 293 families are reachable from exactly one approved population mapping.
- Counts distinguish service families from the larger supporting-concept
  total.

### Epic B: understand one family in context

#### PRD-FAM-001 — Plain-language family overview

As a user who selects a family, I want a concise explanation of the situation
and interaction boundary so that I know whether I am in the right place.

Acceptance criteria:

- The family view shows the canonical title, stable ID, original summary,
  aliases, life-course domain and enclosing process.
- It names applicable jurisdictions and route variants without guessing from
  a website hostname.
- It shows accountable authority and provider roles separately where the
  source supports that distinction.
- It displays specialist-review state and important limitations before the
  user follows a route.

#### PRD-FAM-002 — Enclosing process narrative

As a person trying to understand a process, I want the selected family placed
within its wider context so that I can see what may come before and after.

Acceptance criteria:

- Narrative identifies the domain and enclosing process.
- It distinguishes authored preceding or following relationships from merely
  related families.
- It explains what happens within the selected family in plain language.
- It links to explicitly governed related routes without presenting them as a
  mandatory personal journey.
- Moving between Narrative, Graph, Resources and the family detail preserves
  the selected family and browser history.

#### PRD-FAM-003 — Ordinary and exception journeys

As a person reviewing a family, I want ordinary and exception paths separated
so that failure, enforcement or redress is not hidden.

Acceptance criteria:

- Every family exposes at least one ordinary episode and one exception or
  failure episode.
- Steps appear in their authored order and retain stable identifiers.
- Each step reports supported values or an explicit `not_applicable` or
  `not_published_by_source` state for the required journey dimensions.
- Switching episodes or jurisdiction variants does not silently combine their
  steps.
- Emergency, safeguarding, appeal and deadline boundaries are visibly
  signposted when authored.

#### PRD-FAM-004 — Jurisdiction and local variation

As a user in a UK nation or locality, I want variants shown explicitly so that
I do not follow a route that applies elsewhere.

Acceptance criteria:

- UK-wide, England, Scotland, Wales, Northern Ireland and local applicability
  remain distinct.
- Welsh and English pages are treated as language variants only when the
  publisher explicitly pairs them.
- Local coverage identifies responsibility types and structural archetypes;
  it does not duplicate equivalent council pages merely to increase counts.
- Missing coverage is shown as a gap, not as evidence that a route is shared.

### Epic C: navigate the graph

#### PRD-GRAPH-001 — Hierarchical graph entry

As a user opening a graph, I want the hierarchy to remain visible so that I
understand where I am.

Acceptance criteria:

- The primary hierarchy is life-course domain, enclosing process, service
  family, then ordinary or exception episode.
- Opening a domain shows grouped processes; opening a process shows grouped
  families; opening a family centres its journey.
- The active hierarchy path and opened level remain visible outside the graph
  drawing area.
- Browser Back reverses graph-opening actions in the order they occurred.
- A copied deep link restores the selected view, family and opened hierarchy.

#### PRD-GRAPH-002 — Supporting relationships

As a reviewer, I want to inspect the concepts supporting an episode so that I
can understand its authority, requirements and outcomes.

Acceptance criteria:

- Actors, jurisdictions, evidence, rules, dependencies, outcomes, redress and
  sources branch from the relevant family or episode.
- Every material edge exposes its stable assertion ID, direction, predicate,
  preferred and inverse labels, assertion status, scope, authority,
  derivation, observation time, evidence and rights.
- Reverse navigation changes the display label but does not reverse the
  asserted triple.
- Official, normalised, inferred, model-derived, synthetic and historical
  planes remain distinguishable.

#### PRD-GRAPH-003 — Dense graph handling

As a mouse, keyboard or touch user, I want dense relationships grouped and
selectable so that labels and hit areas do not obscure each other.

Acceptance criteria:

- Large sibling sets open as labelled groups before rendering every child.
- A selected group clearly indicates whether all or only some children are
  open below it.
- Labels use available width and do not overlap another node's active target.
- The selected node has one unambiguous visual and programmatic identity.
- Controls for clearing filters, closing opened hierarchy and resetting layout
  use distinct labels and are placed together by purpose.
- Relationship and hierarchy controls can collapse to preserve graph space
  without hiding the current route.

### Epic D: evidence, trust and official sources

#### PRD-SRC-001 — Source summary and handoff

As a user, I want to know what supports the overview and reach the official
source so that I can verify current information before acting.

Acceptance criteria:

- Every applicable route has at least one current authoritative source or a
  sourced non-applicability decision.
- The resource view shows source label, publisher or owner, jurisdiction,
  observation date, media type, display mode, rights basis and original
  summary.
- Browser-readable text, JSON or XML may be displayed only through the typed
  source contract and within its safety limits.
- A browser-blocked or unsupported response is presented as **Open official
  source**, not as an empty or broken inline viewer.
- A failed primary source is a blocking family issue; a failed secondary source
  is recorded as an explicit gap.

#### PRD-SRC-002 — Provenance and rights

As a reviewer, I want to inspect where a statement came from so that I can
judge its authority and permitted use.

Acceptance criteria:

- Material assertions show source identity, evidence, observation time,
  derivation, assertion status, authority and rights.
- Repository-authored code, documentation and ontology terms are labelled MIT.
- Third-party source material remains linked and summarised rather than
  redistributed.
- OGL attribution and applicable third-party licence notices remain reachable
  in the browser.
- Generated projections never imply that third-party source content has been
  relicensed.

#### PRD-SRC-003 — Freshness and review state

As a person considering whether to rely on a route, I want its freshness and
review state disclosed so that I know when to check further.

Acceptance criteria:

- Every source assertion carries an observation date and freshness state.
- Material legal, clinical and high-impact operational claims identify the
  required reviewer role.
- Missing named acceptance remains visible and prevents a release-grade claim.
- The interface tells the user to check the current authoritative service
  before acting.

### Epic E: learning and explanation

#### PRD-LEARN-001 — Beginner route

As a learner, I want a guided route from a familiar situation to an ontology
so that I can understand the concept without prior semantic-web knowledge.

Acceptance criteria:

- A ten-minute route demonstrates search, jurisdiction, ordinary and exception
  paths, provenance and official-source handoff.
- Longer routes introduce the semantic model, ontology, evidence, licensing,
  evaluation and publication controls in a clear order.
- Missed rubbish collection, learning to drive and speeding, and death and
  bereavement remain worked vertical slices.
- Definitions use plain English and link to a concrete record or journey.

#### PRD-LEARN-002 — Narrative and graph together

As a learner, I want narrative and graph views to explain the same governed
relationships so that I can move between prose and structure.

Acceptance criteria:

- Narrative labels and graph predicates refer to the same stable concepts and
  assertions.
- Opening a graph from a narrative centres the selected concept and adds the
  action to browser history.
- Returning to Narrative restores the prior reading position or selected
  record context.
- The product explains when a displayed relationship is a normalised planning
  relationship rather than an official claim.

### Epic F: machine and AI-assisted use

#### PRD-MACH-001 — Bounded machine retrieval

As a developer or AI-assisted researcher, I want small complete records and a
full audit projection so that I can retrieve safely without losing evidence.

Acceptance criteria:

- A compact catalogue links to one complete human-readable record per family.
- Each family record includes stable identity, summary, jurisdiction routes,
  ordered ordinary and exception episodes, sources, provenance and review
  state.
- The full YAML-LD, JSON-LD and relationship runtime remain available as
  deterministic audit artefacts.
- Every generated record is bound by SHA-256 to the frozen source projection.
- A downstream tool can abstain when the record does not support a requested
  answer.

#### PRD-MACH-002 — Safe answer boundary

As a reviewer of an AI-assisted answer, I want material statements traceable
to records and sources so that unsupported fluency is visible.

Acceptance criteria:

- Stable family, episode, step, source and assertion identifiers can be cited
  from the published records.
- Explicit jurisdiction fields take precedence over hostname or label guesses.
- Related-family grouping cannot be interpreted as authored sequence without a
  governed sequence assertion.
- The record exposes limitations and specialist-review state alongside the
  answerable content.
- No product acceptance measure rewards an invented answer to an unsupported
  question.

### Epic G: inclusive and resilient use

#### PRD-USE-001 — Operable interface

As a user with different access needs or input methods, I want the interface to
remain understandable and operable.

Acceptance criteria:

- All interactive controls are reachable and usable by keyboard.
- Focus is visible and follows the opened content without trapping the user.
- Controls and graph nodes have programmatic names that match their visible
  purpose.
- Colour is never the only indicator of selection, authority, status or
  relationship type.
- Core content remains readable at a narrow 375-pixel viewport without hidden
  horizontal controls.
- Relative text sizing can emphasise the selected context without making
  supporting labels unreadable.

#### PRD-USE-002 — Static and managed-device resilience

As a user on a managed laptop, I want a low-dependency experience so that I can
review the corpus within common network restrictions.

Acceptance criteria:

- The standalone Explore OKF interface makes no runtime API or data request
  after the document has loaded.
- It uses no analytics, cookies, service worker, persistent browser storage,
  third-party font, remote image or installation step.
- If GitHub Pages or an official source is blocked by organisational policy,
  the product explains the boundary and provides a repository or download
  alternative where permitted.
- A failed source fetch does not alter the governed family record.

### Epic H: maintenance and release governance

#### PRD-GOV-001 — Reproducible change

As a maintainer, I want one governed authoring path so that generated surfaces
cannot drift from their evidence.

Acceptance criteria:

- Markdown and structured files under the declared authored roots remain the
  source of truth.
- Generated bundle, semantic, search, graph, retrieval and publication files
  are rebuilt rather than hand-edited.
- Required local checks run through `uv run --locked` and pass offline.
- Live link audits remain a separate metadata-only reviewed acquisition step.
- A material change updates its planning, tracking, status, change log and
  authoring documentation in the same pull request where required by
  [the delivery plan](../PLANNING.md).

#### PRD-GOV-002 — Controlled publication

As the product owner, I want publication separated from implementation so that
untested bytes cannot become public implicitly.

Acceptance criteria:

- Pull requests, pushes and merges do not trigger remote CI or GitHub Pages.
- A publication request names one frozen candidate and exact protected-main
  merge.
- The Pages workflow transports only files and hashes in the reviewed manifest
  and does not rebuild the corpus.
- The exact deployed URL passes cache-bypassed identity and representative
  citizen-journey checks before it is labelled verified.
- A failed verification remains recorded as failed and the URL remains
  unverified.

## End-to-end acceptance journeys

The following visible journeys are required across the product surfaces.

### Local-service failure

Search for a missed bin, find **Report a missed rubbish collection**, identify
the local-authority responsibility boundary, compare ordinary and failure
episodes, inspect complaint or redress relationships, and open the official
postcode route.

### Four-nation health discovery

Search for finding an NHS dentist, identify the family and its nation-specific
routes, preserve the manual link-only health boundary, and open a current
official source without generating clinical advice.

### Enforcement exception

Search for a speeding notice, distinguish Great Britain and Northern Ireland
routes, inspect the notice, deadline, evidence, penalty and court or challenge
branches, and avoid making a legal decision for the user.

### Death and bereavement

Search after a death, distinguish registration, Tell Us Once or manual
notification, estate authority and administration, compare national variants,
and show private dependencies without recommending a provider.

### Education and evidence

Search for applying for a school place, recover the stable family identity,
ordinary and exception steps, jurisdiction routes, sources and review state in
both the human interface and compact retrieval record.

### Unmatched question

Enter a conversational question outside the governed vocabulary. Receive no
invented answer, retain the 24-domain browse route, revise the query and return
to the previous context with browser Back.

### Source unavailable

Open a family whose official page blocks inline browser access. Retain the
family summary and evidence, explain why inline display is unavailable, and
offer a labelled official-source handoff without claiming the source was
verified in that session.

### Dense hierarchy

Open a high-count format or domain group, reveal grouped children one level at
a time, see which level is open, select one node unambiguously, then use Back
to undo each opening action.

## Product success measures

### Discovery

- 293 of 293 canonical titles and registered aliases meet the top-five result
  rule.
- 104 of 104 governed competency questions meet their declared top-ten rule.
- 24 of 24 domains and 48 of 48 processes are browseable and searchable.
- An unmatched query produces zero invented semantic results and always offers
  domain browsing.

### Comprehension

- In moderated review, a participant can identify the selected family's
  domain, process, jurisdiction, ordinary path, exception path and official
  source without opening repository code.
- A participant can distinguish an official assertion from a normalised or
  inferred relationship.
- A participant can explain that related families are not automatically an
  authored sequence.

### Trust and handoff

- Every applicable route variant has an active authoritative link or a sourced
  non-applicability decision.
- Every material graph edge passes provenance and evidence validation.
- Representative national, devolved, local, health, legal and
  private-dependency journeys reach an official source.
- No source response body or snapshot is retained.

### Reliability and governance

- Authored inputs and all generated projections reconcile deterministically.
- Locked local checks pass before review.
- Published files match the authorised manifest byte for byte.
- Real-browser verification reports no unexpected runtime request, storage use
  or console error on the representative journeys.

## Completion and release gates

### Population-complete

All 293 governed families satisfy the discovery, process, journey, source and
relationship contract. Specialist-review warnings may remain. This gate is
met.

### Product-experience complete

The current population is reliably discoverable and understandable through
search, domain browsing, Narrative, Graph and Resources. The open search
fallback and graph-interpretation requirements in this PRD must pass their
visible acceptance journeys before this gate is met.

### Release grade

Every applicable legal, clinical and high-impact operational claim has current
source re-observation and named reviewer acceptance. This gate is not met.

### Publication-ready

A candidate for the intended release class is frozen, explicitly authorised,
deployed without rebuilding and verified at its exact public URLs. The current
population-complete preview has passed this gate for its stated non-release-
grade scope; any later change requires a new candidate and verification.

## Current assessment

| Product outcome | Status at this baseline | Evidence or remaining need |
|---|---|---|
| Governed population and process mapping | Met | 293 families, 24 domains and 48 processes reconcile locally. |
| Ordinary and exception journeys | Met | 586 authored episodes and 881 ordered steps are present. |
| Source-linked discovery | Met for the frozen preview | 879 typed links and representative search-to-source journeys passed. |
| Exact-title and governed-alias search | Met | Local search acceptance and representative browser queries passed. |
| Conversational-query recovery | Partly met | Several ordinary-language questions returned no result. |
| Unmatched-query domain browsing | Not met in the full Explorer | A zero-result query currently reduces all facets to zero. |
| Family narrative and provenance | Met on representative journeys | Narrative, graph edge evidence and source handoff passed. |
| Dense graph and facet interpretation | Partly met | Hierarchy, grouping, target size and control-density improvements remain. |
| Compact AI retrieval | Met for deployed records | Catalogue and 293 family records passed identity and browser verification. |
| Specialist-reviewed release grade | Not met | 291 families require review; none has named acceptance. |

## Dependencies

- **OKF Explorer:** universal Narrative, Graph, Resources, browser history and
  large-corpus behaviour are implemented in the separate Explorer repository.
- **Official publishers:** source availability, language pairing and current
  service content remain outside this product's control.
- **Authority and geography registers:** applicable GSS, ODS and source-native
  identifiers support explicit responsibility and jurisdiction.
- **Specialist reviewers:** release grade depends on named legal, clinical,
  safeguarding and service-owner acceptance.
- **GitHub and GitHub Pages:** repository review and the current public preview
  depend on those services, although local build and validation do not.
- **Locked local toolchain:** `uv.lock`, repository scripts and vendored schema
  and profile files establish deterministic production.

## Risks and mitigations

| Risk | Product effect | Required mitigation |
|---|---|---|
| Official pages change or disappear | A route may become stale or unusable. | Show observation dates, run reviewed metadata-only link audits and block a family when its primary link fails. |
| Similar services differ by nation or locality | A user may follow an inapplicable route. | Model variants explicitly and never infer applicability from labels or domains. |
| Graph density hides meaning | A user cannot tell what is selected or how they arrived. | Open grouped hierarchy progressively, preserve a visible route and make Back undo each opening. |
| Static search misses natural phrasing | A user assumes the corpus has no relevant topic. | Add bounded governed variants, explain no-match states and retain domain browsing without a generative answer. |
| A polished summary is mistaken for advice | A user acts on unreviewed material. | Keep independent, non-release-grade and official-source warnings visible at decision points. |
| Machine consumers invent sequence or authority | Downstream answers appear supported when they are not. | Preserve stable assertions, explicit order, authority planes and abstention-oriented evaluation. |
| Publication drifts from reviewed bytes | Public evidence no longer proves the live site. | Freeze manifests, deploy manually and verify exact URLs after each authorised change. |
| Specialist review does not scale to 293 families | Release grade remains indefinitely incomplete. | Prioritise high-impact claims, record reviewer roles and accept partial reviewed subsets without relabelling the whole corpus. |

## Priorities after this PRD

1. Close the bounded discovery gaps: conversational-query handling and the
   24-domain fallback for unmatched searches.
2. Reduce graph and facet interpretation cost while preserving provenance,
   hierarchy and browser history.
3. Run inclusive usability review across the representative national,
   devolved, local, health, legal and private-dependency journeys.
4. Define and staff the specialist-review programme for legal, clinical and
   high-impact operational claims.
5. Re-observe sources and freeze a new candidate only when an explicitly
   scoped release or publication change is requested.

## Decisions still required for a release-grade product

- Which user group is primary when citizen simplicity and expert evidence
  density compete in one view.
- Which legal, clinical, safeguarding and service-owner reviewers will accept
  each high-impact claim family.
- What freshness intervals apply by source and claim type.
- Whether release grade will be declared only for the whole corpus or for
  clearly labelled reviewed subsets first.
- What independent accessibility and departmental managed-device evidence is
  required beyond repository browser tests.
- What bounded conversational vocabulary can be added without turning static
  lexical search into an inferred or generative answer system.

These decisions do not block the current population-complete educational
preview. They block only the relevant stronger product or release claims.
