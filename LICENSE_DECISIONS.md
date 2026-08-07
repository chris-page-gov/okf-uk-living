# Licensing decisions

Status: approved

Decision date: 2026-08-07

Decision owner: `owner:chris-page-gov`

Machine-readable record: [source/rights-decisions.v1.yaml](source/rights-decisions.v1.yaml)

These determinations set the rights boundary for local authoring and testing.
They do not authorize broad source acquisition, public repository visibility,
GitHub Pages deployment or publication of a bundle. Those actions still need
an explicit owner request and the applicable release checks.

## Repository-authored material

Repository-authored code is licensed under MIT. Repository-authored
documentation and ontology terms are also licensed under MIT. The evidence is
the owner's instruction dated 2026-08-07 and the repository's [LICENSE](LICENSE).

The MIT grant covers only original material authored for this repository. It
does not relicense official pages, third-party standards, logos, images,
personal data or other upstream expression. The generated bundle may be
distributed under MIT only while it contains repository-authored
representations and link-and-summary references, rather than redistributed
source content.

## Acquired source families

“Acquired” presently means a registered HTTPS reference. The three bounded
source registers contain 53 links and no downloaded snapshots. Every source
hostname is mapped to a dated evidence record in the rights register.

The operative policy is deliberately uniform even where a source permits
broader reuse: link to the authoritative page, summarize it in original words,
preserve source identity and observation time, and do not redistribute page
text or assets. A permissive source licence is evidence of what could be done;
it is not an instruction to copy material into this project.

The registered families are:

| Rights family | Registered providers | Determination |
|---|---|---|
| OGL v3.0 | GOV.UK and its agencies, legislation.gov.uk, Scottish Government, mygov.scot, COPFS, Scottish Courts, National Records of Scotland and nidirect | Text made available under OGL may be reused subject to attribution and exclusions; this project still uses links and original summaries only. |
| Coventry open-data terms / page-specific copyright | Coventry City Council | The council's open-data pages identify OGL v1.0, but that is not evidence that every service page is open data. The registered service pages remain link-and-summary only. |
| Provider copyright restrictions | City of Edinburgh Council and Belfast City Council | Their website terms reserve rights and restrict copying; no redistribution is authorized here. |
| Bespoke provider reuse | Local Government and Social Care Ombudsman | Website information may be reused only with source/copyright acknowledgement, accuracy, no amendment, no misleading use and no advertising-led use. This project uses only links and summaries. |
| SPSO website OGL | Scottish Public Services Ombudsman | The SPSO states that all website information is available through the OGL, subject to its conditions. |
| No open licence established | Cardiff Council, Public Services Ombudsman for Wales and Northern Ireland Public Services Ombudsman | No page-wide open reuse grant was established from the recorded official evidence. Default to links and original summaries; do not copy or redistribute. |

Evidence URLs and the observation date for each of the 16 host decisions are
recorded in `source/rights-decisions.v1.yaml`. An unavailable or ambiguous
licence is not interpreted as permission.

## Open Government Licence attribution

For OGL v3.0 material, the project must:

1. use any attribution statement specified by the information provider and,
   where possible, link both the source and the OGL;
2. otherwise use: “Contains public sector information licensed under the Open
   Government Licence v3.0.”;
3. keep a provider/source list when material from multiple providers is used;
4. avoid misleading use and any suggestion of official status or endorsement;
5. exclude personal data, unpublished material, logos, crests, the Royal Arms,
   third-party rights and other items excluded by the licence unless separate
   permission exists.

Evidence reviewed 2026-08-07: the official
[Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/)
and provider terms linked from the rights register. The required repository
notice is in [NOTICE.md](NOTICE.md).

## CPSV-AP

The CPSV-AP 3.2.0 specification states that all material is licensed under
[Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/)
unless stated otherwise and identifies the European Union as copyright owner.
If CPSV-AP material is reused, the project must give appropriate credit,
identify the title and source, link the licence, retain supplied notices and
indicate whether changes were made. Attribution must not imply endorsement.

Decision evidence reviewed 2026-08-07:
[CPSV-AP 3.2.0](https://semiceu.github.io/CPSV-AP/releases/3.2.0/) and the
[CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode).
The current project records a planned mapping reference only; it has not copied
the specification and does not claim CPSV-AP conformance.

## Open Referral UK and HSDS

The current Open Referral UK site is a UK profile of HSDS. Its official terms
state that most website content is under the OGL and that its GitHub code bases
are under “CC BY-SA”; those terms do not specify a Creative Commons version for
the GitHub repositories, so none is inferred. The GOV.UK Open Referral UK
description is itself published under OGL v3.0.

The current international HSDS governance documentation expressly uses
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Reuse requires
credit, a licence link, an indication of changes and ShareAlike licensing for
adapted material. Open Referral UK version 1 is deprecated and its archived
repository does not establish the rights of the current profile.

Decision evidence reviewed 2026-08-07:
[Open Referral UK terms](https://openreferraluk.org/info/terms),
[current profile governance](https://openreferraluk.org/about/50-governance),
[GOV.UK's Open Referral UK record](https://www.gov.uk/government/publications/open-standards-for-government/record-and-share-information-about-public-services-in-local-authorities),
[HSDS governance](https://docs.openreferral.org/en/3.1/about/specification-governance.html)
and the [CC BY-SA 4.0 legal code](https://creativecommons.org/licenses/by-sa/4.0/legalcode).

This project currently maps terminology in original words and links to the
standards. It does not redistribute their schemas or text, so no downstream
ShareAlike claim is made for repository-authored ontology terms.

## Snapshots and generated projections

No source snapshots have been acquired. A future snapshot must not be committed,
published or redistributed until a source-specific decision records the exact
licence, version, attribution, exclusions, acquisition time and checksum. The
current snapshot redistribution decision is therefore `false`.

Generated projections may be distributed under MIT when they contain only
repository-authored structure, original summaries, facts not protected by
copyright, and links. If a projection embeds upstream expression, its source
licence and attribution or ShareAlike conditions must be preserved and a new
compatibility decision recorded. Publication remains a separate owner gate in
all cases.
