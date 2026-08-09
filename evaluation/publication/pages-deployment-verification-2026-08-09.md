# GitHub Pages deployment verification — 2026-08-09

## Result

The owner-authorized 293-family population-complete preview is published and
verified. GitHub Pages serves the exact 1,549-file unit frozen at publication
merge `980c7a9ec19ddd4161cefa348de689d179d1992b`. The repository is public and
the complete source and history are visible, as separately authorized by the
owner on 2026-08-09.

The preview remains educational and navigational, not an official service,
personalised advice or a release-grade corpus. All 291 specialist-review
warnings remain part of the publication contract.

## Owner visibility decision

On 2026-08-09 `owner:chris-page-gov` instructed the project to:

> Make the existing okf-uk-living repository public, exposing its complete
> source and history.

GitHub subsequently reported repository visibility `PUBLIC` and
`isPrivate: false`. No separate publication repository was created.

## Deployment identity

- Workflow: `Publish GitHub Pages`
- Workflow run: [31297841419](https://github.com/chris-page-gov/okf-uk-living/actions/runs/31297841419)
- Trigger: manual `workflow_dispatch`
- Workflow head: `f50e1a141af8a0c8e712b3056432c0c566a6759f`
- Frozen publication source: `980c7a9ec19ddd4161cefa348de689d179d1992b`
- Package job: `93205721997`, success
- Deploy job: `93205740600`, success
- GitHub deployment: `5815993749`
- Successful deployment status: `16567106942`
- HTTPS enforcement: enabled

## Exact-byte verification

The deployed `publication-manifest.json` has SHA-256
`63be5185e0302c367afd338518c550adf5d453e1812ff12c784db8973be9bb1f` and
declares:

- candidate `life-course-population-complete-2026-08-08`;
- 1,549 files;
- 178,842,389 bytes;
- `release_grade: false`;
- `source_snapshots_acquired: false`; and
- no retained source response bodies.

The downloaded landing page and Explorer descriptor matched their manifest
entries exactly:

| Target | SHA-256 | Result |
|---|---|---|
| `index.html` | `584ded105f3eeded3b12410289ab3596b5dbf28e2ad610617f12480717ef1be6` | pass |
| `okf-explorer.json` | `99cb2b86a495c0091f4bfab548025dd872a10197cde02381ce7d023d04329e3e` | pass |

The public descriptor records owner publication authorization, candidate
manifest SHA-256
`0b1df05a4eb440b9193d0906fbe2c071c6463bbe457f9a791472fee7f949b62e`,
291 specialist-review warnings and `release_grade: false`.

## Real-browser verification

The exact public landing opened as `A Life in the UK — population-complete
preview` and displayed 293 service families, 24 life-course domains, 48
enclosing processes and 879 official source links.

The public Explorer URL loaded the published descriptor and displayed 9,757
concepts, 879 resources and 15,810 corpus relationships. The representative
journey passed:

1. `missed bin collection` returned `Report a missed rubbish collection` first
   among four matches.
2. Narrative placed the family within `Manage household waste collections`,
   showed its before/following steps, exception route and four local variants.
3. Graph displayed 37 directly related relationships, including process,
   episode, jurisdiction, provider, redress and source support.
4. Resources displayed 13 official links across GOV.UK, selected councils and
   the four public-service complaint bodies.
5. The GOV.UK handoff opened as `Report a missed bin collection - GOV.UK`.

The previously recorded UI-efficiency findings remain open. In particular,
conversational queries can be over-constrained, zero-result searches remove
domain browsing, and the frozen pre-authorization overview notice is confusing
when shown beneath the later publication envelope. Publication does not close
or conceal those findings.

## Verified public entry points

- [Population-preview landing](https://chris-page-gov.github.io/okf-uk-living/)
- [Published Explorer descriptor](https://chris-page-gov.github.io/okf-uk-living/okf-explorer.json)
- [Exact publication manifest](https://chris-page-gov.github.io/okf-uk-living/publication-manifest.json)
- [OKF Explorer with the published bundle](https://chris-page-gov.github.io/okf-explorer/?bundle=https%3A%2F%2Fchris-page-gov.github.io%2Fokf-uk-living%2Fokf-explorer.json#overview)

## Main protection

After publication, `main` was protected for the sole-developer workflow:

- pull requests required;
- zero approving reviews required;
- administrators included;
- conversation resolution required;
- force-pushes and branch deletion disabled; and
- no required remote status checks, preserving the local-only testing policy.

The manual Pages workflow remains the only authorized hosted action. Ordinary
pull requests and merges do not deploy the site.
