.PHONY: build check test validate

build:
	uv run --locked python scripts/build_okf_bundle.py

check:
	uv run --locked python scripts/build_okf_bundle.py --check
	uv run --locked python scripts/check_okf.py

test:
	uv run --locked python -m unittest discover -s tests

validate:
	uv run --locked python scripts/build_okf_bundle.py
	uv run --locked python scripts/build_okf_bundle.py --check
	uv run --locked python scripts/check_okf.py
	uv run --locked python -m unittest discover -s tests
