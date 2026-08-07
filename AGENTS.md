# Repository Instructions

This repository publishes **A Life in the UK**, a citizen-centred Open
Knowledge Format bundle about public services, rights, responsibilities and
life events from before birth to death and bereavement.

## Working rules

- Treat Markdown and files under `source/` as authored source of truth.
- Keep links as browser-compatible Markdown links. Do not use Obsidian-only
  wikilinks.
- Every non-index OKF concept must declare non-empty `type`, `title` and
  `description` frontmatter.
- Preserve official source identity, jurisdiction, observation time,
  derivation and limitations. Similar labels never establish identity.
- Distinguish `official`, `normalized`, `inferred` and `editorial-example`
  assertions. Never present generated relationships as official claims.
- Do not encode real personal data. Personas and service episodes must be
  synthetic and clearly labelled.
- Do not turn the bundle into a personalised eligibility, medical or legal
  decision engine. Link readers to the current authoritative service.
- Model UK-wide, England, Scotland, Wales, Northern Ireland and local variants
  explicitly. A GOV.UK route is not evidence that one process applies
  uniformly across all four nations.
- Do not edit `generated/`, `okf-bundle.json` or release evidence by hand;
  rebuild them from authored inputs.
- Do not add `.DS_Store`, Word lock files, `_site/`, virtual environments,
  caches or temporary output to Git.
- Preserve unrelated work and use focused feature branches and pull requests
  after the reviewed initialization commit.
- Keep implementation and its planning, tracking, status, changelog and
  authoring documentation in the same pull request, following `PLANNING.md`.
- Keep CI disabled until the bootstrap and domain profile are reviewed.
- Never create remotes, push, publish, enable CI or spend money implicitly.

## Required checks

If OKF Markdown changes, run:

```sh
uv run --locked python scripts/build_okf_bundle.py
uv run --locked python scripts/build_okf_bundle.py --check
uv run --locked python scripts/check_okf.py
uv run --locked python scripts/check_contracts.py
uv run --locked python scripts/check_sources.py
uv run --locked python -m unittest discover -s tests
```

Before any publication change, also validate the approved domain profile,
source inventory, rights decisions, evaluation journeys and frozen candidate.

Never provide a public bundle URL until that exact deployed URL passes a
real-browser identity and journey check. A failed public verification is
reported as failed and the link remains labelled unverified; it does not
silently trigger a release rebuild.

Local checks are the default and only evaluation environment. Pull requests,
pushes and merges must not trigger remote CI or GitHub Pages updates. After
every pull request, state that GitHub Pages was not updated and requires an
explicit owner publication request, unless that pull request records such a
request and its deployment and browser-verification evidence.

## Initial modelling priority

Implement three vertical slices before expanding the corpus:

1. missed rubbish collection;
2. learning to drive through a speeding or parking exception; and
3. death and bereavement through Tell Us Once and estate administration.

These slices must exercise ordinary paths, exceptions, evidence, time,
jurisdiction, authority, required private-sector dependencies and redress.
