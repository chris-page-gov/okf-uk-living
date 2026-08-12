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

Use ordinary Markdown links between local concepts for narrative navigation.
Link direction is meaningful: the source record references the target record.
The small-bundle builder may emit these as compatibility relationships, but a
Markdown link alone does not establish a domain predicate. Governed
large-corpus relationships are generated from the structured dossiers,
registers and predicate registry described below.

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

## Domain profile and fixture contracts

The approved [`okf-domain-profile.v1`](../profiles/okf-domain-profile.v1.md)
governs the first three slice contracts under `evaluation/fixtures/`. Those
fixtures are synthetic `editorial-example` acceptance boundaries, not official
service records. A fixture moves from `authorized_not_started` to
`linked_references_registered` only when its exact bounded denominator is
recorded under `source/`; this state does not authorize snapshots, broad
acquisition or redistribution.

The owner separately authorized the exhaustive link-only reference-family
inventory on 2026-08-07. That authorization covers URLs, owners,
jurisdictions, dates, dated rights decisions, original summaries and gaps for
the 24-domain denominator. It does not authorize snapshots, source-content
redistribution, unbounded or unstaged leaf acquisition or publication.

The owner-approved
[`service-family-denominator.v1`](../source/service-family-denominator.v1.yaml)
contains 293 normalized planning families in three waves. The
[`corpus-acquisition-policy.v1`](../profiles/corpus-acquisition-policy.v1.yaml)
governs local-authority coverage, GSS and applicable ODS identifiers, manual
health links, regulator-first private dependencies, sector redress and
specialist-review gates. A family name authorizes staged source registration;
it is not an official assertion that routes or rules are uniform.

The owner-approved `okf-explorer-large-corpus.v1` projection renders those 293
planning families with seven colour facets. It must remain generated from the
denominator, contain no acquired source content, and keep publication disabled.
The static search and every facet posting must reconcile with the same ordered
record set.

The approved [rights register](../source/rights-decisions.v1.yaml) now resolves
the repository and current linked-source decisions without expanding the use
boundary. Repository-authored code, documentation and ontology terms are MIT.
Official pages remain linked references with original summaries; do not copy
page text, images, logos or other assets into authored or generated output.

## Full-population dossiers

The owner-authorized
[`life-course-population-contract.v1`](../profiles/life-course-population-contract.v1.yaml)
governs the staged 293-family implementation. Each family is authored as a
`life-course-family.v1` dossier under `source/life-course-families/<domain>/`
and has a matching service narrative. The dossier retains structured
applicability, actors, an ordinary journey, at least one exception or failure
journey, dependencies, sources, limitations and review state.

Every family references one of the 48 normalized processes in
[`life-course-processes.v1`](../source/life-course-processes.v1.yaml). Process
membership supports navigation and never establishes official service
identity, shared rules or four-nation equivalence. Material graph edges use the
[governed predicates](../ontology/governed-predicates.v1.yaml) and retain
assertion status, authority, evidence, derivation, observation time and rights.

### Semantic projection and directed assertions

[`okf.semantic.json`](../okf.semantic.json) is the machine-readable contract
for the repository's OKF 0.2 core, additive Bundle Wiki YAML-LD profile,
authoritative inputs, generated outputs, Reader delivery plane and exact
checks. Read it before changing ontology or relationship generation.

`scripts/life_course_projection.py` normalises each governed relationship once
and deterministically emits four synchronised views:

- a direct semantic triple in the YAML-LD/JSON-LD entity graph;
- an evidence-bearing reified `okf:RelationshipAssertion`; and
- a route-scoped `okf-relationship-assertion.v2` runtime row for Explorer and
  its legacy hash-sharded adjacency; and
- a bounded `okf-relationship-runtime-row.v1` in an authority-preserving gzip
  plane, indexed by the SHA-256 route locator.

Every material directed relationship retains a stable absolute assertion IRI,
absolute source and target IRIs, an absolute predicate IRI, validated local
source and target routes, preferred and inverse labels, assertion status and
scope, authority, derivation, observation time, evidence and rights. Semantic
identity and navigation identity are separate: never manufacture an IRI from a
route in the Reader, and never replace an external IRI with a convenient local
slug.

The direct triple and reified assertion must describe the same source,
predicate and target. The reified node carries the provenance needed to judge
the statement; it does not create a second fact. Reverse Explorer navigation
uses `inverse_label` for presentation and does not reverse the asserted triple.
Confidence, similarity and display grouping never upgrade an assertion's
authority.

The build uses pinned contexts and emits deterministic YAML-LD and JSON-LD.
The browser may parse an explicit route-bearing YAML-LD graph, but it does not
fetch arbitrary remote contexts or perform OWL inference. Fix authored inputs
or the generator when semantic checks fail; do not edit `generated/semantic/`,
`large/data/relationships-0.json` or adjacency shards by hand.

The shared assertion contract is pinned locally at
[`schemas/semantic-assertion.schema.json`](../schemas/semantic-assertion.schema.json).
It is byte-identical to the canonical copy in the vendored, locked 16-file
[`profiles/bundle-wiki/v1`](../profiles/bundle-wiki/v1/) mirror. Do not edit the
mirror locally; use the Explorer reconciler's reviewed profile synchronisation
command. The four authored rich-runtime schemas define runtime rows, the
control manifest, the locator and its buckets.
The producer and checker apply its Draft 2020-12 rules exhaustively to both the
semantic assertions and the corresponding runtime rows. Evidence
`normalization` identifies the stable derivation rule with an absolute IRI;
put its human explanation in `rationale`, not in the IRI field. The validation
report records the schema URL, local path, digest, counts and violations before
it can claim `conformant`. The finalized pin requires both `kind` and `label`;
authority, evidence, optional evidence-resource and rights source URLs must be
canonical, credential-free HTTP(S) URLs with a non-empty host and valid port.

### Domain-register authoring and rendering

Population packs are authored compactly in one
`life-course-domain-register.v1` file per domain under
`source/domain-registers/`. Each register contains its reviewed topic-specific
source assertions, shared devolved handoffs, original family summaries,
aliases, situations, user needs, applicable primary jurisdictions,
private-dependency boundary and specialist-review state. It also names the
body-free receipt directory for every link.

`scripts/render_life_course_packs.py` deterministically renders three reviewed
surfaces from those registers:

- `source/life-course-families/<domain>/<family>.v1.yaml`;
- `services/<family>.md`; and
- `life-course/<domain>.md`.

Do not hand-edit those rendered files. Change the domain register and rerun the
renderer. `--check` rejects drift. A national discovery handoff may locate the
current route, but it must be labelled as a handoff and may not support a leaf
eligibility rule, cost, deadline or outcome.

If a contracted pack contains one of the six previously authored vertical
slices, include that identity in the domain register with
`preserve_existing: true`. The validator requires its existing dossier and
narrative, the renderer skips those two files, and cumulative reconciliation
still counts the family exactly once. Do not replace a deeper reviewed slice
with the compact population template.

Each three-domain pack contributes at least 13 natural-language competency
questions under `evaluation/competency-questions/`. The search acceptance check
requires every canonical title and alias in the first five, each expected
competency result in the first ten, staged process titles to be searchable and
an unmatched query to return no invented result.

Health and care domain registers remain manually selected, metadata-audited
and link-only. A health source can support a discovery handoff and original
summary, but its response body is never retained and the generated dossier may
not diagnose, triage, interpret results, decide capacity or safeguarding, or
generalize one nation's clinical route to another.

Civic, organisation and ideas/research registers must keep decision authority
with the current public body, institution or regulated adviser. A devolved
business or democracy page is a discovery handoff, not evidence that
immigration status, franchise, tax, corporate form, intellectual-property
rights, funding eligibility or publication rules are uniform. When one current
official page illustrates only a funder, institution or jurisdiction-specific
route, state that scope and exclusion directly in the source assertion.

Overseas, later-life and death/bereavement registers must separate UK consular
or national discovery handoffs from destination law, devolved health and care
routes, local delivery and territorial succession or registration rules.
Clinical, capacity, cause-of-death, probate, insolvency and tax decisions remain
with the current authority or regulated adviser. A national or devolved topic
page may support navigation across a process but cannot establish an individual
deadline, entitlement, treatment, estate priority or provider recommendation.

Source-link receipts retain response metadata only. They never store response
bodies. An automated block may be resolved by an explicit real-browser receipt;
a discovery page is not sufficient evidence for a leaf-service rule.

## Shared authority and source infrastructure

[`authority-registry.v1`](../source/authority-registry.v1.yaml) is the dated
identity denominator for the population packs. It contains 382 principal local
authority areas and normalized actors, 19 strategic/combined authorities, 397
GSS geographies in total, and shared national, regulator and redress actors.
A GSS code identifies an administrative area and does not by itself name the
legal body or prove that it delivers a service. ODS and source-native identities
are added only within their declared coverage.

English and Welsh labels share identity only when the publisher places them in
the same official record or explicitly pairs the pages. Similar text, translated
slugs or parallel URLs are never identity evidence. ESD Services/LGSL identifiers
are optional mappings and never evidence that a current authority offers a route.

The reviewed live refresh is:

```sh
uv run --locked python scripts/refresh_authority_registry.py --check
```

This parses official metadata in memory and retains only identifiers, names,
dates and links. It is deliberately separate from the offline build. Live link
audits use `scripts/audit_source_links.py` and write `source-link-receipt.v1`
metadata; they never retain response bodies. A failed primary family link blocks
that family, while a failed secondary link creates a visible gap.

Contract validation checks structure, jurisdiction coverage, ordinary and
exception paths, assertion status and publication gates. A passing contract
check does not approve the profile or validate a real service route.

## Linked-reference source registers

The three versioned source registers preserve source owner, authority role,
URL, jurisdictional coverage, exclusions, observation date, freshness policy
and rights basis. `source/rights-decisions.v1.yaml` maps every registered host
to its dated licence evidence. A `linked_reference_only` register stores no
source snapshot: its checksum must remain `not_applicable_no_snapshot`, and
authored summaries must be original, narrow, attributed and rechecked before
use.

Do not acquire, commit or redistribute a snapshot until the exact source,
licence version, required attribution, exclusions, acquisition time and
checksum are approved. Generated projections can be MIT only when upstream
expression is not embedded; otherwise preserve the upstream terms and record
a new compatibility decision.

Official facts belong on the exact local service or authority record they
support. Normalized service families and ontology modules may compare those
facts, but must not turn local times, exclusions, providers or remedies into a
UK-wide rule. Synthetic journeys remain `editorial-example` even when their
branches cite official service facts.

Each implemented slice must add a semantic regression check for its exact
route nodes, responsible providers, jurisdictions, approved source sets,
assertion statuses and required journey links. For enforcement or legal paths,
the check must also preserve the notice-specific or court-specific deadline
boundary and reject a synthetic journey presented as official advice.
For bereavement paths, it must also preserve Tell Us Once coverage, the
Northern Ireland manual-notification boundary, the exact national
registration authority and the distinction between probate and Scottish
confirmation.

## Exhaustive reference-family inventory

[`source/exhaustive-reference-inventory.v1.yaml`](../source/exhaustive-reference-inventory.v1.yaml)
is the Phase 4 discovery denominator. It accounts for 24 life-course domains
across UK-or-England, Scotland, Wales, Northern Ireland and local reference
scope. A `covered` cell means an authoritative discovery family has been
identified; it does not make the category page evidence for a leaf-service
claim. Local cells remain `partial` until current responsible-provider and
redress pages are selected.

Every inventory reference requires an HTTPS URL, owner, jurisdiction,
authority role, observation date, source update value or explicit absence,
dated rights decision and original summary. `scripts/check_inventory.py`
enforces the denominator, rights links, reference identity and gap ledger
offline; live freshness is a separate reviewed acquisition activity.

## Build and check

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). The
locked project environment is created automatically when these commands run:

```sh
uv run --locked python scripts/render_life_course_packs.py
uv run --locked python scripts/render_life_course_packs.py --check
uv run --locked python scripts/build_browser_handoff.py
uv run --locked python scripts/build_browser_handoff.py --check
uv run --locked python scripts/build_okf_bundle.py
uv run --locked python scripts/build_okf_bundle.py --check
uv run --locked python scripts/check_okf.py
uv run --locked python scripts/check_contracts.py
uv run --locked python scripts/check_sources.py
uv run --locked python scripts/check_inventory.py
uv run --locked python scripts/check_service_denominator.py
uv run --locked python scripts/check_corpus_policy.py
uv run --locked python scripts/check_population_contract.py
uv run --locked python scripts/check_domain_registers.py
uv run --locked python scripts/check_life_course_dossiers.py
uv run --locked python scripts/check_authority_registry.py
uv run --locked python scripts/check_rights.py
uv run --locked python scripts/build_large_corpus.py
uv run --locked python scripts/build_large_corpus.py --check
uv run --locked python scripts/check_large_projection.py
uv run --locked python scripts/check_search_acceptance.py
uv run --locked python scripts/build_population_assurance.py
uv run --locked python scripts/build_population_assurance.py --check
uv run --locked python scripts/check_population_assurance.py
uv run --locked python scripts/prepare_pages_publication.py
uv run --locked python -m unittest discover -s tests
```

`generated/browser/`, `generated/assurance/`, `okf-bundle.json`, `large/data/`
and `okf-explorer.json` are reproducible output. Never patch them directly.

## Population assurance and candidate freeze

`evaluation/candidates/population-complete-candidate.v1.yaml` declares the
authored freeze boundary: basis commit, exact data-plane artifact list,
population/release/publication gates, browser journeys and gap dispositions.
Run `build_population_assurance.py` only after rebuilding and checking the
authored dossiers and generated large-corpus projection. It derives the
coverage, omission, link-health, review-status and provenance reports and then
hashes the candidate artifacts into `generated/assurance/candidate-manifest.json`.

Population completion means the discovery contract is fully navigable; it does
not waive a dossier's `specialist_review_required` state. Release grade requires
named acceptance and current source re-observation for applicable legal,
clinical and high-impact operational claims. Publication requires a separate
owner request and a subsequent exact-deployment browser check. Never change a
generated assurance report or manifest by hand, and never rebuild a frozen
publication candidate during promotion.

## Pages publication unit

The public preview is assembled only from files listed in
`publication/pages-file-manifest.json`. Regenerate that manifest deliberately
with `uv run --locked python scripts/prepare_pages_publication.py
--write-manifest`, review its count, total bytes and hashes, and commit it with
the publication descriptor. Ordinary builds do not rewrite it.

The manual Pages workflow calls the same script with `--destination _site`.
That operation verifies every source hash and copies the frozen bytes; it does
not invoke a corpus generator. The only permitted destination is the ignored
repository `_site/` directory. The workflow publishes only the landing page,
the publication descriptor, the small bundle, large-corpus data, browser
handoffs, semantic projections, assurance reports, licence and notice. It does
not publish authored source dossiers, research working files or acquired
source content.

The workflow also requires the exact protected-main merge commit as its
`publication_commit` input and rejects a different workflow event or checkout.
The manifest records the reviewed data commit separately, so a transport-only
descriptor envelope cannot silently change the semantic or rich-runtime bytes.

The publication descriptor may differ from the local descriptor only in its
description, status, owner authorisation flag and the explicit publication
envelope. The validator rejects any other drift. Keep `release_grade: false`,
the specialist-review count and zero-snapshot boundary visible until a later
review changes them.

## Publication boundary

Local validation does not authorize publication. Complete the domain profile,
source/rights review, evaluation, frozen-candidate assurance and exact deployed
browser journey before sharing a public bundle URL.

### Life-course family source assertions

Family dossiers under `source/life-course-families/` may embed a complete
source assertion or point to a canonical linked-reference register with
`id` and `register`. A register reference is not a shortcut around evidence:
the named entry must resolve to its HTTPS URL, owner, authority role,
observation date, rights basis, original coverage summary and limitations.
Validation resolves every reference and rejects missing or duplicate IDs.
Source responses remain link-only unless a typed, browser-readable response
mode is explicitly declared; no response body or snapshot is retained.
