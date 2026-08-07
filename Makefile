.PHONY: build check test

build:
	python3 scripts/build_okf_bundle.py

check:
	python3 scripts/build_okf_bundle.py --check
	python3 scripts/check_okf.py

test:
	python3 -m unittest discover -s tests
