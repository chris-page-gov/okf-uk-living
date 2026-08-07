# A Life in the UK

A citizen-centred Open Knowledge Format (OKF v0.2) bundle about public
services, rights, responsibilities and life events across the United Kingdom,
from before birth to death and bereavement.

Status: **three vertical slices reviewed locally with open release findings**.
The Reader and query journeys pass in OKF Explorer 0.5.7, but relationship and
node provenance, browser-renderable source handoffs, and licence-notice
verification must be resolved before a candidate is frozen. The GitHub
repository is private; validation remains local-only, broad acquisition and CI
remain disabled, and publication requires a separate explicit owner request.

## Start here

- [Research overview and generating prompt](research/overview.md)
- [OKF bundle root](index.md)
- [Implementation roadmap](ROADMAP.md)
- [Delivery planning](PLANNING.md)
- [Delivery tracking](TRACKING.md)
- [Three-slice review and publication plan](docs/review-and-publication-plan.md)
- [2026-08-07 integrated Explorer review](evaluation/reviews/integrated-three-slice-2026-08-07.md)
- [Local Explorer input record](evaluation/compatibility/okf-explorer-local.v1.yaml)
- [`okf-domain-profile.v1` review handoff](profiles/okf-domain-profile.v1.md)
- [Three vertical-slice fixture contracts](evaluation/fixtures/README.md)
- [Missed rubbish collection journey](journeys/missed-rubbish-collection.md)
- [Learning to drive through a speeding exception](journeys/learning-to-drive-speeding.md)
- [Death and bereavement through estate administration](journeys/death-bereavement-estate.md)
- [Missed rubbish linked-reference register](source/missed-rubbish-collection.v1.yaml)
- [Driving and speeding linked-reference register](source/learning-to-drive-speeding.v1.yaml)
- [Death, bereavement and estate linked-reference register](source/death-bereavement-estate.v1.yaml)
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
uv run --locked python scripts/build_okf_bundle.py
uv run --locked python scripts/build_okf_bundle.py --check
uv run --locked python scripts/check_okf.py
uv run --locked python scripts/check_contracts.py
uv run --locked python scripts/check_sources.py
uv run --locked python scripts/check_rights.py
uv run --locked python -m unittest discover -s tests
```

`make validate` runs the same required sequence. Validation is local-only by
default; pull requests and merges do not run remote CI or update GitHub Pages.

The generated small-bundle entrypoint is `okf-bundle.json`. No public URL is
claimed until an exact deployed URL passes a real-browser identity and journey
check.

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

## Authority boundary

This project is an educational and navigational knowledge product. It does not
replace authoritative government services and must not make personalised
eligibility, legal or medical decisions. Every implemented service route must
retain its official source, jurisdiction, observation time and limitations.
