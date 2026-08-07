# Integrated three-slice Explorer review

Review ID: `REVIEW-001/2026-08-07`

Decision date: 2026-08-07

Reviewer: `codex:root`, following owner direction

Result: **content journeys pass; release gate remains open because four
compatibility and provenance findings require remediation or an explicit
disposition.**

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

## Consumer journeys

| Journey | Result | Evidence |
|---|---|---|
| Identity and overview | Pass | Explorer displayed `A Life in the UK`, the expected record types and all three citizen journeys. |
| Record deep link | Pass | Reload retained the selected death-and-bereavement record and query state. |
| Query: continuing service failure | Pass | Returned the missed-rubbish journey and exposed its complaint and ombudsman relationships. |
| Query: Motor insurer | Pass | Returned the private dependency and the composed driving journey. |
| Query: Tell Us Once | Pass | Returned the route, authority role, bereavement journey and Northern Ireland manual-notification exception. |
| Graph view | Partial | SVG graph rendered and retained its selected record after reload, but relationship provenance/authority was unknown. |
| Authored source handoff | Fail | The local target existed and returned HTTP 200, but direct Markdown navigation produced `net::ERR_BLOCKED_BY_CLIENT` in the target browser. |

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
| `REV-001` | High | Open; blocks `REVIEW-001` and `COMPAT-001` | Generated edges contain only source, target, kind and label. In the expanded graph the Explorer displayed 42 instances of `Authority not declared · unknown`, so the graph cannot demonstrate assertion authority or relationship provenance. | Version edge assertion/provenance fields in the domain projection and lock how Explorer consumes them, or explicitly reduce the release claim and record why the graph remains sufficient. |
| `REV-002` | Medium | Open; blocks provenance acceptance | Bundle-level `generated_by` and `generated_at` are present, but the selected node panels displayed both values as `Not declared`; the consumer does not expose inherited build provenance. | Add node-level build provenance or make the Explorer display the authoritative bundle-level values, then retest. |
| `REV-003` | High | Open; blocks source-handoff and publication verification | `Source ↗` resolved to the correct local Markdown path and that target returned HTTP 200, but visible navigation in the target in-app browser failed with `net::ERR_BLOCKED_BY_CLIENT`. | Provide a browser-renderable source route or other compatible handoff and rerun it in the target browser. |
| `REV-004` | High | Open; blocks licence-notice verification | The Evidence record renders relative links to `LICENSE_DECISIONS.md` and the rights register, but neither is a first-class bundle record and `NOTICE.md` is only an indirect handoff. Visible navigation to both tested Markdown/YAML targets failed with `net::ERR_BLOCKED_BY_CLIENT`, so the Explorer cannot yet prove that licence and attribution notices resolve. | Add an explicit bundle/site licence and notice surface, retain OGL/provider attribution, and verify it in the target browser. |

Decision for all four findings: retain them as real failures; do not waive them
silently, freeze a candidate or publish. Search state persistence after clearing
a query was also inconsistent once during the run; it is recorded as an
observation for retest but is not currently a release blocker.

## Gate decision

- `REVIEW-001`: executed, **not passed**; the slice content is reviewable but
  `REV-001` through `REV-004` remain open.
- `COMPAT-001`: evidence captured, **not locked**; record, query and graph deep
  links work, but the provenance, source and notice surfaces are incomplete.
- `SCOPE-001` and `CAND-001`: do not start until the findings are remediated or
  explicitly dispositioned and the review is rerun.
- Publication: not requested and not performed.

The next bounded implementation step is a focused provenance-and-handoff
remediation: define the edge and node build-provenance contract, expose licence
and attribution metadata, and make source/notice links browser-renderable. The
same local Explorer journeys must then be rerun against the resulting bundle.
