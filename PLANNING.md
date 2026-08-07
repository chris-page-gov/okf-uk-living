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
branch protection is deferred while the private repository plan does not
provide it; the repository must not be made public merely to obtain that
feature because public visibility is a separate owner decision.

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
2026-08-07. All three slices and the licensing decisions are merged. The first
integrated local Explorer review has been executed: the content journeys pass,
but four provenance, source-handoff and notice findings remain open. The sample
is reviewable, but it is not yet a frozen publication candidate.

The owner separately authorized exhaustive link-only reference-family
discovery on 2026-08-07. `INVENTORY-001` is complete with 138 external records,
120 assessed coverage cells and 12 actionable gaps. This planning asset does
not change the sample release gates or authorize snapshots, broad leaf
acquisition, CI or publication.

The active sequence is defined in the
[three-slice review and publication plan](docs/review-and-publication-plan.md):

1. Remediate or explicitly disposition `REV-001` through `REV-004` from the
   [2026-08-07 review](evaluation/reviews/integrated-three-slice-2026-08-07.md).
2. Rerun `REVIEW-001` and lock `COMPAT-001` against the same required Reader,
   query, graph, deep-link, source and notice journeys.
3. `SCOPE-001` — approve the initial sample claim and limitations boundary.
4. `CAND-001` — freeze one locally validated candidate and its hashes.
5. `PUB-001` — await an explicit owner publication request naming that
   candidate.
6. `PAGES-001` and `VERIFY-001` — deploy identical bytes manually and verify
   the exact site in a real browser.

For the later complete-corpus track, the next owner gate is `CORPUS-001`:
approve a staged 250–400 service-family denominator and disposition the local
topology, health-permission, private-dependency, redress, freshness, bilingual
identity and large-corpus Explorer gaps in the
[reference gap analysis](research/exhaustive-reference-gap-analysis.md).

The recommended release scope is the bounded three-slice educational sample
without a formal CPSV-AP, Open Referral, OWL or SHACL conformance claim. This
keeps the complete curriculum and governed semantic registry out of the first
sample publication while stating their absence clearly.

## GitHub Pages publication

GitHub Pages is the planned publication channel, but it is not an automatic
deployment target. Pushes, merges and pull requests must not trigger hosted
validation or Pages updates.

A publication request is a separate owner decision that identifies a frozen
candidate. Only after that request may the project enable or invoke a Pages
deployment, and only after the domain profile, source inventory, rights
decisions, evaluation journeys and candidate checks pass. Promotion must
publish the frozen candidate without rebuilding it. The exact deployed site
must then pass real-browser identity and journey checks before any public
bundle link is shared.

After every pull request, use one of these statements in the handoff:

> Publication status: local validation only. GitHub Pages was not updated.
> Publication requires an explicit owner request.

For an explicitly requested publication pull request, replace it with a record
of the request, frozen candidate, deployment result and browser-verification
result. A failed verification remains failed and the public link is withheld.
