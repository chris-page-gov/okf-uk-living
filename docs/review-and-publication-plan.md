# Population-preview review and publication plan

Status: population-preview publication authorized

Plan date: 2026-08-07

Owner: `owner:chris-page-gov`

This is the governed path from the implemented corpus to a verified GitHub
Pages publication. The owner authorized the full population-complete
preview on 2026-08-08. Deployment remains manual-only and exact-byte verified;
the authorization does not make the preview release-grade.

## Current baseline

The population candidate contains 293 service families across 24 domains and
48 enclosing processes, with 9,757 concepts, 879 typed official links and
15,810 governed relationships. Population assurance reconciles 104 competency
questions, six visible Explorer journeys and zero blocking omissions or source
snapshots. Its exact local data-plane bytes were frozen in PR #22.

The publication unit adds only an original landing page and publication
envelope. Its comprehensive manifest freezes all 1,549 served files and their
exact byte counts; the Pages transport verifies and copies them without running
a corpus generator.

## Authorized first publication

The owner superseded the earlier three-slice recommendation with the **full
population-complete educational preview**. It contains all 293 families and
their governed data plane, while explicitly recording that:

- the publication makes no CPSV-AP, Open Referral, OWL or SHACL conformance
  claim;
- normalized and inferred relationships remain visibly distinct from official
  claims;
- the content is educational and navigational, not current individual advice;
- all source denominators, gap dispositions and specialist-review warnings
  remain visible; and
- no source content or snapshot is redistributed.

The publication is useful for discovery and interface evaluation without
claiming release grade. A later formal semantic or operational release remains
a separate review track.

## Delivery gates

| Order | Tracking ID | Bounded output | Acceptance gate |
|---|---|---|---|
| 1 | `REVIEW-001` | Integrated three-slice review report and finding ledger | Each fixture dimension and competency question is traced to the bundle; authority, jurisdiction, exception, evidence, time, private dependency, redress, provenance and plain-language boundaries pass; no blocking finding remains open. |
| 2 | `COMPAT-001` | Actual OKF Explorer consumer inventory and locked compatibility contract | The local candidate loads in the target Explorer; overview, record, query and graph journeys are tested; required fields and deep-link behaviour are versioned; unsupported features are recorded rather than assumed. |
| 3 | `SCOPE-001` | Owner-approved sample release-scope and limitations decision | The release is explicitly either the recommended non-conformance sample or a conformance-bearing release with the required predicate and shape work completed. |
| 4 | `CAND-001` | Frozen candidate manifest and local release evidence | One commit and bundle are identified by SHA-256; `make validate`, rights, source, fixture and review evidence pass; notices and version metadata are included; promotion requires no rebuild. |
| 5 | `PUB-001` | Explicit owner publication request naming the candidate | The request identifies the candidate commit and manifest hash and authorizes the necessary GitHub Pages configuration or update. |
| 6 | `PAGES-001` | Manual-only GitHub Pages deployment of the frozen bytes | Deployment has no push-triggered evaluation or automatic publication; the deployed bytes match the frozen manifest; deployment result and exact URL are recorded. |
| 7 | `VERIFY-001` | Real-browser production verification report | The exact public overview, bundle identity, one record per slice, query and graph journeys pass; source and licence notices resolve; failures remain failures and the URL stays unverified. |
| 8 | `RELEASE-001` | Verified release handoff | Only after `VERIFY-001` passes is the public URL labelled verified and shared as the initial sample. |

## Integrated review contents

The integrated slice reviews and population assurance produced durable evidence
under `evaluation/` and covered:

1. one ordinary and one exception journey for each slice;
2. cross-slice checks for assertion status, source identity and evidence
   lineage;
3. the four-nation and local-authority boundaries exercised by the sample;
4. current-source handoff and stale-information warnings;
5. private dependencies without provider recommendation;
6. accessibility and plain-language review of the educational narrative; and
7. a finding ledger with severity, disposition, reviewer and decision date.

Changes needed to resolve findings remain focused pull requests with full local
validation. Review findings do not authorize source snapshots, leaf-source
acquisition or corpus expansion. The separate 2026-08-07 owner instruction
authorizes only the exhaustive reference-family inventory of links, rights
evidence and original summaries recorded in
[`source/exhaustive-reference-inventory.v1.yaml`](../source/exhaustive-reference-inventory.v1.yaml).

The first run, remediation rerun, eight pack reviews and population assurance
are recorded under `evaluation/reviews/`. `REVIEW-001`, `COMPAT-001`,
`SCOPE-001`, `CAND-001`, `PUB-001`, `PAGES-001`, `VERIFY-001` and the verified
preview handoff are complete. The 2026-08-09 deployment evidence records the
exact public identities and remaining non-release-grade boundary.

## Candidate and publication controls

- Build the candidate once from an identified commit.
- Record hashes before requesting publication.
- Promote the same files; never rebuild during deployment.
- Keep remote CI disabled. If GitHub Actions is selected solely as the Pages
  transport, it must be manual-only and consume the frozen artefact.
- Repository visibility may change only through a separate explicit owner
  decision. The owner made that decision on 2026-08-09; it did not authorize
  automatic publishing or a different candidate.
- Do not label or share a deployed URL as verified until `VERIFY-001` passes in
  a real browser.
- Repository-authored static review documents may be added through the
  validated documentation overlay without rebuilding the frozen corpus. The
  documentation-only dependency gate must pass, the additive manifest must
  bind the rendered bytes, and deployment remains an explicit exact-head manual
  operation followed by the same browser gate.

## Completion definitions

- **Population-complete candidate:** achieved in PR #22.
- **Publication candidate:** achieved when this exact-byte manifest and
  manual-only workflow pass review on `main`.
- **Published preview:** achieved only after the authorized Pages deployment
  and successful real-browser verification; achieved on 2026-08-09.
- **Release grade:** remains a later gate requiring named specialist acceptance
  and current source re-observation for applicable claims.
