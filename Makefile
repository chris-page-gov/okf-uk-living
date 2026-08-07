.PHONY: build check check-contracts check-corpus-policy check-denominator check-inventory check-rights check-sources test validate

build:
	uv run --locked python scripts/build_okf_bundle.py

check:
	uv run --locked python scripts/build_okf_bundle.py --check
	uv run --locked python scripts/check_okf.py
	uv run --locked python scripts/check_contracts.py
	uv run --locked python scripts/check_sources.py
	uv run --locked python scripts/check_inventory.py
	uv run --locked python scripts/check_service_denominator.py
	uv run --locked python scripts/check_corpus_policy.py
	uv run --locked python scripts/check_rights.py

check-contracts:
	uv run --locked python scripts/check_contracts.py

check-sources:
	uv run --locked python scripts/check_sources.py

check-inventory:
	uv run --locked python scripts/check_inventory.py

check-denominator:
	uv run --locked python scripts/check_service_denominator.py

check-corpus-policy:
	uv run --locked python scripts/check_corpus_policy.py

check-rights:
	uv run --locked python scripts/check_rights.py

test:
	uv run --locked python -m unittest discover -s tests

validate:
	uv run --locked python scripts/build_okf_bundle.py
	uv run --locked python scripts/build_okf_bundle.py --check
	uv run --locked python scripts/check_okf.py
	uv run --locked python scripts/check_contracts.py
	uv run --locked python scripts/check_sources.py
	uv run --locked python scripts/check_inventory.py
	uv run --locked python scripts/check_service_denominator.py
	uv run --locked python scripts/check_corpus_policy.py
	uv run --locked python scripts/check_rights.py
	uv run --locked python -m unittest discover -s tests
