# A Life in the UK

A citizen-centred Open Knowledge Format (OKF v0.2) bundle about public
services, rights, responsibilities and life events across the United Kingdom,
from before birth to death and bereavement.

Status: **full 293-family population implementation authorized and contracted**.
The Reader, query, graph provenance, browser source handoff and licence-notice
journeys pass in OKF Explorer 0.5.7. The approved 293-family local projection
also exposes seven reconciled colour facets and static search. The
`life-course-population-contract.v1` contract now governs eight delivery packs,
48 enclosing processes and the distinction between population-complete and
specialist-reviewed release grade. One hundred and forty-eight reviewed families now expose authored
narratives, typed official links and governed journey graphs; the other
families remain explicit planning records. The shared infrastructure now adds
397 dated GSS geographies, 438 reusable authority/regulator/redress records,
ten sector maps and metadata-only source-link receipts. This is not an official service
corpus or publication candidate. The GitHub
repository is private; validation remains local-only, snapshots, unbounded or unstaged leaf
acquisition and CI remain disabled, and publication requires a separate
explicit owner request.

## Start here

- [Research overview and generating prompt](research/overview.md)
- [Exhaustive reference-family inventory and gap analysis](research/exhaustive-reference-gap-analysis.md)
- [Approved corpus acquisition and review decisions](research/corpus-acquisition-decisions.md)
- [OKF bundle root](index.md)
- [Implementation roadmap](ROADMAP.md)
- [Delivery planning](PLANNING.md)
- [Delivery tracking](TRACKING.md)
- [Three-slice review and publication plan](docs/review-and-publication-plan.md)
- [2026-08-07 integrated Explorer review](evaluation/reviews/integrated-three-slice-2026-08-07.md)
- [Local Explorer input record](evaluation/compatibility/okf-explorer-local.v1.yaml)
- [Large-corpus local review](evaluation/reviews/large-corpus-2026-08-07.md)
- [Three-slice population migration review](evaluation/reviews/three-slice-population-migration-2026-08-08.md)
- [Shared authority and source infrastructure review](evaluation/reviews/shared-authority-source-infrastructure-2026-08-08.md)
- [Pack 1 family-beginnings review](evaluation/reviews/pack-1-family-beginnings-2026-08-08.md)
- [Pack 2 learning-and-transition review](evaluation/reviews/pack-2-learning-transition-2026-08-08.md)
- [Pack 3 work-and-money review](evaluation/reviews/pack-3-work-money-2026-08-08.md)
- [Pack 4 home/place/transport review](evaluation/reviews/pack-4-home-place-transport-2026-08-08.md)
- [`okf-domain-profile.v1` review handoff](profiles/okf-domain-profile.v1.md)
- [Three vertical-slice fixture contracts](evaluation/fixtures/README.md)
- [Missed rubbish collection journey](journeys/missed-rubbish-collection.md)
- [Learning to drive through a speeding exception](journeys/learning-to-drive-speeding.md)
- [Death and bereavement through estate administration](journeys/death-bereavement-estate.md)
- [Missed rubbish linked-reference register](source/missed-rubbish-collection.v1.yaml)
- [Driving and speeding linked-reference register](source/learning-to-drive-speeding.v1.yaml)
- [Death, bereavement and estate linked-reference register](source/death-bereavement-estate.v1.yaml)
- [Machine-readable exhaustive reference inventory](source/exhaustive-reference-inventory.v1.yaml)
- [Approved 293-family denominator](source/service-family-denominator.v1.yaml)
- [Full-population implementation contract](profiles/life-course-population-contract.v1.yaml)
- [48 enclosing-process denominator](source/life-course-processes.v1.yaml)
- [Migrated life-course family dossiers](source/life-course-families/)
- [Compact domain source registers](source/domain-registers/)
- [Current authority and geography registry](source/authority-registry.v1.yaml)
- [Reviewed shared regulator and redress seeds](source/shared-authority-seeds.v1.yaml)
- [Governed predicate registry](ontology/governed-predicates.v1.yaml)
- [Corpus acquisition policy](profiles/corpus-acquisition-policy.v1.yaml)
- [Repository status](REPOSITORY_STATUS.md)
- [Authoring and validation guide](docs/authoring.md)
- [Licensing decisions](LICENSE_DECISIONS.md)
- [Attribution and third-party notices](NOTICE.md)
- [Change log](CHANGELOG.md)

## Repository shape

| Path | Purpose |
|---|---|
| `research/` | Evidence-backed research, scope and design decisions |
| `curriculum/` | Beginner-readable educational sequence |
| `ontology/` | Classes, predicates, controlled terms and validation model |
| `life-course/` | Chronological spine and cross-life situations |
| `journeys/` | End-to-end citizen journeys and exception paths |
| `services/` | Canonical service-family descriptions |
| `jurisdictions/` | UK, national and local applicability boundaries |
| `organisations/` | Public authorities and other delivery actors |
| `evidence/` | Source and claim evidence indexes |
| `source/` | Authored inputs and immutable acquired source envelopes |
| `schemas/` and `shapes/` | Family, link-receipt and semantic validation contracts |
| `generated/` | Reproducible output boundary; never edit by hand |
| `evaluation/` | Competency questions, journeys and acceptance evidence |

## Local commands

Install [uv](https://docs.astral.sh/uv/getting-started/installation/). Project
dependencies are declared in `pyproject.toml` and pinned by `uv.lock`; `uv run`
creates and maintains the local environment automatically.

```sh
uv sync --locked
```

Build and verify the bundle:

```sh
uv run --locked python scripts/render_life_course_packs.py
uv run --locked python scripts/render_life_course_packs.py --check
uv run --locked python scripts/build_browser_handoff.py
uv run --locked python scripts/build_browser_handoff.py --check
uv run --locked python scripts/build_okf_bundle.py
uv run --locked python scripts/build_okf_bundle.py --check
uv run --locked python scripts/check_okf.py
uv run --locked python scripts/check_contracts.py
uv run --locked python scripts/check_sources.py
uv run --locked python scripts/check_inventory.py
uv run --locked python scripts/check_service_denominator.py
uv run --locked python scripts/check_corpus_policy.py
uv run --locked python scripts/check_population_contract.py
uv run --locked python scripts/check_domain_registers.py
uv run --locked python scripts/check_life_course_dossiers.py
uv run --locked python scripts/check_authority_registry.py
uv run --locked python scripts/check_rights.py
uv run --locked python scripts/build_large_corpus.py
uv run --locked python scripts/build_large_corpus.py --check
uv run --locked python scripts/check_large_projection.py
uv run --locked python scripts/check_search_acceptance.py
uv run --locked python -m unittest discover -s tests
```

`make validate` runs the same required sequence. Validation is local-only by
default; pull requests and merges do not run remote CI or update GitHub Pages.

The generated entrypoints are `okf-bundle.json` for the reviewed three-slice
bundle and `okf-explorer.json` for the 293-family discovery projection. The
large descriptor distinguishes 293 service families from the larger typed
concept count, currently 5,567 concepts, and exposes generated semantic and
validation entrypoints. Records and static-search results are sharded in
1,000-record chunks so supporting infrastructure remains lazily hydratable. With a
local OKF Explorer build at `../okf-explorer/_site`, start the no-cache overlay:

```sh
uv run --locked python scripts/serve_local_explorer.py --port 8003
```

Open the small bundle at
`http://127.0.0.1:8003/?bundle=http%3A%2F%2F127.0.0.1%3A8003%2Fokf-bundle.json`
or the colour-facet planning projection at
`http://127.0.0.1:8003/?bundle=http%3A%2F%2F127.0.0.1%3A8003%2Fokf-explorer.json`.
These are loopback review URLs, not publication URLs. No public URL is claimed
until an exact deployed URL passes a real-browser identity and journey check.

## Licensing and source use

Repository-authored code, documentation and ontology terms are licensed under
the [MIT License](LICENSE). That does not relicense third-party material.
Official source pages are linked and summarized in original words rather than
redistributed, and no page snapshots have been acquired. Dated provider,
OGL, CPSV-AP, Open Referral UK and HSDS determinations are recorded in
[the licensing decisions](LICENSE_DECISIONS.md), [NOTICE.md](NOTICE.md) and the
[machine-readable rights register](source/rights-decisions.v1.yaml).

Eligible generated projections are MIT when they contain only
repository-authored structure, original summaries, facts and links. Source
snapshots remain non-redistributable until an exact source-specific licence
decision is recorded. These decisions do not change the separate explicit
owner gate for publication.

The reviewed authority refresh is a separate live metadata acquisition step:

```sh
uv run --locked python scripts/refresh_authority_registry.py --check
uv run --locked python scripts/audit_source_links.py
```

It is not part of deterministic offline validation. The refresh transforms
official ONS names, codes and dates in memory; the audit stores response
metadata only. Neither retains a source response body, geometry or snapshot.

## Authority boundary

This project is an educational and navigational knowledge product. It does not
replace authoritative government services and must not make personalised
eligibility, legal or medical decisions. Every implemented service route must
retain its official source, jurisdiction, observation time and limitations.
