# Three-slice review and publication plan

Status: active

Plan date: 2026-08-07

Owner: `owner:chris-page-gov`

This is the bounded path from the implemented three-slice sample to a verified
GitHub Pages publication. It does not authorize publication. Local work may
advance through candidate freezing; enabling or updating GitHub Pages still
requires an explicit owner request naming the frozen candidate.

## Current baseline

The sample has completed its first integrated local review. Main contains:

- the approved domain profile and three synthetic fixture contracts;
- missed rubbish collection, learning to drive through speeding enforcement,
  and death and bereavement through estate administration;
- 78 OKF nodes and 313 relationships;
- 53 linked official references across 16 rights-mapped hosts;
- zero source snapshots;
- MIT licensing for repository-authored code, documentation and ontology
  terms; and
- deterministic locked-`uv` generation and 44 local tests.

The [2026-08-07 review](../evaluation/reviews/integrated-three-slice-2026-08-07.md)
passed the three Reader/query content journeys and recorded the exact Explorer
0.5.7 consumer and bundle bytes. It did not pass the release gate: relationship
authority/provenance, node build-provenance presentation, browser-renderable
source handoffs and licence-notice verification remain open. No candidate or
publication bytes have been frozen.

## Intended first publication

The recommended first publication is an **initial three-slice educational
sample**, not the complete life-course atlas. It can be published before the
full curriculum, cross-domain predicate registry and SHACL shapes only if the
release-scope decision explicitly records that:

- the publication makes no CPSV-AP, Open Referral, OWL or SHACL conformance
  claim;
- normalized and inferred relationships remain visibly distinct from official
  claims;
- the content is educational and navigational, not current individual advice;
- all three source denominators and known omissions remain visible; and
- broader source acquisition and corpus expansion remain out of scope.

That is the shortest responsible route to a useful reviewable publication. A
decision to claim formal semantic conformance would instead bring the governed
predicate registry and validation shapes into the release-critical path.

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

`REVIEW-001` is the next implementation step and can begin locally without a
publication request. It will produce durable evidence under `evaluation/` and
cover:

1. one ordinary and one exception journey for each slice;
2. cross-slice checks for assertion status, source identity and evidence
   lineage;
3. the four-nation and local-authority boundaries exercised by the sample;
4. current-source handoff and stale-information warnings;
5. private dependencies without provider recommendation;
6. accessibility and plain-language review of the educational narrative; and
7. a finding ledger with severity, disposition, reviewer and decision date.

Changes needed to resolve findings remain focused pull requests with full local
validation. Review findings do not authorize broad source acquisition.

The first run is recorded under `evaluation/reviews/`. `REVIEW-001` remains in
progress until `REV-001` through `REV-004` are remediated or explicitly
dispositioned and the affected Explorer journeys pass on rerun. The companion
consumer record under `evaluation/compatibility/` is evaluated but not locked.

## Candidate and publication controls

- Build the candidate once from an identified commit.
- Record hashes before requesting publication.
- Promote the same files; never rebuild during deployment.
- Keep remote CI disabled. If GitHub Actions is selected solely as the Pages
  transport, it must be manual-only and consume the frozen artefact.
- Do not enable Pages, change repository visibility, create a public URL or
  invoke a deployment before `PUB-001`.
- Do not label or share a deployed URL as verified until `VERIFY-001` passes in
  a real browser.

## Completion definitions

- **Reviewable sample:** achieved on main after PRs #5 and #6.
- **Publication candidate:** achieved after `REVIEW-001`, `COMPAT-001`,
  `SCOPE-001` and `CAND-001` pass.
- **Published sample:** achieved only after the owner request, exact-byte Pages
  deployment and successful real-browser verification.
- **Complete life-course atlas:** a later roadmap outcome; it is not required
  for the bounded initial sample.
