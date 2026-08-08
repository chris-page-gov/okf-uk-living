# Population-preview publication authorization — 2026-08-08

## Owner request

On 2026-08-08 `owner:chris-page-gov` explicitly instructed the project to:

> Ensure everything is merged, including any Explorer updates, then you are
> authorised to publish the GitHub Pages site and evaluate, including with OKF
> Explorer, the efficiency of the UI in answering questions.

## Reconciliation before publication

- `chris-page-gov/okf-uk-living` has no open pull requests; population assurance
  PR #22 is merged at `c8b13307e6278f54c89018c075f148781b7c5f44`.
- `chris-page-gov/okf-explorer` has no open pull requests.
- Explorer PR #71 (graph navigation and responsive controls) and PR #72
  (per-record narratives and typed source access) are merged.
- The Explorer Pages workflow succeeded for current `main` commit
  `20654abcf495e659bf6bb822762d32e2b9fa13d0` in run `31269794951`.

## Authorized scope

The authorized publication is the full 293-family population-complete preview,
not the superseded three-slice proposal. It remains educational and
navigational, not an official service, personalised advice, formal semantic
conformance claim or release-grade product. The 291 specialist-review warnings
remain visible.

The authorized candidate is
`life-course-population-complete-2026-08-08`; its candidate manifest SHA-256 is
`0b1df05a4eb440b9193d0906fbe2c071c6463bbe457f9a791472fee7f949b62e`.
The Pages publication manifest contains 1,549 files and records every exact
byte count and SHA-256 value. It includes no acquired source snapshot or source
response body.

Repository visibility is not authorized to change. If the current account
cannot publish Pages from the private repository, publication must stop for a
separate owner decision rather than making the repository public implicitly.

## Required completion evidence

After the publication workflow succeeds, record its run and deployment IDs,
verify the exact deployed landing, descriptor and manifest, and exercise
representative question journeys through search, details, Narrative, Graph,
Resources and official-source handoff in the currently deployed OKF Explorer.

## Deployment attempt

After publication PR #23 merged at
`980c7a9ec19ddd4161cefa348de689d179d1992b`, GitHub was asked to enable
workflow-based Pages for the unchanged private repository. The API returned
HTTP 422 with `Your current plan does not support GitHub Pages for this
repository.` No deployment was created, repository visibility was not changed,
and the public URL remains withheld.

The exact staging bytes and the merged Explorer were evaluated locally. The
[dated UI-efficiency review](../reviews/population-preview-ui-efficiency-2026-08-08.md)
records the passing keyword-led search-to-source journey and the open
natural-language search and zero-result browsing findings.
