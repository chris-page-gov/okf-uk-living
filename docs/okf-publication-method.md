# OKF build and publication method

This repository adopts the
[OKF publication method v1](https://chris-page-gov.github.io/okf-explorer/profile/publication-method/v1/)
through [`okf.publication.json`](../okf.publication.json). The lifecycle
contract complements [`okf.semantic.json`](../okf.semantic.json): the semantic
contract says what the graph means, while the publication contract says how
reviewed source becomes checked and published bytes.

The adoption does not change the project's trust boundary. Validation remains
local by default. Pushes, pull requests and merges do not run routine remote CI
or publish GitHub Pages. Only the existing manual workflow may promote an
owner-authorised protected-main commit.

## Read the dependency graph

The contract declares three source families and eight ordered planes:

1. governed registers, policy and schemas enter the source plane;
2. Markdown and structured assertions produce semantic outputs;
3. the large corpus, browser handoff and Explorer descriptor form the runtime;
4. planning, evidence and guidance form the documentation plane;
5. the standalone Explore OKF and learning surfaces form the application;
6. assurance and file manifests freeze the release candidate;
7. the manual workflow transports those exact bytes; and
8. a live-browser journey verifies the deployed result.

Independent local checks may run in parallel when they do not write the same
output. Promotion remains serial because the release, deployment and browser
planes all depend on the same exact candidate. The shared workflow concurrency
group does not cancel an in-flight publication.

An unknown path does not become a cheap path by default. The shared Explorer
planner fails closed and selects the whole declared contract. This repository
retains its narrower, already governed documentation-overlay route only when
`scripts/check_documentation_only_change.py` proves the diff stays inside that
dependency graph.

## Avoid unnecessary rebuilds

Use the least costly route that proves the affected planes:

- for publication-method code and workflow changes, run the local method,
  lockstep and unit checks without rebuilding the frozen corpus;
- for a proved documentation-overlay change, use
  `BASE_REF=origin/main make validate-documentation-overlay`;
- for semantic, corpus, source, schema or generator changes, use the full
  locked build and validation sequence in [`AGENTS.md`](../AGENTS.md); and
- for deployment, use the manual workflow, which checks and copies the frozen
  base and authorised overlay instead of rebuilding either.

Never run a generator merely to make an unrelated check green. If an exact
deployed check fails, record the failure and diagnose the affected plane. It
does not authorise a new corpus build.

## Documentation lockstep

`scripts/check_documentation_lockstep.py` reads the paths in
`okf.publication.json`. A controlled change must include both:

- a declared documentation or governance file; and
- `CHANGELOG.md`.

The rule covers workflows, dependencies, source, generators, tests, generated
and publication-bound files. Dependency updates have no blanket exemption
because they may change release bytes. Run it against the worktree or a review
range:

```sh
uv run --locked python scripts/check_documentation_lockstep.py
uv run --locked python scripts/check_documentation_lockstep.py --base origin/main...HEAD
```

`scripts/check_publication_method.py` separately protects this repository's
manual-only policy, owner gate, non-cancelling serialisation, timeouts and
installed-Chrome requirement. The canonical Explorer schema and planner supply
the cross-repository validation; the local checker deliberately enforces only
repository-specific policy.

## Manual publication

The active workflow is `.github/workflows/pages-explore-okf.yml`. It requires:

- a full protected-main commit supplied as `publication_commit`;
- the explicit `EXPLORATORY-NOT-RELEASE-GRADE` acknowledgement;
- the dated owner decision in
  `evaluation/publication/explore-okf-review-authorization-2026-08-13.md`;
- the frozen base manifest and authorised additive-overlay manifest to pass;
  and
- transport of those exact files without corpus acquisition or regeneration.

The package job is bounded to 15 minutes and deployment to 10 minutes. Those
limits stop a stuck hosted process; they do not enable hosted validation for
ordinary repository activity.

## Live-browser gate

After the exact protected-main commit is deployed, use installed Google Chrome
with a cache-bypassed URL and record:

1. the workflow head commit and deployment identity;
2. SHA-256 identities for `publication-manifest.json`,
   `explore-okf-publication-manifest.json` and `okf-explorer.json`;
3. the root's independent exploratory warning and 293-family identity;
4. a search for `missed bin`, followed by **Report a missed rubbish
   collection**;
5. the ordinary and exception episodes, provenance and an official-source
   route; and
6. no browser-console errors.

Do not label a new URL verified until this evidence passes. The current served
manifests bind the frozen corpus and overlay, but they do not expose the latest
deployment commit as a served identity. An unattended post-deploy receipt
would therefore overstate exact-head proof unless the owner separately
authorises a new identity envelope and manifest re-freeze. That improvement is
backlogged; this adoption keeps the honest manual gate instead of simulating an
automated receipt.

## What this adoption does not change

- The 1,814-file base, large corpus, semantic graph, assurance evidence and
  publication manifests retain their existing bytes.
- Population completeness remains separate from specialist review and release
  grade.
- No source response bodies or personal data are acquired.
- No current authorisation is widened and no deployment is performed by the
  adoption pull request.
