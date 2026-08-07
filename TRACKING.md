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
| RIGHTS-001 | Resolve repository and bounded source-family licensing | Complete | Merged in PR #6 with 16 slice hosts; INVENTORY-001 and ACQPOL-001 extended dated decisions to 25 hosts while retaining link-and-summary use and zero snapshots |
| SLICE-001 | Missed rubbish collection | Complete | Merged in PR #3 with four local routes and a 13-reference denominator |
| SLICE-002 | Learning to drive and speeding exception | Complete | Merged in PR #4 with GB/NI learning routes, three speeding court boundaries and a 20-reference denominator |
| SLICE-003 | Death, Tell Us Once and estate administration | Complete | Merged in PR #5 with three registration routes, Tell Us Once/NI notification split, three estate-authority routes and a 20-reference denominator |
| REVIEW-001 | Integrated three-slice sample review | Complete: local pass | [2026-08-07 local review](evaluation/reviews/integrated-three-slice-2026-08-07.md) records passing Reader, query, graph-provenance, browser-source and licence-notice journeys; `REV-001` through `REV-004` are closed |
| COMPAT-001 | Lock the actual OKF Explorer consumer contract | Complete: local lock | Explorer 0.5.7, exact bundle bytes and all required journeys are recorded in [`okf-explorer-local.v1`](evaluation/compatibility/okf-explorer-local.v1.yaml) |
| INVENTORY-001 | Exhaustive external reference-family inventory | Complete | Owner authorized link-only discovery on 2026-08-07; 142 external reference records, 120 assessed domain/jurisdiction cells, 25 source-host rights decisions, 12 tracked gaps and zero snapshots |
| CORPUS-001 | Approve the staged 250–400 service-family denominator | Complete | Owner approved [`service-family-denominator.v1`](source/service-family-denominator.v1.yaml) on 2026-08-07: 293 named normalized families in three staged waves |
| ACQPOL-001 | Approve corpus acquisition and specialist-review policy | Complete | Local authority coverage, GSS/ODS identifiers, manual health links, regulator-first dependencies, sector redress and role-based review nominations approved on 2026-08-07 |
| LARGE-001 | Build and review the local colour-facet planning projection | Complete: local pass | [`okf-explorer-large-corpus.v1`](evaluation/reviews/large-corpus-2026-08-07.md) exposes 293 searchable planning records and seven reconciled facets with zero snapshots and publication disabled |
| SCOPE-001 | Approve first-sample claims and limitations | Planned | Recommended: three-slice educational sample with no formal semantic conformance claim |
| CAND-001 | Freeze a reproducible publication candidate | Blocked on review | Requires REVIEW-001, COMPAT-001 and SCOPE-001; record commit, bundle SHA-256 and local release evidence |
| PUB-001 | Authorize publication of the frozen candidate | Blocked by design | Requires explicit owner request naming a passing candidate commit and manifest hash |
| PAGES-001 | Deploy frozen candidate bytes to GitHub Pages | Blocked on authorization | Manual-only deployment after PUB-001; deployed bytes must match the candidate manifest without rebuilding |
| VERIFY-001 | Verify the exact public sample in a real browser | Blocked on publication | Validate identity, overview, bundle, slice records, query, graph, source and licence journeys before sharing the URL |
| RELEASE-001 | Hand off a verified initial sample | Blocked on verification | Label and share the public URL only after VERIFY-001 passes; retain explicit sample limitations |

## Current operating state

- GitHub remote: private repository under `chris-page-gov/okf-uk-living`.
- Main protection: PR-only by project policy; server enforcement is deferred
  because the current private-repository plan does not provide branch protection.
- Default evaluation: local `uv` environment only.
- Remote CI: disabled.
- GitHub Pages: not enabled and not updated.
- Acquisition: 89 exhaustive-inventory references plus 53 implemented-slice
  references give 142 external records and zero snapshots; all 25 source hosts
  and the standards families have dated rights decisions. Source content
  remains link-and-summary only. Staged link registration against the approved
  293 families is authorized; unbounded or unstaged acquisition stays disabled.
- Licensing: repository-authored code, documentation, ontology terms and
  eligible generated projections are MIT; third-party material is not
  relicensed and snapshot redistribution is disabled.
- Public bundle URL: none.
- Review state: the integrated local Explorer remediation rerun passed on
  2026-08-07 and `REV-001` through `REV-004` are closed. The 293-family
  colour-facet projection also passes local search and filter journeys. The
  sample is not a frozen publication candidate until `SCOPE-001` is approved.
- Reference readiness: all 120 declared domain/reference-jurisdiction cells are
  assessed (96 national covered, 24 local partial). The six requested owner
  decisions are complete; authority/regulator mapping and named specialist
  reviewer acceptance remain implementation or external-review work.
