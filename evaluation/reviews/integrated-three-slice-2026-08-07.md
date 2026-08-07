# Integrated three-slice Explorer review

Review ID: `REVIEW-001/2026-08-07`

Decision date: 2026-08-07

Reviewer: `codex:root`, following owner direction

Result: **pass for local review and Explorer compatibility. The four original
findings were remediated and closed in a visible-browser rerun. Publication
and candidate-freeze gates remain separate.**

This was a visible-browser review of the generated local bundle. It did not
publish the repository, enable CI or acquire new source material. The companion
[consumer record](../compatibility/okf-explorer-local.v1.yaml) fixes the exact
Explorer and bundle inputs used.

## Review inputs

| Input | Reviewed value |
|---|---|
| Repository baseline | `1077883fb7950c7f553472472aaaafa760701b42` (PR #7 merge) |
| Bundle | `okf-bundle.json`, SHA-256 `2371b1d3f17d521f0190ae9dd9457d5a26335bf872252a8f745fed1abcb88965` |
| Bundle identity | `A Life in the UK`; `okf-explorer-bundle.v0`; OKF `0.2` |
| Bundle extent | 78 nodes, 313 relationships, 281,493 bytes |
| Bundle generation | `scripts/build_okf_bundle.py` at `2026-08-07T00:00:00+01:00` |
| Explorer | `@okf/explorer` 0.5.7 at `babd00c994ac8450480d1d4b128ccbe58f01cbe0` |
| Browser | visible Codex in-app browser, 710 × 705 viewport |
| Origin | temporary loopback HTTP origin; not a publication URL |

The Explorer assets, bundle and authored Markdown/YAML handoff targets were
served from one temporary loopback origin. The page loaded with no browser
console warnings or errors. The local server returned HTTP 200 for the tested
authored source target even though direct Markdown navigation was blocked by
the target browser, as recorded in `REV-003`.

## Remediation rerun inputs

| Input | Rerun value |
|---|---|
| Repository implementation | `b36a574f55e3bbda0baaafd419712e0cee8738cf` on `codex/explorer-provenance-large-corpus` (stacked review; not a frozen candidate) |
| Bundle | `okf-bundle.json`, SHA-256 `8f39c38997cdc6048df60390dccecfafa43080d87b1ee209b2259315a7ea200a` |
| Bundle extent | 81 nodes, 318 relationships, 780,134 bytes |
| Browser handoffs | 103 deterministic HTML files |
| Explorer | `@okf/explorer` 0.5.7 at `babd00c994ac8450480d1d4b128ccbe58f01cbe0` |
| Origin | `127.0.0.1:8003` no-cache loopback overlay; not a publication URL |

## Consumer journeys

| Journey | Result | Evidence |
|---|---|---|
| Identity and overview | Pass | Explorer displayed `A Life in the UK`, the expected record types and all three citizen journeys. |
| Record deep link | Pass | Reload retained the selected death-and-bereavement record and query state. |
| Query: continuing service failure | Pass | Returned the missed-rubbish journey and exposed its complaint and ombudsman relationships. |
| Query: Motor insurer | Pass | Returned the private dependency and the composed driving journey. |
| Query: Tell Us Once | Pass | Returned the route, authority role, bereavement journey and Northern Ireland manual-notification exception. |
| Graph view | Pass on rerun | SVG graph rendered; the relationship panel displayed deterministic authored-link derivation, normalized assertion status and real-world scope with no unknown authority. |
| Authored source handoff | Pass on rerun | `Source ↗` opened a deterministic HTML rendering with the exact authored path; no Markdown/YAML navigation was browser-blocked. |
| Licence and notice | Pass on rerun | The first-class licensing record opened browser-safe MIT, OGL, CPSV-AP, Open Referral/HSDS, notice and rights-register handoffs. |

## Fixture traceability

| Fixture | Ordinary path | Exception path | Evidence, time and authority | Jurisdiction | Private dependency and redress | Result |
|---|---|---|---|---|---|---|
| Missed rubbish collection | Locate authority, check collection, classify, report and record outcome were readable. | Wrong authority, local timing, contamination, access, channel failure and continuing failure were explicit. | Source register and 2026-08-07 observation were displayed; four councils and four ombudsman routes were linked. | Coventry, Edinburgh, Cardiff and Belfast rules remained separate. | Contractor boundary and council-first complaint sequences were retained. | Pass in Reader; graph provenance finding remains. |
| Learning to drive and speeding | Provisional entitlement, practice, tests and licence handoff were ordered. | Notice identity, driver-information request, disposal and court branches were separated. | DVLA/DVSA and DVA roles, notice-specific timing and source register were displayed. | GB versus NI licensing and England/Wales, Scotland and NI court routes remained distinct. | Instructor and insurer were visibly private; legal/court handoffs did not predict outcomes. | Pass in Reader and query; graph provenance finding remains. |
| Death, bereavement and estate | Certification/investigation, registration, funeral, notification and estate stages were ordered. | Tell Us Once coverage, NI manual notification and disputed/complex estate boundaries were explicit. | Registrar/coroner, court and HMRC roles and the 2026-08-07 source observation were displayed. | England/Wales probate, Scottish confirmation and NI probate remained separate. | Funeral, notification and practitioner roles were private or conditional; official/court handoffs remained case-specific. | Pass in Reader and query; graph provenance finding remains. |

All three narratives were clearly labelled synthetic `editorial-example`
material, contained no real personal data and directed readers to current
official routes rather than deciding eligibility, liability, medical facts or
legal outcomes. The language was readable in the narrow viewport and controls
had visible names. This was a basic plain-language and operability review, not
an independent user study or a full WCAG audit.

## Finding ledger

| ID | Severity | State | Finding and evidence | Required disposition |
|---|---|---|---|---|
| `REV-001` | High | Closed 2026-08-07 | Relationships use `okf-relationship-assertion.v2` with stable IDs, assertion status/scope, authority, derivation, evidence and rights. The graph rerun showed `Deterministic authored-link projection · normalized · real-world` and zero unknown authorities. | Implemented and browser-verified. |
| `REV-002` | Medium | Closed 2026-08-07 | Every node carries node-level `generated.by` and `generated.at`. Explorer displayed `process:okf-bundle-builder` and `2026-08-07T00:00:00+01:00`. | Implemented and browser-verified. |
| `REV-003` | High | Closed 2026-08-07 | Deterministic `generated/browser/` HTML handoffs preserve authored identity and rewrite local links to browser-safe HTML. The curriculum source opened without `ERR_BLOCKED_BY_CLIENT`. | Implemented and browser-verified. |
| `REV-004` | High | Closed 2026-08-07 | `evidence/licensing-and-attribution.md` is a first-class record. Its source handoff opened `LICENSE`, `LICENSE_DECISIONS.md`, `NOTICE.md` and the machine rights register; OGL, CPSV-AP and Open Referral/HSDS terms were visible and none was blocked. | Implemented and browser-verified. |

The original failures remain preserved above as review history; their closed
states are based on implemented contracts and a fresh visible-browser rerun,
not a waiver. Search and filter state were also retested through the separate
large-corpus projection review.

## Gate decision

- `REVIEW-001`: **passed locally**; all four findings are closed.
- `COMPAT-001`: **locked for OKF Explorer 0.5.7 local evaluation**; identity,
  query, graph, provenance, source and notice journeys pass.
- `SCOPE-001`: remains the next owner review gate for the proposed bounded
  educational sample.
- `CAND-001`: remains blocked until scope is approved and a candidate is
  explicitly frozen with hashes.
- Publication: not requested and not performed.

The companion [large-corpus review](large-corpus-2026-08-07.md) records the
approved 293-family, seven-facet planning projection. Neither review authorizes
GitHub Pages or a public bundle URL.
