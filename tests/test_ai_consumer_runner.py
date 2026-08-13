from __future__ import annotations

import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import time
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "scripts" / "run_ai_consumer_pilot.py"
SPEC = importlib.util.spec_from_file_location("ai_consumer_runner", RUNNER_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class AiConsumerRunnerTests(unittest.TestCase):
    def test_cell_timeout_allows_the_complete_thirteen_question_pack(self) -> None:
        self.assertEqual(40 * 60, runner.TIMEOUT_SECONDS)

    def claude_call(
        self,
        condition: str,
        completed: runner.subprocess.CompletedProcess[str] | None = None,
    ) -> tuple[mock.Mock, Path]:
        workspace = Path("/private/tmp/isolated-fixture")
        if completed is None:
            completed = runner.subprocess.CompletedProcess(
                [],
                0,
                json.dumps(
                    {
                        "type": "result",
                        "subtype": "success",
                        "is_error": False,
                        "structured_output": {"answers": []},
                        "modelUsage": {"claude-opus-fixture": {}},
                    }
                ),
                "",
            )
        with (
            mock.patch.object(runner.shutil, "which", return_value="/usr/bin/claude"),
            mock.patch.object(Path, "resolve", return_value=Path("/usr/bin/claude")),
            mock.patch.object(
                runner, "current_home_root", return_value=Path("/Users/fixture")
            ),
            mock.patch.object(runner, "sha256_path", return_value="0" * 64),
            mock.patch.object(
                runner, "run_process", return_value=completed
            ) as called,
        ):
            runner.run_claude(
                workspace,
                condition,
                "fixture prompt",
                {"type": "object"},
                workspace / "_control" / "claude-pilot.sb",
                "scoped-fixture-token",
            )
        return called, workspace

    def test_gold_and_pack_question_sets_are_complete_and_distinct(self) -> None:
        gold, gold_sources = runner.question_set("gold")
        self.assertEqual(len(gold), 8)
        self.assertEqual(len({item["question_id"] for item in gold}), 8)
        self.assertEqual(
            {path.name for path in gold_sources},
            {
                "pack-4-home-place-transport.v1.yaml",
                "pack-5-enforcement-consumer-justice.v1.yaml",
                "pack-6-family-health-care.v1.yaml",
                "pack-8-mobility-later-life-death.v1.yaml",
            },
        )
        for pack in map(str, range(1, 9)):
            questions, sources = runner.question_set(pack)
            self.assertEqual(len(questions), 13)
            self.assertEqual(len({item["question_id"] for item in questions}), 13)
            self.assertEqual(len(sources), 1)

    def test_prompt_supplies_governed_jurisdiction_context_equally(self) -> None:
        questions, _ = runner.question_set("6")
        without = runner.prompt_text("without_bundle", questions)
        with_bundle = runner.prompt_text("with_bundle", questions)
        expected = (
            "pack6-dentist [declared jurisdictions: England]: "
            "I cannot find an NHS dentist taking patients"
        )
        self.assertIn("each of the 13 questions", without)
        self.assertIn(expected, without)
        self.assertIn(expected, with_bundle)
        self.assertIn("reproduce exactly that list", with_bundle)
        self.assertIn(
            "Every WITH BUNDLE answer must use `answer_mode: navigation-only`",
            with_bundle,
        )
        self.assertIn(
            "Do not use `answer_mode: abstention` when bundle evidence is supplied",
            with_bundle,
        )
        self.assertIn(
            "abstained from making the underlying substantive decision",
            with_bundle,
        )
        for prompt in (without, with_bundle):
            self.assertIn("The root object must contain exactly one key", prompt)
            self.assertIn("Put `corpus_review` inside every answer", prompt)
            self.assertIn("Do not omit a field because its value is empty", prompt)
            self.assertIn("Limit `answer_text` to 1,024 characters", prompt)
            self.assertIn("no surrounding prose or Markdown fence", prompt)
            self.assertIn(
                "Every answer must set `abstention.decision_abstained` to true",
                prompt,
            )
            self.assertNotIn("Use false", prompt)
        self.assertIn("use exactly one exact official source URL", with_bundle)
        self.assertIn("Keep `related_family_ids` empty", with_bundle)
        self.assertIn(
            '`journey.episode_order` is exactly `["ordinary", "exception"]`',
            with_bundle,
        )
        self.assertIn(
            "`authority_source` = row `authority.source`", with_bundle
        )
        self.assertIn(
            "alternative keys `assertion_id`, `evidence_url` or `observation_time`",
            with_bundle,
        )

    def test_effective_schema_uses_count_without_mutating_template(self) -> None:
        template = {
            "properties": {
                "answers": {"type": "array", "minItems": 8, "maxItems": 8}
            }
        }
        effective = runner.effective_output_schema(
            template, 13, "without_bundle"
        )
        self.assertEqual(effective["properties"]["answers"]["minItems"], 13)
        self.assertEqual(effective["properties"]["answers"]["maxItems"], 13)
        self.assertEqual(template["properties"]["answers"]["minItems"], 8)

    def test_pilot_schema_keeps_the_thirteen_answer_envelope_compact(self) -> None:
        template = json.loads(
            runner.PILOT_SCHEMA_PATH.read_text(encoding="utf-8")
        )
        answer = template["$defs"]["answer"]["properties"]
        self.assertEqual("string", answer["answer_mode"]["type"])
        self.assertEqual(256, template["$defs"]["httpUrl"]["maxLength"])
        self.assertEqual(1024, answer["answer_text"]["maxLength"])
        self.assertEqual(1, answer["source_urls"]["maxItems"])
        self.assertEqual(1, answer["assertion_ids"]["maxItems"])
        self.assertEqual(1, answer["assertion_provenance"]["maxItems"])
        self.assertEqual(
            "string",
            answer["journey"]["properties"]["episode_order"]["items"]["type"],
        )
        self.assertEqual("string", answer["jurisdictions"]["items"]["type"])
        self.assertEqual("string", answer["specialist_review"]["type"])
        provenance = answer["assertion_provenance"]["items"]["properties"]
        self.assertEqual(1, provenance["evidence_sources"]["maxItems"])
        self.assertEqual(0, answer["related_family_ids"]["maxItems"])
        self.assertEqual(
            256, answer["abstention"]["properties"]["reason"]["maxLength"]
        )
        self.assertEqual(
            [True],
            answer["abstention"]["properties"]["decision_abstained"]["enum"],
        )
        effective = runner.effective_output_schema(
            template, 13, "without_bundle"
        )
        self.assertEqual(13, effective["properties"]["answers"]["minItems"])
        self.assertEqual(13, effective["properties"]["answers"]["maxItems"])
        self.assertEqual(8, template["properties"]["answers"]["minItems"])

    def test_cli_help_describes_governed_packs_without_untouched_claim(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as raised:
            runner.main(["--help"])
        self.assertEqual(0, raised.exception.code)
        normalised = " ".join(output.getvalue().split())
        self.assertIn("one governed 13-question pack", normalised)
        self.assertNotIn("untouched", output.getvalue())

    def test_assisted_schema_requires_a_complete_navigation_handoff(self) -> None:
        template = json.loads(
            runner.PILOT_SCHEMA_PATH.read_text(encoding="utf-8")
        )
        effective = runner.effective_output_schema(template, 13, "with_bundle")
        properties = effective["$defs"]["answer"]["properties"]
        self.assertEqual(
            {"type": "string", "enum": ["navigation-only"]},
            properties["answer_mode"],
        )
        self.assertEqual("string", properties["selected_family"]["type"])
        self.assertEqual(
            2,
            properties["journey"]["properties"]["episode_order"]["minItems"],
        )
        self.assertEqual(
            "string",
            properties["journey"]["properties"]["first_step_id"]["type"],
        )
        for field in (
            "jurisdictions",
            "source_urls",
            "assertion_ids",
            "assertion_provenance",
        ):
            self.assertEqual(1, properties[field]["minItems"])
        self.assertEqual(
            {
                "type": "string",
                "enum": ["accepted", "not_required", "required"],
            },
            properties["specialist_review"],
        )
        self.assertEqual(
            ["abstention", "navigation-only"],
            sorted(template["$defs"]["answer"]["properties"]["answer_mode"]["enum"]),
        )

    def test_effective_schema_rejects_an_unknown_condition(self) -> None:
        template = {
            "properties": {"answers": {"type": "array"}},
            "$defs": {"answer": {"properties": {}}},
        }
        with self.assertRaisesRegex(runner.PilotError, "unsupported pilot condition"):
            runner.effective_output_schema(template, 13, "unexpected")

    def test_effective_schemas_use_standalone_refs_and_typed_enums(self) -> None:
        template = json.loads(
            runner.PILOT_SCHEMA_PATH.read_text(encoding="utf-8")
        )

        def walk(value: object, path: tuple[object, ...] = ()) -> None:
            if isinstance(value, dict):
                if "$ref" in value:
                    self.assertEqual(
                        {"$ref"},
                        set(value),
                        f"$ref has sibling keywords at {path}",
                    )
                if "enum" in value:
                    self.assertIn("type", value, f"enum lacks type at {path}")
                for key, child in value.items():
                    walk(child, (*path, key))
            elif isinstance(value, list):
                for index, child in enumerate(value):
                    walk(child, (*path, index))

        for condition in ("without_bundle", "with_bundle"):
            walk(runner.effective_output_schema(template, 13, condition))

    def test_claude_requires_a_scoped_environment_token(self) -> None:
        with (
            mock.patch.dict("os.environ", {}, clear=True),
            mock.patch.object(
                runner.subprocess,
                "run",
                return_value=runner.subprocess.CompletedProcess([], 1, "", "missing"),
            ),
        ):
            self.assertEqual("", runner.scoped_claude_token())
        with mock.patch.dict(
            "os.environ", {"CLAUDE_CODE_OAUTH_TOKEN": "scoped-fixture-token"}, clear=True
        ):
            self.assertEqual("scoped-fixture-token", runner.scoped_claude_token())

    def test_claude_can_read_only_the_dedicated_keychain_item(self) -> None:
        completed = runner.subprocess.CompletedProcess([], 0, "keychain-token\n", "")
        with (
            mock.patch.dict("os.environ", {"USER": "fixture-user"}, clear=True),
            mock.patch.object(runner.subprocess, "run", return_value=completed) as called,
        ):
            self.assertEqual("keychain-token", runner.scoped_claude_token())
        command = called.call_args.args[0]
        self.assertEqual("/usr/bin/security", command[0])
        self.assertIn(runner.CLAUDE_TOKEN_KEYCHAIN_SERVICE, command)

    def test_claude_runtime_and_configuration_stay_in_workspace(self) -> None:
        called, workspace = self.claude_call("without_bundle")
        environment = called.call_args.kwargs["extra_environment"]
        self.assertEqual(
            str(workspace / "_control" / "claude-config"),
            environment["CLAUDE_CONFIG_DIR"],
        )
        self.assertEqual(
            str(workspace / "_tmp"),
            environment["CLAUDE_CODE_TMPDIR"],
        )

    def test_claude_command_freezes_the_security_policy(self) -> None:
        baseline_call, workspace = self.claude_call("without_bundle")
        assisted_call, _ = self.claude_call("with_bundle")
        baseline = baseline_call.call_args.args[0]
        assisted = assisted_call.call_args.args[0]

        self.assertEqual("/usr/bin/sandbox-exec", baseline[0])
        self.assertIn("HOME_ROOT=/Users/fixture", baseline)
        self.assertIn(f"WORKSPACE={workspace}", baseline)
        self.assertIn("CLAUDE_LAUNCHER=/usr/bin/claude", baseline)
        self.assertIn("CLAUDE_BINARY=/usr/bin/claude", baseline)
        for flag in (
            "--print",
            "--safe-mode",
            "--no-chrome",
            "--disable-slash-commands",
            "--no-session-persistence",
            "--strict-mcp-config",
        ):
            self.assertIn(flag, baseline)
        self.assertEqual(
            '{"mcpServers":{}}', baseline[baseline.index("--mcp-config") + 1]
        )
        self.assertEqual("dontAsk", baseline[baseline.index("--permission-mode") + 1])
        self.assertEqual("", baseline[baseline.index("--tools") + 1])
        self.assertEqual(
            "Read,Glob,Grep", assisted[assisted.index("--tools") + 1]
        )
        for forbidden in (
            "--bare",
            "--dangerously-skip-permissions",
            "--allow-dangerously-skip-permissions",
            "--add-dir",
            "--plugin-dir",
            "--allowedTools",
        ):
            self.assertNotIn(forbidden, baseline)
            self.assertNotIn(forbidden, assisted)

    def test_claude_token_is_environment_only(self) -> None:
        called, _ = self.claude_call("with_bundle")
        command = called.call_args.args[0]
        environment = called.call_args.kwargs["extra_environment"]
        self.assertNotIn("scoped-fixture-token", command)
        self.assertEqual(
            "scoped-fixture-token", environment["CLAUDE_CODE_OAUTH_TOKEN"]
        )

    def test_claude_output_token_leak_fails_closed(self) -> None:
        leaked = runner.subprocess.CompletedProcess(
            [],
            0,
            "scoped-fixture-token",
            "",
        )
        with self.assertRaisesRegex(
            runner.PilotError, "output contained the scoped authentication token"
        ) as raised:
            self.claude_call("without_bundle", leaked)
        self.assertNotIn("scoped-fixture-token", str(raised.exception))

    def test_claude_unstructured_result_reports_only_prose_free_metadata(self) -> None:
        result = "sensitive model prose that must not appear"
        unstructured = runner.subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "result": result,
                }
            ),
            "",
        )
        with self.assertRaisesRegex(
            runner.PilotError,
            rf"no structured output .*result_chars={len(result)}",
        ) as raised:
            self.claude_call("without_bundle", unstructured)
        self.assertNotIn(result, str(raised.exception))

    def test_claude_accepts_whole_and_single_embedded_fenced_json(self) -> None:
        payload = {"answers": []}
        fenced = runner.subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "result": "```json\n" + json.dumps(payload) + "\n```",
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "modelUsage": {"claude-opus-fixture": {}},
                }
            ),
            "",
        )
        with (
            mock.patch.object(runner, "run_process", return_value=fenced),
            mock.patch.object(runner, "sha256_path", return_value="0" * 64),
        ):
            observed, metadata, *_ = runner.run_claude(
                Path("/private/tmp/isolated-fixture"),
                "without_bundle",
                "fixture prompt",
                {"type": "object"},
                Path("/private/tmp/isolated-fixture/_control/claude-pilot.sb"),
                "scoped-fixture-token",
            )
        self.assertEqual(payload, observed)
        self.assertEqual(
            "whole-fenced-json-result", metadata["structured_output_source"]
        )
        self.assertFalse(metadata["native_structured_output_conformant"])
        self.assertEqual("result-json-recovered", metadata["transport_conformance"])

        surrounded = runner.subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "result": "introduction\n```json\n"
                    + json.dumps(payload)
                    + "\n```",
                }
            ),
            "",
        )
        with (
            mock.patch.object(runner, "run_process", return_value=surrounded),
            mock.patch.object(runner, "sha256_path", return_value="0" * 64),
        ):
            observed, metadata, *_ = runner.run_claude(
                Path("/private/tmp/isolated-fixture"),
                "without_bundle",
                "fixture prompt",
                {"type": "object"},
                Path("/private/tmp/isolated-fixture/_control/claude-pilot.sb"),
                "scoped-fixture-token",
            )
        self.assertEqual(payload, observed)
        self.assertEqual(
            "single-embedded-fenced-json-result",
            metadata["structured_output_source"],
        )
        self.assertFalse(metadata["native_structured_output_conformant"])
        self.assertEqual(
            "wrapper-nonconformant-recovered",
            metadata["transport_conformance"],
        )

    def test_claude_native_structured_output_takes_precedence(self) -> None:
        payload = {"answers": []}
        completed = runner.subprocess.CompletedProcess(
            [],
            0,
            json.dumps(
                {
                    "type": "result",
                    "subtype": "success",
                    "is_error": False,
                    "structured_output": payload,
                    "result": "ambiguous {\"answers\": []} and {\"answers\": []}",
                }
            ),
            "",
        )
        with (
            mock.patch.object(runner, "run_process", return_value=completed),
            mock.patch.object(runner, "sha256_path", return_value="0" * 64),
        ):
            observed, metadata, *_ = runner.run_claude(
                Path("/private/tmp/isolated-fixture"),
                "without_bundle",
                "fixture prompt",
                {"type": "object"},
                Path("/private/tmp/isolated-fixture/_control/claude-pilot.sb"),
                "scoped-fixture-token",
            )
        self.assertEqual(payload, observed)
        self.assertTrue(metadata["native_structured_output_conformant"])
        self.assertEqual(
            "native-structured-output", metadata["transport_conformance"]
        )

    def test_claude_rejects_a_non_success_envelope(self) -> None:
        payload = {"answers": []}
        for envelope in (
            {"type": "error", "subtype": "success", "is_error": False},
            {"type": "result", "subtype": "failure", "is_error": False},
            {"type": "result", "subtype": "success", "is_error": True},
        ):
            completed = runner.subprocess.CompletedProcess(
                [], 0, json.dumps({**envelope, "structured_output": payload}), ""
            )
            with self.assertRaisesRegex(
                runner.PilotError, "non-success result envelope"
            ):
                self.claude_call("without_bundle", completed)

    def test_claude_accepts_one_embedded_direct_json_object(self) -> None:
        payload = {"answers": []}
        observed, source = runner.decode_claude_result(
            "Structured result follows:\n" + json.dumps(payload) + "\nDone."
        )
        self.assertEqual(payload, observed)
        self.assertEqual("single-embedded-json-result", source)

    def test_claude_rejects_ambiguous_embedded_json(self) -> None:
        payload = json.dumps({"answers": []})
        for result in (
            f"```json\n{payload}\n```\n```json\n{payload}\n```",
            f"first {payload} second {{\"answers\": []}}",
            f"```json\n{payload}\n``` then {{\"answers\": []}}",
        ):
            observed, source = runner.decode_claude_result(result)
            self.assertIsNone(observed)
            self.assertEqual("unparseable-json-result", source)

    def test_claude_rejects_malformed_array_and_scalar_results(self) -> None:
        for result in ("not JSON", "[]", '"scalar"', "```json\n[]\n```"):
            observed, source = runner.decode_claude_result(result)
            self.assertIsNone(observed)
            self.assertEqual("unparseable-json-result", source)

    def test_recovered_payload_still_requires_exact_schema_and_question_ids(self) -> None:
        schema = {
            "type": "object",
            "required": ["answers"],
            "properties": {
                "answers": {
                    "type": "array",
                    "minItems": 2,
                    "maxItems": 2,
                    "items": {
                        "type": "object",
                        "required": ["question_id"],
                        "properties": {"question_id": {"type": "string"}},
                        "additionalProperties": False,
                    },
                }
            },
            "additionalProperties": False,
        }
        expected = {"pack1-one", "pack1-two"}
        valid = {
            "answers": [
                {"question_id": "pack1-one"},
                {"question_id": "pack1-two"},
            ]
        }
        encoded = "wrapper\n```json\n" + json.dumps(valid) + "\n```\nend"
        recovered, _ = runner.decode_claude_result(encoded)
        assert recovered is not None
        self.assertEqual(2, len(runner.validate_payload(recovered, schema, expected)))

        invalid_payloads = (
            {"answers": [{"question_id": "pack1-one"}]},
            {
                "answers": [
                    {"question_id": "pack1-one"},
                    {"question_id": "pack1-one"},
                ]
            },
            {
                "answers": [
                    {"question_id": "pack1-one", "unexpected": True},
                    {"question_id": "pack1-two"},
                ]
            },
            {"answers": valid["answers"], "unexpected": True},
        )
        for payload in invalid_payloads:
            with self.assertRaises(runner.PilotError):
                runner.validate_payload(payload, schema, expected)

    def test_process_failure_redacts_scoped_token(self) -> None:
        process = runner.subprocess.CompletedProcess(
            [],
            1,
            "stdout scoped-fixture-token",
            "stderr scoped-fixture-token",
        )
        error = runner.process_failure(
            "Claude", process, secrets=("scoped-fixture-token",)
        )
        self.assertNotIn("scoped-fixture-token", str(error))
        self.assertIn("[REDACTED]", str(error))

    def test_model_environment_is_an_explicit_allowlist(self) -> None:
        program = (
            "import json, os; "
            "print(json.dumps({key: os.environ.get(key) for key in "
            "['HOME', 'PATH', 'UNRELATED_SECRET', 'CLAUDE_CODE_OAUTH_TOKEN']}))"
        )
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "_tmp").mkdir()
            with mock.patch.dict(
                os.environ,
                {
                    "HOME": "/Users/fixture",
                    "PATH": "/usr/bin",
                    "UNRELATED_SECRET": "must-not-pass",
                },
                clear=True,
            ):
                completed = runner.run_process(
                    [sys.executable, "-c", program],
                    workspace,
                    extra_environment={
                        "CLAUDE_CODE_OAUTH_TOKEN": "scoped-token"
                    },
                )
        environment = json.loads(completed.stdout)
        self.assertEqual("/Users/fixture", environment["HOME"])
        self.assertEqual("/usr/bin", environment["PATH"])
        self.assertIsNone(environment["UNRELATED_SECRET"])
        self.assertEqual("scoped-token", environment["CLAUDE_CODE_OAUTH_TOKEN"])

    def test_model_output_cap_is_enforced_while_streaming(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "_tmp").mkdir()
            started = time.monotonic()
            with (
                mock.patch.object(runner, "MAX_CAPTURE_BYTES", 1024),
                self.assertRaisesRegex(
                    runner.PilotError, "model stdout exceeds 1024 bytes"
                ),
            ):
                runner.run_process(
                    [
                        sys.executable,
                        "-c",
                        "import os, time; os.write(1, b'x' * 4096); time.sleep(30)",
                    ],
                    workspace,
                )
            self.assertLess(time.monotonic() - started, 5)

    def test_model_timeout_terminates_descendant_process_group(self) -> None:
        child_program = """
import signal
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])

def stop(_signum, _frame):
    (root / "descendant-terminated").write_text("yes", encoding="utf-8")
    raise SystemExit(0)

signal.signal(signal.SIGTERM, stop)
(root / "descendant-ready").write_text("yes", encoding="utf-8")
while True:
    time.sleep(1)
"""
        parent_program = """
import subprocess
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
child_program = sys.argv[2]
subprocess.Popen([sys.executable, "-c", child_program, str(root)])
deadline = time.monotonic() + 5
while not (root / "descendant-ready").exists():
    if time.monotonic() >= deadline:
        raise SystemExit("descendant did not start")
    time.sleep(0.01)
time.sleep(30)
"""
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary)
            (workspace / "_tmp").mkdir()
            with (
                mock.patch.object(runner, "TIMEOUT_SECONDS", 0.5),
                self.assertRaises(runner.subprocess.TimeoutExpired),
            ):
                runner.run_process(
                    [
                        sys.executable,
                        "-c",
                        parent_program,
                        str(workspace),
                        child_program,
                    ],
                    workspace,
                )
            self.assertTrue((workspace / "descendant-terminated").is_file())

    def test_claude_profile_uses_the_parameterised_home_root(self) -> None:
        profile = runner.CLAUDE_SANDBOX_PATH.read_text(encoding="utf-8")
        self.assertIn('(deny file-read* (subpath (param "HOME_ROOT")))', profile)
        self.assertIn('(deny file-write* (subpath (param "HOME_ROOT")))', profile)
        self.assertIn('(allow file-read* (subpath (param "WORKSPACE")))', profile)
        self.assertIn('(allow file-write* (subpath (param "WORKSPACE")))', profile)
        self.assertNotIn("/Users/crpage", profile)

    def test_cli_version_is_resolved_before_claude_invocation(self) -> None:
        events: list[str] = []

        def version(_executable: str, _workspace: Path) -> str:
            events.append("version")
            return "fixture-cli-version"

        def invoke(*_args: object, **_kwargs: object) -> tuple[dict, dict, str, str]:
            events.append("invoke")
            return {"answers": []}, {"provider": "Anthropic"}, "", ""

        workspace = Path("/private/tmp/isolated-fixture")
        with (
            mock.patch.object(runner.shutil, "which", return_value="/usr/bin/claude"),
            mock.patch.object(runner, "command_version", side_effect=version),
            mock.patch.object(
                runner, "scoped_claude_token", return_value="scoped-fixture-token"
            ),
            mock.patch.object(runner, "run_claude", side_effect=invoke),
        ):
            result = runner.run_selected_model(
                "claude",
                workspace,
                "without_bundle",
                "fixture prompt",
                {"type": "object"},
                workspace / "schema.json",
                workspace / "claude-pilot.sb",
            )
        self.assertEqual(["version", "invoke"], events)
        self.assertEqual("fixture-cli-version", result[4])

    def test_version_failure_prevents_paid_invocation(self) -> None:
        workspace = Path("/private/tmp/isolated-fixture")
        with (
            mock.patch.object(runner.shutil, "which", return_value="/usr/bin/claude"),
            mock.patch.object(
                runner,
                "command_version",
                side_effect=runner.PilotError("version failed"),
            ),
            mock.patch.object(runner, "run_claude") as invoke,
        ):
            with self.assertRaisesRegex(runner.PilotError, "version failed"):
                runner.run_selected_model(
                    "claude",
                    workspace,
                    "without_bundle",
                    "fixture prompt",
                    {"type": "object"},
                    workspace / "schema.json",
                    workspace / "claude-pilot.sb",
                )
        invoke.assert_not_called()

    def test_cli_version_uses_the_bounded_process_runner(self) -> None:
        completed = runner.subprocess.CompletedProcess(
            ["fixture", "--version"], 0, "fixture 1.2.3\n", ""
        )
        workspace = Path("/private/tmp/isolated-fixture")
        with mock.patch.object(
            runner, "run_process", return_value=completed
        ) as bounded:
            self.assertEqual(
                "fixture 1.2.3", runner.command_version("fixture", workspace)
            )
        bounded.assert_called_once_with(["fixture", "--version"], workspace)

    def test_cli_version_failure_is_bounded_and_diagnostic(self) -> None:
        completed = runner.subprocess.CompletedProcess(
            ["fixture", "--version"], 7, "", "bounded failure"
        )
        workspace = Path("/private/tmp/isolated-fixture")
        with (
            mock.patch.object(runner, "run_process", return_value=completed),
            self.assertRaisesRegex(
                runner.PilotError,
                "(?s)model CLI version check exited 7.*bounded failure",
            ),
        ):
            runner.command_version("fixture", workspace)

    def test_pilot_cell_commit_is_atomic_and_private(self) -> None:
        artefacts = {
            "answers": b"answers\n",
            "metadata": b"metadata\n",
            "raw_stdout": b"stdout\n",
            "raw_stderr": b"stderr\n",
            "prompt": b"prompt\n",
        }
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "runs" / "fixture-pilot"
            paths = runner.commit_pilot_cell(
                output_dir, "claude-with_bundle-gold", artefacts
            )
            cell_dir = output_dir / "claude-with_bundle-gold"
            self.assertEqual(0o700, stat.S_IMODE(output_dir.stat().st_mode))
            self.assertEqual(0o700, stat.S_IMODE(cell_dir.stat().st_mode))
            self.assertEqual(set(artefacts), set(paths))
            for key, path in paths.items():
                self.assertEqual(0o600, stat.S_IMODE(path.stat().st_mode))
                self.assertEqual(artefacts[key], path.read_bytes())

    def test_pilot_cell_write_failure_leaves_no_partial_cell(self) -> None:
        artefacts = {
            "answers": b"answers\n",
            "metadata": b"metadata\n",
            "raw_stdout": b"stdout\n",
            "raw_stderr": b"stderr\n",
            "prompt": b"prompt\n",
        }
        original = runner.write_private_file
        writes = 0

        def fail_during_write(path: Path, content: bytes) -> None:
            nonlocal writes
            writes += 1
            if writes == 3:
                raise OSError("fixture write failure")
            original(path, content)

        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "fixture-pilot"
            with mock.patch.object(
                runner, "write_private_file", side_effect=fail_during_write
            ):
                with self.assertRaisesRegex(OSError, "fixture write failure"):
                    runner.commit_pilot_cell(
                        output_dir, "claude-with_bundle-gold", artefacts
                    )
            self.assertEqual([], list(output_dir.iterdir()))

    def test_pilot_cell_never_replaces_complete_or_legacy_output(self) -> None:
        artefacts = {
            "answers": b"answers\n",
            "metadata": b"metadata\n",
            "raw_stdout": b"stdout\n",
            "raw_stderr": b"stderr\n",
            "prompt": b"prompt\n",
        }
        stem = "claude-with_bundle-gold"
        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "fixture-pilot"
            paths = runner.commit_pilot_cell(output_dir, stem, artefacts)
            with self.assertRaisesRegex(runner.PilotError, "refusing to replace"):
                runner.commit_pilot_cell(output_dir, stem, artefacts)
            self.assertEqual(b"answers\n", paths["answers"].read_bytes())

        with tempfile.TemporaryDirectory() as temporary:
            output_dir = Path(temporary) / "fixture-pilot"
            runner.ensure_private_directory(output_dir)
            legacy = output_dir / f"{stem}.json"
            legacy.write_bytes(b"legacy\n")
            with self.assertRaisesRegex(runner.PilotError, "refusing to replace"):
                runner.commit_pilot_cell(output_dir, stem, artefacts)
            self.assertEqual(b"legacy\n", legacy.read_bytes())

    def test_atomic_promotion_cannot_replace_a_concurrent_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "staged"
            destination = root / "complete"
            source.mkdir()
            destination.mkdir()
            (source / "value.txt").write_text("new\n", encoding="utf-8")
            (destination / "value.txt").write_text("existing\n", encoding="utf-8")
            with self.assertRaisesRegex(
                runner.PilotError, "concurrently created pilot output"
            ):
                runner.atomic_rename_no_replace(source, destination)
            self.assertEqual("existing\n", (destination / "value.txt").read_text())
            self.assertEqual("new\n", (source / "value.txt").read_text())

    def test_model_timeout_allows_forty_minutes_per_cell(self) -> None:
        self.assertEqual(40 * 60, runner.TIMEOUT_SECONDS)

    def test_private_directory_rejects_a_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "target"
            target.mkdir()
            link = root / "runs"
            link.symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(runner.PilotError, "symlinked"):
                runner.ensure_private_directory(link)


if __name__ == "__main__":
    unittest.main()
