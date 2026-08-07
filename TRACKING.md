# Delivery tracking

Last updated: 2026-08-07

This is the current delivery ledger. Update it in the same pull request as the
work it tracks; [ROADMAP.md](ROADMAP.md) remains the phase-level view.

| ID | Delivery item | State | Evidence or next gate |
|---|---|---|---|
| BOOT-001 | Reviewed local initialization | Complete | Initialization commit `5572d0c`; deterministic local bundle and tests |
| OPS-001 | Standardize local execution on locked `uv` commands | Complete | Merged in PR #1; `make validate` is the local assurance entrypoint |
| GOV-001 | Establish planning, tracking and lockstep documentation | Complete | Merged in PR #1 with mandatory publication-status reporting |
| GOV-002 | Protect remote `main` for the sole-developer workflow | Deferred by platform | GitHub returned HTTP 403: private-repository branch protection requires GitHub Pro or public visibility; operational PR-only policy remains in force |
| PROF-001 | Approve `okf-domain-profile.v1` | Complete | Approved by `owner:chris-page-gov` on 2026-08-07; bounded source registration authorized |
| FIX-001 | Contract the three vertical-slice fixtures | Complete | Three synthetic v1 contracts approved with PROF-001 and validated locally |
| RIGHTS-001 | Resolve repository and bounded source-family licensing | Review | MIT for authored code, documentation and ontology terms; dated evidence for 16 source hosts plus OGL, CPSV-AP, Open Referral UK and HSDS; source use remains link-and-summary with zero snapshots |
| SLICE-001 | Missed rubbish collection | Complete | Merged in PR #3 with four local routes and a 13-reference denominator |
| SLICE-002 | Learning to drive and speeding exception | Complete | Merged in PR #4 with GB/NI learning routes, three speeding court boundaries and a 20-reference denominator |
| SLICE-003 | Death, Tell Us Once and estate administration | Review | Three registration routes, Tell Us Once/NI notification split and three estate-authority routes implemented with a 20-reference denominator; next gate is pull-request review |
| PUB-001 | Publish a frozen candidate to GitHub Pages | Blocked by design | Requires explicit owner publication request and all release gates |

## Current operating state

- GitHub remote: private repository under `chris-page-gov/okf-uk-living`.
- Main protection: PR-only by project policy; server enforcement is deferred
  because the current private-repository plan does not provide branch protection.
- Default evaluation: local `uv` environment only.
- Remote CI: disabled.
- GitHub Pages: not enabled and not updated.
- Acquisition: three bounded registers contain 53 official links and zero
  snapshots; all 16 registered hosts have dated rights decisions, source
  content remains link-and-summary only, and broad acquisition stays disabled.
- Licensing: repository-authored code, documentation, ontology terms and
  eligible generated projections are MIT; third-party material is not
  relicensed and snapshot redistribution is disabled.
- Public bundle URL: none.
