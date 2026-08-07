# Delivery tracking

Last updated: 2026-08-07

This is the current delivery ledger. Update it in the same pull request as the
work it tracks; [ROADMAP.md](ROADMAP.md) remains the phase-level view.

| ID | Delivery item | State | Evidence or next gate |
|---|---|---|---|
| BOOT-001 | Reviewed local initialization | Complete | Initialization commit `5572d0c`; deterministic local bundle and tests |
| OPS-001 | Standardize local execution on locked `uv` commands | In review | `uv sync --locked`, required checks and Makefile validation pass locally |
| GOV-001 | Establish planning, tracking and lockstep documentation | In review | `PLANNING.md`, this ledger and pull-request policy added with OPS-001 |
| PROF-001 | Approve `okf-domain-profile.v1` | Next | Owner review of scope, standards, authority, rights, freshness and consumer lock |
| FIX-001 | Contract the three vertical-slice fixtures | Queued | Begins after PROF-001 is approved |
| SLICE-001 | Missed rubbish collection | Queued | Requires FIX-001 and explicit local source scope |
| SLICE-002 | Learning to drive and enforcement exception | Queued | Requires FIX-001 and a frozen speeding-or-parking choice |
| SLICE-003 | Death, Tell Us Once and estate administration | Queued | Requires FIX-001 and four-nation exception boundaries |
| PUB-001 | Publish a frozen candidate to GitHub Pages | Blocked by design | Requires explicit owner publication request and all release gates |

## Current operating state

- GitHub remote: private repository under `chris-page-gov/okf-uk-living`.
- Default evaluation: local `uv` environment only.
- Remote CI: disabled.
- GitHub Pages: not enabled and not updated.
- Acquisition: disabled pending the domain profile and rights decisions.
- Public bundle URL: none.
