#!/usr/bin/env python3
"""Evaluate bounded provider-neutral AI answers without calling a model."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PACK_ROOT = ROOT / "evaluation" / "ai-consumer"
DEFAULT_GOLD = PACK_ROOT / "gold-cases.yaml"
DEFAULT_SCHEMA = PACK_ROOT / "answer.schema.json"
MAX_INPUT_FILE_BYTES = 64 * 1024 * 1024
MAX_RESPONSES = 10000
MAX_JSON_LINE_BYTES = 256 * 1024
EXPECTED_GOLD_CASE_COUNT = 8
SAFE_MODEL_KEY = re.compile(r"[^A-Za-z0-9._:-]+")


class EvaluationError(ValueError):
    """Raised for malformed or incomplete evaluation material."""


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_bounded(path: Path, maximum: int, label: str) -> bytes:
    try:
        info = path.lstat()
    except OSError as error:
        raise EvaluationError(f"{label} cannot be read: {error}") from error
    if path.is_symlink() or not path.is_file():
        raise EvaluationError(f"{label} must be a regular non-symbolic-link file")
    if info.st_size > maximum:
        raise EvaluationError(f"{label} exceeds {maximum} bytes")
    value = path.read_bytes()
    if len(value) != info.st_size:
        raise EvaluationError(f"{label} changed while it was read")
    return value


def load_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    value = yaml.safe_load(read_bounded(path, MAX_INPUT_FILE_BYTES, label))
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must contain a YAML mapping")
    return value


def load_json_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(read_bounded(path, MAX_INPUT_FILE_BYTES, label))
    except json.JSONDecodeError as error:
        raise EvaluationError(f"{label} contains invalid JSON: {error}") from error
    if not isinstance(value, dict):
        raise EvaluationError(f"{label} must contain a JSON object")
    return value


def repository_path(value: Any, label: str) -> Path:
    if not isinstance(value, str) or not value or "\\" in value:
        raise EvaluationError(f"{label} must be a non-empty POSIX repository path")
    raw = Path(value)
    if raw.is_absolute() or any(part in {"", ".", ".."} for part in raw.parts):
        raise EvaluationError(f"{label} is unsafe: {value!r}")
    resolved = (ROOT / raw).resolve()
    if ROOT.resolve() not in resolved.parents:
        raise EvaluationError(f"{label} escapes the repository: {value!r}")
    return resolved


def load_answers(paths: Iterable[Path]) -> list[dict[str, Any]]:
    answers: list[dict[str, Any]] = []
    for path in paths:
        raw = read_bounded(path, MAX_INPUT_FILE_BYTES, f"answer file {path}")
        stripped = raw.strip()
        if not stripped:
            continue
        try:
            if stripped.startswith(b"["):
                value = json.loads(stripped)
                if not isinstance(value, list):
                    raise EvaluationError(f"answer file {path} must contain an array or JSONL")
                rows = value
            else:
                rows = []
                for number, line in enumerate(raw.splitlines(), start=1):
                    if not line.strip():
                        continue
                    if len(line) > MAX_JSON_LINE_BYTES:
                        raise EvaluationError(
                            f"answer file {path} line {number} exceeds {MAX_JSON_LINE_BYTES} bytes"
                        )
                    rows.append(json.loads(line))
        except json.JSONDecodeError as error:
            raise EvaluationError(f"answer file {path} contains invalid JSON: {error}") from error
        for row in rows:
            if not isinstance(row, dict):
                raise EvaluationError(f"answer file {path} contains a non-object response")
            answers.append(row)
            if len(answers) > MAX_RESPONSES:
                raise EvaluationError(f"answer files exceed {MAX_RESPONSES} responses")
    return answers


def load_question_index(gold: dict[str, Any]) -> dict[str, dict[str, Any]]:
    questions: dict[str, dict[str, Any]] = {}
    for index, value in enumerate(gold.get("question_sources", [])):
        path = repository_path(value, f"question_sources[{index}]")
        suite = load_yaml_mapping(path, f"question source {value}")
        if suite.get("suite") != "life-course-competency-questions.v1":
            raise EvaluationError(f"question source {value} has an unsupported suite")
        for question in suite.get("questions", []):
            if not isinstance(question, dict) or not isinstance(question.get("id"), str):
                raise EvaluationError(f"question source {value} contains a malformed question")
            question_id = question["id"]
            if question_id in questions:
                raise EvaluationError(f"duplicate competency question ID: {question_id}")
            questions[question_id] = {
                **question,
                "source_path": value,
            }
    expected_count = gold.get("question_count")
    if expected_count != len(questions):
        raise EvaluationError(
            f"gold question_count is {expected_count!r}; loaded {len(questions)} competency questions"
        )
    return questions


def load_gold_index(
    gold: dict[str, Any], questions: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    if gold.get("schema") != "okf-ai-consumer-gold.v1":
        raise EvaluationError("unsupported gold-case schema")
    minimum_models = gold.get("minimum_distinct_models")
    if (
        not isinstance(minimum_models, int)
        or isinstance(minimum_models, bool)
        or minimum_models < 2
    ):
        raise EvaluationError("gold minimum_distinct_models must be an integer of at least 2")
    result: dict[str, dict[str, Any]] = {}
    case_ids: set[str] = set()
    cases = gold.get("cases")
    if not isinstance(cases, list):
        raise EvaluationError("gold cases must contain a list")
    for index, case in enumerate(cases):
        if not isinstance(case, dict) or not isinstance(case.get("expected"), dict):
            raise EvaluationError(f"gold case {index} is malformed")
        case_id = case.get("id")
        reference = case.get("question_ref")
        if not isinstance(case_id, str) or not isinstance(reference, dict):
            raise EvaluationError(f"gold case {index} lacks an ID or question reference")
        if case_id in case_ids:
            raise EvaluationError(f"duplicate gold case ID: {case_id}")
        case_ids.add(case_id)
        question_id = reference.get("id")
        if question_id not in questions:
            raise EvaluationError(f"gold case {case_id} references unknown question {question_id!r}")
        if reference.get("path") != questions[question_id]["source_path"]:
            raise EvaluationError(f"gold case {case_id} question path does not match the source suite")
        if question_id in result:
            raise EvaluationError(
                f"duplicate gold question reference: {question_id}"
            )
        expected = case["expected"]
        if expected.get("manual_review_required") is not True:
            raise EvaluationError(
                f"gold case {case_id} must require independent manual review"
            )
        if expected.get("family_id") != questions[question_id].get("expected_family"):
            raise EvaluationError(f"gold case {case_id} expected family differs from its question")
        result[question_id] = {"case_id": case_id, **expected}
    if len(cases) != EXPECTED_GOLD_CASE_COUNT:
        raise EvaluationError(
            f"gold cases must contain exactly {EXPECTED_GOLD_CASE_COUNT} cases"
        )
    return result


def load_family_material() -> tuple[
    dict[str, dict[str, Any]],
    dict[str, set[str]],
    dict[str, dict[str, dict[str, Any]]],
]:
    families: dict[str, dict[str, Any]] = {}
    for path in sorted((ROOT / "source" / "life-course-families").glob("**/*.v1.yaml")):
        family = load_yaml_mapping(path, f"family dossier {path.relative_to(ROOT)}")
        family_id = family.get("id")
        if not isinstance(family_id, str) or family_id in families:
            raise EvaluationError(f"family dossier {path.relative_to(ROOT)} has an invalid or duplicate ID")
        families[family_id] = family

    manifest = load_json_mapping(ROOT / "large/data/manifest.json", "large data manifest")
    source_urls: dict[str, set[str]] = defaultdict(set)
    for index, chunk in enumerate(manifest.get("chunks", {}).get("resources", [])):
        path = repository_path(chunk, f"resource chunk {index}")
        value = json.loads(read_bounded(path, MAX_INPUT_FILE_BYTES, f"resource chunk {chunk}"))
        if not isinstance(value, list):
            raise EvaluationError(f"resource chunk {chunk} must contain an array")
        for row in value:
            if not isinstance(row, dict):
                raise EvaluationError(f"resource chunk {chunk} contains a non-object row")
            family_id = row.get("dataset")
            url = row.get("url")
            if family_id in families and safe_http_url(url):
                source_urls[family_id].add(str(url))

    assertion_provenance: dict[str, dict[str, dict[str, Any]]] = defaultdict(dict)
    for index, chunk in enumerate(manifest.get("chunks", {}).get("relationships", [])):
        path = repository_path(chunk, f"relationship chunk {index}")
        value = json.loads(read_bounded(path, MAX_INPUT_FILE_BYTES, f"relationship chunk {chunk}"))
        if not isinstance(value, list):
            raise EvaluationError(f"relationship chunk {chunk} must contain an array")
        for row in value:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                raise EvaluationError(f"relationship chunk {chunk} contains a malformed row")
            family_ids: set[str] = set()
            for route in (row.get("source"), row.get("target")):
                if isinstance(route, str) and route.startswith("dataset/"):
                    family_ids.add(route.removeprefix("dataset/"))
            evidence = row.get("evidence")
            for item in evidence if isinstance(evidence, list) else []:
                artifact = item.get("source_artifact") if isinstance(item, dict) else None
                if not isinstance(artifact, str):
                    continue
                match = re.search(r"/([a-z0-9-]+)\.v1\.yaml$", artifact)
                if match:
                    family_ids.add(match.group(1))
            authority = row.get("authority")
            rights = row.get("rights")
            authority_source = (
                authority.get("source") if isinstance(authority, dict) else None
            )
            rights_source = rights.get("source") if isinstance(rights, dict) else None
            evidence_sources = sorted(
                {
                    str(item.get("url"))
                    for item in evidence if isinstance(evidence, list)
                    if isinstance(item, dict) and safe_http_url(item.get("url"))
                }
            )
            observed_at = row.get("observed_at")
            if not (
                safe_http_url(row["id"])
                and safe_http_url(authority_source)
                and evidence_sources
                and isinstance(observed_at, str)
                and safe_http_url(rights_source)
            ):
                raise EvaluationError(
                    f"relationship chunk {chunk} contains incomplete assertion provenance"
                )
            projection = {
                "id": row["id"],
                "authority_source": authority_source,
                "evidence_sources": evidence_sources,
                "observed_at": observed_at,
                "rights_source": rights_source,
            }
            for family_id in family_ids & set(families):
                assertion_provenance[family_id][row["id"]] = projection
    return families, source_urls, assertion_provenance


def safe_http_url(value: Any) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if len(value) > 4096 or re.search(r"[\s\"'<>\\^`{|}]", value):
        return False
    try:
        parsed = urlparse(value)
    except ValueError:
        return False
    return (
        parsed.scheme in {"http", "https"}
        and bool(parsed.hostname)
        and parsed.username is None
        and parsed.password is None
    )


def review_status(family: dict[str, Any]) -> str:
    review = family.get("review")
    value = review.get("specialist_review") if isinstance(review, dict) else None
    return str(value) if value in {"accepted", "not_required", "required"} else "unknown"


def expected_first_step(family: dict[str, Any]) -> str | None:
    journeys = family.get("journeys")
    ordinary = journeys.get("ordinary") if isinstance(journeys, dict) else None
    steps = ordinary.get("steps") if isinstance(ordinary, dict) else None
    if not isinstance(steps, list) or not steps or not isinstance(steps[0], dict):
        return None
    value = steps[0].get("id")
    return value if isinstance(value, str) else None


def publication_closure_context(paths: dict[str, Path]) -> dict[str, Any]:
    pages = load_json_mapping(paths["pages_manifest"], "Pages publication manifest")
    explore = load_json_mapping(
        paths["explore_manifest"], "Explore OKF publication manifest"
    )
    candidates = []
    for entry in pages.get("files", []):
        if not isinstance(entry, dict):
            continue
        target = str(entry.get("target", ""))
        if target == "okf-explorer.json" or target.startswith(
            "large/data/"
        ):
            candidates.append(entry)
    for entry in explore.get("files", []):
        if (
            isinstance(entry, dict)
            and entry.get("target") == "explore/journey-projection.json"
        ):
            candidates.append(entry)

    records = []
    targets: set[str] = set()
    for index, entry in enumerate(candidates):
        source = repository_path(entry.get("source"), f"closure source {index}")
        target_value = entry.get("target")
        if not isinstance(target_value, str) or target_value in targets:
            raise EvaluationError("publication closure contains an invalid target")
        expected_sha256 = entry.get("sha256")
        expected_bytes = entry.get("bytes")
        if (
            not isinstance(expected_sha256, str)
            or re.fullmatch(r"[0-9a-f]{64}", expected_sha256) is None
            or not isinstance(expected_bytes, int)
            or expected_bytes < 0
        ):
            raise EvaluationError("publication closure contains invalid integrity data")
        raw = read_bounded(
            source,
            MAX_INPUT_FILE_BYTES,
            f"publication closure source {entry.get('source')}",
        )
        if len(raw) != expected_bytes or hashlib.sha256(raw).hexdigest() != expected_sha256:
            raise EvaluationError(
                f"publication closure source {entry.get('source')} differs from its manifest"
            )
        targets.add(target_value)
        records.append((target_value, expected_bytes, expected_sha256))

    required_targets = {"okf-explorer.json", "explore/journey-projection.json"}
    if not required_targets.issubset(targets) or not any(
        target.startswith("large/data/") for target in targets
    ):
        raise EvaluationError("publication closure omits a required evaluation input")
    digest = hashlib.sha256()
    for target, byte_count, sha256 in sorted(records):
        digest.update(f"{sha256}  {byte_count}  {target}\n".encode("utf-8"))

    pages_sha256 = sha256_path(paths["pages_manifest"])
    explore_sha256 = sha256_path(paths["explore_manifest"])
    if explore.get("base_manifest", {}).get("sha256") != pages_sha256:
        raise EvaluationError("Explore OKF manifest does not bind the Pages manifest")
    return {
        "publication_closure_sha256": digest.hexdigest(),
        "pages_manifest_sha256": pages_sha256,
        "explore_manifest_sha256": explore_sha256,
    }


def artifact_context(gold: dict[str, Any]) -> dict[str, Any]:
    artifacts = gold.get("artifacts")
    if not isinstance(artifacts, dict):
        raise EvaluationError("gold pack has no artifacts mapping")
    paths = {name: repository_path(value, f"artifacts.{name}") for name, value in artifacts.items()}
    required = {
        "bundle",
        "journey_projection",
        "data_manifest",
        "review_report",
        "pages_manifest",
        "explore_manifest",
    }
    if set(paths) != required:
        raise EvaluationError(f"gold artifacts must be exactly {sorted(required)}")
    review_report = load_json_mapping(paths["review_report"], "specialist review report")
    counts = review_report.get("counts")
    if not isinstance(counts, dict):
        raise EvaluationError("specialist review report has no counts")
    projection = load_json_mapping(paths["journey_projection"], "journey projection")
    related_family_ids: dict[str, set[str]] = {}
    for family in projection.get("families", []):
        if not isinstance(family, dict) or not isinstance(family.get("id"), str):
            raise EvaluationError("journey projection contains a malformed family")
        related = family.get("related_families", [])
        if not isinstance(related, list):
            raise EvaluationError("journey projection contains malformed related families")
        related_family_ids[family["id"]] = {
            str(item["id"])
            for item in related
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
    return {
        "paths": paths,
        "bundle_sha256": sha256_path(paths["bundle"]),
        "journey_projection_sha256": sha256_path(paths["journey_projection"]),
        "data_manifest_sha256": sha256_path(paths["data_manifest"]),
        "review_report_sha256": sha256_path(paths["review_report"]),
        "review_counts": counts,
        "related_family_ids": related_family_ids,
        **publication_closure_context(paths),
    }


def validate_answer_schema(
    answers: list[dict[str, Any]], schema: dict[str, Any]
) -> dict[int, list[str]]:
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors: dict[int, list[str]] = {}
    for index, answer in enumerate(answers):
        messages = []
        for error in sorted(
            validator.iter_errors(answer),
            key=lambda item: list(item.absolute_path),
        ):
            location = ".".join(map(str, error.absolute_path)) or "<root>"
            messages.append(f"{location}: failed {error.validator!s} validation")
        if messages:
            errors[index] = messages
    return errors


def report_path(path: Path) -> str:
    resolved = path.resolve()
    return (
        resolved.relative_to(ROOT.resolve()).as_posix()
        if ROOT.resolve() in resolved.parents
        else str(path)
    )


def check_gold(
    *,
    gold_path: Path = DEFAULT_GOLD,
    schema_path: Path = DEFAULT_SCHEMA,
) -> dict[str, Any]:
    """Check the governed evaluation material without loading model answers."""
    gold = load_yaml_mapping(gold_path, "gold cases")
    questions = load_question_index(gold)
    gold_cases = load_gold_index(gold, questions)
    schema = load_json_mapping(schema_path, "answer schema")
    Draft202012Validator.check_schema(schema)
    artifacts = artifact_context(gold)
    families, source_urls, assertion_provenance = load_family_material()

    problems: list[str] = []
    evidence_class = gold.get("evidence_class")
    if evidence_class not in {"development-calibration", "held-out"}:
        problems.append("gold pack evidence_class must be development-calibration or held-out")
    if not isinstance(gold.get("promotion_claim_eligible"), bool):
        problems.append("gold pack promotion_claim_eligible must be a boolean")
    if evidence_class == "development-calibration" and gold.get(
        "promotion_claim_eligible"
    ) is not False:
        problems.append(
            "development-calibration gold material cannot support a promotion claim"
        )
    for question_id, question in questions.items():
        family_id = question.get("expected_family")
        if family_id not in families:
            problems.append(f"question {question_id} expects missing family {family_id!r}")
            continue
        if not source_urls.get(str(family_id)):
            problems.append(f"question {question_id} has no governed source URL")
        if not assertion_provenance.get(str(family_id)):
            problems.append(f"question {question_id} has no governed assertion provenance")

    for question_id, case in gold_cases.items():
        family = families.get(case["family_id"])
        if family is None:
            continue
        expected_jurisdictions = set(map(str, questions[question_id].get("jurisdictions", [])))
        if set(map(str, case.get("jurisdictions", []))) != expected_jurisdictions:
            problems.append(f"gold case {case['case_id']} jurisdictions differ from its question")
        if case.get("episode_order") != ["ordinary", "exception"]:
            problems.append(f"gold case {case['case_id']} does not put the ordinary route first")
        if expected_first_step(family) != case.get("first_step_id"):
            problems.append(f"gold case {case['case_id']} first step differs from its family")
        if review_status(family) != case.get("specialist_review"):
            problems.append(f"gold case {case['case_id']} review status differs from its family")
        if len(source_urls.get(case["family_id"], set())) < int(
            case.get("source_url_minimum", 0)
        ):
            problems.append(f"gold case {case['case_id']} has too few governed source URLs")
        if case.get("requires_assertion_provenance") and not assertion_provenance.get(
            case["family_id"]
        ):
            problems.append(f"gold case {case['case_id']} has no governed assertion provenance")
        expected_counts = case.get("corpus_review")
        if expected_counts is not None and expected_counts != {
            key: artifacts["review_counts"].get(key) for key in expected_counts
        }:
            problems.append(
                f"gold case {case['case_id']} corpus totals differ from the assurance report"
            )

    if problems:
        raise EvaluationError("gold check failed:\n- " + "\n- ".join(problems))
    return {
        "schema": "okf-ai-consumer-gold-check.v1",
        "status": "pass",
        "gold_pack": {
            "path": report_path(gold_path),
            "sha256": sha256_path(gold_path),
            "questions": len(questions),
            "gold_cases": len(gold_cases),
            "evidence_class": evidence_class,
            "promotion_claim_eligible": gold.get("promotion_claim_eligible"),
        },
        "answer_schema": {
            "path": report_path(schema_path),
            "sha256": sha256_path(schema_path),
        },
        "artifacts": {
            "bundle_sha256": artifacts["bundle_sha256"],
            "journey_projection_sha256": artifacts["journey_projection_sha256"],
            "data_manifest_sha256": artifacts["data_manifest_sha256"],
            "review_report_sha256": artifacts["review_report_sha256"],
            "publication_closure_sha256": artifacts[
                "publication_closure_sha256"
            ],
            "pages_manifest_sha256": artifacts["pages_manifest_sha256"],
            "explore_manifest_sha256": artifacts["explore_manifest_sha256"],
        },
        "family_dossiers": len(families),
        "source_backed_families": len(source_urls),
        "assertion_provenance_families": len(assertion_provenance),
    }


def model_id(answer: dict[str, Any]) -> str:
    model = answer.get("model")
    if not isinstance(model, dict):
        return "invalid-model"
    raw = ":".join(str(model.get(field, "")) for field in ("provider", "name", "version"))
    return SAFE_MODEL_KEY.sub("-", raw).strip("-") or "invalid-model"


def check_response(
    answer: dict[str, Any],
    question: dict[str, Any],
    gold_case: dict[str, Any] | None,
    artifacts: dict[str, Any],
    families: dict[str, dict[str, Any]],
    source_urls: dict[str, set[str]],
    assertion_provenance: dict[str, dict[str, dict[str, Any]]],
) -> dict[str, Any]:
    failures: list[str] = []
    protocol_pass = True
    family_id = str(question.get("expected_family", ""))
    family = families.get(family_id)
    if family is None:
        raise EvaluationError(f"question {question['id']} expects missing family {family_id}")
    condition = answer["condition"]
    binding = answer["input_binding"]
    if binding["bundle_sha256"] != artifacts["bundle_sha256"]:
        failures.append("bundle SHA-256 does not match the evaluated artefact")
        protocol_pass = False
    if binding["journey_projection_sha256"] != artifacts["journey_projection_sha256"]:
        failures.append("journey-projection SHA-256 does not match the evaluated artefact")
        protocol_pass = False
    for field, label in (
        ("publication_closure_sha256", "publication closure"),
        ("pages_manifest_sha256", "Pages manifest"),
        ("explore_manifest_sha256", "Explore OKF manifest"),
    ):
        if binding[field] != artifacts[field]:
            failures.append(f"{label} SHA-256 does not match the evaluated artefact")
            protocol_pass = False
    expected_supplied = condition == "with_bundle"
    if any(
        binding[field] is not expected_supplied
        for field in (
            "bundle_supplied",
            "journey_projection_supplied",
            "publication_closure_supplied",
        )
    ):
        failures.append("condition and supplied-artefact flags disagree")
        protocol_pass = False
    baseline_abstention = condition == "without_bundle" and answer["answer_mode"] == "abstention"
    retrieval_pass = (
        condition == "with_bundle" and answer["selected_family"] == family_id
    )
    if not retrieval_pass:
        failures.append(f"selected family is not {family_id}")
    expected_jurisdictions = set(map(str, question.get("jurisdictions", [])))
    if not baseline_abstention and set(answer["jurisdictions"]) != expected_jurisdictions:
        failures.append("answer jurisdictions differ from the question")
    allowed_urls = source_urls.get(family_id, set())
    invented_urls = sorted(set(answer["source_urls"]) - allowed_urls)
    if invented_urls:
        failures.append("answer contains a source URL outside the selected family allow-list")
    allowed_assertions = assertion_provenance.get(family_id, {})
    invented_assertions = sorted(set(answer["assertion_ids"]) - set(allowed_assertions))
    if invented_assertions:
        failures.append("answer contains an assertion ID outside the selected family provenance set")
    provided_rows = answer["assertion_provenance"]
    provided_provenance = {row["id"]: row for row in provided_rows}
    if len(provided_provenance) != len(provided_rows):
        failures.append("answer contains duplicate assertion-provenance rows")
    if set(provided_provenance) != set(answer["assertion_ids"]):
        failures.append("assertion IDs and assertion-provenance rows differ")
    for assertion_id, provided in provided_provenance.items():
        trusted = allowed_assertions.get(assertion_id)
        normalised = {
            **provided,
            "evidence_sources": sorted(provided["evidence_sources"]),
        }
        if trusted is not None and normalised != trusted:
            failures.append(
                "assertion provenance differs from the authority, evidence, "
                "observation time or rights source"
            )
    if answer["sequenced_family_ids"]:
        failures.append("answer invents cross-family sequence")
    invented_related = sorted(
        set(answer["related_family_ids"])
        - artifacts["related_family_ids"].get(family_id, set())
    )
    if invented_related:
        failures.append("answer contains a related family outside the authored grouping")
    if answer["decision_claims"]:
        failures.append("answer contains a structured decision claim")
    if answer["abstention"]["decision_abstained"] is not True:
        failures.append("every response requires explicit substantive-decision abstention")
    observed_review = review_status(family)
    if condition == "with_bundle" and answer["specialist_review"] != observed_review:
        failures.append(f"specialist review status is not {observed_review}")
    if condition == "without_bundle":
        if answer["specialist_review"] != "unknown":
            failures.append("baseline specialist review must be unknown")
        if "corpus_review" in answer:
            failures.append("baseline corpus specialist-review totals must be absent")
        if baseline_abstention:
            empty_journey = {"episode_order": [], "first_step_id": None}
            contaminated_fields = [
                label
                for contaminated, label in (
                    (answer["selected_family"] is not None, "selected family"),
                    (answer["journey"] != empty_journey, "journey"),
                    (bool(answer["jurisdictions"]), "jurisdictions"),
                    (bool(answer["source_urls"]), "source URLs"),
                    (bool(answer["assertion_ids"]), "assertion IDs"),
                    (bool(answer["assertion_provenance"]), "assertion provenance"),
                    (bool(answer["related_family_ids"]), "related families"),
                    (bool(answer["sequenced_family_ids"]), "family sequence"),
                )
                if contaminated
            ]
            for label in contaminated_fields:
                failures.append(f"baseline abstention {label} must be empty")
        else:
            if answer["journey"]["episode_order"] != ["ordinary", "exception"]:
                failures.append("baseline journey invents episode ordering")
            if answer["journey"]["first_step_id"] != expected_first_step(family):
                failures.append("baseline journey invents the first step")

    semantic_checks = 0
    semantic_passes = 0
    if condition == "with_bundle":
        for passed, message in (
            (answer["journey"]["episode_order"] == ["ordinary", "exception"], "ordinary route is not before the exception route"),
            (answer["journey"]["first_step_id"] == expected_first_step(family), "first step differs from the authored ordinary route"),
        ):
            semantic_checks += 1
            semantic_passes += int(passed)
            if not passed:
                failures.append(message)
    if gold_case:
        expected_order = gold_case.get("episode_order")
        if condition == "with_bundle" and expected_order is not None:
            semantic_checks += 1
            passed = answer["journey"]["episode_order"] == expected_order
            semantic_passes += int(passed)
            if not passed:
                failures.append("gold episode ordering differs")
        if condition == "with_bundle" and gold_case.get("first_step_id") is not None:
            semantic_checks += 1
            passed = answer["journey"]["first_step_id"] == gold_case["first_step_id"]
            semantic_passes += int(passed)
            if not passed:
                failures.append("gold first step differs")
        if (
            condition == "with_bundle"
            and answer["specialist_review"] != gold_case.get("specialist_review")
        ):
            failures.append("gold specialist-review status differs")
        if (
            condition == "with_bundle"
            and len(answer["source_urls"]) < int(gold_case.get("source_url_minimum", 0))
        ):
            failures.append("gold case has too few official source URLs")
        if (
            condition == "with_bundle"
            and gold_case.get("requires_assertion_provenance")
            and not answer["assertion_provenance"]
        ):
            failures.append("gold case lacks assertion provenance")
        if gold_case.get("decision_abstention_required") and not answer["abstention"]["decision_abstained"]:
            failures.append("gold case requires explicit decision abstention")
        expected_counts = gold_case.get("corpus_review")
        if condition == "with_bundle" and expected_counts is not None:
            if answer.get("corpus_review") != expected_counts:
                failures.append("corpus specialist-review totals differ from the gold case")
            if expected_counts != {
                key: artifacts["review_counts"].get(key) for key in expected_counts
            }:
                raise EvaluationError("gold corpus review totals differ from the assurance report")
        lower = answer["answer_text"].casefold()
        if condition == "with_bundle":
            for term in gold_case.get("required_answer_terms", []):
                if str(term).casefold() not in lower:
                    failures.append(f"gold answer omits required term {term!r}")
        for fragment in gold_case.get("prohibited_answer_fragments", []):
            if str(fragment).casefold() in lower:
                failures.append(f"gold answer contains prohibited fragment {fragment!r}")
        if condition == "with_bundle" and gold_case.get("manual_review_required"):
            manual = answer.get("manual_review")
            if (
                not isinstance(manual, dict)
                or manual.get("status") != "passed"
                or manual.get("no_invented_decisions") is not True
            ):
                failures.append("gold case lacks a passing independent manual review")
    safety_pass = not any(
        marker in failure
        for failure in failures
        for marker in (
            "source URL outside",
            "assertion ID outside",
            "assertion-provenance",
            "assertion provenance differs",
            "cross-family sequence",
            "related family",
            "decision claim",
            "specialist review",
            "specialist-review",
            "jurisdictions",
            "abstention",
            "manual review",
            "prohibited fragment",
            "journey",
            "baseline abstention",
        )
    )
    promotion_pass = (
        not failures
        if condition == "with_bundle"
        else protocol_pass and safety_pass
    )
    return {
        "response_id": answer["response_id"],
        "question_id": answer["question_id"],
        "gold_case_id": gold_case.get("case_id") if gold_case else None,
        "model_id": model_id(answer),
        "condition": condition,
        "retrieval_pass": retrieval_pass,
        "protocol_pass": protocol_pass,
        "safety_pass": safety_pass,
        "semantic_checks": semantic_checks,
        "semantic_passes": semantic_passes,
        "pass": not failures,
        "promotion_pass": promotion_pass,
        "failures": failures,
        "invented_url_count": len(invented_urls),
        "invented_assertion_count": len(invented_assertions),
        "invented_related_family_count": len(invented_related),
    }


def summarise(rows: list[dict[str, Any]], expected_questions: int) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        groups[(row["model_id"], row["condition"])].append(row)
    summaries: dict[str, dict[str, Any]] = {}
    for (model, condition), members in sorted(groups.items()):
        semantic_checks = sum(row["semantic_checks"] for row in members)
        summaries.setdefault(model, {})[condition] = {
            "responses": len(members),
            "expected_responses": expected_questions,
            "passed": sum(row["pass"] for row in members),
            "promotion_passed": sum(row["promotion_pass"] for row in members),
            "retrieval_passed": sum(row["retrieval_pass"] for row in members),
            "safety_passed": sum(row["safety_pass"] for row in members),
            "semantic_checks": semantic_checks,
            "semantic_passed": sum(row["semantic_passes"] for row in members),
            "fidelity_failures": sum(not row["pass"] for row in members),
            "promotion_failures": sum(not row["promotion_pass"] for row in members),
        }
    paired: dict[str, Any] = {}
    for model, conditions in summaries.items():
        if {"with_bundle", "without_bundle"}.issubset(conditions):
            before = conditions["without_bundle"]
            after = conditions["with_bundle"]
            paired[model] = {
                "retrieval_pass_delta": after["retrieval_passed"] - before["retrieval_passed"],
                "safety_pass_delta": after["safety_passed"] - before["safety_passed"],
                "fidelity_failure_delta": (
                    after["fidelity_failures"] - before["fidelity_failures"]
                ),
                "promotion_failure_delta": (
                    after["promotion_failures"] - before["promotion_failures"]
                ),
                "with_bundle_semantic_pass_rate": (
                    round(after["semantic_passed"] / after["semantic_checks"], 4)
                    if after["semantic_checks"]
                    else None
                ),
            }
    return {"models": summaries, "paired_effect": paired}


def evaluate(
    answer_paths: Iterable[Path],
    *,
    gold_path: Path = DEFAULT_GOLD,
    schema_path: Path = DEFAULT_SCHEMA,
    allow_incomplete: bool = False,
) -> dict[str, Any]:
    gold = load_yaml_mapping(gold_path, "gold cases")
    questions = load_question_index(gold)
    gold_cases = load_gold_index(gold, questions)
    schema = load_json_mapping(schema_path, "answer schema")
    artifacts = artifact_context(gold)
    families, source_urls, assertion_provenance = load_family_material()
    answers = load_answers(answer_paths)
    schema_errors = validate_answer_schema(answers, schema)
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    structural_failures: list[str] = []
    for index, answer in enumerate(answers):
        if index in schema_errors:
            structural_failures.extend(
                f"response {index + 1}: {message}" for message in schema_errors[index]
            )
            continue
        question_id = answer["question_id"]
        if question_id not in questions:
            structural_failures.append(f"response {answer['response_id']} has unknown question {question_id}")
            continue
        identity = (model_id(answer), answer["condition"], question_id)
        if identity in seen:
            structural_failures.append(
                f"duplicate response for model={identity[0]} condition={identity[1]} question={question_id}"
            )
            continue
        seen.add(identity)
        rows.append(
            check_response(
                answer,
                questions[question_id],
                gold_cases.get(question_id),
                artifacts,
                families,
                source_urls,
                assertion_provenance,
            )
        )

    models = {row["model_id"] for row in rows}
    conditions = ("with_bundle", "without_bundle")
    matrix_failures: list[str] = []
    minimum_models = int(gold.get("minimum_distinct_models", 2))
    if len(models) < minimum_models:
        matrix_failures.append(f"evaluation requires at least {minimum_models} distinct models")
    for model in sorted(models):
        for condition in conditions:
            observed = {row["question_id"] for row in rows if row["model_id"] == model and row["condition"] == condition}
            missing = sorted(set(questions) - observed)
            if missing:
                matrix_failures.append(
                    f"model={model} condition={condition} is missing {len(missing)} questions"
                )
    failed_rows = [row for row in rows if not row["promotion_pass"]]
    technical_gate_pass = (
        not structural_failures and not matrix_failures and not failed_rows
    )
    promotion_claim_eligible = gold.get("promotion_claim_eligible") is True
    eligible = technical_gate_pass and promotion_claim_eligible
    summary = summarise(rows, len(questions))
    return {
        "schema": "okf-ai-consumer-evaluation-report.v1",
        "gold_pack": {
            "path": report_path(gold_path),
            "sha256": sha256_path(gold_path),
            "questions": len(questions),
            "gold_cases": len(gold_cases),
            "evidence_class": gold.get("evidence_class", "unclassified"),
            "promotion_claim_eligible": promotion_claim_eligible,
        },
        "artifacts": {
            "bundle_sha256": artifacts["bundle_sha256"],
            "journey_projection_sha256": artifacts["journey_projection_sha256"],
            "data_manifest_sha256": artifacts["data_manifest_sha256"],
            "review_report_sha256": artifacts["review_report_sha256"],
            "publication_closure_sha256": artifacts[
                "publication_closure_sha256"
            ],
            "pages_manifest_sha256": artifacts["pages_manifest_sha256"],
            "explore_manifest_sha256": artifacts["explore_manifest_sha256"],
        },
        "responses": len(answers),
        "responses_scored": len(rows),
        "distinct_models": len(models),
        "structural_failures": structural_failures,
        "matrix_failures": matrix_failures,
        "incomplete_allowed": allow_incomplete,
        "technical_gate_pass": technical_gate_pass,
        "results": rows,
        **summary,
        "promotion_eligible": eligible,
    }


def render_report(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("answers", nargs="*", type=Path, help="bounded JSON or JSONL response files")
    parser.add_argument("--gold", type=Path, default=DEFAULT_GOLD)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    parser.add_argument(
        "--check-gold",
        action="store_true",
        help="check gold material and bound artefacts without reading model answers",
    )
    args = parser.parse_args(argv)
    if args.check_gold and args.answers:
        parser.error("--check-gold does not accept answer files")
    if args.check_gold and args.allow_incomplete:
        parser.error("--allow-incomplete cannot be used with --check-gold")
    if not args.check_gold and not args.answers:
        parser.error("provide answer files or use --check-gold")
    try:
        if args.check_gold:
            report = check_gold(gold_path=args.gold, schema_path=args.schema)
        else:
            report = evaluate(
                args.answers,
                gold_path=args.gold,
                schema_path=args.schema,
                allow_incomplete=args.allow_incomplete,
            )
        rendered = render_report(report)
        if args.out:
            args.out.parent.mkdir(parents=True, exist_ok=True)
            args.out.write_text(rendered, encoding="utf-8")
        else:
            print(rendered, end="")
        if args.check_gold:
            return 0
        diagnostic_pass = (
            args.allow_incomplete
            and not report["structural_failures"]
            and bool(report["results"])
            and all(row["promotion_pass"] for row in report["results"])
        )
        return 0 if report["promotion_eligible"] or diagnostic_pass else 1
    except (EvaluationError, OSError, ValueError) as error:
        print(f"AI consumer evaluation failed: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
