from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_large_corpus import (  # noqa: E402
    build_outputs,
    relationship_bucket,
    remove_generated_tree,
)
from check_large_projection import validate_large_projection  # noqa: E402
from life_course_dossiers import load_dossiers, resolve_sources  # noqa: E402
from life_course_projection import (  # noqa: E402
    PREDICATE_BASE,
    RELATIONSHIP_DERIVATION_RULE,
)
from semantic_assertion_validation import (  # noqa: E402
    SEMANTIC_ASSERTION_SCHEMA_BYTES,
    SEMANTIC_ASSERTION_SCHEMA_PATH,
    SEMANTIC_ASSERTION_SCHEMA_SHA256,
    runtime_relationship_as_assertion,
    validate_assertions,
    validate_relationship_planes,
)


def projected_rows(outputs: dict[Path, str | bytes]) -> list[dict[str, object]]:
    manifest = json.loads(outputs[Path("large/data/manifest.json")])
    return [
        row
        for path in manifest["chunks"]["datasets"]
        for row in json.loads(outputs[Path(path)])
    ]


class LargeProjectionTests(unittest.TestCase):
    def test_generated_tree_cleanup_ignores_finder_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "large-data"
            root.mkdir()
            (root / ".DS_Store").write_bytes(b"finder metadata")
            remove_generated_tree(root)
            self.assertFalse(root.exists())

    def test_projection_is_valid(self) -> None:
        self.assertEqual([], validate_large_projection())

    def test_projection_is_deterministic(self) -> None:
        self.assertEqual(build_outputs(), build_outputs())

    def test_projection_distinguishes_families_from_supporting_concepts(self) -> None:
        rows = projected_rows(build_outputs())
        families = [row for row in rows if row["record_type"] == "Service Family"]
        self.assertEqual(293, len(families))
        self.assertGreater(len(rows), len(families))
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(len(dossiers), sum(row["implementation_status"] == "population-complete" for row in families))
        self.assertTrue(all("upstream-link-only-not-acquired" in row["rights_state"] for row in rows))

    def test_population_stage_projects_narratives_sources_and_provenance(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
        resources = json.loads(outputs[Path("large/data/resources-0.json")])
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        migrated = [
            row for row in rows
            if row.get("record_type") == "Service Family"
            and row.get("implementation_status") == "population-complete"
        ]
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(len(dossiers), len(migrated))
        self.assertTrue(all(row.get("narrative", {}).get("body") for row in migrated))
        expected_resources = sum(len(resolve_sources(dossier)[0]) for dossier in dossiers.values())
        self.assertEqual(expected_resources, len(resources))
        self.assertTrue(all(resource["source_access"]["display_mode"] == "link" for resource in resources))
        self.assertTrue(all(resource["provenance"]["response_body_retained"] is False for resource in resources))
        for relationship in relationships:
            self.assertTrue({
                "id", "source_iri", "target_iri", "predicate", "label",
                "inverse_label", "assertion_status", "assertion_scope",
                "authority", "derivation", "evidence", "rights",
            } <= set(relationship))
            self.assertTrue(relationship["source_iri"].startswith("https://"))
            self.assertTrue(relationship["target_iri"].startswith("https://"))
            self.assertTrue(relationship["predicate"].startswith(PREDICATE_BASE))

    def test_shared_schema_validates_every_relationship_plane(self) -> None:
        outputs = build_outputs()
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        semantic = json.loads(
            outputs[Path("generated/semantic/life-course-corpus.jsonld")]
        )
        validation = json.loads(outputs[Path("large/data/validation-report.json")])
        receipt, violations = validate_relationship_planes(semantic, relationships)
        self.assertEqual([], violations)
        self.assertEqual(
            SEMANTIC_ASSERTION_SCHEMA_SHA256,
            receipt["schema_sha256"],
        )
        self.assertEqual(SEMANTIC_ASSERTION_SCHEMA_BYTES, receipt["schema_bytes"])
        self.assertEqual(
            SEMANTIC_ASSERTION_SCHEMA_BYTES,
            len(SEMANTIC_ASSERTION_SCHEMA_PATH.read_bytes()),
        )
        self.assertEqual(len(relationships), receipt["semantic_assertions_checked"])
        self.assertEqual(len(relationships), receipt["runtime_relationships_checked"])
        self.assertEqual(receipt, validation["semantic_assertion_validation"])
        self.assertEqual("conformant", validation["status"])
        self.assertEqual([], validation["violations"])
        self.assertTrue(all(
            evidence["normalization"] == RELATIONSHIP_DERIVATION_RULE
            and evidence["rationale"] == "Repository-authored governed relationship."
            for relationship in relationships
            for evidence in relationship["evidence"]
        ))

    def test_shared_schema_rejects_prose_normalization(self) -> None:
        outputs = build_outputs()
        relationship = json.loads(
            outputs[Path("large/data/relationships-0.json")]
        )[0]
        assertion = copy.deepcopy(runtime_relationship_as_assertion(relationship))
        assertion["evidence"][0]["normalization"] = (
            "repository-authored governed relationship"
        )
        checked, violations = validate_assertions([assertion], plane="runtime")
        self.assertEqual(1, checked)
        self.assertEqual(1, len(violations))
        self.assertEqual("/evidence/0/normalization", violations[0]["instance_path"])

    def test_shared_schema_rejects_missing_label_and_unsafe_source_urls(self) -> None:
        outputs = build_outputs()
        relationship = json.loads(
            outputs[Path("large/data/relationships-0.json")]
        )[0]
        base = runtime_relationship_as_assertion(relationship)

        missing_label = copy.deepcopy(base)
        missing_label.pop("label")
        empty_host = copy.deepcopy(base)
        empty_host["authority"]["source"] = "https:///missing-host"
        credentials = copy.deepcopy(base)
        credentials["evidence"][0]["url"] = "https://user@example.org/evidence"
        unsafe_resource = copy.deepcopy(base)
        unsafe_resource["evidence"][0]["resource"] = "https://example.org/it's"
        invalid_port = copy.deepcopy(base)
        invalid_port["rights"]["source"] = "https://example.org:0/rights"

        cases = (
            (missing_label, ""),
            (empty_host, "/authority/source"),
            (credentials, "/evidence/0/url"),
            (unsafe_resource, "/evidence/0/resource"),
            (invalid_port, "/rights/source"),
        )
        for assertion, expected_path in cases:
            with self.subTest(expected_path=expected_path):
                checked, violations = validate_assertions(
                    [assertion], plane="runtime"
                )
                self.assertEqual(1, checked)
                self.assertTrue(violations)
                self.assertIn(
                    expected_path,
                    {violation["instance_path"] for violation in violations},
                )

    def test_relationship_adjacency_exactly_repeats_runtime_assertions(self) -> None:
        outputs = build_outputs()
        relationships = json.loads(
            outputs[Path("large/data/relationships-0.json")]
        )
        manifest = json.loads(
            outputs[Path("large/data/relationship-adjacency.json")]
        )
        runtime_by_id = {edge["id"]: edge for edge in relationships}
        self.assertEqual(len(relationships), len(runtime_by_id))
        self.assertEqual(len(relationships), manifest["relationships"])

        incidence: Counter[str] = Counter()
        for bucket, path in manifest["buckets"].items():
            routes = json.loads(outputs[Path(path)])
            for route, edges in routes.items():
                self.assertEqual(bucket, relationship_bucket(route))
                for edge in edges:
                    self.assertIn(route, {edge["source"], edge["target"]})
                    self.assertEqual(runtime_by_id[edge["id"]], edge)
                    incidence[edge["id"]] += 1

        self.assertEqual(set(runtime_by_id), set(incidence))
        self.assertTrue(all(
            incidence[edge["id"]]
            == (1 if edge["source"] == edge["target"] else 2)
            for edge in relationships
        ))

    def test_shared_authority_infrastructure_is_searchable_and_reused(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        geographies = [row for row in rows if row["record_type"] == "Administrative Geography"]
        organisations = [row for row in rows if row["record_type"] == "Organisation"]
        self.assertEqual(397, len(geographies))
        self.assertEqual(438, len(organisations))
        hmcts = next(row for row in organisations if row["title"] == "HM Courts & Tribunals Service")
        self.assertTrue(any(
            edge["target"] == hmcts["route"]
            and edge["predicate"] == f"{PREDICATE_BASE}offered-by"
            for edge in relationships
        ))
        postings = json.loads(outputs[Path("large/data/search/postings.json")])["tokens"]
        ordinal = rows.index(next(row for row in organisations if row["title"] == "Financial Conduct Authority"))
        self.assertIn(ordinal, {item[0] for item in postings["financial"]})
        anglesey = rows.index(next(row for row in geographies if row["title"] == "Isle of Anglesey"))
        self.assertIn(anglesey, {item[0] for item in postings["mon"]})

    def test_static_search_indexes_all_planning_families(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
        search = json.loads(outputs[Path("large/data/search/manifest.json")])
        postings = json.loads(outputs[Path("large/data/search/postings.json")])["tokens"]
        ordinal = next(index for index, row in enumerate(rows) if row["name"] == "report-missed-rubbish-collection")
        self.assertEqual(len(rows), search["counts"]["documents"])
        self.assertIn(ordinal, {item[0] for item in postings["missed"]})
        self.assertIn(ordinal, {item[0] for item in postings["rubbish"]})
        wave_filters = json.loads(outputs[Path("large/data/search/filters/acquisition_wave.json")])
        self.assertEqual(101, len(wave_filters["values"]["wave-3"]))


if __name__ == "__main__":
    unittest.main()
