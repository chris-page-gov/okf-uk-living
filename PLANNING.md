# Delivery planning

This plan turns the phase roadmap into bounded, reviewable delivery units. The
default assurance boundary is the local checkout: no remote CI, hosted build or
GitHub Pages deployment runs unless the owner explicitly requests publication.

## Delivery cadence

1. Select one bounded item from [TRACKING.md](TRACKING.md).
2. Implement it on a focused feature branch with its documentation changes.
3. Run `make validate` locally.
4. Open a draft pull request and record the validation evidence.
5. Review and merge without updating GitHub Pages unless the owner has made a
   separate, explicit publication request.

Changes to `main` remain pull-request-only by project policy. Server-side
branch protection is now active after the owner separately authorized public
visibility on 2026-08-09. The sole-developer rule requires pull requests and
resolved conversations but zero approving reviews or remote status checks.

## Lockstep documentation

Documentation changes ship in the same pull request as the change they
describe. The minimum update set is:

| Change | Required documentation |
|---|---|
| Any bounded delivery item | `TRACKING.md` and `CHANGELOG.md` |
| Scope, sequencing or gate | `PLANNING.md`, `ROADMAP.md` and `REPOSITORY_STATUS.md` |
| Authoring model or validation rule | `docs/authoring.md` and `AGENTS.md` |
| Local command or dependency | `README.md`, `AGENTS.md`, `Makefile`, `pyproject.toml` and `uv.lock` as applicable |
| Licence or source-use decision | `LICENSE_DECISIONS.md`, `NOTICE.md`, `source/rights-decisions.v1.yaml`, domain profile and affected source/evidence records |
| Publication state | `TRACKING.md`, `REPOSITORY_STATUS.md`, `CHANGELOG.md` and release evidence |

The pull-request description must explain either which documents changed or
why a listed document is unaffected. Documentation follow-up is not deferred
to a later pull request.

## Near-term delivery units

The owner approved `okf-domain-profile.v1` and the three fixture contracts on
2026-08-07. All three slices and the licensing decisions are merged. The local
Explorer remediation rerun passed: relationship and node provenance,
browser-safe source handoffs, and the first-class licence/notice surface are
verified. That bounded sample proposal was superseded by the later authorized
population-complete preview.

The owner separately authorized exhaustive link-only reference-family
discovery on 2026-08-07. `INVENTORY-001` is complete with 142 external records,
120 assessed coverage cells and 12 tracked gaps. This planning asset does
not change the sample release gates or authorize snapshots, broad leaf
acquisition, CI or publication.

The original sample sequence is defined in the
[three-slice review and publication plan](docs/review-and-publication-plan.md):

The owner superseded that proposed sample on 2026-08-08 by authorizing the
population-complete corpus as a public preview. `SCOPE-001`, `CAND-001` and
`PUB-001` are therefore complete for the preview. `PAGES-001` must promote the
exact 1,549-file manifest through the manual-only workflow, after which
`VERIFY-001` must test the exact deployed landing page, bundle identity,
search, Narrative, Graph, Resources and official-source handoff.

The manual Pages enablement attempt failed with GitHub HTTP 422 because the
current plan does not support Pages for the private repository. `PAGES-001` is
therefore blocked on an explicit owner choice between making this repository
public and using a separate public publication repository. Local UI review
continues to count as evaluation evidence, not public verification.
The manual workflow checks out publication merge `980c7a9…` so later tracking
and review evidence cannot change the frozen transport bytes.

The owner resolved the blocker on 2026-08-09 by authorizing public visibility
for the existing repository. Manual run `31297841419` deployed the pinned unit;
deployment `5815993749` and exact-browser verification passed. `PAGES-001` and
`VERIFY-001` are complete. The published population preview is not release
grade, and publication does not close the recorded Explorer UI findings.

For the complete-corpus track, `CORPUS-001`, `ACQPOL-001` and `POP-001` are complete.
The owner approved 293 named families, exhaustive-authority plus representative
and exception local coverage, GSS and applicable ODS identifiers, manual
link-only health acquisition, regulator-first private dependencies, sector
redress and role-based specialist review. The
[reference gaps](research/exhaustive-reference-gap-analysis.md) now have explicit
population-gate dispositions. Remaining boundaries concern reviewed freshness,
complete bilingual expression, optional future automation or external reviewer
appointments rather than missing population records.
The 293-family, seven-facet colour projection is complete and approved for
local evaluation; it does not claim leaf-service completeness.

The foundation and Explorer contract are complete. The three-slice migration,
shared authority/source infrastructure, `PACK-001` family-beginnings,
`PACK-002` learning-and-transition, `PACK-003` work-and-money, `PACK-004`
home/place/transport, `PACK-005` enforcement/consumer/justice, `PACK-006`
family/health/care, `PACK-007` civic/enterprise/creativity and `PACK-008`
mobility/later-life/death corpora are locally complete and supply the proving
fixtures, reusable identities and repeatable domain-register renderer for the
whole contracted population. The renderer preserves richer vertical-slice
dossiers when a later pack accounts for those approved identities.
The complete-corpus sequence is complete through `ASSURE-001`. The frozen local
candidate reconciles the 293 dossiers, 104 competency questions, source links,
provenance and six representative browser journeys. No population item remains
active. A later release-grade track may begin only with named reviewer
acceptance and current re-observation of applicable legal, clinical and
high-impact operational claims. The owner has separately authorized the frozen
population preview for publication without changing that review boundary.

Population-complete permits a visible `specialist_review_required` state.
Release grade separately requires named legal, clinical or service-owner
acceptance for affected high-impact claims.

The authorized publication scope is the population-complete educational
preview without a formal CPSV-AP, Open Referral, OWL or SHACL conformance claim.
It retains all 291 specialist-review warnings and does not claim release grade,
official-service status or personalised advice.

## GitHub Pages publication

GitHub Pages is the planned publication channel, but it is not an automatic
deployment target. Pushes, merges and pull requests must not trigger hosted
validation or Pages updates.

A publication request is a separate owner decision that identifies a frozen
candidate. The owner made that request for the population preview on
2026-08-08. The project may now enable and invoke only the manual Pages
deployment defined by the frozen publication manifest. Promotion must
publish the frozen candidate without rebuilding it. The exact deployed site
must then pass real-browser identity and journey checks before any public
bundle link is shared.

Before publication authorization, pull requests used this statement:

> Publication status: local validation only. GitHub Pages was not updated.
> Publication requires an explicit owner request.

This authorized publication pull request instead records the owner request and
frozen candidate. A follow-up evidence pull request must record the deployment
and browser-verification result. A failed verification remains failed and the
public link is withheld.

The 2026-08-09 verification passed, so the exact landing, descriptor, manifest
and Explorer URLs recorded in the publication evidence may now be shared.

The local 2026-08-08 UI-efficiency review also establishes two Explorer
follow-ups before question-answering acceptance can be claimed: bounded
handling of conversational or inflected query terms, and a life-course-domain
browse fallback when static search returns zero results.
