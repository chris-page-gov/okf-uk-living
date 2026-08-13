#!/usr/bin/env python3
"""Run one isolated, answer-blind cell of the AI consumer comparison."""

from __future__ import annotations

import argparse
import copy
import ctypes
import errno
import hashlib
import json
import os
import pwd
import re
import selectors
import signal
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = Path(__file__).resolve()
PACK_ROOT = ROOT / "evaluation" / "ai-consumer"
GOLD_PATH = PACK_ROOT / "gold-cases.yaml"
PILOT_SCHEMA_PATH = PACK_ROOT / "pilot-output.schema.json"
ANSWER_SCHEMA_PATH = PACK_ROOT / "answer.schema.json"
CLAUDE_SANDBOX_PATH = PACK_ROOT / "claude-pilot.sb"
CLAUDE_TOKEN_KEYCHAIN_SERVICE = "okf-ai-consumer-claude-token"
RUNS_ROOT = PACK_ROOT / "runs"
PAGES_MANIFEST_PATH = ROOT / "publication" / "pages-file-manifest.json"
EXPLORE_MANIFEST_PATH = ROOT / "publication" / "explore-okf-file-manifest.json"
MAX_CAPTURE_BYTES = 16 * 1024 * 1024
TIMEOUT_SECONDS = 40 * 60
COPY_CHUNK_BYTES = 1024 * 1024
ISOLATED_TEMP_ROOT = Path("/private/tmp")
RENAME_EXCL = 0x00000004
CAPTURE_READ_BYTES = 64 * 1024
PROCESS_TERMINATION_GRACE_SECONDS = 1.0
MODEL_ENVIRONMENT_KEYS = (
    "HOME",
    "LANG",
    "LC_ALL",
    "LOGNAME",
    "PATH",
    "SHELL",
    "USER",
)


class PilotError(ValueError):
    """Raised when a pilot cell cannot be captured safely."""


CLAUDE_JSON_FENCE = re.compile(
    r"\A```(?:json)?[ \t]*\r?\n(?P<payload>\{.*\})\r?\n```\Z",
    re.IGNORECASE | re.DOTALL,
)
CLAUDE_JSON_FENCE_BLOCK = re.compile(
    r"```(?:json)?[ \t]*\r?\n(?P<payload>.*?)\r?\n```",
    re.IGNORECASE | re.DOTALL,
)


def current_home_root() -> Path:
    """Return the canonical home directory that the Claude sandbox must deny."""
    try:
        home = Path(pwd.getpwuid(os.getuid()).pw_dir).resolve(strict=True)
    except (KeyError, OSError) as error:
        raise PilotError(
            "cannot resolve the current account home for the Claude sandbox"
        ) from error
    if not home.is_absolute() or home == Path("/"):
        raise PilotError("current account home is unsafe for the Claude sandbox")
    return home


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(COPY_CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def decode_claude_result(result: str) -> tuple[dict[str, Any] | None, str]:
    """Extract one unambiguous JSON object without interpreting wrapper prose."""
    candidate = result.strip()
    try:
        decoded = json.loads(candidate)
    except json.JSONDecodeError:
        decoded = None
    if isinstance(decoded, dict):
        return decoded, "direct-json-result"

    whole_fence = CLAUDE_JSON_FENCE.fullmatch(candidate)
    if whole_fence:
        try:
            decoded = json.loads(whole_fence.group("payload"))
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, dict):
            return decoded, "whole-fenced-json-result"

    fence_blocks = list(CLAUDE_JSON_FENCE_BLOCK.finditer(candidate))
    if len(fence_blocks) == 1:
        block = fence_blocks[0]
        wrapper = candidate[: block.start()] + candidate[block.end() :]
        try:
            decoded = json.loads(block.group("payload"))
        except json.JSONDecodeError:
            decoded = None
        if (
            isinstance(decoded, dict)
            and not any(character in wrapper for character in "{}")
        ):
            return decoded, "single-embedded-fenced-json-result"
    if fence_blocks:
        return None, "unparseable-json-result"

    first_object = candidate.find("{")
    if first_object >= 0:
        try:
            decoded, end = json.JSONDecoder().raw_decode(candidate, first_object)
        except json.JSONDecodeError:
            decoded = None
            end = first_object
        prefix = candidate[:first_object]
        suffix = candidate[end:]
        if (
            isinstance(decoded, dict)
            and not any(character in prefix + suffix for character in "{}")
        ):
            return decoded, "single-embedded-json-result"
    return None, "unparseable-json-result"


def read_mapping(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PilotError(f"{path.relative_to(ROOT)} must contain a mapping")
    return value


def read_json_mapping(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise PilotError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def json_mapping_snapshot(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    value = json.loads(raw)
    if not isinstance(value, dict):
        raise PilotError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return {
        "path": path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "value": value,
    }


def file_snapshot(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    return {
        "path": path,
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def safe_relative_path(value: Any, label: str) -> Path:
    path = Path(str(value))
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise PilotError(f"unsafe {label} path in publication manifest: {value!r}")
    return path


def publication_input_snapshot() -> dict[str, Any]:
    """Return the exact public descriptor, projection and large-data closure."""
    pages_snapshot = json_mapping_snapshot(PAGES_MANIFEST_PATH)
    explore_snapshot = json_mapping_snapshot(EXPLORE_MANIFEST_PATH)
    pages = pages_snapshot["value"]
    explore = explore_snapshot["value"]
    candidates = []
    for entry in pages.get("files", []):
        if not isinstance(entry, dict):
            continue
        target = str(entry.get("target", ""))
        if target == "okf-explorer.json" or target.startswith("large/data/"):
            candidates.append(entry)
    for entry in explore.get("files", []):
        if (
            isinstance(entry, dict)
            and entry.get("target") == "explore/journey-projection.json"
        ):
            candidates.append(entry)
    entries = []
    seen_targets: set[str] = set()
    for entry in candidates:
        source_relative = safe_relative_path(entry.get("source"), "source")
        target_relative = safe_relative_path(entry.get("target"), "target")
        expected_sha256 = str(entry.get("sha256", ""))
        expected_bytes = entry.get("bytes")
        if (
            len(expected_sha256) != 64
            or any(character not in "0123456789abcdef" for character in expected_sha256)
            or not isinstance(expected_bytes, int)
            or expected_bytes < 0
        ):
            raise PilotError(f"invalid digest or byte count for {source_relative}")
        target = target_relative.as_posix()
        if target in seen_targets:
            raise PilotError(f"duplicate staged publication target: {target}")
        seen_targets.add(target)
        entries.append(
            {
                "source": ROOT / source_relative,
                "target": target_relative,
                "sha256": expected_sha256,
                "bytes": expected_bytes,
            }
        )
    required = {"okf-explorer.json", "explore/journey-projection.json"}
    if not required.issubset(seen_targets) or not any(
        target.startswith("large/data/") for target in seen_targets
    ):
        raise PilotError("publication manifests do not contain the required pilot inputs")
    entries = sorted(entries, key=lambda item: item["target"].as_posix())
    by_target = {entry["target"].as_posix(): entry for entry in entries}
    bundle = by_target["okf-explorer.json"]
    projection = by_target["explore/journey-projection.json"]
    data_manifest = by_target.get("large/data/manifest.json")
    if data_manifest is None:
        raise PilotError("publication closure has no large-data manifest")
    if explore.get("base_manifest", {}).get("sha256") != pages_snapshot["sha256"]:
        raise PilotError("Explore OKF manifest does not bind the base Pages manifest")
    if explore.get("existing_descriptor", {}).get("sha256") != bundle["sha256"]:
        raise PilotError("Explore OKF manifest does not bind the preserved descriptor")
    verify_file(bundle["source"], bundle["bytes"], bundle["sha256"])
    verify_file(projection["source"], projection["bytes"], projection["sha256"])
    projection_value = read_json_mapping(projection["source"])
    source_identity = projection_value.get("source_identity", {})
    for label, expected, observed in (
        (
            "bundle descriptor",
            bundle["sha256"],
            source_identity.get("bundle_descriptor", {}).get("sha256"),
        ),
        (
            "large-data manifest",
            data_manifest["sha256"],
            source_identity.get("data_manifest", {}).get("sha256"),
        ),
        (
            "candidate manifest",
            pages.get("candidate_manifest_sha256"),
            source_identity.get("candidate_manifest", {}).get("sha256"),
        ),
    ):
        if expected != observed:
            raise PilotError(f"journey projection does not bind the {label}")
    return {
        "entries": entries,
        "pages_manifest": pages_snapshot,
        "explore_manifest": explore_snapshot,
    }


def verify_file(path: Path, expected_bytes: int, expected_sha256: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise PilotError(f"pilot input must be a regular file: {path}")
    if path.stat().st_size != expected_bytes or sha256_path(path) != expected_sha256:
        raise PilotError(f"pilot input differs from its publication manifest: {path}")


def closure_digest(entries: list[dict[str, Any]]) -> str:
    digest = hashlib.sha256()
    for entry in entries:
        line = (
            f"{entry['sha256']}  {entry['bytes']}  "
            f"{entry['target'].as_posix()}\n"
        )
        digest.update(line.encode("utf-8"))
    return digest.hexdigest()


def question_set(selection: str) -> tuple[list[dict[str, Any]], list[Path]]:
    gold = read_mapping(GOLD_PATH)
    questions: dict[str, dict[str, Any]] = {}
    source_paths: dict[str, Path] = {}
    selected_suite_questions: list[dict[str, Any]] | None = None
    selected_suite_path: Path | None = None
    for relative in gold.get("question_sources", []):
        source_path = (ROOT / str(relative)).resolve()
        if ROOT.resolve() not in source_path.parents:
            raise PilotError(f"unsafe question source path: {relative!r}")
        suite = read_mapping(source_path)
        suite_questions = suite.get("questions", [])
        if not isinstance(suite_questions, list):
            raise PilotError(f"{source_path.relative_to(ROOT)} has no questions list")
        if selection != "gold" and str(suite.get("pack_id", "")).startswith(
            f"pack-{selection}-"
        ):
            if selected_suite_questions is not None:
                raise PilotError(f"more than one question suite matches pack {selection}")
            selected_suite_questions = suite_questions
            selected_suite_path = source_path
        for question in suite.get("questions", []):
            if isinstance(question, dict) and isinstance(question.get("id"), str):
                if question["id"] in questions:
                    raise PilotError(f"duplicate competency question ID: {question['id']}")
                questions[question["id"]] = question
                source_paths[question["id"]] = source_path
    result: list[dict[str, Any]] = []
    selected_paths: set[Path] = set()
    if selection != "gold":
        if selected_suite_questions is None or selected_suite_path is None:
            raise PilotError(f"no question suite matches pack {selection}")
        selected_paths.add(selected_suite_path)
        cases = selected_suite_questions
    else:
        cases = []
        for case in gold.get("cases", []):
            reference = case.get("question_ref") if isinstance(case, dict) else None
            question_id = reference.get("id") if isinstance(reference, dict) else None
            question = questions.get(str(question_id))
            if not question:
                raise PilotError(f"gold case references a missing question: {question_id!r}")
            cases.append(question)
            selected_paths.add(source_paths[str(question_id)])
    for question in cases:
        question_id = question.get("id") if isinstance(question, dict) else None
        query = question.get("query") if isinstance(question, dict) else None
        jurisdictions = question.get("jurisdictions") if isinstance(question, dict) else None
        if (
            not isinstance(question_id, str)
            or not isinstance(query, str)
            or not isinstance(jurisdictions, list)
            or not jurisdictions
            or any(not isinstance(value, str) or not value for value in jurisdictions)
        ):
            raise PilotError(f"malformed competency question: {question_id!r}")
        result.append(
            {
                "question_id": question_id,
                "question": query,
                "jurisdictions": jurisdictions,
            }
        )
    expected_count = 8 if selection == "gold" else 13
    if (
        len(result) != expected_count
        or len({item["question_id"] for item in result}) != expected_count
    ):
        raise PilotError(
            f"question set {selection!r} requires exactly {expected_count} distinct questions"
        )
    return result, sorted(selected_paths)


def effective_output_schema(
    template: dict[str, Any], answer_count: int, condition: str
) -> dict[str, Any]:
    schema = copy.deepcopy(template)
    answers = schema.get("properties", {}).get("answers")
    if not isinstance(answers, dict):
        raise PilotError("pilot output schema has no answers property")
    answers["minItems"] = answer_count
    answers["maxItems"] = answer_count
    if condition not in {"with_bundle", "without_bundle"}:
        raise PilotError(f"unsupported pilot condition: {condition!r}")
    if condition == "with_bundle":
        properties = (
            schema.get("$defs", {}).get("answer", {}).get("properties")
        )
        if not isinstance(properties, dict):
            raise PilotError("pilot output schema has no answer properties")
        properties["answer_mode"] = {
            "type": "string",
            "enum": ["navigation-only"],
        }
        properties["selected_family"]["type"] = "string"
        properties["journey"]["properties"]["episode_order"]["minItems"] = 2
        properties["journey"]["properties"]["first_step_id"]["type"] = "string"
        for field in (
            "jurisdictions",
            "source_urls",
            "assertion_ids",
            "assertion_provenance",
        ):
            properties[field]["minItems"] = 1
        properties["specialist_review"] = {
            "type": "string",
            "enum": ["accepted", "not_required", "required"]
        }
    return schema


def prompt_text(condition: str, questions: list[dict[str, Any]]) -> str:
    question_count = len(questions)
    common = f"""You are taking part in a controlled, provider-neutral evaluation of an Open Knowledge Format (OKF) citizen-journey corpus.

Return exactly one structured answer for each of the {question_count} questions below. Treat every answer as navigation and evidence handoff, never as a personalised eligibility, legal, medical, safeguarding or operational decision. Do not invent URLs, assertion IDs, provenance, jurisdiction, review status or cross-family sequence. `sequenced_family_ids` and `decision_claims` must always be empty. Related families are grouping only, never asserted next steps. Use British English.

The root object must contain exactly one key, `answers`. Every item in `answers` must contain all and only these keys: `question_id`, `answer_mode`, `answer_text`, `selected_family`, `journey`, `jurisdictions`, `source_urls`, `assertion_ids`, `assertion_provenance`, `specialist_review`, `corpus_review`, `related_family_ids`, `sequenced_family_ids`, `decision_claims` and `abstention`. Put `corpus_review` inside every answer, never at the root. Even when evidence is unavailable, include `journey` as `{{"episode_order": [], "first_step_id": null}}`; include every required array field as an empty array; set `selected_family` and `corpus_review` to null; and include `abstention` with both required keys. Do not omit a field because its value is empty or null. Before returning, verify that the answer count is {question_count} and that each listed `question_id` appears exactly once.

For a supported answer, `selected_family` is the exact service-family ID; put the ordinary episode before the exception episode; preserve the authored first ordinary step; use exactly one exact official source URL; and include exactly one exact relationship assertion and its matching provenance, with exactly one evidence URL and the same authority source, observation time and rights source. Keep `related_family_ids` empty. The declared jurisdiction context is governed question input supplied equally in both conditions: reproduce exactly that list for a supported answer, and do not broaden or narrow it from family-wide coverage. Include corpus review totals only when the supplied material supports them. Limit `answer_text` to 1,024 characters and `abstention.reason` to 256 characters. Preserve any material contrast stated in the question, name a sole declared jurisdiction, and state that the cited current official source must be checked before action.

Use these exact nested contracts; similar-looking source fields are not substitutes:
- `journey.episode_order` is exactly `["ordinary", "exception"]`. Those are the two episode `kind` values, not episode IDs such as `ordinary-source-linked-route`.
- `journey.first_step_id` is `families[].episodes[]` where `kind` is `ordinary`, then `steps[0].id`.
- `source_urls` contains one exact `families[].sources[].url` value.
- Select one exact assertion URL for the family, preferably a `families[].sources[].relationship_assertion`, and locate the row with that same `id` in `large/data/relationships-0.json`.
- `assertion_ids` contains that one URL. `assertion_provenance` contains exactly one object with exactly these five keys: `id`, `authority_source`, `evidence_sources`, `observed_at`, `rights_source`.
- Map them literally as `id` = relationship row `id`; `authority_source` = row `authority.source`; `evidence_sources` = an array containing one row `evidence[].url`; `observed_at` = row `observed_at`; and `rights_source` = row `rights.source`.
- All four provenance source values are HTTP(S) URLs. Never use an organisation name for `authority_source`, a rights-decision identifier for `rights_source`, or the alternative keys `assertion_id`, `evidence_url` or `observation_time`.

`abstention.decision_abstained` records whether the answer abstained from making the underlying substantive decision; it does not mean that the answer refused to provide navigation. Every answer must set `abstention.decision_abstained` to true. Explain the boundary in `abstention.reason`: the answer may route to evidence, but must not decide personalised eligibility, validity, liability, urgency, diagnosis, treatment, safeguarding, an operational outcome or any other substantive outcome. When the declared context contains one jurisdiction, name that jurisdiction in `answer_text` as well as recording it in `jurisdictions`. `corpus_review` is required by the response envelope: set it to null unless the supplied material explicitly supports all three totals.
"""
    if condition == "without_bundle":
        condition_text = """
Condition: WITHOUT BUNDLE. No OKF descriptor, projection, extracted context, URL or answer derived from them has been supplied. Do not inspect files or use tools, the web or external knowledge to reconstruct the corpus. You may answer from general knowledge only, but internal family and assertion identifiers must not be guessed. Honest abstention is expected when the requested structured evidence is unavailable: use `answer_mode: abstention`, null identifiers, empty arrays, `specialist_review: unknown`, and explain the evidence boundary.
"""
    else:
        condition_text = """
Condition: WITH BUNDLE. The exact Claude-tested public descriptor is available locally as `okf-explorer.json`. The exact governed consumer projection is `explore/journey-projection.json`; its referenced public corpus material is under `large/data/`. Inspect only these supplied local artefacts. Do not use the web, model memory for corpus facts, or any file outside this working directory. Cite only values present in the supplied material. Prefer a compact answer with one sufficient official URL and one sufficient governed assertion rather than copying every available row.

Every WITH BUNDLE answer must use `answer_mode: navigation-only`, an exact non-null `selected_family`, both authored journey episodes, a non-null first step and non-empty jurisdiction, source, assertion and provenance fields. Do not use `answer_mode: abstention` when bundle evidence is supplied. Record any substantive decision boundary with `abstention.decision_abstained` and its reason while still returning the supported navigation route.
"""
    rendered_questions = "\n".join(
        f"{index}. {item['question_id']} "
        f"[declared jurisdictions: {', '.join(item['jurisdictions'])}]: "
        f"{item['question']}"
        for index, item in enumerate(questions, start=1)
    )
    return (
        common
        + condition_text
        + "\nQuestions:\n"
        + rendered_questions
        + "\n\nReturn only the JSON object required by the supplied output schema, with no surrounding prose or Markdown fence."
    )


def prepare_workspace(workspace: Path, condition: str) -> dict[str, Any]:
    """Create and bind an immutable, manifest-verified input snapshot."""
    publication = publication_input_snapshot()
    entries = publication["entries"]
    by_target = {entry["target"].as_posix(): entry for entry in entries}
    bundle = by_target["okf-explorer.json"]
    projection = by_target["explore/journey-projection.json"]
    for entry in (bundle, projection):
        verify_file(entry["source"], entry["bytes"], entry["sha256"])

    staged_entries: list[dict[str, Any]] = []
    if condition == "with_bundle":
        for entry in entries:
            source = entry["source"]
            verify_file(source, entry["bytes"], entry["sha256"])
            destination = workspace / entry["target"]
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, destination)
            verify_file(destination, entry["bytes"], entry["sha256"])
            destination.chmod(0o444)
            staged_entries.append(entry)

    return {
        "bundle_sha256": bundle["sha256"],
        "journey_projection_sha256": projection["sha256"],
        "publication_closure_sha256": closure_digest(entries),
        "publication_file_count": len(entries),
        "publication_bytes": sum(entry["bytes"] for entry in entries),
        "publication_closure_supplied": condition == "with_bundle",
        "pages_manifest_sha256": publication["pages_manifest"]["sha256"],
        "explore_manifest_sha256": publication["explore_manifest"]["sha256"],
        "manifest_snapshots": [
            publication["pages_manifest"],
            publication["explore_manifest"],
        ],
        "staged_file_count": len(staged_entries),
        "staged_bytes": sum(entry["bytes"] for entry in staged_entries),
        "entries": staged_entries,
        "publication_entries": entries,
        "binding_entries": [bundle, projection],
    }


def verify_staged_workspace(workspace: Path, snapshot: dict[str, Any]) -> None:
    for manifest in snapshot["manifest_snapshots"]:
        verify_file(manifest["path"], manifest["bytes"], manifest["sha256"])
    for entry in snapshot["publication_entries"]:
        verify_file(entry["source"], entry["bytes"], entry["sha256"])
    for entry in snapshot["entries"]:
        verify_file(workspace / entry["target"], entry["bytes"], entry["sha256"])
    if (
        closure_digest(snapshot["publication_entries"])
        != snapshot["publication_closure_sha256"]
    ):
        raise PilotError("staged publication closure digest changed during the model call")


def verify_workspace_isolation(workspace: Path) -> None:
    resolved = workspace.resolve()
    if resolved == ROOT.resolve() or ROOT.resolve() in resolved.parents:
        raise PilotError("pilot workspace must be outside the repository")
    for directory in (resolved, *resolved.parents):
        for marker in ("AGENTS.md", ".codex", ".git"):
            if (directory / marker).exists():
                raise PilotError(
                    f"pilot workspace inherits unexpected project context: {directory / marker}"
                )


def command_version(executable: str, workspace: Path) -> str:
    """Resolve a CLI version through the same bounded process runner as inference."""
    process = run_process([executable, "--version"], workspace)
    if process.returncode != 0:
        raise process_failure("model CLI version check", process)
    return (process.stdout or process.stderr).strip()[:256]


def process_group_exists(process_group: int) -> bool:
    try:
        os.killpg(process_group, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    return True


def terminate_process_group(
    process: subprocess.Popen[bytes],
    process_group: int,
) -> None:
    """Bound termination of the model CLI and every process in its session."""
    try:
        os.killpg(process_group, signal.SIGTERM)
    except ProcessLookupError:
        pass
    deadline = time.monotonic() + PROCESS_TERMINATION_GRACE_SECONDS
    while process_group_exists(process_group) and time.monotonic() < deadline:
        process.poll()
        time.sleep(0.01)
    if process_group_exists(process_group):
        try:
            os.killpg(process_group, signal.SIGKILL)
        except ProcessLookupError:
            pass
    try:
        process.wait(timeout=PROCESS_TERMINATION_GRACE_SECONDS)
    except subprocess.TimeoutExpired:
        try:
            process.kill()
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=PROCESS_TERMINATION_GRACE_SECONDS)
        except subprocess.TimeoutExpired:
            pass


def decoded_capture(value: bytearray, label: str) -> str:
    try:
        return bytes(value).decode("utf-8")
    except UnicodeDecodeError as error:
        raise PilotError(f"model {label} is not valid UTF-8") from error


def run_process(
    command: list[str],
    workspace: Path,
    *,
    extra_environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = {
        key: os.environ[key]
        for key in MODEL_ENVIRONMENT_KEYS
        if key in os.environ
    }
    environment.update(
        {
            "NO_COLOR": "1",
            "TERM": "dumb",
            "TMPDIR": str(workspace / "_tmp"),
        }
    )
    if extra_environment:
        environment.update(extra_environment)
    process = subprocess.Popen(
        command,
        cwd=workspace,
        env=environment,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    process_group = process.pid
    selector = selectors.DefaultSelector()
    captured = {"stdout": bytearray(), "stderr": bytearray()}
    streams = {"stdout": process.stdout, "stderr": process.stderr}
    parent_exit_cleaned = False
    try:
        for label, stream in streams.items():
            if stream is None:
                raise PilotError(f"model {label} pipe was not created")
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, label)
        deadline = time.monotonic() + TIMEOUT_SECONDS
        while selector.get_map():
            remaining_time = deadline - time.monotonic()
            if remaining_time <= 0:
                raise subprocess.TimeoutExpired(
                    command,
                    TIMEOUT_SECONDS,
                    output=bytes(captured["stdout"]),
                    stderr=bytes(captured["stderr"]),
                )
            try:
                events = selector.select(timeout=min(0.1, remaining_time))
            except InterruptedError:
                continue
            for key, _mask in events:
                label = str(key.data)
                remaining_bytes = MAX_CAPTURE_BYTES - len(captured[label])
                try:
                    chunk = os.read(
                        key.fd,
                        min(CAPTURE_READ_BYTES, remaining_bytes + 1),
                    )
                except BlockingIOError:
                    continue
                except OSError as error:
                    raise PilotError(f"cannot read model {label}: {error}") from error
                if not chunk:
                    selector.unregister(key.fileobj)
                    key.fileobj.close()
                    continue
                if len(chunk) > remaining_bytes:
                    raise PilotError(
                        f"model {label} exceeds {MAX_CAPTURE_BYTES} bytes"
                    )
                captured[label].extend(chunk)
            if process.poll() is not None and not parent_exit_cleaned:
                terminate_process_group(process, process_group)
                parent_exit_cleaned = True
        remaining_time = deadline - time.monotonic()
        if remaining_time <= 0:
            raise subprocess.TimeoutExpired(
                command,
                TIMEOUT_SECONDS,
                output=bytes(captured["stdout"]),
                stderr=bytes(captured["stderr"]),
            )
        try:
            return_code = process.wait(timeout=remaining_time)
        except subprocess.TimeoutExpired as error:
            raise subprocess.TimeoutExpired(
                command,
                TIMEOUT_SECONDS,
                output=bytes(captured["stdout"]),
                stderr=bytes(captured["stderr"]),
            ) from error
        stdout = decoded_capture(captured["stdout"], "stdout")
        stderr = decoded_capture(captured["stderr"], "stderr")
        return subprocess.CompletedProcess(command, return_code, stdout, stderr)
    finally:
        terminate_process_group(process, process_group)
        for key in list(selector.get_map().values()):
            try:
                selector.unregister(key.fileobj)
            except (KeyError, ValueError):
                pass
            key.fileobj.close()
        selector.close()


def process_failure(
    label: str,
    process: subprocess.CompletedProcess[str],
    *,
    secrets: tuple[str, ...] = (),
) -> PilotError:
    details = "\n".join(
        value[-4000:]
        for value in (process.stderr.strip(), process.stdout.strip())
        if value
    )
    for secret in secrets:
        if secret:
            details = details.replace(secret, "[REDACTED]")
    return PilotError(
        f"{label} exited {process.returncode}"
        + (f":\n{details}" if details else " without diagnostics")
    )


def run_claude(
    workspace: Path,
    condition: str,
    prompt: str,
    schema: dict[str, Any],
    sandbox_path: Path,
    oauth_token: str,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    launcher_value = shutil.which("claude")
    if not launcher_value:
        raise PilotError("Claude Code is not installed")
    launcher = Path(launcher_value)
    binary = launcher.resolve()
    if not oauth_token or oauth_token.isspace():
        raise PilotError(
            "Claude comparison requires a scoped CLAUDE_CODE_OAUTH_TOKEN; "
            "the user's broader Claude configuration remains unavailable to "
            "the evaluated process"
        )
    home_root = current_home_root()
    tools = "" if condition == "without_bundle" else "Read,Glob,Grep"
    command = [
        "/usr/bin/sandbox-exec",
        "-D",
        f"HOME_ROOT={home_root}",
        "-D",
        f"WORKSPACE={workspace}",
        "-D",
        f"CLAUDE_LAUNCHER={launcher}",
        "-D",
        f"CLAUDE_BINARY={binary}",
        "-f",
        str(sandbox_path),
        str(launcher),
        "--print",
        "--safe-mode",
        "--no-chrome",
        "--disable-slash-commands",
        "--no-session-persistence",
        "--strict-mcp-config",
        "--mcp-config",
        '{"mcpServers":{}}',
        "--permission-mode",
        "dontAsk",
        "--tools",
        tools,
        "--model",
        "opus",
        "--effort",
        "high",
        "--max-budget-usd",
        "15",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(schema, ensure_ascii=False, separators=(",", ":")),
        prompt,
    ]
    process = run_process(
        command,
        workspace,
        extra_environment={
            "CLAUDE_CODE_OAUTH_TOKEN": oauth_token,
            "CLAUDE_CONFIG_DIR": str(workspace / "_control" / "claude-config"),
            "CLAUDE_CODE_TMPDIR": str(workspace / "_tmp"),
        },
    )
    if oauth_token in process.stdout or oauth_token in process.stderr:
        raise PilotError("Claude output contained the scoped authentication token")
    if process.returncode != 0:
        raise process_failure("Claude", process, secrets=(oauth_token,))
    try:
        envelope = json.loads(process.stdout)
    except json.JSONDecodeError as error:
        raise PilotError(f"Claude returned invalid JSON: {error}") from error
    if not isinstance(envelope, dict):
        raise PilotError(
            f"Claude returned a {type(envelope).__name__} envelope instead of an object"
        )
    if (
        envelope.get("type") != "result"
        or envelope.get("subtype") != "success"
        or envelope.get("is_error") is not False
    ):
        raise PilotError(
            "Claude returned a non-success result envelope "
            f"(type={envelope.get('type')!r}, subtype={envelope.get('subtype')!r}, "
            f"is_error={envelope.get('is_error')!r})"
        )
    payload = envelope.get("structured_output")
    structured_output_source = "cli-structured-output"
    if not isinstance(payload, dict):
        result = envelope.get("result")
        payload = None
        if isinstance(result, str):
            payload, structured_output_source = decode_claude_result(result)
    if not isinstance(payload, dict):
        result = envelope.get("result")
        result_length = len(result) if isinstance(result, str) else 0
        envelope_keys = ",".join(sorted(map(str, envelope))[:32])
        raise PilotError(
            "Claude returned no structured output "
            f"(type={envelope.get('type')!r}, subtype={envelope.get('subtype')!r}, "
            f"is_error={envelope.get('is_error')!r}, result_type={type(result).__name__}, "
            f"result_chars={result_length}, stop_reason={envelope.get('stop_reason')!r}, "
            f"terminal_reason={envelope.get('terminal_reason')!r}, "
            f"envelope_keys={envelope_keys})"
        )
    model_usage = envelope.get("modelUsage")
    resolved = sorted(model_usage) if isinstance(model_usage, dict) else []
    native_structured_output = structured_output_source == "cli-structured-output"
    wrapper_recovered = structured_output_source.startswith("single-embedded-")
    metadata = {
        "provider": "Anthropic",
        "requested_model": "opus",
        "resolved_models": resolved,
        "model_version": resolved[0] if len(resolved) == 1 else "provider-not-reported",
        "effort": "high",
        "usage": envelope.get("usage"),
        "model_usage": model_usage,
        "total_cost_usd": envelope.get("total_cost_usd"),
        "duration_ms": envelope.get("duration_ms"),
        "host_data_sandbox_sha256": sha256_path(sandbox_path),
        "authentication": "scoped-oauth-token",
        "structured_output_source": structured_output_source,
        "native_structured_output_conformant": native_structured_output,
        "transport_conformance": (
            "native-structured-output"
            if native_structured_output
            else (
                "wrapper-nonconformant-recovered"
                if wrapper_recovered
                else "result-json-recovered"
            )
        ),
        "stop_reason": envelope.get("stop_reason"),
        "terminal_reason": envelope.get("terminal_reason"),
    }
    model_name = resolved[0] if len(resolved) == 1 else "claude-opus"
    return payload, metadata, process.stdout, process.stderr


def scoped_claude_token() -> str:
    token = os.environ.get("CLAUDE_CODE_OAUTH_TOKEN", "")
    if token and not token.isspace():
        return token
    account = os.environ.get("USER", "")
    if not account:
        return ""
    process = subprocess.run(
        [
            "/usr/bin/security",
            "find-generic-password",
            "-a",
            account,
            "-s",
            CLAUDE_TOKEN_KEYCHAIN_SERVICE,
            "-w",
        ],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return process.stdout.strip() if process.returncode == 0 else ""


def run_codex(
    workspace: Path,
    condition: str,
    prompt: str,
    schema_path: Path,
    final_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str, str]:
    permission_filesystem = (
        '{":root"="deny",":minimal"="read",'
        '":workspace_roots"={"."="read"},'
        '":tmpdir"="deny",":slash_tmp"="deny"}'
    )
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--strict-config",
        "--skip-git-repo-check",
        "--cd",
        str(workspace),
        "--model",
        "gpt-5.6-sol",
        "--config",
        'model_reasoning_effort="high"',
        "--config",
        'approval_policy="never"',
        "--config",
        'default_permissions="pilot-read"',
        "--config",
        f"permissions.pilot-read.filesystem={permission_filesystem}",
        "--config",
        "permissions.pilot-read.network.enabled=false",
        "--config",
        'shell_environment_policy.inherit="core"',
        "--config",
        'web_search="disabled"',
        "--config",
        "project_doc_max_bytes=0",
        "--config",
        "project_root_markers=[]",
        "--config",
        "mcp_servers={}",
        "--disable",
        "standalone_web_search",
        "--disable",
        "skill_search",
        "--disable",
        "plugins",
        "--disable",
        "apps",
        "--disable",
        "remote_plugin",
        "--disable",
        "tool_suggest",
        "--disable",
        "browser_use",
        "--disable",
        "browser_use_external",
        "--disable",
        "computer_use",
        "--disable",
        "image_generation",
        "--disable",
        "in_app_browser",
        "--disable",
        "multi_agent",
        "--disable",
        "workspace_dependencies",
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(final_path),
        "--json",
    ]
    if condition == "without_bundle":
        command.extend(["--disable", "shell_tool"])
    command.append(prompt)
    process = run_process(command, workspace)
    if process.returncode != 0:
        raise process_failure("Codex", process)
    try:
        payload = json.loads(final_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise PilotError(f"Codex returned invalid structured output: {error}") from error
    events = []
    for line in process.stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(event, dict):
            events.append(event)
    completion = next(
        (event for event in reversed(events) if event.get("type") == "turn.completed"),
        {},
    )
    tool_items = [
        event
        for event in events
        if event.get("type") == "item.completed"
        and isinstance(event.get("item"), dict)
        and event["item"].get("type")
        not in {"agent_message", "reasoning", "error"}
    ]
    if condition == "without_bundle" and tool_items:
        types = sorted({str(event["item"].get("type")) for event in tool_items})
        raise PilotError(
            "Codex baseline attempted a disabled tool: " + ", ".join(types)
        )
    commands = [
        event for event in tool_items if event["item"].get("type") == "command_execution"
    ]
    metadata = {
        "provider": "OpenAI",
        "requested_model": "gpt-5.6-sol",
        "resolved_models": ["gpt-5.6-sol"],
        "model_version": "provider-not-reported",
        "effort": "high",
        "usage": completion.get("usage"),
        "tool_execution_count": len(tool_items),
        "tool_execution_types": [event["item"].get("type") for event in tool_items],
        "command_execution_count": len(commands),
        "command_executions": [event["item"].get("command") for event in commands],
        "permission_profile": "pilot-read",
        "structured_output_source": "cli-output-schema-file",
        "native_structured_output_conformant": True,
        "transport_conformance": "native-structured-output",
    }
    return payload, metadata, process.stdout, process.stderr


def validate_payload(
    payload: dict[str, Any], schema: dict[str, Any], question_ids: set[str]
) -> list[dict[str, Any]]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(payload), key=lambda item: list(item.absolute_path))
    if errors:
        messages = [
            f"{'.'.join(map(str, error.absolute_path)) or '<root>'}: {error.message}"
            for error in errors[:20]
        ]
        raise PilotError("pilot output failed its schema:\n- " + "\n- ".join(messages))
    answers = payload.get("answers")
    if not isinstance(answers, list):
        raise PilotError("pilot output has no answers array")
    observed = [str(answer.get("question_id")) for answer in answers]
    if len(observed) != len(set(observed)) or set(observed) != question_ids:
        raise PilotError("pilot output question IDs are missing, duplicated or unexpected")
    return answers


def normalise_answers(
    fragments: list[dict[str, Any]],
    *,
    provider: str,
    model_name: str,
    model_version: str,
    condition: str,
    pilot_id: str,
    observed_at: str,
    input_snapshot: dict[str, Any],
) -> list[dict[str, Any]]:
    supplied = condition == "with_bundle"
    answers = []
    for fragment in fragments:
        fragment = dict(fragment)
        if fragment.get("corpus_review") is None:
            fragment.pop("corpus_review")
        question_id = str(fragment["question_id"])
        answers.append(
            {
                "schema": "okf-ai-consumer-answer.v1",
                "run_id": f"{pilot_id}-{provider.casefold()}-{condition}",
                "response_id": f"{pilot_id}-{provider.casefold()}-{condition}-{question_id}",
                "observed_at": observed_at,
                "model": {
                    "provider": provider,
                    "name": model_name,
                    "version": model_version,
                },
                "condition": condition,
                "input_binding": {
                    "bundle_sha256": input_snapshot["bundle_sha256"],
                    "journey_projection_sha256": input_snapshot[
                        "journey_projection_sha256"
                    ],
                    "publication_closure_sha256": input_snapshot[
                        "publication_closure_sha256"
                    ],
                    "pages_manifest_sha256": input_snapshot[
                        "pages_manifest_sha256"
                    ],
                    "explore_manifest_sha256": input_snapshot[
                        "explore_manifest_sha256"
                    ],
                    "bundle_supplied": supplied,
                    "journey_projection_supplied": supplied,
                    "publication_closure_supplied": supplied,
                },
                **fragment,
            }
        )
    return answers


def validate_answers(
    answers: list[dict[str, Any]], schema: dict[str, Any]
) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = []
    for position, answer in enumerate(answers):
        for error in validator.iter_errors(answer):
            location = ".".join(map(str, error.absolute_path)) or "<root>"
            errors.append(f"answer {position + 1} {location}: {error.message}")
    if errors:
        raise PilotError("normalised answers failed the governed schema:\n- " + "\n- ".join(errors[:20]))


def safe_pilot_id(value: str) -> str:
    allowed = "abcdefghijklmnopqrstuvwxyz0123456789-"
    if not value or any(character not in allowed for character in value):
        raise PilotError("pilot ID must contain only lowercase letters, digits and hyphens")
    return value


def ensure_private_directory(path: Path) -> None:
    """Create or tighten a runner-owned directory without following a symlink."""
    if path.is_symlink():
        raise PilotError(f"refusing to use symlinked pilot output directory: {path}")
    path.mkdir(mode=0o700, parents=True, exist_ok=True)
    if not path.is_dir():
        raise PilotError(f"pilot output path is not a directory: {path}")
    path.chmod(0o700)


def pilot_cell_names(stem: str) -> dict[str, str]:
    return {
        "answers": f"{stem}.json",
        "metadata": f"{stem}.metadata.json",
        "raw_stdout": f"{stem}.raw-stdout.txt",
        "raw_stderr": f"{stem}.raw-stderr.txt",
        "prompt": f"{stem}.prompt.txt",
    }


def ensure_pilot_cell_available(output_dir: Path, stem: str) -> Path:
    """Refuse both the atomic cell path and the former flat output layout."""
    cell_dir = output_dir / stem
    conflicts = [cell_dir]
    conflicts.extend(output_dir / name for name in pilot_cell_names(stem).values())
    for path in conflicts:
        if path.exists() or path.is_symlink():
            raise PilotError(f"refusing to replace existing pilot output: {path}")
    return cell_dir


def write_private_file(path: Path, content: bytes) -> None:
    """Create one new private file and flush its content before promotion."""
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)


def atomic_rename_no_replace(source: Path, destination: Path) -> None:
    """Atomically promote a directory and fail if the destination now exists."""
    library = ctypes.CDLL(None, use_errno=True)
    try:
        renamex_np = library.renamex_np
    except AttributeError as error:
        raise PilotError(
            "atomic no-replace pilot output promotion is unavailable"
        ) from error
    renamex_np.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
    renamex_np.restype = ctypes.c_int
    if renamex_np(os.fsencode(source), os.fsencode(destination), RENAME_EXCL) == 0:
        return
    error_number = ctypes.get_errno()
    if error_number in (errno.EEXIST, errno.ENOTEMPTY):
        raise PilotError(
            f"refusing to replace concurrently created pilot output: {destination}"
        )
    raise OSError(error_number, os.strerror(error_number), str(destination))


def fsync_directory(path: Path) -> None:
    descriptor = os.open(path, os.O_RDONLY)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def commit_pilot_cell(
    output_dir: Path,
    stem: str,
    artefacts: dict[str, bytes],
) -> dict[str, Path]:
    """Atomically expose one complete five-artefact cell without replacement."""
    names = pilot_cell_names(stem)
    if set(artefacts) != set(names):
        raise PilotError("pilot cell must contain exactly five governed artefacts")
    ensure_private_directory(output_dir)
    cell_dir = ensure_pilot_cell_available(output_dir, stem)
    staging_dir = Path(
        tempfile.mkdtemp(prefix=f".{stem}-", suffix=".tmp", dir=output_dir)
    )
    staging_dir.chmod(0o700)
    promoted = False
    try:
        for key, name in names.items():
            write_private_file(staging_dir / name, artefacts[key])
        fsync_directory(staging_dir)
        atomic_rename_no_replace(staging_dir, cell_dir)
        promoted = True
        fsync_directory(output_dir)
        return {key: cell_dir / name for key, name in names.items()}
    finally:
        if not promoted and staging_dir.exists():
            shutil.rmtree(staging_dir)


def run_selected_model(
    model: str,
    workspace: Path,
    condition: str,
    prompt: str,
    schema: dict[str, Any],
    staged_schema_path: Path,
    staged_claude_sandbox_path: Path,
) -> tuple[dict[str, Any], dict[str, Any], str, str, str, str]:
    """Resolve and version the CLI before allowing a paid model invocation."""
    executable = shutil.which(model)
    if not executable:
        display_name = "Claude Code" if model == "claude" else "Codex CLI"
        raise PilotError(f"{display_name} is not installed")
    cli_version = command_version(executable, workspace)
    if model == "claude":
        oauth_token = scoped_claude_token()
        if not oauth_token:
            raise PilotError(
                "Claude Code has no scoped automation token; create one with "
                "`claude setup-token`, then supply it through "
                "CLAUDE_CODE_OAUTH_TOKEN or the dedicated macOS Keychain item"
            )
        payload, metadata, raw_stdout, raw_stderr = run_claude(
            workspace,
            condition,
            prompt,
            schema,
            staged_claude_sandbox_path,
            oauth_token,
        )
        model_name = "claude-opus"
    else:
        final_path = workspace / "final.json"
        payload, metadata, raw_stdout, raw_stderr = run_codex(
            workspace,
            condition,
            prompt,
            staged_schema_path,
            final_path,
        )
        model_name = "gpt-5.6-sol"
    return (
        payload,
        metadata,
        raw_stdout,
        raw_stderr,
        cli_version,
        model_name,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", choices=("claude", "codex"), required=True)
    parser.add_argument(
        "--condition", choices=("without_bundle", "with_bundle"), required=True
    )
    parser.add_argument(
        "--pack",
        choices=("gold", "1", "2", "3", "4", "5", "6", "7", "8"),
        default="gold",
        help="run the eight-case gold preflight or one governed 13-question pack",
    )
    parser.add_argument("--pilot-id", default="pilot-20260813-01")
    args = parser.parse_args(argv)
    try:
        pilot_id = safe_pilot_id(args.pilot_id)
        questions, question_source_paths = question_set(args.pack)
        question_ids = {item["question_id"] for item in questions}
        control_snapshots = {
            "runner": file_snapshot(RUNNER_PATH),
            "gold_pack": file_snapshot(GOLD_PATH),
            "pilot_output_schema_template": file_snapshot(PILOT_SCHEMA_PATH),
            "answer_schema": file_snapshot(ANSWER_SCHEMA_PATH),
            "claude_sandbox": file_snapshot(CLAUDE_SANDBOX_PATH),
        }
        question_source_snapshots = [
            file_snapshot(path) for path in question_source_paths
        ]
        schema_template = json.loads(PILOT_SCHEMA_PATH.read_text(encoding="utf-8"))
        schema = effective_output_schema(
            schema_template, len(questions), args.condition
        )
        effective_schema_bytes = json_text(schema).encode("utf-8")
        effective_schema_sha256 = hashlib.sha256(effective_schema_bytes).hexdigest()
        answer_schema = json.loads(ANSWER_SCHEMA_PATH.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator.check_schema(answer_schema)
        prompt = prompt_text(args.condition, questions)
        ensure_private_directory(RUNS_ROOT)
        output_dir = RUNS_ROOT / pilot_id
        ensure_private_directory(output_dir)
        question_set_id = "gold" if args.pack == "gold" else f"pack-{args.pack}"
        stem = f"{args.model}-{args.condition}-{question_set_id}"
        ensure_pilot_cell_available(output_dir, stem)
        observed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )
        with tempfile.TemporaryDirectory(
            prefix="okf-ai-consumer-pilot-", dir=ISOLATED_TEMP_ROOT
        ) as temporary:
            workspace = Path(temporary)
            verify_workspace_isolation(workspace)
            (workspace / "_control").mkdir()
            (workspace / "_tmp").mkdir()
            input_snapshot = prepare_workspace(workspace, args.condition)
            staged_schema_path = workspace / "_control" / "pilot-output.schema.json"
            staged_schema_path.write_bytes(effective_schema_bytes)
            verify_file(
                staged_schema_path,
                len(effective_schema_bytes),
                effective_schema_sha256,
            )
            staged_schema_path.chmod(0o444)
            staged_claude_sandbox_path = workspace / "_control" / "claude-pilot.sb"
            shutil.copyfile(CLAUDE_SANDBOX_PATH, staged_claude_sandbox_path)
            verify_file(
                staged_claude_sandbox_path,
                control_snapshots["claude_sandbox"]["bytes"],
                control_snapshots["claude_sandbox"]["sha256"],
            )
            staged_claude_sandbox_path.chmod(0o444)
            (
                payload,
                metadata,
                raw_stdout,
                raw_stderr,
                cli_version,
                model_name,
            ) = run_selected_model(
                args.model,
                workspace,
                args.condition,
                prompt,
                schema,
                staged_schema_path,
                staged_claude_sandbox_path,
            )
            verify_staged_workspace(workspace, input_snapshot)
            for snapshot in (*control_snapshots.values(), *question_source_snapshots):
                verify_file(snapshot["path"], snapshot["bytes"], snapshot["sha256"])
            verify_file(
                staged_schema_path,
                len(effective_schema_bytes),
                effective_schema_sha256,
            )
            verify_file(
                staged_claude_sandbox_path,
                control_snapshots["claude_sandbox"]["bytes"],
                control_snapshots["claude_sandbox"]["sha256"],
            )
        fragments = validate_payload(payload, schema, question_ids)
        answers = normalise_answers(
            fragments,
            provider=metadata["provider"],
            model_name=model_name,
            model_version=metadata["model_version"],
            condition=args.condition,
            pilot_id=pilot_id,
            observed_at=observed_at,
            input_snapshot=input_snapshot,
        )
        validate_answers(answers, answer_schema)
        metadata.update(
            {
                "schema": "okf-ai-consumer-pilot-cell.v1",
                "pilot_id": pilot_id,
                "question_set": question_set_id,
                "condition": args.condition,
                "observed_at": observed_at,
                "cli_version": cli_version,
                "questions": [item["question_id"] for item in questions],
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "runner_sha256": control_snapshots["runner"]["sha256"],
                "gold_pack_sha256": control_snapshots["gold_pack"]["sha256"],
                "question_source_bindings": [
                    {
                        "path": str(snapshot["path"].relative_to(ROOT)),
                        "bytes": snapshot["bytes"],
                        "sha256": snapshot["sha256"],
                    }
                    for snapshot in question_source_snapshots
                ],
                "pilot_output_schema_template_sha256": control_snapshots[
                    "pilot_output_schema_template"
                ]["sha256"],
                "pilot_output_schema_sha256": effective_schema_sha256,
                "answer_schema_sha256": control_snapshots["answer_schema"]["sha256"],
                "bundle_sha256": input_snapshot["bundle_sha256"],
                "journey_projection_sha256": input_snapshot[
                    "journey_projection_sha256"
                ],
                "publication_closure_sha256": input_snapshot[
                    "publication_closure_sha256"
                ],
                "publication_file_count": input_snapshot["publication_file_count"],
                "publication_bytes": input_snapshot["publication_bytes"],
                "publication_closure_supplied": input_snapshot[
                    "publication_closure_supplied"
                ],
                "staged_file_count": input_snapshot["staged_file_count"],
                "staged_bytes": input_snapshot["staged_bytes"],
                "pages_manifest_sha256": input_snapshot["pages_manifest_sha256"],
                "explore_manifest_sha256": input_snapshot[
                    "explore_manifest_sha256"
                ],
                "network_tools_enabled": False,
                "manual_review": "pending",
                "raw_stdout_sha256": hashlib.sha256(
                    raw_stdout.encode("utf-8")
                ).hexdigest(),
                "raw_stderr_sha256": hashlib.sha256(
                    raw_stderr.encode("utf-8")
                ).hexdigest(),
            }
        )
        cell_paths = commit_pilot_cell(
            output_dir,
            stem,
            {
                "answers": json_text(answers).encode("utf-8"),
                "metadata": json_text(metadata).encode("utf-8"),
                "raw_stdout": raw_stdout.encode("utf-8"),
                "raw_stderr": raw_stderr.encode("utf-8"),
                "prompt": (prompt + "\n").encode("utf-8"),
            },
        )
        output_path = cell_paths["answers"]
        print(
            f"captured {len(answers)} {args.condition} {question_set_id} answers "
            f"from {model_name}; "
            f"manual review pending; output {output_path.relative_to(ROOT)}"
        )
        return 0
    except (OSError, PilotError, subprocess.SubprocessError, json.JSONDecodeError) as error:
        print(f"AI consumer pilot failed: {error}", file=os.sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
