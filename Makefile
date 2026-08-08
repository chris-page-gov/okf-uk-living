.PHONY: build build-assurance check check-authorities check-browser-handoff check-contracts check-corpus-policy check-denominator check-domain-registers check-dossiers check-inventory check-large-projection check-pages-publication check-population-assurance check-population-contract check-rights check-search-acceptance check-sources render-packs test validate

render-packs:
	uv run --locked python scripts/render_life_course_packs.py

build:
	uv run --locked python scripts/render_life_course_packs.py
	uv run --locked python scripts/build_browser_handoff.py
	uv run --locked python scripts/build_okf_bundle.py
	uv run --locked python scripts/build_large_corpus.py
	uv run --locked python scripts/build_population_assurance.py

build-assurance:
	uv run --locked python scripts/build_population_assurance.py

check:
	uv run --locked python scripts/render_life_course_packs.py --check
	uv run --locked python scripts/build_browser_handoff.py --check
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
	uv run --locked python scripts/build_large_corpus.py --check
	uv run --locked python scripts/check_large_projection.py
	uv run --locked python scripts/check_search_acceptance.py
	uv run --locked python scripts/build_population_assurance.py --check
	uv run --locked python scripts/check_population_assurance.py
	uv run --locked python scripts/prepare_pages_publication.py

check-browser-handoff:
	uv run --locked python scripts/build_browser_handoff.py --check

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

check-population-contract:
	uv run --locked python scripts/check_population_contract.py

check-dossiers:
	uv run --locked python scripts/check_life_course_dossiers.py

check-domain-registers:
	uv run --locked python scripts/check_domain_registers.py

check-authorities:
	uv run --locked python scripts/check_authority_registry.py

check-rights:
	uv run --locked python scripts/check_rights.py

check-large-projection:
	uv run --locked python scripts/build_large_corpus.py --check
	uv run --locked python scripts/check_large_projection.py

check-search-acceptance:
	uv run --locked python scripts/check_search_acceptance.py

check-population-assurance:
	uv run --locked python scripts/build_population_assurance.py --check
	uv run --locked python scripts/check_population_assurance.py

check-pages-publication:
	uv run --locked python scripts/prepare_pages_publication.py

test:
	uv run --locked python -m unittest discover -s tests

validate:
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
	uv run --locked python scripts/build_population_assurance.py
	uv run --locked python scripts/build_population_assurance.py --check
	uv run --locked python scripts/check_population_assurance.py
	uv run --locked python scripts/prepare_pages_publication.py
	uv run --locked python -m unittest discover -s tests
