# A Life in the UK

A citizen-centred Open Knowledge Format (OKF v0.2) bundle about public
services, rights, responsibilities and life events across the United Kingdom,
from before birth to death and bereavement.

Status: **research and implementation scaffold**. The repository is local-only;
acquisition, CI, remote creation and publication remain disabled until the
domain profile and source/rights decisions are reviewed.

## Start here

- [Research overview and generating prompt](research/overview.md)
- [OKF bundle root](index.md)
- [Implementation roadmap](ROADMAP.md)
- [Repository status](REPOSITORY_STATUS.md)
- [Authoring and validation guide](docs/authoring.md)
- [Licensing decisions](LICENSE_DECISIONS.md)
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

Create a virtual environment and install the intentionally small authoring
dependency set:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-okf.txt
```

Build and verify the initial bundle:

```sh
.venv/bin/python scripts/build_okf_bundle.py
.venv/bin/python scripts/build_okf_bundle.py --check
.venv/bin/python scripts/check_okf.py
.venv/bin/python -m unittest discover -s tests
```

The generated small-bundle entrypoint is `okf-bundle.json`. No public URL is
claimed until an exact deployed URL passes a real-browser identity and journey
check.

## Authority boundary

This project is an educational and navigational knowledge product. It does not
replace authoritative government services and must not make personalised
eligibility, legal or medical decisions. Every implemented service route must
retain its official source, jurisdiction, observation time and limitations.
