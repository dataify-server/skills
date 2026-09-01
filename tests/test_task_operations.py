import importlib.util
import io
import json
import os
import pathlib
import sys
import unittest
import urllib.error
from unittest import mock


SCRIPT = (
    pathlib.Path(__file__).parents[1]
    / "skills"
    / "dataify-task-operations"
    / "scripts"
    / "wait_for_task.py"
)
SPEC = importlib.util.spec_from_file_location("wait_for_task", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
sys.modules["wait_for_task"] = MODULE

RUNTIME_SPEC = importlib.util.spec_from_file_location(
    "task_runtime", SCRIPT.with_name("task_runtime.py")
)
RUNTIME = importlib.util.module_from_spec(RUNTIME_SPEC)
RUNTIME_SPEC.loader.exec_module(RUNTIME)

TOKEN_SETUP_SPEC = importlib.util.spec_from_file_location(
    "token_setup", SCRIPT.with_name("token_setup.py")
)
TOKEN_SETUP = importlib.util.module_from_spec(TOKEN_SETUP_SPEC)
TOKEN_SETUP_SPEC.loader.exec_module(TOKEN_SETUP)


class WaitForTaskTests(unittest.TestCase):
    def test_token_helper_selects_platform_specific_commands(self):
        cases = (
            ("macos", "zsh", "export DATAIFY_API_TOKEN"),
            ("linux", "bash", "export DATAIFY_API_TOKEN"),
            ("windows", "powershell", "$env:DATAIFY_API_TOKEN"),
            ("windows", "cmd", "set DATAIFY_API_TOKEN"),
        )
        with mock.patch.dict(os.environ, {}, clear=True):
            for system, shell, expected in cases:
                result = TOKEN_SETUP.report(system, shell)
                self.assertFalse(result["configured"])
                self.assertIn(expected, result["setup_command"])
                self.assertFalse(result["token_value_exposed"])

    def test_token_helper_never_returns_configured_token_value(self):
        with mock.patch.dict(os.environ, {"DATAIFY_API_TOKEN": "super-secret"}, clear=True):
            result = TOKEN_SETUP.report("macos", "zsh")
        self.assertTrue(result["configured"])
        self.assertNotIn("super-secret", json.dumps(result))
        self.assertNotIn("setup_command", result)

    def test_production_wait_defaults(self):
        self.assertEqual(MODULE.DEFAULT_WAIT_TIMEOUT, 600)
        self.assertEqual(MODULE.DEFAULT_MAX_INTERVAL, 15)
        self.assertEqual(MODULE.DEFAULT_INTERVALS[-1], 15)

    def test_resume_command_reuses_task_id(self):
        command = MODULE.resume_command("task-resume", 600)
        self.assertIn('--task-id "task-resume"', command)
        self.assertIn("--timeout 600", command)
        self.assertNotIn("submit", command)

    def test_runtime_extracts_nested_task_id(self):
        self.assertEqual("task-nested", RUNTIME.extract_task_id({"data": {"task_id": "task-nested"}}))

    def test_runtime_returns_final_result_envelope(self):
        with mock.patch.object(RUNTIME, "wait_for_task", return_value={"items": [1]}) as waiter:
            result = RUNTIME.complete_task("task-final", "Bearer secret", 600, 60)
        self.assertEqual("succeeded", result["status"])
        self.assertEqual({"items": [1]}, result["data"])
        self.assertEqual("secret", waiter.call_args.args[1])

    def test_runtime_timeout_returns_recovery_command_without_traceback(self):
        with mock.patch.object(RUNTIME, "wait_for_task", side_effect=TimeoutError("still processing")):
            with self.assertRaisesRegex(RuntimeError, "Resume:.*task-timeout") as raised:
                RUNTIME.complete_task("task-timeout", "secret", 600, 60)
        self.assertNotIn("submit_", str(raised.exception))

    def test_runtime_interruption_returns_recovery_command(self):
        with mock.patch.object(RUNTIME, "wait_for_task", side_effect=KeyboardInterrupt):
            with self.assertRaisesRegex(RuntimeError, "(?s)Do not resubmit.*Resume:"):
                RUNTIME.complete_task("task-interrupted", "secret", 600, 60)

    def test_success_downloads_final_result(self):
        responses = [
            {"data": {"status": "处理中", "task_id": "task-1"}},
            {"data": {"status": "成功", "task_id": "task-1"}},
            {"items": [{"id": 1}]},
        ]
        with mock.patch.object(MODULE, "request_json", side_effect=responses) as request_json:
            with mock.patch.object(MODULE.time, "sleep"):
                result = MODULE.wait_for_task("task-1", "secret", 600, 60, 15, False)

        self.assertEqual(result, {"items": [{"id": 1}]})
        self.assertEqual(request_json.call_count, 3)
        self.assertEqual(request_json.call_args_list[-1].args[0], MODULE.DOWNLOAD_ENDPOINT)

    def test_task_registration_delay_retries_status_without_resubmitting(self):
        responses = [
            {"data": "Task_id is error!"},
            {"data": {"status": "处理中", "task_id": "task-late"}},
            {"data": {"status": "成功", "task_id": "task-late"}},
            {"items": [{"id": "ready"}]},
        ]
        with mock.patch.object(MODULE, "request_json", side_effect=responses) as request_json:
            with mock.patch.object(MODULE.time, "sleep"):
                result = MODULE.wait_for_task("task-late", "secret", 600, 60, 15, False)

        self.assertEqual({"items": [{"id": "ready"}]}, result)
        self.assertEqual(4, request_json.call_count)
        self.assertTrue(all(call.args[0] != MODULE.BASE_URL + "/builder" for call in request_json.call_args_list))

    def test_task_registration_error_fails_after_grace_period(self):
        with mock.patch.object(
            MODULE, "request_json", return_value={"data": "Task_id is error!"}
        ):
            with mock.patch.object(MODULE.time, "monotonic", side_effect=[0, 31]):
                with self.assertRaisesRegex(RuntimeError, "Task_id is error"):
                    MODULE.wait_for_task("bad-task", "secret", 600, 60, 15, False)

    def test_failed_task_is_not_downloaded_or_resubmitted(self):
        with mock.patch.object(
            MODULE,
            "request_json",
            return_value={"data": {"status": "失败", "message": "upstream rejected"}},
        ) as request_json:
            with self.assertRaisesRegex(RuntimeError, "upstream rejected"):
                MODULE.wait_for_task("task-2", "secret", 600, 60, 15, False)

        request_json.assert_called_once()

    def test_unknown_status_fails_closed(self):
        with mock.patch.object(
            MODULE,
            "request_json",
            return_value={"data": {"status": "mystery"}},
        ):
            with self.assertRaisesRegex(RuntimeError, "Unknown Dataify task status"):
                MODULE.wait_for_task("task-3", "secret", 600, 60, 15, False)

    def test_invalid_token_cta_does_not_ask_for_new_registration(self):
        error = urllib.error.HTTPError("https://example.invalid", 403, "Forbidden", {}, io.BytesIO(b"invalid key"))
        with mock.patch.object(MODULE.urllib.request, "urlopen", side_effect=error):
            with self.assertRaisesRegex(RuntimeError, "new registration is not required"):
                MODULE.request_json(MODULE.STATUS_ENDPOINT, {}, "secret", 60)

    def test_success_outputs_do_not_contain_dashboard_cta(self):
        root = pathlib.Path(__file__).parents[1] / "skills"
        for script in root.glob("scraper-*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            self.assertNotIn('"dashboard_url": DASHBOARD_URL', text, script)
            self.assertNotIn("Task submitted. Visit", text, script)

    def test_registration_bonus_is_limited_to_account_cta_policy(self):
        repository = pathlib.Path(__file__).parents[1]
        root = repository / "skills"
        messaging = json.loads((repository / "config" / "product-messaging.json").read_text(encoding="utf-8"))
        offer = messaging["signup_offer"]
        expected_copy = offer["copy_en"].format(credits=offer["credits"]).lower()
        for skill in root.glob("*/SKILL.md"):
            text = skill.read_text(encoding="utf-8")
            self.assertIn("## Account CTA policy", text, skill)
            self.assertIn(expected_copy, text.lower(), skill)

        for script in root.glob("*/scripts/*.py"):
            text = script.read_text(encoding="utf-8")
            if "50 free credits" in text or "50 免费积分" in text:
                self.assertNotIn("Task submitted. New accounts receive", text, script)
                self.assertNotIn("status\": \"succeeded\".*50 free credits", text, script)


if __name__ == "__main__":
    unittest.main()
