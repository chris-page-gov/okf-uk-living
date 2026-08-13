from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_service_denominator import load_service_denominator  # noqa: E402
from explore_okf_projection import (  # noqa: E402
    JOURNEY_PROJECTION_SCHEMA_PATH,
    JOURNEY_PROJECTION_SCHEMA_PUBLIC_PATH,
    STEP_FACT_FIELDS,
    STEP_FACT_FLOW_MAPPING_FRAGMENT_RULE,
    build_endpoint_label_index,
    build_journey_projection,
    canonical_json_bytes,
    metadata_endpoint_route,
    normalise_comma_fragments,
    normalise_step_fact,
    projection_assertion_references,
    validate_endpoint_label_index,
    validate_journey_projection,
)
from life_course_dossiers import load_dossiers  # noqa: E402
from life_course_projection import project  # noqa: E402


SNAPSHOT = "life-course-authority-infrastructure-2026-08-08"
GENERATED_AT = "2026-08-08T00:00:00+01:00"
SHA256_A = "a" * 64
SHA256_B = "b" * 64
SHA256_C = "c" * 64
SHA256_D = "d" * 64
SHA256_E = "e" * 64


class ExploreOkfProjectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        denominator, errors = load_service_denominator()
        if errors:
            raise AssertionError(errors)
        cls.rows, cls.resources, cls.relationships, _ = project(denominator)
        cls.source_identity = {
            "bundle_url": "https://chris-page-gov.github.io/okf-uk-living/okf-explorer.json",
            "candidate_id": "life-course-population-complete-2026-08-08",
            "bundle_descriptor": {
                "path": "publication/okf-explorer.json",
                "bytes": 2842,
                "sha256": SHA256_A,
            },
            "data_manifest": {
                "path": "large/data/manifest.json",
                "bytes": 1638,
                "sha256": SHA256_B,
            },
            "relationship_runtime": {
                "path": "large/data/relationship-runtime/manifest.json",
                "bytes": 2649,
                "sha256": SHA256_C,
            },
            "candidate_manifest": {
                "path": "generated/assurance/candidate-manifest.json",
                "bytes": 14201,
                "sha256": SHA256_D,
            },
            "review_status": {
                "path": "generated/assurance/review-status-report.json",
                "bytes": 524,
                "sha256": SHA256_E,
            },
        }
        cls.projection = build_journey_projection(
            cls.rows,
            cls.resources,
            cls.relationships,
            source_identity=cls.source_identity,
            snapshot=SNAPSHOT,
            generated_at_value=GENERATED_AT,
        )
        cls.endpoint_labels = build_endpoint_label_index(
            cls.rows,
            cls.resources,
            cls.relationships,
            snapshot=SNAPSHOT,
            generated_at_value=GENERATED_AT,
        )

    def test_projection_is_deterministic_and_valid(self) -> None:
        rebuilt = build_journey_projection(
            self.rows,
            self.resources,
            self.relationships,
            source_identity=self.source_identity,
            snapshot=SNAPSHOT,
            generated_at_value=GENERATED_AT,
        )
        self.assertEqual(canonical_json_bytes(self.projection), canonical_json_bytes(rebuilt))
        self.assertEqual(
            [],
            validate_journey_projection(
                self.projection, relationships=self.relationships
            ),
        )
        self.assertEqual(self.source_identity, self.projection["source_identity"])

    def test_projection_schema_is_an_additive_public_sidecar(self) -> None:
        self.assertEqual(
            ROOT
            / "evaluation"
            / "ai-consumer"
            / "life-course-journey-projection.schema.json",
            JOURNEY_PROJECTION_SCHEMA_PATH,
        )
        self.assertEqual(
            Path("explore/life-course-journey-projection.schema.json"),
            JOURNEY_PROJECTION_SCHEMA_PUBLIC_PATH,
        )
        schema = json.loads(JOURNEY_PROJECTION_SCHEMA_PATH.read_text(encoding="utf-8"))
        self.assertEqual(
            "https://chris-page-gov.github.io/okf-uk-living/"
            "explore/life-course-journey-projection.schema.json",
            schema["$id"],
        )

    def test_projection_contains_the_complete_review_denominator(self) -> None:
        self.assertEqual(293, self.projection["counts"]["families"])
        self.assertEqual(24, self.projection["counts"]["domains"])
        self.assertEqual(48, self.projection["counts"]["processes"])
        self.assertEqual(0, self.projection["counts"]["specialist_review_accepted"])
        self.assertEqual(
            2, self.projection["counts"]["specialist_review_not_required"]
        )
        self.assertEqual(
            291, self.projection["counts"]["specialist_review_required"]
        )
        self.assertEqual(
            879,
            self.projection["counts"]["sources"],
        )

    def test_ordinary_episode_and_steps_retain_authored_order(self) -> None:
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        projected = {family["id"]: family for family in self.projection["families"]}
        for family_id, dossier in dossiers.items():
            family = projected[family_id]
            expected_journeys = [
                ("ordinary", dossier["journeys"]["ordinary"]),
                *(("exception", item) for item in dossier["journeys"]["exceptions"]),
            ]
            self.assertEqual(
                [(kind, journey["id"]) for kind, journey in expected_journeys],
                [(episode["kind"], episode["id"]) for episode in family["episodes"]],
            )
            for episode, (_, journey) in zip(
                family["episodes"], expected_journeys, strict=True
            ):
                self.assertEqual(
                    [step["id"] for step in journey["steps"]],
                    [step["id"] for step in episode["steps"]],
                )

    def test_comma_fragments_are_rejoined_only_in_the_sidecar(self) -> None:
        self.assertEqual(
            ["Understand that acceptance, points, payment and court alternatives depend on the exact notice."],
            normalise_comma_fragments(
                [
                    "Understand that acceptance",
                    "points",
                    "payment and court alternatives depend on the exact notice.",
                ]
            ),
        )
        family = next(
            item
            for item in self.projection["families"]
            if item["id"] == "accept-fixed-penalty"
        )
        self.assertEqual(
            ["Understand that acceptance, points, payment and court alternatives depend on the exact notice."],
            family["user_needs"],
        )

    def test_legacy_step_fact_fragments_are_losslessly_normalised_in_the_sidecar(
        self,
    ) -> None:
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        projected = {family["id"]: family for family in self.projection["families"]}
        affected_families: set[str] = set()
        affected_facts = 0
        fragment_count = 0

        for family_id, dossier in dossiers.items():
            journeys = [
                dossier["journeys"]["ordinary"],
                *dossier["journeys"]["exceptions"],
            ]
            projected_episodes = {
                episode["id"]: episode for episode in projected[family_id]["episodes"]
            }
            for journey in journeys:
                projected_steps = {
                    step["id"]: step
                    for step in projected_episodes[journey["id"]]["steps"]
                }
                for step in journey["steps"]:
                    for field in STEP_FACT_FIELDS:
                        source_fact = step[field]
                        before = copy.deepcopy(source_fact)
                        narrative_key = (
                            "summary"
                            if source_fact["state"] == "supported"
                            else "reason"
                        )
                        fragments = [
                            key
                            for key in source_fact
                            if key not in {"state", narrative_key}
                        ]
                        canonical = normalise_step_fact(source_fact)
                        self.assertEqual(before, source_fact)
                        self.assertEqual(
                            {"state", narrative_key}, set(canonical)
                        )
                        self.assertEqual(
                            canonical, projected_steps[step["id"]][field]
                        )
                        if fragments:
                            affected_families.add(family_id)
                            affected_facts += 1
                            fragment_count += len(fragments)
                            self.assertTrue(
                                all(source_fact[key] is None for key in fragments)
                            )
                            self.assertEqual(
                                ", ".join(
                                    [source_fact[narrative_key], *fragments]
                                ),
                                canonical[narrative_key],
                            )

        self.assertEqual(
            {
                "administer-an-estate",
                "learn-to-drive-car",
                "notify-organisations-after-a-death",
                "register-a-death",
                "report-missed-rubbish-collection",
                "respond-to-speeding-notice",
            },
            affected_families,
        )
        self.assertEqual(45, affected_facts)
        self.assertEqual(71, fragment_count)
        self.assertEqual(
            STEP_FACT_FLOW_MAPPING_FRAGMENT_RULE,
            self.projection["normalisation"][
                "step_fact_flow_mapping_fragments"
            ],
        )

    def test_step_fact_schema_is_strict_and_referenced_by_all_nine_fields(
        self,
    ) -> None:
        schema = json.loads(JOURNEY_PROJECTION_SCHEMA_PATH.read_text(encoding="utf-8"))
        step_properties = schema["$defs"]["step"]["properties"]
        for field in STEP_FACT_FIELDS:
            self.assertEqual(
                {"$ref": "#/$defs/stepFact"}, step_properties[field]
            )

        fact_validator = Draft202012Validator(
            {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "$ref": "#/$defs/stepFact",
                "$defs": schema["$defs"],
            }
        )
        valid = (
            {"state": "supported", "summary": "A governed summary."},
            {
                "state": "not_published_by_source",
                "reason": "The source does not publish this fact.",
            },
            {
                "state": "not_applicable",
                "reason": "This fact does not apply.",
            },
        )
        for fact in valid:
            self.assertEqual([], list(fact_validator.iter_errors(fact)))
        invalid = (
            {"state": "supported", "reason": "Wrong narrative field."},
            {
                "state": "not_published_by_source",
                "summary": "Wrong narrative field.",
            },
            {"state": "supported", "summary": "Text.", "fragment": None},
        )
        for fact in invalid:
            self.assertTrue(list(fact_validator.iter_errors(fact)))

        with self.assertRaisesRegex(ValueError, "non-canonical property"):
            normalise_step_fact(
                {
                    "state": "supported",
                    "summary": "A summary",
                    "unexpected": "not a null-key fragment",
                }
            )

    def test_standalone_renders_step_fact_state_and_narrative_separately(self) -> None:
        script = (ROOT / "source/explore-okf/standalone.js").read_text(
            encoding="utf-8"
        )
        stylesheet = (ROOT / "source/explore-okf/standalone.css").read_text(
            encoding="utf-8"
        )
        self.assertIn("State: ${stateLabel}", script)
        self.assertIn("Summary: ${value.summary}", script)
        self.assertIn("Reason: ${value.reason}", script)
        self.assertIn("step_fact_flow_mapping_fragments", script)
        self.assertNotIn("summaryValue", script)
        self.assertIn(".fact-state", stylesheet)
        self.assertIn(".fact-narrative", stylesheet)

    def test_aliases_are_exact_and_missed_bin_is_searchable(self) -> None:
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        projected = {family["id"]: family for family in self.projection["families"]}
        for family_id, dossier in dossiers.items():
            self.assertEqual(dossier["aliases"], projected[family_id]["aliases"])
        self.assertIn(
            "missed bin",
            projected["report-missed-rubbish-collection"]["aliases"],
        )

    def test_source_jurisdiction_comes_from_explicit_applicability(self) -> None:
        family = next(
            item
            for item in self.projection["families"]
            if item["id"] == "accept-fixed-penalty"
        )
        source = next(
            item for item in family["sources"] if item["id"] == "accept-fixed-penalty-primary"
        )
        self.assertEqual("www.gov.uk", source["url"].split("/")[2])
        self.assertEqual(["England", "Wales"], source["jurisdictions"])
        for projected_family in self.projection["families"]:
            expected: dict[str, list[str]] = {}
            for applicability in projected_family["applicability"]:
                for source_id in applicability["source_ids"]:
                    expected.setdefault(source_id, [])
                    if applicability["jurisdiction"] not in expected[source_id]:
                        expected[source_id].append(applicability["jurisdiction"])
            for projected_source in projected_family["sources"]:
                self.assertEqual(
                    expected.get(projected_source["id"], []),
                    projected_source["jurisdictions"],
                )

    def test_assertion_references_resolve_to_the_full_graph(self) -> None:
        references = projection_assertion_references(self.projection)
        relationship_ids = {relationship["id"] for relationship in self.relationships}
        self.assertTrue(references)
        self.assertLessEqual(set(references), relationship_ids)
        self.assertEqual(
            len(references),
            self.projection["counts"]["relationship_assertion_references"],
        )

        changed = copy.deepcopy(self.projection)
        changed["families"][0]["relationship_assertions"]["enclosing_process"] = (
            "https://example.test/assertions/not-in-the-full-graph"
        )
        self.assertTrue(
            any(
                "assertion id is absent from the full graph" in error
                for error in validate_journey_projection(
                    changed, relationships=self.relationships
                )
            )
        )

    def test_related_families_are_grouped_without_sequence(self) -> None:
        for family in self.projection["families"]:
            for related in family["related_families"]:
                self.assertEqual("shared-enclosing-process", related["relationship"])
                self.assertFalse(related["sequenced"])
        self.assertFalse(
            any(
                relationship["source"].startswith("dataset/")
                and relationship["target"].startswith("dataset/")
                and relationship["predicate"].endswith(("/precedes", "/follows"))
                for relationship in self.relationships
            )
        )

    def test_endpoint_labels_are_complete_deterministic_and_canonical(self) -> None:
        routes = {entry["route"] for entry in self.endpoint_labels["entries"]}
        graph_routes = {
            str(relationship[endpoint])
            for relationship in self.relationships
            for endpoint in ("source", "target")
        }
        self.assertLessEqual(graph_routes, routes)
        self.assertEqual(
            [],
            validate_endpoint_label_index(
                self.endpoint_labels,
                graph_reachable_routes=routes,
            ),
        )
        rebuilt = build_endpoint_label_index(
            self.rows,
            self.resources,
            self.relationships,
            snapshot=SNAPSHOT,
            generated_at_value=GENERATED_AT,
        )
        self.assertEqual(
            canonical_json_bytes(self.endpoint_labels), canonical_json_bytes(rebuilt)
        )
        self.assertEqual(
            "topic/Business%20%26%20economy",
            metadata_endpoint_route("topic", "Business & economy"),
        )
        self.assertTrue(
            all(entry["label"] != "Missing label" for entry in self.endpoint_labels["entries"])
        )


if __name__ == "__main__":
    unittest.main()
