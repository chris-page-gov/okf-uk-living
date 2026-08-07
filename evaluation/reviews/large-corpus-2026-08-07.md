# Large-corpus colour-facet review

Review ID: `LARGE-001/2026-08-07`

Decision date: 2026-08-07

Reviewer: `codex:root`, following owner approval

Result: **pass for local evaluation.**

This visible-browser review used OKF Explorer 0.5.7 at commit
`babd00c994ac8450480d1d4b128ccbe58f01cbe0` and the generated
`okf-explorer-large-corpus.v1` descriptor. It did not publish the repository,
enable CI, acquire source snapshots or redistribute upstream content.

## Contract and extent

- 293 uniquely named normalized service-family planning records;
- 24 life-course domains and acquisition waves of 96, 96 and 101 families;
- seven ordered colour facets: life-course domain, acquisition wave, delivery
  scope, jurisdiction research, implementation status, assertion status and
  rights state;
- 293 static-search result records plus filter postings for all seven facets;
- zero acquired resources, source snapshots or relationship assertions; and
- `publication_authorized: false` in the descriptor.

The reviewed descriptor SHA-256 is
`930b3624e172bb638c65200014b4e241d756bd23b59693a6abdd656f54f2bdbb`;
its data manifest SHA-256 is
`877d2048bfdac1ba468e7bb0cc7e3a50f829cf2a6527112a28a7537431952f09`;
and its static-search manifest SHA-256 is
`fc520bd92aa5085e5a631b7ef15021eb67a3671f0cbe950b90f9a25d8e7867c0`.

## Browser journeys

| Journey | Result | Evidence |
|---|---|---|
| Identity and overview | Pass | Explorer displayed `A Life in the UK — service-family planning denominator`, 293 service families, zero resources and zero relationships. |
| All colour facets | Pass | Switching to `All` displayed `7 of 7 facets shown`; every approved label was present. |
| Static search | Pass | `missed rubbish` returned exactly `Report missed rubbish collection`, with one shown of one matching record. |
| Search plus colour filter | Pass | `access` with `Acquisition wave: wave-3` returned five shown of five matching records and retained one active filter in the deep link. |
| Planning boundary | Pass | Overview notices state that records are not official assertions, source content is linked and summarized rather than redistributed, and GitHub Pages is not authorized. |

## Decision

`okf-explorer-large-corpus.v1` is approved for local evaluation and may support
staged corpus planning and gap review. It is not an exhaustive leaf-service
corpus, an eligibility or advice system, a publication candidate, or evidence
that a normalized family applies uniformly across UK jurisdictions.

Named legal and clinical reviewer appointments, any future health-provider
permission request for automation, and publication remain owner-dependent
follow-ups. They do not block continued link-only inventory and governed local
implementation.
