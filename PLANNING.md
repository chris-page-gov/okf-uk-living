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
| Publication state | `TRACKING.md`, `REPOSITORY_STATUS.md`, `CHANGELOG.md` and release evidence |

The pull-request description must explain either which documents changed or
why a listed document is unaffected. Documentation follow-up is not deferred
to a later pull request.

## Near-term delivery units

The owner approved `okf-domain-profile.v1` and the three fixture contracts on
2026-08-07. The active delivery sequence is now:

1. Register the bounded source families for missed rubbish collection.
2. Implement and validate the missed-rubbish-collection slice.
3. Implement and validate the learning-to-drive and enforcement slice.
4. Implement and validate the death, Tell Us Once and estate-administration
   slice.
5. Review the three implemented slices before broader source acquisition or
   corpus growth.

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
