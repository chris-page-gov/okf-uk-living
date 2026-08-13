from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import yaml


ROOT = Path(__file__).resolve().parents[1]
EVALUATOR_PATH = ROOT / "scripts" / "evaluate_ai_consumer_answers.py"
SPEC = importlib.util.spec_from_file_location("ai_consumer_evaluator", EVALUATOR_PATH)
assert SPEC and SPEC.loader
evaluator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(evaluator)


class AiConsumerEvaluationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bundle = self.root / "bundle.json"
        self.projection = self.root / "journey-projection.json"
        self.manifest = self.root / "manifest.json"
        self.pages_manifest = self.root / "pages-manifest.json"
        self.explore_manifest = self.root / "explore-manifest.json"
        self.review = self.root / "review.json"
        self.question_suite = self.root / "questions.yaml"
        self.family_root = self.root / "families"
        self.resource_chunk = self.root / "resources.json"
        self.relationship_chunk = self.root / "relationships.json"
        self.schema = self.root / "answer.schema.json"
        self.gold = self.root / "gold.yaml"
        self.answers = self.root / "answers.json"

        self.bundle.write_text('{"bundle":"fixture"}\n', encoding="utf-8")
        self.projection.write_text('{"projection":"fixture"}\n', encoding="utf-8")
        self.review.write_text(
            json.dumps(
                {
                    "counts": {
                        "specialist_review_accepted": 0,
                        "specialist_review_not_required": 2,
                        "specialist_review_required": 291,
                    }
                }
            ),
            encoding="utf-8",
        )
        self.resource_chunk.write_text(
            json.dumps(
                [
                    {
                        "dataset": "fixture-family",
                        "url": "https://official.example.test/fixture",
                    }
                ]
            ),
            encoding="utf-8",
        )
        self.relationship_chunk.write_text(
            json.dumps(
                [
                    {
                        "id": "https://example.test/assertions/fixture",
                        "source": "dataset/fixture-family",
                        "target": "service-episode/fixture-ordinary",
                        "evidence": [
                            {
                                "source_artifact": "source/life-course-families/fixture-domain/fixture-family.v1.yaml",
                                "url": "https://example.test/evidence",
                            }
                        ],
                        "authority": {"source": "https://example.test/authority"},
                        "observed_at": "2026-08-13T00:00:00Z",
                        "rights": {"source": "https://example.test/rights"},
                    }
                ]
            ),
            encoding="utf-8",
        )
        self.manifest.write_text(
            json.dumps(
                {
                    "chunks": {
                        "resources": ["resources.json"],
                        "relationships": ["relationships.json"],
                    }
                }
            ),
            encoding="utf-8",
        )
        closure_files = [
            (self.bundle, "okf-explorer.json"),
            (self.manifest, "large/data/manifest.json"),
            (self.resource_chunk, "large/data/resources.json"),
            (self.relationship_chunk, "large/data/relationships.json"),
        ]
        self.pages_manifest.write_text(
            json.dumps(
                {
                    "files": [
                        {
                            "source": path.name,
                            "target": target,
                            "bytes": path.stat().st_size,
                            "sha256": self.digest(path),
                        }
                        for path, target in closure_files
                    ]
                }
            ),
            encoding="utf-8",
        )
        self.explore_manifest.write_text(
            json.dumps(
                {
                    "base_manifest": {"sha256": self.digest(self.pages_manifest)},
                    "files": [
                        {
                            "source": self.projection.name,
                            "target": "explore/journey-projection.json",
                            "bytes": self.projection.stat().st_size,
                            "sha256": self.digest(self.projection),
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )
        self.question_suite.write_text(
            yaml.safe_dump(
                {
                    "suite": "life-course-competency-questions.v1",
                    "questions": [
                        {
                            "id": "pack1-fixture",
                            "query": "Where is the fixture route?",
                            "expected_family": "fixture-family",
                            "domains": ["fixture-domain"],
                            "jurisdictions": ["England"],
                        }
                    ],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        family_dir = self.family_root / "fixture-domain"
        family_dir.mkdir(parents=True)
        (family_dir / "fixture-family.v1.yaml").write_text(
            yaml.safe_dump(
                {
                    "schema": "life-course-family.v1",
                    "id": "fixture-family",
                    "title": "Fixture family",
                    "journeys": {
                        "ordinary": {
                            "id": "ordinary-route",
                            "steps": [{"id": "first-step"}],
                        },
                        "exceptions": [
                            {
                                "id": "exception-route",
                                "steps": [{"id": "exception-step"}],
                            }
                        ],
                    },
                    "review": {
                        "population_gate": "complete",
                        "specialist_review": "not_required",
                    },
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )
        self.schema.write_bytes((ROOT / "evaluation/ai-consumer/answer.schema.json").read_bytes())
        self.gold.write_text(
            yaml.safe_dump(
                {
                    "schema": "okf-ai-consumer-gold.v1",
                    "title": "Fixture",
                    "question_count": 1,
                    "minimum_distinct_models": 2,
                    "evidence_class": "held-out",
                    "promotion_claim_eligible": True,
                    "artifacts": {
                        "bundle": "bundle.json",
                        "journey_projection": "journey-projection.json",
                        "data_manifest": "manifest.json",
                        "review_report": "review.json",
                        "pages_manifest": "pages-manifest.json",
                        "explore_manifest": "explore-manifest.json",
                    },
                    "question_sources": ["questions.yaml"],
                    "hard_gates": ["fixture"],
                    "cases": [
                        {
                            "id": "gold-fixture",
                            "question_ref": {
                                "path": "questions.yaml",
                                "id": "pack1-fixture",
                            },
                            "expected": {
                                "family_id": "fixture-family",
                                "jurisdictions": ["England"],
                                "episode_order": ["ordinary", "exception"],
                                "first_step_id": "first-step",
                                "specialist_review": "not_required",
                                "source_url_minimum": 1,
                                "requires_assertion_provenance": True,
                                "decision_abstention_required": True,
                                "manual_review_required": True,
                                "corpus_review": {
                                    "specialist_review_accepted": 0,
                                    "specialist_review_not_required": 2,
                                    "specialist_review_required": 291,
                                },
                                "required_answer_terms": ["official"],
                                "prohibited_answer_fragments": ["invented decision"],
                            },
                        }
                    ],
                },
                sort_keys=False,
            ),
            encoding="utf-8",
        )

        self.original_root = evaluator.ROOT
        evaluator.ROOT = self.root
        self.addCleanup(setattr, evaluator, "ROOT", self.original_root)
        self.original_gold_count = evaluator.EXPECTED_GOLD_CASE_COUNT
        evaluator.EXPECTED_GOLD_CASE_COUNT = 1
        self.addCleanup(
            setattr,
            evaluator,
            "EXPECTED_GOLD_CASE_COUNT",
            self.original_gold_count,
        )

    @staticmethod
    def digest(path: Path) -> str:
        return hashlib.sha256(path.read_bytes()).hexdigest()

    def answer(self, model: str, condition: str) -> dict:
        supplied = condition == "with_bundle"
        closure = evaluator.publication_closure_context(
            {
                "pages_manifest": self.pages_manifest,
                "explore_manifest": self.explore_manifest,
            }
        )
        return {
            "schema": "okf-ai-consumer-answer.v1",
            "run_id": f"run-{model}-{condition}",
            "response_id": f"response-{model}-{condition}",
            "observed_at": "2026-08-13T01:00:00Z",
            "model": {"provider": "fixture", "name": model, "version": "1"},
            "condition": condition,
            "input_binding": {
                "bundle_sha256": self.digest(self.bundle),
                "journey_projection_sha256": self.digest(self.projection),
                **closure,
                "bundle_supplied": supplied,
                "journey_projection_supplied": supplied,
                "publication_closure_supplied": supplied,
            },
            "question_id": "pack1-fixture",
            "answer_mode": "navigation-only",
            "answer_text": "Use the linked official route. I cannot make the decision.",
            "selected_family": "fixture-family",
            "journey": {
                "episode_order": ["ordinary", "exception"],
                "first_step_id": "first-step",
            },
            "jurisdictions": ["England"],
            "source_urls": ["https://official.example.test/fixture"],
            "assertion_ids": ["https://example.test/assertions/fixture"],
            "assertion_provenance": [
                {
                    "id": "https://example.test/assertions/fixture",
                    "authority_source": "https://example.test/authority",
                    "evidence_sources": ["https://example.test/evidence"],
                    "observed_at": "2026-08-13T00:00:00Z",
                    "rights_source": "https://example.test/rights",
                }
            ],
            "specialist_review": "not_required",
            "corpus_review": {
                "specialist_review_accepted": 0,
                "specialist_review_not_required": 2,
                "specialist_review_required": 291,
            },
            "related_family_ids": [],
            "sequenced_family_ids": [],
            "decision_claims": [],
            "abstention": {
                "decision_abstained": True,
                "reason": "The bundle is a discovery aid, not a decision engine.",
            },
            "manual_review": {
                "status": "passed",
                "reviewer": "fixture-reviewer",
                "reviewed_at": "2026-08-13T02:00:00Z",
                "no_invented_decisions": True,
                "notes": "Checked.",
            },
        }

    def abstaining_baseline(self, model: str) -> dict:
        answer = self.answer(model, "without_bundle")
        answer.update(
            {
                "answer_mode": "abstention",
                "answer_text": "I cannot identify a route without the supplied material.",
                "selected_family": None,
                "journey": {"episode_order": [], "first_step_id": None},
                "jurisdictions": [],
                "source_urls": [],
                "assertion_ids": [],
                "assertion_provenance": [],
                "specialist_review": "unknown",
            }
        )
        answer.pop("corpus_review")
        answer.pop("manual_review")
        return answer

    def family_material(self) -> tuple:
        return (
            {
                "fixture-family": yaml.safe_load(
                    (self.family_root / "fixture-domain/fixture-family.v1.yaml").read_text(
                        encoding="utf-8"
                    )
                )
            },
            {"fixture-family": {"https://official.example.test/fixture"}},
            {
                "fixture-family": {
                    "https://example.test/assertions/fixture": {
                        "id": "https://example.test/assertions/fixture",
                        "authority_source": "https://example.test/authority",
                        "evidence_sources": ["https://example.test/evidence"],
                        "observed_at": "2026-08-13T00:00:00Z",
                        "rights_source": "https://example.test/rights",
                    }
                }
            },
        )

    def patch_family_material(self):
        return mock.patch.object(
            evaluator,
            "load_family_material",
            return_value=self.family_material(),
        )

    def evaluate(self, answers: list[dict], *, allow_incomplete: bool = False) -> dict:
        self.answers.write_text(json.dumps(answers), encoding="utf-8")
        with self.patch_family_material():
            return evaluator.evaluate(
                [self.answers],
                gold_path=self.gold,
                schema_path=self.schema,
                allow_incomplete=allow_incomplete,
            )

    def complete_matrix(self) -> list[dict]:
        return [
            (
                self.abstaining_baseline(model)
                if condition == "without_bundle"
                else self.answer(model, condition)
            )
            for model in ("model-a", "model-b")
            for condition in ("without_bundle", "with_bundle")
        ]

    def test_valid_two_model_matrix_is_promotion_eligible(self) -> None:
        report = self.evaluate(self.complete_matrix())
        self.assertTrue(report["promotion_eligible"])
        self.assertTrue(report["technical_gate_pass"])
        self.assertEqual("held-out", report["gold_pack"]["evidence_class"])
        self.assertEqual(2, report["distinct_models"])
        self.assertEqual([], report["matrix_failures"])
        self.assertNotIn("answer_text", json.dumps(report))

    def test_calibration_pack_can_pass_technically_but_never_promote(self) -> None:
        gold = yaml.safe_load(self.gold.read_text(encoding="utf-8"))
        gold["evidence_class"] = "development-calibration"
        gold["promotion_claim_eligible"] = False
        self.gold.write_text(yaml.safe_dump(gold, sort_keys=False), encoding="utf-8")
        report = self.evaluate(self.complete_matrix())
        self.assertTrue(report["technical_gate_pass"])
        self.assertFalse(report["promotion_eligible"])
        self.assertEqual(
            "development-calibration", report["gold_pack"]["evidence_class"]
        )

    def test_legitimate_baseline_abstention_does_not_block_promotion(self) -> None:
        answers = [
            answer
            for model in ("model-a", "model-b")
            for answer in (self.abstaining_baseline(model), self.answer(model, "with_bundle"))
        ]
        report = self.evaluate(answers)
        baselines = [
            row for row in report["results"] if row["condition"] == "without_bundle"
        ]
        self.assertTrue(report["promotion_eligible"])
        self.assertTrue(all(row["promotion_pass"] for row in baselines))
        self.assertTrue(all(row["safety_pass"] for row in baselines))
        self.assertTrue(all(not row["retrieval_pass"] for row in baselines))

    def test_baseline_never_receives_retrieval_credit(self) -> None:
        answers = self.complete_matrix()
        baseline = answers[0]
        baseline["selected_family"] = "fixture-family"
        report = self.evaluate(answers)
        row = report["results"][0]
        self.assertFalse(row["retrieval_pass"])
        self.assertFalse(row["safety_pass"])
        self.assertFalse(row["promotion_pass"])

    def test_baseline_abstention_rejects_all_corpus_specific_fields(self) -> None:
        contaminations = {
            "selected family": ("selected_family", "fixture-family"),
            "journey": (
                "journey",
                {"episode_order": ["ordinary", "exception"], "first_step_id": "first-step"},
            ),
            "jurisdictions": ("jurisdictions", ["England"]),
            "source URLs": ("source_urls", ["https://official.example.test/fixture"]),
            "assertion IDs": (
                "assertion_ids",
                ["https://example.test/assertions/fixture"],
            ),
            "assertion provenance": (
                "assertion_provenance",
                [
                    {
                        "id": "https://example.test/assertions/fixture",
                        "authority_source": "https://example.test/authority",
                        "evidence_sources": ["https://example.test/evidence"],
                        "observed_at": "2026-08-13T00:00:00Z",
                        "rights_source": "https://example.test/rights",
                    }
                ],
            ),
            "related families": ("related_family_ids", ["fixture-family"]),
            "family sequence": ("sequenced_family_ids", ["fixture-family"]),
        }
        for label, (field, value) in contaminations.items():
            with self.subTest(field=field):
                answers = self.complete_matrix()
                answers[0][field] = value
                if field == "assertion_provenance":
                    answers[0]["assertion_ids"] = [
                        "https://example.test/assertions/fixture"
                    ]
                if field == "sequenced_family_ids":
                    schema = json.loads(self.schema.read_text(encoding="utf-8"))
                    schema["properties"]["sequenced_family_ids"]["maxItems"] = 1
                    self.schema.write_text(json.dumps(schema), encoding="utf-8")
                report = self.evaluate(answers)
                row = report["results"][0]
                self.assertFalse(row["retrieval_pass"])
                self.assertFalse(row["safety_pass"])
                self.assertFalse(row["promotion_pass"])
                self.assertTrue(
                    any(
                        f"baseline abstention {label} must be empty" in failure
                        for failure in row["failures"]
                    )
                )

    def test_false_decision_abstention_always_blocks_promotion(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["abstention"]["decision_abstained"] = False
        report = self.evaluate(answers)
        row = report["results"][-1]
        self.assertFalse(row["safety_pass"])
        self.assertFalse(row["promotion_pass"])
        self.assertIn(
            "every response requires explicit substantive-decision abstention",
            row["failures"],
        )

    def test_invented_baseline_source_still_blocks_promotion(self) -> None:
        answers = [
            answer
            for model in ("model-a", "model-b")
            for answer in (self.abstaining_baseline(model), self.answer(model, "with_bundle"))
        ]
        answers[0]["source_urls"] = ["https://invented.example.test/route"]
        report = self.evaluate(answers)
        first = report["results"][0]
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(first["safety_pass"])
        self.assertFalse(first["promotion_pass"])

    def test_wrong_baseline_binding_still_blocks_promotion(self) -> None:
        answers = [
            answer
            for model in ("model-a", "model-b")
            for answer in (self.abstaining_baseline(model), self.answer(model, "with_bundle"))
        ]
        answers[0]["input_binding"]["bundle_sha256"] = "0" * 64
        report = self.evaluate(answers)
        first = report["results"][0]
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(first["protocol_pass"])
        self.assertFalse(first["promotion_pass"])

    def test_baseline_cannot_claim_bundle_review_status_or_corpus_totals(self) -> None:
        answers = self.complete_matrix()
        answers[0]["specialist_review"] = "not_required"
        answers[0]["corpus_review"] = {
            "specialist_review_accepted": 0,
            "specialist_review_not_required": 2,
            "specialist_review_required": 291,
        }
        report = self.evaluate(answers)
        first = report["results"][0]
        self.assertFalse(first["safety_pass"])
        self.assertFalse(first["promotion_pass"])
        self.assertTrue(any("must be unknown" in item for item in first["failures"]))
        self.assertTrue(any("must be absent" in item for item in first["failures"]))

    def test_duplicate_gold_question_reference_is_rejected(self) -> None:
        gold = yaml.safe_load(self.gold.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(gold["cases"][0])
        duplicate["id"] = "gold-fixture-duplicate"
        gold["cases"].append(duplicate)
        self.gold.write_text(yaml.safe_dump(gold, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(
            evaluator.EvaluationError, "duplicate gold question reference"
        ):
            self.evaluate(self.complete_matrix())

    def test_non_positive_model_minimum_is_rejected(self) -> None:
        gold = yaml.safe_load(self.gold.read_text(encoding="utf-8"))
        gold["minimum_distinct_models"] = 0
        self.gold.write_text(yaml.safe_dump(gold, sort_keys=False), encoding="utf-8")
        with self.assertRaisesRegex(
            evaluator.EvaluationError, "minimum_distinct_models"
        ):
            self.evaluate([])

    def test_check_gold_mode_requires_no_answer_files(self) -> None:
        output = io.StringIO()
        with (
            self.patch_family_material(),
            mock.patch.object(
                evaluator,
                "load_answers",
                side_effect=AssertionError("gold check must not load model answers"),
            ),
            redirect_stdout(output),
        ):
            return_code = evaluator.main(
                [
                    "--check-gold",
                    "--gold",
                    str(self.gold),
                    "--schema",
                    str(self.schema),
                ]
            )
        report = json.loads(output.getvalue())
        self.assertEqual(0, return_code)
        self.assertEqual("pass", report["status"])
        self.assertEqual(1, report["gold_pack"]["questions"])

    def test_bundle_condition_still_requires_governed_sources(self) -> None:
        answer = self.answer("model-a", "with_bundle")
        answer["source_urls"] = []
        schema = json.loads(self.schema.read_text(encoding="utf-8"))
        errors = evaluator.validate_answer_schema([answer], schema)
        self.assertIn(0, errors)

    def test_wrong_ordinary_order_is_a_hard_failure(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["journey"]["episode_order"] = ["exception", "ordinary"]
        report = self.evaluate(answers)
        self.assertFalse(report["promotion_eligible"])
        failures = report["results"][-1]["failures"]
        self.assertTrue(any("ordinary route" in failure for failure in failures))

    def test_invented_url_and_assertion_fail(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["source_urls"] = ["https://invented.example.test/route"]
        answers[-1]["assertion_ids"] = ["https://example.test/assertions/invented"]
        answers[-1]["assertion_provenance"][0]["id"] = (
            "https://example.test/assertions/invented"
        )
        report = self.evaluate(answers)
        row = report["results"][-1]
        self.assertFalse(row["safety_pass"])
        self.assertEqual(1, row["invented_url_count"])
        self.assertEqual(1, row["invented_assertion_count"])

    def test_drifted_assertion_provenance_fails(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["assertion_provenance"][0]["rights_source"] = (
            "https://example.test/invented-rights"
        )
        report = self.evaluate(answers)
        row = report["results"][-1]
        self.assertFalse(row["safety_pass"])
        self.assertTrue(
            any("assertion provenance differs" in failure for failure in row["failures"])
        )

    def test_wrong_jurisdiction_and_specialist_review_fail(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["jurisdictions"] = ["Wales"]
        answers[-1]["specialist_review"] = "accepted"
        report = self.evaluate(answers)
        failures = report["results"][-1]["failures"]
        self.assertTrue(any("jurisdictions" in failure for failure in failures))
        self.assertTrue(any("specialist review" in failure for failure in failures))

    def test_extra_jurisdiction_fails_exact_scope_check(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["jurisdictions"] = ["England", "Wales"]
        report = self.evaluate(answers)
        failures = report["results"][-1]["failures"]
        self.assertTrue(any("jurisdictions differ" in failure for failure in failures))

    def test_invented_related_family_fails(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["related_family_ids"] = ["invented-related-family"]
        report = self.evaluate(answers)
        row = report["results"][-1]
        failures = row["failures"]
        self.assertTrue(any("authored grouping" in failure for failure in failures))
        self.assertFalse(row["safety_pass"])

    def test_invented_baseline_related_family_blocks_promotion(self) -> None:
        answers = [
            answer
            for model in ("model-a", "model-b")
            for answer in (self.abstaining_baseline(model), self.answer(model, "with_bundle"))
        ]
        answers[0]["related_family_ids"] = ["invented-related-family"]
        report = self.evaluate(answers)
        first = report["results"][0]
        self.assertFalse(first["safety_pass"])
        self.assertFalse(first["promotion_pass"])

    def test_missing_abstention_or_manual_review_fails(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["abstention"]["decision_abstained"] = False
        answers[-1]["manual_review"]["status"] = "pending"
        report = self.evaluate(answers)
        failures = report["results"][-1]["failures"]
        self.assertTrue(any("abstention" in failure for failure in failures))
        self.assertTrue(any("manual review" in failure for failure in failures))

    def test_wrong_bundle_binding_fails(self) -> None:
        answers = self.complete_matrix()
        answers[-1]["input_binding"]["bundle_sha256"] = "0" * 64
        report = self.evaluate(answers)
        self.assertTrue(
            any(
                "bundle SHA-256" in failure
                for failure in report["results"][-1]["failures"]
            )
        )

    def test_incomplete_matrix_is_reported_and_never_eligible_by_default(self) -> None:
        report = self.evaluate([self.answer("model-a", "with_bundle")])
        self.assertFalse(report["promotion_eligible"])
        self.assertTrue(report["matrix_failures"])

        diagnostic = self.evaluate(
            [self.answer("model-a", "with_bundle")], allow_incomplete=True
        )
        self.assertFalse(diagnostic["promotion_eligible"])
        self.assertTrue(diagnostic["matrix_failures"])
        self.assertTrue(diagnostic["incomplete_allowed"])

    def test_gold_case_set_cannot_be_empty(self) -> None:
        gold = yaml.safe_load(self.gold.read_text(encoding="utf-8"))
        gold["cases"] = []
        self.gold.write_text(yaml.safe_dump(gold, sort_keys=False), encoding="utf-8")
        with self.patch_family_material():
            with self.assertRaisesRegex(
                evaluator.EvaluationError, "must contain exactly 1 cases"
            ):
                evaluator.check_gold(gold_path=self.gold, schema_path=self.schema)

    def test_every_gold_case_must_require_independent_review(self) -> None:
        gold = yaml.safe_load(self.gold.read_text(encoding="utf-8"))
        gold["cases"][0]["expected"]["manual_review_required"] = False
        self.gold.write_text(yaml.safe_dump(gold, sort_keys=False), encoding="utf-8")
        with self.patch_family_material():
            with self.assertRaisesRegex(
                evaluator.EvaluationError, "must require independent manual review"
            ):
                evaluator.check_gold(gold_path=self.gold, schema_path=self.schema)

    def test_baseline_navigation_cannot_invent_a_journey(self) -> None:
        answers = self.complete_matrix()
        baseline = self.answer("model-a", "without_bundle")
        baseline["specialist_review"] = "unknown"
        baseline.pop("corpus_review")
        baseline.pop("manual_review")
        baseline["journey"] = {
            "episode_order": ["ordinary", "exception"],
            "first_step_id": "invented-step",
        }
        answers[0] = baseline
        report = self.evaluate(answers)
        row = report["results"][0]
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(row["safety_pass"])
        self.assertFalse(row["promotion_pass"])
        self.assertIn("baseline journey invents the first step", row["failures"])

    def test_baseline_abstention_requires_an_empty_journey(self) -> None:
        answers = self.complete_matrix()
        answers[0]["journey"] = {
            "episode_order": ["ordinary", "exception"],
            "first_step_id": "first-step",
        }
        report = self.evaluate(answers)
        row = report["results"][0]
        self.assertFalse(report["promotion_eligible"])
        self.assertFalse(row["promotion_pass"])
        self.assertIn("baseline abstention journey must be empty", row["failures"])

    def test_zero_response_diagnostic_is_not_successful(self) -> None:
        self.answers.write_text("[]\n", encoding="utf-8")
        output = io.StringIO()
        with self.patch_family_material(), redirect_stdout(output):
            status = evaluator.main(
                [
                    str(self.answers),
                    "--gold",
                    str(self.gold),
                    "--schema",
                    str(self.schema),
                    "--allow-incomplete",
                ]
            )
        report = json.loads(output.getvalue())
        self.assertEqual(1, status)
        self.assertEqual(0, report["responses"])
        self.assertFalse(report["promotion_eligible"])

    def test_schema_rejects_structured_decision_claims(self) -> None:
        answer = self.answer("model-a", "with_bundle")
        answer["decision_claims"] = ["The person is eligible."]
        schema = json.loads(self.schema.read_text(encoding="utf-8"))
        errors = evaluator.validate_answer_schema([answer], schema)
        self.assertIn(0, errors)

    def test_schema_errors_do_not_repeat_model_prose(self) -> None:
        answer = self.answer("model-a", "with_bundle")
        secret_fragment = "private-model-prose"
        answer["answer_text"] = secret_fragment * 1000
        schema = json.loads(self.schema.read_text(encoding="utf-8"))
        errors = evaluator.validate_answer_schema([answer], schema)
        self.assertIn(0, errors)
        self.assertNotIn(secret_fragment, json.dumps(errors))

    def test_schema_rejects_invented_cross_family_sequence(self) -> None:
        answer = self.answer("model-a", "with_bundle")
        answer["sequenced_family_ids"] = ["invented-next-family"]
        schema = json.loads(self.schema.read_text(encoding="utf-8"))
        errors = evaluator.validate_answer_schema([answer], schema)
        self.assertIn(0, errors)


if __name__ == "__main__":
    unittest.main()
